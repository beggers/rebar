#!/usr/bin/env python3
"""Freeze and separately authorize the first-party C Match V19 native build."""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/reproduce_owned_c_original_match_semantics_source_build_v19.py"
PROTOCOL = "oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V19.md"
CONTRACT = "oracle/phase2/c-original-match-semantics-source-build-v19.json"
SCHEMA = "rebar-owned-c-original-match-semantics-source-build-v19"
VERSION = 19
FAMILY = "c"
LABEL = "phase2-v19-c-original-match-semantics-source-build"
DEVICE = 2064
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_TOOL_BYTES = 64 * 1024 * 1024
MAX_PROCESS_OUTPUT = 4 * 1024 * 1024
ORIGINAL_CASE_COUNT = 31237
REFERENCE_CASE_COUNT = 8244
PRIVATE_WAIVER_COUNT = 13
PROPOSED_HOLDOUT_CASE_COUNT = 14155776
DERIVED_SHA256 = (
    "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
)
DERIVED_BYTES = 221647
BASE_VARIANT_SHA256 = (
    "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
)
ROOT_PREFIX = "rebar-phase2-c-original-match-semantics-v19-"
PHASES = ("reference-a", "reference-b")
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
NATIVE_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
BUILD_AUTHORIZATION = "--authorize-first-party-native-build-v19"
SEMANTICS = (
    ("tools/apply_owned_c_original_match_semantics_v1.py",
     "e2a67d418ab531a93bb2f894844a256460ba7fde70a6e1f6fb2ae82eba63b1c6",
     49528, 431406),
    ("oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-V1.md",
     "a71e397d87ecd538ee8a1eb218a6dbdf68849cc9598c208ddc83066dc9aec7b9",
     6310, 525326),
    ("oracle/phase2/c-original-match-semantics-v1.json",
     "6a7a53c77bd20664fed15a61d5ad5c1d7ae5354405e99e8d72427d44ab9f134c",
     14770, 525329),
)
C18 = (
    ("tools/reproduce_owned_c_subject_buffer_source_build_v18.py",
     "bf50ac15a7fdc7633e5804da066a77ee1342540228245cd33a5d977bfdfdc339",
     122194, 430336),
    ("oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V18.md",
     "97ab6a9881e2e2cf7c779660459adb00f7bb9e6db5e5b63da5c75d00f250c5aa",
     10389, 524789),
    ("oracle/phase2/c-subject-buffer-source-build-v18.json",
     "aa68e0da13d666ea02565fe5aed347d5a34150e768df70fc5acc4a1e594b1a6a",
     17921, 524797),
)
C18_BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-"
    "c-subject-buffer-root-provenance-publication-receipt.json",
    "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae",
    4713, 524898,
)
C18_ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-"
    "c-subject-buffer-root-provenance-root-provenance-receipt.json",
    "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8",
    7629, 524899,
)
CANONICAL_C = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185, 428072,
)
CANONICAL_ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707, 428074,
)
EXPECTED_INSTALLED_NATIVE_SHA256 = (
    "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
)
TOOLCHAINS = (
    ("gcc", "/usr/bin/x86_64-linux-gnu-gcc-13",
     "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
     1023032, "GCC 13", True),
    ("python", PYTHON,
     "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
     32387816, "CPython 3.14.6", True),
    ("python_header",
     "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
     "include/python3.14/Python.h",
     "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
     4399, "CPython 3.14.6", False),
    ("python_patchlevel",
     "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
     "include/python3.14/patchlevel.h",
     "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
     1773, "CPython 3.14.6", False),
    ("readelf", "/usr/bin/x86_64-linux-gnu-readelf",
     "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
     789280, "GNU readelf", True),
)


class BuildError(Exception):
    """Frozen provenance, build authority, or native reproducibility failed."""


def need(condition: object, message: str) -> None:
    if not condition:
        raise BuildError(message)


def exact_digest(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require an independently pinned SHA-256: " + role)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "require independently pinned CPython 3.14.6 -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules and "ctypes" not in sys.modules
         and "subprocess" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "reject a preloaded matcher, candidate, native loader, "
         "external package, or subprocess wrapper")


def read_bootstrap(owner: tuple) -> bytes:
    relative, fingerprint, count, inode = owner
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and "holdout" not in relative.lower()
         and "benchmark" not in relative.lower()
         and not relative.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
         and type(count) is int and 0 < count <= MAX_SOURCE_BYTES
         and type(inode) is int and inode > 0,
         "reject an archive, live native, private root, or unbounded bootstrap")
    exact_digest(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable first-party owner: " + relative)
        pieces = []
        remaining = count
        while remaining:
            item = os.read(descriptor, min(remaining, 262144))
            need(bool(item), "reject a truncated bootstrap: " + relative)
            pieces.append(item)
            remaining -= len(item)
        need(not os.read(descriptor, 1),
             "reject extra immutable source bytes: " + relative)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed complete frozen source bytes: " + relative)
        return raw
    finally:
        os.close(descriptor)


def bootstrap_wall() -> tuple[types.ModuleType, types.ModuleType, tuple, tuple]:
    clean_runtime()
    raw = read_bootstrap(SEMANTICS[0])
    semantic = types.ModuleType("_rebar_c_v19_frozen_original_match_semantics")
    semantic.__file__ = ROOT + "/" + SEMANTICS[0][0]
    semantic.__package__ = ""
    exec(compile(raw, semantic.__file__, "exec", dont_inherit=True),
         semantic.__dict__)
    need(semantic.SCHEMA == "rebar-owned-c-original-match-semantics-v1"
         and semantic.ORIGINAL_CASE_COUNT == ORIGINAL_CASE_COUNT
         and semantic.REFERENCE_CASE_COUNT == REFERENCE_CASE_COUNT
         and semantic.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
         and semantic.PROPOSED_HOLDOUT_CASE_COUNT == PROPOSED_HOLDOUT_CASE_COUNT
         and len(semantic.EXPECTED_ROWS) == 13,
         "bootstrap only the committed complete first-party C Match source freeze")
    old, semantic_owners = semantic.bootstrap_wall()
    owners = (semantic_owners + SEMANTICS + C18
              + (C18_BUILD_RECEIPT, C18_ROOT_RECEIPT))
    paths = tuple(item[0] for item in owners)
    need(len(paths) == len(frozenset(paths)),
         "reject duplicate frozen C V19 source-owner identities")
    old.SOURCE, old.PROTOCOL, old.CONTRACT = SOURCE, PROTOCOL, CONTRACT
    old.STATIC_OWNERS = owners
    old.OWNED_PATHS = frozenset(paths) | {SOURCE, PROTOCOL, CONTRACT}
    need(not any(path == CANONICAL_C[0] or path == CANONICAL_ADAPTER[0]
                 or path.startswith("docs/evidence/")
                 or "holdout" in path.lower() or "benchmark" in path.lower()
                 or path.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
                 for path in old.OWNED_PATHS),
         "the V19 physical source wall must deny current candidates, installed "
         "native files, graphs, archives, roots, benchmarks, and holdouts")
    clean_runtime()
    return semantic, old, semantic_owners, owners


def record(owner: tuple) -> dict:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2],
            "device": DEVICE, "inode": owner[3], "mode": "0600", "nlink": 1}


def document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        observed = producer.JsonReader(raw).parse()
    except Exception as error:
        raise BuildError("reject malformed frozen " + role + ": "
                         + str(error)) from error
    need(type(observed) is dict,
         "require an exact frozen machine document: " + role)
    return observed


