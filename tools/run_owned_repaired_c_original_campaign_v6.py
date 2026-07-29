#!/usr/bin/env python3
"""Run the receipt-bound, first-party C18 matcher against frozen originals.

Source modes are matcher-free and physically read-only.  Real C18 root access,
native activation, original observations and evidence publication exist only
behind a separately pinned explicit actual operation.
"""

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
SOURCE = "tools/run_owned_repaired_c_original_campaign_v6.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V6.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v6.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v6"
LABEL = "phase2-v18-c-subject-buffer-root-provenance-original-p0-v6"
FAMILY = "c"
DEVICE = 2064
ROOT_DEVICE = 2049
MAX_OWNER = 8 * 1024 * 1024
MAX_WORKER_STDOUT = 64 * 1024 * 1024
MAX_WORKER_STDERR = 4 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 120
ORIGINAL_CASE_COUNT = 31237
SEPARATE_REFERENCE_CASE_COUNT = 8244
EXPANDED_PROPOSED_CASE_COUNT = 14155776
RECOVERY_ROOT = "/tmp/rebar-phase2-repaired-c-original-campaign-v6"
LOCALE_ROOT = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
NATIVE_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
NATIVE_RELATIVE = "candidates/" + NATIVE_NAME
BACKUP_NAME = ".rebar-c-original-campaign-v6-original-native"
STAGE_NAME = ".rebar-c-original-campaign-v6-staged-native"
JOURNAL_NAME = "original-native-recovery-journal-v6.json"
NATIVE_SHA256 = "f3794f963819a9af3798c1d97f32edcbc2a117f9ed20c56ec554a605de82eeae"
NATIVE_BYTES = 163504

