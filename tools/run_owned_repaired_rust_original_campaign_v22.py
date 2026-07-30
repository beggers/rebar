#!/usr/bin/env python3
"""Freeze the first-party Rust campaign without confusing source and run modes.

The genuine V21 run failed before activation because its exact frozen source
contract compared a physically installed source-only wall against an unwalled
actual entry.  Authenticate that complete, pretty-printed public failure and
the immutable V21 controller.  Normalize that one mode-specific observation
only in the frozen-contract projection.  Never install a source wall for an
actual run, weaken the genuine V3 runtime guard, or execute matching in a
source-only operation.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import os
import stat
import sys
import time
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
DEVICE = 2064
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v22.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v22.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v22"
VERSION = 22
FAMILY = "rust"
BUILD_LABEL = "phase2-v22-rust-capture-shape-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v22"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v22-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
LOCK_NAME = "recoverable-controller-v22.lock"
LOCALE_PATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
MAX_OWNER_BYTES = 4 * 1024 * 1024
CASE_COUNT = 31_237
WORKER_COUNT = 13
SUPPLEMENTAL_CASE_COUNT = 8_244
HOLDOUT_CASE_COUNT = 14_155_776
WALL_FIELD = "source_wall_installed_before_predecessor"
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"

V21 = (
    ("tools/run_owned_repaired_rust_original_campaign_v21.py",
     "54526783bd1ed158009c8aba5e1cdfd29eb18ea90ac98de3257d026b68f08bcc",
     91818, 430924),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V21.md",
     "a061a66837a047b3780da244dd401e2a5a44ed3906054f444a697657e92368c3",
     6917, 525194),
    ("oracle/phase2/repaired-rust-original-campaign-v21.json",
     "397a7e1158c48db5567ef8e79e2c5ab5238e2049a8d58a4794acb0d8e8ccde6d",
     40127, 525203),
)
V21_FAILURE = (
    "oracle/phase2/evidence/"
    "rust-original-campaign-v21-v3-preactivation-contract-failure.json",
    "bf4c321aa10b4961bd40ad1f12584296bd20356d18fef1542d360c03f48e6bda",
    9760, 525282,
)
V21_STDERR = (
    "V21 campaign rejected: CampaignError: reject missing, altered, "
    "or extra original-campaign obligations\n"
)
V21_STDERR_SHA = (
    "6898745a8a9d8ce05e5c6cd8129df20584c1eb02779aa9a760ca89b309b49502"
)
EMPTY_SHA = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
PROPOSAL_PATHS = frozenset((
    "tools/verify_expanded_sealed_holdout_v1.py",
    "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
    "oracle/phase3/expanded-sealed-holdout-v1.json",
))
HISTORICAL_CAPTURE = (
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/"
    "py_bridge.c"
)
FAILURE_ZERO_KEYS = (
    "actual_candidate_workers", "actual_reference_workers",
    "actual_candidate_imports", "actual_native_libraries_loaded",
    "actual_native_compiler_processes", "actual_subinterpreters_created",
    "actual_original_suite_rows", "actual_matching_observations",
    "actual_recovery_roots_created",
    "actual_success_publication_receipts_created",
    "actual_failure_publication_receipts_created",
    "actual_compressed_failure_archives_opened",
    "actual_private_build_archives_opened",
    "actual_benchmark_cases_opened", "actual_timing_trials_run",
)
FAILURE_KEYS = frozenset((
    "schema", "version", "status", "status_scope", "goal_sha256",
    "family", "candidate_status", "failure_stage", "controller",
    "protocol", "contract", "pinned_cpython", "invocation",
    "observed_exit_code", "stdout", "stderr", "root_cause",
    "original_case_execution_denominator", "original_suite_count",
    "supplemental_reference_case_count",
    "supplemental_reference_counted_in_original_denominator",
    *FAILURE_ZERO_KEYS, "all_four_original_targets_restored",
    "restored_original_targets", "previous_rust_candidate_status",
    "previous_rust_verified_passing_case_count",
    "previous_rust_observed_semantic_mismatch_lower_bound",
    "previous_rust_semantic_mismatch_count",
    "new_rust_semantic_mismatch_count", "correctness",
    "runtime_non_delegation", "qualified_candidate_count",
    "holdout_case_count", "holdout", "performance", "memory",
    "undefined_behavior", "winner_selected",
))


class CampaignError(Exception):
    """An immutable owner, actual failure, or one-field policy changed."""


def need(value: object, message: str) -> None:
    if value is not True:
        raise CampaignError(message)


def sha_pin(value: object, label: str) -> str:
    need(type(value) is str and len(value) == 64
         and all(item in "0123456789abcdef" for item in value),
         "require one complete independently pinned SHA-256: " + label)
    assert isinstance(value, str)
    return value


def verify_runtime() -> None:
    need(sys.implementation.name == "cpython"
         and tuple(sys.version_info[:3]) == (3, 14, 6)
         and sys.executable == PYTHON and sys.flags.isolated == 1
         and sys.flags.no_site == 1 and sys.dont_write_bytecode is True
         and "re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules and "ctypes" not in sys.modules
         and "concurrent.interpreters" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "require exact sterile CPython 3.14.6 -I -B -S before any candidate")


def secure_owner(owner: tuple, *, maximum: int = MAX_OWNER_BYTES) -> bytes:
    need(type(owner) is tuple and len(owner) == 4,
         "require one complete first-party immutable plaintext owner")
    relative, fingerprint, count, inode = owner
    need(type(relative) is str and bool(relative)
         and not relative.startswith("/") and ".." not in relative.split("/")
         and not relative.endswith((".gz", ".so"))
         and type(count) is int and 0 < count <= maximum
         and type(inode) is int and inode > 0,
         "reject private, native, compressed, or unbounded evidence")
    sha_pin(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
             and before.st_ino == inode and before.st_size == count
             and before.st_uid == os.geteuid() and before.st_nlink == 1
             and stat.S_IMODE(before.st_mode) == 0o600,
             "reject an exchanged complete public owner: " + relative)
        remaining = count
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(descriptor, min(remaining, 262144))
            need(type(piece) is bytes and bool(piece),
                 "reject a truncated public plaintext owner: " + relative)
            pieces.append(piece)
            remaining -= len(piece)
        need(not os.read(descriptor, 1),
             "reject an expanded public plaintext owner: " + relative)
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and tuple(getattr(before, field) for field in (
                 "st_dev", "st_ino", "st_size", "st_mtime_ns",
                 "st_ctime_ns", "st_nlink"))
             == tuple(getattr(after, field) for field in (
                 "st_dev", "st_ino", "st_size", "st_mtime_ns",
                 "st_ctime_ns", "st_nlink")),
             "reject changed complete public plaintext bytes: " + relative)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(relative: str, fingerprint: str) -> tuple:
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "reject an unrelated live V22 campaign owner")
    sha_pin(fingerprint, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        found = os.fstat(descriptor)
        need(stat.S_ISREG(found.st_mode) and found.st_dev == DEVICE
             and found.st_uid == os.geteuid() and found.st_nlink == 1
             and stat.S_IMODE(found.st_mode) == 0o600
             and 0 < found.st_size <= MAX_OWNER_BYTES,
             "reject an unsafe live V22 frozen campaign owner: " + relative)
        return relative, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


class PhysicalSourceWall:
    """Install the complete hardened V21 source wall before reading V21."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.error_type: type[BaseException] = CampaignError

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type("V22 preinstalled source wall rejected " + category)

    def approved_path(self, path: str) -> bool:
        if (type(path) is not str or not path.startswith("/")
                or path != os.path.normpath(path)
                or any(part in (".", "..") for part in path.split("/"))):
            return False
        standard = PYTHON.rsplit("/bin/", 1)[0] + "/lib/python3.14/"
        if path.startswith(standard):
            relative = path[len(standard):]
            return (relative.endswith((".py", ".pyc"))
                    and "/re/" not in "/" + relative
                    and not relative.startswith((
                        "re.py", "regex", "ctypes/", "socket.py",
                        "subprocess.py", "concurrent/interpreters/")))
        if not path.startswith(ROOT + "/"):
            return False
        relative = path[len(ROOT) + 1:]
        if relative in PROPOSAL_PATHS or relative == HISTORICAL_CAPTURE:
            return True
        if relative == "GOAL.md":
            return True
        if relative.startswith("candidates/"):
            return False
        if relative.endswith((".gz", ".so")):
            return False
        lower = relative.lower()
        if "benchmark" in lower or "holdout" in lower:
            return False
        return ((relative.startswith("tools/") and relative.endswith(".py"))
                or (relative.startswith("oracle/phase1/")
                    and relative.endswith((".py", ".json", ".md", ".txt")))
                or (relative.startswith("oracle/phase2/")
                    and relative.endswith((".py", ".json", ".md", ".svg")))
                or (relative.startswith("docs/evidence/")
                    and relative.endswith((".json", ".svg"))))

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            if type(path) is not str:
                self.deny("foreign-descriptor")
            if type(mode) is str and any(character in mode
                                         for character in "wax+"):
                self.deny("filesystem-write")
            if type(flags) is int and flags & (
                    getattr(os, "O_WRONLY", 0) | getattr(os, "O_RDWR", 0)
                    | getattr(os, "O_CREAT", 0) | getattr(os, "O_TRUNC", 0)
                    | getattr(os, "O_APPEND", 0)):
                self.deny("filesystem-write")
            absolute = path if path.startswith("/") else ROOT + "/" + path
            if not self.approved_path(absolute):
                self.deny("candidate-native-root-archive-holdout:" + absolute)
        elif event == "import":
            name = args[0] if args else None
            if type(name) is not str:
                self.deny("invalid-import")
            if (name in ("re", "_sre", "regex", "ctypes", "inspect",
                         "tokenize", "random", "concurrent.interpreters",
                         "_interpreters", "socket", "subprocess", "tempfile")
                    or name.startswith(("re.", "regex.", "ctypes.",
                                        "candidates.", "socket.",
                                        "concurrent.interpreters."))
                    or name == "candidates"):
                self.deny("matcher-native-network-or-child-import:" + name)
        elif event in ("exec", "compile"):
            item = args[0] if args else None
            filename = (getattr(item, "co_filename", None)
                        if event == "exec"
                        else args[1] if len(args) > 1 else None)
            if filename == "<unknown>" and event == "compile":
                return
            if filename in ("<v16-fail-closed-ctypes-proxy>",
                            "<v16-exact-native-mode-expression>"):
                return
            if event == "compile" and filename is None and isinstance(
                    item, ast.AST):
                return
            if type(filename) is not str:
                self.deny("dynamic-execution:" + event + ":"
                          + type(item).__name__ + ":" + repr(filename))
            absolute = (filename if filename.startswith("/")
                        else ROOT + "/" + filename)
            if not self.approved_path(absolute):
                self.deny("dynamic-execution:" + absolute)
        elif (event.startswith(("subprocess.", "os.exec", "os.spawn",
                                "socket.", "ctypes.", "tempfile.",
                                "threading.", "time."))
              or event in ("os.fork", "os.posix_spawn", "os.posix_spawnp",
                           "os.system", "os.mkdir", "os.remove", "os.rename",
                           "os.replace", "os.rmdir", "os.unlink", "os.chmod",
                           "os.chown", "os.putenv", "os.unsetenv",
                           "os.urandom", "os.getrandom",
                           "_interpreters.create", "_interpreters.exec",
                           "cpython.PyInterpreterState_New")):
            self.deny("process-native-network-mutation-child-or-entropy")

    def _forbidden(self, category: str):
        def blocked(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return blocked

    def install(self) -> None:
        need(self.installed is False, "reject a reused V22 physical source wall")
        sys.addaudithook(self.audit)
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self._forbidden("clock"))
        for name in ("urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("entropy"))
        for name in ("fork", "posix_spawn", "posix_spawnp", "system",
                     "listdir", "scandir"):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("process-or-directory"))
        self.installed = True


