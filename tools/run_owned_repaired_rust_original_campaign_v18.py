#!/usr/bin/env python3
"""Run the actual captured Rust only after its historical helper is proved.

Source modes authenticate the frozen V17 failure and execute the unchanged V7
source-only proof against the complete immutable V2 source and contract. They
never run a matcher or inspect a private root, archive, holdout, or clock. An
explicit actual operation retains the genuine V11 historical-first promotion,
the unchanged physical guard, all 13 original workers, reversible four-owner
restoration, and V17's complete-row durable-publication protection.
"""

from __future__ import annotations

import ast
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v18.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V18.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v18.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v18"
VERSION = 18
BUILD_LABEL = "phase2-v21-rust-captured-findall-root-provenance"
LABEL = BUILD_LABEL + "-original-p0-v18"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v18-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_LABEL + "-original-p0"

V17 = (
    ("tools/run_owned_repaired_rust_original_campaign_v17.py",
     "9ff6b8c213e0a7d370fd51860ba0f6f8f6b98a6e9382bd0a0079dcd52b9b072e",
     79644, 430938),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V17.md",
     "6a609d9f090afd81473d31620b622d1b81c89673f2ace3569be547746f98a3c5",
     5930, 525000),
    ("oracle/phase2/repaired-rust-original-campaign-v17.json",
     "9dc2613370463f6162f65627b21fad854b43caaf6acc31564d7728804f36f40d",
     19442, 525001),
)
V17_FAILURE = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v17-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "original-p0-v17-entry-failure.json",
    "be0de2fe5e72ec17ed181006434176eadf51f06281a6e02aef6838b8e2dd2928",
    1310, 525147,
)
V7 = (
    "tools/run_owned_repaired_rust_original_campaign_v7.py",
    "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
    505616, 431856,
)
V2 = (
    ("tools/run_owned_repaired_rust_original_campaign_v2.py",
     "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3",
     143441, 429079),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md",
     "9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0",
     9342, 524612),
    ("oracle/phase2/repaired-rust-original-campaign-v2.json",
     "bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547",
     15927, 524613),
)
HISTORICAL_BRIDGE_SOURCE_SHA = (
    "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
)
HISTORICAL_BRIDGE_SOURCE_BYTES = 176118
HISTORICAL_ADAPTER_SHA = (
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
)
HISTORICAL_ADAPTER_BYTES = 31464
HISTORICAL_BRIDGE_SHA = (
    "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
)
HISTORICAL_BRIDGE_BYTES = 148656
HISTORICAL_FAILURE = (
    "bind every historical V2 helper role, source, mode and policy "
    "without confusing its adapter with V4, V12, or V13"
)


class CampaignError(Exception):
    """A real frozen predecessor, historical proof, or isolation failed."""


def need(valid: object, reason: str) -> None:
    if valid is not True:
        raise CampaignError(reason)


