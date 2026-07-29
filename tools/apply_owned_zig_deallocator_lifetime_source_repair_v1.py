#!/usr/bin/env python3
"""Freeze one first-party Zig finalizer source change without running a matcher."""

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
SELF = "tools/apply_owned_zig_deallocator_lifetime_source_repair_v1.py"
PROTOCOL = "oracle/phase2/ZIG-DEALLOCATOR-LIFETIME-SOURCE-REPAIR-V1.md"
CONTRACT = "oracle/phase2/zig-deallocator-lifetime-source-repair-v1.json"
SCHEMA = "rebar-owned-zig-deallocator-lifetime-source-repair-v1"
FAMILY = "zig"
LABEL = "phase2-v13-zig-guard-clean-lifetime-v1-source-repair"
BUILD_LABEL = "phase2-v13-zig-scanner-phrase-v4"
DEVICE = 2064
PRIVATE_DEVICE = 2049
MAX_BYTES = 8 * 1024 * 1024
IMMUTABLE_PRODUCER_JSON_BYTES = 4 * 1024 * 1024
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
CPYTHON_LIFETIME_PRECEDENT = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu"
    "/lib/python3.14/concurrent/interpreters/__init__.py:152"
)

GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
    31364044,
)
P0 = (
    ("oracle/phase1/P0-COMPLETENESS-V4.md",
     "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
     4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("oracle/phase1/p0-completeness-v1.json",
     "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
     45632, 524385),
    ("oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
     "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
     3929, 525081),
    ("oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("oracle/phase1/evidence/differential-fuzz-reference-v3-"
     "cpython-3146-two-worker-8244-v3/two-independent-reference-result.json",
     "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
     3658, 524707),
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
ACTUAL_PASSING_SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
ACTUAL_SEMANTIC_FAILURES = (
    ("scanner_verbose_v1", 620),
    ("public_types_v1", 248),
    ("substitution_v2", 64),
    ("shape_v2", 672),
    ("public_surface_v19", 96),
)
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version", "build_zig_engine",
    "build_zig_bridge", "engine_dynamic", "engine_symbols",
    "engine_sections", "engine_notes", "bridge_dynamic", "bridge_symbols",
    "bridge_sections", "bridge_notes",
)
PRODUCER = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py",
     "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
     102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
     "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
     5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json",
     "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
     21036, 524885),
)
GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py",
     "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
     67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
     "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
     4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json",
     "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
     7671, 524887),
)
EXPANDED_HOLDOUT_PROPOSAL = (
    ("tools/verify_expanded_sealed_holdout_v1.py",
     "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
     27311, 428806),
    ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
     "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
     13237, 524760),
    ("oracle/phase3/expanded-sealed-holdout-v1.json",
     "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
     6628, 524761),
)
HISTORICAL_HOLDOUT_PROPOSAL = (
    "docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md",
    "f7509c60065860d30aad7939dda76f53e1c9f6ebb9db5e1298d0881f63a016eb",
    9481, 431040,
)
V13 = (
    ("tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py",
     "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e",
     123672, 431366),
    ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md",
     "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40",
     8765, 524873),
    ("oracle/phase2/zig-scanner-phrase-source-build-v13.json",
     "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15",
     21331, 524874),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-"
     "phase2-v13-zig-scanner-phrase-v4-build-receipt.json",
     "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d",
     170856, 525149),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-"
     "phase2-v13-zig-scanner-phrase-v4-private-root-receipt.json",
     "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2",
     74891, 525148),
)
PREDECESSOR_V12 = (
    ("tools/run_owned_repaired_zig_original_campaign_v12.py",
     "329c8ac8c50b3f61fc176e07267f9771a3878167e9ab5eb9246e06cafac31cf8",
     251811, 430069),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V12.md",
     "10bf90c29b0f23759acb3ea30ae9b364f90a9937d9b41388095b839e5ff5f551",
     5361, 524830),
    ("oracle/phase2/repaired-zig-original-campaign-v12.json",
     "97a04675f4f8afc4a44061979a0a856bff2f5bb8cb9ed1381e6ee52168156b07",
     46081, 524831),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v12-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v12-"
     "failures-publication-receipt.json",
     "ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9",
     77604, 524975),
)
PARENT_ADAPTER = (
    "candidates/zig/variants/scanner_phrase_v4/zig_candidate.py",
    "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b",
    68530, 428966,
)
CLEAN_ADAPTER = (
    "candidates/zig/variants/scanner_phrase_guard_clean_v1/zig_candidate.py",
    "e8a023a388d94369d3eab38260390e853cd8c38394713aef49856875cfd4ac11",
    67262, 429081,
)
LIFETIME_ADAPTER = (
    "candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/"
    "zig_candidate.py",
    "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50",
    67294, 525010,
)
ENGINE_SOURCE = (
    "candidates/zig/mini_regex.zig",
    "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28",
    186915, 429377,
)
BRIDGE_SOURCE = (
    "candidates/zig/py_bridge.c",
    "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b",
    173026, 429075,
)
NATIVE = {
    "engine": (
        "caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071",
        108888,
    ),
    "bridge": (
        "3dfd80e26773d83acfc83cba7f0df1b85a796ed0059aaa6d855ec0a3b5a93121",
        133656,
    ),
}
ORIGINAL_DEALLOCATOR = (
    "    def __del__(self):\n"
    "        handle = getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            _zig_bridge.free(handle)\n"
    "            self._handle = None\n"
)
REPAIRED_DEALLOCATOR = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            self._handle = None\n"
    "            _free(handle)\n"
)
EXPECTED_PATTERN_SLOTS = (
    "pattern", "flags", "groups", "_groupindex", "_handle",
    "_literal", "_templates", "__weakref__",
)
ZERO_KEYS = (
    "actual_candidate_imports", "actual_candidate_workers",
    "actual_reference_workers", "native_libraries_loaded",
    "native_activations", "private_roots_opened", "private_snapshots_opened",
    "matching_archives_opened", "matching_archives_inflated",
    "benchmark_files_opened", "holdout_files_opened", "clock_samples",
    "timing_trials_run", "compiler_processes_started",
    "candidate_processes_started", "network_requests", "files_written",
    "recovery_roots_created", "recovery_journals_created",
    "canonical_targets_modified",
)


class CampaignError(Exception):
    """A pinned source, lifetime proof, or historical fact was not exact."""


class SyntheticReleaseError(Exception):
    """A genuine synthetic release error that must never be suppressed."""

def require(condition, message):
    if not condition:
        raise CampaignError(message)

def pin(value, label):
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "reject incomplete " + label + " SHA-256")
    return value

def digest(data):
    require(type(data) is bytes, "hash only actual complete bytes")
    return hashlib.sha256(data).hexdigest()

REAL_OPEN = os.open
ACTIVE_WALL = None


def owners(*, active=False):
    require(active is False, "source repair has no active matching mode")
    return (
        GOAL, *P0, *PRODUCER, *GUARD, *EXPANDED_HOLDOUT_PROPOSAL,
        HISTORICAL_HOLDOUT_PROPOSAL, *V13, *PREDECESSOR_V12,
        PARENT_ADAPTER, CLEAN_ADAPTER, LIFETIME_ADAPTER,
        ENGINE_SOURCE, BRIDGE_SOURCE,
    )

def record(item):
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "device": DEVICE, "inode": item[3], "mode": "0600",
            "nlink": 1}


REAL_OPEN = os.open
ACTIVE_WALL = None

def relative(path):
    require(type(path) is str and bool(path) and not path.startswith("/")
            and "\\" not in path and "\x00" not in path
            and all(p not in ("", ".", "..") for p in path.split("/")),
            "reject a noncanonical first-party source path")
    return path

def read_owner(item):
    require(type(item) is tuple and len(item) == 4
            and relative(item[0]) == item[0]
            and pin(item[1], item[0])
            and type(item[2]) is int and 0 < item[2] <= MAX_BYTES
            and type(item[3]) is int and item[3] > 0,
            "reject an incomplete independently frozen source owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(ROOT + "/" + item[0], flags)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode)
                and before.st_dev == DEVICE and before.st_ino == item[3]
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_size == item[2],
                "reject a substituted first-party owner: " + item[0])
        parts, left = [], before.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject a truncated owner: " + item[0])
            parts.append(data)
            left -= len(data)
        require(not os.read(fd, 1), "reject an extended owner: " + item[0])
        data = b"".join(parts)
        after = os.fstat(fd)
        require(digest(data) == item[1]
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject bytes changed during first-party verification")
        return data
    finally:
        os.close(fd)

def read_suite(path, expected):
    relative(path)
    pin(expected, path)
    if ACTIVE_WALL is not None:
        ACTIVE_WALL.allowed.add(ROOT + "/" + path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(ROOT + "/" + path, flags)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600
                and 0 < before.st_size <= MAX_BYTES,
                "reject an unfrozen original-suite source")
        parts, left = [], before.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject a truncated original-suite source")
            parts.append(data)
            left -= len(data)
        require(not os.read(fd, 1) and digest(b"".join(parts)) == expected,
                "reject an altered immutable original-suite source: " + path)
    finally:
        os.close(fd)

def load(item, name):
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + item[0]
    exec(compile(read_owner(item), module.__file__, "exec",
                 dont_inherit=True), module.__dict__)
    require(module.__name__ == name, "reject a replaced first-party module")
    return module

def clean():
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and "re" not in sys.modules and "_sre" not in sys.modules
            and not any(n == "candidates" or n.startswith("candidates.")
                        for n in sys.modules),
            "require clean, isolated pinned Python before candidate import")

