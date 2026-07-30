#!/usr/bin/env python3
"""Freeze and, only when separately authorized, run the setter-safe Zig engine."""

from __future__ import annotations

import _io
import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/run_owned_repaired_zig_original_campaign_v14.py"
PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V14.md"
CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v14.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v14"
FAMILY = "zig"
LABEL = "phase2-v14-zig-guard-clean-lifetime-setattr-v2-original-p0-v14"
DEVICE = 2064
MAX_OWNER_BYTES = 8 * 1024 * 1024
CORRECTED_ADAPTER_SHA256 = (
    "c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032"
)
CORRECTED_ADAPTER_BYTES = 67335
RECOVERY = (
    "/tmp/rebar-phase2-repaired-zig-original-campaign-v14-"
    "phase2-v14-zig-guard-clean-lifetime-setattr-v2-original-p0-v14"
)

SETTER = (
    (
        "tools/apply_owned_zig_deallocator_setattr_source_repair_v2.py",
        "42d9ceea51f8a8cb4ba980580ccbc5b079134bc8330bc65b3c05e2f1ec83395b",
        75452,
        430990,
    ),
    (
        "oracle/phase2/ZIG-DEALLOCATOR-SETATTR-SOURCE-REPAIR-V2.md",
        "5aad1504d2b834b2d794cff3659462bff89c573cb8f108010fd7f413683fc359",
        7134,
        525305,
    ),
    (
        "oracle/phase2/zig-deallocator-setattr-source-repair-v2.json",
        "b0b87af889a9147975ccfefc8d3f9cf03f5200a6e6ad90cfaa8679c8c9b5d084",
        13455,
        525306,
    ),
)
PREDECESSOR = (
    (
        "tools/run_owned_repaired_zig_original_campaign_v13.py",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
        246570,
        430932,
    ),
    (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
        9553,
        525201,
    ),
    (
        "oracle/phase2/repaired-zig-original-campaign-v13.json",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
        106084,
        525206,
    ),
)
RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-"
    "original-p0-v13-failures-publication-receipt.json",
    "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca",
    78911,
    525299,
)
ORIGINAL_ADAPTER = (
    "candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/"
    "zig_candidate.py",
    "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50",
    67294,
    525010,
)
V1 = (
    (
        "tools/apply_owned_zig_deallocator_lifetime_source_repair_v1.py",
        "2d2be05fb04d43c453b7e4cd47dc8f55542eeb06b18058c996751b7e8a476e4e",
        85494,
        430556,
    ),
    (
        "oracle/phase2/ZIG-DEALLOCATOR-LIFETIME-SOURCE-REPAIR-V1.md",
        "88dbdad010617a1930bb7e701b8dca02078ab8b6310257bf7f404fc540f3a1bb",
        7910,
        525011,
    ),
    (
        "oracle/phase2/zig-deallocator-lifetime-source-repair-v1.json",
        "2021cca12e9c04ab421dca4fd7cc81e23ffe3b649317eb184dba21e47c6aad4e",
        17782,
        525014,
    ),
)
GUARD = (
    (
        "tools/verify_owned_candidate_runtime_independence_v3.py",
        "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
        59765,
        430856,
    ),
    (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
        "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
        5297,
        525096,
    ),
    (
        "oracle/phase2/candidate-runtime-independence-v3.json",
        "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
        9157,
        525114,
    ),
)
GUARD_V2 = (
    (
        "tools/verify_owned_candidate_runtime_independence_v2.py",
        "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        67097,
        431371,
    ),
    (
        "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
        "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        4437,
        524886,
    ),
    (
        "oracle/phase2/candidate-runtime-independence-v2.json",
        "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        7671,
        524887,
    ),
)
PRODUCER = (
    (
        "tools/run_owned_six_family_original_p0_producer_v5.py",
        "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        102286,
        431370,
    ),
    (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        5270,
        524884,
    ),
    (
        "oracle/phase2/six-family-p0-producer-v5.json",
        "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        21036,
        524885,
    ),
)
SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912),
    ("substitution_v2", 5120),
    ("shape_v2", 10240),
    ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
PASSING = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
MISMATCHES = (
    ("scanner_verbose_v1", 620),
    ("public_types_v1", 248),
    ("substitution_v2", 64),
    ("shape_v2", 672),
    ("public_surface_v19", 96),
)
CALLER_PINS = (
    ("--setter-source-sha256", SETTER[0][1]),
    ("--setter-protocol-sha256", SETTER[1][1]),
    ("--setter-contract-sha256", SETTER[2][1]),
    ("--v13-source-sha256", PREDECESSOR[0][1]),
    ("--v13-protocol-sha256", PREDECESSOR[1][1]),
    ("--v13-contract-sha256", PREDECESSOR[2][1]),
    ("--receipt-sha256", RECEIPT[1]),
    ("--v1-source-sha256", V1[0][1]),
    ("--v1-protocol-sha256", V1[1][1]),
    ("--v1-contract-sha256", V1[2][1]),
    ("--adapter-sha256", ORIGINAL_ADAPTER[1]),
    ("--corrected-adapter-sha256", CORRECTED_ADAPTER_SHA256),
    ("--guard-source-sha256", GUARD[0][1]),
    ("--guard-protocol-sha256", GUARD[1][1]),
    ("--guard-contract-sha256", GUARD[2][1]),
    ("--v2-guard-source-sha256", GUARD_V2[0][1]),
    ("--v2-guard-protocol-sha256", GUARD_V2[1][1]),
    ("--v2-guard-contract-sha256", GUARD_V2[2][1]),
    ("--producer-source-sha256", PRODUCER[0][1]),
    ("--producer-protocol-sha256", PRODUCER[1][1]),
    ("--producer-contract-sha256", PRODUCER[2][1]),
    (
        "--build-receipt-sha256",
        "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d",
    ),
    (
        "--root-receipt-sha256",
        "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2",
    ),
)
MODES = frozenset({
    "--self-test",
    "--verify-frozen-context",
    "--render-contract",
    "--run",
    "--worker",
    "--recover",
})


