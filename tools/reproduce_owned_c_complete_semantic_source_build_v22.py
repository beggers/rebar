#!/usr/bin/env python3
"""Freeze and separately authorize two independent first-party C source builds."""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex", "ctypes")):
    raise SystemExit("integrated C22 source build cannot import a regex engine")

import builtins
import hashlib
import os
import stat
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/reproduce_owned_c_complete_semantic_source_build_v22.py"
PROTOCOL = "oracle/phase2/C-COMPLETE-SEMANTIC-SOURCE-BUILD-V22.md"
CONTRACT = "oracle/phase2/c-complete-semantic-source-build-v22.json"
SCHEMA = "rebar-owned-c-complete-semantic-source-build-v22"
VERSION = 22
DEVICE = 2064
FAMILY = "c"
LABEL = "phase2-v22-c-complete-semantic-source-build"
BUILD_AUTHORIZATION = "--authorize-first-party-complete-native-build-v22"
ROOT_PREFIX = "rebar-phase2-c-complete-native-semantics-v22-"
PHASES = ("reference-a", "reference-b")
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
NATIVE_NAME = "_vm_native.cpython-314-x86_64-linux-gnu.so"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_TOOL_BYTES = 64 * 1024 * 1024
MAX_PROCESS_OUTPUT = 4 * 1024 * 1024

NATIVE_FREEZE = (
    ("tools/apply_owned_c_complete_native_semantics_v1.py",
     "378b3941b3038f8af7b9a42199044517973b2c23012c11faa504a645123341f9",
     76523, 430482),
    ("oracle/phase2/C-COMPLETE-NATIVE-SEMANTICS-V1.md",
     "2dcea6c1d7e03f56bc4662e459f97162b9061041052b0f6459138ae5a55f067e",
     10382, 525542),
    ("oracle/phase2/c-complete-native-semantics-v1.json",
     "46f0f7e409bf60c5271bf84819f88b551bcc2b852a88b69f1045bb7f3a656f0e",
     7427, 525548),
)
ADAPTER_FREEZE = (
    ("tools/apply_owned_c_public_adapter_semantics_v2.py",
     "13173033914a706f4d80e76dc8c95ee016a125f7d3261fdf252ed404a60ebb55",
     55674, 429225),
    ("oracle/phase2/C-PUBLIC-ADAPTER-SEMANTICS-V2.md",
     "ad91932c5b60cace2a632d11ff62e80d3890de4e4018e8e9ed7e6a4b466436a2",
     7529, 524903),
    ("oracle/phase2/c-public-adapter-semantics-v2.json",
     "ed5421ca2ab6a99c59945529cd8ae640636bad2ad42806bd7f36c8cf3ef584ce",
     3806, 524904),
)
GUARD_FREEZE = (
    ("tools/verify_owned_candidate_runtime_independence_v4.py",
     "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
     48687, 429243),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
     "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
     4492, 525890),
    ("oracle/phase2/candidate-runtime-independence-v4.json",
     "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
     9352, 525891),
)
C21_FREEZE = (
    ("tools/reproduce_owned_c_original_match_semantics_source_build_v21.py",
     "a1879dfefab15e91bfec95a74c4665d44e9894bef881c4945bccb3121be04726",
     32001, 429061),
    ("oracle/phase2/C-ORIGINAL-MATCH-SEMANTICS-SOURCE-BUILD-V21.md",
     "20844ff1c5a4b4908bc903d1a3c3e31e72c7f397b863741fce528ecd8b20d226",
     7097, 524815),
    ("oracle/phase2/c-original-match-semantics-source-build-v21.json",
     "a32651018f9c60cfa5963768ffd0cb4463e6c691556958dfd3cd3bea0a42a382",
     18982, 524816),
)
NATIVE_APPLICATION = (
    "oracle/phase2/evidence/c-complete-native-semantics-v1-application.json",
    "1ac3c69067e7b76968fe852e35be7d689149d6de90a48c25a254ff9e9f287a9c",
    1746, 525632,
)
ADAPTER_APPLICATION = (
    "oracle/phase2/evidence/c-public-adapter-semantics-v2-application.json",
    "e3e63acfde8f1eef32f81d48bddc613fb386880a5f1974b898e36b211ab55476",
    1459, 525121,
)
C21_BUILD = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-publication-receipt.json",
    "9475dd0c441a0440136f12425f94e6a4244e4cdc52d49f803e891f6663a647df",
    11878, 524817,
)
C21_ROOT = (
    "oracle/phase2/evidence/native-source-build-v21-c-phase2-v21-"
    "c-original-match-semantics-root-provenance-receipt.json",
    "8f913d623bf5bb4aec3669e9b3daa882df16aad6f2f1bc3db1f02f4988a8afa2",
    10837, 524818,
)
C12_FAILURE = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v12-c-phase2-v21-"
    "c-original-match-semantics-original-p0-v12-failures-publication-receipt.json",
    "a3f4b90b8f289df9dfe49f776266e3c290edb2c21c62713137f501a5f997c21b",
    10943, 525645,
)
CORRECTED_NATIVE = (
    "candidates/c/variants/complete_native_semantics_v1/vm_native.c",
    "0654fe3a970760cc3efb08d819c8a4d8abadb152c35f370e662123e4de20e31f",
    221557, 525629,
)
CORRECTED_ADAPTER = (
    "candidates/c/variants/public_adapter_semantics_v2/vm_candidate.py",
    "4a62cb318592600d53e5ed6b9f8b9edf4edf2068fb2453892ca2130bb203410a",
    61663, 525120,
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
INSTALLED_NATIVE = (
    "candidates/" + NATIVE_NAME,
    "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd",
    149976, 430300,
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
PUBLIC_GROUPS = (NATIVE_FREEZE, ADAPTER_FREEZE, GUARD_FREEZE, C21_FREEZE)
RECEIPTS = (NATIVE_APPLICATION, ADAPTER_APPLICATION, C21_BUILD,
            C21_ROOT, C12_FAILURE)
ANSWER_ENCODER = None


class BuildError(Exception):
    """The exact dual first-party source freeze or reproducible build failed."""


def need(condition: object, reason: str) -> None:
    if condition is not True:
        raise BuildError(reason)


def checked_hash(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(character in "0123456789abcdef" for character in value),
         "require complete lowercase SHA-256 authority: " + label)
    return value


def clean_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.executable == PYTHON
         and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True
         and __file__ == ROOT + "/" + SOURCE,
         "require pinned matcher-free CPython 3.14.6 -I -B -S")
    rejected = ("re", "_sre", "regex", "ctypes", "subprocess", "socket",
                "threading", "multiprocessing", "candidates", "rebar")
    need(not any(name == item or name.startswith(item + ".")
                 for name in sys.modules for item in rejected),
         "reject external matcher, candidate, subprocess, or native loader")


def bootstrap_native_controller() -> types.ModuleType:
    owner = NATIVE_FREEZE[0]
    relative, fingerprint, size, inode = owner
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                         | getattr(os, "O_CLOEXEC", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == size
             and before.st_nlink == 1 and before.st_uid == os.geteuid()
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject substituted exact independently frozen C native controller")
        blocks: list[bytes] = []
        left = size
        while left:
            block = os.read(descriptor, min(left, 65536))
            need(type(block) is bytes and bool(block),
                 "reject truncated exact C native controller")
            blocks.append(block)
            left -= len(block)
        need(os.read(descriptor, 1) == b"",
             "reject extra exact C native controller source bytes")
        raw = b"".join(blocks)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns),
             "reject modified or concurrent complete native controller")
    finally:
        os.close(descriptor)
    module = types.ModuleType("_rebar_v22_authenticated_native_source_freeze")
    module.__file__ = ROOT + "/" + relative
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    need(module.SOURCE == relative
         and module.OUTPUT_SHA256 == CORRECTED_NATIVE[1]
         and module.OUTPUT_BYTES == CORRECTED_NATIVE[2]
         and module.ADAPTER_RECEIPT[1] == ADAPTER_APPLICATION[1]
         and module.C21_SHA256
         == "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2",
         "reject substituted exact first-party complete native source controller")
    clean_runtime()
    return module


def evidence_owners() -> tuple[tuple, ...]:
    return NATIVE_FREEZE + ADAPTER_FREEZE + GUARD_FREEZE + C21_FREEZE + RECEIPTS


def owner_record(owner: tuple) -> dict[str, object]:
    return {"path": owner[0], "sha256": owner[1], "bytes": owner[2],
            "inode": owner[3], "device": DEVICE, "mode": "0600", "nlink": 1}