def secure_owner(owner: tuple, *, maximum: int = 4 * 1024 * 1024) -> bytes:
    need(type(owner) is tuple and len(owner) == 4,
         "require an exact immutable source-only owner")
    path, fingerprint, count, inode = owner
    need(type(path) is str and path and not path.startswith("/")
         and ".." not in path.split("/")
         and not path.endswith((".gz", ".so"))
         and type(fingerprint) is str and len(fingerprint) == 64
         and all(char in "0123456789abcdef" for char in fingerprint)
         and type(count) is int and 0 < count <= maximum
         and type(inode) is int and inode > 0,
         "reject an archive, native library, private root, or unsafe owner")
    descriptor = os.open(
        ROOT + "/" + path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted immutable V18 predecessor: " + path)
        pieces: list[bytes] = []
        remaining = count
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            need(bool(piece), "reject a truncated immutable owner: " + path)
            pieces.append(piece)
            remaining -= len(piece)
        need(not os.read(descriptor, 1),
             "reject an expanded immutable owner: " + path)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a changed immutable owner: " + path)
        return raw
    finally:
        os.close(descriptor)


def literal_assignment(tree: ast.Module, name: str) -> object:
    found: list[ast.AST] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name
                   for target in node.targets):
                need(len(node.targets) == 1,
                     "reject an aliased historical assignment: " + name)
                found.append(node.value)
        elif (isinstance(node, ast.AnnAssign)
              and isinstance(node.target, ast.Name)
              and node.target.id == name):
            need(node.value is not None,
                 "reject an empty historical assignment: " + name)
            found.append(node.value)
        elif (isinstance(node, (ast.AugAssign, ast.Delete))
              and ((isinstance(node, ast.AugAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == name)
                   or (isinstance(node, ast.Delete)
                       and any(isinstance(item, ast.Name) and item.id == name
                               for item in node.targets)))):
            raise CampaignError("reject mutated historical constant: " + name)
    need(len(found) == 1,
         "require exactly one literal historical constant: " + name)
    try:
        return ast.literal_eval(found[0])
    except (ValueError, TypeError, RecursionError) as error:
        raise CampaignError(
            "reject dynamic historical constant: " + name,
        ) from error


def validate_entry_failure(value: object,
                           parent: types.ModuleType) -> dict:
    need(type(value) is dict,
         "require the real complete one-line V17 entry failure")
    assert isinstance(value, dict)
    need(value.get("schema")
         == "rebar-owned-repaired-rust-original-campaign-v17-entry-failure"
         and value.get("status") == "FAIL"
         and value.get("version") == 17
         and value.get("error_type") == "CampaignError"
         and value.get("error_message") == HISTORICAL_FAILURE,
         "preserve the exact genuine V17 historical-helper failure")
    expected = parent.zero_effects()
    need(all(value.get(key) == expected_value
             for key, expected_value in expected.items()),
         "reject any invented V17 workers, native load, root, or measurement")
    need(value.get("actual_candidate_workers_started") == 0
         and value.get("actual_private_build_root_opens") == 0
         and value.get("actual_private_build_root_stats") == 0
         and value.get("expanded_holdout_cases_opened") == 0
         and value.get("candidate_qualified") is False
         and value.get("candidate_correctness") == "NOT MEASURED"
         and value.get("candidate_matching") == "NOT RUN",
         "never reinterpret an early entry failure as a candidate observation")
    return value


def static_historical_verifier(
        parent: types.ModuleType, state: dict) -> dict:
    v7_raw = secure_owner(V7)
    v2_source = secure_owner(V2[0])
    secure_owner(V2[1])
    v2_contract_raw = secure_owner(V2[2])
    guard = state["guard"]
    original = state["original_base"]
    v2_contract = parent.document(
        original, guard, v2_contract_raw,
        "complete immutable original V2 source-freeze contract",
    )
    try:
        v7_tree = ast.parse(v7_raw.decode("utf-8"), filename=V7[0])
        v2_tree = ast.parse(v2_source.decode("utf-8"), filename=V2[0][0])
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise CampaignError("reject malformed exact historical sources") from error
    literal_names = (
        "V2", "SCHEMA", "FAMILY", "ROLE_ORDER",
        "SUITE_COUNT", "CASE_COUNT", "PRIVATE_WAIVER_COUNT",
        "BRIDGE_SOURCE_SHA256", "BRIDGE_SOURCE_BYTES",
        "HISTORICAL_V2_REPAIRED_PUBLIC_SHA256",
        "HISTORICAL_V2_REPAIRED_PUBLIC_BYTES",
        "HISTORICAL_DERIVED_PUBLIC_SHA256",
        "CORRECTED_PUBLIC_SHA256", "CORRECTED_PUBLIC_BYTES",
        "ENGINE_SHA256", "ENGINE_BYTES", "BRIDGE_SHA256",
        "BRIDGE_BYTES", "ORIGINALS", "SUITES",
    )
    values = {name: literal_assignment(v7_tree, name)
              for name in literal_names}
    historical_owners = literal_assignment(v2_tree, "REPAIRED_SOURCE_OWNERS")
    expected_v2 = {
        "source": V2[0][:3],
        "protocol": V2[1][:3],
        "contract": V2[2][:3],
    }
    need(values["V2"] == expected_v2
         and values["SCHEMA"]
         == "rebar-owned-repaired-rust-original-campaign-v7"
         and values["FAMILY"] == "rust"
         and values["ROLE_ORDER"]
         == ("bridge_source", "adapter", "engine", "bridge")
         and values["SUITES"] == parent.SUITES
         and values["SUITE_COUNT"] == parent.WORKER_COUNT
         and values["CASE_COUNT"] == parent.CASE_COUNT
         and values["PRIVATE_WAIVER_COUNT"] == parent.PRIVATE_WAIVER_COUNT
         and values["BRIDGE_SOURCE_SHA256"] == HISTORICAL_BRIDGE_SOURCE_SHA
         and values["BRIDGE_SOURCE_BYTES"] == HISTORICAL_BRIDGE_SOURCE_BYTES
         and values["HISTORICAL_V2_REPAIRED_PUBLIC_SHA256"]
         == HISTORICAL_ADAPTER_SHA
         and values["HISTORICAL_V2_REPAIRED_PUBLIC_BYTES"]
         == HISTORICAL_ADAPTER_BYTES
         and values["CORRECTED_PUBLIC_SHA256"] == parent.ADAPTER_SHA
         and values["CORRECTED_PUBLIC_BYTES"] == parent.ADAPTER_BYTES
         and values["ENGINE_SHA256"] == parent.ENGINE_SHA
         and values["ENGINE_BYTES"] == parent.ENGINE_BYTES
         and values["BRIDGE_SHA256"] == HISTORICAL_BRIDGE_SHA
         and values["BRIDGE_BYTES"] == HISTORICAL_BRIDGE_BYTES
         and type(historical_owners) is tuple
         and len(historical_owners) == len(parent.CORRECTED_SOURCES)
         and historical_owners[0]
         == ("candidates/rust_candidate.py", HISTORICAL_ADAPTER_SHA,
             HISTORICAL_ADAPTER_BYTES)
         and historical_owners[1]
         == ("candidates/rust/py_bridge.c", HISTORICAL_BRIDGE_SOURCE_SHA,
             HISTORICAL_BRIDGE_SOURCE_BYTES)
         and historical_owners[2:] == parent.CORRECTED_SOURCES[2:],
         "separate every authentic immutable V2 role from selected V21 roles")
    definitions = {
        node.name: node for node in v7_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name in (
            "extract_historical_v2_helper_owners",
            "authenticate_historical_v2_helper_source",
        )
    }
    need(set(definitions)
         == {"extract_historical_v2_helper_owners",
             "authenticate_historical_v2_helper_source"},
         "require the two exact authenticated V7 historical source proofs")
    module = types.ModuleType("_rebar_v18_static_immutable_v7_verifier")
    module.__dict__.update(values)
    module.MAX_SOURCE_BYTES = 8 * 1024 * 1024
    module.HISTORICAL_V2_REPAIRED_SOURCE_OWNERS = historical_owners
    module.RESTORATION_ORDER = tuple(reversed(values["ROLE_ORDER"]))
    module.ast = ast
    module.Any = object
    module.CampaignError = CampaignError
    module.require = need
    module.digest = lambda raw: hashlib.sha256(raw).hexdigest()
    module.canonical = guard.canonical

    def grouped(items: dict) -> dict:
        return {
            name: {"path": owner[0], "sha256": owner[1],
                   "bytes": owner[2]}
            for name, owner in sorted(items.items())
        }

    module.grouped_owners = grouped
    extracted = ast.Module(
        body=[
            ast.ImportFrom(module="__future__",
                           names=[ast.alias(name="annotations")], level=0),
            definitions["extract_historical_v2_helper_owners"],
            definitions["authenticate_historical_v2_helper_source"],
        ],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(extracted), V7[0], "exec",
                 dont_inherit=True), module.__dict__)
    proof = module.authenticate_historical_v2_helper_source(
        v2_source, v2_contract,
    )
    need(type(proof) is dict and proof.get("status") == "PASS"
         and proof.get("historical_repaired_source_owner_count") == 9
         and proof.get("historical_public_adapter")
         == {"path": "candidates/rust_candidate.py",
             "sha256": HISTORICAL_ADAPTER_SHA,
             "bytes": HISTORICAL_ADAPTER_BYTES}
         and proof.get("role_order") == list(values["ROLE_ORDER"])
         and proof.get("holdout") == "NOT OPENED"
         and proof.get("candidate_workers_started_by_source_gate") == 0,
         "run and pass the actual unchanged V7 proof before V21 promotion")
    return {"module": module, "proof": proof, "v2_source": v2_source,
            "v2_contract": v2_contract,
            "historical_owners": historical_owners,
            "v7_values": values}