def normalize(raw):
    require(len(raw) == PARENT_ADAPTER[2]
            and digest(raw) == PARENT_ADAPTER[1],
            "reject a changed actual V13 scanner adapter")
    text = raw.decode("utf-8")
    tree = ast.parse(text, filename=ROOT + "/" + PARENT_ADAPTER[0])
    imports = [n for n in tree.body
               if isinstance(n, ast.Import) and len(n.names) == 1
               and n.names[0].name == "ctypes"
               and n.names[0].asname is None]
    classes = [n for n in tree.body
               if isinstance(n, ast.ClassDef) and n.name == "_Native"]
    require(len(imports) == len(classes) == 1,
            "require the unique unused first-party loader")
    methods = [n for n in classes[0].body
               if isinstance(n, ast.FunctionDef) and n.name == "__init__"]
    compile_methods = [n for n in classes[0].body
                       if isinstance(n, ast.FunctionDef) and n.name == "compile"]
    require(len(methods) == len(compile_methods) == 1
            and len(methods[0].body) == 20,
            "reject a changed or incomplete first-party loader")
    all_ctypes = [n for n in ast.walk(tree)
                  if isinstance(n, ast.Name) and n.id == "ctypes"]
    local_ctypes = [n for n in ast.walk(methods[0])
                    if isinstance(n, ast.Name) and n.id == "ctypes"]
    require(bool(local_ctypes) and len(all_ctypes) == len(local_ctypes),
            "reject ctypes used in any actual compiler or matcher")
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line.encode("utf-8")))
    edits = ((offsets[imports[0].lineno - 1],
              offsets[imports[0].end_lineno], b""),
             (offsets[methods[0].body[0].lineno - 1],
              offsets[methods[0].body[-1].end_lineno], b"        pass\n"))
    normalized = raw
    for start, end, replacement in sorted(edits, reverse=True):
        require(0 <= start < end <= len(normalized),
                "reject a changed exact AST source span")
        normalized = normalized[:start] + replacement + normalized[end:]
    actual = ast.parse(normalized.decode("utf-8"))
    tree.body.remove(imports[0])
    methods[0].body = [ast.Pass()]
    bridge_calls = [n for n in ast.walk(actual)
                    if isinstance(n, ast.Attribute)
                    and isinstance(n.value, ast.Name)
                    and n.value.id == "_zig_bridge" and n.attr == "compile"]
    scanners = [n for n in actual.body
                if isinstance(n, ast.ClassDef) and n.name == "Scanner"]
    require(len(normalized) == CLEAN_ADAPTER[2]
            and digest(normalized) == CLEAN_ADAPTER[1]
            and ast.dump(tree, include_attributes=False)
            == ast.dump(actual, include_attributes=False)
            and not any(isinstance(n, ast.Name) and n.id == "ctypes"
                        for n in ast.walk(actual))
            and bool(bridge_calls) and len(scanners) == 1,
            "reject any changed Zig parser, compiler, matcher, or scanner")
    return normalized

class SourceWall:
    def __init__(self):
        self.allowed = {ROOT + "/" + item[0] for item in owners()}
        self.allowed |= {ROOT + "/" + SELF, ROOT + "/" + PROTOCOL,
                         ROOT + "/" + CONTRACT}
        self.saved = {}
        self.active = False
        self.denials = 0

    def deny(self, why):
        self.denials += 1
        raise CampaignError("source-only wall rejected " + why)

    def imported(self, name, globals=None, locals=None, fromlist=(), level=0):
        blocked = {"re", "_sre", "regex", "re2", "ctypes", "subprocess",
                   "socket", "threading", "multiprocessing", "gzip",
                   "json", "pathlib", "tempfile", "time", "unittest"}
        if type(name) is not str or name.split(".", 1)[0] in blocked \
                or name == "candidates" or name.startswith("candidates."):
            self.deny("matching, native-loader, process, or timing import")
        return self.saved["import"](name, globals, locals, fromlist, level)

    def opened(self, path, flags, mode=0o777, *, dir_fd=None):
        if dir_fd is not None or type(path) is not str \
                or path not in self.allowed \
                or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            self.deny("private, native, archive, holdout, or write open")
        return self.saved["open"](path, flags, mode)

    def blocked(self, *args, **kwargs):
        self.deny("mutation, process, native load, or network")

    def audit(self, event, args):
        if not self.active:
            return
        if event == "open":
            path = args[0] if args else None
            if type(path) is str and path not in self.allowed:
                self.deny("unlisted physical file: " + path)
        elif event.startswith(("ctypes.", "subprocess.", "socket.",
                               "os.exec", "os.spawn")) \
                or event in {"os.system", "os.fork", "os.posix_spawn"}:
            self.deny("physical dynamic loader, subprocess, or network")

    def __enter__(self):
        global ACTIVE_WALL
        require(ACTIVE_WALL is None, "reject a reused source-only wall")
        self.saved["import"] = builtins.__import__
        self.saved["builtin_open"] = builtins.open
        self.saved["open"] = os.open
        builtins.__import__ = self.imported
        builtins.open = self.blocked
        os.open = self.opened
        for name in ("system", "popen", "fork", "mkdir", "makedirs",
                     "rename", "replace", "unlink", "remove", "rmdir",
                     "link", "symlink", "chdir", "putenv", "unsetenv",
                     "posix_spawn", "posix_spawnp"):
            if hasattr(os, name):
                self.saved["os." + name] = getattr(os, name)
                setattr(os, name, self.blocked)
        ACTIVE_WALL = self
        self.active = True
        sys.addaudithook(self.audit)
        return self

    def __exit__(self, kind, value, trace):
        global ACTIVE_WALL
        self.active = False
        ACTIVE_WALL = None
        builtins.__import__ = self.saved["import"]
        builtins.open = self.saved["builtin_open"]
        os.open = self.saved["open"]
        for key, previous in self.saved.items():
            if key.startswith("os."):
                setattr(os, key[3:], previous)
        return False

