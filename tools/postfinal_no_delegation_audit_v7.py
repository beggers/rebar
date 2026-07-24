#!/usr/bin/env python3
"""Independently re-audit rebuilt native engines after a real official failure.

``--self-test`` is candidate-, file-, worker-, clock-, and evidence-free.
Only an explicit, fully pinned ``--audit`` can create the exact new V7 report.
"""

from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import importlib
import json
import os
import pickle
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import postfinal_from_scratch_audit_v6 as historical_base
from tools import postfinal_no_delegation_audit_v6 as previous
from tools import postfinal_cpython_locale_v2_failure as failure_recorder


core = historical_base.core
SCHEMA = "rebar-postfinal-no-delegation-audit-v7"
SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v7.py"
SOURCE_PATH = ROOT / SOURCE_RELATIVE
REPORT_RELATIVE = "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json"
REPORT_PATH = ROOT / REPORT_RELATIVE

BASE_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v7.py"
BASE_REPORT_RELATIVE = "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json"
BASE_SCHEMA = "rebar-postfinal-from-scratch-audit-v7"

# Root authorized these only after the independent V7 controller was frozen
# and its genuine passing source report was exclusively created and published.
BASE_SOURCE_SHA256: str | None = (
    "defa306e47a0d325af7d4c7fabb54324f6cb6d4653a494c46846838f5e2cf487"
)
BASE_REPORT_SHA256: str | None = (
    "efae1f94fb06a1eabbab352794410c4d8e20a78202dcbf769b08ff9c7cee130a"
)

V6_STRICT_SOURCE_RELATIVE = previous.SOURCE_RELATIVE
V6_STRICT_SOURCE_SHA256 = (
    "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649"
)
V6_STRICT_REPORT_RELATIVE = previous.REPORT_RELATIVE
V6_STRICT_REPORT_SHA256 = (
    "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f"
)
V6_BASE_SOURCE_RELATIVE = historical_base.SOURCE_RELATIVE
V6_BASE_SOURCE_SHA256 = (
    "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f"
)
V6_BASE_REPORT_RELATIVE = historical_base.REPORT_RELATIVE
V6_BASE_REPORT_SHA256 = (
    "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb"
)

OFFICIAL_V2_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v2.py"
OFFICIAL_V2_SOURCE_SHA256 = (
    "e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1"
)
OFFICIAL_V2_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md"
OFFICIAL_V2_PROTOCOL_SHA256 = (
    "a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5"
)
OFFICIAL_V2_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json"
)
# Root authenticated these only after the actual observed first failure was
# exclusively preserved.  Raw controller streams were not captured or rerun.
OFFICIAL_V2_FAILURE_SHA256 = (
    "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f"
)
FAILURE_RECORDER_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_v2_failure.py"
FAILURE_RECORDER_SOURCE_SHA256 = (
    "42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5"
)
FAILURE_RECORDER_PROTOCOL_RELATIVE = (
    "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2-FAILURE.md"
)
FAILURE_RECORDER_PROTOCOL_SHA256 = (
    "75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818"
)

QUALIFIED_FAMILIES = previous.QUALIFIED_FAMILIES
AUDITED_FAMILIES = previous.AUDITED_FAMILIES
OWNED_SOURCES = previous.OWNED_SOURCES
NATIVE_ROLES = previous.NATIVE_ROLES
NATIVE_FILE_ROLES = previous.NATIVE_FILE_ROLES
NATIVE_LOADER_ALIASES = previous.NATIVE_LOADER_ALIASES
MAX_SOURCE_BYTES = previous.MAX_SOURCE_BYTES
MAX_REPORT_BYTES = previous.MAX_REPORT_BYTES
MAX_WORKER_BYTES = previous.MAX_WORKER_BYTES
EXPECTED_OFFICIAL_METHOD = "ReTests.test_match_repr"
EXPECTED_MATCH_REPR_CASES = ("str", "bytes")
OWNED_BRIDGES = {
    "rust": "candidates._rust_bridge",
    "vm": "candidates._vm_native",
    "zig": "candidates._zig_bridge",
}

PUBLIC_INPUTS = frozenset({
    SOURCE_RELATIVE,
    BASE_SOURCE_RELATIVE,
    BASE_REPORT_RELATIVE,
    V6_STRICT_SOURCE_RELATIVE,
    V6_STRICT_REPORT_RELATIVE,
    V6_BASE_SOURCE_RELATIVE,
    V6_BASE_REPORT_RELATIVE,
    OFFICIAL_V2_SOURCE_RELATIVE,
    OFFICIAL_V2_PROTOCOL_RELATIVE,
    OFFICIAL_V2_FAILURE_RELATIVE,
    FAILURE_RECORDER_SOURCE_RELATIVE,
    FAILURE_RECORDER_PROTOCOL_RELATIVE,
})


class AuditV7Error(previous.AuditV6Error):
    """A rebuilt native engine has no complete independent V7 proof."""


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AuditV7Error(message)


def valid_sha256(value: Any) -> bool:
    return previous.valid_sha256(value)


def _required_pins(synthetic: Mapping[str, Any] | None = None) -> dict[str, str]:
    values: dict[str, Any] = {
        "base_source": BASE_SOURCE_SHA256,
        "base_report": BASE_REPORT_SHA256,
        "official_failure": OFFICIAL_V2_FAILURE_SHA256,
    }
    if synthetic is not None:
        require(isinstance(synthetic, Mapping) and set(synthetic) == set(values),
                "synthetic V7 proofs omitted a required real prerequisite")
        values = dict(synthetic)
    for name, digest in values.items():
        require(valid_sha256(digest),
                "the genuinely produced " + name + " V7 proof is not root-finalized")
    require(len(set(values.values())) == len(values),
            "separate fresh V7 proofs cannot share a substituted fingerprint")
    return values


def validate_public_relative(value: Any) -> str:
    require(type(value) is str, "an exact strict V7 public input must be text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value in PUBLIC_INPUTS,
        "refusing an unapproved, historical-as-current, private, or performance input",
    )
    return value


def destination_name(value: Any) -> str:
    require(type(value) is str, "the exclusive V7 report path must be text")
    path = PurePosixPath(value)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value
        and "\x00" not in value
        and str(path) == value
        and value == REPORT_RELATIVE,
        "only the exact exclusively created V7 no-delegation report is permitted",
    )
    return value


def bounded_public_bytes(path: Path, *, maximum: int) -> tuple[bytes, str]:
    require(isinstance(path, Path) and not path.is_symlink(),
            "an exact strict V7 public input must not be a symlink")
    try:
        resolved = path.resolve(strict=True)
        relative = resolved.relative_to(ROOT.resolve(strict=True)).as_posix()
    except (OSError, RuntimeError, ValueError) as error:
        raise AuditV7Error("an approved strict V7 input escaped the repository") from error
    validate_public_relative(relative)
    require(resolved.is_file(), "an approved strict V7 input is not a regular file")
    digest, payload = core.bounded_file(
        path, maximum=maximum,
        label="exact authenticated strict V7 public input: " + relative,
        keep=True,
    )
    require(isinstance(payload, bytes),
            "a bounded authenticated strict V7 public input returned no bytes")
    return payload, digest


def public_document(path: Path) -> tuple[dict[str, Any], str]:
    payload, fingerprint = bounded_public_bytes(path, maximum=MAX_REPORT_BYTES)
    document = core.decode_report(payload, label="exact authenticated strict V7 public report")
    require(isinstance(document, dict), "the strict V7 public report is not an object")
    return document, fingerprint