def load_previous() -> tuple[types.ModuleType, dict, dict, dict, dict]:
    raw = secure_owner(V17[0])
    secure_owner(V17[1])
    secure_owner(V17[2])
    parent = types.ModuleType("_rebar_v18_immutable_v17_original_campaign")
    parent.__file__ = ROOT + "/" + V17[0][0]
    exec(compile(raw, parent.__file__, "exec", dont_inherit=True),
         parent.__dict__)
    need(parent.SOURCE == V17[0][0] and parent.PROTOCOL == V17[1][0]
         and parent.CONTRACT == V17[2][0]
         and parent.SCHEMA
         == "rebar-owned-repaired-rust-original-campaign-v17"
         and parent.VERSION == 17 and parent.BUILD_LABEL == BUILD_LABEL
         and callable(parent.verify_context)
         and callable(parent.install_exhaustive_publication)
         and callable(parent.bind_captured_controller),
         "authenticate the exact complete original V17 controller")
    previous, state = parent.verify_context(
        V17[0][1], V17[1][1], V17[2][1],
    )
    need(previous.get("status") == "PASS"
         and previous.get("source_sha256") == V17[0][1]
         and previous.get("protocol_sha256") == V17[1][1]
         and previous.get("contract_sha256") == V17[2][1]
         and previous.get("suite_count") == 13
         and previous.get("case_execution_denominator") == 31237
         and previous.get("private_waiver_count") == 13
         and previous.get("candidate_matching") == "NOT RUN"
         and previous.get("expanded_holdout_cases_opened") == 0,
         "preserve the complete frozen V17 reference without a matcher run")
    failure = parent.document(
        state["original_base"], state["guard"], secure_owner(V17_FAILURE),
        "actual single V17 historical-helper preactivation entry failure",
    )
    validate_entry_failure(failure, parent)
    historical = static_historical_verifier(parent, state)
    parent.runtime()
    return parent, previous, state, failure, historical


