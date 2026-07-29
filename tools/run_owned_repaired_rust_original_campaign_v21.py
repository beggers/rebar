#!/usr/bin/env python3
"""Freeze the genuine V3-guarded original campaign for the built Rust V22.

Source modes install a physical wall before authenticating their predecessor.
They never open a canonical candidate, native artifact, build root, archive,
benchmark, or holdout. Only an independently authorized actual operation may
use the receipt-attested native build and unchanged original V5 producer.
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
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v21.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V21.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v21.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v21"
VERSION = 21
FAMILY = "rust"
BUILD_LABEL = "phase2-v22-rust-capture-shape-root-provenance"
BUILD_SUFFIX = BUILD_LABEL + "-original-p0"
LABEL = BUILD_SUFFIX + "-v21"
RECOVERY_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v21-"
RECOVERY_ROOT = "/tmp/" + RECOVERY_PREFIX + BUILD_SUFFIX
LOCALE_PATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
MAX_OWNER_BYTES = 4 * 1024 * 1024
MAX_DIAGNOSTIC_BYTES = 4 * 1024 * 1024
HOLDOUT_CASE_COUNT = 14_155_776
SUPPLEMENTAL_CASE_COUNT = 8_244
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
WORKER_COUNT = 13

V20 = (
    ("tools/run_owned_repaired_rust_original_campaign_v20.py",
     "d8434087da84e6d537f04023a95750297dc558a109c606e5863a2e7ac4177b13",
     66438, 431433),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V20.md",
     "19c3d742887784ab7054c1a63031077a9742c041d6f98c4e91452db1a51f505d",
     6017, 525356),
    ("oracle/phase2/repaired-rust-original-campaign-v20.json",
     "9c973d53a62f3948537cf7471f5fdde7403490053c2b304b6b192d784abeb414",
     29199, 525357),
)
V3 = (
    ("tools/verify_owned_candidate_runtime_independence_v3.py",
     "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
     59765, 430856),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
     "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
     5297, 525096),
    ("oracle/phase2/candidate-runtime-independence-v3.json",
     "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
     9157, 525114),
)
V22 = (
    ("tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py",
     "0ce73b2168c5143e2f95256d454ffe131bdc2c5736d91176509cc651819f58d4",
     65949, 430180),
    ("oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md",
     "31467e166ecc83ef49c43ca51bb97b7699a696068a4267dcd013c64078b3050a",
     5372, 524832),
    ("oracle/phase2/rust-capture-shape-semantics-source-build-v22.json",
     "b43f1a1f5f7c5c72990f4d8c3c9e321e53d7970b3ceaa4b0afdb82a08fa4b308",
     10067, 524833),
)
V22_PUBLICATION = (
    "oracle/phase2/evidence/native-source-build-v22-rust-"
    "phase2-v22-rust-capture-shape-root-provenance-publication-receipt.json",
    "851c7c6fd8546ee59f8107ea3687d0150d0ada0bf6764b040019b083776701b2",
    3500, 524926,
)
V22_ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v22-rust-"
    "phase2-v22-rust-capture-shape-root-provenance-"
    "root-provenance-receipt.json",
    "93cb91b186faaf32522a11caeb564829cd4504751bc88aebf955c36d19e572a3",
    5607, 524930,
)
V20_FAILURE = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v21-rust-captured-findall-root-provenance-"
    "original-p0-v20-failures-publication-receipt.json",
    "ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36",
    45973, 524829,
)
ROOT_PATH = "/tmp/rebar-phase2-native-build-v9-rust-y87f8wof"
ROOT_DEVICE = 2049
ROOT_INODE = 11389928
ENGINE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA = "2813d5ccc8d01a313ab2b7013e95ffc4bb6d2f28c399e160fed8994be99d9da3"
BRIDGE_BYTES = 148720
BRIDGE_SOURCE_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
BRIDGE_SOURCE_BYTES = 179147
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
ARCHIVE_SHA = "63c63350064f780726f8adfa3b93c889bd4c4e5dbf2ce7c1bfb9ab4bb10463b3"
ARCHIVE_BYTES = 108042
ARCHIVE_INODE = 524925
PLAIN_SHA = "3367c946f700b2f83cc299069126582d60aa777a5240c8a11bb3f2f8099a1702"
PLAIN_BYTES = 757194
PHASE_NATIVE_INODES = ((11389975, 11389981), (11389990, 11390003))
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
V20_ROW_DIGESTS = (
    "c48d47f8a8b93489467dc0d0cca71091f9a176f69d5174b9929834fb004365e1",
    "239cd82a735b6e97b768ef9e9b8acd7960c7caed81189b22bc97cea75ff3b0f9",
    "49cfd0908d9279527d2484d0d54a1790f3d15f87645beaf1f3754118bc8f4a47",
    "a9596fabcd2a8e04bc57a9efbe3aed82f9d4b1a86e6d5bbd9183955ef7ca34b1",
    "237ab27d03e720abb70962542707557bfdaaa5c2457eb6cf3b6866d0fb14a7e2",
    "00259aa07b1e4c87b5782a97aa43b6e452fff6df6874f641b066513b4c8ce165",
    "bb2e64d29c429613c5b8c515d15afd214d936f90f3d4a415c1a29cf3400a7696",
    "2fc6d6b133d40ac1c8972aa7fd6e39d1f5eb0144f49f5ef7cefc611c437bcac1",
    "e6b271bec48665b29c0c33d2a6ecf9a8dc43880b6bbd0595569aaa34e166c43b",
    "261561bfad94f6ac7c03924b8d8170be09c00bb117c850f31cd78faf702a6451",
    "8a304f6a3b27a5c88b7f7a1e6e0f72e5d4dff6bc2c21a689a2819058b377a344",
    "340167a5e6936c23fa4345ab1da1ad980cf33ed2c6da7157904faccbda63781e",
    "a37a0e5ef6ea19ee2e7a78f76fbeb7920aabe4b1a127bfa89d329b91c8fbc519",
)
ORIGINALS = (
    ("bridge_source", "candidates/rust/py_bridge.c",
     "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
     175676, 419054, 0o600),
    ("adapter", "candidates/rust_candidate.py",
     "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
     31151, 428100, 0o600),
    ("engine", "candidates/_rust_engine.so",
     "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
     660440, 430563, 0o755),
    ("bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
     "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
     144992, 430629, 0o755),
)
NATIVE_OWNER_KEYS = frozenset((
    "role", "family", "absolute_path", "relative", "file_name", "sha256",
    "bytes", "size_bytes", "device", "inode", "mode", "uid", "nlink",
    "native_loaded",
))
MARKER = b"REBAR-V16-AUTHENTIC-PRODUCER-FAILURE "
FIRST_STDOUT_SHA = "d18d3e94f8783928390c3bcb3dc0d3b2db41ff4b12b2c6606c2e23215a1d515d"
FIRST_STDERR_SHA = "18d36d1530e28fdbc3657a3234bb3790fad9e78c2b2a9911e1e37fa68ce0991c"
FIRST_TRACEBACK_SHA = "44c12197e1d8ebe7da081436299554602c441f0a557e46ca17df43494297135e"
FIRST_NESTED_SHA = "911501a1a654342cc11b970142b177e87f3d86e0321c7a178aa364202f70cf70"
PROPOSAL_PATHS = frozenset((
    "tools/verify_expanded_sealed_holdout_v1.py",
    "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
    "oracle/phase3/expanded-sealed-holdout-v1.json",
))
HISTORICAL_CAPTURE = (
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/"
    "py_bridge.c"
)


class CampaignError(Exception):
    """The exact guard, native provenance, or frozen original suite changed."""


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
         "require one complete immutable plaintext owner")
    relative, fingerprint, count, inode = owner
    need(type(relative) is str and bool(relative)
         and not relative.startswith("/") and ".." not in relative.split("/")
         and not relative.endswith((".gz", ".so"))
         and type(count) is int and 0 < count <= maximum
         and type(inode) is int and inode > 0,
         "reject a private root, native artifact, archive, or unbounded owner")
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
             "reject an exchanged first-party plaintext owner: " + relative)
        left = count
        chunks: list[bytes] = []
        while left:
            chunk = os.read(descriptor, min(left, 262144))
            need(type(chunk) is bytes and bool(chunk),
                 "reject a truncated first-party owner: " + relative)
            chunks.append(chunk)
            left -= len(chunk)
        need(not os.read(descriptor, 1),
             "reject an expanded first-party owner: " + relative)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        need(hashlib.sha256(raw).hexdigest() == fingerprint
             and tuple(getattr(before, field) for field in (
                 "st_dev", "st_ino", "st_size", "st_mtime_ns",
                 "st_ctime_ns", "st_nlink"))
             == tuple(getattr(after, field) for field in (
                 "st_dev", "st_ino", "st_size", "st_mtime_ns",
                 "st_ctime_ns", "st_nlink")),
             "reject changed complete first-party bytes: " + relative)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(relative: str, fingerprint: str) -> tuple:
    need(relative in (SOURCE, PROTOCOL, CONTRACT),
         "reject an unrelated live campaign owner")
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
             "reject an unsafe new frozen campaign owner: " + relative)
        return relative, fingerprint, found.st_size, found.st_ino
    finally:
        os.close(descriptor)


class PhysicalSourceWall:
    """Physically deny matching, clocks, entropy, native roots, and workers."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.installed = False
        self.error_type: type[BaseException] = CampaignError

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type(
            "V21 preinstalled source wall rejected " + category)

    def approved_path(self, path: str) -> bool:
        if (type(path) is not str or not path.startswith("/")
                or path != os.path.normpath(path)
                or any(part in (".", "..") for part in path.split("/"))):
            return False
        standard_library = PYTHON.rsplit("/bin/", 1)[0] + "/lib/python3.14/"
        if path.startswith(standard_library):
            relative_library = path[len(standard_library):]
            return (
                relative_library.endswith((".py", ".pyc"))
                and "/re/" not in "/" + relative_library
                and not relative_library.startswith(("re.py", "regex",
                                                     "ctypes/", "socket.py",
                                                     "subprocess.py",
                                                     "concurrent/interpreters/"))
            )
        if not path.startswith(ROOT + "/"):
            return False
        relative = path[len(ROOT) + 1:]
        if relative in PROPOSAL_PATHS:
            return True
        if relative == HISTORICAL_CAPTURE:
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
        return (
            (relative.startswith("tools/") and relative.endswith(".py"))
            or (relative.startswith("oracle/phase1/")
                and relative.endswith((".py", ".json", ".md", ".txt")))
            or (relative.startswith("oracle/phase2/")
                and relative.endswith((".py", ".json", ".md", ".svg")))
            or (relative.startswith("docs/evidence/")
                and relative.endswith((".json", ".svg")))
        )

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            if type(path) is not str:
                self.deny("foreign-descriptor")
            if (type(mode) is str and any(ch in mode for ch in "wax+")):
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
            value = args[0] if args else None
            filename = (getattr(value, "co_filename", None)
                        if event == "exec"
                        else args[1] if len(args) > 1 else None)
            if filename == "<unknown>" and event == "compile":
                return
            if filename in ("<v16-fail-closed-ctypes-proxy>",
                            "<v16-exact-native-mode-expression>"):
                return
            if event == "compile" and filename is None and isinstance(
                    value, ast.AST):
                return
            if type(filename) is not str:
                self.deny("dynamic-execution:" + event + ":"
                          + type(value).__name__ + ":" + repr(filename))
            absolute = filename if filename.startswith("/") else (
                ROOT + "/" + filename
            )
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
        need(self.installed is False, "reject a reused V21 physical wall")
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


