#!/usr/bin/env python3
"""Freeze an actual-build-capable, first-party Rust semantic source build."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("a first-party Rust native source freeze imported a matcher")

import builtins
import hashlib
import os
import stat
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SCHEMA = "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22"
VERSION = 22
FAMILY = "rust"
SOURCE_PATH = "tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py"
PROTOCOL_PATH = "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md"
CONTRACT_PATH = "oracle/phase2/rust-capture-shape-semantics-source-build-v22.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
BUILD_LABEL = "phase2-v22-rust-capture-shape-root-provenance"
MAX_OWNER_BYTES = 4 * 1024 * 1024
DERIVED_SHA256 = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
DERIVED_BYTES = 179147
CAPTURE_SHA256 = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
CAPTURE_BYTES = 179520
ADAPTER_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
V21 = {
    "source": ("previous_v21_source", "tools/reproduce_owned_rust_captured_findall_source_build_v21.py", "bc5f5b4efd8b20a564692e14f972c77267c58ac44a560b432a0a1cc38e794c58", 100150, 2064, 430883),
    "protocol": ("previous_v21_protocol", "oracle/phase2/RUST-CAPTURED-FINDALL-SOURCE-BUILD-V21.md", "d7c137d2432c2f28f4b6b26fdde3a591b92f7d62e6018d047cfa0b3ccfe0a8c4", 4943, 2064, 524834),
    "contract": ("previous_v21_contract", "oracle/phase2/rust-captured-findall-source-build-v21.json", "61e14e1d47f55759a73721635594b69ba098541bc83c9046c99c0c282223fd4a", 18420, 2064, 524837),
    "build_receipt": ("actual_v21_build_receipt", "oracle/phase2/evidence/native-source-build-v21-rust-phase2-v21-rust-captured-findall-root-provenance-publication-receipt.json", "bc3ebdc835ef6a89d351c4541863274d410e2685d35eacdc9668f4bf3a474102", 3502, 2064, 524894),
    "root_receipt": ("actual_v21_root_receipt", "oracle/phase2/evidence/native-source-build-v21-rust-phase2-v21-rust-captured-findall-root-provenance-root-provenance-receipt.json", "73cee9c0a4f44d113da96b505eb0e9224577584b75c347e6fd351995d1d09a4e", 6306, 2064, 524895),
}
SEMANTIC = {
    "source": ("semantic_v1_source", "tools/apply_owned_rust_capture_shape_semantics_v1.py", "d3213d43bd09b1216f618a3a14472ff0fe290b13852c403a0d1c0ecd8a0408b2", 53555, 2064, 431487),
    "protocol": ("semantic_v1_protocol", "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md", "edbeb811483b39f094dbead1237e912e20af07609474c7256db75fce45887f54", 4883, 2064, 525377),
    "contract": ("semantic_v1_contract", "oracle/phase2/rust-capture-shape-semantics-v1.json", "5e262226341a7554943a7ae21fad616009555231e855ea23b7eb715c94317b63", 6524, 2064, 525378),
}
LATEST_FAILURE = (
    "actual_v20_rust_original_campaign_failure",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v21-rust-captured-findall-root-provenance-original-p0-v20-failures-publication-receipt.json",
    "ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36",
    45973, 2064, 524829,
)
LATEST_SUITES = (
    ("original_bounded_v5", 151, True, 0, 151, "PASS", 81, 0),
    ("public_v3", 864, True, 0, 864, "PASS", 83, 0),
    ("scanner_v3", 1024, True, 0, 1024, "PASS", 84, 0),
    ("buffer_v3", 768, True, 0, 768, "PASS", 85, 0),
    ("managed_v1", 1024, True, 0, 1024, "PASS", 86, 0),
    ("scanner_verbose_v1", 2854, True, 0, 2854, "PASS", 87, 0),
    ("public_types_v1", 6912, True, 0, 6912, "PASS", 88, 0),
    ("substitution_v2", 5120, True, 240, 0, "SEMANTIC MISMATCH", 89, 1),
    ("shape_v2", 10240, True, 1056, 0, "SEMANTIC MISMATCH", 90, 1),
    ("public_surface_v19", 1376, True, 0, 1376, "PASS", 91, 0),
    ("subinterpreter_v2", 128, False, "NOT MEASURED", 0, "INFRASTRUCTURE FAILURE", 188, 2),
    ("pep688_v4", 264, True, 0, 264, "PASS", 189, 0),
    ("threaded_pattern_v1", 512, True, 0, 512, "PASS", 190, 0),
)
ROOT_CAPTURE: dict[str, object] | None = None
ENTROPY_BLOCKED = 0


class GateError(Exception):
    """The exact independently owned first-party native build was falsified."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise GateError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete source bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value), "an independently pinned SHA-256 is required: " + label)
    return value


def source_entropy_wall(event: str, arguments: tuple[object, ...]) -> None:
    global ENTROPY_BLOCKED
    if event in ("os.urandom", "os.getrandom") or event.startswith("random."):
        ENTROPY_BLOCKED += 1
        raise GateError("source-only gate rejected entropy: " + event)


def verify_runtime() -> None:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.executable == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "regex" not in sys.modules
        and not any(name == "candidates" or name.startswith("candidates.") for name in sys.modules),
        "require exact isolated CPython 3.14.6 with -I -B -S and no matcher",
    )


def bootstrap_source(row: tuple[object, ...], namespace_name: str) -> dict[str, object]:
    _label, relative, expected, size, device, inode = row
    require(type(relative) is str and type(expected) is str and type(size) is int, "malformed trusted first-party source owner")
    checked_hash(expected, relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600 and before.st_uid == os.geteuid() and before.st_nlink == 1 and (before.st_dev, before.st_ino, before.st_size) == (device, inode, size) and 0 < size <= MAX_OWNER_BYTES, "trusted first-party bootstrap owner was exchanged")
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            require(type(chunk) is bytes and bool(chunk), "trusted bootstrap owner was truncated")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "trusted bootstrap owner grew")
        after = os.fstat(descriptor)
        require(all(getattr(before, field) == getattr(after, field) for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_nlink")), "trusted bootstrap owner changed during its sole read")
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    require(digest(raw) == expected, "trusted first-party bootstrap SHA-256 changed")
    namespace: dict[str, object] = {"__name__": namespace_name, "__file__": ROOT + "/" + relative, "__package__": None}
    exec(compile(raw, ROOT + "/" + relative, "exec", dont_inherit=True), namespace)
    require("re" not in sys.modules and "_sre" not in sys.modules and "regex" not in sys.modules, "trusted source bootstrap loaded a matching engine")
    return namespace


def bootstrap_controllers() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    semantic = bootstrap_source(SEMANTIC["source"], "_rebar_v22_exact_frozen_first_party_semantic_v1")
    require(semantic.get("SCHEMA") == "rebar-owned-rust-capture-shape-semantics-v1-source-freeze" and semantic.get("DERIVED_BRIDGE_SHA256") == DERIVED_SHA256 and semantic.get("DERIVED_BRIDGE_BYTES") == DERIVED_BYTES and semantic.get("SOURCE") == SEMANTIC["source"][1] and semantic.get("PROTOCOL") == SEMANTIC["protocol"][1] and semantic.get("CONTRACT") == SEMANTIC["contract"][1], "load only the independently frozen exact first-party semantic correction")
    previous = bootstrap_source(V21["source"], "_rebar_v22_exact_frozen_first_party_captured_build_v21")
    require(previous.get("SCHEMA") == "rebar-phase2-owned-rust-captured-findall-source-build-v21" and previous.get("VERSION") == 21 and previous.get("FAMILY") == FAMILY and previous.get("PYTHON") == PYTHON and previous.get("CAPTURE_VARIANT")[2] == CAPTURE_SHA256 and previous.get("CAPTURE_VARIANT")[3] == CAPTURE_BYTES and previous.get("PHASES") == PHASES and previous.get("PROCESS_NAMES") == PROCESS_NAMES, "load only the complete pushed first-party captured-build controller")
    parent = previous["bootstrap_v20"]()
    ancestor, base = previous["load_base"](parent)
    require(type(parent) is dict and type(ancestor) is dict and type(base) is dict and base.get("FAMILY") == FAMILY and tuple(base.get("RUST_SOURCE_NAMES", ())) and len(base["RUST_SOURCE_NAMES"]) == 9 and base.get("CORRECTED_ADAPTER_SHA256") == ADAPTER_SHA256 and base.get("CORRECTED_ADAPTER_BYTES") == ADAPTER_BYTES, "retain all nine independently owned zero-dependency Rust sources and native kernel")
    additions = {ROOT + "/" + SOURCE_PATH, ROOT + "/" + PROTOCOL_PATH, ROOT + "/" + CONTRACT_PATH, ROOT + "/" + LATEST_FAILURE[1]}
    additions.update(ROOT + "/" + owner[1] for owner in V21.values())
    additions.update(ROOT + "/" + owner[1] for owner in SEMANTIC.values())
    additions.update(semantic["ALLOWED_PATHS"])
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | additions)
    return semantic, previous, parent, ancestor, base


def canonical(base: dict[str, object], value: object) -> bytes:
    return (base["canonical"](value) + "\n").encode("ascii")


def decode_owner(base: dict[str, object], row: tuple[object, ...], label: str) -> dict[str, object]:
    raw = base["read_exact"](row)
    document = base["StrictJSON"](raw).decode()
    require(type(document) is dict and canonical(base, document) == raw, "reject duplicate, truncated, or noncanonical evidence: " + label)
    return document


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"name": row[0], "path": row[1], "sha256": row[2], "bytes": row[3], "device": row[4], "inode": row[5], "mode": "0600", "nlink": 1}


