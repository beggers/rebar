#!/usr/bin/env python3
"""Verify phase-one readiness without declaring a replacement compatible."""

from __future__ import annotations

import ast
import builtins
import hashlib
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-cpython-re-p0-completeness-v4"
SELF = "tools/verify_owned_p0_completeness_v4.py"
PROTOCOL = "oracle/phase1/P0-COMPLETENESS-V4.md"
CONTRACT = "oracle/phase1/p0-completeness-v4.json"
P0_V2 = (
    "oracle/phase1/p0-completeness-v2.json",
    "fcd7abac619a6a4733e090cf49acbb958f8162eeb7dc6909a9d14501809e8237",
    28440, 2064, 525073,
)
FUZZ_SOURCE = (
    "tools/run_owned_differential_fuzz_reference_v3.py",
    "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
    43757, 2064, 432216,
)
FUZZ_PROTOCOL = (
    "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
    "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
    3929, 2064, 525081,
)
FUZZ_CONTRACT = (
    "oracle/phase1/p0-differential-fuzz-reference-v3.json",
    "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
    5288, 2064, 525082,
)
EVIDENCE_DIRECTORY = (
    "oracle/phase1/evidence/"
    "differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/"
)
REFERENCE_ONE = (
    EVIDENCE_DIRECTORY + "reference-1.json",
    "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
    270, 2064, 524693,
)
REFERENCE_TWO = (
    EVIDENCE_DIRECTORY + "reference-2.json",
    "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
    270, 2064, 524692,
)
ACTUAL_REFERENCE = (
    EVIDENCE_DIRECTORY + "two-independent-reference-result.json",
    "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
    3658, 2064, 524707,
)
V63 = {
    "source": (
        "tools/render_candidate_current_overview_v63.py",
        "4f33bd240aa70ca8a47de1c56ec8eb405da4f23f587cfab362f4a7ebbed648c4",
        67015, 2064, 428905,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v63.inputs.json",
        "fafba28ae2628e1f1b9747a865747a0ad35ba943b746c95893b0fd3381b91581",
        967168, 2064, 428906,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v63.json",
        "e78207ec0e2af2470287d3afbc12bee0270d29fa7ed7483a1f62eb72a0b4016c",
        2660089, 2064, 428907,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v63.svg",
        "9860367eb080240efd36e5c241fe0f7d6305d351d87152e2007b92beff496d7e",
        14765, 2064, 428916,
    ),
}
BLOCKERS = (
    "ORIGINAL_31237_CANDIDATE_GATE_NOT_PASSED",
    "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
    "PUBLIC_IMPORT_FAIL",
    "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
    "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
)


class ReadinessError(Exception):
    """Reject incomplete Python evidence or an unsafe phase transition."""


def need(value: object, message: str) -> None:
    if not value:
        raise ReadinessError(message)


def source_module() -> dict[str, object]:
    path, digest, size, device, inode = FUZZ_SOURCE
    descriptor = os.open(
        os.path.join(ROOT, path),
        os.O_RDONLY | os.O_CLOEXEC | getattr(os, "O_NOFOLLOW", 0),
    )
    parts: list[bytes] = []
    try:
        identity = os.fstat(descriptor)
        need(stat.S_ISREG(identity.st_mode) and identity.st_nlink == 1
             and stat.S_IMODE(identity.st_mode) == 0o600
             and (identity.st_size, identity.st_dev, identity.st_ino)
             == (size, device, inode), "reject changed bounded source verifier")
        while True:
            part = os.read(descriptor, 65536)
            if not part:
                break
            parts.append(part)
    finally:
        os.close(descriptor)
    raw = b"".join(parts)
    need(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest,
         "reject modified exact differential verifier source")
    namespace: dict[str, object] = {
        "__name__": "rebar_owned_frozen_differential_reference_v3",
        "__file__": os.path.join(ROOT, path),
        "__builtins__": builtins.__dict__,
    }
    exec(compile(raw, os.path.join(ROOT, path), "exec"), namespace)
    namespace["source_wall"]()
    return namespace


def fixed(module: dict[str, object], values: tuple[str, str, int, int, int],
          *, capture: bool = True) -> tuple[bytes, dict[str, object]]:
    return module["owner"](*values, capture=capture)