def previous_source_proof(raw: bytes) -> None:
    tree = ast.parse(raw, filename=ROOT + "/" + V21[0][0])
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef)
                 and node.name == "verify_context"]
    need(len(functions) == 1,
         "require the one immutable V21 frozen-context implementation")
    observations: list[ast.AST] = []
    comparisons: list[ast.Call] = []
    for node in ast.walk(functions[0]):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == WALL_FIELD:
                    observations.append(value)
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "need" and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value
                == "reject missing, altered, or extra original-campaign obligations"):
            comparisons.append(node)
    need(len(observations) == 1 and isinstance(observations[0], ast.Compare)
         and isinstance(observations[0].left, ast.Name)
         and observations[0].left.id == "wall"
         and len(observations[0].ops) == 1
         and isinstance(observations[0].ops[0], ast.IsNot)
         and len(observations[0].comparators) == 1
         and isinstance(observations[0].comparators[0], ast.Constant)
         and observations[0].comparators[0].value is None
         and observations[0].lineno == 1379
         and len(comparisons) == 1
         and comparisons[0].args[1].lineno == 1392,
         "authenticate the one exact immutable V21 preactivation wall cause")


def expected_failure_authority(previous: types.ModuleType) -> dict:
    return {
        "source_sha256": V21[0][1],
        "protocol_sha256": V21[1][1],
        "contract_sha256": V21[2][1],
        "activation_root": (
            "/tmp/rebar-phase2-repaired-rust-original-campaign-v21-"
            + BUILD_SUFFIX
        ),
        "build_private_root": previous.ROOT_PATH,
        "build_private_root_device": previous.ROOT_DEVICE,
        "build_private_root_inode": previous.ROOT_INODE,
        "producer_source_sha256":
            "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        "producer_protocol_sha256":
            "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        "producer_contract_sha256":
            "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        "phase1_v4_source_sha256":
            "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        "phase1_v4_protocol_sha256":
            "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        "phase1_v4_contract_sha256":
            "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        "build_source_sha256": previous.V22[0][1],
        "build_protocol_sha256": previous.V22[1][1],
        "build_contract_sha256": previous.V22[2][1],
        "build_archive_sha256": previous.ARCHIVE_SHA,
        "build_receipt_sha256": previous.V22_PUBLICATION[1],
        "root_receipt_sha256": previous.V22_ROOT_RECEIPT[1],
        "native_engine_sha256": previous.ENGINE_SHA,
        "native_engine_bytes": previous.ENGINE_BYTES,
        "native_bridge_sha256": previous.BRIDGE_SHA,
        "native_bridge_bytes": previous.BRIDGE_BYTES,
        "runtime_guard_source_sha256":
            "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
        "runtime_guard_protocol_sha256":
            "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
        "runtime_guard_contract_sha256":
            "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
        "previous_failure_receipt_sha256":
            "5b1cfdc72f88c3a847f65f5a06da77cd27557ca2c2306320b6c8d44a91e28578",
        "historical_v14_failure_receipt_sha256":
            "09c5ef5dd4919e8005d755a22d77615556a451202ab94c3ed11def2ba8825654",
        "historical_v13_failure_receipt_sha256":
            "6f990183501953c42af374a896fad6b64f909514c731cb9de4fb37faf4d3bf86",
        "historical_v12_failure_receipt_sha256":
            "6537561a46fe6b7ab294126628fa5d82c34f03c3d0bac6455112dae3eea11658",
        "current_graph_source_sha256":
            "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d",
        "current_graph_inputs_sha256":
            "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c",
        "current_graph_summary_sha256":
            "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc",
        "current_graph_svg_sha256":
            "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55",
        "combined_bridge_sha256": previous.BRIDGE_SOURCE_SHA,
        "combined_bridge_bytes": previous.BRIDGE_SOURCE_BYTES,
        "previous_campaign_source_sha256":
            "4705f5afb0639812e4902a455c11cee469b78a2a8f78bd64e1bf3388390d060e",
        "previous_campaign_protocol_sha256":
            "b168f394244c1f2e2f1051a0d9ed038fd11b596708667b9c8dc196b3f8f2c66f",
        "previous_campaign_contract_sha256":
            "1879abea2cfc3665ec5e0eeb9549286f1d566806f4f49482064855199a86d46b",
        "operational_guard_v3_source_sha256": previous.V3[0][1],
        "operational_guard_v3_protocol_sha256": previous.V3[1][1],
        "operational_guard_v3_contract_sha256": previous.V3[2][1],
        "previous_v20_source_sha256": previous.V20[0][1],
        "previous_v20_protocol_sha256": previous.V20[1][1],
        "previous_v20_contract_sha256": previous.V20[2][1],
        "previous_v20_failure_receipt_sha256": previous.V20_FAILURE[1],
    }


