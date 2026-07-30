#!/usr/bin/env python3
"""Freeze a first-party Zig campaign with separate source and runtime authority."""

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
SELF = "tools/run_owned_repaired_zig_original_campaign_v15.py"
PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V15.md"
CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v15.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v15"
FAMILY = "zig"
LABEL = "phase2-v15-zig-guard-clean-lifetime-setattr-v2-original-p0-v15"
DEVICE = 2064
MAX_OWNER_BYTES = 8 * 1024 * 1024
RECOVERY = (
    "/tmp/rebar-phase2-repaired-zig-original-campaign-v15-"
    "phase2-v15-zig-guard-clean-lifetime-setattr-v2-original-p0-v15"
)
PREVIOUS = (
    (
        "tools/run_owned_repaired_zig_original_campaign_v14.py",
        "8757ff2fdda5e8e60ee694b0d803018ddf33ea7266b8d7a5eff6d52d0866569d",
        49601,
        431103,
    ),
    (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V14.md",
        "691ab654b88ed30f6cd0729d987415162708fdfb90c36d91bf41dcefdbb5fcef",
        7539,
        525386,
    ),
    (
        "oracle/phase2/repaired-zig-original-campaign-v14.json",
        "1c7326dc2f63635f3e32ec0558b51f21c952d51480f336e3b0d4d49e38428a0a",
        31103,
        525387,
    ),
)
ACTUAL_V14_FAILURE = (
    "oracle/phase2/evidence/"
    "zig-original-campaign-v14-setter-safe-prepublication-controller-failure.json",
    "2d1bad717e782b7ed3e0af856f8687e9a29abc93ebf1553adc6d65f668aa5c65",
    5474,
    525461,
)
EXPECTED_FAILURE_KEYS = frozenset({
    "actual_candidate_worker_count",
    "actual_completed_suite_count",
    "actual_semantic_mismatch_count",
    "actual_verified_passing_case_count",
    "all_three_original_targets_restored",
    "attempt_count",
    "candidate_process_exit_code",
    "candidate_status",
    "complete_captured_standard_error",
    "complete_captured_standard_output",
    "contract_sha256",
    "controller_error_message",
    "controller_error_type",
    "corrected_finalizer_warning_count",
    "expanded_holdout_proposed_case_count",
    "failure_archive_created",
    "failure_receipt_created",
    "failure_stage",
    "family",
    "frozen_authority",
    "historical_v13_observed_semantic_mismatch_lower_bound",
    "historical_v13_verified_passing_case_count",
    "historical_v13_warning_worker_count",
    "holdout",
    "label",
    "memory",
    "original_case_execution_denominator",
    "original_suite_count",
    "performance",
    "pipeline_exit_code",
    "protocol_sha256",
    "qualified_candidate_count",
    "recovery_root_created",
    "required_locale_path",
    "required_locale_path_verified_before_run",
    "restored_original_targets",
    "schema",
    "source_sha256",
    "status",
    "success_archive_created",
    "success_receipt_created",
    "undefined_behavior",
    "winner_selected",
})
BASE_CALLER_PINS = (
    (
        "--setter-source-sha256",
        "42d9ceea51f8a8cb4ba980580ccbc5b079134bc8330bc65b3c05e2f1ec83395b",
    ),
    (
        "--setter-protocol-sha256",
        "5aad1504d2b834b2d794cff3659462bff89c573cb8f108010fd7f413683fc359",
    ),
    (
        "--setter-contract-sha256",
        "b0b87af889a9147975ccfefc8d3f9cf03f5200a6e6ad90cfaa8679c8c9b5d084",
    ),
    (
        "--v13-source-sha256",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
    ),
    (
        "--v13-protocol-sha256",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
    ),
    (
        "--v13-contract-sha256",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
    ),
    (
        "--receipt-sha256",
        "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca",
    ),
    (
        "--v1-source-sha256",
        "2d2be05fb04d43c453b7e4cd47dc8f55542eeb06b18058c996751b7e8a476e4e",
    ),
    (
        "--v1-protocol-sha256",
        "88dbdad010617a1930bb7e701b8dca02078ab8b6310257bf7f404fc540f3a1bb",
    ),
    (
        "--v1-contract-sha256",
        "2021cca12e9c04ab421dca4fd7cc81e23ffe3b649317eb184dba21e47c6aad4e",
    ),
    (
        "--adapter-sha256",
        "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50",
    ),
    (
        "--corrected-adapter-sha256",
        "c16a6e4c9745eff3a55dcf85eb14c26ec84092d70ddbc40d5e841ab0140d3032",
    ),
    (
        "--guard-source-sha256",
        "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
    ),
    (
        "--guard-protocol-sha256",
        "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
    ),
    (
        "--guard-contract-sha256",
        "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
    ),
    (
        "--v2-guard-source-sha256",
        "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
    ),
    (
        "--v2-guard-protocol-sha256",
        "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
    ),
    (
        "--v2-guard-contract-sha256",
        "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
    ),
    (
        "--producer-source-sha256",
        "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
    ),
    (
        "--producer-protocol-sha256",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
    ),
    (
        "--producer-contract-sha256",
        "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
    ),
    (
        "--build-receipt-sha256",
        "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d",
    ),
    (
        "--root-receipt-sha256",
        "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2",
    ),
)
CALLER_PINS = BASE_CALLER_PINS + (
    ("--v14-source-sha256", PREVIOUS[0][1]),
    ("--v14-protocol-sha256", PREVIOUS[1][1]),
    ("--v14-contract-sha256", PREVIOUS[2][1]),
    ("--v14-failure-receipt-sha256", ACTUAL_V14_FAILURE[1]),
)
SOURCE_MODES = frozenset({
    "--verify-source",
    "--verify-frozen-context",
    "--self-test",
    "--describe",
    "--render-contract",
})
ACTUAL_MODES = frozenset({"--run", "--worker", "--recover"})
MODES = SOURCE_MODES | ACTUAL_MODES


class CampaignError(Exception):
    """A source owner, actual failure, or runtime authority was not genuine."""


def require(condition: object, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "authenticate complete actual source bytes")
    return hashlib.sha256(raw).hexdigest()


def clean() -> None:
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
        "require exact isolated CPython without a loaded regex candidate",
    )