def make_source_wall(native: types.ModuleType) -> object:
    class SourceWall(native.Wall):
        def __init__(self) -> None:
            super().__init__(False)
            self.public = frozenset(
                (SOURCE, PROTOCOL, CONTRACT)
                + tuple(item[0] for item in evidence_owners())
            )
            self.allowed = self.public

    return SourceWall()


def preserve_native_application(native: types.ModuleType,
                               document: object) -> None:
    need(type(document) is dict,
         "require actual exclusively materialized complete C native receipt")
    expected = {
        "schema": "rebar-owned-c-complete-native-semantics-v1-source-freeze-"
                  "root-materialization",
        "status": "PASS",
        "source_sha256": NATIVE_FREEZE[0][1],
        "protocol_sha256": NATIVE_FREEZE[1][1],
        "contract_sha256": NATIVE_FREEZE[2][1],
        "target_path": CORRECTED_NATIVE[0],
        "target_sha256": CORRECTED_NATIVE[1],
        "target_bytes": CORRECTED_NATIVE[2],
        "targeted_native_mismatches": 276,
        "paired_materialized_adapter_mismatches": 330,
        "preserved_c12_observed_mismatch_count": 606,
        "preserved_adapter_application_sha256": ADAPTER_APPLICATION[1],
        "reconstructed_tested_c21_source_sha256": native.C21_SHA256,
        "root_controls_completed_before_candidate_read": True,
    }
    for key, value in expected.items():
        need(document.get(key) == value,
             "preserve exact genuine complete-native materialization: " + key)
    effects = document.get("effects")
    need(type(effects) is dict
         and effects.get("candidate_source_files_read") == 1
         and effects.get("candidate_executions") == 0
         and effects.get("workspace_mutations") == 2,
         "preserve actual corrected native publication and source-only boundaries")


def preserve_native_contract(native: types.ModuleType,
                             document: object) -> None:
    need(type(document) is dict
         and document.get("schema") == native.SCHEMA
         and document.get("source", {}).get("sha256") == NATIVE_FREEZE[0][1]
         and document.get("protocol", {}).get("sha256") == NATIVE_FREEZE[1][1],
         "preserve exact authenticated cumulative C native semantics")
    corrections = document.get("cumulative_native_corrections")
    need(type(corrections) is dict
         and corrections.get("target_sha256") == CORRECTED_NATIVE[1]
         and corrections.get("target_bytes") == CORRECTED_NATIVE[2]
         and corrections.get("native_total_observed_mismatches_targeted") == 276
         and corrections.get("adapter_total_observed_mismatches_targeted") == 330
         and corrections.get("all_observed_mismatches_preserved") == 606
         and corrections.get("exact_reversible_source_site_count") == 7
         and corrections.get("stdlib_regex_delegation") is False
         and corrections.get("external_regex_engine") is False
         and corrections.get("cross_candidate_engine") is False,
         "reject dropped native correction or unowned external regex delegation")


def preserve_c21_contract(native: types.ModuleType,
                          document: object) -> None:
    need(type(document) is dict
         and document.get("schema")
         == "rebar-owned-c-original-match-semantics-source-build-v21-source-freeze"
         and document.get("version") == 21
         and document.get("source", {}).get("sha256") == C21_FREEZE[0][1]
         and document.get("protocol", {}).get("sha256") == C21_FREEZE[1][1]
         and document.get("candidate_correctness") == "NOT MEASURED",
         "preserve actual pushed C21 dual-build controller and all historical pins")
    c19 = document.get("actual_c19_preactivation_failure")
    c20 = document.get("actual_c20_portable_randomness_failure")
    correction = document.get("portable_first_party_entropy_correction")
    policy = document.get("future_actual_build_policy")
    need(type(c19) is dict and c19.get("status") == "FAIL"
         and type(c20) is dict and c20.get("status") == "FAIL"
         and c20.get("failed_private_root_call") == "os.getrandom(16)"
         and c20.get("unreached_journal_call") == "os.getrandom(12)"
         and type(correction) is dict
         and correction.get("fixed_private_root_call") == "os.urandom(16)"
         and correction.get("fixed_private_journal_call") == "os.urandom(12)"
         and type(policy) is dict and policy.get("phase_count") == 2
         and policy.get("expected_compiler_process_count") == 14,
         "preserve every actual failed historical C build and portable-entropy fix")
    owners = policy.get("toolchain_owners")
    need(type(owners) is list and len(owners) == 5,
         "preserve all five immutable historical native-build toolchains")
    for actual, expected in zip(owners, TOOLCHAINS, strict=True):
        need(actual.get("role") == expected[0]
             and actual.get("path") == expected[1]
             and actual.get("sha256") == expected[2]
             and actual.get("bytes") == expected[3],
             "preserve all first-party pinned C compiler/header tooling")


def validate_evidence(native: types.ModuleType,
                      raw: dict[str, bytes]) -> None:
    parse = lambda item: native.JSON(raw[item]).parse()
    native_contract = parse(NATIVE_FREEZE[2][0])
    adapter_contract = parse(ADAPTER_FREEZE[2][0])
    guard_contract = parse(GUARD_FREEZE[2][0])
    c21_contract = parse(C21_FREEZE[2][0])
    native_application = parse(NATIVE_APPLICATION[0])
    adapter_application = parse(ADAPTER_APPLICATION[0])
    build = parse(C21_BUILD[0])
    root = parse(C21_ROOT[0])
    failure = parse(C12_FAILURE[0])
    preserve_native_contract(native, native_contract)
    preserve_native_application(native, native_application)
    native.preserve_adapter(adapter_contract, adapter_application)
    native.preserve_guard(guard_contract)
    native.preserve_c12(failure)
    native.preserve_c21(build, root)
    preserve_c21_contract(native, c21_contract)


def synthetic_plan() -> dict[str, object]:
    return {
        "phase_names": list(PHASES),
        "process_roles": list(PROCESS_ROLES),
        "phase_count": 2,
        "process_count_per_phase": 7,
        "total_process_count": 14,
        "distinct_source_owners": 4,
        "distinct_native_artifacts": 2,
        "native_source_sha256": CORRECTED_NATIVE[1],
        "native_source_bytes": CORRECTED_NATIVE[2],
        "adapter_source_sha256": CORRECTED_ADAPTER[1],
        "adapter_source_bytes": CORRECTED_ADAPTER[2],
        "installed_original_sha256": INSTALLED_NATIVE[1],
        "installed_original_bytes": INSTALLED_NATIVE[2],
        "installed_original_inode": INSTALLED_NATIVE[3],
        "existing_candidate_sources_modified": 0,
        "source_gate_candidate_reads": 0,
        "source_gate_builds": 0,
        "private_root_prefix": ROOT_PREFIX,
        "native_extension_name": NATIVE_NAME,
        "portable_root_entropy": "os.urandom(16)",
        "portable_journal_entropy": "os.urandom(12)",
        "file_prefix_map_destination": "/rebar/c-complete-v22",
        "candidate_correctness": "NOT MEASURED",
        "native_artifact_sha256": "NOT MEASURED",
        "native_artifact_bytes": "NOT MEASURED",
    }


def validate_plan(plan: object) -> None:
    need(type(plan) is dict and plan == synthetic_plan(),
         "reject weakened, delegated, historical-source, or fabricated dual build")