def validate_build(producer):
    receipt = producer.JsonReader(read_owner(V13[3])).parse()
    root = producer.JsonReader(read_owner(V13[4])).parse()
    require(type(receipt) is dict
            and receipt.get("schema")
            == "rebar-owned-zig-scanner-phrase-source-build-v13-plaintext-build-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("family") == FAMILY
            and receipt.get("source_sha256") == V13[0][1]
            and receipt.get("protocol_sha256") == V13[1][1]
            and receipt.get("contract_sha256") == V13[2][1]
            and receipt.get("candidate_correctness") == "NOT MEASURED",
            "reject a fabricated V13 first-party source build")
    linked = receipt.get("private_root_receipt", {})
    require(type(linked) is dict and linked.get("path") == V13[4][0]
            and linked.get("sha256") == V13[4][1]
            and linked.get("bytes") == V13[4][2]
            and linked.get("device") == DEVICE
            and linked.get("inode") == V13[4][3]
            and linked.get("mode") == "0600"
            and root.get("schema")
            == "rebar-owned-zig-scanner-phrase-source-build-v13-private-root-receipt"
            and root.get("status") == "PASS"
            and root.get("label") == BUILD_LABEL
            and root.get("actual_process_count") == 26
            and root.get("phase_names") == ["reference-a", "reference-b"]
            and root.get("candidate_correctness") == "NOT MEASURED",
            "reject a substituted durable private-root receipt")
    actual = receipt.get("complete_actual_build", {})
    require(type(actual) is dict and actual.get("status") == "PASS"
            and actual.get("actual_process_count") == 26
            and actual.get("actual_source_snapshot_count") == 6
            and actual.get("corrected_adapter_sha256") == PARENT_ADAPTER[1]
            and actual.get("first_party_engine_source_sha256") == ENGINE_SOURCE[1]
            and actual.get("first_party_bridge_source_sha256") == BRIDGE_SOURCE[1]
            and actual.get("original_case_execution_denominator") == 31237
            and actual.get("original_suite_count") == 13
            and actual.get("original_named_private_waiver_count") == 13
            and actual.get("supplemental_reference_case_count") == 8244
            and actual.get("cross_family_engine_count") == 0
            and actual.get("external_regex_dependency_count") == 0
            and actual.get("stdlib_regex_engine_count") == 0
            and actual.get("candidate_matching") == "NOT RUN"
            and actual.get("candidate_qualified") is False
            and actual.get("candidate_workers_started") == 0
            and actual.get("holdout_files_opened") == 0
            and actual.get("benchmark_files_opened") == 0
            and actual.get("native_activations") == 0,
            "reject V13 matching claims, hidden access, or external engines")
    processes = actual.get("processes")
    require(type(processes) is list and len(processes) == 26
            and all(type(row.get("pid")) is int and row["pid"] > 0
                    and row.get("returncode") == 0 for row in processes)
            and len({row["pid"] for row in processes}) == 26
            and tuple((row.get("phase"), row.get("role")) for row in processes)
            == tuple((phase, role)
                     for phase in ("reference-a", "reference-b")
                     for role in PROCESS_ROLES),
            "require all 26 genuine distinct first-party build processes")
    phases, roots = actual.get("build_phases"), root.get("phases")
    require(type(phases) is list and type(roots) is list
            and len(phases) == len(roots) == 2
            and [x.get("name") for x in phases]
            == [x.get("name") for x in roots]
            == ["reference-a", "reference-b"],
            "reject missing independent V13 native build phases")
    source_ids, native_ids = set(), {"engine": set(), "bridge": set()}
    expected_sources = {
        "candidates/zig/mini_regex.zig": ENGINE_SOURCE,
        "candidates/zig/py_bridge.c": BRIDGE_SOURCE,
        "candidates/zig_candidate.py": PARENT_ADAPTER,
    }
    for phase, rooted in zip(phases, roots, strict=True):
        sources, root_sources = phase.get("source_snapshots"), rooted.get("source_snapshots")
        require(type(sources) is dict and type(root_sources) is dict
                and set(sources) == set(root_sources) == set(expected_sources),
                "reject an omitted genuine V13 source snapshot")
        for path, expected in expected_sources.items():
            owner = sources[path]
            require(owner == root_sources[path]
                    and owner.get("sha256") == expected[1]
                    and owner.get("bytes") == expected[2]
                    and owner.get("device") == PRIVATE_DEVICE
                    and owner.get("mode") == "0600"
                    and owner.get("uid") == os.geteuid()
                    and owner.get("nlink") == 1,
                    "reject crossed or fabricated V13 first-party source bytes")
            identity = (owner["device"], owner["inode"])
            require(identity not in source_ids, "reject shared V13 source inodes")
            source_ids.add(identity)
        for role, (expected_hash, expected_size) in NATIVE.items():
            output = phase.get("native_outputs", {}).get(role, {})
            rooted_output = rooted.get("native_outputs", {}).get(role, {})
            owner, audit = output.get("owner"), output.get("independence_audit")
            require(type(owner) is dict and owner == rooted_output.get("owner")
                    and owner.get("sha256") == expected_hash
                    and owner.get("bytes") == expected_size
                    and owner.get("device") == PRIVATE_DEVICE
                    and owner.get("mode") == "0700"
                    and owner.get("uid") == os.geteuid()
                    and owner.get("nlink") == 1
                    and type(audit) is dict and audit.get("role") == role
                    and audit.get("cross_family_engine_count") == 0
                    and audit.get("external_regex_dependency_count") == 0
                    and audit.get("stdlib_regex_engine_count") == 0
                    and audit.get("native_loader_dependency_count") == 0,
                    "reject a wrapped, borrowed, or substituted V13 native engine")
            ident = (owner["device"], owner["inode"])
            require(ident not in native_ids[role],
                    "reject a reused independent V13 native phase")
            native_ids[role].add(ident)
            if role == "bridge":
                require(audit.get("needed") == ["_zig_probe.so", "libc.so.6"]
                        and audit.get("runpath") == "$ORIGIN",
                        "reject a bridge not linked to its own adjacent engine")
    repro = actual.get("reproducibility", {})
    require(len(source_ids) == 6 and repro.get("status") == "PASS"
            and repro.get("independent_phase_count") == 2
            and repro.get("compiler_process_count") == 26
            and repro.get("unique_compiler_process_count") == 26
            and repro.get("source_snapshot_count") == 6
            and all(repro.get("native_roles", {}).get(role, {}).get("byte_identical")
                    is True and repro["native_roles"][role].get("sha256") == spec[0]
                    and repro["native_roles"][role].get("bytes") == spec[1]
                    and repro["native_roles"][role].get("distinct_phase_owner_count") == 2
                    for role, spec in NATIVE.items()),
            "require two fully reproducible, complete first-party Zig phases")
    return receipt, root

def pattern_node(tree, label):
    scanners = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Scanner"
    ]
    require(
        len(scanners) == 1,
        "require the exact complete " + label + " first-party scanner",
    )
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Pattern"
    ]
    require(len(classes) == 1, "require one complete " + label + " Pattern")
    methods = [
        node for node in classes[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "__del__"
    ]
    every = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "__del__"
    ]
    require(
        len(methods) == len(every) == 1 and every[0] is methods[0],
        "reject a missing, extra, nested, or foreign " + label + " destructor",
    )
    slot_rows = [
        node for node in classes[0].body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "__slots__"
    ]
    require(
        len(slot_rows) == 1
        and ast.literal_eval(slot_rows[0].value) == EXPECTED_PATTERN_SLOTS,
        "reject changed Pattern instance storage",
    )
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            require(len(node.names) == 1, "reject combined candidate imports")
            imports.append(("import", node.names[0].name, node.names[0].asname))
        elif isinstance(node, ast.ImportFrom):
            require(
                len(node.names) == 1,
                "reject widened first-party bridge imports",
            )
            imports.append((
                "from", node.module, node.level,
                node.names[0].name, node.names[0].asname,
            ))
    require(
        tuple(imports) == (
            ("import", "enum", None),
            ("import", "os", None),
            ("import", "types", None),
            ("import", "unicodedata", None),
            ("import", "warnings", None),
            ("from", "candidates", 0, "_zig_bridge", None),
        ),
        "reject an external, standard-library, or cross-candidate matcher",
    )
    return classes[0], methods[0]


def deallocator_shape(raw, *, repaired):
    require(type(raw) is bytes, "require complete source bytes")
    source = raw.decode("utf-8", "strict")
    tree = ast.parse(source, filename=(
        LIFETIME_ADAPTER[0] if repaired else CLEAN_ADAPTER[0]
    ))
    pattern, method = pattern_node(
        tree, "repaired" if repaired else "original",
    )
    exact = REPAIRED_DEALLOCATOR if repaired else ORIGINAL_DEALLOCATOR
    require(source.count(exact) == 1, "reject an inexact unique destructor")
    snippet = ast.parse("class Pattern:\n" + exact).body[0].body[0]
    require(
        ast.dump(method, include_attributes=False)
        == ast.dump(snippet, include_attributes=False),
        "reject changed defaults, release ordering, or suppressed cleanup",
    )
    if repaired:
        args = method.args
        require(
            [node.arg for node in args.args] == [
                "self", "_free", "_getattr",
            ]
            and not args.posonlyargs and not args.kwonlyargs
            and args.vararg is None and args.kwarg is None
            and len(args.defaults) == 2
            and isinstance(args.defaults[0], ast.Attribute)
            and isinstance(args.defaults[0].value, ast.Name)
            and args.defaults[0].value.id == "_zig_bridge"
            and args.defaults[0].attr == "free"
            and isinstance(args.defaults[1], ast.Name)
            and args.defaults[1].id == "getattr"
            and not any(
                isinstance(node, (ast.Try, ast.TryStar, ast.ExceptHandler))
                for node in ast.walk(method)
            ),
            "reject an uncached first-party release or swallowed failure",
        )
    return tree, pattern, method


