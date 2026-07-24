#!/usr/bin/env python3
"""Run the exact complete CPython suite with genuinely guarded native owners."""

from __future__ import annotations

import argparse
import builtins
import contextlib
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import multiprocessing
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import threading
import time
import types
from typing import Any, Callable, Iterator, Mapping


ROOT = Path(__file__).resolve().parent.parent
if not sys.path or sys.path[0] != str(ROOT):
    sys.path.insert(0, str(ROOT))

from tools import postfinal_cpython_locale_oracle_v5 as original


owner: Any = None
strict: Any = None
durable: Any = None


SCHEMA = "rebar-postfinal-cpython-full-public-locale-v6"
SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v6.py"
PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V6.md"
PROTOCOL_SHA256 = (
    "8e43ceaa61f6e70e2e1193de71bde8583c101cdbe40bc78d862ae789531aff57"
)
V5_SOURCE_RELATIVE = "tools/postfinal_cpython_locale_oracle_v5.py"
V5_SOURCE_SHA256 = (
    "9a4f2ac53617fb91e498ae2935bde622417921415af255e390668f69ba908730"
)
V5_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md"
V5_PROTOCOL_SHA256 = (
    "1329cf9c8e36391af134b2fb2b212e71067ace736b282dacd2a6c90233384840"
)
V5_REFERENCE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json"
)
V5_REFERENCE_SHA256 = (
    "3a5c300640b4d5207694d474eb231ce6ff7cb11ce6f3a17da0edd2e48fea3916"
)
V10_OWNER_SOURCE_RELATIVE = "tools/postfinal_from_scratch_audit_v10.py"
V10_OWNER_SOURCE_SHA256 = (
    "0c4d3f07bb51b0ce5ddc148810cb157d21067ddb07b578d3a793aaac5c671505"
)
V10_STRICT_SOURCE_RELATIVE = "tools/postfinal_no_delegation_audit_v10.py"
V10_STRICT_SOURCE_SHA256 = (
    "885168bd6df92ac9cabc8fc78a8389ee487f0be8d3c7fe67a393e984011b8d95"
)
V10_OWNERSHIP_PROTOCOL_RELATIVE = (
    "candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md"
)
V10_OWNERSHIP_PROTOCOL_SHA256 = (
    "902bc095d08331089dcc1d1d11233747438a0cacb0cf1057ae41a2474bde2fa6"
)
V11_SOURCE_RELATIVE = "tools/postfinal_current_build_proofs_v11.py"
V11_SOURCE_SHA256 = (
    "2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04"
)
V11_PROTOCOL_RELATIVE = "oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V11.md"
V11_PROTOCOL_SHA256 = (
    "334405521f2f945cc58cabf246cf8f784e8a6a5be7091a20587b0daf428412af"
)
METHOD_MATRIX_SHA256 = (
    "5802606619ee4aad65a1d031259740b003c891de8674a5321d0bf6dbce2b590a"
)
FAMILIES = ("rust", "vm", "zig")
REFERENCE_LABELS = ("reference_a", "reference_b")
PROOF_KINDS = (
    "edge_archive", "edge_proof", "deep_archive", "deep_proof",
)
MAX_SOURCE_BYTES = original.MAX_SOURCE_BYTES
MAX_EVIDENCE_BYTES = original.MAX_EVIDENCE_BYTES
MAX_WORKER_OUTPUT_BYTES = original.MAX_WORKER_OUTPUT_BYTES
WORKER_TIMEOUT_SECONDS = original.WORKER_TIMEOUT_SECONDS
SELF_ORACLE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json"
)
SELF_ORACLE_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle-failures.json"
)
REPORT_RELATIVE = "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-all.json"
REPORT_FAILURE_RELATIVE = (
    "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-all-failures.json"
)
ROLE_REPORT_RELATIVES = {
    family: "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-"
    + family + ".json"
    for family in FAMILIES
}
ROLE_FAILURE_RELATIVES = {
    family: "oracle/cpython-3.14.6/evidence/postfinal-locale-v6-"
    + family + "-failures.json"
    for family in FAMILIES
}
APPROVED_OUTPUTS = frozenset({
    SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE,
    REPORT_RELATIVE, REPORT_FAILURE_RELATIVE,
    *ROLE_REPORT_RELATIVES.values(), *ROLE_FAILURE_RELATIVES.values(),
})
_METHOD_GUARD_COUNT_NOT_SUPPLIED = object()


class OfficialV6Error(AssertionError):
    """A frozen full upstream method, actual native owner, or proof failed."""


class OfficialV6WorkerFailure(OfficialV6Error):
    """Preserve genuine original records, actual owner failures, and streams."""

    def __init__(self, role: str, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.role = role
        self.details = dict(details)


def require(condition: Any, message: str) -> None:
    if not condition:
        raise OfficialV6Error(message)


def _load_candidate_modules() -> None:
    global owner, strict, durable
    if owner is None and strict is None and durable is None:
        owner = importlib.import_module(
            "tools.postfinal_from_scratch_audit_v10",
        )
        strict = importlib.import_module(
            "tools.postfinal_no_delegation_audit_v10",
        )
        durable = importlib.import_module(
            "tools.postfinal_current_build_proofs_v11",
        )
    require(owner is not None and strict is not None and durable is not None,
            "the genuine complete candidate-only ownership graph was substituted")


def verify_runtime(*, candidate: bool = False) -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode is True
        and Path(sys.executable).resolve()
        == original.upstream.PINNED_CPYTHON.resolve()
        and bool(sys.path) and sys.path[0] == str(ROOT)
        and Path(__file__).resolve() == (ROOT / SOURCE_RELATIVE).resolve(),
        "the exact direct isolated pinned CPython 3.14.6 V6 source is required",
    )
    require(
        original.SCHEMA == "rebar-postfinal-cpython-full-public-locale-v5"
        and original.SOURCE_RELATIVE == V5_SOURCE_RELATIVE
        and original.PROTOCOL_RELATIVE == V5_PROTOCOL_RELATIVE
        and original.PROTOCOL_SHA256 == V5_PROTOCOL_SHA256
        and original.METHOD_MATRIX_SHA256 == METHOD_MATRIX_SHA256
        and original.REFERENCE_LABELS == REFERENCE_LABELS
        and tuple(original.FAMILIES) == FAMILIES
        and Path(original.__file__).resolve() == ROOT / V5_SOURCE_RELATIVE
        and original.upstream.PUBLIC_METHODS == 152
        and original.upstream.PRIVATE_METHODS == 13
        and original.upstream.ORIGINAL_METHODS == 165
        and original.upstream.CORPUS_CASES == 403
        and original.upstream.EXTERNAL_FIXTURE_ASSERTION_CASES == 11
        and len(original.upstream.OFFICIAL_SUPPORT_MODULES) == 26
        and original.upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES == 40 * 1024**3
        and original.upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
        == 18 * 2**31,
        "the complete unchanged original V5 CPython upstream contract changed",
    )
    if candidate:
        require(
            owner is not None and strict is not None and durable is not None
            and owner.SCHEMA == "rebar-postfinal-from-scratch-audit-v10"
            and strict.SCHEMA == "rebar-postfinal-no-delegation-audit-v10"
            and strict.independent is owner
            and durable.SCHEMA == "rebar-postfinal-current-build-proofs-v11"
            and tuple(owner.CORE_FAMILIES) == FAMILIES
            and tuple(durable.FAMILIES) == FAMILIES
            and owner.PROTOCOL_RELATIVE == V10_OWNERSHIP_PROTOCOL_RELATIVE
            and owner.PROTOCOL_SHA256 == V10_OWNERSHIP_PROTOCOL_SHA256
            and strict.BASE_SOURCE_SHA256 == V10_OWNER_SOURCE_SHA256
            and durable.V10_BASE_SOURCE_SHA256 == V10_OWNER_SOURCE_SHA256
            and durable.V10_STRICT_SOURCE_SHA256 == V10_STRICT_SOURCE_SHA256
            and durable.V10_OWNERSHIP_PROTOCOL_SHA256
            == V10_OWNERSHIP_PROTOCOL_SHA256
            and durable.REFRESH_PROTOCOL_SHA256 == V11_PROTOCOL_SHA256
            and Path(owner.__file__).resolve()
            == ROOT / V10_OWNER_SOURCE_RELATIVE
            and Path(strict.__file__).resolve()
            == ROOT / V10_STRICT_SOURCE_RELATIVE
            and Path(durable.__file__).resolve() == ROOT / V11_SOURCE_RELATIVE,
            "a genuinely frozen independent V10 owner or final V11 proof changed",
        )
    else:
        require(
            owner is None and strict is None and durable is None
            and not any(name in sys.modules for name in (
                "tools.postfinal_from_scratch_audit_v10",
                "tools.postfinal_no_delegation_audit_v10",
                "tools.postfinal_current_build_proofs_v11",
            )),
            "a genuine standard-library-only reference imported a candidate "
            "ownership audit or correctness proof",
        )
    require(
        not any(
            module is not None
            and (name == "candidates" or name.startswith("candidates.")
                 or name == "rebar" or name.startswith("rebar."))
            for name, module in tuple(sys.modules.items())
        ),
        "a candidate or public replacement leaked into the V6 controller",
    )


def _frozen(relative: str, expected: str) -> bytes:
    return original._verify_frozen(relative, expected, MAX_SOURCE_BYTES)


def _safe_output_path(relative: Any) -> Path:
    require(type(relative) is str and relative in APPROVED_OUTPUTS,
            "only a separate exact allowlisted V6 evidence path is permitted")
    parsed = PurePosixPath(relative)
    require(not parsed.is_absolute() and ".." not in parsed.parts
            and "\\" not in relative and "\x00" not in relative
            and parsed.as_posix() == relative,
            "an official V6 evidence path escaped the repository")
    return ROOT / relative


def _preflight_fresh_outputs(relatives: tuple[str, ...]) -> None:
    require(len(relatives) == len(set(relatives)),
            "an official V6 evidence destination cannot be reused")
    for relative in relatives:
        path = _safe_output_path(relative)
        require(path.parent.is_dir() and not path.parent.is_symlink()
                and path.resolve(strict=False) == path
                and not path.exists() and not path.is_symlink(),
                "refusing to retry, overwrite, or redirect V6 evidence: "
                + relative)