def source_controls(native: types.ModuleType, wall: object) -> dict[str, object]:
    native_checks = native.hostile_controls(wall)
    count = 0

    def refuses(action: object, label: str) -> None:
        nonlocal count
        rejected = False
        try:
            action()
        except (BuildError, native.FreezeError, TypeError, ValueError, OSError):
            rejected = True
        need(rejected, "accept forbidden integrated C build control: " + label)
        count += 1

    actual = synthetic_plan()
    validate_plan(actual)
    count += 1
    for key, replacement in (
        ("phase_count", 1), ("process_count_per_phase", 6),
        ("total_process_count", 13), ("distinct_source_owners", 3),
        ("distinct_native_artifacts", 1),
        ("native_source_sha256", "0" * 64),
        ("native_source_bytes", 221647),
        ("adapter_source_sha256", CANONICAL_ADAPTER[1]),
        ("adapter_source_bytes", 60707),
        ("installed_original_sha256", "0" * 64),
        ("installed_original_inode", INSTALLED_NATIVE[3] + 1),
        ("existing_candidate_sources_modified", 1),
        ("source_gate_candidate_reads", 1),
        ("source_gate_builds", 1),
        ("private_root_prefix", "rebar-phase2-c-original-match-semantics-v21-"),
        ("native_extension_name", "regex.so"),
        ("portable_root_entropy", "os.getrandom(16)"),
        ("portable_journal_entropy", "os.getrandom(12)"),
        ("file_prefix_map_destination", "/rebar/c-match-v21"),
        ("candidate_correctness", "PASS"),
        ("native_artifact_sha256", "0" * 64),
        ("native_artifact_bytes", 163504),
    ):
        changed = dict(actual)
        changed[key] = replacement
        refuses(lambda value=changed: validate_plan(value),
                "forged actual-build model: " + key)
    for index, role in enumerate(PROCESS_ROLES):
        roles = list(PROCESS_ROLES)
        roles[index] = "subprocess." + role
        changed = dict(actual, process_roles=roles)
        refuses(lambda value=changed: validate_plan(value),
                "substituted direct compiler role " + role)
    for target in (CORRECTED_NATIVE[0], CORRECTED_ADAPTER[0],
                   CANONICAL_C[0], CANONICAL_ADAPTER[0], INSTALLED_NATIVE[0]):
        refuses(lambda path=target: builtins.open(ROOT + "/" + path, "rb"),
                "physically deny source-only candidate/native owner")
    refuses(lambda: os.urandom(12), "physically deny private journal entropy")
    refuses(lambda: os.urandom(16), "physically deny private build-root entropy")
    refuses(lambda: os.posix_spawn("/usr/bin/x86_64-linux-gnu-gcc-13",
                                   ("gcc", "--version"), {}),
            "physically deny actual compiler in source-only mode")
    native.no_matchers()
    need(count >= 37 and native_checks["hostile_controls"] >= 337,
         "require complete first-party semantics and dual-build hostile controls")
    return {"hostile_controls": native_checks["hostile_controls"] + count,
            "integrated_build_controls": count,
            "inherited_native_semantic_controls":
                native_checks["semantic"]["semantic_checks"],
            "candidate_source_files_read": 0,
            "compiler_processes": 0,
            "private_roots_created": 0,
            "actual_candidate_executions": 0}


class BuildPolicy:
    """Default-deny audit tickets for an explicitly authorized two-phase build."""

    def __init__(self, native: types.ModuleType) -> None:
        self.native = native
        self.open_ticket: tuple[str, int] | None = None
        self.mkdir_ticket: tuple[str, int, int | None] | None = None
        self.replace_ticket: tuple[str, str, int, int] | None = None
        self.spawn_ticket: tuple[str, tuple[str, ...]] | None = None
        self.kill_ticket: int | None = None
        self.native_open = os.open
        self.native_read = os.read
        self.native_write = os.write
        self.native_close = os.close
        self.native_fstat = os.fstat
        self.native_fsync = os.fsync
        self.native_mkdir = os.mkdir
        self.native_replace = os.replace
        self.native_urandom = os.urandom
        self.native_posix_spawn = os.posix_spawn
        self.native_pipe2 = getattr(os, "pipe2", None)
        self.native_pipe = os.pipe
        self.native_waitpid = os.waitpid
        self.native_kill = os.kill
        self.source_reads = 0
        self.candidate_source_reads = 0
        self.toolchain_reads = 0
        self.process_count = 0
        self.random_calls = 0
        self.private_roots_created = 0
        self.workspace_receipts_created = 0
        self.native_libraries_loaded = 0
        self.installed = False

    def reject(self, reason: str) -> None:
        raise BuildError("first-party V22 actual-build wall rejected " + reason)

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            flags = args[2] if len(args) > 2 else None
            if self.open_ticket == (path, flags):
                return
            self.reject("unticketed candidate, source, evidence, or build artifact")
        if event == "os.mkdir":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            parent = args[2] if len(args) > 2 else None
            if self.mkdir_ticket == (path, mode, parent):
                return
            self.reject("unticketed actual private root or phase directory")
        if event == "os.rename":
            source = args[0] if args else None
            target = args[1] if len(args) > 1 else None
            source_fd = args[2] if len(args) > 2 else None
            target_fd = args[3] if len(args) > 3 else None
            if self.replace_ticket == (source, target, source_fd, target_fd):
                return
            self.reject("unticketed private recovery-journal replacement")
        if event == "os.posix_spawn":
            executable = args[0] if args else None
            if self.spawn_ticket is not None and self.spawn_ticket[0] == executable:
                return
            self.reject("shell, subprocess, package, or unauthorized compiler")
        if event == "os.kill":
            pid = args[0] if args else None
            if self.kill_ticket == pid:
                return
            self.reject("unowned external process signal")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.remove", "os.unlink", "os.rmdir", "os.chmod",
                      "os.chown", "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.",
                                     "os.exec", "os.spawn"))):
            self.reject("candidate execution, dynamic code, network, or deletion")

    def install(self) -> None:
        need(not self.installed,
             "install independently authenticated V22 actual-build wall once")
        sys.addaudithook(self.audit)
        time_module = self.native.time
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time_module, name):
                setattr(time_module, name,
                        lambda *_args, **_kwargs: self.reject("actual build clock"))
        self.installed = True

    def open(self, path: str, flags: int, mode: int = 0,
             *, parent: int | None = None) -> int:
        need(self.installed and self.open_ticket is None,
             "reject nested or unaudited actual-build source descriptor")
        self.open_ticket = (path, flags)
        try:
            if parent is None:
                return self.native_open(path, flags, mode)
            return self.native_open(path, flags, mode, dir_fd=parent)
        finally:
            self.open_ticket = None

    def mkdir(self, path: str, mode: int, *, parent: int | None = None) -> None:
        need(self.installed and self.mkdir_ticket is None and mode == 0o700,
             "permit only one owner-private 0700 C build directory")
        self.mkdir_ticket = (path, mode, parent if parent is not None else -1)
        try:
            if parent is None:
                self.native_mkdir(path, mode)
            else:
                self.native_mkdir(path, mode, dir_fd=parent)
        finally:
            self.mkdir_ticket = None

    def replace(self, source: str, target: str, parent: int) -> None:
        need(self.installed and self.replace_ticket is None
             and source.startswith(".rebar-c-complete-v22-journal-")
             and target == "native-build-recovery-journal-v22.json",
             "replace only one authenticated owner-private recovery journal")
        self.replace_ticket = (source, target, parent, parent)
        try:
            self.native_replace(source, target,
                                src_dir_fd=parent, dst_dir_fd=parent)
        finally:
            self.replace_ticket = None

    def randomness(self, count: int) -> bytes:
        need(type(count) is int and count in (12, 16),
             "require portable OS entropy only for actual V22 root/journal")
        value = self.native_urandom(count)
        need(type(value) is bytes and len(value) == count,
             "reject unavailable, deterministic, or partial OS entropy")
        self.random_calls += 1
        return value

    def spawn(self, role: str, command: tuple[str, ...],
              phase: str, executable: str, used: set[int]) -> tuple[dict, bytes]:
        need(role in PROCESS_ROLES and type(command) is tuple
             and len(command) > 1 and command[0] == executable
             and executable in (TOOLCHAINS[0][1], TOOLCHAINS[4][1])
             and phase in PHASES and self.spawn_ticket is None,
             "reject shell, external matcher, or unowned process role")
        if self.native_pipe2 is not None:
            reader, writer = self.native_pipe2(getattr(os, "O_CLOEXEC", 0))
        else:
            reader, writer = self.native_pipe()
        try:
            actions = (
                (os.POSIX_SPAWN_DUP2, writer, 1),
                (os.POSIX_SPAWN_DUP2, writer, 2),
                (os.POSIX_SPAWN_CLOSE, reader),
                (os.POSIX_SPAWN_CLOSE, writer),
            )
            environment = {"LC_ALL": "C", "LANG": "C", "TZ": "UTC",
                           "SOURCE_DATE_EPOCH": "0", "PATH": "/usr/bin:/bin"}
            self.spawn_ticket = (executable, command)
            try:
                pid = self.native_posix_spawn(executable, command, environment,
                                             file_actions=actions)
            finally:
                self.spawn_ticket = None
        except BaseException:
            self.native_close(reader)
            self.native_close(writer)
            raise
        self.native_close(writer)
        blocks: list[bytes] = []
        size = 0
        try:
            while True:
                chunk = self.native_read(reader, 65536)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_PROCESS_OUTPUT:
                    self.kill_ticket = pid
                    try:
                        self.native_kill(pid, 9)
                    finally:
                        self.kill_ticket = None
                    self.native_waitpid(pid, 0)
                    raise BuildError("reject oversized first-party compiler output")
                blocks.append(chunk)
        finally:
            self.native_close(reader)
        observed, status = self.native_waitpid(pid, 0)
        need(observed == pid and type(pid) is int and pid > 0
             and pid not in used and os.WIFEXITED(status)
             and os.WEXITSTATUS(status) == 0,
             "reject failed, incomplete, reused, or invented actual tool process")
        used.add(pid)
        self.process_count += 1
        output = b"".join(blocks)
        record = {"phase": phase, "role": role, "pid": pid, "exit_status": 0,
                  "output_sha256": hashlib.sha256(output).hexdigest(),
                  "output_bytes": len(output), "command": list(command)}
        return record, output


