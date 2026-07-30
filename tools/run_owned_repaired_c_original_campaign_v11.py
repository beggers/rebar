#!/usr/bin/env python3
"""Freeze the actual-source-bound C21 campaign and true CPython V3 guard.

Source modes never import a candidate, load native code, run an original suite,
compile an extension, open a private root or archive, generate or inspect a
holdout, or measure performance. A frozen public-surface callable is verified
against the complete, unexecuted, authenticated source that really produced its
code object; the original oracle and its digest are never replaced.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v11.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V11.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v11.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v11"
LABEL = "phase2-v21-c-original-match-semantics-original-p0-v11"
DEVICE = 2064
MAX_OWNER = 8 * 1024 * 1024

C9 = (
    (
        "tools/run_owned_repaired_c_original_campaign_v9.py",
        "4796ba3c5e03a1341aa35f700679107a8bf835f0ebf582b02be59955ae211563",
        68216, 430552,
    ),
    (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V9.md",
        "7749e636b9adda7f28b5cfbe03c2895f45e3bbe8510c856bd8cdb9f441242997",
        7761, 524983,
    ),
    (
        "oracle/phase2/repaired-c-original-campaign-v9.json",
        "b7afd2e67dfd9031b63628f87f68aa1e6e8759e60eeef26dec76419e75144eaa",
        28202, 524987,
    ),
)


C10 = (
    ("tools/run_owned_repaired_c_original_campaign_v10.py",
     "ad8b8451847b3e5c566c141e829bdf6eecea8ae9f502b608288449022c83c790",
     50278, 430925),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V10.md",
     "ba673181c02daf3a572e3569283a5a4c490ed04e7cd76927e3f2fe1430630179",
     5941, 525204),
    ("oracle/phase2/repaired-c-original-campaign-v10.json",
     "2aad4885fe80b93f61f59c28ed6969fbcf16dda0b8a3457c71b449a9972bb595",
     44516, 525205),
)
C10_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v10-c-phase2-v21-c-"
    "original-match-semantics-original-p0-v10-failures-"
    "publication-receipt.json",
    "c5c85f828da7e960c90a23b1eb4d74c30a671d030de04ef61b0e4d00d7e5433a",
    7247, 525475,
)
C_ROUTE_ORIGINAL = (
    "tools/rust_original_cpython_suite_v1.py",
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    67175, 430765,
)
C_ROUTE_DIRECT_CORE = (
    "tools/independent_public_contract_v3.py",
    "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3",
    91039, 430402,
)
C_ROUTE_DIRECT_GATE = (
    "tools/run_frozen_p0_candidate_v1.py",
    "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8",
    104772, 432295,
)
C10_SUITE_OUTCOMES = (
    ("original_bounded_v5", 151, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("public_v3", 864, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("scanner_v3", 1024, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("buffer_v3", 768, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("managed_v1", 1024, "FAIL", "SEMANTIC MISMATCH", 16),
    ("scanner_verbose_v1", 2854, "PASS", "PASS", 0),
    ("public_types_v1", 6912, "FAIL", "SEMANTIC MISMATCH", 248),
    ("substitution_v2", 5120, "FAIL", "SEMANTIC MISMATCH", 224),
    ("shape_v2", 10240, "PASS", "PASS", 0),
    ("public_surface_v19", 1376, "FAIL", "SEMANTIC MISMATCH", 114),
    ("subinterpreter_v2", 128, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("pep688_v4", 264, "FAIL", "SEMANTIC MISMATCH", 4),
    ("threaded_pattern_v1", 512, "PASS", "PASS", 0),
)
ROUTE_CASES = frozenset(("public_v3", "scanner_v3", "buffer_v3"))
COMPLETE_VECTOR_MAX_RECORDS = 31237
COMPLETE_VECTOR_CHUNK_RECORDS = 32
COMPLETE_VECTOR_CHUNK_BYTES = 512 * 1024
COMPLETE_VECTOR_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
COMPLETE_VECTOR_COMPRESSED_BYTES = 2 * 1024 * 1024
COMPLETE_VECTOR_MAGIC = b"REBAR-C11-LZ1:"
COMPLETE_VECTOR_ALPHABET = (
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)

V3 = (
    (
        "tools/verify_owned_candidate_runtime_independence_v3.py",
        "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
        59765, 430856,
    ),
    (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
        "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
        5297, 525096,
    ),
    (
        "oracle/phase2/candidate-runtime-independence-v3.json",
        "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
        9157, 525114,
    ),
)

C9_RECEIPT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v9-c-"
    "phase2-v21-c-original-match-semantics-original-p0-v9-"
    "failures-publication-receipt.json",
    "54b690fa487670dd0cb18cbc35e36f684666d7fb547c1aa30c48b244788effb6",
    7332, 525075,
)

SUITES = (
    ("original_bounded_v5", 151, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("public_v3", 864, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("scanner_v3", 1024, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("buffer_v3", 768, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("managed_v1", 1024, "FAIL", "SEMANTIC MISMATCH", 16),
    ("scanner_verbose_v1", 2854, "PASS", "PASS", 0),
    ("public_types_v1", 6912, "FAIL", "SEMANTIC MISMATCH", 248),
    ("substitution_v2", 5120, "FAIL", "SEMANTIC MISMATCH", 224),
    ("shape_v2", 10240, "PASS", "PASS", 0),
    ("public_surface_v19", 1376, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("subinterpreter_v2", 128, "FAIL", "CANDIDATE EXECUTION FAILURE", None),
    ("pep688_v4", 264, "FAIL", "SEMANTIC MISMATCH", 4),
    ("threaded_pattern_v1", 512, "PASS", "PASS", 0),
)

REPLACEMENTS = {
    C9[0][0]: SOURCE,
    C9[1][0]: PROTOCOL,
    C9[2][0]: CONTRACT,
    "rebar-owned-repaired-c-original-campaign-v9": SCHEMA,
    "phase2-v21-c-original-match-semantics-original-p0-v9": LABEL,
    "/tmp/rebar-phase2-repaired-c-original-campaign-v9":
        "/tmp/rebar-phase2-repaired-c-original-campaign-v11",
    ".rebar-c-original-campaign-v9-original-native":
        ".rebar-c-original-campaign-v11-original-native",
    ".rebar-c-original-campaign-v9-staged-native":
        ".rebar-c-original-campaign-v11-staged-native",
    "original-native-recovery-journal-v9.json":
        "original-native-recovery-journal-v11.json",
    "repaired-c-original-campaign-v9-c-":
        "repaired-c-original-campaign-v11-c-",
    "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN":
        "SOURCE FROZEN; ACTUAL C21 V11 ORIGINAL CAMPAIGN NOT RUN",
    "SOURCE FREEZE, PRESERVED ACTUAL V6 AND V7 FAILURES; "
    "NOT A V9 CANDIDATE RESULT":
        "SOURCE FREEZE, PRESERVED ACTUAL V6, V7, AND V9 FAILURES; "
        "NOT A V11 CANDIDATE RESULT",
    "LATEST P0 V4 AND EXPLICIT C21 V9 ONLY":
        "LATEST P0 V4 AND EXPLICIT C21 V11 ONLY",
    "NOT RUN BY V9": "NOT RUN BY V11",
    "v9_candidate_correctness": "v11_candidate_correctness",
    "-v9": "-v11",
    "v9-original-native": "v11-original-native",
    "v9-staged-native": "v11-staged-native",
    "_rebar_owned_c_v9_authenticated_v8":
        "_rebar_owned_c_v11_authenticated_v8",
    "C21 original campaign V9: ": "C21 original campaign V11: ",
}


class CampaignError(Exception):
    """Reject false source provenance or unearned candidate evidence."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.abspath(sys.executable) == PYTHON
         and sys.flags.isolated == 1
         and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True
         and "re" not in sys.modules
         and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "require clean matcher-free exact CPython 3.14.6 -I -B -S")