MATCH_REPR_WORKER_FRAGMENT = r'''
match_representations = []
for kind, pattern, subject in (
    ("str", r"(.+)(.*?)\1", "[abracadabra]"),
    ("bytes", br"(.+)(.*?)\1", b"[abracadabra]"),
):
    compiled = module.compile(pattern)
    if type(compiled) is not module.Pattern:
        raise RuntimeError("the V7 official pattern is not genuinely native-owned")
    actual = compiled.search(subject)
    if actual is None or type(actual) is not module.Match:
        raise RuntimeError("the V7 native engine returned a foreign match: " + kind)
    actual_type = type(actual)
    if actual_type.__module__ != {
        "rust": "candidates._rust_bridge",
        "vm": "candidates._vm_native",
        "zig": "candidates._zig_bridge",
    }[role] or actual_type.__qualname__ != "Match":
        raise RuntimeError("the V7 official match type has a foreign owner: " + kind)
    if actual.span() != (1, 12):
        raise RuntimeError("the V7 native engine changed the actual official match span")
    piece = actual.group(0)
    expected_piece = "abracadabra" if kind == "str" else b"abracadabra"
    if piece != expected_piece or type(piece) is not type(expected_piece):
        raise RuntimeError("the V7 native engine changed the official match text")
    suffix = " object; span=(1, 12), match=" + repr(piece) + ">"
    expected_repr = (
        "<" + actual_type.__module__ + "." + actual_type.__qualname__ + suffix
    )
    observed = repr(actual)
    if observed != expected_repr or observed.startswith("<re.Match"):
        raise RuntimeError(
            "the V7 actual official native match representation failed: "
            + role + "/" + kind
        )
    match_representations.append({
        "id": role + ":match-repr:" + kind,
        "role": role,
        "kind": kind,
        "subject_kind": kind,
        "match_type_module": actual_type.__module__,
        "match_type_qualified_name": actual_type.__qualname__,
        "match_module": actual_type.__module__,
        "match_qualified_name": actual_type.__qualname__,
        "span": [1, 12],
        "match": repr(piece),
        "pattern_representation": repr(pattern),
        "subject_representation": repr(subject),
        "matched_representation": repr(piece),
        "observed_repr": observed,
        "actual_repr": observed,
        "expected_repr": expected_repr,
        "native_type_identity": True,
        "genuine_matching_executed": True,
        "passed": True,
    })
if len(match_representations) != 2:
    raise RuntimeError("the V7 worker omitted a true string or bytes official match")
verified_after_matching = stage07._verify_family_native_mappings(
    role, {"native_sha256_by_family": {role: expected}}
)
if verified_after_matching != expected or verified_after_matching != natives:
    raise RuntimeError("actual V7 native matching substituted its audited binary")
loaded_after_matching = sorted(
    name for name, item in sys.modules.items()
    if name.startswith("candidates.")
    and item is not None
    and not isinstance(item, stage07._ForbiddenRegexModule)
)
if loaded_after_matching != loaded:
    raise RuntimeError("actual V7 official matching loaded a foreign candidate")
'''

require(previous.OWNER_WORKER_BOOTSTRAP.count("\noutput = {\n") == 1,
        "the immutable V6 owner bootstrap cannot be extended unambiguously")
require(previous.OWNER_WORKER_BOOTSTRAP.count(
    '    "standard_pickle_check_count": len(roundtrips),\n'
) == 1, "the immutable V6 actual pickle denominator cannot be extended")
OWNER_WORKER_BOOTSTRAP = (
    previous.OWNER_WORKER_BOOTSTRAP
    .replace("the V6", "the V7")
    .replace("a V6", "a V7")
    .replace("public-owner-worker-v6", "public-owner-worker-v7")
    .replace("\noutput = {\n", "\n" + MATCH_REPR_WORKER_FRAGMENT + "\noutput = {\n")
    .replace(
        '    "standard_pickle_check_count": len(roundtrips),\n',
        '    "standard_pickle_check_count": len(roundtrips),\n'
        '    "match_representation_checks": match_representations,\n'
        '    "match_representation_check_count": len(match_representations),\n'
        '    "match_repr_checks": len(match_representations),\n'
        '    "genuine_matching_executed": True,\n',
    )
)


def _repr_rows(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        rows = value
    elif isinstance(value, Mapping):
        rows = next((value.get(key) for key in (
            "match_representation_checks", "records", "checks", "cases"
        ) if isinstance(value.get(key), list)), None)
        if rows is None and set(value) == set(EXPECTED_MATCH_REPR_CASES):
            rows = [value[kind] for kind in EXPECTED_MATCH_REPR_CASES]
    else:
        rows = None
    require(isinstance(rows, list) and len(rows) == 2,
            "an independent native engine omitted a true official repr case")
    require(all(isinstance(item, Mapping) for item in rows),
            "an actual official match representation record is malformed")
    return rows


def validate_match_repr(value: Any, family: str) -> list[dict[str, Any]]:
    require(family in QUALIFIED_FAMILIES, "a foreign match representation was selected")
    rows = _repr_rows(value)
    observed_kinds: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        kind = row.get("kind", row.get("subject_kind", row.get("case")))
        require(type(kind) is str and kind in EXPECTED_MATCH_REPR_CASES
                and kind not in observed_kinds
                and kind == EXPECTED_MATCH_REPR_CASES[index],
                "a true official str/bytes representation was omitted, duplicated, or reordered")
        owner = row.get(
            "match_type_module",
            row.get("match_module", row.get("owner_module", row.get("module"))),
        )
        qualified = row.get("match_type_qualified_name",
                            row.get("match_qualified_name",
                                    row.get("qualified_name", row.get("type_name"))))
        observed = row.get(
            "observed_repr",
            row.get("actual_repr", row.get("representation", row.get("repr"))),
        )
        match = "'abracadabra'" if kind == "str" else "b'abracadabra'"
        pattern = r"(.+)(.*?)\1" if kind == "str" else br"(.+)(.*?)\1"
        subject = "[abracadabra]" if kind == "str" else b"[abracadabra]"
        suffix = " object; span=(1, 12), match=" + match + ">"
        expected = "<" + OWNED_BRIDGES[family] + ".Match" + suffix
        require(
            row.get("passed") is True
            and owner == OWNED_BRIDGES[family]
            and qualified == "Match"
            and row.get("span") == [1, 12]
            and isinstance(observed, str)
            and observed == expected
            and row.get("id") == family + ":match-repr:" + kind
            and row.get("pattern_representation") == repr(pattern)
            and row.get("subject_representation") == repr(subject)
            and row.get("matched_representation") == match
            and row.get("expected_repr") == expected
            and row.get("native_type_identity") is True
            and row.get("genuine_matching_executed") is True
            and ("role" not in row or row.get("role") == family),
            "the actual native-owned official match repr failed: " + family + "/" + kind,
        )
        normalized.append({
            "role": family, "kind": kind,
            "match_type_module": owner,
            "match_type_qualified_name": qualified,
            "span": [1, 12], "observed_repr": observed,
            "passed": True,
        })
        observed_kinds.add(kind)
    require(observed_kinds == set(EXPECTED_MATCH_REPR_CASES),
            "a genuine native family omitted a string or bytes official match")
    return normalized


def validate_source_match_repr(
    document: Any, family: str, native: Mapping[str, str],
) -> list[dict[str, Any]]:
    require(family in QUALIFIED_FAMILIES and isinstance(document, Mapping),
            "the fresh independent source omitted a genuine representation worker")
    require(
        document.get("schema") == BASE_SCHEMA + "-match-repr-worker"
        and document.get("status") == "PASS"
        and document.get("result") == "PASS"
        and document.get("passed") is True
        and document.get("family") == family
        and document.get("candidate_module")
        == "candidates." + family + "_candidate"
        and document.get("native_bridge_module") == OWNED_BRIDGES[family]
        and document.get("native_binary_sha256") == dict(native)
        and document.get("match_repr_checks") == 2
        and document.get("genuine_matching_executed") is True
        and document.get("external_regex_packages") == 0
        and document.get("benchmark_or_timing_executed") is False
        and document.get("fixture_accessed") is False
        and document.get("loaded_candidate_modules") == sorted({
            "candidates." + family + "_candidate", OWNED_BRIDGES[family],
        }),
        "the authentic independent source match worker is incomplete: " + family,
    )
    guard = document.get("guard")
    require(
        isinstance(guard, Mapping)
        and guard.get("family") == family
        and guard.get("native_loader_aliases_blocked")
        == list(NATIVE_LOADER_ALIASES)
        and all(guard.get(name) is True for name in (
            "enabled", "stdlib_re_blocked", "cpython_sre_blocked",
            "third_party_regex_blocked", "cross_family_blocked",
            "foreign_dynamic_libraries_blocked",
        )),
        "the fresh independent source worker weakened native isolation",
    )
    return validate_match_repr(document, family)


def _official_failed_method(document: Mapping[str, Any]) -> str | None:
    for key in ("failed_method", "failure_method", "test", "test_method"):
        value = document.get(key)
        if type(value) is str:
            return value
    for key in ("failure_records", "failures", "records", "method_failures"):
        rows = document.get(key)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, Mapping):
                    for field in ("test", "method", "failed_method", "name"):
                        value = row.get(field)
                        if value == EXPECTED_OFFICIAL_METHOD:
                            return value
    return None