def bootstrap(owner: tuple, name: str,
              *, migrate_v21: bool = False) -> types.ModuleType:
    raw = secure_owner(owner)
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[0]
    if migrate_v21:
        tree = ast.parse(raw, filename=owner[0])

        class ExactV22Literals(ast.NodeTransformer):
            def __init__(self) -> None:
                self.count = 0

            def visit_Constant(self, node: ast.Constant) -> ast.AST:
                if type(node.value) is str and (
                        "v21" in node.value or "V21" in node.value):
                    self.count += 1
                    return ast.copy_location(
                        ast.Constant(value=node.value.replace(
                            "v21", "v22").replace("V21", "V22")), node)
                return node

        migration = ExactV22Literals()
        tree = migration.visit(tree)
        need(migration.count >= 20,
             "reject missing authenticated V21-to-V22 literal migration")
        code = compile(ast.fix_missing_locations(tree), module.__file__,
                       "exec", dont_inherit=True)
        module._v22_literal_migration_count = migration.count
    else:
        code = compile(raw, module.__file__, "exec", dont_inherit=True)
    exec(code, module.__dict__)
    verify_runtime()
    return module


def document(base: types.ModuleType, guard: types.ModuleType,
             owner: tuple, label: str) -> dict:
    raw = secure_owner(owner)
    value = base.parse_document(guard, raw, label)
    need(type(value) is dict and guard.canonical(value) == raw,
         "reject noncanonical authenticated public evidence: " + label)
    return value


def validate_v22(build: dict, root: dict, freeze: dict) -> dict:
    need(type(build) is dict and type(root) is dict and type(freeze) is dict,
         "require both real V22 public receipts and frozen source")
    need(build.get("schema")
         == "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22-"
            "durable-publication-receipt"
         and build.get("status") == "PASS" and build.get("build_status") == "PASS"
         and build.get("family") == FAMILY and build.get("label") == BUILD_LABEL
         and build.get("source_sha256") == V22[0][1]
         and build.get("protocol_sha256") == V22[1][1]
         and build.get("contract_sha256") == V22[2][1]
         and build.get("expected_actual_compiler_process_count") == 28
         and build.get("actual_compiler_process_count") == 28
         and build.get("combined_bridge_sha256") == BRIDGE_SOURCE_SHA
         and build.get("combined_bridge_bytes") == BRIDGE_SOURCE_BYTES
         and build.get("combined_bridge_overlay_apply_count") == 2
         and build.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and build.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and build.get("corrected_public_adapter_overlay_apply_count") == 2
         and build.get("archive_sha256") == ARCHIVE_SHA
         and build.get("archive_bytes") == ARCHIVE_BYTES
         and build.get("uncompressed_sha256") == PLAIN_SHA
         and build.get("uncompressed_bytes") == PLAIN_BYTES
         and build.get("candidate_workers_started") == 0
         and build.get("native_libraries_loaded") == 0
         and build.get("hidden_cases_read") == 0
         and build.get("holdout") == "NOT OPENED",
         "reject stale, unbuilt, external, or falsely qualified V22 native build")
    publication = build.get("archive_publication")
    need(type(publication) is dict and publication.get("sha256") == ARCHIVE_SHA
         and publication.get("bytes") == ARCHIVE_BYTES
         and publication.get("device") == DEVICE
         and publication.get("inode") == ARCHIVE_INODE
         and publication.get("exclusive_creation") is True
         and publication.get("file_fsync_completed") is True,
         "authenticate V22 compressed metadata without opening an archive")
    need(root.get("schema")
         == "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22-"
            "durable-root-provenance-receipt"
         and root.get("status") == "PASS" and root.get("family") == FAMILY
         and root.get("label") == BUILD_LABEL
         and root.get("source_sha256") == V22[0][1]
         and root.get("protocol_sha256") == V22[1][1]
         and root.get("contract_sha256") == V22[2][1]
         and root.get("canonical_build_status") == "PASS"
         and root.get("canonical_build_receipt_relative") == V22_PUBLICATION[0]
         and root.get("canonical_build_receipt_sha256") == V22_PUBLICATION[1]
         and root.get("canonical_build_receipt_bytes") == V22_PUBLICATION[2]
         and root.get("canonical_build_receipt_device") == DEVICE
         and root.get("canonical_build_receipt_inode") == V22_PUBLICATION[3]
         and root.get("canonical_build_archive_sha256") == ARCHIVE_SHA
         and root.get("canonical_build_archive_bytes") == ARCHIVE_BYTES
         and root.get("canonical_build_archive_opened") is False
         and root.get("corrected_semantic_bridge_sha256") == BRIDGE_SOURCE_SHA
         and root.get("corrected_semantic_bridge_bytes") == BRIDGE_SOURCE_BYTES
         and root.get("corrected_public_adapter_sha256") == ADAPTER_SHA
         and root.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
         and root.get("actual_compiler_process_count") == 28
         and root.get("actual_source_phase_count") == 2
         and root.get("bridge_overlay_apply_count") == 2
         and root.get("adapter_overlay_apply_count") == 2
         and root.get("latest_original_campaign_receipt_sha256") == V20_FAILURE[1]
         and root.get("all_original_source_identities_restored") is True
         and root.get("historical_archives_opened") == 0
         and root.get("native_libraries_loaded") == 0
         and root.get("hidden_cases_read") == 0
         and root.get("holdout") == "NOT OPENED"
         and root.get("runtime_non_delegation") == "NOT ESTABLISHED",
         "reject forged V22 root evidence, stale bridge, or candidate result")
    info = root.get("root")
    need(type(info) is dict and info.get("path") == ROOT_PATH
         and info.get("device") == ROOT_DEVICE and info.get("inode") == ROOT_INODE
         and info.get("uid") == os.geteuid() and info.get("mode") == "0700"
         and info.get("phase_count") == 2
         and info.get("directory_scanned") is False,
         "bind the real V22 root only from its canonical public receipt")
    phases = info.get("phases")
    need(type(phases) is list and len(phases) == 2,
         "require both separately built receipt-attested native phases")
    identities: set[tuple[int, int]] = set()
    for position, name in enumerate(("reference-a", "reference-b")):
        phase = phases[position]
        need(type(phase) is dict and phase.get("name") == name
             and phase.get("absolute_path") == ROOT_PATH + "/" + name
             and phase.get("device") == ROOT_DEVICE
             and phase.get("uid") == os.geteuid()
             and phase.get("mode") == "0700",
             "reject substituted receipt-only V22 build phase: " + name)
        outputs = phase.get("native_outputs")
        need(type(outputs) is list and len(outputs) == 2,
             "require both genuine receipt-attested native artifacts")
        for index, spec in enumerate((
                ("engine", ENGINE_SHA, ENGINE_BYTES,
                 "_rust_engine.so", "0600"),
                ("bridge", BRIDGE_SHA, BRIDGE_BYTES,
                 "_rust_bridge.cpython-314-x86_64-linux-gnu.so", "0700"))):
            role, fingerprint, count, filename, mode = spec
            artifact = outputs[index]
            need(type(artifact) is dict and artifact.get("role") == role
                 and artifact.get("sha256") == fingerprint
                 and artifact.get("bytes") == count
                 and artifact.get("file_name") == filename
                 and artifact.get("absolute_path")
                 == ROOT_PATH + "/" + name + "/native/" + filename
                 and artifact.get("device") == ROOT_DEVICE
                 and artifact.get("inode") == PHASE_NATIVE_INODES[position][index]
                 and artifact.get("uid") == os.geteuid()
                 and artifact.get("mode") == mode
                 and artifact.get("nlink") == 1
                 and artifact.get("native_loaded") is False,
                 "reject a crossed V22 " + name + " native " + role)
            identity = (artifact["device"], artifact["inode"])
            need(identity not in identities,
                 "reject reused independently built native output identity")
            identities.add(identity)
    need(len(identities) == 4, "require four distinct V22 native owner identities")
    need(freeze.get("schema")
         == "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22-"
            "source-freeze"
         and freeze.get("version") == 22 and freeze.get("family") == FAMILY
         and freeze.get("source", {}).get("sha256") == V22[0][1]
         and freeze.get("protocol", {}).get("sha256") == V22[1][1],
         "authenticate complete genuine first-party V22 source freeze")
    family = freeze.get("owned_first_party_rust_family")
    semantic = freeze.get("independently_frozen_semantic_correction")
    reference = freeze.get("frozen_python_correctness")
    effects = freeze.get("source_only_effects")
    need(type(family) is dict and family.get("canonical_source_count") == 9
         and family.get("external_cargo_dependency_count") == 0
         and family.get("external_regular_expression_engine") == "FORBIDDEN"
         and family.get("matching_fallback") == "FORBIDDEN"
         and type(semantic) is dict
         and semantic.get("derived_bridge_sha256") == BRIDGE_SOURCE_SHA
         and semantic.get("derived_bridge_bytes") == BRIDGE_SOURCE_BYTES
         and semantic.get("new_external_package") is False
         and semantic.get("new_matching_fallback") is False
         and type(reference) is dict
         and reference.get("original_case_count") == CASE_COUNT
         and reference.get("original_suite_count") == WORKER_COUNT
         and reference.get("named_private_waivers") == PRIVATE_WAIVER_COUNT
         and reference.get("separate_supplemental_reference_case_count")
         == SUPPLEMENTAL_CASE_COUNT
         and reference.get("supplemental_counted_in_original_denominator")
         is False and type(effects) is dict
         and effects.get("hidden_cases_read") == 0
         and effects.get("holdout") == "NOT OPENED",
         "reject an external dependency, changed oracle, or invented holdout")
    return {"phase_count": 2, "native_artifact_count": 4,
            "family": family, "semantic": semantic,
            "phase1": reference, "source_only_effects": effects}