def read_build_owner(policy: BuildPolicy, owner: tuple,
                     *, capture: bool = False,
                     expected_mode: int = 0o600) -> tuple[dict, bytes | None]:
    relative, fingerprint, size, inode = owner
    need(type(relative) is str and not relative.startswith("/")
         and ".." not in relative.split("/")
         and not relative.endswith((".gz", ".zip", ".tar", ".xz")),
         "reject private, compressed, traversal, or final-test build owner")
    checked_hash(fingerprint, relative)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = policy.open(ROOT + "/" + relative, flags)
    try:
        before = policy.native_fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == size
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == expected_mode,
             "reject substituted actual first-party build owner: " + relative)
        blocks: list[bytes] = []
        fingerprint_state = hashlib.sha256()
        remaining = size
        while remaining:
            block = policy.native_read(descriptor, min(remaining, 262144))
            need(type(block) is bytes and bool(block),
                 "reject incomplete actual first-party build owner")
            fingerprint_state.update(block)
            if capture:
                blocks.append(block)
            remaining -= len(block)
        need(policy.native_read(descriptor, 1) == b""
             and fingerprint_state.hexdigest() == fingerprint,
             "reject replaced actual first-party build owner")
        after = policy.native_fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject actual first-party source changed during authentication")
        record = {"path": relative, "sha256": fingerprint, "bytes": size,
                  "device": before.st_dev, "inode": before.st_ino,
                  "mode": format(stat.S_IMODE(before.st_mode), "04o"),
                  "nlink": before.st_nlink}
        return record, b"".join(blocks) if capture else None
    finally:
        policy.native_close(descriptor)


def authenticate_toolchains(policy: BuildPolicy,
                            historical: dict) -> list[dict]:
    expected = historical.get("authenticated_toolchain_owners")
    need(type(expected) is list and len(expected) == 5,
         "require all five actually authenticated earlier compiler owners")
    observed: list[dict] = []
    for role, path, fingerprint, size, version, executable in TOOLCHAINS:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = policy.open(path, flags)
        try:
            before = policy.native_fstat(descriptor)
            need(stat.S_ISREG(before.st_mode)
                 and before.st_size == size and 0 < size <= MAX_TOOL_BYTES
                 and bool(before.st_mode & 0o111) is executable,
                 "reject unsafe pinned C compiler/header owner: " + role)
            state = hashlib.sha256()
            remaining = size
            while remaining:
                block = policy.native_read(descriptor, min(remaining, 262144))
                need(bool(block), "reject truncated authenticated tool: " + role)
                state.update(block)
                remaining -= len(block)
            need(policy.native_read(descriptor, 1) == b""
                 and state.hexdigest() == fingerprint,
                 "reject replaced full compiler/header owner: " + role)
            after = policy.native_fstat(descriptor)
            need((before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
                 == (after.st_dev, after.st_ino, after.st_size,
                     after.st_mtime_ns, after.st_ctime_ns),
                 "reject concurrent compiler/header modification: " + role)
            actual = {"role": role, "path": path, "sha256": fingerprint,
                      "bytes": size, "device": before.st_dev,
                      "inode": before.st_ino, "version": version,
                      "executable": executable}
            policy.toolchain_reads += 1
            observed.append(actual)
        finally:
            policy.native_close(descriptor)
    need(observed == expected,
         "authenticate the exact five prior genuinely published toolchain owners")
    return observed


def write_all(policy: BuildPolicy, descriptor: int, payload: bytes) -> None:
    position = 0
    while position < len(payload):
        count = policy.native_write(descriptor, payload[position:position + 262144])
        need(type(count) is int and count > 0,
             "reject incomplete durable first-party actual-build write")
        position += count


def write_exclusive(policy: BuildPolicy, parent: int, name: str,
                    payload: bytes) -> dict:
    need(type(name) is str and bool(name) and "/" not in name
         and name not in (".", "..") and type(payload) is bytes
         and 0 < len(payload) <= MAX_SOURCE_BYTES,
         "reject unsafe exclusive source, journal, or evidence publication")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    descriptor = policy.open(name, flags, 0o600, parent=parent)
    try:
        write_all(policy, descriptor, payload)
        policy.native_fsync(descriptor)
        info = policy.native_fstat(descriptor)
        need(stat.S_ISREG(info.st_mode) and info.st_uid == os.geteuid()
             and info.st_nlink == 1 and info.st_size == len(payload)
             and stat.S_IMODE(info.st_mode) == 0o600,
             "reject substituted owner-private exclusive first-party artifact")
    finally:
        policy.native_close(descriptor)
    policy.native_fsync(parent)
    return {"name": name, "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": info.st_size, "device": info.st_dev,
            "inode": info.st_ino, "mode": "0600", "nlink": info.st_nlink,
            "exclusive_creation": True, "file_fsync_completed": True,
            "directory_fsync_completed": True}


def canonical_payload(native: types.ModuleType, value: object) -> bytes:
    return (native.canonical(value) + "\n").encode("utf-8")


def write_journal(policy: BuildPolicy, native: types.ModuleType,
                  directory: int, journal: dict) -> dict:
    payload = canonical_payload(native, journal)
    temporary = ".rebar-c-complete-v22-journal-" + policy.randomness(12).hex()
    record = write_exclusive(policy, directory, temporary, payload)
    policy.replace(temporary, "native-build-recovery-journal-v22.json", directory)
    policy.native_fsync(directory)
    record["name"] = "native-build-recovery-journal-v22.json"
    record["atomic_replacement"] = True
    return record


def private_root(policy: BuildPolicy) -> tuple[int, str, dict]:
    for _ in range(32):
        path = "/tmp/" + ROOT_PREFIX + policy.randomness(16).hex()
        try:
            policy.mkdir(path, 0o700)
        except FileExistsError:
            continue
        flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_CLOEXEC", 0))
        descriptor = policy.open(path, flags)
        info = policy.native_fstat(descriptor)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "reject unsafe, substituted, or shared private C build root")
        policy.private_roots_created += 1
        return descriptor, path, {
            "path": path, "prefix": ROOT_PREFIX, "device": info.st_dev,
            "inode": info.st_ino, "uid": info.st_uid, "mode": "0700",
            "nofollow_directory_descriptor": True, "directory_scanned": False,
        }
    raise BuildError("could not create fresh unpredictable private C22 root")


def read_private_artifact(policy: BuildPolicy, parent: int,
                          name: str) -> tuple[dict, bytes]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = policy.open(name, flags, parent=parent)
    try:
        before = policy.native_fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.geteuid()
             and before.st_nlink == 1 and 0 < before.st_size <= MAX_SOURCE_BYTES
             and stat.S_IMODE(before.st_mode) in (0o600, 0o700, 0o755),
             "reject unsafe, borrowed, or oversized private C22 native artifact")
        blocks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            block = policy.native_read(descriptor, min(remaining, 262144))
            need(bool(block), "reject truncated private C22 native artifact")
            blocks.append(block)
            remaining -= len(block)
        need(policy.native_read(descriptor, 1) == b"",
             "reject changed private C22 native artifact length")
        payload = b"".join(blocks)
        after = policy.native_fstat(descriptor)
        need((before.st_dev, before.st_ino, before.st_size,
              before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns),
             "reject replaced private first-party C22 native artifact")
        return ({"name": name, "sha256": hashlib.sha256(payload).hexdigest(),
                 "bytes": len(payload), "device": before.st_dev,
                 "inode": before.st_ino,
                 "mode": format(stat.S_IMODE(before.st_mode), "04o"),
                 "nlink": before.st_nlink}, payload)
    finally:
        policy.native_close(descriptor)