def enrich(context: dict, previous: dict, failure: dict,
           historical: dict) -> dict:
    result = dict(context)
    result.update({
        "schema": SCHEMA + "-frozen-context",
        "version": VERSION,
        "previous_v17_source_sha256": V17[0][1],
        "previous_v17_protocol_sha256": V17[1][1],
        "previous_v17_contract_sha256": V17[2][1],
        "previous_v17_frozen_source_status": previous["status"],
        "actual_v17_entry_failure_path": V17_FAILURE[0],
        "actual_v17_entry_failure_sha256": V17_FAILURE[1],
        "actual_v17_entry_failure_bytes": V17_FAILURE[2],
        "actual_v17_entry_failure_inode": V17_FAILURE[3],
        "actual_v17_entry_failure_schema": failure["schema"],
        "actual_v17_entry_failure_status": failure["status"],
        "actual_v17_entry_failure_error_type": failure["error_type"],
        "actual_v17_entry_failure_error_message": failure["error_message"],
        "actual_v17_entry_failure_is_durable_campaign_receipt": False,
        "actual_v17_entry_failure_observation":
            "GENUINE SINGLE PREACTIVATION ATTEMPT; "
            "NOT A DURABLE CAMPAIGN RECEIPT",
        "actual_v17_entry_failure_candidate_workers_started":
            failure["actual_candidate_workers_started"],
        "actual_v17_entry_failure_private_root_opens":
            failure["actual_private_build_root_opens"],
        "actual_v17_entry_failure_private_root_stats":
            failure["actual_private_build_root_stats"],
        "actual_v17_entry_failure_native_libraries_loaded":
            failure["actual_native_libraries_loaded"],
        "historical_v7_source_sha256": V7[1],
        "historical_v2_source_sha256": V2[0][1],
        "historical_v2_protocol_sha256": V2[1][1],
        "historical_v2_contract_sha256": V2[2][1],
        "historical_v2_preflight_status": historical["proof"]["status"],
        "historical_v2_preflight_method":
            "UNCHANGED AUTHENTICATED V7 SOURCE VERIFIER AGAINST "
            "COMPLETE IMMUTABLE V2 SOURCE AND CANONICAL CONTRACT",
        "historical_v2_bridge_source_sha256": HISTORICAL_BRIDGE_SOURCE_SHA,
        "historical_v2_bridge_source_bytes": HISTORICAL_BRIDGE_SOURCE_BYTES,
        "historical_v2_adapter_sha256": HISTORICAL_ADAPTER_SHA,
        "historical_v2_adapter_bytes": HISTORICAL_ADAPTER_BYTES,
        "historical_v2_native_bridge_sha256": HISTORICAL_BRIDGE_SHA,
        "historical_v2_native_bridge_bytes": HISTORICAL_BRIDGE_BYTES,
        "historical_v2_repaired_source_owner_count":
            historical["proof"]["historical_repaired_source_owner_count"],
        "historical_v2_verified_before_selected_v21_promotion": True,
        "historical_v2_candidate_module_imported": False,
        "historical_v2_helper_module_imported": False,
        "historical_v2_source_archive_opened": False,
        "historical_v2_binding_order":
            "PROVE IMMUTABLE V7/V2 FIRST; THEN USE UNCHANGED AUTHENTIC "
            "V11 FOUR-ROLE PROMOTION TO ACTUAL V21",
        "historical_v7_premature_global_mutation_allowed": False,
        "historical_v7_scoped_promotion_wrapper_added": False,
        "historical_v2_matching_engine_wrapped": False,
        "recovery_lock_filename": "recoverable-controller-v18.lock",
        "public_recovery_root": RECOVERY_ROOT,
        "source_only_historical_failure_reproduced_synthetically": False,
        "actual_v18_original_campaign_attempted": False,
    })
    return result