def decode_stream(previous: types.ModuleType, encoded: object,
                  encoder: object, limit: int) -> bytes:
    return previous.decode_bounded_base64(encoded, maximum=limit,
                                           encoder=encoder)


def validate_v20_failure(value: dict, previous: types.ModuleType,
                         parent: types.ModuleType, state: dict) -> dict:
    need(type(value) is dict
         and value.get("schema") == "rebar-owned-repaired-rust-original-"
                                    "campaign-v20-durable-publication-receipt"
         and value.get("status") == "PASS"
         and value.get("publication_status") == "PASS"
         and value.get("candidate_status") == "FAIL"
         and value.get("candidate_qualified") is False
         and value.get("family") == FAMILY
         and value.get("label")
         == "phase2-v21-rust-captured-findall-root-provenance-original-p0-v20"
         and value.get("campaign_source_sha256") == V20[0][1]
         and value.get("campaign_protocol_sha256") == V20[1][1]
         and value.get("campaign_contract_sha256") == V20[2][1]
         and value.get("suite_count") == WORKER_COUNT
         and value.get("case_execution_denominator") == CASE_COUNT
         and value.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and value.get("attempted_suite_count") == WORKER_COUNT
         and value.get("started_suite_count") == WORKER_COUNT
         and value.get("completed_suite_count") == 12
         and value.get("actual_candidate_workers") == WORKER_COUNT
         and value.get("distinct_worker_process_id_count") == WORKER_COUNT
         and value.get("duplicate_worker_process_id_count") == 0
         and value.get("missing_worker_process_id_count") == 0
         and value.get("verified_passing_case_count") == 15749
         and value.get("semantic_mismatch_count") == "NOT MEASURED"
         and value.get("infrastructure_failure_count") == 1
         and value.get("all_original_observation_vectors_complete") is False
         and value.get("all_four_original_targets_restored") is True
         and value.get("restoration_verified_before_publication") is True
         and value.get("all_original_suite_rows_validated_before_publication")
         is True and value.get("hidden_cases_read") == 0
         and value.get("benchmark_files_read") == 0
         and value.get("clock_samples") == 0
         and value.get("holdout") == "NOT OPENED"
         and value.get("performance") == "NOT MEASURED"
         and value.get("worker_failure_capture_count") == 1
         and value.get("all_worker_failure_capture_count") == 1,
         "preserve real V20 candidate failure independently of publication")
    rows = value.get("suite_integrity")
    need(type(rows) is list and len(rows) == WORKER_COUNT,
         "preserve all genuine prior original worker rows")
    pids: set[int] = set()
    passing = 0
    for index, ((name, count), expected_digest) in enumerate(
            zip(SUITES, V20_ROW_DIGESTS, strict=True)):
        row = rows[index]
        need(type(row) is dict and row.get("suite") == name
             and row.get("case_execution_denominator") == count
             and row.get("worker_attempted") is True
             and row.get("actual_worker_started") is True
             and row.get("complete_original_row_sha256") == expected_digest
             and type(row.get("pid")) is int and row["pid"] > 0
             and row["pid"] not in pids,
             "reject a missing, reused, reordered, or forged V20 row: " + name)
        pids.add(row["pid"])
        if name == "substitution_v2":
            need(row.get("failure_class") == "SEMANTIC MISMATCH"
                 and row.get("fully_observed") is True
                 and row.get("mismatch_count") == 240
                 and row.get("verified_passing_case_count") == 0
                 and row.get("returncode") == 1,
                 "preserve exactly the observed substitution lower bound")
        elif name == "shape_v2":
            need(row.get("failure_class") == "SEMANTIC MISMATCH"
                 and row.get("fully_observed") is True
                 and row.get("mismatch_count") == 1056
                 and row.get("verified_passing_case_count") == 0
                 and row.get("returncode") == 1,
                 "preserve exactly the observed shape lower bound")
        elif name == "subinterpreter_v2":
            need(row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                 and row.get("fully_observed") is False
                 and row.get("mismatch_count") == "NOT MEASURED"
                 and row.get("verified_passing_case_count") == 0
                 and row.get("returncode") == 2,
                 "never classify a real incomplete child suite as matching")
        else:
            need(row.get("failure_class") == "PASS"
                 and row.get("fully_observed") is True
                 and row.get("mismatch_count") == 0
                 and row.get("verified_passing_case_count") == count
                 and row.get("returncode") == 0,
                 "preserve the genuine complete prior passing suite: " + name)
            passing += count
    need(len(pids) == WORKER_COUNT and passing == 15749,
         "reject synthetic historical process identity or passing cases")
    restored = value.get("restored_original_targets")
    need(type(restored) is dict and set(restored)
         == {item[0] for item in ORIGINALS},
         "preserve exactly the four actual prior canonical target owners")
    for role, relative, fingerprint, count, inode, mode in ORIGINALS:
        item = restored[role]
        need(type(item) is dict and item.get("relative") == relative
             and item.get("path") == ROOT + "/" + relative
             and item.get("sha256") == fingerprint
             and item.get("bytes") == count
             and item.get("size_bytes") == count
             and item.get("device") == DEVICE and item.get("inode") == inode
             and item.get("mode") == mode and item.get("uid") == os.geteuid()
             and item.get("nlink") == 1,
             "reject an exchanged restored canonical original: " + role)
    capture = value.get("worker_failure_capture")
    first = capture.get("first_worker_failure") if type(capture) is dict else None
    need(type(capture) is dict and capture.get("actual_failure_count") == 1
         and capture.get("all_failure_metadata_preserved") is True
         and type(first) is dict and first.get("suite") == "subinterpreter_v2"
         and first.get("returncode") == 2
         and first.get("stdout_sha256") == FIRST_STDOUT_SHA
         and first.get("stderr_sha256") == FIRST_STDERR_SHA
         and first.get("traceback_sha256") == FIRST_TRACEBACK_SHA,
         "preserve complete bounded real child stderr, stdout, and traceback")
    encoder = state["parent"].source_only_base64
    material: dict[str, bytes] = {}
    for name, fingerprint, count in (
            ("stdout", FIRST_STDOUT_SHA, 721),
            ("stderr", FIRST_STDERR_SHA, 10046)):
        record = first.get(name)
        need(type(record) is dict and record.get("available") is True
             and record.get("complete") is True
             and record.get("source_sha256") == fingerprint
             and record.get("source_size_bytes") == count
             and record.get("captured_size_bytes") == count,
             "retain every authentic previous failed worker byte: " + name)
        raw = decode_stream(previous, record.get("base64"), encoder, 65536)
        need(len(raw) == count and hashlib.sha256(raw).hexdigest() == fingerprint,
             "reject forged complete V20 failure bytes: " + name)
        material[name] = raw
    need(material["stderr"].count(MARKER) == 1
         and material["stderr"].count(
             b"AttributeError: 'NoneType' object has no attribute 'free'") == 16,
         "retain exact V20 nested producer evidence and 16 destructor warnings")
    line = material["stderr"].split(b"\n", 1)[0]
    need(line.startswith(MARKER), "retain the canonical actual V20 failure prefix")
    diagnostic = parent.document(
        state["original_base"], state["guard"],
        line[len(MARKER):] + b"\n", "genuine V20 nested child failure")
    chain = diagnostic.get("authentic_exception_chain")
    need(diagnostic.get("schema") == SCHEMA.replace("v21", "v20")
         + "-authenticated-original-producer-failure"
         and diagnostic.get("status") == "FAIL"
         and diagnostic.get("diagnostic_only") is True
         and diagnostic.get("suite") == "subinterpreter_v2"
         and diagnostic.get("observer") == "observe_subinterpreters"
         and diagnostic.get("completed_candidate_case_count") == 0
         and type(chain) is list and len(chain) == 3
         and tuple(row.get("exception_type") for row in chain)
         == ("ActualSuiteFailure", "ActualSuiteFailure", "GuardError")
         and chain[-1].get("message", {}).get("text")
         == "runtime guard blocked unattested-child-bootstrap",
         "preserve the actual three-edge V20 child guard failure")
    encoded = diagnostic.get("complete_canonical_failure_details")
    need(type(encoded) is dict and encoded.get("complete") is True
         and encoded.get("source_sha256") == FIRST_NESTED_SHA,
         "retain the complete actual guarded nested failure")
    nested_raw = decode_stream(previous, encoded.get("base64"), encoder, 16384)
    need(hashlib.sha256(nested_raw).hexdigest() == FIRST_NESTED_SHA,
         "reject altered complete nested child lifecycle evidence")
    nested = parent.document(state["original_base"], state["guard"],
                             nested_raw, "actual V20 complete child lifecycle")
    detail = nested.get("complete_original_failure_details")
    need(nested.get("schema")
         == "rebar-owned-six-family-original-p0-producer-v5-genuine-nested-failure"
         and nested.get("actual_child_guards_installed") == 1
         and nested.get("expected_interpreters_created") == 11
         and nested.get("expected_case_interpreter_exec_calls") == 394
         and type(detail) is dict
         and detail.get("active_phase") == "install-original-private-guard-A"
         and detail.get("actual_interpreters_created") == 2
         and detail.get("actual_interpreters_destroyed") == 2
         and detail.get("actual_initialization_interpreter_exec_calls") == 1
         and detail.get("actual_case_interpreter_exec_calls") == 0
         and detail.get("actual_prepared_interpreter_ids") == []
         and detail.get("pipe_ledgers") == []
         and detail.get("error_type") == "GuardError"
         and detail.get("error_message")
         == "runtime guard blocked unattested-child-bootstrap",
         "distinguish one generated old bootstrap from zero real attested children")
    return {"receipt": value, "rows": rows, "restored": restored,
            "diagnostic": diagnostic, "nested": nested,
            "destructor_warning_count": 16, "streams": material}