def prove_lifetime_adapter(clean_raw, repaired_raw):
    require(
        len(clean_raw) == CLEAN_ADAPTER[2]
        and digest(clean_raw) == CLEAN_ADAPTER[1],
        "reject the authentic complete clean scanner adapter",
    )
    require(
        len(repaired_raw) == LIFETIME_ADAPTER[2]
        and digest(repaired_raw) == LIFETIME_ADAPTER[1],
        "reject the authentic complete lifetime scanner adapter",
    )
    old = ORIGINAL_DEALLOCATOR.encode("utf-8")
    new = REPAIRED_DEALLOCATOR.encode("utf-8")
    require(
        clean_raw.count(old) == 1
        and clean_raw.count(b"    def __del__(") == 1
        and repaired_raw.count(new) == 1
        and repaired_raw.count(b"    def __del__(") == 1
        and clean_raw.replace(old, new, 1) == repaired_raw,
        "reject anything beyond the one exact finalizer source edit",
    )
    old_tree, old_pattern, old_method = deallocator_shape(
        clean_raw, repaired=False,
    )
    repaired_tree, _, repaired_method = deallocator_shape(
        repaired_raw, repaired=True,
    )
    index = next(
        i for i, node in enumerate(old_pattern.body)
        if node is old_method
    )
    old_pattern.body[index] = repaired_method
    require(
        ast.dump(old_tree, include_attributes=False)
        == ast.dump(repaired_tree, include_attributes=False),
        "reject any changed matcher, parser, engine, scanner, or imports",
    )
    return {
        "original_destructor_count": 1,
        "repaired_destructor_count": 1,
        "repaired_class": "Pattern",
        "complete_other_ast_unchanged": True,
        "changed_ast_node_count": 1,
        "changed_source_block_count": 1,
        "instance_slots_changed": False,
        "matcher_parser_compiler_scanner_changed": False,
        "bridge_or_native_source_changed": False,
        "release_default": "_zig_bridge.free",
        "attribute_lookup_default": "getattr",
        "release_handle_cleared_before_call": True,
        "release_error_suppressed": False,
        "half_initialized_instance_supported": True,
    }


def validate_publication(predecessor, receipt):
    require(
        type(predecessor) is dict and type(receipt) is dict
        and predecessor.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v12-"
           "guard-clean-source-freeze"
        and predecessor.get("version") == 12
        and predecessor.get("status")
        == "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN"
        and predecessor.get("family") == FAMILY
        and predecessor.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and predecessor.get("source") == record(PREDECESSOR_V12[0])
        and predecessor.get("protocol") == record(PREDECESSOR_V12[1])
        and predecessor.get("corrected_original_matching") == "NOT RUN"
        and predecessor.get("corrected_supplemental_matching") == "NOT RUN"
        and predecessor.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and predecessor.get("qualified_candidate_count") == 0
        and predecessor.get("current_qualified_candidates") == 0
        and predecessor.get("minimum_qualified_candidates") == 3
        and predecessor.get("holdout_case_count") == 14155776,
        "reject the complete pushed V12 first-party source freeze",
    )
    original = predecessor.get("original_oracle", {})
    first_party = predecessor.get("first_party_zig", {})
    require(
        original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("obligation_count") == 73
        and original.get("crosswalk_count") == 34
        and original.get("named_private_waiver_count") == 13
        and original.get("supplemental_case_count") == 8244
        and original.get("supplemental_candidate_matching") == "NOT RUN"
        and original.get("supplemental_cases_added_to_original_denominator")
        is False
        and tuple(
            (row.get("id"), row.get("case_execution_count"))
            for row in original.get("suites", [])
        ) == SUITES
        and first_party.get("guard_clean_scanner_adapter")
        == record(CLEAN_ADAPTER)
        and first_party.get("engine_source") == record(ENGINE_SOURCE)
        and first_party.get("bridge_source") == record(BRIDGE_SOURCE)
        and first_party.get("complete_matching_ast_unchanged") is True
        and first_party.get("v13_build_attests_guard_clean_adapter")
        is False,
        "reject inherited P0, first-party Zig, or prior build claims",
    )
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v12-"
           "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and receipt.get("source_sha256") == PREDECESSOR_V12[0][1]
        and receipt.get("protocol_sha256") == PREDECESSOR_V12[1][1]
        and receipt.get("contract_sha256") == PREDECESSOR_V12[2][1]
        and receipt.get("family") == FAMILY
        and receipt.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and receipt.get("all_original_suites_attempted") is True
        and receipt.get("case_execution_denominator") == 31237
        and receipt.get("suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("unique_candidate_worker_count") == 13
        and receipt.get("completed_suite_count") == 12
        and receipt.get("verified_passing_case_count") == 4607
        and receipt.get("observed_semantic_mismatch_lower_bound") == 1700
        and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
        and receipt.get("infrastructure_failure_count") == 1
        and receipt.get("infrastructure_failure_suites")
        == ["subinterpreter_v2"]
        and receipt.get("failed_suites")
        == [name for name, _ in ACTUAL_SEMANTIC_FAILURES]
           + ["subinterpreter_v2"]
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("original_campaign_passed") is False
        and receipt.get("all_three_original_targets_restored") is True
        and receipt.get("per_suite_timeout_seconds") == 120
        and receipt.get("maximum_serial_worker_timeout_seconds") == 1560
        and receipt.get("timeout_count") == 0
        and receipt.get("timed_out_suites") == []
        and receipt.get("supplemental_candidate_matching") == "NOT RUN"
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("undefined_behavior") == "NOT MEASURED"
        and receipt.get("winner_selected") is False,
        "reject or exaggerate the actual fully guarded V12 publication",
    )
    archive = receipt.get("archive", {})
    require(
        type(archive) is dict
        and archive.get("name")
        == "repaired-zig-original-campaign-v12-phase2-v13-zig-"
           "guard-clean-v1-original-p0-v12-failures.json.gz"
        and archive.get("sha256")
        == "ab8aa0f69cce19d62ffb75f8c56ca57fc22d2441cb3b14b8718f5cc7280de5e4"
        and archive.get("bytes") == 5618052
        and archive.get("device") == DEVICE
        and archive.get("inode") == 524970
        and archive.get("uid") == os.geteuid()
        and archive.get("mode") == 0o600
        and archive.get("nlink") == 1,
        "reject actual archive metadata or claim the archive was opened",
    )
    rows = receipt.get("original_suite_diagnostics")
    require(
        type(rows) is list and len(rows) == 13
        and tuple((row.get("suite"), row.get("case_execution_denominator"))
                  for row in rows) == SUITES
        and all(type(row.get("pid")) is int and row["pid"] > 0
                for row in rows)
        and len({row["pid"] for row in rows}) == 13
        and all(row.get("guard_installed_before_candidate_import") is True
                and row.get("candidate_imported") is True for row in rows),
        "require 13 genuine distinct guard-proven original V12 workers",
    )
    passing = tuple(
        (row["suite"], row["case_execution_denominator"])
        for row in rows
        if row.get("status") == "PASS"
        and row.get("infrastructure_failure") is False
        and row.get("observed_semantic_mismatch_count") == 0
    )
    measured = tuple(
        (row["suite"], row["observed_semantic_mismatch_count"])
        for row in rows
        if row.get("status") == "FAIL"
        and row.get("infrastructure_failure") is False
        and type(row.get("observed_semantic_mismatch_count")) is int
    )
    require(
        passing == ACTUAL_PASSING_SUITES
        and sum(count for _, count in passing) == 4607
        and measured == ACTUAL_SEMANTIC_FAILURES
        and sum(count for _, count in measured) == 1700,
        "preserve all seven genuine passes and all five measured losses",
    )
    warnings = []
    for row in rows:
        excerpt = row.get("stderr_literal_excerpt")
        require(
            type(excerpt) is dict
            and excerpt.get("status") == "CAPTURED"
            and type(excerpt.get("text")) is str
            and "Exception ignored while calling deallocator"
            in excerpt["text"]
            and "line 1086" in excerpt["text"]
            and "'NoneType' object has no attribute 'free'"
            in excerpt["text"],
            "preserve the exact actual V12 warning in every worker",
        )
        warnings.append(row["suite"])
    nested_rows = [
        row for row in rows if row.get("suite") == "subinterpreter_v2"
    ]
    require(
        len(nested_rows) == 1,
        "require the genuine separately preserved original child failure",
    )
    row = nested_rows[0]
    nested = row.get("complete_actual_suite_failure_details")
    original_failure = (
        nested.get("complete_original_failure_details")
        if type(nested) is dict else None
    )
    require(
        row.get("status") == "FAIL"
        and row.get("infrastructure_failure") is True
        and row.get("activation_stage")
        == "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
        and row.get("error_type") == "ActualSuiteFailure"
        and row.get("error_message")
        == "preserve the actual guarded original child lifecycle failure"
        and row.get("observed_semantic_mismatch_count") == "NOT MEASURED"
        and type(nested) is dict
        and nested.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-"
           "genuine-nested-failure"
        and nested.get("error_type") == "ActualSuiteFailure"
        and nested.get("error_message")
        == "retain every genuine failed private-interpreter call and cleanup"
        and nested.get("actual_child_guards_installed") == 1
        and nested.get("actual_candidate_subprocesses") == 0
        and nested.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and nested.get("expected_case_interpreter_exec_calls") == 394
        and nested.get("expected_interpreters_created") == 11
        and type(original_failure) is dict
        and original_failure.get("status") == "FAIL"
        and original_failure.get("active_phase")
        == "install-original-private-guard-A"
        and original_failure.get("actual_prepared_interpreter_ids") == []
        and original_failure.get("actual_case_interpreter_exec_calls") == 0
        and original_failure.get("actual_guard_cleanup_interpreter_exec_calls")
        == 0
        and original_failure.get("actual_initialization_interpreter_exec_calls")
        == 1
        and original_failure.get("actual_interpreters_created") == 2
        and original_failure.get("actual_interpreters_destroyed") == 2
        and original_failure.get("completed_a_records") == []
        and original_failure.get("completed_b_records") == []
        and original_failure.get("error_type") == "GuardError"
        and original_failure.get("error_message")
        == "runtime guard blocked unattested-child-bootstrap",
        "never count a generated child-guard field as installed or matching",
    )
    return {
        "passing_suites": passing,
        "semantic_failures": measured,
        "warning_suites": tuple(warnings),
        "subinterpreter": original_failure,
    }


