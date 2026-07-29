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
SOURCE = "tools/run_owned_repaired_c_original_campaign_v10.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V10.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v10.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v10"
LABEL = "phase2-v21-c-original-match-semantics-original-p0-v10"
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
        "/tmp/rebar-phase2-repaired-c-original-campaign-v10",
    ".rebar-c-original-campaign-v9-original-native":
        ".rebar-c-original-campaign-v10-original-native",
    ".rebar-c-original-campaign-v9-staged-native":
        ".rebar-c-original-campaign-v10-staged-native",
    "original-native-recovery-journal-v9.json":
        "original-native-recovery-journal-v10.json",
    "repaired-c-original-campaign-v9-c-":
        "repaired-c-original-campaign-v10-c-",
    "SOURCE FROZEN; ACTUAL C21 V9 ORIGINAL CAMPAIGN NOT RUN":
        "SOURCE FROZEN; ACTUAL C21 V10 ORIGINAL CAMPAIGN NOT RUN",
    "SOURCE FREEZE, PRESERVED ACTUAL V6 AND V7 FAILURES; "
    "NOT A V9 CANDIDATE RESULT":
        "SOURCE FREEZE, PRESERVED ACTUAL V6, V7, AND V9 FAILURES; "
        "NOT A V10 CANDIDATE RESULT",
    "LATEST P0 V4 AND EXPLICIT C21 V9 ONLY":
        "LATEST P0 V4 AND EXPLICIT C21 V10 ONLY",
    "NOT RUN BY V9": "NOT RUN BY V10",
    "v9_candidate_correctness": "v10_candidate_correctness",
    "-v9": "-v10",
    "v9-original-native": "v10-original-native",
    "v9-staged-native": "v10-staged-native",
    "_rebar_owned_c_v9_authenticated_v8":
        "_rebar_owned_c_v10_authenticated_v8",
    "C21 original campaign V9: ": "C21 original campaign V10: ",
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
    permitted = C9 + V3 + (C9_RECEIPT,)
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


class ExactV9ToV10(ast.NodeTransformer):
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
            node.value.value = 10
            self.inner_version_assignments += 1
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        node = self.generic_visit(node)
        for key, value in zip(node.keys, node.values, strict=True):
            if (isinstance(key, ast.Constant)
                    and key.value == "version"
                    and isinstance(value, ast.Constant)
                    and type(value.value) is int and value.value == 9):
                value.value = 10
                self.contract_version_fields += 1
        return node


def bootstrap_v9() -> tuple[types.ModuleType, dict]:
    clean_runtime()
    tree = ast.parse(exact_owner(C9[0]).decode("utf-8", "strict"),
                     filename=ROOT + "/" + C9[0][0])
    change = ExactV9ToV10()
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
    module = types.ModuleType("_rebar_owned_c_v10_authenticated_complete_v9")
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


def install_v10(historical: types.ModuleType, history: types.ModuleType,
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
        additions = C9 + V3 + (C9_RECEIPT,)
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
        previous_collect = previous.collect_context

        def complete_context(frozen: types.ModuleType, parsed: dict,
                             *, controls: bool = False) -> tuple:
            producer, state, result = previous_collect(
                frozen, parsed, controls=controls
            )
            receipt = state.get("actual_v9_receipt")
            guard = state.get("v3_guard_contract")
            need(type(receipt) is dict
                 and receipt.get("observed_semantic_mismatch_lower_bound") == 492
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
                "public_surface_digest_first_source_line": 251,
                "public_surface_digest_monkeypatched": False,
                "frozen_public_surface_source_modified": False,
            })
            return producer, state, result

        previous.collect_context = complete_context
        need(previous.RECOVERY_ROOT.endswith("-v10")
             and previous.BACKUP_NAME.endswith("v10-original-native")
             and previous.STAGE_NAME.endswith("v10-staged-native")
             and previous.JOURNAL_NAME
             == "original-native-recovery-journal-v10.json",
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
        state["v3_guard_raw"] = guard_raw
        state["v3_guard_contract"] = guard
        state["actual_v9_receipt"] = receipt
        state["complete_v9_contract"] = c9
        base = historical_contract(parsed, old, state,
                                   previous, original_contract)
        need(base.get("schema") == SCHEMA + "-source-freeze"
             and base.get("version") == 10
             and base.get("family") == "c"
             and base.get("label") == LABEL
             and base.get("phase_one_v4", {}).get(
                 "original_case_execution_denominator"
             ) == 31237,
             "reject a reduced or crossed cumulative full C9 campaign")
        policy = dict(base["actual_operation_policy"])
        policy.update({
            "authorization": "EXPLICIT INDEPENDENTLY PINNED C21 C10 --run ONLY",
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
        base["strict_runtime_guard_v3"] = {
            "version": 3,
            "owners": [owner_record(item) for item in V3],
            "immutable_predecessor_v2": guard["immutable_predecessor_v2"],
            "immutable_producer_v5": guard["immutable_producer_v5"],
            "native_owner_policy": guard["native_owner_policy"],
            "subinterpreter_bootstrap": guard["subinterpreter_bootstrap"],
            "source_only_effects": guard["source_only_effects"],
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
        guard = types.ModuleType("_rebar_owned_actual_c_v10_runtime_guard_v3")
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
        need(len(answers) >= 99
             and historical.source_effects()["actual_candidate_workers"] == 0,
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


def main(arguments: list[str]) -> int:
    historical, transform = bootstrap_v9()
    original_install = historical.install_c21

    def install_all(history: types.ModuleType, module: types.ModuleType,
                    previous_transform: dict) -> None:
        original_install(history, module, previous_transform)
        install_v10(historical, history, module, transform)

    historical.install_c21 = install_all
    return historical.main(arguments)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        os.write(2, (
            "C21 original campaign V10: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        ).encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