def validate_failure(value: dict, previous: types.ModuleType) -> dict:
    need(type(value) is dict and set(value) == FAILURE_KEYS
         and len(FAILURE_KEYS) == 52,
         "reject omitted, added, or exchanged genuine V21 failure fields")
    need(value.get("schema")
         == "rebar-phase2-first-party-rust-v21-preactivation-contract-failure-v1"
         and value.get("version") == 1 and value.get("status") == "FAIL"
         and value.get("status_scope")
         == "ONE GENUINE CONTROLLER INVOCATION; NO CANDIDATE WORKER STARTED"
         and value.get("goal_sha256") == GOAL_SHA
         and value.get("family") == FAMILY
         and value.get("candidate_status") == "NOT RUN"
         and value.get("failure_stage")
         == "PREACTIVATION_FROZEN_CONTRACT_COMPARISON"
         and value.get("observed_exit_code") == 2,
         "reject a guessed, semantic, repeated, or post-activation V21 failure")
    owner_keys = frozenset(("path", "sha256", "bytes", "device", "inode",
                             "mode", "nlink"))
    for role, expected in zip(("controller", "protocol", "contract"), V21):
        owner = value.get(role)
        need(type(owner) is dict and set(owner) == owner_keys
             and owner == {
                 "path": expected[0], "sha256": expected[1],
                 "bytes": expected[2], "device": DEVICE,
                 "inode": expected[3], "mode": "0600", "nlink": 1,
             }, "reject an exchanged actual V21 frozen " + role)
    need(value.get("pinned_cpython") == {
        "implementation": "cpython", "version": "3.14.6",
        "executable": PYTHON, "flags": ["-I", "-B", "-S"],
    }, "reject a different actual predecessor interpreter")
    invocation = value.get("invocation")
    need(type(invocation) is dict and set(invocation) == {
        "mode", "execution_count", "family", "label", "environment",
        "authority",
    } and invocation.get("mode") == "--run"
         and invocation.get("execution_count") == 1
         and invocation.get("family") == FAMILY
         and invocation.get("label") == BUILD_SUFFIX + "-v21"
         and invocation.get("environment") == {
             "PATH": "/usr/bin:/bin", "LC_ALL": "C", "LOCPATH": LOCALE_PATH,
         }, "reject a replayed or ambiguously authorized V21 invocation")
    authority = expected_failure_authority(previous)
    need(len(authority) == 46 and invocation.get("authority") == authority,
         "reject omitted, added, or altered actual V21 46-key authority")
    need(value.get("stdout") == {
        "bytes": 0, "sha256": EMPTY_SHA, "text": "",
    }, "reject invented genuine V21 preactivation stdout")
    stderr_bytes = V21_STDERR.encode("utf-8")
    need(len(stderr_bytes) == 102
         and hashlib.sha256(stderr_bytes).hexdigest() == V21_STDERR_SHA
         and value.get("stderr") == {
             "bytes": 102, "sha256": V21_STDERR_SHA, "text": V21_STDERR,
         }, "reject the complete genuine 102-byte V21 failure stderr")
    need(value.get("root_cause") == {
        "source_path": V21[0][0],
        "source_only_wall_marker_line": 1379,
        "failed_contract_comparison_line": 1392,
        "field": WALL_FIELD,
        "source_only_frozen_value": True,
        "actual_run_value": False,
        "actual_run_wall_installed": False,
        "actual_dispatch_reached": False,
        "candidate_semantics_tested": False,
        "classification":
            "SOURCE-ONLY SECURITY CONTEXT INCORRECTLY COMPARED AGAINST ACTUAL MODE",
    }, "reject a guessed or non-preactivation V21 root cause")
    need(all(value.get(key) == 0 for key in FAILURE_ZERO_KEYS),
         "invented a V21 matcher, worker, native, child, archive, or timing")
    expected_roles = [
        {"role": role, "path": path, "sha256": fingerprint,
         "bytes": count, "device": DEVICE, "inode": inode,
         "mode": format(mode, "04o"), "nlink": 1}
        for role, path, fingerprint, count, inode, mode in previous.ORIGINALS
    ]
    need(value.get("all_four_original_targets_restored") is True
         and value.get("restored_original_targets") == expected_roles,
         "reject omitted, reordered, altered, or loaded original owner roles")
    need(value.get("original_case_execution_denominator") == CASE_COUNT
         and value.get("original_suite_count") == WORKER_COUNT
         and value.get("supplemental_reference_case_count")
         == SUPPLEMENTAL_CASE_COUNT
         and value.get("supplemental_reference_counted_in_original_denominator")
         is False and value.get("previous_rust_candidate_status") == "FAIL"
         and value.get("previous_rust_verified_passing_case_count") == 15749
         and value.get("previous_rust_observed_semantic_mismatch_lower_bound")
         == 1296 and value.get("previous_rust_semantic_mismatch_count")
         == "NOT MEASURED" and value.get("new_rust_semantic_mismatch_count")
         == "NOT MEASURED" and value.get("correctness") == "NOT MEASURED"
         and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and value.get("qualified_candidate_count") == 0
         and value.get("holdout_case_count") == HOLDOUT_CASE_COUNT
         and value.get("holdout") == "NOT FROZEN; NOT GENERATED; NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("memory") == "NOT MEASURED"
         and value.get("undefined_behavior") == "NOT MEASURED"
         and value.get("winner_selected") is False,
         "reject inflated prior correctness or unopened V21 holdout evidence")
    return value