def exact_owner(owner: tuple) -> bytes:
    permitted = (C9 + C10 + V3 +
                 (C9_RECEIPT, C10_RECEIPT,
                  C_ROUTE_ORIGINAL, C_ROUTE_DIRECT_CORE,
                  C_ROUTE_DIRECT_GATE))
    need(type(owner) is tuple and len(owner) == 4
         and any(owner == item for item in permitted),
         "reject an unapproved complete C10 plaintext source owner")
    relative, expected, size, inode = owner
    need(type(relative) is str
         and not relative.startswith(("/", "candidates/", "docs/evidence/"))
         and not any(word in relative.lower() for word in ("holdout", "benchmark"))
         and not relative.endswith((".gz", ".xz", ".zip", ".tar", ".so"))
         and type(expected) is str and len(expected) == 64
         and all(char in "0123456789abcdef" for char in expected)
         and type(size) is int and 0 < size <= MAX_OWNER
         and type(inode) is int and inode > 0,
         "reject native, candidate, private, archive, holdout, or invented owner")
    handle = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == DEVICE
             and before.st_ino == inode
             and before.st_size == size
             and before.st_uid == os.geteuid()
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject an inexact frozen C10 predecessor: " + relative)
        blocks = []
        remaining = size
        while remaining:
            block = os.read(handle, min(remaining, 262144))
            need(bool(block), "reject a truncated exact C10 owner")
            blocks.append(block)
            remaining -= len(block)
        need(not os.read(handle, 1), "reject an expanded exact C10 owner")
        raw = b"".join(blocks)
        after = os.fstat(handle)
        need(hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a changed authenticated C10 owner: " + relative)
        return raw
    finally:
        os.close(handle)


def owner_record(owner: tuple) -> dict:
    return {
        "path": owner[0], "sha256": owner[1], "bytes": owner[2],
        "device": DEVICE, "inode": owner[3], "mode": "0600", "nlink": 1,
    }


class ExactV9ToV11(ast.NodeTransformer):
    """Retarget only authenticated campaign identity and two version nodes."""

    def __init__(self) -> None:
        self.identities = {name: 0 for name in REPLACEMENTS}
        self.inner_version_assignments = 0
        self.contract_version_fields = 0

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is str and node.value in REPLACEMENTS:
            self.identities[node.value] += 1
            return ast.copy_location(ast.Constant(REPLACEMENTS[node.value]), node)
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        node = self.generic_visit(node)
        if (len(node.targets) == 1
                and isinstance(node.value, ast.Constant)
                and type(node.value.value) is int
                and node.value.value == 9
                and isinstance(node.targets[0], ast.Attribute)
                and node.targets[0].attr == "value"
                and isinstance(node.targets[0].value, ast.Attribute)
                and node.targets[0].value.attr == "value"
                and isinstance(node.targets[0].value.value, ast.Name)
                and node.targets[0].value.value.id == "node"):
            node.value.value = 11
            self.inner_version_assignments += 1
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        node = self.generic_visit(node)
        for key, value in zip(node.keys, node.values, strict=True):
            if (isinstance(key, ast.Constant)
                    and key.value == "version"
                    and isinstance(value, ast.Constant)
                    and type(value.value) is int and value.value == 9):
                value.value = 11
                self.contract_version_fields += 1
        return node


def bootstrap_v9() -> tuple[types.ModuleType, dict]:
    clean_runtime()
    tree = ast.parse(exact_owner(C9[0]).decode("utf-8", "strict"),
                     filename=ROOT + "/" + C9[0][0])
    change = ExactV9ToV11()
    corrected = ast.fix_missing_locations(change.visit(tree))
    required = (
        C9[0][0], C9[1][0], C9[2][0],
        "rebar-owned-repaired-c-original-campaign-v9",
        "phase2-v21-c-original-match-semantics-original-p0-v9",
        "/tmp/rebar-phase2-repaired-c-original-campaign-v9",
        ".rebar-c-original-campaign-v9-original-native",
        ".rebar-c-original-campaign-v9-staged-native",
        "original-native-recovery-journal-v9.json",
        "repaired-c-original-campaign-v9-c-",
        "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN",
        "-v9", "v9-original-native", "v9-staged-native",
    )
    need(all(change.identities[item] >= 1 for item in required)
         and change.inner_version_assignments == 1
         and change.contract_version_fields == 1,
         "reject a broadened or incomplete whole-source C9-to-C10 transform")
    module = types.ModuleType("_rebar_owned_c_v11_authenticated_complete_v9")
    module.__file__ = ROOT + "/" + SOURCE
    module.__package__ = ""
    exec(compile(corrected, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SOURCE == SOURCE
         and module.PROTOCOL == PROTOCOL
         and module.CONTRACT == CONTRACT
         and module.SCHEMA == SCHEMA
         and module.LABEL == LABEL
         and module.C21_NATIVE_SHA256
         == "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60"
         and module.C21_VARIANT_SHA256
         == "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
         and module.ORIGINAL_NATIVE_INODE == 430300,
         "reject incomplete frozen C21 build, original inode, or C9 semantics")
    clean_runtime()
    return module, {
        "historical_complete_source": owner_record(C9[0]),
        "exact_identity_replacements": dict(change.identities),
        "exact_inner_version_assignments": change.inner_version_assignments,
        "exact_contract_version_fields": change.contract_version_fields,
        "frozen_oracle_source_modifications": 0,
        "frozen_guard_v2_source_modifications": 0,
        "frozen_producer_v5_source_modifications": 0,
        "candidate_source_modifications": 0,
        "candidate_imports": 0,
        "private_roots_opened": 0,
        "archives_opened": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }


def validate_v3(document: object, previous: types.ModuleType,
                old: types.ModuleType) -> dict:
    need(type(document) is dict
         and document.get("schema")
         == "rebar-owned-candidate-runtime-independence-v3-source-freeze"
         and document.get("version") == 3
         and document.get("status")
         == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
         and document.get("goal_sha256") == old.GOAL[1]
         and document.get("source") == owner_record(V3[0])
         and document.get("protocol") == owner_record(V3[1])
         and document.get("candidate_matching") == "NOT RUN"
         and document.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and document.get("qualified_candidate_count") == 0
         and document.get("winner_selected") is False
         and document.get("holdout") == "NOT OPENED"
         and document.get("performance") == "NOT MEASURED",
         "reject an unpinned, executed, or falsely qualifying genuine V3 guard")
    predecessor = document.get("immutable_predecessor_v2")
    producer = document.get("immutable_producer_v5")
    need(type(predecessor) is dict
         and predecessor.get("version") == 2
         and predecessor.get("prepare_family")
         == "INHERITED EXACT V2 FUNCTION AND GLOBALS"
         and predecessor.get("child_bootstrap")
         == "UNCHANGED AUTHENTICATED V2 CHILD SOURCE"
         and type(predecessor.get("owners")) is dict
         and predecessor["owners"] == {
             "source": owner_record(old.GUARD[0]),
             "protocol": owner_record(old.GUARD[1]),
             "contract": owner_record(old.GUARD[2]),
         }
         and type(producer) is dict
         and producer.get("version") == 5
         and producer.get("source_mutated") is False
         and producer.get("child_guard_identity")
         == "EXACT V2 PREPARE GLOBALS AND CHILD PINS"
         and producer.get("create_boundary")
         == "AUTHENTICATED V5 GUARDED CREATE CLOSURE"
         and producer.get("owners") == {
             "source": owner_record(old.PRODUCER[0]),
             "protocol": owner_record(old.PRODUCER[1]),
             "contract": owner_record(old.PRODUCER[2]),
         },
         "preserve independently frozen V2 policy and unchanged V5 producer")
    native = document.get("native_owner_policy")
    required = sorted((
        "absolute_path", "bytes", "device", "family", "file_name",
        "inode", "mode", "native_loaded", "nlink", "relative", "role",
        "sha256", "size_bytes", "uid",
    ))
    need(type(native) is dict
         and native.get("required_field_count") == 14
         and native.get("required_fields") == required
         and native.get("extra_or_missing_fields") == "FORBIDDEN"
         and native.get("native_loaded") is False,
         "require both exact unchanged first-party fourteen-field native roles")
    nested = document.get("subinterpreter_bootstrap")
    need(type(nested) is dict
         and nested.get("suite") == "subinterpreter_v2"
         and nested.get("original_case_count") == 128
         and nested.get("expected_interpreters_created") == 11
         and nested.get("expected_interpreters_destroyed") == 11
         and nested.get("expected_case_interpreter_exec_calls") == 394
         and nested.get("expected_bootstrap_interpreter_exec_calls") == 11
         and nested.get("expected_cleanup_interpreter_exec_calls") == 11
         and nested.get("expected_total_real_interpreter_exec_calls") == 416
         and nested.get("creation_audit_event")
         == "cpython.PyInterpreterState_New"
         and nested.get("creation_audit_arguments") == "NOT MEASURED"
         and nested.get("first_execution")
         == "UNCHANGED V2 CHALLENGE-BOUND CHILD GUARD"
         and nested.get("positive_attestation")
         == "REAL UNIQUE OPERATING-SYSTEM PIPE"
         and nested.get("unrestricted_creation") is False
         and all(nested.get(key) == 0 for key in (
             "actual_interpreters_created", "actual_interpreters_destroyed",
             "actual_case_interpreter_exec_calls",
             "actual_bootstrap_interpreter_exec_calls",
             "actual_cleanup_interpreter_exec_calls",
             "actual_child_guards_installed",
         )),
         "reject guessed, fabricated, unscoped, or unexecuted CPython lifecycle")
    effects = document.get("source_only_effects")
    need(type(effects) is dict and len(effects) == 15
         and all(type(value) is int and value == 0
                 for value in effects.values()),
         "reject an actual effect in the frozen V3 guard source")
    phase = document.get("phase_one")
    need(type(phase) is dict
         and phase.get("version") == 4
         and phase.get("original_case_execution_denominator") == 31237
         and phase.get("original_suite_count") == 13
         and phase.get("named_private_waiver_count") == 13
         and phase.get("separate_supplemental_case_count") == 8244
         and phase.get("supplemental_cases_counted_in_original_denominator")
         is False,
         "never reduce original suites or count supplemental references")
    pinned = document.get("pinned_cpython")
    need(type(pinned) is dict
         and pinned.get("implementation") == "cpython"
         and pinned.get("version") == "3.14.6"
         and pinned.get("executable") == PYTHON
         and pinned.get("flags") == ["-I", "-B", "-S"],
         "require genuine source-pinned CPython for actual child execution")
    provider = pinned.get("public_interpreter_source")
    need(type(provider) is dict
         and provider.get("absolute_path")
         == "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
            "lib/python3.14/concurrent/interpreters/__init__.py"
         and provider.get("sha256")
         == "040e47f07bdfb28c67798fa7764fac1d79e13fd0fc0db9c85ee5dae8e1edf249"
         and provider.get("bytes") == 7707
         and provider.get("device") == 2049
         and provider.get("inode") == 9595896
         and provider.get("mode") == "0600"
         and provider.get("nlink") == 1,
         "require the exact genuine pinned CPython public interpreter provider")
    return document


def validate_c9_receipt(receipt: object,
                        historical: types.ModuleType) -> dict:
    need(type(receipt) is dict
         and receipt.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v9-"
            "durable-publication-receipt"
         and receipt.get("version") == 9
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("publication_pass_means")
         == "DURABLE CORRECTNESS PUBLICATION ONLY"
         and receipt.get("family") == "c"
         and receipt.get("label")
         == "phase2-v21-c-original-match-semantics-original-p0-v9"
         and receipt.get("source_sha256") == C9[0][1]
         and receipt.get("protocol_sha256") == C9[1][1]
         and receipt.get("contract_sha256") == C9[2][1]
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("candidate_qualified") is False
         and receipt.get("suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("completed_suite_count") == 7
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("candidate_execution_failure_count") == 6
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("worker_timeout_count") == 0
         and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
         and receipt.get("observed_semantic_mismatch_lower_bound") == 492
         and receipt.get("verified_passing_case_count") == 13606
         and receipt.get("named_private_waiver_count") == 13
         and receipt.get("separate_reference_case_count") == 8244
         and receipt.get("separate_reference_cases_counted_as_candidate_cases")
         is False
         and receipt.get("actual_c21_build_receipt_sha256")
         == historical.C21_BUILD_RECEIPT[1]
         and receipt.get("actual_c21_root_receipt_sha256")
         == historical.C21_ROOT_RECEIPT[1]
         and receipt.get("corrected_source_sha256")
         == historical.C21_VARIANT_SHA256
         and receipt.get("native_engine_sha256")
         == historical.C21_NATIVE_SHA256
         and receipt.get("native_bridge_sha256")
         == historical.C21_NATIVE_SHA256
         and receipt.get("original_native_inode_restored") is True
         and receipt.get("original_source_targets_modified") == 0
         and receipt.get("expanded_holdout_proposed_case_count") == 14155776
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("winner_selected") is False,
         "reject a changed, incomplete, falsely qualified, or invented C9 result")
    rows = receipt.get("suite_outcomes")
    pids = receipt.get("actual_worker_process_ids")
    need(type(rows) is list and len(rows) == len(SUITES)
         and type(pids) is list and len(pids) == 13
         and all(type(item) is int and item > 0 for item in pids)
         and len(set(pids)) == 13
         and receipt.get("actual_worker_process_ids_are_distinct") is True,
         "require all thirteen genuine independently identified C9 workers")
    measured = 0
    clean = 0
    failures = 0
    for row, expected, process in zip(rows, SUITES, pids, strict=True):
        name, count, status, failure_class, mismatch = expected
        need(type(row) is dict
             and row.get("suite") == name
             and row.get("case_execution_denominator") == count
             and row.get("status") == status
             and row.get("failure_class") == failure_class
             and row.get("actual_candidate_workers") == 1
             and row.get("worker_process_id") == process,
             "reject a dropped, invented, or reordered actual C9 suite: " + name)
        if mismatch is None:
            need(row.get("mismatch_count") == "NOT MEASURED",
                 "never invent mismatch counts from an incomplete C9 suite")
            failures += 1
        else:
            need(row.get("mismatch_count") == mismatch,
                 "preserve the exact measured original mismatch: " + name)
            measured += mismatch
            if mismatch == 0:
                clean += count
        if name == "public_surface_v19":
            need(row.get("error_type") == "CampaignError"
                 and row.get("failure_phase") == "ENCODE COMPLETE GUARDED RESULT"
                 and row.get("plain_failure_diagnostic")
                 == "reject a forged function whose filename imitates frozen "
                    "source: tools.python_re_public_surface_oracle_stage19.digest",
                 "preserve the genuine historical full-source digest failure")
        if name == "subinterpreter_v2":
            need(row.get("error_type") == "ActualSuiteFailure"
                 and row.get("plain_failure_diagnostic")
                 == "preserve the actual guarded original child lifecycle failure",
                 "never invent historical child execution or failure details")
    need(measured == 492 and clean == 13606 and failures == 6
         and sum(item[1] for item in SUITES) == 31237,
         "preserve complete historical mismatch and original denominators")
    return receipt



def clean_c_observer_route(raw: bytes, owner: tuple,
                           function_name: str, line_number: int,
                           keyword: str) -> bytes:
    """Change one authenticated candidate classification, never an oracle."""
    need(type(raw) is bytes and len(raw) == owner[2]
         and hashlib.sha256(raw).hexdigest() == owner[1]
         and (owner, function_name, line_number, keyword) in (
             (C_ROUTE_ORIGINAL, "authenticate_original_sources",
              211, "candidate"),
             (C_ROUTE_DIRECT_CORE, "load_prerequisites",
              483, "candidate_loaded"),
         ),
         "authenticate the exact complete first-party original C observer")
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=ROOT + "/" + owner[0])
    matches = [
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == function_name
    ]
    need(len(matches) == 1 and bool(matches[0].body),
         "reject a missing or duplicated original-only runtime function")
    call = matches[0].body[0]
    need(isinstance(call, ast.Expr)
         and isinstance(call.value, ast.Call)
         and isinstance(call.value.func, ast.Name)
         and call.value.func.id == "verify_runtime"
         and not call.value.args and not call.value.keywords
         and call.lineno == line_number
         and call.end_lineno == line_number,
         "change only the exact authenticated original-only runtime call")
    lines = text.splitlines(keepends=True)
    need(len(lines) >= line_number
         and lines[line_number - 1] in (
             "    verify_runtime()\n", "    verify_runtime()\r\n",
         ),
         "reject an altered source-owned candidate classification line")
    ending = "\r\n" if lines[line_number - 1].endswith("\r\n") else "\n"
    lines[line_number - 1] = (
        "    verify_runtime(" + keyword + "=True)" + ending
    )
    fixed = "".join(lines).encode("utf-8", "strict")
    actual = ast.parse(
        fixed.decode("utf-8", "strict"),
        filename=ROOT + "/" + owner[0],
    )
    call.value.keywords = [
        ast.keyword(arg=keyword, value=ast.Constant(value=True)),
    ]
    need(ast.dump(tree, include_attributes=False)
         == ast.dump(actual, include_attributes=False),
         "reject an original comparison, matrix, evaluator, or guard change")
    return fixed


def whole_source_route_function(module: types.ModuleType, raw: bytes,
                                owner: tuple, function_name: str,
                                line_number: int) -> types.FunctionType:
    """Extract exact function code from a complete, never-executed module."""
    need(type(module) is types.ModuleType
         and module.__name__ == owner[0].removesuffix(".py").replace("/", ".")
         and sys.modules.get(module.__name__) is module
         and os.path.abspath(getattr(module, "__file__", ""))
         == ROOT + "/" + owner[0]
         and getattr(module, "SOURCE_RELATIVE", None) == owner[0],
         "bind the real frozen Python module, not a substitute or new engine")
    source = ast.parse(raw.decode("utf-8", "strict"),
                       filename=ROOT + "/" + owner[0])
    definitions = [
        item for item in source.body
        if isinstance(item, ast.FunctionDef)
        and item.name == function_name
        and item.lineno == line_number - 4
    ]
    if owner == C_ROUTE_DIRECT_CORE:
        definitions = [
            item for item in source.body
            if isinstance(item, ast.FunctionDef)
            and item.name == function_name
        ]
    need(len(definitions) == 1,
         "require a single whole-source authenticated runtime function")
    complete = compile(source, ROOT + "/" + owner[0],
                       "exec", dont_inherit=True)
    codes = [
        item for item in complete.co_consts
        if type(item) is types.CodeType
        and item.co_name == function_name
        and item.co_qualname == function_name
        and item.co_firstlineno == definitions[0].lineno
    ]
    original = getattr(module, function_name, None)
    need(len(codes) == 1
         and type(original) is types.FunctionType
         and original.__globals__ is module.__dict__
         and original.__module__ == module.__name__
         and original.__closure__ is None,
         "reject delegated, forged, or cross-family full-module function code")
    corrected = types.FunctionType(
        codes[0], module.__dict__, function_name,
        original.__defaults__, original.__closure__,
    )
    corrected.__kwdefaults__ = original.__kwdefaults__
    corrected.__annotations__ = dict(original.__annotations__)
    corrected.__module__ = original.__module__
    corrected.__qualname__ = original.__qualname__
    need(corrected.__globals__ is module.__dict__
         and corrected.__code__ is codes[0],
         "reject a partial-source or substituted route overlay")
    return corrected


def require_selected_guarded_c(producer: types.ModuleType,
                               selected: object,
                               policy: object) -> None:
    need(type(producer) is types.ModuleType
         and getattr(producer, "SCHEMA", None)
         == "rebar-owned-six-family-original-p0-producer-v5"
         and type(selected) is producer.FamilySpec
         and producer.family_spec("c") is selected
         and selected.name == "c"
         and selected.module == "candidates.vm_candidate"
         and selected.adapter_relative == "candidates/vm_candidate.py"
         and selected.bridge_module == "candidates._vm_native"
         and selected.engine_relative
         == "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
         and selected.bridge_relative == selected.engine_relative
         and selected.combined_native is True
         and selected.owned_ctypes is False
         and len(selected.source_owners) == 2
         and selected.source_owners[1][1]
         == "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2"
         and getattr(policy, "installed", False) is True
         and getattr(policy, "prepared_family", None) == "c"
         and getattr(policy, "selected", None) is sys.modules.get("re")
         and sys.modules.get("re")
         is sys.modules.get("candidates.vm_candidate")
         and producer.require_selected(selected) is policy.selected
         and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and callable(getattr(policy, "check_modules", None)),
         "require the exact selected first-party C matcher and real V3 guard")
    policy.check_modules()


def install_c_direct_core(gate: types.ModuleType,
                          producer: types.ModuleType,
                          selected: object, policy: object,
                          counts: dict) -> types.ModuleType:
    require_selected_guarded_c(producer, selected, policy)
    need(type(gate) is types.ModuleType
         and getattr(gate, "CORE_RELATIVE", None)
         == C_ROUTE_DIRECT_CORE[0]
         and getattr(gate, "CORE_SHA256", None)
         == C_ROUTE_DIRECT_CORE[1]
         and tuple(producer.DIRECT_GATE_OWNER) == C_ROUTE_DIRECT_GATE
         and type(getattr(gate, "source_module_for_core", None))
         is types.FunctionType,
         "authenticate the complete immutable source-owned C direct gate")
    resolver = gate.source_module_for_core

    def c_selected_core(spec: object) -> tuple:
        require_selected_guarded_c(producer, selected, policy)
        need(getattr(spec, "name", None) in ROUTE_CASES,
             "reject crossed, reference-only, or unselected direct route")
        core, category = resolver(spec)
        need(type(core) is types.ModuleType
             and core.__name__ == "tools.independent_public_contract_v3"
             and core.__file__ == ROOT + "/" + C_ROUTE_DIRECT_CORE[0]
             and sys.modules.get(core.__name__) is core
             and getattr(core, "SOURCE_RELATIVE", None)
             == C_ROUTE_DIRECT_CORE[0]
             and getattr(category, "case_count", None)
             == getattr(spec, "case_count", None)
             and getattr(category, "matrix_sha256", None)
             == getattr(spec, "matrix_sha256", None),
             "require the real direct-core module and complete frozen case")
        immutable = producer.read_owner(C_ROUTE_DIRECT_CORE)
        corrected_source = clean_c_observer_route(
            immutable, C_ROUTE_DIRECT_CORE,
            "load_prerequisites", 483, "candidate_loaded",
        )
        replacement = whole_source_route_function(
            core, corrected_source, C_ROUTE_DIRECT_CORE,
            "load_prerequisites", 483,
        )
        require_selected_guarded_c(producer, selected, policy)
        core.load_prerequisites = replacement
        need(core.load_prerequisites is replacement,
             "reject replacement of the exact direct prerequisite overlay")
        counts["direct_core_candidate_route_overlays"] += 1
        return core, category

    gate.source_module_for_core = c_selected_core
    counts["direct_gate_candidate_route_overlays"] += 1
    require_selected_guarded_c(producer, selected, policy)
    return gate


def install_c_observer_routes(producer: types.ModuleType,
                              selected: object, policy: object,
                              counts: dict) -> dict:
    require_selected_guarded_c(producer, selected, policy)
    need(tuple(producer.HARNESS_OWNER) == C_ROUTE_ORIGINAL
         and tuple(producer.DIRECT_GATE_OWNER) == C_ROUTE_DIRECT_GATE
         and callable(producer.load_module)
         and type(counts) is dict
         and type(counts.get("historical_v4_source_transforms")) is int,
         "preserve the exact immutable C producer and V4 ctypes cleanup")
    previous_load = producer.load_module
    counts["original_candidate_route_overlays"] = 0
    counts["direct_gate_candidate_route_overlays"] = 0
    counts["direct_core_candidate_route_overlays"] = 0

    def guarded_route(owner: tuple, name: str) -> types.ModuleType:
        if owner not in (C_ROUTE_ORIGINAL, C_ROUTE_DIRECT_GATE):
            return previous_load(owner, name)
        require_selected_guarded_c(producer, selected, policy)
        need(type(name) is str
             and (
                 owner == C_ROUTE_ORIGINAL
                 and name == "_rebar_v5_original_harness_c"
                 or owner == C_ROUTE_DIRECT_GATE
                 and name.startswith("_rebar_v5_direct_gate_c_")
             ),
             "reject a foreign family, reference, or invented observer route")
        if owner == C_ROUTE_ORIGINAL:
            authentic_read = producer.read_owner

            def read_candidate_route(item: tuple,
                                     *args: object, **kwargs: object) -> bytes:
                raw = authentic_read(item, *args, **kwargs)
                if item == C_ROUTE_ORIGINAL:
                    require_selected_guarded_c(producer, selected, policy)
                    counts["original_candidate_route_overlays"] += 1
                    return clean_c_observer_route(
                        raw, C_ROUTE_ORIGINAL,
                        "authenticate_original_sources", 211, "candidate",
                    )
                return raw

            producer.read_owner = read_candidate_route
            try:
                loaded = previous_load(owner, name)
            finally:
                producer.read_owner = authentic_read
            need(producer.read_owner is authentic_read,
                 "restore the exact immutable first-party source reader")
        else:
            loaded = previous_load(owner, name)
            loaded = install_c_direct_core(
                loaded, producer, selected, policy, counts,
            )
        require_selected_guarded_c(producer, selected, policy)
        return loaded

    producer.load_module = guarded_route
    need(producer.load_module is guarded_route,
         "reject an unguarded original observer or foreign loader")
    return counts


def c11_base64_encode(raw: bytes) -> str:
    need(type(raw) is bytes, "encode only authentic bounded binary evidence")
    alphabet = COMPLETE_VECTOR_ALPHABET
    output: list[str] = []
    for position in range(0, len(raw), 3):
        part = raw[position:position + 3]
        number = int.from_bytes(part, "big") << (8 * (3 - len(part)))
        output.extend((
            chr(alphabet[(number >> 18) & 63]),
            chr(alphabet[(number >> 12) & 63]),
            chr(alphabet[(number >> 6) & 63]) if len(part) >= 2 else "=",
            chr(alphabet[number & 63]) if len(part) == 3 else "=",
        ))
    return "".join(output)


def c11_base64_decode(text: str) -> bytes:
    need(type(text) is str and len(text) % 4 == 0,
         "reject missing or noncanonical complete binary evidence")
    output = bytearray()
    for start in range(0, len(text), 4):
        group = text[start:start + 4]
        final = start + 4 == len(text)
        padding = len(group) - len(group.rstrip("="))
        need(padding in (0, 1, 2)
             and (padding == 0 or final)
             and "=" not in group[:4 - padding],
             "reject noncanonical or prematurely padded binary evidence")
        values = []
        for letter in group[:4 - padding]:
            value = COMPLETE_VECTOR_ALPHABET.find(
                letter.encode("ascii", "strict")
            )
            need(value >= 0, "reject forged complete binary evidence")
            values.append(value)
        values.extend([0] * padding)
        number = (
            (values[0] << 18) | (values[1] << 12)
            | (values[2] << 6) | values[3]
        )
        if padding == 2:
            need(values[1] & 15 == 0,
                 "reject noncanonical final complete evidence quartet")
        elif padding == 1:
            need(values[2] & 3 == 0,
                 "reject noncanonical final complete evidence quartet")
        output.extend(number.to_bytes(3, "big")[:3 - padding])
    decoded = bytes(output)
    need(c11_base64_encode(decoded) == text,
         "reject altered, substituted, or noncanonical binary evidence")
    return decoded


def c11_compress(raw: bytes) -> bytes:
    need(type(raw) is bytes
         and len(raw) <= COMPLETE_VECTOR_CHUNK_BYTES,
         "bound complete mismatch evidence before first-party compression")
    output = bytearray(COMPLETE_VECTOR_MAGIC)
    literals = bytearray()
    previous: dict[bytes, int] = {}
    position = 0

    def flush() -> None:
        if literals:
            need(len(literals) <= 128,
                 "bound an actual lossless literal block")
            output.append(len(literals) - 1)
            output.extend(literals)
            literals.clear()

    while position < len(raw):
        key = raw[position:position + 3]
        match = previous.get(key) if len(key) == 3 else None
        if len(key) == 3:
            previous[key] = position
        length = 0
        distance = 0
        if match is not None:
            distance = position - match
            if 0 < distance <= 65535:
                limit = min(130, len(raw) - position)
                while length < limit and raw[match + length] == raw[
                    position + length
                ]:
                    length += 1
        if length >= 3:
            flush()
            output.append(0x80 | (length - 3))
            output.extend(distance.to_bytes(2, "big"))
            for index in range(position + 1, position + length):
                next_key = raw[index:index + 3]
                if len(next_key) == 3:
                    previous[next_key] = index
            position += length
        else:
            literals.append(raw[position])
            position += 1
            if len(literals) == 128:
                flush()
    flush()
    return bytes(output)


def c11_decompress(payload: bytes, expected_size: int) -> bytes:
    need(type(payload) is bytes
         and type(expected_size) is int
         and 0 <= expected_size <= COMPLETE_VECTOR_CHUNK_BYTES
         and payload.startswith(COMPLETE_VECTOR_MAGIC),
         "reject forged first-party compressed mismatch evidence")
    output = bytearray()
    cursor = len(COMPLETE_VECTOR_MAGIC)
    while cursor < len(payload):
        control = payload[cursor]
        cursor += 1
        if control & 0x80:
            need(cursor + 2 <= len(payload),
                 "reject a truncated complete mismatch back-reference")
            distance = int.from_bytes(payload[cursor:cursor + 2], "big")
            cursor += 2
            length = (control & 0x7f) + 3
            need(0 < distance <= len(output)
                 and len(output) + length <= expected_size,
                 "reject crossed or expanded complete mismatch evidence")
            for _ in range(length):
                output.append(output[-distance])
        else:
            length = control + 1
            need(cursor + length <= len(payload)
                 and len(output) + length <= expected_size,
                 "reject truncated or expanded complete mismatch literals")
            output.extend(payload[cursor:cursor + length])
            cursor += length
    need(len(output) == expected_size,
         "reject incomplete lossless original mismatch evidence")
    return bytes(output)


def encode_complete_c_mismatches(records: object,
                                 producer: types.ModuleType,
                                 history: types.ModuleType,
                                 suite: str, expected: int) -> dict:
    need(type(records) in (list, tuple)
         and type(expected) is int
         and 0 <= expected <= COMPLETE_VECTOR_MAX_RECORDS
         and len(records) == expected
         and suite in {item[0] for item in C10_SUITE_OUTCOMES},
         "preserve every genuine observed C mismatch in original case order")
    summary = history.lossless_vector(
        records, producer, suite_name=suite,
    )
    digest = hashlib.sha256()
    digest.update(b"[")
    complete_chunks: list[dict] = []
    block: list[bytes] = []
    block_bytes = 2
    observed_bytes = 0
    observed_records = 0

    def commit() -> None:
        nonlocal block, block_bytes, observed_bytes
        if not block:
            return
        raw = b"[" + b",".join(block) + b"]\n"
        need(len(raw) <= COMPLETE_VECTOR_CHUNK_BYTES,
             "bound every complete original counterexample chunk")
        compressed = c11_compress(raw)
        need(c11_decompress(compressed, len(raw)) == raw,
             "require byte-exact first-party mismatch compression")
        decoded = producer.JsonReader(raw).parse()
        need(type(decoded) is list and len(decoded) == len(block),
             "reject missing complete frozen counterexample observations")
        complete_chunks.append({
            "index": len(complete_chunks),
            "first_record_index": observed_records - len(block),
            "record_count": len(block),
            "uncompressed_bytes": len(raw),
            "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
            "compressed_bytes": len(compressed),
            "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
            "codec": "FIRST-PARTY C11 BOUNDED LZ1",
            "complete_compressed_base64": c11_base64_encode(compressed),
        })
        observed_bytes += len(raw)
        need(observed_bytes <= COMPLETE_VECTOR_UNCOMPRESSED_BYTES,
             "bound the complete genuine original mismatch archive")
        block = []
        block_bytes = 2

    for index, actual in enumerate(records):
        normalized = history.normalize_transport(actual, producer)
        encoded = producer.canonical(normalized)
        need(encoded.endswith(b"\n")
             and len(encoded) + 2 <= COMPLETE_VECTOR_CHUNK_BYTES,
             "bound each exact original mismatch after real comparison")
        encoded = encoded[:-1]
        prospective = block_bytes + len(encoded) + (1 if block else 0)
        if block and (
            len(block) >= COMPLETE_VECTOR_CHUNK_RECORDS
            or prospective > COMPLETE_VECTOR_CHUNK_BYTES
        ):
            commit()
            prospective = 2 + len(encoded)
        if index:
            digest.update(b",")
        digest.update(encoded)
        block.append(encoded)
        block_bytes = prospective
        observed_records += 1
    commit()
    digest.update(b"]\n")
    need(observed_records == expected
         and summary.get("total_count") == expected
         and summary.get("transport_complete_vector_sha256")
         == digest.hexdigest(),
         "reject a discarded, reordered, normalized-before-comparison mismatch")
    result = {
        **summary,
        "schema": SCHEMA + "-lossless-original-mismatch-vector",
        "suite": suite,
        "all_observed_records_preserved": True,
        "complete_record_count": expected,
        "complete_chunk_count": len(complete_chunks),
        "complete_chunks": complete_chunks,
        "complete_vector_embedded": True,
        "preview_truncated": bool(summary.get("truncated")),
        "truncated": False,
        "transport_complete_vector_sha256": digest.hexdigest(),
        "compression_stage": "ONLY AFTER COMPLETE ORIGINAL OBSERVATION",
        "source_comparison_modified": False,
    }
    validate_complete_c_mismatches(
        result, producer, suite, expected,
    )
    return result


def validate_complete_c_mismatches(value: object,
                                   producer: types.ModuleType,
                                   suite: str, expected: int) -> dict:
    need(type(value) is dict
         and value.get("schema")
         == SCHEMA + "-lossless-original-mismatch-vector"
         and value.get("suite") == suite
         and value.get("all_observed_records_preserved") is True
         and value.get("complete_vector_embedded") is True
         and value.get("truncated") is False
         and value.get("source_comparison_modified") is False
         and value.get("compression_stage")
         == "ONLY AFTER COMPLETE ORIGINAL OBSERVATION"
         and type(expected) is int
         and 0 <= expected <= COMPLETE_VECTOR_MAX_RECORDS
         and value.get("complete_record_count") == expected
         and value.get("total_count") == expected,
         "reject missing, false, or cross-suite complete C counterexamples")
    chunks = value.get("complete_chunks")
    need(type(chunks) is list
         and value.get("complete_chunk_count") == len(chunks)
         and (bool(chunks) == (expected > 0)),
         "reject omitted or invented complete C mismatch chunks")
    digest = hashlib.sha256()
    digest.update(b"[")
    position = 0
    total_bytes = 0
    required_keys = {
        "index", "first_record_index", "record_count",
        "uncompressed_bytes", "uncompressed_sha256",
        "compressed_bytes", "compressed_sha256",
        "codec", "complete_compressed_base64",
    }
    for index, chunk in enumerate(chunks):
        need(type(chunk) is dict
             and set(chunk) == required_keys
             and chunk.get("index") == index
             and chunk.get("first_record_index") == position
             and type(chunk.get("record_count")) is int
             and 0 < chunk["record_count"]
             <= COMPLETE_VECTOR_CHUNK_RECORDS
             and type(chunk.get("uncompressed_bytes")) is int
             and 0 < chunk["uncompressed_bytes"]
             <= COMPLETE_VECTOR_CHUNK_BYTES
             and chunk.get("codec") == "FIRST-PARTY C11 BOUNDED LZ1",
             "reject a missing, duplicated, crossed, or unbounded vector chunk")
        compressed = c11_base64_decode(
            chunk["complete_compressed_base64"]
        )
        need(len(compressed) == chunk.get("compressed_bytes")
             and hashlib.sha256(compressed).hexdigest()
             == chunk.get("compressed_sha256"),
             "reject substituted complete compressed C counterexamples")
        raw = c11_decompress(compressed, chunk["uncompressed_bytes"])
        need(hashlib.sha256(raw).hexdigest()
             == chunk.get("uncompressed_sha256")
             and raw.startswith(b"[") and raw.endswith(b"]\n"),
             "reject substituted or truncated original vector chunk")
        records = producer.JsonReader(raw).parse()
        need(type(records) is list
             and len(records) == chunk["record_count"],
             "reject omitted or fabricated original mismatch records")
        for record in records:
            canonical = producer.canonical(record)
            need(canonical.endswith(b"\n"),
                 "preserve the original canonical case newline")
            if position:
                digest.update(b",")
            digest.update(canonical[:-1])
            position += 1
        total_bytes += len(raw)
        need(total_bytes <= COMPLETE_VECTOR_UNCOMPRESSED_BYTES,
             "reject unbounded complete archived mismatch evidence")
    digest.update(b"]\n")
    need(position == expected
         and value.get("transport_complete_vector_sha256")
         == digest.hexdigest(),
         "reject a truncated, reordered, or digest-substituted full vector")
    return {
        "record_count": position,
        "chunk_count": len(chunks),
        "transport_complete_vector_sha256": digest.hexdigest(),
        "all_observed_records_preserved": True,
    }


def validate_c10_actual_receipt(receipt: object,
                               historical: types.ModuleType) -> dict:
    need(type(receipt) is dict
         and receipt.get("schema")
         == "rebar-owned-repaired-c-original-campaign-v10-"
            "durable-publication-receipt"
         and receipt.get("version") == 10
         and receipt.get("status") == "PASS"
         and receipt.get("publication_status") == "PASS"
         and receipt.get("publication_pass_means")
         == "DURABLE CORRECTNESS PUBLICATION ONLY"
         and receipt.get("family") == "c"
         and receipt.get("label")
         == "phase2-v21-c-original-match-semantics-original-p0-v10"
         and receipt.get("source_sha256") == C10[0][1]
         and receipt.get("protocol_sha256") == C10[1][1]
         and receipt.get("contract_sha256") == C10[2][1]
         and receipt.get("candidate_status") == "FAIL"
         and receipt.get("candidate_qualified") is False
         and receipt.get("suite_count") == 13
         and receipt.get("attempted_suite_count") == 13
         and receipt.get("completed_suite_count") == 8
         and receipt.get("case_execution_denominator") == 31237
         and receipt.get("actual_candidate_workers") == 13
         and receipt.get("candidate_execution_failure_count") == 5
         and receipt.get("infrastructure_failure_count") == 0
         and receipt.get("worker_timeout_count") == 0
         and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
         and receipt.get("observed_semantic_mismatch_lower_bound") == 606
         and receipt.get("verified_passing_case_count") == 13606
         and receipt.get("named_private_waiver_count") == 13
         and receipt.get("separate_reference_case_count") == 8244
         and receipt.get("separate_reference_cases_counted_as_candidate_cases")
         is False
         and receipt.get("actual_c21_build_receipt_sha256")
         == historical.C21_BUILD_RECEIPT[1]
         and receipt.get("actual_c21_root_receipt_sha256")
         == historical.C21_ROOT_RECEIPT[1]
         and receipt.get("corrected_source_sha256")
         == historical.C21_VARIANT_SHA256
         and receipt.get("native_engine_sha256")
         == historical.C21_NATIVE_SHA256
         and receipt.get("native_bridge_sha256")
         == historical.C21_NATIVE_SHA256
         and receipt.get("original_native_inode_restored") is True
         and receipt.get("original_source_targets_modified") == 0
         and receipt.get("expanded_holdout_proposed_case_count") == 14155776
         and receipt.get("hidden_cases_read") == 0
         and receipt.get("benchmark_files_read") == 0
         and receipt.get("clock_samples") == 0
         and receipt.get("timing_trials_run") == 0
         and receipt.get("holdout") == "NOT OPENED"
         and receipt.get("performance") == "NOT MEASURED"
         and receipt.get("winner_selected") is False,
         "preserve the exact genuine incomplete C V10 campaign and its losses")
    archive = receipt.get("archive")
    need(type(archive) is dict
         and archive.get("sha256")
         == "35b36907e699546b77d36bb7c5eea96fee5ce2fc1022b0c0f1eefe652128cc37"
         and archive.get("bytes") == 52085
         and archive.get("inode") == 525474
         and archive.get("mode") == "0600"
         and archive.get("nlink") == 1
         and archive.get("exclusive_creation") is True
         and archive.get("file_fsync_completed") is True
         and archive.get("directory_fsync_completed") is True,
         "pin genuine V10 archive metadata without opening compressed evidence")
    outcomes = receipt.get("suite_outcomes")
    processes = receipt.get("actual_worker_process_ids")
    need(type(outcomes) is list and len(outcomes) == 13
         and type(processes) is list and len(processes) == 13
         and all(type(value) is int and value > 0 for value in processes)
         and len(set(processes)) == 13
         and receipt.get("actual_worker_process_ids_are_distinct") is True,
         "preserve all genuine C10 workers without invented execution")
    mismatches = 0
    incomplete = 0
    passing = 0
    for row, expected, pid in zip(
        outcomes, C10_SUITE_OUTCOMES, processes, strict=True,
    ):
        name, count, status, category, observed = expected
        need(type(row) is dict
             and row.get("suite") == name
             and row.get("case_execution_denominator") == count
             and row.get("status") == status
             and row.get("failure_class") == category
             and row.get("actual_candidate_workers") == 1
             and row.get("worker_process_id") == pid,
             "preserve each authentic published C10 suite: " + name)
        if observed is None:
            need(row.get("mismatch_count") == "NOT MEASURED",
                 "never invent C10 mismatches for an aborted original case")
            incomplete += 1
        else:
            need(row.get("mismatch_count") == observed,
                 "preserve every actual original C10 observed mismatch")
            mismatches += observed
            if observed == 0:
                passing += count
    need(mismatches == 606 and incomplete == 5
         and passing == 13606
         and sum(item[1] for item in C10_SUITE_OUTCOMES) == 31237,
         "reject a changed historical mismatch or full original denominator")
    return receipt


def c11_vector_hostile_controls(producer: types.ModuleType,
                                 history: types.ModuleType) -> list[str]:
    controls: list[str] = []
    original = [
        {"case": "source-only-original-" + str(index),
         "expected": {"value": "expected-" + str(index % 19)},
         "actual": {"value": "observed-" + str(index % 23)}}
        for index in range(606)
    ]
    full = encode_complete_c_mismatches(
        original, producer, history, "public_surface_v19", len(original),
    )
    observed = validate_complete_c_mismatches(
        full, producer, "public_surface_v19", len(original),
    )
    need(observed["record_count"] == 606
         and full["complete_chunk_count"] > 1
         and full["preview_truncated"] is True
         and full["truncated"] is False
         and full["all_observed_records_preserved"] is True,
         "reject the historical 24-record prefix as complete counterevidence")
    controls.append("preserve all 606 individual genuine-sized mismatch controls")
    controls.append("preserve all 514 historically unrecorded-sized controls")

    def reject(label: str, changed: dict, count: int = 606,
               suite: str = "public_surface_v19") -> None:
        refused = False
        try:
            validate_complete_c_mismatches(changed, producer, suite, count)
        except (CampaignError, ValueError, TypeError, producer.ProducerError):
            refused = True
        need(refused, "accept incomplete complete-vector evidence: " + label)
        controls.append(label)

    def copy_vector() -> dict:
        return {
            **full,
            "complete_chunks": [dict(chunk)
                                for chunk in full["complete_chunks"]],
        }

    missing = copy_vector()
    missing["complete_chunks"] = missing["complete_chunks"][:-1]
    missing["complete_chunk_count"] = len(missing["complete_chunks"])
    reject("reject dropped genuine mismatch chunk", missing)

    truncated = copy_vector()
    truncated["truncated"] = True
    reject("reject a falsely complete truncated mismatch vector", truncated)

    forged_count = copy_vector()
    forged_count["complete_record_count"] -= 1
    reject("reject invented complete mismatch record count", forged_count)

    crossed_suite = copy_vector()
    crossed_suite["suite"] = "scanner_v3"
    reject("reject cross-suite complete original mismatch vectors", crossed_suite)

    forged_digest = copy_vector()
    forged_digest["transport_complete_vector_sha256"] = "0" * 64
    reject("reject substituted complete original vector digest", forged_digest)

    broken_chunk = copy_vector()
    broken_chunk["complete_chunks"][0]["uncompressed_sha256"] = "0" * 64
    reject("reject substituted archived original mismatch bytes", broken_chunk)

    bad_compression = copy_vector()
    bad_compression["complete_chunks"][0]["compressed_sha256"] = "0" * 64
    reject("reject substituted compressed original mismatch bytes", bad_compression)

    wrong_index = copy_vector()
    wrong_index["complete_chunks"][0]["first_record_index"] = 1
    reject("reject reordered complete original mismatch chunks", wrong_index)

    missing_payload = copy_vector()
    missing_payload["complete_chunks"][0]["complete_compressed_base64"] = ""
    reject("reject missing complete compressed counterexample payload",
           missing_payload)

    duplicate = copy_vector()
    duplicate["complete_chunks"][1] = dict(
        duplicate["complete_chunks"][0]
    )
    reject("reject duplicated complete original mismatch chunk", duplicate)

    wrong_codec = copy_vector()
    wrong_codec["complete_chunks"][0]["codec"] = "EXTERNAL REGEX ENGINE"
    reject("reject external or substituted mismatch archive codec", wrong_codec)

    changed_comparison = copy_vector()
    changed_comparison["source_comparison_modified"] = True
    reject("reject normalization before true original case comparison",
           changed_comparison)

    empty = encode_complete_c_mismatches(
        [], producer, history, "shape_v2", 0,
    )
    need(validate_complete_c_mismatches(
        empty, producer, "shape_v2", 0,
    )["record_count"] == 0,
         "reject a falsely invented counterexample for a passing suite")
    controls.append("preserve zero real mismatches without invented failures")

    samples = (b"", b"x", b"xy", b"xyz",
               b"literal" * 80, bytes(range(256)) * 3)
    for sample in samples:
        need(c11_base64_decode(c11_base64_encode(sample)) == sample
             and c11_decompress(c11_compress(sample), len(sample)) == sample,
             "reject a lossy first-party source-only mismatch codec")
    controls.append("prove pure first-party compressed payload round trips")
    return controls


def c11_route_hostile_controls(old: types.ModuleType) -> list[str]:
    controls: list[str] = []
    for owner, function_name, line, keyword in (
        (C_ROUTE_ORIGINAL, "authenticate_original_sources", 211, "candidate"),
        (C_ROUTE_DIRECT_CORE, "load_prerequisites",
         483, "candidate_loaded"),
    ):
        raw = old.read_owner(owner)
        repaired = clean_c_observer_route(
            raw, owner, function_name, line, keyword,
        )
        need(raw != repaired
             and hashlib.sha256(raw).hexdigest() == owner[1]
             and (
                 "verify_runtime(" + keyword + "=True)"
             ).encode("ascii") in repaired,
             "authenticate one genuine candidate-only source overlay")
        controls.append("authenticate only C-selected " + function_name)
        variants = (
            ("wrong line", line + 1),
            ("wrong keyword",
             "candidate_loaded" if keyword == "candidate" else "candidate"),
            ("wrong function",
             "load_prerequisites" if keyword == "candidate"
             else "authenticate_original_sources"),
        )
        for label, changed in variants:
            refused = False
            try:
                if label == "wrong line":
                    clean_c_observer_route(
                        raw, owner, function_name, changed, keyword,
                    )
                elif label == "wrong keyword":
                    clean_c_observer_route(
                        raw, owner, function_name, line, changed,
                    )
                else:
                    clean_c_observer_route(
                        raw, owner, changed, line, keyword,
                    )
            except (CampaignError, ValueError, SyntaxError):
                refused = True
            need(refused,
                 "accept weakened original-only candidate route: " + label)
            controls.append("reject " + label + " for " + function_name)
        invented = raw.replace(
            b"    verify_runtime()\n",
            b"    verify_runtime(candidate=True)\n",
            1,
        )
        refused = False
        try:
            clean_c_observer_route(
                invented, owner, function_name, line, keyword,
            )
        except (CampaignError, ValueError, SyntaxError):
            refused = True
        need(refused,
             "accept already altered immutable source-owner evidence")
        controls.append("reject changed immutable source " + function_name)
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "never run a C candidate or weaken the source-only matcher wall")
    controls.append("preserve matcher-free candidate-only route isolation")
    return controls




def lossless_c11_protected_worker(
    parsed: dict, producer: types.ModuleType, state: dict,
    previous: types.ModuleType, history: types.ModuleType,
    module: types.ModuleType,
) -> dict:
    """Archive every mismatch only after the immutable comparison has run."""
    try:
        row = previous.actual_worker(parsed, producer, state)
        need(type(row) is dict
             and row.get("suite") == parsed.get("--suite")
             and row.get("actual_candidate_workers") == 1,
             "preserve exactly one genuine guarded original C worker")
        observed = row.get("original_observation")
        if type(observed) is dict:
            compact = dict(observed)
            records = compact.get("candidate_records")
            if type(records) in (list, tuple):
                compact["candidate_records"] = history.lossless_vector(
                    records, producer,
                    expected=compact.get("candidate_records_sha256"),
                    suite_name=parsed.get("--suite"),
                )
                need(
                    compact["candidate_records"]["total_count"]
                    == compact.get(
                        "actual_candidate_case_count",
                        compact["candidate_records"]["total_count"],
                    ),
                    "preserve the genuine complete original case denominator",
                )
            mismatches = compact.get("all_mismatches")
            mismatch_count = row.get("mismatch_count")
            if type(mismatches) in (list, tuple):
                need(type(mismatch_count) is int
                     and len(mismatches) == mismatch_count,
                     "never discard a real original semantic counterexample")
                compact["all_mismatches"] = (
                    encode_complete_c_mismatches(
                        mismatches, producer, history,
                        parsed["--suite"], mismatch_count,
                    )
                )
                row["all_observed_semantic_mismatch_records_preserved"] = True
                row["complete_observed_semantic_mismatch_record_count"] = (
                    mismatch_count
                )
                row["complete_observed_semantic_mismatch_chunk_count"] = (
                    compact["all_mismatches"]["complete_chunk_count"]
                )
                row["complete_observed_semantic_mismatch_vector_sha256"] = (
                    compact["all_mismatches"]
                    ["transport_complete_vector_sha256"]
                )
            else:
                need(mismatch_count == 0,
                     "reject a mismatch count lacking every original record")
                compact["all_mismatches"] = (
                    encode_complete_c_mismatches(
                        [], producer, history,
                        parsed["--suite"], 0,
                    )
                )
                row["all_observed_semantic_mismatch_records_preserved"] = True
                row["complete_observed_semantic_mismatch_record_count"] = 0
                row["complete_observed_semantic_mismatch_chunk_count"] = (
                    compact["all_mismatches"]["complete_chunk_count"]
                )
                row["complete_observed_semantic_mismatch_vector_sha256"] = (
                    compact["all_mismatches"]
                    ["transport_complete_vector_sha256"]
                )
            row["original_observation"] = history.normalize_transport(
                compact, producer,
            )
            row["all_original_records_and_mismatches_preserved"] = bool(
                type(records) not in (list, tuple)
                or len(records) <= history.MAX_VECTOR_PREFIX
            )
            row["all_original_record_and_mismatch_digests_preserved"] = True
            row["original_record_prefix_explicitly_truncated"] = bool(
                type(records) in (list, tuple)
                and len(records) > history.MAX_VECTOR_PREFIX
            )
            row["lossless_mismatch_archival_stage"] = (
                "ONLY AFTER COMPLETE IMMUTABLE ORIGINAL COMPARISON"
            )
        if row.get("status") == "FAIL":
            details = row.get("complete_genuine_failure_details")
            error_type, message, chain = history.nested_failure_details(
                details
            )
            if error_type == "NOT ESTABLISHED":
                error_type = str(
                    row.get("error_type", "CandidateError")
                )
                message = str(
                    row.get("error_message",
                            "guarded original case failed")
                )
            row["complete_genuine_failure_details"] = (
                history.normalize_transport(details, producer)
            )
            row["literal_original_failure_chain"] = (
                history.normalize_transport(chain, producer)
            )
            row["plain_failure_diagnostic"] = (
                error_type + ": " + message
            )[:module.MAX_SUMMARY_DIAGNOSTIC]
            row.setdefault(
                "failure_phase", "OBSERVE COMPLETE ORIGINAL SUITE",
            )
        row.setdefault(
            "observed_semantic_mismatch_lower_bound",
            row.get("mismatch_count", 0)
            if type(row.get("mismatch_count")) is int else 0,
        )
        encoded = producer.canonical(
            history.normalize_transport(row, producer)
        )
        need(len(encoded) <= module.MAX_WORKER_STDOUT
             and len(encoded) < producer.MAX_JSON_BYTES,
             "never truncate or publish oversized complete C mismatch evidence")
        decoded = producer.JsonReader(encoded).parse()
        need(type(decoded) is dict
             and decoded.get("schema")
             == SCHEMA + "-actual-original-worker"
             and decoded.get("suite") == parsed.get("--suite"),
             "strictly round-trip the entire actual lossless C11 worker")
        if type(decoded.get("mismatch_count")) is int:
            count = decoded["mismatch_count"]
            need(
                decoded.get(
                    "all_observed_semantic_mismatch_records_preserved"
                ) is True
                and decoded.get(
                    "complete_observed_semantic_mismatch_record_count"
                ) == count,
                "never claim preserved mismatches without complete records",
            )
            observation = decoded.get("original_observation")
            if count or (
                type(observation) is dict
                and type(observation.get("all_mismatches")) is dict
            ):
                need(type(observation) is dict,
                     "reject an invented completed original observation")
                full = observation.get("all_mismatches")
                validate_complete_c_mismatches(
                    full, producer, parsed["--suite"], count,
                )
        return decoded
    except Exception as error:
        return module.early_worker_failure(
            parsed, error, "ENCODE COMPLETE GUARDED RESULT", previous,
        )


def collect_complete_c11_vectors(
    document: dict, producer: types.ModuleType,
) -> dict:
    rows = document.get("suite_results")
    need(type(rows) is list and len(rows) == 13
         and document.get("case_execution_denominator") == 31237
         and document.get("suite_count") == 13,
         "require every genuine complete or unfinished original C11 suite")
    preserved = 0
    complete = 0
    chunks = 0
    fingerprints: list[dict] = []
    for row, expected in zip(
        rows, C10_SUITE_OUTCOMES, strict=True,
    ):
        name, count, _, _, _ = expected
        need(type(row) is dict
             and row.get("suite") == name
             and row.get("case_execution_denominator") == count,
             "reject omitted or reordered original suite: " + name)
        mismatch = row.get("mismatch_count")
        if type(mismatch) is not int:
            need(mismatch == "NOT MEASURED",
                 "reject an invented incomplete original mismatch count")
            continue
        need(0 <= mismatch <= count
             and row.get(
                 "all_observed_semantic_mismatch_records_preserved"
             ) is True
             and row.get(
                 "complete_observed_semantic_mismatch_record_count"
             ) == mismatch,
             "reject any completed suite with missing mismatch records")
        observed = row.get("original_observation")
        need(type(observed) is dict,
             "reject a completed suite without its source observation")
        vector = observed.get("all_mismatches")
        evidence = validate_complete_c_mismatches(
            vector, producer, name, mismatch,
        )
        need(row.get(
            "complete_observed_semantic_mismatch_vector_sha256"
        ) == evidence["transport_complete_vector_sha256"],
             "reject a substituted full original counterexample digest")
        preserved += mismatch
        complete += 1
        chunks += evidence["chunk_count"]
        fingerprints.append({
            "suite": name,
            "case_execution_denominator": count,
            "complete_record_count": mismatch,
            "complete_chunk_count": evidence["chunk_count"],
            "complete_vector_sha256":
            evidence["transport_complete_vector_sha256"],
            "all_observed_records_preserved": True,
        })
    need(preserved == document.get(
        "observed_semantic_mismatch_lower_bound"
    )
         and complete == document.get("completed_suite_count"),
         "never discard even one genuinely observed original mismatch")
    return {
        "all_observed_semantic_mismatch_records_preserved": True,
        "complete_observed_semantic_mismatch_record_count": preserved,
        "complete_mismatch_suite_count": complete,
        "complete_mismatch_chunk_count": chunks,
        "complete_mismatch_suite_vector_fingerprints": fingerprints,
        "complete_counterexample_archive":
        "ALL RECORDS IN THE EXCLUSIVE DIGEST-BOUND MAIN COMPRESSED ARCHIVE",
        "counterexample_compression":
        "FIRST-PARTY C11 LZ1; ACTUAL FIRST-PARTY GZIP ARCHIVE",
        "counterexample_observation_order": "EXACT ORIGINAL SUITE AND CASE ORDER",
        "counterexample_normalization_before_original_comparison": False,
        "counterexample_preview_only": False,
    }


def publish_lossless_c11_evidence(
    document: dict, producer: types.ModuleType,
    previous: types.ModuleType, capture: dict,
) -> dict:
    need(type(document) is dict
         and document.get("schema") == SCHEMA + "-actual-original-campaign"
         and document.get("family") == "c"
         and document.get("label") == LABEL
         and document.get("original_native_inode_restored") is True
         and document.get("hidden_cases_read") == 0
         and document.get("benchmark_files_read") == 0
         and document.get("clock_samples") == 0
         and document.get("timing_trials_run") == 0
         and document.get("holdout") == "NOT OPENED"
         and document.get("performance") == "NOT MEASURED",
         "publish only a genuinely restored complete first-party C campaign")
    vectors = collect_complete_c11_vectors(document, producer)
    document.update(vectors)
    document["successfully_returned_guarded_interpreter_creations"] = (
        "NOT MEASURED"
    )
    document["transient_physical_interpreter_creations"] = "NOT MEASURED"
    document["zero_returned_creations_proves_zero_physical_creations"] = False
    gzip = __import__("gzip")
    raw = producer.canonical(document)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    suffix = "results" if document["candidate_status"] == "PASS" else "failures"
    stem = (
        "repaired-c-original-campaign-v11-c-"
        + LABEL + "-" + suffix
    )
    evidence = ROOT + "/oracle/phase2/evidence"

    def publish(name: str, payload: bytes) -> dict:
        parent = previous.directory(evidence, device=DEVICE)
        handle = None
        try:
            handle = os.open(
                name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600, dir_fd=parent,
            )
            before = os.fstat(handle)
            need(stat.S_ISREG(before.st_mode)
                 and before.st_dev == DEVICE
                 and before.st_uid == os.geteuid()
                 and before.st_nlink == 1
                 and stat.S_IMODE(before.st_mode) == 0o600,
                 "exclusively create one owner-only C11 evidence inode")
            previous.write_all(handle, payload)
            os.fsync(handle)
            after = os.fstat(handle)
            need((before.st_dev, before.st_ino)
                 == (after.st_dev, after.st_ino)
                 and after.st_size == len(payload),
                 "reject incomplete or substituted durable C11 evidence")
            os.close(handle)
            handle = None
            os.fsync(parent)
            return {
                "path": "oracle/phase2/evidence/" + name,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "device": after.st_dev,
                "inode": after.st_ino,
                "mode": "0600",
                "nlink": 1,
                "exclusive_creation": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True,
            }
        finally:
            if handle is not None:
                os.close(handle)
            os.close(parent)

    archive = publish(stem + ".json.gz", compressed)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "version": 11,
        "family": "c",
        "label": LABEL,
        "candidate_status": document["candidate_status"],
        "candidate_qualified": document["candidate_qualified"],
        "source_sha256": document["source_sha256"],
        "protocol_sha256": document["protocol_sha256"],
        "contract_sha256": document["contract_sha256"],
        "preserved_actual_v6_failure_receipt_sha256":
        document["preserved_actual_v6_failure_receipt_sha256"],
        "preserved_actual_v7_failure_receipt_sha256":
        previous.actual_authority()[
            "previous_v7_failure_receipt_sha256"
        ],
        "preserved_actual_v9_failure_receipt_sha256":
        C9_RECEIPT[1],
        "preserved_actual_v10_failure_receipt_sha256":
        C10_RECEIPT[1],
        "actual_c21_build_receipt_sha256":
        previous.BUILD_RECEIPT[1],
        "actual_c21_root_receipt_sha256":
        previous.ROOT_RECEIPT[1],
        "corrected_source_sha256":
        previous.CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256":
        previous.ADAPTER[1],
        "native_engine_sha256":
        previous.NATIVE_SHA256,
        "native_bridge_sha256":
        previous.NATIVE_SHA256,
        "suite_count":
        len(previous.SUITES),
        "case_execution_denominator":
        previous.ORIGINAL_CASE_COUNT,
        "named_private_waiver_count":
        13,
        "separate_reference_case_count":
        previous.SEPARATE_REFERENCE_CASE_COUNT,
        "separate_reference_cases_counted_as_candidate_cases":
        False,
        "worker_timeout_seconds":
        document["worker_timeout_seconds"],
        "original_source_targets_modified":
        0,
        "original_native_inode_restored":
        document["original_native_inode_restored"],
        "archive": archive,
        "uncompressed_bytes": len(raw),
        "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
        "expanded_holdout_proposed_case_count":
        previous.EXPANDED_PROPOSED_CASE_COUNT,
        "all_observed_semantic_mismatch_records_preserved":
        vectors["all_observed_semantic_mismatch_records_preserved"],
        "complete_observed_semantic_mismatch_record_count":
        vectors["complete_observed_semantic_mismatch_record_count"],
        "complete_mismatch_suite_count":
        vectors["complete_mismatch_suite_count"],
        "complete_mismatch_chunk_count":
        vectors["complete_mismatch_chunk_count"],
        "complete_mismatch_suite_vector_fingerprints":
        vectors["complete_mismatch_suite_vector_fingerprints"],
        "complete_counterexample_archive":
        vectors["complete_counterexample_archive"],
        "counterexample_normalization_before_original_comparison":
        False,
        "counterexample_preview_only":
        False,
        "successfully_returned_guarded_interpreter_creations":
        "NOT MEASURED",
        "transient_physical_interpreter_creations":
        "NOT MEASURED",
        "zero_returned_creations_proves_zero_physical_creations":
        False,
        "hidden_cases_read":
        0,
        "benchmark_files_read":
        0,
        "clock_samples":
        0,
        "timing_trials_run":
        0,
        "performance":
        "NOT MEASURED",
        "memory":
        "NOT MEASURED",
        "undefined_behavior":
        "NOT MEASURED",
        "holdout":
        "NOT OPENED",
        "winner_selected":
        False,
    }
    for key in (
        "suite_outcomes", "attempted_suite_count",
        "completed_suite_count", "actual_candidate_workers",
        "actual_worker_process_ids",
        "actual_worker_process_ids_are_distinct",
        "semantic_mismatch_count",
        "observed_semantic_mismatch_lower_bound",
        "verified_passing_case_count",
        "infrastructure_failure_count",
        "candidate_execution_failure_count", "worker_timeout_count",
    ):
        receipt[key] = document[key]
    need(receipt["complete_observed_semantic_mismatch_record_count"]
         == receipt["observed_semantic_mismatch_lower_bound"]
         and receipt["complete_mismatch_suite_count"]
         == receipt["completed_suite_count"]
         and all(
             item["all_observed_records_preserved"] is True
             for item
             in receipt["complete_mismatch_suite_vector_fingerprints"]
         ),
         "never durably publish a missing original counterexample")
    owner = publish(
        stem + "-publication-receipt.json",
        producer.canonical(receipt),
    )
    capture.clear()
    capture.update({
        "all_observed_semantic_mismatch_records_preserved": True,
        "complete_observed_semantic_mismatch_record_count":
        receipt["complete_observed_semantic_mismatch_record_count"],
        "complete_mismatch_suite_count":
        receipt["complete_mismatch_suite_count"],
        "complete_mismatch_chunk_count":
        receipt["complete_mismatch_chunk_count"],
        "complete_counterexample_archive_owner": archive,
    })
    return {
        "archive": archive,
        "receipt": receipt,
        "receipt_owner": owner,
    }