class CampaignError(Exception):
    """The frozen source, independently owned engine, or real evidence changed."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete authenticated bytes")
    return hashlib.sha256(raw).hexdigest()


def validate_clean() -> None:
    require(
        sys.executable == PYTHON
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.dont_write_bytecode
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "regex" not in sys.modules
        and "ctypes" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "require the isolated pinned CPython and no loaded regex candidate",
    )


def load_repair() -> types.ModuleType:
    validate_clean()
    path, expected, size, inode = SETTER[0]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + path, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_size == size,
            "reject the altered independently frozen setter V2 source owner",
        )
        pieces = []
        remaining = size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            require(bool(chunk), "reject truncated V2 setter source")
            pieces.append(chunk)
            remaining -= len(chunk)
        require(not os.read(descriptor, 1), "reject extended V2 setter source")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        require(
            digest(raw) == expected
            and (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
                before.st_nlink,
            ) == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
                after.st_nlink,
            ),
            "reject setter source bytes changed while they were authenticated",
        )
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_zig_v14_independent_frozen_setter_v2")
    module.__file__ = ROOT + "/" + path
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    require(
        module.SELF == SETTER[0][0]
        and module.PROTOCOL == SETTER[1][0]
        and module.CONTRACT == SETTER[2][0]
        and module.V13 == PREDECESSOR
        and module.V1 == V1
        and module.ACTUAL_V13 == RECEIPT
        and module.LIFETIME_INPUT == ORIGINAL_ADAPTER
        and module.SUITES == SUITES
        and tuple(module.PASSING) == PASSING
        and tuple(module.MISMATCHES) == MISMATCHES
        and len(module.ZERO_KEYS) == 25,
        "reject substituted V2 repair, original test suite, or V13 evidence",
    )
    validate_clean()
    return module


def validate_pins(args: dict[str, str]) -> None:
    require(type(args) is dict, "require independently supplied V14 caller pins")
    for option, expected in CALLER_PINS:
        actual = args.get(option)
        require(
            type(actual) is str
            and len(actual) == 64
            and all(char in "0123456789abcdef" for char in actual)
            and actual == expected,
            "reject omitted, borrowed, or changed V14 caller pin " + option,
        )


def repair_arguments(args: dict[str, str]) -> dict[str, str]:
    return {
        "--v1-source-sha256": args["--v1-source-sha256"],
        "--v1-protocol-sha256": args["--v1-protocol-sha256"],
        "--v1-contract-sha256": args["--v1-contract-sha256"],
        "--v13-source-sha256": args["--v13-source-sha256"],
        "--v13-protocol-sha256": args["--v13-protocol-sha256"],
        "--v13-contract-sha256": args["--v13-contract-sha256"],
        "--receipt-sha256": args["--receipt-sha256"],
        "--adapter-sha256": args["--adapter-sha256"],
    }


def projected_rows(repair: types.ModuleType, state: dict) -> list[dict]:
    rows = state["receipt"]["original_suite_diagnostics"]
    projected = []
    visible_warning_count = 0
    for expected, row in zip(SUITES, rows, strict=True):
        excerpt = row["stderr_literal_excerpt"]
        text = excerpt["text"]
        warning_count = text.count("Exception ignored while calling deallocator")
        visible_warning_count += warning_count
        projected.append({
            "suite": row["suite"],
            "case_execution_denominator": row["case_execution_denominator"],
            "pid": row["pid"],
            "returncode": row["returncode"],
            "status": row["status"],
            "infrastructure_failure": row["infrastructure_failure"],
            "observed_semantic_mismatch_count": (
                row["observed_semantic_mismatch_count"]
            ),
            "guard_installed_before_candidate_import": (
                row["guard_installed_before_candidate_import"]
            ),
            "candidate_imported": row["candidate_imported"],
            "stdout": dict(row["stdout"]),
            "stderr": dict(row["stderr"]),
            "captured_warning_excerpt_bytes": excerpt["captured_bytes"],
            "captured_warning_excerpt_sha256": digest(text.encode("utf-8")),
            "captured_warning_visible_occurrence_count": warning_count,
            "complete_warning_count": "NOT MEASURED",
        })
        require(
            (row["suite"], row["case_execution_denominator"]) == expected
            and warning_count > 0,
            "reject crossed original suite or missing actual V13 warning",
        )
    require(
        len(projected) == 13
        and len({row["pid"] for row in projected}) == 13
        and visible_warning_count == 143,
        "reject the 13 distinct workers or alter their 143 visible warnings",
    )
    return projected


def fixed_original_targets(campaign: types.ModuleType) -> list[dict]:
    require(
        type(campaign.ORIGINALS) is dict
        and set(campaign.ORIGINALS) == {"adapter", "bridge", "engine"},
        "reject the three immutable Zig canonical recovery roles",
    )
    result = []
    for role in ("adapter", "bridge", "engine"):
        expected = campaign.ORIGINALS[role]
        result.append({
            "role": role,
            "path": expected["relative"],
            "sha256": expected["sha256"],
            "bytes": expected["bytes"],
            "device": expected["device"],
            "inode": expected["inode"],
            "mode": format(expected["mode"], "04o"),
            "nlink": expected["nlink"],
            "identity_verified_without_opening": True,
        })
    return result


def build_state(
    repair: types.ModuleType,
    args: dict[str, str],
    wall: object,
    *,
    active: bool = False,
) -> dict:
    validate_pins(args)
    own_paths = (SELF, PROTOCOL, CONTRACT)
    for path in own_paths:
        repair.relative(path)
        wall.allowed.add(ROOT + "/" + path)
    own_source = repair.dynamic_owner(SELF, args["--source-sha256"])
    own_protocol = repair.dynamic_owner(PROTOCOL, args["--protocol-sha256"])
    saved_targets = repair.original_targets
    if active:
        repair.original_targets = fixed_original_targets
    try:
        inherited = repair.context(
            args["--setter-source-sha256"],
            args["--setter-protocol-sha256"],
            repair_arguments(args),
            wall,
        )
    finally:
        repair.original_targets = saved_targets
    producer = inherited["producer"]
    setter_owner = repair.dynamic_owner(
        SETTER[2][0], args["--setter-contract-sha256"],
    )
    setter_raw = repair.read_owner(setter_owner)
    setter_document = producer.JsonReader(setter_raw).parse()
    require(
        setter_document == repair.contract_value(inherited)
        and producer.canonical(setter_document) == setter_raw,
        "reject noncanonical, incomplete, or weakened whole V2 setter freeze",
    )
    corrected = inherited["corrected"]
    require(
        digest(corrected) == CORRECTED_ADAPTER_SHA256
        and len(corrected) == CORRECTED_ADAPTER_BYTES
        and args["--corrected-adapter-sha256"] == digest(corrected)
        and inherited["campaign"].GUARD == GUARD
        and inherited["campaign"].GUARD_V2 == GUARD_V2
        and inherited["campaign"].PRODUCER == PRODUCER
        and inherited["campaign"].V13[3][1]
        == args["--build-receipt-sha256"]
        and inherited["campaign"].V13[4][1]
        == args["--root-receipt-sha256"]
        and inherited["actual"]["passing_suites"] == PASSING
        and inherited["actual"]["semantic_failures"] == MISMATCHES
        and inherited["actual"]["warning_suites"]
        == tuple(name for name, _ in SUITES)
        and inherited["actual"]["stderr_bytes"] == 428866
        and inherited["actual"]["stdout_bytes"] == 82236727
        and inherited["actual"]["captured_warning_bytes"] == 53211
        and inherited["original_targets"]
        == fixed_original_targets(inherited["campaign"])
        and inherited["campaign_state"]["guard_implementation"].CREATE_EVENT
        == "cpython.PyInterpreterState_New"
        and inherited["campaign_state"]["guard_implementation"]
        .RuntimePolicy.prepare_family
        is inherited["campaign_state"]["guard_implementation"]
        .BASE.RuntimePolicy.prepare_family,
        "reject the actual V13 failure, true V3 guard, or in-memory setter repair",
    )
    projected = projected_rows(repair, inherited)
    validate_clean()
    return {
        "repair": repair,
        "producer": producer,
        "repair_state": inherited,
        "repair_contract": setter_document,
        "source": own_source,
        "protocol": own_protocol,
        "rows": projected,
        "corrected": corrected,
        "active": active,
    }


def contract_value(state: dict) -> dict:
    repair = state["repair"]
    inherited = state["repair_state"]
    actual = state["repair_contract"]["actual_v13_failure"]
    future_stem = "repaired-zig-original-campaign-v14-" + LABEL
    return {
        "schema": SCHEMA + "-guarded-setter-safe-source-freeze",
        "version": 14,
        "status": (
            "SOURCE FROZEN; V3-GUARDED SETTER-SAFE ZIG MATCHING NOT RUN"
        ),
        "family": FAMILY,
        "label": LABEL,
        "source": repair.record(state["source"]),
        "protocol": repair.record(state["protocol"]),
        "goal": repair.record(repair.GOAL),
        "pinned_cpython": dict(state["repair_contract"]["pinned_cpython"]),
        "original_oracle": dict(state["repair_contract"]["original_oracle"]),
        "immutable_v5_original_producer": {
            "owners": [repair.record(owner) for owner in PRODUCER],
            "version": 5,
            "source_modified": False,
            "original_suites_modified": False,
            "original_workers_started_by_source_gate": 0,
        },
        "independently_frozen_setter_v2": {
            "owners": [repair.record(owner) for owner in SETTER],
            "schema": state["repair_contract"]["schema"],
            "version": 2,
            "whole_canonical_contract_authenticated": True,
            "must_be_committed_and_pushed_before_v14": True,
            "independent_source_effect_count": len(repair.ZERO_KEYS),
            "source_only_effects": dict(
                state["repair_contract"]["source_only_effects"]
            ),
        },
        "pushed_v13_original_campaign": {
            "owners": [repair.record(owner) for owner in PREDECESSOR],
            "source_schema": (
                "rebar-owned-repaired-zig-original-campaign-v13-"
                "guarded-lifetime-source-freeze"
            ),
            "version": 13,
            "source_modified": False,
            "whole_source_contract_verified": True,
        },
        "complete_actual_v13_publication": {
            "plaintext_owner": repair.record(RECEIPT),
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "actual_candidate_workers": 13,
            "unique_candidate_worker_count": 13,
            "completed_suite_count": 12,
            "verified_passing_suite_count": 7,
            "verified_passing_case_count": 4607,
            "verified_passing_suites": list(
                actual["verified_passing_suites"]
            ),
            "completed_semantic_failure_count": 5,
            "completed_semantic_failures": list(
                actual["completed_semantic_failures"]
            ),
            "observed_semantic_mismatch_lower_bound": 1700,
            "semantic_mismatch_count": "NOT MEASURED",
            "infrastructure_failure_count": 1,
            "all_original_suites_attempted": True,
            "all_three_original_targets_restored": True,
            "actual_complete_stdout_bytes": 82236727,
            "actual_complete_stderr_bytes": 428866,
            "actual_captured_warning_excerpt_bytes": 53211,
            "warning_worker_count": 13,
            "warning_passing_worker_count": 7,
            "visible_warning_occurrence_lower_bound": 143,
            "full_warning_occurrence_count": "NOT MEASURED",
            "complete_original_suite_rows": list(state["rows"]),
            "original_public_rows_canonical_sha256": digest(
                state["producer"].canonical(
                    inherited["receipt"]["original_suite_diagnostics"]
                )
            ),
            "actual_subinterpreter_failure": dict(
                actual["separate_actual_subinterpreter_failure"]
            ),
            "actual_child_interpreters_created": 0,
            "actual_child_guards_installed": 0,
            "actual_child_case_executions": 0,
            "archive_metadata": dict(inherited["receipt"]["archive"]),
            "compressed_archive_opened": False,
            "corrected_warning_status": "NOT MEASURED",
            "corrected_child_behavior": "NOT MEASURED",
        },
        "first_party_in_memory_setter_safe_adapter": {
            "frozen_input": repair.record(ORIGINAL_ADAPTER),
            "prospective_variant": dict(
                state["repair_contract"]["first_party_setter_repair"]
                ["prospective_variant"]
            ),
            "whole_source_sha256": CORRECTED_ADAPTER_SHA256,
            "whole_source_bytes": CORRECTED_ADAPTER_BYTES,
            "source_repair": dict(inherited["proof"]),
            "complete_byte_replacement_proven_in_memory": True,
            "physical_status": "NOT MATERIALIZED",
            "prospective_variant_written": False,
            "public_pattern_setter_changed": False,
            "early_bound_object_setattr": True,
            "module_global_pattern_methods_accessed_in_finalizer": False,
            "release_before_handle_clear": False,
            "native_release_failure_suppressed": False,
            "matcher_parser_compiler_scanner_changed": False,
            "engine_or_bridge_changed": False,
            "external_regex_dependency_added": False,
            "stdlib_regex_fallback_added": False,
            "cross_candidate_engine_added": False,
            "candidate_built": False,
            "candidate_imported": False,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
        },
        "pushed_v3_real_interpreter_guard": {
            "owners": [repair.record(owner) for owner in GUARD],
            "version": 3,
            "inherited_v2_owners": [
                repair.record(owner) for owner in GUARD_V2
            ],
            "exact_v2_function_and_globals": True,
            "native_owner_field_count": 14,
            "genuine_live_provider_frame_required": True,
            "expected_child_interpreters_created": 11,
            "expected_child_case_executions": 394,
            "expected_child_bootstrap_executions": 11,
            "expected_child_cleanup_executions": 11,
            "expected_total_real_child_executions": 416,
            "actual_child_interpreters_created_in_source_gate": 0,
            "actual_child_guards_installed_in_source_gate": 0,
            "actual_child_case_executions_in_source_gate": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "future_actual_run": {
            "authorization": "SEPARATE EXPLICIT FULLY PINNED --run",
            "root_exclusive_canonical_target_window_required": True,
            "caller_pins": [
                {"option": option, "sha256": value}
                for option, value in CALLER_PINS
            ],
            "family": FAMILY,
            "label": LABEL,
            "prospective_adapter_sha256": CORRECTED_ADAPTER_SHA256,
            "prospective_adapter_bytes": CORRECTED_ADAPTER_BYTES,
            "adapter_materialization": (
                "IN MEMORY; CANONICAL ACTIVATION ONLY DURING AUTHORIZED RUN"
            ),
            "candidate_workers_required": 13,
            "unique_candidate_workers_required": 13,
            "case_execution_denominator": 31237,
            "guard_installed_before_candidate_import": True,
            "guard_version": 3,
            "native_build_authorized": False,
            "compiler_processes_authorized": False,
            "recovery_root": RECOVERY,
            "exclusive_recovery_lock": "campaign-v14.lock",
            "role_order": ["engine", "bridge", "adapter"],
            "restoration_order": ["adapter", "bridge", "engine"],
            "canonical_original_targets": dict(
                inherited["campaign"].ORIGINALS
            ),
            "exact_original_inode_backup_required": True,
            "all_three_original_targets_restored_before_publication": True,
            "separate_pinned_recovery_action": "--recover",
            "per_suite_timeout_seconds": 120,
            "maximum_serial_timeout_seconds": 1560,
            "continue_after_every_recorded_failure": True,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "failure_publication_receipt": (
                "oracle/phase2/evidence/" + future_stem
                + "-failures-publication-receipt.json"
            ),
            "failure_result_archive": (
                "oracle/phase2/evidence/" + future_stem
                + "-failures.json.gz"
            ),
            "success_publication_receipt": (
                "oracle/phase2/evidence/" + future_stem
                + "-success-publication-receipt.json"
            ),
            "success_result_archive": (
                "oracle/phase2/evidence/" + future_stem
                + "-success.json.gz"
            ),
            "hidden_cases_read": 0,
            "benchmark_files_opened": 0,
            "holdout_files_opened": 0,
        },
        "source_only_worker_transport": {
            "injective_unicode_transport_required": True,
            "reserved_key_collisions_rejected": True,
            "full_worker_stdout_and_stderr_preserved": True,
            "all_13_original_diagnostics_preserved": True,
            "complete_nested_failure_preserved": True,
            "source_gate_candidate_workers": 0,
        },
        "expanded_sealed_holdout_proposal": dict(
            state["repair_contract"]["expanded_sealed_holdout_proposal"]
        ),
        "physical_source_wall": {
            "inherited_corrected_setter_v2_wall": True,
            "direct_io_open_audit_enforced": True,
            "physical_owner_mode_and_flags_verified": True,
            "direct_stdout_and_stderr_descriptor_writes_forbidden": True,
            "direct_os_writev_forbidden_when_available": True,
            "candidate_namespace_import_forbidden": True,
            "stdlib_and_external_regex_import_forbidden": True,
            "native_library_open_forbidden": True,
            "archive_open_forbidden": True,
            "private_root_open_forbidden": True,
            "holdout_open_forbidden": True,
            "clock_and_benchmark_forbidden": True,
            "source_only_effect_count": len(repair.ZERO_KEYS),
        },
        "source_only_effects": {key: 0 for key in repair.ZERO_KEYS},
        "corrected_original_matching": "NOT RUN",
        "corrected_supplemental_matching": "NOT RUN",
        "corrected_warning": "NOT MEASURED",
        "corrected_subinterpreter": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "current_qualified_candidates": 0,
        "minimum_qualified_candidates": 3,
        "holdout_case_count": 14155776,
        "holdout_case_status": "NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def verify_document(document: object, state: dict) -> None:
    producer = state["producer"]
    require(
        type(document) is dict
        and document == contract_value(state)
        and producer.canonical(document)
        == producer.canonical(contract_value(state)),
        "reject a noncanonical, truncated, or silently changed V14 contract",
    )


def reject(operation: object, label: str, repair: types.ModuleType) -> int:
    require(callable(operation), "require an actual hostile source control")
    try:
        operation()
    except (
        CampaignError,
        repair.CampaignError,
        OSError,
        ImportError,
        SyntaxError,
        ValueError,
        TypeError,
        AttributeError,
        KeyError,
    ):
        return 1
    raise CampaignError("accepted hostile V14 source-only control: " + label)


def hostile_controls(state: dict, args: dict, wall: object) -> tuple[int, int]:
    repair = state["repair"]
    inherited = state["repair_state"]
    inherited_checks = repair.hostile_source_controls(inherited, wall)
    require(inherited_checks >= 80, "reject incomplete inherited V2 controls")
    checks = 0
    producer = state["producer"]
    for option, expected in CALLER_PINS:
        forged = dict(args)
        forged[option] = "0" * 64 if expected != "0" * 64 else "f" * 64
        checks += reject(
            lambda value=forged: validate_pins(value),
            "forged independent caller authority " + option,
            repair,
        )
    for name in ("re", "_sre", "regex", "re2", "ctypes", "subprocess",
                 "gzip", "socket", "threading", "_interpreters",
                 "candidates", "candidates.zig_candidate",
                 "candidates.rust_candidate", "performance.final_holdout"):
        checks += reject(
            lambda item=name: builtins.__import__(item),
            "forbidden regex, candidate, worker, or final-holdout import " + name,
            repair,
        )
    for path in (
        ROOT + "/candidates/zig_candidate.py",
        ROOT + "/candidates/rust_candidate.py",
        ROOT + "/candidates/_zig_probe.so",
        ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ROOT + "/" + repair.PROSPECTIVE_VARIANT,
        ROOT + "/performance/final-holdout.json",
        ROOT + "/README.md",
        ROOT + "/oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v13-"
        "phase2-v13-zig-guard-clean-lifetime-v1-"
        "original-p0-v13-failures.json.gz",
        RECOVERY,
    ):
        checks += reject(
            lambda item=path: os.open(item, os.O_RDONLY),
            "forbidden native, archive, private recovery, or holdout " + path,
            repair,
        )
    for path in (ROOT + "/" + SELF, ROOT + "/" + PROTOCOL,
                 ROOT + "/" + CONTRACT, ROOT + "/" + ORIGINAL_ADAPTER[0]):
        checks += reject(
            lambda item=path: _io.FileIO(item, "r+"),
            "direct _io owner mutation " + path,
            repair,
        )
        checks += reject(
            lambda item=path: sys.audit(
                "open", item, "w", os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            ),
            "synthetic physical truncation audit " + path,
            repair,
        )
    for operation, label in (
        (lambda: os.write(1, b"forged"), "direct stdout descriptor"),
        (lambda: os.write(2, b"forged"), "direct stderr descriptor"),
        (
            lambda: sys.audit("subprocess.Popen", "zig", [], None, None),
            "candidate worker or Zig compiler",
        ),
        (lambda: sys.audit("ctypes.dlopen", "foreign.so"), "native loader"),
        (
            lambda: sys.audit("cpython.PyInterpreterState_New", None),
            "fabricated or real child interpreter",
        ),
        (lambda: repair.relative("../holdout"), "escaped source path"),
    ):
        checks += reject(operation, label, repair)
    if hasattr(os, "writev"):
        checks += reject(
            lambda: os.writev(1, [b"forged"]),
            "direct vectored stdout descriptor write",
            repair,
        )
    for index, (suite, _count) in enumerate(SUITES):
        poisoned = repair.cloned(inherited["receipt"], producer)
        poisoned["original_suite_diagnostics"][index]["suite"] = (
            suite + "_forged"
        )
        checks += reject(
            lambda document=poisoned: repair.validate_v13_publication(
                document, inherited["campaign"]
            ),
            "changed complete genuine V13 suite " + suite,
            repair,
        )
    for suite, _ in MISMATCHES:
        poisoned = repair.mutated_row(
            inherited, suite, "observed_semantic_mismatch_count", 0
        )
        checks += reject(
            lambda document=poisoned: repair.validate_v13_publication(
                document, inherited["campaign"]
            ),
            "suppressed separately measured V13 failure " + suite,
            repair,
        )
    for key, replacement in (
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("verified_passing_case_count", 4608),
        ("completed_suite_count", 13),
        ("unique_candidate_worker_count", 12),
        ("observed_semantic_mismatch_lower_bound", 1699),
        ("semantic_mismatch_count", 0),
        ("infrastructure_failure_count", 0),
        ("all_three_original_targets_restored", False),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        poisoned = repair.mutated_receipt(inherited, key, replacement)
        checks += reject(
            lambda document=poisoned: repair.validate_v13_publication(
                document, inherited["campaign"]
            ),
            "fabricated V13 result or measurement " + key,
            repair,
        )
    for field, value in (
        ("status", "PASS"),
        ("version", 13),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("corrected_warning", "PASS"),
        ("corrected_subinterpreter", "PASS"),
        ("winner_selected", True),
    ):
        poisoned = repair.cloned(contract_value(state), producer)
        poisoned[field] = value
        checks += reject(
            lambda document=poisoned: verify_document(document, state),
            "invented V14 source-freeze result " + field,
            repair,
        )
    for selected in ("--apply", "--build", "--install", "--benchmark",
                     "--generate", "--open-holdout", "--worker-timeout-seconds"):
        checks += reject(
            lambda mode=selected: parse([mode]),
            "unauthorized or incomplete V14 action " + selected,
            repair,
        )
    require(
        checks >= 80 and inherited_checks >= 80 and wall.denials >= 50,
        "reject incomplete genuine V13, setter-safe, and physical V14 controls",
    )
    validate_clean()
    return inherited_checks, checks


def source_result(
    state: dict,
    args: dict,
    *,
    inherited_checks: int,
    controls: int,
    mode: str,
) -> dict:
    repair = state["repair"]
    return {
        "schema": SCHEMA + (
            "-source-self-test"
            if mode == "--self-test" else "-verified-frozen-context"
        ),
        "status": "PASS",
        "family": FAMILY,
        "label": LABEL,
        "source_sha256": args["--source-sha256"],
        "protocol_sha256": args["--protocol-sha256"],
        "contract_sha256": args["--contract-sha256"],
        "setter_source_sha256": SETTER[0][1],
        "setter_protocol_sha256": SETTER[1][1],
        "setter_contract_sha256": SETTER[2][1],
        "v13_source_sha256": PREDECESSOR[0][1],
        "v13_protocol_sha256": PREDECESSOR[1][1],
        "v13_contract_sha256": PREDECESSOR[2][1],
        "actual_v13_receipt_sha256": RECEIPT[1],
        "actual_v13_publication_status": "PASS",
        "actual_v13_publication_pass_means": "DURABLE PUBLICATION ONLY",
        "actual_v13_candidate_status": "FAIL",
        "actual_v13_candidate_qualified": False,
        "actual_v13_candidate_workers": 13,
        "actual_v13_unique_candidate_workers": 13,
        "actual_v13_completed_suite_count": 12,
        "actual_v13_verified_passing_suite_count": 7,
        "actual_v13_verified_passing_case_count": 4607,
        "actual_v13_semantic_failure_count": 5,
        "actual_v13_semantic_mismatch_lower_bound": 1700,
        "actual_v13_semantic_mismatch_count": "NOT MEASURED",
        "actual_v13_warning_worker_count": 13,
        "actual_v13_visible_warning_occurrence_lower_bound": 143,
        "actual_v13_complete_warning_occurrence_count": "NOT MEASURED",
        "actual_v13_warning_passing_worker_count": 7,
        "actual_v13_complete_stderr_bytes": 428866,
        "actual_v13_complete_stdout_bytes": 82236727,
        "actual_v13_captured_warning_excerpt_bytes": 53211,
        "actual_v13_infrastructure_failure_count": 1,
        "actual_v13_child_interpreters_created": 0,
        "actual_v13_child_guards_installed": 0,
        "actual_v13_child_case_executions": 0,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "named_private_waiver_count": 13,
        "supplemental_reference_case_count": 8244,
        "supplemental_candidate_matching": "NOT RUN",
        "original_lifetime_adapter_sha256": ORIGINAL_ADAPTER[1],
        "prospective_setter_adapter_sha256": CORRECTED_ADAPTER_SHA256,
        "prospective_setter_adapter_bytes": CORRECTED_ADAPTER_BYTES,
        "prospective_setter_adapter_status": "NOT MATERIALIZED",
        "changed_finalizer_count": 1,
        "other_ast_unchanged": True,
        "public_pattern_setter_changed": False,
        "early_bound_object_setattr": True,
        "immutable_guard_version": 3,
        "immutable_guard_source_sha256": GUARD[0][1],
        "immutable_v2_guard_source_sha256": GUARD_V2[0][1],
        "expected_real_child_interpreters": 11,
        "expected_real_child_case_executions": 394,
        "expected_total_real_child_executions": 416,
        "synthetic_setter_lifecycle_controls": (
            "PASS" if mode == "--self-test" else "NOT RUN"
        ),
        "inherited_v2_source_only_hostile_controls": inherited_checks,
        "new_v14_source_only_hostile_controls": controls,
        "source_only_hostile_controls": inherited_checks + controls,
        "source_only_effects": {name: 0 for name in repair.ZERO_KEYS},
        "direct_io_write_bypass_forbidden": True,
        "direct_stdout_descriptor_write_forbidden": True,
        "corrected_candidate_matching": "NOT RUN",
        "corrected_warning": "NOT MEASURED",
        "corrected_subinterpreter": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "holdout_case_count": 14155776,
        "holdout_case_status": "NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def source_mode(mode: str, args: dict[str, str]) -> bytes:
    repair = load_repair()
    with repair.SourceWall() as wall:
        original_write = os.write
        original_writev = getattr(os, "writev", None)
        os.write = wall.blocked
        if original_writev is not None:
            os.writev = wall.blocked
        try:
            state = build_state(repair, args, wall)
            producer = state["producer"]
            if mode == "--render-contract":
                return producer.canonical(contract_value(state))
            contract_owner = repair.dynamic_owner(
                CONTRACT, args["--contract-sha256"],
            )
            raw = repair.read_owner(contract_owner)
            document = producer.JsonReader(raw).parse()
            require(
                producer.canonical(document) == raw,
                "reject altered or noncanonical whole V14 contract bytes",
            )
            verify_document(document, state)
            inherited_checks = controls = 0
            if mode == "--self-test":
                inherited_checks, controls = hostile_controls(state, args, wall)
            return producer.canonical(source_result(
                state,
                args,
                inherited_checks=inherited_checks,
                controls=controls,
                mode=mode,
            ))
        finally:
            os.write = original_write
            if original_writev is not None:
                os.writev = original_writev


def parse(arguments: list[str]) -> tuple[str, dict[str, str]]:
    require(type(arguments) is list, "reject noncanonical V14 command arguments")
    selected = [argument for argument in arguments if argument in MODES]
    require(len(selected) == 1, "select exactly one frozen V14 campaign action")
    mode = selected[0]
    allowed = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        "--family", "--label", "--suite", "--recovery-journal-sha256",
        *(option for option, _expected in CALLER_PINS),
    }
    result = {}
    index = 0
    while index < len(arguments):
        option = arguments[index]
        if option in MODES:
            require(option == mode, "reject conflicting V14 execution authority")
            index += 1
            continue
        require(
            option in allowed
            and option not in result
            and index + 1 < len(arguments),
            "reject unknown, repeated, missing, or incomplete V14 authority",
        )
        result[option] = arguments[index + 1]
        index += 2
    required = {
        "--source-sha256", "--protocol-sha256",
        *(option for option, _expected in CALLER_PINS),
    }
    if mode != "--render-contract":
        required.add("--contract-sha256")
    if mode in {"--run", "--worker", "--recover"}:
        required |= {"--family", "--label"}
    if mode in {"--worker", "--recover"}:
        required.add("--recovery-journal-sha256")
    if mode == "--worker":
        required.add("--suite")
    require(
        set(result) == required,
        "require all independently supplied V14, V13, V2, and guard pins",
    )
    validate_pins(result)
    if mode in {"--run", "--worker", "--recover"}:
        require(
            result["--family"] == FAMILY and result["--label"] == LABEL,
            "reject a cross-family or unpinned actual V14 campaign",
        )
    return mode, result


def v14_recovery_directory(previous: types.ModuleType, create: bool):
    previous.require(
        type(create) is bool
        and os.path.dirname(RECOVERY) == "/tmp"
        and RECOVERY.startswith("/tmp/rebar-phase2-repaired-zig-"),
        "reject an unsafe V14 recovery-root target",
    )
    if create:
        try:
            os.mkdir(RECOVERY, 0o700)
        except FileExistsError:
            pass
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(RECOVERY, flags)
    try:
        info = os.fstat(directory)
        previous.require(
            stat.S_ISDIR(info.st_mode)
            and stat.S_IMODE(info.st_mode) == 0o700
            and info.st_uid == os.geteuid(),
            "reject a shared or substituted V14 recovery root",
        )
        lock_flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        lock_flags |= getattr(os, "O_NOFOLLOW", 0)
        if create:
            lock_flags |= os.O_CREAT
        lock = os.open("campaign-v14.lock", lock_flags, 0o600, dir_fd=directory)
        try:
            owner = os.fstat(lock)
            previous.require(
                stat.S_ISREG(owner.st_mode)
                and stat.S_IMODE(owner.st_mode) == 0o600
                and owner.st_uid == os.geteuid()
                and owner.st_nlink == 1,
                "reject a foreign V14 recovery lock",
            )
            fcntl = __import__("fcntl")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(lock)
            raise
        return directory, lock
    except BaseException:
        os.close(directory)
        raise


def v14_names(previous: types.ModuleType, role: str) -> tuple[str, str]:
    previous.require(role in previous.ROLES, "reject a crossed V14 native role")
    stem = ".rebar-zig-setter-safe-v14-" + role
    return stem + ".stage", stem + ".original"


def prepare_active_state(args: dict[str, str]) -> tuple[types.ModuleType, dict]:
    repair = load_repair()
    with repair.SourceWall() as wall:
        state = build_state(repair, args, wall, active=True)
        owner = repair.dynamic_owner(CONTRACT, args["--contract-sha256"])
        raw = repair.read_owner(owner)
        document = state["producer"].JsonReader(raw).parse()
        require(
            state["producer"].canonical(document) == raw,
            "reject noncanonical actual V14 worker context",
        )
        verify_document(document, state)
    previous = state["repair_state"]["campaign"]
    runtime = dict(state["repair_state"]["campaign_state"])
    runtime["proof"] = dict(state["repair_state"]["proof"])
    raw_read_owner = previous.read_owner
    corrected_owner = (
        repair.PROSPECTIVE_VARIANT,
        CORRECTED_ADAPTER_SHA256,
        CORRECTED_ADAPTER_BYTES,
        ORIGINAL_ADAPTER[3],
    )

    def in_memory_read(owner):
        if owner == corrected_owner:
            return state["corrected"]
        return raw_read_owner(owner)

    def active_verify(source_sha, protocol_sha, contract_sha, *, active=False):
        previous.require(
            source_sha == args["--source-sha256"]
            and protocol_sha == args["--protocol-sha256"]
            and contract_sha == args["--contract-sha256"],
            "reject changed actual V14 worker campaign source pins",
        )
        return runtime

    def stem(suffix, *, observed=None):
        previous.require(
            suffix in ("success", "failures"),
            "reject an invented actual V14 publication result",
        )
        expected = "repaired-zig-original-campaign-v14-" + LABEL + "-" + suffix
        if observed is not None:
            previous.require(
                observed == expected,
                "reject a crossed V14 publication owner",
            )
        return expected

    previous.SELF = SELF
    previous.PROTOCOL = PROTOCOL
    previous.CONTRACT = CONTRACT
    previous.SCHEMA = SCHEMA
    previous.LABEL = LABEL
    previous.RECOVERY = RECOVERY
    previous.LIFETIME_ADAPTER = corrected_owner
    previous.REPAIRED_DEALLOCATOR = repair.NEW_DEALLOCATOR
    previous.ACTUAL_CALLER_PINS = CALLER_PINS
    previous.read_owner = in_memory_read
    previous.verify = active_verify
    previous.recovery_directory = lambda create: v14_recovery_directory(
        previous, create
    )
    previous.names = lambda role: v14_names(previous, role)
    previous.publication_stem = stem
    require(
        previous.SUITES == SUITES
        and previous.GUARD == GUARD
        and previous.GUARD_V2 == GUARD_V2
        and previous.PRODUCER == PRODUCER
        and previous.LIFETIME_ADAPTER[1] == CORRECTED_ADAPTER_SHA256
        and previous.LIFETIME_ADAPTER[2] == CORRECTED_ADAPTER_BYTES
        and previous.SCHEMA == SCHEMA
        and previous.LABEL == LABEL
        and previous.RECOVERY == RECOVERY,
        "reject crossed source, real guard, matcher, or actual V14 recovery",
    )
    return previous, state


def actual_mode(mode: str, args: dict[str, str]) -> bytes:
    previous, state = prepare_active_state(args)
    if mode == "--worker":
        return previous.worker_canonical(previous.worker(args))
    if mode == "--recover":
        return state["producer"].canonical(previous.recover(args))
    require(mode == "--run", "reject an unselected real V14 candidate action")
    return state["producer"].canonical(previous.campaign(args))


def main() -> int:
    mode, args = parse(list(sys.argv[1:]))
    if mode in {"--self-test", "--verify-frozen-context", "--render-contract"}:
        output = source_mode(mode, args)
    else:
        output = actual_mode(mode, args)
    require(type(output) is bytes and bool(output), "reject incomplete V14 output")
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        sys.stderr.write(
            "first-party V3-guarded setter-safe Zig V14 campaign rejected: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        )
        raise SystemExit(1) from error