def corrected_controller(parent: types.ModuleType,
                         historical: dict):
    historical_owners = historical["historical_owners"]
    values = historical["v7_values"]

    def bind(state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        runner = state["runner"]
        base = state["base"]
        guard = state["guard"]
        legacy = runner.bind_v16_legacy(context, guard, base, bundle, counts)
        originals = tuple(legacy.SOURCE_OWNERS)
        need(len(originals) == 9
             and sum(row[0] == "candidates/rust/py_bridge.c"
                     for row in originals) == 1
             and sum(row[0] == "candidates/rust_candidate.py"
                     for row in originals) == 1,
             "preserve all nine authenticated original Rust sources")
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
            for path, fingerprint, count in originals
        )
        need(tuple(legacy.corrected_source_tuples())
             == parent.CORRECTED_SOURCES,
             "bind all nine actual selected V21 first-party source owners")
        previous_loader = legacy.load_frozen_module

        def historical_first_loader(owner: object,
                                    name: str) -> types.ModuleType:
            module = previous_loader(owner, name)
            if (type(module) is types.ModuleType
                    and getattr(module, "SCHEMA", None)
                    == "rebar-owned-repaired-rust-original-campaign-v7"):
                originals = tuple(module.ORIGINAL_SOURCE_OWNERS)
                need(
                    len(originals) == len(parent.CORRECTED_SOURCES)
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
                    == historical_owners
                    and module.BRIDGE_SOURCE_SHA256
                    == HISTORICAL_BRIDGE_SOURCE_SHA
                    and module.BRIDGE_SOURCE_BYTES
                    == HISTORICAL_BRIDGE_SOURCE_BYTES
                    and module.HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
                    == HISTORICAL_ADAPTER_SHA
                    and module.HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
                    == HISTORICAL_ADAPTER_BYTES
                    and module.CORRECTED_PUBLIC_SHA256
                    == values["CORRECTED_PUBLIC_SHA256"]
                    and module.CORRECTED_PUBLIC_BYTES
                    == values["CORRECTED_PUBLIC_BYTES"]
                    and module.ENGINE_SHA256 == parent.ENGINE_SHA
                    and module.ENGINE_BYTES == parent.ENGINE_BYTES
                    and module.BRIDGE_SHA256 == HISTORICAL_BRIDGE_SHA
                    and module.BRIDGE_BYTES == HISTORICAL_BRIDGE_BYTES
                    and callable(module.patched_v2_helpers),
                    "require entirely unmodified immutable V7/V2 roles "
                    "before authentic historical helper verification",
                )
                # The genuine V11 controller verifies this unchanged V7/V2
                # helper first. Its existing configure_historical_helpers
                # then promotes all four actual V21 roles. Do not write any
                # historical module global here: doing so caused V17 to fail.
            return module

        legacy.load_frozen_module = historical_first_loader
        legacy.LOCK_NAME = "recoverable-controller-v18.lock"
        need(
            legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
            and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
            and legacy.BUILD_LABEL == BUILD_LABEL
            and legacy.VERIFIED_BUILD_PRIVATE_ROOT == parent.ROOT_PATH
            and legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE == parent.ROOT_DEVICE
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
            "retain the exact V21 engine, bridge, original suites, "
            "four-role recovery journal, and genuine authenticated controller",
        )
        if bundle is None:
            parent.install_exhaustive_publication(legacy)
        return legacy

    return bind