def load_previous() -> dict:
    previous = bootstrap(V20[0], "_rebar_v21_exact_frozen_previous_v20")
    for owner in V20[1:]:
        secure_owner(owner)
    need(previous.SOURCE == V20[0][0]
         and previous.PROTOCOL == V20[1][0]
         and previous.CONTRACT == V20[2][0]
         and previous.SCHEMA
         == "rebar-owned-repaired-rust-original-campaign-v20"
         and previous.VERSION == 20,
         "load only the complete genuine V20 original campaign source")
    campaign, ancestor, parent, historical_context, _unused, evidence, history, proof = (
        previous.load_previous()
    )
    previous.prepare_parent(parent, campaign, ancestor,
                            historical_context, evidence, history, proof)
    context, state = parent.verify_context(V20[0][1], V20[1][1], V20[2][1])
    context = previous.enrich(context, campaign, ancestor,
                              historical_context, evidence, proof)
    state["historical_v2"] = history
    state["v17_failure"] = parent.document(
        state["original_base"], state["guard"],
        secure_owner(ancestor.V17_FAILURE),
        "genuine historical V17 source-only entry failure")
    state["v18_failure"] = proof["failure_v18"]
    state["actual_v19_receipt"] = evidence
    need(context.get("status") == "PASS"
         and context.get("schema") == previous.SCHEMA + "-frozen-context"
         and context.get("source_sha256") == V20[0][1]
         and context.get("protocol_sha256") == V20[1][1]
         and context.get("contract_sha256") == V20[2][1]
         and context.get("suite_count") == WORKER_COUNT
         and context.get("case_execution_denominator") == CASE_COUNT
         and context.get("expanded_holdout_cases_opened") == 0,
         "authenticate complete historical V20 before new native migration")
    old_receipt = document(state["original_base"], state["guard"],
                           V20_FAILURE, "actual small V20 failed public receipt")
    observed = validate_v20_failure(old_receipt, previous, parent, state)
    return {"module": previous, "campaign": campaign, "ancestor": ancestor,
            "parent": parent, "historical_context": historical_context,
            "context": context, "state": state, "evidence": evidence,
            "history": history, "proof": proof, "actual_v20": observed}


def corrected_sources(original: tuple) -> tuple:
    need(type(original) is tuple and len(original) == 9,
         "preserve every first-party Rust source owner")
    result = tuple(
        (path, BRIDGE_SOURCE_SHA, BRIDGE_SOURCE_BYTES)
        if path == "candidates/rust/py_bridge.c"
        else (path, ADAPTER_SHA, ADAPTER_BYTES)
        if path == "candidates/rust_candidate.py"
        else (path, fingerprint, count)
        for path, fingerprint, count in original
    )
    need(sum(row[0] == "candidates/rust/py_bridge.c" for row in result) == 1
         and sum(row[0] == "candidates/rust_candidate.py" for row in result) == 1
         and len(result) == 9,
         "reject stale a0 bridge, missing f9 source, or external dependency")
    return result


def load_operational_guard(original_base: types.ModuleType,
                           canonical_guard: types.ModuleType) -> tuple:
    for owner in V3:
        secure_owner(owner)
    operational = bootstrap(V3[0], "_rebar_v21_actual_frozen_operational_guard_v3")
    need(operational.SELF == V3[0][0]
         and operational.PROTOCOL == V3[1][0]
         and operational.CONTRACT == V3[2][0]
         and tuple(operational.V2["source"]) == tuple(original_base.GUARD[0])
         and tuple(operational.V2["protocol"]) == tuple(original_base.GUARD[1])
         and tuple(operational.V2["contract"]) == tuple(original_base.GUARD[2])
         and operational.BASE.SELF == original_base.GUARD[0][0]
         and operational.BASE.PROTOCOL == original_base.GUARD[1][0]
         and operational.BASE.CONTRACT == original_base.GUARD[2][0]
         and operational.RuntimePolicy.__bases__
         == (operational.BASE.RuntimePolicy,)
         and operational.RuntimePolicy.prepare_family
         is operational.BASE.RuntimePolicy.prepare_family
         and operational.RuntimePolicy.prepare_family.__globals__
         is operational.BASE.__dict__
         and operational.RuntimePolicy.prepare_family.__code__.co_filename
         == ROOT + "/" + original_base.GUARD[0][0]
         and operational.canonical is operational.BASE.canonical
         and operational.JsonReader is operational.BASE.JsonReader
         and operational.child_bootstrap_source
         is operational.BASE.child_bootstrap_source,
         "preserve real V3 policy and exact immutable V2/V5 child identity")
    guard_bytes = secure_owner(V3[2])
    contract = operational.strict_document(
        guard_bytes, "actual frozen genuine-interpreter operational guard")
    normalized_guard = operational.canonical(contract)
    need(type(contract) is dict and type(normalized_guard) is bytes
         and 0 < len(normalized_guard) <= MAX_OWNER_BYTES,
         "reject incomplete genuine V3 operational guard document")
    predecessor = contract.get("immutable_predecessor_v2")
    producer = contract.get("immutable_producer_v5")
    bootstrap_proof = contract.get("subinterpreter_bootstrap")
    isolation = contract.get("runtime_isolation_policy")
    guard_effects = contract.get("source_only_effects")
    need(contract.get("schema")
         == "rebar-owned-candidate-runtime-independence-v3-source-freeze"
         and contract.get("version") == 3
         and contract.get("status")
         == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
         and contract.get("source", {}).get("sha256") == V3[0][1]
         and contract.get("protocol", {}).get("sha256") == V3[1][1]
         and type(predecessor) is dict and type(producer) is dict
         and type(bootstrap_proof) is dict
         and predecessor.get("version") == 2
         and predecessor.get("prepare_family")
         == "INHERITED EXACT V2 FUNCTION AND GLOBALS"
         and predecessor.get("child_bootstrap")
         == "UNCHANGED AUTHENTICATED V2 CHILD SOURCE"
         and producer.get("version") == 5
         and producer.get("source_mutated") is False
         and producer.get("child_guard_identity")
         == "EXACT V2 PREPARE GLOBALS AND CHILD PINS"
         and bootstrap_proof.get("suite") == "subinterpreter_v2"
         and bootstrap_proof.get("original_case_count") == 128
         and bootstrap_proof.get("expected_interpreters_created") == 11
         and bootstrap_proof.get("expected_interpreters_destroyed") == 11
         and bootstrap_proof.get("expected_case_interpreter_exec_calls") == 394
         and bootstrap_proof.get("expected_bootstrap_interpreter_exec_calls") == 11
         and bootstrap_proof.get("expected_cleanup_interpreter_exec_calls") == 11
         and bootstrap_proof.get("expected_total_real_interpreter_exec_calls")
         == 416
         and bootstrap_proof.get("creation_audit_event")
         == "cpython.PyInterpreterState_New"
         and bootstrap_proof.get("actual_interpreters_created") == 0
         and bootstrap_proof.get("actual_interpreters_destroyed") == 0
         and bootstrap_proof.get("actual_case_interpreter_exec_calls") == 0
         and bootstrap_proof.get("actual_bootstrap_interpreter_exec_calls") == 0
         and bootstrap_proof.get("actual_cleanup_interpreter_exec_calls") == 0
         and bootstrap_proof.get("actual_child_guards_installed") == 0
         and bootstrap_proof.get("candidate_status") == "NOT RUN"
         and type(isolation) is dict
         and isolation.get("guard_installed_before_candidate_import") is True
         and isolation.get("stdlib_re_engine") == "FORBIDDEN"
         and isolation.get("stdlib_sre_engine") == "FORBIDDEN"
         and isolation.get("external_regex_package") == "FORBIDDEN"
         and isolation.get("cross_candidate_engine") == "FORBIDDEN"
         and isolation.get("matching_fallback") == "FORBIDDEN"
         and type(guard_effects) is dict
         and all(guard_effects.get(name) == 0
                 for name in operational.EFFECT_KEYS)
         and contract.get("holdout") == "NOT OPENED",
         "reject an invented guard run, replaced child source, or V3 contract")
    for index, role in enumerate(("source", "protocol", "contract")):
        item = predecessor.get("owners", {}).get(role)
        expected = original_base.GUARD[index]
        need(type(item) is dict and item.get("path") == expected[0]
             and item.get("sha256") == expected[1]
             and item.get("bytes") == expected[2]
             and item.get("device") == DEVICE
             and item.get("inode") == expected[3]
             and item.get("mode") == "0600" and item.get("nlink") == 1,
             "reject forged V3 immutable child V2 " + role)
        item = producer.get("owners", {}).get(role)
        expected = original_base.PRODUCER[index]
        need(type(item) is dict and item.get("path") == expected[0]
             and item.get("sha256") == expected[1]
             and item.get("bytes") == expected[2]
             and item.get("device") == DEVICE
             and item.get("inode") == expected[3]
             and item.get("mode") == "0600" and item.get("nlink") == 1,
             "reject forged V3 immutable original V5 " + role)
    return operational, contract