def build_phase(policy: BuildPolicy, root_fd: int, root_path: str,
                phase: str, native_source: bytes, adapter_source: bytes,
                pids: set[int]) -> dict:
    policy.mkdir(phase, 0o700, parent=root_fd)
    flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    phase_fd = policy.open(phase, flags, parent=root_fd)
    try:
        info = policy.native_fstat(phase_fd)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid()
             and stat.S_IMODE(info.st_mode) == 0o700,
             "reject substituted, reused, or shared actual private C22 phase")
        source = write_exclusive(policy, phase_fd, "vm_native.c", native_source)
        adapter = write_exclusive(policy, phase_fd,
                                  "vm_candidate.py", adapter_source)
        need(source["sha256"] == CORRECTED_NATIVE[1]
             and source["bytes"] == CORRECTED_NATIVE[2]
             and adapter["sha256"] == CORRECTED_ADAPTER[1]
             and adapter["bytes"] == CORRECTED_ADAPTER[2],
             "refuse old C21 engine or uncorrected public Python adapter")
        phase_path = root_path + "/" + phase
        output_path = phase_path + "/" + NATIVE_NAME
        source_path = phase_path + "/vm_native.c"
        include = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/" \
                  "include/python3.14"
        compiler, readelf = TOOLCHAINS[0][1], TOOLCHAINS[4][1]
        commands = (
            ("readelf_version", (readelf, "--version"), readelf),
            ("gcc_version", (compiler, "--version"), compiler),
            ("build_c_extension", (
                compiler, "-std=c11", "-O3", "-g0", "-fPIC", "-shared",
                "-fno-semantic-interposition",
                "-ffile-prefix-map=" + phase_path + "=/rebar/c-complete-v22",
                "-I", include, "-Wl,--build-id=sha1", "-Wl,--hash-style=gnu",
                "-o", output_path, source_path,
            ), compiler),
            ("extension_dynamic", (readelf, "--dynamic", output_path), readelf),
            ("extension_symbols", (readelf, "--syms", output_path), readelf),
            ("extension_sections", (readelf, "--sections", output_path), readelf),
            ("extension_notes", (readelf, "--notes", output_path), readelf),
        )
        processes: list[dict] = []
        for expected, (role, command, executable) in zip(
                PROCESS_ROLES, commands, strict=True):
            need(role == expected,
                 "reject omitted or reordered direct first-party compiler role")
            process, output = policy.spawn(role, command, phase, executable, pids)
            if role == "extension_symbols":
                need(b"PyInit__vm_native" in output,
                     "require exact Python C extension entry point")
                for token in (b"pcre2_", b"onig_", b"PyImport_ImportModule",
                              b"dlopen", b"dlsym", b"RE2::"):
                    need(token not in output,
                         "reject external matching engine or dynamic delegation")
            if role == "extension_dynamic":
                for token in (b"libpcre", b"libre2", b"libonig"):
                    need(token not in output,
                         "reject linked external regular-expression package")
            processes.append(process)
        artifact, payload = read_private_artifact(policy, phase_fd, NATIVE_NAME)
        need(payload.startswith(b"\x7fELF")
             and artifact["sha256"] != INSTALLED_NATIVE[1]
             and artifact["sha256"]
             != "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60",
             "require genuinely new independently built first-party C extension")
        policy.native_fsync(phase_fd)
        return {
            "name": phase, "device": info.st_dev, "inode": info.st_ino,
            "uid": info.st_uid, "mode": "0700",
            "source_owners": [
                {**source, "role": "complete-first-party-native-source"},
                {**adapter, "role": "corrected-first-party-python-adapter"},
            ],
            "native_output": {**artifact, "native_loaded": False},
            "processes": processes,
        }
    finally:
        policy.native_close(phase_fd)


def verify_phases(phases: list, pids: set[int]) -> tuple[str, int]:
    need(type(phases) is list and len(phases) == 2
         and type(pids) is set and len(pids) == 14,
         "require two real independent phases and fourteen distinct processes")
    source_owners: set[tuple[int, int]] = set()
    artifacts: set[tuple[int, int]] = set()
    fingerprints: set[str] = set()
    sizes: set[int] = set()
    for position, phase in enumerate(phases):
        need(type(phase) is dict and phase.get("name") == PHASES[position]
             and phase.get("mode") == "0700",
             "reject omitted, reused, or reordered independent C22 phase")
        sources = phase.get("source_owners")
        processes = phase.get("processes")
        need(type(sources) is list and len(sources) == 2
             and type(processes) is list and len(processes) == 7,
             "require one corrected native and adapter and seven processes")
        requirements = (
            ("complete-first-party-native-source", CORRECTED_NATIVE[1],
             CORRECTED_NATIVE[2]),
            ("corrected-first-party-python-adapter", CORRECTED_ADAPTER[1],
             CORRECTED_ADAPTER[2]),
        )
        for source, expected in zip(sources, requirements, strict=True):
            need(source.get("role") == expected[0]
                 and source.get("sha256") == expected[1]
                 and source.get("bytes") == expected[2]
                 and source.get("mode") == "0600",
                 "reject old engine, wrong adapter, or unsafe private source")
            identity = (source.get("device"), source.get("inode"))
            need(identity not in source_owners,
                 "reject source-owner reuse between independent build phases")
            source_owners.add(identity)
        for index, process in enumerate(processes):
            need(process.get("phase") == PHASES[position]
                 and process.get("role") == PROCESS_ROLES[index]
                 and process.get("pid") in pids
                 and process.get("exit_status") == 0,
                 "reject fabricated, failed, or reordered actual build process")
        artifact = phase.get("native_output")
        need(type(artifact) is dict and artifact.get("name") == NATIVE_NAME
             and artifact.get("native_loaded") is False,
             "reject activated, missing, or renamed native C extension")
        identity = (artifact.get("device"), artifact.get("inode"))
        need(identity not in artifacts,
             "reject reusing one native artifact as two independent builds")
        artifacts.add(identity)
        fingerprints.add(checked_hash(artifact.get("sha256"), "compiled extension"))
        sizes.add(artifact.get("bytes"))
    need(len(source_owners) == 4 and len(artifacts) == 2
         and len(fingerprints) == 1 and len(sizes) == 1,
         "require four fresh sources and two byte-identical compiled ELF files")
    return next(iter(fingerprints)), next(iter(sizes))


def evidence_directory(policy: BuildPolicy) -> int:
    flags = (os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0))
    descriptor = policy.open(ROOT + "/oracle/phase2/evidence", flags)
    info = policy.native_fstat(descriptor)
    need(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
         and info.st_uid == os.geteuid(),
         "reject substituted or unsafe actual C22 evidence directory")
    return descriptor