def prepare_parent(parent: types.ModuleType, previous: dict,
                   failure: dict, historical: dict) -> None:
    inherited_runner = parent.make_runner

    def make_runner(previous_controller: types.ModuleType) -> types.ModuleType:
        runner = inherited_runner(previous_controller)
        inherited_required = runner.actual_required_authority

        def required(base: types.ModuleType) -> dict[str, str]:
            result = dict(inherited_required(base))
            result.update({
                "previous_v17_source_sha256": V17[0][1],
                "previous_v17_protocol_sha256": V17[1][1],
                "previous_v17_contract_sha256": V17[2][1],
                "previous_v17_entry_failure_sha256": V17_FAILURE[1],
            })
            return result

        runner.actual_required_authority = required
        return runner

    def contract_document(context: dict) -> dict:
        result = enrich(context, previous, failure, historical)
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


def rejected(call: object, label: str,
             parent: types.ModuleType) -> str:
    need(callable(call), "require an executable V18 historical control")
    try:
        call()
    except (CampaignError, parent.CampaignError, ValueError, TypeError,
            SyntaxError, UnicodeError, OSError):
        return label
    raise CampaignError("accepted a hostile V18 historical control: " + label)


def historical_controls(parent: types.ModuleType, state: dict,
                        historical: dict, failure: dict) -> list[str]:
    module = historical["module"]
    source = historical["v2_source"]
    contract = historical["v2_contract"]
    controls: list[str] = []
    changes = (
        ("BRIDGE_SOURCE_SHA256", parent.CAPTURE_SHA,
         "reject-selected-v21-source-before-historical-v2-proof", True),
        ("BRIDGE_SOURCE_BYTES", parent.CAPTURE_BYTES,
         "reject-selected-v21-source-bytes-before-historical-v2-proof", True),
        ("HISTORICAL_V2_REPAIRED_PUBLIC_SHA256", parent.ADAPTER_SHA,
         "reject-selected-v21-adapter-as-historical-v2-adapter", True),
        ("HISTORICAL_V2_REPAIRED_PUBLIC_BYTES", parent.ADAPTER_BYTES,
         "reject-selected-v21-adapter-bytes-as-historical-v2-adapter", True),
        ("BRIDGE_SHA256", parent.BRIDGE_SHA,
         "reject-selected-v21-native-bridge-as-historical-v2-bridge", True),
        ("BRIDGE_BYTES", parent.BRIDGE_BYTES,
         "reject-selected-v21-native-bridge-bytes-as-historical-v2-bridge", True),
        ("ENGINE_SHA256", "0" * 64,
         "reject-foreign-historical-native-engine", True),
        ("ENGINE_BYTES", parent.ENGINE_BYTES - 1,
         "reject-truncated-historical-native-engine", True),
        ("HISTORICAL_V2_REPAIRED_SOURCE_OWNERS", parent.CORRECTED_SOURCES,
         "reject-all-nine-premature-selected-v21-historical-source-owners",
         False),
        ("ROLE_ORDER", tuple(reversed(module.ROLE_ORDER)),
         "reject-reordered-historical-four-role-verification", True),
    )
    exact_failure_reproduced = 0
    for key, replacement, label, exact_message in changes:
        original = getattr(module, key)
        try:
            setattr(module, key, replacement)
            try:
                module.authenticate_historical_v2_helper_source(
                    source, contract,
                )
            except CampaignError as error:
                if exact_message:
                    need(str(error) == HISTORICAL_FAILURE,
                         "reproduce the exact recorded historical failure: "
                         + label)
                    exact_failure_reproduced += 1
                controls.append(label)
            else:
                raise CampaignError("accepted premature historical role: "
                                    + label)
        finally:
            setattr(module, key, original)
        clean = module.authenticate_historical_v2_helper_source(source, contract)
        need(clean == historical["proof"],
             "restore authentic historical V2 identities after " + label)
    base = state["original_base"]
    guard = state["guard"]
    for key, replacement, label in (
        ("schema", "rebar-owned-repaired-rust-original-campaign-v18-"
         "durable-publication-receipt", "reject-invented-v17-durable-receipt"),
        ("actual_candidate_workers_started", 1,
         "reject-invented-v17-candidate-worker"),
        ("actual_private_build_root_opens", 1,
         "reject-invented-v17-private-root-access"),
        ("candidate_qualified", True,
         "reject-invented-v17-candidate-qualification"),
        ("error_message", "wrong",
         "reject-changed-actual-v17-preactivation-error"),
        ("expanded_holdout_cases_opened", 1,
         "reject-invented-v17-holdout-access"),
    ):
        hostile = parent.copy_document(guard, base, failure)
        hostile[key] = replacement
        controls.append(rejected(
            lambda value=hostile: validate_entry_failure(value, parent),
            label, parent,
        ))
    need(exact_failure_reproduced >= 9,
         "reproduce the real V17 preactivation failure for every V2 role")
    return controls