def validate_c18_source(raw: bytes) -> None:
    tree = ast.parse(raw, filename=C18[0][0])
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "SCHEMA", "VERSION", "FAMILY", "SOURCE_PATH",
                    "PROTOCOL_PATH", "CONTRACT_PATH", "PHASES", "PROCESS_NAMES",
                    "PYTHON",
                }:
                    values[target.id] = ast.literal_eval(node.value)
    need(values.get("SCHEMA")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18"
         and values.get("VERSION") == 18 and values.get("FAMILY") == FAMILY
         and values.get("SOURCE_PATH") == C18[0][0]
         and values.get("PROTOCOL_PATH") == C18[1][0]
         and values.get("CONTRACT_PATH") == C18[2][0]
         and values.get("PYTHON") == PYTHON
         and values.get("PHASES") == PHASES
         and values.get("PROCESS_NAMES") == PROCESS_ROLES,
         "preserve the independently frozen two-phase, seven-role C18 design "
         "without loading or forwarding its old-variant build")
    need(b"def run_build(" in raw
         and b"def capture_root_descriptor(" in raw
         and b"def publish_root_provenance(" in raw
         and b"C_TOOLCHAINS = {" in raw,
         "require the complete immutable first-party C18 provenance controller")


def validate_c18(c18: dict, build: dict, root: dict) -> None:
    need(c18.get("schema")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18-source-freeze"
         and c18.get("version") == 18
         and c18.get("family") == FAMILY
         and c18.get("source", {}).get("sha256") == C18[0][1]
         and c18.get("protocol", {}).get("sha256") == C18[1][1],
         "authenticate immutable C18 source, protocol, and build contract")
    common = (
        ("version", 18), ("status", "PASS"), ("family", FAMILY),
        ("label", "phase2-v18-c-subject-buffer-root-provenance"),
        ("source_sha256", C18[0][1]),
        ("protocol_sha256", C18[1][1]),
        ("contract_sha256", C18[2][1]),
        ("actual_compiler_process_count", 14),
        ("expected_compiler_process_count", 14),
        ("authenticated_toolchain_owner_count", 5),
        ("toolchain_audit_status", "PASS"),
        ("candidate_correctness", "NOT MEASURED"),
        ("candidate_matching", "NOT RUN"),
        ("native_libraries_loaded", 0),
        ("clock_samples", 0),
        ("hidden_cases_read", 0),
        ("performance", "NOT MEASURED"),
        ("holdout", "NOT OPENED"),
        ("winner_selected", False),
    )
    for key, expected in common:
        need(build.get(key) == expected and root.get(key) == expected,
             "reject actual C18 build/root receipt field: " + key)
    need(build.get("schema")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18-"
            "durable-publication-receipt"
         and build.get("publication_pass_means")
         == "DURABLE BUILD PUBLICATION ONLY"
         and build.get("build_status") == "PASS"
         and build.get("variant_source_sha256") == BASE_VARIANT_SHA256
         and build.get("variant_source_bytes") == 222212
         and build.get("original_source_sha256") == CANONICAL_C[1]
         and build.get("adapter_source_sha256") == CANONICAL_ADAPTER[1]
         and build.get("expected_source_apply_count") == 2
         and build.get("actual_source_apply_count") == 2
         and build.get("candidate_processes_started") == 0
         and build.get("installed_native_read") is False
         and build.get("installed_native_activated") is False
         and build.get("historical_archives_opened") == 0,
         "authenticate the real historical C18 build without claiming it "
         "compiled the newer Match-corrected source")
    need(root.get("schema")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18-"
            "durable-root-provenance-receipt"
         and root.get("publication_pass_means")
         == "DURABLE REPRODUCIBLE FIRST-PARTY C BUILD ROOT PROVENANCE ONLY"
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_sha256")
         == C18_BUILD_RECEIPT[1]
         and root.get("actual_source_phase_count") == 2
         and root.get("distinct_actual_phase_source_owner_count") == 4
         and root.get("distinct_actual_native_extension_count") == 2
         and root.get("subject_buffer_source_overlay_apply_count") == 2
         and root.get("native_source_delegation_audit") == "PASS"
         and root.get("python_adapter_delegation_audit") == "PASS"
         and root.get("candidate_workers_started") == 0
         and root.get("historical_archives_opened") == 0,
         "authenticate the exact real C18 root attestation and build link")
    nested = root.get("root")
    need(type(nested) is dict and nested.get("device") == 2049
         and type(nested.get("inode")) is int and nested["inode"] > 0
         and nested.get("mode") == "0700"
         and nested.get("nofollow_directory_descriptor") is True
         and nested.get("descriptor_opened_during_live_verification") is True
         and nested.get("directory_scanned") is False
         and nested.get("phase_count") == 2
         and nested.get("distinct_source_owner_count") == 4
         and nested.get("distinct_native_owner_count") == 2
         and nested.get("byte_identical_native_output") is True,
         "attest the historical /tmp root from its small receipt only; "
         "never assume workspace device 2064 or open the historical root")
    phases = nested.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require exactly two historical source-attested C18 phases")
    ids = set()
    native_ids = set()
    native_hashes = set()
    for index, phase in enumerate(phases):
        need(type(phase) is dict and phase.get("name") == PHASES[index]
             and phase.get("mode") == "0700"
             and type(phase.get("source_owners")) is list
             and len(phase["source_owners"]) == 2,
             "reject a substituted actual historical C18 private phase")
        for source in phase["source_owners"]:
            need(type(source) is dict and source.get("mode") == "0600"
                 and source.get("nlink") == 1
                 and type(source.get("device")) is int
                 and type(source.get("inode")) is int,
                 "reject an unowned historical source identity")
            pair = source["device"], source["inode"]
            need(pair not in ids,
                 "reject reused historical C18 private source owners")
            ids.add(pair)
        native = phase.get("native_output")
        need(type(native) is dict and native.get("native_loaded") is False
             and native.get("file_name") == NATIVE_NAME
             and native.get("nlink") == 1
             and type(native.get("device")) is int
             and type(native.get("inode")) is int,
             "reject historical native loading or substituted C18 outputs")
        pair = native["device"], native["inode"]
        need(pair not in native_ids,
             "reject borrowed historical C18 native phase artifacts")
        native_ids.add(pair)
        native_hashes.add(exact_digest(native.get("sha256"),
                                      "historical C18 native output"))
    need(len(ids) == 4 and len(native_ids) == 2 and len(native_hashes) == 1,
         "attest historical independent C18 phase owners and identical outputs")


