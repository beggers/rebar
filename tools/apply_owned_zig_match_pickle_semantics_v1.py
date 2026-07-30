#!/usr/bin/env python3
"""Freeze first-party Zig scanner and legacy-match-pickling corrections."""

from __future__ import annotations

import argparse
import copyreg
import hashlib
import json
import os
import pickle
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/apply_owned_zig_match_pickle_semantics_v1.py"
PROTOCOL = "oracle/phase2/ZIG-MATCH-PICKLE-SEMANTICS-V1.md"
CONTRACT = "oracle/phase2/zig-match-pickle-semantics-v1.json"
BRIDGE = "candidates/zig/py_bridge.c"
BRIDGE_SHA256 = "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b"
BRIDGE_BYTES = 173026
ENGINE = "candidates/zig/mini_regex.zig"
ENGINE_SHA256 = "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28"
ENGINE_BYTES = 186915
SCANNER_SOURCE = "tools/apply_owned_zig_scanner_capture_semantics_v1.py"
SCANNER_SOURCE_SHA256 = "155183987fbc30f716b315d41ddfc9dddf0356c065177de4661198bdc60b85ad"
SCANNER_PROTOCOL = "oracle/phase2/ZIG-SCANNER-CAPTURE-SEMANTICS-V1.md"
SCANNER_PROTOCOL_SHA256 = "48de77e626818bc75ff451e225e1c895445d9ca29b91b59778543c9847032947"
SCANNER_CONTRACT = "oracle/phase2/zig-scanner-capture-semantics-v1.json"
SCANNER_CONTRACT_SHA256 = "fe43d924d74c2bfe1dac5d7e1f936a1975bb53461a7bb73394841e8934ecb27c"
SCANNER_BRIDGE_SHA256 = "a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148"
SCANNER_BRIDGE_BYTES = 173082
ADAPTER_SOURCE = "tools/apply_owned_zig_public_adapter_semantics_v1.py"
ADAPTER_SOURCE_SHA256 = "14ffb1f8a8fc611a64ad307e4e5c86c17a635d2dc0b509c1a0c2eb60d3a75782"
ADAPTER_PROTOCOL = "oracle/phase2/ZIG-PUBLIC-ADAPTER-SEMANTICS-V1.md"
ADAPTER_PROTOCOL_SHA256 = "db81ccb98ccc018f8bec21f6e37ed33f3829be92ce435ba0f5198db28e655226"
ADAPTER_CONTRACT = "oracle/phase2/zig-public-adapter-semantics-v1.json"
ADAPTER_CONTRACT_SHA256 = "26a48a86a9d6d99d138d7e4f44bec5e2ba70c9dd36249305d4733fa9370ee765"
RECEIPT = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13-"
    "failures-publication-receipt.json"
)
RECEIPT_SHA256 = "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca"
TARGET = "candidates/zig/variants/match_pickle_semantics_v1/py_bridge.c"

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
OLD_REDUCER = (
    "static PyObject *zig_match_reduce(ZigMatch *match, PyObject *ignored) "
    "{ (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError, "
    "\"cannot pickle 're.Match' object\"); return NULL; }\n"
)
NEW_REDUCER = OLD_REDUCER + (
    "static PyObject *zig_match_reduce_ex(ZigMatch *match, PyObject *protocol) {\n"
    "    Py_ssize_t version = PyLong_AsSsize_t(protocol);\n"
    "    if (version == -1 && PyErr_Occurred()) return NULL;\n"
    "    if (version < 0 || version >= 2) {\n"
    "        return zig_match_reduce(match, NULL);\n"
    "    }\n"
    "    PyObject *registry = PyImport_ImportModule(\"copyreg\");\n"
    "    if (registry == NULL) return NULL;\n"
    "    PyObject *reconstructor = PyObject_GetAttrString(\n"
    "        registry, \"_reconstructor\");\n"
    "    Py_DECREF(registry);\n"
    "    if (reconstructor == NULL) return NULL;\n"
    "    PyObject *arguments = PyTuple_Pack(\n"
    "        3, (PyObject *)Py_TYPE(match),\n"
    "        (PyObject *)&PyBaseObject_Type, Py_None);\n"
    "    if (arguments == NULL) {\n"
    "        Py_DECREF(reconstructor);\n"
    "        return NULL;\n"
    "    }\n"
    "    PyObject *reduction = PyTuple_Pack(2, reconstructor, arguments);\n"
    "    Py_DECREF(reconstructor);\n"
    "    Py_DECREF(arguments);\n"
    "    return reduction;\n"
    "}\n"
)
OLD_REDUCER_METHOD = (
    "    {\"__reduce_ex__\", (PyCFunction)zig_match_reduce, METH_O, "
    "\"Matches cannot be pickled.\"},\n"
)
NEW_REDUCER_METHOD = (
    "    {\"__reduce_ex__\", (PyCFunction)zig_match_reduce_ex, METH_O, "
    "\"Return the Python-compatible protocol-specific match reduction.\"},\n"
)
ZERO_EFFECTS = (
    "candidate_imports", "candidate_processes", "candidate_matching_calls",
    "native_library_loads", "native_builds", "archive_opens", "holdout_opens",
    "benchmark_opens", "seed_opens", "private_root_opens", "files_written",
    "canonical_targets_changed", "subinterpreters_created", "reference_workers",
    "compiler_processes", "clock_samples",
)