def build_v22_parent(loaded: dict, build: dict, root: dict,
                     freeze: dict, operational: types.ModuleType) -> dict:
    ancestor = loaded["ancestor"]
    original_parent = loaded["state"]["parent"]
    original_base = loaded["state"]["original_base"]
    parent = bootstrap(ancestor.V17[0],
                       "_rebar_v21_v22_migrated_original_campaign_parent",
                       migrate_v21=True)
    values = {
        "SOURCE": SOURCE, "PROTOCOL": PROTOCOL, "CONTRACT": CONTRACT,
        "SCHEMA": SCHEMA, "VERSION": VERSION, "FAMILY": FAMILY,
        "BUILD_LABEL": BUILD_LABEL, "LABEL": LABEL,
        "RECOVERY_PREFIX": RECOVERY_PREFIX, "RECOVERY_ROOT": RECOVERY_ROOT,
        "V21": V22, "V21_PUBLICATION": V22_PUBLICATION,
        "V21_ROOT": V22_ROOT_RECEIPT, "ROOT_DEVICE": ROOT_DEVICE,
        "ROOT_INODE": ROOT_INODE, "ROOT_PATH": ROOT_PATH,
        "ENGINE_SHA": ENGINE_SHA, "ENGINE_BYTES": ENGINE_BYTES,
        "BRIDGE_SHA": BRIDGE_SHA, "BRIDGE_BYTES": BRIDGE_BYTES,
        "CAPTURE_SHA": BRIDGE_SOURCE_SHA,
        "CAPTURE_BYTES": BRIDGE_SOURCE_BYTES,
        "ADAPTER_SHA": ADAPTER_SHA, "ADAPTER_BYTES": ADAPTER_BYTES,
        "ARCHIVE_SHA": ARCHIVE_SHA, "ARCHIVE_BYTES": ARCHIVE_BYTES,
        "ARCHIVE_INODE": ARCHIVE_INODE, "PLAIN_SHA": PLAIN_SHA,
        "PLAIN_BYTES": PLAIN_BYTES,
        "PHASE_NATIVE_INODES": PHASE_NATIVE_INODES,
        "CORRECTED_SOURCES": corrected_sources(
            tuple(loaded["parent"].CORRECTED_SOURCES)),
    }
    for name, value in values.items():
        setattr(parent, name, value)

    def validate(build_document: dict, root_document: dict,
                 freeze_document: dict) -> dict:
        return validate_v22(build_document, root_document, freeze_document)

    parent.validate_v21_documents = validate
    base = parent.make_v21_base(original_parent, original_base,
                                build, root, freeze)
    need(tuple(base.GUARD) == tuple(original_base.GUARD)
         and base.BUILD == V22 and base.BUILD_RECEIPT == V22_PUBLICATION
         and base.ROOT_RECEIPT == V22_ROOT_RECEIPT
         and base.BUILD_LABEL == BUILD_LABEL
         and base.ROOT_PATH == ROOT_PATH and base.ROOT_DEVICE == ROOT_DEVICE
         and base.ROOT_INODE == ROOT_INODE
         and base.ENGINE_SHA == ENGINE_SHA and base.ENGINE_BYTES == ENGINE_BYTES
         and base.BRIDGE_SHA == BRIDGE_SHA and base.BRIDGE_BYTES == BRIDGE_BYTES
         and base.CORRECTED_ADAPTER_SHA == ADAPTER_SHA
         and base.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES
         and tuple(base.P0) == tuple(original_base.P0)
         and tuple(base.PRODUCER) == tuple(original_base.PRODUCER)
         and tuple(base.ROLE_ORDER) == tuple(original_base.ROLE_ORDER),
         "reject old V21 native globals or replacement of V2/V5/P0 recovery")
    base.load_guard = lambda: operational
    original_install = base.install_worker_guard

    def exact_guard_install(guard: types.ModuleType) -> dict:
        need(guard is operational,
             "install only the actual independently frozen V3 operational policy")
        bundle = original_install(guard)
        need(type(bundle) is dict and type(bundle.get("policy"))
             is operational.RuntimePolicy
             and bundle["policy"].installed is True
             and bundle.get("candidate") is sys.modules.get("re")
             and bundle.get("candidate")
             is sys.modules.get("candidates.rust_candidate")
             and "_sre" not in sys.modules and "ctypes" not in sys.modules,
             "install V3 before exactly one attested first-party candidate import")
        for role in ("bridge", "engine"):
            expected = canonical_native_owner(bundle[role], role)
            need(bundle[role] == expected
                 and getattr(bundle["policy"], role + "_owner") == expected,
                 "prepare only the exact immutable V5 fourteen-field " + role)
        bundle["policy"].check_modules()
        return bundle

    base.install_worker_guard = exact_guard_install
    runner = parent.make_runner(original_parent)
    need(runner.SOURCE == SOURCE and runner.PROTOCOL == PROTOCOL
         and runner.CONTRACT == CONTRACT and runner.SCHEMA == SCHEMA
         and runner.LABEL == LABEL and runner.RECOVERY_PREFIX == RECOVERY_PREFIX
         and runner.RECOVERY_ROOT == RECOVERY_ROOT
         and tuple(runner.SUITES) == SUITES
         and runner.WORKER_COUNT == WORKER_COUNT
         and runner.CASE_COUNT == CASE_COUNT,
         "migrate the genuine immutable 13-worker V16 implementation to V22")
    inherited = runner.actual_required_authority

    def required(actual_base: types.ModuleType) -> dict[str, str]:
        result = dict(inherited(actual_base))
        result.update({
            "combined_bridge_sha256": BRIDGE_SOURCE_SHA,
            "combined_bridge_bytes": str(BRIDGE_SOURCE_BYTES),
            "operational_guard_v3_source_sha256": V3[0][1],
            "operational_guard_v3_protocol_sha256": V3[1][1],
            "operational_guard_v3_contract_sha256": V3[2][1],
            "previous_v20_source_sha256": V20[0][1],
            "previous_v20_protocol_sha256": V20[1][1],
            "previous_v20_contract_sha256": V20[2][1],
            "previous_v20_failure_receipt_sha256": V20_FAILURE[1],
        })
        return result

    runner.actual_required_authority = required
    runner.bounded_diagnostic_traceback = bounded_unicode_traceback
    historical_campaign = bootstrap(
        loaded["module"].V19[0], "_rebar_v21_authenticated_historical_v19")
    for name, value in (
            ("SCHEMA", SCHEMA), ("VERSION", VERSION), ("SOURCE", SOURCE),
            ("PROTOCOL", PROTOCOL), ("CONTRACT", CONTRACT),
            ("BUILD_LABEL", BUILD_LABEL), ("BUILD_SUFFIX", BUILD_SUFFIX),
            ("LABEL", LABEL), ("RECOVERY_PREFIX", RECOVERY_PREFIX),
            ("RECOVERY_ROOT", RECOVERY_ROOT)):
        setattr(historical_campaign, name, value)
    helper = bootstrap(V20[0], "_rebar_v21_exact_original_v20_observer_helper")
    for name, value in (
            ("SCHEMA", SCHEMA), ("VERSION", VERSION), ("SOURCE", SOURCE),
            ("PROTOCOL", PROTOCOL), ("CONTRACT", CONTRACT),
            ("BUILD_LABEL", BUILD_LABEL), ("BUILD_SUFFIX", BUILD_SUFFIX),
            ("LABEL", LABEL), ("RECOVERY_PREFIX", RECOVERY_PREFIX),
            ("RECOVERY_ROOT", RECOVERY_ROOT)):
        setattr(helper, name, value)
    parent.bind_captured_controller = helper.corrected_controller(
        historical_campaign, parent, loaded["history"])
    return {"parent": parent, "base": base, "runner": runner,
            "guard": operational, "original_base": original_base,
            "historical_parent": original_parent, "helper": helper,
            "historical_campaign": historical_campaign,
            "build": build, "root": root, "freeze": freeze,
            "required": required(base)}


def canonical_native_owner(owner: dict, role: str) -> dict:
    need(type(owner) is dict and set(owner) == NATIVE_OWNER_KEYS
         and role in ("bridge", "engine")
         and owner.get("role") == role and owner.get("family") == FAMILY,
         "reject cross-family actual native owner: " + role)
    relative = owner.get("relative")
    count = owner.get("bytes")
    expected_sha = BRIDGE_SHA if role == "bridge" else ENGINE_SHA
    expected_bytes = BRIDGE_BYTES if role == "bridge" else ENGINE_BYTES
    need(type(relative) is str and relative.startswith("candidates/")
         and ".." not in relative.split("/")
         and owner.get("absolute_path") == ROOT + "/" + relative
         and owner.get("sha256") == expected_sha and count == expected_bytes
         and owner.get("device") == DEVICE
         and type(owner.get("inode")) is int and owner["inode"] > 0
         and owner.get("mode") == 0o600
         and owner.get("uid") == os.geteuid()
         and owner.get("nlink") == 1,
         "reject unverified genuine activated Rust " + role + " identity")
    result = {
        "role": role, "family": FAMILY,
        "absolute_path": ROOT + "/" + relative,
        "relative": relative, "file_name": relative.rsplit("/", 1)[-1],
        "sha256": expected_sha, "bytes": expected_bytes,
        "size_bytes": expected_bytes, "device": DEVICE,
        "inode": owner["inode"], "mode": 0o600,
        "uid": os.geteuid(), "nlink": 1, "native_loaded": False,
    }
    need(set(result) == NATIVE_OWNER_KEYS and len(result) == 14,
         "require exactly fourteen immutable V5-compatible native owner fields")
    need(owner == result,
         "reject stale, extra, omitted, or loaded actual native owner")
    return result


