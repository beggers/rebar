#!/usr/bin/env python3
"""Run the immutable CPython public suite with real, unskipped locales."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "rebar-postfinal-cpython-public-locale-v1"
ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = "tools/postfinal_cpython_locale_oracle_v1.py"
PINNED = Path("/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14")
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ORIGINAL_MANIFEST_PATH = "oracle/cpython-3.14.6/manifest.json"
ORIGINAL_MANIFEST_SHA256 = "2c89ce37e474cb6f59d61f86ad810662b50b83bbdce3610c04523fe092688597"
ORIGINAL_RUNNER_PATH = "tools/cpython_re_oracle.py"
ORIGINAL_RUNNER_SHA256 = "d5084fd43352f34267f3ed9b4b5d60a6070e2c50d4b787739270502c856e18bb"
SELECTED_METHOD_SHA256 = "d33571d09a3a9cb428a84dece5af233e66267b831d3043c90e3ad77cb8de5178"
SOURCE_HASHES = {
    "LICENSE": "b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231",
    "re_tests.py": "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab",
    "test_re.py": "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2",
}
METHOD_WAIVERS = {
    "ReTests.test_re_groupref_overflow": "PRIVATE-CONSTANTS: imports re._constants.MAXGROUPS",
    "ReTests.test_large_search": "RESOURCE-BIGMEM: requires a multi-gigabyte test resource",
    "ReTests.test_large_subn": "RESOURCE-BIGMEM: requires a multi-gigabyte test resource",
    "ReTests.test_search_anchor_at_beginning": "PERFORMANCE-ASSERTION: timing threshold belongs in the frozen performance oracle",
    "ReTests.test_regression_gh94675": "ENV-MULTIPROCESSING: sandbox cannot create the required forkserver socket",
    "ReTests.test_memory_leaks": "PRIVATE-DEBUG-HOOK: requires Pattern._fail_after from a debug CPython build",
}
CLASS_WAIVERS = {
    "DebugTests": "PRIVATE-DEBUG-TEXT: stdlib opcode/debug text is not a public contract",
    "ImplementationTest": "PRIVATE-INTERNAL-COMPILER: checks re._compiler, _sre, and deprecated internal modules",
}
ROLE_MODULES = {
    "re": "re",
    "rust": "candidates.rust_candidate",
    "vm": "candidates.vm_candidate",
    "zig": "candidates.zig_candidate",
}
SOURCE_PATHS = frozenset({
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
NATIVE_PATHS = {
    "candidates.rust_candidate:native-bridge": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
    "candidates.rust_candidate:native-engine": "candidates/_rust_engine.so",
    "candidates.vm_candidate:native-engine": "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
    "candidates.zig_candidate:native-bridge": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    "candidates.zig_candidate:native-engine": "candidates/_zig_probe.so",
}
REQUIRED_LOCALE_TESTS = frozenset({
    "ReTests.test_locale_caching",
    "ReTests.test_locale_compiled",
})
EVIDENCE_PATH = ROOT / "oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json"
LOCALE_SOURCE = Path("/usr/share/i18n/locales/en_US")
CHARMAPS = {
    "iso88591": Path("/usr/share/i18n/charmaps/ISO-8859-1.gz"),
    "utf8": Path("/usr/share/i18n/charmaps/UTF-8.gz"),
}
LOCALE_NAMES = {"iso88591": "en_US.iso88591", "utf8": "en_US.utf8"}
LOCALEDEF = Path("/usr/bin/localedef")
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_BINARY_BYTES = 128 * 1024 * 1024


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")


def checked_repo_path(relative: str) -> Path:
    require(isinstance(relative, str), "a production path must be a string")
    candidate = ROOT / relative
    require(not candidate.is_symlink(), f"a production path is a symlink: {relative}")
    resolved = candidate.resolve(strict=True)
    require(resolved.is_relative_to(ROOT), f"a production path escaped the project: {relative}")
    require(resolved.is_file(), f"a production file is missing: {relative}")
    return resolved


def sha256_path(path: Path, *, maximum: int = MAX_BINARY_BYTES) -> str:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), f"not a regular file: {path}")
        require(metadata.st_size <= maximum, f"file exceeds its safety bound: {path}")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            return hashlib.file_digest(stream, "sha256").hexdigest()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def read_json(path: Path) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode), f"JSON is not a regular file: {path}")
        require(metadata.st_size <= MAX_JSON_BYTES, f"JSON exceeds its safety bound: {path}")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            document = json.load(stream)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    require(isinstance(document, dict), f"JSON evidence is not an object: {path}")
    return document


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython", "genuine CPython is required")
    require(tuple(sys.version_info[:3]) == (3, 14, 6), "CPython 3.14.6 is required")
    require(Path(sys.executable).resolve() == PINNED.resolve(), "the pinned interpreter is required")
    require(bool(sys.flags.isolated), "run the controller with -I")
    require(bool(sys.dont_write_bytecode), "run the controller with -B")


def validate_manifest(document: dict[str, Any]) -> None:
    require(document.get("schema") == "rebar-cpython-re-oracle-v1", "official oracle schema changed")
    require(document.get("python") == "3.14.6", "official Python version changed")
    require(document.get("implementation") == "CPython", "official implementation changed")
    require(document.get("goal_sha256") == GOAL_SHA256, "official objective changed")
    require(document.get("runner_sha256") == ORIGINAL_RUNNER_SHA256, "official runner fingerprint changed")
    require(document.get("source_sha256") == SOURCE_HASHES, "official upstream source changed")
    require(document.get("test_methods") == 152, "official public denominator changed")
    require(document.get("selected_methods") == 146, "official selected denominator changed")
    require(document.get("corpus_cases") == 403, "official upstream corpus changed")
    require(document.get("public_classes") == ["ReTests", "PatternReprTests", "ExternalTests"],
            "official public test classes changed")
    require(document.get("named_waivers") == (CLASS_WAIVERS | METHOD_WAIVERS),
            "a named official waiver was silently added, removed, or relaxed")


def audit_version(path: str, family: str) -> int:
    for version in (4, 5):
        expected = f"candidates/audits/POSTFINAL-{family}-AUDIT-V{version}.json"
        if path == expected:
            return version
    raise AssertionError(f"only exact version-four/five {family} audit paths are accepted")


def validate_audits(
    source: dict[str, Any], strict: dict[str, Any], *,
    source_relative: str, strict_relative: str, source_digest: str,
) -> tuple[dict[str, str], dict[str, str]]:
    version = audit_version(source_relative, "FROM-SCRATCH")
    require(audit_version(strict_relative, "NO-DELEGATION") == version,
            "source and no-delegation audit versions differ")
    require(source.get("postfinal_schema") == f"rebar-postfinal-from-scratch-audit-v{version}",
            "from-scratch schema is not the exact selected version")
    require(strict.get("postfinal_schema") == f"rebar-postfinal-no-delegation-audit-v{version}",
            "no-delegation schema is not the exact selected version")
    source_controller = f"tools/postfinal_from_scratch_audit_v{version}.py"
    strict_controller = f"tools/postfinal_no_delegation_audit_v{version}.py"
    require(source.get("audit_source_path") == source_controller,
            "from-scratch audit used a substituted controller")
    require(is_sha256(source.get("audit_source_sha256")),
            "from-scratch audit omitted its authenticated controller")
    require(strict.get("audit_source_path") == strict_controller,
            "no-delegation audit used a substituted controller")
    require(is_sha256(strict.get("audit_source_sha256")),
            "no-delegation audit omitted its authenticated controller")
    for label, document in (("from-scratch", source), ("no-delegation", strict)):
        require(document.get("status") == "PASS", f"{label} audit did not pass")
        require(document.get("result") == "PASS", f"{label} audit has no passing result")
        require(document.get("passed") is True, f"{label} audit has no actual passing verdict")
        families = document.get("families")
        require(isinstance(families, dict) and set(families) == {"ast", "rust", "vm", "zig"},
                f"{label} audit omitted an independent engine family")
        for family in ("rust", "vm", "zig"):
            require(families[family].get("passed") is True,
                    f"{label} audit did not qualify the actual {family} family")
    require(source.get("verified_distinct_pipeline_count") == 4,
            "from-scratch audit omitted an independently owned pipeline")
    require(source.get("verified_core_family_count") == 3,
            "from-scratch audit omitted a native candidate family")
    require(strict.get("base_audit_report_path") == source_relative,
            "no-delegation audit is not bound to this source audit")
    require(strict.get("base_audit_report_sha256") == source_digest,
            "no-delegation audit is bound to a stale source audit")
    require(strict.get("inherited_control_count") == 76,
            "no-delegation audit weakened the inherited controls")
    sources = strict.get("qualified_source_fingerprints")
    require(isinstance(sources, dict) and set(sources) == SOURCE_PATHS,
            "no-delegation audit omitted or substituted a source role")
    require(all(is_sha256(value) for value in sources.values()),
            "no-delegation audit contains an invalid source fingerprint")
    natives = strict.get("native_elf_fingerprints")
    require(isinstance(natives, dict) and set(natives) == set(NATIVE_PATHS),
            "no-delegation audit omitted or substituted a native role")
    require(all(is_sha256(value) for value in natives.values()),
            "no-delegation audit contains an invalid native fingerprint")
    return dict(sources), dict(natives)


def verify_production_fingerprints(sources: dict[str, str], natives: dict[str, str]) -> None:
    for relative, expected in sorted(sources.items()):
        require(sha256_path(checked_repo_path(relative)) == expected,
                f"audited production source changed: {relative}")
    for role, expected in sorted(natives.items()):
        relative = NATIVE_PATHS[role]
        require(sha256_path(checked_repo_path(relative)) == expected,
                f"audited native engine changed: {relative}")


def validate_role(
    document: dict[str, Any], module: str, *, expected_ids: frozenset[str] | None = None,
) -> dict[str, Any]:
    require(document.get("schema") == "rebar-cpython-re-result-v1", "official result schema changed")
    require(document.get("module") == module, "official result selected another engine")
    require(document.get("runner_sha256") == ORIGINAL_RUNNER_SHA256,
            "official result ran a different test runner")
    require(document.get("source_sha256") == SOURCE_HASHES,
            "official result used different upstream tests")
    for name, value in (("methods", 146), ("passed", 146), ("skipped", 0),
                        ("failed", 0), ("crashes", 0), ("timeouts", 0)):
        require(document.get(name) == value, f"official {module} {name} is not {value}")
    records = document.get("records")
    require(isinstance(records, list) and len(records) == 146,
            "official result does not preserve all 146 individual methods")
    identifiers: set[str] = set()
    for record in records:
        require(isinstance(record, dict), "official method record is malformed")
        name = record.get("test")
        require(isinstance(name, str) and name.startswith(("ReTests.", "PatternReprTests.", "ExternalTests.")),
                "official method has no upstream public identity")
        require(name not in identifiers, "official method result was duplicated")
        require(name not in METHOD_WAIVERS, "a waived method entered the selected denominator")
        require(record.get("status") == "passed", f"official method did not pass: {name}")
        require(record.get("skipped") == 0, f"official method skipped: {name}")
        require(record.get("reason") is None, f"official method retained a skip reason: {name}")
        require(not record.get("failures"), f"official method retained a failure: {name}")
        identifiers.add(name)
    require(REQUIRED_LOCALE_TESTS <= identifiers, "an actual upstream locale test is missing")
    if expected_ids is not None:
        require(identifiers == expected_ids, "candidate changed the exact CPython selected test identities")
    return {
        "module": module,
        "methods": 146,
        "passed": 146,
        "skipped": 0,
        "failed": 0,
        "failures": 0,
        "errors": 0,
        "crashes": 0,
        "timeouts": 0,
        "locale_caching_passed": True,
        "locale_compiled_passed": True,
        "records": records,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def check_locale_inputs() -> dict[str, dict[str, str]]:
    require(LOCALEDEF.is_file() and os.access(LOCALEDEF, os.X_OK),
            "the real system localedef compiler is unavailable")
    require(LOCALE_SOURCE.is_file(), "the real en_US locale definition is unavailable")
    source_digest = sha256_path(LOCALE_SOURCE)
    metadata: dict[str, dict[str, str]] = {}
    for role, path in CHARMAPS.items():
        require(path.is_file(), f"the real {role} character map is unavailable")
        metadata[role] = {
            "name": LOCALE_NAMES[role],
            "source_sha256": source_digest,
            "charmap_sha256": sha256_path(path),
        }
    return metadata


def build_private_locales(directory: Path) -> dict[str, Any]:
    metadata = check_locale_inputs()
    for role, encoding in (("iso88591", "ISO-8859-1"), ("utf8", "UTF-8")):
        destination = directory / LOCALE_NAMES[role]
        result = subprocess.run(
            [str(LOCALEDEF), "--no-archive", "-f", encoding, "-i", "en_US", str(destination)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=False, timeout=120,
        )
        require(result.returncode == 0,
                f"real private {encoding} locale compilation failed: {result.stderr[-4000:]}")
        require(destination.is_dir() and not destination.is_symlink(),
                f"real private {encoding} locale was not created")
    return {"private": True, "genuine": True, **metadata,
            "holdout_accessed": False, "timing_performed": False,
            "performance": "NOT MEASURED"}


LOCALE_REFERENCE = r'''
import json
import locale
import os
import re
import sys
assert sys.implementation.name == "cpython"
assert tuple(sys.version_info[:3]) == (3, 14, 6)
assert sys.flags.isolated
assert sys.dont_write_bytecode
assert os.environ.get("LOCPATH") == sys.argv[1]
assert not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules)
original = locale.setlocale(locale.LC_CTYPE)
try:
    for name in ("en_US.iso88591", "en_US.utf8"):
        assert locale.setlocale(locale.LC_CTYPE, name) == name
    locale.setlocale(locale.LC_CTYPE, "en_US.iso88591")
    assert re.match(b"\xc5", b"\xe5", re.L | re.I)
    assert re.match(b"\xe5", b"\xc5", re.L | re.I)
    assert re.match(b"(?Li)\xc5", b"\xe5")
    assert re.match(b"(?Li)\xe5", b"\xc5")
    patterns = (
        re.compile(b"\xc5\xe5", re.L | re.I),
        re.compile(b"[a\xc5][a\xe5]", re.L | re.I),
        re.compile(b"[az\xc5][az\xe5]", re.L | re.I),
    )
    negative = re.compile(b"[^\xc5][^\xe5]", re.L | re.I)
    for pattern in patterns:
        for subject in (b"\xc5\xe5", b"\xe5\xe5", b"\xc5\xc5"):
            assert pattern.match(subject)
    for subject in (b"\xe5\xc5", b"\xe5\xe5", b"\xc5\xc5"):
        assert negative.match(subject) is None
    locale.setlocale(locale.LC_CTYPE, "en_US.utf8")
    assert re.match(b"\xc5", b"\xe5", re.L | re.I) is None
    assert re.match(b"\xe5", b"\xc5", re.L | re.I) is None
    assert re.match(b"(?Li)\xc5", b"\xe5") is None
    assert re.match(b"(?Li)\xe5", b"\xc5") is None
    for pattern in patterns:
        assert pattern.match(b"\xc5\xe5")
        assert pattern.match(b"\xe5\xe5") is None
        assert pattern.match(b"\xc5\xc5") is None
    assert negative.match(b"\xe5\xc5")
    assert negative.match(b"\xe5\xe5") is None
    assert negative.match(b"\xc5\xc5") is None
finally:
    locale.setlocale(locale.LC_CTYPE, original)
print(json.dumps({"status":"PASS","python":"3.14.6","candidate_modules_loaded":False,
                  "genuine_locales":True,"compiled_locale_switch":True,
                  "holdout_accessed":False,"timing_performed":False},sort_keys=True))
'''


def isolated_environment(locale_root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["LOCPATH"] = str(locale_root)
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONSTARTUP", None)
    return environment


def verify_locale_reference(locale_root: Path) -> dict[str, Any]:
    child = subprocess.run(
        [str(PINNED), "-I", "-B", "-c", LOCALE_REFERENCE, str(locale_root)],
        cwd=str(ROOT), env=isolated_environment(locale_root), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        check=False, timeout=60,
    )
    require(child.returncode == 0,
            f"genuine isolated CPython locale self-reference failed: {child.stderr[-4000:]}")
    try:
        report = json.loads(child.stdout.strip())
    except (ValueError, json.JSONDecodeError) as error:
        raise AssertionError("genuine locale self-reference produced invalid evidence") from error
    require(report == {
        "status": "PASS", "python": "3.14.6", "candidate_modules_loaded": False,
        "genuine_locales": True, "compiled_locale_switch": True,
        "holdout_accessed": False, "timing_performed": False,
    }, "genuine locale self-reference was weakened")
    return report


def run_original_role(role: str, locale_root: Path, temporary: Path) -> dict[str, Any]:
    module = ROLE_MODULES[role]
    output = temporary / f"official-{role}.json"
    require(not output.exists(), "a private official report already exists")
    child = subprocess.run(
        [str(PINNED), "-I", "-B", str(ROOT / ORIGINAL_RUNNER_PATH),
         "verify", "--module", module, "--output", str(output)],
        cwd=str(ROOT), env=isolated_environment(locale_root), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        check=False, timeout=2400,
    )
    require(child.returncode == 0,
            f"original CPython oracle rejected {role}: {child.stderr[-6000:]} {child.stdout[-3000:]}")
    require(output.is_file() and not output.is_symlink(),
            f"original CPython oracle omitted its complete {role} method records")
    return read_json(output)


def exclusive_evidence(report: dict[str, Any]) -> None:
    parent = EVIDENCE_PATH.parent
    require(parent.resolve().is_relative_to(ROOT), "locale evidence escaped the project")
    parent.mkdir(mode=0o755, parents=False, exist_ok=True)
    require(parent.is_dir() and not parent.is_symlink(), "locale evidence directory is unsafe")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(EVIDENCE_PATH, flags, 0o600)
    try:
        payload = canonical(report) + b"\n"
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        directory = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def run_audit(source_relative: str, strict_relative: str) -> dict[str, Any]:
    verify_runtime()
    require(not EVIDENCE_PATH.exists() and not EVIDENCE_PATH.is_symlink(),
            "exclusive locale evidence already exists")
    require(sha256_path(checked_repo_path("GOAL.md")) == GOAL_SHA256,
            "the immutable objective changed")
    manifest_path = checked_repo_path(ORIGINAL_MANIFEST_PATH)
    require(sha256_path(manifest_path) == ORIGINAL_MANIFEST_SHA256,
            "the frozen official manifest changed")
    runner_path = checked_repo_path(ORIGINAL_RUNNER_PATH)
    require(sha256_path(runner_path) == ORIGINAL_RUNNER_SHA256,
            "the frozen official runner changed")
    manifest = read_json(manifest_path)
    validate_manifest(manifest)
    for name, expected in SOURCE_HASHES.items():
        path = checked_repo_path(f"oracle/cpython-3.14.6/{name}")
        require(sha256_path(path) == expected, f"frozen upstream source changed: {name}")
    source_path = checked_repo_path(source_relative)
    strict_path = checked_repo_path(strict_relative)
    source_digest = sha256_path(source_path)
    strict_digest = sha256_path(strict_path)
    source_audit = read_json(source_path)
    strict_audit = read_json(strict_path)
    sources, natives = validate_audits(
        source_audit, strict_audit, source_relative=source_relative,
        strict_relative=strict_relative, source_digest=source_digest,
    )
    source_controller = checked_repo_path(source_audit["audit_source_path"])
    strict_controller = checked_repo_path(strict_audit["audit_source_path"])
    require(sha256_path(source_controller) == source_audit["audit_source_sha256"],
            "from-scratch controller changed after its source audit")
    require(sha256_path(strict_controller) == strict_audit["audit_source_sha256"],
            "no-delegation controller changed after its strict audit")
    verify_production_fingerprints(sources, natives)
    with tempfile.TemporaryDirectory(prefix="rebar-postfinal-official-locale-v1-", dir="/tmp") as private:
        private_root = Path(private)
        locales = build_private_locales(private_root)
        reference = verify_locale_reference(private_root)
        roles: dict[str, dict[str, Any]] = {}
        baseline = run_original_role("re", private_root, private_root)
        roles["re"] = validate_role(baseline, "re")
        selected_ids = frozenset(record["test"] for record in roles["re"]["records"])
        require(len(selected_ids) == 146, "baseline did not identify all official methods")
        selected_digest = hashlib.sha256(canonical(sorted(selected_ids))).hexdigest()
        require(selected_digest == SELECTED_METHOD_SHA256,
                "baseline changed the immutable original 146 official method identities")
        for role in ("rust", "vm", "zig"):
            verify_production_fingerprints(sources, natives)
            document = run_original_role(role, private_root, private_root)
            roles[role] = validate_role(document, ROLE_MODULES[role], expected_ids=selected_ids)
            verify_production_fingerprints(sources, natives)
        require(sha256_path(source_path) == source_digest and sha256_path(strict_path) == strict_digest,
                "a production independence proof changed during the correctness run")
        require(sha256_path(source_controller) == source_audit["audit_source_sha256"],
                "the current source-audit controller changed during the correctness run")
        require(sha256_path(strict_controller) == strict_audit["audit_source_sha256"],
                "the current no-delegation controller changed during the correctness run")
        producer = checked_repo_path(SOURCE_PATH)
        report = {
            "schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "python": "3.14.6",
            "goal_sha256": GOAL_SHA256,
            "source_path": SOURCE_PATH,
            "source_sha256": sha256_path(producer),
            "original_oracle": {
                "manifest_path": ORIGINAL_MANIFEST_PATH,
                "manifest_sha256": ORIGINAL_MANIFEST_SHA256,
                "runner_path": ORIGINAL_RUNNER_PATH,
                "runner_sha256": ORIGINAL_RUNNER_SHA256,
                "source_sha256": SOURCE_HASHES,
                "total_public_methods": 152,
                "selected_methods": 146,
                "selected_method_sha256": selected_digest,
                "named_waivers": METHOD_WAIVERS,
                "named_class_waivers": CLASS_WAIVERS,
                "all_named_waivers": manifest["named_waivers"],
                "corpus_cases": 403,
            },
            "audits": {
                "from_scratch": {
                    "path": source_relative,
                    "sha256": source_digest,
                    "postfinal_schema": source_audit["postfinal_schema"],
                    "source_path": source_audit["audit_source_path"],
                    "source_sha256": source_audit["audit_source_sha256"],
                },
                "no_delegation": {
                    "path": strict_relative,
                    "sha256": strict_digest,
                    "postfinal_schema": strict_audit["postfinal_schema"],
                    "source_path": strict_audit["audit_source_path"],
                    "source_sha256": strict_audit["audit_source_sha256"],
                },
            },
            "qualified_source_fingerprints": sources,
            "native_elf_fingerprints": natives,
            "locales": locales,
            "locale_reference": reference,
            "roles": roles,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
        }
        exclusive_evidence(report)
    return report


def self_test() -> dict[str, Any]:
    """Exercise only synthetic in-memory documents: no files or candidates."""
    checks = 0

    def accept(action: Any) -> None:
        nonlocal checks
        action()
        checks += 1

    def reject(action: Any) -> None:
        nonlocal checks
        try:
            action()
        except (AssertionError, TypeError, ValueError, KeyError):
            checks += 1
            return
        raise AssertionError("synthetic poison was silently accepted")

    manifest: dict[str, Any] = {
        "schema": "rebar-cpython-re-oracle-v1",
        "python": "3.14.6",
        "implementation": "CPython",
        "goal_sha256": GOAL_SHA256,
        "runner_sha256": ORIGINAL_RUNNER_SHA256,
        "source_sha256": dict(SOURCE_HASHES),
        "test_methods": 152,
        "selected_methods": 146,
        "corpus_cases": 403,
        "public_classes": ["ReTests", "PatternReprTests", "ExternalTests"],
        "named_waivers": CLASS_WAIVERS | METHOD_WAIVERS,
    }
    accept(lambda: validate_manifest(manifest))
    for key, poisoned in (
        ("schema", "fake"), ("python", "3.14.5"), ("implementation", "other"),
        ("goal_sha256", "0" * 64), ("runner_sha256", "0" * 64),
        ("source_sha256", {}), ("test_methods", 151), ("selected_methods", 145),
        ("corpus_cases", 402), ("public_classes", ["ReTests"]),
        ("named_waivers", METHOD_WAIVERS),
    ):
        changed = copy.deepcopy(manifest)
        changed[key] = poisoned
        reject(lambda changed=changed: validate_manifest(changed))

    identities = ["ReTests.test_locale_caching", "ReTests.test_locale_compiled"]
    identities += [f"ReTests.test_synthetic_{number:03d}" for number in range(144)]
    records = [{"test": name, "status": "passed", "skipped": 0, "reason": None}
               for name in identities]
    role: dict[str, Any] = {
        "schema": "rebar-cpython-re-result-v1", "module": "re",
        "runner_sha256": ORIGINAL_RUNNER_SHA256,
        "source_sha256": dict(SOURCE_HASHES), "methods": 146, "passed": 146,
        "skipped": 0, "failed": 0, "crashes": 0, "timeouts": 0,
        "records": records,
    }
    expected = frozenset(identities)
    accept(lambda: validate_role(role, "re", expected_ids=expected))
    for key, poisoned in (
        ("schema", "fake"), ("module", "candidates.rust_candidate"),
        ("runner_sha256", "0" * 64), ("source_sha256", {}),
        ("methods", 145), ("passed", 145), ("skipped", 1),
        ("failed", 1), ("crashes", 1), ("timeouts", 1),
        ("records", records[:-1]),
    ):
        changed = copy.deepcopy(role)
        changed[key] = poisoned
        reject(lambda changed=changed: validate_role(changed, "re", expected_ids=expected))
    for record_key, poisoned in (
        ("test", "ReTests.test_large_search"),
        ("test", "OtherTests.synthetic"), ("status", "skipped"),
        ("status", "failed"), ("skipped", 1), ("reason", "unsupported locale"),
        ("failures", [{"reason": "hidden mismatch"}]),
    ):
        changed = copy.deepcopy(role)
        changed["records"][3][record_key] = poisoned
        reject(lambda changed=changed: validate_role(changed, "re", expected_ids=expected))
    duplicate = copy.deepcopy(role)
    duplicate["records"][3]["test"] = duplicate["records"][4]["test"]
    reject(lambda: validate_role(duplicate, "re", expected_ids=expected))
    missing_locale = copy.deepcopy(role)
    missing_locale["records"][0]["test"] = "ReTests.test_substituted"
    reject(lambda: validate_role(missing_locale, "re", expected_ids=expected))
    reject(lambda: validate_role(role, "re", expected_ids=frozenset(set(expected) - {identities[-1]})))

    synthetic_sha = "a" * 64
    families = {name: {"passed": True} for name in ("ast", "rust", "vm", "zig")}
    source: dict[str, Any] = {
        "postfinal_schema": "rebar-postfinal-from-scratch-audit-v4",
        "audit_source_path": "tools/postfinal_from_scratch_audit_v4.py",
        "audit_source_sha256": synthetic_sha,
        "status": "PASS", "result": "PASS", "passed": True,
        "verified_distinct_pipeline_count": 4, "verified_core_family_count": 3,
        "families": families,
    }
    strict: dict[str, Any] = {
        "postfinal_schema": "rebar-postfinal-no-delegation-audit-v4",
        "audit_source_path": "tools/postfinal_no_delegation_audit_v4.py",
        "audit_source_sha256": synthetic_sha,
        "status": "PASS", "result": "PASS", "passed": True,
        "families": copy.deepcopy(families),
        "base_audit_report_path": "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json",
        "base_audit_report_sha256": synthetic_sha,
        "inherited_control_count": 76,
        "qualified_source_fingerprints": {name: synthetic_sha for name in SOURCE_PATHS},
        "native_elf_fingerprints": {name: synthetic_sha for name in NATIVE_PATHS},
    }

    def inspect_audits(left: dict[str, Any], right: dict[str, Any],
                       source_name: str = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V4.json",
                       strict_name: str = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V4.json",
                       digest: str = synthetic_sha) -> Any:
        return validate_audits(left, right, source_relative=source_name,
                               strict_relative=strict_name, source_digest=digest)

    accept(lambda: inspect_audits(source, strict))
    version_five_source = copy.deepcopy(source)
    version_five_source["postfinal_schema"] = "rebar-postfinal-from-scratch-audit-v5"
    version_five_source["audit_source_path"] = "tools/postfinal_from_scratch_audit_v5.py"
    version_five_strict = copy.deepcopy(strict)
    version_five_strict["postfinal_schema"] = "rebar-postfinal-no-delegation-audit-v5"
    version_five_strict["audit_source_path"] = "tools/postfinal_no_delegation_audit_v5.py"
    version_five_strict["base_audit_report_path"] = (
        "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json"
    )
    accept(lambda: inspect_audits(
        version_five_source, version_five_strict,
        source_name="candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json",
        strict_name="candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json",
    ))
    for label, key, poisoned in (
        ("source", "postfinal_schema", "fake"),
        ("source", "audit_source_path", "tools/substituted.py"),
        ("source", "audit_source_sha256", "invalid"),
        ("source", "status", "FAIL"), ("source", "result", "FAIL"),
        ("source", "passed", False), ("source", "verified_distinct_pipeline_count", 3),
        ("source", "verified_core_family_count", 2),
        ("strict", "postfinal_schema", "fake"),
        ("strict", "audit_source_path", "tools/substituted.py"),
        ("strict", "audit_source_sha256", "invalid"),
        ("strict", "status", "FAIL"), ("strict", "result", "FAIL"),
        ("strict", "passed", False), ("strict", "base_audit_report_path", "other.json"),
        ("strict", "base_audit_report_sha256", "b" * 64),
        ("strict", "inherited_control_count", 75),
        ("strict", "qualified_source_fingerprints", {}),
        ("strict", "native_elf_fingerprints", {}),
    ):
        left, right = copy.deepcopy(source), copy.deepcopy(strict)
        (left if label == "source" else right)[key] = poisoned
        reject(lambda left=left, right=right: inspect_audits(left, right))
    for label in ("source", "strict"):
        for family in ("ast", "rust", "vm", "zig"):
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            del (left if label == "source" else right)["families"][family]
            reject(lambda left=left, right=right: inspect_audits(left, right))
        for family in ("rust", "vm", "zig"):
            left, right = copy.deepcopy(source), copy.deepcopy(strict)
            (left if label == "source" else right)["families"][family]["passed"] = False
            reject(lambda left=left, right=right: inspect_audits(left, right))
    for path in ("../audit.json", "candidates/audits/fake.json",
                 "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json"):
        reject(lambda path=path: inspect_audits(source, strict, source_name=path))
    reject(lambda: inspect_audits(
        source, strict,
        strict_name="candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json"))
    require(checks >= 73, "candidate-free locale self-test silently lost controls")
    return {
        "schema": f"{SCHEMA}-self-test", "status": "PASS", "passed": checks,
        "candidate_imported": False, "candidate_executed": False,
        "files_read": 0, "files_written": 0, "locales_compiled": 0,
        "holdout_accessed": False, "timing_performed": False,
        "performance": "NOT MEASURED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true", help="run only in-memory poison controls")
    mode.add_argument("--audit", action="store_true", help="exclusively create the strict four-role locale proof")
    parser.add_argument("--source-audit",
                        default="candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json")
    parser.add_argument("--strict-audit",
                        default="candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json")
    args = parser.parse_args(argv)
    try:
        report = self_test() if args.self_test else run_audit(args.source_audit, args.strict_audit)
    except (AssertionError, OSError, subprocess.SubprocessError,
            UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error)},
                         sort_keys=True), file=sys.stderr)
        return 1
    if args.self_test:
        print(json.dumps(report, sort_keys=True))
    else:
        print(json.dumps({
            "schema": report["schema"], "status": "PASS",
            "roles": {name: {key: value for key, value in item.items() if key != "records"}
                      for name, item in report["roles"].items()},
            "evidence": EVIDENCE_PATH.relative_to(ROOT).as_posix(),
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