class FreezeError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def absolute(relative: str) -> str:
    require(type(relative) is str and relative and not relative.startswith("/")
            and ".." not in relative.split("/"),
            "reject unowned or traversing Zig pickle input")
    return os.path.join(ROOT, relative)


class SourceWall:
    def __init__(self, owners: set[str]):
        self.owners = {absolute(owner) for owner in owners}
        self.active = False

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if not self.active:
            return
        if event == "open":
            require(len(arguments) == 3 and type(arguments[0]) is str
                    and arguments[0] in self.owners
                    and arguments[1] in (None, "r", "rb")
                    and type(arguments[2]) is int
                    and arguments[2] & os.O_ACCMODE == os.O_RDONLY
                    and arguments[2] & (os.O_CREAT | os.O_APPEND | os.O_TRUNC) == 0,
                    "pickle source wall rejected unowned or mutable open")
            return
        if event == "import":
            name = arguments[0] if arguments else ""
            banned = ("candidates", "re", "_sre", "regex", "ctypes", "inspect")
            require(not any(name == item or name.startswith(item + ".")
                            for item in banned),
                    "pickle source wall rejected matching engine import")
            return
        banned_events = (
            "subprocess.", "socket.", "ctypes.", "_posixsubprocess.",
            "os.mkdir", "os.rmdir", "os.remove", "os.rename", "os.replace",
            "os.unlink", "os.chmod", "os.chown", "os.system", "os.putenv",
            "os.posix_spawn", "os.fork", "os.exec", "threading.",
        )
        require(not event.startswith(banned_events),
                "pickle source wall rejected external action " + event)

    def __enter__(self) -> "SourceWall":
        sys.addaudithook(self.audit)
        self.active = True
        return self

    def __exit__(self, kind: object, value: object, traceback: object) -> None:
        self.active = False