def frozen_projection(context: dict) -> dict:
    need(type(context) is dict
         and context.get("schema") == SCHEMA + "-frozen-context"
         and context.get("status") == "PASS"
         and context.get("version") == VERSION
         and WALL_FIELD in context
         and type(context[WALL_FIELD]) is bool
         and context.get("source_wall_required_before_predecessor_for_source_modes")
         is True
         and context.get("source_wall_observation_scope")
         == "CURRENT ENTRY MODE ONLY; NEVER FAKE PHYSICAL INSTALLATION"
         and context.get("actual_modes_require_no_source_wall") is True
         and context.get("contract_projection_normalized_fields") == [WALL_FIELD]
         and context.get("previous_v21_source_sha256") == V21[0][1]
         and context.get("previous_v21_protocol_sha256") == V21[1][1]
         and context.get("previous_v21_contract_sha256") == V21[2][1]
         and context.get("actual_v21_preactivation_failure_receipt_sha256")
         == V21_FAILURE[1],
         "reject a missing, forged, or non-boolean mode-scoped source wall")
    result = dict(context)
    result[WALL_FIELD] = True
    result["schema"] = SCHEMA + "-recoverable-source-freeze"
    result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
    result.pop("contract_sha256", None)
    return result


def enrich_context(context: dict, failure: dict) -> dict:
    need(type(context) is dict and type(failure) is dict,
         "require complete immutable V21 predecessor and live V22 context")
    context.update({
        "previous_v21_source_sha256": V21[0][1],
        "previous_v21_protocol_sha256": V21[1][1],
        "previous_v21_contract_sha256": V21[2][1],
        "previous_v21_frozen_contract_field_count": 402,
        "actual_v21_preactivation_failure_receipt_sha256": V21_FAILURE[1],
        "actual_v21_preactivation_failure_receipt_bytes": V21_FAILURE[2],
        "actual_v21_preactivation_failure_receipt_device": DEVICE,
        "actual_v21_preactivation_failure_receipt_inode": V21_FAILURE[3],
        "actual_v21_preactivation_failure_receipt_format":
            "AUTHENTICATED COMPLETE PRETTY-PRINTED PUBLIC JSON",
        "actual_v21_preactivation_failure_stage": failure["failure_stage"],
        "actual_v21_preactivation_exit_code": failure["observed_exit_code"],
        "actual_v21_preactivation_stderr_sha256": V21_STDERR_SHA,
        "actual_v21_preactivation_stderr_bytes": 102,
        "actual_v21_preactivation_stdout_sha256": EMPTY_SHA,
        "actual_v21_preactivation_source_wall_field": WALL_FIELD,
        "actual_v21_preactivation_source_frozen_wall": True,
        "actual_v21_preactivation_actual_wall_installed": False,
        "actual_v21_preactivation_actual_dispatch_reached": False,
        "actual_v21_preactivation_candidate_workers": 0,
        "actual_v21_preactivation_original_suite_rows": 0,
        "actual_v21_preactivation_candidate_imports": 0,
        "actual_v21_preactivation_native_libraries_loaded": 0,
        "actual_v21_preactivation_all_four_original_targets_restored": True,
        "actual_v21_original_campaign_attempted": True,
        "actual_v21_candidate_status": "NOT RUN",
        "actual_v21_candidate_semantic_mismatch_count": "NOT MEASURED",
        "actual_v22_original_campaign_attempted": False,
        "actual_v22_candidate_semantic_mismatch_count": "NOT MEASURED",
        "source_wall_required_before_predecessor_for_source_modes": True,
        "source_wall_observation_scope":
            "CURRENT ENTRY MODE ONLY; NEVER FAKE PHYSICAL INSTALLATION",
        "actual_modes_require_no_source_wall": True,
        "actual_modes_require_v3_guard_before_candidate_import": True,
        "contract_projection_normalized_fields": [WALL_FIELD],
        "contract_projection_preserves_all_other_fields": True,
        "contract_projection_synthetic_actual_activation_count": 0,
        "recovery_lock_filename": LOCK_NAME,
    })
    return context