def synthetic_plan() -> dict:
    phases = []
    for index, name in enumerate(PHASES):
        phases.append({
            "synthetic": True, "name": name, "mode": "0700",
            "source_owners": [
                {"synthetic": True, "role": "match-corrected-native-source",
                 "sha256": DERIVED_SHA256, "bytes": DERIVED_BYTES,
                 "device": 2049, "inode": 9001 + 2 * index, "mode": "0600"},
                {"synthetic": True, "role": "unchanged-python-adapter",
                 "sha256": CANONICAL_ADAPTER[1],
                 "bytes": CANONICAL_ADAPTER[2],
                 "device": 2049, "inode": 9002 + 2 * index, "mode": "0600"},
            ],
            "native_output": {
                "synthetic": True, "device": 2049,
                "inode": 9101 + index, "sha256": "0" * 64,
                "native_loaded": False,
            },
        })
    return {"synthetic": True, "phase_count": 2, "phases": phases,
            "processes": [
                {"synthetic": True, "phase": PHASES[index // 7],
                 "role": PROCESS_ROLES[index % 7], "pid": 9201 + index,
                 "exit_status": 0}
                for index in range(14)
            ]}


def validate_synthetic_plan(plan: object) -> dict:
    need(type(plan) is dict and plan.get("synthetic") is True
         and plan.get("phase_count") == 2,
         "reject an actual root or unlabeled synthetic C build plan")
    phases = plan.get("phases")
    processes = plan.get("processes")
    need(type(phases) is list and len(phases) == 2
         and type(processes) is list and len(processes) == 14,
         "require two synthetic phases and fourteen synthetic process roles")
    sources = set()
    natives = set()
    hashes = set()
    pids = set()
    for index, phase in enumerate(phases):
        need(type(phase) is dict and phase.get("synthetic") is True
             and phase.get("name") == PHASES[index]
             and phase.get("mode") == "0700",
             "reject an invented or unowned synthetic build phase")
        items = phase.get("source_owners")
        need(type(items) is list and len(items) == 2,
             "require two independent synthetic C input owners per phase")
        for position, item in enumerate(items):
            expected = (DERIVED_SHA256, DERIVED_BYTES,
                        "match-corrected-native-source") if position == 0 else (
                            CANONICAL_ADAPTER[1], CANONICAL_ADAPTER[2],
                            "unchanged-python-adapter")
            need(type(item) is dict and item.get("synthetic") is True
                 and item.get("sha256") == expected[0]
                 and item.get("bytes") == expected[1]
                 and item.get("role") == expected[2]
                 and item.get("mode") == "0600"
                 and type(item.get("device")) is int
                 and type(item.get("inode")) is int,
                 "reject an old C variant or fake synthetic phase source")
            identity = item["device"], item["inode"]
            need(identity not in sources,
                 "reject shared synthetic phase-source ownership")
            sources.add(identity)
        native = phase.get("native_output")
        need(type(native) is dict and native.get("synthetic") is True
             and native.get("native_loaded") is False,
             "reject an actual or loaded synthetic native artifact")
        identity = native.get("device"), native.get("inode")
        need(identity not in natives,
             "reject an aliased synthetic native output owner")
        natives.add(identity)
        hashes.add(exact_digest(native.get("sha256"), "synthetic native"))
    for index, process in enumerate(processes):
        need(type(process) is dict and process.get("synthetic") is True
             and process.get("phase") == PHASES[index // 7]
             and process.get("role") == PROCESS_ROLES[index % 7]
             and type(process.get("pid")) is int and process["pid"] > 0
             and process["pid"] not in pids
             and process.get("exit_status") == 0,
             "reject missing, duplicate, reordered, or actual compiler roles")
        pids.add(process["pid"])
    need(len(sources) == 4 and len(natives) == 2
         and len(hashes) == 1 and len(pids) == 14,
         "reject fake first-party source or reproducibility provenance")
    return plan


def validate_context(semantic: types.ModuleType, old: types.ModuleType,
                     semantic_owners: tuple, raw: dict,
                     producer: types.ModuleType) -> tuple[dict, bytes, dict, dict]:
    receipt, derived = semantic.validate_context(old, raw, producer)
    need(hashlib.sha256(derived).hexdigest() == DERIVED_SHA256
         and len(derived) == DERIVED_BYTES
         and derived.count(semantic.NEW_REDUCERS) == 1
         and semantic.OLD_REDUCERS not in derived
         and derived.count(semantic.COPY_ANCHOR) == 1
         and derived.count(semantic.CAPTURE_ANCHOR) == 1
         and derived.count(semantic.SUBJECT_FAILURE_ANCHOR) == 1,
         "derive only the real one-change 221,647-byte Match-corrected C source")
    machine = document(producer, raw[SEMANTICS[2][0]],
                       "pushed first-party C Match semantic freeze")
    expected = semantic.contract_document(
        old, receipt, derived, semantic_owners,
        SEMANTICS[0][1], SEMANTICS[1][1],
    )
    need(producer.canonical(machine) == raw[SEMANTICS[2][0]]
         and machine == expected
         and machine.get("source", {}).get("sha256") == SEMANTICS[0][1]
         and machine.get("protocol", {}).get("sha256") == SEMANTICS[1][1]
         and machine.get("source_correction", {}).get("derived_variant_sha256")
         == DERIVED_SHA256
         and machine.get("source_correction", {}).get("derived_variant_bytes")
         == DERIVED_BYTES
         and machine.get("source_correction", {}).get(
             "derived_variant_materialized") is False
         and machine.get("candidate_correctness") == "NOT MEASURED",
         "reject changed pushed Match semantics or falsely claim a built C")
    validate_c18_source(raw[C18[0][0]])
    c18 = document(producer, raw[C18[2][0]], "immutable C18 build contract")
    previous_build = document(producer, raw[C18_BUILD_RECEIPT[0]],
                              "small genuine C18 build receipt")
    previous_root = document(producer, raw[C18_ROOT_RECEIPT[0]],
                             "small genuine C18 root receipt")
    validate_c18(c18, previous_build, previous_root)
    validate_synthetic_plan(synthetic_plan())
    clean_runtime()
    return receipt, derived, previous_build, previous_root


def source_effects() -> dict:
    return {
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_libraries_loaded": 0,
        "actual_compiler_processes": 0,
        "actual_archives_opened": 0,
        "actual_private_roots_opened": 0,
        "actual_private_roots_created": 0,
        "actual_graph_owners_opened": 0,
        "actual_canonical_candidate_owners_opened": 0,
        "actual_guard_installations": 0,
        "actual_holdout_cases_read": 0,
        "actual_benchmark_files_read": 0,
        "actual_clock_samples": 0,
        "actual_network_requests": 0,
        "actual_workspace_mutations": 0,
    }


def contract_document(old: types.ModuleType, owners: tuple, receipt: dict,
                      previous_build: dict, previous_root: dict,
                      source_sha: str, protocol_sha: str) -> dict:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "PHASE 2: CANDIDATES",
        "status": "SOURCE FROZEN; MATCH-CORRECTED C NATIVE BUILD NOT RUN",
        "status_scope": "FIRST-PARTY REPRODUCIBLE BUILD DESIGN ONLY; "
                        "NOT A BUILD OR CANDIDATE RESULT",
        "family": FAMILY,
        "label": LABEL,
        "goal_sha256": old.GOAL[1],
        "source": {"path": SOURCE, "sha256": source_sha},
        "protocol": {"path": PROTOCOL, "sha256": protocol_sha},
        "pinned_cpython": {
            "path": PYTHON, "version": "3.14.6",
            "required_flags": ["-I", "-B", "-S"],
        },
        "phase_one": {
            "status": "PASS",
            "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": 13,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "separate_reference_case_count": REFERENCE_CASE_COUNT,
            "separate_reference_cases_counted_in_original_denominator": False,
            "owners": [record(item) for item in old.P0],
        },
        "frozen_original_producer": {
            "version": 5,
            "family_count": 6,
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": 13,
            "owners": [record(item) for item in old.PRODUCER],
        },
        "strict_first_party_runtime_guard": {
            "version": 2,
            "owners": [record(item) for item in old.GUARD],
            "guard_installed": False,
            "standard_library_re": "FORBIDDEN",
            "cpython_sre_engine": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "another_candidate": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED; CANDIDATE NOT RUN",
        },
        "committed_first_party_match_semantics": {
            "version": 1,
            "owners": [record(item) for item in SEMANTICS],
            "base_variant_sha256": BASE_VARIANT_SHA256,
            "base_variant_bytes": 222212,
            "derived_variant_sha256": DERIVED_SHA256,
            "derived_variant_bytes": DERIVED_BYTES,
            "source_change_count": 1,
            "match_pickle_protocols": [0, 1, 2, 3, 4, 5],
            "numeric_protocol_validation_preserved": True,
            "match_copy_identity_source_preserved": True,
            "match_deepcopy_identity_source_preserved": True,
            "nested_buffer_capture_source_preserved": True,
            "released_subject_error_source_preserved": True,
            "nested_exporter_acquisition_flags": [0, 0, 284],
            "nested_exporter_release_order": "LIFO",
            "candidate_correctness": "NOT MEASURED",
        },
        "actual_previous_c18_build": {
            "owners": [record(item) for item in C18],
            "build_receipt": record(C18_BUILD_RECEIPT),
            "root_receipt": record(C18_ROOT_RECEIPT),
            "build_status": previous_build["build_status"],
            "root_status": previous_root["status"],
            "root_device": previous_root["root"]["device"],
            "root_path_accessed": False,
            "phase_count": 2,
            "actual_compiler_process_count": 14,
            "actual_source_owner_count": 4,
            "actual_native_artifact_count": 2,
            "actual_native_artifacts_byte_identical": True,
            "historical_compiled_variant_sha256": BASE_VARIANT_SHA256,
            "historical_build_compiled_match_corrected_variant": False,
            "historical_candidate_matching": "NOT RUN",
        },
        "latest_actual_c_correctness": {
            "candidate_status": receipt["candidate_status"],
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "attempted_suite_count": receipt["attempted_suite_count"],
            "completed_suite_count": receipt["completed_suite_count"],
            "actual_candidate_workers": receipt["actual_candidate_workers"],
            "observed_semantic_mismatch_lower_bound":
                receipt["observed_semantic_mismatch_lower_bound"],
            "semantic_mismatch_count": "NOT MEASURED",
            "verified_passing_case_count": receipt["verified_passing_case_count"],
            "infrastructure_failure_count": receipt["infrastructure_failure_count"],
            "candidate_execution_failure_count":
                receipt["candidate_execution_failure_count"],
            "match_correction_effect": "NOT MEASURED",
        },
        "future_actual_build_policy": {
            "authorization": "ROOT-APPROVED EXPLICIT --build ONLY, AFTER "
                             "SOURCE FREEZE REVIEW, COMMIT, AND PUSH",
            "explicit_authorization_flag": BUILD_AUTHORIZATION,
            "source_freeze_builds_native_code": False,
            "root_prefix": "/tmp/" + ROOT_PREFIX,
            "root_mode": "0700",
            "root_device_assumed": False,
            "phase_names": list(PHASES),
            "phase_count": 2,
            "phase_mode": "0700",
            "source_owner_mode": "0600",
            "phase_source_count": 4,
            "match_corrected_source_applications": 2,
            "required_phase_source_sha256": DERIVED_SHA256,
            "required_phase_source_bytes": DERIVED_BYTES,
            "previous_8131_variant_in_phase": "FORBIDDEN",
            "unchanged_adapter_sha256": CANONICAL_ADAPTER[1],
            "native_extension_name": NATIVE_NAME,
            "independent_native_artifact_count": 2,
            "byte_identical_native_artifacts_required": True,
            "process_roles_per_phase": list(PROCESS_ROLES),
            "compiler_process_count_per_phase": 7,
            "expected_compiler_process_count": 14,
            "distinct_actual_process_ids_required": True,
            "process_launcher": "DIRECT POSIX SPAWN; NO SHELL OR SUBPROCESS",
            "toolchain_owner_count": 5,
            "toolchain_owners": [
                {"role": role, "path": path, "sha256": digest,
                 "bytes": count, "version": version, "executable": executable,
                 "authenticated_during_source_freeze": False}
                for role, path, digest, count, version, executable in TOOLCHAINS
            ],
            "recovery_journal": "OWNER-PRIVATE ATOMIC 0600 FILE; "
                                "FILE AND ROOT DIRECTORY FSYNC",
            "phase_source_publication": "EXCLUSIVE 0600 CREATE; FSYNC",
            "evidence_publication": "EXCLUSIVE 0600 CREATE; FILE AND "
                                    "EVIDENCE DIRECTORY FSYNC",
            "existing_native_activation": "FORBIDDEN",
            "existing_candidate_source_mutation": "FORBIDDEN",
            "existing_native_inode_preservation": "REQUIRED",
            "standard_library_matcher": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
        },
        "source_only_effects": source_effects(),
        "expanded_holdout": {
            "proposed_case_count": PROPOSED_HOLDOUT_CASE_COUNT,
            "case_status": "NOT GENERATED; NOT OPENED",
            "proposal_owner_opened": False,
            "final_protocol_status": "NOT FROZEN",
            "holdout_opened": False,
        },
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualification": "NOT ESTABLISHED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def rejected(label: str, action: object) -> str:
    try:
        action()
    except Exception as error:
        need(type(error).__name__ in {
            "BuildError", "SourceError", "CampaignError", "ProducerError",
        }, "unexpected source-only hostile failure: " + label)
        return label
    raise BuildError("accepted forbidden C V19 source-only operation: " + label)


def source_controls(semantic: types.ModuleType, old: types.ModuleType,
                    wall: object, producer: types.ModuleType, receipt: dict,
                    raw: dict, previous_build: dict,
                    previous_root: dict) -> list:
    controls = semantic.semantic_controls(
        old, wall, producer, receipt,
        raw["candidates/c/variants/subject_buffer_ownership_v1/vm_native.c"],
    )

    def changed_plan(kind: str) -> None:
        plan = synthetic_plan()
        if kind == "old-source":
            plan["phases"][0]["source_owners"][0]["sha256"] = BASE_VARIANT_SHA256
        elif kind == "duplicate-source":
            plan["phases"][1]["source_owners"][0]["inode"] = 9001
        elif kind == "duplicate-native":
            plan["phases"][1]["native_output"]["inode"] = 9101
        elif kind == "duplicate-process":
            plan["processes"][1]["pid"] = plan["processes"][0]["pid"]
        elif kind == "wrong-role":
            plan["processes"][2]["role"] = "external-regex-wrapper"
        elif kind == "fake-actual":
            plan["processes"][0]["synthetic"] = False
        elif kind == "wrong-source-size":
            plan["phases"][0]["source_owners"][0]["bytes"] = 222212
        elif kind == "loaded-native":
            plan["phases"][0]["native_output"]["native_loaded"] = True
        elif kind == "phase-mode":
            plan["phases"][0]["mode"] = "0755"
        elif kind == "different-output":
            plan["phases"][1]["native_output"]["sha256"] = "1" * 64
        else:
            raise BuildError("reject unknown synthetic hostility")
        validate_synthetic_plan(plan)

    def changed_receipt(kind: str) -> None:
        build = dict(previous_build)
        root = dict(previous_root)
        c18 = document(producer, raw[C18[2][0]], "frozen C18 contract control")
        if kind == "fake-current-source":
            build["variant_source_sha256"] = DERIVED_SHA256
        elif kind == "borrowed-build":
            root["canonical_build_receipt_sha256"] = "0" * 64
        elif kind == "fake-root-device":
            root["root"] = dict(root["root"], device=DEVICE)
        elif kind == "false-candidate-pass":
            build["candidate_correctness"] = "PASS"
        elif kind == "false-build-count":
            root["actual_compiler_process_count"] = 13
        elif kind == "false-publication-schema":
            build["publication_status"] = "PASS"
            need("publication_status" not in build,
                 "reject invented C18 publication_status schema")
        else:
            raise BuildError("reject unknown C18 hostility")
        validate_c18(c18, build, root)

    additional = []
    for name in (
        "old-source", "duplicate-source", "duplicate-native",
        "duplicate-process", "wrong-role", "fake-actual", "wrong-source-size",
        "loaded-native", "phase-mode", "different-output",
    ):
        additional.append(("reject synthetic " + name,
                           lambda item=name: changed_plan(item)))
    for name in (
        "fake-current-source", "borrowed-build", "fake-root-device",
        "false-candidate-pass", "false-build-count",
        "false-publication-schema",
    ):
        additional.append(("reject historical " + name,
                           lambda item=name: changed_receipt(item)))
    additional.extend((
        ("reject an unpinned actual C V19 build",
         lambda: parse_options(["--build"])),
        ("reject a guessed private build root",
         lambda: os.open("/tmp/" + ROOT_PREFIX + "forbidden",
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject actual compiler spawning",
         lambda: os.posix_spawn("/usr/bin/x86_64-linux-gnu-gcc-13",
                                ["gcc", "--version"], {})),
        ("reject current canonical C source",
         lambda: os.open(ROOT + "/" + CANONICAL_C[0],
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject current canonical Python adapter",
         lambda: os.open(ROOT + "/" + CANONICAL_ADAPTER[0],
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject actual installed native extension",
         lambda: os.open(ROOT + "/candidates/" + NATIVE_NAME,
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject historical C18 evidence archive",
         lambda: os.open(
             ROOT + "/oracle/phase2/evidence/native-source-build-v18-c-"
             "phase2-v18-c-subject-buffer-root-provenance.json.gz",
             os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject frozen holdout proposal access",
         lambda: os.open(ROOT + "/oracle/phase3/"
                         "expanded-sealed-holdout-v1.json",
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))),
        ("reject a compiler timing observation", lambda: os.times()),
    ))
    controls.extend(rejected(label, action) for label, action in additional)
    need(len(controls) >= 75 and sum(wall.blocked.values()) >= 40,
         "require physically hostile build, root, native, source, archive, "
         "clock, old-variant, and synthetic-reproducibility controls")
    clean_runtime()
    return controls


def exact_owner(relative: str, fingerprint: str, size: int,
                inode: int | None = None,
                capture: bool = True) -> tuple[dict, bytes | None]:
    exact_digest(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and info.st_dev == DEVICE
             and info.st_uid == os.geteuid() and info.st_nlink == 1
             and info.st_size == size
             and (inode is None or info.st_ino == inode),
             "reject a substituted actual owned candidate snapshot: " + relative)
        result = hashlib.sha256()
        parts = []
        remaining = size
        while remaining:
            block = os.read(descriptor, min(remaining, 262144))
            need(bool(block), "reject truncated candidate snapshot: " + relative)
            result.update(block)
            if capture:
                parts.append(block)
            remaining -= len(block)
        need(not os.read(descriptor, 1)
             and result.hexdigest() == fingerprint,
             "reject modified complete first-party owner: " + relative)
        after = os.fstat(descriptor)
        need((info.st_dev, info.st_ino, info.st_size,
              info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject concurrent native-source replacement: " + relative)
        return ({"path": relative, "sha256": fingerprint,
                 "bytes": size, "device": info.st_dev, "inode": info.st_ino,
                 "mode": format(stat.S_IMODE(info.st_mode), "04o"),
                 "nlink": info.st_nlink}, b"".join(parts) if capture else None)
    finally:
        os.close(descriptor)


def authenticate_toolchains() -> list:
    observations = []
    for role, path, fingerprint, count, version, executable in TOOLCHAINS:
        descriptor = os.open(path,
                             os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0))
        try:
            before = os.fstat(descriptor)
            need(stat.S_ISREG(before.st_mode)
                 and 0 < before.st_size == count <= MAX_TOOL_BYTES
                 and bool(before.st_mode & 0o111) is executable,
                 "reject unsafe C19 toolchain owner: " + role)
            fingerprint_state = hashlib.sha256()
            left = count
            while left:
                chunk = os.read(descriptor, min(left, 262144))
                need(bool(chunk), "reject truncated C19 toolchain: " + role)
                fingerprint_state.update(chunk)
                left -= len(chunk)
            need(not os.read(descriptor, 1)
                 and fingerprint_state.hexdigest() == fingerprint,
                 "reject substituted complete C19 toolchain: " + role)
            after = os.fstat(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject a C19 toolchain changed during authentication: " + role)
            observations.append({
                "role": role, "path": path, "sha256": fingerprint,
                "bytes": count, "device": before.st_dev,
                "inode": before.st_ino, "version": version,
                "executable": executable,
            })
        finally:
            os.close(descriptor)
    need(len(observations) == 5,
         "authenticate all five real first-party C19 build tools")
    return observations


def write_all(descriptor: int, payload: bytes) -> None:
    cursor = 0
    while cursor < len(payload):
        wrote = os.write(descriptor, payload[cursor:cursor + 262144])
        need(type(wrote) is int and wrote > 0,
             "reject an incomplete durable first-party C19 write")
        cursor += wrote


def write_exclusive(directory: int, name: str, payload: bytes) -> dict:
    need(type(name) is str and name and "/" not in name
         and name not in (".", "..") and type(payload) is bytes
         and 0 < len(payload) <= MAX_SOURCE_BYTES,
         "reject unsafe private C19 source or evidence publication")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        write_all(descriptor, payload)
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
             and info.st_nlink == 1 and info.st_size == len(payload)
             and stat.S_IMODE(info.st_mode) == 0o600,
             "reject an unsafe exclusive owner-private C19 artifact")
    finally:
        os.close(descriptor)
    os.fsync(directory)
    return {"name": name, "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": info.st_size, "device": info.st_dev,
            "inode": info.st_ino, "mode": "0600", "nlink": info.st_nlink,
            "exclusive_creation": True, "file_fsync_completed": True,
            "directory_fsync_completed": True}


def write_atomic_journal(directory: int, producer: types.ModuleType,
                         journal: dict) -> dict:
    payload = producer.canonical(journal)
    temporary = ".rebar-c-match-v19-journal-" + os.getrandom(12).hex()
    published = write_exclusive(directory, temporary, payload)
    os.replace(temporary, "native-build-recovery-journal-v19.json",
               src_dir_fd=directory, dst_dir_fd=directory)
    os.fsync(directory)
    published["name"] = "native-build-recovery-journal-v19.json"
    published["atomic_replacement"] = True
    return published


def private_root() -> tuple[int, str, dict]:
    for _ in range(32):
        path = "/tmp/" + ROOT_PREFIX + os.getrandom(16).hex()
        try:
            os.mkdir(path, 0o700)
        except FileExistsError:
            continue
        descriptor = os.open(path,
                             os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "reject an unsafe, shared, or substituted C19 private root")
        return descriptor, path, {
            "path": path, "prefix": ROOT_PREFIX, "device": info.st_dev,
            "inode": info.st_ino, "uid": info.st_uid, "mode": "0700",
            "nofollow_directory_descriptor": True, "directory_scanned": False,
        }
    raise BuildError("could not create a fresh unpredictable owner-private C19 root")


def spawn_tool(role: str, command: tuple, phase: str,
               expected_tool: str, used_pids: set) -> dict:
    need(role in PROCESS_ROLES and type(command) is tuple
         and len(command) >= 2 and command[0] == expected_tool,
         "reject a shell, external package, or unauthenticated build process")
    pipe_flags = getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "pipe2"):
        reader, writer = os.pipe2(pipe_flags)
    else:
        reader, writer = os.pipe()
    try:
        actions = (
            (os.POSIX_SPAWN_DUP2, writer, 1),
            (os.POSIX_SPAWN_DUP2, writer, 2),
            (os.POSIX_SPAWN_CLOSE, reader),
            (os.POSIX_SPAWN_CLOSE, writer),
        )
        environment = {
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
            "SOURCE_DATE_EPOCH": "0", "PATH": "/usr/bin:/bin",
        }
        pid = os.posix_spawn(expected_tool, command, environment,
                             file_actions=actions)
    except BaseException:
        os.close(reader)
        os.close(writer)
        raise
    os.close(writer)
    parts = []
    total = 0
    try:
        while True:
            chunk = os.read(reader, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_PROCESS_OUTPUT:
                os.kill(pid, 9)
                os.waitpid(pid, 0)
                raise BuildError("reject oversized actual C19 compiler output")
            parts.append(chunk)
    finally:
        os.close(reader)
    observed, state = os.waitpid(pid, 0)
    need(observed == pid and pid > 0 and pid not in used_pids
         and os.WIFEXITED(state) and os.WEXITSTATUS(state) == 0,
         "reject failed, fake, reused, or incomplete C19 process: " + role)
    used_pids.add(pid)
    output = b"".join(parts)
    return {"phase": phase, "role": role, "pid": pid, "exit_status": 0,
            "output_sha256": hashlib.sha256(output).hexdigest(),
            "output_bytes": len(output), "command": list(command)}


def read_phase_artifact(directory: int, name: str) -> tuple[dict, bytes]:
    descriptor = os.open(name,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
    try:
        first = os.fstat(descriptor)
        need(stat.S_ISREG(first.st_mode) and first.st_uid == os.geteuid()
             and first.st_nlink == 1 and 0 < first.st_size <= MAX_SOURCE_BYTES
             and stat.S_IMODE(first.st_mode) in (0o600, 0o700, 0o755),
             "reject unsafe or borrowed private C19 artifact: " + name)
        pieces = []
        left = first.st_size
        while left:
            item = os.read(descriptor, min(left, 262144))
            need(bool(item), "reject truncated private C19 artifact: " + name)
            pieces.append(item)
            left -= len(item)
        need(not os.read(descriptor, 1),
             "reject changed private C19 artifact length: " + name)
        payload = b"".join(pieces)
        after = os.fstat(descriptor)
        need((first.st_dev, first.st_ino, first.st_size,
              first.st_mtime_ns, first.st_ctime_ns, first.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a C19 artifact replaced during authentication")
        return ({"name": name, "sha256": hashlib.sha256(payload).hexdigest(),
                 "bytes": len(payload), "device": first.st_dev,
                 "inode": first.st_ino,
                 "mode": format(stat.S_IMODE(first.st_mode), "04o"),
                 "nlink": first.st_nlink}, payload)
    finally:
        os.close(descriptor)


def build_phase(root_fd: int, root_path: str, phase: str,
                derived: bytes, adapter: bytes, pids: set) -> dict:
    os.mkdir(phase, 0o700, dir_fd=root_fd)
    phase_fd = os.open(phase,
                       os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd)
    try:
        info = os.fstat(phase_fd)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "reject unsafe actual private C19 build phase")
        native_source = write_exclusive(phase_fd, "vm_native.c", derived)
        bridge_source = write_exclusive(phase_fd, "vm_candidate.py", adapter)
        need(native_source["sha256"] == DERIVED_SHA256
             and native_source["bytes"] == DERIVED_BYTES
             and native_source["sha256"] != BASE_VARIANT_SHA256
             and bridge_source["sha256"] == CANONICAL_ADAPTER[1],
             "refuse to compile the historical C18 source or changed adapter")
        phase_path = root_path + "/" + phase
        output_path = phase_path + "/" + NATIVE_NAME
        native_path = phase_path + "/vm_native.c"
        include = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/" \
                  "include/python3.14"
        gcc = TOOLCHAINS[0][1]
        readelf = TOOLCHAINS[4][1]
        commands = (
            ("readelf_version", (readelf, "--version"), readelf),
            ("gcc_version", (gcc, "--version"), gcc),
            ("build_c_extension", (
                gcc, "-std=c11", "-O3", "-g0", "-fPIC", "-shared",
                "-fno-semantic-interposition",
                "-ffile-prefix-map=" + phase_path + "=/rebar/c-match-v19",
                "-I", include, "-Wl,--build-id=sha1",
                "-Wl,--hash-style=gnu", "-o", output_path, native_path,
            ), gcc),
            ("extension_dynamic", (readelf, "--dynamic", output_path), readelf),
            ("extension_symbols", (readelf, "--syms", output_path), readelf),
            ("extension_sections", (readelf, "--sections", output_path), readelf),
            ("extension_notes", (readelf, "--notes", output_path), readelf),
        )
        processes = []
        for expected, (role, command, executable) in zip(
                PROCESS_ROLES, commands, strict=True):
            need(role == expected,
                 "reject changed or reordered genuine C19 compiler roles")
            processes.append(spawn_tool(role, command, phase, executable, pids))
        native, payload = read_phase_artifact(phase_fd, NATIVE_NAME)
        need(payload.startswith(b"\x7fELF") and native["sha256"]
             not in (BASE_VARIANT_SHA256, EXPECTED_INSTALLED_NATIVE_SHA256),
             "require a genuinely new, privately built C ELF artifact")
        os.fsync(phase_fd)
        return {
            "name": phase, "device": info.st_dev, "inode": info.st_ino,
            "uid": info.st_uid, "mode": "0700",
            "source_owners": [
                {**native_source, "role": "match-corrected-native-source"},
                {**bridge_source, "role": "unchanged-python-adapter"},
            ],
            "native_output": {**native, "native_loaded": False},
            "processes": processes,
        }
    finally:
        os.close(phase_fd)


def verify_actual_phases(phases: list, pids: set) -> None:
    need(type(phases) is list and len(phases) == 2 and len(pids) == 14,
         "require two genuinely compiled C19 phases and fourteen distinct PIDs")
    source_ids = set()
    native_ids = set()
    native_hashes = set()
    for index, phase in enumerate(phases):
        need(type(phase) is dict and phase.get("name") == PHASES[index]
             and phase.get("mode") == "0700",
             "reject missing or reordered real C19 private phases")
        sources = phase.get("source_owners")
        processes = phase.get("processes")
        need(type(sources) is list and len(sources) == 2
             and type(processes) is list and len(processes) == 7,
             "reject missing actual owned C19 sources or compiler processes")
        expected_sources = (
            ("match-corrected-native-source", DERIVED_SHA256, DERIVED_BYTES),
            ("unchanged-python-adapter", CANONICAL_ADAPTER[1],
             CANONICAL_ADAPTER[2]),
        )
        for source, expected in zip(sources, expected_sources, strict=True):
            need(source.get("role") == expected[0]
                 and source.get("sha256") == expected[1]
                 and source.get("bytes") == expected[2]
                 and source.get("mode") == "0600",
                 "reject borrowed, old-variant, or weakened real C19 source")
            identity = source.get("device"), source.get("inode")
            need(identity not in source_ids,
                 "reject C19 source-owner reuse between actual phases")
            source_ids.add(identity)
        for offset, process in enumerate(processes):
            need(process.get("phase") == PHASES[index]
                 and process.get("role") == PROCESS_ROLES[offset]
                 and process.get("pid") in pids
                 and process.get("exit_status") == 0,
                 "reject fake, failed, or reordered real C19 process evidence")
        native = phase["native_output"]
        need(native.get("name") == NATIVE_NAME
             and native.get("native_loaded") is False,
             "reject an activated or borrowed C19 native extension")
        identity = native.get("device"), native.get("inode")
        need(identity not in native_ids,
             "reject a reused real C19 private native artifact")
        native_ids.add(identity)
        native_hashes.add(exact_digest(native.get("sha256"),
                                      "actual C19 extension"))
    need(len(source_ids) == 4 and len(native_ids) == 2
         and len(native_hashes) == 1,
         "require four fresh C19 sources and two byte-identical native files")


def evidence_directory() -> int:
    descriptor = os.open(ROOT + "/oracle/phase2/evidence",
                         os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    observed = os.fstat(descriptor)
    need(stat.S_ISDIR(observed.st_mode) and observed.st_dev == DEVICE
         and observed.st_uid == os.geteuid(),
         "reject unsafe first-party C19 actual evidence destination")
    return descriptor


def run_actual_build(options: dict, context: dict) -> dict:
    need(options["mode"] == "--build"
         and options.get("authorized") is True,
         "deny native compilation before independent root authorization")
    derived = context["derived"]
    producer = context["producer"]
    need(hashlib.sha256(derived).hexdigest() == DERIVED_SHA256
         and len(derived) == DERIVED_BYTES,
         "refuse any native build not derived from committed Match V1")
    canonical, _ = exact_owner(*CANONICAL_C, capture=False)
    adapter, adapter_bytes = exact_owner(*CANONICAL_ADAPTER, capture=True)
    need(type(adapter_bytes) is bytes,
         "require complete authentic first-party C adapter bytes")
    installed_path = "candidates/" + NATIVE_NAME
    installed_before, _ = exact_owner(
        installed_path, EXPECTED_INSTALLED_NATIVE_SHA256, 163504,
        capture=False,
    )
    tools = authenticate_toolchains()
    root_fd, root_path, root_record = private_root()
    journal = {
        "schema": SCHEMA + "-atomic-recovery-journal",
        "version": VERSION, "status": "PRIVATE ROOT CREATED",
        "family": FAMILY, "label": LABEL,
        "source_sha256": options["--source-sha256"],
        "protocol_sha256": options["--protocol-sha256"],
        "contract_sha256": options["--contract-sha256"],
        "match_semantics_contract_sha256": SEMANTICS[2][1],
        "derived_variant_sha256": DERIVED_SHA256,
        "derived_variant_bytes": DERIVED_BYTES,
        "root": root_record,
        "canonical_c_before": canonical,
        "canonical_adapter_before": adapter,
        "installed_native_before": installed_before,
        "installed_native_activated": False,
        "canonical_sources_modified": False,
        "phases": [],
    }
    try:
        write_atomic_journal(root_fd, producer, journal)
        phases = []
        pids = set()
        for phase in PHASES:
            actual = build_phase(root_fd, root_path, phase,
                                 derived, adapter_bytes, pids)
            phases.append(actual)
            journal["status"] = "PRIVATE PHASE " + phase + " DURABLY BUILT"
            journal["phases"] = phases
            write_atomic_journal(root_fd, producer, journal)
        verify_actual_phases(phases, pids)
        canonical_after, _ = exact_owner(*CANONICAL_C, capture=False)
        adapter_after, _ = exact_owner(*CANONICAL_ADAPTER, capture=False)
        native_after, _ = exact_owner(
            installed_path, EXPECTED_INSTALLED_NATIVE_SHA256, 163504,
            capture=False,
        )
        need(canonical_after == canonical and adapter_after == adapter
             and native_after == installed_before,
             "reject any changed candidate source, adapter, native hash, "
             "or original installed-native inode")
        journal["status"] = "PASS; FOUR SOURCES AND TWO MATCHING NATIVE FILES"
        journal["canonical_c_after"] = canonical_after
        journal["canonical_adapter_after"] = adapter_after
        journal["installed_native_after"] = native_after
        final_journal = write_atomic_journal(root_fd, producer, journal)
        evidence_fd = evidence_directory()
        try:
            phase_summary = [{
                "name": item["name"], "device": item["device"],
                "inode": item["inode"], "mode": item["mode"],
                "source_owners": item["source_owners"],
                "native_output": item["native_output"],
                "processes": item["processes"],
            } for item in phases]
            actual = {
                "schema": SCHEMA + "-durable-publication-receipt",
                "version": VERSION, "status": "PASS",
                "publication_pass_means":
                    "DURABLE FIRST-PARTY C MATCH-SOURCE BUILD ONLY",
                "build_status": "PASS", "family": FAMILY, "label": LABEL,
                "source_sha256": options["--source-sha256"],
                "protocol_sha256": options["--protocol-sha256"],
                "contract_sha256": options["--contract-sha256"],
                "semantic_source_sha256": SEMANTICS[0][1],
                "semantic_contract_sha256": SEMANTICS[2][1],
                "previous_c18_build_receipt_sha256": C18_BUILD_RECEIPT[1],
                "previous_c18_root_receipt_sha256": C18_ROOT_RECEIPT[1],
                "base_variant_sha256": BASE_VARIANT_SHA256,
                "variant_source_sha256": DERIVED_SHA256,
                "variant_source_bytes": DERIVED_BYTES,
                "adapter_source_sha256": CANONICAL_ADAPTER[1],
                "actual_source_apply_count": 2,
                "expected_source_apply_count": 2,
                "actual_compiler_process_count": 14,
                "expected_compiler_process_count": 14,
                "actual_compiler_process_ids": sorted(pids),
                "authenticated_toolchain_owner_count": 5,
                "authenticated_toolchain_owners": tools,
                "source_audit_status": "PASS",
                "private_phase_count": 2,
                "distinct_phase_source_owner_count": 4,
                "distinct_native_artifact_count": 2,
                "byte_identical_native_artifacts": True,
                "root": root_record,
                "phases": phase_summary,
                "recovery_journal": final_journal,
                "installed_native_before": installed_before,
                "installed_native_after": native_after,
                "installed_native_inode_preserved": True,
                "installed_native_activated": False,
                "candidate_source_mutations": 0,
                "historical_archives_opened": 0,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
                "candidate_workers_started": 0,
                "native_libraries_loaded": 0,
                "hidden_cases_read": 0,
                "clock_samples": 0,
                "timing_trials_run": 0,
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "winner_selected": False,
            }
            build_name = (
                "native-source-build-v19-c-phase2-v19-c-original-match-"
                "semantics-publication-receipt.json"
            )
            build_publication = write_exclusive(
                evidence_fd, build_name, producer.canonical(actual),
            )
            root_proof = {
                "schema": SCHEMA + "-durable-root-provenance-receipt",
                "version": VERSION, "status": "PASS",
                "publication_pass_means":
                    "DURABLE FIRST-PARTY C MATCH-SOURCE ROOT PROVENANCE ONLY",
                "family": FAMILY, "label": LABEL,
                "source_sha256": options["--source-sha256"],
                "protocol_sha256": options["--protocol-sha256"],
                "contract_sha256": options["--contract-sha256"],
                "canonical_build_status": "PASS",
                "canonical_build_receipt_relative":
                    "oracle/phase2/evidence/" + build_name,
                "canonical_build_receipt_sha256": build_publication["sha256"],
                "previous_c18_root_receipt_sha256": C18_ROOT_RECEIPT[1],
                "match_semantics_contract_sha256": SEMANTICS[2][1],
                "derived_variant_sha256": DERIVED_SHA256,
                "derived_variant_bytes": DERIVED_BYTES,
                "root": {**root_record,
                         "phase_count": 2,
                         "distinct_source_owner_count": 4,
                         "distinct_native_owner_count": 2,
                         "byte_identical_native_output": True,
                         "phases": phase_summary},
                "actual_compiler_process_count": 14,
                "expected_compiler_process_count": 14,
                "actual_compiler_process_ids": sorted(pids),
                "authenticated_toolchain_owner_count": 5,
                "authenticated_toolchain_owners": tools,
                "installed_native_inode_preserved": True,
                "installed_native_activated": False,
                "canonical_sources_modified": False,
                "historical_archives_opened": 0,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
                "candidate_workers_started": 0,
                "native_libraries_loaded": 0,
                "hidden_cases_read": 0,
                "clock_samples": 0,
                "performance": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "winner_selected": False,
            }
            root_name = (
                "native-source-build-v19-c-phase2-v19-c-original-match-"
                "semantics-root-provenance-receipt.json"
            )
            root_publication = write_exclusive(
                evidence_fd, root_name, producer.canonical(root_proof),
            )
        finally:
            os.close(evidence_fd)
        journal["status"] = "PASS; ACTUAL BUILD AND ROOT RECEIPTS DURABLE"
        journal["build_receipt_sha256"] = build_publication["sha256"]
        journal["root_receipt_sha256"] = root_publication["sha256"]
        write_atomic_journal(root_fd, producer, journal)
        return {
            "schema": SCHEMA + "-actual-published-build",
            "status": "PASS", "family": FAMILY, "label": LABEL,
            "build_receipt": build_publication,
            "root_receipt": root_publication,
            "actual_compiler_process_count": 14,
            "actual_source_phase_count": 2,
            "derived_variant_sha256": DERIVED_SHA256,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        }
    except BaseException as error:
        journal["status"] = "FAIL; PRIVATE ROOT AND RECOVERY JOURNAL RETAINED"
        journal["failure_type"] = type(error).__name__
        journal["failure_message"] = str(error)[:4096]
        try:
            write_atomic_journal(root_fd, producer, journal)
        except BaseException:
            pass
        raise
    finally:
        os.close(root_fd)


def parse_options(arguments: list) -> dict:
    need(type(arguments) is list and arguments,
         "require one separately authorized C19 source operation")
    modes = ("--render-contract", "--self-test", "--verify-frozen-context",
             "--build")
    need(arguments[0] in modes,
         "deny native build, worker, candidate, recovery, or timing without "
         "one explicit supported C19 operation")
    options = {"mode": arguments[0], "authorized": False}
    mapping = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        "--semantic-source-sha256", "--semantic-protocol-sha256",
        "--semantic-contract-sha256", "--phase1-source-sha256",
        "--phase1-protocol-sha256", "--phase1-contract-sha256",
        "--guard-source-sha256", "--guard-protocol-sha256",
        "--guard-contract-sha256", "--producer-source-sha256",
        "--producer-protocol-sha256", "--producer-contract-sha256",
        "--c18-source-sha256", "--c18-protocol-sha256",
        "--c18-contract-sha256", "--c18-build-receipt-sha256",
        "--c18-root-receipt-sha256", "--derived-variant-sha256",
    }
    index = 1
    while index < len(arguments):
        key = arguments[index]
        if key == BUILD_AUTHORIZATION:
            need(options["mode"] == "--build" and options["authorized"] is False,
                 "reject repeated or source-only native build authorization")
            options["authorized"] = True
            index += 1
            continue
        need(key in mapping and key not in options
             and index + 1 < len(arguments),
             "reject abbreviated, duplicated, unknown, root, native, or "
             "candidate build authority")
        options[key] = exact_digest(arguments[index + 1], key)
        index += 2
    need("--source-sha256" in options and "--protocol-sha256" in options,
         "independently pin exact C19 controller and protocol")
    if options["mode"] == "--render-contract":
        need("--contract-sha256" not in options,
             "render canonical contract before its exact final hash exists")
    else:
        need("--contract-sha256" in options,
             "independently pin complete exact C19 machine contract")
    actual_keys = mapping - {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
    }
    if options["mode"] != "--build":
        need(options["authorized"] is False
             and not any(key in options for key in actual_keys),
             "source-only gates never authorize a candidate, actual build, "
             "toolchain, archive, or private root")
        return options
    need(options["authorized"] is True,
         "require independently explicit root-authorized native build")
    expected = {
        "--semantic-source-sha256": SEMANTICS[0][1],
        "--semantic-protocol-sha256": SEMANTICS[1][1],
        "--semantic-contract-sha256": SEMANTICS[2][1],
        "--phase1-source-sha256":
            "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        "--phase1-protocol-sha256":
            "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        "--phase1-contract-sha256":
            "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        "--guard-source-sha256":
            "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        "--guard-protocol-sha256":
            "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        "--guard-contract-sha256":
            "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        "--producer-source-sha256":
            "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        "--producer-protocol-sha256":
            "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        "--producer-contract-sha256":
            "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        "--c18-source-sha256": C18[0][1],
        "--c18-protocol-sha256": C18[1][1],
        "--c18-contract-sha256": C18[2][1],
        "--c18-build-receipt-sha256": C18_BUILD_RECEIPT[1],
        "--c18-root-receipt-sha256": C18_ROOT_RECEIPT[1],
        "--derived-variant-sha256": DERIVED_SHA256,
    }
    need(set(actual_keys) == set(expected)
         and all(options.get(key) == value for key, value in expected.items()),
         "independently pin the complete pushed semantic correction, P0, "
         "guard, original producer, both real C18 receipts, and fe5bd C source")
    return options


def collect_source(options: dict) -> tuple[types.ModuleType, dict, bytes, dict]:
    semantic, old, semantic_owners, owners = bootstrap_wall()
    with old.SourceWall() as wall:
        own = old.read_dynamic(SOURCE, options["--source-sha256"])
        protocol = old.read_dynamic(PROTOCOL, options["--protocol-sha256"])
        need(hashlib.sha256(own).hexdigest() == options["--source-sha256"]
             and hashlib.sha256(protocol).hexdigest()
             == options["--protocol-sha256"],
             "reject substituted exact C19 controller or protocol")
        tree = ast.parse(own, filename=SOURCE)
        imports = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.extend(item.name for item in node.names)
            if isinstance(node, ast.ImportFrom) and node.module != "__future__":
                raise BuildError("reject an external top-level C19 source import")
        need(tuple(imports)
             == ("ast", "builtins", "hashlib", "os", "stat", "sys", "types"),
             "permit only matcher-free C19 source-verification imports")
        raw = {item[0]: old.read_owner(item) for item in owners}
        producer = old.load_producer(raw[old.PRODUCER[0][0]])
        receipt, derived, previous_build, previous_root = validate_context(
            semantic, old, semantic_owners, raw, producer,
        )
        frozen = contract_document(
            old, owners, receipt, previous_build, previous_root,
            options["--source-sha256"], options["--protocol-sha256"],
        )
        if options["mode"] != "--render-contract":
            actual_raw = old.read_dynamic(CONTRACT,
                                          options["--contract-sha256"])
            actual = document(producer, actual_raw,
                              "complete pinned C19 build-freeze contract")
            need(producer.canonical(actual) == actual_raw
                 and actual == frozen,
                 "reject a changed, noncanonical, falsely successful, or "
                 "false-variant C19 machine contract")
        controls = source_controls(
            semantic, old, wall, producer, receipt, raw,
            previous_build, previous_root,
        )
        effects = source_effects()
        need(all(type(value) is int and value == 0
                 for value in effects.values()),
             "all source-only C19 candidate and build effects must be zero")
        observed = {
            "schema": SCHEMA + (
                "-self-test" if options["mode"] == "--self-test"
                else "-frozen-context"
            ),
            "version": VERSION, "status": "PASS",
            "source_sha256": options["--source-sha256"],
            "protocol_sha256": options["--protocol-sha256"],
            "contract_sha256": options.get("--contract-sha256"),
            "authenticated_source_owner_count": len(owners),
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": 13,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "separate_reference_case_count": REFERENCE_CASE_COUNT,
            "actual_previous_c18_compiler_process_count": 14,
            "actual_previous_c18_phase_count": 2,
            "actual_previous_c18_root_device": 2049,
            "actual_previous_c18_variant_sha256": BASE_VARIANT_SHA256,
            "actual_previous_c_candidate_status": "FAIL",
            "actual_previous_c_mismatch_lower_bound": 236,
            "actual_previous_c_mismatch_count": "NOT MEASURED",
            "derived_variant_sha256": DERIVED_SHA256,
            "derived_variant_bytes": DERIVED_BYTES,
            "source_semantic_change_count": 1,
            "derived_variant_materialized": False,
            "actual_compiler_process_count": 0,
            "future_compiler_process_count": 14,
            "future_phase_count": 2,
            "hostile_controls": len(controls),
            "blocked_physical_operations": sum(wall.blocked.values()),
            "effects": effects,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
        context = {"producer": producer, "derived": derived,
                   "frozen": frozen, "observed": observed}
        return producer, frozen, derived, context


def main() -> int:
    try:
        clean_runtime()
        options = parse_options(list(sys.argv[1:]))
        producer, frozen, _derived, context = collect_source(options)
        if options["mode"] == "--render-contract":
            payload = producer.canonical(frozen)
        elif options["mode"] == "--build":
            payload = producer.canonical(run_actual_build(options, context))
        else:
            payload = producer.canonical(context["observed"])
        need(type(payload) is bytes and 0 < len(payload) <= MAX_SOURCE_BYTES,
             "bound complete canonical C19 source-only output")
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
        clean_runtime()
        return 0
    except Exception as error:
        sys.stderr.write("C original Match source build V19: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