def read_owner(path: str, identity: str | None = None,
               length: int | None = None) -> bytes:
    descriptor = os.open(absolute(path), os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        metadata = os.fstat(descriptor)
        require(stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1
                and metadata.st_uid == os.getuid()
                and metadata.st_size <= 1024 * 1024,
                "reject nonowned first-party Zig pickle input " + path)
        if length is not None:
            require(metadata.st_size == length,
                    "reject first-party Zig pickle input length " + path)
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    value = b"".join(chunks)
    if identity is not None:
        require(digest(value) == identity,
                "reject first-party Zig pickle input digest " + path)
    return value


def replace_once(value: bytes, old: str, new: str, label: str) -> bytes:
    before = old.encode()
    after = new.encode()
    require(value.count(before) == 1,
            "reject missing or duplicated owned bridge block " + label)
    return value.replace(before, after, 1)


def derive(original: bytes) -> tuple[bytes, bytes]:
    require(len(original) == BRIDGE_BYTES and digest(original) == BRIDGE_SHA256,
            "reject original first-party Zig native binding")
    scanner = replace_once(original, OLD_CAPTURE, NEW_CAPTURE, "scanner capture")
    require(len(scanner) == SCANNER_BRIDGE_BYTES
            and digest(scanner) == SCANNER_BRIDGE_SHA256,
            "reject independently frozen exact Zig scanner source")
    corrected = replace_once(scanner, OLD_REDUCER, NEW_REDUCER,
                             "protocol-specific match reduction")
    corrected = replace_once(corrected, OLD_REDUCER_METHOD, NEW_REDUCER_METHOD,
                             "protocol-specific native method registration")
    rollback = corrected.replace(NEW_REDUCER_METHOD.encode(),
                                 OLD_REDUCER_METHOD.encode(), 1)
    rollback = rollback.replace(NEW_REDUCER.encode(), OLD_REDUCER.encode(), 1)
    require(rollback == scanner,
            "reject unrelated Zig native bridge changes")
    require(corrected.count(b"PyImport_ImportModule(\"copyreg\")") == 1,
            "reject missing ordinary Python serialization helper")
    for forbidden in (
        b"PyImport_ImportModule(\"re\")",
        b"PyImport_ImportModule(\"_sre\")",
        b"PyImport_ImportModule(\"regex\")",
        b"PyImport_ImportModule(\"candidates.",
    ):
        require(forbidden not in corrected,
                "reject borrowed Python or candidate regular-expression engine")
    return scanner, corrected


class SyntheticMatch:
    def __reduce__(self):
        raise TypeError("cannot pickle 're.Match' object")

    def __reduce_ex__(self, protocol):
        if protocol < 0 or protocol >= 2:
            return self.__reduce__()
        return copyreg._reconstructor, (type(self), object, None)


def self_test(original: bytes, scanner: bytes, corrected: bytes) -> int:
    controls = 0
    value = SyntheticMatch()
    for protocol in (0, 1):
        reduction = value.__reduce_ex__(protocol)
        require(type(reduction) is tuple and len(reduction) == 2
                and reduction[0] is copyreg._reconstructor
                and reduction[1] == (SyntheticMatch, object, None),
                "reject genuine legacy Python match reduction")
        payload = pickle.dumps(value, protocol=protocol)
        require(isinstance(payload, bytes)
                and b"_reconstructor" in payload
                and b"SyntheticMatch" in payload,
                "reject genuine protocol-zero or protocol-one pickle")
        controls += 2
    for protocol in (-1, 2, 3, 4, 5):
        try:
            value.__reduce_ex__(protocol)
        except TypeError as error:
            require(str(error) == "cannot pickle 're.Match' object",
                    "reject preserved modern protocol error")
            controls += 1
        else:
            raise FreezeError("accepted unsupported modern match pickle")
    try:
        value.__reduce__()
    except TypeError:
        controls += 1
    else:
        raise FreezeError("relaxed direct native match reduction")
    for altered in (
        original + b"\n",
        original.replace(OLD_CAPTURE.encode(), b"", 1),
        original.replace(OLD_REDUCER.encode(), b"", 1),
        original.replace(OLD_REDUCER_METHOD.encode(), b"", 1),
    ):
        try:
            derive(altered)
        except FreezeError:
            controls += 1
        else:
            raise FreezeError("accepted poisoned first-party Zig bridge")
    require(scanner.count(NEW_CAPTURE.encode()) == 1,
            "reject lost separately corrected scanner projection")
    controls += 1
    require(corrected.count(NEW_CAPTURE.encode()) == 1,
            "reject lost composed scanner projection")
    controls += 1
    require(corrected.count(NEW_REDUCER_METHOD.encode()) == 1
            and corrected.count(OLD_REDUCER_METHOD.encode()) == 0,
            "reject stale protocol-independent native reduction")
    controls += 1
    require(corrected.count(b"#include") == scanner.count(b"#include"),
            "reject added native regex package include")
    controls += 1
    require(corrected.count(b"extern ") == scanner.count(b"extern "),
            "reject borrowed matching engine entry point")
    controls += 1
    return controls


def verify_history(receipt: bytes, scanner_contract: bytes,
                   adapter_contract: bytes) -> None:
    observed = json.loads(receipt)
    require(observed.get("candidate_status") == "FAIL"
            and observed.get("case_execution_denominator") == 31237
            and observed.get("actual_candidate_workers") == 13
            and observed.get("verified_passing_case_count") == 4607
            and observed.get("observed_semantic_mismatch_lower_bound") == 1700
            and observed.get("semantic_mismatch_count") == "NOT MEASURED",
            "reject observed original Zig campaign")
    rows = observed.get("original_suite_diagnostics")
    require(isinstance(rows, list) and len(rows) == 13,
            "reject original candidate suite denominator")
    public = next((row for row in rows if row.get("suite") == "public_types_v1"), None)
    require(public is not None and public.get("case_execution_denominator") == 6912
            and public.get("observed_semantic_mismatch_count") == 248,
            "reject actual Zig public-type failure group")
    scanner = json.loads(scanner_contract)
    require(scanner.get("source_modeled_scanner_corrections") == 620
            and scanner.get("prospective_variant", {}).get("sha256")
                   == SCANNER_BRIDGE_SHA256,
            "reject separately frozen Zig scanner correction")
    adapter = json.loads(adapter_contract)
    require(adapter.get("source_modeled_corrected_case_count") == 312
            and adapter.get("preserved_public_failures", {}).get("pickle-match-rejection") == 32,
            "reject independently preserved Zig pickle failures")


def owners(options: argparse.Namespace) -> set[str]:
    result = {
        SELF, PROTOCOL, BRIDGE, ENGINE, RECEIPT,
        SCANNER_SOURCE, SCANNER_PROTOCOL, SCANNER_CONTRACT,
        ADAPTER_SOURCE, ADAPTER_PROTOCOL, ADAPTER_CONTRACT,
    }
    if options.contract_sha256:
        result.add(CONTRACT)
    return result


def build(options: argparse.Namespace, *, run_self_test: bool) -> dict[str, object]:
    with SourceWall(owners(options)):
        source = read_owner(SELF, options.source_sha256, options.source_bytes)
        protocol = read_owner(PROTOCOL, options.protocol_sha256)
        original = read_owner(BRIDGE, options.bridge_sha256, options.bridge_bytes)
        engine = read_owner(ENGINE, options.engine_sha256, options.engine_bytes)
        receipt = read_owner(RECEIPT, options.receipt_sha256)
        scanner_source = read_owner(SCANNER_SOURCE, options.scanner_source_sha256)
        scanner_protocol = read_owner(SCANNER_PROTOCOL, options.scanner_protocol_sha256)
        scanner_contract = read_owner(SCANNER_CONTRACT, options.scanner_contract_sha256)
        adapter_source = read_owner(ADAPTER_SOURCE, options.adapter_source_sha256)
        adapter_protocol = read_owner(ADAPTER_PROTOCOL, options.adapter_protocol_sha256)
        adapter_contract = read_owner(ADAPTER_CONTRACT, options.adapter_contract_sha256)
        verify_history(receipt, scanner_contract, adapter_contract)
        scanner, corrected = derive(original)
        if options.variant_sha256 is not None:
            require(digest(corrected) == options.variant_sha256,
                    "reject pinned Zig scanner and pickle bridge")
        if options.variant_bytes is not None:
            require(len(corrected) == options.variant_bytes,
                    "reject pinned Zig scanner and pickle bridge size")
        require(not os.path.lexists(absolute(TARGET)),
                "reject materialized Zig match-pickle correction")
        controls = self_test(original, scanner, corrected)
        result = {
            "schema": "rebar-owned-zig-match-pickle-semantics-v1-source-freeze",
            "status": "SOURCE FROZEN; NATIVE BUILD AND CANDIDATE NOT RUN",
            "family": "zig",
            "source": {"path": SELF, "sha256": digest(source), "bytes": len(source)},
            "protocol": {"path": PROTOCOL, "sha256": digest(protocol),
                         "bytes": len(protocol)},
            "original_bridge": {"path": BRIDGE, "sha256": digest(original),
                                "bytes": len(original)},
            "independent_zig_engine": {"path": ENGINE, "sha256": digest(engine),
                                       "bytes": len(engine)},
            "independently_derived_scanner_bridge": {
                "sha256": digest(scanner), "bytes": len(scanner),
                "physical_target_opened": False,
                "source_modeled_scanner_corrections": 620,
            },
            "prospective_variant": {"path": TARGET, "sha256": digest(corrected),
                                    "bytes": len(corrected),
                                    "physical_status": "NOT MATERIALIZED"},
            "legacy_match_reduction": {
                "protocol_zero_observed_failures": 16,
                "protocol_one_observed_failures": 16,
                "protocol_zero_or_one_corrections": 32,
                "protocol_two_and_higher_rejection_preserved": True,
                "direct_reduce_rejection_preserved": True,
                "helper": "copyreg._reconstructor",
                "helper_is_a_regex_engine": False,
                "reconstructor_arguments": ["type(match)", "object", None],
            },
            "original_oracle": {
                "case_execution_denominator": 31237,
                "suite_count": 13,
                "historical_verified_passing_cases": 4607,
                "historical_measured_mismatches": 1700,
                "historical_complete_mismatch_count": "NOT MEASURED",
                "unfinished_subinterpreter_cases": 128,
            },
            "source_modeled_scanner_and_pickle_corrections": 652,
            "source_modeled_scanner_and_pickle_remaining_measured_failures": 1048,
            "source_modeled_combined_public_adapter_corrections": 964,
            "source_modeled_combined_remaining_measured_failures": 736,
            "remaining_original_failures": {
                "substitution_v2": 64,
                "shape_v2": 672,
            },
            "modeled_results_are_actual_runs": False,
            "candidate_correctness": "NOT RUN",
            "candidate_qualified": False,
            "native_engine_changed": False,
            "native_bridge_built": False,
            "cross_candidate_engine_used": False,
            "stdlib_regex_engine_used": False,
            "external_regex_package_used": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "source_only_effects": {name: 0 for name in ZERO_EFFECTS},
            "source_only_self_test_control_count": controls,
            "frozen_authority": {
                "v13_failure_receipt": digest(receipt),
                "scanner_source": digest(scanner_source),
                "scanner_protocol": digest(scanner_protocol),
                "scanner_contract": digest(scanner_contract),
                "public_adapter_source": digest(adapter_source),
                "public_adapter_protocol": digest(adapter_protocol),
                "public_adapter_contract": digest(adapter_contract),
            },
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        if options.contract_sha256:
            require(read_owner(CONTRACT, options.contract_sha256) == canonical(result),
                    "reject complete composed Zig match-pickle contract")
        if run_self_test:
            require(self_test(original, scanner, corrected) == controls,
                    "reject unstable synthetic legacy serialization controls")
    result["_candidate_bytes"] = corrected
    return result


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
    parser.add_argument("--scanner-source-sha256", required=True)
    parser.add_argument("--scanner-protocol-sha256", required=True)
    parser.add_argument("--scanner-contract-sha256", required=True)
    parser.add_argument("--adapter-source-sha256", required=True)
    parser.add_argument("--adapter-protocol-sha256", required=True)
    parser.add_argument("--adapter-contract-sha256", required=True)
    parser.add_argument("--variant-sha256")
    parser.add_argument("--variant-bytes", type=int)
    options = parser.parse_args()
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == absolute(SELF),
            "use pinned isolated bytecode-disabled CPython 3.14.6 only")
    require(options.bridge_sha256 == BRIDGE_SHA256
            and options.bridge_bytes == BRIDGE_BYTES
            and options.engine_sha256 == ENGINE_SHA256
            and options.engine_bytes == ENGINE_BYTES
            and options.receipt_sha256 == RECEIPT_SHA256
            and options.scanner_source_sha256 == SCANNER_SOURCE_SHA256
            and options.scanner_protocol_sha256 == SCANNER_PROTOCOL_SHA256
            and options.scanner_contract_sha256 == SCANNER_CONTRACT_SHA256
            and options.adapter_source_sha256 == ADAPTER_SOURCE_SHA256
            and options.adapter_protocol_sha256 == ADAPTER_PROTOCOL_SHA256
            and options.adapter_contract_sha256 == ADAPTER_CONTRACT_SHA256,
            "reject incomplete independently frozen Zig source authority")
    if not options.render_contract:
        require(options.contract_sha256 is not None
                and options.variant_sha256 is not None
                and options.variant_bytes is not None,
                "reject incomplete Zig match-pickle freeze pins")
    return options


def publish(options: argparse.Namespace, corrected: bytes) -> dict[str, object]:
    require(options.apply, "reject unrequested Zig bridge publication")
    destination = absolute(TARGET)
    directory = os.path.dirname(destination)
    parent = os.path.dirname(directory)
    parent_owner = os.lstat(parent)
    require(stat.S_ISDIR(parent_owner.st_mode)
            and not stat.S_ISLNK(parent_owner.st_mode)
            and not os.path.lexists(directory)
            and not os.path.lexists(destination),
            "reject foreign or existing Zig match-pickle destination")
    os.mkdir(directory, 0o700)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        offset = 0
        while offset < len(corrected):
            count = os.write(descriptor, corrected[offset:])
            require(count > 0, "reject interrupted Zig native-source publication")
            offset += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    owner = os.open(directory, os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_CLOEXEC", 0))
    try:
        os.fsync(owner)
    finally:
        os.close(owner)
    require(read_owner(TARGET, options.variant_sha256, options.variant_bytes)
            == corrected, "reject changed materialized Zig match pickle source")
    return {
        "schema": "rebar-owned-zig-match-pickle-semantics-v1-application",
        "status": "PASS; NATIVE SOURCE MATERIALIZED ONLY",
        "family": "zig",
        "target": TARGET,
        "source_sha256": digest(corrected),
        "source_bytes": len(corrected),
        "original_case_execution_denominator": 31237,
        "historical_measured_mismatches": 1700,
        "source_modeled_scanner_and_pickle_corrections": 652,
        "source_modeled_combined_remaining_measured_failures": 736,
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
            result = publish(options, candidate)
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
    except (FreezeError, OSError, ValueError, KeyError, json.JSONDecodeError,
            pickle.PickleError) as error:
        print("first-party Zig match-pickle correction rejected: "
              + type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