def contract_document(source_hash: str, protocol_hash: str) -> dict[str, object]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; INTEGRATED NATIVE BUILD NOT RUN",
        "phase": "CANDIDATES; REPRODUCIBLE FIRST-PARTY C BUILD",
        "source": {"path": SOURCE, "sha256": source_hash},
        "protocol": {"path": PROTOCOL, "sha256": protocol_hash},
        "pinned_cpython": {"path": PYTHON, "version": "3.14.6",
                            "required_flags": ["-I", "-B", "-S"]},
        "original_correctness_oracle": {
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "named_private_waiver_count": 13,
            "separate_reference_case_count": 8244,
            "supplemental_cases_counted_in_denominator": False,
            "expanded_holdout_proposed_case_count": 14155776,
            "holdout": "NOT GENERATED; NOT OPENED",
        },
        "latest_actual_c12_failure": {
            "receipt": owner_record(C12_FAILURE),
            "candidate_status": "FAIL",
            "verified_passing_case_count": 16413,
            "observed_mismatch_count": 606,
            "exact_total_mismatch_count": "NOT MEASURED",
            "completed_suite_count": 12,
            "unfinished_child_interpreter_suite": True,
        },
        "historical_c21_build": {
            "owners": [owner_record(row) for row in C21_FREEZE],
            "actual_build_receipt": owner_record(C21_BUILD),
            "actual_root_receipt": owner_record(C21_ROOT),
            "historical_native_source_sha256":
                "fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2",
            "historical_native_artifact_sha256":
                "7a5f8db27154cdcbd4203d727e02c0828ba1f9bf3fa2fdc1a86223ee57825f60",
            "historical_c19_failure_preserved": True,
            "historical_c20_entropy_failure_preserved": True,
        },
        "corrected_native": {
            "source_freeze": [owner_record(row) for row in NATIVE_FREEZE],
            "actual_materialization": owner_record(NATIVE_APPLICATION),
            "materialized_source": owner_record(CORRECTED_NATIVE),
            "targeted_observed_native_mismatches": 276,
            "source_only_candidate_source_opened": False,
        },
        "corrected_public_adapter": {
            "source_freeze": [owner_record(row) for row in ADAPTER_FREEZE],
            "actual_materialization": owner_record(ADAPTER_APPLICATION),
            "materialized_source": owner_record(CORRECTED_ADAPTER),
            "targeted_observed_public_adapter_mismatches": 330,
            "source_only_candidate_source_opened": False,
        },
        "corrected_runtime_guard": {
            "owners": [owner_record(row) for row in GUARD_FREEZE],
            "version": 4,
            "candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "future_execution_requires_canonical_module_identities": True,
            "future_execution_requires_separate_dual_target_activation": True,
        },
        "canonical_original_preservation": {
            "native_engine_source": owner_record(CANONICAL_C),
            "python_adapter": owner_record(CANONICAL_ADAPTER),
            "installed_native": {
                "path": INSTALLED_NATIVE[0],
                "sha256": INSTALLED_NATIVE[1],
                "bytes": INSTALLED_NATIVE[2],
                "inode": INSTALLED_NATIVE[3],
                "device": DEVICE, "mode": "0755", "nlink": 1,
            },
            "existing_candidate_sources_modified": 0,
            "installed_native_activated": False,
            "installed_original_inode_preserved": True,
        },
        "future_actual_build": {
            "authorization": BUILD_AUTHORIZATION,
            "frozen_commit_must_equal_pushed_commit": True,
            "root_prefix": ROOT_PREFIX,
            "root_mode": "0700",
            "private_root_entropy": "os.urandom(16)",
            "private_journal_entropy": "os.urandom(12)",
            "private_root_retained_on_success_or_failure": True,
            "phase_names": list(PHASES),
            "phase_mode": "0700",
            "phase_source_mode": "0600",
            "phase_count": 2,
            "phase_source_owner_count": 4,
            "independent_native_artifact_count": 2,
            "byte_identical_native_artifacts_required": True,
            "native_artifact_sha256": "NOT MEASURED",
            "native_artifact_bytes": "NOT MEASURED",
            "native_extension_name": NATIVE_NAME,
            "file_prefix_map_destination": "/rebar/c-complete-v22",
            "process_launcher": "DIRECT POSIX SPAWN; NO SHELL OR SUBPROCESS",
            "process_roles_per_phase": list(PROCESS_ROLES),
            "compiler_process_count_per_phase": 7,
            "expected_compiler_process_count": 14,
            "distinct_process_ids_required": True,
            "toolchains": [
                {"role": role, "path": path, "sha256": fingerprint,
                 "bytes": size, "version": version, "executable": executable}
                for role, path, fingerprint, size, version, executable
                in TOOLCHAINS
            ],
            "recovery_journal": "PRIVATE ATOMIC 0600; FILE AND DIRECTORY FSYNC",
            "receipts": "TWO EXCLUSIVE 0600 FILES; FILE AND DIRECTORY FSYNC",
            "external_regex_engine": "FORBIDDEN",
            "stdlib_regex_engine": "FORBIDDEN",
            "cross_candidate_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
        },
        "source_only_effects": {
            "bootstrap_plaintext_owner_reads": 1,
            "verified_plaintext_owner_count": 20,
            "candidate_source_files_read": 0,
            "candidate_imports": 0,
            "candidate_executions": 0,
            "compiler_processes": 0,
            "native_libraries_loaded": 0,
            "private_roots_created": 0,
            "private_roots_opened": 0,
            "compressed_archives_opened": 0,
            "hidden_cases_read": 0,
            "entropy_requests": 0,
            "clock_samples": 0,
            "workspace_mutations": 0,
            "candidate_correctness": "NOT MEASURED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        },
    }


def authority_mapping() -> dict[str, str]:
    return {
        "--native-source-sha256": NATIVE_FREEZE[0][1],
        "--native-protocol-sha256": NATIVE_FREEZE[1][1],
        "--native-contract-sha256": NATIVE_FREEZE[2][1],
        "--native-application-sha256": NATIVE_APPLICATION[1],
        "--adapter-source-sha256": ADAPTER_FREEZE[0][1],
        "--adapter-protocol-sha256": ADAPTER_FREEZE[1][1],
        "--adapter-contract-sha256": ADAPTER_FREEZE[2][1],
        "--adapter-application-sha256": ADAPTER_APPLICATION[1],
        "--guard-source-sha256": GUARD_FREEZE[0][1],
        "--guard-protocol-sha256": GUARD_FREEZE[1][1],
        "--guard-contract-sha256": GUARD_FREEZE[2][1],
        "--c21-source-sha256": C21_FREEZE[0][1],
        "--c21-protocol-sha256": C21_FREEZE[1][1],
        "--c21-contract-sha256": C21_FREEZE[2][1],
        "--c21-build-receipt-sha256": C21_BUILD[1],
        "--c21-root-receipt-sha256": C21_ROOT[1],
        "--c12-failure-receipt-sha256": C12_FAILURE[1],
        "--corrected-native-sha256": CORRECTED_NATIVE[1],
        "--corrected-adapter-sha256": CORRECTED_ADAPTER[1],
        "--installed-native-sha256": INSTALLED_NATIVE[1],
    }


def parse_options(values: list[str]) -> dict[str, object]:
    modes = {"--self-test", "--verify-source", "--build"}
    flags = modes | {BUILD_AUTHORIZATION}
    standard = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
                "--frozen-commit", "--pushed-commit"}
    build_pins = authority_mapping()
    parsed: dict[str, object] = {}
    index = 0
    while index < len(values):
        item = values[index]
        need(item in flags or item in standard or item in build_pins,
             "reject unknown, external, or abbreviated actual build authority")
        need(item not in parsed,
             "reject duplicated immutable V22 source/build authority")
        if item in flags:
            parsed[item] = True
            index += 1
        else:
            need(index + 1 < len(values),
                 "reject missing immutable V22 build authority value")
            parsed[item] = values[index + 1]
            index += 2
    selected = [item for item in modes if parsed.get(item)]
    need(len(selected) == 1,
         "require exactly one source self-test, source verification, or actual build")
    mode = selected[0]
    if mode == "--self-test":
        need(set(parsed) == {mode},
             "self-test cannot receive candidate or build authority")
        return parsed
    source_keys = {mode, "--source-sha256", "--protocol-sha256",
                   "--contract-sha256"}
    if mode == "--verify-source":
        need(set(parsed) == source_keys,
             "source verification cannot request a compiler, private root, or candidate")
    else:
        required = source_keys | {BUILD_AUTHORIZATION, "--frozen-commit",
                                  "--pushed-commit"} | set(build_pins)
        need(set(parsed) == required,
             "require root-only authorization and every independent V22 build pin")
        need(parsed["--frozen-commit"] == parsed["--pushed-commit"]
             and type(parsed["--frozen-commit"]) is str
             and len(parsed["--frozen-commit"]) == 40
             and all(item in "0123456789abcdef"
                     for item in parsed["--frozen-commit"]),
             "require the exact complete V22 freeze to be committed and pushed")
        for key, expected in build_pins.items():
            need(checked_hash(parsed[key], key) == expected,
                 "reject substituted independent V22 actual build pin: " + key)
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        checked_hash(parsed[key], key)
    return parsed