def install_v11(historical: types.ModuleType, history: types.ModuleType,
                module: types.ModuleType, transform: dict) -> None:
    historical_configure = module.configure_previous
    historical_contract = module.contract_document
    historical_controls = module.source_controls

    def whole_source_callable(selected: object, owner: tuple,
                              function_name: str) -> types.FunctionType:
        need = history.need
        relative, expected, _, _ = owner
        module_name = relative.removesuffix(".py").replace("/", ".")
        function = getattr(selected, function_name, None)
        absolute = ROOT + "/" + relative
        need(type(selected) is types.ModuleType
             and selected.__name__ == module_name
             and sys.modules.get(module_name) is selected
             and os.path.abspath(getattr(selected, "__file__", "")) == absolute
             and getattr(selected, "SOURCE_RELATIVE", None) == relative
             and type(function) is types.FunctionType
             and function.__module__ == module_name
             and function.__globals__ is selected.__dict__
             and os.path.abspath(function.__code__.co_filename) == absolute,
             "reject an unowned, replaced, or crossed frozen source callable: "
             + module_name + "." + function_name)
        cache_key = (module_name, function_name)
        cache = history.SOURCE_ATTESTATIONS.get(cache_key)
        if cache is not None:
            need(cache == (selected, function, function.__code__, expected),
                 "reject replacement of an authenticated whole-source callable")
            return function
        raw = history.read_historical(owner)
        tree = ast.parse(raw.decode("utf-8", "strict"), filename=absolute)
        definitions = [item for item in tree.body
                       if isinstance(item, ast.FunctionDef)
                       and item.name == function_name]
        need(len(definitions) == 1,
             "require exactly one authenticated original top-level function")
        complete = compile(tree, absolute, "exec", dont_inherit=True)
        candidates = [item for item in complete.co_consts
                      if type(item) is types.CodeType
                      and item.co_name == function_name
                      and item.co_qualname == function_name
                      and item.co_firstlineno == definitions[0].lineno]
        need(len(candidates) == 1,
             "require the unique genuine unexecuted full-source function code")
        actual = function.__code__
        reference = candidates[0]
        fields = (
            "co_code", "co_consts", "co_names", "co_varnames",
            "co_freevars", "co_cellvars", "co_argcount",
            "co_posonlyargcount", "co_kwonlyargcount", "co_flags",
            "co_stacksize", "co_firstlineno", "co_qualname",
            "co_filename", "co_exceptiontable", "co_linetable",
        )
        need(all(getattr(actual, field) == getattr(reference, field)
                 for field in fields),
             "reject a replaced, fabricated, or partial whole-source callable: "
             + module_name + "." + function_name)
        history.SOURCE_ATTESTATIONS[cache_key] = (
            selected, function, actual, expected
        )
        return function

    history.attest_source_callable = whole_source_callable

    def configure(previous: types.ModuleType) -> tuple:
        old, original_contract = historical_configure(previous)
        additions = (
            C9 + C10 + V3
            + (C9_RECEIPT, C10_RECEIPT,
               C_ROUTE_ORIGINAL, C_ROUTE_DIRECT_CORE,
               C_ROUTE_DIRECT_GATE)
        )
        existing = {item[0]: item for item in old.STATIC_OWNERS}
        for owner in additions:
            before = existing.get(owner[0])
            need(before is None or before == owner,
                 "reject crossed C9 receipt, V3 guard, or historical owner")
            if before is None:
                existing[owner[0]] = owner
        for relative in existing:
            need(not relative.startswith(("/", "candidates/", "docs/evidence/"))
                 and not any(word in relative.lower()
                             for word in ("holdout", "benchmark"))
                 and not relative.endswith(
                     (".so", ".gz", ".xz", ".zip", ".tar")
                 ),
                 "physically exclude candidate, private, archive, or holdout")
        old.STATIC_OWNERS = tuple(existing.values())
        old.OWNED_PATHS = frozenset(existing) | {SOURCE, PROTOCOL, CONTRACT}
        previous_authority = previous.actual_authority

        def authority() -> dict:
            actual = previous_authority()
            actual.update({
                "family": "c",
                "label": LABEL,
                "guard_source_sha256": V3[0][1],
                "guard_protocol_sha256": V3[1][1],
                "guard_contract_sha256": V3[2][1],
                "previous_v9_failure_receipt_sha256": C9_RECEIPT[1],
                "previous_v10_failure_receipt_sha256": C10_RECEIPT[1],
                "v10_source_sha256": C10[0][1],
                "v10_protocol_sha256": C10[1][1],
                "v10_contract_sha256": C10[2][1],
                "original_c_harness_source_sha256": C_ROUTE_ORIGINAL[1],
                "original_c_direct_core_source_sha256":
                C_ROUTE_DIRECT_CORE[1],
                "v9_source_sha256": C9[0][1],
                "v9_protocol_sha256": C9[1][1],
                "v9_contract_sha256": C9[2][1],
                "immutable_v2_guard_source_sha256": old.GUARD[0][1],
                "immutable_v2_guard_protocol_sha256": old.GUARD[1][1],
                "immutable_v2_guard_contract_sha256": old.GUARD[2][1],
            })
            return actual

        previous.actual_authority = authority
        previous.install_worker_guard = install_actual_v3_guard
        original_v5_patch = previous.patch_v5_loader

        def patch_selected_c_v5(producer: types.ModuleType) -> dict:
            counts = original_v5_patch(producer)
            selected = producer.family_spec("c")
            policy = producer.active_runtime_policy(selected)
            require_selected_guarded_c(producer, selected, policy)
            return install_c_observer_routes(
                producer, selected, policy, counts,
            )

        previous.patch_v5_loader = patch_selected_c_v5
        previous_collect = previous.collect_context

        def complete_context(frozen: types.ModuleType, parsed: dict,
                             *, controls: bool = False) -> tuple:
            producer, state, result = previous_collect(
                frozen, parsed, controls=controls
            )
            receipt = state.get("actual_v9_receipt")
            c10_actual = state.get("actual_v10_receipt")
            guard = state.get("v3_guard_contract")
            need(type(receipt) is dict
                 and receipt.get("observed_semantic_mismatch_lower_bound") == 492
                 and type(c10_actual) is dict
                 and c10_actual.get("observed_semantic_mismatch_lower_bound")
                 == 606
                 and c10_actual.get("completed_suite_count") == 8
                 and c10_actual.get("candidate_execution_failure_count") == 5
                 and type(guard) is dict and guard.get("version") == 3,
                 "require complete V3 and real C9 history in source evidence")
            result.update({
                "runtime_guard_version": 3,
                "runtime_guard_source_sha256": V3[0][1],
                "runtime_guard_protocol_sha256": V3[1][1],
                "runtime_guard_contract_sha256": V3[2][1],
                "immutable_v2_runtime_guard_source_sha256":
                    frozen.GUARD[0][1],
                "previous_v9_failure_receipt_sha256": C9_RECEIPT[1],
                "previous_v9_mismatch_lower_bound": 492,
                "previous_v9_exact_mismatch_count": "NOT MEASURED",
                "previous_v9_attempted_suite_count": 13,
                "previous_v9_completed_suite_count": 7,
                "previous_v9_candidate_execution_failure_count": 6,
                "previous_v9_verified_passing_case_count": 13606,
                "required_real_subinterpreter_creations": 11,
                "required_real_case_interpreter_exec_calls": 394,
                "required_real_total_interpreter_exec_calls": 416,
                "source_mode_actual_interpreters_created": 0,
                "source_mode_actual_interpreter_exec_calls": 0,
                "source_mode_interpreter_creation_calls": 0,
                "historical_v10_returned_guarded_interpreter_creations":
                "NOT MEASURED",
                "historical_v10_transient_physical_interpreter_creations":
                "NOT MEASURED",
                "future_actual_transient_physical_interpreter_creations":
                "NOT MEASURED",
                "zero_returned_creations_proves_zero_physical_creations":
                False,
                "public_surface_digest_first_source_line": 251,
                "public_surface_digest_monkeypatched": False,
                "frozen_public_surface_source_modified": False,
                "previous_v10_failure_receipt_sha256": C10_RECEIPT[1],
                "previous_v10_mismatch_lower_bound": 606,
                "previous_v10_exact_mismatch_count": "NOT MEASURED",
                "previous_v10_attempted_suite_count": 13,
                "previous_v10_completed_suite_count": 8,
                "previous_v10_candidate_execution_failure_count": 5,
                "previous_v10_verified_passing_case_count": 13606,
                "previous_v10_recorded_counterexample_count": 92,
                "previous_v10_missing_counterexample_count": 514,
                "previous_v10_missing_counterexample_status":
                "NOT RECORDED; NEVER FABRICATED",
                "previous_v10_archive_opened": False,
                "c_only_original_route_call_site_count": 2,
                "c_only_original_harness_source_sha256":
                C_ROUTE_ORIGINAL[1],
                "c_only_direct_core_source_sha256":
                C_ROUTE_DIRECT_CORE[1],
                "source_mode_original_route_overlays_executed": 0,
                "source_mode_full_vector_archive_creations": 0,
                "source_mode_preserved_counterexample_records": 0,
                "full_mismatch_archive_required": True,
                "full_mismatch_prefix_only_permitted": False,
                "comparison_normalization_before_observation": False,
            })
            if parsed["mode"] == "--run":
                publication_capture: dict = {}
                previous_publisher = module.publish_evidence
                previous_campaign = module.run_campaign
                need(type(previous_publisher) is types.FunctionType
                     and type(previous_campaign) is types.FunctionType,
                     "preserve authentic guarded C campaign and publisher")

                def publish_all(document: dict,
                                live_producer: types.ModuleType,
                                live_previous: types.ModuleType) -> dict:
                    need(live_producer is producer
                         and live_previous is previous,
                         "reject crossed actual C counterexample publication")
                    return publish_lossless_c11_evidence(
                        document, live_producer, live_previous,
                        publication_capture,
                    )

                module.publish_evidence = publish_all

                def complete_run(actual: dict,
                                 live_producer: types.ModuleType,
                                 live_state: dict,
                                 live_previous: types.ModuleType) -> dict:
                    need(live_producer is producer
                         and live_state is state
                         and live_previous is previous,
                         "reject crossed original complete C campaign")
                    answer = previous_campaign(
                        actual, live_producer, live_state, live_previous,
                    )
                    need(type(answer) is dict
                         and publication_capture.get(
                             "all_observed_semantic_mismatch_records_preserved"
                         ) is True
                         and publication_capture.get(
                             "complete_observed_semantic_mismatch_record_count"
                         ) == answer.get(
                             "observed_semantic_mismatch_lower_bound"
                         ),
                         "reject durable publication missing any real mismatch")
                    answer.update(publication_capture)
                    return answer

                module.run_campaign = complete_run
            return producer, state, result

        previous.collect_context = complete_context
        need(previous.RECOVERY_ROOT.endswith("-v11")
             and previous.BACKUP_NAME.endswith("v11-original-native")
             and previous.STAGE_NAME.endswith("v11-staged-native")
             and previous.JOURNAL_NAME
             == "original-native-recovery-journal-v11.json",
             "require independently named exact C10 native recovery owners")
        return old, original_contract

    def contract_document(parsed: dict, old: types.ModuleType,
                          state: dict, previous: types.ModuleType,
                          original_contract: object) -> dict:
        producer = old.load_producer(state["producer_raw"])
        c9_raw = old.read_owner(C9[2])
        c9 = previous.parse_document(producer, c9_raw,
                                     "complete immutable C9 frozen contract")
        need(c9.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v9-source-freeze"
             and c9.get("version") == 9
             and c9.get("source", {}).get("sha256") == C9[0][1]
             and c9.get("protocol", {}).get("sha256") == C9[1][1]
             and c9.get("goal_sha256") == old.GOAL[1]
             and c9.get("qualified_candidate_count") == 0
             and c9.get("holdout") == "NOT OPENED"
             and c9.get("performance") == "NOT MEASURED",
             "reject the complete genuinely frozen C9 source history")
        c10 = previous.parse_document(
            producer, old.read_owner(C10[2]),
            "complete immutable C10 first-party frozen source contract",
        )
        need(c10.get("schema")
             == "rebar-owned-repaired-c-original-campaign-v10-source-freeze"
             and c10.get("version") == 10
             and c10.get("source", {}).get("sha256") == C10[0][1]
             and c10.get("protocol", {}).get("sha256") == C10[1][1]
             and c10.get("goal_sha256") == old.GOAL[1]
             and c10.get("qualified_candidate_count") == 0
             and c10.get("holdout") == "NOT OPENED"
             and c10.get("performance") == "NOT MEASURED"
             and c10.get("phase_one_v4", {}).get(
                 "original_case_execution_denominator"
             ) == 31237,
             "preserve the entire unchanged authenticated C10 source freeze")
        guard_raw = old.read_owner(V3[0])
        guard_document = previous.parse_document(
            producer, old.read_owner(V3[2]), "complete immutable V3 guard"
        )
        guard = validate_v3(guard_document, previous, old)
        receipt = previous.parse_document(
            producer, old.read_owner(C9_RECEIPT),
            "small genuinely published complete actual C9 failure receipt",
        )
        validate_c9_receipt(receipt, historical)
        c10_receipt = previous.parse_document(
            producer, old.read_owner(C10_RECEIPT),
            "small immutable genuine C10 complete publication receipt",
        )
        validate_c10_actual_receipt(c10_receipt, historical)
        original_route = old.read_owner(C_ROUTE_ORIGINAL)
        direct_route = old.read_owner(C_ROUTE_DIRECT_CORE)
        gate_route = old.read_owner(C_ROUTE_DIRECT_GATE)
        need(hashlib.sha256(original_route).hexdigest()
             == C_ROUTE_ORIGINAL[1]
             and hashlib.sha256(direct_route).hexdigest()
             == C_ROUTE_DIRECT_CORE[1]
             and hashlib.sha256(gate_route).hexdigest()
             == C_ROUTE_DIRECT_GATE[1],
             "preserve every exact original source-owned C observer route")
        clean_c_observer_route(
            original_route, C_ROUTE_ORIGINAL,
            "authenticate_original_sources", 211, "candidate",
        )
        clean_c_observer_route(
            direct_route, C_ROUTE_DIRECT_CORE,
            "load_prerequisites", 483, "candidate_loaded",
        )
        state["actual_v10_receipt"] = c10_receipt
        state["complete_v10_contract"] = c10
        state["v3_guard_raw"] = guard_raw
        state["v3_guard_contract"] = guard
        state["actual_v9_receipt"] = receipt
        state["complete_v9_contract"] = c9
        base = historical_contract(parsed, old, state,
                                   previous, original_contract)
        need(base.get("schema") == SCHEMA + "-source-freeze"
             and base.get("version") == 11
             and base.get("family") == "c"
             and base.get("label") == LABEL
             and base.get("phase_one_v4", {}).get(
                 "original_case_execution_denominator"
             ) == 31237,
             "reject a reduced or crossed cumulative full C9 campaign")
        policy = dict(base["actual_operation_policy"])
        policy.update({
            "authorization": "EXPLICIT INDEPENDENTLY PINNED C21 C11 --run ONLY",
            "required_authority": previous.actual_authority(),
            "guard_version": 3,
            "true_cpython_audit_hook_before_candidate_import": True,
            "immutable_v2_prepare_family_and_child_source_preserved": True,
            "immutable_v5_producer_source_preserved": True,
            "strict_original_subinterpreter_guard_unchanged": True,
            "strict_original_subinterpreter_owner_field_count": 14,
            "strict_original_subinterpreter_owner_roles": ["bridge", "engine"],
            "required_real_subinterpreter_creations": 11,
            "required_real_subinterpreter_destructions": 11,
            "required_real_case_interpreter_exec_calls": 394,
            "required_real_bootstrap_interpreter_exec_calls": 11,
            "required_real_cleanup_interpreter_exec_calls": 11,
            "required_real_total_interpreter_exec_calls": 416,
            "real_creation_audit_event": "cpython.PyInterpreterState_New",
            "real_creation_audit_event_arguments": "NOT MEASURED",
            "real_creation_count_scope":
            "ONLY SUCCESSFULLY RETURNED AND RECORDED GUARDED CALLS",
            "physical_transient_creation_count": "NOT MEASURED",
            "zero_returned_creations_proves_zero_physical_creations": False,
            "synthetic_or_legacy_creation_audit_events": "FORBIDDEN",
            "public_surface_digest_source": "COMPLETE AUTHENTICATED ORIGINAL MODULE",
            "public_surface_digest_monkeypatch": "FORBIDDEN",
            "public_surface_digest_full_source_code_required": True,
            "previous_actual_v9_receipt_sha256": C9_RECEIPT[1],
            "previous_actual_v9_semantic_mismatch_lower_bound": 492,
            "previous_actual_v9_exact_total_semantic_mismatches": "NOT MEASURED",
            "previous_actual_v9_original_suite_workers": 13,
            "previous_actual_v9_completed_original_suites": 7,
            "previous_actual_v9_original_candidate_execution_failures": 6,
            "source_freeze_runs_candidate": False,
            "previous_actual_v10_receipt_sha256": C10_RECEIPT[1],
            "previous_actual_v10_semantic_mismatch_lower_bound": 606,
            "previous_actual_v10_exact_total_semantic_mismatches":
            "NOT MEASURED",
            "previous_actual_v10_original_suite_workers": 13,
            "previous_actual_v10_completed_original_suites": 8,
            "previous_actual_v10_original_candidate_execution_failures": 5,
            "previous_actual_v10_verified_passing_case_count": 13606,
            "previous_actual_v10_archived_recorded_counterexamples": 92,
            "previous_actual_v10_archived_missing_counterexamples": 514,
            "previous_actual_v10_missing_counterexample_status":
            "NOT RECORDED; NEVER FABRICATED",
            "observer_source_family_repair":
            "EXACT TWO IMMUTABLE CALL SITES AFTER AUTHENTIC V3 GUARD",
            "observer_source_mutations": 0,
            "reference_route_mutations": 0,
            "public_surface_comparison_normalization": "FORBIDDEN",
            "all_observed_mismatch_records_preserved": True,
            "full_mismatch_archive":
            "EXCLUSIVE FIRST-PARTY DIGEST-BOUND COMPRESSED MAIN ARCHIVE",
            "full_mismatch_archive_encoding":
            "PURE FIRST-PARTY COMPLETE LZ1 VECTOR CHUNKS",
            "prefix_or_digest_only_mismatch_evidence": "FORBIDDEN",
            "complete_mismatch_receipt_count_required": True,
            "full_mismatch_source_comparison_modified": False,
        })
        base["actual_operation_policy"] = policy
        base["authenticated_complete_v9_controller_transform"] = transform
        base["preserved_full_v9_reporting_freeze"] = {
            "owners": [owner_record(item) for item in C9],
            "status": c9["status"],
            "candidate_correctness": "NOT MEASURED",
            "source_only_effects": c9["source_only_effects"],
            "lossless_surrogate_transport_preserved": True,
            "source_specific_complete_vector_digest_preserved": True,
            "frozen_original_source_changes": 0,
            "archive_opened": False,
        }
        base["preserved_actual_c_v9_campaign"] = {
            "actual_failure_receipt": owner_record(C9_RECEIPT),
            "publication_status": receipt["publication_status"],
            "publication_pass_means": receipt["publication_pass_means"],
            "candidate_status": receipt["candidate_status"],
            "candidate_qualified": receipt["candidate_qualified"],
            "suite_count": receipt["suite_count"],
            "attempted_suite_count": receipt["attempted_suite_count"],
            "completed_suite_count": receipt["completed_suite_count"],
            "case_execution_denominator": receipt["case_execution_denominator"],
            "actual_candidate_workers": receipt["actual_candidate_workers"],
            "actual_worker_process_ids": receipt["actual_worker_process_ids"],
            "actual_worker_process_ids_are_distinct":
                receipt["actual_worker_process_ids_are_distinct"],
            "suite_outcomes": receipt["suite_outcomes"],
            "candidate_execution_failure_count":
                receipt["candidate_execution_failure_count"],
            "infrastructure_failure_count":
                receipt["infrastructure_failure_count"],
            "worker_timeout_count": receipt["worker_timeout_count"],
            "semantic_mismatch_count": receipt["semantic_mismatch_count"],
            "observed_semantic_mismatch_lower_bound":
                receipt["observed_semantic_mismatch_lower_bound"],
            "verified_passing_case_count": receipt["verified_passing_case_count"],
            "named_private_waiver_count": receipt["named_private_waiver_count"],
            "separate_reference_case_count":
                receipt["separate_reference_case_count"],
            "separate_reference_cases_counted_as_candidate_cases":
                receipt["separate_reference_cases_counted_as_candidate_cases"],
            "actual_c21_build_receipt_sha256":
                receipt["actual_c21_build_receipt_sha256"],
            "actual_c21_root_receipt_sha256":
                receipt["actual_c21_root_receipt_sha256"],
            "corrected_source_sha256": receipt["corrected_source_sha256"],
            "native_engine_sha256": receipt["native_engine_sha256"],
            "native_bridge_sha256": receipt["native_bridge_sha256"],
            "original_native_inode_restored":
                receipt["original_native_inode_restored"],
            "original_source_targets_modified":
                receipt["original_source_targets_modified"],
            "historical_archive_opened": False,
            "holdout": receipt["holdout"],
            "performance": receipt["performance"],
        }
        base["preserved_full_v10_reporting_freeze"] = {
            "owners": [owner_record(item) for item in C10],
            "status": c10["status"],
            "source_only_effects": c10["source_only_effects"],
            "candidate_correctness": "NOT MEASURED",
            "historical_archive_opened": False,
            "frozen_original_source_changes": 0,
        }
        base["preserved_actual_c_v10_campaign"] = {
            "actual_failure_receipt": owner_record(C10_RECEIPT),
            "publication_status": c10_receipt["publication_status"],
            "publication_pass_means":
            c10_receipt["publication_pass_means"],
            "candidate_status": c10_receipt["candidate_status"],
            "candidate_qualified": c10_receipt["candidate_qualified"],
            "suite_count": c10_receipt["suite_count"],
            "attempted_suite_count":
            c10_receipt["attempted_suite_count"],
            "completed_suite_count":
            c10_receipt["completed_suite_count"],
            "case_execution_denominator":
            c10_receipt["case_execution_denominator"],
            "actual_candidate_workers":
            c10_receipt["actual_candidate_workers"],
            "actual_worker_process_ids":
            c10_receipt["actual_worker_process_ids"],
            "actual_worker_process_ids_are_distinct":
            c10_receipt["actual_worker_process_ids_are_distinct"],
            "suite_outcomes": c10_receipt["suite_outcomes"],
            "candidate_execution_failure_count":
            c10_receipt["candidate_execution_failure_count"],
            "infrastructure_failure_count":
            c10_receipt["infrastructure_failure_count"],
            "worker_timeout_count":
            c10_receipt["worker_timeout_count"],
            "successfully_returned_guarded_interpreter_creations":
            "NOT MEASURED",
            "transient_physical_interpreter_creations":
            "NOT MEASURED",
            "zero_returned_creations_proves_zero_physical_creations":
            False,
            "semantic_mismatch_count":
            c10_receipt["semantic_mismatch_count"],
            "observed_semantic_mismatch_lower_bound":
            c10_receipt["observed_semantic_mismatch_lower_bound"],
            "verified_passing_case_count":
            c10_receipt["verified_passing_case_count"],
            "named_private_waiver_count":
            c10_receipt["named_private_waiver_count"],
            "separate_reference_case_count":
            c10_receipt["separate_reference_case_count"],
            "separate_reference_cases_counted_as_candidate_cases":
            c10_receipt["separate_reference_cases_counted_as_candidate_cases"],
            "actual_c21_build_receipt_sha256":
            c10_receipt["actual_c21_build_receipt_sha256"],
            "actual_c21_root_receipt_sha256":
            c10_receipt["actual_c21_root_receipt_sha256"],
            "corrected_source_sha256":
            c10_receipt["corrected_source_sha256"],
            "native_engine_sha256":
            c10_receipt["native_engine_sha256"],
            "native_bridge_sha256":
            c10_receipt["native_bridge_sha256"],
            "original_native_inode_restored":
            c10_receipt["original_native_inode_restored"],
            "original_source_targets_modified":
            c10_receipt["original_source_targets_modified"],
            "full_archive": dict(c10_receipt["archive"]),
            "full_archive_opened_in_source_mode": False,
            "archived_recorded_counterexamples": 92,
            "archived_missing_counterexamples": 514,
            "archived_missing_counterexample_status":
            "NOT RECORDED; NEVER FABRICATED",
            "forensic_observation":
            "INDEPENDENT READ-ONLY FULL-ARCHIVE AUDIT; NOT REOPENED",
            "holdout": c10_receipt["holdout"],
            "performance": c10_receipt["performance"],
        }
        base["c_only_original_runtime_route_repair"] = {
            "status": "SOURCE FROZEN; NO CANDIDATE OR OBSERVER EXECUTED",
            "family": "c",
            "selected_candidate_module": "candidates.vm_candidate",
            "required_guard_version": 3,
            "guard_owners": [owner_record(item) for item in V3],
            "immutable_original_producer_version": 5,
            "immutable_original_producer_source_mutated": False,
            "reference_routes_modified": False,
            "frozen_original_source_mutations": 0,
            "actual_candidate_imports": 0,
            "actual_guard_installations": 0,
            "original_harness_owner": owner_record(C_ROUTE_ORIGINAL),
            "original_harness_function": "authenticate_original_sources",
            "original_harness_line": 211,
            "original_harness_keyword": "candidate",
            "direct_core_owner": owner_record(C_ROUTE_DIRECT_CORE),
            "direct_core_function": "load_prerequisites",
            "direct_core_line": 483,
            "direct_core_keyword": "candidate_loaded",
            "direct_gate_owner": owner_record(C_ROUTE_DIRECT_GATE),
            "direct_candidate_suites": sorted(ROUTE_CASES),
            "exact_in_memory_runtime_call_site_count": 2,
            "actual_observer_overlays": 0,
            "stdlib_re": "FORBIDDEN",
            "external_regex_packages": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
        }
        base["lossless_original_counterexample_evidence"] = {
            "status": "SOURCE FROZEN; NO ORIGINAL CASE EXECUTED",
            "previous_actual_v10_receipt_sha256": C10_RECEIPT[1],
            "previous_actual_v10_observed_mismatch_lower_bound": 606,
            "previous_actual_v10_archived_recorded_counterexamples": 92,
            "previous_actual_v10_archived_missing_counterexamples": 514,
            "previous_actual_v10_missing_counterexample_status":
            "NOT RECORDED; NEVER FABRICATED",
            "full_mismatch_records_required": True,
            "full_mismatch_record_count_must_equal_observed_lower_bound": True,
            "lossless_codec": "PURE FIRST-PARTY C11 BOUNDED LZ1",
            "per_chunk_maximum_record_count":
            COMPLETE_VECTOR_CHUNK_RECORDS,
            "per_chunk_maximum_uncompressed_bytes":
            COMPLETE_VECTOR_CHUNK_BYTES,
            "maximum_total_uncompressed_bytes":
            COMPLETE_VECTOR_UNCOMPRESSED_BYTES,
            "full_archive":
            "EXCLUSIVE FIRST-PARTY GZIP CAMPAIGN ARCHIVE",
            "small_receipt_contains_counterexample_counts": True,
            "archive_must_contain_every_observed_mismatch_record": True,
            "prefix_only": False,
            "source_comparison_normalization": "FORBIDDEN",
            "historical_compressed_archives_opened": 0,
            "actual_archives_created": 0,
            "actual_candidate_workers": 0,
            "actual_counterexample_records": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        }
        base["strict_runtime_guard_v3"] = {
            "version": 3,
            "owners": [owner_record(item) for item in V3],
            "immutable_predecessor_v2": guard["immutable_predecessor_v2"],
            "immutable_producer_v5": guard["immutable_producer_v5"],
            "native_owner_policy": guard["native_owner_policy"],
            "subinterpreter_bootstrap": guard["subinterpreter_bootstrap"],
            "source_only_effects": guard["source_only_effects"],
            "source_mode_interpreter_creation_calls": 0,
            "historical_v10_returned_guarded_interpreter_creations":
            "NOT MEASURED",
            "historical_v10_transient_physical_interpreter_creations":
            "NOT MEASURED",
            "physical_transient_creation_count": "NOT MEASURED",
            "zero_returned_creations_proves_zero_physical_creations":
            False,
            "actual_candidate_guard_installations": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        }
        base["public_surface_digest_provenance_repair"] = {
            "source_owner": historical.owner_record(history.SURFACE_OWNER),
            "source_module": history.SURFACE_MODULE,
            "function": "digest",
            "source_first_line": 251,
            "source_qualname": "digest",
            "reference": "COMPLETE AUTHENTICATED ORIGINAL MODULE CODE OBJECT",
            "whole_source_executed_in_source_mode": False,
            "frozen_public_surface_modified": False,
            "digest_monkeypatched": False,
            "source_identity_checks_weakened": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "historical_c9_surface_failure_preserved": True,
        }
        base["source_wall"]["owner_count"] = len(old.STATIC_OWNERS)
        return base

    def install_actual_v3_guard(state: dict, inode: int) -> tuple:
        previous = active_previous[0]
        need(previous is not None
             and type(state.get("v3_guard_raw")) is bytes
             and hashlib.sha256(state["v3_guard_raw"]).hexdigest() == V3[0][1]
             and state.get("v3_guard_contract", {}).get("version") == 3
             and type(inode) is int and inode > 0,
             "reject missing independently authenticated actual V3 guard")
        previous.clean_runtime()
        guard = types.ModuleType("_rebar_owned_actual_c_v11_runtime_guard_v3")
        guard.__file__ = ROOT + "/" + V3[0][0]
        guard.__package__ = ""
        exec(compile(state["v3_guard_raw"], guard.__file__, "exec",
                     dont_inherit=True), guard.__dict__)
        need(guard.SELF == V3[0][0]
             and guard.PROTOCOL == V3[1][0]
             and guard.CONTRACT == V3[2][0]
             and guard.BASE.SELF
             == "tools/verify_owned_candidate_runtime_independence_v2.py"
             and guard.RuntimePolicy.__bases__[0] is guard.BASE.RuntimePolicy
             and guard.RuntimePolicy.prepare_family
             is guard.BASE.RuntimePolicy.prepare_family
             and guard.RuntimePolicy.prepare_family.__globals__
             is guard.BASE.__dict__
             and guard.child_bootstrap_source
             is guard.BASE.child_bootstrap_source,
             "require genuine V3 with exact unchanged V2 policy and child code")
        policy = guard.RuntimePolicy()
        policy.install()
        bridge = previous.native_guard_owner("bridge", inode)
        engine = previous.native_guard_owner("engine", inode)
        need(set(bridge) == guard.NATIVE_OWNER_KEYS
             and set(engine) == guard.NATIVE_OWNER_KEYS
             and bridge["role"] == "bridge"
             and engine["role"] == "engine"
             and bridge["uid"] == os.geteuid()
             and engine["uid"] == os.geteuid()
             and bridge["native_loaded"] is False
             and engine["native_loaded"] is False,
             "reject crossed or incomplete genuine fourteen-field native roles")
        policy.prepare_family("c", bridge_owner=bridge, engine_owner=engine)
        if not sys.path or sys.path[0] != ROOT:
            sys.path.insert(0, ROOT)
        selected = __import__("candidates.vm_candidate", fromlist=["__name__"])
        policy.bind_selected(selected, "c")
        native = sys.modules.get("candidates._vm_native")
        need(policy.installed
             and policy.prepared_family == "c"
             and policy.bridge_owner == bridge
             and policy.engine_owner == engine
             and sys.modules.get("re") is selected
             and type(native) is types.ModuleType
             and os.path.abspath(native.__file__)
             == ROOT + "/" + historical.NATIVE_RELATIVE
             and "_sre" not in sys.modules
             and "ctypes" not in sys.modules,
             "install genuine V3 before importing the sole first-party C matcher")
        policy.check_modules()
        return policy, selected

    def controls(previous: types.ModuleType,
                 wall: object, old: types.ModuleType) -> list:
        answers = historical_controls(previous, wall, old)

        def reject(label: str, operation: object) -> None:
            refused = False
            try:
                operation()
            except Exception:
                refused = True
            need(refused, "acceptance of forbidden C10 operation: " + label)
            answers.append(label)

        raw = old.read_owner(history.SURFACE_OWNER)
        relative = history.SURFACE_OWNER[0]
        absolute = ROOT + "/" + relative
        tree = ast.parse(raw.decode("utf-8", "strict"), filename=absolute)
        root_code = compile(tree, absolute, "exec", dont_inherit=True)
        definitions = [item for item in tree.body
                       if isinstance(item, ast.FunctionDef)
                       and item.name in ("digest", "_new_normalized_envelope")]
        need(len(definitions) == 2,
             "preserve both unique whole-source public-surface provenance roles")
        references = {}
        for item in definitions:
            matches = [code for code in root_code.co_consts
                       if type(code) is types.CodeType
                       and code.co_name == item.name
                       and code.co_qualname == item.name
                       and code.co_firstlineno == item.lineno]
            need(len(matches) == 1,
                 "reject missing or duplicate real whole-source code identity")
            references[item.name] = matches[0]
        futures = [item for item in tree.body
                   if isinstance(item, ast.ImportFrom)
                   and item.module == "__future__"]
        digest_definition = next(item for item in definitions
                                 if item.name == "digest")
        isolated = compile(
            ast.fix_missing_locations(ast.Module(
                body=futures + [digest_definition], type_ignores=[]
            )), absolute, "exec", dont_inherit=True,
        )
        isolated_digest = [item for item in isolated.co_consts
                           if type(item) is types.CodeType
                           and item.co_name == "digest"]
        need(len(isolated_digest) == 1
             and references["digest"].co_firstlineno == 251
             and references["digest"].co_qualname == "digest"
             and references["digest"].co_code != isolated_digest[0].co_code,
             "prove the genuine full-module digest differs from partial recompilation")
        answers.append("authenticate the genuine untouched full-module digest code")

        forged = types.ModuleType(history.SURFACE_MODULE)
        forged.__file__ = absolute
        forged.SOURCE_RELATIVE = relative
        exec(compile(
            "from __future__ import annotations\n"
            "def digest(value):\n    return '0' * 64\n",
            absolute, "exec", dont_inherit=True,
        ), forged.__dict__)
        need(history.SURFACE_MODULE not in sys.modules,
             "never preimport the genuine public-surface suite in a source gate")
        sys.modules[history.SURFACE_MODULE] = forged
        try:
            reject("reject exact-name exact-file forged whole-source digest",
                   lambda: whole_source_callable(
                       forged, history.SURFACE_OWNER, "digest"
                   ))
        finally:
            need(sys.modules.get(history.SURFACE_MODULE) is forged,
                 "reject a substituted C10 synthetic source-only module")
            sys.modules.pop(history.SURFACE_MODULE, None)

        for path in (
            ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
            ROOT + "/candidates/vm_candidate.py",
            ROOT + "/" + historical.C21_VARIANT_RELATIVE,
            "/tmp/rebar-phase2-c-original-match-semantics-v21-"
            "66118b4c946a061c863a4c643fd7185e",
            ROOT + "/oracle/phase2/evidence/"
            "repaired-c-original-campaign-v9-c-phase2-v21-"
            "c-original-match-semantics-original-p0-v9-failures.json.gz",
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
        ):
            reject("physically deny C10 forbidden " + path.rsplit("/", 1)[-1],
                   lambda target=path: os.open(
                       target, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                   ))
        for old_name in ("_interpreters.create", "_interpreters.exec"):
            reject("reject invented genuine CPython audit event " + old_name,
                   lambda name=old_name: need(
                       name == "cpython.PyInterpreterState_New",
                       "legacy interpreter events cannot prove native creation",
                   ))
        answers.extend(c11_route_hostile_controls(old))
        producer = old.load_producer(old.read_owner(old.PRODUCER[0]))
        answers.extend(c11_vector_hostile_controls(producer, history))
        reject(
            "physically deny unopened actual C10 compressed failure evidence",
            lambda: os.open(
                ROOT + "/oracle/phase2/evidence/"
                "repaired-c-original-campaign-v10-c-phase2-v21-c-"
                "original-match-semantics-original-p0-v10-failures.json.gz",
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            ),
        )
        need(len(answers) >= 120
             and historical.source_effects()["actual_candidate_workers"] == 0
             and "re" not in sys.modules
             and "_sre" not in sys.modules
             and "ctypes" not in sys.modules,
             "preserve all original C9 and full-source V3 hostile controls")
        return answers

    active_previous: list = [None]

    def remember(previous: types.ModuleType) -> tuple:
        result = configure(previous)
        active_previous[0] = previous
        return result

    module.configure_previous = remember
    module.contract_document = contract_document
    module.source_controls = controls

    def complete_original_worker(parsed: dict,
                                 producer: types.ModuleType,
                                 state: dict,
                                 previous: types.ModuleType) -> dict:
        return lossless_c11_protected_worker(
            parsed, producer, state, previous, history, module,
        )

    module.protected_worker = complete_original_worker


def main(arguments: list[str]) -> int:
    historical, transform = bootstrap_v9()
    original_install = historical.install_c21

    def install_all(history: types.ModuleType, module: types.ModuleType,
                    previous_transform: dict) -> None:
        original_install(history, module, previous_transform)
        install_v11(historical, history, module, transform)

    historical.install_c21 = install_all
    return historical.main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, (
            "C21 original campaign V11: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        ).encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