def load_previous() -> tuple[types.ModuleType, dict]:
    raw = secure_owner(V21[0])
    secure_owner(V21[1])
    secure_owner(V21[2])
    previous_source_proof(raw)
    previous = types.ModuleType("_rebar_v22_immutable_frozen_previous_v21")
    previous.__file__ = ROOT + "/" + V21[0][0]
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True),
         previous.__dict__)
    need(previous.SOURCE == V21[0][0]
         and previous.PROTOCOL == V21[1][0]
         and previous.CONTRACT == V21[2][0]
         and previous.SCHEMA
         == "rebar-owned-repaired-rust-original-campaign-v21"
         and previous.VERSION == 21
         and callable(previous.verify_context)
         and previous.verify_context.__globals__ is previous.__dict__
         and callable(previous.source_controls)
         and callable(previous.actual_operation)
         and callable(previous.contract_document)
         and len(previous.SUITES) == WORKER_COUNT
         and sum(count for _, count in previous.SUITES) == CASE_COUNT,
         "reject replaced immutable full V21 controller or original suites")
    immutable_v20_validator = previous.validate_v20_failure
    historical_globals = dict(previous.__dict__)
    historical_validator = types.FunctionType(
        immutable_v20_validator.__code__, historical_globals,
        immutable_v20_validator.__name__,
        immutable_v20_validator.__defaults__,
        immutable_v20_validator.__closure__,
    )
    need(historical_validator.__code__ is immutable_v20_validator.__code__
         and historical_validator.__globals__["SCHEMA"]
         == "rebar-owned-repaired-rust-original-campaign-v21"
         and historical_validator.__globals__["V20"] == previous.V20,
         "preserve exact historical V21 code and V20 diagnostic schema")
    captured: dict[str, object] = {"failure": None, "contract": None}
    original_document = previous.document

    def authenticated_document(base: types.ModuleType,
                               guard: types.ModuleType,
                               owner: tuple, label: str) -> dict:
        result = original_document(base, guard, owner, label)
        if owner == previous.V20_FAILURE and captured["failure"] is None:
            failure_raw = secure_owner(V21_FAILURE)
            failure = base.parse_document(
                guard, failure_raw,
                "exact complete pretty-printed actual V21 preactivation receipt",
            )
            need(type(failure) is dict
                 and type(guard.canonical(failure)) is bytes
                 and guard.canonical(failure) != failure_raw,
                 "preserve genuine noncanonical pretty-printed V21 raw bytes")
            captured["failure"] = validate_failure(failure, previous)
            frozen_raw = secure_owner(V21[2])
            frozen = base.parse_document(
                guard, frozen_raw, "entire canonical immutable V21 contract",
            )
            need(type(frozen) is dict and guard.canonical(frozen) == frozen_raw
                 and len(frozen) == 402
                 and frozen.get("schema")
                 == "rebar-owned-repaired-rust-original-campaign-v21-"
                 "recoverable-source-freeze"
                 and frozen.get("source_sha256") == V21[0][1]
                 and frozen.get("protocol_sha256") == V21[1][1]
                 and frozen.get(WALL_FIELD) is True
                 and frozen.get("suite_count") == WORKER_COUNT
                 and frozen.get("case_execution_denominator") == CASE_COUNT
                 and frozen.get("expanded_holdout_cases_opened") == 0,
                 "reject any of the 402 complete original V21 obligations")
            captured["contract"] = frozen
        return result

    previous.document = authenticated_document
    previous.validate_v20_failure = historical_validator
    for name, value in (
            ("SOURCE", SOURCE), ("PROTOCOL", PROTOCOL),
            ("CONTRACT", CONTRACT), ("SCHEMA", SCHEMA),
            ("VERSION", VERSION), ("LABEL", LABEL),
            ("RECOVERY_PREFIX", RECOVERY_PREFIX),
            ("RECOVERY_ROOT", RECOVERY_ROOT)):
        setattr(previous, name, value)

    def project(context: dict) -> dict:
        failure = captured["failure"]
        need(type(failure) is dict,
             "authenticate the actual V21 failure before frozen projection")
        return frozen_projection(enrich_context(context, failure))

    previous.contract_document = project
    verify_runtime()
    return previous, captured


def install_actual_authority(previous: types.ModuleType,
                             state: dict) -> None:
    runner = state["runner"]
    base = state["base"]
    parent = state["parent"]
    original_required = runner.actual_required_authority

    def required(actual_base: types.ModuleType) -> dict[str, str]:
        result = dict(original_required(actual_base))
        result.update({
            "previous_v21_source_sha256": V21[0][1],
            "previous_v21_protocol_sha256": V21[1][1],
            "previous_v21_contract_sha256": V21[2][1],
            "previous_v21_preactivation_failure_receipt_sha256":
                V21_FAILURE[1],
        })
        return result

    runner.actual_required_authority = required
    state["required"] = required(base)
    original_bind = parent.bind_captured_controller

    def bind(actual_state: dict, context: dict, bundle: dict | None,
             counts: dict[str, int]) -> types.ModuleType:
        legacy = original_bind(actual_state, context, bundle, counts)
        need(legacy.LOCK_NAME == "recoverable-controller-v20.lock"
             and legacy.SCHEMA == SCHEMA and legacy.LABEL == LABEL
             and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT,
             "authenticate the genuine V20 recovery before V22 lock migration")
        legacy.LOCK_NAME = LOCK_NAME
        need(legacy.LOCK_NAME == LOCK_NAME
             and tuple(legacy.ROLE_ORDER) == tuple(base.ROLE_ORDER)
             and tuple(legacy.SUITES) == tuple(previous.SUITES),
             "retain the exact V22 four-role recovery and original workers")
        return legacy

    parent.bind_captured_controller = bind


def verify_context(options: dict,
                   wall: PhysicalSourceWall | None) -> tuple[dict, dict]:
    verify_runtime()
    source_mode = options["mode"] in (
        "--self-test", "--verify-frozen-context", "--render-contract",
    )
    need((type(wall) is PhysicalSourceWall and wall.installed)
         if source_mode else wall is None,
         "require the real preinstalled source wall only in source modes")
    secure_owner(dynamic_owner(SOURCE, options["source_sha256"]))
    secure_owner(dynamic_owner(PROTOCOL, options["protocol_sha256"]))
    if options["mode"] != "--render-contract":
        secure_owner(dynamic_owner(CONTRACT, options["contract_sha256"]))
    previous, captured = load_previous()
    context, state = previous.verify_context(options, wall)
    failure = captured["failure"]
    predecessor = captured["contract"]
    need(type(failure) is dict and type(predecessor) is dict
         and context.get(WALL_FIELD) is (wall is not None)
         and (wall is None or wall.installed),
         "preserve the truthful physical wall observation in its real mode")
    context = enrich_context(context, failure)
    state["context"] = context
    state["previous_v21"] = previous
    state["previous_v21_failure"] = failure
    state["previous_v21_frozen_contract"] = predecessor
    install_actual_authority(previous, state)
    need(state["required"].get("previous_v21_source_sha256") == V21[0][1]
         and state["required"].get("previous_v21_protocol_sha256") == V21[1][1]
         and state["required"].get("previous_v21_contract_sha256") == V21[2][1]
         and state["required"].get(
             "previous_v21_preactivation_failure_receipt_sha256")
         == V21_FAILURE[1]
         and context.get("recovery_lock_filename") == LOCK_NAME
         and context.get("operational_guard_version") == 3
         and context.get("required_native_owner_field_count") == 14
         and context.get("expected_real_child_interpreters") == 11
         and context.get("expected_original_case_interpreter_exec_calls") == 394
         and context.get("expected_total_real_interpreter_exec_calls") == 416
         and context.get("suite_count") == WORKER_COUNT
         and context.get("case_execution_denominator") == CASE_COUNT
         and context.get("expanded_holdout_cases_opened") == 0,
         "reject weakened original V3, V2, V5, recovery, or holdout obligations")
    verify_runtime()
    return context, state