def bounded_unicode_traceback(legacy: types.ModuleType, budget: dict) -> dict:
    text = legacy.traceback.format_exc()
    need(type(text) is str, "preserve the actual complete worker exception")
    raw = text.encode("utf-8", "surrogatepass")
    remaining = max(0, MAX_DIAGNOSTIC_BYTES - budget["captured_bytes"])
    maximum = min(65536, remaining)
    prefix = raw[:maximum]
    while prefix:
        try:
            reversible = prefix.decode("utf-8", "surrogatepass")
            break
        except UnicodeDecodeError as error:
            need(error.end == len(prefix),
                 "reject a corrupted genuine traceback transport")
            prefix = prefix[:error.start]
    else:
        reversible = ""
    need(reversible.encode("utf-8", "surrogatepass") == prefix,
         "reject lossy or guessed Unicode diagnostic transport")
    budget["captured_bytes"] += len(prefix)
    return {
        "text": reversible,
        "complete": len(prefix) == len(raw),
        "truncated": len(prefix) != len(raw),
        "source_size_bytes": len(raw),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "captured_size_bytes": len(prefix),
        "capture_limit_bytes": maximum,
        "unicode_transport": "UTF-8 SURROGATEPASS; REVERSIBLE",
    }


def verify_context(options: dict, wall: PhysicalSourceWall | None) -> tuple:
    verify_runtime()
    secure_owner(dynamic_owner(SOURCE, options["source_sha256"]))
    secure_owner(dynamic_owner(PROTOCOL, options["protocol_sha256"]))
    rendering = options["mode"] == "--render-contract"
    if not rendering:
        secure_owner(dynamic_owner(CONTRACT, options["contract_sha256"]))
    loaded = load_previous()
    if wall is not None:
        inherited_error = loaded["parent"].CampaignError
        need(type(loaded["parent"]) is types.ModuleType
             and loaded["parent"].__file__
             == ROOT + "/" + loaded["ancestor"].V17[0][0]
             and type(inherited_error) is type
             and issubclass(inherited_error, Exception)
             and inherited_error.__name__ == "CampaignError"
             and inherited_error.__module__ == loaded["parent"].__name__,
             "authenticate the immutable predecessor hostile-control exception")
        wall.error_type = inherited_error
    old_state = loaded["state"]
    original_base = old_state["original_base"]
    canonical_guard = old_state["guard"]
    for owner in V22:
        secure_owner(owner)
    build = document(original_base, canonical_guard, V22_PUBLICATION,
                     "actual first-party V22 public native-build receipt")
    root = document(original_base, canonical_guard, V22_ROOT_RECEIPT,
                    "actual first-party V22 receipt-only private provenance")
    freeze = document(original_base, canonical_guard, V22[2],
                      "complete frozen V22 first-party source contract")
    native_proof = validate_v22(build, root, freeze)
    operational, operational_contract = load_operational_guard(
        original_base, canonical_guard)
    state = build_v22_parent(loaded, build, root, freeze, operational)
    required = state["required"]
    need(required.get("family") == FAMILY
         and required.get("label") == LABEL
         and required.get("activation_root") == RECOVERY_ROOT
         and required.get("build_private_root") == ROOT_PATH
         and required.get("build_private_root_device") == str(ROOT_DEVICE)
         and required.get("build_private_root_inode") == str(ROOT_INODE)
         and required.get("build_source_sha256") == V22[0][1]
         and required.get("build_protocol_sha256") == V22[1][1]
         and required.get("build_contract_sha256") == V22[2][1]
         and required.get("build_archive_sha256") == ARCHIVE_SHA
         and required.get("build_receipt_sha256") == V22_PUBLICATION[1]
         and required.get("root_receipt_sha256") == V22_ROOT_RECEIPT[1]
         and required.get("native_engine_sha256") == ENGINE_SHA
         and required.get("native_engine_bytes") == str(ENGINE_BYTES)
         and required.get("native_bridge_sha256") == BRIDGE_SHA
         and required.get("native_bridge_bytes") == str(BRIDGE_BYTES)
         and required.get("combined_bridge_sha256") == BRIDGE_SOURCE_SHA
         and required.get("combined_bridge_bytes") == str(BRIDGE_SOURCE_BYTES)
         and required.get("operational_guard_v3_source_sha256") == V3[0][1]
         and required.get("operational_guard_v3_protocol_sha256") == V3[1][1]
         and required.get("operational_guard_v3_contract_sha256") == V3[2][1]
         and required.get("previous_v20_failure_receipt_sha256") == V20_FAILURE[1],
         "reject missing V22 native, V3 operational guard, or V20 authority")
    result = dict(loaded["context"])
    for key in tuple(result):
        if key.startswith("actual_v21_build_") or key.startswith(
                ("actual_v21_native_", "actual_v21_private_",
                 "actual_v21_capture_", "actual_v21_source_",
                 "actual_v21_root_", "actual_v21_compiler_")):
            result["historical_" + key] = result.pop(key)
    result.update({
        "schema": SCHEMA + "-frozen-context", "status": "PASS",
        "version": VERSION,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options.get("contract_sha256"),
        "previous_v20_source_sha256": V20[0][1],
        "previous_v20_protocol_sha256": V20[1][1],
        "previous_v20_contract_sha256": V20[2][1],
        "actual_v20_failure_receipt_sha256": V20_FAILURE[1],
        "actual_v20_durable_publication_status": "PASS",
        "actual_v20_candidate_status": "FAIL",
        "actual_v20_candidate_qualified": False,
        "actual_v20_original_campaign_attempted": True,
        "actual_v20_actual_candidate_workers": WORKER_COUNT,
        "actual_v20_distinct_worker_process_count": WORKER_COUNT,
        "actual_v20_completed_suite_count": 12,
        "actual_v20_verified_passing_case_count": 15749,
        "actual_v20_substitution_observed_mismatch_count": 240,
        "actual_v20_shape_observed_mismatch_count": 1056,
        "actual_v20_fully_observed_semantic_mismatch_lower_bound": 1296,
        "actual_v20_total_semantic_mismatch_count": "NOT MEASURED",
        "actual_v20_infrastructure_failure_count": 1,
        "actual_v20_infrastructure_failure_suite": "subinterpreter_v2",
        "actual_v20_nested_failure_type": "GuardError",
        "actual_v20_nested_failure_message":
            "runtime guard blocked unattested-child-bootstrap",
        "actual_v20_nested_active_phase": "install-original-private-guard-A",
        "actual_v20_nested_interpreters_created": 2,
        "actual_v20_nested_interpreters_destroyed": 2,
        "actual_v20_nested_prepared_interpreter_ids": [],
        "actual_v20_nested_matching_execution_count": 0,
        "actual_v20_nested_generated_bootstrap_count": 1,
        "actual_v20_nested_registered_bootstrap_count": 0,
        "actual_v20_stderr_sha256": FIRST_STDERR_SHA,
        "actual_v20_stdout_sha256": FIRST_STDOUT_SHA,
        "actual_v20_traceback_sha256": FIRST_TRACEBACK_SHA,
        "actual_v20_nested_diagnostic_sha256": FIRST_NESTED_SHA,
        "actual_v20_destructor_warning_count": 16,
        "actual_v20_all_four_original_targets_restored": True,
        "actual_v20_original_target_owners": [
            {"role": role, "relative": relative, "sha256": fingerprint,
             "bytes": count, "device": DEVICE, "inode": inode,
             "mode": mode, "uid": os.geteuid(), "nlink": 1}
            for role, relative, fingerprint, count, inode, mode in ORIGINALS
        ],
        "actual_v20_complete_original_suite_integrity": [
            dict(row) for row in loaded["actual_v20"]["rows"]
        ],
        "actual_v22_build_source_sha256": V22[0][1],
        "actual_v22_build_protocol_sha256": V22[1][1],
        "actual_v22_build_contract_sha256": V22[2][1],
        "actual_v22_build_receipt_sha256": V22_PUBLICATION[1],
        "actual_v22_root_receipt_sha256": V22_ROOT_RECEIPT[1],
        "actual_v22_build_label": BUILD_LABEL,
        "actual_v22_compiler_process_count": 28,
        "actual_v22_compiler_individual_pids": "NOT PUBLISHED",
        "actual_v22_source_build_phase_count": native_proof["phase_count"],
        "actual_v22_native_artifact_count": native_proof["native_artifact_count"],
        "actual_v22_private_build_root_provenance":
            "AUTHENTICATED SMALL PUBLIC ROOT RECEIPT ONLY; NOT OPENED",
        "actual_v22_private_build_root": ROOT_PATH,
        "actual_v22_private_build_root_device": ROOT_DEVICE,
        "actual_v22_private_build_root_inode": ROOT_INODE,
        "actual_v22_native_engine_sha256": ENGINE_SHA,
        "actual_v22_native_engine_bytes": ENGINE_BYTES,
        "actual_v22_native_bridge_sha256": BRIDGE_SHA,
        "actual_v22_native_bridge_bytes": BRIDGE_BYTES,
        "actual_v22_corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA,
        "actual_v22_corrected_bridge_source_bytes": BRIDGE_SOURCE_BYTES,
        "actual_v22_corrected_adapter_sha256": ADAPTER_SHA,
        "actual_v22_corrected_adapter_bytes": ADAPTER_BYTES,
        "actual_v22_archive_metadata_sha256": ARCHIVE_SHA,
        "actual_v22_archive_metadata_bytes": ARCHIVE_BYTES,
        "actual_v22_archive_opened": False,
        "operational_guard_version": 3,
        "operational_guard_v3_source_sha256": V3[0][1],
        "operational_guard_v3_protocol_sha256": V3[1][1],
        "operational_guard_v3_contract_sha256": V3[2][1],
        "immutable_child_guard_v2_source_sha256":
            original_base.GUARD[0][1],
        "immutable_child_guard_v2_protocol_sha256":
            original_base.GUARD[1][1],
        "immutable_child_guard_v2_contract_sha256":
            original_base.GUARD[2][1],
        "immutable_original_v5_producer_source_sha256":
            original_base.PRODUCER[0][1],
        "operational_guard_preserves_exact_v2_prepare_family": True,
        "operational_guard_preserves_exact_v2_child_source": True,
        "actual_v3_child_interpreters_created": 0,
        "actual_v3_child_interpreters_destroyed": 0,
        "actual_v3_registered_child_bootstraps": 0,
        "actual_v3_original_case_interpreter_exec_calls": 0,
        "actual_v3_total_real_interpreter_exec_calls": 0,
        "expected_real_child_interpreters": 11,
        "expected_original_case_interpreter_exec_calls": 394,
        "expected_total_real_interpreter_exec_calls": 416,
        "required_native_owner_field_count": 14,
        "corrected_rust_source_owner_count": 9,
        "corrected_rust_source_owners": [
            {"path": path, "sha256": fingerprint, "bytes": count}
            for path, fingerprint, count in state["parent"].CORRECTED_SOURCES
        ],
        "candidate_aware_harness_source_overlay_sites": 1,
        "candidate_aware_public_core_source_overlay_sites": 1,
        "candidate_aware_observer_changes_frozen_oracle_bytes": False,
        "candidate_aware_observer_weakens_runtime_guard": False,
        "candidate_aware_observer_claims_semantic_repair": False,
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "supplemental_case_count": SUPPLEMENTAL_CASE_COUNT,
        "supplemental_cases_counted_in_original_denominator": False,
        "expanded_holdout_proposal_case_count": HOLDOUT_CASE_COUNT,
        "expanded_holdout_cases_generated": 0,
        "expanded_holdout_cases_opened": 0,
        "planned_actual_original_candidate_worker_count": WORKER_COUNT,
        "suites": [{"id": name, "case_execution_count": count}
                   for name, count in SUITES],
        "recovery_role_order": [row[0] for row in ORIGINALS],
        "recovery_restoration_order": [row[0] for row in reversed(ORIGINALS)],
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v21.lock",
        "expected_actual_evidence_stem":
            "repaired-rust-original-campaign-v16-rust-" + LABEL,
        "future_failed_worker_capture":
            "COMPLETE BOUNDED ACTUAL STDOUT STDERR TRACEBACK; REVERSIBLE UTF-8",
        "actual_v21_original_campaign_attempted": False,
        "actual_v21_candidate_semantic_mismatch_count": "NOT MEASURED",
        "actual_candidate_imports": 0,
        "actual_candidate_workers_started": 0,
        "actual_reference_workers_started": 0,
        "actual_compiler_processes_started": 0,
        "actual_native_libraries_loaded": 0,
        "actual_private_build_root_opens": 0,
        "actual_private_build_root_stats": 0,
        "actual_build_archive_opens": 0,
        "actual_build_archive_inflations": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "timing_trials_run": 0,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "confidence_intervals": "NOT MEASURED",
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
        "source_wall_installed_before_predecessor": wall is not None,
    })
    need(sum(count for _, count in SUITES) == CASE_COUNT
         and len(SUITES) == WORKER_COUNT
         and len(result["named_private_waivers"]) == PRIVATE_WAIVER_COUNT
         and operational_contract["source_only_effects"]
             ["subinterpreters_created"] == 0,
         "retain every original obligation without manufacturing child success")
    if not rendering:
        actual = document(original_base, canonical_guard,
                          dynamic_owner(CONTRACT, options["contract_sha256"]),
                          "complete new V21 V3-guarded machine contract")
        need(actual == contract_document(result),
             "reject missing, altered, or extra original-campaign obligations")
    state.update({"loaded": loaded, "operational_contract": operational_contract,
                  "native_proof": native_proof, "context": result,
                  "prior_parent": loaded["parent"]})
    verify_runtime()
    return result, state


