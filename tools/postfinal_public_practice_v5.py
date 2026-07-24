#!/usr/bin/env python3
"""Run immutable public-practice V4 with surrogate-safe private worker framing.

This additive V5 protocol preserves the 8,192 frozen public cases, four
independently guarded engines, full correctness proofs, and paired measurement
rules. Its only worker change is ASCII-escaped JSON, allowing valid Python
regular expressions containing lone Unicode surrogates to cross a UTF-8 pipe.
The failed V4 manifest and partial observations are fingerprinted, never reused.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools import postfinal_public_practice_v4 as frozen_v4


ROOT = frozen_v4.ROOT
FROZEN_V4_VERSION = "postfinal-public-practice-v4"
FROZEN_V4_RUNNER_PATH = ROOT / "tools" / "postfinal_public_practice_v4.py"
FROZEN_V4_RUNNER_SHA256 = (
    "69d42bf668b60145520ac54873966ccf52c42d624bab809e484e239229256600"
)
FROZEN_V4_MANIFEST_PATH = (
    ROOT / "performance" / "postfinal-public-v4" / "manifest.json"
)
FROZEN_V4_MANIFEST_SHA256 = (
    "15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55"
)
FROZEN_V4_PARTIAL_RAW_PATH = (
    ROOT
    / "performance"
    / "postfinal-public-v4"
    / "evidence"
    / "postfinal-public-practice-v4-raw.jsonl.gz"
)
FROZEN_V4_PARTIAL_RAW_SHA256 = (
    "4132e485b605f924fbc4edf09324987f09361f0562a9884fd0ceb06e09544f8a"
)
V5_SOURCE_PATH = Path(__file__).resolve()

VERSION = "postfinal-public-practice-v5"
VERSION_ROOT = ROOT / "performance" / "postfinal-public-v5"
EVIDENCE_ROOT = VERSION_ROOT / "evidence"
MANIFEST_PATH = VERSION_ROOT / "manifest.json"
RAW_PATH = EVIDENCE_ROOT / f"{VERSION}-raw.jsonl.gz"
SUMMARY_PATH = EVIDENCE_ROOT / f"{VERSION}-summary.json"
INTEGRITY_PATH = EVIDENCE_ROOT / f"{VERSION}-integrity.json"
POSTFINAL_PLAN_SCHEMA = "rebar-postfinal-public-practice-plan-v5"
POSTFINAL_REPORT_SCHEMA = "rebar-postfinal-public-practice-report-v5"
POSTFINAL_INTEGRITY_SCHEMA = "rebar-postfinal-public-practice-integrity-v5"
EXCLUSIVE_SLOT = VERSION
PRIVATE_WORKER_WIRE_FORMAT = "canonical-ascii-json-utf8"


def require_immutable_v4_source() -> None:
    """Reject a substituted predecessor without inspecting any evidence."""

    frozen_v4.require_candidate_free()
    frozen_v4.require(
        FROZEN_V4_RUNNER_PATH.resolve()
        == (ROOT / "tools" / "postfinal_public_practice_v4.py").resolve(),
        "the immutable public V4 runner escaped its exact owned source path",
    )
    frozen_v4.require(
        frozen_v4.pilot.file_sha256(FROZEN_V4_RUNNER_PATH)
        == FROZEN_V4_RUNNER_SHA256,
        "the immutable public V4 runner was changed or substituted",
    )


frozen_v4.require(
    frozen_v4.VERSION == FROZEN_V4_VERSION,
    "the immutable public V4 predecessor changed its protocol version",
)
frozen_v4.require(
    Path(frozen_v4.__file__).resolve() == FROZEN_V4_RUNNER_PATH.resolve(),
    "the immutable public V4 predecessor was imported from a foreign source",
)
require_immutable_v4_source()

_FROZEN_V4_MAKE_MANIFEST = frozen_v4.make_manifest
_FROZEN_V4_SELF_TEST = frozen_v4.synthetic_self_test
_FROZEN_V4_WORKER = frozen_v4.PersistentGuardedWorker


def encode_private_worker_request(document: dict[str, Any]) -> str:
    """Encode one canonical, newline-safe, lossless UTF-8 worker request."""

    return json.dumps(
        document,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class PersistentGuardedWorker(_FROZEN_V4_WORKER):
    """Retain every frozen worker guard while safely framing Unicode."""

    def request(self, document: dict[str, Any]) -> dict[str, Any]:
        frozen_v4.require(
            self.process.poll() is None,
            f"the independently guarded {self.module} worker stopped",
        )
        frozen_v4.require(
            self.process.stdin is not None and self.process.stdout is not None,
            f"the independently guarded {self.module} worker lost its protocol",
        )
        try:
            request = encode_private_worker_request(document)
            self.process.stdin.write(request + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, TypeError, ValueError) as error:
            raise RuntimeError(
                f"the independently guarded {self.module} worker rejected a request"
            ) from error
        for response_index in range(2):
            try:
                encoded = self.process.stdout.readline(
                    frozen_v4.MAX_WORKER_RESPONSE_BYTES + 1
                )
            except OSError as error:
                raise RuntimeError(
                    f"the independently guarded {self.module} worker response failed"
                ) from error
            frozen_v4.require(
                bool(encoded)
                and len(encoded) <= frozen_v4.MAX_WORKER_RESPONSE_BYTES
                and encoded.endswith("\n"),
                "the independently guarded "
                f"{self.module} worker returned an invalid response",
            )
            try:
                response = json.loads(encoded)
            except (UnicodeError, json.JSONDecodeError) as error:
                raise RuntimeError(
                    "the independently guarded "
                    f"{self.module} worker returned invalid JSON"
                ) from error
            frozen_v4.require(
                isinstance(response, dict),
                "the independently guarded "
                f"{self.module} worker changed its protocol",
            )
            if (
                response_index == 0
                and response.get("op") in {"ready", "startup"}
                and document.get("op") not in {"ready", "startup"}
            ):
                frozen_v4.require(
                    response.get("passed") is True,
                    f"the independently guarded {self.module} worker failed startup",
                )
                continue
            frozen_v4.require(
                response.get("passed") is True
                and response.get("op") == document.get("op"),
                "the independently guarded "
                f"{self.module} worker rejected {document.get('op')!r}",
            )
            return response
        raise RuntimeError(
            f"the independently guarded {self.module} worker omitted its response"
        )


def verified_failed_v4_provenance() -> dict[str, Any]:
    """Fingerprint V4 evidence bytes without loading cases or observations."""

    require_immutable_v4_source()
    expected_manifest = (
        ROOT / "performance" / "postfinal-public-v4" / "manifest.json"
    ).resolve()
    expected_raw = (
        ROOT
        / "performance"
        / "postfinal-public-v4"
        / "evidence"
        / "postfinal-public-practice-v4-raw.jsonl.gz"
    ).resolve()
    frozen_v4.require(
        FROZEN_V4_MANIFEST_PATH.resolve() == expected_manifest
        and FROZEN_V4_MANIFEST_PATH.is_file()
        and frozen_v4.pilot.file_sha256(FROZEN_V4_MANIFEST_PATH)
        == FROZEN_V4_MANIFEST_SHA256,
        "the failed public V4 manifest is missing, changed, or substituted",
    )
    frozen_v4.require(
        FROZEN_V4_PARTIAL_RAW_PATH.resolve() == expected_raw
        and FROZEN_V4_PARTIAL_RAW_PATH.is_file()
        and frozen_v4.pilot.file_sha256(FROZEN_V4_PARTIAL_RAW_PATH)
        == FROZEN_V4_PARTIAL_RAW_SHA256,
        "the failed public V4 partial observations were changed or substituted",
    )
    return {
        "source_public_v4_runner_path": "tools/postfinal_public_practice_v4.py",
        "source_public_v4_runner_sha256": FROZEN_V4_RUNNER_SHA256,
        "source_public_v4_manifest_path": (
            "performance/postfinal-public-v4/manifest.json"
        ),
        "source_public_v4_manifest_sha256": FROZEN_V4_MANIFEST_SHA256,
        "source_public_v4_partial_raw_path": (
            "performance/postfinal-public-v4/evidence/"
            "postfinal-public-practice-v4-raw.jsonl.gz"
        ),
        "source_public_v4_partial_raw_sha256": FROZEN_V4_PARTIAL_RAW_SHA256,
        "private_worker_wire_format": PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
    }


def make_manifest(edge_paths: list[Path]) -> tuple[Any, list[Any], dict[str, Any]]:
    """Preserve frozen public selection and bind the failed V4 predecessor."""

    provenance = verified_failed_v4_provenance()
    suite, entries, document = _FROZEN_V4_MAKE_MANIFEST(edge_paths)
    frozen_v4.require(
        document.get("protocol_version") == VERSION
        and document.get("postfinal_schema") == POSTFINAL_PLAN_SCHEMA
        and document.get("exclusive_slot") == EXCLUSIVE_SLOT
        and document.get("runner_sha256")
        == frozen_v4.pilot.file_sha256(V5_SOURCE_PATH),
        "the additive V5 public manifest changed its exact source or protocol",
    )
    for field, value in provenance.items():
        frozen_v4.require(
            field not in document,
            f"the additive V5 predecessor provenance collides with {field}",
        )
        document[field] = value
    return suite, entries, document


def synthetic_self_test() -> dict[str, Any]:
    """Prove surrogate-safe framing without a worker, timing, or evidence."""

    require_immutable_v4_source()
    inherited = _FROZEN_V4_SELF_TEST()
    frozen_v4.require(
        inherited.get("result") == "PASS"
        and inherited.get("protocol_version") == VERSION
        and inherited.get("schema") == POSTFINAL_INTEGRITY_SCHEMA + "-self-test"
        and inherited.get("candidate_imported") is False
        and inherited.get("holdout_accessed") is False
        and inherited.get("held_out_cases_generated") == 0
        and inherited.get("held_out_records_deserialized") == 0
        and inherited.get("timing_performed") is False
        and inherited.get("failed") == 0,
        "the inherited candidate-free expanded public controls failed",
    )
    frozen_v4.require(
        inherited.get("prospective_cases") == 8_192
        and inherited.get("synthetic_public_operations") == 12
        and inherited.get("prospective_stage05_correctness_artifact_count") == 12
        and inherited.get("prospective_stage05_fresh_edge_proof_count") == 3
        and inherited.get("prospective_universal_oracle_proof_field_count") == 23
        and inherited.get("prospective_stage05_deep_family_mapping")
        == {"rust": "RUST", "vm": "C", "zig": "ZIG"}
        and inherited.get("owned_source_poisoned_control_count") == 4
        and inherited.get("postfinal_poisoned_control_count") == 10,
        "an additive V5 correctness artifact or inherited poison control changed",
    )

    wire_controls: list[dict[str, Any]] = []
    examples = (
        ("lone-high-surrogate", "\ud800"),
        ("lone-low-surrogate", "\udfff"),
        ("separated-lone-surrogates", "\ud800x\udfff"),
        ("emoji", "\U0001f600"),
        ("astral-code-point", "\U00010348"),
        ("combining-text", "e\u0301"),
        ("escaped-newline", "left\nright"),
    )
    for name, value in examples:
        document = {
            "op": "prepare",
            "case": {"pattern": value, "string": value},
            "expected": {"value": value},
        }
        encoded = encode_private_worker_request(document)
        frozen_v4.require(
            encoded.isascii()
            and "\n" not in encoded
            and json.loads(encoded) == document
            and encode_private_worker_request(json.loads(encoded)) == encoded,
            f"the additive V5 private wire failed {name}",
        )
        wire_controls.append({"name": name, "passed": True})

    circular: dict[str, Any] = {}
    circular["self"] = circular
    rejected = (
        ("nan", {"op": "prepare", "value": float("nan")}),
        ("positive-infinity", {"op": "prepare", "value": float("inf")}),
        ("negative-infinity", {"op": "prepare", "value": float("-inf")}),
        ("unserializable-object", {"op": "prepare", "value": object()}),
        ("unserializable-bytes", {"op": "prepare", "value": b"private"}),
        ("circular-document", circular),
    )
    for name, document in rejected:
        try:
            encode_private_worker_request(document)
        except (TypeError, ValueError, OverflowError, RecursionError):
            wire_controls.append({"name": name, "passed": True})
            continue
        raise RuntimeError(f"the additive V5 private wire accepted {name}")

    frozen_v4.require_candidate_free()
    return {
        **inherited,
        "source_public_v4_runner_path": "tools/postfinal_public_practice_v4.py",
        "source_public_v4_runner_sha256": FROZEN_V4_RUNNER_SHA256,
        "source_public_v4_manifest_sha256": FROZEN_V4_MANIFEST_SHA256,
        "source_public_v4_partial_raw_sha256": FROZEN_V4_PARTIAL_RAW_SHA256,
        "failed_v4_evidence_accessed": False,
        "private_worker_wire_format": PRIVATE_WORKER_WIRE_FORMAT,
        "private_worker_wire_ensure_ascii": True,
        "private_worker_wire_control_count": len(wire_controls),
        "private_worker_wire_controls": wire_controls,
        "worker_processes_started": 0,
        "failed": 0,
    }


for name, value in {
    "__file__": str(V5_SOURCE_PATH),
    "VERSION": VERSION,
    "VERSION_ROOT": VERSION_ROOT,
    "EVIDENCE_ROOT": EVIDENCE_ROOT,
    "MANIFEST_PATH": MANIFEST_PATH,
    "RAW_PATH": RAW_PATH,
    "SUMMARY_PATH": SUMMARY_PATH,
    "INTEGRITY_PATH": INTEGRITY_PATH,
    "POSTFINAL_PLAN_SCHEMA": POSTFINAL_PLAN_SCHEMA,
    "POSTFINAL_REPORT_SCHEMA": POSTFINAL_REPORT_SCHEMA,
    "POSTFINAL_INTEGRITY_SCHEMA": POSTFINAL_INTEGRITY_SCHEMA,
    "EXCLUSIVE_SLOT": EXCLUSIVE_SLOT,
    "PersistentGuardedWorker": PersistentGuardedWorker,
    "make_manifest": make_manifest,
    "synthetic_self_test": synthetic_self_test,
}.items():
    setattr(frozen_v4, name, value)


def __getattr__(name: str) -> Any:
    """Expose the unchanged audited V4 protocol and candidate contracts."""

    return getattr(frozen_v4, name)


def main() -> None:
    """Use the original fail-closed CLI with additive V5 paths and framing."""

    frozen_v4.main()


if __name__ == "__main__":
    main()