def rejected(action: object, label: str, *kinds: type) -> str:
    need(callable(action), "require one executable source-only hostile control")
    try:
        action()
    except (CampaignError, ValueError, TypeError, OSError, UnicodeError,
            SyntaxError, *kinds):
        return label
    raise CampaignError("accepted hostile V22 original authority: " + label)


def different(value: object) -> object:
    if value is None:
        return "HOSTILE NON-NULL VALUE"
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "-HOSTILE"
    if type(value) is list:
        return [*value, "HOSTILE EXTRA ITEM"]
    if type(value) is dict:
        result = dict(value)
        need("__hostile_extra_field__" not in result,
             "require one fresh synthetic document key")
        result["__hostile_extra_field__"] = True
        return result
    raise CampaignError("reject unsupported frozen JSON mutation")


def native_candidate_identity(options: dict | None,
                              modules: dict) -> bool:
    candidate = modules.get("re")
    return (type(options) is dict and options.get("mode") == "--worker"
            and type(candidate) is types.ModuleType
            and candidate is modules.get("candidates.rust_candidate")
            and "_sre" not in modules)


def validate_actual_failure_classification(result: dict,
                                           options: dict | None,
                                           loaded: bool) -> dict:
    need(type(result) is dict and result.get("status") == "FAIL"
         and result.get("version") == VERSION
         and result.get("candidate_qualified") is False
         and result.get("candidate_correctness") == "NOT MEASURED"
         and result.get("performance") == "NOT MEASURED"
         and result.get("holdout") == "NOT OPENED"
         and result.get("winner_selected") is False,
         "reject invented source, candidate, or actual worker failure")
    if loaded:
        need(type(options) is dict and options.get("mode") == "--worker"
             and result.get("schema")
             == SCHEMA + "-actual-original-suite-worker-failure"
             and result.get("failure_class") == "INFRASTRUCTURE FAILURE"
             and result.get("suite") == options.get("suite")
             and result.get("actual_candidate_workers") == 1
             and result.get("actual_candidate_imports") == 1
             and result.get("actual_native_libraries_loaded") == 2
             and result.get("runtime_guard_installed_before_candidate_import")
             is True
             and result.get("semantic_mismatch_count") == "NOT MEASURED",
             "never erase a genuine guarded native Rust worker failure")
    else:
        need(result.get("schema") == SCHEMA + "-entry-failure"
             and result.get("actual_candidate_imports") == 0
             and result.get("actual_candidate_workers_started") == 0
             and result.get("actual_native_libraries_loaded") == 0
             and result.get("actual_private_build_root_opens") == 0
             and result.get("actual_build_archive_opens") == 0
             and result.get("actual_hidden_cases_read") == 0
             and result.get("actual_clock_samples") == 0,
             "claim zero actual effects only before candidate activation")
    return result


def failure_classification_controls(state: dict) -> list[str]:
    previous = state["previous_v21"]
    guard = state["guard"]
    kinds = (previous.CampaignError, guard.GuardError,
             guard.BootstrapError)
    options = {"mode": "--worker", "suite": "subinterpreter_v2"}
    clean_modules: dict[str, types.ModuleType] = {}
    selected = types.ModuleType("_rebar_v22_synthetic_local_candidate_only")
    matched = {"re": selected, "candidates.rust_candidate": selected}
    need(native_candidate_identity(options, clean_modules) is False
         and native_candidate_identity(options, matched) is True
         and "re" not in sys.modules and "_sre" not in sys.modules
         and "candidates.rust_candidate" not in sys.modules,
         "prove synthetic module identity without importing a real candidate")
    entry = previous.actual_failure(
        state.get("parent"), options,
        CampaignError("SOURCE-ONLY SYNTHETIC PREACTIVATION FAILURE"),
    )
    validate_actual_failure_classification(entry, options, False)
    worker = {
        "schema": SCHEMA + "-actual-original-suite-worker-failure",
        "status": "FAIL", "version": VERSION,
        "error_type": "CampaignError",
        "error_message": "SOURCE-ONLY SYNTHETIC POST-IMPORT FAILURE",
        "candidate_qualified": False,
        "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "suite": options["suite"],
        "actual_candidate_workers": 1,
        "actual_candidate_imports": 1,
        "actual_native_libraries_loaded": 2,
        "runtime_guard_installed_before_candidate_import": True,
        "semantic_mismatch_count": "NOT MEASURED",
    }
    validate_actual_failure_classification(worker, options, True)
    checks = [
        "synthetic-preactivation-failure-delegates-authenticated-v21-classifier",
        "synthetic-post-import-failure-preserves-one-real-worker",
        "synthetic-post-import-failure-preserves-two-native-owners",
        "synthetic-candidate-module-identity-never-imports-a-candidate",
    ]

    def reject_identity(mapping: dict, candidate_options: dict) -> None:
        need(native_candidate_identity(candidate_options, mapping) is True,
             "reject forged synthetic selected-candidate module identity")

    foreign = types.ModuleType("_rebar_v22_synthetic_foreign_only")
    for mapping, candidate_options, label in (
            ({"re": selected, "candidates.rust_candidate": foreign},
             options, "different-candidate-module"),
            ({"re": selected}, options, "missing-selected-candidate"),
            ({"re": selected, "candidates.rust_candidate": selected,
              "_sre": foreign}, options, "stdlib-native-regex-engine"),
            ({"re": "forged", "candidates.rust_candidate": "forged"},
             options, "nonmodule-candidate"),
            (matched, {"mode": "--run"}, "nonworker-actual-mode")):
        checks.append(rejected(
            lambda item=mapping, choice=candidate_options:
            reject_identity(item, choice),
            "reject-forged-synthetic-worker-identity-" + label, *kinds,
        ))
    for key in ("schema", "status", "version", "candidate_qualified",
                "candidate_correctness", "failure_class", "suite",
                "actual_candidate_workers", "actual_candidate_imports",
                "actual_native_libraries_loaded",
                "runtime_guard_installed_before_candidate_import",
                "semantic_mismatch_count", "holdout", "performance",
                "winner_selected"):
        forged = dict(worker)
        forged[key] = different(forged[key])
        checks.append(rejected(
            lambda item=forged:
            validate_actual_failure_classification(item, options, True),
            "reject-forged-post-import-worker-failure-" + key, *kinds,
        ))
    checks.append(rejected(
        lambda: validate_actual_failure_classification(entry, options, True),
        "reject-post-import-worker-disguised-as-zero-effect-entry", *kinds,
    ))
    checks.append(rejected(
        lambda: validate_actual_failure_classification(worker, options, False),
        "reject-preactivation-entry-disguised-as-loaded-worker", *kinds,
    ))
    verify_runtime()
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "candidates.rust_candidate" not in sys.modules,
         "never import or install a candidate for a synthetic worker proof")
    return checks