def load_v14() -> types.ModuleType:
    clean()
    path, expected, size, inode = PREVIOUS[0]
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
            "reject an incomplete or substituted exact V14 controller owner",
        )
        chunks = []
        remaining = size
        while remaining:
            part = os.read(descriptor, min(remaining, 262144))
            require(bool(part), "reject a truncated frozen V14 controller")
            chunks.append(part)
            remaining -= len(part)
        require(not os.read(descriptor, 1), "reject an extended V14 controller")
        raw = b"".join(chunks)
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
            "reject V14 controller source changed during authentication",
        )
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_zig_v15_frozen_setter_safe_campaign_v14")
    previous.__file__ = ROOT + "/" + path
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    require(
        previous.SELF == PREVIOUS[0][0]
        and previous.PROTOCOL == PREVIOUS[1][0]
        and previous.CONTRACT == PREVIOUS[2][0]
        and previous.SCHEMA == "rebar-owned-repaired-zig-original-campaign-v14"
        and previous.FAMILY == FAMILY
        and previous.LABEL
        == "phase2-v14-zig-guard-clean-lifetime-setattr-v2-original-p0-v14"
        and previous.CALLER_PINS == BASE_CALLER_PINS
        and len(previous.SUITES) == 13
        and sum(count for _, count in previous.SUITES) == 31237
        and previous.CORRECTED_ADAPTER_SHA256
        == dict(BASE_CALLER_PINS)["--corrected-adapter-sha256"]
        and previous.CORRECTED_ADAPTER_BYTES == 67335,
        "reject the independent frozen V14 controller or its complete authority",
    )
    clean()
    return previous


def validate_pins(args: dict[str, str]) -> None:
    require(type(args) is dict, "require genuine independently supplied V15 pins")
    for option, expected in CALLER_PINS:
        value = args.get(option)
        require(
            type(value) is str
            and len(value) == 64
            and all(char in "0123456789abcdef" for char in value)
            and value == expected,
            "reject missing, crossed, duplicated, or forged V15 pin " + option,
        )


def v14_arguments(args: dict[str, str]) -> dict[str, str]:
    result = {name: args[name] for name, _expected in BASE_CALLER_PINS}
    result.update({
        "--source-sha256": args["--v14-source-sha256"],
        "--protocol-sha256": args["--v14-protocol-sha256"],
        "--contract-sha256": args["--v14-contract-sha256"],
    })
    return result


def failure_authority(previous: types.ModuleType) -> dict[str, str]:
    renames = {
        "--receipt-sha256": "v13_failure_receipt_sha256",
        "--adapter-sha256": "original_adapter_sha256",
        "--corrected-adapter-sha256": "setter_safe_adapter_sha256",
    }
    result = {}
    for option, expected in previous.CALLER_PINS:
        key = renames.get(option, option.removeprefix("--").replace("-", "_"))
        require(key not in result, "reject duplicate compact failure authority")
        result[key] = expected
    require(len(result) == 23, "require all exact historical actual-run pins")
    return result


def normalized_targets(previous_campaign: types.ModuleType) -> dict[str, dict]:
    require(
        type(previous_campaign.ORIGINALS) is dict
        and set(previous_campaign.ORIGINALS) == {"adapter", "bridge", "engine"},
        "require all three original first-party Zig recovery roles",
    )
    result = {}
    for role in ("adapter", "bridge", "engine"):
        owner = previous_campaign.ORIGINALS[role]
        require(
            type(owner) is dict
            and set(owner) == {
                "relative", "sha256", "bytes", "device", "inode",
                "mode", "uid", "nlink",
            }
            and owner["device"] == DEVICE
            and owner["uid"] == os.geteuid()
            and owner["nlink"] == 1
            and owner["mode"] in (0o600, 0o700),
            "reject incomplete, borrowed, or unsafe original Zig role " + role,
        )
        result[role] = {
            **owner,
            "mode": format(owner["mode"], "04o"),
        }
    return result


def validate_failure(document: object, previous: types.ModuleType,
                     inherited: dict) -> None:
    require(
        type(document) is dict
        and set(document) == EXPECTED_FAILURE_KEYS
        and document.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v14-"
           "prepublication-controller-failure-v1"
        and document.get("status") == "FAIL"
        and document.get("candidate_status") == "NOT MEASURED"
        and document.get("family") == FAMILY
        and document.get("label") == previous.LABEL
        and document.get("attempt_count") == 1
        and document.get("pipeline_exit_code") == 4
        and document.get("candidate_process_exit_code") == "NOT MEASURED"
        and document.get("failure_stage")
        == "ACTUAL THREE-ROLE CAMPAIGN OR RECOVERY BEFORE PUBLICATION"
        and document.get("controller_error_type") == "CampaignError"
        and document.get("controller_error_message")
        == "actual three-role campaign/recovery failed: CampaignError: "
           "source-only wall rejected unlisted, native, archive, holdout "
           "or write open"
        and document.get("complete_captured_standard_output") == ""
        and document.get("complete_captured_standard_error")
        == "first-party V3-guarded setter-safe Zig V14 campaign rejected: "
           "CampaignError: actual three-role campaign/recovery failed: "
           "CampaignError: source-only wall rejected unlisted, native, "
           "archive, holdout or write open\n"
        and len(document["complete_captured_standard_error"].encode("utf-8"))
        == 211
        and document.get("source_sha256") == PREVIOUS[0][1]
        and document.get("protocol_sha256") == PREVIOUS[1][1]
        and document.get("contract_sha256") == PREVIOUS[2][1]
        and document.get("frozen_authority") == failure_authority(previous)
        and document.get("required_locale_path")
        == "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
        and document.get("required_locale_path_verified_before_run") is True
        and document.get("original_case_execution_denominator") == 31237
        and document.get("original_suite_count") == 13
        and document.get("actual_completed_suite_count") == "NOT MEASURED"
        and document.get("actual_candidate_worker_count") == "NOT MEASURED"
        and document.get("actual_verified_passing_case_count") == "NOT MEASURED"
        and document.get("actual_semantic_mismatch_count") == "NOT MEASURED"
        and document.get("corrected_finalizer_warning_count") == "NOT MEASURED"
        and document.get("recovery_root_created") is False
        and document.get("success_receipt_created") is False
        and document.get("success_archive_created") is False
        and document.get("failure_receipt_created") is False
        and document.get("failure_archive_created") is False
        and document.get("all_three_original_targets_restored") is True
        and document.get("restored_original_targets")
        == normalized_targets(inherited["repair_state"]["campaign"])
        and document.get("historical_v13_verified_passing_case_count") == 4607
        and document.get("historical_v13_observed_semantic_mismatch_lower_bound")
        == 1700
        and document.get("historical_v13_warning_worker_count") == 13
        and document.get("qualified_candidate_count") == 0
        and document.get("expanded_holdout_proposed_case_count") == 14155776
        and document.get("holdout") == "NOT OPENED"
        and document.get("performance") == "NOT MEASURED"
        and document.get("memory") == "NOT MEASURED"
        and document.get("undefined_behavior") == "NOT MEASURED"
        and document.get("winner_selected") is False,
        "reject the complete actual once-only V14 prepublication failure",
    )