def object_file(module: dict[str, object], values: tuple[str, str, int, int, int]
                ) -> tuple[dict[str, object], dict[str, object]]:
    raw, identity = fixed(module, values)
    document = module["decode"](raw)
    need(isinstance(document, dict), "require a complete strict JSON source owner")
    return document, identity


def clone(value: object) -> object:
    if isinstance(value, dict):
        return {key: clone(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clone(item) for item in value]
    if isinstance(value, tuple):
        return tuple(clone(item) for item in value)
    return value


def readiness_gate() -> dict[str, object]:
    return {
        "status": "PASS",
        "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
        "source_crosswalk_status": "PASS",
        "candidate_evaluation_authorized": True,
        "native_build_authorized": True,
        "performance_oracle_authorized": False,
        "final_holdout_authorized": False,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }


def qualification_gate() -> dict[str, object]:
    return {
        "status": "BLOCKED",
        "status_scope": "PHASE 2 CANDIDATE QUALIFICATION ONLY",
        "candidate_family_count": 6,
        "qualified_candidate_count": 0,
        "blockers": list(BLOCKERS),
        "candidate_fuzz_status": "NOT RUN",
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def effects() -> dict[str, object]:
    return {
        "actual_reference_workers_started": 0,
        "actual_candidate_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "actual_native_activations": 0,
        "compressed_archives_opened": 0,
        "hidden_holdout_opened": False,
        "clock_samples": 0,
        "network_operations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_gate(gate: object, candidate: object) -> None:
    need(isinstance(gate, dict) and gate == readiness_gate(),
         "reject incomplete or prematurely opened phase-one readiness gate")
    need(isinstance(candidate, dict) and candidate == qualification_gate(),
         "reject invented candidate qualification or missing real blocker")
    need(gate["status"] == "PASS"
         and gate["candidate_evaluation_authorized"] is True
         and gate["native_build_authorized"] is True
         and gate["performance_oracle_authorized"] is False
         and gate["final_holdout_authorized"] is False
         and candidate["status"] == "BLOCKED"
         and len(candidate["blockers"]) == 7
         and len(set(candidate["blockers"])) == 7
         and candidate["qualified_candidate_count"] == 0,
         "keep passing reference readiness separate from candidate qualification")


def make_contract(source_pin: str, protocol_pin: str) -> dict[str, object]:
    module = source_module()
    module["source_wall"]()
    runtime = module["runtime_owner"]()
    self_identity = os.stat(os.path.join(ROOT, SELF), follow_symlinks=False)
    _, own_source = module["owner"](
        SELF, module["exact_hash"](source_pin, "V4 readiness source"),
        self_identity.st_size, self_identity.st_dev, self_identity.st_ino,
    )
    protocol_identity = os.stat(os.path.join(ROOT, PROTOCOL), follow_symlinks=False)
    _, own_protocol = module["owner"](
        PROTOCOL, module["exact_hash"](protocol_pin, "V4 readiness protocol"),
        protocol_identity.st_size, protocol_identity.st_dev, protocol_identity.st_ino,
    )
    previous, previous_owner = object_file(module, P0_V2)
    need(previous.get("schema") == "rebar-cpython-re-p0-completeness-v2"
         and previous.get("status") == "BLOCKED"
         and previous.get("source_crosswalk_status") == "PASS"
         and previous.get("phase1_canonical_candidate_context_crosswalk") == "PASS",
         "preserve the complete historical BLOCKED phase-one crosswalk")
    old_gate = previous.get("phase_gate")
    need(isinstance(old_gate, dict) and old_gate.get("status") == "BLOCKED"
         and old_gate.get("candidate_evaluation_authorized") is False
         and old_gate.get("native_build_authorized") is False
         and old_gate.get("performance_oracle_authorized") is False
         and old_gate.get("final_holdout_authorized") is False
         and len(old_gate.get("blockers", [])) == 7,
         "reject altered historical blocked phase-one gate")
    original = previous.get("original_oracle")
    need(isinstance(original, dict)
         and original.get("case_execution_denominator") == 31237
         and original.get("suite_count") == 13
         and original.get("named_private_waiver_count") == 13
         and original.get("total_named_obligation_count") == 73
         and original.get("crosswalk_count") == 34
         and isinstance(original.get("suites"), list)
         and len(original["suites"]) == 13
         and sum(case["case_execution_count"] for case in original["suites"])
         == 31237
         and len(original.get("named_private_waivers", [])) == 13
         and original.get("legacy_abstract_fuzz_waivers_inherited") == 0,
         "reject a changed original CPython case, obligation, suite or waiver")
    corrected = previous.get("corrected_candidate_context_public_type_reference")
    need(isinstance(corrected, dict) and corrected.get("status") == "PASS"
         and corrected.get("reference_status") == "PASS"
         and corrected.get("case_count") == 6912
         and corrected.get("actual_reference_worker_count") == 2
         and corrected.get("reference_pids") == [81, 82]
         and corrected.get("records_sha256")
         == "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
         and corrected.get("cache_records_sha256")
         == "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad",
         "reject the complete actual corrected 6,912-case reference")
    supplement = previous.get("supplemental_differential_property_fuzz")
    need(isinstance(supplement, dict) and supplement.get("case_count") == 8244
         and supplement.get("two_independent_reference_process_status") == "NOT RUN"
         and supplement.get("candidate_status") == "NOT RUN"
         and supplement.get("case_denominator_included_in_original_31237") is False,
         "preserve the historical phase-two-worker status without overwriting it")
    inherited = module["owner_records"](previous)
    unique_owners = {item["path"]: item for item in inherited}
    need(len(unique_owners) == 61,
         "require the complete streaming-verified phase-one source-owner closure")
    actual, aggregate_owner = object_file(module, ACTUAL_REFERENCE)
    first, first_owner = object_file(module, REFERENCE_ONE)
    second, second_owner = object_file(module, REFERENCE_TWO)
    source_raw, fuzz_source_owner = fixed(module, FUZZ_SOURCE)
    need(hashlib.sha256(source_raw).hexdigest() == FUZZ_SOURCE[1],
         "reject the frozen actual reference controller")
    _, fuzz_protocol_owner = fixed(module, FUZZ_PROTOCOL)
    fuzz_contract, fuzz_contract_owner = object_file(module, FUZZ_CONTRACT)
    need(fuzz_contract.get("status") == "BLOCKED"
         and fuzz_contract.get("source_only_effects", {}).get(
             "actual_reference_worker_count") == 0,
         "preserve the unrun source-freeze contract as historical evidence")
    need(first == second
         and first.get("schema") == "rebar-correctness-result-v2"
         and first.get("module") == "re"
         and first.get("cases") == 8244
         and first.get("passed") == 8244
         and first.get("failed") == 0
         and first.get("failures") == []
         and first.get("obligations") == 45
         and first.get("mapped_obligations") == 45
         and first_owner["inode"] != second_owner["inode"]
         and first_owner["sha256"] == second_owner["sha256"],
         "require both complete genuinely distinct real Python result owners")
    workers = actual.get("workers")
    pids = actual.get("actual_reference_worker_process_ids")
    need(actual.get("schema") ==
         "rebar-owned-differential-fuzz-reference-v3-actual-reference"
         and actual.get("status") == "PASS"
         and actual.get("actual_reference_worker_count") == 2
         and isinstance(pids, list) and len(pids) == 2
         and all(isinstance(pid, int) and pid > 0 for pid in pids)
         and len(set(pids)) == 2
         and isinstance(workers, list) and len(workers) == 2,
         "require two actually observed, independently recorded worker PIDs")
    for index, (worker, expected, role) in enumerate((
        (workers[0], first_owner, "independent-reference-a"),
        (workers[1], second_owner, "independent-reference-b"),
    )):
        need(isinstance(worker, dict)
             and worker.get("role") == role
             and worker.get("pid") == pids[index]
             and worker.get("exit_code") == 0
             and worker.get("result_schema") == "rebar-correctness-result-v2"
             and worker.get("module") == "re"
             and worker.get("case_count") == 8244
             and worker.get("passed") == 8244
             and worker.get("failed") == 0
             and worker.get("failures") == [],
             "reject an incomplete, unobserved or failing genuine worker")
        observed_owner = worker.get("result")
        need(isinstance(observed_owner, dict)
             and observed_owner.get("path")
             == os.path.join(ROOT, expected["path"])
             and observed_owner.get("sha256") == expected["sha256"]
             and observed_owner.get("bytes") == expected["bytes"]
             and observed_owner.get("device") == expected["device"]
             and observed_owner.get("inode") == expected["inode"],
             "reject crossed, copied, or fabricated genuine worker owner")
        stdout = worker.get("stdout")
        need(isinstance(stdout, dict) and isinstance(stdout.get("text"), str),
             "preserve the actual original Python worker stdout")
        summary = module["decode"](stdout["text"].encode("utf-8"))
        need(isinstance(summary, dict) and summary.get("schema")
             == "rebar-correctness-result-v2"
             and summary.get("passed") == 8244
             and summary.get("failed") == 0,
             "reject an invented original Python result stream")
    corpus = module["corpus_records"](module["CORPUS"], 8244, full=True)
    parent = module["corpus_records"](module["V1_CORPUS"], 2048, full=False)
    need(actual.get("corpus_sha256") == corpus["sha256"]
         and first.get("expected_sha256") == corpus["sha256"]
         and actual.get("record_kind_counts") == corpus["record_kind_counts"]
         and actual.get("frozen_seeds") == module["FIXED_SEEDS"]
         and actual.get("mapped_obligation_count") == 45
         and actual.get("original_case_execution_denominator") == 31237
         and actual.get("supplemental_case_count") == 8244
         and actual.get("case_denominator_included_in_original_31237") is False
         and actual.get("actual_candidate_worker_count") == 0
         and actual.get("candidate_status") == "NOT RUN"
         and actual.get("qualified_candidate_count") == 0
         and actual.get("native_build_status") == "NOT RUN"
         and actual.get("holdout") == "NOT OPENED"
         and actual.get("performance") == "NOT MEASURED",
         "reject incomplete supplemental execution or invented candidate work")
    overview: dict[str, dict[str, object]] = {}
    for role, values in V63.items():
        _, overview[role] = fixed(module, values, capture=False)
    overview_raw, _ = fixed(module, V63["summary"])
    graph = module["decode"](overview_raw)
    need(isinstance(graph, dict) and graph.get("version") == 63
         and graph.get("status") == "PASS"
         and graph.get("actual_current_graph_predecessor_version") == 62
         and graph.get("phase1_completeness_status") == "BLOCKED"
         and graph.get("phase1_differential_fuzz_reference_v3_execution_status")
         == "PASS"
         and graph.get("phase1_differential_fuzz_reference_v3_worker_count") == 2
         and graph.get("phase1_differential_fuzz_reference_v3_worker_process_ids")
         == pids
         and graph.get("actual_rust_v10_semantic_mismatch_count") == 1440
         and graph.get("qualified_candidate_count") == 0
         and graph.get("authenticated_evidence_owner_lower_bound") == 213
         and graph.get("authenticated_history_reference_lower_bound") == 218
         and graph.get("performance") == "NOT MEASURED"
         and graph.get("final_holdout_opened") is False,
         "reject the complete actual reference-result graph history")
    gate = readiness_gate()
    candidate = qualification_gate()
    validate_gate(gate, candidate)
    module["source_wall"]()
    return {
        "schema": SCHEMA,
        "version": 4,
        "phase": "CORRECTNESS ORACLE",
        "status": "PASS",
        "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
        "source": own_source,
        "protocol": own_protocol,
        "pinned_cpython": runtime,
        "previous_phase1_completeness": previous_owner,
        "previous_phase1_completeness_status": "BLOCKED",
        "source_crosswalk_status": "PASS",
        "phase1_canonical_candidate_context_crosswalk": "PASS",
        "original_oracle": clone(original),
        "corrected_candidate_context_public_type_reference": clone(corrected),
        "historical_supplemental_differential_property_fuzz": clone(supplement),
        "supplemental_public_contracts": clone(
            previous["supplemental_public_contracts"]),
        "authenticated_inherited_source_owner_count": len(unique_owners),
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "original_named_private_waiver_count": 13,
        "original_obligation_count": 73,
        "original_crosswalk_count": 34,
        "actual_supplemental_two_reference": {
            "status": "PASS",
            "controller_source": fuzz_source_owner,
            "controller_protocol": fuzz_protocol_owner,
            "historical_source_contract": fuzz_contract_owner,
            "aggregate": aggregate_owner,
            "reference_one": first_owner,
            "reference_two": second_owner,
            "actual_reference_worker_count": 2,
            "actual_reference_worker_process_ids": clone(pids),
            "case_count_per_worker": [8244, 8244],
            "failed_per_worker": [0, 0],
            "worker_exit_codes": [0, 0],
            "total_actual_reference_case_executions": 16488,
            "case_denominator_included_in_original_31237": False,
            "record_kind_counts": clone(corpus["record_kind_counts"]),
            "record_mapped_obligation_ids": clone(
                corpus["record_mapped_obligation_ids"]),
            "frozen_seeds": clone(module["FIXED_SEEDS"]),
            "supplemental_corpus": corpus,
            "v1_parent_corpus": parent,
            "worker_result_provenance": clone(workers),
        },
        "previous_overview": overview,
        "previous_overview_version": 63,
        "historical_phase_transition": {
            "previous_version": 2,
            "previous_phase_gate_status": "BLOCKED",
            "resolved_reference_blocker":
                "SUPPLEMENTAL_8244_TWO_INDEPENDENT_REFERENCE_PROCESSES_NOT_RUN",
            "resolution":
                "TWO AUTHENTICATED COMPLETE REFERENCE WORKERS PASSED",
            "historical_single_context_worker_provenance": "NOT CAPTURED",
            "original_case_execution_denominator_unchanged": True,
        },
        "phase_gate": gate,
        "candidate_qualification_gate": candidate,
        "source_only_effects": effects(),
        "first_party_candidate_family_count": 6,
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def arguments(argv: list[str]) -> dict[str, str]:
    choices = ("--self-test", "--verify-frozen-context", "--render-contract")
    modes = [item for item in choices if item in argv]
    need(len(modes) == 1, "choose exactly one safe phase-readiness source mode")
    result = {"mode": modes[0]}
    offset = 0
    while offset < len(argv):
        item = argv[offset]
        if item in choices:
            offset += 1
            continue
        need(item in ("--source-sha256", "--protocol-sha256",
                      "--contract-sha256"), "reject unknown source-readiness option")
        need(offset + 1 < len(argv) and item not in result,
             "reject missing or repeated source-readiness option")
        result[item] = argv[offset + 1]
        offset += 2
    need("--source-sha256" in result and "--protocol-sha256" in result,
         "require independently pinned readiness source and protocol")
    if result["mode"] == "--render-contract":
        need("--contract-sha256" not in result,
             "render cannot assert an uncreated readiness contract")
    else:
        need("--contract-sha256" in result,
             "require independently pinned canonical readiness contract")
    return result


def verified_contract(options: dict[str, str]) -> tuple[dict[str, object],
                                                        dict[str, object]]:
    module = source_module()
    result = make_contract(options["--source-sha256"],
                           options["--protocol-sha256"])
    identity = os.stat(os.path.join(ROOT, CONTRACT), follow_symlinks=False)
    raw, contract_owner = module["owner"](
        CONTRACT,
        module["exact_hash"](options["--contract-sha256"], "V4 contract"),
        identity.st_size, identity.st_dev, identity.st_ino,
    )
    need(raw == module["canonical"](result) + b"\n",
         "reject fabricated or incomplete canonical phase readiness")
    module["source_wall"]()
    return result, contract_owner


def safe_self_test(document: dict[str, object]) -> dict[str, object]:
    rejected = 0
    for section, factory in (("phase_gate", readiness_gate),
                             ("candidate_qualification_gate", qualification_gate)):
        template = factory()
        for key, value in list(template.items()):
            hostile = clone(template)
            if isinstance(value, bool):
                hostile[key] = not value
            elif isinstance(value, int):
                hostile[key] = value + 1
            elif isinstance(value, str):
                hostile[key] = "PASS" if value != "PASS" else "BLOCKED"
            elif isinstance(value, list):
                hostile[key] = value[:-1]
            else:
                hostile[key] = None
            try:
                if section == "phase_gate":
                    validate_gate(hostile, qualification_gate())
                else:
                    validate_gate(readiness_gate(), hostile)
            except ReadinessError:
                rejected += 1
            else:
                raise ReadinessError("accepted hostile readiness gate: " + key)
    for index in range(len(BLOCKERS)):
        hostile = qualification_gate()
        hostile["blockers"] = list(BLOCKERS[:index] + BLOCKERS[index + 1:])
        try:
            validate_gate(readiness_gate(), hostile)
        except ReadinessError:
            rejected += 1
        else:
            raise ReadinessError("accepted missing real candidate blocker")
    actual = document.get("actual_supplemental_two_reference")
    need(isinstance(actual, dict) and actual.get("status") == "PASS"
         and actual.get("actual_reference_worker_count") == 2,
         "reject invented actual passing Python-reference evidence")
    validate_gate(document["phase_gate"], document["candidate_qualification_gate"])
    need(document["source_only_effects"] == effects(),
         "reject matching, timing or hidden holdout during source checks")
    return {"schema": SCHEMA + "-source-self-test", "status": "PASS",
            "hostile_controls_rejected": rejected,
            "phase1_readiness_status": "PASS",
            "candidate_qualification_status": "BLOCKED",
            "candidate_evaluation_authorized": True,
            "native_build_authorized": True,
            "performance_oracle_authorized": False,
            "final_holdout_authorized": False,
            "historical_p0_v2_status": "BLOCKED",
            "actual_supplemental_reference_status": "PASS",
            "observed_supplemental_reference_worker_count": 2,
            "new_reference_workers_started": 0,
            "new_candidate_workers_started": 0,
            "qualified_candidate_count": 0,
            "original_case_execution_denominator": 31237,
            "supplemental_case_count": 8244,
            "holdout": "NOT OPENED", "performance": "NOT MEASURED"}


def main(argv: list[str]) -> int:
    options = arguments(argv)
    if options["mode"] == "--render-contract":
        module = source_module()
        document = make_contract(options["--source-sha256"],
                                 options["--protocol-sha256"])
        output = module["publish"](os.path.join(ROOT, "oracle/phase1"),
                                    "p0-completeness-v4.json", document)
        module["source_wall"]()
        result = {"schema": SCHEMA + "-canonical-contract-render",
                  "status": "PASS", "phase1_readiness_status": "PASS",
                  "candidate_qualification_status": "BLOCKED",
                  "new_reference_workers_started": 0,
                  "new_candidate_workers_started": 0,
                  "contract": output}
    else:
        document, contract_owner = verified_contract(options)
        if options["mode"] == "--self-test":
            result = safe_self_test(document)
        else:
            validate_gate(document["phase_gate"],
                          document["candidate_qualification_gate"])
            result = {
                "schema": SCHEMA + "-frozen-context",
                "status": "PASS",
                "phase1_readiness_status": "PASS",
                "candidate_qualification_status": "BLOCKED",
                "candidate_qualification_blockers": list(BLOCKERS),
                "candidate_evaluation_authorized": True,
                "native_build_authorized": True,
                "performance_oracle_authorized": False,
                "final_holdout_authorized": False,
                "historical_p0_v2_status": "BLOCKED",
                "original_case_execution_denominator": 31237,
                "original_suite_count": 13,
                "original_named_private_waiver_count": 13,
                "original_obligation_count": 73,
                "original_crosswalk_count": 34,
                "supplemental_case_count": 8244,
                "actual_supplemental_reference_status": "PASS",
                "observed_supplemental_reference_worker_count": 2,
                "observed_supplemental_reference_worker_pids": [81, 82],
                "supplemental_case_kind_count": 19,
                "supplemental_mapped_obligation_count": 45,
                "authenticated_inherited_source_owner_count": 61,
                "source_only_effects": effects(),
                "contract_sha256": contract_owner["sha256"],
                "qualified_candidate_count": 0,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            }
    module = source_module()
    module["source_wall"]()
    os.write(1, module["canonical"](result) + b"\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        if isinstance(error, ReadinessError) or type(error).__name__ == "ReferenceError":
            message = {"schema": SCHEMA + "-error", "status": "FAIL",
                       "error": str(error)}
            try:
                module = source_module()
                os.write(2, module["canonical"](message) + b"\n")
            except BaseException:
                os.write(2, b"phase-one readiness rejected\n")
            raise SystemExit(2)
        raise
