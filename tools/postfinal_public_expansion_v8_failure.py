#!/usr/bin/env python3
"""Preserve the genuinely failed, immutable public V8 expansion experiment.

``--self-test`` is exclusively synthetic and blocks clocks, files, and workers.
Only an explicitly authorized root ``--record`` can create the one exclusive
public failure report. The frozen V8 sources are never changed or executed.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


# Direct ``python -I -B tools/...py`` otherwise places only ``tools/`` on
# sys.path. Establish the exact repository root before a project import.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PINNED_PYTHON = Path(
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
)
SCHEMA = "rebar-postfinal-public-expansion-freeze-failure-v8"
SELF_TEST_SCHEMA = f"{SCHEMA}-self-test"
EVIDENCE_RELATIVE = (
    "performance/postfinal-public-v8/evidence/"
    "postfinal-public-freeze-failure-v8.json"
)
FROZEN_SHA256 = {
    "GOAL.md":
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    "tools/postfinal_public_expansion_v8.py":
        "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97",
    "tools/postfinal_public_practice_v8.py":
        "7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f",
    "performance/postfinal-public-v8/PROTOCOL.md":
        "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095",
    "performance/v7/evidence/rust-calibration-fixture.jsonl.gz":
        "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5",
}
FIXTURE_CASES = 10_312
AFFECTED_CASES = 577
EXPECTED_AFFECTED_APIS = {"escape": 48, "findall": 483, "split": 46}
EXPECTED_AFFECTED_INPUTS = {"text": 577}
FIRST_FAILURE = {
    "id": "cal.unicode.words",
    "api": "findall",
    "category": "unicode",
    "cohort": "calibration",
    "recorded_sha256":
        "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949",
    "legacy_utf8_sha256":
        "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949",
    "frozen_v8_ascii_sha256":
        "af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885",
}
MAX_SOURCE_BYTES = 64 * 1024 * 1024


class FailureEvidenceError(RuntimeError):
    """An immutable-source, public-only, or exclusive-evidence gate failed."""


def require(condition: object, explanation: str) -> None:
    if not condition:
        raise FailureEvidenceError(explanation)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def legacy_fixture_digest(value: Any) -> str:
    """Reproduce the exact frozen tools/perf_v5.py result producer."""
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def frozen_v8_digest(value: Any) -> str:
    """Reproduce the exact incorrect V8 fixture-result comparison."""
    return hashlib.sha256(canonical_json(value)).hexdigest()


def bounded_sha256(path: Path, *, maximum: int = MAX_SOURCE_BYTES) -> str:
    require(isinstance(path, Path), "a frozen source path is invalid")
    require(not path.is_symlink(), "a frozen source cannot be a symlink")
    try:
        information = path.stat()
    except OSError as error:
        raise FailureEvidenceError("a frozen source is absent") from error
    require(path.is_file(), "a frozen source is not a regular file")
    require(0 < information.st_size <= maximum,
            "a frozen source exceeds its bounded size")
    observed = 0
    hasher = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                observed += len(block)
                require(observed <= maximum,
                        "a frozen source changed beyond its bounded size")
                hasher.update(block)
    except OSError as error:
        raise FailureEvidenceError("a frozen source cannot be read") from error
    require(observed == information.st_size,
            "a frozen source changed during verification")
    return hasher.hexdigest()


def pinned_repository_path(relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative),
            "a frozen repository path is invalid")
    requested = Path(relative)
    require(not requested.is_absolute()
            and ".." not in requested.parts
            and str(requested) == relative,
            "a frozen repository path is not canonical")
    candidate = ROOT / requested
    try:
        resolved = candidate.resolve(strict=True)
        inside = resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError) as error:
        raise FailureEvidenceError(
            f"a frozen repository input is absent: {relative}"
        ) from error
    require(inside == requested and not candidate.is_symlink(),
            f"a frozen repository path was replaced: {relative}")
    return candidate


def verify_frozen_inputs() -> dict[str, str]:
    result: dict[str, str] = {}
    for relative, expected in sorted(FROZEN_SHA256.items()):
        actual = bounded_sha256(pinned_repository_path(relative))
        require(actual == expected,
                f"the pushed public V8 source changed: {relative}")
        result[relative] = actual
    return result


def skip_opaque_json(source: str, offset: int) -> int:
    while offset < len(source) and source[offset] in " \t\r\n":
        offset += 1
    require(offset < len(source), "an opaque synthetic value was truncated")
    first = source[offset]
    if first == '"':
        cursor = offset + 1
        while cursor < len(source):
            character = source[cursor]
            if character == "\\":
                cursor += 2
            elif character == '"':
                return cursor + 1
            else:
                cursor += 1
        raise FailureEvidenceError("an opaque synthetic string is incomplete")
    if first in "[{":
        stack = ["]" if first == "[" else "}"]
        cursor = offset + 1
        quoted = False
        while cursor < len(source) and stack:
            character = source[cursor]
            if quoted:
                if character == "\\":
                    cursor += 2
                    continue
                if character == '"':
                    quoted = False
            elif character == '"':
                quoted = True
            elif character in "[{":
                stack.append("]" if character == "[" else "}")
            elif character in "]}":
                require(character == stack.pop(),
                        "opaque synthetic brackets do not match")
            cursor += 1
        require(not stack and not quoted,
                "an opaque synthetic value is incomplete")
        return cursor
    cursor = offset
    while cursor < len(source) and source[cursor] not in ",}] \t\r\n":
        cursor += 1
    require(cursor > offset, "an opaque synthetic scalar is invalid")
    return cursor


class HistorySpy:
    """Detect an attempted JSON decode of the opaque archive-history value."""

    def __init__(self) -> None:
        self.parser = json.JSONDecoder()
        self.history_fields = 0
        self.history_value_decodes = 0
        self.pending_history = False

    def raw_decode(self, text: str, index: int = 0) -> tuple[Any, int]:
        if self.pending_history:
            cursor = index
            while cursor < len(text) and text[cursor] in " \t\r\n":
                cursor += 1
            if cursor >= len(text) or text[cursor] != '"':
                self.history_value_decodes += 1
                raise FailureEvidenceError(
                    "opaque archive history reached JSON deserialization"
                )
        result, end = self.parser.raw_decode(text, index)
        if self.pending_history:
            if not isinstance(result, str) or result not in {
                "schema", "cohort", "position", "case", "expected"
            }:
                self.history_value_decodes += 1
                raise FailureEvidenceError(
                    "an opaque archive-history value was deserialized"
                )
            self.pending_history = False
        if isinstance(result, str) and result == "historical":
            self.history_fields += 1
            self.pending_history = True
        return result, end


def decode_synthetic_public_line(raw: bytes, spy: HistorySpy) -> dict[str, Any]:
    """Synthetic-only reproduction of the frozen public selective decoder."""
    require(isinstance(raw, bytes), "a synthetic public line is not bytes")
    try:
        source = raw.decode("utf-8")
    except UnicodeError as error:
        raise FailureEvidenceError("invalid synthetic public UTF-8") from error

    def trim(position: int) -> int:
        while position < len(source) and source[position] in " \t\r\n":
            position += 1
        return position

    offset = trim(0)
    require(offset < len(source) and source[offset] == "{",
            "a synthetic public row is not an object")
    offset += 1
    result: dict[str, Any] = {}
    seen: set[str] = set()
    approved = {"schema", "cohort", "position", "case", "expected"}
    while True:
        offset = trim(offset)
        require(offset < len(source), "a synthetic public row is truncated")
        if source[offset] == "}":
            offset += 1
            break
        try:
            key, offset = spy.raw_decode(source, offset)
        except (UnicodeError, ValueError) as error:
            raise FailureEvidenceError("invalid synthetic public field") from error
        require(isinstance(key, str)
                and (key in approved or key == "historical")
                and key not in seen,
                "a synthetic public field is missing or repeated")
        seen.add(key)
        offset = trim(offset)
        require(offset < len(source) and source[offset] == ":",
                "a synthetic public separator is missing")
        offset = trim(offset + 1)
        if key == "historical":
            offset = skip_opaque_json(source, offset)
        else:
            try:
                value, offset = spy.raw_decode(source, offset)
            except (UnicodeError, ValueError) as error:
                raise FailureEvidenceError(
                    "a synthetic public value is malformed"
                ) from error
            result[key] = value
        offset = trim(offset)
        require(offset < len(source),
                "a synthetic public field separator is missing")
        if source[offset] == "}":
            offset += 1
            break
        require(source[offset] == ",",
                "a synthetic public field separator is malformed")
        offset += 1
    require(trim(offset) == len(source),
            "a synthetic public row has trailing data")
    require(set(result) == approved,
            "a synthetic public row has incomplete approved fields")
    return result


def load_frozen_public_decoder() -> Any:
    path = pinned_repository_path("tools/postfinal_public_expansion_v8.py")
    require(bounded_sha256(path)
            == FROZEN_SHA256["tools/postfinal_public_expansion_v8.py"],
            "the frozen failed V8 decoder was replaced")
    before = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    specification = importlib.util.spec_from_file_location(
        "rebar_frozen_public_v8_failure_decoder", path
    )
    require(specification is not None and specification.loader is not None,
            "the frozen failed V8 decoder cannot be loaded")
    module = importlib.util.module_from_spec(specification)
    try:
        specification.loader.exec_module(module)
    except Exception as error:
        raise FailureEvidenceError(
            "the frozen failed V8 decoder cannot be authenticated"
        ) from error
    after = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    require(before == after,
            "a candidate entered read-only V8 failure diagnosis")
    require(callable(getattr(module, "decode_public_fixture_line", None)),
            "the frozen V8 selective decoder disappeared")
    require(callable(getattr(module, "source_kind", None)),
            "the frozen V8 public subject-kind decoder disappeared")
    return module


def diagnose_public_fixture() -> dict[str, Any]:
    """Read public cases only; never deserialize archived case history."""
    module = load_frozen_public_decoder()
    fixture = pinned_repository_path(
        "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
    )
    rows = 0
    legacy_matches = 0
    ascii_matches = 0
    non_ascii = 0
    history_fields = 0
    history_decodes = 0
    first_failure: dict[str, Any] | None = None
    api_counts: collections.Counter[str] = collections.Counter()
    input_counts: collections.Counter[str] = collections.Counter()
    before = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    try:
        stream = gzip.open(fixture, "rb")
    except OSError as error:
        raise FailureEvidenceError(
            "the pinned public-only calibration fixture cannot be opened"
        ) from error
    with stream:
        for raw in stream:
            spy = HistorySpy()
            try:
                document = module.decode_public_fixture_line(raw, spy)
            except Exception as error:
                raise FailureEvidenceError(
                    "the frozen public-only selective decoder failed"
                ) from error
            history_fields += spy.history_fields
            history_decodes += spy.history_value_decodes
            require("historical" not in document,
                    "the public decoder exposed archived case history")
            case = document.get("case")
            expected = document.get("expected")
            require(isinstance(case, dict) and isinstance(expected, dict),
                    "a public fixture row omitted its case or reference")
            require(document.get("cohort") == "calibration"
                    and case.get("cohort") == "calibration"
                    and expected.get("cohort") == "calibration",
                    "a non-public row entered frozen failure diagnosis")
            require(case.get("id") == expected.get("id")
                    and case.get("category") == expected.get("category"),
                    "a public case and its reference are inconsistent")
            result = expected.get("result")
            recorded = expected.get("result_sha256")
            legacy = legacy_fixture_digest(result)
            incorrect = frozen_v8_digest(result)
            rows += 1
            require(legacy == recorded,
                    "a public answer does not match its original UTF-8 producer")
            legacy_matches += 1
            ascii_matches += int(incorrect == recorded)
            if legacy != incorrect:
                non_ascii += 1
                api = case.get("api")
                require(isinstance(api, str), "a public case has no operation")
                api_counts[api] += 1
                input_counts[module.source_kind(case)] += 1
                if first_failure is None:
                    first_failure = {
                        "id": case["id"],
                        "api": api,
                        "category": case["category"],
                        "cohort": case["cohort"],
                        "recorded_sha256": recorded,
                        "legacy_utf8_sha256": legacy,
                        "frozen_v8_ascii_sha256": incorrect,
                    }
    require(rows == FIXTURE_CASES, "the pinned public denominator changed")
    require(legacy_matches == FIXTURE_CASES,
            "the original UTF-8 producer did not authenticate every answer")
    require(ascii_matches == FIXTURE_CASES - AFFECTED_CASES,
            "the frozen V8 ASCII mismatch denominator changed")
    require(non_ascii == AFFECTED_CASES,
            "the frozen V8 public Unicode failure count changed")
    require(first_failure == FIRST_FAILURE,
            "the first genuine public V8 failure changed")
    require(dict(sorted(api_counts.items())) == EXPECTED_AFFECTED_APIS,
            "the affected public operation counts changed")
    require(dict(sorted(input_counts.items())) == EXPECTED_AFFECTED_INPUTS,
            "the affected public input counts changed")
    require(history_fields == FIXTURE_CASES and history_decodes == 0,
            "an opaque archived history value was deserialized")
    require(before == {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }, "a candidate entered public V8 failure diagnosis")
    return {
        "public_fixture_cases": rows,
        "legacy_utf8_digest_matches": legacy_matches,
        "frozen_v8_ascii_digest_matches": ascii_matches,
        "failed_reference_answers": non_ascii,
        "first_failure": first_failure,
        "affected_public_api_counts": dict(sorted(api_counts.items())),
        "affected_public_input_counts": dict(sorted(input_counts.items())),
        "opaque_history_fields_skipped": history_fields,
        "opaque_history_values_deserialized": history_decodes,
    }


def evidence_document(fingerprints: dict[str, str],
                      diagnosis: dict[str, Any]) -> dict[str, Any]:
    python = str(PINNED_PYTHON)
    direct = (
        "env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "
        f"{python} -I -B tools/postfinal_public_practice_v8.py --freeze"
    )
    module = (
        "env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "
        f"{python} -I -B -c "
        "'import sys;sys.path.insert(0,\".\");"
        "from tools.postfinal_public_practice_v8 import main;"
        "main([\"freeze\"])'"
    )
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "result": "FAIL",
        "python": "3.14.6",
        "measurement_role": "PUBLIC DEVELOPMENT; not independently secret",
        "frozen_design": {
            "goal_path": "GOAL.md",
            "goal_sha256": fingerprints["GOAL.md"],
            "expander_path": "tools/postfinal_public_expansion_v8.py",
            "expander_sha256": fingerprints[
                "tools/postfinal_public_expansion_v8.py"
            ],
            "runner_path": "tools/postfinal_public_practice_v8.py",
            "runner_sha256": fingerprints[
                "tools/postfinal_public_practice_v8.py"
            ],
            "protocol_path": "performance/postfinal-public-v8/PROTOCOL.md",
            "protocol_sha256": fingerprints[
                "performance/postfinal-public-v8/PROTOCOL.md"
            ],
            "fixture_path":
                "performance/v7/evidence/rust-calibration-fixture.jsonl.gz",
            "fixture_sha256": fingerprints[
                "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
            ],
        },
        "failure": {
            "phase": "pre-candidate public fixture authentication",
            "class": "PublicExpansionError",
            "module": "tools.postfinal_public_expansion_v8",
            "message": "corrupt public reference answer",
            "cause": (
                "The authentic V5 fixture producer hashes Unicode results as "
                "unescaped UTF-8, while the frozen V8 expander incorrectly "
                "hashes those same result values as ASCII-escaped JSON."
            ),
        },
        "reproduction": [
            {
                "mode": "direct isolated frozen practice runner",
                "command": direct,
                "exception_class": "ModuleNotFoundError",
                "exception_module": "builtins",
                "message": "No module named 'tools'",
            },
            {
                "mode": "isolated frozen practice runner with explicit repository root",
                "command": module,
                "exception_class": "PublicExpansionError",
                "exception_module": "tools.postfinal_public_expansion_v8",
                "message": "corrupt public reference answer",
            },
        ],
        "public_fixture_diagnosis": diagnosis,
        "recording_source_path":
            "tools/postfinal_public_expansion_v8_failure.py",
        "recording_source_sha256": bounded_sha256(Path(__file__).resolve()),
        "production_manifest_created": False,
        "production_cases_generated": 0,
        "candidate_imports": 0,
        "candidate_processes": 0,
        "benchmark_or_timing_executed": False,
        "clock_samples": 0,
        "held_out_records_deserialized": 0,
        "performance": "NOT MEASURED",
    }


def exclusive_record(document: dict[str, Any]) -> Path:
    output = ROOT / EVIDENCE_RELATIVE
    expected_root = (ROOT / "performance/postfinal-public-v8").resolve()
    parent = output.parent
    require(parent.parent.resolve() == expected_root,
            "the public failure evidence escaped its exact V8 directory")
    if not parent.exists():
        parent.mkdir(mode=0o755, parents=False, exist_ok=False)
    require(parent.is_dir() and not parent.is_symlink()
            and parent.resolve().parent == expected_root,
            "the public failure evidence directory was replaced")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(output, flags, 0o644)
    except FileExistsError as error:
        raise FailureEvidenceError(
            "the frozen V8 public failure evidence already exists"
        ) from error
    except OSError as error:
        raise FailureEvidenceError(
            "the frozen V8 public failure evidence cannot be created"
        ) from error
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_json(document) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_CLOEXEC", 0)
    directory = os.open(parent, directory_flags)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return output


def record() -> None:
    require(tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and Path(sys.executable).resolve() == PINNED_PYTHON.resolve(),
            "failure recording requires the exact isolated CPython 3.14.6")
    before = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    fingerprints = verify_frozen_inputs()
    diagnosis = diagnose_public_fixture()
    require(verify_frozen_inputs() == fingerprints,
            "a pushed V8 input changed during public failure diagnosis")
    require(before == {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }, "a candidate entered frozen V8 failure recording")
    evidence = evidence_document(fingerprints, diagnosis)
    output = exclusive_record(evidence)
    print(json.dumps({
        "schema": SCHEMA,
        "status": "RECORDED",
        "design_result": "FAIL",
        "evidence": str(output.relative_to(ROOT)),
        "failed_reference_answers": diagnosis["failed_reference_answers"],
        "opaque_history_values_deserialized": 0,
        "candidate_processes": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
    }, sort_keys=True, ensure_ascii=True))


def self_test() -> None:
    checks: list[str] = []
    blocked: collections.Counter[str] = collections.Counter()
    before = {
        name for name in sys.modules
        if name == "candidates" or name.startswith("candidates.")
    }
    real_run = subprocess.run
    real_gzip = gzip.open
    real_path_open = Path.open
    real_path_read = Path.read_bytes
    real_open = os.open
    clock_names = (
        "time", "time_ns", "monotonic", "monotonic_ns",
        "perf_counter", "perf_counter_ns", "process_time", "process_time_ns",
    )
    real_clocks = {name: getattr(time, name) for name in clock_names}

    def reject_action(kind: str) -> Any:
        def forbidden(*_args: Any, **_kwargs: Any) -> Any:
            blocked[kind] += 1
            raise FailureEvidenceError(
                "synthetic failure self-test blocked " + kind
            )

        return forbidden

    subprocess.run = reject_action("worker")  # type: ignore[assignment]
    gzip.open = reject_action("fixture")  # type: ignore[assignment]
    Path.open = reject_action("path")  # type: ignore[assignment]
    Path.read_bytes = reject_action("file")  # type: ignore[assignment]
    os.open = reject_action("output")  # type: ignore[assignment]
    for name in clock_names:
        setattr(time, name, reject_action("clock"))

    def check(name: str, condition: object) -> None:
        require(name not in checks,
                "a synthetic failure control was counted twice")
        require(condition,
                "a synthetic public failure control did not pass: " + name)
        checks.append(name)

    def rejected(name: str, action: Any) -> None:
        try:
            action()
        except FailureEvidenceError:
            check(name, True)
        else:
            raise FailureEvidenceError(
                "synthetic public failure poison was accepted: " + name
            )

    check("isolated-repository-bootstrap-is-explicit",
          sys.path[0] == str(ROOT))
    check("legacy-ascii-and-v8-ascii-agree",
          legacy_fixture_digest({"value": "plain-ascii"})
          == frozen_v8_digest({"value": "plain-ascii"}))
    check("utf8-unicode-and-v8-escaped-ascii-diverge",
          legacy_fixture_digest({"value": "caf\u00e9 \U0001f600"})
          != frozen_v8_digest({"value": "caf\u00e9 \U0001f600"}))
    check("legacy-unicode-digest-is-reproducible",
          legacy_fixture_digest(["caf\u00e9", "\u03a9"])
          == legacy_fixture_digest(["caf\u00e9", "\u03a9"]))
    check("legacy-json-keys-are-sorted",
          legacy_fixture_digest({"b": "\u03a9", "a": "\u00e9"})
          == legacy_fixture_digest({"a": "\u00e9", "b": "\u03a9"}))
    check("ascii-canonical-keys-are-sorted",
          frozen_v8_digest({"b": "\u03a9", "a": "\u00e9"})
          == frozen_v8_digest({"a": "\u00e9", "b": "\u03a9"}))
    check("utf8-codec-produces-real-unescaped-characters",
          json.dumps("caf\u00e9", ensure_ascii=False).encode("utf-8")
          != json.dumps("caf\u00e9", ensure_ascii=True).encode("ascii"))
    check("canonical-output-is-strict-ascii",
          canonical_json({"unicode": "caf\u00e9 \U0001f600"}).isascii())
    check("all-five-frozen-inputs-are-explicit",
          len(FROZEN_SHA256) == 5)
    check("immutable-goal-hash-is-pinned",
          FROZEN_SHA256["GOAL.md"]
          == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62")
    check("frozen-failed-expander-hash-is-pinned",
          FROZEN_SHA256["tools/postfinal_public_expansion_v8.py"]
          == "e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97")
    check("frozen-runner-hash-is-pinned",
          FROZEN_SHA256["tools/postfinal_public_practice_v8.py"]
          == "7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f")
    check("frozen-protocol-hash-is-pinned",
          FROZEN_SHA256["performance/postfinal-public-v8/PROTOCOL.md"]
          == "e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095")
    check("public-only-fixture-hash-is-pinned",
          FROZEN_SHA256[
              "performance/v7/evidence/rust-calibration-fixture.jsonl.gz"
          ] == "c9fb716b609bfd1b007482db251bc8095990ba7f571e5f041db0dbc6abf41bf5")
    check("public-denominator-is-10312", FIXTURE_CASES == 10_312)
    check("actual-mismatch-denominator-is-577", AFFECTED_CASES == 577)
    check("actual-unaffected-denominator-is-9735",
          FIXTURE_CASES - AFFECTED_CASES == 9_735)
    check("first-failure-is-public-unicode",
          FIRST_FAILURE["id"] == "cal.unicode.words"
          and FIRST_FAILURE["cohort"] == "calibration")
    check("first-legacy-result-reproduces-frozen-record",
          FIRST_FAILURE["legacy_utf8_sha256"]
          == FIRST_FAILURE["recorded_sha256"])
    check("first-v8-result-is-falsified",
          FIRST_FAILURE["frozen_v8_ascii_sha256"]
          != FIRST_FAILURE["recorded_sha256"])
    check("first-legacy-digest-is-pinned",
          FIRST_FAILURE["legacy_utf8_sha256"]
          == "21f3db7cbb6c5d5bb6fcaf4dc6847779d647399a97f9e62a62861733a4fa1949")
    check("first-v8-digest-is-pinned",
          FIRST_FAILURE["frozen_v8_ascii_sha256"]
          == "af46c189444aa11a5f11a6894aaac409e79913384e82e6ea96e6668468f10885")
    check("all-affected-operation-counts-sum-exactly",
          sum(EXPECTED_AFFECTED_APIS.values()) == AFFECTED_CASES)
    check("all-affected-input-counts-sum-exactly",
          sum(EXPECTED_AFFECTED_INPUTS.values()) == AFFECTED_CASES)
    check("actual-findall-failure-count-is-pinned",
          EXPECTED_AFFECTED_APIS["findall"] == 483)
    check("actual-escape-failure-count-is-pinned",
          EXPECTED_AFFECTED_APIS["escape"] == 48)
    check("actual-split-failure-count-is-pinned",
          EXPECTED_AFFECTED_APIS["split"] == 46)

    synthetic = {
        "case": {
            "id": "cal.synthetic.unicode",
            "cohort": "calibration",
            "category": "synthetic-public-unicode",
            "api": "findall",
        },
        "cohort": "calibration",
        "expected": {
            "id": "cal.synthetic.unicode",
            "cohort": "calibration",
            "category": "synthetic-public-unicode",
            "result": ["caf\u00e9", "\u03a9"],
            "result_sha256": legacy_fixture_digest(["caf\u00e9", "\u03a9"]),
        },
        "historical": {
            "poison": [
                {"nested": "must never be decoded"},
                {"quotes": "brace \\\" { } [ ]"},
            ],
        },
        "position": 0,
        "schema": "rebar-rust-sealed-calibration-fixture-v7",
    }
    encoded = canonical_json(synthetic) + b"\n"
    spy = HistorySpy()
    decoded = decode_synthetic_public_line(encoded, spy)
    check("synthetic-selective-decoder-preserves-only-public-fields",
          set(decoded)
          == {"case", "cohort", "expected", "position", "schema"})
    check("synthetic-opaque-history-is-not-returned",
          "historical" not in decoded)
    check("synthetic-opaque-history-key-is-observed",
          spy.history_fields == 1)
    check("synthetic-opaque-history-value-is-never-decoded",
          spy.history_value_decodes == 0)
    check("synthetic-public-unicode-result-is-authentic",
          legacy_fixture_digest(decoded["expected"]["result"])
          == decoded["expected"]["result_sha256"])
    check("synthetic-v8-unicode-codec-is-falsified",
          frozen_v8_digest(decoded["expected"]["result"])
          != decoded["expected"]["result_sha256"])

    rejected("synthetic-worker-creation-is-blocked",
             lambda: subprocess.run(["not-a-real-worker"]))
    rejected("synthetic-real-fixture-opening-is-blocked",
             lambda: gzip.open("not-a-real-fixture", "rb"))
    rejected("synthetic-path-opening-is-blocked",
             lambda: Path("not-a-real-path").open("rb"))
    rejected("synthetic-file-read-is-blocked",
             lambda: Path("not-a-real-file").read_bytes())
    rejected("synthetic-output-creation-is-blocked",
             lambda: os.open("not-a-real-output", os.O_CREAT))
    for name in clock_names:
        rejected("synthetic-" + name + "-clock-is-blocked",
                 lambda clock=name: getattr(time, clock)())
    check("all-clock-file-and-worker-guards-were-exercised",
          dict(blocked)
          == {"worker": 1, "fixture": 1, "path": 1, "file": 1,
              "output": 1, "clock": len(clock_names)})
    check("no-candidate-was-imported",
          before == {
              name for name in sys.modules
              if name == "candidates" or name.startswith("candidates.")
          })
    subprocess.run = real_run  # type: ignore[assignment]
    gzip.open = real_gzip  # type: ignore[assignment]
    Path.open = real_path_open  # type: ignore[assignment]
    Path.read_bytes = real_path_read  # type: ignore[assignment]
    os.open = real_open  # type: ignore[assignment]
    for name, clock in real_clocks.items():
        setattr(time, name, clock)
    print(json.dumps({
        "schema": SELF_TEST_SCHEMA,
        "status": "PASS",
        "synthetic_controls": len(checks),
        "checks": checks,
        "actual_public_fixture_rows_read": 0,
        "actual_archived_history_values_deserialized": 0,
        "candidate_imports": [],
        "candidate_processes": 0,
        "clock_samples": 0,
        "files_read": 0,
        "files_written": 0,
        "evidence_recorded": False,
        "performance": "NOT MEASURED",
    }, ensure_ascii=True, sort_keys=True))


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument("--self-test", action="store_true",
                         help="run in-memory, side-effect-free poison controls")
    choices.add_argument("--record", action="store_true",
                         help="exclusively record the actual frozen V8 failure")
    values = parser.parse_args(arguments)
    if values.self_test:
        self_test()
    else:
        record()


if __name__ == "__main__":
    try:
        main()
    except FailureEvidenceError as error:
        print(json.dumps({
            "schema": SCHEMA,
            "status": "FAIL",
            "error": str(error),
            "performance": "NOT MEASURED",
        }, ensure_ascii=True, sort_keys=True), file=sys.stderr)
        raise SystemExit(1) from error