def validate_actual_v21(build: object, root: object) -> dict[str, object]:
    require(type(build) is dict and type(root) is dict, "both actual V21 publication receipts are mandatory")
    for field, expected in (
        ("schema", "rebar-phase2-owned-rust-captured-findall-source-build-v21-durable-publication-receipt"),
        ("status", "PASS"), ("build_status", "PASS"), ("family", FAMILY),
        ("label", "phase2-v21-rust-captured-findall-root-provenance"),
        ("source_sha256", V21["source"][2]), ("protocol_sha256", V21["protocol"][2]),
        ("contract_sha256", V21["contract"][2]), ("actual_compiler_process_count", 28),
        ("expected_actual_compiler_process_count", 28), ("combined_bridge_sha256", CAPTURE_SHA256),
        ("combined_bridge_bytes", CAPTURE_BYTES), ("combined_bridge_overlay_apply_count", 2),
        ("corrected_public_adapter_sha256", ADAPTER_SHA256),
        ("corrected_public_adapter_bytes", ADAPTER_BYTES),
        ("corrected_public_adapter_overlay_apply_count", 2),
        ("candidate_matching", "NOT RUN"), ("candidate_qualified", False),
        ("holdout", "NOT OPENED"), ("performance", "NOT MEASURED"),
    ):
        require(build.get(field) == expected, "the genuine 28-process V21 build receipt changed: " + field)
    for field, expected in (
        ("schema", "rebar-phase2-owned-rust-captured-findall-source-build-v21-durable-root-provenance-receipt"),
        ("status", "PASS"), ("version", 21), ("family", FAMILY),
        ("label", "phase2-v21-rust-captured-findall-root-provenance"),
        ("source_sha256", V21["source"][2]), ("protocol_sha256", V21["protocol"][2]),
        ("contract_sha256", V21["contract"][2]), ("canonical_build_status", "PASS"),
        ("canonical_build_receipt_relative", V21["build_receipt"][1]),
        ("canonical_build_receipt_sha256", V21["build_receipt"][2]),
        ("canonical_build_receipt_bytes", V21["build_receipt"][3]),
        ("cumulative_captured_bridge_sha256", CAPTURE_SHA256),
        ("cumulative_captured_bridge_bytes", CAPTURE_BYTES),
        ("actual_compiler_process_count", 28), ("expected_compiler_process_count", 28),
        ("actual_source_phase_count", 2), ("bridge_overlay_apply_count", 2),
        ("adapter_overlay_apply_count", 2), ("candidate_correctness", "NOT MEASURED"),
        ("candidate_matching", "NOT RUN"), ("candidate_qualified", False),
        ("historical_archives_opened", 0), ("hidden_cases_read", 0),
        ("clock_samples", 0), ("holdout", "NOT OPENED"),
        ("performance", "NOT MEASURED"), ("winner_selected", False),
    ):
        require(root.get(field) == expected, "the genuine V21 root receipt changed: " + field)
    captured = root.get("root")
    require(type(captured) is dict and captured.get("mode") == "0700" and captured.get("uid") == os.geteuid() and captured.get("phase_count") == 2 and captured.get("directory_scanned") is False and captured.get("nofollow_directory_descriptor") is True and captured.get("descriptor_opened_during_live_verification") is True, "the previous genuine source root was not attested inside its live callback")
    phases = captured.get("phases")
    require(type(phases) is list and len(phases) == 2, "two actual historical private phases must be receipt-attested")
    identities: set[tuple[int, int]] = set()
    per_role: dict[str, str] = {}
    for index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("name") == PHASES[index] and phase.get("mode") == "0700" and phase.get("uid") == os.geteuid(), "a genuine historical V21 phase was omitted or reordered")
        outputs = phase.get("native_outputs")
        require(type(outputs) is list and len(outputs) == 2, "a genuine historical engine or bridge was omitted")
        for position, expected_role in enumerate(("engine", "bridge")):
            item = outputs[position]
            require(type(item) is dict and item.get("role") == expected_role and item.get("native_loaded") is False and item.get("nlink") == 1 and item.get("uid") == os.geteuid() and item.get("hash_provenance") == "COMPLETE ORIGINAL FIRST-PARTY ELF VERIFICATION", "a genuine historical native source artifact was forged")
            checked_hash(item.get("sha256"), "historical " + expected_role + " ELF")
            identity = (item.get("device"), item.get("inode"))
            require(all(type(value) is int for value in identity) and identity not in identities, "a historical native artifact inode was borrowed")
            identities.add(identity)
            if expected_role in per_role:
                require(per_role[expected_role] == item["sha256"], "the actually reproducible V21 source-build output differs across phases")
            else:
                per_role[expected_role] = item["sha256"]
    require(len(identities) == 4 and len(per_role) == 2, "all four independently owned V21 outputs are mandatory")
    return {"status": "PASS", "actual_compiler_process_count": 28, "actual_phase_count": 2, "actual_distinct_native_output_count": 4, "build_receipt_sha256": V21["build_receipt"][2], "root_receipt_sha256": V21["root_receipt"][2], "private_root_opened": False, "archive_opened": False, "native_loaded": False}