OLD = (
    ("tools/run_owned_repaired_c_original_campaign_v5.py", "a98e080fa3c9b556122316966723ea7f69589ffddd6293e1ebe199c0dde07810", 50004, 429083),
    ("oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V5.md", "bec733d3181da1198fc44c6b22cb45d7df8a6721ef073e09cde7650c47453237", 6313, 524779),
    ("oracle/phase2/repaired-c-original-campaign-v5.json", "95de401d8a63a6a7272d86ef062c775100ce7305d74fec85be1ed7b0236381f2", 8950, 524786),
)
BUILD = (
    ("tools/reproduce_owned_c_subject_buffer_source_build_v18.py", "bf50ac15a7fdc7633e5804da066a77ee1342540228245cd33a5d977bfdfdc339", 122194, 430336),
    ("oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V18.md", "97ab6a9881e2e2cf7c779660459adb00f7bb9e6db5e5b63da5c75d00f250c5aa", 10389, 524789),
    ("oracle/phase2/c-subject-buffer-source-build-v18.json", "aa68e0da13d666ea02565fe5aed347d5a34150e768df70fc5acc4a1e594b1a6a", 17921, 524797),
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-c-subject-buffer-root-provenance-publication-receipt.json",
    "4070feca7129fdcf3dc9762fae853649c68c722940af6157ecdcfa59d23e65ae", 4713, 524898,
)
ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-c-subject-buffer-root-provenance-root-provenance-receipt.json",
    "a231eec31b29ca796c75cee03b702a3e35a9195e74675c8f56209419dfeb03c8", 7629, 524899,
)
V1_MANIFEST = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 524385,
)
CORRECTED_SOURCE = (
    "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c",
    "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962", 222212, 524723,
)
CANONICAL_SOURCE = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55", 218185, 428072,
)
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096", 60707, 428074,
)
PROPOSAL = (
    ("tools/verify_expanded_sealed_holdout_v1.py", "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309", 27311, 428806),
    ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md", "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4", 13237, 524760),
    ("oracle/phase3/expanded-sealed-holdout-v1.json", "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76", 6628, 524761),
)
GRAPH87 = (
    ("tools/render_candidate_current_overview_v87.py", "176ff7cee7735bb6a25475bf3d8f112def2ea0ff12779b28e1469c2fb85cdd44", 82214, 430870),
    ("docs/evidence/candidate-current-overview-v87.inputs.json", "03c191f676a4551b6643a3c57d86f57cac21a51517e40a86926bf49e5176a8ee", 1348917, 430884),
    ("docs/evidence/candidate-current-overview-v87.json", "1bd2765e4f22cc279872a5ab0253b1c55422899fad996bc2bc1aac4d4f300233", 4106304, 430885),
    ("docs/evidence/candidate-current-overview-v87.svg", "7af85c8f26d47ec5b7ff7813aa7bfd3ceec5f82498b60da8be5884558c521101", 6365, 430886),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
V4_PRODUCER = (
    "tools/run_owned_six_family_original_p0_producer_v4.py",
    "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782, 431710,
)
PROXY_SOURCE = (
    "class _RebarV6ForbiddenCtypes:\n"
    "    __slots__ = ()\n"
    "    def __getattribute__(self, name):\n"
    "        raise RuntimeError('V6 forbids historical ctypes: ' + str(name))\n"
    "ctypes = _RebarV6ForbiddenCtypes()\n"
)


class CampaignError(Exception):
    """An owner, original observation, recovery, or effect was rejected."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def exact_digest(value: object, role: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(char in "0123456789abcdef" for char in value),
         "require an exact lowercase SHA-256: " + role)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and os.path.realpath(sys.executable) == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True,
         "require independently pinned CPython 3.14.6 -I -B -S")
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "never preload a matcher, candidate, ctypes, or CPython regex engine")


def read_bootstrap(item: tuple) -> bytes:
    relative, expected, size, inode = item
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and not relative.endswith((".so", ".gz", ".zip", ".xz", ".tar"))
         and exact_digest(expected, relative)
         and type(size) is int and 0 < size <= MAX_OWNER,
         "require one bounded first-party source owner")
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == size
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject a substituted complete immutable owner: " + relative)
        blocks = []
        left = size
        while left:
            block = os.read(descriptor, min(left, 262144))
            need(bool(block), "reject truncated owner: " + relative)
            blocks.append(block)
            left -= len(block)
        need(not os.read(descriptor, 1), "reject extended owner: " + relative)
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed authenticated owner: " + relative)
        return raw
    finally:
        os.close(descriptor)


def bootstrap_previous() -> types.ModuleType:
    clean_runtime()
    raw = read_bootstrap(OLD[0])
    module = types.ModuleType("_rebar_owned_c_v6_frozen_source_wall_v5")
    module.__file__ = ROOT + "/" + OLD[0][0]
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.SCHEMA == "rebar-owned-repaired-c-original-campaign-v5"
         and module.SOURCE == OLD[0][0]
         and module.PROTOCOL == OLD[1][0]
         and module.CONTRACT == OLD[2][0]
         and module.ORIGINAL_CASES == ORIGINAL_CASE_COUNT
         and module.SUPPLEMENTAL_CASES == SEPARATE_REFERENCE_CASE_COUNT
         and tuple((name, count) for name, count, _ in module.SUITES) == SUITES,
         "reject an incomplete, changed, or non-source-clean V5 predecessor")
    extra = OLD + BUILD + (BUILD_RECEIPT, ROOT_RECEIPT, V1_MANIFEST,
                           CORRECTED_SOURCE, CANONICAL_SOURCE, ADAPTER,
                           V4_PRODUCER) + PROPOSAL + GRAPH87
    module.OWNED_PATHS = frozenset(module.OWNED_PATHS) | {
        SOURCE, PROTOCOL, CONTRACT, *(item[0] for item in extra)
    }
    module.SOURCE, module.PROTOCOL, module.CONTRACT = SOURCE, PROTOCOL, CONTRACT
    clean_runtime()
    return module


def record(item: tuple) -> dict:
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "device": DEVICE, "inode": item[3], "mode": "0600", "nlink": 1}


def parse_document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        value = producer.JsonReader(raw).parse()
    except Exception as error:
        raise CampaignError("reject malformed complete " + role + ": "
                            + str(error)) from error
    need(type(value) is dict, "require one complete machine document: " + role)
    return value


def require_old_contract(value: dict) -> None:
    need(value.get("schema") == "rebar-owned-repaired-c-original-campaign-v5-source-freeze"
         and value.get("version") == 5 and value.get("family") == FAMILY
         and value.get("goal_sha256")
         == "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
         and value.get("source", {}).get("sha256") == OLD[0][1]
         and value.get("protocol", {}).get("sha256") == OLD[1][1]
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("qualified_candidate_count") == 0,
         "preserve, without repurposing, the genuine historical C V5 freeze")


def validate_v1_manifest(value: dict, producer: types.ModuleType) -> None:
    phase = value.get("phase_gate")
    denominator = value.get("denominator")
    rows = value.get("suites")
    need(value.get("schema") == "rebar-cpython-re-p0-completeness-v1"
         and value.get("version") == 1
         and type(phase) is dict and phase.get("status") == "PASS"
         and phase.get("final_holdout_authorized") is False
         and type(denominator) is dict
         and denominator.get("final_required_case_execution_denominator")
         == ORIGINAL_CASE_COUNT
         and denominator.get("counted_suite_ids")
         == [name for name, _ in SUITES]
         and type(rows) is list and len(rows) == len(SUITES),
         "require the genuine original V1 direct-reference manifest")
    for row, (name, count) in zip(rows, SUITES, strict=True):
        spec = producer.suite_spec(name)
        need(type(row) is dict and row.get("id") == name
             and row.get("case_execution_count") == count
             and row.get("matrix_sha256") == spec.matrix_sha256
             and type(row.get("source")) is dict
             and row["source"].get("path") == spec.source_relative
             and row["source"].get("sha256") == spec.source_sha256
             and (name == "public_types_v1"
                  or row.get("baseline_records_sha256")
                  == spec.reference_sha256),
             "reject changed original V1 reference inventory: " + name)


def validate_build_and_root(build: dict, root_receipt: dict) -> dict:
    need(build.get("schema")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18-durable-publication-receipt"
         and build.get("version") == 18 and build.get("family") == FAMILY
         and build.get("status") == "PASS" and build.get("build_status") == "PASS"
         and build.get("label") == "phase2-v18-c-subject-buffer-root-provenance"
         and build.get("source_sha256") == BUILD[0][1]
         and build.get("protocol_sha256") == BUILD[1][1]
         and build.get("contract_sha256") == BUILD[2][1]
         and build.get("actual_compiler_process_count") == 14
         and build.get("expected_compiler_process_count") == 14
         and build.get("actual_source_apply_count") == 2
         and build.get("adapter_source_sha256") == ADAPTER[1]
         and build.get("original_source_sha256") == CANONICAL_SOURCE[1]
         and build.get("variant_source_sha256") == CORRECTED_SOURCE[1]
         and build.get("variant_source_bytes") == CORRECTED_SOURCE[2]
         and build.get("candidate_matching") == "NOT RUN"
         and build.get("candidate_correctness") == "NOT MEASURED"
         and build.get("native_libraries_loaded") == 0
         and build.get("holdout") == "NOT OPENED"
         and build.get("proposed_final_holdout_case_count")
         == EXPANDED_PROPOSED_CASE_COUNT,
         "require the genuine independently published 14-process C18 build")
    root = root_receipt.get("root")
    need(root_receipt.get("schema")
         == "rebar-phase2-owned-c-subject-buffer-source-build-v18-durable-root-provenance-receipt"
         and root_receipt.get("status") == "PASS"
         and root_receipt.get("version") == 18
         and root_receipt.get("family") == FAMILY
         and root_receipt.get("label") == build["label"]
         and root_receipt.get("source_sha256") == BUILD[0][1]
         and root_receipt.get("protocol_sha256") == BUILD[1][1]
         and root_receipt.get("contract_sha256") == BUILD[2][1]
         and root_receipt.get("canonical_build_receipt_sha256")
         == BUILD_RECEIPT[1]
         and root_receipt.get("canonical_build_receipt_bytes")
         == BUILD_RECEIPT[2]
         and root_receipt.get("canonical_build_receipt_device") == DEVICE
         and root_receipt.get("canonical_build_receipt_inode")
         == BUILD_RECEIPT[3]
         and root_receipt.get("actual_compiler_process_count") == 14
         and root_receipt.get("actual_source_phase_count") == 2
         and root_receipt.get("distinct_actual_phase_source_owner_count") == 4
         and root_receipt.get("distinct_actual_native_extension_count") == 2
         and root_receipt.get("canonical_build_archive_opened") is False
         and root_receipt.get("tmp_directory_scanned") is False
         and root_receipt.get("candidate_matching") == "NOT RUN"
         and root_receipt.get("holdout") == "NOT OPENED"
         and type(root) is dict and root.get("device") == ROOT_DEVICE
         and root.get("mode") == "0700"
         and root.get("nofollow_directory_descriptor") is True
         and root.get("phase_count") == 2
         and type(root.get("path")) is str
         and root["path"].startswith("/tmp/rebar-phase2-native-build-v8-c-")
         and type(root.get("phases")) is list and len(root["phases"]) == 2,
         "require a separately authenticated live C18 root-provenance receipt")
    identities = set()
    native_identities = set()
    for phase, expected_name in zip(root["phases"],
                                    ("reference-a", "reference-b"), strict=True):
        need(type(phase) is dict and phase.get("name") == expected_name
             and phase.get("device") == ROOT_DEVICE
             and phase.get("mode") == "0700"
             and phase.get("absolute_path") == root["path"] + "/" + expected_name
             and type(phase.get("source_owners")) is list
             and len(phase["source_owners"]) == 2,
             "reject a fabricated or reordered independently built C18 phase")
        native = phase.get("native_output")
        need(type(native) is dict and native.get("role") == "extension"
             and native.get("file_name") == NATIVE_NAME
             and native.get("sha256") == NATIVE_SHA256
             and native.get("bytes") == NATIVE_BYTES
             and native.get("device") == ROOT_DEVICE
             and native.get("mode") == "0700" and native.get("nlink") == 1
             and native.get("native_loaded") is False
             and native.get("absolute_path")
             == phase["absolute_path"] + "/native/" + NATIVE_NAME,
             "reject an unowned or preloaded genuine C18 phase extension")
        native_identities.add((native["device"], native.get("inode")))
        for owner, expected in zip(phase["source_owners"],
                                   (CORRECTED_SOURCE, ADAPTER), strict=True):
            expected_relative = ("candidates/_vm_native.c"
                                 if expected is CORRECTED_SOURCE
                                 else "candidates/vm_candidate.py")
            need(type(owner) is dict and owner.get("relative_path")
                 == expected_relative
                 and owner.get("sha256") == expected[1]
                 and owner.get("bytes") == expected[2]
                 and owner.get("device") == ROOT_DEVICE
                 and owner.get("mode") == "0600"
                 and owner.get("nlink") == 1
                 and owner.get("absolute_path")
                 == phase["absolute_path"] + "/source/" + expected_relative,
                 "reject a crossed corrected-source or unchanged-adapter owner")
            identities.add((owner["device"], owner.get("inode")))
    need(len(identities) == 4 and len(native_identities) == 2,
         "require two actual distinct phases, four source owners, and two outputs")
    need(build.get("current_rust_attempted_suite_count") == 13
         and build.get("current_rust_candidate_status") == "FAIL"
         and build.get("current_rust_completed_suite_count") == 8
         and build.get("current_rust_infrastructure_failure_count") == 5
         and build.get("current_rust_verified_passing_case_count") == 12942
         and build.get("current_rust_semantic_mismatch_count") == "NOT MEASURED"
         and root_receipt.get("current_rust_failure_receipt_sha256")
         == build.get("current_rust_failure_receipt_sha256"),
         "preserve actual signed Rust results without inventing conclusions")
    return root


def validate_proposal(value: dict) -> None:
    need(value.get("schema") == "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
         and value.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
         and value.get("case_count") == EXPANDED_PROPOSED_CASE_COUNT
         and value.get("original_p0_case_count") == ORIGINAL_CASE_COUNT
         and value.get("separate_differential_case_count")
         == SEPARATE_REFERENCE_CASE_COUNT
         and value.get("final_protocol_status") == "NOT FROZEN"
         and value.get("secret_status") == "NOT GENERATED"
         and value.get("case_status") == "NOT GENERATED; NOT OPENED"
         and value.get("qualified_independent_family_count") == 0,
         "never generate, weaken, open, or count expanded holdout proposals")


def source_effects() -> dict:
    return {
        "actual_archives_opened": 0,
        "actual_candidate_imports": 0,
        "actual_candidate_workers": 0,
        "actual_clock_samples": 0,
        "actual_compiler_processes": 0,
        "actual_guard_installations": 0,
        "actual_holdout_cases_read": 0,
        "actual_native_libraries_loaded": 0,
        "actual_network_requests": 0,
        "actual_private_roots_opened": 0,
        "actual_reference_workers": 0,
        "actual_workspace_mutations": 0,
    }


def actual_authority() -> dict:
    return {
        "family": FAMILY,
        "label": LABEL,
        "build_source_sha256": BUILD[0][1],
        "build_protocol_sha256": BUILD[1][1],
        "build_contract_sha256": BUILD[2][1],
        "build_receipt_sha256": BUILD_RECEIPT[1],
        "root_receipt_sha256": ROOT_RECEIPT[1],
        "producer_source_sha256":
            "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        "producer_protocol_sha256":
            "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        "producer_contract_sha256":
            "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        "guard_source_sha256":
            "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        "guard_protocol_sha256":
            "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        "guard_contract_sha256":
            "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        "phase1_v4_contract_sha256":
            "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        "original_v1_manifest_sha256": V1_MANIFEST[1],
        "proposal_contract_sha256": PROPOSAL[2][1],
        "native_engine_sha256": NATIVE_SHA256,
        "native_bridge_sha256": NATIVE_SHA256,
        "worker_timeout_seconds": str(WORKER_TIMEOUT_SECONDS),
    }


def options(arguments: list[str]) -> dict:
    need(type(arguments) is list and all(type(item) is str for item in arguments),
         "reject malformed C18 campaign authorization")
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    chosen = [mode for mode in modes if arguments.count(mode) == 1]
    need(len(chosen) == 1
         and sum(arguments.count(mode) for mode in modes) == 1,
         "select exactly one unambiguous frozen source or actual operation")
    mode = chosen[0]
    accepted = {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
    actual = mode in ("--run", "--worker", "--recover")
    if actual:
        accepted.update("--" + key.replace("_", "-")
                        for key in actual_authority())
        if mode == "--worker":
            accepted.update({"--suite", "--activation-inode",
                             "--recovery-journal-sha256"})
        if mode == "--recover":
            accepted.add("--recovery-journal-sha256")
    answer = {"mode": mode}
    index = 0
    while index < len(arguments):
        flag = arguments[index]
        if flag == mode:
            index += 1
            continue
        need(flag in accepted and flag not in answer
             and index + 1 < len(arguments),
             "reject unpinned, duplicate, guessed-root, or hidden authorization")
        answer[flag] = arguments[index + 1]
        index += 2
    for flag in ("--source-sha256", "--protocol-sha256"):
        need(flag in answer, "independently pin " + flag)
        exact_digest(answer[flag], flag)
    if mode == "--render-contract":
        need("--contract-sha256" not in answer,
             "do not claim an independently frozen contract while rendering it")
    else:
        need("--contract-sha256" in answer, "independently pin V6 contract")
        exact_digest(answer["--contract-sha256"], "V6 contract")
    if actual:
        authority = actual_authority()
        for key, expected in authority.items():
            flag = "--" + key.replace("_", "-")
            need(answer.get(flag) == expected,
                 "require separately pinned genuine actual C18 authority: " + flag)
        if mode == "--worker":
            need(answer.get("--suite") in dict(SUITES),
                 "pin exactly one immutable genuine original suite")
            need(type(answer.get("--activation-inode")) is str
                 and answer["--activation-inode"].isdigit()
                 and int(answer["--activation-inode"]) > 0,
                 "pin one actual promoted original native inode")
            exact_digest(answer.get("--recovery-journal-sha256"),
                         "actual original-native recovery journal")
        if mode == "--recover":
            exact_digest(answer.get("--recovery-journal-sha256"),
                         "actual original-native recovery journal")
    else:
        need(set(answer) <= {"mode", "--source-sha256",
                             "--protocol-sha256", "--contract-sha256"},
             "never authorize an actual root, worker, native, or candidate in source mode")
    return answer


def original_owner_document(value: dict, key: str, item: tuple) -> None:
    observed = value.get(key)
    need(type(observed) is dict and observed.get("path") == item[0]
         and observed.get("sha256") == item[1],
         "reject substituted frozen " + key)


def collect_context(old: types.ModuleType, parsed: dict,
                    *, controls: bool = False) -> tuple[types.ModuleType, dict, dict]:
    clean_runtime()
    with old.SourceWall() as wall:
        own_source = old.read_dynamic(SOURCE, parsed["--source-sha256"])
        protocol = old.read_dynamic(PROTOCOL, parsed["--protocol-sha256"])
        need(own_source.endswith(b"\n") and not own_source.endswith(b"\n\n")
             and protocol.endswith(b"\n") and not protocol.endswith(b"\n\n"),
             "freeze complete V6 controller and protocol")
        raw_by_path = {item[0]: old.read_owner(item)
                       for item in old.STATIC_OWNERS}
        additions = OLD + BUILD + (BUILD_RECEIPT, ROOT_RECEIPT, V1_MANIFEST,
                                   CORRECTED_SOURCE, CANONICAL_SOURCE, ADAPTER,
                                   V4_PRODUCER) + PROPOSAL + GRAPH87
        for item in additions:
            if item[0] not in raw_by_path:
                raw_by_path[item[0]] = read_bootstrap(item)
        producer = old.load_producer(raw_by_path[old.PRODUCER[0][0]])
        context = old.validate_context(raw_by_path, producer)
        require_old_contract(parse_document(
            producer, raw_by_path[OLD[2][0]], "complete historical C V5 contract"))
        manifest = parse_document(producer, raw_by_path[V1_MANIFEST[0]],
                                  "original V1 independent reference manifest")
        validate_v1_manifest(manifest, producer)
        build_contract = parse_document(producer, raw_by_path[BUILD[2][0]],
                                        "C18 source-build contract")
        need(build_contract.get("schema")
             == "rebar-phase2-owned-c-subject-buffer-source-build-v18-source-freeze"
             and build_contract.get("version") == 18
             and build_contract.get("family") == FAMILY,
             "reject the independently frozen first-party C18 source contract")
        build = parse_document(producer, raw_by_path[BUILD_RECEIPT[0]],
                               "actual small C18 build publication receipt")
        root_document = parse_document(producer, raw_by_path[ROOT_RECEIPT[0]],
                                       "actual small C18 root-provenance receipt")
        root = validate_build_and_root(build, root_document)
        proposal = parse_document(producer, raw_by_path[PROPOSAL[2][0]],
                                  "unopened expanded-holdout proposal")
        validate_proposal(proposal)
        graph = parse_document(producer, raw_by_path[GRAPH87[2][0]],
                               "independently frozen overview at version 87")
        need(graph.get("schema") == "rebar-candidate-current-overview-v87-summary"
             and graph.get("version") == 87
             and graph.get("status") == "PASS"
             and graph.get("full_case_denominator") == ORIGINAL_CASE_COUNT
             and graph.get("suite_count") == len(SUITES)
             and graph.get("qualified_candidate_count") == 0
             and graph.get("final_holdout_opened") is False
             and graph.get("performance") == "NOT MEASURED",
             "preserve the separately published authentic V87 overview")
        state = {"historical_context": context, "source_raw": own_source,
                 "protocol_raw": protocol, "producer_raw":
                 raw_by_path[old.PRODUCER[0][0]], "guard_raw":
                 raw_by_path[old.GUARD[0][0]], "phase1_v4":
                 parse_document(producer, raw_by_path[old.P0[2][0]],
                                "passing frozen P0 V4"),
                 "manifest": manifest, "build": build,
                 "root_receipt": root_document, "root": root,
                 "proposal": proposal, "graph": graph}
        expected = contract_document(parsed, old, state)
        if parsed["mode"] != "--render-contract":
            contract_raw = old.read_dynamic(CONTRACT,
                                            parsed["--contract-sha256"])
            actual = parse_document(producer, contract_raw,
                                    "independently frozen complete C V6 contract")
            need(contract_raw == producer.canonical(expected)
                 and actual == expected,
                 "reject an altered, noncanonical, or incompletely pinned C V6 contract")
        rejected = hostile_controls(wall, old) if controls else []
        result = {"schema": SCHEMA + "-frozen-context",
                  "status": "PASS", "family": FAMILY, "label": LABEL,
                  "source_sha256": parsed["--source-sha256"],
                  "protocol_sha256": parsed["--protocol-sha256"],
                  "contract_sha256": parsed.get("--contract-sha256"),
                  "suite_count": len(SUITES),
                  "case_execution_denominator": ORIGINAL_CASE_COUNT,
                  "separate_reference_case_count": SEPARATE_REFERENCE_CASE_COUNT,
                  "separate_reference_cases_counted_as_candidate_cases": False,
                  "actual_build_compiler_process_count": 14,
                  "actual_build_source_phase_count": 2,
                  "build_receipt_sha256": BUILD_RECEIPT[1],
                  "root_receipt_sha256": ROOT_RECEIPT[1],
                  "expanded_holdout_proposed_case_count": EXPANDED_PROPOSED_CASE_COUNT,
                  "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
                  "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                  "candidate_matching": "NOT RUN",
                  "candidate_correctness": "NOT MEASURED",
                  "candidate_qualified": False,
                  "runtime_non_delegation": "NOT ESTABLISHED",
                  "performance": "NOT MEASURED", "memory": "NOT MEASURED",
                  "undefined_behavior": "NOT MEASURED",
                  "holdout": "NOT OPENED", "winner_selected": False,
                  "source_only_effects": source_effects(),
                  "hostile_controls": rejected,
                  "physical_source_wall_read_count": wall.read_count}
    clean_runtime()
    return producer, state, result


def contract_document(parsed: dict, old: types.ModuleType, state: dict) -> dict:
    return {
        "schema": SCHEMA + "-source-freeze", "version": 6,
        "phase": "PHASE 2: CANDIDATES",
        "status": "SOURCE FROZEN; ACTUAL C18 ORIGINAL CAMPAIGN NOT RUN",
        "status_scope": "SOURCE FREEZE AND ACTUAL RUN AUTHORIZATION; NOT A CANDIDATE RESULT",
        "family": FAMILY, "label": LABEL,
        "goal_sha256": old.GOAL[1],
        "source": {"path": SOURCE, "sha256": parsed["--source-sha256"],
                   "bytes": len(state["source_raw"])},
        "protocol": {"path": PROTOCOL, "sha256": parsed["--protocol-sha256"],
                     "bytes": len(state["protocol_raw"])},
        "pinned_cpython": {"path": PYTHON, "version": "3.14.6",
                            "required_flags": ["-I", "-B", "-S"]},
        "historical_v5_source_freeze": {"owners": [record(item) for item in OLD],
                                         "actual_campaign_run": False},
        "phase_one_v4": {"status": "PASS",
            "owners": [record(item) for item in old.P0],
            "original_obligation_count": 73,
            "original_crosswalk_count": 34,
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "original_suite_count": len(SUITES),
            "named_private_waiver_count": 13,
            "separate_reference_case_count": SEPARATE_REFERENCE_CASE_COUNT,
            "separate_reference_cases_counted_in_original_denominator": False},
        "original_reference_manifest_v1": {
            "owner": record(V1_MANIFEST),
            "use": "SOURCE-OWNED ORIGINAL REFERENCE VECTORS ONLY",
            "candidate_authorization": "LATEST P0 V4 AND EXPLICIT V6 ONLY",
            "archive_opens_in_source_modes": 0,
            "original_suite_count": len(SUITES),
            "original_case_execution_denominator": ORIGINAL_CASE_COUNT,
            "public_types_uses_corrected_v5_reference": True},
        "frozen_original_producer": {"version": 5,
            "owners": [record(item) for item in old.PRODUCER],
            "family_count": 6, "suite_count": len(SUITES),
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "suites": [{"suite": name, "case_execution_count": count}
                       for name, count in SUITES],
            "candidate_source_file_modified": False,
            "authenticated_corrected_family_overlay_in_memory_only": True},
        "first_party_c_sources": {
            "original_canonical_source": record(CANONICAL_SOURCE),
            "corrected_source_variant": record(CORRECTED_SOURCE),
            "unchanged_python_adapter": record(ADAPTER),
            "corrected_native_sha256": NATIVE_SHA256,
            "corrected_native_bytes": NATIVE_BYTES,
            "native_engine_and_bridge_share_one_owned_extension": True,
            "source_targets_modified": 0,
            "external_package": "FORBIDDEN",
            "stdlib_re_delegation": "FORBIDDEN",
            "cross_candidate_delegation": "FORBIDDEN",
            "fallback": "FORBIDDEN"},
        "actual_first_party_c18_build": {
            "owners": [record(item) for item in BUILD],
            "build_receipt": record(BUILD_RECEIPT),
            "root_provenance_receipt": record(ROOT_RECEIPT),
            "status": "PASS", "build_status": "PASS",
            "actual_compiler_process_count": 14,
            "actual_source_apply_count": 2,
            "actual_distinct_source_phase_count": 2,
            "actual_distinct_phase_source_owner_count": 4,
            "actual_distinct_native_extension_count": 2,
            "private_phase_device": ROOT_DEVICE,
            "private_native_mode": "0700",
            "required_promoted_workspace_device": DEVICE,
            "required_promoted_workspace_mode": "0600",
            "build_archive_opened": False,
            "source_modes_open_private_root": False,
            "source_modes_read_installed_native": False,
            "candidate_matching": "NOT RUN",
            "build_pass_means": "REPRODUCIBLE NATIVE BUILD AND ROOT PROVENANCE ONLY"},
        "runtime_guard": {"version": 2,
            "owners": [record(item) for item in old.GUARD],
            "guard_installed_before_candidate_import": True,
            "native_roles": ["engine", "bridge"],
            "nested_original_case_count": 128,
            "required_child_interpreters": 11,
            "required_nested_case_executions": 394,
            "historical_ctypes_import": "EXACT AUTHENTICATED IN-MEMORY FAIL-CLOSED PROXY",
            "historical_producer_source": record(V4_PRODUCER),
            "runtime_non_delegation": "NOT ESTABLISHED"},
        "preserved_historical_c_results": state["historical_context"]["history"],
        "rust_results_bound_to_signed_c18_receipts": {
            "candidate_status": "FAIL", "attempted_suite_count": 13,
            "completed_suite_count": 8, "infrastructure_failure_count": 5,
            "verified_passing_case_count": 12942,
            "semantic_mismatch_count": "NOT MEASURED",
            "underlying_failure_cause": "NOT ESTABLISHED",
            "failure_receipt_sha256":
                state["build"]["current_rust_failure_receipt_sha256"]},
        "published_overview_at_source_freeze": {
            "version": 87, "owners": [record(item) for item in GRAPH87],
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED",
            "holdout": "NOT OPENED"},
        "expanded_holdout_proposal": {
            "owners": [record(item) for item in PROPOSAL],
            "proposed_case_count": EXPANDED_PROPOSED_CASE_COUNT,
            "case_status": "NOT GENERATED; NOT OPENED",
            "final_protocol_status": "NOT FROZEN",
            "holdout_opened": False,
            "proposal_is_candidate_correctness": False},
        "actual_operation_policy": {
            "authorization": "EXPLICIT INDEPENDENTLY PINNED --run ONLY",
            "source_freeze_runs_candidate": False,
            "required_authority": actual_authority(),
            "worker_count": len(SUITES),
            "actual_worker_process_ids_required": True,
            "distinct_worker_process_count_required": len(SUITES),
            "worker_command_flags": ["-I", "-B", "-S"],
            "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
            "timeout_is_per_original_suite": True,
            "timeout_discards_remaining_suites": False,
            "max_worker_stdout_bytes": MAX_WORKER_STDOUT,
            "max_worker_stderr_bytes": MAX_WORKER_STDERR,
            "required_external_locale_names": ["en_US.iso88591", "en_US.utf8"],
            "candidate_localedef_workers": 0,
            "preserve_scoped_original_fork_and_correctness_clock": True,
            "preserve_all_original_records_and_failures": True,
            "recovery": "DURABLE JOURNAL AND EXACT ORIGINAL INODE RESTORATION",
            "standard_library_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN"},
        "source_only_effects": source_effects(),
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualification": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "supplemental_candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def blocked(label: str, operation: object) -> str:
    try:
        operation()
    except Exception:
        return label
    raise CampaignError("accepted forbidden source-only operation: " + label)


def hostile_controls(wall: object, old: types.ModuleType) -> list:
    del old
    actions = []
    for name in ("re", "_sre", "regex", "re2", "pcre2", "ctypes", "cffi",
                 "subprocess", "socket", "threading", "multiprocessing",
                 "time", "gzip", "zipfile", "tarfile",
                 "candidates.vm_candidate", "candidates.rust_candidate"):
        actions.append(("forbidden import " + name,
                        lambda item=name: builtins.__import__(item)))
    for label, path in (
        ("installed C native", ROOT + "/" + NATIVE_RELATIVE),
        ("unattested C18 private root", "/tmp/rebar-phase2-native-build-v8-c-forbidden"),
        ("unopened C18 build archive",
         ROOT + "/oracle/phase2/evidence/native-source-build-v18-c-phase2-v18-c-subject-buffer-root-provenance.json.gz"),
        ("unopened final holdout", ROOT + "/performance/holdout/forbidden.json"),
    ):
        actions.append((label, lambda item=path: os.open(
            item, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))))
    actions.extend((
        ("workspace creation", lambda: os.open(
            ROOT + "/.rebar-v6-never-created", os.O_WRONLY | os.O_CREAT, 0o600)),
        ("private root directory scan", lambda: os.listdir("/tmp")),
        ("canonical native stat", lambda: os.stat(ROOT + "/" + NATIVE_RELATIVE)),
        ("candidate native replacement", lambda: os.replace("not-a", "not-b")),
        ("unreviewed actual campaign", lambda: options(["--run"])),
        ("unreviewed actual worker", lambda: options(["--worker"])),
        ("unreviewed native recovery", lambda: options(["--recover"])),
        ("candidate worker process", lambda: os.system("false")),
        ("candidate interpreter pipe", lambda: os.pipe()),
        ("native activation durability", lambda: os.fsync(0)),
        ("benchmark clock sample", lambda: os.times()),
    ))
    answers = [blocked(name, action) for name, action in actions]
    need(len(answers) >= 30 and len(wall.blocked) >= 10
         and sum(wall.blocked.values()) >= 23,
         "physically reject matchers, archives, roots, native activation and timing")
    return answers


def write_all(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        count = os.write(descriptor, payload[offset:])
        need(type(count) is int and count > 0, "reject an incomplete durable write")
        offset += count


def directory(path: str, *, device: int | None = None,
              inode: int | None = None, mode: int | None = None) -> int:
    handle = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                     | getattr(os, "O_CLOEXEC", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(handle)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and (device is None or info.st_dev == device)
             and (inode is None or info.st_ino == inode)
             and (mode is None or stat.S_IMODE(info.st_mode) == mode),
             "reject substituted exact no-follow activation directory")
        return handle
    except BaseException:
        os.close(handle)
        raise


def exclusive_document(root: str, name: str, document: dict,
                       producer: types.ModuleType) -> dict:
    need(type(name) is str and name not in ("", ".", "..") and "/" not in name,
         "write only one exact exclusive durable journal owner")
    parent = directory(root, mode=0o700)
    handle = None
    try:
        raw = producer.canonical(document)
        handle = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=parent)
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
             and stat.S_IMODE(before.st_mode) == 0o600
             and before.st_nlink == 1,
             "reject substituted exclusive original recovery evidence")
        write_all(handle, raw)
        os.fsync(handle)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
             and after.st_size == len(raw), "reject incomplete durable evidence")
        os.close(handle)
        handle = None
        os.fsync(parent)
        return {"path": root + "/" + name, "relative": name,
                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                "device": after.st_dev, "inode": after.st_ino,
                "mode": "0600", "nlink": 1,
                "exclusive_creation": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True}
    finally:
        if handle is not None:
            os.close(handle)
        os.close(parent)


def read_private(name: str, digest: str,
                 producer: types.ModuleType) -> tuple[dict, dict]:
    exact_digest(digest, "durable private recovery owner")
    parent = directory(RECOVERY_ROOT, mode=0o700)
    try:
        handle = os.open(name, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent)
        try:
            info = os.fstat(handle)
            need(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
                 and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o600
                 and 0 < info.st_size <= MAX_OWNER,
                 "reject changed original-native recovery journal")
            chunks = []
            left = info.st_size
            while left:
                chunk = os.read(handle, min(left, 262144))
                need(bool(chunk), "reject a truncated native recovery journal")
                chunks.append(chunk)
                left -= len(chunk)
            need(not os.read(handle, 1), "reject appended native recovery evidence")
            raw = b"".join(chunks)
            need(hashlib.sha256(raw).hexdigest() == digest,
                 "reject an unpinned or substituted durable recovery journal")
            value = parse_document(producer, raw, "durable native recovery journal")
            return value, {"relative": name, "path": RECOVERY_ROOT + "/" + name,
                           "sha256": digest, "bytes": info.st_size,
                           "device": info.st_dev, "inode": info.st_ino,
                           "mode": "0600", "nlink": 1}
        finally:
            os.close(handle)
    finally:
        os.close(parent)


def hash_descriptor(handle: int, expected_size: int,
                    expected_digest: str) -> bytes:
    state = hashlib.sha256()
    chunks = []
    left = expected_size
    while left:
        block = os.read(handle, min(left, 262144))
        need(bool(block), "reject truncated authentic native or source owner")
        chunks.append(block)
        state.update(block)
        left -= len(block)
    need(not os.read(handle, 1) and state.hexdigest() == expected_digest,
         "reject changed complete authentic native or source bytes")
    return b"".join(chunks)


def exact_original_native() -> tuple[bytes, dict]:
    expected_digest = "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
    expected_inode, expected_bytes = 430300, 149976
    handle = os.open(ROOT + "/" + NATIVE_RELATIVE,
                     os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == expected_inode
             and before.st_size == expected_bytes
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o755,
             "refuse to replace a changed, temporarily activated, or foreign C native")
        raw = hash_descriptor(handle, expected_bytes, expected_digest)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a C canonical native changed while authenticating it")
        return raw, {"relative": NATIVE_RELATIVE, "sha256": expected_digest,
                     "bytes": expected_bytes, "device": DEVICE,
                     "inode": expected_inode, "mode": "0755", "nlink": 1}
    finally:
        os.close(handle)


def read_root_phase(root: dict) -> tuple[bytes, dict]:
    phase = root["phases"][0]
    rootfd = directory(root["path"], device=ROOT_DEVICE,
                       inode=root["inode"], mode=0o700)
    phasefd = nativefd = handle = None
    try:
        phasefd = os.open("reference-a", os.O_RDONLY
                          | getattr(os, "O_DIRECTORY", 0)
                          | getattr(os, "O_CLOEXEC", 0)
                          | getattr(os, "O_NOFOLLOW", 0), dir_fd=rootfd)
        pinfo = os.fstat(phasefd)
        need(stat.S_ISDIR(pinfo.st_mode)
             and pinfo.st_dev == phase["device"]
             and pinfo.st_ino == phase["inode"]
             and pinfo.st_uid == os.geteuid()
             and stat.S_IMODE(pinfo.st_mode) == 0o700,
             "reject a substituted receipt-bound genuine C18 phase")
        nativefd = os.open("native", os.O_RDONLY
                           | getattr(os, "O_DIRECTORY", 0)
                           | getattr(os, "O_CLOEXEC", 0)
                           | getattr(os, "O_NOFOLLOW", 0), dir_fd=phasefd)
        native = phase["native_output"]
        handle = os.open(NATIVE_NAME, os.O_RDONLY
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), dir_fd=nativefd)
        before = os.fstat(handle)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == native["device"]
             and before.st_ino == native["inode"]
             and before.st_size == NATIVE_BYTES
             and before.st_uid == native["uid"]
             and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o700,
             "reject an unbound or substituted actual C18 original ELF owner")
        payload = hash_descriptor(handle, NATIVE_BYTES, NATIVE_SHA256)
        after = os.fstat(handle)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject a C18 phase output swapped during verified streaming")
        return payload, dict(native)
    finally:
        for item in (handle, nativefd, phasefd, rootfd):
            if item is not None:
                os.close(item)


def native_directory() -> int:
    return directory(ROOT + "/candidates", device=DEVICE)


def prepare_recovery_root() -> None:
    try:
        os.mkdir(RECOVERY_ROOT, 0o700)
    except FileExistsError as error:
        raise CampaignError(
            "existing V6 recovery evidence requires separately pinned --recover") from error
    handle = directory(RECOVERY_ROOT, mode=0o700)
    try:
        os.fsync(handle)
    finally:
        os.close(handle)


def activate_native(parsed: dict, producer: types.ModuleType,
                    state: dict) -> dict:
    _, original = exact_original_native()
    payload, phase_native = read_root_phase(state["root"])
    need(phase_native["device"] != original["device"],
         "require the authentic cross-device C18 output and workspace")
    prepare_recovery_root()
    journal = {
        "schema": SCHEMA + "-durable-original-native-recovery-journal",
        "status": "PREPARED", "version": 6, "family": FAMILY, "label": LABEL,
        "controller_source_sha256": parsed["--source-sha256"],
        "controller_protocol_sha256": parsed["--protocol-sha256"],
        "controller_contract_sha256": parsed["--contract-sha256"],
        "build_receipt_sha256": BUILD_RECEIPT[1],
        "root_receipt_sha256": ROOT_RECEIPT[1],
        "target_relative": NATIVE_RELATIVE, "backup_filename": BACKUP_NAME,
        "stage_filename": STAGE_NAME, "original": original,
        "phase_native": phase_native,
        "corrected_source": record(CORRECTED_SOURCE),
        "unchanged_adapter": record(ADAPTER),
        "phase_native_sha256": NATIVE_SHA256,
        "cross_device_rename_performed": False,
        "source_targets_modified": 0, "holdout": "NOT OPENED",
    }
    journal_owner = exclusive_document(RECOVERY_ROOT, JOURNAL_NAME,
                                       journal, producer)
    parent = native_directory()
    staged = None
    backup_linked = False
    try:
        for name in (BACKUP_NAME, STAGE_NAME):
            try:
                os.stat(name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise CampaignError("reject an existing unowned C native recovery artifact")
        exclusive_document(RECOVERY_ROOT, "link-intention-v6.json", {
            "schema": SCHEMA + "-mutation-intention", "status": "PREPARED",
            "operation": "ADJACENT EXACT ORIGINAL HARD LINK",
            "journal_sha256": journal_owner["sha256"],
            "original_device": original["device"],
            "original_inode": original["inode"],
            "backup_filename": BACKUP_NAME}, producer)
        _, current_original = exact_original_native()
        need(current_original == original,
             "original native changed after durable recovery journal")
        os.link(NATIVE_NAME, BACKUP_NAME, src_dir_fd=parent,
                dst_dir_fd=parent, follow_symlinks=False)
        backup_linked = True
        os.fsync(parent)
        exclusive_document(RECOVERY_ROOT, "stage-intention-v6.json", {
            "schema": SCHEMA + "-mutation-intention", "status": "PREPARED",
            "operation": "EXCLUSIVE SAME-DEVICE STREAM COPY",
            "journal_sha256": journal_owner["sha256"],
            "stage_filename": STAGE_NAME, "stage_mode": "0600",
            "native_sha256": NATIVE_SHA256,
            "native_bytes": NATIVE_BYTES}, producer)
        staged = os.open(STAGE_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0),
                         0o600, dir_fd=parent)
        stage_info = os.fstat(staged)
        need(stat.S_ISREG(stage_info.st_mode)
             and stage_info.st_dev == DEVICE
             and stage_info.st_uid == os.geteuid()
             and stage_info.st_nlink == 1
             and stat.S_IMODE(stage_info.st_mode) == 0o600,
             "require exact exclusive 0600 same-device C18 native stage")
        exclusive_document(RECOVERY_ROOT, "stage-inode-intention-v6.json", {
            "schema": SCHEMA + "-mutation-intention", "status": "PREPARED",
            "operation": "JOURNALED NEW STAGE INODE BEFORE STREAMING",
            "journal_sha256": journal_owner["sha256"],
            "stage_device": stage_info.st_dev,
            "stage_inode": stage_info.st_ino,
            "stage_uid": stage_info.st_uid,
            "stage_mode": "0600",
            "native_sha256": NATIVE_SHA256}, producer)
        write_all(staged, payload)
        os.fsync(staged)
        completed = os.fstat(staged)
        need((completed.st_dev, completed.st_ino)
             == (stage_info.st_dev, stage_info.st_ino)
             and completed.st_size == NATIVE_BYTES,
             "reject incomplete, substituted, or unjournaled C18 stage")
        os.close(staged)
        staged = None
        exclusive_document(RECOVERY_ROOT, "promotion-intention-v6.json", {
            "schema": SCHEMA + "-mutation-intention", "status": "PREPARED",
            "operation": "ATOMIC SAME-DIRECTORY PROMOTION",
            "journal_sha256": journal_owner["sha256"],
            "stage_device": completed.st_dev,
            "stage_inode": completed.st_ino,
            "native_sha256": NATIVE_SHA256,
            "original_inode_recoverable": original["inode"],
            "cross_device_rename_performed": False}, producer)
        os.replace(STAGE_NAME, NATIVE_NAME, src_dir_fd=parent,
                   dst_dir_fd=parent)
        os.fsync(parent)
        active = os.stat(NATIVE_NAME, dir_fd=parent, follow_symlinks=False)
        backup = os.stat(BACKUP_NAME, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(active.st_mode)
             and (active.st_dev, active.st_ino, active.st_size)
             == (DEVICE, completed.st_ino, NATIVE_BYTES)
             and stat.S_IMODE(active.st_mode) == 0o600
             and active.st_nlink == 1
             and (backup.st_dev, backup.st_ino, backup.st_nlink)
             == (DEVICE, original["inode"], 1)
             and stat.S_IMODE(backup.st_mode) == 0o755,
             "reject promoted C18 identity or exact original hard-link recovery")
        result = {"schema": SCHEMA + "-native-activation", "status": "PASS",
                  "family": FAMILY, "label": LABEL,
                  "journal": journal_owner,
                  "journal_document": journal,
                  "phase_native_sha256": NATIVE_SHA256,
                  "native_sha256": NATIVE_SHA256,
                  "native_bytes": NATIVE_BYTES,
                  "native_device": active.st_dev,
                  "native_inode": active.st_ino,
                  "native_mode": "0600", "native_nlink": 1,
                  "original": original,
                  "corrected_source_sha256": CORRECTED_SOURCE[1],
                  "adapter_sha256": ADAPTER[1],
                  "source_targets_modified": 0,
                  "holdout": "NOT OPENED"}
        result["activation"] = exclusive_document(
            RECOVERY_ROOT, "native-activation-v6.json", result, producer)
        return result
    except BaseException:
        if staged is not None:
            os.close(staged)
        if backup_linked:
            restore_native(journal, journal_owner["sha256"], producer)
        raise
    finally:
        os.close(parent)


def restore_native(journal: dict, journal_sha256: str,
                   producer: types.ModuleType) -> dict:
    disk, _ = read_private(JOURNAL_NAME, journal_sha256, producer)
    need(disk == journal
         and journal.get("schema")
         == SCHEMA + "-durable-original-native-recovery-journal"
         and journal.get("family") == FAMILY
         and journal.get("label") == LABEL
         and journal.get("target_relative") == NATIVE_RELATIVE
         and journal.get("backup_filename") == BACKUP_NAME
         and journal.get("stage_filename") == STAGE_NAME
         and journal.get("phase_native_sha256") == NATIVE_SHA256
         and journal.get("build_receipt_sha256") == BUILD_RECEIPT[1]
         and journal.get("root_receipt_sha256") == ROOT_RECEIPT[1],
         "refuse a substituted or overly broad original native recovery journal")
    original = journal["original"]
    parent = native_directory()
    operations = []
    try:
        try:
            backup = os.stat(BACKUP_NAME, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            backup = None
        target = os.stat(NATIVE_NAME, dir_fd=parent, follow_symlinks=False)
        if backup is not None:
            need(stat.S_ISREG(backup.st_mode)
                 and (backup.st_dev, backup.st_ino)
                 == (original["device"], original["inode"])
                 and stat.S_IMODE(backup.st_mode) == 0o755,
                 "refuse to restore an unrelated C native backup")
            if (target.st_dev, target.st_ino) == (original["device"],
                                                  original["inode"]):
                need(target.st_nlink == 2 and backup.st_nlink == 2,
                     "reject changed original C hard-link ownership")
                os.unlink(BACKUP_NAME, dir_fd=parent)
                operations.append("REMOVE EXACT ORIGINAL RECOVERY HARD LINK")
            else:
                need(target.st_dev == DEVICE and target.st_size == NATIVE_BYTES
                     and target.st_nlink == 1
                     and stat.S_IMODE(target.st_mode) == 0o600,
                     "refuse to overwrite a foreign C canonical native")
                handle = os.open(NATIVE_NAME,
                                 os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                                 | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent)
                try:
                    hash_descriptor(handle, NATIVE_BYTES, NATIVE_SHA256)
                finally:
                    os.close(handle)
                os.replace(BACKUP_NAME, NATIVE_NAME,
                           src_dir_fd=parent, dst_dir_fd=parent)
                operations.append("RESTORE AUTHENTICATED EXACT ORIGINAL INODE")
            os.fsync(parent)
        else:
            need((target.st_dev, target.st_ino)
                 == (original["device"], original["inode"]),
                 "refuse recovery of an unjournaled foreign C native")
        try:
            stage = os.stat(STAGE_NAME, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            stage = None
        if stage is not None:
            need(stat.S_ISREG(stage.st_mode) and stage.st_dev == DEVICE
                 and stage.st_uid == os.geteuid()
                 and stage.st_nlink == 1
                 and stat.S_IMODE(stage.st_mode) == 0o600,
                 "refuse to remove an unrelated C native stage")
            need(stage.st_size <= NATIVE_BYTES,
                 "reject an overlarge recovery-journal-bound C native stage")
            handle = os.open(STAGE_NAME,
                             os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0), dir_fd=parent)
            try:
                prefix = os.read(handle, NATIVE_BYTES + 1)
                root_payload, _ = read_root_phase(
                    validate_build_and_root(
                        parse_document(producer, read_bootstrap(BUILD_RECEIPT),
                                       "genuine C18 build receipt"),
                        parse_document(producer, read_bootstrap(ROOT_RECEIPT),
                                       "genuine C18 root receipt")))
                need(prefix == root_payload[:len(prefix)],
                     "refuse to remove a stage not matching exact C18 native prefix")
            finally:
                os.close(handle)
            os.unlink(STAGE_NAME, dir_fd=parent)
            os.fsync(parent)
            operations.append("REMOVE AUTHENTICATED JOURNALED C18 PREFIX STAGE")
        _, restored = exact_original_native()
        need(restored == original,
             "require restoration of exact original C inode, bytes and mode")
        return {"schema": SCHEMA + "-native-recovery", "status": "PASS",
                "family": FAMILY, "label": LABEL,
                "journal_sha256": journal_sha256,
                "restored_original": restored,
                "original_inode_restored": True,
                "operations": operations,
                "source_targets_modified": 0,
                "hidden_cases_read": 0, "holdout": "NOT OPENED"}
    finally:
        os.close(parent)


def reject_dynamic_ctypes(tree: ast.AST) -> None:
    for item in ast.walk(tree):
        if isinstance(item, ast.ImportFrom):
            need(not (isinstance(item.module, str)
                      and (item.module == "ctypes"
                           or item.module.startswith("ctypes."))),
                 "reject historical from-ctypes delegation")
        if isinstance(item, ast.Import):
            for alias in item.names:
                if alias.name == "ctypes" or alias.name.startswith("ctypes."):
                    need(item in getattr(tree, "body", ())
                         and len(item.names) == 1 and alias.name == "ctypes"
                         and alias.asname is None,
                         "reject hidden, aliased, or expanded ctypes import")
        if isinstance(item, ast.Call) and item.args:
            first = item.args[0]
            if (isinstance(first, ast.Constant)
                    and isinstance(first.value, str)
                    and (first.value == "ctypes"
                         or first.value.startswith("ctypes."))):
                direct = isinstance(item.func, ast.Name)
                direct = direct and item.func.id == "__import__"
                indirect = (isinstance(item.func, ast.Attribute)
                            and item.func.attr == "import_module")
                need(not (direct or indirect),
                     "reject a dynamic historical ctypes import")


def clean_historical_v4(raw: bytes) -> bytes:
    need(type(raw) is bytes and len(raw) == V4_PRODUCER[2]
         and hashlib.sha256(raw).hexdigest() == V4_PRODUCER[1],
         "authenticate complete immutable V4 source before narrow cleanup")
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=V4_PRODUCER[0])
    reject_dynamic_ctypes(tree)
    nodes = [node for node in tree.body
             if isinstance(node, ast.Import)
             and any(alias.name == "ctypes" for alias in node.names)]
    need(len(nodes) == 1 and nodes[0].lineno == 21
         and nodes[0].end_lineno == 21 and nodes[0].col_offset == 0
         and len(nodes[0].names) == 1
         and nodes[0].names[0].name == "ctypes"
         and nodes[0].names[0].asname is None,
         "replace only exact authenticated top-level historical ctypes line")
    lines = text.splitlines(keepends=True)
    need(len(lines) >= 21 and lines[20] in ("import ctypes\n",
                                            "import ctypes\r\n"),
         "reject a modified historical ctypes line")
    fixed = ("".join(lines[:20]) + PROXY_SOURCE
             + "".join(lines[21:])).encode("utf-8")
    clean = ast.parse(fixed, filename=V4_PRODUCER[0])
    reject_dynamic_ctypes(clean)
    need(not any(isinstance(item, ast.Import)
                 and any(alias.name == "ctypes"
                         or alias.name.startswith("ctypes.")
                         for alias in item.names)
                 for item in ast.walk(clean)),
         "never execute or permit a historical ctypes import")
    return fixed


def patch_v5_loader(producer: types.ModuleType) -> dict:
    original = producer.load_module
    counts = {"historical_v4_source_transforms": 0}

    def guarded_loader(item: tuple, name: str) -> types.ModuleType:
        if item != V4_PRODUCER:
            return original(item, name)
        need(type(name) is str
             and (name.startswith("_rebar_v5_legacy_producer_c_")
                  or name == "_rebar_v5_guarded_nested_legacy_c"),
             "reject an unauthorized historical producer route")
        previous = producer.read_owner

        def guarded_read(owner: tuple, *args: object, **kwargs: object) -> bytes:
            raw = previous(owner, *args, **kwargs)
            if owner == V4_PRODUCER:
                counts["historical_v4_source_transforms"] += 1
                return clean_historical_v4(raw)
            return raw

        producer.read_owner = guarded_read
        try:
            return original(item, name)
        finally:
            producer.read_owner = previous

    producer.load_module = guarded_loader
    return counts


def activate_corrected_family(producer: types.ModuleType) -> tuple[object, dict, dict]:
    original = producer.family_spec(FAMILY)
    need(original.module == "candidates.vm_candidate"
         and original.bridge_module == "candidates._vm_native"
         and original.adapter_relative == ADAPTER[0]
         and original.engine_relative == NATIVE_RELATIVE
         and original.bridge_relative == NATIVE_RELATIVE
         and original.combined_native is True
         and original.owned_ctypes is False,
         "preserve the exact immutable first-party C public/bridge contract")
    owners = ((ADAPTER[0], ADAPTER[1], ADAPTER[2]),
              (CORRECTED_SOURCE[0], CORRECTED_SOURCE[1], CORRECTED_SOURCE[2]))
    corrected = producer.FamilySpec(
        original.name, original.module, original.adapter_relative,
        original.bridge_module, original.engine_relative,
        original.bridge_relative, owners,
        original.combined_native, original.owned_ctypes)
    producer.OWNED_SOURCES[FAMILY] = owners
    producer.FAMILIES[FAMILY] = corrected
    pins = {"source": ADAPTER[1], "native_engine": NATIVE_SHA256,
            "native_bridge": NATIVE_SHA256}
    source_pins = {relative: digest for relative, digest, _ in owners}
    need(producer.family_spec(FAMILY) is corrected
         and source_pins[ADAPTER[0]] == ADAPTER[1]
         and source_pins[CORRECTED_SOURCE[0]] == CORRECTED_SOURCE[1],
         "apply only an authenticated corrected-source in-memory C family overlay")
    return corrected, pins, source_pins


def native_guard_owner(role: str, inode: int) -> dict:
    return {"family": FAMILY, "role": role, "relative": NATIVE_RELATIVE,
            "absolute_path": ROOT + "/" + NATIVE_RELATIVE,
            "sha256": NATIVE_SHA256, "bytes": NATIVE_BYTES,
            "device": DEVICE, "inode": inode,
            "mode": 0o600, "nlink": 1}


def install_worker_guard(state: dict, inode: int) -> tuple[object, object]:
    clean_runtime()
    guard = types.ModuleType("_rebar_owned_actual_c_v6_runtime_guard_v2")
    guard.__file__ = ROOT + "/tools/verify_owned_candidate_runtime_independence_v2.py"
    guard.__package__ = ""
    exec(compile(state["guard_raw"], guard.__file__, "exec",
                 dont_inherit=True), guard.__dict__)
    need(guard.SELF == "tools/verify_owned_candidate_runtime_independence_v2.py"
         and guard.PROTOCOL
         == "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md"
         and guard.CONTRACT
         == "oracle/phase2/candidate-runtime-independence-v2.json",
         "install only the complete independently authenticated strict V2 guard")
    policy = guard.RuntimePolicy()
    policy.install()
    policy.prepare_family(FAMILY,
                          bridge_owner=native_guard_owner("bridge", inode),
                          engine_owner=native_guard_owner("engine", inode))
    if not sys.path or sys.path[0] != ROOT:
        sys.path.insert(0, ROOT)
    selected = __import__("candidates.vm_candidate", fromlist=["__name__"])
    policy.bind_selected(selected, FAMILY)
    bridge = sys.modules.get("candidates._vm_native")
    need(policy.installed and sys.modules.get("re") is selected
         and type(bridge) is types.ModuleType
         and os.path.abspath(bridge.__file__) == ROOT + "/" + NATIVE_RELATIVE
         and "_sre" not in sys.modules and "ctypes" not in sys.modules,
         "bind one actual first-party C18 matcher after physical guard installation")
    policy.check_modules()
    return policy, selected


def actual_worker(parsed: dict, producer: types.ModuleType, state: dict) -> dict:
    journal, journal_owner = read_private(
        JOURNAL_NAME, parsed["--recovery-journal-sha256"], producer)
    need(journal.get("schema")
         == SCHEMA + "-durable-original-native-recovery-journal"
         and journal.get("family") == FAMILY
         and journal.get("label") == LABEL
         and journal.get("build_receipt_sha256") == BUILD_RECEIPT[1]
         and journal.get("root_receipt_sha256") == ROOT_RECEIPT[1]
         and journal.get("phase_native_sha256") == NATIVE_SHA256,
         "require exact C18 build-root-bound original-native recovery journal")
    inode = int(parsed["--activation-inode"])
    policy, selected = install_worker_guard(state, inode)
    corrected, pins, source_pins = activate_corrected_family(producer)
    transform = patch_v5_loader(producer)
    suite = producer.suite_spec(parsed["--suite"])
    need((suite.name, suite.case_count)
         == (parsed["--suite"], dict(SUITES)[parsed["--suite"]]),
         "require one whole frozen original C18 observation")
    try:
        if suite.name == "original_bounded_v5":
            observed = producer.observe_original_upstream(
                suite, corrected, pins, source_pins)
        elif suite.name == "subinterpreter_v2":
            observed = producer.observe_subinterpreters(
                suite, corrected, pins, source_pins,
                producer_sha256=actual_authority()["producer_source_sha256"])
        else:
            observed = producer.observe_direct_suite(
                suite, corrected, pins, source_pins, state["manifest"])
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        details = getattr(error, "details", None)
        policy.check_modules()
        return {"schema": SCHEMA + "-actual-original-worker",
                "status": "FAIL",
                "failure_class": "CANDIDATE EXECUTION FAILURE",
                "candidate_family": FAMILY, "label": LABEL,
                "suite": suite.name,
                "case_execution_denominator": suite.case_count,
                "mismatch_count": "NOT MEASURED",
                "error_type": type(error).__qualname__,
                "error_message": str(error),
                "complete_genuine_failure_details": details,
                "actual_candidate_workers": 1,
                "runtime_guard_installed_before_candidate_import": True,
                "historical_v4_source_transforms":
                    transform["historical_v4_source_transforms"],
                "recovery_journal_sha256": journal_owner["sha256"],
                "native_engine_sha256": NATIVE_SHA256,
                "native_bridge_sha256": NATIVE_SHA256,
                "corrected_source_sha256": CORRECTED_SOURCE[1],
                "unchanged_adapter_sha256": ADAPTER[1],
                "original_source_targets_modified": 0,
                "hidden_cases_read": 0, "benchmark_files_read": 0,
                "clock_samples": 0, "timing_trials_run": 0,
                "performance": "NOT MEASURED",
                "holdout": "NOT OPENED", "candidate_qualified": False,
                "winner_selected": False}
    policy.check_modules()
    need(sys.modules.get("re") is selected and "_sre" not in sys.modules
         and "ctypes" not in sys.modules
         and type(observed) is dict and observed.get("suite") == suite.name
         and observed.get("case_execution_denominator") == suite.case_count
         and observed.get("actual_candidate_workers") == 1,
         "preserve the complete authentic guarded original candidate observation")
    mismatch = observed.get("mismatch_count")
    need(type(mismatch) is int and mismatch >= 0
         and (observed.get("status") == "PASS") == (mismatch == 0),
         "classify every real original mismatch without suppressing failures")
    need(transform["historical_v4_source_transforms"]
         == (0 if suite.name == "original_bounded_v5" else 1),
         "execute exactly one source-authenticated V4 observer cleanup")
    return {"schema": SCHEMA + "-actual-original-worker",
            "status": "PASS" if mismatch == 0 else "FAIL",
            "failure_class": "PASS" if mismatch == 0 else "SEMANTIC MISMATCH",
            "candidate_family": FAMILY, "label": LABEL,
            "suite": suite.name,
            "case_execution_denominator": suite.case_count,
            "mismatch_count": mismatch,
            "all_original_records_and_mismatches_preserved": True,
            "actual_candidate_workers": 1,
            "original_observer_source_sha256":
                actual_authority()["producer_source_sha256"],
            "original_reference_manifest_sha256": V1_MANIFEST[1],
            "actual_c18_build_receipt_sha256": BUILD_RECEIPT[1],
            "actual_c18_root_receipt_sha256": ROOT_RECEIPT[1],
            "runtime_guard_installed_before_candidate_import": True,
            "runtime_guard_source_sha256": actual_authority()["guard_source_sha256"],
            "native_engine_sha256": NATIVE_SHA256,
            "native_bridge_sha256": NATIVE_SHA256,
            "corrected_source_sha256": CORRECTED_SOURCE[1],
            "unchanged_adapter_sha256": ADAPTER[1],
            "corrected_source_family_overlay_in_memory_only": True,
            "historical_v4_source_transforms":
                transform["historical_v4_source_transforms"],
            "recovery_journal_sha256": journal_owner["sha256"],
            "original_observation": observed,
            "original_source_targets_modified": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
            "candidate_qualified": False, "winner_selected": False}


def worker_arguments(parsed: dict, suite: str, active: dict) -> list:
    args = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SOURCE,
            "--worker", "--source-sha256", parsed["--source-sha256"],
            "--protocol-sha256", parsed["--protocol-sha256"],
            "--contract-sha256", parsed["--contract-sha256"],
            "--suite", suite,
            "--activation-inode", str(active["native_inode"]),
            "--recovery-journal-sha256", active["journal"]["sha256"]]
    for key, value in actual_authority().items():
        args.extend(("--" + key.replace("_", "-"), value))
    return args


def encoded_stream(raw: bytes) -> dict:
    base64 = __import__("base64")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def execute_worker(parsed: dict, producer: types.ModuleType,
                   active: dict, name: str, count: int) -> dict:
    subprocess = __import__("subprocess")
    environment = dict(os.environ)
    environment["LOCPATH"] = LOCALE_ROOT
    environment["LC_ALL"] = "C"
    argv = worker_arguments(parsed, name, active)
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=environment, cwd=ROOT)
    process_id = child.pid
    need(type(process_id) is int and process_id > 0,
         "require a real operating-system original candidate worker")
    try:
        output, errors = child.communicate(timeout=WORKER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        child.kill()
        output, errors = child.communicate()
        return {"schema": SCHEMA + "-bounded-worker-result",
                "status": "FAIL", "failure_class": "WORKER TIMEOUT",
                "suite": name, "case_execution_denominator": count,
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "worker_terminated": True,
                "worker_process_id": process_id,
                "returncode": child.returncode,
                "stdout": encoded_stream(output[:MAX_WORKER_STDOUT]),
                "stderr": encoded_stream(errors[:MAX_WORKER_STDERR]),
                "stdout_truncated": len(output) > MAX_WORKER_STDOUT,
                "stderr_truncated": len(errors) > MAX_WORKER_STDERR,
                "mismatch_count": "NOT MEASURED",
                "actual_candidate_workers": 1,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
    except Exception as error:
        try:
            if child.poll() is None:
                child.kill()
            output, errors = child.communicate()
        except Exception as cleanup:
            output = b""
            errors = (type(cleanup).__qualname__ + ": " + str(cleanup)).encode(
                "utf-8", "backslashreplace")
        return {"schema": SCHEMA + "-bounded-worker-result",
                "status": "FAIL", "failure_class": "WORKER INFRASTRUCTURE FAILURE",
                "suite": name, "case_execution_denominator": count,
                "worker_process_id": process_id,
                "returncode": child.returncode,
                "error_type": type(error).__qualname__,
                "error_message": str(error),
                "stdout": encoded_stream(output[:MAX_WORKER_STDOUT]),
                "stderr": encoded_stream(errors[:MAX_WORKER_STDERR]),
                "stdout_truncated": len(output) > MAX_WORKER_STDOUT,
                "stderr_truncated": len(errors) > MAX_WORKER_STDERR,
                "mismatch_count": "NOT MEASURED",
                "actual_candidate_workers": 1,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
    if len(output) > MAX_WORKER_STDOUT or len(errors) > MAX_WORKER_STDERR:
        return {"schema": SCHEMA + "-bounded-worker-result",
                "status": "FAIL", "failure_class": "WORKER OUTPUT LIMIT",
                "suite": name, "case_execution_denominator": count,
                "worker_process_id": process_id,
                "returncode": child.returncode,
                "stdout": encoded_stream(output[:MAX_WORKER_STDOUT]),
                "stderr": encoded_stream(errors[:MAX_WORKER_STDERR]),
                "stdout_truncated": len(output) > MAX_WORKER_STDOUT,
                "stderr_truncated": len(errors) > MAX_WORKER_STDERR,
                "mismatch_count": "NOT MEASURED",
                "actual_candidate_workers": 1,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
    try:
        document = parse_document(producer, output,
                                  "complete guarded original C18 worker " + name)
        need(document.get("schema") == SCHEMA + "-actual-original-worker"
             and document.get("status") in ("PASS", "FAIL")
             and child.returncode
             == (0 if document.get("status") == "PASS" else 1)
             and document.get("suite") == name
             and document.get("case_execution_denominator") == count
             and document.get("actual_candidate_workers") == 1,
             "reject incomplete or forged original candidate worker " + name)
    except Exception as error:
        return {"schema": SCHEMA + "-bounded-worker-result",
                "status": "FAIL", "failure_class": "WORKER INFRASTRUCTURE FAILURE",
                "suite": name, "case_execution_denominator": count,
                "worker_process_id": process_id,
                "returncode": child.returncode,
                "error_type": type(error).__qualname__,
                "error_message": str(error),
                "stdout": encoded_stream(output),
                "stderr": encoded_stream(errors),
                "mismatch_count": "NOT MEASURED",
                "actual_candidate_workers": 1,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED"}
    document["worker_process_id"] = process_id
    document["worker_process_returncode"] = child.returncode
    document["complete_worker_stdout"] = encoded_stream(output)
    document["complete_worker_stderr"] = encoded_stream(errors)
    document["worker_timeout_seconds"] = WORKER_TIMEOUT_SECONDS
    return document


def publish_evidence(document: dict, producer: types.ModuleType) -> dict:
    gzip = __import__("gzip")
    raw = producer.canonical(document)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    suffix = "results" if document["candidate_status"] == "PASS" else "failures"
    stem = "repaired-c-original-campaign-v6-c-" + LABEL + "-" + suffix
    evidence = ROOT + "/oracle/phase2/evidence"

    def publish(name: str, payload: bytes) -> dict:
        parent = directory(evidence, device=DEVICE)
        handle = None
        try:
            handle = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0),
                             0o600, dir_fd=parent)
            before = os.fstat(handle)
            need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                 and before.st_uid == os.geteuid()
                 and before.st_nlink == 1
                 and stat.S_IMODE(before.st_mode) == 0o600,
                 "publish only a new first-party exclusive correctness owner")
            write_all(handle, payload)
            os.fsync(handle)
            after = os.fstat(handle)
            need((before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
                 and after.st_size == len(payload),
                 "reject incomplete original correctness publication")
            os.close(handle)
            handle = None
            os.fsync(parent)
            return {"path": "oracle/phase2/evidence/" + name,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "bytes": len(payload), "device": after.st_dev,
                    "inode": after.st_ino, "mode": "0600", "nlink": 1,
                    "exclusive_creation": True,
                    "file_fsync_completed": True,
                    "directory_fsync_completed": True}
        finally:
            if handle is not None:
                os.close(handle)
            os.close(parent)

    archive = publish(stem + ".json.gz", compressed)
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "publication_status": "PASS",
        "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
        "version": 6, "family": FAMILY, "label": LABEL,
        "candidate_status": document["candidate_status"],
        "candidate_qualified": document["candidate_qualified"],
        "source_sha256": document["source_sha256"],
        "protocol_sha256": document["protocol_sha256"],
        "contract_sha256": document["contract_sha256"],
        "actual_c18_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": ROOT_RECEIPT[1],
        "corrected_source_sha256": CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": ADAPTER[1],
        "native_engine_sha256": NATIVE_SHA256,
        "native_bridge_sha256": NATIVE_SHA256,
        "suite_count": len(SUITES),
        "attempted_suite_count": document["attempted_suite_count"],
        "completed_suite_count": document["completed_suite_count"],
        "case_execution_denominator": ORIGINAL_CASE_COUNT,
        "actual_candidate_workers": document["actual_candidate_workers"],
        "actual_worker_process_ids": document["actual_worker_process_ids"],
        "actual_worker_process_ids_are_distinct":
            document["actual_worker_process_ids_are_distinct"],
        "semantic_mismatch_count": document["semantic_mismatch_count"],
        "verified_passing_case_count": document["verified_passing_case_count"],
        "infrastructure_failure_count": document["infrastructure_failure_count"],
        "candidate_execution_failure_count":
            document["candidate_execution_failure_count"],
        "worker_timeout_count": document["worker_timeout_count"],
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": SEPARATE_REFERENCE_CASE_COUNT,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "original_source_targets_modified": 0,
        "original_native_inode_restored":
            document["original_native_inode_restored"],
        "archive": archive, "uncompressed_bytes": len(raw),
        "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
        "expanded_holdout_proposed_case_count": EXPANDED_PROPOSED_CASE_COUNT,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    receipt_owner = publish(stem + "-publication-receipt.json",
                            producer.canonical(receipt))
    return {"archive": archive, "receipt": receipt,
            "receipt_owner": receipt_owner}


def run_campaign(parsed: dict, producer: types.ModuleType, state: dict) -> dict:
    active = activate_native(parsed, producer, state)
    original = active["original"]
    journal = active["journal_document"]
    results = []
    recovery = None
    try:
        confirmed, _ = read_private(JOURNAL_NAME,
                                    active["journal"]["sha256"], producer)
        need(confirmed == journal,
             "require the exact durable journal inside the protected recovery scope")
        for index, (name, count) in enumerate(SUITES, start=1):
            os.write(2, producer.canonical({
                "schema": SCHEMA + "-actual-suite-progress",
                "status": "START", "suite": name,
                "suite_index": index, "suite_count": len(SUITES),
                "case_execution_denominator": count,
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "holdout": "NOT OPENED",
                "performance": "NOT MEASURED",
            }))
            try:
                row = execute_worker(parsed, producer, active, name, count)
            except Exception as error:
                row = {"schema": SCHEMA + "-bounded-worker-result",
                       "status": "FAIL",
                       "failure_class": "WORKER INFRASTRUCTURE FAILURE",
                       "suite": name, "case_execution_denominator": count,
                       "error_type": type(error).__qualname__,
                       "error_message": str(error),
                       "mismatch_count": "NOT MEASURED",
                       "actual_candidate_workers": 0,
                       "holdout": "NOT OPENED",
                       "performance": "NOT MEASURED"}
            results.append(row)
            progress = {
                "schema": SCHEMA + "-actual-suite-progress",
                "status": row["status"],
                "suite": name, "suite_index": index,
                "suite_count": len(SUITES),
                "case_execution_denominator": count,
                "failure_class": row.get("failure_class", "PASS"),
                "mismatch_count": row.get("mismatch_count", "NOT MEASURED"),
                "actual_candidate_workers": row["actual_candidate_workers"],
                "worker_process_id": row.get("worker_process_id"),
                "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
                "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            }
            if row.get("error_type") is not None:
                progress["error_type"] = row["error_type"]
                progress["error_message"] = str(row.get("error_message", ""))[:2048]
            os.write(2, producer.canonical(progress))
    finally:
        recovery = restore_native(journal, active["journal"]["sha256"],
                                  producer)
    need(recovery is not None and recovery.get("status") == "PASS"
         and recovery.get("restored_original") == original,
         "restore exact original C native before publishing any actual result")
    infrastructure = [row for row in results
                      if row.get("failure_class") in
                      ("WORKER TIMEOUT", "WORKER OUTPUT LIMIT",
                       "WORKER INFRASTRUCTURE FAILURE")]
    executions = [row for row in results
                  if row.get("failure_class") == "CANDIDATE EXECUTION FAILURE"]
    complete = [row for row in results
                if row.get("failure_class") in ("PASS", "SEMANTIC MISMATCH")]
    process_ids = [row["worker_process_id"] for row in results
                   if row.get("actual_candidate_workers") == 1
                   and type(row.get("worker_process_id")) is int
                   and row["worker_process_id"] > 0]
    distinct_workers = len(process_ids) == len(set(process_ids))
    mismatches = (sum(row["mismatch_count"] for row in complete)
                  if not infrastructure and not executions
                  else "NOT MEASURED")
    verified = sum(row["case_execution_denominator"]
                   for row in complete if row.get("status") == "PASS")
    qualified = (len(results) == len(SUITES) and len(complete) == len(SUITES)
                 and len(process_ids) == len(SUITES) and distinct_workers
                 and mismatches == 0 and not infrastructure and not executions)
    report = {
        "schema": SCHEMA + "-actual-original-campaign",
        "status": "PASS" if qualified else "FAIL",
        "candidate_status": "PASS" if qualified else "FAIL",
        "version": 6, "family": FAMILY, "label": LABEL,
        "source_sha256": parsed["--source-sha256"],
        "protocol_sha256": parsed["--protocol-sha256"],
        "contract_sha256": parsed["--contract-sha256"],
        "actual_c18_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_c18_root_receipt_sha256": ROOT_RECEIPT[1],
        "original_observer_source_sha256":
            actual_authority()["producer_source_sha256"],
        "original_reference_manifest_sha256": V1_MANIFEST[1],
        "runtime_guard_source_sha256": actual_authority()["guard_source_sha256"],
        "runtime_guard_installed_before_candidate_import": True,
        "corrected_source_sha256": CORRECTED_SOURCE[1],
        "unchanged_adapter_sha256": ADAPTER[1],
        "native_engine_sha256": NATIVE_SHA256,
        "native_bridge_sha256": NATIVE_SHA256,
        "suite_count": len(SUITES),
        "attempted_suite_count": len(results),
        "completed_suite_count": len(complete),
        "case_execution_denominator": ORIGINAL_CASE_COUNT,
        "actual_candidate_workers": len(process_ids),
        "actual_worker_process_ids": process_ids,
        "actual_worker_process_ids_are_distinct": distinct_workers,
        "semantic_mismatch_count": mismatches,
        "verified_passing_case_count": verified,
        "infrastructure_failure_count": len(infrastructure),
        "candidate_execution_failure_count": len(executions),
        "worker_timeout_count": sum(
            row.get("failure_class") == "WORKER TIMEOUT" for row in results),
        "worker_timeout_seconds": WORKER_TIMEOUT_SECONDS,
        "suite_results": results,
        "named_private_waiver_count": 13,
        "separate_reference_case_count": SEPARATE_REFERENCE_CASE_COUNT,
        "separate_reference_cases_counted_as_candidate_cases": False,
        "original_source_targets_modified": 0,
        "original_native_inode_restored": True,
        "native_recovery": recovery,
        "expanded_holdout_proposed_case_count": EXPANDED_PROPOSED_CASE_COUNT,
        "candidate_qualified": qualified,
        "runtime_non_delegation": "ESTABLISHED FOR THIS CANDIDATE RUN"
            if qualified else "NOT ESTABLISHED",
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    publication = publish_evidence(report, producer)
    return {"schema": SCHEMA + "-actual-publication",
            "status": "PASS", "publication_status": "PASS",
            "publication_pass_means": "DURABLE CORRECTNESS PUBLICATION ONLY",
            "candidate_status": report["candidate_status"],
            "candidate_qualified": qualified,
            "suite_count": len(SUITES),
            "attempted_suite_count": len(results),
            "completed_suite_count": len(complete),
            "case_execution_denominator": ORIGINAL_CASE_COUNT,
            "actual_candidate_workers": len(process_ids),
            "actual_worker_process_ids": process_ids,
            "actual_worker_process_ids_are_distinct": distinct_workers,
            "semantic_mismatch_count": mismatches,
            "verified_passing_case_count": verified,
            "infrastructure_failure_count": len(infrastructure),
            "candidate_execution_failure_count": len(executions),
            "worker_timeout_count": report["worker_timeout_count"],
            "original_native_inode_restored": True,
            "archive_owner": publication["archive"],
            "receipt_owner": publication["receipt_owner"],
            "holdout": "NOT OPENED", "performance": "NOT MEASURED",
            "winner_selected": False}


def perform_recovery(parsed: dict, producer: types.ModuleType) -> dict:
    journal, _ = read_private(JOURNAL_NAME,
                              parsed["--recovery-journal-sha256"], producer)
    return restore_native(journal, parsed["--recovery-journal-sha256"],
                          producer)


def main(arguments: list[str]) -> int:
    clean_runtime()
    parsed = options(arguments)
    old = bootstrap_previous()
    producer, state, result = collect_context(
        old, parsed, controls=parsed["mode"] == "--self-test")
    mode = parsed["mode"]
    if mode == "--render-contract":
        sys.stdout.buffer.write(producer.canonical(
            contract_document(parsed, old, state)))
        return 0
    if mode == "--self-test":
        result["schema"] = SCHEMA + "-self-test"
        result["hostile_control_count"] = len(result["hostile_controls"])
    elif mode == "--worker":
        result = actual_worker(parsed, producer, state)
    elif mode == "--run":
        result = run_campaign(parsed, producer, state)
    elif mode == "--recover":
        result = perform_recovery(parsed, producer)
    sys.stdout.buffer.write(producer.canonical(result))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CampaignError as error:
        os.write(2, ("C18 original campaign V6: " + str(error) + "\n")
                 .encode("utf-8", "backslashreplace"))
        raise SystemExit(2)