def captured_wall_opener(campaign: types.ModuleType, wall: object) -> bool:
    opener = campaign.REAL_OPEN
    return (
        callable(opener)
        and getattr(opener, "__self__", None) is wall
        and getattr(opener, "__func__", None) is type(wall).opened
    )


def truthful_v13_child_history(state: dict) -> dict:
    """Preserve recorded child counters without inventing native lifetimes."""
    previous = state["previous_document"]["complete_actual_v13_publication"]
    producer = state["inherited"]["producer"]
    original_failure = previous["actual_subinterpreter_failure"]
    require(
        type(previous) is dict
        and type(original_failure) is dict
        and previous.get("actual_child_interpreters_created") == 0
        and previous.get("actual_child_guards_installed") == 0
        and previous.get("actual_child_case_executions") == 0
        and original_failure.get("original_active_phase")
        == "create-genuine-owned-interpreter-A"
        and original_failure.get("original_error_message")
        == "runtime guard blocked missing-or-fabricated-native-child-creation"
        and original_failure.get("actual_interpreters_created") == 0
        and original_failure.get("actual_interpreters_destroyed") == 0
        and original_failure.get("actual_prepared_interpreter_ids") == []
        and original_failure.get("actual_child_guards_installed") == 0
        and original_failure.get("actual_case_interpreter_exec_calls") == 0
        and original_failure.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and original_failure.get("actual_initialization_interpreter_exec_calls") == 0,
        "reject the exact V13 recorded, unreturned child-lifecycle evidence",
    )
    normalized = dict(previous)
    normalized["preserved_v14_history_canonical_sha256"] = digest(
        producer.canonical(previous)
    )
    normalized["child_counter_scope"] = (
        "SUCCESSFULLY RETURNED, RECORDED, OR GUARD-VERIFIED CHILDREN ONLY; "
        "NOT PHYSICAL NATIVE ALLOCATIONS"
    )
    normalized["recorded_successfully_returned_child_interpreters"] = (
        normalized.pop("actual_child_interpreters_created")
    )
    normalized["recorded_installed_child_guards"] = (
        normalized.pop("actual_child_guards_installed")
    )
    normalized["recorded_child_case_executions"] = (
        normalized.pop("actual_child_case_executions")
    )
    normalized["physical_native_interpreters_created"] = "NOT MEASURED"
    normalized["physical_native_interpreters_destroyed"] = "NOT MEASURED"
    normalized["physical_native_interpreter_live_set_restored"] = "NOT MEASURED"

    failure = dict(original_failure)
    failure["recorded_successfully_returned_child_interpreters"] = (
        failure.pop("actual_interpreters_created")
    )
    failure["recorded_destroyed_returned_child_interpreters"] = (
        failure.pop("actual_interpreters_destroyed")
    )
    failure["recorded_prepared_interpreter_ids"] = (
        failure.pop("actual_prepared_interpreter_ids")
    )
    failure["recorded_installed_child_guards"] = (
        failure.pop("actual_child_guards_installed")
    )
    failure["recorded_child_case_executions"] = (
        failure.pop("actual_case_interpreter_exec_calls")
    )
    failure["recorded_child_guard_cleanup_executions"] = (
        failure.pop("actual_guard_cleanup_interpreter_exec_calls")
    )
    failure["recorded_child_initialization_executions"] = (
        failure.pop("actual_initialization_interpreter_exec_calls")
    )
    failure["physical_native_interpreters_created"] = "NOT MEASURED"
    failure["physical_native_interpreters_destroyed"] = "NOT MEASURED"
    failure["physical_native_interpreter_live_set_restored"] = "NOT MEASURED"
    failure["native_create_before_failed_postcondition"] = "NOT MEASURED"
    normalized["actual_subinterpreter_failure"] = failure
    return normalized


def build_state(
    previous: types.ModuleType,
    repair: types.ModuleType,
    args: dict[str, str],
    wall: object,
    *,
    active: bool = False,
) -> dict:
    validate_pins(args)
    for path in (SELF, PROTOCOL, CONTRACT, ACTUAL_V14_FAILURE[0]):
        repair.relative(path)
        wall.allowed.add(ROOT + "/" + path)
    source = repair.dynamic_owner(SELF, args["--source-sha256"])
    protocol = repair.dynamic_owner(PROTOCOL, args["--protocol-sha256"])
    base_args = v14_arguments(args)
    inherited = previous.build_state(repair, base_args, wall, active=active)
    previous_owner = repair.dynamic_owner(PREVIOUS[2][0], PREVIOUS[2][1])
    previous_raw = repair.read_owner(previous_owner)
    previous_document = inherited["producer"].JsonReader(previous_raw).parse()
    require(
        inherited["producer"].canonical(previous_document) == previous_raw,
        "reject the canonical complete frozen V14 campaign contract",
    )
    previous.verify_document(previous_document, inherited)
    failure_owner = repair.dynamic_owner(
        ACTUAL_V14_FAILURE[0], args["--v14-failure-receipt-sha256"],
    )
    require(
        failure_owner == ACTUAL_V14_FAILURE,
        "reject the exact once-only V14 controller-failure owner",
    )
    failure_raw = repair.read_owner(failure_owner)
    failure = inherited["producer"].JsonReader(failure_raw).parse()
    validate_failure(failure, previous, inherited)
    campaign = inherited["repair_state"]["campaign"]
    require(
        captured_wall_opener(campaign, wall)
        and wall.active is True
        and repair.ACTIVE_WALL is wall
        and os.open is not repair.REAL_OPEN
        and campaign.REAL_OPEN is not repair.REAL_OPEN
        and previous_document["first_party_in_memory_setter_safe_adapter"]
        ["physical_status"] == "NOT MATERIALIZED"
        and inherited["corrected"] == inherited["repair_state"]["corrected"]
        and digest(inherited["corrected"])
        == previous.CORRECTED_ADAPTER_SHA256
        and len(inherited["corrected"]) == previous.CORRECTED_ADAPTER_BYTES
        and campaign.GUARD == previous.GUARD
        and campaign.GUARD_V2 == previous.GUARD_V2
        and campaign.PRODUCER == previous.PRODUCER,
        "reject exact measured stale source-wall capture or first-party lineage",
    )
    clean()
    return {
        "previous": previous,
        "repair": repair,
        "inherited": inherited,
        "previous_document": previous_document,
        "failure": failure,
        "source": source,
        "protocol": protocol,
        "corrected": inherited["corrected"],
        "active": active,
    }