def validate_latest_failure(value: object) -> dict[str, object]:
    require(type(value) is dict, "the latest genuinely completed Rust campaign is mandatory")
    for key, expected in (
        ("schema", "rebar-owned-repaired-rust-original-campaign-v20-durable-publication-receipt"),
        ("status", "PASS"), ("publication_status", "PASS"),
        ("candidate_status", "FAIL"), ("candidate_qualified", False),
        ("case_execution_denominator", 31237), ("suite_count", 13),
        ("attempted_suite_count", 13), ("started_suite_count", 13),
        ("completed_suite_count", 12), ("actual_candidate_workers", 13),
        ("distinct_worker_process_id_count", 13), ("verified_passing_case_count", 15749),
        ("semantic_mismatch_count", "NOT MEASURED"),
        ("infrastructure_failure_count", 1), ("named_private_waiver_count", 13),
        ("combined_bridge_source_sha256", CAPTURE_SHA256),
        ("corrected_public_adapter_sha256", ADAPTER_SHA256),
        ("all_original_observation_vectors_complete", False),
        ("all_four_original_targets_restored", True),
        ("holdout", "NOT OPENED"), ("performance", "NOT MEASURED"),
        ("clock_samples", 0), ("benchmark_files_read", 0),
        ("hidden_cases_read", 0),
    ):
        require(value.get(key) == expected, "the latest genuine V20 Rust result changed: " + key)
    rows = value.get("suite_integrity")
    require(type(rows) is list and len(rows) == len(LATEST_SUITES), "one actual latest Rust worker was dropped or invented")
    for actual, expected in zip(rows, LATEST_SUITES, strict=True):
        require(type(actual) is dict, "a genuine latest Rust original suite was forged")
        received = (actual.get("suite"), actual.get("case_execution_denominator"), actual.get("fully_observed"), actual.get("mismatch_count"), actual.get("verified_passing_case_count"), actual.get("failure_class"), actual.get("pid"), actual.get("returncode"))
        require(received == expected, "an actual latest Rust suite changed: " + expected[0])
    require(sum(row[1] for row in LATEST_SUITES) == 31237 and sum(row[4] for row in LATEST_SUITES) == 15749 and len({row[6] for row in LATEST_SUITES}) == 13, "latest original denominator, verified passes, or genuine workers changed")
    return value


def checked_label(value: object) -> str:
    require(type(value) is str and value == BUILD_LABEL and len(value) <= 48 and all(char.isascii() and (char.isalnum() or char in "-_") for char in value), "require the unique V22 first-party evidence label")
    return value


def evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool, "a genuine successful or failed build outcome is mandatory")
    stem = "native-source-build-v22-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    return "native-source-build-v22-rust-" + checked_label(label) + "-root-provenance-receipt.json"


def clone(base: dict[str, object], value: object) -> object:
    return base["StrictJSON"](canonical(base, value)).decode()


def parse_cli(parent: dict[str, object], base: dict[str, object], values: list[str]) -> dict[str, object]:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    selected = [item for item in modes if item in values]
    require(len(selected) == 1 and values.count(selected[0]) == 1, "exactly one isolated V22 source mode or explicitly authorized build is mandatory")
    mode = selected[0]
    result: dict[str, object] = {"mode": mode, "owned_source_sha256": []}
    mapping = {
        "--source-sha256": "source_sha256", "--protocol-sha256": "protocol_sha256", "--contract-sha256": "contract_sha256",
        "--label": "label", "--combined-bridge-sha256": "combined_bridge_sha256", "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256", "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--predecessor-bridge-sha256": "predecessor_bridge_sha256", "--predecessor-bridge-bytes": "predecessor_bridge_bytes",
        "--previous-v21-source-sha256": "previous_v21_source_sha256", "--previous-v21-protocol-sha256": "previous_v21_protocol_sha256", "--previous-v21-contract-sha256": "previous_v21_contract_sha256",
        "--previous-v21-build-receipt-sha256": "previous_v21_build_receipt_sha256", "--previous-v21-root-receipt-sha256": "previous_v21_root_receipt_sha256",
        "--semantic-source-sha256": "semantic_source_sha256", "--semantic-protocol-sha256": "semantic_protocol_sha256", "--semantic-contract-sha256": "semantic_contract_sha256",
        "--latest-rust-failure-receipt-sha256": "latest_rust_failure_receipt_sha256",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256", "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256", "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
    }
    index = 0
    while index < len(values):
        flag = values[index]
        if flag == mode:
            index += 1
            continue
        if flag == "--owned-source-sha256":
            require(index + 1 < len(values), "an exact independently owned Rust source pin is incomplete")
            result["owned_source_sha256"].append(values[index + 1])
            index += 2
            continue
        require(flag in mapping and index + 1 < len(values), "reject abbreviated or unowned V22 source-build authority")
        name = mapping[flag]
        require(name not in result, "reject repeated V22 source-build authority: " + flag)
        value: object = values[index + 1]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(), "an exact positive byte count is mandatory")
            value = int(value)
        result[name] = value
        index += 2
    require("source_sha256" in result and "protocol_sha256" in result, "caller-pin the independent V22 source and protocol")
    checked_hash(result["source_sha256"], "V22 source")
    checked_hash(result["protocol_sha256"], "V22 protocol")
    if mode == "--render-contract":
        require("contract_sha256" not in result, "the contract cannot self-pin before canonical rendering")
    else:
        require("contract_sha256" in result, "caller-pin the complete V22 canonical contract")
        checked_hash(result["contract_sha256"], "V22 contract")
    build_only = set(mapping.values()) - {"source_sha256", "protocol_sha256", "contract_sha256"}
    if mode != "--build":
        require(not result["owned_source_sha256"] and not any(key in result for key in build_only), "a source-only verification must not carry native build authority")
        return result
    for field, expected in (
        ("label", BUILD_LABEL), ("combined_bridge_sha256", DERIVED_SHA256),
        ("combined_bridge_bytes", DERIVED_BYTES), ("corrected_adapter_sha256", ADAPTER_SHA256),
        ("corrected_adapter_bytes", ADAPTER_BYTES), ("predecessor_bridge_sha256", CAPTURE_SHA256),
        ("predecessor_bridge_bytes", CAPTURE_BYTES),
        ("previous_v21_source_sha256", V21["source"][2]),
        ("previous_v21_protocol_sha256", V21["protocol"][2]),
        ("previous_v21_contract_sha256", V21["contract"][2]),
        ("previous_v21_build_receipt_sha256", V21["build_receipt"][2]),
        ("previous_v21_root_receipt_sha256", V21["root_receipt"][2]),
        ("semantic_source_sha256", SEMANTIC["source"][2]),
        ("semantic_protocol_sha256", SEMANTIC["protocol"][2]),
        ("semantic_contract_sha256", SEMANTIC["contract"][2]),
        ("latest_rust_failure_receipt_sha256", LATEST_FAILURE[2]),
    ):
        require(result.get(field) == expected, "independently caller-pin complete genuine V22 build ancestry: " + field)
    for role, key in (("source", "phase1_v4_source_sha256"), ("protocol", "phase1_v4_protocol_sha256"), ("contract", "phase1_v4_contract_sha256")):
        require(result.get(key) == parent["V19_PHASE1"][role][2], "independently caller-pin every genuine passing phase-one owner")
    expected_owned = {base["OWNER_BY_NAME"][name][1] + "=" + base["OWNER_BY_NAME"][name][2] for name in base["RUST_SOURCE_NAMES"]}
    provided = result["owned_source_sha256"]
    require(type(provided) is list and len(provided) == 9 and set(provided) == expected_owned, "caller-pin precisely nine independent canonical Rust source owners")
    return result