def context(source_sha, protocol_sha):
    clean()
    for path, expected in (
        (SELF, pin(source_sha, "source")),
        (PROTOCOL, pin(protocol_sha, "protocol")),
    ):
        info = os.stat(ROOT + "/" + path, follow_symlinks=False)
        read_owner((path, expected, info.st_size, info.st_ino))
    for item in owners():
        read_owner(item)
    producer = load(
        PRODUCER[0], "_rebar_zig_lifetime_v1_immutable_v5_json",
    )
    require(
        producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and producer.CASE_DENOMINATOR == 31237
        and producer.SUITE_COUNT == 13
        and producer.PRIVATE_WAIVER_COUNT == 13
        and producer.ORIGINAL_OBLIGATION_COUNT == 73
        and producer.ORIGINAL_CROSSWALK_COUNT == 34
        and producer.SUPPLEMENTAL_CASE_COUNT == 8244
        and tuple(
            (row.name, row.case_count) for row in producer.SUITES
        ) == SUITES
        and sum(count for _, count in SUITES) == 31237,
        "reject an altered immutable V5 original correctness producer",
    )
    phase = producer.JsonReader(read_owner(P0[1])).parse()
    gate = phase.get("phase_gate", {})
    oracle = phase.get("original_oracle", {})
    require(
        phase.get("schema") == "rebar-cpython-re-p0-completeness-v4"
        and phase.get("version") == 4
        and phase.get("status") == "PASS"
        and phase.get("original_case_execution_denominator") == 31237
        and phase.get("original_suite_count") == 13
        and phase.get("original_named_private_waiver_count") == 13
        and phase.get("original_obligation_count") == 73
        and phase.get("original_crosswalk_count") == 34
        and gate.get("status") == "PASS"
        and gate.get("candidate_evaluation_authorized") is True
        and gate.get("final_holdout_authorized") is False
        and gate.get("performance_oracle_authorized") is False
        and tuple(
            (row.get("id"), row.get("case_execution_count"))
            for row in oracle.get("suites", [])
        ) == SUITES,
        "reject a weakened or renumbered complete frozen P0 matrix",
    )
    for suite in producer.SUITES:
        read_suite(suite.source_relative, suite.source_sha256)
    manifest = producer.JsonReader(read_owner(P0[2])).parse()
    require(
        type(manifest.get("suites")) is list
        and len(manifest["suites"]) == 13,
        "reject an incomplete original CPython baseline manifest",
    )
    fuzz = producer.JsonReader(read_owner(P0[5])).parse()
    workers = fuzz.get("workers", [])
    require(
        fuzz.get("status") == "PASS"
        and fuzz.get("actual_reference_worker_count") == 2
        and fuzz.get("supplemental_case_count") == 8244
        and len(workers) == 2
        and {row.get("pid") for row in workers} == {81, 82}
        and all(row.get("case_count") == 8244 for row in workers)
        and fuzz.get("holdout") == "NOT OPENED",
        "reject the separate frozen two-worker differential reference",
    )
    proposal = producer.JsonReader(
        read_owner(EXPANDED_HOLDOUT_PROPOSAL[2])
    ).parse()
    required = proposal.get("required_public_owners", [])
    historical = [
        row for row in required
        if type(row) is dict
        and row.get("path") == HISTORICAL_HOLDOUT_PROPOSAL[0]
    ]
    require(
        proposal.get("schema")
        == "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
        and proposal.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
        and proposal.get("final_protocol_status") == "NOT FROZEN"
        and proposal.get("generator_status") == "NOT FROZEN"
        and proposal.get("secret_status") == "NOT GENERATED"
        and proposal.get("case_status") == "NOT GENERATED; NOT OPENED"
        and proposal.get("timing_status") == "NOT RUN; NOT MEASURED"
        and proposal.get("memory_status") == "NOT RUN; NOT MEASURED"
        and proposal.get("runtime_independence_status") == "NOT ESTABLISHED"
        and proposal.get("winner_status") == "NOT SELECTED"
        and proposal.get("qualified_independent_family_count") == 0
        and proposal.get("minimum_qualified_independent_family_count") == 3
        and proposal.get("original_p0_case_count") == 31237
        and proposal.get("original_p0_suite_count") == 13
        and proposal.get("named_private_waiver_count") == 13
        and proposal.get("separate_differential_case_count") == 8244
        and proposal.get("pinned_python_version") == "3.14.6"
        and proposal.get("pinned_python_path") == PYTHON
        and proposal.get("pinned_python_sha256") == PINNED_PYTHON_SHA256
        and proposal.get("preserved_previous_proposal_case_count") == 4194304
        and proposal.get("case_count") == 14155776
        and proposal.get("timed_case_count") == 14155776
        and proposal.get("operation_count") == 36
        and proposal.get("pattern_family_count") == 24
        and proposal.get("subject_type_count") == 4
        and proposal.get("lifecycle_count") == 4
        and proposal.get("cases_per_stratum") == 1024
        and proposal.get("stratum_count") == 13824
        and 36 * 24 * 4 * 4 * 1024 == 14155776
        and proposal.get("candidate_participant_count") == 3
        and proposal.get("baseline_participant_count") == 1
        and proposal.get("participant_count") == 4
        and len(proposal.get("operations", [])) == 36
        and len(proposal.get("primary_pattern_families", [])) == 24
        and len(proposal.get("subject_types", [])) == 4
        and len(proposal.get("lifecycle_slots", [])) == 4
        and len(historical) == 1
        and historical[0].get("sha256")
        == HISTORICAL_HOLDOUT_PROPOSAL[1],
        "reject opening, weakening, or inventing the expanded holdout",
    )
    producer_contract = producer.JsonReader(
        read_owner(PRODUCER[2])
    ).parse()
    zig = [
        row for row in producer_contract.get("families", [])
        if row.get("name") == FAMILY
    ]
    require(
        producer_contract.get("version") == 5
        and producer_contract.get("original_obligation_count") == 73
        and producer_contract.get("original_crosswalk_count") == 34
        and producer_contract.get("supplemental_case_count") == 8244
        and len(zig) == 1
        and zig[0].get("owned_ctypes") is True,
        "reject a changed first-party six-family P0 contract",
    )
    guard = producer.JsonReader(read_owner(GUARD[2])).parse()
    require(
        guard.get("schema")
        == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and guard.get("version") == 2
        and guard.get("source") == record(GUARD[0])
        and guard.get("protocol") == record(GUARD[1])
        and guard.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and guard.get("qualified_candidate_count") == 0,
        "reject or weaken the strict original guard-before-import contract",
    )
    previous = producer.JsonReader(
        read_owner(PREDECESSOR_V12[2])
    ).parse()
    publication = producer.JsonReader(
        read_owner(PREDECESSOR_V12[3])
    ).parse()
    actual = validate_publication(previous, publication)
    build, build_root = validate_build(producer)
    clean_adapter = read_owner(CLEAN_ADAPTER)
    require(
        normalize(read_owner(PARENT_ADAPTER)) == clean_adapter,
        "reject the complete source-authenticated V13 clean scanner lineage",
    )
    repaired = read_owner(LIFETIME_ADAPTER)
    proof = prove_lifetime_adapter(clean_adapter, repaired)
    clean()
    return {
        "producer": producer,
        "phase": phase,
        "manifest": manifest,
        "fuzz": fuzz,
        "proposal": proposal,
        "producer_contract": producer_contract,
        "guard": guard,
        "predecessor": previous,
        "publication": publication,
        "actual": actual,
        "build": build,
        "build_root": build_root,
        "clean_adapter": clean_adapter,
        "repaired_adapter": repaired,
        "proof": proof,
    }