def projection_controls(context: dict, state: dict) -> list[str]:
    guard = state["guard"]
    previous = state["previous_v21"]
    base = state["original_base"]
    kinds = (previous.CampaignError, guard.GuardError,
             guard.BootstrapError)
    source = dict(context)
    source[WALL_FIELD] = True
    actual = dict(context)
    actual[WALL_FIELD] = False
    changed = {key for key in source if source[key] != actual.get(key)}
    need(changed == {WALL_FIELD}
         and source[WALL_FIELD] is True and actual[WALL_FIELD] is False,
         "require exactly one truthful synthetic source-versus-actual field")
    expected = frozen_projection(source)
    expected_raw = guard.canonical(expected)
    need(guard.canonical(frozen_projection(actual)) == expected_raw
         and source[WALL_FIELD] is True and actual[WALL_FIELD] is False
         and context[WALL_FIELD] is True,
         "prove the actual-mode contract without activating a candidate")
    checks = [
        "synthetic-source-mode-retains-real-installed-wall",
        "synthetic-actual-mode-retains-real-absent-wall",
        "synthetic-source-and-actual-differ-in-exactly-one-wall-field",
        "synthetic-actual-projects-complete-frozen-source-contract",
        "synthetic-actual-mode-starts-zero-candidate-workers",
    ]

    def require_unchanged(candidate: dict) -> None:
        need(guard.canonical(frozen_projection(candidate)) == expected_raw,
             "reject any non-wall source contract alteration")

    for key in sorted(source):
        if key in (WALL_FIELD, "contract_sha256"):
            continue
        forged = dict(source)
        forged[key] = different(forged[key])
        checks.append(rejected(
            lambda item=forged: require_unchanged(item),
            "reject-altered-nonwall-frozen-obligation-" + key, *kinds,
        ))
    extra = dict(source)
    extra["__hostile_extra_frozen_obligation__"] = True
    checks.append(rejected(
        lambda: require_unchanged(extra),
        "reject-extra-nonwall-frozen-obligation", *kinds,
    ))
    for key in (WALL_FIELD, "source_wall_required_before_predecessor_for_source_modes",
                "actual_modes_require_no_source_wall",
                "contract_projection_normalized_fields",
                "previous_v21_source_sha256",
                "actual_v21_preactivation_failure_receipt_sha256"):
        forged = dict(source)
        forged.pop(key)
        checks.append(rejected(
            lambda item=forged: require_unchanged(item),
            "reject-missing-frozen-wall-authority-" + key, *kinds,
        ))
    for value, label in ((None, "none"), (1, "integer"),
                         ("false", "string"), ([], "list")):
        forged = dict(source)
        forged[WALL_FIELD] = value
        checks.append(rejected(
            lambda item=forged: require_unchanged(item),
            "reject-nonboolean-mode-scoped-wall-" + label, *kinds,
        ))

    original = state["previous_v21_failure"]
    for key in sorted(FAILURE_KEYS):
        forged = previous.clone_document(guard, base, original)
        forged[key] = different(forged[key])
        checks.append(rejected(
            lambda item=forged: validate_failure(item, previous),
            "reject-altered-genuine-v21-preactivation-" + key, *kinds,
        ))
        missing = previous.clone_document(guard, base, original)
        missing.pop(key)
        checks.append(rejected(
            lambda item=missing: validate_failure(item, previous),
            "reject-missing-genuine-v21-preactivation-" + key, *kinds,
        ))
    extra_failure = previous.clone_document(guard, base, original)
    extra_failure["__hostile_extra_failure_field__"] = True
    checks.append(rejected(
        lambda: validate_failure(extra_failure, previous),
        "reject-extra-genuine-v21-preactivation-field", *kinds,
    ))
    for key in sorted(original["invocation"]["authority"]):
        forged = previous.clone_document(guard, base, original)
        forged["invocation"]["authority"][key] = different(
            forged["invocation"]["authority"][key],
        )
        checks.append(rejected(
            lambda item=forged: validate_failure(item, previous),
            "reject-altered-genuine-v21-preactivation-authority-" + key,
            *kinds,
        ))
    for index, row in enumerate(original["restored_original_targets"]):
        for key in sorted(row):
            forged = previous.clone_document(guard, base, original)
            forged["restored_original_targets"][index][key] = different(
                forged["restored_original_targets"][index][key],
            )
            checks.append(rejected(
                lambda item=forged: validate_failure(item, previous),
                "reject-altered-genuine-v21-original-role-"
                + row["role"] + "-" + key, *kinds,
            ))
    return checks


def source_controls(context: dict, state: dict,
                    wall: PhysicalSourceWall) -> list[str]:
    need(wall.installed and context.get(WALL_FIELD) is True,
         "never manufacture an installed V22 source-only physical wall")
    previous = state["previous_v21"]
    checks = list(previous.source_controls(context, state, wall))
    need(len(checks) == 324,
         "preserve every one of the 324 authentic immutable V21 controls")
    traversal = [item for item in checks
                 if "traversal" in item or "double-separator" in item]
    need(len(traversal) == 10,
         "preserve all ten hardened actual V21 lexical traversal controls")
    checks.extend(projection_controls(context, state))
    checks.extend(failure_classification_controls(state))
    verify_runtime()
    need(wall.installed and context.get(WALL_FIELD) is True
         and len(checks) > 324
         and context.get("actual_candidate_imports") == 0
         and context.get("actual_candidate_workers_started") == 0
         and context.get("actual_native_libraries_loaded") == 0
         and context.get("actual_private_build_root_opens") == 0
         and context.get("actual_build_archive_opens") == 0
         and context.get("expanded_holdout_cases_opened") == 0
         and context.get("contract_projection_synthetic_actual_activation_count")
         == 0,
         "reject weakened hostility, actual activation, or unopened holdout")
    return checks


