#!/usr/bin/env python3
"""Run the complete original oracle against the corrected first-party Zig build.

The source-only actions never load a runtime guard, inspect a private build,
import a candidate, open a proposed holdout, or run a matching operation.  An
actual campaign is available only after an independently pinned, committed,
pushed, root-authorized invocation.  Its three canonical owners are replaced
reversibly and restored at their original inode identities before publication.
"""

from __future__ import annotations

import ast
import builtins
import collections
import hashlib
import importlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SELF = "tools/run_owned_repaired_zig_original_campaign_v16.py"
PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V16.md"
CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v16.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v16"
FAMILY = "zig"
LABEL = "phase2-v16-zig-full-semantic-original-p0-v16"
BUILD_LABEL = "phase2-v16-zig-full-semantic-root-provenance"
DEVICE = 2064
PRIVATE_DEVICE = 2049
MAX_BYTES = 256 * 1024 * 1024
RECOVERY = "/tmp/rebar-phase2-repaired-zig-original-campaign-v16-phase2-v16-zig-full-semantic-original-p0-v16"
EXTERNAL_LOCPATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044)
PRODUCER = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py", "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538", 102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md", "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4", 5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json", "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53", 21036, 524885),
)
GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v4.py", "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3", 48687, 429243),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md", "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16", 4492, 525890),
    ("oracle/phase2/candidate-runtime-independence-v4.json", "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2", 9352, 525891),
)
GUARD_V2 = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py", "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a", 67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md", "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c", 4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json", "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473", 7671, 524887),
)
LEGACY = (
    ("tools/run_owned_repaired_zig_original_campaign_v13.py", "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8", 246570, 430932),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md", "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c", 9553, 525201),
    ("oracle/phase2/repaired-zig-original-campaign-v13.json", "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f", 106084, 525206),
)
BUILD = (
    ("tools/reproduce_owned_zig_full_semantic_source_build_v16.py", "b53e0d01a0302021e4ef5671a8c9f4f6f80f2f2a09061e3385381cb76fd9f1f3", 58450, 430803),
    ("oracle/phase2/ZIG-FULL-SEMANTIC-SOURCE-BUILD-V16.md", "fd4070d798da38b2b2473ebb480780f0b13b57e7378d05eaeb77a9efabab089e", 6580, 525882),
    ("oracle/phase2/zig-full-semantic-source-build-v16.json", "faeea68ada0ee3c47beb2e5ee24acbbb9e19c324fb4ddb0c2b8f098a54e4f543", 18059, 525961),
    ("oracle/phase2/evidence/zig-full-semantic-source-build-v16-phase2-v16-zig-full-semantic-root-provenance-build-receipt.json", "5a20e5fc1c052d58b25cf279db926bdf8c227e652d3a37be529b1491987b28f1", 174596, 526113),
    ("oracle/phase2/evidence/zig-full-semantic-source-build-v16-phase2-v16-zig-full-semantic-root-provenance-private-root-receipt.json", "08b4b95edf4212198e5d8f44e51876e3e1ba098491db59acd5ee6c412dd2d158", 77900, 526112),
)
HISTORY = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v12-phase2-v13-zig-guard-clean-v1-original-p0-v12-failures-publication-receipt.json",
    "ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9", 77604, 524975,
)
P0 = (
    ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 524385),
    ("oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/two-independent-reference-result.json", "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096", 3658, 524707),
)
ENGINE_SOURCE = ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915, 429377)
BRIDGE_SOURCE = ("candidates/zig/variants/replacement_event_semantics_v1/py_bridge.c", "07337863f6b4a0e749a8d60b2e5704bb961e43dc09bfa85c238f0efa40d3583c", 176765, 525558)
ADAPTER_SOURCE = ("candidates/zig/variants/public_adapter_semantics_v1/zig_candidate.py", "7129c63bdfd3c265a44541500238c26a8a5511f8932140de7d06bb49c13f588d", 67735, 525024)
NATIVE = {
    "engine": ("caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071", 108888),
    "bridge": ("59b2c21c220ec019338289e6c64dc73b820645cc273cb5100268ab770127d4fe", 138104),
}
ORIGINALS = {
    "engine": {"relative": "candidates/_zig_probe.so", "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652", "bytes": 478432, "device": DEVICE, "inode": 431260, "mode": 0o700, "uid": 1000, "nlink": 1},
    "bridge": {"relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b", "bytes": 134112, "device": DEVICE, "inode": 431274, "mode": 0o700, "uid": 1000, "nlink": 1},
    "adapter": {"relative": "candidates/zig_candidate.py", "sha256": "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", "bytes": 68422, "device": DEVICE, "inode": 429360, "mode": 0o600, "uid": 1000, "nlink": 1},
}
ROLES = ("engine", "bridge", "adapter")
RESTORE = ("adapter", "bridge", "engine")
NATIVE_OWNER_FIELDS = frozenset(("absolute_path", "bytes", "device", "family", "file_name", "inode", "mode", "native_loaded", "nlink", "relative", "role", "sha256", "size_bytes", "uid"))
SOURCE_EFFECTS = (
    "candidate_imports", "candidate_workers_started", "native_libraries_loaded",
    "native_activations", "private_roots_opened", "private_snapshots_opened",
    "matching_archives_opened", "holdout_files_opened", "holdout_proposals_opened",
    "benchmark_files_opened", "timing_trials_run", "runtime_guards_executed",
    "runtime_guards_installed", "compiler_processes_started", "subinterpreters_created",
    "candidate_sources_opened", "files_written", "git_commands_run",
)
ACTUAL_PINS = (
    ("--python-sha256", PYTHON_SHA256),
    ("--goal-sha256", GOAL[1]),
    ("--build-source-sha256", BUILD[0][1]),
    ("--build-protocol-sha256", BUILD[1][1]),
    ("--build-contract-sha256", BUILD[2][1]),
    ("--build-receipt-sha256", BUILD[3][1]),
    ("--root-receipt-sha256", BUILD[4][1]),
    ("--producer-source-sha256", PRODUCER[0][1]),
    ("--producer-protocol-sha256", PRODUCER[1][1]),
    ("--producer-contract-sha256", PRODUCER[2][1]),
    ("--guard-source-sha256", GUARD[0][1]),
    ("--guard-protocol-sha256", GUARD[1][1]),
    ("--guard-contract-sha256", GUARD[2][1]),
    ("--v2-guard-source-sha256", GUARD_V2[0][1]),
    ("--v2-guard-protocol-sha256", GUARD_V2[1][1]),
    ("--v2-guard-contract-sha256", GUARD_V2[2][1]),
    ("--legacy-source-sha256", LEGACY[0][1]),
    ("--legacy-protocol-sha256", LEGACY[1][1]),
    ("--legacy-contract-sha256", LEGACY[2][1]),
    ("--history-receipt-sha256", HISTORY[1]),
    ("--adapter-sha256", ADAPTER_SOURCE[1]),
    ("--bridge-source-sha256", BRIDGE_SOURCE[1]),
    ("--engine-source-sha256", ENGINE_SOURCE[1]),
    ("--bridge-native-sha256", NATIVE["bridge"][0]),
    ("--engine-native-sha256", NATIVE["engine"][0]),
)
REAL_OPEN = os.open
WALL = None


class CampaignError(Exception):
    """A pinned source, actual owner, execution boundary, or result changed."""


def require(value, message):
    if value is not True:
        raise CampaignError(message)


def sha(value, label):
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require a complete independent lowercase SHA-256: " + label)
    return value


def digest(raw):
    require(type(raw) is bytes, "hash only authenticated complete bytes")
    return hashlib.sha256(raw).hexdigest()


