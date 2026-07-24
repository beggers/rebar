#!/usr/bin/env python3
"""Audit independently rebuilt regex engines and genuine match representations."""

from __future__ import annotations

import sys

if __name__ == "__main__":
    import os as _v7_entry_os
    from pathlib import Path as _V7EntryPath

    _v7_entry_root = str(_V7EntryPath(__file__).resolve().parent.parent)
    _v7_entry = (
        "import sys;sys.path.insert(0,sys.argv[1]);"
        "from tools.postfinal_from_scratch_audit_v7 import main;"
        "raise SystemExit(main(sys.argv[2:]))"
    )
    _v7_entry_os.execv(
        sys.executable,
        [sys.executable, "-I", "-B", "-c", _v7_entry,
         _v7_entry_root, *sys.argv[1:]],
    )

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v6 as source_v6


core = source_v6.core
SCHEMA = "rebar-postfinal-from-scratch-audit-v7"
SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v7.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
REPORT_PATH = ROOT / REPORT_RELATIVE
MAX_SOURCE_BYTES = source_v6.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = source_v6.MAX_REPORT_BYTES
MAX_WORKER_BYTES = source_v6.MAX_WORKER_BYTES
CORE_FAMILIES = source_v6.CORE_FAMILIES
NATIVE_LOADER_ALIASES = source_v6.NATIVE_LOADER_ALIASES
OWNED_NATIVE_MODULES = dict(source_v6.OWNED_NATIVE_MODULES)

V6_BASE_SOURCE_SHA256 = (
    "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f"
)
V6_BASE_REPORT_SHA256 = (
    "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb"
)
V6_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v6.py"
V6_STRICT_SOURCE_SHA256 = (
    "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649"
)
V6_STRICT_REPORT_RELATIVE = (
    "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json"
)
V6_STRICT_REPORT_SHA256 = (
    "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f"
)
OFFICIAL_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v2.py"
OFFICIAL_SOURCE_SHA256 = (
    "e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1"
)
OFFICIAL_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md"
OFFICIAL_PROTOCOL_SHA256 = (
    "a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5"
)
OFFICIAL_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json"
)
OFFICIAL_FAILURE_SHA256: str | None = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)
OFFICIAL_FAILURE_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_v2_failure.py"
OFFICIAL_FAILURE_SOURCE_SHA256 = (
    "42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5"
)
OFFICIAL_FAILURE_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md"
)
OFFICIAL_FAILURE_PROTOCOL_SHA256 = (
    "75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818"
)

STAGE12_SOURCE_RELATIVE = "tools/python_re_generic_alias_public_oracle_stage12.py"
STAGE12_SOURCE_SHA256 = (
    "361e080a0475f5ee7fd7d5da0386a4e2443775069aadca84e053bac357554aaa"
)
STAGE12_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md"
)
STAGE12_PROTOCOL_SHA256 = (
    "1cec5253aabb5464c16d0de461bdd11463ddf11fafea9da6347b8a0af3d30cb1"
)
STAGE12_SELF_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json"
)
STAGE12_SELF_SHA256 = (
    "b235bd68afbbfa9b8e7e046d0e007385617c976c6e5a5f5b614cc7d93b891aff"
)
STAGE12_ALL_RELATIVE = (
    "candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json"
)
STAGE12_ALL_SHA256 = (
    "6b0188e22f80a64e79252660d6b308d16d7a38ec01c45013bf67484b8d49be8c"
)

FROZEN_HISTORICAL_INPUTS = {
    source_v6.SOURCE_RELATIVE: V6_BASE_SOURCE_SHA256,
    source_v6.REPORT_RELATIVE: V6_BASE_REPORT_SHA256,
    V6_STRICT_SOURCE_RELATIVE: V6_STRICT_SOURCE_SHA256,
    V6_STRICT_REPORT_RELATIVE: V6_STRICT_REPORT_SHA256,
    OFFICIAL_SOURCE_RELATIVE: OFFICIAL_SOURCE_SHA256,
    OFFICIAL_PROTOCOL_RELATIVE: OFFICIAL_PROTOCOL_SHA256,
    OFFICIAL_FAILURE_SOURCE_RELATIVE: OFFICIAL_FAILURE_SOURCE_SHA256,
    OFFICIAL_FAILURE_PROTOCOL_RELATIVE: OFFICIAL_FAILURE_PROTOCOL_SHA256,
    STAGE12_SOURCE_RELATIVE: STAGE12_SOURCE_SHA256,
    STAGE12_PROTOCOL_RELATIVE: STAGE12_PROTOCOL_SHA256,
    STAGE12_SELF_RELATIVE: STAGE12_SELF_SHA256,
    STAGE12_ALL_RELATIVE: STAGE12_ALL_SHA256,
}


