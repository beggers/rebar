#!/usr/bin/env python3
"""Run only the separately frozen, public, corrected V10 regex experiment.

The actual V8 freeze failed. Its sources, protocol, and complete failure record
are immutable inputs, not successful experiments. This additive V10 controller
keeps the independently qualified V8 worker, correctness, memory, interval,
and replay machinery, but verifies regex results using the original V5 UTF-8
result digest. Manifest, identity, transport, and replay bytes deliberately
retain a distinct strict-ASCII canonical domain.

Direct ``python -I -B tools/postfinal_public_practice_v10.py`` first starts an
isolated interpreter with the exact repository root explicitly inserted. The
synthetic self-test never opens a fixture or starts a candidate, worker, clock,
freeze, or benchmark.
"""

from __future__ import annotations

import sys as _bootstrap_sys


_BOOTSTRAP_ENTRY = (
    "import sys;sys.path.insert(0,sys.argv[1]);"
    "from tools.postfinal_public_practice_v10 import main;"
    "main(sys.argv[2:])"
)


if __name__ == "__main__":
    import os as _bootstrap_os
    from pathlib import Path as _BootstrapPath

    _bootstrap_root = str(_BootstrapPath(__file__).resolve().parent.parent)
    _bootstrap_os.execv(
        _bootstrap_sys.executable,
        [
            _bootstrap_sys.executable,
            "-I",
            "-B",
            "-c",
            _BOOTSTRAP_ENTRY,
            _bootstrap_root,
            *_bootstrap_sys.argv[1:],
        ],
    )


import argparse
import builtins
import collections
from contextlib import contextmanager
import gzip
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterator, Mapping

from tools import postfinal_public_practice_v8 as frozen


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = Path(__file__).resolve()
VERSION = "postfinal-public-practice-v10"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v10"
PROTOCOL_PATH = VERSION_ROOT / "PROTOCOL.md"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"
GENERATOR_SOURCE_PATH = ROOT / "tools" / "postfinal_public_expansion_v10.py"

# Root independently validated every real public archive record before
# authorizing these exact stopped generator and protocol source fingerprints.
GENERATOR_SOURCE_SHA256 = (
    "ae0ff9664939b4d86a25fb860d93c02119a9a195ccf3fc32cbb805170a242065"
)
PROTOCOL_SHA256 = (
    "e918053c99255e1a528102738e02a1e5979d65eadf0049ef3beed84d26941257"
)

PLAN_SCHEMA = "rebar-postfinal-public-development-plan-v10"
REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v10"
INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v10"
ROW_SCHEMA = "rebar-postfinal-public-practice-row-v10"
SELF_TEST_SCHEMA = "rebar-postfinal-public-practice-self-test-v10"
ORACLE_SCHEMA = "rebar-postfinal-public-development-self-oracle-v10"
SEED_DOMAIN = "rebar/public-development/v10"
SELECTION_SEED = 2_026_072_450
ORDER_SEED = 2_026_072_451
BOOTSTRAP_SEED = 2_026_072_452

FROZEN_V7_MANIFEST_PATH = (
    ROOT / "performance" / "postfinal-public-v7" / "manifest.json"
)
FROZEN_V7_MANIFEST_SHA256 = (
    "465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26"
)
FROZEN_PUBLIC_FIXTURE_RELATIVE = (
    "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
)
FROZEN_PUBLIC_FIXTURE_SHA256 = (
    "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5"
)
FROZEN_PUBLIC_FIXTURE_CASES = 10_312
FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES = 9_731
FROZEN_BOUNDED_INELIGIBLE_PUBLIC_CASES = 581

FROZEN_V8_SOURCE_PATH = ROOT / "tools" / "postfinal_public_practice_v8.py"
FROZEN_V8_SOURCE_SHA256 = (
    "7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f"
)
FROZEN_V8_GENERATOR_PATH = ROOT / "tools" / "postfinal_public_expansion_v8.py"
FROZEN_V8_GENERATOR_SHA256 = (
    "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97"
)
FROZEN_V8_PROTOCOL_PATH = (
    ROOT / "performance" / "postfinal-public-v8" / "PROTOCOL.md"
)
FROZEN_V8_PROTOCOL_SHA256 = (
    "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095"
)
FROZEN_V8_RECORDER_PATH = (
    ROOT / "tools" / "postfinal_public_expansion_v8_failure.py"
)
FROZEN_V8_RECORDER_SHA256 = (
    "800963bc33227c936a2f8506fa80057672acb1c831b772a1bb412aec6540eb94"
)
FROZEN_V8_FAILURE_PATH = (
    ROOT / "performance" / "postfinal-public-v8" / "evidence"
    / "postfinal-public-freeze-failure-v8.json"
)
FROZEN_V8_FAILURE_SHA256 = (
    "e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba"
)
FROZEN_V8_FAILURE_SCHEMA = "rebar-postfinal-public-expansion-freeze-failure-v8"
FROZEN_V8_FIRST_LEGACY_SHA256 = (
    "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949"
)
FROZEN_V8_FIRST_ASCII_SHA256 = (
    "af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885"
)

PublicPracticeError = frozen.PublicPracticeError
require = frozen.require
valid_sha256 = frozen.valid_sha256
json_bytes = frozen.json_bytes
value_digest = frozen.value_digest
file_sha256 = frozen.file_sha256
require_candidate_free = frozen.require_candidate_free
candidate_imports = frozen.candidate_imports
pack_public = frozen.pack_public
unpack_public = frozen.unpack_public
canonical_public = frozen.canonical_public
semantic_identity = frozen.semantic_identity
source_kind = frozen.source_kind
result_density = frozen.result_density
process_memory_valid = frozen.process_memory_valid

_FROZEN_V8_VERIFIED_PROVENANCE = frozen.verified_provenance
_FROZEN_V8_MEASURE = frozen.measure
_FROZEN_V8_VERIFY = frozen.verify
_FROZEN_V8_SELF_TEST = frozen.self_test
_FROZEN_V8_QUALIFICATION_WORKER = frozen.run_qualification_worker