def validate_official_failure(
    document: Mapping[str, Any], *, expected_digest: str,
) -> dict[str, Any]:
    require(valid_sha256(expected_digest),
            "the actual official V2 Rust failure has not been root-authenticated")
    require(isinstance(document, Mapping),
            "the genuine previous official failure is not a JSON object")
    require(document.get("schema") == failure_recorder.SCHEMA
            and document.get("status") == "FAIL"
            and document.get("result") == "FAIL"
            and document.get("python") == "3.14.6"
            and document.get("failed_role") == "rust"
            and document.get("failed_module") == "candidates.rust_candidate"
            and _official_failed_method(document) == EXPECTED_OFFICIAL_METHOD,
            "the real official Rust match-representation failure was omitted or hidden")
    require(document.get("source_path") == FAILURE_RECORDER_SOURCE_RELATIVE
            and document.get("source_sha256") == FAILURE_RECORDER_SOURCE_SHA256
            and document.get("protocol_path") == FAILURE_RECORDER_PROTOCOL_RELATIVE
            and document.get("protocol_sha256") == FAILURE_RECORDER_PROTOCOL_SHA256,
            "the actual observed-failure recorder or frozen protocol was substituted")
    failure_recorder.validate_report(dict(document))
    roles = document.get("roles")
    require(isinstance(roles, Mapping)
            and set(roles) == {"re", "rust", "vm", "zig"},
            "the actual failure omitted or invented an official engine result")
    rust = roles["rust"]
    require(isinstance(rust, Mapping)
            and rust.get("methods") == 146
            and rust.get("passed") == 145
            and rust.get("failed") == 1
            and rust.get("failed_method") == EXPECTED_OFFICIAL_METHOD,
            "the true official 145/146 Rust failure was hidden or rewritten")
    require(all(isinstance(roles[family], Mapping)
                and roles[family].get("execution") == "NOT RUN"
                and roles[family].get("status") == "NOT RUN"
                for family in ("vm", "zig")),
            "an official compatibility pass was fabricated for C or Zig")
    require(document.get("performance", "NOT MEASURED") == "NOT MEASURED"
            and document.get("benchmark_or_timing_executed", False) is False
            and document.get("timing_performed", False) is False
            and document.get("holdout_accessed", False) is False
            and document.get("holdout_or_case_fixture_access", False) is False,
            "the official correctness failure accessed performance or a holdout")
    return {
        "schema": document.get("schema"),
        "path": OFFICIAL_V2_FAILURE_RELATIVE,
        "sha256": expected_digest,
        "source_path": FAILURE_RECORDER_SOURCE_RELATIVE,
        "source_sha256": FAILURE_RECORDER_SOURCE_SHA256,
        "protocol_path": FAILURE_RECORDER_PROTOCOL_RELATIVE,
        "protocol_sha256": FAILURE_RECORDER_PROTOCOL_SHA256,
        "official_source_path": OFFICIAL_V2_SOURCE_RELATIVE,
        "official_source_sha256": OFFICIAL_V2_SOURCE_SHA256,
        "official_protocol_path": OFFICIAL_V2_PROTOCOL_RELATIVE,
        "official_protocol_sha256": OFFICIAL_V2_PROTOCOL_SHA256,
        "status": "FAIL",
        "result": "FAIL",
        "failed_role": "rust",
        "failed_method": EXPECTED_OFFICIAL_METHOD,
        "historical": True,
        "qualifies_current_engines": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
    }


def validate_base_document(
    document: Mapping[str, Any], pins: Mapping[str, str],
    *, failure_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(document, dict), "the fresh V7 source proof is not an object")
    expected: dict[str, Any] = {
        "schema": BASE_SCHEMA,
        "postfinal_schema": BASE_SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_native_role_count": 5,
        "standard_pickle_checks": 48,
        "verified_match_repr_checks": 6,
    }
    for name, value in expected.items():
        require(document.get(name) == value
                and type(document.get(name)) is type(value),
                "the actual independent V7 source report is incomplete: " + name)
    graph = historical_base._validate_fresh_graph(document)
    require(graph.get("source_count") == 12
            and graph.get("native_binary_count") == 5,
            "the independent V7 source report weakened its owned source graph")
    natives = previous._expected_native_by_family(document)
    require(sum(len(items) for items in natives.values()) == 5,
            "the fresh V7 base omitted an actual role-specific native ELF")
    owner_reports = document.get("public_type_ownership")
    representations = document.get("public_match_repr")
    require(isinstance(owner_reports, Mapping)
            and set(owner_reports) == set(QUALIFIED_FAMILIES)
            and isinstance(representations, Mapping)
            and set(representations) == set(QUALIFIED_FAMILIES),
            "the fresh V7 source omitted owned public types or official representations")
    for family in QUALIFIED_FAMILIES:
        owner = owner_reports[family]
        require(isinstance(owner, Mapping),
                "the fresh V7 source omitted a real native public owner")
        compatible = dict(owner)
        compatible["schema"] = historical_base.SCHEMA + "-owned-types"
        historical_base._validate_owner(compatible, family, natives[family])
        validate_source_match_repr(representations[family], family, natives[family])
    controls = document.get("postfinal_wrapper_self_test")
    require(isinstance(controls, Mapping)
            and controls.get("passed") is True
            and controls.get("check_count", 0) >= 198,
            "the independently produced V7 source did not pass its malicious controls")
    manifest = document.get("manifest_provenance")
    require(isinstance(manifest, Mapping)
            and manifest.get("python_dependencies") == []
            and manifest.get("rust_third_party_dependency_count") == 0
            and manifest.get("issues") == [],
            "the fresh V7 matching engines delegate to an external package")
    if failure_provenance is not None:
        require(document.get("official_v2_rust_failure_path")
                == failure_provenance["path"]
                and document.get("official_v2_rust_failure_sha256")
                == failure_provenance["sha256"]
                and document.get("official_v2_rust_failure_historical") is True,
                "the fresh V7 source concealed its genuine prior official failure")
    return {"graph": graph, "natives": natives}


def _validate_v6_history() -> dict[str, Any]:
    _, source_sha = bounded_public_bytes(
        ROOT / V6_STRICT_SOURCE_RELATIVE, maximum=MAX_SOURCE_BYTES,
    )
    require(source_sha == V6_STRICT_SOURCE_SHA256,
            "the preserved actual V6 no-delegation source changed")
    strict, strict_sha = public_document(ROOT / V6_STRICT_REPORT_RELATIVE)
    require(strict_sha == V6_STRICT_REPORT_SHA256,
            "the preserved actual V6 no-delegation report changed")
    require(
        strict.get("schema") == previous.SCHEMA
        and strict.get("postfinal_schema") == previous.SCHEMA
        and strict.get("status") == "PASS"
        and strict.get("result") == "PASS"
        and strict.get("passed") is True
        and strict.get("audit_source_path") == V6_STRICT_SOURCE_RELATIVE
        and strict.get("audit_source_sha256") == V6_STRICT_SOURCE_SHA256
        and strict.get("base_audit_source_path") == V6_BASE_SOURCE_RELATIVE
        and strict.get("base_audit_source_sha256") == V6_BASE_SOURCE_SHA256
        and strict.get("base_audit_report_path") == V6_BASE_REPORT_RELATIVE
        and strict.get("base_audit_report_sha256") == V6_BASE_REPORT_SHA256
        and strict.get("verified_core_family_count") == 3
        and strict.get("verified_distinct_pipeline_count") == 4
        and strict.get("verified_public_type_family_count") == 3
        and strict.get("verified_standard_pickle_count") == 48,
        "the immutable historical V6 strict proof was substituted or marked current",
    )
    _, base_source_sha = bounded_public_bytes(
        ROOT / V6_BASE_SOURCE_RELATIVE, maximum=MAX_SOURCE_BYTES,
    )
    base, base_sha = public_document(ROOT / V6_BASE_REPORT_RELATIVE)
    require(base_source_sha == V6_BASE_SOURCE_SHA256
            and base_sha == V6_BASE_REPORT_SHA256
            and base.get("schema") == historical_base.SCHEMA
            and base.get("status") == "PASS"
            and base.get("passed") is True,
            "the preserved historical V6 source proof was changed")
    return strict


def _load_v7_source_proof(
    pins: Mapping[str, str], failure: Mapping[str, Any],
) -> tuple[Any, dict[str, Any], str]:
    source_path = ROOT / BASE_SOURCE_RELATIVE
    _, source_sha = bounded_public_bytes(source_path, maximum=MAX_SOURCE_BYTES)
    require(source_sha == pins["base_source"],
            "the independently authored V7 from-scratch controller changed")
    try:
        independent = importlib.import_module("tools.postfinal_from_scratch_audit_v7")
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
        raise AuditV7Error("the genuine independent V7 source audit is unavailable") from error
    require(independent.SCHEMA == BASE_SCHEMA
            and independent.SOURCE_RELATIVE == BASE_SOURCE_RELATIVE
            and independent.REPORT_RELATIVE == BASE_REPORT_RELATIVE
            and Path(independent.__file__).resolve() == source_path.resolve(),
            "the independent fresh V7 source-audit controller was replaced")
    document, observed = public_document(ROOT / BASE_REPORT_RELATIVE)
    require(observed == pins["base_report"],
            "the genuinely produced V7 from-scratch report was replaced")
    validated = validate_base_document(document, pins, failure_provenance=failure)
    authentic = getattr(independent, "_validate_repr", None)
    require(callable(authentic),
            "the independently authored V7 source has no real match validator")
    for family in QUALIFIED_FAMILIES:
        authentic(
            document["public_match_repr"][family],
            family,
            validated["natives"][family],
        )
    return independent, document, observed