def _exclusive_write(document: Mapping[str, Any], relative: str) -> str:
    require(isinstance(document, Mapping),
            "only a complete actual V6 evidence object may be published")
    path = _safe_output_path(relative)
    require(path.parent.is_dir() and not path.parent.is_symlink()
            and path.resolve(strict=False) == path,
            "the exact genuine V6 report parent is unavailable or unsafe")
    payload = original.canonical(document) + b"\n"
    require(0 < len(payload) <= MAX_EVIDENCE_BYTES,
            "a complete original V6 report exceeded its frozen bound")
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    directory = os.open(path.parent, directory_flags)
    try:
        actual_parent = os.fstat(directory)
        expected_parent = os.stat(path.parent, follow_symlinks=False)
        require(stat.S_ISDIR(actual_parent.st_mode)
                and (actual_parent.st_dev, actual_parent.st_ino)
                == (expected_parent.st_dev, expected_parent.st_ino),
                "the exact V6 report parent changed before publication")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(path.name, flags, 0o600, dir_fd=directory)
        except OSError as error:
            raise OfficialV6Error(
                "refusing to replace or retry actual V6 evidence: " + relative
            ) from error
        try:
            remaining = memoryview(payload)
            while remaining:
                count = os.write(descriptor, remaining)
                require(count > 0,
                        "an exclusively created actual V6 report was truncated")
                remaining = remaining[count:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
            descriptor = -1
        os.fsync(directory)
    finally:
        if descriptor != -1:
            os.close(descriptor)
        os.close(directory)
    return hashlib.sha256(payload).hexdigest()


def _chosen(selected: str) -> tuple[str, ...]:
    require(selected in ("all", *FAMILIES),
            "exactly one genuine native family or all three must be selected")
    return FAMILIES if selected == "all" else (selected,)


def _candidate_pin_values(
    selected: str, supplied: Mapping[str, Any],
) -> dict[str, str]:
    require(isinstance(supplied, Mapping),
            "actual independently published V10/V11 proof pins are required")
    chosen = _chosen(selected)
    required: dict[str, Any] = {
        "base_report": supplied.get("base_report"),
        "strict_report": supplied.get("strict_report"),
    }
    for family in FAMILIES:
        for kind in PROOF_KINDS:
            label = family + "_" + kind
            value = supplied.get(label)
            if family in chosen:
                required[label] = value
            else:
                require(value is None,
                        "unselected families cannot secretly change the V6 proof "
                        "denominator: " + label)
    for label, value in required.items():
        require(original.valid_sha256(value),
                "BLOCKED: independently publish the actual "
                + label + " SHA-256 before an official candidate run")
    frozen = {
        V5_SOURCE_SHA256, V5_PROTOCOL_SHA256, V5_REFERENCE_SHA256,
        V10_OWNER_SOURCE_SHA256, V10_STRICT_SOURCE_SHA256,
        V10_OWNERSHIP_PROTOCOL_SHA256, V11_SOURCE_SHA256,
        V11_PROTOCOL_SHA256, PROTOCOL_SHA256,
    }
    require(len(set(required.values())) == len(required)
            and not (set(required.values()) & frozen),
            "real passing report/archive/proof hashes cannot be repeated, "
            "guessed from a frozen source, or substituted across families")
    return {label: str(value) for label, value in required.items()}


def authenticate_controller(
    source_sha256: Any, protocol_sha256: Any, *, candidate: bool,
) -> None:
    verify_runtime()
    require(original.valid_sha256(source_sha256),
            "BLOCKED: independently publish the actual V6 controller SHA-256")
    require(protocol_sha256 == PROTOCOL_SHA256,
            "BLOCKED: independently publish the exact frozen V6 protocol")
    _frozen(SOURCE_RELATIVE, str(source_sha256))
    _frozen(PROTOCOL_RELATIVE, PROTOCOL_SHA256)
    _frozen(V5_SOURCE_RELATIVE, V5_SOURCE_SHA256)
    _frozen(V5_PROTOCOL_RELATIVE, V5_PROTOCOL_SHA256)
    if candidate:
        for relative, digest in (
            (V10_OWNER_SOURCE_RELATIVE, V10_OWNER_SOURCE_SHA256),
            (V10_STRICT_SOURCE_RELATIVE, V10_STRICT_SOURCE_SHA256),
            (V10_OWNERSHIP_PROTOCOL_RELATIVE, V10_OWNERSHIP_PROTOCOL_SHA256),
            (V11_SOURCE_RELATIVE, V11_SOURCE_SHA256),
            (V11_PROTOCOL_RELATIVE, V11_PROTOCOL_SHA256),
        ):
            _frozen(relative, digest)
        _load_candidate_modules()
        verify_runtime(candidate=True)


def _original_reference_prerequisites() -> dict[str, Any]:
    return original.authenticate_reference_prerequisites(
        V5_SOURCE_SHA256, V5_PROTOCOL_SHA256,
    )


def _base_document(
    provenance: Mapping[str, Any], source_sha256: str,
) -> dict[str, Any]:
    document = original._base_document(provenance)
    document.update({
        "source_path": SOURCE_RELATIVE,
        "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": PROTOCOL_SHA256,
        "immutable_v5_source_path": V5_SOURCE_RELATIVE,
        "immutable_v5_source_sha256": V5_SOURCE_SHA256,
        "immutable_v5_protocol_path": V5_PROTOCOL_RELATIVE,
        "immutable_v5_protocol_sha256": V5_PROTOCOL_SHA256,
        "synthetic": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    })
    return document


def _validate_v6_reference(
    document: Any, provenance: Mapping[str, Any], source_sha256: str,
) -> dict[str, dict[str, Any]]:
    require(isinstance(document, dict),
            "the actual two-worker V6 reference must be complete canonical JSON")
    for key, expected in {
        "schema": SCHEMA + "-self-oracle",
        "status": "PASS", "synthetic": False, "python": "3.14.6",
        "source_path": SOURCE_RELATIVE, "source_sha256": source_sha256,
        "protocol_path": PROTOCOL_RELATIVE,
        "protocol_sha256": PROTOCOL_SHA256,
        "immutable_v5_source_sha256": V5_SOURCE_SHA256,
        "immutable_v5_protocol_sha256": V5_PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "actual_independent_reference_count": 2,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }.items():
        require(document.get(key) == expected,
                "the complete independent original V6 reference changed: " + key)
    roles = document.get("roles")
    require(isinstance(roles, dict) and tuple(roles) == REFERENCE_LABELS,
            "exactly two genuinely independent actual V6 references are required")
    matrix = provenance["official"]["public_method_matrix"]
    for label in REFERENCE_LABELS:
        require(isinstance(roles.get(label), dict),
                "a genuine complete V6 reference was omitted: " + label)
        original._validate_role("stdlib", roles[label], matrix)
    first = original._status_vector(roles["reference_a"]["records"])
    second = original._status_vector(roles["reference_b"]["records"])
    require(len(first) == 152 and first == second
            and document.get("reference_status_vector_sha256")
            == original.digest(first),
            "the two actual original 152-method V6 reference vectors disagree")
    return {name: dict(roles[name]) for name in REFERENCE_LABELS}


def _read_reference(
    reference_sha256: Any, provenance: Mapping[str, Any],
    source_sha256: str,
) -> tuple[str, dict[str, dict[str, Any]]]:
    require(original.valid_sha256(reference_sha256),
            "BLOCKED: publish the actual complete two-reference baseline SHA-256")
    if reference_sha256 == V5_REFERENCE_SHA256:
        report = original._read_verified_evidence(
            V5_REFERENCE_RELATIVE, V5_REFERENCE_SHA256,
        )
        return V5_REFERENCE_RELATIVE, original._validate_reference(
            report, provenance,
        )
    raw = original._read_bounded(
        _safe_output_path(SELF_ORACLE_RELATIVE), MAX_EVIDENCE_BYTES,
        "actual independent complete official V6 two-reference self-oracle",
    )
    require(hashlib.sha256(raw).hexdigest() == reference_sha256,
            "the externally supplied V6 reference hash is not its real full report")
    document = original.upstream._strict_json(raw, SELF_ORACLE_RELATIVE)
    require(isinstance(document, dict)
            and original.canonical(document) + b"\n" == raw,
            "the actual genuine V6 baseline is not exact canonical original JSON")
    return SELF_ORACLE_RELATIVE, _validate_v6_reference(
        document, provenance, source_sha256,
    )


def _validate_inline_guard(
    record: Any,
    *, method_check_count: Any = _METHOD_GUARD_COUNT_NOT_SUPPLIED,
) -> dict[str, Any]:
    require(isinstance(record, dict)
            and set(record) == {
                "stage07_source_sha256", "required_descendants",
                "discovered_descendants", "observations_before",
                "observations_after", "cached_alias_count",
                "helper_alias_replacement_count",
                "all_cached_aliases_same_sentinel",
                "before_matching_verified", "after_matching_verified",
            }
            and record.get("stage07_source_sha256") == owner.STAGE07_SHA256
            and record.get("required_descendants")
            == list(owner.REQUIRED_MATCHER_DESCENDANTS)
            and record.get("all_cached_aliases_same_sentinel") is True
            and record.get("before_matching_verified") is True
            and record.get("after_matching_verified") is True,
            "the authentic V10 cache guard did not protect the official methods")
    names = record.get("discovered_descendants")
    require(isinstance(names, list) and names == sorted(set(names))
            and set(owner.REQUIRED_MATCHER_DESCENDANTS) <= set(names)
            and all(isinstance(name, str) and name.startswith("re.")
                    for name in names),
            "an original cached Python regex descendant escaped the official suite")
    expected = [
        {"module": name, "blocked": True, "sentinel_identity": True,
         "cache_identity": True, "sentinel_type_exact": True}
        for name in names
    ]
    require(record.get("observations_before") == expected
            and record.get("observations_after") == expected,
            "a genuine cached regex matcher returned during an original test")
    count = record.get("cached_alias_count")
    replacement = record.get("helper_alias_replacement_count")
    require(type(count) is int and count >= 0
            and type(replacement) is int and replacement == count,
            "the authentic cached-matcher holder helper was not used exactly")
    if method_check_count is not _METHOD_GUARD_COUNT_NOT_SUPPLIED:
        require(type(method_check_count) is int
                and method_check_count == 2 * original.upstream.PUBLIC_METHODS,
                "the real sentinel was not independently verified immediately "
                "before and after all 152 original public methods")
    return record


@contextlib.contextmanager
def _official_cached_matcher_guard() -> Iterator[
    tuple[dict[str, Any], Callable[[], list[dict[str, Any]]]]
]:
    stage07 = importlib.import_module(
        "tools.python_re_universal_public_oracle_stage07",
    )
    require(Path(stage07.__file__).resolve() == ROOT / owner.STAGE07_RELATIVE
            and callable(stage07._poison_cached_module_aliases),
            "the original authenticated Stage 07 cache helper was substituted")
    sentinel_type = stage07._ForbiddenRegexModule
    unique = {
        id(value): value for value in tuple(sys.modules.values())
        if type(value) is sentinel_type
    }
    require(len(unique) == 1,
            "the official candidate lost its one original Stage 07 sentinel")
    sentinel = next(iter(unique.values()))
    cached = tuple(
        (name, module) for name, module in tuple(sys.modules.items())
        if name.startswith("re.") and isinstance(module, types.ModuleType)
        and module is not sentinel
    )
    by_name = {name: module for name, module in cached}
    require(set(owner.REQUIRED_MATCHER_DESCENDANTS) <= set(by_name)
            and len({id(module) for _, module in cached}) == len(cached),
            "the actual original cached CPython matchers disappeared or merged")
    originals = tuple(module for _, module in cached)
    bindings: list[tuple[types.ModuleType, str, types.ModuleType]] = []
    for holder in tuple(sys.modules.values()):
        if not isinstance(holder, types.ModuleType):
            continue
        try:
            entries = tuple(vars(holder).items())
        except (TypeError, ValueError):
            continue
        for alias, observed in entries:
            if any(observed is module for module in originals):
                bindings.append((holder, alias, observed))
    replaced = stage07._poison_cached_module_aliases(
        sys.modules, originals, sentinel,
    )
    require(type(replaced) is int and replaced >= 0
            and replaced == len(bindings),
            "the real original Stage 07 holder helper returned a forged count")
    names = tuple(sorted(by_name))
    record: dict[str, Any] = {
        "stage07_source_sha256": owner.STAGE07_SHA256,
        "required_descendants": list(owner.REQUIRED_MATCHER_DESCENDANTS),
        "discovered_descendants": list(names),
        "observations_before": [], "observations_after": [],
        "cached_alias_count": len(bindings),
        "helper_alias_replacement_count": replaced,
        "all_cached_aliases_same_sentinel": True,
        "before_matching_verified": False,
        "after_matching_verified": False,
    }

    def observe() -> list[dict[str, Any]]:
        require(stage07._ForbiddenRegexModule is sentinel_type
                and type(sentinel) is sentinel_type,
                "the official original Stage 07 poison was replaced")
        observations: list[dict[str, Any]] = []
        for name in names:
            module = sys.modules.get(name)
            imported = importlib.import_module(name)
            row = {
                "module": name, "blocked": True,
                "sentinel_identity": imported is sentinel,
                "cache_identity": module is sentinel,
                "sentinel_type_exact": type(module) is sentinel_type,
            }
            require(all(row[key] is True for key in (
                "blocked", "sentinel_identity", "cache_identity",
                "sentinel_type_exact",
            )), "a real cached CPython regex matcher escaped: " + name)
            observations.append(row)
        require(all(vars(holder).get(alias) is sentinel
                    for holder, alias, _ in bindings),
                "a cached original matcher holder alias escaped the sentinel")
        for holder in tuple(sys.modules.values()):
            if not isinstance(holder, types.ModuleType):
                continue
            try:
                values = tuple(vars(holder).values())
            except (TypeError, ValueError):
                continue
            require(not any(value is module for value in values
                            for module in originals),
                    "a live module still reaches an original Python matcher")
        return observations

    try:
        for name, _ in cached:
            sys.modules[name] = sentinel
        record["observations_before"] = observe()
        record["before_matching_verified"] = True
        yield record, observe
        record["observations_after"] = observe()
        record["after_matching_verified"] = True
        _validate_inline_guard(record)
    finally:
        for holder, alias, previous in reversed(bindings):
            setattr(holder, alias, previous)
        for name, module in cached:
            sys.modules[name] = module


def _execute_guarded_original_role(
    family: str, provenance: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(family in FAMILIES,
            "only a genuine independently owned official candidate is permitted")
    upstream = original.upstream
    matrix = provenance["official"]["public_method_matrix"]
    expected_path = upstream.UPSTREAM_LIB / "test" / "test_re.py"
    raw = original._read_bounded(
        expected_path, MAX_SOURCE_BYTES,
        "literal unchanged complete original CPython Lib/test/test_re.py",
    )
    require(hashlib.sha256(raw).hexdigest() == upstream.TEST_SOURCE_SHA256,
            "the literal original official upstream test source changed")
    previous_path = list(sys.path)
    output = io.StringIO()
    errors = io.StringIO()
    records: list[dict[str, Any]] = []
    active: str | None = None
    inline: dict[str, Any] | None = None
    method_guard_checks = 0
    try:
        sys.path.insert(0, str(upstream.UPSTREAM_LIB))
        baseline = importlib.import_module("re")
        constants = importlib.import_module("re._constants")
        support = importlib.import_module("test.support")
        warnings_helper = importlib.import_module("test.support.warnings_helper")
        corpus = importlib.import_module("test.re_tests")
        upstream._validate_preloaded_support(sys.modules)
        fixtures_before = upstream._verify_live_official_fixtures(
            support, warnings_helper, corpus,
        )
        require(support.bigmemtest.__module__ == "test.support"
                and support.requires_resource.__module__ == "test.support"
                and support._2G == 2**31,
                "a genuine original upstream resource decorator was replaced")
        support.verbose = 0
        support.set_memlimit("40G")
        require(support.real_max_memuse == upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES
                and support.is_resource_enabled("cpu"),
                "the original actual 40-GiB memory or CPU limit is unavailable")
        require("fork" in multiprocessing.get_all_start_methods(),
                "the original complete process regression requires actual fork")
        multiprocessing.set_start_method("fork", force=True)
        require(multiprocessing.get_start_method() == "fork",
                "the real original fork process was replaced")
        with upstream._single_memory_worker():
            with upstream._fresh_private_locales() as locale_report:
                with upstream._role_regex_module(
                    family, baseline, constants, provenance,
                ) as (regex, guard):
                    with _official_cached_matcher_guard() as (
                        inline, observe_matcher_guards,
                    ):
                        specification = importlib.util.spec_from_file_location(
                            "test.test_re", expected_path,
                        )
                        require(specification is not None
                                and specification.loader is not None,
                                "the complete original upstream source is unavailable")
                        namespace = importlib.util.module_from_spec(specification)
                        previous_official = sys.modules.get("test.test_re")
                        try:
                            sys.modules["test.test_re"] = namespace
                            with contextlib.redirect_stdout(output):
                                with contextlib.redirect_stderr(errors):
                                    require(
                                        observe_matcher_guards()
                                        == inline["observations_before"],
                                        "a real cached matcher escaped before the "
                                        "literal original test module import",
                                    )
                                    specification.loader.exec_module(namespace)
                                    require(
                                        observe_matcher_guards()
                                        == inline["observations_before"],
                                        "a real cached matcher returned during "
                                        "literal original test module import",
                                    )
                                    require(
                                        upstream._verify_live_official_fixtures(
                                            support, warnings_helper, corpus,
                                        ) == fixtures_before,
                                        "a genuine original support fixture changed",
                                    )
                                    for requirement in matrix:
                                        active = requirement["test"]
                                        require(
                                            observe_matcher_guards()
                                            == inline["observations_before"],
                                            "a cached original regex matcher "
                                            "escaped before: " + active,
                                        )
                                        method_guard_checks += 1
                                        if active in {
                                            "ExternalTests.test_re_tests",
                                            "ExternalTests.test_re_benchmarks",
                                        }:
                                            require(
                                                upstream._verify_live_official_fixtures(
                                                    support, warnings_helper, corpus,
                                                ) == fixtures_before,
                                                "the exact original 403/11 external "
                                                "fixture was replaced",
                                            )
                                        records.append(
                                            upstream._run_one_original_method(
                                                namespace, requirement,
                                                expected_path, support, "fork",
                                            )
                                        )
                                        require(
                                            observe_matcher_guards()
                                            == inline["observations_before"],
                                            "a cached original regex matcher "
                                            "returned during: " + active,
                                        )
                                        method_guard_checks += 1
                                        active = None
                                    fixtures_after = (
                                        upstream._verify_live_official_fixtures(
                                            support, warnings_helper, corpus,
                                        )
                                    )
                                    require(fixtures_after == fixtures_before,
                                            "an actual original upstream fixture changed")
                        finally:
                            if previous_official is None:
                                sys.modules.pop("test.test_re", None)
                            else:
                                sys.modules["test.test_re"] = previous_official
                    require(errors.getvalue() == "",
                            "the actual original official candidate wrote stderr")
                    require(inline is not None,
                            "the actual official cached-matcher guard disappeared")
                    _validate_inline_guard(
                        inline, method_check_count=method_guard_checks,
                    )
                    require(type(method_guard_checks) is int
                            and method_guard_checks == 2 * len(matrix)
                            and len(matrix) == 152,
                            "a real cached matcher was not checked on both sides "
                            "of every original public method")
                    summary = upstream.assess_role_records(family, records, matrix)
                    report = {
                        **summary,
                        "records": records,
                        "locale": locale_report,
                        "guard": guard,
                        "resource_provenance": {
                            "real_max_memuse": support.real_max_memuse,
                            "large_method_sizes": {
                                item["test"]: item.get("resource", {}).get(
                                    "delivered_size",
                                )
                                for item in records
                                if item["test"] in {
                                    "ReTests.test_large_search",
                                    "ReTests.test_large_subn",
                                }
                            },
                            "cpu_resource_enabled": support.is_resource_enabled("cpu"),
                            "multiprocessing_extension_available": (
                                importlib.util.find_spec("_multiprocessing")
                                is not None
                            ),
                            "multiprocessing_start_method": "fork",
                            "private_debug_fail_after": hasattr(
                                regex.Pattern, "_fail_after",
                            ),
                            "actual_upstream_corpus_cases": len(corpus.tests),
                            "actual_external_fixture_assertion_cases": len(
                                corpus.benchmarks,
                            ),
                            "exclusive_big_memory_worker": True,
                            "official_support_shim_used": False,
                            "official_test_source_rewritten": False,
                        },
                        "executed_test_source_sha256": upstream.TEST_SOURCE_SHA256,
                        "official_support_tree_sha256": (
                            upstream.OFFICIAL_SUPPORT_TREE_SHA256
                        ),
                        "live_official_fixture_provenance": fixtures_after,
                        "captured_official_stdout": output.getvalue(),
                        "captured_official_stderr": errors.getvalue(),
                        "actual_cached_matcher_method_guard_checks": (
                            method_guard_checks
                        ),
                    }
                    original._validate_role(family, report, matrix)
                    return report, dict(inline)
    except OfficialV6WorkerFailure:
        raise
    except (OfficialV6Error, original.OfficialV5Error,
            original.upstream.OfficialV4Error, OSError, MemoryError,
            UnicodeError, ValueError, KeyError, TypeError) as error:
        raise OfficialV6WorkerFailure(
            family,
            "the genuine fully guarded original upstream candidate stopped: "
            + family,
            {
                "completed_original_method_records": records,
                "completed_original_method_count": len(records),
                "active_original_method": active,
                "actual_error_type": type(error).__name__,
                "actual_error": str(error),
                "captured_official_stdout": (
                    original.upstream._bounded_failure_stream(output.getvalue())
                ),
                "captured_official_stderr": (
                    original.upstream._bounded_failure_stream(errors.getvalue())
                ),
                "actual_inline_cached_matcher_guard": inline,
                "actual_cached_matcher_method_guard_checks": method_guard_checks,
                "production_observations_invented": False,
                "performance": "NOT MEASURED",
                "holdout": "NOT ACCESSED",
            },
        ) from error
    finally:
        sys.path[:] = previous_path


def _complete_durable_proof(
    document: Any, family: str, state: Mapping[str, Any], *, deep: bool,
    original_document: Mapping[str, Any], archive_path: Path,
    archive_digest: str, archive_bytes: int,
    edge_pair: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(document, dict),
            "a genuine full V11 archive requires its separate complete owner proof")
    expected_path = (
        durable.deep_proof_target(family, True)
        if deep else durable.edge_proof_target(family, True, True)
    )
    expected_mode = "qualified-deep" if deep else "qualified-edge"
    require(document.get("schema")
            == durable.SCHEMA + "-" + expected_mode + "-durable-proof"
            and document.get("status") == "PASS"
            and document.get("result") == "PASS"
            and document.get("mode") == expected_mode
            and document.get("campaign_qualified") is True
            and document.get("proof_path")
            == expected_path.relative_to(ROOT).as_posix()
            and document.get("original_archive_path")
            == archive_path.relative_to(ROOT).as_posix()
            and document.get("original_archive_sha256") == archive_digest
            and document.get("original_archive_bytes") == archive_bytes
            and document.get("actual_v10_base_report_sha256")
            == state["audits"]["pins"]["base_report"]
            and document.get("actual_v10_strict_report_sha256")
            == state["audits"]["pins"]["strict_report"]
            and type(document.get("original_worker_returncode")) is int
            and document.get("original_worker_returncode") == 0
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED",
            "a real V11 qualified archive, exact family, or actual audit pin changed")
    producer = subprocess.CompletedProcess(
        args=["complete-durably-recorded-original-v11-producer"],
        returncode=document.get("original_worker_returncode"),
        stdout=durable.restore_complete_stream(
            document.get("original_worker_stdout"),
            "complete genuine original V11 producer stdout",
        ),
        stderr=durable.restore_complete_stream(
            document.get("original_worker_stderr"),
            "complete genuine original V11 producer stderr",
        ),
    )
    return durable.validate_durable_wrapper(
        document, family, state, qualified=True, deep=deep, passed=True,
        original=original_document, archive_path=archive_path,
        archive_sha256=archive_digest, archive_bytes=archive_bytes,
        owner_before=document.get("corrected_v10_native_owner_before"),
        owner_after=document.get("corrected_v10_native_owner_after"),
        producer=producer, qualified_edge=edge_pair,
    )


def _validate_current_family_snapshot(
    family: str, snapshot: Any, audits: Any,
) -> dict[str, Any]:
    require(family in FAMILIES and isinstance(snapshot, dict)
            and isinstance(audits, Mapping)
            and isinstance(audits.get("graph"), Mapping),
            "an actual selected V10-audited native family is incomplete")
    metadata = durable.FAMILIES[family]
    sources = snapshot.get("source_sha256_by_path")
    native = snapshot.get("native_sha256_by_path")
    audited_sources = durable.audited_graph_provenance({
        "audits": audits,
    })["all_family_source_sha256_by_path"]
    native_graph = audits["graph"].get("native_sha256_by_family")
    require(isinstance(sources, dict)
            and isinstance(native, dict)
            and isinstance(audited_sources, dict)
            and isinstance(native_graph, dict)
            and snapshot.get("family") == family
            and snapshot.get("module") == metadata["module"]
            and set(sources) == set(metadata["sources"])
            and set(native) == set(metadata["native"].values())
            and native == native_graph.get(family)
            and all(audited_sources.get(relative) == digest
                    for relative, digest in sources.items()),
            "an actual current selected source digest or mapped native ELF "
            "changed after the independently passing real V10 audits")
    return snapshot


def _authenticate_family_proofs(
    family: str, pins: Mapping[str, str], audits: Mapping[str, Any],
    legacy: Any, contract: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = durable.FAMILIES[family]
    snapshot = durable.snapshot_family(family)
    _validate_current_family_snapshot(family, snapshot, audits)

    edge_path = durable.edge_target(family, True, True)
    edge_raw = durable.read_regular(
        edge_path, "complete actual V11 qualified original edge archive",
    )
    edge_digest = hashlib.sha256(edge_raw).hexdigest()
    require(edge_digest == pins[family + "_edge_archive"],
            "the independently published complete V11 edge archive changed")
    edge_original, edge_contract, edge_passed = legacy.validate_original_edge(
        edge_raw, edge_path, family, snapshot, contract,
    )
    require(edge_passed is True and isinstance(edge_original, Mapping)
            and isinstance(edge_contract, Mapping)
            and edge_contract.get("failed") == 0
            and edge_contract.get("checks") == durable.EDGE_CHECKS
            and edge_contract.get("category_count") == durable.EDGE_CATEGORIES,
            "the complete original 223,198-observation V11 edge did not pass")
    edge_proof_path = durable.edge_proof_target(family, True, True)
    edge_proof_raw = durable.read_regular(
        edge_proof_path, "complete actual durable V11 qualified edge owner proof",
    )
    edge_proof_digest = hashlib.sha256(edge_proof_raw).hexdigest()
    require(edge_proof_digest == pins[family + "_edge_proof"],
            "the actual complete V11 edge owner-proof bytes changed")
    edge_proof = durable.decode_json(
        edge_proof_raw, "actual canonical complete V11 qualified edge owner proof",
    )
    require(durable.canonical(edge_proof) == edge_proof_raw,
            "the complete actual V11 edge owner proof is not canonical")
    history = edge_proof.get("preserved_immutable_history")
    require(isinstance(history, Mapping),
            "the complete actual V11 qualified edge omitted immutable history")
    durable.validate_historical_v10_raw_summary(
        history.get("historical_v10_unqualified_rust_original_edge"),
    )
    state: dict[str, Any] = {
        "owner": owner, "strict": strict, "snapshot": snapshot,
        "audits": audits, "history": dict(history),
    }
    _complete_durable_proof(
        edge_proof, family, state, deep=False,
        original_document=edge_original, archive_path=edge_path,
        archive_digest=edge_digest, archive_bytes=len(edge_raw),
    )
    edge_pair = {
        "status": "PASS", "campaign_qualified": True,
        "archive_path": edge_path.relative_to(ROOT).as_posix(),
        "archive_sha256": edge_digest,
        "proof_path": edge_proof_path.relative_to(ROOT).as_posix(),
        "proof_sha256": edge_proof_digest,
    }

    deep_path = durable.deep_target(family, True)
    deep_raw = durable.read_regular(
        deep_path, "complete actual V11 qualified original deep archive",
    )
    deep_digest = hashlib.sha256(deep_raw).hexdigest()
    require(deep_digest == pins[family + "_deep_archive"],
            "the independently published complete V11 deep archive changed")
    deep_original, deep_passed = legacy.validate_deep(
        deep_raw, family, edge_contract, snapshot, contract,
    )
    require(deep_passed is True and isinstance(deep_original, Mapping)
            and deep_original.get("public_mismatch_count") == 0,
            "the complete genuine current-build V11 deep suite did not pass")
    deep_proof_path = durable.deep_proof_target(family, True)
    deep_proof_raw = durable.read_regular(
        deep_proof_path, "complete actual durable V11 qualified deep owner proof",
    )
    deep_proof_digest = hashlib.sha256(deep_proof_raw).hexdigest()
    require(deep_proof_digest == pins[family + "_deep_proof"],
            "the actual complete V11 deep owner-proof bytes changed")
    deep_proof = durable.decode_json(
        deep_proof_raw, "actual canonical complete V11 qualified deep owner proof",
    )
    require(durable.canonical(deep_proof) == deep_proof_raw,
            "the complete actual V11 deep owner proof is not canonical")
    _complete_durable_proof(
        deep_proof, family, state, deep=True,
        original_document=deep_original, archive_path=deep_path,
        archive_digest=deep_digest, archive_bytes=len(deep_raw),
        edge_pair=edge_pair,
    )
    require(durable.snapshot_family(family) == snapshot,
            "an actual independently owned family changed during proof validation")
    return {
        "family": family,
        "candidate_module": metadata["module"],
        "edge_archive_path": edge_pair["archive_path"],
        "edge_archive_sha256": edge_digest,
        "edge_proof_path": edge_pair["proof_path"],
        "edge_proof_sha256": edge_proof_digest,
        "edge_checks": durable.EDGE_CHECKS,
        "edge_categories": durable.EDGE_CATEGORIES,
        "deep_archive_path": deep_path.relative_to(ROOT).as_posix(),
        "deep_archive_sha256": deep_digest,
        "deep_proof_path": deep_proof_path.relative_to(ROOT).as_posix(),
        "deep_proof_sha256": deep_proof_digest,
        "deep_checks": durable.DEEP_CHECKS,
        "deep_seeded_cases": durable.DEEP_SEEDED_CASES,
        "native_sha256_by_path": dict(snapshot["native_sha256_by_path"]),
        "source_sha256_by_path": dict(snapshot["source_sha256_by_path"]),
        "all_family_audit_qualified": True,
        "campaign_qualified": True,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def authenticate_candidate_prerequisites(
    selected: str, supplied: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _candidate_pin_values(selected, supplied)
    actual_pins = durable.validated_report_pins(
        True, pins["base_report"], pins["strict_report"],
    )
    require(isinstance(actual_pins, dict),
            "the two real V10 all-family reports were not externally pinned")
    audits = durable.audit_v11_reports(owner, strict, actual_pins)
    require(isinstance(audits, dict)
            and audits.get("pins") == actual_pins
            and audits["graph"].get("source_count") == 12
            and audits["graph"].get("native_binary_count") == 5,
            "the complete actual all-family 12-source/5-ELF graph changed")
    legacy = durable.import_frozen(
        "tools.postfinal_current_build_proofs_v8",
        durable.V8_PROOF_RELATIVE, durable.V8_PROOF_SHA256,
    )
    contract = legacy.load_contract()
    qualified = {
        family: _authenticate_family_proofs(
            family, pins, audits, legacy, contract,
        )
        for family in _chosen(selected)
    }
    return {
        "candidate_prerequisite_sha256": pins,
        "actual_v10_base_report_sha256": pins["base_report"],
        "actual_v10_strict_report_sha256": pins["strict_report"],
        "v10_native_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "v11_proof_source_sha256": V11_SOURCE_SHA256,
        "v11_proof_protocol_sha256": V11_PROTOCOL_SHA256,
        "native_sha256_by_family": audits["graph"]["native_sha256_by_family"],
        "qualified_family_proofs": qualified,
    }


WORKER_BOOTSTRAP = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_cpython_locale_oracle_v6 import worker_entry;"
    "raise SystemExit(worker_entry(sys.argv[2],sys.argv[3],sys.argv[4],"
    "sys.argv[5],sys.argv[6],sys.argv[7]))"
)


def worker_entry(
    role: str, reference_label: str, source_sha256: str,
    protocol_sha256: str, reference_sha256: str,
    encoded_candidate_pins: str,
) -> int:
    try:
        require(role in ("stdlib", *FAMILIES),
                "an unapproved genuine original V6 worker was requested")
        reference = role == "stdlib"
        require((reference and reference_label in REFERENCE_LABELS)
                or (not reference and reference_label == "candidate"),
                "the genuine V6 worker role and reference label were substituted")
        pins = original.upstream._strict_json(
            encoded_candidate_pins.encode("ascii"),
            "genuine isolated complete V6 candidate proof pins",
        )
        require(isinstance(pins, dict),
                "isolated actual V6 worker pins must be one strict JSON object")
        require(not reference or (pins == {} and reference_sha256 == ""),
                "a standard-library V6 reference cannot consume candidate evidence")
        authenticate_controller(source_sha256, protocol_sha256,
                                candidate=not reference)
        if reference:
            provenance = _original_reference_prerequisites()
            result = original._execute_original_role("stdlib", provenance)
            original._validate_role(
                "stdlib", result,
                provenance["official"]["public_method_matrix"],
            )
            owner_before = None
            owner_after = None
            inline = None
            method_guard_checks = 0
        else:
            qualified = authenticate_candidate_prerequisites(role, pins)
            provenance = _original_reference_prerequisites()
            _, references = _read_reference(
                reference_sha256, provenance, source_sha256,
            )
            provenance.update(qualified)
            expected = qualified["native_sha256_by_family"][role]
            snapshot = durable.snapshot_family(role)
            proven_snapshot = qualified["qualified_family_proofs"][role]
            require(snapshot["family"] == role
                    and snapshot["native_sha256_by_path"] == expected
                    and snapshot["native_sha256_by_path"]
                    == proven_snapshot["native_sha256_by_path"]
                    and snapshot["source_sha256_by_path"]
                    == proven_snapshot["source_sha256_by_path"],
                    "an actual V10-audited candidate source or native ELF "
                    "changed before original official tests")
            owner_before = durable.validate_owner(
                owner, owner.run_native_worker(role, expected), role, expected,
            )
            require(durable.snapshot_family(role) == snapshot,
                    "the real before-suite V10 native owner changed its family")
            result, inline = _execute_guarded_original_role(role, provenance)
            method_guard_checks = result.get(
                "actual_cached_matcher_method_guard_checks",
            )
            require(original._status_vector(result["records"])
                    == original._status_vector(
                        references["reference_a"]["records"],
                    )
                    == original._status_vector(
                        references["reference_b"]["records"],
                    ),
                    "the actual original native vector differs from both references")
            owner_after = durable.validate_owner(
                owner, owner.run_native_worker(role, expected), role, expected,
            )
            require(durable.snapshot_family(role) == snapshot,
                    "the native source or real mapped ELF changed during the suite")
            _validate_inline_guard(
                inline, method_check_count=method_guard_checks,
            )
        document = {
            "schema": SCHEMA + "-actual-worker",
            "status": "PASS", "python": "3.14.6",
            "role": role, "reference_label": reference_label,
            "source_sha256": source_sha256,
            "protocol_sha256": protocol_sha256,
            "reference_sha256": reference_sha256 or None,
            "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
            "role_report": result,
            "actual_v10_native_owner_before": owner_before,
            "actual_v10_native_owner_after": owner_after,
            "actual_inline_cached_matcher_guards": inline,
            "actual_inline_cached_matcher_method_guard_checks": (
                method_guard_checks
            ),
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
    except OfficialV6WorkerFailure as error:
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL", "role": error.role,
            "reference_label": reference_label,
            "reason": str(error), "details": error.details,
            "production_observations_invented": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    except (OfficialV6Error, original.OfficialV5Error,
            original.upstream.OfficialV4Error,
            OSError, MemoryError, subprocess.SubprocessError,
            UnicodeError, ValueError, KeyError, TypeError, AssertionError) as error:
        details = getattr(error, "evidence", None)
        print(json.dumps({
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL", "role": role,
            "reference_label": reference_label,
            "actual_error_type": type(error).__name__,
            "reason": str(error),
            "actual_native_owner_failure": (
                dict(details) if isinstance(details, Mapping) else None
            ),
            "production_observations_invented": False,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, sort_keys=True, separators=(",", ":")))
        return 2
    print(json.dumps(document, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")))
    return 0


def _run_isolated_worker(
    role: str, reference_label: str, source_sha256: str,
    reference_sha256: str, candidate_pins: Mapping[str, str],
) -> dict[str, Any]:
    require((role == "stdlib" and reference_label in REFERENCE_LABELS
             and not candidate_pins and reference_sha256 == "")
            or (role in FAMILIES and reference_label == "candidate"
                and original.valid_sha256(reference_sha256)
                and bool(candidate_pins)),
            "an isolated original V6 reference or genuine candidate is required")
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "PATH": "/usr/bin:/bin",
    }
    try:
        completed = subprocess.run(
            [str(original.upstream.PINNED_CPYTHON), "-I", "-B", "-c",
             WORKER_BOOTSTRAP, str(ROOT), role, reference_label,
             source_sha256, PROTOCOL_SHA256, reference_sha256,
             original.canonical(dict(candidate_pins)).decode("ascii")],
            cwd=str(ROOT), env=environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=WORKER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise OfficialV6WorkerFailure(
            role, "the genuine complete original V6 worker timed out: " + role,
            {
                "status": "TIMEOUT", "reference_label": reference_label,
                "timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "stdout": original.upstream._bounded_failure_stream(error.stdout),
                "stderr": original.upstream._bounded_failure_stream(error.stderr),
                "production_observations_invented": False,
            },
        ) from error
    stdout = original.upstream._bounded_failure_stream(completed.stdout)
    stderr = original.upstream._bounded_failure_stream(completed.stderr)
    details: dict[str, Any] = {
        "reference_label": reference_label,
        "returncode": completed.returncode,
        "signal": -completed.returncode if completed.returncode < 0 else None,
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stdout_sha256": stdout["sha256"],
        "stderr_sha256": stderr["sha256"],
        "stdout": stdout, "stderr": stderr,
        "production_observations_invented": False,
    }
    if (len(completed.stdout) > MAX_WORKER_OUTPUT_BYTES
            or len(completed.stderr) > MAX_WORKER_OUTPUT_BYTES):
        raise OfficialV6WorkerFailure(
            role, "the genuine V6 worker exceeded complete stream bounds", details,
        )
    try:
        document = original.upstream._strict_json(
            completed.stdout, "genuine complete original V6 worker " + role,
        )
    except original.upstream.OfficialV4Error as error:
        details["actual_json_error"] = str(error)
        raise OfficialV6WorkerFailure(
            role, "a real original V6 worker returned invalid evidence", details,
        ) from error
    if isinstance(document, Mapping):
        details["actual_worker_document"] = dict(document)
    if completed.returncode != 0 or completed.stderr:
        raise OfficialV6WorkerFailure(
            role, "the genuine isolated V6 worker failed or wrote stderr", details,
        )
    require(isinstance(document, dict)
            and document.get("schema") == SCHEMA + "-actual-worker"
            and document.get("status") == "PASS"
            and document.get("role") == role
            and document.get("reference_label") == reference_label
            and document.get("source_sha256") == source_sha256
            and document.get("protocol_sha256") == PROTOCOL_SHA256
            and document.get("reference_sha256") == (reference_sha256 or None)
            and document.get("public_method_matrix_sha256")
            == METHOD_MATRIX_SHA256
            and document.get("performance") == "NOT MEASURED"
            and document.get("holdout") == "NOT ACCESSED"
            and isinstance(document.get("role_report"), dict),
            "the complete actual isolated V6 worker changed frozen provenance")
    if role == "stdlib":
        require(document.get("actual_v10_native_owner_before") is None
                and document.get("actual_v10_native_owner_after") is None
                and document.get("actual_inline_cached_matcher_guards") is None
                and type(document.get(
                    "actual_inline_cached_matcher_method_guard_checks",
                )) is int
                and document["actual_inline_cached_matcher_method_guard_checks"]
                == 0,
                "a stdlib-only reference cannot execute native proof workers")
    else:
        expected = candidate_pins
        require(bool(expected), "an original native worker lost its proof pins")
        count = document.get("actual_inline_cached_matcher_method_guard_checks")
        require(document["role_report"].get(
            "actual_cached_matcher_method_guard_checks",
        ) == count,
                "the original candidate changed its real per-method guard count")
        _validate_inline_guard(
            document.get("actual_inline_cached_matcher_guards"),
            method_check_count=count,
        )
    return document


def run_self_oracle(source_sha256: str) -> dict[str, Any]:
    authenticate_controller(source_sha256, PROTOCOL_SHA256, candidate=False)
    _preflight_fresh_outputs((
        SELF_ORACLE_RELATIVE, SELF_ORACLE_FAILURE_RELATIVE,
    ))
    provenance = _original_reference_prerequisites()
    matrix = provenance["official"]["public_method_matrix"]
    observed: dict[str, dict[str, Any]] = {}
    for label in REFERENCE_LABELS:
        try:
            worker = _run_isolated_worker(
                "stdlib", label, source_sha256, "", {},
            )
            report = worker["role_report"]
            original._validate_role("stdlib", report, matrix)
            observed[label] = report
        except (OfficialV6WorkerFailure, OfficialV6Error,
                original.OfficialV5Error) as error:
            details = (
                dict(error.details) if isinstance(error, OfficialV6WorkerFailure)
                else {"actual_validation_failure": str(error)}
            )
            details.update({
                "actual_completed_reference_roles": observed,
                "actual_failed_reference_label": label,
            })
            raise OfficialV6WorkerFailure(
                "stdlib", "the actual independent Python reference failed: " + label,
                details,
            ) from error
    vector = original._status_vector(observed["reference_a"]["records"])
    require(vector == original._status_vector(
        observed["reference_b"]["records"],
    ), "the two genuine full original Python reference processes disagree")
    document = {
        **_base_document(provenance, source_sha256),
        "schema": SCHEMA + "-self-oracle",
        "status": "PASS",
        "actual_independent_reference_count": 2,
        "reference_status_vector_sha256": original.digest(vector),
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "roles": observed,
    }
    _validate_v6_reference(document, provenance, source_sha256)
    _exclusive_write(document, SELF_ORACLE_RELATIVE)
    return document


def run_candidates(
    selected: str, source_sha256: str,
    reference_sha256: str, supplied: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _candidate_pin_values(selected, supplied)
    authenticate_controller(source_sha256, PROTOCOL_SHA256, candidate=True)
    qualified = authenticate_candidate_prerequisites(selected, pins)
    provenance = _original_reference_prerequisites()
    reference_path, references = _read_reference(
        reference_sha256, provenance, source_sha256,
    )
    provenance.update(qualified)
    chosen = _chosen(selected)
    destinations = tuple(
        destination for family in chosen
        for destination in (
            ROLE_REPORT_RELATIVES[family], ROLE_FAILURE_RELATIVES[family],
        )
    )
    if selected == "all":
        destinations += (REPORT_RELATIVE, REPORT_FAILURE_RELATIVE)
    _preflight_fresh_outputs(destinations)
    matrix = provenance["official"]["public_method_matrix"]
    baseline_vector = original._status_vector(
        references["reference_a"]["records"],
    )
    require(baseline_vector == original._status_vector(
        references["reference_b"]["records"],
    ) and len(baseline_vector) == 152,
            "the two independent complete original CPython roles disagree")
    reports: dict[str, Any] = dict(references)
    workers: dict[str, Any] = {}
    for family in chosen:
        worker: dict[str, Any] | None = None
        try:
            family_pins = {
                key: value for key, value in pins.items()
                if key in {"base_report", "strict_report"}
                or key.startswith(family + "_")
            }
            worker = _run_isolated_worker(
                family, "candidate", source_sha256,
                reference_sha256, family_pins,
            )
            role = worker["role_report"]
            original._validate_role(family, role, matrix)
            require(original._status_vector(role["records"]) == baseline_vector,
                    "an actual original candidate differs from both Python roles")
            expected = qualified["native_sha256_by_family"][family]
            for label in ("actual_v10_native_owner_before",
                          "actual_v10_native_owner_after"):
                durable.validate_owner(owner, worker.get(label), family, expected)
            proven_snapshot = qualified["qualified_family_proofs"][family]
            actual_snapshot = durable.snapshot_family(family)
            require(actual_snapshot["source_sha256_by_path"]
                    == proven_snapshot["source_sha256_by_path"]
                    and actual_snapshot["native_sha256_by_path"]
                    == proven_snapshot["native_sha256_by_path"],
                    "an audited real candidate source or native ELF changed "
                    "during the original isolated official worker")
            method_guard_checks = worker.get(
                "actual_inline_cached_matcher_method_guard_checks",
            )
            require(role.get("actual_cached_matcher_method_guard_checks")
                    == method_guard_checks,
                    "the official role substituted its genuine per-method guards")
            _validate_inline_guard(
                worker.get("actual_inline_cached_matcher_guards"),
                method_check_count=method_guard_checks,
            )
        except (OfficialV6WorkerFailure, OfficialV6Error,
                original.OfficialV5Error,
                OSError, UnicodeError, ValueError, KeyError,
                TypeError, AssertionError) as error:
            details = (
                dict(error.details) if isinstance(error, OfficialV6WorkerFailure)
                else {"actual_validation_failure": str(error),
                      "actual_error_type": type(error).__name__}
            )
            if worker is not None:
                details["complete_actual_original_worker"] = worker
            details["actual_completed_candidate_roles"] = {
                name: result for name, result in reports.items()
                if name in FAMILIES
            }
            raise OfficialV6WorkerFailure(
                family, "the fully guarded actual original candidate failed: "
                + family, details,
            ) from error
        role_document = {
            **_base_document(provenance, source_sha256),
            "schema": SCHEMA + "-actual-" + family + "-role",
            "status": "PASS",
            "reference_path": reference_path,
            "reference_sha256": reference_sha256,
            "reference_status_vector_sha256": original.digest(baseline_vector),
            "candidate_prerequisite_sha256": dict(family_pins),
            "actual_v10_base_report_sha256": pins["base_report"],
            "actual_v10_strict_report_sha256": pins["strict_report"],
            "v11_proof_source_sha256": V11_SOURCE_SHA256,
            "v11_proof_protocol_sha256": V11_PROTOCOL_SHA256,
            "qualified_family_proof": qualified["qualified_family_proofs"][family],
            "actual_v10_native_owner_before": worker[
                "actual_v10_native_owner_before"
            ],
            "actual_v10_native_owner_after": worker[
                "actual_v10_native_owner_after"
            ],
            "actual_inline_cached_matcher_guards": worker[
                "actual_inline_cached_matcher_guards"
            ],
            "actual_inline_cached_matcher_method_guard_checks": worker[
                "actual_inline_cached_matcher_method_guard_checks"
            ],
            "roles": {family: role},
        }
        try:
            _exclusive_write(role_document, ROLE_REPORT_RELATIVES[family])
        except (OfficialV6Error, OSError, ValueError, TypeError) as error:
            raise OfficialV6WorkerFailure(
                family,
                "the genuine completed V6 role could not be durably published: "
                + family,
                {
                    "actual_error_type": type(error).__name__,
                    "actual_error": str(error),
                    "complete_actual_original_worker": worker,
                    "complete_actual_unpublished_role_document": role_document,
                    "actual_completed_candidate_roles": {
                        name: result for name, result in reports.items()
                        if name in FAMILIES
                    },
                    "production_observations_invented": False,
                },
            ) from error
        reports[family] = role
        workers[family] = {
            "before": worker["actual_v10_native_owner_before"],
            "after": worker["actual_v10_native_owner_after"],
            "inline": worker["actual_inline_cached_matcher_guards"],
            "inline_method_guard_checks": worker[
                "actual_inline_cached_matcher_method_guard_checks"
            ],
        }
    if selected != "all":
        return {
            "schema": SCHEMA + "-single-candidate-result",
            "status": "PASS", "role": selected,
            "path": ROLE_REPORT_RELATIVES[selected],
            "reference_path": reference_path,
            "reference_sha256": reference_sha256,
            "original_public_methods": 152,
            "actual_native_owners": 2,
            "cached_matchers_guarded_during_original_methods": True,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }
    require(set(reports) == {*REFERENCE_LABELS, *FAMILIES}
            and set(workers) == set(FAMILIES),
            "both actual full references and all three native families are required")
    document = {
        **_base_document(provenance, source_sha256),
        "schema": SCHEMA, "status": "PASS",
        "reference_path": reference_path,
        "reference_sha256": reference_sha256,
        "actual_independent_reference_count": 2,
        "reference_status_vector_sha256": original.digest(baseline_vector),
        "candidate_prerequisite_sha256": pins,
        "actual_v10_base_report_sha256": pins["base_report"],
        "actual_v10_strict_report_sha256": pins["strict_report"],
        "v10_native_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "v11_proof_source_sha256": V11_SOURCE_SHA256,
        "v11_proof_protocol_sha256": V11_PROTOCOL_SHA256,
        "qualified_family_proofs": qualified["qualified_family_proofs"],
        "actual_v10_native_owner_workers": workers,
        "all_official_method_contexts_cache_guarded": True,
        "cached_matcher_guard_checks_per_original_role": 304,
        "roles": reports,
    }
    try:
        _exclusive_write(document, REPORT_RELATIVE)
    except (OfficialV6Error, OSError, ValueError, TypeError) as error:
        raise OfficialV6WorkerFailure(
            "all",
            "all genuine V6 candidates completed but the full report could "
            "not be durably published",
            {
                "actual_error_type": type(error).__name__,
                "actual_error": str(error),
                "complete_actual_unpublished_all_family_document": document,
                "actual_completed_candidate_roles": {
                    name: reports[name] for name in FAMILIES
                },
                "actual_v10_native_owner_workers": workers,
                "production_observations_invented": False,
            },
        ) from error
    return document


def _synthetic_digest(label: str) -> str:
    return hashlib.sha256(("candidate-free-official-v6:" + label).encode(
        "ascii",
    )).hexdigest()


def _synthetic_reference(
    matrix: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    roles = {
        name: original._synthetic_release("stdlib", matrix)
        for name in REFERENCE_LABELS
    }
    vector = original._status_vector(roles["reference_a"]["records"])
    provenance: dict[str, Any] = {
        "source_sha256": V5_SOURCE_SHA256,
        "protocol_sha256": V5_PROTOCOL_SHA256,
        "official": {"public_method_matrix": matrix},
    }
    document = {
        "schema": original.SCHEMA + "-self-oracle",
        "status": "PASS", "synthetic": False,
        "python": "3.14.6",
        "source_sha256": V5_SOURCE_SHA256,
        "protocol_sha256": V5_PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "actual_independent_reference_count": 2,
        "old_v7_campaign_prerequisite": False,
        "reference_candidate_imports": 0,
        "reference_candidate_audits_read": 0,
        "reference_candidate_proofs_read": 0,
        "reference_holdout_cases_read": 0,
        "reference_status_vector_sha256": original.digest(vector),
        "roles": roles,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }
    return document, provenance


def _synthetic_pins(selected: str) -> dict[str, str]:
    return {
        "base_report": _synthetic_digest("actual-base-report-shape"),
        "strict_report": _synthetic_digest("actual-strict-report-shape"),
        **{
            family + "_" + kind:
            _synthetic_digest("actual-proof-shape:" + family + ":" + kind)
            for family in _chosen(selected) for kind in PROOF_KINDS
        },
    }


def _synthetic_inline_guard() -> dict[str, Any]:
    names = list(owner.REQUIRED_MATCHER_DESCENDANTS)
    rows = [
        {"module": name, "blocked": True, "sentinel_identity": True,
         "cache_identity": True, "sentinel_type_exact": True}
        for name in names
    ]
    return {
        "stage07_source_sha256": owner.STAGE07_SHA256,
        "required_descendants": list(names),
        "discovered_descendants": list(names),
        "observations_before": copy.deepcopy(rows),
        "observations_after": copy.deepcopy(rows),
        "cached_alias_count": 0,
        "helper_alias_replacement_count": 0,
        "all_cached_aliases_same_sentinel": True,
        "before_matching_verified": True,
        "after_matching_verified": True,
    }


def _synthetic_durable_pair(
    family: str, *, deep: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    state, observed = durable.synthetic_durable_state(family, qualified=True)
    metadata = durable.FAMILIES[family]
    original_document: dict[str, Any]
    if deep:
        original_document = {
            "candidate_sha256": durable.DEEP_REFERENCE_SHA256,
            "public_mismatch_count": 0,
            "public_mismatch_family_counts": {family: 0},
        }
        archive = durable.deep_target(family, True)
    else:
        original_document = {
            "actual_sha256": durable.EDGE_REFERENCE_SHA256,
            "failed": 0, "failures": [],
        }
        archive = durable.edge_target(family, True, True)
    archive_digest = _synthetic_digest(
        "synthetic-original:" + family + ":" + ("deep" if deep else "edge"),
    )
    archive_bytes = 137
    edge_pair = None
    if deep:
        edge_pair = {
            "status": "PASS", "campaign_qualified": True,
            "archive_path": durable.edge_target(
                family, True, True,
            ).relative_to(ROOT).as_posix(),
            "archive_sha256": _synthetic_digest(
                "synthetic-original:" + family + ":edge",
            ),
            "proof_path": durable.edge_proof_target(
                family, True, True,
            ).relative_to(ROOT).as_posix(),
            "proof_sha256": _synthetic_digest(
                "synthetic-durable-proof:" + family + ":edge",
            ),
        }
    producer = subprocess.CompletedProcess(
        args=["candidate-free-in-memory-only"], returncode=0,
        stdout=b"candidate-free-synthetic-original\n", stderr=b"",
    )
    wrapper = durable.build_durable_wrapper(
        family, state, qualified=True, deep=deep, passed=True,
        original=original_document, archive_path=archive,
        archive_sha256=archive_digest, archive_bytes=archive_bytes,
        owner_before=observed, owner_after=copy.deepcopy(observed),
        producer=producer, qualified_edge=edge_pair,
    )
    require(wrapper.get("candidate_module") == metadata["module"],
            "an in-memory-only V11 wrapper substituted its family")
    return wrapper, state, original_document, {
        "archive_path": archive,
        "archive_sha256": archive_digest,
        "archive_bytes": archive_bytes,
        "edge_pair": edge_pair,
    }


def source_self_test() -> dict[str, Any]:
    verify_runtime()
    inherited = original.source_self_test()
    require(inherited.get("status") == "PASS"
            and inherited.get("passed") is True
            and inherited.get("check_count", 0) >= 69
            and inherited.get("candidate_imports") == 0
            and inherited.get("subprocesses") == 0
            and inherited.get("file_reads") == 0
            and inherited.get("file_writes") == 0
            and inherited.get("clock_samples") == 0
            and inherited.get("actual_reference_workers") == 0
            and inherited.get("actual_official_roles_run") == 0,
            "the complete immutable original V5 source-only controls failed")
    _load_candidate_modules()
    verify_runtime(candidate=True)
    checks: list[dict[str, Any]] = [
        {"name": "immutable-v5:" + item["name"],
         "passed": item.get("passed") is True}
        for item in inherited["checks"]
    ]

    def accept(name: str, condition: Any) -> None:
        require(not any(row["name"] == name for row in checks),
                "an original V6 source-only poison control was duplicated")
        checks.append({"name": name, "passed": bool(condition)})

    def rejected(name: str, action: Callable[[], Any]) -> None:
        try:
            action()
        except (OfficialV6Error, original.OfficialV5Error,
                original.upstream.OfficialV4Error,
                AssertionError, OSError,
                UnicodeError, ValueError, KeyError, TypeError, ImportError):
            accept(name, True)
        else:
            accept(name, False)

    with original._source_only_boundary() as effects:
        matrix = original._synthetic_matrix()
        reference, provenance = _synthetic_reference(matrix)
        accepted_reference = original._validate_reference(
            reference, provenance,
        )
        synthetic_v6_source = _synthetic_digest("independent-v6-source-shape")
        synthetic_v6_reference = {
            **_base_document(provenance, synthetic_v6_source),
            "schema": SCHEMA + "-self-oracle",
            "status": "PASS",
            "actual_independent_reference_count": 2,
            "reference_candidate_imports": 0,
            "reference_candidate_audits_read": 0,
            "reference_candidate_proofs_read": 0,
            "reference_holdout_cases_read": 0,
            "reference_status_vector_sha256": reference[
                "reference_status_vector_sha256"
            ],
            "roles": copy.deepcopy(reference["roles"]),
        }
        accepted_v6_reference = _validate_v6_reference(
            synthetic_v6_reference, provenance, synthetic_v6_source,
        )
        accept("preserve-actual-immutable-v5-source-hash", V5_SOURCE_SHA256
               == durable.OFFICIAL_V5_SOURCE_SHA256)
        accept("preserve-actual-immutable-v5-protocol-hash", V5_PROTOCOL_SHA256
               == durable.OFFICIAL_V5_PROTOCOL_SHA256)
        accept("preserve-actual-immutable-v5-two-reference-hash",
               V5_REFERENCE_SHA256 == durable.BASELINE_SHA256)
        accept("freeze-only-corrected-final-immutable-v11-source",
               V11_SOURCE_SHA256
               == "2895dd28b3dc69985cc0f6f8575398e8b8b10f58141f0612645a687478da9f04")
        accept("freeze-only-corrected-final-immutable-v11-protocol",
               V11_PROTOCOL_SHA256 == durable.REFRESH_PROTOCOL_SHA256)
        accept("freeze-actual-corrected-v10-base-owner-source",
               V10_OWNER_SOURCE_SHA256 == strict.BASE_SOURCE_SHA256)
        accept("freeze-actual-corrected-v10-strict-source",
               V10_STRICT_SOURCE_SHA256 == durable.V10_STRICT_SOURCE_SHA256)
        accept("freeze-actual-original-stage07-matcher-helper",
               owner.STAGE07_SHA256 == durable.STAGE07_SHA256)
        accept("preserve-all-165-authentic-original-upstream-methods",
               original.upstream.ORIGINAL_METHODS == 165)
        accept("preserve-exactly-152-original-public-methods",
               original.upstream.PUBLIC_METHODS == 152 and len(matrix) == 152)
        accept("account-for-13-original-private-methods-separately",
               original.upstream.PRIVATE_METHODS == 13
               and len(original.upstream.PRIVATE_CLASS_WAIVERS) == 2)
        accept("never-waive-an-original-public-method",
               not original.upstream.PUBLIC_METHOD_WAIVERS)
        accept("preserve-all-26-genuine-original-support-files",
               len(original.upstream.OFFICIAL_SUPPORT_MODULES) == 26)
        accept("preserve-all-403-genuine-original-corpus-cases",
               original.upstream.CORPUS_CASES == 403)
        accept("preserve-all-11-genuine-original-external-fixtures",
               original.upstream.EXTERNAL_FIXTURE_ASSERTION_CASES == 11)
        accept("retain-the-real-original-40-gibibyte-resource-limit",
               original.upstream.CONFIGURED_OFFICIAL_MEMORY_BYTES
               == 40 * 1024**3)
        accept("retain-the-real-original-36-gibibyte-subn-requirement",
               original.upstream.REQUIRED_OFFICIAL_SUBN_MEMORY_BYTES
               == 18 * 2**31)
        accept("retain-two-distinct-genuine-stdlib-reference-labels",
               REFERENCE_LABELS == ("reference_a", "reference_b"))
        accept("validate-the-complete-actual-v5-reference-contract-in-memory",
               set(accepted_reference) == set(REFERENCE_LABELS))
        accept("validate-the-complete-independent-v6-reference-contract-in-memory",
               set(accepted_v6_reference) == set(REFERENCE_LABELS))
        accept("keep-both-official-reference-workers-independent-of-audits",
               "_load_candidate_modules" not in run_self_oracle.__code__.co_names
               and "authenticate_candidate_prerequisites"
               not in run_self_oracle.__code__.co_names)
        accept("retain-exact-151-applicable-and-one-private-debug-condition",
               all(role.get("applicable") == 151
                   and role.get("passed") == 151
                   and role.get("named_private_debug_skips") == 1
                   for role in accepted_reference.values()))
        for index, identity in enumerate(original.upstream.PUBLIC_ORIGINAL_METHODS):
            accept("retain-unchanged-public-method-at-exact-source-index:"
                   + str(index) + ":" + identity,
                   matrix[index]["test"] == identity
                   and original.valid_sha256(matrix[index]["source_ast_sha256"]))

        def poison_reference(name: str,
                             transform: Callable[[dict[str, Any]], None]) -> None:
            changed = copy.deepcopy(reference)
            transform(changed)
            rejected(name, lambda: original._validate_reference(
                changed, provenance,
            ))

        for key, wrong in (
            ("status", "FAIL"), ("synthetic", True),
            ("python", "3.14.5"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("public_method_matrix_sha256", "0" * 64),
            ("actual_independent_reference_count", 1),
            ("reference_candidate_imports", 1),
            ("reference_candidate_audits_read", 1),
            ("reference_candidate_proofs_read", 1),
            ("reference_holdout_cases_read", 1),
            ("reference_status_vector_sha256", "0" * 64),
            ("performance", "measured"),
        ):
            poison_reference("reject-substituted-genuine-two-reference:" + key,
                             lambda value, key=key, wrong=wrong:
                             value.update({key: wrong}))

        def poison_v6_reference(
            name: str, transform: Callable[[dict[str, Any]], None],
        ) -> None:
            changed = copy.deepcopy(synthetic_v6_reference)
            transform(changed)
            rejected(name, lambda: _validate_v6_reference(
                changed, provenance, synthetic_v6_source,
            ))

        for key, wrong in (
            ("schema", SCHEMA + "-forged"), ("status", "FAIL"),
            ("synthetic", True), ("python", "3.14.5"),
            ("source_path", V5_SOURCE_RELATIVE),
            ("source_sha256", "0" * 64),
            ("protocol_path", V5_PROTOCOL_RELATIVE),
            ("protocol_sha256", "0" * 64),
            ("immutable_v5_source_sha256", "0" * 64),
            ("immutable_v5_protocol_sha256", "0" * 64),
            ("public_method_matrix_sha256", "0" * 64),
            ("actual_independent_reference_count", 1),
            ("reference_candidate_imports", 1),
            ("reference_candidate_audits_read", 1),
            ("reference_candidate_proofs_read", 1),
            ("reference_holdout_cases_read", 1),
            ("reference_status_vector_sha256", "0" * 64),
            ("performance", "MEASURED"), ("holdout", "ACCESSED"),
        ):
            poison_v6_reference(
                "reject-forged-real-v6-two-reference:" + key,
                lambda value, key=key, wrong=wrong: value.update({key: wrong}),
            )
        for label in REFERENCE_LABELS:
            poison_v6_reference(
                "reject-missing-real-v6-independent-reference:" + label,
                lambda value, label=label: value["roles"].pop(label),
            )
            poison_v6_reference(
                "reject-dropped-real-v6-public-method:" + label,
                lambda value, label=label:
                value["roles"][label]["records"].pop(),
            )
            poison_v6_reference(
                "reject-reordered-real-v6-public-method:" + label,
                lambda value, label=label:
                value["roles"][label]["records"].reverse(),
            )
        for label in REFERENCE_LABELS:
            poison_reference("reject-omitted-independent-original-reference:" + label,
                             lambda value, label=label:
                             value["roles"].pop(label))
            poison_reference("reject-missing-original-public-method:" + label,
                             lambda value, label=label:
                             value["roles"][label]["records"].pop())
            poison_reference("reject-reordered-original-public-method:" + label,
                             lambda value, label=label:
                             value["roles"][label]["records"].reverse())
            poison_reference("reject-unexplained-original-public-skip:" + label,
                             lambda value, label=label:
                             value["roles"][label]["records"][0].update({
                                 "status": "SKIP", "reason": "synthetic poison",
                             }))
            for status in ("FAIL", "ERROR", "TIMEOUT", "CRASH"):
                poison_reference(
                    "reject-genuine-reference-method-" + status.lower()
                    + ":" + label,
                    lambda value, label=label, status=status:
                    value["roles"][label]["records"][0].update({
                        "status": status, "reason": "source-only poison",
                    }),
                )

        inline = _synthetic_inline_guard()
        accept("accept-genuine-zero-cached-holder-aliases",
               _validate_inline_guard(copy.deepcopy(inline)) == inline)
        accept("accept-exact-304-genuine-method-adjacent-cache-guards",
               _validate_inline_guard(
                   copy.deepcopy(inline), method_check_count=304,
               ) == inline)
        for wrong in (0, 303, 305, -1, False, True, None, "304"):
            rejected(
                "reject-forged-or-omitted-method-adjacent-cache-count:"
                + repr(wrong),
                lambda wrong=wrong: _validate_inline_guard(
                    copy.deepcopy(inline), method_check_count=wrong,
                ),
            )
        for count in (1, 2):
            positive = copy.deepcopy(inline)
            positive.update({
                "cached_alias_count": count,
                "helper_alias_replacement_count": count,
            })
            accept("accept-exact-real-cached-holder-alias-count:" + str(count),
                   _validate_inline_guard(positive) == positive)
        for field in ("cached_alias_count", "helper_alias_replacement_count"):
            for wrong in (-1, False, True, 3, None, "0"):
                altered = copy.deepcopy(inline)
                altered[field] = wrong
                rejected("reject-forged-official-cache-helper:" + field
                         + ":" + repr(wrong),
                         lambda altered=altered: _validate_inline_guard(altered))
        for key in (
            "stage07_source_sha256", "required_descendants",
            "discovered_descendants", "observations_before",
            "observations_after", "all_cached_aliases_same_sentinel",
            "before_matching_verified", "after_matching_verified",
        ):
            omitted = copy.deepcopy(inline)
            omitted.pop(key)
            rejected("reject-omitted-real-in-method-matcher-guard:" + key,
                     lambda omitted=omitted: _validate_inline_guard(omitted))
        for phase in ("observations_before", "observations_after"):
            for field in ("blocked", "sentinel_identity", "cache_identity",
                          "sentinel_type_exact"):
                altered = copy.deepcopy(inline)
                altered[phase][0][field] = False
                rejected("reject-restored-actual-in-method-matcher:"
                         + phase + ":" + field,
                         lambda altered=altered:
                         _validate_inline_guard(altered))
        altered_names = copy.deepcopy(inline)
        altered_names["discovered_descendants"].remove("re._compiler")
        rejected("reject-live-cached-re-compiler-during-original-tests",
                 lambda: _validate_inline_guard(altered_names))
        altered_names = copy.deepcopy(inline)
        altered_names["discovered_descendants"].remove("re._parser")
        rejected("reject-live-cached-re-parser-during-original-tests",
                 lambda: _validate_inline_guard(altered_names))

        for selected in (*FAMILIES, "all"):
            pins = _synthetic_pins(selected)
            validated = _candidate_pin_values(selected, pins)
            expected_count = 2 + 4 * len(_chosen(selected))
            accept("require-four-exact-durable-artifacts-per-family:" + selected,
                   len(validated) == expected_count)
            for key in tuple(pins):
                changed = dict(pins)
                changed.pop(key)
                rejected("reject-each-missing-real-proof-pin:"
                         + selected + ":" + key,
                         lambda changed=changed, selected=selected:
                         _candidate_pin_values(selected, changed))
            duplicated = dict(pins)
            duplicated[next(iter(key for key in pins
                                if key not in {"base_report", "strict_report"}))] = (
                pins["base_report"]
            )
            rejected("reject-cross-artifact-reused-actual-hash:" + selected,
                     lambda duplicated=duplicated, selected=selected:
                     _candidate_pin_values(selected, duplicated))
            guessed = dict(pins)
            guessed["base_report"] = V10_OWNER_SOURCE_SHA256
            rejected("reject-owner-source-as-actual-report:" + selected,
                     lambda guessed=guessed, selected=selected:
                     _candidate_pin_values(selected, guessed))

        for family in FAMILIES:
            synthetic_state, _ = durable.synthetic_durable_state(
                family, qualified=True,
            )
            current = copy.deepcopy(synthetic_state["snapshot"])
            audited = copy.deepcopy(synthetic_state["audits"])
            accept("accept-exact-complete-v10-audited-family-source-digests:"
                   + family,
                   _validate_current_family_snapshot(
                       family, copy.deepcopy(current), audited,
                   ) == current)
            for relative in tuple(current["source_sha256_by_path"]):
                altered = copy.deepcopy(current)
                altered["source_sha256_by_path"][relative] = "0" * 64
                rejected("reject-changed-actual-v10-audited-source-digest:"
                         + family + ":" + relative,
                         lambda altered=altered, audited=audited,
                         family=family: _validate_current_family_snapshot(
                             family, altered, audited,
                         ))
            for relative in tuple(current["native_sha256_by_path"]):
                altered = copy.deepcopy(current)
                altered["native_sha256_by_path"][relative] = "0" * 64
                rejected("reject-changed-actual-v10-audited-native-elf:"
                         + family + ":" + relative,
                         lambda altered=altered, audited=audited,
                         family=family: _validate_current_family_snapshot(
                             family, altered, audited,
                         ))
            for key, wrong in (("family", "forged"),
                               ("module", "candidates.forged")):
                altered = copy.deepcopy(current)
                altered[key] = wrong
                rejected("reject-substituted-real-audited-family:"
                         + family + ":" + key,
                         lambda altered=altered, audited=audited,
                         family=family: _validate_current_family_snapshot(
                             family, altered, audited,
                         ))
            altered_audit = copy.deepcopy(audited)
            altered_audit["base"]["families"][family][
                "python_source"
            ]["sha256"] = "0" * 64
            rejected("reject-substituted-audited-original-source-content:"
                     + family,
                     lambda altered_audit=altered_audit, current=current,
                     family=family: _validate_current_family_snapshot(
                         family, current, altered_audit,
                     ))
            for deep in (False, True):
                wrapper, state, outcome, context = _synthetic_durable_pair(
                    family, deep=deep,
                )
                mode = "deep" if deep else "edge"
                positive = _complete_durable_proof(
                    wrapper, family, state, deep=deep,
                    original_document=outcome,
                    archive_path=context["archive_path"],
                    archive_digest=context["archive_sha256"],
                    archive_bytes=context["archive_bytes"],
                    edge_pair=context["edge_pair"],
                )
                accept("accept-complete-actual-shape-archive-and-owner-pair:"
                       + family + ":" + mode, positive == wrapper)
                for key, wrong in (
                    ("schema", SCHEMA + "-forged"),
                    ("status", "FAIL"), ("result", "FAIL"),
                    ("campaign_qualified", False),
                    ("original_archive_sha256", "0" * 64),
                    ("actual_v10_base_report_sha256", "0" * 64),
                    ("actual_v10_strict_report_sha256", "0" * 64),
                    ("performance", "MEASURED"),
                    ("holdout", "ACCESSED"),
                    ("corrected_v10_native_owner_before", None),
                    ("corrected_v10_native_owner_after", None),
                ):
                    changed = copy.deepcopy(wrapper)
                    changed[key] = wrong
                    rejected(
                        "reject-forged-durable-original-ownership:"
                        + family + ":" + mode + ":" + key,
                        lambda changed=changed, family=family, state=state,
                        deep=deep, outcome=outcome, context=context:
                        _complete_durable_proof(
                            changed, family, state, deep=deep,
                            original_document=outcome,
                            archive_path=context["archive_path"],
                            archive_digest=context["archive_sha256"],
                            archive_bytes=context["archive_bytes"],
                            edge_pair=context["edge_pair"],
                        ),
                    )
                for wrong in (False, True, -1, 1, None):
                    changed = copy.deepcopy(wrapper)
                    changed["original_worker_returncode"] = wrong
                    rejected(
                        "reject-forged-real-original-worker-returncode:"
                        + family + ":" + mode + ":" + repr(wrong),
                        lambda changed=changed, family=family, state=state,
                        deep=deep, outcome=outcome, context=context:
                        _complete_durable_proof(
                            changed, family, state, deep=deep,
                            original_document=outcome,
                            archive_path=context["archive_path"],
                            archive_digest=context["archive_sha256"],
                            archive_bytes=context["archive_bytes"],
                            edge_pair=context["edge_pair"],
                        ),
                    )
                for phase in ("corrected_v10_native_owner_before",
                              "corrected_v10_native_owner_after"):
                    for field in ("regex_guard_count", "native_loader_guard_count",
                                  "standard_pickle_check_count",
                                  "external_regex_packages"):
                        changed = copy.deepcopy(wrapper)
                        changed[phase][field] = 999
                        rejected(
                            "reject-weakened-genuine-durable-owner:"
                            + family + ":" + mode + ":" + phase + ":" + field,
                            lambda changed=changed, family=family, state=state,
                            deep=deep, outcome=outcome, context=context:
                            _complete_durable_proof(
                                changed, family, state, deep=deep,
                                original_document=outcome,
                                archive_path=context["archive_path"],
                                archive_digest=context["archive_sha256"],
                                archive_bytes=context["archive_bytes"],
                                edge_pair=context["edge_pair"],
                            ),
                        )
                if deep:
                    changed = copy.deepcopy(wrapper)
                    changed["qualified_edge"]["proof_sha256"] = "0" * 64
                    rejected(
                        "reject-deep-proof-unbound-from-complete-edge-owner:"
                        + family,
                        lambda changed=changed, family=family, state=state,
                        outcome=outcome, context=context:
                        _complete_durable_proof(
                            changed, family, state, deep=True,
                            original_document=outcome,
                            archive_path=context["archive_path"],
                            archive_digest=context["archive_sha256"],
                            archive_bytes=context["archive_bytes"],
                            edge_pair=context["edge_pair"],
                        ),
                    )

        for name, relative in (
            ("absolute", "/tmp/postfinal-locale-v6-forged.json"),
            ("traversal", "oracle/cpython-3.14.6/evidence/../forged.json"),
            ("old-v5", original.REPORT_RELATIVE),
            ("v5-real-reference", V5_REFERENCE_RELATIVE),
            ("backslash", "oracle\\cpython-3.14.6\\forged.json"),
            ("nul", "oracle/cpython-3.14.6/evidence/forged\x00.json"),
        ):
            rejected("reject-unsafe-historical-evidence-destination:" + name,
                     lambda relative=relative: _safe_output_path(relative))
        for relative in sorted(APPROVED_OUTPUTS):
            accept("allow-only-an-exact-separate-v6-destination:" + relative,
                   _safe_output_path(relative) == ROOT / relative)
        for name in ("time", "monotonic", "perf_counter", "process_time"):
            rejected("block-every-source-only-clock:" + name,
                     lambda name=name: getattr(time, name)())
        rejected("block-any-real-source-only-worker",
                 lambda: subprocess.run([str(original.upstream.PINNED_CPYTHON)]))
        rejected("block-any-real-source-only-thread",
                 lambda: threading.Thread(target=lambda: None).start())
        for family in FAMILIES:
            rejected("block-every-source-only-candidate-import:" + family,
                     lambda family=family: importlib.import_module(
                         "candidates." + family + "_candidate",
                     ))
        rejected("block-source-only-builtin-candidate-import",
                 lambda: builtins.__import__("candidates.rust_candidate"))
        rejected("block-all-source-only-os-evidence-or-source-reads",
                 lambda: os.open(ROOT / SOURCE_RELATIVE, os.O_RDONLY))
        rejected("block-all-source-only-builtin-evidence-or-source-reads",
                 lambda: builtins.open(ROOT / SOURCE_RELATIVE, "r"))
        rejected("block-source-only-reference-evidence-read",
                 lambda: original._read_verified_evidence(
                     V5_REFERENCE_RELATIVE, V5_REFERENCE_SHA256,
                 ))
        rejected("block-source-only-real-original-worker",
                 lambda: _run_isolated_worker(
                     "stdlib", "reference_a", "0" * 64, "", {},
                 ))
        rejected("block-source-only-real-v10-native-owner",
                 lambda: owner.run_native_worker("rust", {
                     "synthetic": "0" * 64,
                 }))
        rejected("block-source-only-real-private-locale",
                 lambda: tempfile.TemporaryDirectory())
        rejected("block-source-only-exclusive-v6-report",
                 lambda: _exclusive_write(
                     {"synthetic": True}, REPORT_RELATIVE,
                 ))
        rejected("block-unpublished-real-v10-and-v11-production-pins",
                 lambda: _candidate_pin_values("all", {}))
        accept("actually-block-every-worker-clock-candidate-and-locale",
               effects["clock_attempts_blocked"] >= 4
               and effects["worker_attempts_blocked"] >= 3
               and effects["candidate_import_attempts_blocked"] >= 4
               and effects["file_read_attempts_blocked"] >= 3
               and effects["locale_attempts_blocked"] >= 1)
        accept("never-read-or-write-official-evidence-fixtures-or-holdouts",
               effects["file_reads"] == 0 and effects["file_writes"] == 0)
        accept("never-start-a-reference-candidate-clock-or-native-worker",
               effects["subprocesses"] == 0
               and effects["clock_samples"] == 0
               and effects["candidate_imports"] == 0)
        failed = [row["name"] for row in checks
                  if row.get("passed") is not True]
        require(not failed,
                "a frozen original V6 candidate-free control failed: "
                + ", ".join(failed))
        require(len(checks) >= 240,
                "at least 240 real deterministic source-only controls are required")
        observed_effects = dict(effects)
    verify_runtime(candidate=True)
    return {
        "schema": SCHEMA + "-source-self-test",
        "status": "PASS", "passed": True,
        "python": "3.14.6", "check_count": len(checks),
        "checks": checks,
        "immutable_v5_control_count": inherited["check_count"],
        "immutable_v5_source_sha256": V5_SOURCE_SHA256,
        "immutable_v5_protocol_sha256": V5_PROTOCOL_SHA256,
        "immutable_v5_reference_sha256": V5_REFERENCE_SHA256,
        "v10_native_owner_source_sha256": V10_OWNER_SOURCE_SHA256,
        "v10_no_delegation_source_sha256": V10_STRICT_SOURCE_SHA256,
        "v10_native_ownership_protocol_sha256": V10_OWNERSHIP_PROTOCOL_SHA256,
        "v11_proof_source_sha256": V11_SOURCE_SHA256,
        "v11_proof_protocol_sha256": V11_PROTOCOL_SHA256,
        "v6_protocol_sha256": PROTOCOL_SHA256,
        "public_method_matrix_sha256": METHOD_MATRIX_SHA256,
        "original_public_method_count": 152,
        "original_private_method_count": 13,
        "original_support_module_count": 26,
        "original_corpus_case_count": 403,
        "original_external_fixture_assertion_count": 11,
        "qualified_artifacts_required_per_family": 4,
        "candidate_imports": 0, "subprocesses": 0,
        "file_reads": 0, "file_writes": 0, "clock_samples": 0,
        "actual_reference_workers": 0,
        "actual_candidate_workers": 0,
        "actual_native_owner_workers": 0,
        "actual_official_method_checks": 0,
        "synthetic_results_qualify_candidates": False,
        "holdout_cases_read": 0, "performance_fixtures_read": 0,
        "effects": observed_effects,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run every original Python regex test on genuinely owned engines.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--self-oracle", action="store_true")
    modes.add_argument("--candidate", choices=("all", *FAMILIES))
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--reference-sha256")
    parser.add_argument("--base-report-sha256")
    parser.add_argument("--strict-report-sha256")
    for family in FAMILIES:
        for kind in PROOF_KINDS:
            parser.add_argument(
                "--" + family + "-" + kind.replace("_", "-") + "-sha256",
            )
    return parser.parse_args(arguments)


def _failure_document(
    error: OfficialV6WorkerFailure, options: argparse.Namespace,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-actual-role-failure",
        "status": "FAIL", "role": error.role,
        "reason": str(error), "details": error.details,
        "source_sha256": options.source_sha256,
        "protocol_sha256": options.protocol_sha256,
        "synthetic": False,
        "production_observations_invented": False,
        "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
    }


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)
    try:
        if options.self_test:
            require(options.source_sha256 is None
                    and options.protocol_sha256 is None
                    and options.reference_sha256 is None
                    and options.base_report_sha256 is None
                    and options.strict_report_sha256 is None
                    and all(getattr(options, family + "_" + kind + "_sha256")
                            is None for family in FAMILIES for kind in PROOF_KINDS),
                    "a candidate-free V6 source control cannot consume real evidence")
            result = source_self_test()
        elif options.self_oracle:
            require(original.valid_sha256(options.source_sha256)
                    and options.protocol_sha256 == PROTOCOL_SHA256,
                    "BLOCKED: independently publish the real V6 source and protocol")
            require(options.reference_sha256 is None
                    and options.base_report_sha256 is None
                    and options.strict_report_sha256 is None
                    and all(getattr(options, family + "_" + kind + "_sha256")
                            is None for family in FAMILIES for kind in PROOF_KINDS),
                    "genuine Python-only references cannot consume candidate proofs")
            result = run_self_oracle(str(options.source_sha256))
        else:
            require(original.valid_sha256(options.source_sha256)
                    and options.protocol_sha256 == PROTOCOL_SHA256
                    and original.valid_sha256(options.reference_sha256),
                    "BLOCKED: independently publish the actual V6 source, exact "
                    "protocol, and genuine complete two-reference report")
            supplied: dict[str, Any] = {
                "base_report": options.base_report_sha256,
                "strict_report": options.strict_report_sha256,
                **{
                    family + "_" + kind:
                    getattr(options, family + "_" + kind + "_sha256")
                    for family in FAMILIES for kind in PROOF_KINDS
                },
            }
            _candidate_pin_values(str(options.candidate), supplied)
            result = run_candidates(
                str(options.candidate), str(options.source_sha256),
                str(options.reference_sha256), supplied,
            )
    except OfficialV6WorkerFailure as error:
        failure = _failure_document(error, options)
        destinations: list[str] = []
        if error.role == "stdlib":
            destinations.append(SELF_ORACLE_FAILURE_RELATIVE)
        elif error.role in FAMILIES:
            destinations.append(ROLE_FAILURE_RELATIVES[error.role])
            if options.candidate == "all":
                destinations.append(REPORT_FAILURE_RELATIVE)
        elif error.role == "all" and options.candidate == "all":
            destinations.append(REPORT_FAILURE_RELATIVE)
        preserved: list[dict[str, str]] = []
        for destination in destinations:
            try:
                payload = dict(failure)
                payload["actual_failure_destination"] = destination
                if destination == REPORT_FAILURE_RELATIVE:
                    payload["schema"] = SCHEMA + "-all-family-failure"
                    payload["all_family_campaign_qualified"] = False
                observed = _exclusive_write(payload, destination)
                preserved.append({
                    "path": destination,
                    "sha256": observed,
                })
            except (OfficialV6Error, OSError) as preservation_error:
                failure.setdefault("actual_preservation_errors", []).append({
                    "path": destination,
                    "actual_error_type": type(preservation_error).__name__,
                    "actual_error": str(preservation_error),
                })
        failure["actual_exclusively_preserved_failure_reports"] = preserved
        print(json.dumps(failure, ensure_ascii=True, allow_nan=False,
                         sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    except (OfficialV6Error, original.OfficialV5Error,
            original.upstream.OfficialV4Error,
            OSError, MemoryError, subprocess.SubprocessError,
            UnicodeError, ValueError, KeyError, TypeError, AssertionError) as error:
        print(json.dumps({
            "schema": SCHEMA + "-controller-failure",
            "status": "BLOCKED", "reason": str(error),
            "actual_error_type": type(error).__name__,
            "production_observations_invented": False,
            "actual_execution_or_publication_not_asserted": True,
            "performance": "NOT MEASURED", "holdout": "NOT ACCESSED",
        }, sort_keys=True, separators=(",", ":")), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