def contract_value(state: dict) -> dict:
    repair = state["repair"]
    previous = state["previous"]
    prior = state["previous_document"]
    failure = state["failure"]
    inherited = state["inherited"]
    future_stem = "repaired-zig-original-campaign-v15-" + LABEL
    return {
        "schema": SCHEMA + "-guarded-runtime-authority-source-freeze",
        "version": 15,
        "status": "SOURCE FROZEN; RUNTIME-AUTHORIZED ZIG MATCHING NOT RUN",
        "family": FAMILY,
        "label": LABEL,
        "source": repair.record(state["source"]),
        "protocol": repair.record(state["protocol"]),
        "goal": dict(prior["goal"]),
        "pinned_cpython": dict(prior["pinned_cpython"]),
        "original_oracle": dict(prior["original_oracle"]),
        "immutable_v5_original_producer": dict(
            prior["immutable_v5_original_producer"]
        ),
        "independently_frozen_setter_v2": dict(
            prior["independently_frozen_setter_v2"]
        ),
        "pushed_v13_original_campaign": dict(
            prior["pushed_v13_original_campaign"]
        ),
        "complete_actual_v13_publication": truthful_v13_child_history(state),
        "authenticated_v14_original_campaign": {
            "owners": [repair.record(owner) for owner in PREVIOUS],
            "schema": prior["schema"],
            "version": 14,
            "whole_canonical_contract_authenticated": True,
            "source_modified": False,
            "all_23_independent_caller_pins_preserved": True,
        },
        "actual_v14_prepublication_controller_failure": {
            "owner": repair.record(ACTUAL_V14_FAILURE),
            "complete_exact_failure": dict(failure),
            "attempt_count": 1,
            "failure_stage": failure["failure_stage"],
            "controller_error_type": "CampaignError",
            "candidate_status": "NOT MEASURED",
            "candidate_worker_count": "NOT MEASURED",
            "candidate_pass_count": "NOT MEASURED",
            "corrected_finalizer_warnings": "NOT MEASURED",
            "recovery_root_created": False,
            "candidate_failure_archive_created": False,
            "candidate_failure_receipt_created": False,
            "candidate_success_archive_created": False,
            "candidate_success_receipt_created": False,
            "all_three_original_targets_restored": True,
            "restored_original_targets": dict(
                failure["restored_original_targets"]
            ),
            "history_silently_replaced": False,
            "compressed_archive_opened": False,
            "candidate_failure_is_measured": False,
        },
        "first_party_in_memory_setter_safe_adapter": dict(
            prior["first_party_in_memory_setter_safe_adapter"]
        ),
        "pushed_v3_real_interpreter_guard": dict(
            prior["pushed_v3_real_interpreter_guard"]
        ),
        "root_cause_and_runtime_authority": {
            "measured_v14_failure_receipt_sha256": ACTUAL_V14_FAILURE[1],
            "frozen_v13_owner_captures_os_open_under_v2_source_wall": True,
            "captured_opener_must_be_exact_current_wall_bound_method": True,
            "source_wall_remains_deny_default_in_all_source_modes": True,
            "unrestricted_opener_exposed_inside_source_wall": False,
            "runtime_authority_requires_explicit_actual_action": True,
            "runtime_authority_requires_all_independent_caller_pins": True,
            "runtime_authority_requires_frozen_v15_contract": True,
            "runtime_authority_requires_actual_wall_exit": True,
            "runtime_authority_requires_no_active_repair_wall": True,
            "runtime_authority_requires_restored_os_open": True,
            "runtime_authority_requires_authentic_repair_real_open": True,
            "only_authenticated_v13_module_opener_is_rebound": True,
            "builtins_or_global_source_wall_policy_modified": False,
            "unrestricted_opener_rebound_in_source_gate": False,
            "native_owner_opened_in_source_gate": False,
            "private_root_opened_in_source_gate": False,
            "candidate_run_in_source_gate": False,
        },
        "future_actual_run": {
            "authorization": "SEPARATE EXPLICIT FULLY PINNED --run",
            "root_exclusive_canonical_target_window_required": True,
            "caller_pins": [
                {"option": option, "sha256": expected}
                for option, expected in CALLER_PINS
            ],
            "inherited_v14_caller_pin_count": len(BASE_CALLER_PINS),
            "v14_failure_and_owner_pin_count": 4,
            "candidate_family": FAMILY,
            "candidate_label": LABEL,
            "corrected_adapter_sha256": previous.CORRECTED_ADAPTER_SHA256,
            "corrected_adapter_bytes": previous.CORRECTED_ADAPTER_BYTES,
            "corrected_adapter_materialization": (
                "IN MEMORY; CANONICAL ACTIVATION ONLY DURING AUTHORIZED RUN"
            ),
            "source_wall_must_be_inactive_before_native_owner_access": True,
            "genuine_raw_open_identity_required": True,
            "guard_version": 3,
            "candidate_workers_required": 13,
            "distinct_candidate_workers_required": 13,
            "case_execution_denominator": 31237,
            "recovery_root": RECOVERY,
            "exclusive_recovery_lock": "campaign-v15.lock",
            "role_order": ["engine", "bridge", "adapter"],
            "restoration_order": ["adapter", "bridge", "engine"],
            "canonical_original_targets": dict(
                inherited["repair_state"]["campaign"].ORIGINALS
            ),
            "exact_original_inode_backup_required": True,
            "separate_pinned_recovery_action": "--recover",
            "all_original_roles_restored_before_publication": True,
            "per_suite_timeout_seconds": 120,
            "maximum_serial_timeout_seconds": 1560,
            "continue_after_every_actual_failure": True,
            "native_build_authorized": False,
            "compiler_processes_authorized": False,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "failure_publication_receipt": (
                "oracle/phase2/evidence/" + future_stem
                + "-failures-publication-receipt.json"
            ),
            "failure_result_archive": (
                "oracle/phase2/evidence/" + future_stem + "-failures.json.gz"
            ),
            "success_publication_receipt": (
                "oracle/phase2/evidence/" + future_stem
                + "-success-publication-receipt.json"
            ),
            "success_result_archive": (
                "oracle/phase2/evidence/" + future_stem + "-success.json.gz"
            ),
            "hidden_cases_read": 0,
            "benchmark_files_opened": 0,
            "holdout_files_opened": 0,
        },
        "source_only_worker_transport": dict(
            prior["source_only_worker_transport"]
        ),
        "expanded_sealed_holdout_proposal": dict(
            prior["expanded_sealed_holdout_proposal"]
        ),
        "physical_source_wall": {
            **dict(prior["physical_source_wall"]),
            "v14_stale_bound_opener_reproduced_without_native_access": True,
            "runtime_only_rebinding_required": True,
            "source_modes_expose_raw_native_open": False,
            "source_only_effect_count": len(repair.ZERO_KEYS),
        },
        "source_only_effects": {name: 0 for name in repair.ZERO_KEYS},
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
    producer = state["inherited"]["producer"]
    expected = contract_value(state)
    require(
        type(document) is dict
        and document == expected
        and producer.canonical(document) == producer.canonical(expected),
        "reject truncated, noncanonical, or fabricated V15 frozen contract",
    )


def reject(operation: object, label: str, repair: types.ModuleType) -> int:
    require(callable(operation), "require a genuine V15 hostile control")
    try:
        operation()
    except (
        CampaignError,
        repair.CampaignError,
        OSError,
        ImportError,
        SyntaxError,
        TypeError,
        ValueError,
        AttributeError,
        KeyError,
    ):
        return 1
    raise CampaignError("accepted hostile V15 source-only control: " + label)


def activate_runtime_opener(campaign: types.ModuleType,
                            repair: types.ModuleType,
                            wall: object) -> None:
    require(
        repair.ACTIVE_WALL is None
        and wall.active is False
        and callable(repair.REAL_OPEN)
        and os.open is repair.REAL_OPEN
        and builtins.__import__ is wall.saved.get("import")
        and builtins.open is wall.saved.get("builtin_open")
        and captured_wall_opener(campaign, wall)
        and campaign.REAL_OPEN is not repair.REAL_OPEN,
        "refuse unrestricted Zig owner authority before genuine wall exit",
    )
    campaign.REAL_OPEN = repair.REAL_OPEN
    require(
        campaign.REAL_OPEN is repair.REAL_OPEN
        and campaign.REAL_OPEN is os.open
        and repair.ACTIVE_WALL is None
        and wall.active is False,
        "reject borrowed or partially restored actual native owner authority",
    )


def hostile_controls(state: dict, args: dict, wall: object) -> tuple[int, int]:
    previous = state["previous"]
    repair = state["repair"]
    inherited = state["inherited"]
    producer = inherited["producer"]
    base_args = v14_arguments(args)
    v2_checks, v14_checks = previous.hostile_controls(inherited, base_args, wall)
    require(
        v2_checks == 139 and v14_checks >= 106,
        "reject missing inherited V2/V14 source-only controls",
    )
    checks = 0
    for option, expected in CALLER_PINS:
        forged = dict(args)
        forged[option] = "0" * 64 if expected != "0" * 64 else "f" * 64
        checks += reject(
            lambda value=forged: validate_pins(value),
            "forged inherited or compact-failure caller pin " + option,
            repair,
        )
    campaign = inherited["repair_state"]["campaign"]
    require(
        captured_wall_opener(campaign, wall),
        "reject a fabricated source-wall stale-opener failure reproduction",
    )
    checks += reject(
        lambda: activate_runtime_opener(campaign, repair, wall),
        "unrestricted raw opener while the source wall is active",
        repair,
    )
    for role in ("engine", "bridge", "adapter"):
        owner = campaign.ORIGINALS[role]
        checks += reject(
            lambda item=owner: campaign.REAL_OPEN(
                ROOT + "/" + item["relative"], os.O_RDONLY
            ),
            "stale wall blocked genuine " + role + " without native access",
            repair,
        )
    for name in (
        "re", "_sre", "regex", "re2", "ctypes", "subprocess",
        "gzip", "socket", "threading", "_interpreters",
        "candidates", "candidates.zig_candidate",
        "candidates.rust_candidate", "performance.final_holdout",
    ):
        checks += reject(
            lambda value=name: builtins.__import__(value),
            "forbidden matcher, native loader, process, or holdout " + name,
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
            lambda value=path: os.open(value, os.O_RDONLY),
            "forbidden first-party native, archive, candidate, or private root",
            repair,
        )
    for path in (SELF, PROTOCOL, CONTRACT, ACTUAL_V14_FAILURE[0]):
        full = ROOT + "/" + path
        checks += reject(
            lambda value=full: _io.FileIO(value, "r+"),
            "direct physical _io source or immutable evidence mutation",
            repair,
        )
        checks += reject(
            lambda value=full: sys.audit(
                "open", value, "w", os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            ),
            "forged physical source-owner audit",
            repair,
        )
    for operation, label in (
        (lambda: os.write(1, b"forged"), "direct standard output descriptor"),
        (lambda: os.write(2, b"forged"), "direct standard error descriptor"),
        (
            lambda: sys.audit("subprocess.Popen", "zig", [], None, None),
            "real worker or compiler creation",
        ),
        (lambda: sys.audit("ctypes.dlopen", "foreign"), "foreign engine"),
        (
            lambda: sys.audit("cpython.PyInterpreterState_New", None),
            "real or fabricated subinterpreter",
        ),
        (lambda: repair.relative("../performance"), "escaped holdout path"),
    ):
        checks += reject(operation, label, repair)
    if hasattr(os, "writev"):
        checks += reject(
            lambda: os.writev(1, [b"forged"]),
            "direct vectored standard output descriptor",
            repair,
        )
    failure = state["failure"]
    for field, replacement in (
        ("status", "PASS"),
        ("candidate_status", "PASS"),
        ("attempt_count", 2),
        ("pipeline_exit_code", 0),
        ("candidate_process_exit_code", 0),
        ("controller_error_type", "GuardError"),
        ("controller_error_message", "suppressed"),
        ("complete_captured_standard_output", "fabricated"),
        ("complete_captured_standard_error", "suppressed"),
        ("original_case_execution_denominator", 31238),
        ("original_suite_count", 12),
        ("actual_completed_suite_count", 0),
        ("actual_candidate_worker_count", 0),
        ("actual_verified_passing_case_count", 0),
        ("actual_semantic_mismatch_count", 0),
        ("corrected_finalizer_warning_count", 0),
        ("recovery_root_created", True),
        ("success_receipt_created", True),
        ("success_archive_created", True),
        ("failure_receipt_created", True),
        ("failure_archive_created", True),
        ("all_three_original_targets_restored", False),
        ("historical_v13_verified_passing_case_count", 4608),
        ("historical_v13_observed_semantic_mismatch_lower_bound", 1699),
        ("historical_v13_warning_worker_count", 12),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        forged = repair.cloned(failure, producer)
        forged[field] = replacement
        checks += reject(
            lambda value=forged: validate_failure(value, previous, inherited),
            "fabricated preserved prepublication evidence " + field,
            repair,
        )
    for key in sorted(failure["frozen_authority"]):
        forged = repair.cloned(failure, producer)
        forged["frozen_authority"][key] = "0" * 64
        checks += reject(
            lambda value=forged: validate_failure(value, previous, inherited),
            "substituted actual historical authority " + key,
            repair,
        )
    for role in ("adapter", "bridge", "engine"):
        for field, replacement in (
            ("mode", "0644"), ("inode", 0), ("nlink", 2),
            ("device", DEVICE + 1), ("sha256", "0" * 64),
        ):
            forged = repair.cloned(failure, producer)
            forged["restored_original_targets"][role][field] = replacement
            checks += reject(
                lambda value=forged: validate_failure(value, previous, inherited),
                "forged exact original " + role + " owner " + field,
                repair,
            )
    for field, replacement in (
        ("version", 14),
        ("status", "PASS"),
        ("qualified_candidate_count", 1),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("corrected_warning", "PASS"),
        ("corrected_subinterpreter", "PASS"),
        ("winner_selected", True),
    ):
        forged = repair.cloned(contract_value(state), producer)
        forged[field] = replacement
        checks += reject(
            lambda value=forged: verify_document(value, state),
            "fabricated future V15 candidate result " + field,
            repair,
        )
    for field, replacement in (
        ("recorded_successfully_returned_child_interpreters", 1),
        ("recorded_installed_child_guards", 1),
        ("recorded_child_case_executions", 1),
        ("physical_native_interpreters_created", 0),
        ("physical_native_interpreters_destroyed", 0),
        ("physical_native_interpreter_live_set_restored", True),
    ):
        forged = repair.cloned(contract_value(state), producer)
        forged["complete_actual_v13_publication"][field] = replacement
        checks += reject(
            lambda value=forged: verify_document(value, state),
            "invented V13 recorded or physical child outcome " + field,
            repair,
        )
    for field, replacement in (
        ("recorded_successfully_returned_child_interpreters", 1),
        ("recorded_destroyed_returned_child_interpreters", 1),
        ("recorded_prepared_interpreter_ids", [1]),
        ("recorded_installed_child_guards", 1),
        ("recorded_child_case_executions", 1),
        ("recorded_child_guard_cleanup_executions", 1),
        ("recorded_child_initialization_executions", 1),
        ("physical_native_interpreters_created", 0),
        ("physical_native_interpreters_destroyed", 0),
        ("physical_native_interpreter_live_set_restored", True),
        ("native_create_before_failed_postcondition", False),
    ):
        forged = repair.cloned(contract_value(state), producer)
        forged["complete_actual_v13_publication"][
            "actual_subinterpreter_failure"
        ][field] = replacement
        checks += reject(
            lambda value=forged: verify_document(value, state),
            "invented nested V13 native child outcome " + field,
            repair,
        )
    for mode in (
        "--apply", "--build", "--install", "--benchmark",
        "--generate", "--open-holdout", "--invalid-runtime",
    ):
        checks += reject(
            lambda value=mode: parse([value]),
            "unauthorized actual V15 mode " + mode,
            repair,
        )
    require(
        checks >= 100
        and v2_checks == 139
        and v14_checks >= 106
        and captured_wall_opener(campaign, wall)
        and repair.ACTIVE_WALL is wall
        and wall.active is True,
        "reject incomplete physical, stale-opener, and failure-evidence controls",
    )
    clean()
    return v2_checks + v14_checks, checks


def source_result(state: dict, args: dict, mode: str,
                  inherited_controls: int, new_controls: int) -> dict:
    repair = state["repair"]
    prior = state["previous_document"]
    return {
        "schema": SCHEMA + (
            "-source-self-test" if mode == "--self-test"
            else "-verified-frozen-context"
        ),
        "status": "PASS",
        "mode": mode,
        "family": FAMILY,
        "label": LABEL,
        "source_sha256": args["--source-sha256"],
        "protocol_sha256": args["--protocol-sha256"],
        "contract_sha256": args["--contract-sha256"],
        "v14_source_sha256": PREVIOUS[0][1],
        "v14_protocol_sha256": PREVIOUS[1][1],
        "v14_contract_sha256": PREVIOUS[2][1],
        "v14_prepublication_failure_sha256": ACTUAL_V14_FAILURE[1],
        "v14_prepublication_attempt_count": 1,
        "v14_prepublication_status": "FAIL",
        "v14_candidate_status": "NOT MEASURED",
        "v14_candidate_worker_count": "NOT MEASURED",
        "v14_candidate_matching": "NOT MEASURED",
        "v14_corrected_warning_count": "NOT MEASURED",
        "v14_recovery_root_created": False,
        "v14_candidate_archive_created": False,
        "v14_candidate_receipt_created": False,
        "v14_all_three_original_targets_restored": True,
        "v14_stale_source_wall_opener_reproduced": True,
        "v15_runtime_opener_rebound_in_source_gate": False,
        "v15_source_wall_active_and_deny_default": True,
        "source_only_runtime_raw_opener_exposed": False,
        "preserved_v14_independent_caller_pin_count": 23,
        "v15_total_independent_caller_pin_count": len(CALLER_PINS),
        "actual_v13_receipt_sha256": dict(BASE_CALLER_PINS)[
            "--receipt-sha256"
        ],
        "actual_v13_candidate_status": "FAIL",
        "actual_v13_candidate_workers": 13,
        "actual_v13_verified_passing_case_count": 4607,
        "actual_v13_semantic_mismatch_lower_bound": 1700,
        "actual_v13_semantic_mismatch_count": "NOT MEASURED",
        "actual_v13_warning_worker_count": 13,
        "actual_v13_visible_warning_occurrence_lower_bound": 143,
        "actual_v13_complete_warning_occurrence_count": "NOT MEASURED",
        "v13_recorded_successfully_returned_child_interpreters": 0,
        "v13_recorded_destroyed_returned_child_interpreters": 0,
        "v13_recorded_prepared_interpreter_ids": [],
        "v13_recorded_installed_child_guards": 0,
        "v13_recorded_child_case_executions": 0,
        "v13_recorded_child_initialization_executions": 0,
        "v13_recorded_child_guard_cleanup_executions": 0,
        "v13_physical_native_interpreters_created": "NOT MEASURED",
        "v13_physical_native_interpreters_destroyed": "NOT MEASURED",
        "v13_physical_native_interpreter_live_set_restored": "NOT MEASURED",
        "v13_native_create_before_failed_postcondition": "NOT MEASURED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "named_private_waiver_count": 13,
        "separate_supplemental_reference_case_count": 8244,
        "supplemental_cases_added_to_original_denominator": False,
        "prospective_setter_adapter_sha256": (
            state["previous"].CORRECTED_ADAPTER_SHA256
        ),
        "prospective_setter_adapter_bytes": (
            state["previous"].CORRECTED_ADAPTER_BYTES
        ),
        "prospective_setter_adapter_status": "NOT MATERIALIZED",
        "immutable_guard_version": 3,
        "guard_source_sha256": dict(BASE_CALLER_PINS)[
            "--guard-source-sha256"
        ],
        "immutable_v2_guard_source_sha256": dict(BASE_CALLER_PINS)[
            "--v2-guard-source-sha256"
        ],
        "expected_real_child_interpreters": 11,
        "expected_real_child_case_executions": 394,
        "expected_total_real_child_executions": 416,
        "inherited_v2_and_v14_hostile_controls": inherited_controls,
        "new_v15_hostile_controls": new_controls,
        "source_only_hostile_controls": inherited_controls + new_controls,
        "synthetic_stale_opener_controls": (
            "PASS" if mode == "--self-test" else "NOT RUN"
        ),
        "source_only_effects": {name: 0 for name in repair.ZERO_KEYS},
        "source_only_effect_count": len(repair.ZERO_KEYS),
        "corrected_original_matching": "NOT RUN",
        "corrected_warning": "NOT MEASURED",
        "corrected_subinterpreter": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "expanded_holdout_case_count": 14155776,
        "holdout_case_status": "NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def source_mode(mode: str, args: dict[str, str]) -> bytes:
    previous = load_v14()
    repair = previous.load_repair()
    with repair.SourceWall() as wall:
        original_write = os.write
        original_writev = getattr(os, "writev", None)
        os.write = wall.blocked
        if original_writev is not None:
            os.writev = wall.blocked
        try:
            state = build_state(previous, repair, args, wall)
            producer = state["inherited"]["producer"]
            if mode == "--render-contract":
                return producer.canonical(contract_value(state))
            owner = repair.dynamic_owner(CONTRACT, args["--contract-sha256"])
            raw = repair.read_owner(owner)
            document = producer.JsonReader(raw).parse()
            require(
                producer.canonical(document) == raw,
                "reject noncanonical complete physical V15 contract bytes",
            )
            verify_document(document, state)
            inherited_controls = new_controls = 0
            if mode == "--self-test":
                inherited_controls, new_controls = hostile_controls(
                    state, args, wall
                )
            require(
                repair.ACTIVE_WALL is wall
                and wall.active is True
                and captured_wall_opener(
                    state["inherited"]["repair_state"]["campaign"], wall
                ),
                "reject source-gate raw opener exposure or disabled deny wall",
            )
            return producer.canonical(source_result(
                state, args, mode, inherited_controls, new_controls
            ))
        finally:
            os.write = original_write
            if original_writev is not None:
                os.writev = original_writev


def parse(arguments: list[str]) -> tuple[str, dict[str, str]]:
    require(type(arguments) is list, "reject invalid V15 authority arguments")
    selected = [value for value in arguments if value in MODES]
    require(len(selected) == 1, "select exactly one isolated V15 action")
    mode = selected[0]
    allowed = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        "--family", "--label", "--suite", "--recovery-journal-sha256",
        *(name for name, _ in CALLER_PINS),
    }
    result = {}
    index = 0
    while index < len(arguments):
        option = arguments[index]
        if option in MODES:
            require(option == mode, "reject conflicting actual V15 authorities")
            index += 1
            continue
        require(
            option in allowed
            and option not in result
            and index + 1 < len(arguments),
            "reject unknown, duplicated, omitted, or incomplete V15 authority",
        )
        result[option] = arguments[index + 1]
        index += 2
    required = {
        "--source-sha256", "--protocol-sha256",
        *(name for name, _ in CALLER_PINS),
    }
    if mode != "--render-contract":
        required.add("--contract-sha256")
    if mode in ACTUAL_MODES:
        required |= {"--family", "--label"}
    if mode in {"--worker", "--recover"}:
        required.add("--recovery-journal-sha256")
    if mode == "--worker":
        required.add("--suite")
    require(
        set(result) == required,
        "require all 27 independent V14/V15/runtime failure authority pins",
    )
    validate_pins(result)
    if mode in ACTUAL_MODES:
        require(
            result["--family"] == FAMILY and result["--label"] == LABEL,
            "reject cross-family or substituted actual V15 campaign",
        )
    return mode, result


def recovery_directory(campaign: types.ModuleType, create: bool):
    campaign.require(
        type(create) is bool
        and os.path.dirname(RECOVERY) == "/tmp"
        and RECOVERY.startswith("/tmp/rebar-phase2-repaired-zig-"),
        "reject unsafe first-party V15 recovery directory",
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
        owner = os.fstat(directory)
        campaign.require(
            stat.S_ISDIR(owner.st_mode)
            and stat.S_IMODE(owner.st_mode) == 0o700
            and owner.st_uid == os.geteuid(),
            "reject foreign first-party V15 recovery root",
        )
        lock_flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0)
        lock_flags |= getattr(os, "O_NOFOLLOW", 0)
        if create:
            lock_flags |= os.O_CREAT
        lock = os.open("campaign-v15.lock", lock_flags, 0o600, dir_fd=directory)
        try:
            info = os.fstat(lock)
            campaign.require(
                stat.S_ISREG(info.st_mode)
                and stat.S_IMODE(info.st_mode) == 0o600
                and info.st_uid == os.geteuid()
                and info.st_nlink == 1,
                "reject foreign first-party V15 recovery lock",
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


def names(campaign: types.ModuleType, role: str) -> tuple[str, str]:
    campaign.require(role in campaign.ROLES, "reject crossed V15 staged role")
    stem = ".rebar-zig-setter-safe-v15-" + role
    return stem + ".stage", stem + ".original"


def prepare_active_state(args: dict[str, str]) -> tuple[types.ModuleType, dict]:
    previous = load_v14()
    repair = previous.load_repair()
    with repair.SourceWall() as wall:
        state = build_state(previous, repair, args, wall, active=True)
        owner = repair.dynamic_owner(CONTRACT, args["--contract-sha256"])
        raw = repair.read_owner(owner)
        producer = state["inherited"]["producer"]
        document = producer.JsonReader(raw).parse()
        require(
            producer.canonical(document) == raw,
            "reject the complete genuine actual-mode V15 contract",
        )
        verify_document(document, state)
        campaign = state["inherited"]["repair_state"]["campaign"]
        require(
            repair.ACTIVE_WALL is wall
            and wall.active is True
            and captured_wall_opener(campaign, wall),
            "reject invented original V14 captured source-only opener",
        )

    # Runtime authority starts only here. The corrected authentic V13 module
    # was loaded under the frozen source wall, and therefore captured that
    # wall's bound os.open. Rebind only this authenticated module, and only
    # after the complete frozen contract, failure record, and wall restoration.
    activate_runtime_opener(campaign, repair, wall)

    runtime = dict(state["inherited"]["repair_state"]["campaign_state"])
    runtime["proof"] = dict(state["inherited"]["repair_state"]["proof"])
    raw_read_owner = campaign.read_owner
    corrected_owner = (
        repair.PROSPECTIVE_VARIANT,
        previous.CORRECTED_ADAPTER_SHA256,
        previous.CORRECTED_ADAPTER_BYTES,
        previous.ORIGINAL_ADAPTER[3],
    )

    def in_memory_read(owner):
        if owner == corrected_owner:
            return state["corrected"]
        return raw_read_owner(owner)

    def active_verify(source_sha, protocol_sha, contract_sha, *, active=False):
        campaign.require(
            source_sha == args["--source-sha256"]
            and protocol_sha == args["--protocol-sha256"]
            and contract_sha == args["--contract-sha256"]
            and campaign.REAL_OPEN is repair.REAL_OPEN
            and campaign.REAL_OPEN is os.open
            and repair.ACTIVE_WALL is None
            and wall.active is False,
            "reject unauthenticated actual V15 source or stale runtime opener",
        )
        return runtime

    def publication_stem(suffix, *, observed=None):
        campaign.require(
            suffix in ("success", "failures"),
            "reject invented actual V15 publication outcome",
        )
        expected = "repaired-zig-original-campaign-v15-" + LABEL + "-" + suffix
        if observed is not None:
            campaign.require(
                observed == expected,
                "reject crossed actual V15 campaign evidence path",
            )
        return expected

    campaign.SELF = SELF
    campaign.PROTOCOL = PROTOCOL
    campaign.CONTRACT = CONTRACT
    campaign.SCHEMA = SCHEMA
    campaign.LABEL = LABEL
    campaign.RECOVERY = RECOVERY
    campaign.LIFETIME_ADAPTER = corrected_owner
    campaign.REPAIRED_DEALLOCATOR = repair.NEW_DEALLOCATOR
    campaign.ACTUAL_CALLER_PINS = CALLER_PINS
    campaign.read_owner = in_memory_read
    campaign.verify = active_verify
    campaign.recovery_directory = lambda create: recovery_directory(
        campaign, create
    )
    campaign.names = lambda role: names(campaign, role)
    campaign.publication_stem = publication_stem
    require(
        campaign.SUITES == previous.SUITES
        and campaign.GUARD == previous.GUARD
        and campaign.GUARD_V2 == previous.GUARD_V2
        and campaign.PRODUCER == previous.PRODUCER
        and campaign.REAL_OPEN is repair.REAL_OPEN
        and campaign.REAL_OPEN is os.open
        and campaign.LIFETIME_ADAPTER[1]
        == previous.CORRECTED_ADAPTER_SHA256
        and campaign.LIFETIME_ADAPTER[2]
        == previous.CORRECTED_ADAPTER_BYTES
        and campaign.SCHEMA == SCHEMA
        and campaign.LABEL == LABEL
        and campaign.RECOVERY == RECOVERY
        and repair.ACTIVE_WALL is None,
        "reject first-party engine, restored opener, guard, or exact recovery",
    )
    return campaign, state


def actual_mode(mode: str, args: dict[str, str]) -> bytes:
    campaign, state = prepare_active_state(args)
    if mode == "--worker":
        return campaign.worker_canonical(campaign.worker(args))
    if mode == "--recover":
        return state["inherited"]["producer"].canonical(campaign.recover(args))
    require(mode == "--run", "reject a missing actual V15 campaign action")
    return state["inherited"]["producer"].canonical(campaign.campaign(args))


def main() -> int:
    mode, args = parse(list(sys.argv[1:]))
    if mode in SOURCE_MODES:
        output = source_mode(mode, args)
    else:
        output = actual_mode(mode, args)
    require(type(output) is bytes and bool(output), "reject incomplete V15 output")
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
            "first-party runtime-authorized setter-safe Zig V15 campaign "
            "rejected: " + type(error).__qualname__ + ": " + str(error) + "\n"
        )
        raise SystemExit(1) from error