def contract_document(context: dict) -> dict:
    result = dict(context)
    result["schema"] = SCHEMA + "-recoverable-source-freeze"
    result["status"] = "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
    result.pop("contract_sha256", None)
    return result


def rejected(action: object, label: str, *kinds: type) -> str:
    need(callable(action), "require one executable source-only hostile control")
    try:
        action()
    except (CampaignError, ValueError, TypeError, OSError, UnicodeError,
            SyntaxError, *kinds):
        return label
    raise CampaignError("accepted hostile V3/V22 original authority: " + label)


def clone_document(guard: types.ModuleType, base: types.ModuleType,
                   item: dict) -> dict:
    raw = guard.canonical(item)
    result = base.parse_document(guard, raw, "synthetic canonical hostility")
    need(type(result) is dict and guard.canonical(result) == raw,
         "require complete synthetic canonical test only")
    return result


def source_controls(context: dict, state: dict,
                    wall: PhysicalSourceWall) -> list[str]:
    loaded = state["loaded"]
    previous = loaded["module"]
    prior_parent = loaded["parent"]
    campaign = loaded["campaign"]
    ancestor = loaded["ancestor"]
    old_state = loaded["state"]
    checks = list(prior_parent.hostile_controls(
        loaded["context"], old_state, wall))
    checks.extend(previous.source_hostile_controls(
        prior_parent, campaign, ancestor, old_state,
        loaded["evidence"], loaded["history"], loaded["proof"]))
    kinds = (prior_parent.CampaignError, previous.CampaignError,
             campaign.CampaignError, ancestor.CampaignError,
             state["guard"].BootstrapError, state["guard"].GuardError)
    for event, args, label in (
            ("import", ("re",), "stdlib-re"),
            ("import", ("_sre",), "stdlib-native-regex"),
            ("import", ("regex",), "external-regex"),
            ("import", ("ctypes",), "ctypes-native"),
            ("import", ("candidates.rust_candidate",), "early-rust-import"),
            ("import", ("concurrent.interpreters",), "actual-child-provider"),
            ("subprocess.Popen", ("blocked",), "candidate-worker"),
            ("socket.connect", ("blocked",), "network"),
            ("ctypes.dlopen", ("blocked",), "native-load"),
            ("cpython.PyInterpreterState_New", (), "actual-child"),
            ("_interpreters.create", (), "synthetic-child"),
            ("open", (ROOT_PATH, "r", 0), "private-root"),
            ("open", (ROOT + "/candidates/rust_candidate.py", "r", 0),
             "current-rust-adapter"),
            ("open", (ROOT + "/candidates/rust/py_bridge.c", "r", 0),
             "current-rust-bridge-source"),
            ("open", (ROOT + "/candidates/_rust_engine.so", "r", 0),
             "current-native-engine"),
            ("open", (ROOT + "/tools/../candidates/rust_candidate.py",
                       "r", 0), "traversal-to-current-rust-adapter"),
            ("open", (ROOT + "/tools/./../candidates/rust_candidate.py",
                       "r", 0), "dot-traversal-to-current-rust-adapter"),
            ("open", (ROOT + "/tools//../candidates/rust_candidate.py",
                       "r", 0), "separator-traversal-to-current-rust-adapter"),
            ("open", (ROOT + "/tools/../candidates/_rust_engine.so",
                       "r", 0), "traversal-to-current-native-engine"),
            ("open", (ROOT + "/oracle/phase2/../../candidates/"
                       "rust_candidate.py", "r", 0),
             "oracle-traversal-to-current-rust-adapter"),
            ("open", (ROOT + "/tools/../oracle/phase2/evidence/"
                       "native-source-build-v22-rust-"
                       "phase2-v22-rust-capture-shape-root-provenance.json.gz",
                       "r", 0), "traversal-to-compressed-build-archive"),
            ("open", (ROOT + "/tools/../../../../tmp/hidden-holdout",
                       "r", 0), "traversal-to-secret-holdout"),
            ("open", (PYTHON.rsplit("/bin/", 1)[0]
                       + "/lib/python3.14/collections/../re/__init__.py",
                       "r", 0), "stdlib-traversal-to-regex-parser"),
            ("open", (PYTHON.rsplit("/bin/", 1)[0]
                       + "/lib/python3.14/../../../../../home/dev-user/"
                       "src/rebar/candidates/rust_candidate.py", "r", 0),
             "stdlib-traversal-to-current-rust-adapter"),
            ("open", (ROOT + "//tools/run_owned_repaired_"
                       "rust_original_campaign_v21.py", "r", 0),
             "noncanonical-double-separator"),
            ("open", (ROOT + "/" + state["build"]["archive_relative"],
                       "r", 0), "compressed-build-archive"),
            ("open", ("/tmp/rebar-hidden-holdout", "r", 0), "secret-holdout"),
            ("open", (ROOT + "/" + SOURCE, "w", os.O_WRONLY),
             "frozen-source-write")):
        checks.append(rejected(
            lambda name=event, values=args: wall.audit(name, values),
            "preinstalled-wall-rejects-" + label, *kinds))
    for name in ("time", "monotonic", "perf_counter", "sleep"):
        operation = getattr(time, name, None)
        if callable(operation):
            checks.append(rejected(
                lambda call=operation, label=name:
                call(0) if label == "sleep" else call(),
                "physical-wall-rejects-clock-" + name, *kinds))
    for name in ("urandom", "getrandom"):
        operation = getattr(os, name, None)
        if callable(operation):
            checks.append(rejected(lambda call=operation: call(8),
                                   "physical-wall-rejects-entropy-" + name,
                                   *kinds))
    guard = old_state["guard"]
    base = old_state["original_base"]
    original = loaded["actual_v20"]["receipt"]
    for key, value, label in (
            ("candidate_status", "PASS", "forged-v20-candidate-pass"),
            ("candidate_qualified", True, "forged-v20-qualification"),
            ("completed_suite_count", 13, "invented-v20-child-completion"),
            ("verified_passing_case_count", 17045, "counted-v20-mismatches"),
            ("semantic_mismatch_count", 1296, "invented-v20-global-total"),
            ("infrastructure_failure_count", 0, "hidden-v20-child-failure"),
            ("all_four_original_targets_restored", False,
             "missing-v20-four-owner-restoration"),
            ("holdout", "OPENED", "opened-v20-holdout")):
        bad = clone_document(guard, base, original)
        bad[key] = value
        checks.append(rejected(
            lambda item=bad: validate_v20_failure(
                item, previous, prior_parent, old_state),
            "reject-" + label, *kinds))
    for index, field, value, label in (
            (7, "mismatch_count", 0, "hidden-actual-240-substitution"),
            (8, "mismatch_count", 0, "hidden-actual-1056-shape"),
            (10, "fully_observed", True, "invented-real-child-pass"),
            (10, "mismatch_count", 0, "guessed-real-child-mismatch"),
            (10, "pid", 0, "missing-real-child-pid"),
            (10, "complete_original_row_sha256", "0" * 64,
             "changed-real-child-row")):
        bad = clone_document(guard, base, original)
        bad["suite_integrity"][index][field] = value
        checks.append(rejected(
            lambda item=bad: validate_v20_failure(
                item, previous, prior_parent, old_state),
            "reject-" + label, *kinds))
    for role, field, value in (
            ("bridge_source", "sha256", "0" * 64),
            ("adapter", "inode", 1),
            ("engine", "mode", 0o600),
            ("bridge", "bytes", BRIDGE_BYTES)):
        bad = clone_document(guard, base, original)
        bad["restored_original_targets"][role][field] = value
        checks.append(rejected(
            lambda item=bad: validate_v20_failure(
                item, previous, prior_parent, old_state),
            "reject-changed-real-original-" + role + "-" + field, *kinds))
    for key, value in (
            ("combined_bridge_sha256", "0" * 64),
            ("combined_bridge_bytes", BRIDGE_SOURCE_BYTES - 1),
            ("actual_compiler_process_count", 27),
            ("corrected_public_adapter_sha256", "0" * 64),
            ("archive_sha256", "0" * 64),
            ("candidate_workers_started", 1),
            ("native_libraries_loaded", 1),
            ("hidden_cases_read", 1)):
        bad = clone_document(guard, base, state["build"])
        bad[key] = value
        checks.append(rejected(
            lambda item=bad: validate_v22(item, state["root"], state["freeze"]),
            "reject-forged-v22-build-" + key, *kinds))
    for phase in range(2):
        for native in range(2):
            for field, value in (("sha256", "0" * 64),
                                 ("bytes", 1), ("inode", 1),
                                 ("native_loaded", True)):
                bad = clone_document(guard, base, state["root"])
                bad["root"]["phases"][phase]["native_outputs"][native][field] = (
                    value
                )
                checks.append(rejected(
                    lambda item=bad: validate_v22(
                        state["build"], item, state["freeze"]),
                    "reject-v22-phase-" + str(phase) + "-native-"
                    + str(native) + "-" + field, *kinds))
    synthetic = {
        "role": "bridge", "family": FAMILY,
        "absolute_path": ROOT + "/candidates/"
        "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "file_name": "_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": BRIDGE_SHA, "bytes": BRIDGE_BYTES,
        "size_bytes": BRIDGE_BYTES, "device": DEVICE,
        "inode": 71321, "mode": 0o600, "uid": os.geteuid(),
        "nlink": 1, "native_loaded": False,
    }
    need(canonical_native_owner(synthetic, "bridge") == synthetic,
         "prove exact fourteen-field synthetic V5 native owner without loading")
    for field in sorted(NATIVE_OWNER_KEYS):
        bad = dict(synthetic)
        bad.pop(field)
        checks.append(rejected(
            lambda item=bad: canonical_native_owner(item, "bridge"),
            "reject-missing-v5-native-field-" + field, *kinds))
    for field, value in (("role", "engine"), ("family", "zig"),
                         ("sha256", "0" * 64), ("bytes", BRIDGE_BYTES - 1),
                         ("size_bytes", BRIDGE_BYTES - 1),
                         ("device", ROOT_DEVICE), ("inode", 0),
                         ("mode", 0o700), ("uid", os.geteuid() + 1),
                         ("nlink", 2), ("native_loaded", True),
                         ("relative", "candidates/foreign.so"),
                         ("absolute_path", ROOT + "/foreign.so"),
                         ("file_name", "foreign.so")):
        bad = dict(synthetic)
        bad[field] = value
        checks.append(rejected(
            lambda item=bad: canonical_native_owner(item, "bridge"),
            "reject-changed-v5-native-field-" + field, *kinds))
    extra = dict(synthetic)
    extra["path"] = synthetic["absolute_path"]
    checks.append(rejected(lambda: canonical_native_owner(extra, "bridge"),
                           "reject-extra-v5-native-path-field", *kinds))
    verify_runtime()
    need(wall.installed and len(checks) >= 200
         and sum(count for _, count in SUITES) == CASE_COUNT,
         "reject incomplete hostile coverage or real source-only side effects")
    return checks