def future_arguments(parent: dict[str, object], base: dict[str, object], source_pin: str, protocol_pin: str, contract_pin: str) -> list[str]:
    arguments = [
        "--build", "--source-sha256", source_pin, "--protocol-sha256", protocol_pin,
        "--contract-sha256", contract_pin, "--label", BUILD_LABEL,
        "--combined-bridge-sha256", DERIVED_SHA256, "--combined-bridge-bytes", str(DERIVED_BYTES),
        "--corrected-adapter-sha256", ADAPTER_SHA256, "--corrected-adapter-bytes", str(ADAPTER_BYTES),
        "--predecessor-bridge-sha256", CAPTURE_SHA256, "--predecessor-bridge-bytes", str(CAPTURE_BYTES),
        "--previous-v21-source-sha256", V21["source"][2], "--previous-v21-protocol-sha256", V21["protocol"][2],
        "--previous-v21-contract-sha256", V21["contract"][2],
        "--previous-v21-build-receipt-sha256", V21["build_receipt"][2],
        "--previous-v21-root-receipt-sha256", V21["root_receipt"][2],
        "--semantic-source-sha256", SEMANTIC["source"][2],
        "--semantic-protocol-sha256", SEMANTIC["protocol"][2],
        "--semantic-contract-sha256", SEMANTIC["contract"][2],
        "--latest-rust-failure-receipt-sha256", LATEST_FAILURE[2],
    ]
    for role, flag in (("source", "--phase1-v4-source-sha256"), ("protocol", "--phase1-v4-protocol-sha256"), ("contract", "--phase1-v4-contract-sha256")):
        arguments.extend((flag, parent["V19_PHASE1"][role][2]))
    for name in base["RUST_SOURCE_NAMES"]:
        row = base["OWNER_BY_NAME"][name]
        arguments.extend(("--owned-source-sha256", row[1] + "=" + row[2]))
    return arguments


def boundary() -> dict[str, object]:
    return {
        "actual_compiler_process_count": 0, "compiler_processes_started": 0,
        "candidate_workers_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "private_root_opens": 0,
        "archive_opens": 0, "archive_inflations": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_build": "NOT RUN", "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED", "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED", "holdout": "NOT OPENED",
        "expanded_holdout_case_count": 14155776,
        "expanded_holdout_cases": "NOT GENERATED; NOT OPENED",
        "qualified_candidate_count": 0, "winner_selected": False,
    }