def help_text() -> str:
    return (
        "Frozen first-party Rust original correctness campaign V18\n"
        "Authenticates the genuine V17 preactivation failure and proves the "
        "immutable historical V2 helper before authentic V21 promotion.\n"
        "Source-only: --render-contract | --self-test | "
        "--verify-frozen-context\n"
        "Actual, separately authorized: --run | --worker | --recover\n"
        "Always pin --source-sha256 and --protocol-sha256; all but "
        "--render-contract also require --contract-sha256.\n"
        "Actual operations require the complete original V21, P0, strict-guard, "
        "V16, V17, V17-failure, recovery, and captured-source authorities.\n"
        "No matcher, candidate, compiler, archive, private root, clock, or "
        "holdout is activated by help or source-only modes.\n"
    )


def main(arguments: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if arguments is None else arguments)
    if values == ["--help"]:
        sys.stdout.write(help_text())
        return 0
    guard = None
    try:
        parent, previous, prior_state, failure, historical = load_previous()
        guard = prior_state["guard"]
        prepare_parent(parent, previous, failure, historical)
        options = parent.parse_options(values)
        mode = options["mode"]
        context, state = parent.verify_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"),
            rendering=mode == "--render-contract",
        )
        context = enrich(context, previous, failure, historical)
        state["historical_v2"] = historical
        state["v17_failure"] = failure
        if mode == "--render-contract":
            result = parent.contract_document(context)
        elif mode in ("--self-test", "--verify-frozen-context"):
            allowed = parent.allowed_source_paths(state["parent"])
            allowed.update(ROOT + "/" + owner[0]
                           for owner in (*V17, V7, *V2, V17_FAILURE))
            wall = parent.StrictSourceWall(allowed)
            wall.install()
            if mode == "--self-test":
                result = dict(context)
                result["schema"] = SCHEMA + "-source-self-test"
                controls = parent.hostile_controls(context, state, wall)
                controls.extend(historical_controls(
                    parent, state, historical, failure,
                ))
                need(len(controls) >= 160,
                     "require all inherited and actual historical controls")
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
             "bound the complete canonical V18 source or actual result")
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
            sys.stderr.write("V18 campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