def parse_options(arguments: list[str]) -> dict:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    selected = [item for item in arguments if item in modes]
    need(len(selected) == 1,
         "choose exactly one frozen-source or explicitly authorized actual mode")
    result: dict[str, object] = {"mode": selected[0]}
    cursor = 0
    while cursor < len(arguments):
        flag = arguments[cursor]
        if flag in modes:
            cursor += 1
            continue
        need(type(flag) is str and flag.startswith("--")
             and cursor + 1 < len(arguments),
             "reject unpinned, positional, or partial campaign authority")
        key = flag[2:].replace("-", "_")
        need(key not in result, "reject duplicate caller authority: " + flag)
        result[key] = arguments[cursor + 1]
        cursor += 2
    sha_pin(result.get("source_sha256"), "V21 campaign source")
    sha_pin(result.get("protocol_sha256"), "V21 campaign protocol")
    if result["mode"] == "--render-contract":
        need("contract_sha256" not in result,
             "rendering cannot pin the not-yet-published contract")
    else:
        sha_pin(result.get("contract_sha256"), "V21 campaign contract")
    if result["mode"] in ("--self-test", "--verify-frozen-context",
                           "--render-contract"):
        need(set(result) <= {"mode", "source_sha256", "protocol_sha256",
                             "contract_sha256"},
             "source verification cannot authorize a process or candidate")
    return result


def actual_failure(parent: types.ModuleType | None,
                   options: dict | None, error: BaseException) -> dict:
    result = {"schema": SCHEMA + "-entry-failure", "status": "FAIL",
              "version": VERSION, "error_type": type(error).__name__,
              "error_message": str(error)[:8192],
              "candidate_qualified": False, "candidate_correctness":
                  "NOT MEASURED", "performance": "NOT MEASURED",
              "holdout": "NOT OPENED", "winner_selected": False}
    candidate = sys.modules.get("re")
    if (type(options) is dict and options.get("mode") == "--worker"
            and type(candidate) is types.ModuleType
            and candidate is sys.modules.get("candidates.rust_candidate")
            and "_sre" not in sys.modules):
        result.update({"schema": SCHEMA + "-actual-original-suite-worker-failure",
                       "failure_class": "INFRASTRUCTURE FAILURE",
                       "suite": options.get("suite"),
                       "actual_candidate_workers": 1,
                       "actual_candidate_imports": 1,
                       "actual_native_libraries_loaded": 2,
                       "runtime_guard_installed_before_candidate_import": True,
                       "semantic_mismatch_count": "NOT MEASURED"})
    else:
        result.update({"actual_candidate_imports": 0,
                       "actual_candidate_workers_started": 0,
                       "actual_native_libraries_loaded": 0,
                       "actual_private_build_root_opens": 0,
                       "actual_build_archive_opens": 0,
                       "actual_hidden_cases_read": 0,
                       "actual_clock_samples": 0})
    return result


def actual_operation(options: dict, context: dict, state: dict) -> dict:
    parent = state["parent"]
    result = parent.actual_operation(options, context, state)
    if options["mode"] == "--worker":
        need(result.get("runtime_guard_installed_before_candidate_import")
             is True and result.get("actual_candidate_workers") == 1,
             "require genuine V3 guard installation before original matching")
        result["operational_guard_v3_source_sha256"] = V3[0][1]
        result["operational_guard_v3_protocol_sha256"] = V3[1][1]
        result["operational_guard_v3_contract_sha256"] = V3[2][1]
        result["runtime_guard_source_sha256"] = state["base"].GUARD[0][1]
        return result
    if options["mode"] == "--recover":
        return result
    need(options["mode"] == "--run"
         and result.get("suite_count") == WORKER_COUNT
         and result.get("case_execution_denominator") == CASE_COUNT
         and result.get("all_four_original_targets_restored") is True
         and result.get("actual_v22_build_receipt_sha256")
         == V22_PUBLICATION[1]
         and result.get("actual_v22_root_receipt_sha256")
         == V22_ROOT_RECEIPT[1],
         "retain the authentic complete V22 first-party correctness campaign")
    result["operational_guard_v3_source_sha256"] = V3[0][1]
    result["operational_guard_v3_protocol_sha256"] = V3[1][1]
    result["operational_guard_v3_contract_sha256"] = V3[2][1]
    result["previous_v20_failure_receipt_sha256"] = V20_FAILURE[1]
    return result


def main(arguments: list[str] | None = None) -> int:
    options: dict | None = None
    state: dict | None = None
    wall: PhysicalSourceWall | None = None
    try:
        verify_runtime()
        options = parse_options(list(sys.argv[1:] if arguments is None
                                     else arguments))
        if options["mode"] in ("--self-test", "--verify-frozen-context",
                               "--render-contract"):
            wall = PhysicalSourceWall()
            wall.install()
        context, state = verify_context(options, wall)
        if options["mode"] == "--render-contract":
            result = contract_document(context)
        elif options["mode"] == "--verify-frozen-context":
            result = context
        elif options["mode"] == "--self-test":
            need(wall is not None, "physically install the source wall first")
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
             "bound the complete canonical source or genuine actual evidence")
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED") else 1
    except BaseException as error:
        if state is not None:
            try:
                sys.stdout.buffer.write(state["guard"].canonical(
                    actual_failure(state.get("parent"), options, error)))
                sys.stdout.buffer.flush()
            except BaseException:
                pass
        else:
            try:
                sys.stderr.write("V21 campaign rejected: "
                                 + type(error).__name__ + ": "
                                 + str(error)[:8192] + "\n")
            except BaseException:
                pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