def collect_context(semantic: dict[str, object], previous: dict[str, object], parent: dict[str, object], ancestor: dict[str, object], base: dict[str, object], source_pin: str, protocol_pin: str, contract_pin: str | None = None) -> tuple[dict[str, object], dict[str, object]]:
    source_raw, source_info = base["read_self"](SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = base["read_self"](PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n") and protocol_raw.endswith(b"\n") and not protocol_raw.endswith(b"\n\n"), "require exact source and protocol owner final newlines")
    v21_context, v21_state = previous["collect_context"](parent, ancestor, base, V21["source"][2], V21["protocol"][2], V21["contract"][2])
    require(v21_context.get("status") == "PASS" and v21_context.get("version") == 21 and v21_context.get("first_party_rust_source_owner_count") == 9 and v21_context.get("future_total_compiler_process_count") == 28 and v21_context.get("original_case_execution_denominator") == 31237 and v21_context.get("original_suite_count") == 13, "preserve complete independently frozen captured native source and Python oracle")
    v21_build = decode_owner(base, V21["build_receipt"], "actual V21 native build")
    v21_root = decode_owner(base, V21["root_receipt"], "actual V21 private-root receipt")
    actual_build = validate_actual_v21(v21_build, v21_root)
    latest = validate_latest_failure(decode_owner(base, LATEST_FAILURE, "latest actual V20 original Rust failure"))
    for role in ("source", "protocol", "contract"):
        base["read_exact"](SEMANTIC[role])
    semantic_owners, derived, older = semantic["load_context"]()
    require(type(semantic_owners) is dict and type(derived) is bytes and digest(derived) == DERIVED_SHA256 and len(derived) == DERIVED_BYTES and semantic_owners.get("selected_bridge") == v21_state.get("captured_bytes"), "derive the complete frozen semantic bridge from the exact actually built V21 predecessor")
    require(type(older) is dict and older.get("candidate_status") == "FAIL" and older.get("completed_suite_count") == 8 and older.get("verified_passing_case_count") == 12942 and older.get("semantic_mismatch_count") == "NOT MEASURED", "do not overwrite or conflate the separately recorded historical V19 failure")
    semantic_contract = decode_owner(base, SEMANTIC["contract"], "independent first-party semantic source freeze")
    semantic_source = semantic["read_owner"](SEMANTIC["source"][1], SEMANTIC["source"][2], SEMANTIC["source"][3])
    semantic_protocol = semantic["read_owner"](SEMANTIC["protocol"][1], SEMANTIC["protocol"][2], SEMANTIC["protocol"][3])
    semantic_expected = semantic["build_contract"](SEMANTIC["source"][2], semantic_source, SEMANTIC["protocol"][2], semantic_protocol, derived)
    require(semantic_contract == semantic_expected, "the complete semantic bridge freeze was not independently regenerated")
    require(type(v21_state.get("v18_state")) is dict and type(v21_state["v18_state"].get("originals")) is dict and len(v21_state["v18_state"]["originals"]) == 9 and digest(v21_state["v18_state"]["corrected_adapter"]) == ADAPTER_SHA256 and len(v21_state["v18_state"]["corrected_adapter"]) == ADAPTER_BYTES, "retain every original source and exact independently owned public adapter")
    context: dict[str, object] = {
        "schema": SCHEMA + "-read-only-frozen-context", "version": VERSION,
        "status": "PASS", "family": FAMILY,
        "source": source_info, "protocol": protocol_info,
        "previous_v21_build_status": "PASS", "previous_v21_root_status": "PASS",
        "previous_v21_compiler_process_count": 28,
        "previous_v21_private_phase_count": 2,
        "previous_v21_build_receipt_sha256": V21["build_receipt"][2],
        "previous_v21_root_receipt_sha256": V21["root_receipt"][2],
        "semantic_source_sha256": SEMANTIC["source"][2],
        "semantic_protocol_sha256": SEMANTIC["protocol"][2],
        "semantic_contract_sha256": SEMANTIC["contract"][2],
        "previous_captured_bridge_sha256": CAPTURE_SHA256,
        "semantic_corrected_bridge_sha256": DERIVED_SHA256,
        "semantic_corrected_bridge_bytes": DERIVED_BYTES,
        "preserved_capture_fast_path_lines": 17,
        "original_rust_source_owner_count": 9,
        "cargo_external_dependency_count": 0,
        "phase_one_readiness": "PASS", "candidate_qualification": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13, "named_private_waiver_count": 13,
        "supplemental_reference_case_count": 8244,
        "latest_actual_rust_candidate_status": "FAIL",
        "latest_actual_rust_attempted_suite_count": 13,
        "latest_actual_rust_completed_suite_count": 12,
        "latest_actual_rust_infrastructure_failure_count": 1,
        "latest_actual_rust_verified_passing_case_count": 15749,
        "latest_actual_rust_global_semantic_mismatch_count": "NOT MEASURED",
        "latest_actual_rust_observed_suite_mismatch_counts": {"substitution_v2": 240, "shape_v2": 1056},
        "latest_actual_rust_failure_receipt_sha256": LATEST_FAILURE[2],
        "historical_v19_rust_completed_suite_count": 8,
        "historical_v19_rust_verified_passing_case_count": 12942,
        "future_phase_count": 2, "future_roles_per_phase": 14,
        "future_total_compiler_process_count": 28,
        **boundary(),
    }
    state = {"source_info": source_info, "protocol_info": protocol_info, "v21_context": v21_context, "v21_state": v21_state, "v21_build_receipt": v21_build, "v21_root_receipt": v21_root, "v21_actual_build": actual_build, "semantic_contract": semantic_contract, "semantic_observed": semantic_owners, "semantic_derived": derived, "historical_v19_failure": older, "latest_v20_failure": latest}
    expected = contract_document(parent, base, source_pin, protocol_pin, state)
    if contract_pin is not None:
        checked_hash(contract_pin, "V22 complete canonical source contract")
        raw, info = base["read_self"](CONTRACT_PATH, contract_pin)
        require(raw == canonical(base, expected) and base["StrictJSON"](raw).decode() == expected, "reject a partial, stale, or fabricated V22 source-build contract")
        context["contract"] = info
    base["no_matching_imports"]()
    return context, state


def contract_document(parent: dict[str, object], base: dict[str, object], source_pin: str, protocol_pin: str, state: dict[str, object]) -> dict[str, object]:
    owners = base["OWNER_BY_NAME"]
    success_archive, success_receipt = evidence_names(BUILD_LABEL, False)
    failure_archive, failure_receipt = evidence_names(BUILD_LABEL, True)
    return {
        "schema": SCHEMA + "-source-freeze", "version": VERSION,
        "status": "SOURCE FROZEN; CORRECTED FIRST-PARTY NATIVE NOT BUILT OR RUN",
        "phase": "PHASE 2: FIRST-PARTY RUST CANDIDATE CORRECTNESS",
        "family": FAMILY,
        "source": {"path": SOURCE_PATH, "sha256": source_pin, "bytes": state["source_info"]["bytes"]},
        "protocol": {"path": PROTOCOL_PATH, "sha256": protocol_pin, "bytes": state["protocol_info"]["bytes"]},
        "pinned_python": {"implementation": "CPython", "version": "3.14.6", "path": PYTHON, "isolated": True, "no_site": True, "bytecode": False},
        "independently_frozen_v21_source": {role: owner_document(row) for role, row in V21.items()},
        "actual_successful_previous_v21_build": state["v21_actual_build"],
        "independently_frozen_semantic_correction": {
            "owners": {role: owner_document(row) for role, row in SEMANTIC.items()},
            "base_bridge_sha256": CAPTURE_SHA256, "base_bridge_bytes": CAPTURE_BYTES,
            "derived_bridge_sha256": DERIVED_SHA256, "derived_bridge_bytes": DERIVED_BYTES,
            "changed_first_party_function_count": 2,
            "changed_functions": ["rust_restore_original_template_error", "rust_replacement_cache"],
            "preserved_two_capture_fast_path_lines": 17,
            "unchanged_original_rust_matching_engine": True,
            "new_external_package": False, "new_matching_fallback": False,
            "effect_on_candidate_correctness": "NOT MEASURED",
            "candidate_native_build": "NOT RUN",
        },
        "owned_first_party_rust_family": {
            "canonical_source_count": 9,
            "canonical_sources": [{"path": owners[name][1], "sha256": owners[name][2], "bytes": owners[name][3], "device": owners[name][4], "inode": owners[name][5]} for name in base["RUST_SOURCE_NAMES"]],
            "cargo_package_count": 1, "external_cargo_dependency_count": 0,
            "external_regular_expression_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN", "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN", "canonical_sources_modified": False,
            "corrected_public_adapter_sha256": ADAPTER_SHA256,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
        },
        "latest_actual_rust_original_campaign": {
            "receipt": owner_document(LATEST_FAILURE), "publication_status": "PASS",
            "candidate_status": "FAIL", "candidate_qualified": False,
            "original_case_denominator": 31237, "named_private_waiver_count": 13,
            "attempted_worker_count": 13, "completed_suite_count": 12,
            "infrastructure_failure_count": 1, "verified_passing_case_count": 15749,
            "global_semantic_mismatch_count": "NOT MEASURED",
            "fully_observed_suite_mismatch_counts": {"shape_v2": 1056, "substitution_v2": 240},
            "failed_suite_cases_counted_as_passing": False,
            "all_original_targets_restored": True,
        },
        "preserved_prior_semantic_observation": {
            "actual_v19_receipt_sha256": "e48a4115a85d827cbf16a32b6b44390d2bf4b092e1823989c9bcafe874fa04fe",
            "candidate_status": "FAIL", "completed_suite_count": 8,
            "infrastructure_failure_count": 5, "verified_passing_case_count": 12942,
            "global_mismatches": "NOT MEASURED", "not_current_result": True,
        },
        "frozen_python_correctness": {
            "phase_one_status": "PASS", "candidate_qualification_status": "BLOCKED",
            "original_case_count": 31237, "original_suite_count": 13,
            "named_private_waivers": 13,
            "separate_supplemental_reference_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
        },
        "future_exclusive_offline_build": {
            "authorization": "EXPLICIT ROOT-APPROVED --build ONLY",
            "label": BUILD_LABEL, "root_parent": "/tmp",
            "root_prefix": "rebar-phase2-native-build-v9-rust-",
            "private_root_status": "NOT CREATED; NOT OPENED",
            "phase_names": list(PHASES), "phase_count": 2,
            "roles_per_phase": list(PROCESS_NAMES),
            "processes_per_phase": 14, "total_compiler_processes": 28,
            "cargo_flags": ["--release", "--locked", "--offline", "--frozen"],
            "external_dependency_count": 0,
            "semantic_bridge_overlay_count": 2,
            "corrected_adapter_overlay_count": 2,
            "cross_phase_identical_complete_engine_and_bridge_elf": True,
            "process_identity": "28 DISTINCT ACTUAL PIDS REQUIRED",
            "root_capture": "LIVE EXACT COMPLETED 28-ROLE VERIFICATION CALLBACK ONLY",
            "root_receipt_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "receipt_and_directory_fsync": True,
            "success_archive": success_archive,
            "success_public_receipt": success_receipt,
            "failure_archive": failure_archive,
            "failure_public_receipt": failure_receipt,
            "root_public_receipt": root_receipt_name(BUILD_LABEL),
            "build_pass_means": "REPRODUCIBLE FIRST-PARTY NATIVE COMPILATION ONLY",
            "candidate_correctness": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "source_only_effects": boundary(),
    }


def expect_rejection(action: object, label: str) -> None:
    try:
        action()
    except Exception:
        return
    raise GateError("a hostile source-only native-build control was accepted: " + label)


def self_test(semantic: dict[str, object], previous: dict[str, object], parent: dict[str, object], ancestor: dict[str, object], base: dict[str, object], source_pin: str, protocol_pin: str, contract_pin: str) -> dict[str, object]:
    context, state = collect_context(semantic, previous, parent, ancestor, base, source_pin, protocol_pin, contract_pin)
    count = 0

    def reject(action: object, label: str) -> None:
        nonlocal count
        expect_rejection(action, label)
        count += 1

    for key, value in (("candidate_status", "PASS"), ("candidate_qualified", True), ("completed_suite_count", 13), ("infrastructure_failure_count", 0), ("verified_passing_case_count", 31237), ("semantic_mismatch_count", 1296), ("case_execution_denominator", 31236), ("named_private_waiver_count", 12), ("all_four_original_targets_restored", False), ("holdout", "OPENED"), ("clock_samples", 1), ("performance", "1.5x")):
        forged = clone(base, state["latest_v20_failure"])
        forged[key] = value
        reject(lambda document=forged: validate_latest_failure(document), "forged latest 13-worker Rust result: " + key)
    for index, field, value in ((7, "mismatch_count", 0), (8, "mismatch_count", 0), (7, "verified_passing_case_count", 4880), (8, "verified_passing_case_count", 9184), (10, "fully_observed", True), (10, "failure_class", "PASS"), (0, "pid", 190)):
        forged = clone(base, state["latest_v20_failure"])
        forged["suite_integrity"][index][field] = value
        reject(lambda document=forged: validate_latest_failure(document), "forged genuine latest suite: " + str(index) + ":" + field)
    for field, value in (("status", "FAIL"), ("build_status", "FAIL"), ("actual_compiler_process_count", 27), ("combined_bridge_sha256", DERIVED_SHA256), ("combined_bridge_overlay_apply_count", 1), ("corrected_public_adapter_overlay_apply_count", 1), ("candidate_qualified", True), ("candidate_matching", "PASS"), ("performance", "1.5x"), ("holdout", "OPENED")):
        forged = clone(base, state["v21_build_receipt"])
        forged[field] = value
        reject(lambda document=forged: validate_actual_v21(document, state["v21_root_receipt"]), "forged actual V21 build receipt: " + field)
    for field, value in (("status", "FAIL"), ("canonical_build_status", "FAIL"), ("canonical_build_receipt_sha256", "0" * 64), ("actual_compiler_process_count", 27), ("actual_source_phase_count", 1), ("cumulative_captured_bridge_sha256", DERIVED_SHA256), ("candidate_qualified", True), ("hidden_cases_read", 1), ("historical_archives_opened", 1), ("holdout", "OPENED")):
        forged = clone(base, state["v21_root_receipt"])
        forged[field] = value
        reject(lambda document=forged: validate_actual_v21(state["v21_build_receipt"], document), "forged actual V21 root receipt: " + field)
    for field, value in (("phase_count", 1), ("directory_scanned", True), ("nofollow_directory_descriptor", False), ("descriptor_opened_during_live_verification", False), ("mode", "0755")):
        forged = clone(base, state["v21_root_receipt"])
        forged["root"][field] = value
        reject(lambda document=forged: validate_actual_v21(state["v21_build_receipt"], document), "forged historical private-root receipt metadata: " + field)

    base_bridge = state["semantic_observed"]["selected_bridge"]
    predecessor = state["semantic_observed"]["literal_bridge"]
    derive = semantic["derive_bridge"]
    reject(lambda: derive(base_bridge + b"\n", predecessor), "substituted actual captured first-party bridge")
    reject(lambda: derive(base_bridge, predecessor + b"\n"), "substituted first-party literal predecessor")
    reject(lambda: derive(base_bridge.replace(semantic["CAPTURE_INSERTION"], b"", 1), predecessor), "removed 17-line first-party captured fast path")
    reject(lambda: derive(base_bridge.replace(semantic["OUTER_LENGTH_REWRITE"], b"", 1), predecessor), "concealed outer visible-buffer defect")
    reject(lambda: derive(base_bridge.replace(semantic["FAILED_REPLACEMENT_ORIGINAL"], b"        } else {\n            return -1;\n", 1), predecessor), "concealed genuine replacement-exception defect")
    for nested in (0, 1, 2, 5, 8):
        reject(lambda size=nested: semantic["validate_visible_position"](13, size, 12), "outer-size substituted for visible nested error position: " + str(nested))
    ledger = semantic["EXPECTED_LEDGER"]
    for index, replacement in ((0, ("acquire", "replacement", 0, 0, 1)), (1, ("acquire", "subject", 0, 0, 1)), (2, ("acquire", "replacement", 0, 0, 1)), (3, ("release", "subject", None, 2, 1))):
        forged = list(ledger)
        forged[index] = replacement
        reject(lambda value=forged: semantic["validate_ledger"](value), "forged exact nested role, FULL_READONLY flag, or LIFO release")
    for role, kind, message in semantic["EXPECTED_ERRORS"]:
        reject(lambda label=role, text=message: semantic["validate_error"]((label, "RuntimeError", text)), "substituted role-specific original error: " + role)
        reject(lambda label=role, error=kind: semantic["validate_error"]((label, error, "forged message")), "substituted role-specific error message: " + role)

    contract = contract_document(parent, base, source_pin, protocol_pin, state)
    candidate = future_arguments(parent, base, source_pin, protocol_pin, contract_pin)
    parsed = parse_cli(parent, base, list(candidate))
    require(parsed.get("mode") == "--build" and parsed.get("combined_bridge_sha256") == DERIVED_SHA256 and len(parsed.get("owned_source_sha256", ())) == 9 and base.get("_WALL_ENABLED") is True and ROOT_CAPTURE is None, "validate the precise future build argv without authorizing compilation")

    def validate_future_authority(arguments: list[str]) -> dict[str, object]:
        exact = parse_cli(parent, base, arguments)
        require(
            exact.get("source_sha256") == source_pin
            and exact.get("protocol_sha256") == protocol_pin
            and exact.get("contract_sha256") == contract_pin,
            "reject substituted caller-pinned V22 native-build owner authority",
        )
        return exact

    for flag in ("--source-sha256", "--protocol-sha256", "--contract-sha256", "--combined-bridge-sha256", "--semantic-source-sha256", "--semantic-protocol-sha256", "--semantic-contract-sha256", "--previous-v21-build-receipt-sha256", "--previous-v21-root-receipt-sha256", "--latest-rust-failure-receipt-sha256"):
        forged_args = list(candidate)
        index = forged_args.index(flag)
        forged_args[index + 1] = "0" * 64
        reject(lambda argv=forged_args: validate_future_authority(argv), "substituted future first-party native build pin: " + flag)
    for flag in ("--label", "--combined-bridge-bytes", "--corrected-adapter-bytes", "--predecessor-bridge-bytes"):
        forged_args = list(candidate)
        index = forged_args.index(flag)
        forged_args[index + 1] = "0"
        reject(lambda argv=forged_args: parse_cli(parent, base, argv), "substituted future build authority: " + flag)
    source_args = ["--self-test", "--source-sha256", source_pin, "--protocol-sha256", protocol_pin, "--contract-sha256", contract_pin]
    reject(lambda: parse_cli(parent, base, source_args + ["--label", BUILD_LABEL]), "source-only invocation secretly authorizes compilation")
    reject(lambda: parse_cli(parent, base, source_args + ["--build"]), "source and actual native modes combined")
    for forged in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":01}', b'{"x":"\\uD800"}', b'{"x":1}{"x":2}', b'[1,]'):
        reject(lambda raw=forged: base["StrictJSON"](raw).decode(), "malformed, repeated, or nonfinite native-build evidence")

    physical = (
        ("unlisted filesystem", lambda: builtins.open("/etc/hosts", "rb")),
        ("compressed native archive", lambda: builtins.open(ROOT + "/" + EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, False)[0], "rb")),
        ("historical V21 native archive", lambda: builtins.open(ROOT + "/" + EVIDENCE_PATH + "/native-source-build-v21-rust-phase2-v21-rust-captured-findall-root-provenance.json.gz", "rb")),
        ("hidden final holdout", lambda: builtins.open(ROOT + "/benchmarks/holdout.json", "rb")),
        ("source-file mutation", lambda: builtins.open(ROOT + "/" + SOURCE_PATH, "w")),
        ("standard-library matcher", lambda: sys.audit("import", "re", None, None, None, None)),
        ("CPython matcher", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("external package matcher", lambda: sys.audit("import", "regex", None, None, None, None)),
        ("candidate activation", lambda: sys.audit("import", "candidates.rust_candidate", None, None, None, None)),
        ("native loading", lambda: sys.audit("ctypes.dlopen", "forbidden.so")),
        ("compiler process", lambda: sys.audit("subprocess.Popen", "rustc", (), None, None)),
        ("private temporary root", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
        ("network request", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("clock sample", lambda: sys.audit("time.monotonic")),
        ("entropy", lambda: sys.audit("os.urandom", 32)),
        ("dynamic compilation", lambda: sys.audit("compile", b"forbidden", "<forged>")),
        ("dynamic execution", lambda: sys.audit("exec", "forbidden")),
        ("destructive rename", lambda: sys.audit("os.rename", "old", "new", -1, -1)),
    )
    for label, action in physical:
        reject(action, "physical source-only audit wall: " + label)
    for key in ("filesystem", "matching_import", "process", "native", "network", "clock", "temporary", "dynamic_execution"):
        require(base["_BLOCKED"].get(key, 0) > 0, "an irreversible physical native-build boundary was not proven: " + key)
    require(ENTROPY_BLOCKED > 0, "the source-only entropy boundary was not physically proven")
    base["no_matching_imports"]()
    return {**context, "schema": SCHEMA + "-source-only-self-test", "mode": "self-test", "source_only_hostile_controls": count, "physical_audit_controls": len(physical), "future_build_argv_validated": True, "future_build_started": False, "blocked_physical_effects": dict(base["_BLOCKED"])}


def assert_fresh_root_receipt(label: str) -> None:
    target = ROOT + "/" + EVIDENCE_PATH + "/" + root_receipt_name(label)
    try:
        os.lstat(target)
    except FileNotFoundError:
        return
    raise GateError("reject a preexisting V22 corrected-build root receipt")


def publish_root_provenance(previous: dict[str, object], parent: dict[str, object], ancestor: dict[str, object], base: dict[str, object], module: object, state: dict[str, object], result: dict[str, object], options: dict[str, object]) -> dict[str, object]:
    require(result.get("status") == "PASS" and result.get("build_status") == "PASS" and result.get("family") == FAMILY and result.get("label") == BUILD_LABEL and type(ROOT_CAPTURE) is dict, "publish a root receipt only after 28 genuinely successful native processes")
    capture = ROOT_CAPTURE
    require(capture.get("unique_process_count") == 28 and capture.get("phase_count") == 2, "reject incomplete real two-phase corrected Rust compilation")
    runtime = state.get("runtime_state")
    require(type(runtime) is dict and runtime.get("kernel") is not None, "retain the actual durable original build kernel")
    kernel = runtime["kernel"]
    relative = result.get("receipt_relative")
    receipt_hash = result.get("receipt_sha256")
    require(relative == EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, False)[1], "bind the unique actual V22 success receipt")
    checked_hash(receipt_hash, "actual corrected native-build publication receipt")
    observed = os.stat(ROOT + "/" + relative, follow_symlinks=False)
    row = ("fresh_actual_v22_semantic_native_receipt", relative, receipt_hash, observed.st_size, observed.st_dev, observed.st_ino)
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | {ROOT + "/" + relative})
    receipt = decode_owner(base, row, "fresh actual semantic-corrected native build")
    for field, expected in (
        ("schema", SCHEMA + "-durable-publication-receipt"), ("status", "PASS"),
        ("build_status", "PASS"), ("family", FAMILY), ("label", BUILD_LABEL),
        ("source_sha256", options["source_sha256"]),
        ("protocol_sha256", options["protocol_sha256"]),
        ("contract_sha256", options["contract_sha256"]),
        ("expected_actual_compiler_process_count", 28),
        ("actual_compiler_process_count", 28),
        ("combined_bridge_sha256", DERIVED_SHA256),
        ("combined_bridge_bytes", DERIVED_BYTES),
        ("combined_bridge_overlay_apply_count", 2),
        ("corrected_public_adapter_sha256", ADAPTER_SHA256),
        ("corrected_public_adapter_bytes", ADAPTER_BYTES),
        ("corrected_public_adapter_overlay_apply_count", 2),
        ("candidate_matching", "NOT RUN"), ("candidate_qualified", False),
    ):
        require(receipt.get(field) == expected, "the fresh actual corrected-build receipt was incomplete: " + field)
    for name in base["RUST_SOURCE_NAMES"]:
        base["read_exact"](base["OWNER_BY_NAME"][name])
    record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt", "version": VERSION,
        "status": "PASS", "publication_pass_means": "DURABLE FIRST-PARTY NATIVE SOURCE BUILD ONLY",
        "family": FAMILY, "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "previous_v21_source_sha256": V21["source"][2],
        "previous_v21_protocol_sha256": V21["protocol"][2],
        "previous_v21_contract_sha256": V21["contract"][2],
        "previous_v21_build_receipt_sha256": V21["build_receipt"][2],
        "previous_v21_root_receipt_sha256": V21["root_receipt"][2],
        "semantic_source_sha256": SEMANTIC["source"][2],
        "semantic_protocol_sha256": SEMANTIC["protocol"][2],
        "semantic_contract_sha256": SEMANTIC["contract"][2],
        "latest_original_campaign_receipt_sha256": LATEST_FAILURE[2],
        "previous_captured_bridge_sha256": CAPTURE_SHA256,
        "corrected_semantic_bridge_sha256": DERIVED_SHA256,
        "corrected_semantic_bridge_bytes": DERIVED_BYTES,
        "corrected_public_adapter_sha256": ADAPTER_SHA256,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": relative,
        "canonical_build_receipt_sha256": receipt_hash,
        "canonical_build_receipt_bytes": observed.st_size,
        "canonical_build_receipt_device": observed.st_dev,
        "canonical_build_receipt_inode": observed.st_ino,
        "root": capture["root"], "actual_compiler_process_count": 28,
        "expected_compiler_process_count": 28, "actual_source_phase_count": 2,
        "bridge_overlay_apply_count": 2, "adapter_overlay_apply_count": 2,
        "original_source_identity_count": 9,
        "all_original_source_identities_restored": True,
        "candidate_correctness": "NOT MEASURED", "candidate_matching": "NOT RUN",
        "candidate_qualified": False, "candidate_workers_started": 0,
        "native_libraries_loaded": 0, "canonical_sources_modified": False,
        "tmp_directory_scanned": False, "historical_archives_opened": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    payload = canonical(base, record)
    require(0 < len(payload) <= MAX_OWNER_BYTES, "bound the complete durable V22 corrected root receipt")
    saved = kernel.write_fresh(module.ROOT / EVIDENCE_PATH / root_receipt_name(BUILD_LABEL), payload, synchronize=True)
    synced = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(saved.get("sha256") == digest(payload) and saved.get("bytes") == len(payload) and saved.get("exclusive_creation") is True and saved.get("file_fsync_completed") is True and synced.get("completed") is True, "publish exactly one no-follow, exclusively created, fully synchronized corrected root receipt")
    return {**result, "root_provenance_status": "PASS", "root_provenance_receipt_relative": EVIDENCE_PATH + "/" + root_receipt_name(BUILD_LABEL), "root_provenance_receipt_sha256": saved["sha256"], "root_provenance_receipt_bytes": saved["bytes"], "root_provenance_directory_fsync": synced, "actual_compiler_process_count": 28, "actual_private_phase_count": 2, "semantic_corrected_bridge_sha256": DERIVED_SHA256, "semantic_corrected_bridge_bytes": DERIVED_BYTES, "all_original_source_identities_restored": True, "candidate_matching": "NOT RUN", "candidate_correctness": "NOT MEASURED"}


def run_build(semantic: dict[str, object], previous: dict[str, object], parent: dict[str, object], ancestor: dict[str, object], base: dict[str, object], options: dict[str, object]) -> dict[str, object]:
    global ROOT_CAPTURE
    require(options.get("mode") == "--build" and options.get("label") == BUILD_LABEL and ROOT_CAPTURE is None and base.get("_WALL_ENABLED") is False, "native compilation requires one root-authorized exclusive V22 build")
    base["verify_future_phase_one_v4"](options)
    context, state = collect_context(semantic, previous, parent, ancestor, base, options["source_sha256"], options["protocol_sha256"], options["contract_sha256"])
    previous_state = state["v21_state"]["v18_state"]
    raw = previous_state["owners"]["v16_builder"]
    owner = base["OWNER_BY_NAME"]["v16_builder"]
    require(type(raw) is bytes and digest(raw) == owner[2], "execute only the independently frozen zero-dependency first-party native compiler kernel")
    name = "_rebar_v22_explicit_owned_capture_shape_semantic_native_kernel"
    require(name not in sys.modules, "reject reused or cross-candidate native build authority")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
        require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16" and module.VERSION == 16 and module.FAMILY == FAMILY and module.PHASES == PHASES and module.PROCESS_NAMES == PROCESS_NAMES and module.ROOT_PREFIX == "rebar-phase2-native-build-v9-rust-", "retain only the genuine first-party 28-process compiler and original evidence recorder")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE_PATH
        module.PROTOCOL_PATH = PROTOCOL_PATH
        module.CONTRACT_PATH = CONTRACT_PATH
        module.FINAL_GRAPH_VERSION = previous["GRAPH_VERSION"]
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = previous["EVIDENCE_FLOOR"]
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = previous["HISTORY_FLOOR"]
        module.COMBINED_VARIANT = module.Owner(previous["CAPTURE_VARIANT"][1], DERIVED_SHA256, DERIVED_BYTES)
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(module.Owner(base["OWNER_BY_NAME"][role][1], base["OWNER_BY_NAME"][role][2], base["OWNER_BY_NAME"][role][3]) for role in ("v2_repair", "v2_protocol", "v2_contract"))
        module.FINAL_GRAPH = tuple(module.Owner(row[1], row[2], row[3]) for row in parent["GRAPH"].values())

        def verified_context(source_pin: str, protocol_pin: str, contract_pin: str) -> tuple[dict[str, object], dict[str, object]]:
            require((source_pin, protocol_pin, contract_pin) == (options["source_sha256"], options["protocol_sha256"], options["contract_sha256"]), "reject substituted corrected-source native build authority")
            runtime = {"originals": previous_state["originals"], "combined_bridge": state["semantic_derived"], "corrected_adapter": previous_state["corrected_adapter"], "low_level_v9_source": previous_state["low_level_v9_source"]}
            state["runtime_state"] = runtime
            return context, runtime

        original_verifier = module.verify_reproduced_phases

        def verify_actual_phases(low_level: object, kernel: object, workdir: str, phases: list[object], steps: list[object]) -> dict[str, object]:
            global ROOT_CAPTURE
            require(ROOT_CAPTURE is None and type(steps) is list and len(steps) == 28, "require exactly 28 real first-party compile and ELF inspection processes")
            pids: set[int] = set()
            for index, operation in enumerate(steps):
                expected_phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(operation) is dict and operation.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)] and ("phase" not in operation or operation.get("phase") == expected_phase) and type(operation.get("pid")) is int and operation["pid"] > 0 and operation["pid"] not in pids and operation.get("exit_status") == 0 and operation.get("working_directory") == "<FRESH_PRIVATE_TMP>/" + expected_phase, "a real corrected first-party compiler process was missing, repeated, reordered, or failed")
                pids.add(operation["pid"])
            descriptor, root = ancestor["capture_root_descriptor"](low_level, workdir, phases)
            try:
                proof = original_verifier(low_level, kernel, workdir, phases, steps)
                require(type(proof) is dict and proof.get("status") == "PASS" and proof.get("unique_process_count") == 28 and proof.get("combined_bridge_overlay_count") == 2 and proof.get("corrected_public_adapter_overlay_count") == 2 and proof.get("combined_bridge_sha256") == DERIVED_SHA256 and proof.get("combined_bridge_bytes") == DERIVED_BYTES and proof.get("byte_identical") is True and proof.get("native_libraries_loaded") == 0, "verify complete independently reproducible corrected Rust engine and bridge ELF")
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(after.st_mode) and stat.S_IMODE(after.st_mode) == 0o700 and after.st_uid == os.geteuid() and (after.st_dev, after.st_ino) == (root["device"], root["inode"]) and (named.st_dev, named.st_ino) == (root["device"], root["inode"]), "reject borrowed or exchanged live corrected-build root")
                ROOT_CAPTURE = {"root": root, "phase_count": 2, "unique_process_count": 28, "compiler_process_ids": sorted(pids), "original_reproducibility": "PASS"}
                return proof
            finally:
                os.close(descriptor)

        module.verify_frozen_context = verified_context
        module.evidence_names = evidence_names
        module.verify_reproduced_phases = verify_actual_phases
        assert_fresh_root_receipt(BUILD_LABEL)

        class Options:
            pass

        forwarded = Options()
        for field in ("source_sha256", "protocol_sha256", "contract_sha256", "owned_source_sha256", "combined_bridge_sha256", "combined_bridge_bytes", "corrected_adapter_sha256", "corrected_adapter_bytes", "label"):
            setattr(forwarded, field, options[field])
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY, "publish only a genuine corrected first-party native build result")
        if result.get("status") != "PASS":
            require(result.get("failure_preserved") is True, "publish failed corrected compilation without inventing private-root provenance")
            return result
        return publish_root_provenance(previous, parent, ancestor, base, module, state, result, options)
    finally:
        sys.modules.pop(name, None)


