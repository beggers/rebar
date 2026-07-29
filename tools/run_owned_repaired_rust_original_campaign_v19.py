#!/usr/bin/env python3
"""Verify both actual Rust preflight failures before the original campaign.

Source modes replay the exact unchanged V7 historical-helper verification and
the genuine inherited V16 recovery-prefix verifier using an in-memory helper.
No matcher, compiler, native library, root, archive, clock, or holdout runs.
An explicitly authorized real operation changes one data constant in that
same authenticated recovery function, preserving its bytecode, identity,
historical V2 authentication, selected V21 roles, and complete 13-row receipt.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v19.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V19.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v19.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v19"
VERSION = 19
BUILD_LABEL = "phase2-v21-rust-captured-findall-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v19"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v19-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
HISTORICAL_V16_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v16-"
HISTORICAL_V2_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v2-"
RECOVERY_FAILURE = "derive one exact distinct V16 recovery prefix and immutable root"

V18 = (
    ("tools/run_owned_repaired_rust_original_campaign_v18.py",
     "1ade4e2c35dfece5354ef2b710ea4be4f23f085df73bd726fefcc7461fecf860",
     35566, 431126),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V18.md",
     "687e6f4b497dd64445fa0c0016f79b26cb8028c8ebc27cdc0dc984f91a9cb409",
     6467, 525183),
    ("oracle/phase2/repaired-rust-original-campaign-v18.json",
     "bbd2dce49459a0dae8b92ec5ac772e33817c42a7fe2a11ae1fc3826e81e7b38d",
     22497, 525184),
)
V18_FAILURE = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v18-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "original-p0-v18-entry-failure.json",
    "d657afab044974a9badbf6d4466aea015e5a27328d1ca234828abdfddf5e6e69",
    1262, 525202,
)
V11 = (
    "tools/run_owned_repaired_rust_original_campaign_v11.py",
    "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d",
    310760, 430525,
)


class CampaignError(Exception):
    """Authentic historical recovery or strict source-only isolation failed."""


def need(valid: object, reason: str) -> None:
    if valid is not True:
        raise CampaignError(reason)


def secure_owner(owner: tuple, *, maximum: int = 4 * 1024 * 1024) -> bytes:
    need(type(owner) is tuple and len(owner) == 4,
         "require one exact immutable V19 source-only owner")
    path, fingerprint, count, inode = owner
    need(type(path) is str and bool(path) and not path.startswith("/")
         and ".." not in path.split("/")
         and not path.endswith((".gz", ".so"))
         and type(fingerprint) is str and len(fingerprint) == 64
         and all(char in "0123456789abcdef" for char in fingerprint)
         and type(count) is int and 0 < count <= maximum
         and type(inode) is int and inode > 0,
         "reject a native owner, archive, root, holdout, or unsafe source")
    descriptor = os.open(
        ROOT + "/" + path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable historical owner: " + path)
        pieces: list[bytes] = []
        remaining = count
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            need(bool(piece), "reject a truncated historical owner: " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(not os.read(descriptor, 1),
             "reject an expanded historical owner: " + path)
        result = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(result).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a changed immutable historical owner: " + path)
        return result
    finally:
        os.close(descriptor)


def validate_v18_failure(value: object,
                         parent: types.ModuleType) -> dict:
    need(type(value) is dict,
         "require the actual complete V18 preactivation failure")
    assert isinstance(value, dict)
    need(value.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v18-entry-failure"
         and value.get("status") == "FAIL"
         and value.get("version") == 18
         and value.get("error_type") == "CampaignError"
         and value.get("error_message") == RECOVERY_FAILURE,
         "authenticate the exact real V18 historical recovery-prefix failure")
    need(all(value.get(key) == expected
             for key, expected in parent.zero_effects().items()),
         "reject invented workers, matching, roots, archives, or holdout")
    need(value.get("candidate_qualified") is False
         and value.get("candidate_correctness") == "NOT MEASURED"
         and value.get("candidate_matching") == "NOT RUN"
         and value.get("expanded_holdout_cases_opened") == 0,
         "never reinterpret V18 entry failure as candidate or timing evidence")
    return value


def replace_exact_recovery_prefix(module: types.ModuleType,
                                  *, synthetic: bool = False) -> dict:
    need(type(module) is types.ModuleType
         and getattr(module, "SCHEMA", None) == SCHEMA
         and getattr(module, "PUBLIC_RECOVERY_PRIVATE_PREFIX", None)
         == RECOVERY_PREFIX
         and getattr(module, "PUBLIC_RECOVERY_ROOT", None) == RECOVERY_ROOT
         and getattr(module, "HISTORICAL_V2_PRIVATE_PREFIX", None)
         == HISTORICAL_V2_PREFIX
         and RECOVERY_PREFIX != HISTORICAL_V16_PREFIX
         and RECOVERY_PREFIX != HISTORICAL_V2_PREFIX
         and RECOVERY_ROOT == "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
         and len(RECOVERY_ROOT.split("/")) == 3,
         "require the exact unique V19 root and immutable historical V2 prefix")
    function = getattr(module, "authenticate_and_rebind_v16_recovery_prefix",
                       None)
    checker = getattr(module, "checked_v16_recovery_helper_root", None)
    need(type(function) is types.FunctionType
         and type(checker) is types.FunctionType
         and function.__globals__ is module.__dict__
         and checker.__globals__ is module.__dict__
         and function.__closure__ is None
         and function.__code__.co_name
         == "authenticate_and_rebind_v16_recovery_prefix"
         and checker.__code__.co_name == "checked_v16_recovery_helper_root",
         "retain the two exact unchanged genuine V16 recovery functions")
    original = function.__code__
    constants = original.co_consts
    need(sum(item == HISTORICAL_V16_PREFIX for item in constants) == 1
         and sum(item == BUILD_SUFFIX for item in constants) == 1
         and sum(item == RECOVERY_FAILURE for item in constants) == 1
         and all(item != RECOVERY_PREFIX for item in constants)
         and original.co_freevars == ()
         and original.co_argcount == 1
         and original.co_kwonlyargcount == 1,
         "require exactly one authentic stale V16 prefix and V21 root proof")
    updated = tuple(
        RECOVERY_PREFIX if item == HISTORICAL_V16_PREFIX else item
        for item in constants
    )
    changed = original.replace(co_consts=updated)
    need(changed.co_code == original.co_code
         and changed.co_names == original.co_names
         and changed.co_varnames == original.co_varnames
         and changed.co_freevars == original.co_freevars
         and changed.co_cellvars == original.co_cellvars
         and changed.co_exceptiontable == original.co_exceptiontable
         and changed.co_consts == updated
         and sum(item == RECOVERY_PREFIX for item in changed.co_consts) == 1
         and sum(item == HISTORICAL_V16_PREFIX
                 for item in changed.co_consts) == 0
         and sum(item == BUILD_SUFFIX for item in changed.co_consts) == 1
         and sum(item == RECOVERY_FAILURE for item in changed.co_consts) == 1,
         "change one recovery data constant without changing function bytecode")
    previous_checker = checker.__code__
    previous_globals = function.__globals__
    previous_defaults = function.__defaults__
    previous_keywords = function.__kwdefaults__
    function.__code__ = changed
    need(getattr(module, "authenticate_and_rebind_v16_recovery_prefix")
         is function
         and getattr(module, "checked_v16_recovery_helper_root") is checker
         and checker.__code__ is previous_checker
         and function.__code__ is changed
         and function.__globals__ is previous_globals
         and function.__defaults__ is previous_defaults
         and function.__kwdefaults__ is previous_keywords
         and function.__closure__ is None,
         "preserve actual verifier identity, checker, globals and V2 ordering")
    return {
        "status": "PASS",
        "immutable_source_sha256": V11[1],
        "recovery_function_name": function.__name__,
        "stale_prefix": HISTORICAL_V16_PREFIX,
        "selected_prefix": RECOVERY_PREFIX,
        "selected_root": RECOVERY_ROOT,
        "selected_build_suffix": BUILD_SUFFIX,
        "recovery_code_constants_changed": 1,
        "recovery_function_identity_preserved": True,
        "recovery_function_bytecode_preserved": True,
        "recovery_checker_identity_preserved": True,
        "historical_v2_prefix_preserved": True,
        "production_wrapper_added": False,
        "synthetic_in_memory_only": synthetic,
    }


def make_synthetic_helper() -> types.ModuleType:
    helper = types.ModuleType("_rebar_v19_synthetic_historical_v2_helper")
    helper.SCHEMA = "rebar-owned-repaired-rust-original-campaign-v2"
    helper.PRIVATE_PREFIX = HISTORICAL_V2_PREFIX

    def checked_private_root(root: object) -> str:
        need(type(root) is str
             and root.startswith("/tmp/" + helper.PRIVATE_PREFIX)
             and len(root.split("/")) == 3
             and root == root.rstrip("/")
             and "\x00" not in root and "\\" not in root,
             "reject a synthetic historical V2 root without opening a root")
        return root

    helper.checked_private_root = checked_private_root
    return helper


def static_recovery_verifier(parent: types.ModuleType,
                             previous: dict, state: dict) -> dict:
    source = secure_owner(V11)
    records = previous.get("historical_ctypes_sources")
    need(type(records) is list
         and sum(type(row) is dict and row.get("role") == "v11"
                 and row.get("path") == V11[0]
                 and row.get("sha256") == V11[1]
                 and row.get("bytes") == V11[2]
                 and row.get("inode") == V11[3]
                 for row in records) == 1,
         "authenticate the actual immutable historical V11 recovery owner")
    dispatcher = state["runner"].bind_v16_legacy
    need(type(dispatcher) is types.FunctionType
         and sum(item == BUILD_SUFFIX
                 for item in dispatcher.__code__.co_consts) == 1,
         "retain the authentic V16 dispatcher and exact migrated V21 route")
    try:
        transformed = source.decode("utf-8", "strict")
        transformed = transformed.replace(
            "phase2-v18-rust-buffer-shape-pickle-original-p0-v11", LABEL,
        ).replace(
            "phase2-v18-rust-buffer-shape-pickle-original-p0", BUILD_SUFFIX,
        ).replace(
            "phase2-v18-rust-buffer-shape-pickle-lifetime", BUILD_LABEL,
        ).replace(
            "rebar-owned-six-family-original-p0-producer-v4",
            "rebar-owned-six-family-original-p0-producer-v5",
        ).replace(
            "frozen_original_six_family_v4", "frozen_original_six_family_v5",
        ).replace(
            '"original_v4_producer_version": 4',
            '"original_v5_producer_version": 5',
        ).replace(
            "original_v4_producer_", "original_v5_producer_",
        ).replace(
            '"original_observer_version": 4',
            '"original_observer_version": 5',
        ).replace(
            'observed.get("original_observer_version") == 4',
            'observed.get("original_observer_version") == 5',
        )
        for before, after in (
                ("v11", "v16"), ("V11", "V16"),
                ("v18", "v21"), ("V18", "V21"),
                ("v69", "v86"), ("V69", "V86")):
            transformed = transformed.replace(before, after)
        tree = ast.parse(transformed, filename=V11[0])
    except (UnicodeError, SyntaxError, ValueError, RecursionError) as error:
        raise CampaignError("reject changed authentic V16 recovery source") from error
    wanted = {
        "authenticate_and_rebind_v16_recovery_prefix",
        "checked_v16_recovery_helper_root",
    }
    definitions = {
        node.name: node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    }
    need(set(definitions) == wanted,
         "extract only the two genuine inherited V16 recovery functions")
    module = types.ModuleType("_rebar_v19_synthetic_authentic_v16_recovery")
    module.SCHEMA = SCHEMA
    module.types = types
    module.Any = object
    module.require = need
    module.CampaignError = CampaignError
    module.PUBLIC_RECOVERY_PRIVATE_PREFIX = RECOVERY_PREFIX
    module.PUBLIC_RECOVERY_ROOT = RECOVERY_ROOT
    module.HISTORICAL_V2_PRIVATE_PREFIX = HISTORICAL_V2_PREFIX
    extracted = ast.Module(
        body=[
            ast.ImportFrom(module="__future__",
                           names=[ast.alias(name="annotations")], level=0),
            definitions["checked_v16_recovery_helper_root"],
            definitions["authenticate_and_rebind_v16_recovery_prefix"],
        ],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(extracted), V11[0], "exec",
                 dont_inherit=True), module.__dict__)
    helper = make_synthetic_helper()
    ledger = {"recovery_roots_created": 0,
              "recovery_root_creation_attempted": False}
    try:
        module.authenticate_and_rebind_v16_recovery_prefix(
            helper, ledger=ledger,
        )
    except CampaignError as error:
        need(str(error) == RECOVERY_FAILURE
             and helper.PRIVATE_PREFIX == HISTORICAL_V2_PREFIX
             and ledger["recovery_roots_created"] == 0
             and ledger["recovery_root_creation_attempted"] is False,
             "reproduce the exact real V18 prefix failure before any root")
    else:
        raise CampaignError("failed to reproduce the authentic V18 prefix error")
    proof = replace_exact_recovery_prefix(module, synthetic=True)
    result = module.authenticate_and_rebind_v16_recovery_prefix(
        helper, ledger=ledger,
    )
    need(result is helper and helper.PRIVATE_PREFIX == RECOVERY_PREFIX
         and module.checked_v16_recovery_helper_root(helper, RECOVERY_ROOT)
         == RECOVERY_ROOT
         and ledger.get("historical_v2_original_private_prefix_authenticated")
         is True
         and ledger.get("v16_recovery_private_prefix_rebound") is True
         and ledger.get("v16_recovery_private_prefix") == RECOVERY_PREFIX
         and ledger.get("v16_recovery_prefix_rebound_before_root_creation")
         is True
         and ledger["recovery_roots_created"] == 0
         and ledger["recovery_root_creation_attempted"] is False,
         "execute authentic V2-first V19 recovery proof without any mkdir")
    return {"module": module, "proof": proof,
            "real_failure_reproduced": True,
            "authentic_corrected_recovery_executed": True,
            "synthetic_ledger": ledger}


def load_previous() -> tuple[types.ModuleType, types.ModuleType,
                             dict, dict, dict, dict, dict]:
    raw = secure_owner(V18[0])
    secure_owner(V18[1])
    secure_owner(V18[2])
    ancestor = types.ModuleType("_rebar_v19_immutable_v18_original_campaign")
    ancestor.__file__ = ROOT + "/" + V18[0][0]
    exec(compile(raw, ancestor.__file__, "exec", dont_inherit=True),
         ancestor.__dict__)
    need(ancestor.SOURCE == V18[0][0]
         and ancestor.PROTOCOL == V18[1][0]
         and ancestor.CONTRACT == V18[2][0]
         and ancestor.SCHEMA
         == "rebar-owned-repaired-rust-original-campaign-v18"
         and ancestor.VERSION == 18
         and ancestor.BUILD_LABEL == BUILD_LABEL
         and callable(ancestor.load_previous)
         and callable(ancestor.prepare_parent)
         and callable(ancestor.corrected_controller)
         and callable(ancestor.historical_controls),
         "authenticate the complete immutable V18 historical-first controller")
    parent, previous_v17, previous_state, failure_v17, historical = (
        ancestor.load_previous()
    )
    ancestor.prepare_parent(parent, previous_v17, failure_v17, historical)
    context, state = parent.verify_context(
        V18[0][1], V18[1][1], V18[2][1],
    )
    previous = ancestor.enrich(context, previous_v17, failure_v17, historical)
    need(previous.get("status") == "PASS"
         and previous.get("version") == 18
         and previous.get("source_sha256") == V18[0][1]
         and previous.get("protocol_sha256") == V18[1][1]
         and previous.get("contract_sha256") == V18[2][1]
         and previous.get("historical_v2_preflight_status") == "PASS"
         and previous.get("actual_v17_entry_failure_sha256")
         == ancestor.V17_FAILURE[1]
         and previous.get("suite_count") == 13
         and previous.get("case_execution_denominator") == 31237
         and previous.get("private_waiver_count") == 13
         and previous.get("actual_candidate_workers_started") == 0
         and previous.get("expanded_holdout_cases_opened") == 0,
         "retain V17 failure, genuine V2 proof, and complete frozen V18")
    failure = parent.document(
        state["original_base"], state["guard"], secure_owner(V18_FAILURE),
        "actual single V18 immutable recovery-prefix preactivation failure",
    )
    validate_v18_failure(failure, parent)
    recovery = static_recovery_verifier(parent, previous, state)
    parent.runtime()
    return ancestor, parent, previous, state, failure, historical, recovery


def enrich(context: dict, ancestor: types.ModuleType, previous: dict,
           failure: dict, recovery: dict) -> dict:
    result = dict(context)
    result.update({
        "schema": SCHEMA + "-frozen-context",
        "version": VERSION,
        "previous_v18_source_sha256": V18[0][1],
        "previous_v18_protocol_sha256": V18[1][1],
        "previous_v18_contract_sha256": V18[2][1],
        "previous_v18_frozen_source_status": previous["status"],
        "actual_v17_entry_failure_sha256": ancestor.V17_FAILURE[1],
        "actual_v17_entry_failure_error_message": ancestor.HISTORICAL_FAILURE,
        "actual_v17_entry_failure_is_durable_campaign_receipt": False,
        "actual_v18_entry_failure_path": V18_FAILURE[0],
        "actual_v18_entry_failure_sha256": V18_FAILURE[1],
        "actual_v18_entry_failure_bytes": V18_FAILURE[2],
        "actual_v18_entry_failure_inode": V18_FAILURE[3],
        "actual_v18_entry_failure_schema": failure["schema"],
        "actual_v18_entry_failure_status": failure["status"],
        "actual_v18_entry_failure_error_type": failure["error_type"],
        "actual_v18_entry_failure_error_message": failure["error_message"],
        "actual_v18_entry_failure_is_durable_campaign_receipt": False,
        "actual_v18_entry_failure_observation":
            "GENUINE SINGLE PREACTIVATION ATTEMPT; "
            "NOT A DURABLE CAMPAIGN RECEIPT",
        "actual_v18_entry_failure_candidate_workers_started":
            failure["actual_candidate_workers_started"],
        "actual_v18_entry_failure_private_root_opens":
            failure["actual_private_build_root_opens"],
        "actual_v18_entry_failure_private_root_stats":
            failure["actual_private_build_root_stats"],
        "actual_v18_entry_failure_native_libraries_loaded":
            failure["actual_native_libraries_loaded"],
        "historical_recovery_verifier_source_sha256": V11[1],
        "historical_recovery_verifier_source_bytes": V11[2],
        "historical_recovery_verifier_source_inode": V11[3],
        "historical_recovery_prefix_verifier_status":
            recovery["proof"]["status"],
        "historical_recovery_prefix_real_failure_reproduced":
            recovery["real_failure_reproduced"],
        "historical_recovery_prefix_corrected_function_executed":
            recovery["authentic_corrected_recovery_executed"],
        "historical_recovery_prefix_stale_v16": HISTORICAL_V16_PREFIX,
        "historical_recovery_prefix_immutable_v2": HISTORICAL_V2_PREFIX,
        "historical_recovery_prefix_selected_v19": RECOVERY_PREFIX,
        "historical_recovery_prefix_selected_root": RECOVERY_ROOT,
        "historical_recovery_prefix_build_suffix": BUILD_SUFFIX,
        "historical_recovery_code_constants_changed": 1,
        "historical_recovery_function_identity_preserved": True,
        "historical_recovery_function_bytecode_preserved": True,
        "historical_recovery_checker_identity_preserved": True,
        "historical_recovery_function_wrapper_added": False,
        "historical_recovery_synthetic_root_opens": 0,
        "historical_recovery_synthetic_root_creations": 0,
        "historical_recovery_binding_order":
            "AUTHENTICATE IMMUTABLE V2 PREFIX FIRST; REBIND EXACT "
            "SELECTED V19 PREFIX BEFORE ANY ROOT CREATION; THEN "
            "PROMOTE THE ORIGINAL FOUR V21 ROLES",
        "historical_v2_preflight_status": "PASS",
        "historical_v7_premature_global_mutation_allowed": False,
        "historical_v7_scoped_promotion_wrapper_added": False,
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v19.lock",
        "expected_actual_evidence_stem":
            "repaired-rust-original-campaign-v16-rust-" + LABEL,
        "expected_actual_success_archive":
            "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
            + LABEL + ".json.gz",
        "expected_actual_success_receipt":
            "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
            + LABEL + "-publication-receipt.json",
        "expected_actual_failure_archive":
            "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
            + LABEL + "-failures.json.gz",
        "expected_actual_failure_receipt":
            "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
            + LABEL + "-failures-publication-receipt.json",
        "actual_v19_original_campaign_attempted": False,
    })
    return result


def corrected_controller(parent: types.ModuleType,
                         historical: dict):
    owners = historical["historical_owners"]
    historical_values = historical["v7_values"]

    def bind(state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        runner = state["runner"]
        base = state["base"]
        guard = state["guard"]
        legacy = runner.bind_v16_legacy(context, guard, base, bundle, counts)
        repair = replace_exact_recovery_prefix(legacy)
        need(repair["status"] == "PASS"
             and repair["recovery_code_constants_changed"] == 1
             and repair["production_wrapper_added"] is False,
             "repair only the authentic stale V16 prefix before configuration")
        original_sources = tuple(legacy.SOURCE_OWNERS)
        need(len(original_sources) == 9
             and sum(row[0] == "candidates/rust/py_bridge.c"
                     for row in original_sources) == 1
             and sum(row[0] == "candidates/rust_candidate.py"
                     for row in original_sources) == 1,
             "preserve all nine authenticated original Rust source owners")
        legacy.COMBINED_BRIDGE_SHA256 = parent.CAPTURE_SHA
        legacy.COMBINED_BRIDGE_BYTES = parent.CAPTURE_BYTES
        legacy.CORRECTED_ADAPTER_SHA256 = parent.ADAPTER_SHA
        legacy.CORRECTED_ADAPTER_BYTES = parent.ADAPTER_BYTES
        legacy.SOURCE_OWNERS = tuple(
            (path, parent.CAPTURE_SHA, parent.CAPTURE_BYTES)
            if path == "candidates/rust/py_bridge.c"
            else (path, parent.ADAPTER_SHA, parent.ADAPTER_BYTES)
            if path == "candidates/rust_candidate.py"
            else (path, fingerprint, count)
            for path, fingerprint, count in original_sources
        )
        need(tuple(legacy.corrected_source_tuples())
             == parent.CORRECTED_SOURCES,
             "bind the complete actual V21 first-party source closure")
        previous_loader = legacy.load_frozen_module

        def historical_first_loader(owner: object,
                                    name: str) -> types.ModuleType:
            module = previous_loader(owner, name)
            if (type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                    == "rebar-owned-repaired-rust-original-campaign-v7"):
                originals = tuple(module.ORIGINAL_SOURCE_OWNERS)
                need(
                    len(originals) == 9
                    and originals[0]
                    == ("candidates/rust_candidate.py",
                        "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
                        31151)
                    and originals[1]
                    == ("candidates/rust/py_bridge.c",
                        "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
                        175676)
                    and originals[2:] == parent.CORRECTED_SOURCES[2:]
                    and tuple(module.HISTORICAL_V2_REPAIRED_SOURCE_OWNERS)
                    == owners
                    and module.BRIDGE_SOURCE_SHA256
                    == historical_values["BRIDGE_SOURCE_SHA256"]
                    and module.BRIDGE_SOURCE_BYTES
                    == historical_values["BRIDGE_SOURCE_BYTES"]
                    and module.HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
                    == historical_values[
                        "HISTORICAL_V2_REPAIRED_PUBLIC_SHA256"
                    ]
                    and module.HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
                    == historical_values[
                        "HISTORICAL_V2_REPAIRED_PUBLIC_BYTES"
                    ]
                    and module.CORRECTED_PUBLIC_SHA256
                    == historical_values["CORRECTED_PUBLIC_SHA256"]
                    and module.CORRECTED_PUBLIC_BYTES
                    == historical_values["CORRECTED_PUBLIC_BYTES"]
                    and module.ENGINE_SHA256 == parent.ENGINE_SHA
                    and module.ENGINE_BYTES == parent.ENGINE_BYTES
                    and module.BRIDGE_SHA256
                    == historical_values["BRIDGE_SHA256"]
                    and module.BRIDGE_BYTES
                    == historical_values["BRIDGE_BYTES"]
                    and callable(module.patched_v2_helpers),
                    "prove unchanged V7/V2 roles before actual V21 promotion",
                )
            return module

        legacy.load_frozen_module = historical_first_loader
        legacy.LOCK_NAME = "recoverable-controller-v19.lock"
        need(legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
             and legacy.PUBLIC_RECOVERY_PRIVATE_PREFIX == RECOVERY_PREFIX
             and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
             and legacy.BUILD_LABEL == BUILD_LABEL
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT == parent.ROOT_PATH
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE
             == parent.ROOT_DEVICE
             and legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE == parent.ROOT_INODE
             and legacy.VERIFIED_NATIVE_ENGINE_SHA256 == parent.ENGINE_SHA
             and legacy.VERIFIED_NATIVE_ENGINE_BYTES == parent.ENGINE_BYTES
             and legacy.VERIFIED_NATIVE_BRIDGE_SHA256 == parent.BRIDGE_SHA
             and legacy.VERIFIED_NATIVE_BRIDGE_BYTES == parent.BRIDGE_BYTES
             and legacy.BUILD[0].sha256 == parent.V21[0][1]
             and legacy.BUILD_RECEIPT.sha256 == parent.V21_PUBLICATION[1]
             and legacy.BUILD_ARCHIVE.sha256 == parent.ARCHIVE_SHA
             and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
             and tuple(legacy.RESTORATION_ORDER)
             == tuple(reversed(base.ROLE_ORDER))
             and tuple(legacy.SUITES) == parent.SUITES,
             "retain exact V21 provenance and original four-role recovery")
        if bundle is None:
            parent.install_exhaustive_publication(legacy)
        return legacy

    return bind


def prepare_parent(parent: types.ModuleType, ancestor: types.ModuleType,
                   previous: dict, failure: dict, historical: dict,
                   recovery: dict) -> None:
    inherited_make_runner = parent.make_runner

    def make_runner(previous_controller: types.ModuleType) -> types.ModuleType:
        runner = inherited_make_runner(previous_controller)
        original_required = runner.actual_required_authority

        def required(base: types.ModuleType) -> dict[str, str]:
            values = dict(original_required(base))
            values.update({
                "previous_v18_source_sha256": V18[0][1],
                "previous_v18_protocol_sha256": V18[1][1],
                "previous_v18_contract_sha256": V18[2][1],
                "previous_v18_entry_failure_sha256": V18_FAILURE[1],
            })
            return values

        runner.actual_required_authority = required
        return runner

    def contract_document(context: dict) -> dict:
        result = enrich(context, ancestor, previous, failure, recovery)
        result["schema"] = SCHEMA + "-recoverable-source-freeze"
        result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
        result.pop("contract_sha256", None)
        return result

    parent.SOURCE = SOURCE
    parent.PROTOCOL = PROTOCOL
    parent.CONTRACT = CONTRACT
    parent.SCHEMA = SCHEMA
    parent.VERSION = VERSION
    parent.LABEL = LABEL
    parent.RECOVERY_PREFIX = RECOVERY_PREFIX
    parent.RECOVERY_ROOT = RECOVERY_ROOT
    parent.make_runner = make_runner
    parent.contract_document = contract_document
    parent.bind_captured_controller = corrected_controller(parent, historical)


def rejected(call: object, label: str, parent: types.ModuleType,
             ancestor: types.ModuleType) -> str:
    need(callable(call), "require an executable V19 source-only control")
    try:
        call()
    except (CampaignError, parent.CampaignError, ancestor.CampaignError,
            ValueError, TypeError, SyntaxError, UnicodeError, OSError):
        return label
    raise CampaignError("accepted hostile actual V19 recovery control: " + label)


def recovery_controls(parent: types.ModuleType, ancestor: types.ModuleType,
                      state: dict, historical: dict, failure: dict,
                      recovery: dict) -> list[str]:
    controls = ancestor.historical_controls(
        parent, state, historical, state["v17_failure"],
    )
    base = state["original_base"]
    guard = state["guard"]
    for key, changed, label in (
        ("schema", SCHEMA + "-durable-publication-receipt",
         "reject-invented-v18-durable-campaign-receipt"),
        ("error_message", "wrong",
         "reject-changed-real-v18-recovery-prefix-failure"),
        ("actual_candidate_workers_started", 1,
         "reject-invented-v18-candidate-worker"),
        ("actual_private_build_root_opens", 1,
         "reject-invented-v18-build-root-access"),
        ("actual_native_libraries_loaded", 1,
         "reject-invented-v18-native-library-load"),
        ("expanded_holdout_cases_opened", 1,
         "reject-invented-v18-expanded-holdout-access"),
        ("candidate_qualified", True,
         "reject-invented-v18-candidate-qualification"),
    ):
        hostile = parent.copy_document(guard, base, failure)
        hostile[key] = changed
        controls.append(rejected(
            lambda value=hostile: validate_v18_failure(value, parent),
            label, parent, ancestor,
        ))
    module = recovery["module"]
    actual_function = module.authenticate_and_rebind_v16_recovery_prefix
    actual_checker = module.checked_v16_recovery_helper_root
    for root, label in (
        ("/", "reject-recovery-filesystem-root"),
        (RECOVERY_ROOT + "/", "reject-recovery-trailing-slash"),
        (RECOVERY_ROOT + "/child", "reject-recovery-nested-child"),
        (RECOVERY_ROOT + "\\cross-family", "reject-recovery-backslash"),
        ("/tmp/" + HISTORICAL_V16_PREFIX + BUILD_SUFFIX,
         "reject-stale-v16-recovery-root"),
        ("/tmp/" + ancestor.RECOVERY_PREFIX + BUILD_SUFFIX,
         "reject-stale-v18-recovery-root"),
        ("/tmp/" + HISTORICAL_V2_PREFIX + BUILD_SUFFIX,
         "reject-immutable-v2-as-selected-recovery-root"),
        ("/tmp/" + RECOVERY_PREFIX + "phase2-v19-stale-original-p0",
         "reject-stale-v19-build-suffix"),
    ):
        helper = make_synthetic_helper()
        helper.PRIVATE_PREFIX = RECOVERY_PREFIX
        controls.append(rejected(
            lambda value=root, item=helper:
                actual_checker(item, value),
            label, parent, ancestor,
        ))
    for prefix, label in (
        (HISTORICAL_V16_PREFIX, "reject-stale-v16-production-recovery-prefix"),
        (ancestor.RECOVERY_PREFIX, "reject-stale-v18-production-recovery-prefix"),
        (HISTORICAL_V2_PREFIX, "reject-reused-historical-v2-recovery-prefix"),
    ):
        synthetic = types.ModuleType("_rebar_v19_hostile_recovery_identity")
        synthetic.__dict__.update(module.__dict__)
        synthetic.PUBLIC_RECOVERY_PRIVATE_PREFIX = prefix
        controls.append(rejected(
            lambda value=synthetic: replace_exact_recovery_prefix(
                value, synthetic=True,
            ),
            label, parent, ancestor,
        ))
    for label, alter in (
        ("reject-missing-authenticated-stale-prefix-constant",
         lambda code: tuple(
             "foreign" if item == HISTORICAL_V16_PREFIX else item
             for item in code.co_consts
         )),
        ("reject-duplicated-authenticated-stale-prefix-constant",
         lambda code: code.co_consts + (HISTORICAL_V16_PREFIX,)),
        ("reject-foreign-authenticated-v21-route-constant",
         lambda code: tuple(
             "phase2-v19-stale-original-p0"
             if item == BUILD_SUFFIX else item
             for item in code.co_consts
         )),
        ("reject-changed-authentic-v18-recovery-failure-constant",
         lambda code: tuple(
             "forged historical failure"
             if item == RECOVERY_FAILURE else item
             for item in code.co_consts
         )),
    ):
        original = actual_function.__code__
        old = tuple(
            HISTORICAL_V16_PREFIX if item == RECOVERY_PREFIX else item
            for item in original.co_consts
        )
        candidate_code = original.replace(co_consts=old)
        candidate_code = candidate_code.replace(
            co_consts=alter(candidate_code),
        )
        candidate = types.ModuleType("_rebar_v19_hostile_recovery_code")
        candidate.__dict__.update(module.__dict__)
        candidate.SCHEMA = SCHEMA
        fake_checker = types.FunctionType(
            actual_checker.__code__, candidate.__dict__,
            actual_checker.__name__, actual_checker.__defaults__,
            actual_checker.__closure__,
        )
        fake_function = types.FunctionType(
            candidate_code, candidate.__dict__, actual_function.__name__,
            actual_function.__defaults__, actual_function.__closure__,
        )
        fake_function.__kwdefaults__ = actual_function.__kwdefaults__
        candidate.checked_v16_recovery_helper_root = fake_checker
        candidate.authenticate_and_rebind_v16_recovery_prefix = fake_function
        controls.append(rejected(
            lambda value=candidate: replace_exact_recovery_prefix(
                value, synthetic=True,
            ),
            label, parent, ancestor,
        ))
    helper = make_synthetic_helper()
    ledger = {"recovery_roots_created": 0,
              "recovery_root_creation_attempted": False}
    restored = actual_function(helper, ledger=ledger)
    need(restored is helper and helper.PRIVATE_PREFIX == RECOVERY_PREFIX
         and ledger["recovery_roots_created"] == 0
         and ledger.get("v16_recovery_prefix_rebound_before_root_creation")
         is True,
         "retain authentic successful corrected recovery after hostile controls")
    return controls


def help_text() -> str:
    return (
        "Frozen first-party Rust original correctness campaign V19\n"
        "Proves both genuine V17/V18 preactivation failures; authenticates "
        "the exact V2 helper and corrects one V16 recovery code constant.\n"
        "Source-only: --render-contract | --self-test | "
        "--verify-frozen-context\n"
        "Actual, separately authorized: --run | --worker | --recover\n"
        "Always pin --source-sha256 and --protocol-sha256; all but "
        "--render-contract require --contract-sha256.\n"
        "Actual operations retain every V21, phase-one, producer, guard, "
        "V16, V17, V18, failure, and recovery authority.\n"
        "Source modes never activate candidates, matching, compilation, "
        "native libraries, roots, archives, clocks, or the holdout.\n"
    )


def main(arguments: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if values == ["--help"]:
        sys.stdout.write(help_text())
        return 0
    guard = None
    try:
        ancestor, parent, previous, prior_state, failure, historical, recovery = (
            load_previous()
        )
        guard = prior_state["guard"]
        prepare_parent(parent, ancestor, previous, failure,
                       historical, recovery)
        options = parent.parse_options(values)
        mode = options["mode"]
        context, state = parent.verify_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"),
            rendering=mode == "--render-contract",
        )
        context = enrich(context, ancestor, previous, failure, recovery)
        state["historical_v2"] = historical
        state["v17_failure"] = parent.document(
            state["original_base"], guard,
            secure_owner(ancestor.V17_FAILURE),
            "actual immutable V17 historical-helper entry failure",
        )
        state["v18_failure"] = failure
        state["historical_recovery"] = recovery
        if mode == "--render-contract":
            result = parent.contract_document(context)
        elif mode in ("--self-test", "--verify-frozen-context"):
            allowed = parent.allowed_source_paths(state["parent"])
            allowed.update(ROOT + "/" + owner[0]
                           for owner in (
                               *V18, *ancestor.V17, ancestor.V7,
                               *ancestor.V2, ancestor.V17_FAILURE,
                               V18_FAILURE, V11,
                           ))
            wall = parent.StrictSourceWall(allowed)
            wall.install()
            if mode == "--self-test":
                result = dict(context)
                result["schema"] = SCHEMA + "-source-self-test"
                controls = parent.hostile_controls(context, state, wall)
                controls.extend(recovery_controls(
                    parent, ancestor, state, historical, failure, recovery,
                ))
                need(len(controls) >= 180,
                     "require complete V2, real failure and recovery controls")
                result["hostile_controls"] = controls
                result["hostile_control_count"] = len(controls)
                result["physically_blocked_effects"] = dict(wall.blocked)
                result["source_only_historical_failure_reproduced_synthetically"] = True
            else:
                result = context
            parent.runtime()
        else:
            result = parent.actual_operation(options, context, state)
        payload = guard.canonical(result)
        need(type(payload) is bytes and 0 < len(payload) <= 1024 * 1024,
             "bound the complete canonical V19 source or original result")
        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except Exception as error:
        if guard is not None:
            try:
                payload = guard.canonical({
                    "schema": SCHEMA + "-entry-failure",
                    "status": "FAIL",
                    "version": VERSION,
                    "error_type": type(error).__name__,
                    "error_message": str(error)[:8192],
                    **parent.zero_effects(),
                })
                sys.stdout.buffer.write(payload)
                sys.stdout.buffer.flush()
            except (OSError, TypeError, ValueError):
                pass
        else:
            sys.stderr.write("V19 campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