def contract_value(source_sha, protocol_sha, state):
    source_stat = os.stat(ROOT + "/" + SELF, follow_symlinks=False)
    protocol_stat = os.stat(ROOT + "/" + PROTOCOL, follow_symlinks=False)
    actual = state["actual"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 1,
        "status": (
            "SOURCE FROZEN; FIRST-PARTY LIFETIME VARIANT NOT BUILT OR RUN"
        ),
        "family": FAMILY,
        "label": LABEL,
        "source": record((
            SELF, source_sha, source_stat.st_size, source_stat.st_ino,
        )),
        "protocol": record((
            PROTOCOL, protocol_sha,
            protocol_stat.st_size, protocol_stat.st_ino,
        )),
        "goal": record(GOAL),
        "pinned_cpython": {
            "path": PYTHON,
            "version": "3.14.6",
            "sha256": PINNED_PYTHON_SHA256,
            "isolated": True,
            "bytecode_writes": False,
        },
        "cpython_lifetime_precedent": {
            "source_reference": CPYTHON_LIFETIME_PRECEDENT,
            "callable": "_interpreters.decref",
            "definition_time_default": "_interp_decref=_interpreters.decref",
            "documented_reason": (
                "Module globals may already be destroyed during finalization."
            ),
            "precedent_imported": False,
            "stdlib_regex_engine_imported": False,
        },
        "pushed_v12_predecessor": {
            "owners": [record(item) for item in PREDECESSOR_V12],
            "source_freeze_schema": state["predecessor"]["schema"],
            "source_freeze_version": 12,
            "actual_publication": {
                "owner": record(PREDECESSOR_V12[3]),
                "publication_status": "PASS",
                "publication_pass_means": "DURABLE PUBLICATION ONLY",
                "candidate_status": "FAIL",
                "candidate_qualified": False,
                "original_campaign_passed": False,
                "all_original_suites_attempted": True,
                "original_case_execution_denominator": 31237,
                "original_suite_count": 13,
                "actual_candidate_workers": 13,
                "unique_candidate_worker_count": 13,
                "all_parent_guard_and_candidate_markers_proven": True,
                "completed_suite_count": 12,
                "verified_passing_suite_count": 7,
                "verified_passing_case_count": 4607,
                "verified_passing_suites": [
                    {"suite": name, "cases": count}
                    for name, count in actual["passing_suites"]
                ],
                "completed_semantic_failure_count": 5,
                "genuine_completed_semantic_failures": [
                    {
                        "suite": name,
                        "observed_semantic_mismatch_count": count,
                        "infrastructure_failure": False,
                    }
                    for name, count in actual["semantic_failures"]
                ],
                "observed_semantic_mismatch_lower_bound": 1700,
                "semantic_mismatch_count": "NOT MEASURED",
                "infrastructure_failure_count": 1,
                "deallocator_warning": {
                    "observed_suite_count": 13,
                    "observed_in_all_seven_passing_suites": True,
                    "observed_suite_names": list(actual["warning_suites"]),
                    "literal_warning": (
                        "Exception ignored while calling deallocator"
                    ),
                    "original_source_line": 1086,
                    "literal_error": (
                        "'NoneType' object has no attribute 'free'"
                    ),
                    "warning_after_lifetime_repair": "NOT MEASURED",
                    "stderr_suppressed": False,
                    "archive_opened": False,
                },
                "separate_subinterpreter_infrastructure_failure": {
                    "suite": "subinterpreter_v2",
                    "activation_stage": (
                        "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
                    ),
                    "outer_error_type": "ActualSuiteFailure",
                    "nested_error_type": "ActualSuiteFailure",
                    "nested_error_message": (
                        "retain every genuine failed private-interpreter "
                        "call and cleanup"
                    ),
                    "published_wrapper_child_guard_count": 1,
                    "published_count_proves_actual_installation": False,
                    "original_active_phase": (
                        "install-original-private-guard-A"
                    ),
                    "actual_prepared_interpreter_ids": [],
                    "actual_case_interpreter_exec_calls": 0,
                    "actual_guard_cleanup_interpreter_exec_calls": 0,
                    "actual_initialization_interpreter_exec_calls": 1,
                    "actual_interpreters_created": 2,
                    "actual_interpreters_destroyed": 2,
                    "original_error_type": "GuardError",
                    "original_error_message": (
                        "runtime guard blocked unattested-child-bootstrap"
                    ),
                    "expected_interpreters_created": 11,
                    "expected_case_interpreter_exec_calls": 394,
                    "semantic_mismatch_count": "NOT MEASURED",
                    "lifetime_repair_fixes_child_bootstrap": (
                        "NOT ESTABLISHED"
                    ),
                    "guard_weakened": False,
                    "producer_modified": False,
                },
                "per_suite_timeout_seconds": 120,
                "maximum_serial_worker_timeout_seconds": 1560,
                "timeout_count": 0,
                "all_three_original_targets_restored": True,
                "matching_archive_opened": False,
            },
        },
        "original_oracle": {
            "owners": [record(item) for item in P0],
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "obligation_count": 73,
            "crosswalk_count": 34,
            "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_reference_worker_count": 2,
            "supplemental_candidate_matching": "NOT RUN",
            "supplemental_cases_added_to_original_denominator": False,
            "phase_one_gate_status": "PASS",
            "holdout_authorized": False,
            "performance_oracle_authorized": False,
        },
        "immutable_v5_producer": {
            "owners": [record(item) for item in PRODUCER],
            "maximum_json_bytes": IMMUTABLE_PRODUCER_JSON_BYTES,
            "candidate_or_engine_imported": False,
            "only_manual_canonical_json_parser_loaded": True,
            "producer_source_modified": False,
        },
        "immutable_v2_runtime_guard": {
            "owners": [record(item) for item in GUARD],
            "guard_weakened": False,
            "guard_source_modified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "actual_v13_first_party_source_build": {
            "owners": [record(item) for item in V13],
            "status": "PASS",
            "label": BUILD_LABEL,
            "actual_process_count": 26,
            "unique_process_count": 26,
            "independent_phase_count": 2,
            "first_party_source_snapshot_count": 6,
            "phase_source_snapshots_independent": True,
            "native_build_reproducible": True,
            "engine_source": record(ENGINE_SOURCE),
            "bridge_source": record(BRIDGE_SOURCE),
            "v13_original_scanner_adapter": record(PARENT_ADAPTER),
            "guard_clean_adapter_included_in_v13_native_build": False,
            "lifetime_adapter_included_in_v13_native_build": False,
            "native_engine": {
                "sha256": NATIVE["engine"][0],
                "bytes": NATIVE["engine"][1],
            },
            "native_bridge": {
                "sha256": NATIVE["bridge"][0],
                "bytes": NATIVE["bridge"][1],
            },
            "cross_family_engine_count": 0,
            "external_regex_dependency_count": 0,
            "stdlib_regex_engine_count": 0,
            "native_libraries_loaded_by_this_verifier": 0,
            "private_roots_opened_by_this_verifier": 0,
            "candidate_correctness": "NOT MEASURED",
        },
        "first_party_lifetime_repair": {
            "clean_input": record(CLEAN_ADAPTER),
            "additive_lifetime_variant": record(LIFETIME_ADAPTER),
            "original_destructor": ORIGINAL_DEALLOCATOR,
            "repaired_destructor": REPAIRED_DEALLOCATOR,
            "complete_byte_replacement_proven": True,
            **state["proof"],
            "definition_time_callable_retains_bridge_module": True,
            "reentrant_release_is_at_most_once": True,
            "release_error_propagates": True,
            "ordinary_scanner_failure_cleanup_changed": False,
            "external_regex_dependency_added": False,
            "stdlib_regex_fallback_added": False,
            "cross_candidate_engine_added": False,
            "adapter_imported": False,
            "native_bridge_loaded": False,
            "candidate_built": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
        },
        "expanded_sealed_holdout_proposal": {
            "owners": [
                record(item) for item in EXPANDED_HOLDOUT_PROPOSAL
            ],
            "historical_proposal": record(HISTORICAL_HOLDOUT_PROPOSAL),
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "case_count": 14155776,
            "historical_case_count": 4194304,
            "operation_count": 36,
            "pattern_family_count": 24,
            "subject_type_count": 4,
            "lifecycle_count": 4,
            "stratum_count": 13824,
            "cases_per_stratum": 1024,
            "candidate_participant_count": 3,
            "baseline_participant_count": 1,
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "holdout_case_status": "NOT GENERATED; NOT OPENED",
            "holdout_files_opened": 0,
            "benchmark_files_opened": 0,
            "timing_trials_run": 0,
            "proposal_verifier_executed": False,
        },
        "source_verifier": {
            "allowed_actions": [
                "--self-test",
                "--verify-frozen-context",
                "--render-contract",
            ],
            "candidate_execution_action_exists": False,
            "native_build_action_exists": False,
            "candidate_install_action_exists": False,
            "physical_source_wall_required": True,
            "complete_candidate_namespace_import_forbidden": True,
            "stdlib_regex_engine_import_forbidden": True,
            "native_dynamic_loading_forbidden": True,
            "candidate_processes_forbidden": True,
            "private_roots_forbidden": True,
            "matching_archives_forbidden": True,
            "holdout_cases_forbidden": True,
            "all_filesystem_writes_forbidden": True,
            "synthetic_destructor_controls_run_only_in_self_test": True,
        },
        "source_only_effects": {name: 0 for name in ZERO_KEYS},
        "corrected_original_matching": "NOT RUN",
        "corrected_supplemental_matching": "NOT RUN",
        "repaired_warning_status": "NOT MEASURED",
        "repaired_subinterpreter_status": "NOT MEASURED",
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


def verify(source_sha, protocol_sha, contract_sha):
    state = context(source_sha, protocol_sha)
    info = os.stat(ROOT + "/" + CONTRACT, follow_symlinks=False)
    item = (
        CONTRACT, pin(contract_sha, "contract"),
        info.st_size, info.st_ino,
    )
    raw = read_owner(item)
    actual = state["producer"].JsonReader(raw).parse()
    require(
        actual == contract_value(source_sha, protocol_sha, state)
        and state["producer"].canonical(actual) == raw,
        "reject altered or noncanonical complete lifetime source contract",
    )
    return state


def reject(operation, label):
    try:
        operation()
    except (
        CampaignError, OSError, ImportError, SyntaxError, ValueError,
        TypeError,
    ):
        return 1
    raise CampaignError("accepted hostile source control: " + label)


class SyntheticRelease:
    __slots__ = ("calls", "owner", "reenter", "failure")

    def __init__(self, *, reenter=False, failure=False):
        self.calls = []
        self.owner = None
        self.reenter = reenter
        self.failure = failure

    def __call__(self, handle):
        self.calls.append(handle)
        if self.reenter:
            self.reenter = False
            require(self.owner is not None, "missing synthetic owner")
            self.owner.__del__()
        if self.failure:
            raise SyntheticReleaseError("genuine synthetic release failure")


def synthetic_pattern(*, reenter=False, failure=False):
    release = SyntheticRelease(reenter=reenter, failure=failure)
    bridge = types.SimpleNamespace(free=release)
    namespace = {
        "__name__": "_rebar_zig_lifetime_v1_synthetic",
        "__builtins__": builtins.__dict__,
        "_zig_bridge": bridge,
        "getattr": builtins.getattr,
    }
    source = (
        "class SyntheticPattern:\n"
        "    __slots__ = ('_handle',)\n"
        + REPAIRED_DEALLOCATOR
    )
    synthetic_tree = ast.parse(source)
    synthetic_method = [
        node for node in synthetic_tree.body[0].body
        if isinstance(node, ast.FunctionDef)
        and node.name == "__del__"
    ]
    require(
        len(synthetic_method) == 1
        and ast.dump(
            synthetic_method[0], include_attributes=False,
        ) == ast.dump(
            ast.parse("class Pattern:\n" + REPAIRED_DEALLOCATOR)
            .body[0].body[0],
            include_attributes=False,
        ),
        "reject execution of an unauthenticated synthetic finalizer",
    )
    exec(
        compile(source, "<first-party-synthetic-lifetime-v1>", "exec",
                dont_inherit=True),
        namespace,
    )
    pattern = namespace["SyntheticPattern"]
    require(
        pattern.__del__.__defaults__ == (release, builtins.getattr)
        and pattern.__del__.__defaults__[0] is bridge.free
        and pattern.__del__.__defaults__[1] is builtins.getattr,
        "reject substituted definition-time lifetime defaults",
    )
    return pattern, release, namespace


def synthetic_lifetime_controls():
    checks = 0
    pattern, release, namespace = synthetic_pattern()
    target = pattern.__new__(pattern)
    target._handle = 71
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    target.__del__()
    require(
        release.calls == [71] and target._handle is None
        and pattern.__del__.__defaults__[0] is release
        and pattern.__del__.__defaults__[1] is builtins.getattr,
        "reject a first-party finalizer after module globals are destroyed",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [71] and target._handle is None,
        "reject double release after a successful finalizer",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    half = pattern.__new__(pattern)
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    half.__del__()
    half.__del__()
    require(
        release.calls == [] and not hasattr(half, "_handle"),
        "reject cleanup of a genuinely half-initialized pattern",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    for value in (None, 0, False):
        target = pattern.__new__(pattern)
        target._handle = value
        target.__del__()
    require(
        release.calls == [],
        "reject native cleanup for an absent or falsy handle",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern(reenter=True)
    target = pattern.__new__(pattern)
    target._handle = 103
    release.owner = target
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    target.__del__()
    release.owner = None
    require(
        release.calls == [103] and target._handle is None,
        "reject a reentrant double release",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern(failure=True)
    target = pattern.__new__(pattern)
    target._handle = 149
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    try:
        target.__del__()
    except SyntheticReleaseError as error:
        require(
            str(error) == "genuine synthetic release failure",
            "reject a changed genuine cleanup error",
        )
    else:
        raise CampaignError("suppressed a genuine native-release failure")
    require(
        release.calls == [149] and target._handle is None,
        "reject uncleared ownership when genuine release fails",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [149],
        "reject retry or double release after a genuine failure",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    original_callable = pattern.__del__.__defaults__[0]
    namespace["_zig_bridge"] = types.SimpleNamespace(
        free=lambda handle: (_ for _ in ()).throw(
            SyntheticReleaseError("poisoned module bridge"),
        ),
    )
    namespace["getattr"] = lambda *args: (_ for _ in ()).throw(
        SyntheticReleaseError("poisoned module getattr"),
    )
    target = pattern.__new__(pattern)
    target._handle = 211
    target.__del__()
    require(
        release.calls == [211]
        and pattern.__del__.__defaults__[0] is original_callable
        and target._handle is None,
        "reject a late rebound or poisoned finalizer module global",
    )
    checks += 1
    return checks


def altered_publication(receipt, *, field=None, value=None,
                        warning=False, child=False):
    changed = dict(receipt)
    if field is not None:
        changed[field] = value
    if warning or child:
        rows = list(receipt["original_suite_diagnostics"])
        index = 0 if warning else next(
            index for index, row in enumerate(rows)
            if row.get("suite") == "subinterpreter_v2"
        )
        row = dict(rows[index])
        if warning:
            excerpt = dict(row["stderr_literal_excerpt"])
            excerpt["text"] = "warning intentionally removed"
            row["stderr_literal_excerpt"] = excerpt
        else:
            nested = dict(row["complete_actual_suite_failure_details"])
            original = dict(nested["complete_original_failure_details"])
            original["actual_case_interpreter_exec_calls"] = 1
            nested["complete_original_failure_details"] = original
            row["complete_actual_suite_failure_details"] = nested
        rows[index] = row
        changed["original_suite_diagnostics"] = rows
    return changed


def hostile_source_controls(state, wall):
    checks = 0
    for name in (
        "re", "_sre", "regex", "re2", "ctypes", "subprocess", "socket",
        "threading", "multiprocessing", "gzip", "json", "pathlib",
        "tempfile", "time", "unittest", "candidates",
        "candidates.zig_candidate", "candidates.rust_candidate",
        "candidates._zig_bridge",
    ):
        checks += reject(
            lambda item=name: builtins.__import__(item),
            "forbidden source import " + name,
        )
    forbidden = (
        "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-yhzrep3u",
        "/tmp/rebar-phase2-repaired-zig-original-campaign-v12-"
        "phase2-v13-zig-guard-clean-v1-original-p0-v12",
        ROOT + "/candidates/_zig_probe.so",
        ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ROOT + "/candidates/zig_candidate.py",
        ROOT + "/candidates/rust_candidate.py",
        ROOT + "/oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v12-phase2-v13-zig-"
        "guard-clean-v1-original-p0-v12-failures.json.gz",
        ROOT + "/performance/final-holdout.json",
        ROOT + "/README.md",
    )
    for path in forbidden:
        checks += reject(
            lambda item=path: os.open(item, os.O_RDONLY),
            "forbidden physical owner " + path,
        )
    for operation, label in (
        (
            lambda: os.open(ROOT + "/" + SELF, os.O_WRONLY),
            "source mutation",
        ),
        (
            lambda: os.open(
                ROOT + "/" + LIFETIME_ADAPTER[0], os.O_RDWR,
            ),
            "candidate source mutation",
        ),
        (
            lambda: builtins.open(ROOT + "/" + CONTRACT, "w"),
            "built-in contract write",
        ),
        (
            lambda: os.mkdir("/tmp/rebar-zig-lifetime-v1-forbidden"),
            "temporary mutation",
        ),
        (
            lambda: sys.audit("ctypes.dlopen", "forbidden"),
            "physical native library load",
        ),
        (
            lambda: sys.audit(
                "ctypes.dlsym", None, "rebar_zig_compile",
            ),
            "physical native matcher lookup",
        ),
        (
            lambda: sys.audit(
                "subprocess.Popen", "zig", [], None, None,
            ),
            "compiler or candidate process",
        ),
        (
            lambda: sys.audit("socket.connect", None, None),
            "network access",
        ),
        (
            lambda: pin("x" * 63, "malformed"),
            "incomplete source digest",
        ),
        (
            lambda: relative("../holdout"),
            "escaped physical owner",
        ),
        (
            lambda: owners(active=True),
            "actual matching activation",
        ),
    ):
        checks += reject(operation, label)
    original = state["clean_adapter"]
    repaired = state["repaired_adapter"]
    mutations = (
        (
            REPAIRED_DEALLOCATOR.encode("utf-8"),
            REPAIRED_DEALLOCATOR.replace(
                "_free=_zig_bridge.free", "_free=getattr", 1,
            ).encode("utf-8"),
            "uncached or foreign release default",
        ),
        (
            REPAIRED_DEALLOCATOR.encode("utf-8"),
            REPAIRED_DEALLOCATOR.replace(
                "_getattr=getattr", "_getattr=None", 1,
            ).encode("utf-8"),
            "uncached attribute lookup",
        ),
        (
            b"            self._handle = None\n"
            b"            _free(handle)\n",
            b"            _free(handle)\n"
            b"            self._handle = None\n",
            "release before ownership is cleared",
        ),
        (
            b"            _free(handle)\n",
            b"            try:\n"
            b"                _free(handle)\n"
            b"            except Exception:\n"
            b"                pass\n",
            "suppressed genuine release failure",
        ),
        (
            b'__slots__ = ("pattern", "flags", "groups", "_groupindex", '
            b'"_handle",\n',
            b'__slots__ = ("pattern", "flags", "groups", "_groupindex", '
            b'"_borrow",\n',
            "changed Pattern instance slot",
        ),
        (
            b"class Scanner:",
            b"class ScanneR:",
            "changed complete scanner implementation",
        ),
        (
            b"from candidates import _zig_bridge\n",
            b"from candidates import _rust_bridge\n",
            "cross-candidate bridge dependency",
        ),
    )
    for old, new, label in mutations:
        require(
            repaired.count(old) == 1,
            "missing exact hostile-control source for " + label,
        )
        changed = repaired.replace(old, new, 1)
        checks += reject(
            lambda raw=changed: deallocator_shape(raw, repaired=True),
            label,
        )
        checks += reject(
            lambda raw=changed: prove_lifetime_adapter(original, raw),
            "full source proof for " + label,
        )
    duplicate = (
        repaired
        + b"\ndef __del__(self):\n    return None\n"
    )
    checks += reject(
        lambda: deallocator_shape(duplicate, repaired=True),
        "duplicate or foreign destructor",
    )
    for mode in (
        "--run", "--worker", "--recover", "--build", "--apply",
        "--install", "--benchmark",
    ):
        checks += reject(
            lambda item=mode: parse([item]),
            "forbidden candidate execution mode " + mode,
        )
    predecessor = state["predecessor"]
    receipt = state["publication"]
    for field, value in (
        ("verified_passing_case_count", 4608),
        ("observed_semantic_mismatch_lower_bound", 1699),
        ("semantic_mismatch_count", 0),
        ("completed_suite_count", 13),
        ("candidate_qualified", True),
        ("infrastructure_failure_count", 0),
    ):
        checks += reject(
            lambda key=field, replacement=value: validate_publication(
                predecessor,
                altered_publication(
                    receipt, field=key, value=replacement,
                ),
            ),
            "invented actual historical result " + field,
        )
    checks += reject(
        lambda: validate_publication(
            predecessor, altered_publication(receipt, warning=True),
        ),
        "removed genuine V12 finalizer warning",
    )
    checks += reject(
        lambda: validate_publication(
            predecessor, altered_publication(receipt, child=True),
        ),
        "invented successful guarded child regex execution",
    )
    checks += synthetic_lifetime_controls()
    require(
        checks >= 65 and wall.denials >= 34,
        "reject incomplete physical, lifetime, or historical controls",
    )
    clean()
    return checks


def parse(arguments):
    modes = {
        "--self-test",
        "--verify-frozen-context",
        "--render-contract",
    }
    selected = [item for item in arguments if item in modes]
    require(
        len(selected) == 1,
        "select exactly one physically source-only lifetime action",
    )
    mode = selected[0]
    allowed = {
        "--source-sha256",
        "--protocol-sha256",
        "--contract-sha256",
    }
    parsed = {}
    index = 0
    while index < len(arguments):
        key = arguments[index]
        if key in modes:
            require(
                key == mode,
                "reject conflicting source-only lifetime actions",
            )
            index += 1
            continue
        require(
            key in allowed and key not in parsed
            and index + 1 < len(arguments),
            "reject unknown, duplicated, or incomplete lifetime authority",
        )
        parsed[key] = arguments[index + 1]
        index += 2
    required = {"--source-sha256", "--protocol-sha256"}
    if mode != "--render-contract":
        required.add("--contract-sha256")
    require(
        set(parsed) == required,
        "require independent exact source-only caller pins",
    )
    return mode, parsed


def source_mode(mode, args):
    with SourceWall() as wall:
        if mode == "--render-contract":
            state = context(
                args["--source-sha256"], args["--protocol-sha256"],
            )
            return state["producer"].canonical(contract_value(
                args["--source-sha256"],
                args["--protocol-sha256"],
                state,
            ))
        state = verify(
            args["--source-sha256"],
            args["--protocol-sha256"],
            args["--contract-sha256"],
        )
        checks = (
            hostile_source_controls(state, wall)
            if mode == "--self-test" else 0
        )
        clean()
        result = {
            "schema": SCHEMA + (
                "-source-self-test" if mode == "--self-test"
                else "-verified-frozen-context"
            ),
            "status": "PASS",
            "family": FAMILY,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_obligation_count": 73,
            "original_crosswalk_count": 34,
            "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_candidate_matching": "NOT RUN",
            "historical_v12_actual_candidate_workers": 13,
            "historical_v12_unique_candidate_workers": 13,
            "historical_v12_completed_suite_count": 12,
            "historical_v12_verified_passing_suite_count": 7,
            "historical_v12_verified_passing_case_count": 4607,
            "historical_v12_semantic_failure_count": 5,
            "historical_v12_semantic_mismatch_lower_bound": 1700,
            "historical_v12_semantic_mismatch_count": "NOT MEASURED",
            "historical_v12_warning_observed_suite_count": 13,
            "historical_v12_warning_observed_in_passing_suites": True,
            "historical_v12_infrastructure_failure_count": 1,
            "historical_v12_child_guard_reported_count": 1,
            "historical_v12_child_guard_actually_installed": (
                "NOT ESTABLISHED"
            ),
            "historical_v12_actual_prepared_interpreter_count": 0,
            "historical_v12_actual_case_interpreter_exec_calls": 0,
            "historical_v12_original_child_error": (
                "runtime guard blocked unattested-child-bootstrap"
            ),
            "v13_first_party_build_process_count": 26,
            "v13_first_party_independent_build_phase_count": 2,
            "clean_adapter_sha256": CLEAN_ADAPTER[1],
            "lifetime_adapter_sha256": LIFETIME_ADAPTER[1],
            "changed_destructor_count": 1,
            "matching_ast_unchanged": True,
            "new_instance_slots": 0,
            "clear_before_release": True,
            "release_errors_suppressed": False,
            "synthetic_lifetime_controls": (
                "PASS" if mode == "--self-test" else "NOT RUN"
            ),
            "source_only_hostile_controls": checks,
            "source_only_effects": {name: 0 for name in ZERO_KEYS},
            "candidate_matching": "NOT RUN",
            "repaired_warning": "NOT MEASURED",
            "repaired_subinterpreter": "NOT MEASURED",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "holdout_case_count": 14155776,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
        return state["producer"].canonical(result)


def main():
    mode, args = parse(list(sys.argv[1:]))
    output = source_mode(mode, args)
    require(
        type(output) is bytes and bool(output),
        "reject incomplete source-only canonical output",
    )
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
            "first-party Zig deallocator lifetime source repair rejected: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        )
        raise SystemExit(1) from error