class AuditV7Error(source_v6.AuditV6Error):
    """A repaired matching engine, genuine representation, or history failed."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV7Error(message)


def _exact_relative(value: Any, allowed: Mapping[str, Any]) -> str:
    require(type(value) is str, "a source-audit path is not exact text")
    parsed = PurePosixPath(value)
    require(
        not parsed.is_absolute()
        and ".." not in parsed.parts
        and "\\" not in value
        and "\x00" not in value
        and str(parsed) == value
        and value in allowed,
        "refusing an unapproved, traversing, or historical V7 output path",
    )
    return value


def destination_name(value: Any) -> str:
    return _exact_relative(value, {REPORT_RELATIVE: True})


def _require_published_failure() -> str:
    require(
        isinstance(OFFICIAL_FAILURE_SHA256, str)
        and core.valid_sha256(OFFICIAL_FAILURE_SHA256),
        "the genuine 145-of-146 Rust official failure is not yet published",
    )
    return OFFICIAL_FAILURE_SHA256


def _read_exact(relative: str, expected: str,
                *, failure: bool = False) -> tuple[bytes, str]:
    if failure:
        _exact_relative(relative, {OFFICIAL_FAILURE_RELATIVE: True})
    else:
        _exact_relative(relative, FROZEN_HISTORICAL_INPUTS)
        require(FROZEN_HISTORICAL_INPUTS[relative] == expected,
                "an immutable historical source fingerprint was substituted")
    require(core.valid_sha256(expected), "a genuine source fingerprint is missing")
    path = ROOT / relative
    require(not path.is_symlink(), "a historical source or report is a symlink")
    observed, payload = core.bounded_file(
        path,
        maximum=MAX_REPORT_BYTES if relative.endswith(".json") else MAX_SOURCE_BYTES,
        label="exact V7 preserved public source: " + relative,
        keep=True,
    )
    require(observed == expected and type(payload) is bytes,
            "a genuinely preserved public source or result changed: " + relative)
    return payload, observed


def _validate_historical_failure(document: Any) -> dict[str, Any]:
    require(isinstance(document, dict),
            "the real first official Rust representation failure is absent")
    require(
        document.get("schema")
        == "rebar-postfinal-cpython-public-locale-v2-rust-failure-v1"
        and document.get("status") == "FAIL"
        and document.get("result") == "FAIL"
        and document.get("python") == "3.14.6"
        and document.get("source_path") == OFFICIAL_FAILURE_SOURCE_RELATIVE
        and document.get("source_sha256") == OFFICIAL_FAILURE_SOURCE_SHA256
        and document.get("protocol_path") == OFFICIAL_FAILURE_PROTOCOL_RELATIVE
        and document.get("protocol_sha256") == OFFICIAL_FAILURE_PROTOCOL_SHA256
        and document.get("failed_role") == "rust"
        and document.get("failed_module") == "candidates.rust_candidate"
        and document.get("failed_method") == "ReTests.test_match_repr"
        and document.get("official_v2_status") == "FAIL"
        and document.get("official_v2_complete_result_created") is False
        and document.get("official_v2_complete_result_path")
        == "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json"
        and document.get("holdout_accessed") is False
        and document.get("timing_performed") is False
        and document.get("performance") == "NOT MEASURED",
        "the genuine failed official Python run was fabricated or rewritten",
    )
    roles = document.get("roles")
    require(isinstance(roles, dict)
            and set(roles) == {"re", "rust", "vm", "zig"},
            "the original failed experiment omitted or invented an official role")
    baseline = roles["re"]
    require(
        isinstance(baseline, dict)
        and baseline.get("execution") == "EXECUTED"
        and baseline.get("status") == "NOT RECORDED"
        and baseline.get("individual_method_records_preserved") is False
        and baseline.get("inferred_pass") is False,
        "an unrecorded original Python baseline was invented or hidden",
    )
    rust = roles["rust"]
    require(
        isinstance(rust, dict)
        and rust.get("execution") == "EXECUTED"
        and rust.get("status") == "FAIL"
        and rust.get("module") == "candidates.rust_candidate"
        and rust.get("methods") == 146
        and rust.get("passed") == 145
        and rust.get("failed") == 1
        and rust.get("skipped") == 0
        and rust.get("crashes") == 0
        and rust.get("timeouts") == 0
        and rust.get("failed_method") == "ReTests.test_match_repr"
        and rust.get("individual_method_records_preserved") is False,
        "the genuinely observed 145-of-146 Rust failure was changed",
    )
    for role in ("vm", "zig"):
        pending = roles[role]
        require(
            isinstance(pending, dict)
            and pending.get("execution") == "NOT RUN"
            and pending.get("status") == "NOT RUN"
            and pending.get("individual_method_records_preserved") is False
            and pending.get("inferred_pass") is False,
            "the failed first run falsely claimed an unexecuted candidate: " + role,
        )
    provenance = document.get("actual_current_provenance")
    require(
        isinstance(provenance, dict)
        and provenance.get("official_source_path") == OFFICIAL_SOURCE_RELATIVE
        and provenance.get("official_source_sha256") == OFFICIAL_SOURCE_SHA256
        and provenance.get("official_protocol_path") == OFFICIAL_PROTOCOL_RELATIVE
        and provenance.get("official_protocol_sha256") == OFFICIAL_PROTOCOL_SHA256
        and provenance.get("source_audit_source_path") == source_v6.SOURCE_RELATIVE
        and provenance.get("source_audit_source_sha256") == V6_BASE_SOURCE_SHA256
        and provenance.get("source_audit_report_path") == source_v6.REPORT_RELATIVE
        and provenance.get("source_audit_report_sha256") == V6_BASE_REPORT_SHA256
        and provenance.get("strict_audit_source_path") == V6_STRICT_SOURCE_RELATIVE
        and provenance.get("strict_audit_source_sha256") == V6_STRICT_SOURCE_SHA256
        and provenance.get("strict_audit_report_path") == V6_STRICT_REPORT_RELATIVE
        and provenance.get("strict_audit_report_sha256") == V6_STRICT_REPORT_SHA256
        and provenance.get("selected_methods") == 146
        and provenance.get("corpus_cases") == 403
        and provenance.get("named_waiver_count") == 8
        and provenance.get("verified_owned_source_count") == 12
        and provenance.get("verified_native_binary_count") == 5
        and provenance.get("verified_standard_pickle_count") == 48,
        "the real first failed run was detached from its frozen current sources",
    )
    aliases = provenance.get("stage12")
    require(
        isinstance(aliases, dict)
        and aliases.get("source_path") == STAGE12_SOURCE_RELATIVE
        and aliases.get("source_sha256") == STAGE12_SOURCE_SHA256
        and aliases.get("protocol_path") == STAGE12_PROTOCOL_RELATIVE
        and aliases.get("protocol_sha256") == STAGE12_PROTOCOL_SHA256
        and aliases.get("self_oracle_path") == STAGE12_SELF_RELATIVE
        and aliases.get("self_oracle_sha256") == STAGE12_SELF_SHA256
        and aliases.get("all_candidates_path") == STAGE12_ALL_RELATIVE
        and aliases.get("all_candidates_sha256") == STAGE12_ALL_SHA256
        and aliases.get("cases") == 128
        and aliases.get("stdlib_checks") == 256
        and aliases.get("candidate_checks") == 384
        and aliases.get("completed_candidates") == list(CORE_FAMILIES),
        "the failed official run concealed its actual historical generic-alias proof",
    )
    first = document.get("first_run")
    require(
        isinstance(first, dict)
        and first.get("controller") == OFFICIAL_SOURCE_RELATIVE
        and first.get("exit_code") == 1
        and first.get("rerun") is False,
        "the recorder did not preserve the exact original failed execution",
    )
    first_failure = first.get("failure")
    require(
        isinstance(first_failure, dict)
        and first_failure.get("failed_role") == "rust"
        and first_failure.get("failed_module") == "candidates.rust_candidate"
        and first_failure.get("failed_method") == "ReTests.test_match_repr"
        and first_failure.get("exception_type") == "AssertionError"
        and first_failure.get("failure_rerun") is False
        and first_failure.get("original_method_records_preserved") is False
        and first_failure.get("raw_stream_bytes") == "NOT RECORDED"
        and first_failure.get("raw_stream_sha256") == "NOT RECORDED"
        and first_failure.get("actual_match_repr")
        == "<re.Match object; span=(1, 12), match='abracadabra'>",
        "the genuine first failure invented raw output or changed its actual mismatch",
    )
    scope = document.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("actual_first_failure_preserved") is True
        and scope.get("baseline_method_records_fabricated") is False
        and scope.get("failure_reproduced_or_rerun") is False
        and scope.get("raw_controller_stream_recorded") is False
        and scope.get("unexecuted_candidate_results_invented") is False
        and scope.get("candidate_imports") == 0
        and scope.get("candidate_processes") == 0
        and scope.get("official_test_processes_started") == 0
        and scope.get("locale_compilations") == 0
        and scope.get("benchmark_or_timing_executed") is False
        and scope.get("holdout_access") is False
        and scope.get("performance_fixture_access") is False,
        "the genuine official failure recorder fabricated, reran, or measured work",
    )
    return document


REPR_WORKER_BOOTSTRAP = r'''
import importlib
import json
import sys
from pathlib import Path

if len(sys.argv) != 4:
    raise RuntimeError("the match-representation worker arguments are not exact")
root = Path(sys.argv[1]).resolve(strict=True)
role = sys.argv[2]
expected_native = json.loads(sys.argv[3])
if role not in ("rust", "vm", "zig"):
    raise RuntimeError("a match representation worker requested a foreign family")
if not isinstance(expected_native, dict) or not expected_native:
    raise RuntimeError("a match representation worker omitted its owned native engine")
sys.path.insert(0, str(root))
from tools import python_re_universal_public_oracle_stage07 as stage07
aliases = (
    "ctypes.CDLL", "ctypes.cdll.LoadLibrary", "ctypes.cdll._dlltype",
    "ctypes._dlopen", "_ctypes.dlopen",
)
if tuple(stage07.NATIVE_LOADER_ALIASES) != aliases:
    raise RuntimeError("a genuine match worker changed its frozen loader guards")
guard = stage07._install_family_guard(role, expected_native)
for key in (
    "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
    "third_party_regex_blocked", "cross_family_blocked",
    "foreign_dynamic_libraries_blocked",
):
    if guard.get(key) is not True:
        raise RuntimeError("a genuine match worker weakened: " + key)
if guard.get("family") != role:
    raise RuntimeError("a representation worker substituted its native family")
if guard.get("native_loader_aliases_blocked") != list(aliases):
    raise RuntimeError("a representation worker substituted a dynamic loader")
name = "candidates." + role + "_candidate"
module = importlib.import_module(name)
bridge_name = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}[role]
bridge = importlib.import_module(bridge_name)
if module.Match is not bridge.Match:
    raise RuntimeError("the candidate match type is not its real owned native type")
match_type = module.Match
if (
    not isinstance(match_type, type)
    or match_type.__module__ != bridge_name
    or match_type.__name__ != "Match"
    or match_type.__qualname__ != "Match"
    or getattr(importlib.import_module(match_type.__module__), "Match", None)
    is not match_type
):
    raise RuntimeError("the genuine matching type is not owned and importable")
live = {
    item for item, value in sys.modules.items()
    if item.startswith("candidates.")
    and value is not None
    and not isinstance(value, stage07._ForbiddenRegexModule)
}
if live != {name, bridge_name}:
    raise RuntimeError("a genuine representation loaded a foreign candidate")
mapped = stage07._verify_family_native_mappings(
    role, {"native_sha256_by_family": {role: expected_native}},
)
if mapped != expected_native:
    raise RuntimeError("the genuine match process mapped a substituted native")
records = []
for kind, pattern, subject, expected_group in (
    ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
    ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
):
    compiled = module.compile(pattern)
    observed = compiled.search(subject)
    if observed is None or type(observed) is not match_type:
        raise RuntimeError("a genuine regular-expression matcher was not executed")
    if observed.span() != (1, 12) or observed.group(0) != expected_group:
        raise RuntimeError("the owned native match returned the wrong real result")
    representation = repr(observed)
    expected = (
        "<" + match_type.__module__ + "." + match_type.__qualname__
        + " object; span=" + repr(observed.span())
        + ", match=" + repr(observed.group(0)) + ">"
    )
    if representation != expected:
        raise RuntimeError("the genuine native match representation is incorrect")
    if representation.startswith("<re.Match"):
        raise RuntimeError("the owned native match fabricated a standard Python owner")
    records.append({
        "id": role + ":match-repr:" + kind,
        "kind": kind, "span": [1, 12],
        "pattern_representation": repr(pattern),
        "subject_representation": repr(subject),
        "matched_representation": repr(observed.group(0)),
        "match_module": match_type.__module__,
        "match_qualified_name": match_type.__qualname__,
        "actual_repr": representation,
        "expected_repr": expected,
        "native_type_identity": True,
        "genuine_matching_executed": True,
        "passed": True,
    })
after = {
    item for item, value in sys.modules.items()
    if item.startswith("candidates.")
    and value is not None
    and not isinstance(value, stage07._ForbiddenRegexModule)
}
if after != live:
    raise RuntimeError("genuine matching imported a foreign native candidate")
print(json.dumps({
    "schema": "rebar-postfinal-from-scratch-audit-v7-match-repr-worker",
    "status": "PASS", "result": "PASS", "passed": True,
    "family": role, "candidate_module": name,
    "native_bridge_module": bridge_name,
    "native_binary_sha256": mapped,
    "guard": guard,
    "loaded_candidate_modules": sorted(live),
    "records": records, "match_repr_checks": 2,
    "genuine_matching_executed": True,
    "external_regex_packages": 0,
    "benchmark_or_timing_executed": False,
    "fixture_accessed": False,
}, sort_keys=True, ensure_ascii=True, separators=(",", ":")))
'''


def _validate_repr(document: Any, family: str,
                   expected_native: Mapping[str, str]) -> dict[str, Any]:
    bridge = OWNED_NATIVE_MODULES[family]
    candidate = "candidates." + family + "_candidate"
    require(
        isinstance(document, dict)
        and document.get("schema") == SCHEMA + "-match-repr-worker"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True
        and document.get("family") == family
        and document.get("candidate_module") == candidate
        and document.get("native_bridge_module") == bridge
        and document.get("native_binary_sha256") == dict(expected_native)
        and document.get("match_repr_checks") == 2
        and document.get("genuine_matching_executed") is True
        and document.get("external_regex_packages") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("fixture_accessed") is False
        and document.get("loaded_candidate_modules")
        == sorted({candidate, bridge}),
        "a genuine native matching and representation worker failed: " + family,
    )
    guard = document.get("guard")
    require(
        isinstance(guard, dict)
        and guard.get("family") == family
        and guard.get("native_loader_aliases_blocked")
        == list(NATIVE_LOADER_ALIASES)
        and all(guard.get(key) is True for key in (
            "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
            "third_party_regex_blocked", "cross_family_blocked",
            "foreign_dynamic_libraries_blocked",
        )),
        "a real match representation weakened an independence guard: " + family,
    )
    records = document.get("records")
    require(isinstance(records, list) and len(records) == 2,
            "a representation worker omitted a true str or bytes match")
    for index, (kind, pattern, subject, matched) in enumerate((
        ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
        ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
    )):
        row = records[index]
        expected = (
            "<" + bridge + ".Match object; span=(1, 12), match="
            + repr(matched) + ">"
        )
        require(
            isinstance(row, dict)
            and row.get("id") == family + ":match-repr:" + kind
            and row.get("kind") == kind
            and row.get("span") == [1, 12]
            and row.get("pattern_representation") == repr(pattern)
            and row.get("subject_representation") == repr(subject)
            and row.get("matched_representation") == repr(matched)
            and row.get("match_module") == bridge
            and row.get("match_qualified_name") == "Match"
            and row.get("actual_repr") == expected
            and row.get("expected_repr") == expected
            and row.get("native_type_identity") is True
            and row.get("genuine_matching_executed") is True
            and row.get("passed") is True,
            "a true match representation was forged or misattributed: " + family,
        )
    return document


def _run_repr_worker(family: str,
                     natives: dict[str, str]) -> dict[str, Any]:
    require(family in CORE_FAMILIES and isinstance(natives, dict) and bool(natives),
            "a genuine representation worker requires an audited native family")
    payload = json.dumps(natives, sort_keys=True, ensure_ascii=True,
                         separators=(",", ":"))
    require(len(payload.encode("ascii")) <= 16 * 1024,
            "a representation worker exceeded its safe argument boundary")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    child = subprocess.run(
        [sys.executable, "-I", "-B", "-c", REPR_WORKER_BOOTSTRAP,
         str(ROOT), family, payload],
        capture_output=True, check=False, timeout=45, env=environment,
    )
    require(child.returncode == 0 and not child.stderr
            and 0 < len(child.stdout) <= MAX_WORKER_BYTES,
            "a guarded genuine native match worker failed: " + family)
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise AuditV7Error("a native match worker returned unsafe evidence") from error
    return _validate_repr(document, family, natives)


def _synthetic_repr(family: str) -> tuple[dict[str, Any], dict[str, str]]:
    bridge = OWNED_NATIVE_MODULES[family]
    candidate = "candidates." + family + "_candidate"
    native = {
        path: "a" * 64
        for path in source_v6.OWNED_NATIVE_PATHS[family].values()
    }
    rows = []
    for kind, pattern, subject, matched in (
        ("str", r"(.+)(.*?)\1", "[abracadabra]", "abracadabra"),
        ("bytes", br"(.+)(.*?)\1", b"[abracadabra]", b"abracadabra"),
    ):
        representation = (
            "<" + bridge + ".Match object; span=(1, 12), match="
            + repr(matched) + ">"
        )
        rows.append({
            "id": family + ":match-repr:" + kind,
            "kind": kind, "span": [1, 12],
            "pattern_representation": repr(pattern),
            "subject_representation": repr(subject),
            "matched_representation": repr(matched),
            "match_module": bridge, "match_qualified_name": "Match",
            "actual_repr": representation, "expected_repr": representation,
            "native_type_identity": True,
            "genuine_matching_executed": True, "passed": True,
        })
    return {
        "schema": SCHEMA + "-match-repr-worker",
        "status": "PASS", "result": "PASS", "passed": True,
        "family": family, "candidate_module": candidate,
        "native_bridge_module": bridge,
        "native_binary_sha256": native,
        "guard": {
            "enabled": True, "family": family,
            "stdlib_re_blocked": True, "cpython_sre_blocked": True,
            "third_party_regex_blocked": True,
            "cross_family_blocked": True,
            "foreign_dynamic_libraries_blocked": True,
            "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
        },
        "loaded_candidate_modules": sorted({candidate, bridge}),
        "records": rows, "match_repr_checks": 2,
        "genuine_matching_executed": True,
        "external_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "fixture_accessed": False,
    }, native


def _synthetic_failure() -> dict[str, Any]:
    return {
        "schema": "rebar-postfinal-cpython-public-locale-v2-rust-failure-v1",
        "status": "FAIL", "result": "FAIL", "python": "3.14.6",
        "source_path": OFFICIAL_FAILURE_SOURCE_RELATIVE,
        "source_sha256": OFFICIAL_FAILURE_SOURCE_SHA256,
        "protocol_path": OFFICIAL_FAILURE_PROTOCOL_RELATIVE,
        "protocol_sha256": OFFICIAL_FAILURE_PROTOCOL_SHA256,
        "failed_role": "rust",
        "failed_module": "candidates.rust_candidate",
        "failed_method": "ReTests.test_match_repr",
        "official_v2_status": "FAIL",
        "official_v2_complete_result_created": False,
        "official_v2_complete_result_path":
            "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-all.json",
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "roles": {
            "re": {
                "execution": "EXECUTED", "status": "NOT RECORDED",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
            "rust": {
                "execution": "EXECUTED", "status": "FAIL",
                "module": "candidates.rust_candidate",
                "methods": 146, "passed": 145,
                "failed": 1, "skipped": 0,
                "crashes": 0, "timeouts": 0,
                "failed_method": "ReTests.test_match_repr",
                "individual_method_records_preserved": False,
            },
            "vm": {
                "execution": "NOT RUN", "status": "NOT RUN",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
            "zig": {
                "execution": "NOT RUN", "status": "NOT RUN",
                "individual_method_records_preserved": False,
                "inferred_pass": False,
            },
        },
        "actual_current_provenance": {
            "official_source_path": OFFICIAL_SOURCE_RELATIVE,
            "official_source_sha256": OFFICIAL_SOURCE_SHA256,
            "official_protocol_path": OFFICIAL_PROTOCOL_RELATIVE,
            "official_protocol_sha256": OFFICIAL_PROTOCOL_SHA256,
            "source_audit_source_path": source_v6.SOURCE_RELATIVE,
            "source_audit_source_sha256": V6_BASE_SOURCE_SHA256,
            "source_audit_report_path": source_v6.REPORT_RELATIVE,
            "source_audit_report_sha256": V6_BASE_REPORT_SHA256,
            "strict_audit_source_path": V6_STRICT_SOURCE_RELATIVE,
            "strict_audit_source_sha256": V6_STRICT_SOURCE_SHA256,
            "strict_audit_report_path": V6_STRICT_REPORT_RELATIVE,
            "strict_audit_report_sha256": V6_STRICT_REPORT_SHA256,
            "selected_methods": 146, "corpus_cases": 403,
            "named_waiver_count": 8,
            "verified_owned_source_count": 12,
            "verified_native_binary_count": 5,
            "verified_standard_pickle_count": 48,
            "stage12": {
                "source_path": STAGE12_SOURCE_RELATIVE,
                "source_sha256": STAGE12_SOURCE_SHA256,
                "protocol_path": STAGE12_PROTOCOL_RELATIVE,
                "protocol_sha256": STAGE12_PROTOCOL_SHA256,
                "self_oracle_path": STAGE12_SELF_RELATIVE,
                "self_oracle_sha256": STAGE12_SELF_SHA256,
                "all_candidates_path": STAGE12_ALL_RELATIVE,
                "all_candidates_sha256": STAGE12_ALL_SHA256,
                "cases": 128, "stdlib_checks": 256,
                "candidate_checks": 384,
                "completed_candidates": list(CORE_FAMILIES),
            },
        },
        "first_run": {
            "controller": OFFICIAL_SOURCE_RELATIVE,
            "exit_code": 1, "rerun": False,
            "failure": {
                "failed_role": "rust",
                "failed_module": "candidates.rust_candidate",
                "failed_method": "ReTests.test_match_repr",
                "exception_type": "AssertionError",
                "failure_rerun": False,
                "original_method_records_preserved": False,
                "raw_stream_bytes": "NOT RECORDED",
                "raw_stream_sha256": "NOT RECORDED",
                "actual_match_repr":
                    "<re.Match object; span=(1, 12), match='abracadabra'>",
            },
        },
        "scope": {
            "actual_first_failure_preserved": True,
            "baseline_method_records_fabricated": False,
            "failure_reproduced_or_rerun": False,
            "raw_controller_stream_recorded": False,
            "unexecuted_candidate_results_invented": False,
            "candidate_imports": 0, "candidate_processes": 0,
            "official_test_processes_started": 0,
            "locale_compilations": 0,
            "benchmark_or_timing_executed": False,
            "holdout_access": False,
            "performance_fixture_access": False,
        },
    }


def self_test() -> dict[str, Any]:
    core.ensure_candidate_free()
    inherited = source_v6.self_test()
    require(inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 324
            and inherited.get("candidate_imports") == 0
            and inherited.get("file_reads") == 0
            and inherited.get("file_writes") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("clock_samples") == 0,
            "the full hardened version-six source controls failed")
    effects = core.previous.BlockSelfTestEffects()
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: Any) -> None:
        checks.append({"name": name, "passed": bool(passed)})

    def reject(name: str, action: Any) -> None:
        try:
            action()
        except (
            source_v6.AuditV6Error, TypeError, ValueError,
            KeyError, UnicodeError, OSError,
        ):
            check(name, True)
        else:
            check(name, False)

    with effects:
        for item in inherited["checks"]:
            check("v6:" + item["name"], item["passed"] is True)
        check("preserve-all-324-source-bound-v6-safeguards",
              inherited["check_count"] >= 324)
        check("preserve-three-genuine-native-implementation-families",
              CORE_FAMILIES == ("rust", "vm", "zig"))
        check("preserve-twelve-current-native-source-paths",
              sum(map(len, source_v6.OWNED_SOURCE_PATHS.values())) == 12)
        check("preserve-five-genuinely-owned-native-roles",
              sum(map(len, source_v6.OWNED_NATIVE_PATHS.values())) == 5)
        check("retain-five-exact-foreign-dynamic-loader-denials",
              NATIVE_LOADER_ALIASES == (
                  "ctypes.CDLL", "ctypes.cdll.LoadLibrary",
                  "ctypes.cdll._dlltype", "ctypes._dlopen", "_ctypes.dlopen",
              ))
        check("pin-twelve-immutable-public-v6-official-and-stage12-artifacts",
              len(FROZEN_HISTORICAL_INPUTS) == 12
              and all(core.valid_sha256(value)
                      for value in FROZEN_HISTORICAL_INPUTS.values()))
        if OFFICIAL_FAILURE_SHA256 is None:
            reject("fail-closed-before-the-real-145-of-146-failure-is-published",
                   _require_published_failure)
        else:
            check("require-a-real-published-official-failure-fingerprint",
                  core.valid_sha256(OFFICIAL_FAILURE_SHA256)
                  and _require_published_failure() == OFFICIAL_FAILURE_SHA256)
        failure = _synthetic_failure()
        check("accept-only-an-explicitly-failed-official-rust-experiment",
              _validate_historical_failure(failure) is failure)
        for key, poisoned in (
            ("status", "PASS"), ("result", "PASS"),
            ("python", "3.13.0"),
            ("source_path", OFFICIAL_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", OFFICIAL_PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("failed_role", "vm"),
            ("failed_module", "candidates.vm_candidate"),
            ("failed_method", "ExternalTests.test_re_tests"),
            ("official_v2_status", "PASS"),
            ("official_v2_complete_result_created", True),
            ("holdout_accessed", True),
            ("timing_performed", True),
        ):
            reject(
                "reject-a-forged-historical-rust-failure:" + key,
                lambda name=key, value=poisoned:
                _validate_historical_failure({**failure, name: value}),
            )
        for role in ("re", "rust", "vm", "zig"):
            changed_roles = {
                name: dict(value) for name, value in failure["roles"].items()
            }
            changed_roles[role]["status"] = "PASS"
            reject(
                "reject-an-invented-or-concealed-official-role:" + role,
                lambda roles=changed_roles:
                _validate_historical_failure({**failure, "roles": roles}),
            )
        for key, poisoned in (
            ("actual_first_failure_preserved", False),
            ("baseline_method_records_fabricated", True),
            ("failure_reproduced_or_rerun", True),
            ("raw_controller_stream_recorded", True),
            ("unexecuted_candidate_results_invented", True),
            ("candidate_imports", 1),
            ("official_test_processes_started", 1),
            ("benchmark_or_timing_executed", True),
        ):
            poisoned_scope = {**failure["scope"], key: poisoned}
            reject(
                "reject-fabricated-official-failure-scope:" + key,
                lambda scope=poisoned_scope:
                _validate_historical_failure({**failure, "scope": scope}),
            )
        check("admit-only-the-new-exclusive-version-seven-proof",
              destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, target in (
            ("historical-v6", source_v6.REPORT_RELATIVE),
            ("historical-strict-v6", V6_STRICT_REPORT_RELATIVE),
            ("historical-official-failure", OFFICIAL_FAILURE_RELATIVE),
            ("absolute", "/" + REPORT_RELATIVE),
            ("traversal", "candidates/audits/../FOREIGN.json"),
            ("noncanonical", "candidates//audits/FOREIGN.json"),
            ("nul", REPORT_RELATIVE + "\x00"),
            ("nontext", 7),
        ):
            reject("reject-unsafe-exclusive-destination:" + label,
                   lambda value=target: destination_name(value))
        for family in CORE_FAMILIES:
            synthetic, native = _synthetic_repr(family)
            check("accept-real-owned-str-and-bytes-match-shape:" + family,
                  _validate_repr(synthetic, family, native) is synthetic)
            for key, poisoned in (
                ("status", "FAIL"),
                ("passed", False),
                ("family", "foreign"),
                ("candidate_module", "candidates.foreign_candidate"),
                ("native_bridge_module", "re"),
                ("native_binary_sha256", {}),
                ("match_repr_checks", 1),
                ("genuine_matching_executed", False),
                ("external_regex_packages", 1),
                ("benchmark_or_timing_executed", True),
                ("fixture_accessed", True),
                ("records", synthetic["records"][:-1]),
                ("loaded_candidate_modules", []),
            ):
                reject(
                    "reject-forged-real-match-worker:" + family + ":" + key,
                    lambda name=key, value=poisoned, item=synthetic, owned=native:
                    _validate_repr({**item, name: value}, family, owned),
                )
            for key, poisoned in (
                ("id", family + ":match-repr:forged"),
                ("kind", "bytes"),
                ("span", [0, 1]),
                ("pattern_representation", "'a'"),
                ("subject_representation", "'a'"),
                ("matched_representation", "'a'"),
                ("match_module", "re"),
                ("match_qualified_name", "Foreign"),
                ("actual_repr", "<re.Match object; span=(1, 12), match='abracadabra'>"),
                ("expected_repr", "<re.Match object; span=(1, 12), match='abracadabra'>"),
                ("native_type_identity", False),
                ("genuine_matching_executed", False),
                ("passed", False),
            ):
                records = [dict(row) for row in synthetic["records"]]
                records[0][key] = poisoned
                reject(
                    "reject-false-native-match-representation:"
                    + family + ":" + key,
                    lambda rows=records, item=synthetic, owned=native:
                    _validate_repr({**item, "records": rows}, family, owned),
                )
            swapped = [dict(row) for row in reversed(synthetic["records"])]
            reject(
                "reject-swapped-str-and-bytes-match-records:" + family,
                lambda rows=swapped, item=synthetic, owned=native:
                _validate_repr({**item, "records": rows}, family, owned),
            )
            for name, aliases in (
                ("missing", list(NATIVE_LOADER_ALIASES[:-1])),
                ("swapped", list(reversed(NATIVE_LOADER_ALIASES))),
                ("duplicate", [*NATIVE_LOADER_ALIASES[:-1],
                                 NATIVE_LOADER_ALIASES[0]]),
                ("invented", ["a", "b", "c", "d", "e"]),
            ):
                poisoned = {**synthetic["guard"],
                            "native_loader_aliases_blocked": aliases}
                reject(
                    "reject-fake-match-native-loaders:" + family + ":" + name,
                    lambda guard=poisoned, item=synthetic, owned=native:
                    _validate_repr({**item, "guard": guard}, family, owned),
                )
        core.ensure_candidate_free()
    check("zero-candidate-source-or-evidence-file-reads",
          effects.counts["files"] == 0)
    check("zero-candidate-source-or-evidence-file-writes",
          effects.counts["files"] == 0)
    check("zero-native-repr-worker-or-subprocess-starts",
          effects.counts["processes"] == 0)
    check("zero-timing-clock-samples", effects.counts["clocks"] == 0)
    check("zero-production-entropy-draws", effects.counts["entropy"] == 0)
    names = [item["name"] for item in checks]
    failed = sorted(item["name"] for item in checks
                    if item["passed"] is not True)
    if len(names) != len(set(names)):
        failed.append("duplicate-version-seven-synthetic-source-control")
    core.ensure_candidate_free()
    return {
        "schema": SCHEMA + "-self-test",
        "status": "PASS" if not failed else "FAIL",
        "result": "PASS" if not failed else "FAIL",
        "passed": not failed, "checks": checks,
        "check_count": len(checks), "failed": failed,
        "inherited_v6_control_count": inherited["check_count"],
        "fixture_storage": "in-memory only",
        "candidate_imported": False, "candidate_imports": 0,
        "file_reads": effects.counts["files"], "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "official_failure_published": OFFICIAL_FAILURE_SHA256 is not None,
        "standard_pickle_checks_required": 48,
        "native_match_repr_checks_required": 6,
        "holdout_or_case_fixture_access": False,
        "benchmark_or_timing_executed": False,
        "production_cases_materialized": 0,
        "report_written": False,
    }


def audit() -> dict[str, Any]:
    runtime = core.verify_production_runtime()
    core.ensure_candidate_free()
    failure_sha = _require_published_failure()
    preserved: dict[str, str] = {}
    records: dict[str, dict[str, Any]] = {}
    for relative, expected in FROZEN_HISTORICAL_INPUTS.items():
        payload, observed = _read_exact(relative, expected)
        preserved[relative] = observed
        if relative.endswith(".json"):
            records[relative] = core.decode_report(payload, label=relative)
    raw_failure, observed_failure = _read_exact(
        OFFICIAL_FAILURE_RELATIVE, failure_sha, failure=True,
    )
    actual_failure = core.decode_report(raw_failure, label=OFFICIAL_FAILURE_RELATIVE)
    _validate_historical_failure(actual_failure)
    require(observed_failure == failure_sha,
            "the genuine first Rust official failure was substituted")
    preserved[OFFICIAL_FAILURE_RELATIVE] = observed_failure

    old_base = records[source_v6.REPORT_RELATIVE]
    old_strict = records[V6_STRICT_REPORT_RELATIVE]
    require(
        isinstance(old_base, dict)
        and old_base.get("schema") == source_v6.SCHEMA
        and old_base.get("status") == "PASS"
        and old_base.get("audit_source_sha256") == V6_BASE_SOURCE_SHA256
        and isinstance(old_strict, dict)
        and old_strict.get("schema")
        == "rebar-postfinal-no-delegation-audit-v6"
        and old_strict.get("status") == "PASS"
        and old_strict.get("audit_source_sha256") == V6_STRICT_SOURCE_SHA256
        and old_strict.get("base_audit_report_sha256") == V6_BASE_REPORT_SHA256,
        "the actual version-six audits were hidden or represented as new proofs",
    )
    alias_reference = records[STAGE12_SELF_RELATIVE]
    alias_candidates = records[STAGE12_ALL_RELATIVE]
    require(
        isinstance(alias_reference, dict)
        and alias_reference.get("status") == "PASS"
        and alias_reference.get("source_sha256") == STAGE12_SOURCE_SHA256
        and alias_reference.get("cases") == 128
        and isinstance(alias_candidates, dict)
        and alias_candidates.get("status") == "PASS"
        and alias_candidates.get("source_sha256") == STAGE12_SOURCE_SHA256
        and alias_candidates.get("candidate_checks") == 384
        and alias_candidates.get("completed_candidates") == list(CORE_FAMILIES),
        "the historical genuine repaired generic-alias experiment was modified",
    )
    controls = self_test()
    require(controls.get("passed") is True,
            "the inherited no-effect native match-representation controls failed")
    core.ensure_candidate_free()
    gc.collect()
    fresh = source_v6.audit()
    graph = source_v6._validate_fresh_graph(fresh)
    core.ensure_candidate_free()
    owners = fresh.get("public_type_ownership")
    require(
        isinstance(owners, dict)
        and set(owners) == set(CORE_FAMILIES)
        and fresh.get("standard_pickle_checks") == 48
        and all(
            source_v6._validate_owner(
                owners[role], role, graph["native_sha256_by_family"][role],
            ) is owners[role]
            for role in CORE_FAMILIES
        ),
        "the newly rebuilt source audit lost genuine type ownership or standard pickle",
    )
    representation = {
        role: _run_repr_worker(role, graph["native_sha256_by_family"][role])
        for role in CORE_FAMILIES
    }
    core.ensure_candidate_free()
    current_source, _ = core.bounded_file(
        SOURCE_PATH, maximum=MAX_SOURCE_BYTES,
        label="actual immutable version-seven source audit controller",
    )
    report = dict(fresh)
    report.update({
        "schema": SCHEMA, "postfinal_schema": SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": current_source,
        "previous_v6_audit_source_path": source_v6.SOURCE_RELATIVE,
        "previous_v6_audit_source_sha256": V6_BASE_SOURCE_SHA256,
        "previous_v6_audit_report_path": source_v6.REPORT_RELATIVE,
        "previous_v6_audit_report_sha256": V6_BASE_REPORT_SHA256,
        "previous_v6_report_historical": True,
        "previous_v6_strict_audit_source_path": V6_STRICT_SOURCE_RELATIVE,
        "previous_v6_strict_audit_source_sha256": V6_STRICT_SOURCE_SHA256,
        "previous_v6_strict_audit_report_path": V6_STRICT_REPORT_RELATIVE,
        "previous_v6_strict_audit_report_sha256": V6_STRICT_REPORT_SHA256,
        "previous_v6_strict_report_historical": True,
        "official_v2_source_path": OFFICIAL_SOURCE_RELATIVE,
        "official_v2_source_sha256": OFFICIAL_SOURCE_SHA256,
        "official_v2_protocol_path": OFFICIAL_PROTOCOL_RELATIVE,
        "official_v2_protocol_sha256": OFFICIAL_PROTOCOL_SHA256,
        "official_v2_rust_failure_path": OFFICIAL_FAILURE_RELATIVE,
        "official_v2_rust_failure_sha256": observed_failure,
        "official_v2_rust_failure_historical": True,
        "historical_public_input_sha256": preserved,
        "postfinal_wrapper_self_test": controls,
        "postfinal_interpreter": runtime,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": graph["source_paths"],
        "verified_native_role_count": 5,
        "native_sha256_by_family": graph["native_sha256_by_family"],
        "public_type_ownership": owners,
        "standard_pickle_checks_per_family": 16,
        "standard_pickle_checks": 48,
        "public_match_repr": representation,
        "match_repr_checks_per_family": 2,
        "verified_match_repr_checks": 6,
        "historical_stage12_only": True,
        "stage12_candidate_results_qualify_current_sources": False,
        "postfinal_scope": {
            "append_only": True,
            "exclusive_report_path": REPORT_RELATIVE,
            "previous_v6_report_preserved": True,
            "previous_v6_report_historical": True,
            "previous_v6_strict_report_preserved": True,
            "official_v2_actual_rust_failure_preserved": True,
            "exact_current_owned_candidate_source_count": 12,
            "actual_current_native_binary_count": 5,
            "standard_pickle_checks": 48,
            "genuine_match_repr_checks": 6,
            "candidate_imports": "isolated guarded subprocesses only",
            "mapped_binaries_hashed_against_static_elf": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
    })
    require(
        sum(item["match_repr_checks"] for item in representation.values()) == 6,
        "the actual genuine match-representation denominator was weakened",
    )
    core.ensure_candidate_free()
    return report


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(isinstance(target, Path), "the exclusive version-seven output is unsafe")
    relative = (
        target.relative_to(ROOT).as_posix()
        if target.is_absolute() and target.is_relative_to(ROOT)
        else target.as_posix() if not target.is_absolute() else ""
    )
    destination_name(relative)
    require(
        not target.is_symlink()
        and target.name == REPORT_PATH.name
        and target.parent.resolve(strict=True)
        == REPORT_PATH.parent.resolve(strict=True),
        "only the exact new version-seven source report is authorized",
    )
    payload = core.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES,
            "the genuine complete source report exceeds its safe bound")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(REPORT_PATH.parent.resolve(strict=True), flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusive version-seven output parent is unsafe")
        create = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        create |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(REPORT_PATH.name, create, 0o644, dir_fd=directory)
        try:
            pending = memoryview(payload)
            while pending:
                written = os.write(descriptor, pending)
                require(written > 0, "the one-use source-report write stalled")
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
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--self-test", action="store_true")
    commands.add_argument("--audit", action="store_true")
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args(arguments)
    try:
        core.ensure_candidate_free()
        if args.self_test:
            require(args.output == REPORT_PATH,
                    "the no-effect synthetic controls may not create a report")
            report = self_test()
            sys.stdout.buffer.write(core.canonical(report) + b"\n")
            return 0 if report["passed"] else 1
        report = audit()
        report_sha = write_report(report, args.output)
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "PASS", "result": "PASS", "passed": True,
            "report": REPORT_RELATIVE, "report_sha256": report_sha,
            "audit_source_sha256": report["audit_source_sha256"],
            "verified_core_family_count": 3,
            "verified_distinct_pipeline_count": 4,
            "verified_candidate_source_count": 12,
            "verified_native_role_count": 5,
            "standard_pickle_checks": 48,
            "verified_match_repr_checks": 6,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 0
    except (
        source_v6.AuditV6Error, OSError, RuntimeError, TypeError,
        ValueError, KeyError, UnicodeError, subprocess.SubprocessError,
    ) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA, "postfinal_schema": SCHEMA,
            "status": "FAIL", "result": "FAIL", "passed": False,
            "error": str(error),
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