def verify_source(native: types.ModuleType,
                  options: dict[str, object]) -> dict[str, object]:
    wall = make_source_wall(native)
    native.no_matchers()
    wall.install()
    if options.get("--self-test"):
        controls = source_controls(native, wall)
        need(wall.root is None and wall.public_reads == 0
             and wall.candidate_reads == 0 and wall.workspace_mutations == 0,
             "synthetic self-test must never access any workspace candidate")
        return {"schema": SCHEMA + "-self-test", "status": "PASS",
                "controls": controls,
                "effects": {"bootstrap_plaintext_owner_reads": 1,
                            "additional_plaintext_owner_reads": 0,
                            "candidate_source_files_read": 0,
                            "compiler_processes": 0,
                            "private_roots_created": 0,
                            "workspace_mutations": 0,
                            "candidate_correctness": "NOT MEASURED"}}

    source_hash = options["--source-sha256"]
    protocol_hash = options["--protocol-sha256"]
    contract_hash = options["--contract-sha256"]
    need(type(source_hash) is str and type(protocol_hash) is str
         and type(contract_hash) is str,
         "require three distinct exact V22 source-owner fingerprints")
    wall.open_root()
    wall.read(SOURCE, source_hash)
    wall.read(PROTOCOL, protocol_hash)
    manifest = native.JSON(wall.read(CONTRACT, contract_hash)).parse()
    need(manifest == contract_document(source_hash, protocol_hash),
         "reject weakened, falsely qualified, or changed V22 build contract")
    raw: dict[str, bytes] = {NATIVE_FREEZE[0][0]: b"BOOTSTRAPPED BEFORE WALL"}
    for owner in evidence_owners():
        if owner == NATIVE_FREEZE[0]:
            continue
        raw[owner[0]] = wall.read(*owner)
    validate_evidence(native, raw)
    need(wall.public_reads == 19 and wall.candidate_reads == 0
         and wall.workspace_mutations == 0,
         "verify twenty exact plaintext owners including one authenticated bootstrap")
    controls = source_controls(native, wall)
    native.no_matchers()
    return {"schema": SCHEMA + "-source-verification", "status": "PASS",
            "source_sha256": source_hash, "protocol_sha256": protocol_hash,
            "contract_sha256": contract_hash,
            "corrected_native_sha256": CORRECTED_NATIVE[1],
            "corrected_native_bytes": CORRECTED_NATIVE[2],
            "corrected_adapter_sha256": CORRECTED_ADAPTER[1],
            "corrected_adapter_bytes": CORRECTED_ADAPTER[2],
            "preserved_c12_observed_mismatch_count": 606,
            "controls": controls,
            "effects": {"bootstrap_plaintext_owner_reads": 1,
                        "additional_plaintext_owner_reads": wall.public_reads,
                        "total_plaintext_owner_reads": wall.public_reads + 1,
                        "candidate_source_files_read": 0,
                        "compiler_processes": 0,
                        "private_roots_created": 0,
                        "compressed_archives_opened": 0,
                        "workspace_mutations": 0,
                        "candidate_correctness": "NOT MEASURED",
                        "native_artifact_sha256": "NOT MEASURED",
                        "performance": "NOT MEASURED"}}


def read_dynamic_build_owner(policy: BuildPolicy, relative: str,
                             fingerprint: str) -> bytes:
    checked_hash(fingerprint, relative)
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "authenticate only the exact three current V22 source-freeze owners")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = policy.open(ROOT + "/" + relative, flags)
    try:
        before = policy.native_fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600
             and 0 < before.st_size <= MAX_SOURCE_BYTES,
             "reject substituted actual-build source freeze owner")
        remaining = before.st_size
        blocks: list[bytes] = []
        while remaining:
            block = policy.native_read(descriptor, min(remaining, 262144))
            need(bool(block), "reject truncated actual-build source owner")
            blocks.append(block)
            remaining -= len(block)
        need(policy.native_read(descriptor, 1) == b"",
             "reject extra actual-build source owner bytes")
        payload = b"".join(blocks)
        after = policy.native_fstat(descriptor)
        need(hashlib.sha256(payload).hexdigest() == fingerprint
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns),
             "reject modified frozen V22 actual-build owner")
        policy.source_reads += 1
        return payload
    finally:
        policy.native_close(descriptor)