def legacy_result_digest(value: Any) -> str:
    """Reproduce the original, genuine ``tools.perf_v5.digest`` exactly."""

    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def v8_failure_contract() -> dict[str, Any]:
    """Expose exactly the agreed, genuinely failed public-freeze evidence."""

    return {
        "source_path": str(FROZEN_V8_GENERATOR_PATH.relative_to(ROOT)),
        "source_sha256": FROZEN_V8_GENERATOR_SHA256,
        "runner_path": str(FROZEN_V8_SOURCE_PATH.relative_to(ROOT)),
        "runner_sha256": FROZEN_V8_SOURCE_SHA256,
        "protocol_path": str(FROZEN_V8_PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_sha256": FROZEN_V8_PROTOCOL_SHA256,
        "recorder_path": str(FROZEN_V8_RECORDER_PATH.relative_to(ROOT)),
        "recorder_sha256": FROZEN_V8_RECORDER_SHA256,
        "report_path": str(FROZEN_V8_FAILURE_PATH.relative_to(ROOT)),
        "report_sha256": FROZEN_V8_FAILURE_SHA256,
        "status": "FAIL",
        "failure_class": "PublicExpansionError",
        "public_fixture_cases": FROZEN_PUBLIC_FIXTURE_CASES,
        "failed_reference_answers": 577,
        "first_failure_id": "cal.unicode.words",
        "first_failure_legacy_utf8_sha256": FROZEN_V8_FIRST_LEGACY_SHA256,
        "first_failure_frozen_v8_ascii_sha256": FROZEN_V8_FIRST_ASCII_SHA256,
        "opaque_history_values_deserialized": 0,
    }


def validate_v8_failure_contract(document: Any) -> dict[str, Any]:
    """Reject any omitted, extra, or rewritten historical failure field."""

    expected = v8_failure_contract()
    require(
        isinstance(document, dict) and set(document) == set(expected),
        "the public V10 manifest changed the exact frozen V8 failure contract",
    )
    for name, value in expected.items():
        actual = document.get(name)
        require(
            type(actual) is type(value) and actual == value,
            f"the frozen public V8 failure evidence changed: {name}",
        )
    return document


def validate_v8_failure_report(document: Any) -> dict[str, Any]:
    """Validate the real failure without opening or decoding any fixture."""

    require(isinstance(document, dict), "the actual public V8 failure is missing")
    required = {
        "schema": FROZEN_V8_FAILURE_SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "production_cases_generated": 0,
        "production_manifest_created": False,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
        "recording_source_path": str(FROZEN_V8_RECORDER_PATH.relative_to(ROOT)),
        "recording_source_sha256": FROZEN_V8_RECORDER_SHA256,
    }
    for name, value in required.items():
        actual = document.get(name)
        require(
            type(actual) is type(value) and actual == value,
            f"the genuine failed V8 experiment was rewritten: {name}",
        )
    frozen_design = document.get("frozen_design")
    expected_design = {
        "expander_path": str(FROZEN_V8_GENERATOR_PATH.relative_to(ROOT)),
        "expander_sha256": FROZEN_V8_GENERATOR_SHA256,
        "runner_path": str(FROZEN_V8_SOURCE_PATH.relative_to(ROOT)),
        "runner_sha256": FROZEN_V8_SOURCE_SHA256,
        "protocol_path": str(FROZEN_V8_PROTOCOL_PATH.relative_to(ROOT)),
        "protocol_sha256": FROZEN_V8_PROTOCOL_SHA256,
        "fixture_path": FROZEN_PUBLIC_FIXTURE_RELATIVE,
        "fixture_sha256": FROZEN_PUBLIC_FIXTURE_SHA256,
        "goal_path": "GOAL.md",
        "goal_sha256": frozen.GOAL_SHA256,
    }
    require(
        isinstance(frozen_design, dict)
        and frozen_design == expected_design,
        "the actual V8 failure substituted its pushed source or fixture provenance",
    )
    failure = document.get("failure")
    require(
        isinstance(failure, dict)
        and failure.get("class") == "PublicExpansionError"
        and failure.get("module") == "tools.postfinal_public_expansion_v8"
        and failure.get("phase") == "pre-candidate public fixture authentication"
        and failure.get("message") == "corrupt public reference answer"
        and isinstance(failure.get("cause"), str)
        and "unescaped UTF-8" in failure["cause"]
        and "ASCII-escaped" in failure["cause"],
        "the frozen V8 failure was relabeled or attributed to a candidate",
    )
    diagnosis = document.get("public_fixture_diagnosis")
    require(
        isinstance(diagnosis, dict)
        and diagnosis.get("public_fixture_cases") == 10_312
        and diagnosis.get("legacy_utf8_digest_matches") == 10_312
        and diagnosis.get("frozen_v8_ascii_digest_matches") == 9_735
        and diagnosis.get("failed_reference_answers") == 577
        and diagnosis.get("opaque_history_fields_skipped") == 10_312
        and diagnosis.get("opaque_history_values_deserialized") == 0
        and diagnosis.get("affected_public_input_counts") == {"text": 577}
        and diagnosis.get("affected_public_api_counts")
        == {"escape": 48, "findall": 483, "split": 46},
        "the frozen V8 failure concealed a genuine public Unicode answer",
    )
    first = diagnosis.get("first_failure")
    require(
        isinstance(first, dict)
        and first.get("id") == "cal.unicode.words"
        and first.get("api") == "findall"
        and first.get("category") == "unicode"
        and first.get("cohort") == "calibration"
        and first.get("legacy_utf8_sha256") == FROZEN_V8_FIRST_LEGACY_SHA256
        and first.get("recorded_sha256") == FROZEN_V8_FIRST_LEGACY_SHA256
        and first.get("frozen_v8_ascii_sha256") == FROZEN_V8_FIRST_ASCII_SHA256
        and first["legacy_utf8_sha256"] != first["frozen_v8_ascii_sha256"],
        "the frozen V8 first failing Unicode result was omitted or substituted",
    )
    reproductions = document.get("reproduction")
    require(
        isinstance(reproductions, list)
        and len(reproductions) == 2
        and all(isinstance(item, dict) for item in reproductions)
        and reproductions[0].get("exception_class") == "ModuleNotFoundError"
        and reproductions[0].get("message") == "No module named 'tools'"
        and reproductions[1].get("exception_class") == "PublicExpansionError"
        and reproductions[1].get("message") == "corrupt public reference answer",
        "the actual V8 isolation and result-codec failures were misrepresented",
    )
    return document


def validate_v7_parent_manifest(document: Any) -> dict[str, Any]:
    """Validate the exact public V7 parent without reading timing or results."""

    require(
        isinstance(document, dict),
        "the exact frozen public V7 parent is not an object",
    )
    expected_header = {
        "schema": "rebar-rust-balanced-calibration-plan-v7",
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v7",
        "python": "3.14.6",
        "cohort": frozen.COHORT,
        "cases": frozen.ORIGINAL_CASE_COUNT,
        "all_bounded_workload_categories": frozen.CATEGORY_COUNT,
        "goal_sha256": frozen.GOAL_SHA256,
        "runner_sha256": frozen.V7_SOURCE_SHA256,
        "timing_performed": False,
        "holdout_accessed": False,
    }
    for name, expected in expected_header.items():
        actual = document.get(name)
        require(
            type(actual) is type(expected) and actual == expected,
            f"the exact frozen public V7 parent changed: {name}",
        )

    descriptors = document.get("selected_cases")
    categories = document.get("categories")
    operations = document.get("public_operations")
    require(
        isinstance(descriptors, list)
        and len(descriptors) == frozen.ORIGINAL_CASE_COUNT
        and isinstance(categories, dict)
        and len(categories) == frozen.CATEGORY_COUNT
        and all(
            isinstance(name, str)
            and bool(name)
            and type(count) is int
            and count > 0
            for name, count in categories.items()
        )
        and sum(categories.values()) == frozen.ORIGINAL_CASE_COUNT
        and isinstance(operations, dict)
        and set(operations) == frozen.PUBLIC_OPERATIONS
        and all(type(count) is int and count > 0 for count in operations.values())
        and sum(operations.values()) == frozen.ORIGINAL_CASE_COUNT,
        "the exact frozen V7 parent lost an original case, category, or API",
    )

    descriptor_keys = {
        "api",
        "case",
        "category",
        "cohort",
        "expected_result_sha256",
        "frozen_operations",
        "input",
        "lifecycle",
        "result_count",
        "result_density",
        "selection_reasons",
        "subject_length",
    }
    seen: set[str] = set()
    counted_categories: collections.Counter[str] = collections.Counter()
    counted_operations: collections.Counter[str] = collections.Counter()
    input_kinds: set[str] = set()
    for index, descriptor in enumerate(descriptors):
        require(
            isinstance(descriptor, dict)
            and set(descriptor) == descriptor_keys,
            f"the frozen V7 parent changed an original descriptor: {index}",
        )
        identifier = descriptor["case"]
        category = descriptor["category"]
        operation = descriptor["api"]
        input_kind = descriptor["input"]
        reasons = descriptor["selection_reasons"]
        require(
            isinstance(identifier, str)
            and bool(identifier)
            and identifier not in seen
            and category in categories
            and operation in operations
            and descriptor["cohort"] == frozen.COHORT
            and valid_sha256(descriptor["expected_result_sha256"])
            and type(descriptor["frozen_operations"]) is int
            and descriptor["frozen_operations"] > 0
            and input_kind in {"text", "bytes", "bytearray", "memoryview"}
            and descriptor["lifecycle"] in {"cold", "compiled", "module"}
            and type(descriptor["result_count"]) is int
            and 0 <= descriptor["result_count"] <= frozen.RESULT_LIMIT
            and descriptor["result_density"] in {"few", "many", "none", "one"}
            and isinstance(reasons, list)
            and all(isinstance(reason, str) and bool(reason) for reason in reasons)
            and type(descriptor["subject_length"]) is int
            and 0 <= descriptor["subject_length"] <= frozen.SUBJECT_LIMIT,
            f"the frozen V7 parent substituted original case {index}",
        )
        seen.add(identifier)
        counted_categories[category] += 1
        counted_operations[operation] += 1
        input_kinds.add(input_kind)
    require(
        dict(sorted(counted_categories.items())) == categories
        and dict(sorted(counted_operations.items())) == operations
        and input_kinds == {"text", "bytes", "bytearray", "memoryview"},
        "the frozen public V7 parent misreported its original descriptors",
    )
    return document


def validate_original_descriptor_prefix(
    v6_parent: Any,
    v7_parent: Any,
    descriptors: Any,
) -> None:
    """Bind every V10 original descriptor independently to both parents."""

    checked_v7 = validate_v7_parent_manifest(v7_parent)
    require(
        isinstance(v6_parent, dict)
        and v6_parent.get("postfinal_schema")
        == "rebar-postfinal-public-practice-plan-v6"
        and v6_parent.get("python") == "3.14.6"
        and v6_parent.get("cohort") == frozen.COHORT
        and v6_parent.get("cases") == frozen.ORIGINAL_CASE_COUNT
        and isinstance(v6_parent.get("selected_cases"), list)
        and len(v6_parent["selected_cases"]) == frozen.ORIGINAL_CASE_COUNT
        and isinstance(descriptors, list)
        and len(descriptors) >= frozen.ORIGINAL_CASE_COUNT
        and descriptors[:frozen.ORIGINAL_CASE_COUNT]
        == checked_v7["selected_cases"]
        == v6_parent["selected_cases"],
        "V10 changed one of the exact 8,192 frozen V6 and V7 descriptors",
    )


@contextmanager
def v10_context() -> Iterator[None]:
    """Temporarily reuse audited V8 machinery without changing frozen bytes."""

    updates: dict[str, Any] = {
        "SOURCE_PATH": SOURCE_PATH,
        "VERSION": VERSION,
        "VERSION_ROOT": VERSION_ROOT,
        "PROTOCOL_PATH": PROTOCOL_PATH,
        "MANIFEST_PATH": MANIFEST_PATH,
        "EVIDENCE_ROOT": EVIDENCE_ROOT,
        "RAW_PATH": RAW_PATH,
        "SUMMARY_PATH": SUMMARY_PATH,
        "INTEGRITY_PATH": INTEGRITY_PATH,
        "GENERATOR_SOURCE_PATH": GENERATOR_SOURCE_PATH,
        "GENERATOR_SOURCE_SHA256": GENERATOR_SOURCE_SHA256,
        "PROTOCOL_SHA256": PROTOCOL_SHA256,
        "PLAN_SCHEMA": PLAN_SCHEMA,
        "REPORT_SCHEMA": REPORT_SCHEMA,
        "INTEGRITY_SCHEMA": INTEGRITY_SCHEMA,
        "ROW_SCHEMA": ROW_SCHEMA,
        "SELF_TEST_SCHEMA": SELF_TEST_SCHEMA,
        "SEED_DOMAIN": SEED_DOMAIN,
        "SELECTION_SEED": SELECTION_SEED,
        "ORDER_SEED": ORDER_SEED,
        "BOOTSTRAP_SEED": BOOTSTRAP_SEED,
        "verified_provenance": verified_provenance,
        "load_manifest": load_manifest,
    }
    originals = {name: getattr(frozen, name) for name in updates}
    try:
        for name, value in updates.items():
            setattr(frozen, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(frozen, name, value)


def verified_v8_failure() -> dict[str, Any]:
    """Read only the exact pushed V8 source, recorder, and FAIL evidence."""

    require_candidate_free()
    require(
        getattr(frozen, "__name__", None)
        == "tools.postfinal_public_practice_v8"
        and Path(getattr(frozen, "__file__", "")).resolve()
        == FROZEN_V8_SOURCE_PATH.resolve(),
        "the immutable failed V8 source module was substituted",
    )
    for path, digest, label in (
        (FROZEN_V8_SOURCE_PATH, FROZEN_V8_SOURCE_SHA256, "frozen failed V8 runner"),
        (
            FROZEN_V8_GENERATOR_PATH,
            FROZEN_V8_GENERATOR_SHA256,
            "frozen failed V8 expander",
        ),
        (
            FROZEN_V8_PROTOCOL_PATH,
            FROZEN_V8_PROTOCOL_SHA256,
            "frozen failed V8 protocol",
        ),
        (
            FROZEN_V8_RECORDER_PATH,
            FROZEN_V8_RECORDER_SHA256,
            "frozen actual V8 failure recorder",
        ),
    ):
        frozen.require_pinned_file(path, digest, label)
    report = frozen.read_pinned_json(
        FROZEN_V8_FAILURE_PATH,
        FROZEN_V8_FAILURE_SHA256,
        "actual source-bound pre-candidate V8 failure",
    )
    validate_v8_failure_report(report)
    require_candidate_free()
    return v8_failure_contract()


def verified_provenance() -> dict[str, Any]:
    """Independently authenticate V10 proofs and the genuine V8 failure."""

    if frozen.VERSION != VERSION or frozen.SOURCE_PATH != SOURCE_PATH:
        with v10_context():
            return verified_provenance()
    require_candidate_free()
    require(
        valid_sha256(GENERATOR_SOURCE_SHA256)
        and valid_sha256(PROTOCOL_SHA256),
        "the separate V10 expander and protocol are not finalized",
    )
    parent = frozen.read_pinned_json(
        FROZEN_V7_MANIFEST_PATH,
        FROZEN_V7_MANIFEST_SHA256,
        "exact original 8,192-case public V7 manifest",
    )
    validate_v7_parent_manifest(parent)
    failure = verified_v8_failure()
    inherited = _FROZEN_V8_VERIFIED_PROVENANCE()
    require(
        isinstance(inherited, dict)
        and inherited.get("runner_sha256") == file_sha256(SOURCE_PATH)
        and inherited.get("generator_source_sha256") == GENERATOR_SOURCE_SHA256
        and inherited.get("protocol_sha256") == PROTOCOL_SHA256
        and frozen.validate_stage10_correctness_contract(
            inherited.get("stage10_correctness")
        ) == frozen.stage10_correctness_contract(),
        "the additive V10 runner lost its independently qualified provenance",
    )
    require_candidate_free()
    return {
        **inherited,
        "v7_manifest_sha256": FROZEN_V7_MANIFEST_SHA256,
        "v8_failure": failure,
    }


def load_manifest(path: Path, provenance: Mapping[str, Any]) -> dict[str, Any]:
    """Validate every V10 case using the authentic legacy result hash."""

    if frozen.VERSION != VERSION or frozen.SOURCE_PATH != SOURCE_PATH:
        with v10_context():
            return load_manifest(path, provenance)
    exact = frozen.exact_output(path, MANIFEST_PATH, "frozen public V10 manifest")
    try:
        with exact.open("rb") as stream:
            document = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PublicPracticeError(
            "cannot read the exact frozen public V10 manifest"
        ) from error
    require(isinstance(document, dict), "the public V10 manifest is not an object")
    expected_header = {
        "schema": PLAN_SCHEMA,
        "python": "3.14.6",
        "cohort": frozen.COHORT,
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "seed_domain": SEED_DOMAIN,
        "selection_seed": SELECTION_SEED,
        "order_seed_domain": SEED_DOMAIN + "/paired-order",
        "order_seed": ORDER_SEED,
        "bootstrap_seed_domain": SEED_DOMAIN + "/bootstrap",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "runner_path": "tools/postfinal_public_expansion_v10.py",
        "runner_sha256": GENERATOR_SOURCE_SHA256,
        "protocol_path": "performance/postfinal-public-v10/PROTOCOL.md",
        "protocol_sha256": PROTOCOL_SHA256,
        "measurement_runner_path": "tools/postfinal_public_practice_v10.py",
        "measurement_runner_sha256": provenance["runner_sha256"],
        "cases": frozen.CASE_COUNT,
        "original_cases_preserved": frozen.ORIGINAL_CASE_COUNT,
        "all_bounded_workload_categories": frozen.CATEGORY_COUNT,
        "cases_per_category": frozen.CASES_PER_CATEGORY,
        "frozen_warmups": frozen.WARMUPS,
        "frozen_trials": frozen.TRIALS,
        "frozen_bootstrap_samples": frozen.BOOTSTRAPS,
        "expected_raw_rows": frozen.EXPECTED_RAW_ROWS,
        "expected_correctness_answers": frozen.EXPECTED_CORRECTNESS_ANSWERS,
        "expected_confidence_intervals": frozen.EXPECTED_CONFIDENCE_INTERVALS,
        "expected_process_native_checks": frozen.EXPECTED_PROCESS_NATIVE_CHECKS,
        "baseline": frozen.MODULES[0],
        "candidates": list(frozen.MODULES[1:]),
        "maximum_subject_limit": frozen.SUBJECT_LIMIT,
        "maximum_result_limit": frozen.RESULT_LIMIT,
        "goal_sha256": frozen.GOAL_SHA256,
        "source_public_manifest": "performance/postfinal-public-v6/manifest.json",
        "source_public_manifest_sha256": frozen.PUBLIC_V6_MANIFEST_SHA256,
        "source_public_v6_manifest_path":
            "performance/postfinal-public-v6/manifest.json",
        "source_public_v6_manifest_sha256": frozen.PUBLIC_V6_MANIFEST_SHA256,
        "source_public_v7_manifest_path":
            "performance/postfinal-public-v7/manifest.json",
        "source_public_v7_manifest_sha256": FROZEN_V7_MANIFEST_SHA256,
        "source_public_fixture": FROZEN_PUBLIC_FIXTURE_RELATIVE,
        "source_public_fixture_sha256": FROZEN_PUBLIC_FIXTURE_SHA256,
        "qualified_source_fingerprints": provenance["qualified_source_fingerprints"],
        "native_elf_fingerprints": provenance["native_elf_fingerprints"],
        "candidate_imports": [],
        "historical_results_read": 0,
        "source_public_cases": FROZEN_PUBLIC_FIXTURE_CASES,
        "eligible_practice_cases": FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES,
        "excluded_unbounded_public_cases":
            FROZEN_BOUNDED_INELIGIBLE_PUBLIC_CASES,
        "bounded_eligible_public_source_cases":
            FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES,
        "bounded_ineligible_public_source_cases":
            FROZEN_BOUNDED_INELIGIBLE_PUBLIC_CASES,
        "opaque_history_fields_skipped": FROZEN_PUBLIC_FIXTURE_CASES,
        "opaque_history_values_deserialized": 0,
        "public_fixture_original_answers_validated": FROZEN_PUBLIC_FIXTURE_CASES,
        "timing_performed": False,
        "performance": "NOT MEASURED",
    }
    for name, expected in expected_header.items():
        actual = document.get(name)
        require(
            type(actual) is type(expected) and actual == expected,
            f"the frozen V10 public manifest changed: {name}",
        )

    oracle = document.get("independent_cpython_self_oracle")
    require(
        isinstance(oracle, dict)
        and oracle.get("workers") == 2
        and oracle.get("schema") == ORACLE_SCHEMA
        and oracle.get("python") == "3.14.6"
        and oracle.get("failed") == 0,
        "both isolated V10 public CPython references have not passed",
    )
    pinned_inputs = document.get("pinned_public_input_sha256")
    require(
        isinstance(pinned_inputs, dict),
        "the V10 generator omitted its frozen public input fingerprints",
    )
    required_inputs = (
        ("GOAL.md", frozen.GOAL_SHA256),
        (
            "performance/postfinal-public-v6/manifest.json",
            frozen.PUBLIC_V6_MANIFEST_SHA256,
        ),
        (
            "performance/postfinal-public-v7/manifest.json",
            FROZEN_V7_MANIFEST_SHA256,
        ),
        (FROZEN_PUBLIC_FIXTURE_RELATIVE, FROZEN_PUBLIC_FIXTURE_SHA256),
        ("tools/postfinal_public_practice_v7.py", frozen.V7_SOURCE_SHA256),
        (
            "performance/postfinal-public-v7/PROTOCOL.md",
            frozen.V7_PROTOCOL_SHA256,
        ),
        (
            "tools/postfinal_from_scratch_audit_v5.py",
            frozen.BASE_AUDIT_SOURCE_SHA256,
        ),
        (
            "tools/postfinal_no_delegation_audit_v5.py",
            frozen.STRICT_AUDIT_SOURCE_SHA256,
        ),
        ("tools/postfinal_no_delegation_audit_v1.py", frozen.GUARD_SOURCE_SHA256),
        (
            "tools/postfinal_cpython_locale_oracle_v1.py",
            frozen.LOCALE_SOURCE_SHA256,
        ),
        (
            "tools/python_re_universal_public_oracle_stage06.py",
            frozen.UNIVERSAL_SOURCE_SHA256,
        ),
        (
            "candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json",
            frozen.BASE_AUDIT_SHA256,
        ),
        (
            "candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json",
            frozen.STRICT_AUDIT_SHA256,
        ),
        (
            str(FROZEN_V8_SOURCE_PATH.relative_to(ROOT)),
            FROZEN_V8_SOURCE_SHA256,
        ),
        (
            str(FROZEN_V8_GENERATOR_PATH.relative_to(ROOT)),
            FROZEN_V8_GENERATOR_SHA256,
        ),
        (
            str(FROZEN_V8_PROTOCOL_PATH.relative_to(ROOT)),
            FROZEN_V8_PROTOCOL_SHA256,
        ),
        (
            str(FROZEN_V8_RECORDER_PATH.relative_to(ROOT)),
            FROZEN_V8_RECORDER_SHA256,
        ),
        (
            str(FROZEN_V8_FAILURE_PATH.relative_to(ROOT)),
            FROZEN_V8_FAILURE_SHA256,
        ),
    )
    for relative, digest in required_inputs:
        require(
            pinned_inputs.get(relative) == digest,
            f"the V10 manifest substituted a source-bound public input: {relative}",
        )
    for role, (relative, digest) in frozen.FROZEN_FAMILY_PROOFS.items():
        require(
            pinned_inputs.get(relative) == digest,
            f"the V10 manifest omitted its exact frozen {role} proof",
        )
    require(
        "stage07_correctness" not in document,
        "the V10 manifest represented a failed Stage 07 experiment as passing",
    )
    stage10 = frozen.validate_stage10_correctness_contract(
        document.get("stage10_correctness")
    )
    require(
        stage10 == provenance["stage10_correctness"],
        "the V10 manifest substituted its actual passed compatibility proof",
    )
    failure = validate_v8_failure_contract(document.get("v8_failure"))
    require(
        failure == provenance["v8_failure"],
        "the V10 manifest omitted the actual frozen V8 failure",
    )

    records = document.get("case_records")
    descriptors = document.get("selected_cases")
    categories = document.get("categories")
    operations = document.get("public_operations")
    require(
        isinstance(records, list)
        and isinstance(descriptors, list)
        and len(records) == len(descriptors) == frozen.CASE_COUNT
        and isinstance(categories, dict)
        and len(categories) == frozen.CATEGORY_COUNT
        and all(value == frozen.CASES_PER_CATEGORY for value in categories.values())
        and isinstance(operations, dict)
        and set(operations) == frozen.PUBLIC_OPERATIONS
        and all(
            isinstance(value, int)
            and not isinstance(value, bool)
            and value > 0
            for value in operations.values()
        )
        and sum(operations.values()) == frozen.CASE_COUNT,
        "the public V10 matrix lost a case, operation, or balanced category",
    )
    seen: set[str] = set()
    seen_semantic_identities: set[str] = set()
    semantic_identities: list[str] = []
    counted_categories: collections.Counter[str] = collections.Counter()
    counted_operations: collections.Counter[str] = collections.Counter()
    input_kinds: set[str] = set()
    generated = 0
    for index, (record, descriptor) in enumerate(
        zip(records, descriptors, strict=True)
    ):
        require(
            isinstance(record, dict) and isinstance(descriptor, dict),
            "the frozen V10 case or descriptor is not an object",
        )
        case = record.get("case")
        expected = record.get("expected")
        require(
            isinstance(case, dict) and isinstance(expected, dict),
            "the frozen V10 case omitted its actual reference result",
        )
        identifier = case.get("id")
        require(
            isinstance(identifier, str)
            and bool(identifier)
            and identifier not in seen
            and descriptor.get("case") == identifier
            and case.get("cohort") == expected.get("cohort") == frozen.COHORT
            and expected.get("id") == identifier
            and case.get("category")
            == expected.get("category")
            == descriptor.get("category")
            and case.get("api") in frozen.PUBLIC_OPERATIONS
            and descriptor.get("api") == case.get("api")
            and descriptor.get("lifecycle") == case.get("lifecycle")
            and isinstance(case.get("ops"), int)
            and not isinstance(case.get("ops"), bool)
            and case["ops"] > 0
            and expected.get("result_sha256")
            == legacy_result_digest(expected.get("result")),
            f"the frozen V10 case or authentic UTF-8 answer changed at {index}",
        )
        require(
            isinstance(record.get("generated"), bool)
            and record["generated"]
            is (index >= frozen.ORIGINAL_CASE_COUNT),
            "V10 did not retain the original 8,192 public cases in order",
        )
        identity = semantic_identity(case)
        require(
            record.get("semantic_identity") == identity
            and identity not in seen_semantic_identities,
            "the frozen V10 matrix repeated a type-sensitive case identity",
        )
        subject = unpack_public(case.get("string"))
        require(
            subject is None
            or (
                isinstance(subject, (str, bytes, bytearray, memoryview))
                and len(subject) <= frozen.SUBJECT_LIMIT
            ),
            "a frozen V10 public subject exceeded its exact limit",
        )
        kind = source_kind(case)
        require(
            kind in {"text", "bytes", "bytearray", "memoryview"},
            "the frozen V10 case lost its actual Python input type",
        )
        input_kinds.add(kind)
        result = expected["result"]
        result_count = (
            0 if result is None
            else len(result) if isinstance(result, (list, tuple))
            else 1
        )
        require(
            result_count <= frozen.RESULT_LIMIT,
            "the frozen V10 result exceeded its exact result bound",
        )
        require(
            isinstance(record.get("source_case"), str)
            and bool(record["source_case"]),
            "a frozen V10 case omitted its original public source identity",
        )
        if record["generated"]:
            require(
                descriptor.get("input") == kind
                and descriptor.get("source_case") == record["source_case"]
                and descriptor.get("expected_result_sha256")
                == expected["result_sha256"]
                and descriptor.get("frozen_operations") == case["ops"]
                and descriptor.get("result_count") == result_count
                and descriptor.get("result_density") == result_density(result),
                "a generated V10 case changed its input, source, or UTF-8 answer",
            )
        seen.add(identifier)
        semantic_identities.append(identity)
        seen_semantic_identities.add(identity)
        counted_categories[case["category"]] += 1
        counted_operations[case["api"]] += 1
        generated += int(record["generated"])

    v6_parent = frozen.read_pinned_json(
        frozen.PUBLIC_V6_MANIFEST_PATH,
        frozen.PUBLIC_V6_MANIFEST_SHA256,
        "exact original 8,192-case public V6 manifest",
    )
    v7_parent = frozen.read_pinned_json(
        FROZEN_V7_MANIFEST_PATH,
        FROZEN_V7_MANIFEST_SHA256,
        "exact original 8,192-case public V7 manifest",
    )
    require(
        provenance.get("v7_manifest_sha256") == FROZEN_V7_MANIFEST_SHA256,
        "the source-qualified V10 runner omitted its frozen V7 parent",
    )
    validate_original_descriptor_prefix(v6_parent, v7_parent, descriptors)
    require(
        generated == frozen.GENERATED_CASE_COUNT
        and dict(sorted(counted_categories.items())) == categories
        and dict(sorted(counted_operations.items())) == operations
        and len(semantic_identities)
        == len(seen_semantic_identities)
        == frozen.CASE_COUNT
        and document.get("semantic_identity_count") == frozen.CASE_COUNT
        and document.get("semantic_identity_sha256")
        == value_digest(semantic_identities)
        and input_kinds == {"text", "bytes", "bytearray", "memoryview"},
        "V10 changed public input types, structural identities, or denominators",
    )
    return document


def freeze(_args: argparse.Namespace) -> dict[str, Any]:
    """Freeze V10 only after authenticating the real failure and all proofs."""

    with v10_context():
        provenance = verified_provenance()
        require(
            not MANIFEST_PATH.exists() and not MANIFEST_PATH.is_symlink(),
            "refusing to overwrite the prospective public V10 manifest",
        )
        require(
            all(
                not path.exists() and not path.is_symlink()
                for path in (RAW_PATH, SUMMARY_PATH, INTEGRITY_PATH)
            ),
            "a prospective V10 freeze cannot follow any public observations",
        )
        generator = importlib.import_module(
            "tools.postfinal_public_expansion_v10"
        )
        require(
            Path(getattr(generator, "__file__", "")).resolve()
            == GENERATOR_SOURCE_PATH.resolve()
            and file_sha256(Path(generator.__file__).resolve())
            == GENERATOR_SOURCE_SHA256
            and getattr(generator, "SCHEMA", None) == PLAN_SCHEMA
            and callable(getattr(generator, "freeze_public_development", None)),
            "the exact independent V10 public expander was substituted",
        )
        require_candidate_free()
        generator.freeze_public_development()
        require_candidate_free()
        manifest = load_manifest(MANIFEST_PATH, provenance)
        return {
            "schema": PLAN_SCHEMA,
            "status": "PASS",
            "protocol_version": VERSION,
            "freeze_only": True,
            "cohort": frozen.COHORT,
            "cases": frozen.CASE_COUNT,
            "categories": frozen.CATEGORY_COUNT,
            "cases_per_category": frozen.CASES_PER_CATEGORY,
            "original_cases_preserved": frozen.ORIGINAL_CASE_COUNT,
            "generated_public_cases": frozen.GENERATED_CASE_COUNT,
            "selection_seed": SELECTION_SEED,
            "order_seed": ORDER_SEED,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "expected_raw_rows": frozen.EXPECTED_RAW_ROWS,
            "expected_correctness_answers": frozen.EXPECTED_CORRECTNESS_ANSWERS,
            "expected_confidence_intervals": frozen.EXPECTED_CONFIDENCE_INTERVALS,
            "expected_process_native_checks": frozen.EXPECTED_PROCESS_NATIVE_CHECKS,
            "goal_sha256": frozen.GOAL_SHA256,
            "v7_source_sha256": frozen.V7_SOURCE_SHA256,
            "v7_protocol_sha256": frozen.V7_PROTOCOL_SHA256,
            "v7_manifest_sha256": FROZEN_V7_MANIFEST_SHA256,
            "source_public_fixture_sha256": FROZEN_PUBLIC_FIXTURE_SHA256,
            "source_public_cases": manifest["source_public_cases"],
            "eligible_practice_cases": manifest["eligible_practice_cases"],
            "excluded_unbounded_public_cases":
                manifest["excluded_unbounded_public_cases"],
            "bounded_eligible_public_source_cases":
                manifest["bounded_eligible_public_source_cases"],
            "bounded_ineligible_public_source_cases":
                manifest["bounded_ineligible_public_source_cases"],
            "public_fixture_original_answers_validated":
                manifest["public_fixture_original_answers_validated"],
            "opaque_history_fields_skipped":
                manifest["opaque_history_fields_skipped"],
            "opaque_history_values_deserialized":
                manifest["opaque_history_values_deserialized"],
            "generator_source_sha256": GENERATOR_SOURCE_SHA256,
            "protocol_sha256": PROTOCOL_SHA256,
            "stage10_correctness": provenance["stage10_correctness"],
            "v8_failure": provenance["v8_failure"],
            "runner_sha256": provenance["runner_sha256"],
            "manifest_sha256": file_sha256(MANIFEST_PATH),
            "campaigns": provenance["campaigns"],
            "verified_family_proofs": provenance["verified_family_proofs"],
            "candidate_imported": False,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
            "public_operations": manifest["public_operations"],
            "failed": 0,
        }


def measure(args: argparse.Namespace) -> dict[str, Any]:
    """Keep every unchanged source-bound worker and per-trial V8 gate."""

    with v10_context():
        return _FROZEN_V8_MEASURE(args)


def verify(args: argparse.Namespace) -> dict[str, Any]:
    """Replay all V10 public rows without importing any regex candidate."""

    with v10_context():
        return _FROZEN_V8_VERIFY(args)


def _synthetic_v8_failure_report() -> dict[str, Any]:
    """Create the complete failure shape entirely from frozen constants."""

    return {
        "schema": FROZEN_V8_FAILURE_SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "production_cases_generated": 0,
        "production_manifest_created": False,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
        "recording_source_path": str(FROZEN_V8_RECORDER_PATH.relative_to(ROOT)),
        "recording_source_sha256": FROZEN_V8_RECORDER_SHA256,
        "frozen_design": {
            "expander_path": str(FROZEN_V8_GENERATOR_PATH.relative_to(ROOT)),
            "expander_sha256": FROZEN_V8_GENERATOR_SHA256,
            "runner_path": str(FROZEN_V8_SOURCE_PATH.relative_to(ROOT)),
            "runner_sha256": FROZEN_V8_SOURCE_SHA256,
            "protocol_path": str(FROZEN_V8_PROTOCOL_PATH.relative_to(ROOT)),
            "protocol_sha256": FROZEN_V8_PROTOCOL_SHA256,
            "fixture_path": FROZEN_PUBLIC_FIXTURE_RELATIVE,
            "fixture_sha256": FROZEN_PUBLIC_FIXTURE_SHA256,
            "goal_path": "GOAL.md",
            "goal_sha256": frozen.GOAL_SHA256,
        },
        "failure": {
            "class": "PublicExpansionError",
            "module": "tools.postfinal_public_expansion_v8",
            "phase": "pre-candidate public fixture authentication",
            "message": "corrupt public reference answer",
            "cause": "synthetic unescaped UTF-8 versus ASCII-escaped JSON",
        },
        "public_fixture_diagnosis": {
            "public_fixture_cases": FROZEN_PUBLIC_FIXTURE_CASES,
            "legacy_utf8_digest_matches": FROZEN_PUBLIC_FIXTURE_CASES,
            "frozen_v8_ascii_digest_matches": 9_735,
            "failed_reference_answers": 577,
            "opaque_history_fields_skipped": FROZEN_PUBLIC_FIXTURE_CASES,
            "opaque_history_values_deserialized": 0,
            "affected_public_input_counts": {"text": 577},
            "affected_public_api_counts": {
                "escape": 48,
                "findall": 483,
                "split": 46,
            },
            "first_failure": {
                "id": "cal.unicode.words",
                "api": "findall",
                "category": "unicode",
                "cohort": "calibration",
                "legacy_utf8_sha256": FROZEN_V8_FIRST_LEGACY_SHA256,
                "recorded_sha256": FROZEN_V8_FIRST_LEGACY_SHA256,
                "frozen_v8_ascii_sha256": FROZEN_V8_FIRST_ASCII_SHA256,
            },
        },
        "reproduction": [
            {
                "exception_class": "ModuleNotFoundError",
                "message": "No module named 'tools'",
            },
            {
                "exception_class": "PublicExpansionError",
                "message": "corrupt public reference answer",
            },
        ],
    }


def _synthetic_v7_parent_manifest() -> dict[str, Any]:
    """Make all original-parent controls in memory without opening a file."""

    operations = sorted(frozen.PUBLIC_OPERATIONS)
    input_kinds = ("text", "bytes", "bytearray", "memoryview")
    selected = [
        {
            "api": operations[index % len(operations)],
            "case": f"synthetic-public-v7-original-{index}",
            "category": f"synthetic-public-category-{index % frozen.CATEGORY_COUNT:03d}",
            "cohort": frozen.COHORT,
            "expected_result_sha256": "a" * 64,
            "frozen_operations": 1,
            "input": input_kinds[index % len(input_kinds)],
            "lifecycle": "module",
            "result_count": 1,
            "result_density": "one",
            "selection_reasons": ["synthetic-public-parent-control"],
            "subject_length": 0,
        }
        for index in range(frozen.ORIGINAL_CASE_COUNT)
    ]
    category_counts = collections.Counter(
        descriptor["category"] for descriptor in selected
    )
    operation_counts = collections.Counter(
        descriptor["api"] for descriptor in selected
    )
    return {
        "schema": "rebar-rust-balanced-calibration-plan-v7",
        "postfinal_schema": "rebar-postfinal-public-practice-plan-v7",
        "python": "3.14.6",
        "cohort": frozen.COHORT,
        "cases": frozen.ORIGINAL_CASE_COUNT,
        "all_bounded_workload_categories": frozen.CATEGORY_COUNT,
        "goal_sha256": frozen.GOAL_SHA256,
        "runner_sha256": frozen.V7_SOURCE_SHA256,
        "timing_performed": False,
        "holdout_accessed": False,
        "selected_cases": selected,
        "categories": dict(sorted(category_counts.items())),
        "public_operations": dict(sorted(operation_counts.items())),
    }


def self_test() -> dict[str, Any]:
    """Run inherited and V10-specific controls without clocks or files."""

    before = candidate_imports()
    inherited = _FROZEN_V8_SELF_TEST()
    require(
        isinstance(inherited, dict)
        and inherited.get("status") == "PASS"
        and inherited.get("failed") == 0
        and inherited.get("checks") == 212
        and inherited.get("candidate_imports") == []
        and inherited.get("worker_processes_started") == 0
        and inherited.get("oracle_processes_started") == 0
        and inherited.get("public_case_files_opened") == 0
        and inherited.get("manifest_files_opened") == 0
        and inherited.get("files_written") == 0
        and inherited.get("historical_results_read") == 0
        and inherited.get("holdout_accessed") is False
        and inherited.get("timing_performed") is False
        and inherited.get("performance") == "NOT MEASURED",
        "the immutable V8 synthetic controls or source guards were weakened",
    )
    inherited_names = inherited.get("check_names")
    require(
        isinstance(inherited_names, list)
        and len(inherited_names) == inherited["checks"]
        and all(isinstance(name, str) for name in inherited_names),
        "the complete V8 control identities were omitted",
    )
    checks = ["inherited-v8/" + name for name in inherited_names]
    effects: collections.Counter[str] = collections.Counter()

    def check(name: str, condition: object) -> None:
        require(name not in checks, f"duplicate synthetic V10 control: {name}")
        require(condition, f"synthetic V10 public-practice control failed: {name}")
        checks.append(name)

    def rejects(name: str, action: Any) -> None:
        try:
            action()
        except (
            PublicPracticeError,
            OSError,
            TypeError,
            ValueError,
            UnicodeError,
            OverflowError,
        ):
            check(name, True)
        else:
            raise PublicPracticeError(f"synthetic V10 poison was accepted: {name}")

    def blocked(kind: str) -> Any:
        def deny(*_args: Any, **_kwargs: Any) -> Any:
            effects[kind] += 1
            raise PublicPracticeError(f"V10 synthetic controls cannot access {kind}")

        return deny

    clock_names = (
        "perf_counter",
        "perf_counter_ns",
        "monotonic",
        "monotonic_ns",
        "process_time",
        "process_time_ns",
        "thread_time",
        "thread_time_ns",
        "time",
        "time_ns",
    )
    saved_run = subprocess.run
    saved_popen = subprocess.Popen
    saved_gzip = gzip.open
    saved_path_open = Path.open
    saved_builtin_open = builtins.open
    saved_os_open = os.open
    saved_clocks = {
        name: getattr(time, name)
        for name in clock_names
        if hasattr(time, name)
    }
    subprocess.run = blocked("worker")  # type: ignore[assignment]
    subprocess.Popen = blocked("worker")  # type: ignore[assignment]
    gzip.open = blocked("fixture")  # type: ignore[assignment]
    Path.open = blocked("path")  # type: ignore[assignment]
    builtins.open = blocked("file")  # type: ignore[assignment]
    os.open = blocked("output")  # type: ignore[assignment]
    for name in saved_clocks:
        setattr(time, name, blocked("clock"))

    try:
        check("v10-domain-is-separate", SEED_DOMAIN == "rebar/public-development/v10")
        check(
            "v10-three-seeds-are-exact-and-distinct",
            (SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED)
            == (2_026_072_450, 2_026_072_451, 2_026_072_452)
            and len({SELECTION_SEED, ORDER_SEED, BOOTSTRAP_SEED}) == 3,
        )
        check(
            "v10-schemas-cannot-alias-failed-v8",
            all(value.endswith("-v10") for value in (
                PLAN_SCHEMA,
                REPORT_SCHEMA,
                INTEGRITY_SCHEMA,
                ROW_SCHEMA,
                SELF_TEST_SCHEMA,
                ORACLE_SCHEMA,
            )),
        )
        check(
            "v10-independent-generator-is-pinned-or-explicitly-fail-closed",
            GENERATOR_SOURCE_SHA256 is None
            or valid_sha256(GENERATOR_SOURCE_SHA256),
        )
        check(
            "v10-independent-protocol-is-pinned-or-explicitly-fail-closed",
            PROTOCOL_SHA256 is None or valid_sha256(PROTOCOL_SHA256),
        )
        check(
            "v10-rejects-the-actually-falsified-provisional-generator",
            GENERATOR_SOURCE_SHA256
            != "9459e68cd9bf3d4190670e15f518b70f7127c6a3ab472d85e127cdd388b5a43e",
        )
        check(
            "v10-statically-pins-the-exact-pushed-public-v7-runner",
            frozen.V7_SOURCE_SHA256
            == "cc5b79daf3a0d018d15c76d01665cf94a30d3838c5a5c21389cba51444e96e7e",
        )
        check(
            "v10-statically-pins-the-exact-pushed-public-v7-protocol",
            frozen.V7_PROTOCOL_SHA256
            == "c8fed02bde3d2b096905a44db99405b47801743749053e8dc402cb70cc1f51c0",
        )
        check(
            "v10-statically-pins-the-exact-pushed-public-v7-manifest",
            FROZEN_V7_MANIFEST_SHA256
            == "465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26"
            and valid_sha256(FROZEN_V7_MANIFEST_SHA256)
            and str(FROZEN_V7_MANIFEST_PATH.relative_to(ROOT))
            == "performance/postfinal-public-v7/manifest.json",
        )
        check(
            "v10-pins-every-authenticated-public-archive-answer",
            FROZEN_PUBLIC_FIXTURE_CASES == 10_312
            and FROZEN_PUBLIC_FIXTURE_RELATIVE
            == "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
            and FROZEN_PUBLIC_FIXTURE_SHA256
            == "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5"
            and valid_sha256(FROZEN_PUBLIC_FIXTURE_SHA256),
        )
        check(
            "v10-preserves-the-entire-public-archive-and-bounded-denominators",
            FROZEN_PUBLIC_FIXTURE_CASES == 10_312
            and FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES == 9_731
            and FROZEN_BOUNDED_INELIGIBLE_PUBLIC_CASES == 581
            and FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES
            + FROZEN_BOUNDED_INELIGIBLE_PUBLIC_CASES
            == FROZEN_PUBLIC_FIXTURE_CASES
            and FROZEN_BOUNDED_ELIGIBLE_PUBLIC_CASES
            >= frozen.ORIGINAL_CASE_COUNT,
        )
        check(
            "v10-outputs-never-reuse-failed-v8-or-reserved-v9",
            all(
                "postfinal-public-v10" in str(path)
                and "postfinal-public-v8" not in str(path)
                and "postfinal-public-v9" not in str(path)
                for path in (
                    PROTOCOL_PATH,
                    MANIFEST_PATH,
                    RAW_PATH,
                    SUMMARY_PATH,
                    INTEGRITY_PATH,
                )
            ),
        )
        check(
            "v10-isolated-bootstrap-imports-the-exact-public-module",
            "tools.postfinal_public_practice_v10 import main"
            in _BOOTSTRAP_ENTRY
            and "sys.path.insert(0,sys.argv[1])" in _BOOTSTRAP_ENTRY,
        )
        sample_ascii = {"value": "plain-ascii"}
        sample_unicode = {
            "value": "caf\u00e9 \u03a9 \U0001f600",
            "nested": ["\u4e2d", {"name": "\u00e9"}],
        }
        reference_utf8 = hashlib.sha256(
            json.dumps(
                sample_unicode,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        check(
            "v10-legacy-and-structural-ascii-digests-agree-for-ascii",
            legacy_result_digest(sample_ascii) == value_digest(sample_ascii),
        )
        check(
            "v10-legacy-utf8-and-escaped-structural-digests-diverge",
            legacy_result_digest(sample_unicode) != value_digest(sample_unicode),
        )
        check(
            "v10-legacy-utf8-result-reproduces-the-original-v5-codec",
            legacy_result_digest(sample_unicode) == reference_utf8,
        )
        check(
            "v10-legacy-result-hash-preserves-sorted-nested-json",
            legacy_result_digest({"b": "\u03a9", "a": "\u00e9"})
            == legacy_result_digest({"a": "\u00e9", "b": "\u03a9"}),
        )
        check(
            "v10-manifest-transport-remains-strict-ascii",
            json_bytes(sample_unicode).isascii(),
        )
        rejects(
            "v10-legacy-utf8-rejects-an-unencodable-lone-surrogate",
            lambda: legacy_result_digest({"value": "\ud800"}),
        )
        check(
            "v10-structural-domain-preserves-lone-surrogates",
            value_digest({"value": "\ud800"})
            != value_digest({"value": "\ufffd"}),
        )
        synthetic_parent = _synthetic_v7_parent_manifest()
        check(
            "v10-authenticates-all-8192-public-v7-parent-descriptors",
            validate_v7_parent_manifest(synthetic_parent) == synthetic_parent,
        )
        for name, poisoned in (
            ("schema", "rebar-substituted-parent"),
            ("postfinal_schema", "rebar-postfinal-public-practice-plan-v8"),
            ("python", "3.14.5"),
            ("cohort", "holdout"),
            ("cases", 8_191),
            ("all_bounded_workload_categories", 259),
            ("goal_sha256", "0" * 64),
            ("runner_sha256", "0" * 64),
            ("timing_performed", True),
            ("holdout_accessed", True),
        ):
            rejects(
                "v10-rejects-substituted-public-v7-parent-" + name,
                lambda field=name, value=poisoned: (
                    validate_v7_parent_manifest({
                        **synthetic_parent,
                        field: value,
                    })
                ),
            )
        rejects(
            "v10-rejects-a-missing-public-v7-parent-original",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "selected_cases": synthetic_parent["selected_cases"][:-1],
            }),
        )
        rejects(
            "v10-rejects-a-duplicated-public-v7-parent-original",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "selected_cases": [
                    synthetic_parent["selected_cases"][0],
                    synthetic_parent["selected_cases"][0],
                    *synthetic_parent["selected_cases"][2:],
                ],
            }),
        )
        rejects(
            "v10-rejects-a-substituted-public-v7-parent-result-hash",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "selected_cases": [
                    {
                        **synthetic_parent["selected_cases"][0],
                        "expected_result_sha256": "not-a-result-fingerprint",
                    },
                    *synthetic_parent["selected_cases"][1:],
                ],
            }),
        )
        rejects(
            "v10-rejects-a-substituted-public-v7-parent-api",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "selected_cases": [
                    {
                        **synthetic_parent["selected_cases"][0],
                        "api": "hidden-foreign-api",
                    },
                    *synthetic_parent["selected_cases"][1:],
                ],
            }),
        )
        rejects(
            "v10-rejects-a-substituted-public-v7-parent-input-type",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "selected_cases": [
                    {
                        **synthetic_parent["selected_cases"][0],
                        "input": "foreign-type",
                    },
                    *synthetic_parent["selected_cases"][1:],
                ],
            }),
        )
        rejects(
            "v10-rejects-misreported-public-v7-parent-category-counts",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "categories": {
                    **synthetic_parent["categories"],
                    "synthetic-public-category-000": 0,
                },
            }),
        )
        rejects(
            "v10-rejects-misreported-public-v7-parent-api-counts",
            lambda: validate_v7_parent_manifest({
                **synthetic_parent,
                "public_operations": {
                    **synthetic_parent["public_operations"],
                    "compile": 0,
                },
            }),
        )
        synthetic_v6_parent = {
            "postfinal_schema": "rebar-postfinal-public-practice-plan-v6",
            "python": "3.14.6",
            "cohort": frozen.COHORT,
            "cases": frozen.ORIGINAL_CASE_COUNT,
            "selected_cases": list(synthetic_parent["selected_cases"]),
        }
        check(
            "v10-authenticates-every-original-against-both-public-parents",
            validate_original_descriptor_prefix(
                synthetic_v6_parent,
                synthetic_parent,
                list(synthetic_parent["selected_cases"]),
            )
            is None,
        )
        rejects(
            "v10-rejects-a-divergent-frozen-v6-parent-original",
            lambda: validate_original_descriptor_prefix(
                {
                    **synthetic_v6_parent,
                    "selected_cases": [
                        {
                            **synthetic_parent["selected_cases"][0],
                            "case": "substituted-v6-original",
                        },
                        *synthetic_parent["selected_cases"][1:],
                    ],
                },
                synthetic_parent,
                list(synthetic_parent["selected_cases"]),
            ),
        )
        rejects(
            "v10-rejects-a-divergent-v10-original-descriptor-prefix",
            lambda: validate_original_descriptor_prefix(
                synthetic_v6_parent,
                synthetic_parent,
                [
                    {
                        **synthetic_parent["selected_cases"][0],
                        "case": "substituted-v10-original",
                    },
                    *synthetic_parent["selected_cases"][1:],
                ],
            ),
        )
        failure = v8_failure_contract()
        check(
            "v10-preserves-only-the-exact-18-field-real-v8-failure",
            set(failure) == {
                "source_path",
                "source_sha256",
                "runner_path",
                "runner_sha256",
                "protocol_path",
                "protocol_sha256",
                "recorder_path",
                "recorder_sha256",
                "report_path",
                "report_sha256",
                "status",
                "failure_class",
                "public_fixture_cases",
                "failed_reference_answers",
                "first_failure_id",
                "first_failure_legacy_utf8_sha256",
                "first_failure_frozen_v8_ascii_sha256",
                "opaque_history_values_deserialized",
            }
            and len(failure) == 18,
        )
        check(
            "v10-authenticates-an-actual-fail-never-a-passing-v8",
            validate_v8_failure_contract(dict(failure)) == failure
            and failure["status"] == "FAIL"
            and failure["failed_reference_answers"] == 577,
        )
        for name, expected in failure.items():
            if isinstance(expected, bool):
                poisoned: Any = not expected
            elif isinstance(expected, int):
                poisoned = expected + 1
            elif name.endswith("sha256"):
                poisoned = "0" * 64
            else:
                poisoned = "substituted-failure"
            rejects(
                "v10-rejects-substituted-v8-failure-" + name,
                lambda field=name, value=poisoned: (
                    validate_v8_failure_contract({**failure, field: value})
                ),
            )
        rejects(
            "v10-rejects-extra-v8-failure-fields",
            lambda: validate_v8_failure_contract({**failure, "hidden": True}),
        )
        synthetic_report = _synthetic_v8_failure_report()
        check(
            "v10-validates-the-real-shaped-pre-candidate-v8-failure",
            validate_v8_failure_report(dict(synthetic_report))
            == synthetic_report,
        )
        for name, poisoned in (
            ("status", "PASS"),
            ("result", "PASS"),
            ("candidate_imports", 1),
            ("candidate_processes", 1),
            ("benchmark_or_timing_executed", True),
            ("clock_samples", 1),
            ("production_cases_generated", 1),
            ("production_manifest_created", True),
            ("held_out_records_deserialized", 1),
            ("recording_source_sha256", "0" * 64),
            ("performance", "MEASURED"),
        ):
            rejects(
                "v10-rejects-falsified-v8-failure-report-" + name,
                lambda field=name, value=poisoned: (
                    validate_v8_failure_report({**synthetic_report, field: value})
                ),
            )
        diagnosis = synthetic_report["public_fixture_diagnosis"]
        for name, poisoned in (
            ("public_fixture_cases", 10_311),
            ("legacy_utf8_digest_matches", 10_311),
            ("frozen_v8_ascii_digest_matches", 9_734),
            ("failed_reference_answers", 576),
            ("opaque_history_fields_skipped", 10_311),
            ("opaque_history_values_deserialized", 1),
            ("affected_public_input_counts", {"bytes": 577}),
        ):
            rejects(
                "v10-rejects-hidden-v8-unicode-diagnosis-" + name,
                lambda field=name, value=poisoned: (
                    validate_v8_failure_report({
                        **synthetic_report,
                        "public_fixture_diagnosis": {**diagnosis, field: value},
                    })
                ),
            )
        first = diagnosis["first_failure"]
        for name, poisoned in (
            ("id", "foreign-case"),
            ("api", "search"),
            ("legacy_utf8_sha256", "0" * 64),
            ("recorded_sha256", "0" * 64),
            ("frozen_v8_ascii_sha256", "0" * 64),
        ):
            rejects(
                "v10-rejects-substituted-first-unicode-failure-" + name,
                lambda field=name, value=poisoned: (
                    validate_v8_failure_report({
                        **synthetic_report,
                        "public_fixture_diagnosis": {
                            **diagnosis,
                            "first_failure": {**first, field: value},
                        },
                    })
                ),
            )
        original_version = frozen.VERSION
        original_root = frozen.VERSION_ROOT
        original_seed = frozen.SEED_DOMAIN
        original_loader = frozen.load_manifest
        original_provenance = frozen.verified_provenance
        with v10_context():
            check(
                "v10-inherits-all-33280-exact-balanced-cases",
                frozen.CASE_COUNT == 33_280
                and frozen.CATEGORY_COUNT == 260
                and frozen.CASES_PER_CATEGORY == 128
                and frozen.ORIGINAL_CASE_COUNT == 8_192,
            )
            check(
                "v10-inherits-all-four-isolated-real-families",
                frozen.MODULES == (
                    "re",
                    "candidates.rust_candidate",
                    "candidates.vm_candidate",
                    "candidates.zig_candidate",
                ),
            )
            check(
                "v10-inherits-all-twelve-public-regex-apis",
                len(frozen.PUBLIC_OPERATIONS) == 12,
            )
            check(
                "v10-frozen-trials-warmups-and-bootstrap-remain-exact",
                frozen.TRIALS == 13
                and frozen.WARMUPS == 4
                and frozen.BOOTSTRAPS == 2_000,
            )
            check(
                "v10-preserves-all-99840-untimed-global-qualifications",
                frozen.EXPECTED_GLOBAL_PREQUALIFICATIONS == 99_840,
            )
            check(
                "v10-preserves-all-1730560-paired-raw-observations",
                frozen.EXPECTED_RAW_ROWS == 1_730_560,
            )
            check(
                "v10-preserves-all-5191680-three-point-correctness-gates",
                frozen.EXPECTED_CORRECTNESS_ANSWERS == 5_191_680,
            )
            check(
                "v10-preserves-all-99843-case-and-ranking-intervals",
                frozen.EXPECTED_CONFIDENCE_INTERVALS == 99_843,
            )
            check(
                "v10-preserves-all-266248-mapped-native-runtime-guards",
                frozen.EXPECTED_PROCESS_NATIVE_CHECKS == 266_248,
            )
            check(
                "v10-reversibly-installs-only-the-additive-version",
                frozen.VERSION == VERSION
                and frozen.VERSION_ROOT == VERSION_ROOT
                and frozen.SEED_DOMAIN == SEED_DOMAIN
                and frozen.load_manifest is load_manifest
                and frozen.verified_provenance is verified_provenance,
            )
            sample_order = frozen.paired_order("synthetic-v10-case", 0)
            check(
                "v10-paired-order-preserves-four-real-engine-identities",
                set(sample_order) == set(frozen.MODULES)
                and sample_order == frozen.paired_order("synthetic-v10-case", 0),
            )
            ratios = [math.log(2.0)] * frozen.TRIALS
            speed, low, high = frozen.paired_interval(
                ratios,
                "synthetic-v10-case",
                frozen.MODULES[1],
                draws=32,
            )
            check(
                "v10-replays-deterministic-paired-confidence-intervals",
                math.isclose(speed, 2.0)
                and math.isclose(low, 2.0)
                and math.isclose(high, 2.0),
            )
            check(
                "v10-preserves-all-frozen-native-provenance-families",
                len(frozen.EXPECTED_SOURCE_FINGERPRINTS) == 12
                and len(frozen.EXPECTED_NATIVE_FILES) == 5
                and len(frozen.FROZEN_FAMILY_PROOFS) == 9
                and len(frozen.CAMPAIGN_DIGESTS) == 3,
            )
            stage = frozen.stage10_correctness_contract()
            check(
                "v10-preserves-the-real-thirteen-field-stage10-proof",
                len(stage) == 13
                and frozen.validate_stage10_correctness_contract(dict(stage))
                == stage
                and stage["source_sha256"] == frozen.STAGE10_SOURCE_SHA256
                and stage["self_oracle_sha256"]
                == frozen.STAGE10_SELF_ORACLE_SHA256
                and stage["all_candidates_sha256"]
                == frozen.STAGE10_ALL_CANDIDATE_SHA256,
            )
        check(
            "v10-restores-every-frozen-v8-version-global",
            frozen.VERSION == original_version
            and frozen.VERSION_ROOT == original_root
            and frozen.SEED_DOMAIN == original_seed
            and frozen.load_manifest is original_loader
            and frozen.verified_provenance is original_provenance,
        )
        for name, action in (
            ("worker", lambda: subprocess.run(["forbidden-v10-worker"])),
            ("fixture", lambda: gzip.open("forbidden-v10-fixture", "rb")),
            ("path", lambda: Path("forbidden-v10-path").open("rb")),
            ("file", lambda: builtins.open("forbidden-v10-file", "rb")),
            ("output", lambda: os.open("forbidden-v10-output", os.O_RDONLY)),
        ):
            rejects("v10-synthetic-blocks-real-" + name, action)
        for name in saved_clocks:
            rejects(
                "v10-synthetic-blocks-clock-" + name,
                lambda clock=name: getattr(time, clock)(),
            )
        check(
            "v10-exercises-all-zero-side-effect-process-file-and-clock-poisons",
            effects == {
                "worker": 1,
                "fixture": 1,
                "path": 1,
                "file": 1,
                "output": 1,
                "clock": len(saved_clocks),
            },
        )
        check(
            "v10-synthetic-controller-imports-no-regex-candidate",
            candidate_imports() == before == [],
        )
    finally:
        subprocess.run = saved_run  # type: ignore[assignment]
        subprocess.Popen = saved_popen  # type: ignore[assignment]
        gzip.open = saved_gzip  # type: ignore[assignment]
        Path.open = saved_path_open  # type: ignore[assignment]
        builtins.open = saved_builtin_open  # type: ignore[assignment]
        os.open = saved_os_open  # type: ignore[assignment]
        for name, original in saved_clocks.items():
            setattr(time, name, original)

    return {
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "protocol_version": VERSION,
        "checks": len(checks),
        "check_names": checks,
        "inherited_frozen_v8_controls": inherited["checks"],
        "cases": frozen.CASE_COUNT,
        "categories": frozen.CATEGORY_COUNT,
        "cases_per_category": frozen.CASES_PER_CATEGORY,
        "expected_raw_rows": frozen.EXPECTED_RAW_ROWS,
        "expected_correctness_answers": frozen.EXPECTED_CORRECTNESS_ANSWERS,
        "expected_confidence_intervals": frozen.EXPECTED_CONFIDENCE_INTERVALS,
        "expected_process_native_checks": frozen.EXPECTED_PROCESS_NATIVE_CHECKS,
        "expected_global_candidate_prequalifications": (
            frozen.EXPECTED_GLOBAL_PREQUALIFICATIONS
        ),
        "frozen_v8_failure_status": "FAIL",
        "frozen_v8_failed_reference_answers": 577,
        "candidate_imports": [],
        "worker_processes_started": 0,
        "oracle_processes_started": 0,
        "public_case_files_opened": 0,
        "manifest_files_opened": 0,
        "files_written": 0,
        "historical_results_read": 0,
        "holdout_accessed": False,
        "timing_performed": False,
        "performance": "NOT MEASURED",
        "failed": 0,
    }