def _owner_worker(role: str, expected: dict[str, str]) -> dict[str, Any]:
    require(role in QUALIFIED_FAMILIES,
            "refusing to launch a foreign strict V7 ownership worker")
    command = [
        sys.executable, "-I", "-B", "-c", OWNER_WORKER_BOOTSTRAP,
        str(ROOT), role,
        json.dumps(expected, ensure_ascii=True, sort_keys=True,
                   separators=(",", ":")),
    ]
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": str(ROOT),
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    try:
        child = subprocess.run(
            command, cwd=str(ROOT), env=environment,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=120, check=False,
        )
    except subprocess.SubprocessError as error:
        raise AuditV7Error("the genuine isolated V7 owner failed: " + role) from error
    require(child.returncode == 0
            and 0 < len(child.stdout) <= MAX_WORKER_BYTES
            and len(child.stderr) <= MAX_WORKER_BYTES,
            "a genuine isolated V7 owner crashed or returned unsafe evidence")
    try:
        document = json.loads(child.stdout)
    except (UnicodeError, ValueError) as error:
        raise AuditV7Error("an isolated V7 owner returned malformed evidence") from error
    validate_owner_document(document, role, expected)
    return document


def validate_owner_document(
    document: Mapping[str, Any], family: str, native: Mapping[str, str],
) -> list[dict[str, Any]]:
    require(family in QUALIFIED_FAMILIES and isinstance(document, Mapping),
            "a genuine V7 public-type worker has no valid family")
    require(
        document.get("schema")
        == "rebar-postfinal-no-delegation-public-owner-worker-v7"
        and document.get("status") == "PASS"
        and document.get("role") == family
        and document.get("standard_pickle_check_count") == 16
        and document.get("match_representation_check_count") == 2
        and document.get("match_repr_checks") == 2
        and document.get("genuine_matching_executed") is True
        and document.get("native_binary_sha256") == dict(native)
        and document.get("cached_json_decoder_regex_blocked") is True
        and document.get("benchmark_or_timing_executed") is False
        and document.get("holdout_or_case_fixture_access") is False,
            "an isolated V7 native worker forged owner, pickle, repr, or scope evidence",
    )
    require(document.get("loaded_candidate_modules") == sorted({
        "candidates." + family + "_candidate", OWNED_BRIDGES[family],
    }), "a genuine strict V7 worker loaded a cross-family native engine")
    owners = document.get("public_type_ownership")
    require(isinstance(owners, Mapping) and set(owners) == {"Pattern", "Match"},
            "an actual V7 native worker omitted a genuine public Pattern or Match")
    for name in ("Pattern", "Match"):
        evidence = owners[name]
        allowed = {
            "candidates." + family + "_candidate",
            OWNED_BRIDGES[family],
        }
        require(isinstance(evidence, Mapping)
                and evidence.get("name") == name
                and evidence.get("qualified_name") == name
                and evidence.get("module") in allowed
                and evidence.get("genuinely_importable") is True,
                "the actual V7 pickle worker substituted a foreign public owner")
        if name == "Match":
            require(evidence.get("module") == OWNED_BRIDGES[family],
                    "the actual official match is not owned by its native engine")
    checks = document.get("standard_pickle_checks")
    require(isinstance(checks, list) and len(checks) == 16,
            "an actual V7 worker omitted an ordinary pickle round trip")
    expected = [
        (origin, argument, protocol)
        for origin in ("Pattern", "Match")
        for argument in ("str", "bytes")
        for protocol in (0, 2, 4, pickle.HIGHEST_PROTOCOL)
    ]
    require(all(isinstance(row, Mapping) for row in checks)
            and [(row.get("origin"), row.get("argument"), row.get("protocol"))
                 for row in checks] == expected
            and all(row.get("passed") is True for row in checks),
            "an actual strict V7 worker weakened ordinary standard pickle")
    guard = document.get("guard")
    require(isinstance(guard, Mapping)
            and guard.get("enabled") is True
            and guard.get("family") == family
            and all(guard.get(name) is True for name in (
                "stdlib_re_blocked", "cpython_sre_blocked",
                "third_party_regex_blocked", "cross_family_blocked",
                "foreign_dynamic_libraries_blocked",
            ))
            and guard.get("native_loader_aliases_blocked")
            == list(NATIVE_LOADER_ALIASES),
            "an isolated real V7 native worker weakened stdlib or loader isolation")
    return validate_match_repr(document.get("match_representation_checks"), family)


def _synthetic_digest(value: str) -> str:
    return hashlib.sha256(("strict-v7:" + value).encode("ascii")).hexdigest()