def relative(value):
    require(type(value) is str and value and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an escaped source path")
    return value


def owner_record(item):
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "inode": item[3], "device": DEVICE, "mode": "0600", "nlink": 1}


def read_owner(item):
    require(type(item) is tuple and len(item) == 4
            and relative(item[0]) == item[0] and sha(item[1], item[0])
            and type(item[2]) is int and 0 < item[2] <= MAX_BYTES
            and type(item[3]) is int and item[3] > 0,
            "reject an incomplete source identity")
    descriptor = REAL_OPEN(ROOT + "/" + item[0],
                           os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                           | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                and before.st_ino == item[3] and before.st_uid == os.geteuid()
                and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_size == item[2],
                "reject a substituted source owner: " + item[0])
        chunks, remaining = [], before.st_size
        while remaining:
            chunk = os.read(descriptor, min(262144, remaining))
            require(bool(chunk), "reject truncated source owner: " + item[0])
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require(not os.read(descriptor, 1) and digest(raw) == item[1]
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject changed source bytes: " + item[0])
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(path, expected):
    expected = sha(expected, path)
    identity = os.stat(ROOT + "/" + relative(path), follow_symlinks=False)
    return (path, expected, identity.st_size, identity.st_ino)


def clean():
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and "re" not in sys.modules and "_sre" not in sys.modules
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "require clean isolated pinned CPython before candidate import")


class SourceWall:
    """A physical, scoped deny-by-default source-only audit boundary."""

    def __init__(self, allowed):
        self.allowed = frozenset(allowed)
        self.active = False
        self.audit_count = 0
        self.denials = 0

    def audit(self, event, args):
        if not self.active:
            return
        self.audit_count += 1
        if event == "open":
            target = args[0] if args else None
            flags = args[2] if len(args) > 2 else 0
            require(type(target) is str and target in self.allowed
                    and type(flags) is int
                    and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                 | os.O_TRUNC | os.O_APPEND) == 0,
                    "source-only wall rejected filesystem open: " + str(target))
        elif event == "import":
            name = args[0] if args else ""
            require(type(name) is str
                    and name not in {"re", "_sre", "regex", "re2", "ctypes",
                                     "subprocess", "socket", "threading",
                                     "multiprocessing", "gzip", "json", "tempfile",
                                     "time", "concurrent.interpreters", "_interpreters",
                                     "candidates", "copyreg"}
                    and not name.startswith("candidates."),
                    "source-only wall rejected import: " + str(name))
        elif event in {"subprocess.Popen", "socket.connect", "ctypes.dlopen",
                       "ctypes.dlsym", "cpython.PyInterpreterState_New",
                       "_interpreters.create", "_interpreters.exec",
                       "os.mkdir", "os.remove", "os.rename", "os.link",
                       "os.chmod", "os.chown", "os.symlink"}:
            raise CampaignError("source-only wall rejected effect: " + event)

    def __enter__(self):
        global WALL
        require(WALL is None, "reject nested source-only audit boundaries")
        WALL = self
        sys.addaudithook(self.audit)
        self.active = True
        return self

    def __exit__(self, kind, value, trace):
        global WALL
        self.active = False
        WALL = None
        return False