def run_actual_build(native: types.ModuleType,
                     options: dict[str, object]) -> dict[str, object]:
    need(options.get("--build") is True
         and options.get(BUILD_AUTHORIZATION) is True,
         "deny actual C22 compilation before explicit frozen root authority")
    policy = BuildPolicy(native)
    native.no_matchers()
    policy.install()

    source_hash = options["--source-sha256"]
    protocol_hash = options["--protocol-sha256"]
    contract_hash = options["--contract-sha256"]
    need(type(source_hash) is str and type(protocol_hash) is str
         and type(contract_hash) is str,
         "require all independently committed actual-build source owners")
    own_source = read_dynamic_build_owner(policy, SOURCE, source_hash)
    own_protocol = read_dynamic_build_owner(policy, PROTOCOL, protocol_hash)
    own_contract = read_dynamic_build_owner(policy, CONTRACT, contract_hash)
    need(bool(own_source) and bool(own_protocol),
         "reject empty genuine actual-build source/protocol")
    manifest = native.JSON(own_contract).parse()
    need(manifest == contract_document(source_hash, protocol_hash),
         "reject changed exact actual-build source-freeze contract")

    raw: dict[str, bytes] = {NATIVE_FREEZE[0][0]: b"AUTHENTICATED BOOTSTRAP"}
    for owner in evidence_owners():
        if owner == NATIVE_FREEZE[0]:
            continue
        _, payload = read_build_owner(policy, owner, capture=True)
        need(type(payload) is bytes,
             "capture complete immutable actual-build evidence owner")
        raw[owner[0]] = payload
        policy.source_reads += 1
    validate_evidence(native, raw)

    canonical_before, _ = read_build_owner(policy, CANONICAL_C)
    adapter_before, _ = read_build_owner(policy, CANONICAL_ADAPTER)
    installed_before, _ = read_build_owner(policy, INSTALLED_NATIVE,
                                           expected_mode=0o755)
    corrected_native_owner, corrected_native_source = read_build_owner(
        policy, CORRECTED_NATIVE, capture=True,
    )
    corrected_adapter_owner, corrected_adapter_source = read_build_owner(
        policy, CORRECTED_ADAPTER, capture=True,
    )
    policy.candidate_source_reads += 2
    need(type(corrected_native_source) is bytes
         and type(corrected_adapter_source) is bytes,
         "require complete exclusively materialized native and adapter bytes")
    native.preserve_engine(corrected_native_source)
    configure = corrected_adapter_source.find(b"_vm_native.configure(")
    public_flag = corrected_adapter_source.find(b'RegexFlag.__module__ = "re"')
    need(configure >= 0 and configure < public_flag
         and corrected_adapter_source.count(b"from candidates import _vm_native") == 1,
         "preserve owned native configuration before public flag module identity")

    historical_build = native.JSON(raw[C21_BUILD[0]]).parse()
    tools = authenticate_toolchains(policy, historical_build)
    root_fd, root_path, root_record = private_root(policy)
    journal = {
        "schema": SCHEMA + "-private-recovery-journal",
        "version": VERSION,
        "status": "PRIVATE ROOT AUTHENTICATED; BUILD NOT STARTED",
        "source_sha256": source_hash,
        "protocol_sha256": protocol_hash,
        "contract_sha256": contract_hash,
        "frozen_commit": options["--frozen-commit"],
        "pushed_commit": options["--pushed-commit"],
        "root": root_record,
        "corrected_native_source": corrected_native_owner,
        "corrected_python_adapter": corrected_adapter_owner,
        "canonical_c_before": canonical_before,
        "canonical_adapter_before": adapter_before,
        "installed_native_before": installed_before,
        "installed_native_activated": False,
        "candidate_source_targets_temporarily_modified": 0,
        "candidate_sources_persistently_modified": 0,
        "phases": [],
    }

    try:
        write_journal(policy, native, root_fd, journal)
        phases: list[dict] = []
        pids: set[int] = set()
        for phase in PHASES:
            actual = build_phase(policy, root_fd, root_path, phase,
                                 corrected_native_source,
                                 corrected_adapter_source, pids)
            phases.append(actual)
            journal["status"] = "PRIVATE PHASE " + phase + " DURABLY BUILT"
            journal["phases"] = phases
            write_journal(policy, native, root_fd, journal)

        artifact_sha, artifact_bytes = verify_phases(phases, pids)
        canonical_after, _ = read_build_owner(policy, CANONICAL_C)
        adapter_after, _ = read_build_owner(policy, CANONICAL_ADAPTER)
        installed_after, _ = read_build_owner(policy, INSTALLED_NATIVE,
                                              expected_mode=0o755)
        corrected_native_after, _ = read_build_owner(policy, CORRECTED_NATIVE)
        corrected_adapter_after, _ = read_build_owner(policy, CORRECTED_ADAPTER)
        policy.candidate_source_reads += 2
        need(canonical_after == canonical_before and adapter_after == adapter_before
             and installed_after == installed_before
             and corrected_native_after == corrected_native_owner
             and corrected_adapter_after == corrected_adapter_owner,
             "never alter canonical/variant candidate sources or installed native")

        journal["status"] = "PASS; FOUR OWNED SOURCES AND TWO MATCHING NATIVE ELFS"
        journal["canonical_c_after"] = canonical_after
        journal["canonical_adapter_after"] = adapter_after
        journal["installed_native_after"] = installed_after
        journal["corrected_native_after"] = corrected_native_after
        journal["corrected_adapter_after"] = corrected_adapter_after
        journal["independently_built_native_sha256"] = artifact_sha
        journal["independently_built_native_bytes"] = artifact_bytes
        final_journal = write_journal(policy, native, root_fd, journal)

        evidence_fd = evidence_directory(policy)
        try:
            phase_summary = [{
                "name": phase["name"], "device": phase["device"],
                "inode": phase["inode"], "mode": phase["mode"],
                "source_owners": phase["source_owners"],
                "native_output": phase["native_output"],
                "processes": phase["processes"],
            } for phase in phases]
            receipt = {
                "schema": SCHEMA + "-durable-publication-receipt",
                "version": VERSION, "status": "PASS", "family": FAMILY,
                "label": LABEL, "build_status": "PASS",
                "publication_pass_means":
                    "DURABLE FIRST-PARTY C DUAL SOURCE BUILD ONLY",
                "source_sha256": source_hash,
                "protocol_sha256": protocol_hash,
                "contract_sha256": contract_hash,
                "frozen_commit": options["--frozen-commit"],
                "pushed_commit": options["--pushed-commit"],
                "corrected_native_source_sha256": CORRECTED_NATIVE[1],
                "corrected_native_source_bytes": CORRECTED_NATIVE[2],
                "corrected_adapter_source_sha256": CORRECTED_ADAPTER[1],
                "corrected_adapter_source_bytes": CORRECTED_ADAPTER[2],
                "actual_native_materialization_receipt_sha256":
                    NATIVE_APPLICATION[1],
                "actual_adapter_materialization_receipt_sha256":
                    ADAPTER_APPLICATION[1],
                "corrected_guard_source_sha256": GUARD_FREEZE[0][1],
                "preserved_latest_c12_failure_receipt_sha256": C12_FAILURE[1],
                "preserved_latest_c12_observed_mismatches": 606,
                "previous_c21_build_receipt_sha256": C21_BUILD[1],
                "previous_c21_root_receipt_sha256": C21_ROOT[1],
                "authenticated_toolchain_owner_count": 5,
                "authenticated_toolchain_owners": tools,
                "actual_compiler_process_count": policy.process_count,
                "expected_compiler_process_count": 14,
                "actual_compiler_process_ids": sorted(pids),
                "private_phase_count": 2,
                "distinct_phase_source_owner_count": 4,
                "distinct_native_artifact_count": 2,
                "byte_identical_native_artifacts": True,
                "native_artifact_sha256": artifact_sha,
                "native_artifact_bytes": artifact_bytes,
                "root": root_record,
                "phases": phase_summary,
                "recovery_journal": final_journal,
                "canonical_c_before": canonical_before,
                "canonical_c_after": canonical_after,
                "canonical_adapter_before": adapter_before,
                "canonical_adapter_after": adapter_after,
                "installed_native_before": installed_before,
                "installed_native_after": installed_after,
                "installed_native_inode_preserved": True,
                "installed_native_activated": False,
                "candidate_source_targets_temporarily_modified": 0,
                "candidate_sources_persistently_modified": 0,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
                "runtime_non_delegation": "NOT ESTABLISHED",
                "candidate_workers_started": 0,
                "native_libraries_loaded": 0,
                "compressed_archives_opened": 0,
                "hidden_cases_read": 0,
                "clock_samples": 0,
                "performance": "NOT MEASURED",
                "memory": "NOT MEASURED",
                "undefined_behavior": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "winner_selected": False,
            }
            build_name = (
                "native-source-build-v22-c-phase2-v22-c-complete-semantics-"
                "publication-receipt.json"
            )
            publication = write_exclusive(
                policy, evidence_fd, build_name, canonical_payload(native, receipt),
            )
            policy.workspace_receipts_created += 1
            root_receipt = {
                "schema": SCHEMA + "-durable-root-provenance-receipt",
                "version": VERSION, "status": "PASS", "family": FAMILY,
                "label": LABEL,
                "publication_pass_means":
                    "DURABLE FIRST-PARTY C DUAL SOURCE ROOT ONLY",
                "source_sha256": source_hash,
                "protocol_sha256": protocol_hash,
                "contract_sha256": contract_hash,
                "canonical_build_receipt_relative":
                    "oracle/phase2/evidence/" + build_name,
                "canonical_build_receipt_sha256": publication["sha256"],
                "corrected_native_source_sha256": CORRECTED_NATIVE[1],
                "corrected_adapter_source_sha256": CORRECTED_ADAPTER[1],
                "native_artifact_sha256": artifact_sha,
                "native_artifact_bytes": artifact_bytes,
                "actual_native_materialization_receipt_sha256":
                    NATIVE_APPLICATION[1],
                "actual_adapter_materialization_receipt_sha256":
                    ADAPTER_APPLICATION[1],
                "latest_c12_failure_receipt_sha256": C12_FAILURE[1],
                "root": {**root_record, "phase_count": 2,
                         "distinct_source_owner_count": 4,
                         "distinct_native_owner_count": 2,
                         "byte_identical_native_output": True,
                         "phases": phase_summary},
                "actual_compiler_process_count": policy.process_count,
                "expected_compiler_process_count": 14,
                "actual_compiler_process_ids": sorted(pids),
                "authenticated_toolchain_owner_count": 5,
                "authenticated_toolchain_owners": tools,
                "installed_native_before": installed_before,
                "installed_native_after": installed_after,
                "installed_native_inode_preserved": True,
                "installed_native_activated": False,
                "candidate_source_targets_temporarily_modified": 0,
                "candidate_sources_persistently_modified": 0,
                "candidate_matching": "NOT RUN",
                "candidate_correctness": "NOT MEASURED",
                "runtime_non_delegation": "NOT ESTABLISHED",
                "candidate_workers_started": 0,
                "native_libraries_loaded": 0,
                "compressed_archives_opened": 0,
                "hidden_cases_read": 0,
                "clock_samples": 0,
                "performance": "NOT MEASURED",
                "holdout": "NOT OPENED",
                "winner_selected": False,
            }
            root_name = (
                "native-source-build-v22-c-phase2-v22-c-complete-semantics-"
                "root-provenance-receipt.json"
            )
            root_publication = write_exclusive(
                policy, evidence_fd, root_name,
                canonical_payload(native, root_receipt),
            )
            policy.workspace_receipts_created += 1
        finally:
            policy.native_close(evidence_fd)
        journal["status"] = "PASS; ACTUAL BUILD AND ROOT RECEIPTS DURABLE"
        journal["build_receipt_sha256"] = publication["sha256"]
        journal["root_receipt_sha256"] = root_publication["sha256"]
        write_journal(policy, native, root_fd, journal)
        native.no_matchers()
        return {"schema": SCHEMA + "-actual-published-build",
                "status": "PASS", "family": FAMILY, "label": LABEL,
                "build_receipt": publication, "root_receipt": root_publication,
                "actual_compiler_process_count": policy.process_count,
                "actual_source_phase_count": 2,
                "corrected_native_source_sha256": CORRECTED_NATIVE[1],
                "corrected_adapter_source_sha256": CORRECTED_ADAPTER[1],
                "native_artifact_sha256": artifact_sha,
                "native_artifact_bytes": artifact_bytes,
                "installed_native_inode_preserved": True,
                "candidate_source_targets_temporarily_modified": 0,
                "candidate_correctness": "NOT MEASURED",
                "runtime_non_delegation": "NOT ESTABLISHED",
                "performance": "NOT MEASURED", "holdout": "NOT OPENED"}
    except BaseException as error:
        journal["status"] = "FAIL; PRIVATE ROOT AND RECOVERY JOURNAL RETAINED"
        journal["failure_type"] = type(error).__name__
        journal["failure_message"] = str(error)[:4096]
        try:
            write_journal(policy, native, root_fd, journal)
        except BaseException:
            pass
        raise
    finally:
        policy.native_close(root_fd)


def main(argv: list[str]) -> dict[str, object]:
    global ANSWER_ENCODER
    clean_runtime()
    options = parse_options(argv)
    native = bootstrap_native_controller()
    ANSWER_ENCODER = native.canonical
    if options.get("--build"):
        return run_actual_build(native, options)
    return verify_source(native, options)


if __name__ == "__main__":
    try:
        result = main(list(sys.argv[1:]))
        need(callable(ANSWER_ENCODER), "require authenticated JSON encoder")
        sys.stdout.write(ANSWER_ENCODER(result) + "\n")
    except Exception as error:
        sys.stderr.write("C complete semantic source build V22: FAIL: "
                         + type(error).__name__ + ": " + str(error) + "\n")
        raise SystemExit(2)