def parse_options(arguments: list[str]) -> dict:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    selected = [argument for argument in arguments if argument in modes]
    need(len(selected) == 1,
         "select exactly one V22 source-only or root-authorized actual mode")
    result: dict[str, object] = {"mode": selected[0]}
    index = 0
    while index < len(arguments):
        flag = arguments[index]
        if flag in modes:
            index += 1
            continue
        need(type(flag) is str and flag.startswith("--")
             and index + 1 < len(arguments),
             "reject missing, positional, or partial V22 caller authority")
        key = flag[2:].replace("-", "_")
        need(key not in result, "reject repeated V22 caller authority: " + flag)
        result[key] = arguments[index + 1]
        index += 2
    sha_pin(result.get("source_sha256"), "V22 campaign source")
    sha_pin(result.get("protocol_sha256"), "V22 campaign protocol")
    if result["mode"] == "--render-contract":
        need("contract_sha256" not in result,
             "rendering cannot pin its not-yet-published V22 contract")
    else:
        sha_pin(result.get("contract_sha256"), "V22 campaign contract")
    if result["mode"] in (
            "--self-test", "--verify-frozen-context", "--render-contract"):
        need(set(result) <= {"mode", "source_sha256", "protocol_sha256",
                             "contract_sha256"},
             "source-only verification cannot authorize workers or candidates")
    return result


def actual_failure(state: dict | None, options: dict | None,
                   error: BaseException) -> dict:
    if type(state) is dict:
        previous = state.get("previous_v21")
        need(type(previous) is types.ModuleType
             and previous.__file__ == ROOT + "/" + V21[0][0]
             and previous.SCHEMA == SCHEMA and previous.VERSION == VERSION
             and callable(previous.actual_failure)
             and state.get("previous_v21_failure", {}).get("schema")
             == "rebar-phase2-first-party-rust-v21-"
             "preactivation-contract-failure-v1",
             "reject an unauthenticated actual V21 failure classifier")
        result = previous.actual_failure(state.get("parent"), options, error)
        loaded = native_candidate_identity(options, sys.modules)
        result = validate_actual_failure_classification(result, options, loaded)
        result.update({
            "previous_v21_source_sha256": V21[0][1],
            "previous_v21_protocol_sha256": V21[1][1],
            "previous_v21_contract_sha256": V21[2][1],
            "previous_v21_preactivation_failure_receipt_sha256": V21_FAILURE[1],
        })
        return result
    return {
        "schema": SCHEMA + "-entry-failure", "status": "FAIL",
        "version": VERSION, "error_type": type(error).__name__,
        "error_message": str(error)[:8192],
        "candidate_qualified": False, "candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_native_libraries_loaded": 0,
        "actual_private_build_root_opens": 0,
        "actual_build_archive_opens": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "mode": options.get("mode") if type(options) is dict else None,
    }


def actual_operation(options: dict, context: dict, state: dict) -> dict:
    need(options["mode"] in ("--run", "--worker", "--recover")
         and context.get(WALL_FIELD) is False
         and context.get("source_wall_required_before_predecessor_for_source_modes")
         is True and context.get("actual_modes_require_no_source_wall") is True
         and state["required"].get(
             "previous_v21_preactivation_failure_receipt_sha256")
         == V21_FAILURE[1],
         "require the truthful unwalled actual entry and full V21 authority")
    previous = state["previous_v21"]
    result = previous.actual_operation(options, context, state)
    if options["mode"] == "--worker":
        need(result.get("runtime_guard_installed_before_candidate_import")
             is True
             and result.get("operational_guard_v3_source_sha256")
             == previous.V3[0][1]
             and result.get("actual_candidate_workers") == 1,
             "require the genuine V3 runtime guard before native Rust matching")
    if options["mode"] == "--run":
        need(result.get("suite_count") == WORKER_COUNT
             and result.get("case_execution_denominator") == CASE_COUNT
             and result.get("all_four_original_targets_restored") is True
             and result.get("actual_v22_build_receipt_sha256")
             == previous.V22_PUBLICATION[1]
             and result.get("actual_v22_root_receipt_sha256")
             == previous.V22_ROOT_RECEIPT[1],
             "require all genuine V22 suites, native owners, and original roles")
    result["previous_v21_preactivation_failure_receipt_sha256"] = V21_FAILURE[1]
    result["previous_v21_source_sha256"] = V21[0][1]
    result["previous_v21_protocol_sha256"] = V21[1][1]
    result["previous_v21_contract_sha256"] = V21[2][1]
    return result


def main(arguments: list[str] | None = None) -> int:
    options: dict | None = None
    state: dict | None = None
    wall: PhysicalSourceWall | None = None
    try:
        verify_runtime()
        options = parse_options(list(sys.argv[1:] if arguments is None
                                     else arguments))
        if options["mode"] in (
                "--self-test", "--verify-frozen-context", "--render-contract"):
            wall = PhysicalSourceWall()
            wall.install()
        context, state = verify_context(options, wall)
        if options["mode"] == "--render-contract":
            result = frozen_projection(context)
        elif options["mode"] == "--verify-frozen-context":
            result = context
        elif options["mode"] == "--self-test":
            need(wall is not None and wall.installed,
                 "physically install the complete V22 source wall first")
            result = dict(context)
            result["schema"] = SCHEMA + "-source-self-test"
            checks = source_controls(context, state, wall)
            result["hostile_controls"] = checks
            result["hostile_control_count"] = len(checks)
            result["physically_blocked_effects"] = dict(wall.blocked)
        else:
            result = actual_operation(options, context, state)
        encoded = state["guard"].canonical(result)
        need(type(encoded) is bytes and 0 < len(encoded) <= MAX_OWNER_BYTES,
             "bound the exact source freeze or separately authorized result")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except BaseException as error:
        if state is not None:
            try:
                sys.stdout.buffer.write(state["guard"].canonical(
                    actual_failure(state, options, error),
                ))
                sys.stdout.buffer.flush()
            except BaseException:
                pass
        else:
            try:
                sys.stderr.write("V22 campaign rejected: "
                                 + type(error).__name__ + ": "
                                 + str(error)[:8192] + "\n")
            except BaseException:
                pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