def main(argv: list[str] | None = None) -> None:
    """Dispatch synthetic, exclusive-freeze, guarded-worker, and replay modes."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "--qualify-worker":
        hidden = argparse.ArgumentParser(add_help=False)
        hidden.add_argument("--family", choices=("rust", "vm", "zig"), required=True)
        hidden.add_argument("--native-fingerprints", required=True)
        hidden.add_argument("--runner-sha256", required=True)
        parsed_hidden = hidden.parse_args(arguments[1:])
        with v10_context():
            _FROZEN_V8_QUALIFICATION_WORKER(parsed_hidden)
        return

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action")
    subparsers.add_parser("self-test", help="run only in-memory synthetic controls")
    subparsers.add_parser("freeze", help="prospectively freeze the additive V10 plan")
    live = subparsers.add_parser("measure", help="measure a pushed V10 plan only")
    live.add_argument("--exclusive-slot", required=True)
    live.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    live.add_argument("--raw", type=Path, default=RAW_PATH)
    live.add_argument("--output", type=Path, default=SUMMARY_PATH)
    live.add_argument("--cases", type=int, default=frozen.CASE_COUNT)
    live.add_argument("--trials", type=int, default=frozen.TRIALS)
    live.add_argument("--bootstraps", type=int, default=frozen.BOOTSTRAPS)
    live.add_argument("--max-operations", type=int, default=frozen.MAX_OPERATIONS)
    replay = subparsers.add_parser(
        "verify",
        help="independently replay every public row without a candidate",
    )
    replay.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    replay.add_argument("--raw", type=Path, default=RAW_PATH)
    replay.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    replay.add_argument("--output", type=Path, default=INTEGRITY_PATH)
    if arguments and arguments[0] == "--self-test":
        arguments[0] = "self-test"
    elif arguments and arguments[0] == "--freeze":
        arguments[0] = "freeze"
    parsed = parser.parse_args(arguments)
    require(parsed.action is not None, "select --self-test, --freeze, measure, or verify")
    try:
        if parsed.action == "self-test":
            result = self_test()
        elif parsed.action == "freeze":
            result = freeze(parsed)
        elif parsed.action == "verify":
            result = verify(parsed)
        else:
            result = measure(parsed)
    except (
        PublicPracticeError,
        OSError,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
        RecursionError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        print(json.dumps({
            "schema": REPORT_SCHEMA,
            "status": "FAIL",
            "protocol_version": VERSION,
            "holdout_accessed": False,
            "timing_performed": False,
            "performance": "NOT MEASURED",
            "error": str(error),
            "failed": 1,
        }, sort_keys=True, ensure_ascii=True, allow_nan=False))
        raise SystemExit(1) from error
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, allow_nan=False))