def entry_boundary() -> dict[str, object]:
    return {"actual_candidate_workers": 0, "actual_compiler_process_count": 0, "archive_opens": 0, "private_root_opens": 0, "native_libraries_loaded": 0, "hidden_cases_read": 0, "clock_samples": 0, "candidate_matching": "NOT RUN", "candidate_correctness": "NOT MEASURED", "candidate_qualified": False, "performance": "NOT MEASURED", "holdout": "NOT OPENED", "expanded_holdout_proposal_case_count": 14155776, "winner_selected": False}


def main() -> int:
    verify_runtime()
    semantic, previous, parent, ancestor, base = bootstrap_controllers()
    options = parse_cli(parent, base, list(sys.argv[1:]))
    mode = options["mode"]
    if mode != "--build":
        sys.addaudithook(source_entropy_wall)
        base["install_wall"]()
    if mode == "--render-contract":
        _context, state = collect_context(semantic, previous, parent, ancestor, base, options["source_sha256"], options["protocol_sha256"])
        result = contract_document(parent, base, options["source_sha256"], options["protocol_sha256"], state)
    elif mode == "--verify-frozen-context":
        result, _state = collect_context(semantic, previous, parent, ancestor, base, options["source_sha256"], options["protocol_sha256"], options["contract_sha256"])
    elif mode == "--self-test":
        result = self_test(semantic, previous, parent, ancestor, base, options["source_sha256"], options["protocol_sha256"], options["contract_sha256"])
    else:
        result = run_build(semantic, previous, parent, ancestor, base, options)
    encoded = canonical(base, result)
    require(0 < len(encoded) <= MAX_OWNER_BYTES, "bound the complete corrected native build result")
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()
    return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        failed = {"schema": SCHEMA + "-entry-failure", "status": "FAIL", "version": VERSION, "family": FAMILY, "error_type": type(error).__name__, "error_message": str(error)[:4096], **entry_boundary()}
        try:
            if "base" in globals() and type(globals()["base"]) is dict:
                sys.stdout.buffer.write(canonical(globals()["base"], failed))
            else:
                sys.stderr.write("Rust semantic native build failed: " + str(error) + "\n")
        except Exception:
            pass
        raise SystemExit(1)
