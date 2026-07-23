#!/usr/bin/env python3
"""Additive, isolated checks for observable regex cache-key reentrancy.

The original versioned correctness matrices, fixtures, and reports are not
changed. Cache size and eviction policy remain covered by the existing named
PRIVATE-CACHE-LAYOUT waiver; a different private policy is never hidden or
counted as an exact match.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
RUNNER = Path(__file__).resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import rust_v8_multi_candidate_contract as contract


SCHEMA = "rebar-v9-cache-reentrancy-oracle-v1"
SELF_TEST_SCHEMA = "rebar-v9-cache-reentrancy-self-test-v1"
FIXTURE_SCHEMA = "rebar-v9-cache-reentrancy-fixture-v1"
SEED = 2026072361
PRIVATE_CACHE_WAIVER = "PRIVATE-CACHE-LAYOUT"
FROZEN_FIXTURE_SHA256 = (
    "36afb18cb56cd8d331c6ea4c8cbc36bb0d6256b92bd050b05771512b3c4ccca6"
)
WORKER_TIMEOUT_SECONDS = 90
MAX_CAPTURED_WORKER_BYTES = 1_048_576
REFERENCE_ROLES = frozenset({"stdlib-a", "stdlib-b"})
WORKER_ROLES = frozenset(
    {"stdlib-a", "stdlib-b", "candidate", "guard-self-test", "semantic-poison"}
)
CASE_FIXTURES: tuple[dict[str, Any], ...] = (
    {
        "id": "cache-equal-key-reentrant-compile",
        "obligations": [
            "API-COMPILE",
            "API-PATTERN",
            "PUBLIC-CACHE-KEY-EQUALITY-REENTRY",
        ],
    },
    {
        "arm_after_fills": 0,
        "fills": 255,
        "id": "cache-fifo-purge-during-eviction",
        "obligations": ["API-COMPILE", "PUBLIC-CACHE-EVICTION-REENTRY"],
        "private_waiver": PRIVATE_CACHE_WAIVER,
    },
    {
        "arm_after_fills": 256,
        "fills": 511,
        "id": "cache-lru-purge-during-eviction",
        "obligations": ["API-COMPILE", "PUBLIC-CACHE-EVICTION-REENTRY"],
        "private_waiver": PRIVATE_CACHE_WAIVER,
    },
)
CASE_IDS = tuple(item["id"] for item in CASE_FIXTURES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def fixture_document() -> dict[str, Any]:
    return {
        "cases": copy.deepcopy(list(CASE_FIXTURES)),
        "schema": FIXTURE_SCHEMA,
        "seed": SEED,
    }


def verify_fixture() -> None:
    fixture = fixture_document()
    require(
        digest(fixture) == FROZEN_FIXTURE_SHA256,
        "the additive three-case cache fixture changed",
    )
    require(
        tuple(item["id"] for item in fixture["cases"]) == CASE_IDS,
        "the additive cache fixture lost, repeated, or reordered a case",
    )
    require(len(CASE_IDS) == 3 and len(set(CASE_IDS)) == 3,
            "the additive cache denominator must remain exactly three")


def verify_runtime(*, isolated_worker: bool = False) -> None:
    require(sys.implementation.name == "cpython",
            "the cache oracle requires CPython")
    require(tuple(sys.version_info[:3]) == (3, 14, 6),
            "the cache oracle requires pinned CPython 3.14.6")
    require(
        Path(sys.executable).resolve() == contract.PINNED_EXECUTABLE.resolve(),
        "the cache oracle requires the exact pinned Python executable",
    )
    if isolated_worker:
        require(os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
                "isolated cache workers must not create bytecode")
        require(os.environ.get("PYTHONHASHSEED") == "0",
                "isolated cache workers require the frozen hash seed")


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, str):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return {"kind": type(value).__name__, "hex": bytes(value).hex()}
    if isinstance(value, type):
        return {
            "kind": "type",
            "module": value.__module__,
            "qualname": value.__qualname__,
        }
    if isinstance(value, (tuple, list)):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): normalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    return {"kind": type(value).__name__}


def exception_snapshot(error: BaseException) -> dict[str, Any]:
    return {
        "args": normalize(error.args),
        "cause": (
            {
                "args": normalize(error.__cause__.args),
                "type": type(error.__cause__).__name__,
            }
            if error.__cause__ is not None
            else None
        ),
        "context": (
            {
                "args": normalize(error.__context__.args),
                "type": type(error.__context__).__name__,
            }
            if error.__context__ is not None
            else None
        ),
        "suppress_context": bool(error.__suppress_context__),
        "type": type(error).__name__,
    }


def attempted(action: Any) -> dict[str, Any]:
    try:
        return {"status": "value", "value": normalize(action())}
    except Exception as error:
        return {"status": "error", "error": exception_snapshot(error)}


class CollisionText(str):
    """Equal cache keys expose which operand receives rich comparison."""

    def __new__(
        cls,
        value: str,
        trace: list[Any],
        module: Any,
        label: str,
        *,
        reenter: bool,
    ) -> CollisionText:
        item = str.__new__(cls, value)
        item.trace = trace
        item.module = module
        item.label = label
        item.reenter = reenter
        item.armed = False
        item.active = False
        return item

    def __hash__(self) -> int:
        if self.armed:
            self.trace.append(("hash", self.label))
        return str.__hash__(self)

    def __eq__(self, other: object) -> Any:
        if self.armed:
            other_label = (
                other.label
                if isinstance(other, CollisionText)
                else {"kind": type(other).__name__, "value": str(other)}
            )
            self.trace.append(("equal", self.label, other_label))
            if self.reenter and not self.active:
                self.active = True
                try:
                    self.trace.append(("nested-compile", "enter"))
                    nested = self.module.compile("v9_cache_nested_literal")
                    self.trace.append(
                        (
                            "nested-compile",
                            "return",
                            nested.pattern == "v9_cache_nested_literal",
                        )
                    )
                finally:
                    self.active = False
        return str.__eq__(self, other)


class EvictionText(str):
    """Purge only when the candidate itself hashes an armed old cache key."""

    def __new__(
        cls,
        value: str,
        trace: list[Any],
        module: Any,
        label: str,
    ) -> EvictionText:
        item = str.__new__(cls, value)
        item.trace = trace
        item.module = module
        item.label = label
        item.armed = False
        item.active = False
        item.fired = False
        item.fill_index = 0
        return item

    def __hash__(self) -> int:
        if self.armed:
            self.trace.append(
                ("victim-hash", self.label, self.fill_index)
            )
            if not self.active and not self.fired:
                self.active = True
                self.fired = True
                try:
                    self.trace.append(
                        ("purge", "enter", self.label, self.fill_index)
                    )
                    self.module.purge()
                    self.trace.append(
                        ("purge", "return", self.label, self.fill_index)
                    )
                finally:
                    self.active = False
        return str.__hash__(self)


def equality_case(module: Any) -> dict[str, Any]:
    trace: list[Any] = []
    module.purge()
    first_text = CollisionText("v9_cache_equal_literal", trace, module,
                               "first", reenter=True)
    second_text = CollisionText("v9_cache_equal_literal", trace, module,
                                "second", reenter=False)
    first_pattern = module.compile(first_text)
    trace.clear()
    first_text.armed = True
    second_text.armed = True

    def invoke() -> dict[str, bool]:
        result = module.compile(second_text)
        return {
            "pattern_is_first_source": result.pattern is first_text,
            "returns_first_compiled_pattern": result is first_pattern,
        }

    result = attempted(invoke)
    observation = {"result": result, "trace": normalize(trace)}
    first_text.armed = False
    second_text.armed = False
    recovery = attempted(module.purge)
    observation["cleanup"] = recovery
    return observation


def eviction_case(
    module: Any, *, fills: int, arm_after_fills: int, label: str
) -> dict[str, Any]:
    require(type(fills) is int and type(arm_after_fills) is int
            and 0 <= arm_after_fills <= fills,
            "the frozen cache eviction arming schedule is invalid")
    trace: list[Any] = []
    module.purge()
    victim = EvictionText("v9_cache_eviction_victim", trace, module, label)
    original = module.compile(victim)
    trace.clear()
    victim.armed = arm_after_fills == 0
    for number in range(fills):
        if number == arm_after_fills:
            victim.armed = True
        victim.fill_index = number + 1
        module.compile(f"v9_cache_fill_{label}_{number:04d}")
    victim.fill_index = fills + 1
    trigger = f"v9_cache_eviction_trigger_{label}"
    captured: dict[str, Any] = {}

    def invoke() -> dict[str, Any]:
        value = module.compile(trigger)
        captured["trigger"] = value
        return {"flags": int(value.flags), "pattern": value.pattern}

    result = attempted(invoke)
    observed_trace = normalize(trace)
    victim.armed = False
    recovery: dict[str, Any] = {}
    if result["status"] == "value":
        recovery["victim_still_cached"] = attempted(
            lambda: module.compile(victim) is original
        )
        recovery["same_before_explicit_purge"] = attempted(
            lambda: module.compile(trigger) is captured["trigger"]
        )
        recovery["explicit_purge"] = attempted(module.purge)
        if recovery["explicit_purge"]["status"] == "value":
            recovery["same_after_explicit_purge"] = attempted(
                lambda: module.compile(trigger) is captured["trigger"]
            )
        else:
            recovery["same_after_explicit_purge"] = {
                "status": "not-run",
                "reason": "explicit purge failed",
            }
    else:
        recovery["cleanup"] = attempted(module.purge)
    return {
        "armed_after_fills": arm_after_fills,
        "eviction_hash_observed": bool(victim.fired),
        "prefill_count": fills,
        "recovery": recovery,
        "result": result,
        "trace": observed_trace,
        "trigger_fill_index": fills + 1,
    }


def evaluate_cases(module: Any) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for fixture in CASE_FIXTURES:
        identity = fixture["id"]
        if identity == "cache-equal-key-reentrant-compile":
            observed = equality_case(module)
        elif identity == "cache-fifo-purge-during-eviction":
            observed = eviction_case(
                module,
                fills=fixture["fills"],
                arm_after_fills=fixture["arm_after_fills"],
                label="fifo",
            )
        elif identity == "cache-lru-purge-during-eviction":
            observed = eviction_case(
                module,
                fills=fixture["fills"],
                arm_after_fills=fixture["arm_after_fills"],
                label="lru",
            )
        else:
            raise AssertionError(f"unknown frozen cache case: {identity}")
        normalized = normalize(observed)
        observations.append(
            {
                "id": identity,
                "obligations": list(fixture["obligations"]),
                "observation": normalized,
                "sha256": digest(normalized),
            }
        )
    return observations


class ReferenceCacheBypass:
    """Reference-only real negative control; never used as production."""

    def __init__(self, module: Any) -> None:
        self.module = module

    def purge(self) -> Any:
        return self.module.purge()

    def compile(self, pattern: Any, flags: Any = 0) -> Any:
        if isinstance(pattern, CollisionText):
            return self.module.compile(str(pattern), flags)
        return self.module.compile(pattern, flags)


def reference_module() -> Any:
    standard = importlib.import_module("re")
    location = Path(standard.__file__).resolve()
    pinned_root = contract.PINNED_EXECUTABLE.resolve().parent.parent
    require(location.is_relative_to(pinned_root),
            "the cache reference is not the pinned standard library")
    require(
        not any(name == "candidates" or name.startswith("candidates.")
                for name in sys.modules),
        "an isolated standard-library cache worker imported a candidate",
    )
    return standard


def worker_base(role: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "role": role,
        "python": "3.14.6",
        "implementation": "cpython",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": len(CASE_IDS),
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def observation_worker(role: str, module: Any) -> dict[str, Any]:
    rows = evaluate_cases(module)
    return {
        **worker_base(role),
        "observations": rows,
        "observation_sha256": digest(rows),
    }


def guard_worker(spec: contract.CandidateSpec) -> dict[str, Any]:
    suite = contract.load_frozen_suite()
    with contract.active_cross_engine_guard(suite, spec) as isolation:
        guards = suite.install_regex_guards()
        initial = suite.audit_regex_guards(guards)
        cross = contract.audit_cross_engine_guards(isolation)
        final = suite.audit_regex_guards(guards)
        require(initial == final and len(initial) == 13,
                "cache self-test lost an active standard-library poison")
        require(len(cross) >= 10,
                "cache self-test lost independent cross-family poisons")
        return {
            **worker_base("guard-self-test"),
            "candidate_module": spec.module,
            "candidate_family": spec.family,
            "guard_count": len(final),
            "guards": final,
            "cross_engine_guard_count": len(cross),
            "cross_engine_guards": cross,
        }


def candidate_worker(
    spec: contract.CandidateSpec, edge_path: Path
) -> dict[str, Any]:
    authorized, proof, _ = contract.read_edge_proof(edge_path, spec)
    suite = contract.load_frozen_suite()
    with contract.active_cross_engine_guard(suite, spec) as isolation:
        selected = importlib.import_module(spec.module)
        initial_artifacts = contract.production_provenance(
            selected, spec, authorized, isolation
        )
        require(initial_artifacts == proof["production_artifacts"],
                "the cache worker loaded artifacts outside its passing edge proof")
        cross_before = contract.audit_cross_engine_guards(isolation)
        guards = suite.install_regex_guards()
        regex_before = suite.audit_regex_guards(guards)
        report = observation_worker("candidate", selected)
        regex_after = suite.audit_regex_guards(guards)
        cross_after = contract.audit_cross_engine_guards(isolation)
        final_artifacts = contract.production_provenance(
            selected, spec, authorized, isolation
        )
        require(regex_before == regex_after and len(regex_after) == 13,
                "the cache worker removed a standard-library regex poison")
        require(cross_before == cross_after and len(cross_after) >= 10,
                "the cache worker removed a cross-family regex poison")
        require(initial_artifacts == final_artifacts,
                "the cache worker changed a proven production artifact")
        return {
            **report,
            "candidate_module": spec.module,
            "candidate_family": spec.family,
            "native_artifacts": final_artifacts,
            "guard_count": len(regex_after),
            "guards": regex_after,
            "cross_engine_guard_count": len(cross_after),
            "cross_engine_guards": cross_after,
            "edge_oracle": proof,
        }


def validate_worker(
    report: Any,
    role: str,
    spec: contract.CandidateSpec,
    proof: dict[str, Any] | None = None,
) -> None:
    require(isinstance(report, dict), "cache worker did not return a JSON object")
    for key, expected in worker_base(role).items():
        require(report.get(key) == expected,
                f"isolated cache worker changed {key}")
    if role == "guard-self-test":
        require(report.get("candidate_module") == spec.module,
                "guard self-test substituted the candidate family")
        require(report.get("candidate_family") == spec.family,
                "guard self-test changed the candidate family")
        require(report.get("guard_count") == 13,
                "guard self-test lost a standard-library poison")
        require(isinstance(report.get("guards"), list)
                and len(report["guards"]) == 13,
                "guard self-test concealed a standard-library poison")
        cross = report.get("cross_engine_guards")
        require(isinstance(cross, list)
                and len(cross) >= 10
                and report.get("cross_engine_guard_count") == len(cross),
                "guard self-test concealed a cross-family poison")
        require("observations" not in report,
                "guard self-test silently evaluated a candidate")
        return

    rows = report.get("observations")
    require(isinstance(rows, list) and len(rows) == len(CASE_IDS),
            "cache worker changed the three-case denominator")
    require(tuple(row.get("id") for row in rows) == CASE_IDS,
            "cache worker dropped, repeated, or reordered a case")
    for fixture, row in zip(CASE_FIXTURES, rows, strict=True):
        require(isinstance(row, dict), "cache worker returned a malformed case")
        require(row.get("obligations") == fixture["obligations"],
                "cache worker changed a frozen obligation mapping")
        observation = row.get("observation")
        require(isinstance(observation, dict),
                "cache worker omitted a case observation")
        require(row.get("sha256") == digest(observation),
                "cache worker forged an individual observation")
    require(report.get("observation_sha256") == digest(rows),
            "cache worker forged its complete observation digest")

    if role in REFERENCE_ROLES or role == "semantic-poison":
        require("candidate_module" not in report
                and "native_artifacts" not in report,
                "reference cache worker concealed a candidate import")
        return

    require(role == "candidate" and proof is not None,
            "production cache worker lacks its passing edge proof")
    require(report.get("candidate_module") == spec.module,
            "cache worker substituted its candidate module")
    require(report.get("candidate_family") == spec.family,
            "cache worker substituted its engine family")
    require(report.get("edge_oracle") == proof,
            "cache worker changed its explicit passing edge proof")
    require(report.get("native_artifacts") == proof["production_artifacts"],
            "cache worker substituted a proven production artifact")
    guards = report.get("guards")
    require(isinstance(guards, list)
            and len(guards) == 13
            and report.get("guard_count") == 13,
            "cache worker lost an active standard-library regex poison")
    cross = report.get("cross_engine_guards")
    require(isinstance(cross, list)
            and len(cross) >= 10
            and report.get("cross_engine_guard_count") == len(cross),
            "cache worker lost an active cross-family poison")


def validate_reference_semantics(report: dict[str, Any]) -> None:
    rows = {row["id"]: row["observation"]
            for row in report["observations"]}
    equality = rows["cache-equal-key-reentrant-compile"]
    equality_trace = equality.get("trace")
    require(isinstance(equality_trace, list),
            "pinned CPython omitted the equal-key event trace")
    expected_hash = ["hash", "second"]
    expected_equality = ["equal", "first", "second"]
    nested_enter = ["nested-compile", "enter"]
    nested_return = ["nested-compile", "return", True]
    require(all(event in equality_trace for event in (
        expected_hash, expected_equality, nested_enter, nested_return
    )), "pinned CPython did not exercise equal-key compilation reentry")
    require(
        equality_trace.index(expected_hash)
        < equality_trace.index(expected_equality)
        < equality_trace.index(nested_enter)
        < equality_trace.index(nested_return),
        "pinned CPython did not complete the equal-key reentry",
    )
    require(equality.get("result") == {
        "status": "value",
        "value": {
            "pattern_is_first_source": True,
            "returns_first_compiled_pattern": True,
        },
    }, "pinned CPython changed equal-cache-key pattern identity")
    require(equality.get("cleanup") == {"status": "value", "value": None},
            "pinned CPython failed to restore its equality-case cache")
    for identity, label in (
        ("cache-fifo-purge-during-eviction", "fifo"),
        ("cache-lru-purge-during-eviction", "lru"),
    ):
        fixture = next(item for item in CASE_FIXTURES
                       if item["id"] == identity)
        observation = rows[identity]
        trace = observation.get("trace")
        require(isinstance(trace, list),
                f"pinned CPython omitted the {label} eviction trace")
        require(observation.get("armed_after_fills")
                == fixture["arm_after_fills"]
                and observation.get("prefill_count") == fixture["fills"]
                and observation.get("trigger_fill_index")
                == fixture["fills"] + 1,
                f"pinned CPython changed the frozen {label} fill schedule")
        hashes = [
            (position, event[2])
            for position, event in enumerate(trace)
            if isinstance(event, list)
            and len(event) == 3
            and event[:2] == ["victim-hash", label]
            and type(event[2]) is int
        ]
        entries = [
            (position, event[3])
            for position, event in enumerate(trace)
            if isinstance(event, list)
            and len(event) == 4
            and event[:3] == ["purge", "enter", label]
            and type(event[3]) is int
        ]
        returns = [
            (position, event[3])
            for position, event in enumerate(trace)
            if isinstance(event, list)
            and len(event) == 4
            and event[:3] == ["purge", "return", label]
            and type(event[3]) is int
        ]
        require(hashes and len(entries) == 1 and len(returns) == 1,
                f"pinned CPython did not exercise {label} eviction reentry")
        require(hashes[0][0] < entries[0][0] < returns[0][0]
                and hashes[0][1] == entries[0][1] == returns[0][1]
                and fixture["arm_after_fills"] < hashes[0][1]
                <= fixture["fills"] + 1,
                f"pinned CPython did not complete {label} eviction reentry")
        require(observation.get("eviction_hash_observed") is True,
                f"pinned CPython did not exercise {label} eviction")
        result = observation.get("result", {})
        require(result.get("status") == "value"
                and result.get("value", {}).get("pattern")
                == f"v9_cache_eviction_trigger_{label}",
                f"pinned CPython leaked a {label} eviction exception")
        recovery = observation.get("recovery", {})
        victim = recovery.get("victim_still_cached")
        require(isinstance(victim, dict)
                and victim.get("status") == "value"
                and type(victim.get("value")) is bool,
                f"pinned CPython omitted public {label} victim identity")
        require(recovery.get("same_before_explicit_purge")
                == {"status": "value", "value": True},
                f"pinned CPython lost its {label} replacement pattern")
        require(recovery.get("explicit_purge")
                == {"status": "value", "value": None},
                f"pinned CPython failed its {label} explicit purge")
        require(recovery.get("same_after_explicit_purge")
                == {"status": "value", "value": False},
                f"pinned CPython retained its {label} pattern after purge")


class ReferenceValidationFailure(AssertionError):
    """Keep both genuine reference observations when validation fails."""

    def __init__(
        self,
        message: str,
        first: dict[str, Any],
        second: dict[str, Any],
    ) -> None:
        super().__init__(message)
        self.first = copy.deepcopy(first)
        self.second = copy.deepcopy(second)


def validate_reference_pair(
    first: dict[str, Any], second: dict[str, Any]
) -> None:
    try:
        require(
            first.get("observation_sha256")
            == second.get("observation_sha256"),
            "the independently pinned cache-reference digests differ",
        )
        require(
            canonical(first["observations"])
            == canonical(second["observations"]),
            "the independently pinned cache references differ byte-for-byte",
        )
        validate_reference_semantics(first)
        validate_reference_semantics(second)
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        raise ReferenceValidationFailure(
            str(error), first, second
        ) from error


def reference_failure_report(
    error: ReferenceValidationFailure, command: str
) -> dict[str, Any]:
    first = error.first
    second = error.second
    left = first.get("observations")
    right = second.get("observations")
    references_match = (
        isinstance(left, list)
        and isinstance(right, list)
        and first.get("observation_sha256")
        == second.get("observation_sha256")
        and canonical(left) == canonical(right)
    )
    return {
        "schema": SELF_TEST_SCHEMA if command == "self-test" else SCHEMA,
        "status": "FAIL",
        "python": "3.14.6",
        "implementation": "cpython",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": len(CASE_IDS),
        "case_ids": list(CASE_IDS),
        "source_path": "tools/rust_v9_cache_reentrancy_oracle.py",
        "source_sha256": contract.sha256_path(RUNNER),
        "failure_type": "reference-validation",
        "failure_message": str(error),
        "stdlib_vs_stdlib": "PASS" if references_match else "FAIL",
        "reference_a_sha256": first.get("observation_sha256"),
        "reference_b_sha256": second.get("observation_sha256"),
        "reference": first,
        "reference_independent_repeat": second,
        "private_cache_waiver": PRIVATE_CACHE_WAIVER,
        "forbidden_regex_guard_count": "NOT RUN",
        "cross_engine_guard_count": "NOT RUN",
        "candidate_imported": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def applicable_private_waiver(
    fixture: dict[str, Any], expected: dict[str, Any], actual: dict[str, Any]
) -> dict[str, Any] | None:
    if fixture.get("private_waiver") != PRIVATE_CACHE_WAIVER:
        return None
    if actual.get("eviction_hash_observed") is not False:
        return None
    if actual.get("trace") != []:
        return None
    expected_result = expected.get("result")
    actual_result = actual.get("result")
    if expected_result != actual_result:
        return None
    recovery = actual.get("recovery")
    if not isinstance(recovery, dict):
        return None
    for name, value in (
        ("same_before_explicit_purge", True),
        ("same_after_explicit_purge", False),
    ):
        if recovery.get(name) != {"status": "value", "value": value}:
            return None
    if recovery.get("explicit_purge") != {"status": "value", "value": None}:
        return None
    victim = recovery.get("victim_still_cached")
    if not isinstance(victim, dict) or victim.get("status") != "value":
        return None
    if type(victim.get("value")) is not bool:
        return None
    return {
        "case_id": fixture["id"],
        "name": PRIVATE_CACHE_WAIVER,
        "reason": (
            "The independent engine did not hash the old key at CPython's "
            "private capacity. Its public compilation, cache identity, "
            "and explicit purge still succeeded. Eviction capacity and "
            "policy are expressly waived; this is not an exact trace pass."
        ),
        "victim_still_cached": victim["value"],
    }


def compare_observations(
    reference: list[dict[str, Any]], actual: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    require(len(reference) == len(CASE_FIXTURES)
            and len(actual) == len(CASE_FIXTURES),
            "cache comparison changed its three-case denominator")
    mismatches: list[dict[str, Any]] = []
    waivers: list[dict[str, Any]] = []
    for fixture, expected_row, actual_row in zip(
        CASE_FIXTURES, reference, actual, strict=True
    ):
        require(expected_row.get("id") == fixture["id"]
                and actual_row.get("id") == fixture["id"],
                "cache comparison substituted a frozen case")
        expected = expected_row["observation"]
        observed = actual_row["observation"]
        if observed == expected:
            continue
        waiver = applicable_private_waiver(fixture, expected, observed)
        if waiver is not None:
            waivers.append(waiver)
            continue
        mismatches.append(
            {
                "id": fixture["id"],
                "obligations": list(fixture["obligations"]),
                "expected": expected,
                "actual": observed,
            }
        )
    return mismatches, waivers


def worker_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    environment["PYTHONPATH"] = str(ROOT)
    environment.pop("PYTHONSTARTUP", None)
    environment.pop("PYTHONINSPECT", None)
    return environment


def run_worker(
    role: str,
    spec: contract.CandidateSpec,
    edge_path: Path | None = None,
) -> dict[str, Any]:
    require(role in WORKER_ROLES, "unknown isolated cache worker")
    command = [
        str(contract.PINNED_EXECUTABLE),
        "-B",
        str(RUNNER),
        "worker",
        "--role",
        role,
        "--module",
        spec.module,
    ]
    if edge_path is not None:
        command.extend(("--edge-oracle", str(edge_path.resolve())))
    try:
        process = subprocess.run(
            command,
            cwd=str(ROOT),
            env=worker_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=WORKER_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AssertionError(
            f"isolated {spec.family} {role} cache worker timed out"
        ) from error
    require(len(process.stdout.encode("utf-8")) <= MAX_CAPTURED_WORKER_BYTES
            and len(process.stderr.encode("utf-8"))
            <= MAX_CAPTURED_WORKER_BYTES,
            "isolated cache worker exceeded its bounded output")
    if process.returncode:
        raise AssertionError(
            f"isolated {spec.family} {role} cache worker failed "
            f"({process.returncode}): {process.stderr[-4000:]} "
            f"{process.stdout[-2000:]}"
        )
    try:
        report = json.loads(process.stdout)
    except (TypeError, ValueError) as error:
        raise AssertionError(
            f"isolated {role} cache worker returned invalid JSON"
        ) from error
    proof = None
    if role == "candidate":
        require(edge_path is not None,
                "candidate cache worker requires an explicit passing edge proof")
        _, proof, _ = contract.read_edge_proof(edge_path, spec)
    validate_worker(report, role, spec, proof)
    return report


def evaluate_worker(
    role: str, spec: contract.CandidateSpec, edge_path: Path | None
) -> dict[str, Any]:
    verify_runtime(isolated_worker=True)
    verify_fixture()
    if role in REFERENCE_ROLES:
        require(edge_path is None,
                "a standard-library cache worker cannot load candidate evidence")
        return observation_worker(role, reference_module())
    if role == "semantic-poison":
        require(edge_path is None,
                "a semantic cache poison cannot load candidate evidence")
        return observation_worker(
            role, ReferenceCacheBypass(reference_module())
        )
    if role == "guard-self-test":
        require(edge_path is None,
                "the cache guard self-test cannot load candidate evidence")
        return guard_worker(spec)
    require(role == "candidate" and edge_path is not None,
            "production cache worker requires a proven candidate")
    return candidate_worker(spec, edge_path)


def expect_rejection(name: str, action: Any) -> dict[str, str]:
    try:
        action()
    except (
        AssertionError,
        FileNotFoundError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        return {
            "name": name,
            "status": "PASS",
            "error_type": type(error).__name__,
        }
    raise AssertionError(f"additive cache poison unexpectedly passed: {name}")


def require_exact_comparison(
    reference: list[dict[str, Any]], actual: list[dict[str, Any]]
) -> None:
    mismatches, waivers = compare_observations(reference, actual)
    require(not mismatches and not waivers,
            "the cache oracle accepted a genuinely different observation")


def run_self_test(spec: contract.CandidateSpec) -> dict[str, Any]:
    verify_runtime()
    verify_fixture()
    first = run_worker("stdlib-a", spec)
    second = run_worker("stdlib-b", spec)
    validate_reference_pair(first, second)
    guards = run_worker("guard-self-test", spec)
    poisoned = run_worker("semantic-poison", spec)
    semantic_failures, semantic_waivers = compare_observations(
        first["observations"], poisoned["observations"]
    )
    require(
        any(item["id"] == "cache-equal-key-reentrant-compile"
            for item in semantic_failures),
        "a genuinely cache-bypassing reference was not detected",
    )
    require(not semantic_waivers,
            "a semantic cache bypass was concealed by a private waiver")

    checks: list[dict[str, str]] = []

    def reject_changed_reference(name: str, mutate: Any) -> None:
        changed = copy.deepcopy(first)
        mutate(changed)
        checks.append(expect_rejection(
            name, lambda: validate_worker(changed, "stdlib-a", spec)
        ))

    reject_changed_reference(
        "missing-case", lambda value: value["observations"].pop()
    )
    reject_changed_reference(
        "reordered-cases", lambda value: value["observations"].reverse()
    )
    reject_changed_reference(
        "duplicated-case",
        lambda value: value["observations"].__setitem__(
            1, copy.deepcopy(value["observations"][0])
        ),
    )
    reject_changed_reference(
        "changed-observation-without-digest",
        lambda value: value["observations"][0]["observation"].update(
            trace=[]
        ),
    )
    reject_changed_reference(
        "wrong-fixture", lambda value: value.update(fixture_sha256="0" * 64)
    )
    reject_changed_reference(
        "changed-denominator", lambda value: value.update(checks=2)
    )
    reject_changed_reference(
        "reference-imported-candidate",
        lambda value: value.update(candidate_module=spec.module),
    )

    changed_trace = copy.deepcopy(first["observations"])
    changed_trace[0]["observation"]["trace"] = []
    changed_trace[0]["sha256"] = digest(changed_trace[0]["observation"])
    checks.append(expect_rejection(
        "changed-observation-with-recomputed-digest",
        lambda: require_exact_comparison(first["observations"], changed_trace),
    ))

    synthetic_proof = {
        "module": spec.module,
        "family": spec.family,
        "production_artifacts": [
            {
                "role": "public-python",
                "path": spec.public_path,
                "sha256": "0" * 64,
            }
        ],
    }
    synthetic_candidate = copy.deepcopy(first)
    synthetic_candidate.update(
        role="candidate",
        candidate_module=spec.module,
        candidate_family=spec.family,
        native_artifacts=copy.deepcopy(
            synthetic_proof["production_artifacts"]
        ),
        edge_oracle=copy.deepcopy(synthetic_proof),
        guard_count=guards["guard_count"],
        guards=copy.deepcopy(guards["guards"]),
        cross_engine_guard_count=guards["cross_engine_guard_count"],
        cross_engine_guards=copy.deepcopy(guards["cross_engine_guards"]),
    )
    validate_worker(synthetic_candidate, "candidate", spec, synthetic_proof)

    def reject_changed_candidate(name: str, mutate: Any) -> None:
        changed = copy.deepcopy(synthetic_candidate)
        mutate(changed)
        checks.append(expect_rejection(
            name,
            lambda: validate_worker(changed, "candidate", spec, synthetic_proof),
        ))

    reject_changed_candidate(
        "wrong-candidate-family", lambda value: value.update(candidate_family="OTHER")
    )
    reject_changed_candidate(
        "wrong-candidate-module",
        lambda value: value.update(candidate_module="candidates.wrong_engine"),
    )
    reject_changed_candidate(
        "missing-production-artifact",
        lambda value: value["native_artifacts"].clear(),
    )
    reject_changed_candidate(
        "missing-stdlib-poison", lambda value: value["guards"].pop()
    )
    reject_changed_candidate(
        "missing-cross-family-poison",
        lambda value: value["cross_engine_guards"].pop(),
    )
    reject_changed_candidate(
        "changed-edge-proof",
        lambda value: value["edge_oracle"].update(family="OTHER"),
    )

    def rejected_guard(name: str, mutate: Any) -> None:
        changed = copy.deepcopy(guards)
        mutate(changed)
        checks.append(expect_rejection(
            name, lambda: validate_worker(changed, "guard-self-test", spec)
        ))

    rejected_guard(
        "guard-self-test-lost-stdlib-poison",
        lambda value: value["guards"].pop(),
    )
    rejected_guard(
        "guard-self-test-lost-cross-family-poison",
        lambda value: value["cross_engine_guards"].pop(),
    )
    rejected_guard(
        "guard-self-test-imported-a-candidate",
        lambda value: value.update(observations=[]),
    )

    hidden_failure = copy.deepcopy(first["observations"])
    hidden_failure[1]["observation"]["result"] = {
        "status": "error",
        "error": {
            "args": ["synthetic eviction failure"],
            "cause": None,
            "context": None,
            "suppress_context": False,
            "type": "KeyError",
        },
    }
    hidden_failure[1]["observation"]["eviction_hash_observed"] = True
    hidden_failure[1]["sha256"] = digest(
        hidden_failure[1]["observation"]
    )
    checks.append(expect_rejection(
        "private-waiver-cannot-hide-fired-eviction-failure",
        lambda: require_exact_comparison(first["observations"], hidden_failure),
    ))

    unobserved_eviction = copy.deepcopy(first["observations"])
    waived_row = unobserved_eviction[1]
    waived_row["observation"]["trace"] = []
    waived_row["observation"]["eviction_hash_observed"] = False
    waived_row["observation"]["recovery"]["victim_still_cached"] = {
        "status": "value",
        "value": True,
    }
    waived_row["sha256"] = digest(waived_row["observation"])
    no_failures, named_waivers = compare_observations(
        first["observations"], unobserved_eviction
    )
    require(not no_failures
            and len(named_waivers) == 1
            and named_waivers[0]["name"] == PRIVATE_CACHE_WAIVER
            and named_waivers[0]["case_id"]
            == "cache-fifo-purge-during-eviction",
            "the explicitly named private-layout waiver is not accurate")

    require(len(checks) >= 17,
            "cache self-test did not execute enough independent poisons")
    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "python": "3.14.6",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "checks": len(CASE_IDS),
        "case_ids": list(CASE_IDS),
        "stdlib_vs_stdlib_failures": [],
        "reference_a_sha256": first["observation_sha256"],
        "reference_b_sha256": second["observation_sha256"],
        "reference": first,
        "reference_independent_repeat": second,
        "semantic_poison_mismatch_count": len(semantic_failures),
        "integrity_poison_count": len(checks),
        "integrity_poisons": checks,
        "private_cache_waiver": PRIVATE_CACHE_WAIVER,
        "private_waiver_self_test_count": len(named_waivers),
        "forbidden_regex_guard_count": guards["guard_count"],
        "cross_engine_guard_count": guards["cross_engine_guard_count"],
        "guard_self_test": guards,
        "source_path": "tools/rust_v9_cache_reentrancy_oracle.py",
        "source_sha256": contract.sha256_path(RUNNER),
        "candidate_imported": False,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }


def validate_output(path: Path, spec: contract.CandidateSpec) -> Path:
    require(not path.is_symlink(),
            "cache evidence must not target a symbolic link")
    resolved = path.resolve()
    directory = (ROOT / "candidates" / "evidence").resolve()
    require(resolved.parent == directory,
            "cache evidence escaped the candidate evidence directory")
    prefix = f"rust-v9-cache-reentrancy-{spec.family.casefold()}-"
    require(resolved.name.startswith(prefix)
            and resolved.name.endswith(".json.gz"),
            "cache evidence requires its actual independent family and gzip suffix")
    stage = resolved.name[len(prefix):-len(".json.gz")]
    require(bool(stage)
            and all(char.isascii()
                    and (char.isalnum() or char == "-") for char in stage),
            "cache evidence requires a safe explicit stage name")
    require(directory.is_dir(), "candidate evidence directory is unavailable")
    require(not resolved.exists(),
            "refusing to overwrite existing cache evidence")
    return resolved


def write_evidence(path: Path, report: dict[str, Any]) -> str:
    payload = canonical(report) + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as destination:
        with gzip.GzipFile(
            filename="",
            fileobj=destination,
            mode="wb",
            compresslevel=9,
            mtime=0,
        ) as archive:
            archive.write(payload)
    compressed = path.read_bytes()
    require(len(compressed) >= 10
            and compressed[:2] == b"\x1f\x8b"
            and not compressed[3] & 0x08
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "cache evidence has nondeterministic gzip metadata")
    require(gzip.decompress(compressed) == payload,
            "cache evidence failed its canonical round trip")
    return hashlib.sha256(compressed).hexdigest()


def run_gate(
    spec: contract.CandidateSpec, edge_path: Path, output_path: Path
) -> tuple[dict[str, Any], dict[str, Any], int]:
    verify_runtime()
    verify_fixture()
    _, proof, _ = contract.read_edge_proof(edge_path, spec)
    destination = validate_output(output_path, spec)
    first = run_worker("stdlib-a", spec)
    second = run_worker("stdlib-b", spec)
    validate_reference_pair(first, second)
    reference_failures, reference_waivers = compare_observations(
        first["observations"], second["observations"]
    )
    require(not reference_failures and not reference_waivers,
            "independently isolated pinned cache references disagree")
    guards = run_worker("guard-self-test", spec)
    poisoned = run_worker("semantic-poison", spec)
    semantic_failures, semantic_waivers = compare_observations(
        first["observations"], poisoned["observations"]
    )
    require(any(item["id"] == "cache-equal-key-reentrant-compile"
                for item in semantic_failures)
            and not semantic_waivers,
            "cache gate failed to reject a real cache-bypass control")
    candidate = run_worker("candidate", spec, edge_path)
    failures, waivers = compare_observations(
        first["observations"], candidate["observations"]
    )
    exact_passes = len(CASE_IDS) - len(failures) - len(waivers)
    require(exact_passes >= 0, "cache gate changed its case denominator")
    report = {
        "schema": SCHEMA,
        "status": "FAIL" if failures else "PASS",
        "python": "3.14.6",
        "implementation": "cpython",
        "seed": SEED,
        "fixture_sha256": FROZEN_FIXTURE_SHA256,
        "suite_path": "tools/rust_v9_cache_reentrancy_oracle.py",
        "suite_sha256": contract.sha256_path(RUNNER),
        "checks": len(CASE_IDS),
        "case_ids": list(CASE_IDS),
        "exact_public_passes": exact_passes,
        "public_mismatch_count": len(failures),
        "public_mismatches": failures,
        "private_waiver_count": len(waivers),
        "private_waivers": waivers,
        "named_private_waivers": [PRIVATE_CACHE_WAIVER],
        "stdlib_vs_stdlib_failures": reference_failures,
        "reference_a_sha256": first["observation_sha256"],
        "reference_b_sha256": second["observation_sha256"],
        "candidate_sha256": candidate["observation_sha256"],
        "semantic_poison_mismatch_count": len(semantic_failures),
        "forbidden_regex_guard_count": candidate["guard_count"],
        "forbidden_regex_guards": candidate["guards"],
        "cross_engine_guard_count": candidate["cross_engine_guard_count"],
        "cross_engine_guards": candidate["cross_engine_guards"],
        "guard_self_test": guards,
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "native_artifacts": candidate["native_artifacts"],
        "edge_oracle": proof,
        "reference": first,
        "reference_independent_repeat": second,
        "candidate": candidate,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    require(report["checks"]
            == report["exact_public_passes"]
            + report["public_mismatch_count"]
            + report["private_waiver_count"],
            "cache gate silently changed its pass, loss, or waiver denominator")
    evidence_sha256 = write_evidence(destination, report)
    summary = {
        "schema": SCHEMA,
        "status": report["status"],
        "python": "3.14.6",
        "checks": len(CASE_IDS),
        "case_ids": list(CASE_IDS),
        "exact_public_passes": exact_passes,
        "public_mismatch_count": len(failures),
        "private_waiver_count": len(waivers),
        "private_waivers": waivers,
        "stdlib_vs_stdlib_failures": 0,
        "semantic_poison_mismatch_count": len(semantic_failures),
        "forbidden_regex_guard_count": candidate["guard_count"],
        "cross_engine_guard_count": candidate["cross_engine_guard_count"],
        "candidate_module": spec.module,
        "candidate_family": spec.family,
        "evidence_path": str(destination),
        "evidence_sha256": evidence_sha256,
        "performance": "NOT MEASURED",
        "holdout": "NOT ACCESSED",
    }
    if failures:
        summary["first_public_mismatches"] = failures[:3]
    return report, summary, int(bool(failures))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    self_test = commands.add_parser(
        "self-test", help="verify the pinned reference and real guard poisons"
    )
    self_test.add_argument(
        "--module", choices=tuple(contract.SPECS),
        default="candidates.ast_candidate",
        help="name a guard family without importing that candidate",
    )

    verify = commands.add_parser(
        "verify", help="verify one edge-proven independent candidate"
    )
    verify.add_argument("--module", choices=tuple(contract.SPECS), required=True)
    verify.add_argument("--edge-oracle", type=Path, required=True)
    verify.add_argument("--output", type=Path, required=True)

    worker = commands.add_parser("worker", help=argparse.SUPPRESS)
    worker.add_argument("--role", choices=tuple(sorted(WORKER_ROLES)),
                        required=True)
    worker.add_argument("--module", choices=tuple(contract.SPECS), required=True)
    worker.add_argument("--edge-oracle", type=Path)
    return parser.parse_args()


def main() -> int:
    options = parse_args()
    spec = contract.SPECS[options.module]
    if options.command == "worker":
        result = evaluate_worker(options.role, spec, options.edge_oracle)
        print(canonical(result).decode("ascii"))
        return 0
    if options.command == "self-test":
        try:
            result = run_self_test(spec)
        except ReferenceValidationFailure as error:
            print(canonical(
                reference_failure_report(error, "self-test")
            ).decode("ascii"))
            return 1
        print(canonical(result).decode("ascii"))
        return 0
    if options.command == "verify":
        try:
            _, summary, status = run_gate(
                spec, options.edge_oracle, options.output
            )
        except ReferenceValidationFailure as error:
            print(canonical(
                reference_failure_report(error, "verify")
            ).decode("ascii"))
            return 1
        print(canonical(summary).decode("ascii"))
        return status
    raise AssertionError("unknown additive cache oracle command")


if __name__ == "__main__":
    raise SystemExit(main())
