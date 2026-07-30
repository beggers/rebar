#!/usr/bin/env python3
"""Freeze an exact first-party Zig native scanner-capture correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/apply_owned_zig_scanner_capture_semantics_v1.py"
PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/zig-scanner-capture-semantics-v1.json"
BRIDGE = "candidates/zig/py_bridge.c"
BRIDGE_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
BRIDGE_BYTES = 173026
ENGINE = "candidates/zig/mini_regex.zig"
ENGINE_SHA256 = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_BYTES = 186915
TARGET = "candidates/zig/variants/scanner_capture_semantics_v1/py_bridge.c"
RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13-"
    "failures-publication-receipt.json"
)
RECEIPT_SHA256 = "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca"
ADAPTER_SOURCE = "tools/apply_owned_zig_public_adapter_semantics_v1.py"
ADAPTER_SOURCE_SHA256 = "14ffb1f8a8fc611a64ad307e4e5c86c17a635d2dc0b509c1a0c2eb60d3a75782"
ADAPTER_PROTOCOL = "oracle/phase2/ZIG-PUBLIC-ADAPTER-SEMANTICS-V1.md"
ADAPTER_PROTOCOL_SHA256 = "db81ccb98ccc018f8bec21f6e37ed33f3829be92ce435ba0f5198db28e655226"
ADAPTER_CONTRACT = "oracle/phase2/zig-public-adapter-semantics-v1.json"
ADAPTER_CONTRACT_SHA256 = "26a48a86a9d6d99d138d7e4f44bec5e2ba70c9dd36249305d4733fa9370ee765"
V15_SOURCE = "tools/run_owned_repaired_zig_original_campaign_v15.py"
V15_SOURCE_SHA256 = "4a0f50d3e6f5cc9ca987f306cb8b412149b0253d9b5add84abc05721a1a14c47"
V15_PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V15.md"
V15_PROTOCOL_SHA256 = "7576c945a29e691cdf211a1067dfa5d88837d19eca634c4114b1b58737e42950"
V15_CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v15.json"
V15_CONTRACT_SHA256 = "311fa3803b1dae37f8aebb430584eb8d7c085b00302e11f0929bda71124dd205"

OLD_CAPTURE = (
    "    size_t branch_group = active + 1;\n"
    "    match->spans[branch_group] = begins[0];\n"
    "    match->spans[exposed_stride + branch_group] = ends[0];\n"
    "    match->lastindex = (Py_ssize_t)branch_group;\n"
)
NEW_CAPTURE = (
    "    size_t branch_group = active + 1;\n"
    "    if (match->spans[branch_group] < 0) {\n"
    "        match->spans[branch_group] = begins[0];\n"
    "        match->spans[exposed_stride + branch_group] = ends[0];\n"
    "    }\n"
    "    match->lastindex = (Py_ssize_t)branch_group;\n"
)
ZERO_EFFECTS = (
    "candidate_imports", "candidate_processes", "candidate_matching_calls",
    "native_library_loads", "native_builds", "archive_opens", "holdout_opens",
    "benchmark_opens", "seed_opens", "private_root_opens", "files_written",
    "canonical_targets_changed", "subinterpreters_created",
    "reference_workers", "compiler_processes", "clock_samples",
)
FAILURES = {
    "scanner_verbose_v1": 620,
    "public_types_v1": 248,
    "substitution_v2": 64,
    "shape_v2": 672,
    "public_surface_v19": 96,
}


class FreezeError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def absolute(relative: str) -> str:
    require(type(relative) is str and relative and not relative.startswith("/")
            and ".." not in relative.split("/"),
            "reject non-owned or traversing scanner source")
    return os.path.join(ROOT, relative)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class SourceWall:
    def __init__(self, owners: set[str]):
        self.owners = {absolute(path) for path in owners}
        self.active = False

    def audit(self, event: str, values: tuple[object, ...]) -> None:
        if not self.active:
            return
        if event == "open":
            require(len(values) == 3 and type(values[0]) is str
                    and values[0] in self.owners,
                    "scanner source wall rejected unowned file")
            require(values[1] in (None, "r", "rb") and type(values[2]) is int
                    and values[2] & os.O_ACCMODE == os.O_RDONLY
                    and values[2] & (os.O_CREAT | os.O_TRUNC | os.O_APPEND) == 0,
                    "scanner source wall rejected mutable descriptor")
            return
        if event == "import":
            name = values[0] if values else ""
            forbidden = ("candidates", "re", "_sre", "regex", "ctypes", "inspect")
            require(not any(name == item or name.startswith(item + ".")
                            for item in forbidden),
                    "scanner source wall rejected engine or package import")
            return
        rejected = (
            "subprocess.", "socket.", "ctypes.", "_posixsubprocess.",
            "os.mkdir", "os.rmdir", "os.remove", "os.rename", "os.replace",
            "os.unlink", "os.chmod", "os.chown", "os.system", "os.putenv",
            "os.posix_spawn", "os.fork", "os.exec", "threading.",
        )
        require(not event.startswith(rejected),
                "scanner source wall rejected external effect " + event)

    def __enter__(self) -> "SourceWall":
        sys.addaudithook(self.audit)
        self.active = True
        return self

    def __exit__(self, kind: object, value: object, traceback: object) -> None:
        self.active = False


def read_owner(path: str, expected: str | None = None,
               length: int | None = None) -> bytes:
    descriptor = os.open(absolute(path), os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode)
                and metadata.st_nlink == 1 and metadata.st_uid == os.getuid(),
                "reject non-owned scanner input " + path)
        require(metadata.st_size <= 1024 * 1024,
                "reject oversized scanner input " + path)
        if length is not None:
            require(metadata.st_size == length,
                    "reject changed scanner input size " + path)
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    content = b"".join(chunks)
    if expected is not None:
        require(digest(content) == expected,
                "reject changed scanner input identity " + path)
    return content


def derive(original: bytes) -> bytes:
    require(len(original) == BRIDGE_BYTES and digest(original) == BRIDGE_SHA256,
            "reject altered owned Zig bridge")
    before = OLD_CAPTURE.encode()
    after = NEW_CAPTURE.encode()
    require(original.count(before) == 1,
            "reject missing or duplicate Zig scanner projection defect")
    corrected = original.replace(before, after, 1)
    require(corrected.count(after) == 1 and corrected.replace(after, before, 1) == original,
            "reject extra Zig scanner or native bridge changes")
    for marker in (
        b"static int zig_scanner_project_match(",
        b"static PyObject *zig_scanner_match(",
        b"static PyObject *zig_scanner_search(",
        b"extern int rebar_zig_match_captures_wide(",
        b"if (match->spans[branch_group] < 0) {",
    ):
        require(marker in corrected, "reject absent first-party scanner obligation")
    return corrected


def project(groups: int, active: int, outers: list[int], begins: list[int],
            ends: list[int], native_last: int, *, corrected: bool) -> dict[str, object]:
    require(type(groups) is int and groups > 0
            and len(outers) == groups and len(begins) == len(ends)
            and len(begins) > 1,
            "synthetic scanner rejected malformed capture sizes")
    native_groups = len(begins) - 1
    require(0 <= active < groups and begins[0] >= 0
            and ends[0] >= begins[0] and 1 <= native_last <= native_groups,
            "synthetic scanner rejected malformed match metadata")
    require(all(1 <= value <= native_groups for value in outers)
            and all(left < right for left, right in zip(outers, outers[1:])),
            "synthetic scanner rejected invalid outer groups")
    require(outers[active] == native_last and begins[native_last] >= 0
            and ends[native_last] >= begins[native_last],
            "synthetic scanner rejected inactive branch capture")
    starts = [-1] * (groups + 1)
    finishes = [-1] * (groups + 1)
    starts[0], finishes[0] = begins[0], ends[0]
    outer = outers[active]
    next_outer = outers[active + 1] if active + 1 < groups else native_groups + 1
    for logical in range(1, groups + 1):
        if logical > native_groups - outer:
            break
        actual = outer + logical
        if actual >= next_outer:
            break
        if begins[actual] < 0:
            continue
        require(ends[actual] >= begins[actual],
                "synthetic scanner rejected inverted local capture")
        starts[logical], finishes[logical] = begins[actual], ends[actual]
    branch_group = active + 1
    if not corrected or starts[branch_group] < 0:
        starts[branch_group], finishes[branch_group] = begins[0], ends[0]
    return {"starts": starts, "ends": finishes, "lastindex": branch_group}


def self_test(original: bytes, corrected: bytes) -> int:
    controls = 0
    witness = dict(groups=2, active=0, outers=[1, 3],
                   begins=[0, 0, 1, -1], ends=[3, 3, 3, -1], native_last=1)
    old = project(**witness, corrected=False)
    new = project(**witness, corrected=True)
    require(old["starts"][1] == 0 and new["starts"][1] == 1,
            "reject measured first text scanner capture correction")
    controls += 1
    require(old["ends"][1] == 3 and new["ends"][1] == 3,
            "reject scanner capture end preservation")
    controls += 1
    require(old["starts"][0] == new["starts"][0] == 0
            and old["ends"][0] == new["ends"][0] == 3,
            "reject full scanner match preservation")
    controls += 1
    require(old["lastindex"] == new["lastindex"] == 1,
            "reject scanner branch lastindex preservation")
    controls += 1
    missing = dict(groups=2, active=0, outers=[1, 2],
                   begins=[0, 0, -1], ends=[3, 3, -1], native_last=1)
    result = project(**missing, corrected=True)
    require(result["starts"] == [0, 0, -1],
            "reject existing branch-only scanner fallback")
    controls += 1
    second = dict(groups=2, active=1, outers=[1, 3],
                  begins=[4, -1, -1, 4, 6], ends=[9, -1, -1, 9, 9],
                  native_last=3)
    preserved = project(**second, corrected=True)
    require(preserved["starts"][1] == 6 and preserved["starts"][2] == 4
            and preserved["lastindex"] == 2,
            "reject inactive or second-branch scanner captures")
    controls += 1
    poisoned = (
        dict(witness, groups=0),
        dict(witness, active=4),
        dict(witness, outers=[3, 1]),
        dict(witness, begins=[-1, 0, 1, -1]),
        dict(witness, ends=[-1, 3, 3, -1]),
        dict(witness, native_last=3),
        dict(witness, ends=[3, 3, 0, -1]),
    )
    for values in poisoned:
        try:
            project(**values, corrected=True)
        except FreezeError:
            controls += 1
        else:
            raise FreezeError("accepted malformed synthetic scanner capture")
    for alteration in (
        original + b"\n",
        original.replace(OLD_CAPTURE.encode(), b"", 1),
        original.replace(OLD_CAPTURE.encode(), OLD_CAPTURE.encode() * 2, 1),
    ):
        try:
            derive(alteration)
        except FreezeError:
            controls += 1
        else:
            raise FreezeError("accepted poisoned independent scanner source")
    require(corrected.replace(NEW_CAPTURE.encode(), OLD_CAPTURE.encode(), 1) == original,
            "reject unrelated bridge source mutation")
    controls += 1
    require(corrected.count(b"zig_scanner_project_match(iterator") >= 2,
            "reject shared native search and match capture projection")
    controls += 1
    require(corrected.count(b"#include") == original.count(b"#include"),
            "reject external native dependency")
    controls += 1
    require(corrected.count(b"extern ") == original.count(b"extern "),
            "reject borrowed regular-expression engine entry point")
    controls += 1
    return controls


def verify_history(receipt: bytes, adapter_contract: bytes,
                   v15_contract: bytes) -> None:
    observed = json.loads(receipt)
    require(observed.get("candidate_status") == "FAIL"
            and observed.get("actual_candidate_workers") == 13
            and observed.get("case_execution_denominator") == 31237
            and observed.get("verified_passing_case_count") == 4607
            and observed.get("observed_semantic_mismatch_lower_bound") == 1700
            and observed.get("semantic_mismatch_count") == "NOT MEASURED",
            "reject genuine previous first-party Zig failure")
    rows = observed.get("original_suite_diagnostics")
    require(isinstance(rows, list) and len(rows) == 13,
            "reject changed original scanner suite denominator")
    scanner = next((row for row in rows
                    if row.get("suite") == "scanner_verbose_v1"), None)
    require(scanner is not None and scanner.get("case_execution_denominator") == 2854
            and scanner.get("observed_semantic_mismatch_count") == 620
            and scanner.get("infrastructure_failure") is False,
            "reject lost 620 measured Zig scanner differences")
    unfinished = next((row for row in rows
                       if row.get("suite") == "subinterpreter_v2"), None)
    require(unfinished is not None and unfinished.get("infrastructure_failure") is True
            and unfinished.get("observed_semantic_mismatch_count") == "NOT MEASURED",
            "reject fabricated genuine interpreter completion")
    adapter = json.loads(adapter_contract)
    require(adapter.get("family") == "zig"
            and adapter.get("source_modeled_corrected_case_count") == 312
            and adapter.get("source_modeled_remaining_measured_failures") == 1388
            and adapter.get("candidate_correctness") == "NOT RUN",
            "reject independently frozen Zig public adapter lineage")
    future = json.loads(v15_contract)
    require(future.get("family") == "zig"
            and future.get("original_oracle", {}).get("case_execution_denominator") == 31237,
            "reject independently frozen first-party original campaign")


def allowed(options: argparse.Namespace) -> set[str]:
    paths = {
        SELF, PROTOCOL, BRIDGE, ENGINE, RECEIPT,
        ADAPTER_SOURCE, ADAPTER_PROTOCOL, ADAPTER_CONTRACT,
        V15_SOURCE, V15_PROTOCOL, V15_CONTRACT,
    }
    if options.contract_sha256:
        paths.add(CONTRACT)
    return paths


def build(options: argparse.Namespace, *, run_self_test: bool) -> dict[str, object]:
    with SourceWall(allowed(options)):
        source = read_owner(SELF, options.source_sha256, options.source_bytes)
        protocol = read_owner(PROTOCOL, options.protocol_sha256)
        original = read_owner(BRIDGE, options.bridge_sha256, options.bridge_bytes)
        engine = read_owner(ENGINE, options.engine_sha256, options.engine_bytes)
        receipt = read_owner(RECEIPT, options.receipt_sha256)
        adapter_source = read_owner(ADAPTER_SOURCE, options.adapter_source_sha256)
        adapter_protocol = read_owner(ADAPTER_PROTOCOL, options.adapter_protocol_sha256)
        adapter_contract = read_owner(ADAPTER_CONTRACT, options.adapter_contract_sha256)
        v15_source = read_owner(V15_SOURCE, options.v15_source_sha256)
        v15_protocol = read_owner(V15_PROTOCOL, options.v15_protocol_sha256)
        v15_contract = read_owner(V15_CONTRACT, options.v15_contract_sha256)
        verify_history(receipt, adapter_contract, v15_contract)
        corrected = derive(original)
        if options.variant_sha256 is not None:
            require(digest(corrected) == options.variant_sha256,
                    "reject caller-pinned first-party scanner correction")
        if options.variant_bytes is not None:
            require(len(corrected) == options.variant_bytes,
                    "reject caller-pinned scanner source size")
        require(not os.path.lexists(absolute(TARGET)),
                "reject already materialized Zig scanner correction")
        controls = self_test(original, corrected)
        contract = {
            "schema": "rebar-owned-zig-scanner-capture-semantics-v1-source-freeze",
            "status": "SOURCE FROZEN; NATIVE BUILD AND CANDIDATE NOT RUN",
            "family": "zig",
            "source": {"path": SELF, "sha256": digest(source), "bytes": len(source)},
            "protocol": {"path": PROTOCOL, "sha256": digest(protocol),
                         "bytes": len(protocol)},
            "original_bridge": {"path": BRIDGE, "sha256": digest(original),
                                "bytes": len(original)},
            "independent_zig_engine": {"path": ENGINE, "sha256": digest(engine),
                                       "bytes": len(engine)},
            "prospective_variant": {"path": TARGET, "sha256": digest(corrected),
                                    "bytes": len(corrected),
                                    "physical_status": "NOT MATERIALIZED"},
            "defect": {
                "function": "zig_scanner_project_match",
                "actual_text_capture": "#ab",
                "expected_text_capture": "ab",
                "actual_bytes_capture_hex": "236162",
                "expected_bytes_capture_hex": "6162",
                "changed_native_source_block_count": 1,
                "preserve_existing_inner_capture": True,
                "preserve_branch_only_outer_capture": True,
                "preserve_scanner_lastindex": True,
            },
            "original_oracle": {
                "case_execution_denominator": 31237,
                "suite_count": 13,
                "historical_verified_passing_cases": 4607,
                "historical_measured_mismatches": 1700,
                "historical_complete_mismatch_count": "NOT MEASURED",
                "scanner_suite_cases": 2854,
                "scanner_suite_mismatches": 620,
                "scanner_text_mismatches": 310,
                "scanner_bytes_mismatches": 310,
                "unfinished_subinterpreter_cases": 128,
                "historical_mismatch_groups": FAILURES,
            },
            "source_modeled_scanner_corrections": 620,
            "source_modeled_standalone_remaining_measured_failures": 1080,
            "source_modeled_combined_public_adapter_corrections": 932,
            "source_modeled_combined_remaining_measured_failures": 768,
            "modeled_results_are_actual_runs": False,
            "candidate_correctness": "NOT RUN",
            "candidate_qualified": False,
            "native_engine_changed": False,
            "native_bridge_built": False,
            "cross_candidate_engine_used": False,
            "stdlib_regex_engine_used": False,
            "external_regex_package_used": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "source_only_effects": {key: 0 for key in ZERO_EFFECTS},
            "source_only_self_test_control_count": controls,
            "frozen_authority": {
                "v13_failure_receipt": digest(receipt),
                "public_adapter_source": digest(adapter_source),
                "public_adapter_protocol": digest(adapter_protocol),
                "public_adapter_contract": digest(adapter_contract),
                "v15_source": digest(v15_source),
                "v15_protocol": digest(v15_protocol),
                "v15_contract": digest(v15_contract),
            },
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if options.contract_sha256:
            require(read_owner(CONTRACT, options.contract_sha256)
                    == canonical(contract),
                    "reject complete first-party scanner correction contract")
        if run_self_test:
            require(self_test(original, corrected) == controls,
                    "reject unstable adversarial scanner controls")
    contract["_candidate_bytes"] = corrected
    return contract


def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--apply", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", type=int, required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--bridge-sha256", required=True)
    parser.add_argument("--bridge-bytes", type=int, required=True)
    parser.add_argument("--engine-sha256", required=True)
    parser.add_argument("--engine-bytes", type=int, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--adapter-source-sha256", required=True)
    parser.add_argument("--adapter-protocol-sha256", required=True)
    parser.add_argument("--adapter-contract-sha256", required=True)
    parser.add_argument("--v15-source-sha256", required=True)
    parser.add_argument("--v15-protocol-sha256", required=True)
    parser.add_argument("--v15-contract-sha256", required=True)
    parser.add_argument("--variant-sha256")
    parser.add_argument("--variant-bytes", type=int)
    options = parser.parse_args()
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == absolute(SELF),
            "use isolated, bytecode-disabled pinned CPython 3.14.6")
    require(options.bridge_sha256 == BRIDGE_SHA256
            and options.bridge_bytes == BRIDGE_BYTES
            and options.engine_sha256 == ENGINE_SHA256
            and options.engine_bytes == ENGINE_BYTES
            and options.receipt_sha256 == RECEIPT_SHA256
            and options.adapter_source_sha256 == ADAPTER_SOURCE_SHA256
            and options.adapter_protocol_sha256 == ADAPTER_PROTOCOL_SHA256
            and options.adapter_contract_sha256 == ADAPTER_CONTRACT_SHA256
            and options.v15_source_sha256 == V15_SOURCE_SHA256
            and options.v15_protocol_sha256 == V15_PROTOCOL_SHA256
            and options.v15_contract_sha256 == V15_CONTRACT_SHA256,
            "reject changed independent scanner history or first-party lineage")
    if not options.render_contract:
        require(options.contract_sha256 is not None
                and options.variant_sha256 is not None
                and options.variant_bytes is not None,
                "reject unpinned complete first-party scanner freeze")
    return options


def apply_variant(options: argparse.Namespace, corrected: bytes) -> dict[str, object]:
    require(options.apply, "reject unrequested scanner source publication")
    destination = absolute(TARGET)
    directory = os.path.dirname(destination)
    parent = os.path.dirname(directory)
    metadata = os.lstat(parent)
    require(stat.S_ISDIR(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
            and not os.path.lexists(directory)
            and not os.path.lexists(destination),
            "reject preexisting or unowned Zig scanner destination")
    os.mkdir(directory, 0o700)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_CLOEXEC", 0), 0o600)
    try:
        position = 0
        while position < len(corrected):
            written = os.write(descriptor, corrected[position:])
            require(written > 0, "reject interrupted scanner source publication")
            position += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    directory_descriptor = os.open(directory, os.O_RDONLY
                                   | getattr(os, "O_DIRECTORY", 0)
                                   | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)
    observed = read_owner(TARGET, options.variant_sha256, options.variant_bytes)
    require(observed == corrected,
            "reject nonidentical materialized first-party scanner bridge")
    return {
        "schema": "rebar-owned-zig-scanner-capture-semantics-v1-application",
        "status": "PASS; NATIVE SOURCE MATERIALIZED ONLY",
        "family": "zig",
        "target": TARGET,
        "source_sha256": digest(observed),
        "source_bytes": len(observed),
        "original_case_execution_denominator": 31237,
        "historical_measured_mismatches": 1700,
        "source_modeled_scanner_corrections": 620,
        "source_modeled_combined_remaining_measured_failures": 768,
        "native_build": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def main() -> int:
    try:
        options = parse()
        contract = build(options, run_self_test=options.self_test)
        candidate = contract.pop("_candidate_bytes")
        if options.apply:
            result = apply_variant(options, candidate)
        elif options.render_contract:
            result = contract
        else:
            result = {
                "status": "PASS",
                "mode": "self-test" if options.self_test else "verify-frozen-context",
                "source_sha256": options.source_sha256,
                "contract_sha256": options.contract_sha256,
                "prospective_variant_sha256": digest(candidate),
                "prospective_variant_bytes": len(candidate),
                "synthetic_control_count": contract["source_only_self_test_control_count"],
                "source_only_effects": {key: 0 for key in ZERO_EFFECTS},
                "native_build": "NOT RUN",
                "candidate_matching": "NOT RUN",
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            }
        print(canonical(result).decode(), end="")
        return 0
    except (FreezeError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("first-party Zig scanner source rejected: "
              + type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