def _synthetic_records(
    family: str, native: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = "candidates." + family + "_candidate"
    bridge = OWNED_BRIDGES[family]
    guard = {
        "family": family,
        "enabled": True,
        "stdlib_re_blocked": True,
        "cpython_sre_blocked": True,
        "third_party_regex_blocked": True,
        "cross_family_blocked": True,
        "foreign_dynamic_libraries_blocked": True,
        "native_loader_aliases_blocked": list(NATIVE_LOADER_ALIASES),
    }
    owner_records: list[dict[str, Any]] = []
    pickle_records: list[dict[str, Any]] = []
    for origin in ("Pattern", "Match"):
        for argument in ("str", "bytes"):
            for protocol_name, protocol in (
                ("protocol-0", 0),
                ("protocol-2", 2),
                ("protocol-4", 4),
                ("highest-protocol", pickle.HIGHEST_PROTOCOL),
            ):
                pickle_records.append({
                    "origin": origin, "argument": argument,
                    "protocol": protocol, "passed": True,
                })
                owner_records.append({
                    "id": origin + ":" + argument + ":" + protocol_name,
                    "origin": origin, "argument": argument,
                    "protocol_name": protocol_name, "protocol": protocol,
                    "passed": True, "genuine_generic_alias": True,
                    "same_owned_native_origin": True,
                    "standard_pickle_round_trip": True,
                })
    public = {
        name: {
            "module": bridge if name == "Match" else candidate,
            "name": name, "qualified_name": name,
            "genuinely_importable": True,
        }
        for name in ("Pattern", "Match")
    }
    base_types = {
        name: {
            **details,
            "native_bridge_module": bridge,
            "candidate_identity": True,
            "native_bridge_identity": name == "Match",
        }
        for name, details in public.items()
    }
    repr_records = []
    for kind in EXPECTED_MATCH_REPR_CASES:
        piece = "'abracadabra'" if kind == "str" else "b'abracadabra'"
        repr_records.append({
            "id": family + ":match-repr:" + kind,
            "role": family, "kind": kind, "subject_kind": kind,
            "match_type_module": bridge,
            "match_type_qualified_name": "Match",
            "match_module": bridge,
            "match_qualified_name": "Match",
            "span": [1, 12],
            "pattern_representation": repr(
                r"(.+)(.*?)\1" if kind == "str" else br"(.+)(.*?)\1"
            ),
            "subject_representation": repr(
                "[abracadabra]" if kind == "str" else b"[abracadabra]"
            ),
            "matched_representation": piece,
            "observed_repr": (
                "<" + bridge + ".Match object; span=(1, 12), match="
                + piece + ">"
            ),
            "actual_repr": (
                "<" + bridge + ".Match object; span=(1, 12), match="
                + piece + ">"
            ),
            "expected_repr": (
                "<" + bridge + ".Match object; span=(1, 12), match="
                + piece + ">"
            ),
            "native_type_identity": True,
            "genuine_matching_executed": True,
            "passed": True,
        })
    source_owner = {
        "schema": BASE_SCHEMA + "-owned-types",
        "status": "PASS", "result": "PASS", "passed": True,
        "family": family, "candidate_module": candidate,
        "native_bridge_module": bridge, "native_sha256": dict(native),
        "standard_pickle_checks": 16,
        "public_types": base_types, "records": owner_records,
        "guard": guard,
        "loaded_candidate_modules": sorted({candidate, bridge}),
        "candidate_regex_matching_executed": False,
        "third_party_regex_packages": 0,
        "benchmark_or_timing_executed": False,
        "fixture_accessed": False,
    }
    worker = {
        "schema": "rebar-postfinal-no-delegation-public-owner-worker-v7",
        "status": "PASS", "role": family,
        "public_type_ownership": public,
        "standard_pickle_checks": pickle_records,
        "standard_pickle_check_count": 16,
        "native_binary_sha256": dict(native),
        "guard": guard,
        "cached_json_decoder_regex_blocked": True,
        "loaded_candidate_modules": sorted({candidate, bridge}),
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "match_representation_checks": repr_records,
        "match_representation_check_count": 2,
        "match_repr_checks": 2,
        "genuine_matching_executed": True,
    }
    return source_owner, worker


def _synthetic_base(pins: Mapping[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    families: dict[str, Any] = {"ast": {"passed": True}}
    native_families: dict[str, Any] = {}
    owners: dict[str, Any] = {}
    matches: dict[str, Any] = {}
    workers: dict[str, Any] = {}
    all_paths: list[str] = []
    for family in QUALIFIED_FAMILIES:
        records = [{
            "file": path,
            "sha256": _synthetic_digest("source:" + path),
            "passed": True,
            "issues": [],
        } for path in historical_base.OWNED_SOURCE_PATHS[family]]
        families[family] = {
            "passed": True,
            "owned_pipeline": {"passed": True, "issues": []},
            "python_source": records[0],
            "native_sources": records[1:],
        }
        all_paths.extend(record["file"] for record in records)
        files: dict[str, Any] = {}
        by_path: dict[str, str] = {}
        for role, path in NATIVE_FILE_ROLES[family].items():
            needed = ["libc.so.6"]
            if (family, role) == ("rust", "bridge"):
                needed = ["_rust_engine.so", "libc.so.6"]
            elif (family, role) == ("zig", "bridge"):
                needed = ["_zig_probe.so", "libc.so.6"]
            fingerprint = _synthetic_digest("native:" + path)
            files[role] = {
                "file": path, "sha256": fingerprint, "elf_class": 64,
                "forbidden_regex_symbols": [], "cross_candidate_symbols": [],
                "runpaths": ["$ORIGIN"] if role == "bridge" else [],
                "needed": needed,
            }
            by_path[path] = fingerprint
        native_families[family] = {
            "passed": True, "issues": [], "files": files,
        }
        owners[family], workers[family] = _synthetic_records(family, by_path)
        matches[family] = {
            "schema": BASE_SCHEMA + "-match-repr-worker",
            "status": "PASS", "result": "PASS", "passed": True,
            "family": family,
            "candidate_module": "candidates." + family + "_candidate",
            "native_bridge_module": OWNED_BRIDGES[family],
            "native_binary_sha256": dict(by_path),
            "guard": copy.deepcopy(workers[family]["guard"]),
            "loaded_candidate_modules": sorted({
                "candidates." + family + "_candidate", OWNED_BRIDGES[family],
            }),
            "records": copy.deepcopy(
                workers[family]["match_representation_checks"]
            ),
            "match_repr_checks": 2,
            "genuine_matching_executed": True,
            "external_regex_packages": 0,
            "benchmark_or_timing_executed": False,
            "fixture_accessed": False,
        }
    source = {
        "schema": BASE_SCHEMA, "postfinal_schema": BASE_SCHEMA,
        "status": "PASS", "result": "PASS", "passed": True,
        "audit_source_path": BASE_SOURCE_RELATIVE,
        "audit_source_sha256": pins["base_source"],
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "verified_candidate_source_count": 12,
        "verified_candidate_source_paths": all_paths,
        "verified_native_role_count": 5,
        "standard_pickle_checks": 48,
        "standard_pickle_checks_per_family": 16,
        "verified_match_repr_checks": 6,
        "official_v2_rust_failure_path": OFFICIAL_V2_FAILURE_RELATIVE,
        "official_v2_rust_failure_sha256": pins["official_failure"],
        "official_v2_rust_failure_historical": True,
        "families": families,
        "manifest_provenance": {
            "passed": True, "issues": [], "python_dependencies": [],
            "rust_third_party_dependency_count": 0,
            "rust_lock_packages": ["rebar-rust-continuation"],
        },
        "native_elf_provenance": {
            "passed": True, "issues": [],
            "audited_binary_count": 5,
            "expected_binary_count": 5,
            "families": native_families,
        },
        "runtime_native_mapping_provenance": {"passed": True},
        "postfinal_wrapper_self_test": {"passed": True, "check_count": 198},
        "public_type_ownership": owners,
        "public_match_repr": matches,
    }
    return source, workers


def _synthetic_failure(pins: Mapping[str, str]) -> dict[str, Any]:
    capture = failure_recorder.validate_capture(
        failure_recorder.TRANSCRIBED_CONTROLLER_FAILURE
    )
    report = failure_recorder.build_report(
        capture,
        {"synthetic_only": True},
        source_sha256=FAILURE_RECORDER_SOURCE_SHA256,
        protocol_sha256=FAILURE_RECORDER_PROTOCOL_SHA256,
    )
    require(valid_sha256(pins["official_failure"]),
            "an in-memory preserved-failure poison lacks its synthetic fingerprint")
    return report


def candidate_free_self_test() -> dict[str, Any]:
    legacy = previous.previous.previous.previous
    legacy.verify_pinned_runtime()
    legacy.require_candidate_free()
    effects = previous.historical_source.previous.previous.previous.BlockSelfTestEffects()
    controls: list[dict[str, Any]] = []

    def check(name: str, value: Any) -> None:
        require(not any(item["name"] == name for item in controls),
                "an independent V7 synthetic poison control was counted twice")
        controls.append({"name": name, "passed": bool(value)})

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except (AuditV7Error, previous.AuditV6Error,
                failure_recorder.FailureRecorderError,
                previous.previous.AuditV5Error,
                TypeError, ValueError, UnicodeError,
                KeyError, RuntimeError, OSError):
            check(name, True)
        else:
            check(name, False)

    with effects:
        inherited = previous.candidate_free_self_test()
        check("retain-all-real-v6-candidate-free-independence-controls",
              inherited.get("schema") == previous.SCHEMA + "-self-test"
              and inherited.get("passed") is True
              and inherited.get("failed") == []
              and inherited.get("check_count", 0) >= 75
              and inherited.get("inherited_v5_control_count", 0) >= 676
              and inherited.get("file_reads") == 0
              and inherited.get("subprocesses") == 0
              and inherited.get("clock_samples") == 0
              and inherited.get("candidate_imports") == 0)
        check("preserve-all-676-historical-malicious-isolation-controls",
              inherited.get("inherited_v5_control_count", 0) >= 676)
        check("preserve-exact-twelve-owned-native-production-sources",
              len(OWNED_SOURCES) == 12)
        check("preserve-exact-five-owned-native-elf-roles",
              len(NATIVE_ROLES) == 5)
        check("preserve-all-three-independently-owned-native-families",
              QUALIFIED_FAMILIES == ("rust", "vm", "zig"))
        check("preserve-all-four-independent-source-pipelines",
              set(AUDITED_FAMILIES) == {"ast", "rust", "vm", "zig"})
        check("preserve-all-five-native-loader-alias-blockers",
              NATIVE_LOADER_ALIASES == (
                  "ctypes.CDLL", "ctypes.cdll.LoadLibrary",
                  "ctypes.cdll._dlltype", "ctypes._dlopen", "_ctypes.dlopen",
              ))
        check("pin-actual-immutable-v6-strict-controller",
              V6_STRICT_SOURCE_SHA256
              == "a936abe91d67169ea361b6770404ffe7bc925fdb3275aef854fbe12fe68a8649")
        check("pin-actual-immutable-v6-strict-report",
              V6_STRICT_REPORT_SHA256
              == "93f174f0861b0ee6e9feadf6e49bf222f0766b393ff74179219e65452b03d84f")
        check("pin-actual-immutable-v6-source-controller",
              V6_BASE_SOURCE_SHA256
              == "77e7ea97f96280019b3be9abfeeb8fc6ff27ca6ecd13189e611586af5719c18f")
        check("pin-actual-immutable-v6-source-report",
              V6_BASE_REPORT_SHA256
              == "0314e3e5de3386d7c9c1e7f8fa4648554ff53cb53e3aafcecc4cb8e4923ddcbb")
        check("pin-actually-frozen-failing-official-v2-controller",
              OFFICIAL_V2_SOURCE_SHA256
              == "e6858d00747645c6f81cad66e2d6ca957c374e88718abc356fc5367b5be100e1")
        check("pin-actually-frozen-failing-official-v2-protocol",
              OFFICIAL_V2_PROTOCOL_SHA256
              == "a515d2a81d8d02df523316d8315ca3617fe3f4330d33745f536ed15917ff20c5")
        check("pin-actually-frozen-first-failure-recorder",
              FAILURE_RECORDER_SOURCE_SHA256
              == "42069714991730daff44351eb76ef2fe44478720eb0c51d76b9ea162600b96a5")
        check("pin-actually-frozen-first-failure-recorder-protocol",
              FAILURE_RECORDER_PROTOCOL_SHA256
              == "75e9a2709c7755de96ae23106db536a38bfd97a80fb37c5ea3f6a98139e26818")
        check("pin-actual-exclusively-preserved-rust-145-of-146-failure",
              OFFICIAL_V2_FAILURE_SHA256
              == "a77f47cbfb992aa9ae3ced5394bffb75575e6f305f0d2bd0fe2677092517654f")
        check("fail-close-unfinalized-independent-v7-source",
              BASE_SOURCE_SHA256 is None or valid_sha256(BASE_SOURCE_SHA256))
        check("fail-close-unfinalized-genuine-v7-source-report",
              BASE_REPORT_SHA256 is None or valid_sha256(BASE_REPORT_SHA256))
        check("fail-close-unfinalized-actual-official-v2-rust-failure",
              OFFICIAL_V2_FAILURE_SHA256 is None
              or valid_sha256(OFFICIAL_V2_FAILURE_SHA256))
        if all(valid_sha256(value) for value in (
            BASE_SOURCE_SHA256, BASE_REPORT_SHA256, OFFICIAL_V2_FAILURE_SHA256
        )):
            current_pins = _required_pins()
            check("accept-only-all-three-actually-root-authenticated-v7-pins",
                  current_pins["base_source"] == BASE_SOURCE_SHA256
                  and current_pins["base_report"] == BASE_REPORT_SHA256
                  and current_pins["official_failure"] == OFFICIAL_V2_FAILURE_SHA256)
        else:
            rejected("reject-real-audit-until-all-three-genuine-new-pins-exist",
                     _required_pins)
        for label, replacement in (
            ("reject-an-unpinned-fresh-v7-source", {"base_source": None}),
            ("reject-an-unpinned-fresh-v7-source-report", {"base_report": None}),
            ("reject-an-unpinned-genuine-prior-official-failure", {"official_failure": None}),
            ("reject-a-forged-fresh-v7-source", {"base_source": "forged"}),
            ("reject-a-forged-official-rust-failure", {"official_failure": "forged"}),
        ):
            def poison_pin(change: Mapping[str, Any] = replacement) -> None:
                pins = {key: _synthetic_digest(key) for key in (
                    "base_source", "base_report", "official_failure"
                )}
                pins.update(change)
                _required_pins(pins)

            rejected(label, poison_pin)
        synthetic_pins = _required_pins({
            key: _synthetic_digest(key)
            for key in ("base_source", "base_report", "official_failure")
        })
        synthetic_failure = _synthetic_failure(synthetic_pins)
        validated_failure = validate_official_failure(
            synthetic_failure, expected_digest=synthetic_pins["official_failure"],
        )
        check("accept-only-real-shaped-preserved-145-of-146-official-failure",
              validated_failure["failed_role"] == "rust"
              and validated_failure["failed_method"] == EXPECTED_OFFICIAL_METHOD
              and validated_failure["qualifies_current_engines"] is False)
        for label, mutation in (
            ("reject-prior-failure-claimed-as-pass", lambda d: d.update(status="PASS")),
            ("reject-prior-failure-hidden-result", lambda d: d.update(result="PASS")),
            ("reject-prior-failure-foreign-candidate", lambda d: d.update(failed_role="vm")),
            ("reject-prior-failure-foreign-official-method", lambda d: d.update(failed_method="ReTests.test_search")),
            ("reject-prior-failure-weakened-method-denominator", lambda d: d["roles"]["rust"].update(methods=145)),
            ("reject-prior-failure-concealed-match-mismatch", lambda d: d["roles"]["rust"].update(passed=146)),
            ("reject-prior-failure-foreign-official-source", lambda d: d.update(source_path=V6_BASE_SOURCE_RELATIVE)),
            ("reject-prior-failure-forged-source-fingerprint", lambda d: d.update(source_sha256="0" * 64)),
            ("reject-prior-failure-performance-sampling", lambda d: d["scope"].update(benchmark_or_timing_executed=True)),
            ("reject-prior-failure-holdout-access", lambda d: d.update(holdout_accessed=True)),
            ("reject-fabricated-c-official-compatibility", lambda d: d["roles"]["vm"].update(status="PASS")),
            ("reject-fabricated-zig-official-compatibility", lambda d: d["roles"]["zig"].update(status="PASS")),
        ):
            def poison_failure(change: Any = mutation) -> None:
                poisoned = copy.deepcopy(synthetic_failure)
                change(poisoned)
                validate_official_failure(
                    poisoned, expected_digest=synthetic_pins["official_failure"],
                )

            rejected(label, poison_failure)
        source, workers = _synthetic_base(synthetic_pins)
        validated_base = validate_base_document(
            source, synthetic_pins, failure_provenance=validated_failure,
        )
        check("accept-only-twelve-synthetic-owned-sources-and-five-native-elves",
              validated_base["graph"]["source_count"] == 12
              and validated_base["graph"]["native_binary_count"] == 5)
        for family in QUALIFIED_FAMILIES:
            actual = validate_owner_document(
                workers[family], family, validated_base["natives"][family],
            )
            check("accept-six-role-owned-official-str-and-bytes-reprs:" + family,
                  len(actual) == 2
                  and {row["kind"] for row in actual}
                  == set(EXPECTED_MATCH_REPR_CASES))
            for label, mutation in (
                ("foreign-native-match-owner", lambda d: d["public_type_ownership"]["Match"].update(module="re")),
                ("foreign-actual-bridge-mapping", lambda d: d.update(native_binary_sha256={})),
                ("omitted-standard-pickle-round-trip", lambda d: d["standard_pickle_checks"].pop()),
                ("failed-standard-pickle-round-trip", lambda d: d["standard_pickle_checks"][0].update(passed=False)),
                ("omitted-official-string-repr", lambda d: d["match_representation_checks"].pop()),
                ("foreign-official-match-repr-owner", lambda d: d["match_representation_checks"][0].update(match_type_module="re")),
                ("hardcoded-re-match-representation", lambda d: d["match_representation_checks"][0].update(observed_repr="<re.Match object; span=(1, 12), match='abracadabra'>")),
                ("concealed-official-span-substitution", lambda d: d["match_representation_checks"][0].update(span=[0, 11])),
                ("failed-actual-bytes-representation", lambda d: d["match_representation_checks"][1].update(passed=False)),
                ("concealed-real-native-match-execution", lambda d: d.update(genuine_matching_executed=False)),
                ("foreign-native-family-loaded", lambda d: d.update(loaded_candidate_modules=["candidates.zig_candidate"])),
                ("omitted-fifth-loader-alias", lambda d: d["guard"].update(native_loader_aliases_blocked=list(NATIVE_LOADER_ALIASES[:-1]))),
                ("stdlib-delegation-enabled", lambda d: d["guard"].update(stdlib_re_blocked=False)),
                ("cross-family-delegation-enabled", lambda d: d["guard"].update(cross_family_blocked=False)),
                ("json-decoder-enum-bypass-enabled", lambda d: d.update(cached_json_decoder_regex_blocked=False)),
            ):
                def poison_worker(change: Any = mutation,
                                  role: str = family) -> None:
                    poisoned = copy.deepcopy(workers[role])
                    change(poisoned)
                    validate_owner_document(
                        poisoned, role, validated_base["natives"][role],
                    )

                rejected("reject-" + label + ":" + family, poison_worker)
        for label, mutation in (
            ("reject-base-omitted-owned-source", lambda d: d.update(verified_candidate_source_count=11)),
            ("reject-base-omitted-real-native-role", lambda d: d.update(verified_native_role_count=4)),
            ("reject-base-omitted-official-repr-case", lambda d: d.update(verified_match_repr_checks=5)),
            ("reject-base-omitted-ordinary-pickle", lambda d: d.update(standard_pickle_checks=47)),
            ("reject-base-omitted-independent-native-family", lambda d: d["public_match_repr"].pop("zig")),
            ("reject-base-external-python-package", lambda d: d["manifest_provenance"].update(python_dependencies=["regex"])),
            ("reject-base-external-rust-regex-crate", lambda d: d["manifest_provenance"].update(rust_third_party_dependency_count=1)),
            ("reject-base-v6-as-current-source-schema", lambda d: d.update(schema=historical_base.SCHEMA)),
            ("reject-base-stale-v6-source-hash", lambda d: d.update(audit_source_sha256=V6_BASE_SOURCE_SHA256)),
            ("reject-base-cross-family-official-repr", lambda d: d["public_match_repr"]["vm"]["records"][0].update(match_type_module=OWNED_BRIDGES["rust"])),
            ("reject-base-hardcoded-repr", lambda d: d["public_match_repr"]["zig"]["records"][0].update(observed_repr="<re.Match object; span=(1, 12), match='abracadabra'>")),
            ("reject-base-reordered-official-str-and-bytes", lambda d: d["public_match_repr"]["rust"]["records"].reverse()),
            ("reject-base-foreign-match-worker-native", lambda d: d["public_match_repr"]["zig"].update(native_binary_sha256={})),
            ("reject-base-match-worker-delegation", lambda d: d["public_match_repr"]["vm"]["guard"].update(third_party_regex_blocked=False)),
            ("reject-base-forged-rust-origin-runpath", lambda d: d["native_elf_provenance"]["families"]["rust"]["files"]["bridge"].update(runpaths=["/tmp"])),
            ("reject-base-cross-family-zig-engine", lambda d: d["native_elf_provenance"]["families"]["rust"]["files"]["bridge"].update(needed=["_rust_engine.so", "_zig_probe.so"])),
        ):
            def poison_base(change: Any = mutation) -> None:
                poisoned = copy.deepcopy(source)
                change(poisoned)
                validate_base_document(
                    poisoned, synthetic_pins, failure_provenance=validated_failure,
                )

            rejected(label, poison_base)
        check("retain-genuine-owner-worker-guard-installation",
              "stage07._install_family_guard(role, expected)" in OWNER_WORKER_BOOTSTRAP)
        check("retain-genuine-native-mapping-verification-before-and-after-matching",
              OWNER_WORKER_BOOTSTRAP.count("stage07._verify_family_native_mappings") >= 2)
        check("retain-genuine-enum-json-decoder-delegation-blocker",
              'decoder.re.compile("forbidden")' in OWNER_WORKER_BOOTSTRAP
              and "enum.sys.modules.get" in OWNER_WORKER_BOOTSTRAP)
        check("retain-all-real-standard-library-generic-alias-pickles",
              "pickle.loads(pickle.dumps(alias, protocol=protocol))"
              in OWNER_WORKER_BOOTSTRAP)
        check("execute-real-owned-native-string-and-bytes-matching",
              "module.compile(pattern)" in OWNER_WORKER_BOOTSTRAP
              and "compiled.search(subject)" in OWNER_WORKER_BOOTSTRAP
              and "type(actual) is not module.Match" in OWNER_WORKER_BOOTSTRAP)
        check("bind-official-match-repr-to-genuine-native-owned-type",
              "actual_type.__module__" in OWNER_WORKER_BOOTSTRAP
              and "actual_type.__qualname__" in OWNER_WORKER_BOOTSTRAP
              and "observed = repr(actual)" in OWNER_WORKER_BOOTSTRAP)
        check("permit-only-exact-new-exclusive-v7-strict-output",
              destination_name(REPORT_RELATIVE) == REPORT_RELATIVE)
        for label, target in (
            ("historical-v6-strict-output", V6_STRICT_REPORT_RELATIVE),
            ("fresh-v7-source-report", BASE_REPORT_RELATIVE),
            ("actual-official-v2-rust-failure", OFFICIAL_V2_FAILURE_RELATIVE),
            ("absolute-v7-strict-output", "/" + REPORT_RELATIVE),
            ("traversing-v7-strict-output",
             "candidates/audits/../POSTFINAL-NO-DELEGATION-AUDIT-V7.json"),
            ("foreign-v7-strict-output", "candidates/audits/FOREIGN.json"),
            ("backslash-v7-strict-output",
             "candidates\\audits\\POSTFINAL-NO-DELEGATION-AUDIT-V7.json"),
            ("nul-v7-strict-output", REPORT_RELATIVE + "\x00"),
            ("nontext-v7-strict-output", 7),
        ):
            rejected("reject-" + label, lambda value=target: destination_name(value))
        for label, target in (
            ("private-case-input", "sealed/private/cases.json"),
            ("held-out-case-input", "sealed/holdout/cases.json"),
            ("final-case-input", "sealed/final/cases.json"),
            ("performance-input", "performance/v9/manifest.json"),
            ("benchmark-input", "benchmarks/cases.json"),
            ("unapproved-v7-input", "candidates/audits/FOREIGN.json"),
            ("traversing-v7-input", "candidates/audits/../FOREIGN.json"),
            ("nul-v7-input", SOURCE_RELATIVE + "\x00"),
        ):
            rejected("reject-" + label,
                     lambda value=target: validate_public_relative(value))
        check("zero-production-or-historical-file-reads", effects.counts["files"] == 0)
        check("zero-candidate-or-reference-subprocesses", effects.counts["processes"] == 0)
        check("zero-benchmark-or-performance-clock-samples", effects.counts["clocks"] == 0)
        check("zero-production-entropy-or-case-materialization",
              effects.counts["entropy"] == 0)
        legacy.require_candidate_free()

    failures = [item["name"] for item in controls if item["passed"] is not True]
    return {
        "schema": SCHEMA + "-self-test",
        "postfinal_schema": SCHEMA + "-self-test",
        "status": "PASS" if not failures else "FAIL",
        "result": "PASS" if not failures else "FAIL",
        "passed": not failures,
        "checks": controls,
        "check_count": len(controls),
        "failed": failures,
        "inherited_v6_self_test": inherited,
        "inherited_v6_control_count": inherited.get("check_count"),
        "inherited_v5_control_count": inherited.get("inherited_v5_control_count"),
        "fixture_storage": "in-memory only",
        "candidate_imports": 0,
        "candidate_imported": False,
        "file_reads": effects.counts["files"],
        "file_writes": 0,
        "subprocesses": effects.counts["processes"],
        "clock_samples": effects.counts["clocks"],
        "production_entropy_drawn": False,
        "production_cases_materialized": 0,
        "report_written": False,
        "benchmark_or_timing_executed": False,
        "holdout_or_case_fixture_access": False,
        "verified_synthetic_match_repr_checks": 6,
    }


def run_audit() -> dict[str, Any]:
    legacy = previous.previous.previous.previous
    immutable_v2 = legacy.previous
    legacy.verify_pinned_runtime()
    legacy.require_candidate_free()
    pins = _required_pins()
    history = _validate_v6_history()
    for relative, expected in (
        (OFFICIAL_V2_SOURCE_RELATIVE, OFFICIAL_V2_SOURCE_SHA256),
        (OFFICIAL_V2_PROTOCOL_RELATIVE, OFFICIAL_V2_PROTOCOL_SHA256),
        (FAILURE_RECORDER_SOURCE_RELATIVE, FAILURE_RECORDER_SOURCE_SHA256),
        (FAILURE_RECORDER_PROTOCOL_RELATIVE, FAILURE_RECORDER_PROTOCOL_SHA256),
    ):
        _, actual = bounded_public_bytes(ROOT / relative, maximum=MAX_SOURCE_BYTES)
        require(actual == expected,
                "the actual failing official upstream source or protocol changed")
    failure, failure_sha = public_document(ROOT / OFFICIAL_V2_FAILURE_RELATIVE)
    require(failure_sha == pins["official_failure"],
            "the genuine exclusively preserved Rust official failure changed")
    provenance = validate_official_failure(failure, expected_digest=failure_sha)
    source, base, base_sha = _load_v7_source_proof(pins, provenance)
    del source
    controls = candidate_free_self_test()
    require(controls.get("passed") is True,
            "the complete independent V7 malicious controls failed")
    immutable = immutable_v2.import_pinned_strict_v1()
    strict_controls = immutable.self_test()
    immutable_v2.validate_controls(
        {"self_test": strict_controls},
        names=immutable_v2.STRICT_CONTROL_NAMES,
        label="actual immutable V7 32-control native no-delegation proof",
    )
    original_loader = immutable._load_original_report
    original_report = immutable.original.REPORT

    def load_fresh_base() -> tuple[dict[str, Any], str]:
        _source, candidate, observed = _load_v7_source_proof(pins, provenance)
        require(candidate == base and observed == base_sha,
                "the actual independently owned V7 source changed during audit")
        return candidate, observed

    immutable._load_original_report = load_fresh_base
    immutable.original.REPORT = ROOT / BASE_REPORT_RELATIVE
    try:
        gc.collect()
        with previous.historical_source.allow_owned_locale_ctype():
            with previous.previous.scoped_original_control_bootstrap(
                previous.V5_SOURCE_SHA256
            ):
                actual = immutable.run_audit()
    finally:
        immutable.original.REPORT = original_report
        immutable._load_original_report = original_loader

    legacy.require_candidate_free()
    require(isinstance(actual, dict)
            and actual.get("schema") == immutable_v2.IMMUTABLE_STRICT_SCHEMA
            and actual.get("passed") is True
            and actual.get("result") == "PASS"
            and actual.get("inherited_control_count") == 76,
            "the genuinely rerun immutable native V7 no-delegation audit failed")
    immutable_v2.validate_controls(
        actual, names=immutable_v2.STRICT_CONTROL_NAMES,
        label="actual complete immutable V7 native no-delegation controls",
    )
    immutable_v2._verify_result_native(actual, base)
    legacy._validate_flattened_native(
        actual, label="the exact real five-role independent V7 native proof",
    )
    qualified = actual.get("qualified_source_fingerprints")
    flattened = actual.get("native_elf_fingerprints")
    require(isinstance(qualified, Mapping)
            and set(qualified) == OWNED_SOURCES
            and all(valid_sha256(value) for value in qualified.values())
            and isinstance(flattened, Mapping)
            and set(flattened) == NATIVE_ROLES
            and all(valid_sha256(value) for value in flattened.values()),
            "the actual native audit omitted one of 12 sources or five ELF roles")
    native = previous._expected_native_by_family(base)
    ownership = {family: _owner_worker(family, native[family])
                 for family in QUALIFIED_FAMILIES}
    match_repr = {
        family: validate_owner_document(ownership[family], family, native[family])
        for family in QUALIFIED_FAMILIES
    }
    require(len(ownership) == 3
            and sum(item["standard_pickle_check_count"]
                    for item in ownership.values()) == 48
            and sum(len(rows) for rows in match_repr.values()) == 6,
            "a genuine guarded V7 engine omitted pickle or match-repr observations")
    for family in QUALIFIED_FAMILIES:
        expected_rows = validate_source_match_repr(
            base["public_match_repr"][family], family, native[family],
        )
        require(match_repr[family] == expected_rows,
                "fresh strict and source workers observed different native reprs: " + family)
    _, strict_sha = bounded_public_bytes(SOURCE_PATH, maximum=MAX_SOURCE_BYTES)
    legacy.require_candidate_free()
    actual.update({
        "schema": SCHEMA,
        "postfinal_schema": SCHEMA,
        "status": "PASS",
        "result": "PASS",
        "passed": True,
        "audit_source_path": SOURCE_RELATIVE,
        "audit_source_sha256": strict_sha,
        "base_audit_source_path": BASE_SOURCE_RELATIVE,
        "base_audit_source_sha256": pins["base_source"],
        "base_audit_report_path": BASE_REPORT_RELATIVE,
        "base_audit_report_sha256": base_sha,
        "base_audit_postfinal_schema": BASE_SCHEMA,
        "previous_v6_audit_source_path": V6_STRICT_SOURCE_RELATIVE,
        "previous_v6_audit_source_sha256": V6_STRICT_SOURCE_SHA256,
        "previous_v6_audit_report_path": V6_STRICT_REPORT_RELATIVE,
        "previous_v6_audit_report_sha256": V6_STRICT_REPORT_SHA256,
        "previous_v6_report_historical": True,
        "previous_v6_source_audit_source_path": V6_BASE_SOURCE_RELATIVE,
        "previous_v6_source_audit_source_sha256": V6_BASE_SOURCE_SHA256,
        "previous_v6_source_audit_report_path": V6_BASE_REPORT_RELATIVE,
        "previous_v6_source_audit_report_sha256": V6_BASE_REPORT_SHA256,
        "previous_v6_source_report_historical": True,
        "official_v2_failure_provenance": provenance,
        "official_v2_failure_preserved": True,
        "official_v2_failure_qualifies_current_engines": False,
        "postfinal_wrapper_self_test": controls,
        "verified_core_family_count": 3,
        "verified_distinct_pipeline_count": 4,
        "manifest_provenance": base["manifest_provenance"],
        "native_elf_provenance": base["native_elf_provenance"],
        "public_type_ownership": ownership,
        "verified_public_type_family_count": 3,
        "verified_standard_pickle_count": 48,
        "public_match_repr": copy.deepcopy(base["public_match_repr"]),
        "strict_public_match_repr": copy.deepcopy(ownership),
        "verified_match_repr_checks": 6,
        "scope": {
            **dict(actual.get("scope", {})),
            "immutable_v6_strict_report_preserved": True,
            "immutable_v6_source_report_preserved": True,
            "actual_official_v2_rust_failure_preserved": True,
            "fresh_v7_source_report_only": True,
            "explicit_source_paths_only": True,
            "closed_owned_source_graph": True,
            "mapped_binaries_hashed_against_static_elf": True,
            "public_owners_verified_in_isolated_guarded_processes": True,
            "actual_string_and_bytes_match_repr_verified": True,
            "all_five_native_loader_aliases_blocked": True,
            "enum_json_decoder_registry_bypass_blocked": True,
            "candidate_imports": "isolated guarded subprocesses only",
            "production_report_path": REPORT_RELATIVE,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        },
        "supersedes": {
            "schema": previous.SCHEMA,
            "source_path": V6_STRICT_SOURCE_RELATIVE,
            "source_sha256": V6_STRICT_SOURCE_SHA256,
            "report_path": V6_STRICT_REPORT_RELATIVE,
            "report_sha256": V6_STRICT_REPORT_SHA256,
            "source_preserved": True,
            "report_historical": True,
            "qualifies_current_engines": False,
            "historical_verified_pickle_checks": history["verified_standard_pickle_count"],
        },
    })
    legacy.require_candidate_free()
    return actual


def write_report(report: Mapping[str, Any], target: Path) -> str:
    require(isinstance(target, Path)
            and destination_name(target.relative_to(ROOT).as_posix()) == REPORT_RELATIVE
            and target.name == REPORT_PATH.name
            and not target.is_symlink()
            and target.parent.resolve() == REPORT_PATH.parent.resolve(),
            "only the exact exclusive, non-symlink V7 strict report is authorized")
    parent = REPORT_PATH.parent
    require(not parent.is_symlink(), "the exclusive V7 strict parent is symbolic")
    resolved = parent.resolve(strict=True)
    require(resolved.is_relative_to(ROOT.resolve(strict=True)),
            "the exclusive V7 no-delegation report escaped its repository")
    payload = core.canonical(report) + b"\n"
    require(len(payload) <= MAX_REPORT_BYTES,
            "the complete genuine V7 strict report exceeds its bounded size")
    directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    file_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    directory = os.open(resolved, directory_flags)
    try:
        require(stat.S_ISDIR(os.fstat(directory).st_mode),
                "the exclusively bounded V7 parent is not a directory")
        descriptor = os.open(REPORT_PATH.name, file_flags, 0o644, dir_fd=directory)
        try:
            view = memoryview(payload)
            while view:
                count = os.write(descriptor, view)
                require(count > 0, "the exclusively created V7 report write stalled")
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
        previous.previous.previous.previous.require_candidate_free()
        if options.self_test:
            require(options.output == REPORT_PATH,
                    "the V7 strict self-test cannot create or redirect evidence")
            result = candidate_free_self_test()
            compact = dict(result)
            inherited = compact.pop("inherited_v6_self_test")
            compact["inherited_v6_self_test_sha256"] = hashlib.sha256(
                core.canonical(inherited)
            ).hexdigest()
            sys.stdout.buffer.write(core.canonical(compact) + b"\n")
            return 0 if result.get("passed") is True else 1
        result = run_audit()
        report_sha256 = write_report(result, options.output)
        summary = {
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "PASS",
            "result": "PASS",
            "passed": True,
            "report": REPORT_RELATIVE,
            "report_sha256": report_sha256,
            "audit_source_sha256": result["audit_source_sha256"],
            "base_audit_report_path": BASE_REPORT_RELATIVE,
            "base_audit_report_sha256": result["base_audit_report_sha256"],
            "verified_core_family_count": 3,
            "verified_native_role_count": 5,
            "verified_public_type_family_count": 3,
            "verified_standard_pickle_count": 48,
            "verified_match_repr_checks": 6,
            "actual_official_failure_preserved": True,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }
        sys.stdout.buffer.write(core.canonical(summary) + b"\n")
        return 0
    except (AuditV7Error, previous.AuditV6Error,
            failure_recorder.FailureRecorderError,
            previous.previous.AuditV5Error, OSError, RuntimeError,
            TypeError, ValueError, KeyError, subprocess.SubprocessError) as error:
        sys.stdout.buffer.write(core.canonical({
            "schema": SCHEMA,
            "postfinal_schema": SCHEMA,
            "status": "FAIL",
            "result": "FAIL",
            "passed": False,
            "error": str(error),
            "candidate_imported": False,
            "benchmark_or_timing_executed": False,
            "holdout_or_case_fixture_access": False,
        }) + b"\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