def load_module(item, name):
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + item[0]
    exec(compile(read_owner(item), module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(module.__name__ == name, "reject a substituted authenticated module")
    return module


def owner_list(include_contract=False):
    owners = (GOAL,) + P0 + PRODUCER + GUARD + LEGACY + BUILD + (HISTORY,)
    if include_contract:
        identity = os.stat(ROOT + "/" + CONTRACT, follow_symlinks=False)
        owners += ((CONTRACT, "0" * 64, identity.st_size, identity.st_ino),)
    return owners


def validate_v4_guard(value):
    child = value.get("subinterpreter_bootstrap", {})
    native = value.get("native_owner_policy", {})
    producer = value.get("immutable_producer_v5", {})
    predecessor = value.get("immutable_predecessor_v3", {})
    require(value.get("schema")
            == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
            and value.get("version") == 4
            and value.get("status") == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
            and value.get("source") == owner_record(GUARD[0])
            and value.get("protocol") == owner_record(GUARD[1])
            and value.get("goal_sha256") == GOAL[1]
            and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and value.get("qualified_candidate_count") == 0
            and value.get("holdout") == "NOT OPENED"
            and value.get("candidate_matching") == "NOT RUN"
            and producer.get("version") == 5
            and producer.get("owners") == {
                "source": owner_record(PRODUCER[0]),
                "protocol": owner_record(PRODUCER[1]),
                "contract": owner_record(PRODUCER[2]),
            }
            and predecessor.get("version") == 3
            and child.get("suite") == "subinterpreter_v2"
            and child.get("original_case_count") == 128
            and child.get("expected_interpreters_created") == 11
            and child.get("expected_interpreters_destroyed") == 11
            and child.get("expected_case_interpreter_exec_calls") == 394
            and child.get("expected_bootstrap_interpreter_exec_calls") == 11
            and child.get("expected_cleanup_interpreter_exec_calls") == 11
            and child.get("expected_total_real_interpreter_exec_calls") == 416
            and child.get("creation_audit_event")
            == "NOT EMITTED TO PARENT PYTHON AUDIT HOOK"
            and set(child.get("creation_audit_event_names_rejected", []))
            == {"cpython.PyInterpreterState_New", "_interpreters.create", "_interpreters.exec"}
            and child.get("actual_interpreters_created") == 0
            and child.get("actual_interpreters_destroyed") == 0
            and child.get("actual_child_guards_installed") == 0
            and native.get("required_field_count") == 14
            and native.get("required_fields") == sorted(NATIVE_OWNER_FIELDS)
            and native.get("extra_or_missing_fields") == "FORBIDDEN"
            and native.get("native_loaded") is False,
            "reject weakened V4 child boundaries, ownership, or producer lineage")
    return value


def snapshot_identity(owner, role, phase_name, private_root):
    expected = ADAPTER_SOURCE if role == "adapter" else (
        BRIDGE_SOURCE if role == "bridge_source" else ENGINE_SOURCE
    )
    suffix = {
        "engine_source": "/source/candidates/zig/mini_regex.zig",
        "bridge_source": "/source/candidates/zig/py_bridge.c",
        "adapter": "/source/candidates/zig_candidate.py",
    }[role]
    require(type(owner) is dict and owner.get("sha256") == expected[1]
            and owner.get("bytes") == expected[2]
            and owner.get("device") == PRIVATE_DEVICE
            and owner.get("uid") == os.geteuid()
            and owner.get("nlink") == 1 and owner.get("mode") == "0600"
            and type(owner.get("inode")) is int and owner["inode"] > 0
            and owner.get("path") == private_root + "/" + phase_name + suffix,
            "reject altered first-party build snapshot metadata: " + role)
    return owner


def native_identity(owner, role, phase_name, private_root):
    suffix = {
        "engine": "/native/_zig_probe.so",
        "bridge": "/native/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
    }[role]
    require(type(owner) is dict and owner.get("sha256") == NATIVE[role][0]
            and owner.get("bytes") == NATIVE[role][1]
            and owner.get("device") == PRIVATE_DEVICE
            and owner.get("uid") == os.geteuid() and owner.get("nlink") == 1
            and owner.get("mode") == "0700"
            and type(owner.get("inode")) is int and owner["inode"] > 0
            and owner.get("path") == private_root + "/" + phase_name + suffix,
            "reject altered corrected native artifact metadata: " + role)
    return owner


def audit_identity(value, role):
    require(type(value) is dict and value.get("role") == role
            and value.get("external_regex_dependency_count") == 0
            and value.get("stdlib_regex_engine_count") == 0
            and value.get("cross_family_engine_count") == 0
            and value.get("python_code_loader_count") == 0
            and value.get("general_python_import_count") == 0
            and value.get("native_loader_dependency_count") == 0
            and value.get("copyreg_import_is_matching_engine") is False
            and value.get("copyreg_import_requires_exact_complete_bridge_sha256")
            == BRIDGE_SOURCE[1]
            and value.get("benign_copyreg_import_count")
            == (1 if role == "bridge" else 0)
            and value.get("benign_copyreg_import")
            == ("copyreg" if role == "bridge" else None),
            "reject an external engine, Python loader, or unbounded copyreg exception")


def frozen_context(source_sha, protocol_sha, contract_sha=None):
    clean()
    own = dynamic_owner(SELF, source_sha)
    document = dynamic_owner(PROTOCOL, protocol_sha)
    allowed = {ROOT + "/" + item[0] for item in owner_list()}
    allowed.update((ROOT + "/" + SELF, ROOT + "/" + PROTOCOL))
    if contract_sha is not None:
        allowed.add(ROOT + "/" + CONTRACT)
    with SourceWall(allowed) as wall:
        read_owner(own)
        read_owner(document)
        for item in owner_list():
            read_owner(item)
        producer = load_module(PRODUCER[0], "_rebar_zig_v16_frozen_json_only")
        parse = lambda item: producer.JsonReader(read_owner(item)).parse()
        matrix = parse(P0[1])
        gate = matrix.get("phase_gate", {})
        require(matrix.get("schema") == "rebar-cpython-re-p0-completeness-v4"
                and matrix.get("version") == 4 and matrix.get("status") == "PASS"
                and matrix.get("original_case_execution_denominator") == 31237
                and matrix.get("original_suite_count") == 13
                and matrix.get("original_named_private_waiver_count") == 13
                and matrix.get("original_obligation_count") == 73
                and matrix.get("original_crosswalk_count") == 34
                and gate.get("status") == "PASS"
                and gate.get("candidate_evaluation_authorized") is True
                and gate.get("performance_oracle_authorized") is False
                and gate.get("final_holdout_authorized") is False
                and tuple((row.get("id"), row.get("case_execution_count"))
                          for row in matrix.get("original_oracle", {}).get("suites", []))
                == SUITES,
                "reject a changed original P0 matrix or a premature performance gate")
        manifest = parse(P0[2])
        require(type(manifest.get("suites")) is list and len(manifest["suites"]) == 13,
                "reject an incomplete original baseline manifest")
        fuzz = parse(P0[3])
        require(fuzz.get("status") == "PASS"
                and fuzz.get("actual_reference_worker_count") == 2
                and fuzz.get("supplemental_case_count") == 8244
                and fuzz.get("holdout") == "NOT OPENED",
                "reject the independently preserved differential reference")
        producer_contract = parse(PRODUCER[2])
        zig = [row for row in producer_contract.get("families", [])
               if row.get("name") == FAMILY]
        require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
                and producer.CASE_DENOMINATOR == 31237
                and producer.SUITE_COUNT == 13
                and producer.PRIVATE_WAIVER_COUNT == 13
                and producer.ORIGINAL_OBLIGATION_COUNT == 73
                and producer.ORIGINAL_CROSSWALK_COUNT == 34
                and producer.SUPPLEMENTAL_CASE_COUNT == 8244
                and tuple((row.name, row.case_count) for row in producer.SUITES)
                == SUITES and len(zig) == 1 and zig[0].get("owned_ctypes") is True,
                "reject the frozen complete first-party original producer")
        guard = validate_v4_guard(parse(GUARD[2]))
        legacy = parse(LEGACY[2])
        require(legacy.get("schema")
                == "rebar-owned-repaired-zig-original-campaign-v13-guarded-lifetime-source-freeze"
                and legacy.get("version") == 13 and legacy.get("family") == FAMILY
                and legacy.get("source") == owner_record(LEGACY[0])
                and legacy.get("protocol") == owner_record(LEGACY[1])
                and legacy.get("holdout") == "NOT OPENED",
                "reject substituted observer/recorder source history")
        build_contract = parse(BUILD[2])
        sources = build_contract.get("complete_first_party_sources", {})
        require(build_contract.get("schema")
                == "rebar-owned-zig-full-semantic-source-build-v16-source-freeze"
                and build_contract.get("version") == 16
                and build_contract.get("goal_sha256") == GOAL[1]
                and sources.get("engine", {}).get("sha256") == ENGINE_SOURCE[1]
                and sources.get("engine", {}).get("path") == ENGINE_SOURCE[0]
                and sources.get("corrected_bridge", {}).get("sha256") == BRIDGE_SOURCE[1]
                and sources.get("corrected_bridge", {}).get("path") == BRIDGE_SOURCE[0]
                and sources.get("corrected_adapter", {}).get("sha256") == ADAPTER_SOURCE[1]
                and sources.get("corrected_adapter", {}).get("path") == ADAPTER_SOURCE[0]
                and sources.get("external_regex_engine_count") == 0
                and sources.get("external_regex_package_count") == 0
                and sources.get("stdlib_re_engine_count") == 0
                and sources.get("stdlib_sre_engine_count") == 0
                and sources.get("cross_candidate_engine_count") == 0
                and sources.get("matching_fallback_count") == 0,
                "reject substituted or delegated corrected first-party Zig sources")
        historical = parse(HISTORY)
        require(historical.get("status") == "PASS"
                and historical.get("candidate_status") == "FAIL"
                and historical.get("case_execution_denominator") == 31237
                and historical.get("suite_count") == 13
                and historical.get("completed_suite_count") == 12
                and historical.get("verified_passing_case_count") == 4607
                and historical.get("observed_semantic_mismatch_lower_bound") == 1700
                and historical.get("semantic_mismatch_count") == "NOT MEASURED"
                and historical.get("infrastructure_failure_count") == 1
                and len(historical.get("original_suite_diagnostics", [])) == 13
                and historical.get("candidate_qualified") is False,
                "preserve every measured historical mismatch without opening its archive")
        build = parse(BUILD[3])
        root = parse(BUILD[4])
        actual = build.get("complete_actual_build", {})
        private_root = root.get("private_root", {})
        require(build.get("schema")
                == "rebar-owned-zig-full-semantic-source-build-v16-plaintext-build-receipt"
                and build.get("status") == "PASS" and build.get("label") == BUILD_LABEL
                and build.get("source_sha256") == BUILD[0][1]
                and build.get("protocol_sha256") == BUILD[1][1]
                and build.get("contract_sha256") == BUILD[2][1]
                and build.get("private_root_receipt_sha256") == BUILD[4][1]
                and root.get("schema")
                == "rebar-owned-zig-full-semantic-source-build-v16-private-root-receipt"
                and root.get("status") == "PASS" and root.get("label") == BUILD_LABEL
                and root.get("source_sha256") == BUILD[0][1]
                and root.get("protocol_sha256") == BUILD[1][1]
                and root.get("contract_sha256") == BUILD[2][1]
                and root.get("private_root_retained") is True
                and type(private_root.get("path")) is str
                and private_root["path"].startswith(
                    "/tmp/rebar-phase2-zig-full-semantic-source-build-v16-")
                and private_root.get("device") == PRIVATE_DEVICE
                and private_root.get("mode") == "0700"
                and private_root.get("uid") == os.geteuid()
                and actual.get("status") == "PASS"
                and actual.get("family") == FAMILY
                and actual.get("label") == BUILD_LABEL
                and actual.get("actual_process_count") == 26
                and actual.get("actual_source_snapshot_count") == 6
                and actual.get("original_case_execution_denominator") == 31237
                and actual.get("original_suite_count") == 13
                and actual.get("original_named_private_waiver_count") == 13
                and actual.get("corrected_adapter_sha256") == ADAPTER_SOURCE[1]
                and actual.get("first_party_bridge_source_sha256") == BRIDGE_SOURCE[1]
                and actual.get("first_party_engine_source_sha256") == ENGINE_SOURCE[1]
                and actual.get("historical_zig_failure_receipt_sha256") == HISTORY[1]
                and actual.get("historical_zig_observed_mismatch_lower_bound") == 1700
                and actual.get("strict_runtime_guard_version") == 4
                and actual.get("strict_runtime_guard_contract_sha256") == GUARD[2][1]
                and actual.get("external_regex_dependency_count") == 0
                and actual.get("cross_family_engine_count") == 0
                and actual.get("candidate_workers_started") == 0
                and actual.get("candidate_imports") == 0
                and actual.get("native_activations") == 0
                and actual.get("holdout") == "NOT OPENED"
                and root.get("corrected_adapter_sha256") == ADAPTER_SOURCE[1]
                and root.get("corrected_bridge_source_sha256") == BRIDGE_SOURCE[1]
                and root.get("first_party_engine_source_sha256") == ENGINE_SOURCE[1]
                and root.get("strict_runtime_guard_version") == 4
                and root.get("strict_runtime_guard_contract_sha256") == GUARD[2][1]
                and root.get("historical_zig_failure_sha256") == HISTORY[1]
                and root.get("historical_zig_observed_mismatch_lower_bound") == 1700,
                "reject false full-source private-build receipt provenance")
        exception = actual.get("copyreg_compatibility_exception", {})
        require(exception.get("allowed_import_count") == 1
                and exception.get("allowed_role") == "bridge"
                and exception.get("literal_module") == "copyreg"
                and exception.get("engine_import_allowed") is False
                and exception.get("other_python_module_import_allowed") is False
                and exception.get("external_regex_engine_count") == 0
                and exception.get("required_complete_bridge_sha256") == BRIDGE_SOURCE[1],
                "never expand the single digest-bound nonmatching copyreg exception")
        phases = actual.get("build_phases", [])
        roots = root.get("phases", [])
        require(len(phases) == len(roots) == 2
                and [row.get("name") for row in phases]
                == [row.get("name") for row in roots]
                == ["reference-a", "reference-b"]
                and root.get("phase_names") == ["reference-a", "reference-b"],
                "reject an incomplete independently rebuilt Zig pair")
        seen = set()
        for phase, root_phase in zip(phases, roots):
            name = phase["name"]
            snapshots = phase.get("source_snapshots", {})
            rooted = root_phase.get("source_snapshots", {})
            require(type(snapshots) is dict and len(snapshots) == 3
                    and type(rooted) is dict
                    and set(snapshots) == set(rooted)
                    == {"candidates/zig/mini_regex.zig",
                        "candidates/zig/py_bridge.c",
                        "candidates/zig_candidate.py"},
                    "reject omitted corrected native-build snapshots")
            expected = (("engine_source", "candidates/zig/mini_regex.zig"),
                        ("bridge_source", "candidates/zig/py_bridge.c"),
                        ("adapter", "candidates/zig_candidate.py"))
            for role, key in expected:
                observed = snapshots[key]
                source = snapshot_identity(observed, role, name, private_root["path"])
                require(rooted[key] == source,
                        "reject crossed canonical snapshot-to-variant provenance")
                require(source["inode"] not in seen,
                        "reject reused supposedly independent source snapshot")
                seen.add(source["inode"])
            for role in ("engine", "bridge"):
                artifact = phase.get("native_outputs", {}).get(role, {})
                rooted_artifact = root_phase.get("native_outputs", {}).get(role, {})
                identity = native_identity(artifact.get("owner"), role, name,
                                           private_root["path"])
                require(rooted_artifact.get("owner") == identity,
                        "reject crossed public/private native provenance")
                require(identity["inode"] not in seen,
                        "reject reused independently compiled native inode")
                seen.add(identity["inode"])
                audit_identity(artifact.get("independence_audit"), role)
                audit_identity(rooted_artifact.get("independence_audit"), role)
        if contract_sha is not None:
            current = dynamic_owner(CONTRACT, contract_sha)
            contract = producer.JsonReader(read_owner(current)).parse()
            require(contract == contract_value(source_sha, protocol_sha,
                                               matrix, guard, build, root,
                                               historical),
                    "reject an altered or silently weakened source contract")
        else:
            contract = None
        clean()
        return {"producer": producer, "manifest": manifest, "matrix": matrix,
                "guard": guard, "build": build, "build_root": root,
                "history": historical, "contract": contract,
                "source_sha256": source_sha, "protocol_sha256": protocol_sha,
                "contract_sha256": contract_sha,
                "audited_source_event_count": wall.audit_count,
                "private_root_metadata_only": True}


def contract_value(source_sha, protocol_sha, matrix, guard, build, root, historical):
    own = dynamic_owner(SELF, source_sha)
    protocol = dynamic_owner(PROTOCOL, protocol_sha)
    return {
        "schema": SCHEMA + "-source-freeze", "version": 16,
        "status": "SOURCE FROZEN; CORRECTED FIRST-PARTY ZIG ORIGINAL MATCHING NOT RUN",
        "source": owner_record(own), "protocol": owner_record(protocol),
        "goal_sha256": GOAL[1], "family": FAMILY, "label": LABEL,
        "pinned_python": {"path": PYTHON, "version": "3.14.6", "sha256": PYTHON_SHA256},
        "original_oracle": {
            "case_execution_denominator": 31237, "suite_count": 13,
            "named_private_waiver_count": 13, "obligation_count": 73,
            "crosswalk_count": 34, "suites": [
                {"name": name, "case_count": count} for name, count in SUITES
            ], "supplemental_case_count": 8244,
            "supplemental_cases_counted_in_original_denominator": False,
            "phase_gate_status": matrix["phase_gate"]["status"],
        },
        "immutable_producer_v5": {"owners": [owner_record(item) for item in PRODUCER]},
        "strict_runtime_guard_v4": {
            "owners": [owner_record(item) for item in GUARD], "version": 4,
            "executed_in_source_modes": False,
            "native_owner_field_count": 14,
            "native_owner_fields": sorted(NATIVE_OWNER_FIELDS),
            "interpreter_creation_audit_event": "NOT EMITTED TO PARENT PYTHON AUDIT HOOK",
            "expected_interpreters_created": 11,
            "expected_interpreters_destroyed": 11,
            "expected_case_interpreter_exec_calls": 394,
            "expected_bootstrap_interpreter_exec_calls": 11,
            "expected_cleanup_interpreter_exec_calls": 11,
            "expected_total_real_interpreter_exec_calls": 416,
        },
        "legacy_recorder_v13": {"owners": [owner_record(item) for item in LEGACY],
                                  "unsafe_context_executed": False,
                                  "proposal_files_opened": 0},
        "complete_first_party_build_v16": {
            "owners": [owner_record(item) for item in BUILD],
            "label": BUILD_LABEL, "phase_names": ["reference-a", "reference-b"],
            "actual_build_process_count": 26, "corrected_engine_source": owner_record(ENGINE_SOURCE),
            "corrected_bridge_source": owner_record(BRIDGE_SOURCE),
            "corrected_adapter_source": owner_record(ADAPTER_SOURCE),
            "engine_native": {"sha256": NATIVE["engine"][0], "bytes": NATIVE["engine"][1]},
            "bridge_native": {"sha256": NATIVE["bridge"][0], "bytes": NATIVE["bridge"][1]},
            "private_root_metadata_only": True,
            "external_regex_dependency_count": 0,
            "cross_family_engine_count": 0,
            "copyreg_compatibility_exception": build["complete_actual_build"]["copyreg_compatibility_exception"],
        },
        "historical_original_campaign": {
            "owner": owner_record(HISTORY), "candidate_status": "FAIL",
            "verified_passing_case_count": historical["verified_passing_case_count"],
            "observed_semantic_mismatch_lower_bound": 1700,
            "semantic_mismatch_count": "NOT MEASURED",
            "completed_suite_count": 12, "infrastructure_failure_count": 1,
            "compressed_archive_opened": False,
        },
        "activation": {"roles": list(ROLES), "restoration_order": list(RESTORE),
                       "journaled": True, "exact_original_inode_restoration": True,
                       "private_build_phase": "reference-a",
                       "root_authorization_required": True,
                       "committed_pushed_freeze_required": True},
        "source_only_effects": {key: 0 for key in SOURCE_EFFECTS},
        "corrected_original_matching": "NOT RUN", "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED", "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    }


def source_result(mode, args):
    state = frozen_context(args["--source-sha256"], args["--protocol-sha256"],
                           None if mode == "--render-contract"
                           else args["--contract-sha256"])
    if mode == "--render-contract":
        return state["producer"].canonical(contract_value(
            args["--source-sha256"], args["--protocol-sha256"],
            state["matrix"], state["guard"], state["build"],
            state["build_root"], state["history"]))
    checks = source_self_test(state) if mode == "--self-test" else 0
    return state["producer"].canonical({
        "schema": SCHEMA + "-source-only-result", "status": "PASS",
        "mode": mode, "source_sha256": args["--source-sha256"],
        "protocol_sha256": args["--protocol-sha256"],
        "contract_sha256": args["--contract-sha256"],
        "suite_count": 13, "original_case_execution_denominator": 31237,
        "named_private_waiver_count": 13,
        "historical_observed_semantic_mismatch_lower_bound": 1700,
        "build_process_count_previously_observed": 26,
        "runtime_guard_version": 4,
        "self_test_control_count": checks,
        "source_only_effects": {key: 0 for key in SOURCE_EFFECTS},
        "candidate_matching": "NOT RUN", "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "winner_selected": False,
    })


def rejected(operation, label):
    try:
        operation()
    except (CampaignError, OSError, ImportError, ValueError, TypeError):
        return 1
    raise CampaignError("accepted hostile source-only control: " + label)


def source_self_test(state):
    allowed = {ROOT + "/" + item[0] for item in owner_list()}
    allowed.update((ROOT + "/" + SELF, ROOT + "/" + PROTOCOL,
                    ROOT + "/" + CONTRACT))
    checks = 0
    with SourceWall(allowed):
        for name in ("re", "_sre", "regex", "ctypes", "subprocess", "copyreg",
                     "candidates", "candidates.zig_candidate", "_interpreters"):
            checks += rejected(lambda value=name: builtins.__import__(value), name)
        for path in (RECOVERY,
                     state["build_root"]["private_root"]["path"],
                     ROOT + "/candidates/_zig_probe.so",
                     ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                     ROOT + "/candidates/zig_candidate.py",
                     ROOT + "/" + ADAPTER_SOURCE[0],
                     ROOT + "/" + BRIDGE_SOURCE[0],
                     ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
                     ROOT + "/performance/final-holdout.json",
                     ROOT + "/.git/config"):
            checks += rejected(lambda value=path: os.open(value, os.O_RDONLY), path)
        for event in ("subprocess.Popen", "socket.connect", "ctypes.dlopen",
                      "cpython.PyInterpreterState_New", "_interpreters.create",
                      "_interpreters.exec"):
            checks += rejected(lambda value=event: sys.audit(value), event)
        raw = read_owner(dynamic_owner(SELF, state["source_sha256"]))
        tree = ast.parse(raw.decode("utf-8"), filename=ROOT + "/" + SELF)
        workers = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == "worker"]
        require(len(workers) == 1, "reject omitted root-only V4 worker source")
        calls = sorted((node.lineno, node.func.attr, node)
                       for node in ast.walk(workers[0])
                       if isinstance(node, ast.Call)
                       and isinstance(node.func, ast.Attribute)
                       and isinstance(node.func.value, ast.Name)
                       and ((node.func.value.id == "policy"
                             and node.func.attr in ("install", "prepare_family"))
                            or (node.func.value.id == "importlib"
                                and node.func.attr == "import_module")))
        install = [line for line, name, _ in calls if name == "install"]
        prepare = [line for line, name, _ in calls if name == "prepare_family"]
        imports = [line for line, name, node in calls
                   if name == "import_module" and len(node.args) == 1
                   and isinstance(node.args[0], ast.Constant)
                   and node.args[0].value == "candidates.zig_candidate"]
        require(len(install) == len(prepare) == len(imports) == 1
                and install[0] < prepare[0] < imports[0],
                "require V4 installation and native preparation before sole candidate import")
        checks += 1
    clean()
    return checks


def validate_authority(args, worker=False):
    require(args.get("--root-authorized") is True
            and args.get("--frozen-committed-pushed") is True
            and args.get("--family") == FAMILY and args.get("--label") == LABEL
            and all(args.get(name) == value for name, value in ACTUAL_PINS),
            "require every root, oracle, build, guard, native, and source authority")
    commit = args.get("--frozen-commit")
    pushed = args.get("--pushed-commit")
    require(type(commit) is str and len(commit) == 40
            and all(character in "0123456789abcdef" for character in commit)
            and pushed == commit,
            "require the same complete root-observed committed and pushed freeze")
    if worker:
        require(args.get("--suite") in dict(SUITES),
                "reject a substituted or absent original worker suite")


def patched_legacy(state):
    legacy = load_module(LEGACY[0], "_rebar_zig_v16_authenticated_original_recorder")
    legacy.SELF = SELF
    legacy.PROTOCOL = PROTOCOL
    legacy.CONTRACT = CONTRACT
    legacy.SCHEMA = SCHEMA
    legacy.FAMILY = FAMILY
    legacy.LABEL = LABEL
    legacy.BUILD_LABEL = BUILD_LABEL
    legacy.RECOVERY = RECOVERY
    legacy.GUARD = GUARD
    legacy.GUARD_V2 = GUARD_V2
    legacy.PRODUCER = PRODUCER
    legacy.NATIVE = dict(NATIVE)
    legacy.LIFETIME_ADAPTER = ADAPTER_SOURCE
    legacy.PARENT_ADAPTER = ADAPTER_SOURCE
    legacy.ORIGINAL_ADAPTER = (ORIGINALS["adapter"]["relative"],
                               ORIGINALS["adapter"]["sha256"],
                               ORIGINALS["adapter"]["bytes"],
                               ORIGINALS["adapter"]["inode"])
    legacy.BRIDGE_SOURCE = BRIDGE_SOURCE
    legacy.ENGINE_SOURCE = ENGINE_SOURCE
    legacy.ORIGINALS = dict(ORIGINALS)
    legacy.ACTUAL_CALLER_PINS = ACTUAL_PINS
    legacy.require_actual_authority = validate_authority
    legacy.context = forbidden_legacy_context
    legacy.verify = lambda source, protocol, contract, active=False: (
        frozen_context(source, protocol, contract)
    )
    legacy.private_owner = private_owner
    legacy.prepare = lambda current: prepare(legacy, current)
    legacy.read_live_journal = lambda producer, journal_sha: read_live_journal(
        legacy, producer, journal_sha)
    legacy.recovery_directory = lambda create: recovery_directory(legacy, create)
    legacy.names = names
    legacy.worker = lambda args, bootstrap_hook=None: worker(
        args, state=state, legacy=legacy, bootstrap_hook=bootstrap_hook)
    legacy.command = lambda args, suite, journal_sha: command(args, suite, journal_sha)
    legacy.publication_stem = publication_stem
    return legacy


def forbidden_legacy_context(*_args, **_kwargs):
    raise CampaignError("unsafe historical V13 proposal/context execution is forbidden")


def names(role):
    require(role in ROLES, "reject a crossed activation role")
    stem = ".rebar-zig-full-semantic-original-v16-" + role
    return stem + ".stage", stem + ".original"


def recovery_directory(legacy, create):
    require(os.path.dirname(RECOVERY) == "/tmp"
            and RECOVERY.startswith("/tmp/rebar-phase2-repaired-zig-original-campaign-v16-"),
            "reject an unsafe exact recovery target")
    if create:
        try:
            os.mkdir(RECOVERY, 0o700)
        except FileExistsError:
            pass
    descriptor = os.open(RECOVERY, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_DIRECTORY", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "reject a substituted root-owned recovery directory")
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT
        lock = os.open("campaign-v16.lock", flags, 0o600, dir_fd=descriptor)
        try:
            identity = os.fstat(lock)
            require(stat.S_ISREG(identity.st_mode)
                    and stat.S_IMODE(identity.st_mode) == 0o600
                    and identity.st_uid == os.geteuid() and identity.st_nlink == 1,
                    "reject an unsafe V16 campaign lock")
            fcntl = __import__("fcntl")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(lock)
            raise
        return descriptor, lock
    except BaseException:
        os.close(descriptor)
        raise


def private_owner(owner, role):
    if role == "adapter":
        expected = ADAPTER_SOURCE[1:3]
        suffix = "/reference-a/source/candidates/zig_candidate.py"
        mode = 0o600
    else:
        expected = NATIVE[role]
        suffix = "/reference-a/native/" + (
            "_zig_probe.so" if role == "engine"
            else "_zig_bridge.cpython-314-x86_64-linux-gnu.so")
        mode = 0o700
    require(type(owner) is dict and type(owner.get("path")) is str
            and owner["path"].startswith(
                "/tmp/rebar-phase2-zig-full-semantic-source-build-v16-")
            and owner["path"].endswith(suffix)
            and owner.get("device") == PRIVATE_DEVICE
            and owner.get("uid") == os.geteuid() and owner.get("nlink") == 1
            and owner.get("sha256") == expected[0]
            and owner.get("bytes") == expected[1]
            and owner.get("mode") == format(mode, "04o"),
            "reject an altered root-authorized private artifact: " + role)
    descriptor = REAL_OPEN(owner["path"], os.O_RDONLY
                           | getattr(os, "O_CLOEXEC", 0)
                           | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and before.st_dev == PRIVATE_DEVICE
                and before.st_ino == owner["inode"]
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == mode
                and before.st_size == expected[1],
                "reject changed actual private artifact identity")
        chunks, remaining = [], before.st_size
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            require(bool(chunk), "reject a truncated actual private artifact")
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        require(not os.read(descriptor, 1) and digest(raw) == expected[0],
                "reject substituted actual first-party private bytes")
        return raw
    finally:
        os.close(descriptor)


def prepare(legacy, state):
    for role in ROLES:
        legacy.target_identity(role, ORIGINALS[role])
    phase = state["build"]["complete_actual_build"]["build_phases"][0]
    phase_root = state["build_root"]["phases"][0]
    data = {
        "engine": private_owner(phase["native_outputs"]["engine"]["owner"], "engine"),
        "bridge": private_owner(phase["native_outputs"]["bridge"]["owner"], "bridge"),
        "adapter": private_owner(phase_root["source_snapshots"]["candidates/zig_candidate.py"],
                                  "adapter"),
    }
    recovery_fd, lock_fd = recovery_directory(legacy, True)
    candidate_fd = legacy.candidate_directory()
    journal = None
    stages = {}
    try:
        for role in ROLES:
            stage, _ = names(role)
            stages[role] = legacy.exclusive(candidate_fd, stage, data[role])
            expected = ADAPTER_SOURCE[1] if role == "adapter" else NATIVE[role][0]
            require(stages[role]["device"] == DEVICE
                    and stages[role]["sha256"] == expected,
                    "require exact mode-0600 repository-device corrected stages")
        producer = state["producer"]
        journal = {
            "schema": SCHEMA + "-three-role-journal", "status": "PREPARED",
            "family": FAMILY, "label": LABEL, "build_label": BUILD_LABEL,
            "build_receipt_sha256": BUILD[3][1],
            "root_receipt_sha256": BUILD[4][1],
            "recovery_root": RECOVERY, "role_order": list(ROLES),
            "restoration_order": list(RESTORE), "atomic_group": False,
            "lifetime_adapter_sha256": ADAPTER_SOURCE[1],
            "corrected_adapter_sha256": ADAPTER_SOURCE[1],
            "strict_runtime_guard_version": 4,
            "strict_runtime_guard_contract_sha256": GUARD[2][1],
            "roles": {role: {"original": ORIGINALS[role],
                             "stage": stages[role], "backup_name": names(role)[1],
                             "stage_name": names(role)[0]} for role in ROLES},
        }
        with legacy.CriticalSignals():
            journal_owner = legacy.exclusive(recovery_fd, "recovery-journal.json",
                                             producer.canonical(journal))
            journal["published_journal"] = journal_owner
            for role in ROLES:
                target = ORIGINALS[role]["relative"].rsplit("/", 1)[1]
                stage, backup = names(role)
                os.link(target, backup, src_dir_fd=candidate_fd,
                        dst_dir_fd=candidate_fd, follow_symlinks=False)
                os.fsync(candidate_fd)
                os.replace(stage, target, src_dir_fd=candidate_fd,
                           dst_dir_fd=candidate_fd)
                os.fsync(candidate_fd)
                legacy.exclusive(recovery_fd, "activation-" + role + ".json",
                                 producer.canonical({
                                     "schema": SCHEMA + "-activation-step",
                                     "status": "PASS", "role": role,
                                     "journal_sha256": journal_owner["sha256"],
                                 }))
        return recovery_fd, lock_fd, candidate_fd, journal
    except BaseException as primary:
        recovery_failure = None
        try:
            if journal is not None:
                with legacy.CriticalSignals():
                    legacy.restore(candidate_fd, journal)
            for role, stage in stages.items():
                stage_name, _ = names(role)
                try:
                    identity = os.stat(stage_name, dir_fd=candidate_fd,
                                       follow_symlinks=False)
                except FileNotFoundError:
                    continue
                require(identity.st_dev == stage["device"]
                        and identity.st_ino == stage["inode"]
                        and identity.st_uid == os.geteuid()
                        and identity.st_nlink == 1
                        and stat.S_IMODE(identity.st_mode) == 0o600,
                        "refuse cleanup of an unrelated user-owned stage")
                os.unlink(stage_name, dir_fd=candidate_fd)
                os.fsync(candidate_fd)
        except BaseException as error:
            recovery_failure = error
        finally:
            os.close(candidate_fd)
            os.close(lock_fd)
            os.close(recovery_fd)
        if recovery_failure is not None:
            raise CampaignError("actual activation failed; exact recovery needs the "
                                "published root journal: "
                                + type(recovery_failure).__qualname__ + ": "
                                + str(recovery_failure)) from primary
        raise


def read_live_journal(legacy, producer, expected_sha):
    expected_sha = sha(expected_sha, "actual recovery journal")
    directory = os.open(RECOVERY, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                        | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0))
    try:
        identity = os.fstat(directory)
        require(stat.S_ISDIR(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o700
                and identity.st_uid == os.geteuid(),
                "reject a substituted live actual recovery directory")
        descriptor = os.open("recovery-journal.json", os.O_RDONLY
                             | getattr(os, "O_CLOEXEC", 0)
                             | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        try:
            info = os.fstat(descriptor)
            require(stat.S_ISREG(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o600
                    and info.st_uid == os.geteuid() and info.st_nlink == 1
                    and 0 < info.st_size < MAX_BYTES,
                    "reject an unsafe actual V16 recovery journal")
            chunks, remaining = [], info.st_size
            while remaining:
                chunk = os.read(descriptor, min(262144, remaining))
                require(bool(chunk), "reject truncated actual recovery journal")
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b"".join(chunks)
            require(not os.read(descriptor, 1) and digest(raw) == expected_sha,
                    "reject an unannounced actual activation journal")
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)
    journal = producer.JsonReader(raw).parse()
    require(journal.get("schema") == SCHEMA + "-three-role-journal"
            and journal.get("family") == FAMILY and journal.get("label") == LABEL
            and journal.get("build_receipt_sha256") == BUILD[3][1]
            and journal.get("root_receipt_sha256") == BUILD[4][1]
            and journal.get("corrected_adapter_sha256") == ADAPTER_SOURCE[1]
            and journal.get("lifetime_adapter_sha256") == ADAPTER_SOURCE[1]
            and journal.get("strict_runtime_guard_version") == 4
            and journal.get("strict_runtime_guard_contract_sha256") == GUARD[2][1]
            and journal.get("role_order") == list(ROLES)
            and journal.get("restoration_order") == list(RESTORE)
            and set(journal.get("roles", {})) == set(ROLES),
            "reject forged or crossed actual corrected three-role activation")
    return journal


def worker(args, *, state=None, legacy=None, bootstrap_hook=None):
    stage = "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
    suite_name = None
    suite_count = None
    installed = False
    imported = False
    observer_proxy = None
    synthetic = bootstrap_hook is not None
    try:
        require(type(args) is dict, "reject noncanonical actual worker arguments")
        suite_name = args.get("--suite")
        suite_count = dict(SUITES).get(suite_name)
        if bootstrap_hook is not None:
            require(callable(bootstrap_hook), "reject uncallable synthetic control")
            bootstrap_hook()
        stage = "VERIFY_ACTIVE_FROZEN_CONTEXT"
        state = frozen_context(args["--source-sha256"], args["--protocol-sha256"],
                               args["--contract-sha256"]) if state is None else state
        producer = state["producer"]
        legacy = patched_legacy(state) if legacy is None else legacy
        stage = "VALIDATE_PINNED_WORKER_AUTHORITY"
        validate_authority(args, worker=True)
        stage = "READ_AUTHENTICATED_ACTIVE_RECOVERY_JOURNAL"
        journal = read_live_journal(legacy, producer,
                                   args["--recovery-journal-sha256"])
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_ENGINE"
        engine = legacy.active_owner("engine", journal["roles"]["engine"]["stage"])
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_BRIDGE"
        bridge = legacy.active_owner("bridge", journal["roles"]["bridge"]["stage"])
        stage = "AUTHENTICATE_ACTIVE_CORRECTED_ADAPTER"
        legacy.active_owner("adapter", journal["roles"]["adapter"]["stage"])
        stage = "VERIFY_CLEAN_PRE_GUARD_MODULE_STATE"
        clean()
        stage = "LOAD_IMMUTABLE_FIRST_PARTY_RUNTIME_GUARD_V4"
        guard = load_module(GUARD[0], "_rebar_zig_v16_exact_runtime_guard_v4")
        stage = "CONSTRUCT_IMMUTABLE_RUNTIME_POLICY"
        policy = guard.RuntimePolicy()
        require(guard.SELF == GUARD[0][0]
                and guard.PROTOCOL == GUARD[1][0]
                and guard.CONTRACT == GUARD[2][0]
                and type(policy).prepare_family is guard.BASE.RuntimePolicy.prepare_family
                and type(policy).prepare_family.__globals__ is guard.BASE.__dict__
                and type(policy).prepare_family.__globals__["SELF"] == GUARD_V2[0][0]
                and type(policy).prepare_family.__globals__["PROTOCOL"] == GUARD_V2[1][0]
                and type(policy).prepare_family.__globals__["CONTRACT"] == GUARD_V2[2][0]
                and type(policy).prepare_family.__code__.co_filename
                == ROOT + "/" + GUARD_V2[0][0]
                and guard.child_bootstrap_source is guard.BASE.child_bootstrap_source
                and guard.NATIVE_OWNER_KEYS == NATIVE_OWNER_FIELDS,
                "reject V4 without the exact immutable V2 native/child policy")
        stage = "INSTALL_IMMUTABLE_RUNTIME_GUARD_V4"
        policy.install()
        installed = True
        stage = "PREPARE_AUTHENTICATED_FIRST_PARTY_NATIVE_FAMILY"
        policy.prepare_family(FAMILY, bridge_owner=bridge, engine_owner=engine)
        stage = "AUTHENTICATE_GUARDED_FIRST_PARTY_NAMESPACE"
        namespace = legacy.authenticated_first_party_namespace()
        stage = "PREPEND_AUTHENTICATED_ISOLATED_FIRST_PARTY_ROOT"
        legacy.prepend_authenticated_first_party_namespace(namespace)
        stage = "VERIFY_RUNTIME_GUARD_BEFORE_CANDIDATE_IMPORT"
        require(installed and policy.installed and policy.prepared_family == FAMILY
                and sys.path[0] == ROOT and "candidates" not in sys.modules
                and "candidates.zig_candidate" not in sys.modules
                and "re" not in sys.modules and "_sre" not in sys.modules,
                "require strict genuine V4 before the sole first-party candidate import")
        stage = "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE"
        candidate = importlib.import_module("candidates.zig_candidate")
        imported = True
        stage = "BIND_SELECTED_FIRST_PARTY_CANDIDATE"
        policy.bind_selected(candidate, FAMILY)
        stage = "BUILD_IMMUTABLE_FIRST_PARTY_FAMILY_SPEC"
        base = producer.family_spec(FAMILY)
        source_owners = (
            (ORIGINALS["adapter"]["relative"], ADAPTER_SOURCE[1], ADAPTER_SOURCE[2]),
            (ENGINE_SOURCE[0], ENGINE_SOURCE[1], ENGINE_SOURCE[2]),
            (BRIDGE_SOURCE[0], BRIDGE_SOURCE[1], BRIDGE_SOURCE[2]),
        )
        selected = producer.FamilySpec(base.name, base.module, base.adapter_relative,
                                       base.bridge_module, base.engine_relative,
                                       base.bridge_relative, source_owners,
                                       False, False)
        stage = "VERIFY_GUARDED_FIRST_PARTY_FAMILY_IDENTITY"
        require(producer.family_spec(FAMILY) is base and base.owned_ctypes is True
                and selected.owned_ctypes is False
                and producer.require_selected(selected) is candidate
                and policy.selected is candidate and sys.modules.get("re") is candidate,
                "preserve exact immutable original producer and first-party alias")
        pins = {"source": ADAPTER_SOURCE[1], "native_engine": NATIVE["engine"][0],
                "native_bridge": NATIVE["bridge"][0]}
        source_pins = {path: value for path, value, _ in source_owners}
        stage = "INSTALL_AUTHENTICATED_ZIG_OBSERVER_SOURCE_PROXY"
        observer_proxy = legacy.install_authenticated_zig_observer_proxy(
            producer, selected, policy)
        stage = "RESOLVE_IMMUTABLE_ORIGINAL_SUITE"
        suite = producer.suite_spec(args["--suite"])
        suite_name, suite_count = suite.name, suite.case_count
        if suite.name == "original_bounded_v5":
            stage = "OBSERVE_COMPLETE_UPSTREAM_ORIGINAL_SUITE"
            observation = producer.observe_original_upstream(suite, selected,
                                                            pins, source_pins)
        elif suite.name == "subinterpreter_v2":
            stage = "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
            observation = producer.observe_subinterpreters(
                suite, selected, pins, source_pins,
                producer_sha256=PRODUCER[0][1])
        else:
            stage = "OBSERVE_COMPLETE_DIRECT_ORIGINAL_SUITE"
            observation = producer.observe_direct_suite(
                suite, selected, pins, source_pins, state["manifest"])
        stage = "VALIDATE_COMPLETE_ORIGINAL_SUITE_OBSERVATION"
        require(type(observation) is dict and observation.get("suite") == suite.name
                and observation.get("candidate_family") == FAMILY
                and observation.get("case_execution_denominator") == suite.case_count
                and observation.get("actual_candidate_workers") == 1
                and observation.get("hidden_cases_read") == 0
                and observation.get("benchmark_files_read") == 0
                and observation.get("holdout") == "NOT OPENED",
                "reject omitted or fabricated genuine original records")
        return {"schema": SCHEMA + "-actual-suite-worker",
                "status": observation.get("status"), "family": FAMILY,
                "label": LABEL, "suite": suite.name,
                "case_execution_denominator": suite.case_count,
                "complete_actual_observation": observation,
                "activation_stage": "COMPLETE_ORIGINAL_OBSERVATION",
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import": True,
                "candidate_imported": True, "actual_candidate_workers": 1,
                "synthetic_control": False,
                "observer_source_proxy": dict(observer_proxy),
                "hidden_cases_read": 0, "benchmark_files_read": 0,
                "timing_trials_run": 0, "holdout": "NOT OPENED",
                "performance": "NOT MEASURED", "winner_selected": False}
    except BaseException as error:
        failure = (legacy.failure_details(error, stage) if legacy is not None else
                   {"error_type": type(error).__qualname__,
                    "error_message": str(error), "failure_stage": stage})
        return {"schema": SCHEMA + "-actual-worker-failure", "status": "FAIL",
                "family": FAMILY, "label": LABEL, "suite": suite_name,
                "case_execution_denominator": suite_count, **failure,
                "complete_actual_suite_failure_details": getattr(error, "details", None),
                "runtime_guard_version": 4,
                "guard_installed_before_candidate_import": installed,
                "candidate_imported": imported,
                "actual_candidate_workers": 0 if synthetic else 1,
                "synthetic_control": synthetic,
                "observer_source_proxy": dict(observer_proxy)
                if type(observer_proxy) is dict else None,
                "hidden_cases_read": 0, "benchmark_files_read": 0,
                "timing_trials_run": 0, "holdout": "NOT OPENED",
                "performance": "NOT MEASURED", "winner_selected": False}


def command(args, suite, journal_sha):
    validate_authority(args)
    require(suite in dict(SUITES), "reject an omitted actual original worker")
    command = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SELF, "--worker",
               "--root-authorized", "--frozen-committed-pushed"]
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256",
                "--frozen-commit", "--pushed-commit"):
        command.extend((key, args[key]))
    for key, expected in ACTUAL_PINS:
        require(args.get(key) == expected, "reject omitted actual worker authority")
        command.extend((key, expected))
    for key, value in (("--family", FAMILY), ("--label", LABEL),
                       ("--suite", suite),
                       ("--recovery-journal-sha256", sha(journal_sha, "journal"))):
        command.extend((key, value))
    return command


def publication_stem(suffix, *, observed=None):
    require(suffix in ("success", "failures"), "reject invented publication outcome")
    expected = "repaired-zig-original-campaign-v16-" + LABEL + "-" + suffix
    if observed is not None:
        require(observed == expected, "reject crossed actual publication owner")
    return expected


def campaign(args, state, legacy):
    validate_authority(args)
    require(os.environ.get("LOCPATH") == EXTERNAL_LOCPATH,
            "require independently provisioned complete original locale")
    return legacy.campaign(args)


def recover(args, state, legacy):
    validate_authority(args)
    return legacy.recover(args)


def parse(arguments):
    modes = {"--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover"}
    selected = [item for item in arguments if item in modes]
    require(len(selected) == 1, "select exactly one frozen V16 campaign action")
    mode = selected[0]
    flags = {"--root-authorized", "--frozen-committed-pushed"}
    values = {"--source-sha256", "--protocol-sha256", "--contract-sha256",
              "--family", "--label", "--suite", "--recovery-journal-sha256",
              "--frozen-commit", "--pushed-commit"}
    values.update(name for name, _ in ACTUAL_PINS)
    args = {}
    position = 0
    while position < len(arguments):
        item = arguments[position]
        if item in modes:
            require(item == mode, "reject conflicting root campaign actions")
            position += 1
        elif item in flags:
            require(item not in args, "reject repeated actual root authorization")
            args[item] = True
            position += 1
        else:
            require(item in values and item not in args
                    and position + 1 < len(arguments),
                    "reject omitted, repeated, or unknown root campaign authority")
            args[item] = arguments[position + 1]
            position += 2
    source = {"--source-sha256", "--protocol-sha256"}
    if mode == "--render-contract":
        required = source
    elif mode in ("--self-test", "--verify-frozen-context"):
        required = source | {"--contract-sha256"}
    else:
        required = source | {"--contract-sha256", "--family", "--label",
                             "--frozen-commit", "--pushed-commit"} | flags
        required.update(name for name, _ in ACTUAL_PINS)
        if mode in ("--worker", "--recover"):
            required.add("--recovery-journal-sha256")
        if mode == "--worker":
            required.add("--suite")
    require(set(args) == required,
            "require every independent frozen, root, source, native, and guard pin")
    return mode, args


def main():
    mode, args = parse(list(sys.argv[1:]))
    if mode in ("--self-test", "--verify-frozen-context", "--render-contract"):
        output = source_result(mode, args)
    else:
        validate_authority(args, worker=(mode == "--worker"))
        state = frozen_context(args["--source-sha256"], args["--protocol-sha256"],
                               args["--contract-sha256"])
        legacy = patched_legacy(state)
        if mode == "--worker":
            output = legacy.worker_canonical(worker(args, state=state, legacy=legacy))
        elif mode == "--recover":
            output = state["producer"].canonical(recover(args, state, legacy))
        else:
            output = state["producer"].canonical(campaign(args, state, legacy))
    require(type(output) is bytes and bool(output),
            "reject incomplete canonical source or actual worker evidence")
    os.write(1, output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        try:
            os.write(2, ("corrected first-party V4-guarded Zig campaign rejected: "
                         + type(error).__qualname__ + ": " + str(error) + "\n")
                     .encode("utf-8", "backslashreplace"))
        except BaseException:
            pass
        raise SystemExit(1) from error
