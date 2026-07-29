#!/usr/bin/env python3
"""Freeze an authenticated isolated namespace for first-party Zig correctness."""

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
SELF = "tools/run_owned_repaired_zig_original_campaign_v8.py"
PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V8.md"
CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v8.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v8"
FAMILY = "zig"
LABEL = "phase2-v13-zig-guard-clean-v1-original-p0-v8"
BUILD_LABEL = "phase2-v13-zig-scanner-phrase-v4"
DEVICE = 2064
PRIVATE_DEVICE = 2049
MAX_BYTES = 8 * 1024 * 1024
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version", "build_zig_engine",
    "build_zig_bridge", "engine_dynamic", "engine_symbols",
    "engine_sections", "engine_notes", "bridge_dynamic", "bridge_symbols",
    "bridge_sections", "bridge_notes",
)
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044)
P0 = (
    ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 524385),
    ("oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md", "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6", 3929, 525081),
    ("oracle/phase1/p0-differential-fuzz-reference-v3.json", "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288, 525082),
    ("oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/two-independent-reference-result.json", "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096", 3658, 524707),
)
GRAPH = (
    ("tools/render_candidate_current_overview_v86.py", "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d", 75354, 431699),
    ("docs/evidence/candidate-current-overview-v86.inputs.json", "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c", 1345744, 430944),
    ("docs/evidence/candidate-current-overview-v86.json", "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc", 4128155, 431704),
    ("docs/evidence/candidate-current-overview-v86.svg", "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55", 6214, 431705),
)
EXPANDED_HOLDOUT_PROPOSAL = (
    ("tools/verify_expanded_sealed_holdout_v1.py", "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309", 27311, 428806),
    ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md", "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4", 13237, 524760),
    ("oracle/phase3/expanded-sealed-holdout-v1.json", "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76", 6628, 524761),
)
HISTORICAL_HOLDOUT_PROPOSAL = (
    "docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md",
    "f7509c60065860d30aad7939dda76f53e1c9f6ebb9db5e1298d0881f63a016eb",
    9481,
    431040,
)
PRODUCER = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py", "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538", 102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md", "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4", 5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json", "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53", 21036, 524885),
)
GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py", "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a", 67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md", "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c", 4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json", "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473", 7671, 524887),
)
SCANNER = (
    ("tools/apply_owned_zig_scanner_phrase_source_repair_v4.py", "31dafa08a8f394a8803fa352dd31c806fdac7aa6ee9160e67f2d5f60b2736a63", 65425, 428967),
    ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md", "e17a46e13652e2950171d84096a0bf812020c88168589c17e50e1bab187339cf", 6919, 524729),
    ("oracle/phase2/zig-scanner-phrase-source-repair-v4.json", "5c8f9a220bf93fc56e9d8054002ea4358323c23a9a951d3ce28201b59947b19c", 11500, 524730),
)
V13 = (
    ("tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py", "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e", 123672, 431366),
    ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md", "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40", 8765, 524873),
    ("oracle/phase2/zig-scanner-phrase-source-build-v13.json", "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15", 21331, 524874),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-phase2-v13-zig-scanner-phrase-v4-build-receipt.json", "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d", 170856, 525149),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-phase2-v13-zig-scanner-phrase-v4-private-root-receipt.json", "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2", 74891, 525148),
)
HISTORY = ("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json", "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111, 524696)
PARENT_ADAPTER = ("candidates/zig/variants/scanner_phrase_v4/zig_candidate.py", "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b", 68530, 428966)
CLEAN_ADAPTER = ("candidates/zig/variants/scanner_phrase_guard_clean_v1/zig_candidate.py", "e8a023a388d94369d3eab38260390e853cd8c38394713aef49856875cfd4ac11", 67262, 429081)
ENGINE_SOURCE = ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915, 429377)
BRIDGE_SOURCE = ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026, 429075)
ORIGINAL_ADAPTER = ("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422, 429360)
NATIVE = {
    "engine": ("caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071", 108888),
    "bridge": ("3dfd80e26773d83acfc83cba7f0df1b85a796ed0059aaa6d855ec0a3b5a93121", 133656),
}
ORIGINALS = {
    "engine": {"relative": "candidates/_zig_probe.so", "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652", "bytes": 478432, "device": DEVICE, "inode": 431260, "mode": 0o700, "uid": 1000, "nlink": 1},
    "bridge": {"relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b", "bytes": 134112, "device": DEVICE, "inode": 431274, "mode": 0o700, "uid": 1000, "nlink": 1},
    "adapter": {"relative": ORIGINAL_ADAPTER[0], "sha256": ORIGINAL_ADAPTER[1], "bytes": ORIGINAL_ADAPTER[2], "device": DEVICE, "inode": ORIGINAL_ADAPTER[3], "mode": 0o600, "uid": 1000, "nlink": 1},
}
ROLES = ("engine", "bridge", "adapter")
RESTORE = ("adapter", "bridge", "engine")
RECOVERY = "/tmp/rebar-phase2-repaired-zig-original-campaign-v8-phase2-v13-zig-guard-clean-v1-original-p0-v8"
PREDECESSOR_V7 = (
    ("tools/run_owned_repaired_zig_original_campaign_v7.py",
     "068af44d35bc9ce49219cf6637b903d1cb1c7d1eb2cc04bd5eec35899efa540e",
     128515, 431115),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V7.md",
     "5344997fd7cc3cb02b118acc163d9694d3e47953ca5ee878bc47940c9a0ee70f",
     5550, 525145),
    ("oracle/phase2/repaired-zig-original-campaign-v7.json",
     "eda54fe33314ca44d96817e54f3847e2435656d9b7543a34cb2f380eee4d2550",
     24243, 525146),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v7-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v7-"
     "failures-publication-receipt.json",
     "b7e9091f24bde56dd67ecceacc3195e931916dffd7f7fd15c09e2bb301a365ab",
     47922, 525166),
)
REPOSITORY_ROOT_INODE = 31364017
REPOSITORY_ROOT_MODE = 0o775
CANDIDATE_NAMESPACE_INODE = 427975
CANDIDATE_NAMESPACE_MODE = 0o700

PREDECESSOR_V6 = (
    ("tools/run_owned_repaired_zig_original_campaign_v6.py",
     "200024fba683d8027b4ad59f0b3ebab63304104493c165f0c4549d4dba2bfb2e",
     101571, 430939),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V6.md",
     "013fac08c19c3721882196fe2550958871b738ba2a7f75c7268c8ea006bc250c",
     5276, 525002),
    ("oracle/phase2/repaired-zig-original-campaign-v6.json",
     "103a22716f101198f070c6c8b3c0a182b77d57eb160f2768998f078208333df4",
     21517, 525003),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v6-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v6-"
     "failures-publication-receipt.json",
     "c04bab24727a44ee56f6fd0e38129c0504b48ece8ad3a1fa73639f5d89cc2d52",
     11417, 525106),
)
MAX_FAILURE_MESSAGE_BYTES = 4096
MAX_FAILURE_TRACEBACK_BYTES = 16384
MAX_FAILURE_TRACEBACK_FRAMES = 24
MAX_PUBLIC_STDERR_BYTES = 4096

PREDECESSOR_V5 = (
    ("tools/run_owned_repaired_zig_original_campaign_v5.py",
     "cc01b6743cde15bbcf4d2c8a5bf54f3d6a6cd1307de6e2295038d8edfb457b0e",
     89272, 430182),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V5.md",
     "eefba93b3d37659a5de32c6be7bf308ebef507e4ab6abe83fd4a6d4f7fa23c3f",
     8044, 524787),
    ("oracle/phase2/repaired-zig-original-campaign-v5.json",
     "c574ed19f870c5ae57505c980dbc8512971833dfab9f7cd3251f1a223ec1ad70",
     19190, 524788),
)
EXTERNAL_LOCPATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
SUITE_TIMEOUT_SECONDS = 120
MAX_SERIAL_SUITE_TIMEOUT_SECONDS = 13 * SUITE_TIMEOUT_SECONDS

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
    pass


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


def owners(*, active=False):
    result = (GOAL, *P0, *GRAPH, *EXPANDED_HOLDOUT_PROPOSAL,
              HISTORICAL_HOLDOUT_PROPOSAL, *PREDECESSOR_V7,
              *PREDECESSOR_V6,
              *PREDECESSOR_V5, *PRODUCER, *GUARD, *SCANNER,
              *V13, HISTORY, PARENT_ADAPTER, CLEAN_ADAPTER,
              ENGINE_SOURCE, BRIDGE_SOURCE)
    return result if active else result + (ORIGINAL_ADAPTER,)


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


def context(source_sha, protocol_sha, *, active=False):
    clean()
    for path, expected in ((SELF, pin(source_sha, "source")),
                           (PROTOCOL, pin(protocol_sha, "protocol"))):
        info = os.stat(ROOT + "/" + path, follow_symlinks=False)
        read_owner((path, expected, info.st_size, info.st_ino))
    for item in owners(active=active):
        read_owner(item)
    producer = load(PRODUCER[0], "_rebar_guard_clean_zig_v5_producer")
    require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
            and producer.CASE_DENOMINATOR == 31237
            and producer.SUITE_COUNT == 13
            and producer.ORIGINAL_OBLIGATION_COUNT == 73
            and producer.ORIGINAL_CROSSWALK_COUNT == 34
            and tuple((row.name, row.case_count) for row in producer.SUITES)
            == SUITES and sum(n for _, n in SUITES) == 31237,
            "reject a changed immutable V5 correctness producer")
    predecessor = producer.JsonReader(read_owner(PREDECESSOR_V5[2])).parse()
    predecessor_oracle = predecessor.get("original_oracle", {})
    predecessor_holdout = predecessor.get(
        "expanded_sealed_holdout_proposal", {})
    require(
        predecessor.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v5-guard-clean-source-freeze"
        and predecessor.get("version") == 5
        and predecessor.get("status")
        == "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN"
        and predecessor.get("family") == FAMILY
        and predecessor.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v5"
        and predecessor.get("source") == record(PREDECESSOR_V5[0])
        and predecessor.get("protocol") == record(PREDECESSOR_V5[1])
        and predecessor_oracle.get("case_execution_denominator") == 31237
        and predecessor_oracle.get("suite_count") == 13
        and predecessor_oracle.get("supplemental_case_count") == 8244
        and predecessor_oracle.get("supplemental_candidate_matching")
        == "NOT RUN"
        and predecessor_holdout.get("status") == "PRE-PHASE-3 PROPOSAL"
        and predecessor_holdout.get("case_status")
        == "NOT GENERATED; NOT OPENED"
        and predecessor_holdout.get("case_count") == 14155776
        and predecessor_holdout.get("qualified_independent_family_count")
        == 0
        and predecessor.get("corrected_original_matching") == "NOT RUN"
        and predecessor.get("corrected_supplemental_matching") == "NOT RUN"
        and predecessor.get("qualified_candidate_count") == 0
        and predecessor.get("holdout_case_count") == 14155776
        and predecessor.get("minimum_qualified_candidates") == 3
        and predecessor.get("current_qualified_candidates") == 0,
        "reject an unauthenticated, executed, miscounted, or "
        "falsely qualified pushed V5 Zig campaign predecessor",
    )
    previous_v6 = producer.JsonReader(
        read_owner(PREDECESSOR_V6[2])
    ).parse()
    previous_receipt = producer.JsonReader(
        read_owner(PREDECESSOR_V6[3])
    ).parse()
    previous_rows = previous_receipt.get("original_suite_diagnostics", [])
    require(
        previous_v6.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v6-guard-clean-source-freeze"
        and previous_v6.get("version") == 6
        and previous_v6.get("source") == record(PREDECESSOR_V6[0])
        and previous_v6.get("protocol") == record(PREDECESSOR_V6[1])
        and previous_v6.get("family") == FAMILY
        and previous_v6.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v6"
        and previous_v6.get("corrected_original_matching") == "NOT RUN"
        and previous_v6.get("corrected_supplemental_matching") == "NOT RUN"
        and previous_v6.get("qualified_candidate_count") == 0
        and previous_v6.get("holdout_case_count") == 14155776
        and previous_v6.get("current_qualified_candidates") == 0
        and previous_v6.get("minimum_qualified_candidates") == 3,
        "reject an unauthenticated or falsely qualified pushed V6 freeze",
    )
    require(
        previous_receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v6-durable-publication-receipt"
        and previous_receipt.get("status") == "PASS"
        and previous_receipt.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and previous_receipt.get("candidate_status") == "FAIL"
        and previous_receipt.get("original_campaign_passed") is False
        and previous_receipt.get("candidate_qualified") is False
        and previous_receipt.get("family") == FAMILY
        and previous_receipt.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v6"
        and previous_receipt.get("source_sha256") == PREDECESSOR_V6[0][1]
        and previous_receipt.get("protocol_sha256") == PREDECESSOR_V6[1][1]
        and previous_receipt.get("contract_sha256") == PREDECESSOR_V6[2][1]
        and previous_receipt.get("case_execution_denominator") == 31237
        and previous_receipt.get("suite_count") == 13
        and previous_receipt.get("all_original_suites_attempted") is True
        and previous_receipt.get("actual_candidate_workers") == 13
        and previous_receipt.get("unique_candidate_worker_count") == 13
        and previous_receipt.get("completed_suite_count") == 0
        and previous_receipt.get("verified_passing_case_count") == 0
        and previous_receipt.get("infrastructure_failure_count") == 13
        and previous_receipt.get("semantic_mismatch_count") == "NOT MEASURED"
        and previous_receipt.get("observed_semantic_mismatch_lower_bound")
        == 0
        and previous_receipt.get("per_suite_timeout_seconds") == 120
        and previous_receipt.get("maximum_serial_worker_timeout_seconds")
        == 1560
        and previous_receipt.get("timeout_count") == 0
        and previous_receipt.get("timed_out_suites") == []
        and previous_receipt.get("all_three_original_targets_restored")
        is True
        and previous_receipt.get("supplemental_candidate_matching")
        == "NOT RUN"
        and previous_receipt.get("holdout") == "NOT OPENED"
        and previous_receipt.get("performance") == "NOT MEASURED"
        and type(previous_rows) is list
        and len(previous_rows) == 13
        and tuple(
            (item.get("suite"), item.get("case_execution_denominator"))
            for item in previous_rows
        ) == SUITES
        and [item.get("pid") for item in previous_rows]
        == list(range(81, 94))
        and all(
            item.get("returncode") == 1
            and item.get("status") == "FAIL"
            and item.get("infrastructure_failure") is True
            and item.get("actual_worker_schema") is None
            and item.get("observed_semantic_mismatch_count")
            == "NOT MEASURED"
            and type(item.get("stdout")) is dict
            and item["stdout"].get("bytes") == 0
            and item["stdout"].get("sha256")
            == "e3b0c44298fc1c149afbf4c8996fb924"
               "27ae41e4649b934ca495991b7852b855"
            and type(item.get("stderr")) is dict
            and item["stderr"].get("bytes") == 106
            and item["stderr"].get("sha256")
            == "0eae62828a696afbaaaa1212c0979f0b"
               "86afe95f59d1870f3ad0dea7fe2c08b7"
            for item in previous_rows
        ),
        "reject invented, incomplete, semantically misclassified, or "
        "archive-derived historical V6 worker-failure evidence",
    )
    previous_v7 = producer.JsonReader(
        read_owner(PREDECESSOR_V7[2])
    ).parse()
    previous_v7_receipt = producer.JsonReader(
        read_owner(PREDECESSOR_V7[3])
    ).parse()
    previous_v7_rows = previous_v7_receipt.get(
        "original_suite_diagnostics", []
    )
    require(
        previous_v7.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v7-guard-clean-source-freeze"
        and previous_v7.get("version") == 7
        and previous_v7.get("source") == record(PREDECESSOR_V7[0])
        and previous_v7.get("protocol") == record(PREDECESSOR_V7[1])
        and previous_v7.get("family") == FAMILY
        and previous_v7.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v7"
        and previous_v7.get("corrected_original_matching") == "NOT RUN"
        and previous_v7.get("corrected_supplemental_matching") == "NOT RUN"
        and previous_v7.get("qualified_candidate_count") == 0
        and previous_v7.get("holdout_case_count") == 14155776
        and previous_v7.get("minimum_qualified_candidates") == 3
        and previous_v7.get("current_qualified_candidates") == 0,
        "reject an unauthenticated or falsely qualified pushed V7 freeze",
    )
    require(
        previous_v7_receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v7-durable-publication-receipt"
        and previous_v7_receipt.get("status") == "PASS"
        and previous_v7_receipt.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and previous_v7_receipt.get("candidate_status") == "FAIL"
        and previous_v7_receipt.get("original_campaign_passed") is False
        and previous_v7_receipt.get("candidate_qualified") is False
        and previous_v7_receipt.get("family") == FAMILY
        and previous_v7_receipt.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v7"
        and previous_v7_receipt.get("source_sha256")
        == PREDECESSOR_V7[0][1]
        and previous_v7_receipt.get("protocol_sha256")
        == PREDECESSOR_V7[1][1]
        and previous_v7_receipt.get("contract_sha256")
        == PREDECESSOR_V7[2][1]
        and previous_v7_receipt.get("case_execution_denominator") == 31237
        and previous_v7_receipt.get("suite_count") == 13
        and previous_v7_receipt.get("all_original_suites_attempted")
        is True
        and previous_v7_receipt.get("actual_candidate_workers") == 13
        and previous_v7_receipt.get("unique_candidate_worker_count") == 13
        and previous_v7_receipt.get("completed_suite_count") == 0
        and previous_v7_receipt.get("verified_passing_case_count") == 0
        and previous_v7_receipt.get("infrastructure_failure_count") == 13
        and previous_v7_receipt.get("semantic_mismatch_count")
        == "NOT MEASURED"
        and previous_v7_receipt.get("per_suite_timeout_seconds") == 120
        and previous_v7_receipt.get(
            "maximum_serial_worker_timeout_seconds"
        ) == 1560
        and previous_v7_receipt.get("timeout_count") == 0
        and previous_v7_receipt.get("all_three_original_targets_restored")
        is True
        and previous_v7_receipt.get("supplemental_candidate_matching")
        == "NOT RUN"
        and previous_v7_receipt.get("holdout") == "NOT OPENED"
        and type(previous_v7_rows) is list
        and len(previous_v7_rows) == 13
        and tuple(
            (row.get("suite"), row.get("case_execution_denominator"))
            for row in previous_v7_rows
        ) == SUITES
        and [row.get("pid") for row in previous_v7_rows]
        == list(range(81, 94))
        and all(
            row.get("returncode") == 0
            and row.get("status") == "FAIL"
            and row.get("infrastructure_failure") is True
            and row.get("actual_worker_schema")
            == "rebar-owned-repaired-zig-original-campaign-v7-"
               "actual-worker-failure"
            and row.get("activation_stage")
            == "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE"
            and row.get("error_type") == "ModuleNotFoundError"
            and row.get("error_class") == "builtins.ModuleNotFoundError"
            and row.get("error_message") == "No module named 'candidates'"
            and row.get("guard_installed_before_candidate_import") is True
            and row.get("candidate_imported") is False
            and type(row.get("error_traceback")) is dict
            and row["error_traceback"].get("total_bytes") == 831
            and row["error_traceback"].get("captured_bytes") == 831
            and row["error_traceback"].get("sha256")
            == "de2674e9cfbdcb1fceedacc2bf30fb15"
               "2396ca3dea5dcb2960f70bd9a0c75aa5"
            and type(row.get("traceback_frames")) is list
            and len(row["traceback_frames"]) == 9
            and row["traceback_frames"][0].get("file")
            == ROOT + "/tools/run_owned_repaired_zig_original_campaign_v7.py"
            and row["traceback_frames"][0].get("line") == 1841
            and type(row.get("stdout")) is dict
            and row["stdout"].get("bytes", 0) > 0
            and type(row.get("stderr")) is dict
            and row["stderr"].get("bytes") == 0
            and type(row.get("stderr_literal_excerpt")) is dict
            and row["stderr_literal_excerpt"].get("status") == "CAPTURED"
            and row["stderr_literal_excerpt"].get("text") == ""
            for row in previous_v7_rows
        ),
        "reject invented, unguarded, archive-derived, or changed actual "
        "V7 namespace-import failure evidence",
    )
    phase = producer.JsonReader(read_owner(P0[1])).parse()
    gate, oracle = phase.get("phase_gate", {}), phase.get("original_oracle", {})
    require(phase.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and phase.get("version") == 4 and phase.get("status") == "PASS"
            and phase.get("original_case_execution_denominator") == 31237
            and phase.get("original_suite_count") == 13
            and phase.get("original_named_private_waiver_count") == 13
            and phase.get("original_obligation_count") == 73
            and phase.get("original_crosswalk_count") == 34
            and gate.get("status") == "PASS"
            and gate.get("candidate_evaluation_authorized") is True
            and gate.get("final_holdout_authorized") is False
            and gate.get("performance_oracle_authorized") is False
            and [(row.get("id"), row.get("case_execution_count"))
                 for row in oracle.get("suites", [])] == list(SUITES),
            "preserve exactly the frozen complete phase-one P0 matrix")
    for suite in producer.SUITES:
        read_suite(suite.source_relative, suite.source_sha256)
    manifest = producer.JsonReader(read_owner(P0[2])).parse()
    require(type(manifest.get("suites")) is list
            and len(manifest["suites"]) == 13,
            "reject the original archived baseline manifest")
    fuzz = producer.JsonReader(read_owner(P0[5])).parse()
    workers = fuzz.get("workers", [])
    require(fuzz.get("status") == "PASS"
            and fuzz.get("actual_reference_worker_count") == 2
            and len(workers) == 2
            and {row.get("pid") for row in workers} == {81, 82}
            and all(row.get("case_count") == 8244 for row in workers)
            and fuzz.get("holdout") == "NOT OPENED",
            "preserve the separate 8,244-case dual-Python reference")
    proposal = producer.JsonReader(
        read_owner(EXPANDED_HOLDOUT_PROPOSAL[2])
    ).parse()
    required = proposal.get("required_public_owners", [])
    historical = [
        item for item in required
        if type(item) is dict
        and item.get("path") == HISTORICAL_HOLDOUT_PROPOSAL[0]
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
        and proposal.get("pinned_python_sha256")
        == "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
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
        and historical[0].get("sha256") == HISTORICAL_HOLDOUT_PROPOSAL[1],
        "reject a stale, generated, opened, falsely authorized, or "
        "miscounted 14,155,776-case public holdout proposal",
    )
    graph = producer.JsonReader(read_owner(GRAPH[2])).parse()
    require(graph.get("schema") == "rebar-candidate-current-overview-v86-summary"
            and graph.get("version") == 86
            and graph.get("authenticated_evidence_owner_lower_bound") == 277
            and graph.get("authenticated_history_reference_lower_bound") == 282
            and graph.get("actual_zig_semantic_mismatch_count") == 1764
            and graph.get("qualified_candidate_count") == 0
            and graph.get("zig_v13_first_party_source_build_status")
            == "NATIVE BUILD PASS; CANDIDATE MATCHING NOT RUN"
            and graph.get("performance") == "NOT MEASURED",
            "preserve actual published losses and current overview")
    history = producer.JsonReader(read_owner(HISTORY)).parse()
    require(history.get("schema")
            == "rebar-owned-repaired-zig-original-campaign-v3-durable-publication-receipt"
            and history.get("status") == "PASS"
            and history.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and history.get("candidate_status") == "FAIL"
            and history.get("semantic_mismatch_count") == 1764
            and history.get("verified_passing_case_count") == 3711
            and history.get("actual_candidate_workers") == 13
            and history.get("completed_suite_count") == 13
            and history.get("infrastructure_failure_count") == 0
            and history.get("case_execution_denominator") == 31237,
            "preserve every actual historical Zig failure")
    producer_contract = producer.JsonReader(read_owner(PRODUCER[2])).parse()
    zig = [row for row in producer_contract.get("families", [])
           if row.get("name") == "zig"]
    require(producer_contract.get("version") == 5
            and producer_contract.get("original_obligation_count") == 73
            and producer_contract.get("original_crosswalk_count") == 34
            and producer_contract.get("supplemental_case_count") == 8244
            and len(zig) == 1 and zig[0].get("owned_ctypes") is True,
            "reject an edited immutable six-family correctness producer")
    guard = producer.JsonReader(read_owner(GUARD[2])).parse()
    require(guard.get("schema")
            == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
            and guard.get("source", {}).get("sha256") == GUARD[0][1]
            and guard.get("protocol", {}).get("sha256") == GUARD[1][1],
            "reject a weakened or replaced guard-before-import policy")
    build, root = validate_build(producer)
    normalized = normalize(read_owner(PARENT_ADAPTER))
    require(normalized == read_owner(CLEAN_ADAPTER),
            "bind the complete new first-party adapter to its exact AST proof")
    namespace = authenticated_first_party_namespace()
    clean()
    return {"producer": producer, "predecessor": predecessor,
            "predecessor_v7": previous_v7,
            "predecessor_v7_publication": previous_v7_receipt,
            "predecessor_v6": previous_v6,
            "predecessor_v6_publication": previous_receipt,
            "first_party_namespace": namespace,
            "phase": phase, "manifest": manifest,
            "fuzz": fuzz, "graph": graph, "history": history,
            "build": build, "root": root, "expanded_holdout": proposal}


def contract_value(source_sha, protocol_sha, state=None):
    if state is None:
        state = context(source_sha, protocol_sha)
    source_stat = os.stat(ROOT + "/" + SELF, follow_symlinks=False)
    protocol_stat = os.stat(ROOT + "/" + PROTOCOL, follow_symlinks=False)
    return {
        "schema": SCHEMA + "-guard-clean-source-freeze",
        "version": 8,
        "status": "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN",
        "family": FAMILY, "label": LABEL,
        "source": record((SELF, source_sha, source_stat.st_size, source_stat.st_ino)),
        "protocol": record((PROTOCOL, protocol_sha, protocol_stat.st_size, protocol_stat.st_ino)),
        "goal": record(GOAL),
        "pushed_v7_predecessor": {
            "owners": [record(item) for item in PREDECESSOR_V7],
            "source_freeze_schema": state["predecessor_v7"]["schema"],
            "source_freeze_version": 7,
            "plaintext_publication": {
                "owner": record(PREDECESSOR_V7[3]),
                "publication_status": "PASS",
                "publication_pass_means": "DURABLE PUBLICATION ONLY",
                "candidate_status": "FAIL",
                "actual_candidate_workers": 13,
                "unique_candidate_worker_count": 13,
                "worker_pids": list(range(81, 94)),
                "worker_exit_status": 0,
                "completed_suite_count": 0,
                "infrastructure_failure_count": 13,
                "semantic_mismatch_count": "NOT MEASURED",
                "failure_activation_stage":
                    "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE",
                "failure_exception_class": "builtins.ModuleNotFoundError",
                "failure_exception_message":
                    "No module named 'candidates'",
                "failure_traceback_bytes": 831,
                "failure_traceback_sha256":
                    "de2674e9cfbdcb1fceedacc2bf30fb15"
                    "2396ca3dea5dcb2960f70bd9a0c75aa5",
                "guard_installed_before_candidate_import": True,
                "candidate_imported": False,
                "matching_archive_opened": False,
                "all_three_original_targets_restored": True,
            },
        },
        "first_party_namespace": {
            "verified_source_owner": state["first_party_namespace"],
            "repository_root": {
                "absolute_path": ROOT,
                "device": DEVICE,
                "inode": REPOSITORY_ROOT_INODE,
                "mode": "0775",
                "uid": 1000,
            },
            "namespace_directory": {
                "absolute_path": ROOT + "/candidates",
                "device": DEVICE,
                "inode": CANDIDATE_NAMESPACE_INODE,
                "mode": "0700",
                "uid": 1000,
                "package_kind": "PEP 420 NAMESPACE; NO __init__.py",
            },
            "canonical_candidate_module": "candidates.zig_candidate",
            "canonical_candidate_source":
                ROOT + "/candidates/zig_candidate.py",
            "resolver":
                "_frozen_importlib_external.PathFinder",
            "root_insert_position": 0,
            "insert_only_after_runtime_guard_installation": True,
            "insert_only_after_authenticated_family_preparation": True,
            "relative_or_empty_path_allowed": False,
            "working_directory_fallback_allowed": False,
            "environment_path_fallback_allowed": False,
            "foreign_package_root_allowed": False,
            "native_or_candidate_import_during_source_modes": False,
        },
        "pushed_v6_predecessor": {
            "owners": [record(item) for item in PREDECESSOR_V6],
            "source_freeze_schema": state["predecessor_v6"]["schema"],
            "source_freeze_version": 6,
            "plaintext_publication": {
                "owner": record(PREDECESSOR_V6[3]),
                "publication_status": "PASS",
                "publication_pass_means": "DURABLE PUBLICATION ONLY",
                "candidate_status": "FAIL",
                "actual_candidate_workers": 13,
                "unique_candidate_worker_count": 13,
                "worker_pids": list(range(81, 94)),
                "worker_exit_status": 1,
                "completed_suite_count": 0,
                "infrastructure_failure_count": 13,
                "semantic_mismatch_count": "NOT MEASURED",
                "actual_stderr_bytes_per_worker": 106,
                "actual_stderr_sha256":
                    "0eae62828a696afbaaaa1212c0979f0b"
                    "86afe95f59d1870f3ad0dea7fe2c08b7",
                "actual_stdout_bytes_per_worker": 0,
                "actual_stdout_sha256":
                    "e3b0c44298fc1c149afbf4c8996fb924"
                    "27ae41e4649b934ca495991b7852b855",
                "historical_literal_stderr":
                    "NOT PUBLISHED; NOT RECOVERED FROM ARCHIVE",
                "historical_failure_cause": "NOT ESTABLISHED",
                "matching_archive_opened": False,
                "all_three_original_targets_restored": True,
            },
        },
        "pushed_v5_predecessor": {
            "owners": [record(item) for item in PREDECESSOR_V5],
            "schema": state["predecessor"]["schema"],
            "version": state["predecessor"]["version"],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "supplemental_candidate_matching": "NOT RUN",
            "corrected_original_matching": "NOT RUN",
            "holdout_case_count": 14155776,
            "qualified_candidate_count": 0,
        },
        "pinned_cpython": {"path": PYTHON, "version": "3.14.6",
                           "flags": ["-I", "-B", "-S"]},
        "original_oracle": {
            "matrix_version": 4, "case_execution_denominator": 31237,
            "suite_count": 13, "obligation_count": 73,
            "crosswalk_count": 34, "named_private_waiver_count": 13,
            "suites": [{"id": x.name, "case_execution_count": x.case_count,
                        "source": x.source_relative,
                        "source_sha256": x.source_sha256,
                        "matrix_sha256": x.matrix_sha256,
                        "reference_sha256": x.reference_sha256,
                        "seed": x.seed, "route": x.route}
                       for x in state["producer"].SUITES],
            "supplemental_case_count": 8244,
            "supplemental_reference_workers": 2,
            "supplemental_cases_added_to_original_denominator": False,
            "supplemental_candidate_matching": "NOT RUN",
            "phase_one_owners": [record(x) for x in P0],
        },
        "immutable_v5_observer": {
            "owners": [record(x) for x in PRODUCER],
            "observer_or_cases_modified": False,
            "fresh_guard_clean_zig_family_spec_required": True,
        },
        "immutable_v2_runtime_guard": {
            "owners": [record(x) for x in GUARD],
            "installed_before_candidate_import": True,
            "native_owner_mode": "0600",
            "ctypes_dlopen_permitted": False,
            "stdlib_regex_engine_permitted": False,
            "external_regex_package_permitted": False,
            "other_candidate_permitted": False,
            "fallback_permitted": False,
        },
        "first_party_zig": {
            "engine_source": record(ENGINE_SOURCE),
            "bridge_source": record(BRIDGE_SOURCE),
            "v13_original_scanner_adapter": record(PARENT_ADAPTER),
            "guard_clean_scanner_adapter": record(CLEAN_ADAPTER),
            "exact_removed_ctypes_import_count": 1,
            "exact_removed_dead_initializer_statement_count": 20,
            "replacement_initializer_statement": "pass",
            "complete_matching_ast_unchanged": True,
            "v13_build_attests_guard_clean_adapter": False,
            "scanner_repair_owners": [record(x) for x in SCANNER],
        },
        "actual_v13_source_build": {
            "status": "PASS", "label": BUILD_LABEL,
            "owners": [record(x) for x in V13],
            "actual_process_count": 26,
            "independent_phase_count": 2,
            "source_snapshot_count": 6,
            "native_engine": {"sha256": NATIVE["engine"][0],
                              "bytes": NATIVE["engine"][1]},
            "native_bridge": {"sha256": NATIVE["bridge"][0],
                              "bytes": NATIVE["bridge"][1]},
            "private_native_mode": "0700",
            "private_native_device": PRIVATE_DEVICE,
            "guard_clean_adapter_included": False,
            "candidate_matching": "NOT RUN",
            "external_regex_dependency_count": 0,
            "stdlib_regex_engine_count": 0,
            "cross_family_engine_count": 0,
        },
        "preserved_history": {
            "receipt": record(HISTORY),
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1764,
            "verified_passing_case_count": 3711,
            "actual_candidate_workers": 13,
        },
        "published_graph": {
            "version": 86, "owners": [record(x) for x in GRAPH],
            "authenticated_evidence_owner_lower_bound": 277,
            "authenticated_history_reference_lower_bound": 282,
        },
        "expanded_sealed_holdout_proposal": {
            "status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "generator_status": "NOT FROZEN",
            "secret_status": "NOT GENERATED",
            "case_status": "NOT GENERATED; NOT OPENED",
            "case_count": 14155776,
            "timed_case_count": 14155776,
            "minimum_qualified_independent_family_count": 3,
            "qualified_independent_family_count": 0,
            "operation_count": 36,
            "pattern_family_count": 24,
            "subject_type_count": 4,
            "lifecycle_count": 4,
            "cases_per_stratum": 1024,
            "stratum_count": 13824,
            "proposal_verifier_executed": False,
            "holdout_generator_executed": False,
            "holdout_files_opened": 0,
            "timing_trials_run": 0,
            "owners": [
                record(item) for item in EXPANDED_HOLDOUT_PROPOSAL
            ],
            "historical_proposal": {
                "owner": record(HISTORICAL_HOLDOUT_PROPOSAL),
                "case_count": 4194304,
                "status": "PROPOSED; NOT FROZEN; NOT GENERATED; NOT OPENED",
            },
        },
        "bounded_original_campaign": {
            "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "timeout_scope": "120 SECONDS FOR EACH COMPLETE ORIGINAL SUITE",
            "original_suite_attempt_count": 13,
            "original_case_execution_denominator": 31237,
            "maximum_serial_worker_timeout_seconds":
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
            "worker_startup_output_and_recovery_overhead_included": False,
            "all_original_suites_attempted_after_timeout": True,
            "continue_after_every_infrastructure_failure": True,
            "timeout_classification": "INFRASTRUCTURE FAILURE",
            "timed_out_suite_status": "FAIL",
            "partial_or_unavailable_mismatch_count": "NOT MEASURED",
            "preserve_complete_stdout_and_stderr": True,
            "preserve_actual_suite_failure_details": True,
            "complete_worker_bootstrap_enclosed": True,
            "historical_v7_failure_cause":
                "AUTHENTICATED ISOLATED NAMESPACE NOT ON sys.path",
            "historical_v7_failure_evidence_opened":
                "PUSHED PLAINTEXT RECEIPT ONLY",
            "first_party_namespace_owner_authenticated": True,
            "first_party_namespace_is_pep_420": True,
            "only_authenticated_repository_root_prepended": True,
            "repository_root_insert_position": 0,
            "namespace_path_inserted_after_strict_guard": True,
            "foreign_root_or_working_directory_fallback": False,
            "namespace_spec_verified_without_candidate_import": True,
            "bootstrap_failure_stage_visible": True,
            "bootstrap_exception_class_visible": True,
            "bootstrap_message_limit_bytes": MAX_FAILURE_MESSAGE_BYTES,
            "bootstrap_traceback_limit_bytes":
                MAX_FAILURE_TRACEBACK_BYTES,
            "bootstrap_traceback_frame_limit":
                MAX_FAILURE_TRACEBACK_FRAMES,
            "worker_json_independent_of_post_guard_module_load": True,
            "worker_json_matches_immutable_producer_canonical": True,
            "literal_stderr_excerpt_limit_bytes": MAX_PUBLIC_STDERR_BYTES,
            "literal_stderr_in_plaintext_publication_receipt": True,
            "literal_stderr_in_actual_run_stdout": True,
            "unavailable_stderr_explicitly_not_measured": True,
            "plaintext_publication_receipt_contains_timeout_evidence": True,
            "plaintext_publication_receipt_contains_all_suite_diagnostics":
                True,
            "actual_run_stdout_contains_timeout_evidence": True,
            "actual_run_stdout_contains_all_suite_diagnostics": True,
            "complete_worker_stream_payloads_preserved_in_archive": True,
            "stream_hashes_and_sizes_visible_without_archive": True,
            "timeout_can_qualify_candidate": False,
            "supplemental_candidate_matching": "NOT RUN",
            "benchmark_cases_read": 0,
            "holdout_cases_read": 0,
        },
        "future_actual_run": {
            "authorization": "SEPARATE EXPLICIT FULLY PINNED --run",
            "recovery_root": RECOVERY,
            "role_order": list(ROLES),
            "restoration_order": list(RESTORE),
            "canonical_original_targets": ORIGINALS,
            "canonical_role_count": 3,
            "guard_clean_native_mode": "0600",
            "cross_device_native_copy_required": True,
            "durable_three_role_journal_before_replacement": True,
            "adjacent_exact_inode_backups_required": True,
            "atomic_group": False,
            "distinct_original_suite_workers": 13,
            "externally_prepared_locpath": EXTERNAL_LOCPATH,
            "locale_data_created_by_campaign": False,
            "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "maximum_serial_worker_timeout_seconds":
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
            "timeout_classification": "INFRASTRUCTURE FAILURE",
            "continue_after_every_failure": True,
            "preserve_actual_suite_failure_details": True,
            "all_original_targets_restored_before_publication": True,
            "separate_pinned_recovery_mode": "--recover",
            "recovery_without_candidate_import": True,
            "distinct_exclusive_result_archive_required": True,
            "distinct_exclusive_publication_receipt_required": True,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "full_candidate_qualification_before_supplemental": False,
        },
        "source_only_effects": {name: 0 for name in ZERO_KEYS},
        "corrected_original_matching": "NOT RUN",
        "corrected_supplemental_matching": "NOT RUN",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "holdout_case_count": 14155776,
        "holdout_case_status":
            "PROPOSED; NOT FROZEN; NOT GENERATED; NOT OPENED",
        "historical_holdout_case_count": 4194304,
        "minimum_qualified_candidates": 3,
        "current_qualified_candidates": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def verify(source_sha, protocol_sha, contract_sha, *, active=False):
    info = os.stat(ROOT + "/" + CONTRACT, follow_symlinks=False)
    item = (CONTRACT, pin(contract_sha, "contract"), info.st_size, info.st_ino)
    state = context(source_sha, protocol_sha, active=active)
    actual = state["producer"].JsonReader(read_owner(item)).parse()
    require(actual == contract_value(source_sha, protocol_sha, state)
            and state["producer"].canonical(actual) == read_owner(item),
            "reject modified or noncanonical complete source-freeze contract")
    return state


def reject(operation, label):
    try:
        operation()
    except (CampaignError, OSError, ImportError, SyntaxError, ValueError):
        return 1
    raise CampaignError("accepted negative control: " + label)


def source_mode(mode, args):
    with SourceWall() as wall:
        if mode == "--render-contract":
            return contract_value(args["--source-sha256"],
                                  args["--protocol-sha256"])
        state = verify(args["--source-sha256"], args["--protocol-sha256"],
                       args["--contract-sha256"])
        checks = 0
        if mode == "--self-test":
            for name in ("re", "_sre", "regex", "re2", "ctypes",
                         "candidates", "candidates.zig_candidate",
                         "candidates.rust_candidate", "subprocess", "socket",
                         "threading", "multiprocessing", "gzip", "json", "time"):
                checks += reject(lambda n=name: builtins.__import__(n), name)
            for path in (RECOVERY, EXTERNAL_LOCPATH,
                         "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-yhzrep3u",
                         ROOT + "/candidates/_zig_probe.so",
                         ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
                         ROOT + "/oracle/phase2/evidence/forbidden.json.gz",
                         ROOT + "/performance/final-holdout.json"):
                checks += reject(lambda p=path: os.open(p, os.O_RDONLY), path)
            for operation, label in (
                    (lambda: os.open(ROOT + "/" + SELF, os.O_WRONLY), "write"),
                    (lambda: os.mkdir("/tmp/rebar-zig-v8-forbidden"), "mkdir"),
                    (lambda: sys.audit("ctypes.dlopen", "forbidden"), "dlopen"),
                    (lambda: sys.audit("ctypes.dlsym", None, "rebar_zig_compile"), "dlsym"),
                    (lambda: sys.audit("subprocess.Popen", "zig", [], None, None), "process"),
                    (lambda: sys.audit("socket.connect", None, None), "network"),
                    (lambda: pin("x" * 63, "bad"), "invalid hash"),
                    (lambda: relative("../holdout"), "escaped owner")):
                checks += reject(operation, label)
            raw = read_owner(PARENT_ADAPTER)
            checks += reject(lambda: normalize(
                raw.replace(b"class Scanner:", b"class ScanneR:", 1)),
                "changed complete scanner")
            checks += reject(lambda: normalize(
                raw.replace(b"import ctypes\n", b"import ctypes as x\n", 1)),
                "changed loader import")
            checks += reject(
                lambda: public_campaign_diagnostics({}),
                "omitted actual public suite diagnostics",
            )
            checks += reject(
                lambda: public_stream_owner({
                    "bytes": 0, "sha256": "invalid", "complete": True,
                }),
                "unauthenticated actual public worker stream",
            )
            checks += synthetic_evidence_controls(state["producer"])
            checks += synthetic_first_party_namespace_controls()
            require(checks >= 48 and wall.denials >= 33,
                    "reject incomplete source-wall hostile controls")
        clean()
        return {
            "schema": SCHEMA + ("-source-self-test"
                                if mode == "--self-test"
                                else "-verified-frozen-context"),
            "status": "PASS", "family": FAMILY,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13, "original_obligation_count": 73,
            "worker_bootstrap_enclosed": True,
            "historical_v7_failure_cause":
                "ModuleNotFoundError: No module named 'candidates'",
            "historical_v7_failure_activation_stage":
                "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE",
            "historical_v7_traceback_bytes": 831,
            "historical_v7_traceback_sha256":
                "de2674e9cfbdcb1fceedacc2bf30fb15"
                "2396ca3dea5dcb2960f70bd9a0c75aa5",
            "historical_v7_infrastructure_failure_count": 13,
            "first_party_namespace_repair_control":
                "PASS" if mode == "--self-test" else "NOT RUN",
            "first_party_namespace_root": ROOT,
            "first_party_namespace_root_inode":
                REPOSITORY_ROOT_INODE,
            "first_party_namespace_directory_inode":
                CANDIDATE_NAMESPACE_INODE,
            "first_party_namespace_is_pep_420": True,
            "historical_v6_failure_cause": "NOT ESTABLISHED",
            "historical_v6_infrastructure_failure_count": 13,
            "historical_v6_stderr_bytes": 106,
            "historical_v6_stderr_sha256":
                "0eae62828a696afbaaaa1212c0979f0b"
                "86afe95f59d1870f3ad0dea7fe2c08b7",
            "synthetic_pretry_bootstrap_control":
                "PASS" if mode == "--self-test" else "NOT RUN",
            "synthetic_literal_stderr_publication_control":
                "PASS" if mode == "--self-test" else "NOT RUN",
            "independent_worker_canonical_control":
                "PASS" if mode == "--self-test" else "NOT RUN",
            "worker_error_message_limit_bytes":
                MAX_FAILURE_MESSAGE_BYTES,
            "worker_traceback_limit_bytes":
                MAX_FAILURE_TRACEBACK_BYTES,
            "worker_traceback_frame_limit":
                MAX_FAILURE_TRACEBACK_FRAMES,
            "literal_stderr_excerpt_limit_bytes":
                MAX_PUBLIC_STDERR_BYTES,
            "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "maximum_serial_worker_timeout_seconds":
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
            "all_original_suites_attempted_after_timeout": True,
            "timeout_classification": "INFRASTRUCTURE FAILURE",
            "original_crosswalk_count": 34, "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_candidate_matching": "NOT RUN",
            "holdout_case_count": 14155776,
            "holdout_case_status":
                "PROPOSED; NOT FROZEN; NOT GENERATED; NOT OPENED",
            "historical_holdout_case_count": 4194304,
            "minimum_qualified_candidates": 3,
            "current_qualified_candidates": 0,
            "expanded_proposal_verifier_executed": False,
            "historical_zig_mismatch_count": 1764,
            "v13_actual_build_process_count": 26,
            "guard_clean_adapter_sha256": CLEAN_ADAPTER[1],
            "guard_clean_adapter_bytes": CLEAN_ADAPTER[2],
            "complete_matching_ast_unchanged": True,
            "v13_build_attests_guard_clean_adapter": False,
            "source_only_hostile_controls": checks,
            "source_only_effects": {name: 0 for name in ZERO_KEYS},
            "candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }


class CriticalSignals:
    """Block termination while the exact durable recovery state changes."""

    def __init__(self):
        self.signal = None
        self.previous = None

    def __enter__(self):
        self.signal = __import__("signal")
        require(callable(getattr(self.signal, "pthread_sigmask", None)),
                "require real POSIX recovery signal masking")
        mask = {
            getattr(self.signal, name)
            for name in ("SIGINT", "SIGTERM", "SIGHUP")
            if hasattr(self.signal, name)
        }
        require(bool(mask), "require independently real controller signals")
        self.previous = self.signal.pthread_sigmask(
            self.signal.SIG_BLOCK, mask)
        return self

    def __exit__(self, kind, value, trace):
        require(self.signal is not None and self.previous is not None,
                "reject a fabricated recovery signal state")
        self.signal.pthread_sigmask(
            self.signal.SIG_SETMASK, self.previous)
        return False


def private_owner(owner, role):
    expected = (PARENT_ADAPTER[1:3] if role == "adapter" else NATIVE[role])
    require(type(owner) is dict and type(owner.get("path")) is str
            and owner["path"].startswith(
                "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-")
            and "/reference-a/" in owner["path"]
            and owner.get("device") == PRIVATE_DEVICE
            and owner.get("uid") == os.geteuid()
            and owner.get("nlink") == 1
            and owner.get("sha256") == expected[0]
            and owner.get("bytes") == expected[1]
            and owner.get("mode") in ("0600", "0700"),
            "reject a crossed V13 actual private snapshot: " + role)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(owner["path"], flags)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == owner["device"]
                and info.st_ino == owner["inode"]
                and info.st_uid == owner["uid"] and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == int(owner["mode"], 8)
                and info.st_size == expected[1],
                "reject changed actual private V13 inode")
        parts, left = [], info.st_size
        while left:
            part = os.read(fd, min(left, 262144))
            require(bool(part), "reject truncated private V13 output")
            parts.append(part)
            left -= len(part)
        raw = b"".join(parts)
        require(not os.read(fd, 1) and digest(raw) == expected[0],
                "reject modified genuine private V13 native bytes")
        return raw
    finally:
        os.close(fd)


def target_identity(role, expected):
    path = ROOT + "/" + ORIGINALS[role]["relative"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(path, flags)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == expected["device"]
                and info.st_ino == expected["inode"]
                and info.st_uid == expected["uid"]
                and info.st_nlink == expected["nlink"]
                and stat.S_IMODE(info.st_mode) == expected["mode"]
                and info.st_size == expected["bytes"],
                "reject a changed exact canonical Zig " + role)
        state, left = hashlib.sha256(), info.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject truncated canonical role")
            state.update(data)
            left -= len(data)
        require(not os.read(fd, 1) and state.hexdigest() == expected["sha256"],
                "reject changed complete canonical role bytes")
        return dict(expected)
    finally:
        os.close(fd)


def exclusive(directory, name, data):
    require(type(name) is str and "/" not in name and name not in ("", ".", ".."),
            "reject a nonlocal exclusive owner")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    fd = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        pending = memoryview(data)
        while pending:
            wrote = os.write(fd, pending)
            require(type(wrote) is int and wrote > 0,
                    "reject incomplete durable stage")
            pending = pending[wrote:]
        os.fsync(fd)
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_uid == os.geteuid() and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == 0o600
                and info.st_size == len(data),
                "reject an unsafe staged owner")
        result = {"name": name, "sha256": digest(data),
                  "bytes": info.st_size, "device": info.st_dev,
                  "inode": info.st_ino, "mode": 0o600,
                  "uid": info.st_uid, "nlink": info.st_nlink}
    finally:
        os.close(fd)
    os.fsync(directory)
    return result


def recovery_directory(create):
    require(os.path.dirname(RECOVERY) == "/tmp"
            and RECOVERY.startswith("/tmp/rebar-phase2-repaired-zig-"),
            "reject an unsafe recovery-root target")
    if create:
        try:
            os.mkdir(RECOVERY, 0o700)
        except FileExistsError:
            pass
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(RECOVERY, flags)
    try:
        info = os.fstat(directory)
        require(stat.S_ISDIR(info.st_mode)
                and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "reject a shared or substituted recovery root")
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT
        lock = os.open("campaign-v8.lock", flags, 0o600, dir_fd=directory)
        try:
            owner = os.fstat(lock)
            require(stat.S_ISREG(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o600
                    and owner.st_uid == os.geteuid()
                    and owner.st_nlink == 1,
                    "reject a foreign recovery lock")
            fcntl = __import__("fcntl")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(lock)
            raise
        return directory, lock
    except BaseException:
        os.close(directory)
        raise


def names(role):
    require(role in ROLES, "reject a crossed activation role")
    stem = ".rebar-zig-guard-clean-v8-" + role
    return stem + ".stage", stem + ".original"


def candidate_directory():
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    fd = os.open(ROOT + "/candidates", flags)
    info = os.fstat(fd)
    require(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
            and info.st_uid == os.geteuid(),
            "reject a substituted candidates directory")
    return fd


def prepare(state):
    for role in ROLES:
        target_identity(role, ORIGINALS[role])
    phase = state["build"]["complete_actual_build"]["build_phases"][0]
    data = {}
    for role in ROLES:
        if role == "adapter":
            actual = private_owner(
                phase["source_snapshots"]["candidates/zig_candidate.py"], role)
            data[role] = normalize(actual)
            require(data[role] == read_owner(CLEAN_ADAPTER),
                    "reject altered guard-clean adapter provenance")
        else:
            data[role] = private_owner(
                phase["native_outputs"][role]["owner"], role)
    recovery_fd, lock_fd = recovery_directory(True)
    candidate_fd = candidate_directory()
    journal = None
    stages = {}
    try:
        for role in ROLES:
            stage, _ = names(role)
            stages[role] = exclusive(candidate_fd, stage, data[role])
            expected = CLEAN_ADAPTER[1] if role == "adapter" else NATIVE[role][0]
            require(stages[role]["device"] == DEVICE
                    and stages[role]["sha256"] == expected,
                    "require exact mode-0600 repository-device native stages")
        producer = state["producer"]
        journal = {
            "schema": SCHEMA + "-three-role-journal", "status": "PREPARED",
            "family": FAMILY, "label": LABEL, "build_label": BUILD_LABEL,
            "build_receipt_sha256": V13[3][1],
            "root_receipt_sha256": V13[4][1],
            "recovery_root": RECOVERY, "role_order": list(ROLES),
            "restoration_order": list(RESTORE), "atomic_group": False,
            "guard_clean_adapter_sha256": CLEAN_ADAPTER[1],
            "roles": {
                role: {"original": ORIGINALS[role],
                       "stage": stages[role], "backup_name": names(role)[1],
                       "stage_name": names(role)[0]}
                for role in ROLES
            },
        }
        with CriticalSignals():
            journal_owner = exclusive(
                recovery_fd, "recovery-journal.json",
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
                exclusive(recovery_fd, "activation-" + role + ".json",
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
                with CriticalSignals():
                    restore(candidate_fd, journal)
            for role, stage in stages.items():
                stage_name, _backup = names(role)
                try:
                    info = os.stat(stage_name, dir_fd=candidate_fd,
                                   follow_symlinks=False)
                except FileNotFoundError:
                    continue
                require(info.st_dev == stage["device"]
                        and info.st_ino == stage["inode"]
                        and stat.S_IMODE(info.st_mode) == 0o600
                        and info.st_uid == os.geteuid()
                        and info.st_nlink == 1,
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
            raise CampaignError(
                "actual activation failed and exact three-role recovery "
                "requires the published recovery journal: "
                + type(recovery_failure).__qualname__ + ": "
                + str(recovery_failure)
            ) from primary
        raise


def restore(candidate_fd, journal):
    require(journal.get("schema") == SCHEMA + "-three-role-journal"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("role_order") == list(ROLES)
            and journal.get("restoration_order") == list(RESTORE)
            and set(journal.get("roles", {})) == set(ROLES),
            "reject unauthenticated three-role recovery")
    result = []
    for role in RESTORE:
        entry = journal["roles"][role]
        _, backup = names(role)
        require(entry["original"] == ORIGINALS[role]
                and entry["backup_name"] == backup,
                "reject crossed original backup identity")
        try:
            info = os.stat(backup, dir_fd=candidate_fd, follow_symlinks=False)
        except FileNotFoundError:
            result.append(target_identity(role, ORIGINALS[role]))
            continue
        original = ORIGINALS[role]
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == original["device"]
                and info.st_ino == original["inode"]
                and info.st_uid == original["uid"]
                and stat.S_IMODE(info.st_mode) == original["mode"],
                "reject a substituted exact original-inode hardlink")
        os.replace(backup, original["relative"].rsplit("/", 1)[1],
                   src_dir_fd=candidate_fd, dst_dir_fd=candidate_fd)
        os.fsync(candidate_fd)
        result.append(target_identity(role, original))
    require(len(result) == 3,
            "require exact restoration of all three original source/native owners")
    for role in ROLES:
        stage_name, _backup = names(role)
        try:
            actual = os.stat(stage_name, dir_fd=candidate_fd,
                             follow_symlinks=False)
        except FileNotFoundError:
            continue
        stage = journal["roles"][role]["stage"]
        require(stat.S_ISREG(actual.st_mode)
                and actual.st_dev == stage["device"]
                and actual.st_ino == stage["inode"]
                and actual.st_uid == stage["uid"]
                and actual.st_nlink == 1
                and stat.S_IMODE(actual.st_mode) == 0o600
                and actual.st_size == stage["bytes"],
                "refuse to remove an unrelated user-owned recovery stage")
        os.unlink(stage_name, dir_fd=candidate_fd)
        os.fsync(candidate_fd)
    return result


def active_owner(role, staged):
    expected_hash, expected_size = (
        (CLEAN_ADAPTER[1], CLEAN_ADAPTER[2])
        if role == "adapter" else NATIVE[role]
    )
    expected = {
        "relative": ORIGINALS[role]["relative"], "sha256": expected_hash,
        "bytes": expected_size, "device": DEVICE,
        "inode": staged["inode"], "mode": 0o600,
        "uid": os.geteuid(), "nlink": 1,
    }
    target_identity(role, expected)
    return {"family": FAMILY, "role": role,
            "absolute_path": ROOT + "/" + expected["relative"], **expected}


def read_live_journal(producer, expected_sha):
    expected_sha = pin(expected_sha, "recovery journal")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(RECOVERY, flags)
    try:
        root = os.fstat(directory)
        require(stat.S_ISDIR(root.st_mode)
                and stat.S_IMODE(root.st_mode) == 0o700
                and root.st_uid == os.geteuid(),
                "reject a substituted read-only actual recovery root")
        file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                      | getattr(os, "O_NOFOLLOW", 0))
        fd = os.open("recovery-journal.json", file_flags, dir_fd=directory)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o600
                    and info.st_uid == os.geteuid()
                    and info.st_nlink == 1
                    and 0 < info.st_size < MAX_BYTES,
                    "reject an unsafe original three-role journal")
            pieces, left = [], info.st_size
            while left:
                chunk = os.read(fd, min(left, 262144))
                require(bool(chunk), "reject a truncated live journal")
                pieces.append(chunk)
                left -= len(chunk)
            raw = b"".join(pieces)
            require(not os.read(fd, 1) and digest(raw) == expected_sha,
                    "reject an unannounced actual three-role journal")
        finally:
            os.close(fd)
    finally:
        os.close(directory)
    journal = producer.JsonReader(raw).parse()
    require(journal.get("schema") == SCHEMA + "-three-role-journal"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("build_receipt_sha256") == V13[3][1]
            and journal.get("root_receipt_sha256") == V13[4][1]
            and journal.get("guard_clean_adapter_sha256") == CLEAN_ADAPTER[1]
            and journal.get("role_order") == list(ROLES)
            and journal.get("restoration_order") == list(RESTORE)
            and set(journal.get("roles", {})) == set(ROLES),
            "reject fabricated or crossed actual activation")
    return journal


def authenticated_first_party_namespace(path=ROOT):
    require(
        type(path) is str
        and path == ROOT
        and path == "/home/dev-user/src/rebar"
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1,
        "reject an unpinned, relative, environment-derived, or "
        "non-isolated first-party package root",
    )
    root = os.stat(path, follow_symlinks=False)
    namespace_path = path + "/candidates"
    namespace = os.stat(namespace_path, follow_symlinks=False)
    adapter_path = namespace_path + "/zig_candidate.py"
    adapter = os.stat(adapter_path, follow_symlinks=False)
    uid = os.geteuid()
    require(
        stat.S_ISDIR(root.st_mode)
        and root.st_dev == DEVICE
        and root.st_ino == REPOSITORY_ROOT_INODE
        and stat.S_IMODE(root.st_mode) == REPOSITORY_ROOT_MODE
        and root.st_uid == uid
        and stat.S_ISDIR(namespace.st_mode)
        and namespace.st_dev == DEVICE
        and namespace.st_ino == CANDIDATE_NAMESPACE_INODE
        and stat.S_IMODE(namespace.st_mode) == CANDIDATE_NAMESPACE_MODE
        and namespace.st_uid == uid
        and stat.S_ISREG(adapter.st_mode)
        and adapter.st_dev == DEVICE
        and stat.S_IMODE(adapter.st_mode) == 0o600
        and adapter.st_uid == uid
        and adapter.st_nlink == 1,
        "reject a substituted, symlinked, foreign, or unowned "
        "first-party namespace",
    )
    finder = importlib._bootstrap_external.PathFinder
    require(
        finder in sys.meta_path
        and finder.__module__ == "_frozen_importlib_external"
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject a replaced finder or preloaded matching package",
    )
    package = finder.find_spec("candidates", [path])
    require(
        package is not None
        and package.name == "candidates"
        and package.loader is None
        and package.origin is None
        and tuple(package.submodule_search_locations or ())
        == (namespace_path,),
        "reject a foreign or noncanonical PEP 420 namespace",
    )
    candidate = finder.find_spec(
        "candidates.zig_candidate", [namespace_path]
    )
    require(
        candidate is not None
        and candidate.name == "candidates.zig_candidate"
        and candidate.origin == adapter_path
        and type(candidate.loader).__module__
        == "_frozen_importlib_external"
        and type(candidate.loader).__name__ == "SourceFileLoader"
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules,
        "reject a crossed candidate source without importing it",
    )
    return {
        "root": path,
        "namespace": namespace_path,
        "adapter": adapter_path,
        "root_inode": root.st_ino,
        "namespace_inode": namespace.st_ino,
    }


def prepend_authenticated_first_party_namespace(owner):
    require(
        type(owner) is dict
        and owner.get("root") == ROOT
        and owner.get("namespace") == ROOT + "/candidates"
        and owner.get("adapter") == ROOT + "/candidates/zig_candidate.py"
        and owner.get("root_inode") == REPOSITORY_ROOT_INODE
        and owner.get("namespace_inode") == CANDIDATE_NAMESPACE_INODE
        and type(sys.path) is list
        and all(type(item) is str for item in sys.path)
        and ROOT not in sys.path
        and "" not in sys.path
        and "." not in sys.path
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject a duplicate, relative, preloaded, or foreign package path",
    )
    before = tuple(sys.path)
    sys.path.insert(0, ROOT)
    require(
        sys.path[0] == ROOT
        and tuple(sys.path[1:]) == before,
        "prepend only the exact authenticated repository root",
    )
    finder = importlib._bootstrap_external.PathFinder
    package = finder.find_spec("candidates", None)
    require(
        package is not None
        and package.name == "candidates"
        and package.loader is None
        and package.origin is None
        and tuple(package.submodule_search_locations or ())
        == (ROOT + "/candidates",)
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject first-party namespace resolution or a guard bypass",
    )
    return owner


def bounded_literal(value, maximum):
    require(type(maximum) is int and maximum > 0,
            "reject an unbounded diagnostic excerpt")
    if type(value) is str:
        raw = value.encode("utf-8", "backslashreplace")
    else:
        require(type(value) is bytes,
                "reject a fabricated nonliteral diagnostic excerpt")
        raw = value
    captured = raw[:maximum]
    return {
        "text": captured.decode("utf-8", "backslashreplace"),
        "total_bytes": len(raw),
        "captured_bytes": len(captured),
        "limit_bytes": maximum,
        "truncated": len(raw) > maximum,
        "sha256": digest(raw),
        "encoding": "UTF-8; INVALID BYTES BACKSLASH-ESCAPED",
    }


def literal_stderr(value, reason=None):
    if value is None:
        require(type(reason) is str and bool(reason),
                "require a genuine reason for unavailable worker stderr")
        return {
            "status": "NOT AVAILABLE",
            "reason": bounded_literal(reason, MAX_FAILURE_MESSAGE_BYTES),
            "text": None,
            "total_bytes": "NOT MEASURED",
            "captured_bytes": 0,
            "limit_bytes": MAX_PUBLIC_STDERR_BYTES,
            "truncated": "NOT MEASURED",
            "sha256": "NOT MEASURED",
            "encoding": "NOT MEASURED",
        }
    require(type(value) is bytes,
            "preserve only genuine complete captured worker stderr")
    return {
        "status": "CAPTURED",
        **bounded_literal(value, MAX_PUBLIC_STDERR_BYTES),
    }


def failure_details(error, stage):
    require(isinstance(error, BaseException)
            and type(stage) is str and bool(stage),
            "capture only genuine stage-attributed exceptions")
    kind = type(error)
    qualified = kind.__module__ + "." + kind.__qualname__
    try:
        message = str(error)
    except BaseException as secondary:
        other = type(secondary)
        message = (
            "<exception string failed: "
            + other.__module__ + "." + other.__qualname__ + ">"
        )
    bounded_message = bounded_literal(
        message, MAX_FAILURE_MESSAGE_BYTES
    )
    frames = []
    trace = error.__traceback__
    while trace is not None and len(frames) < MAX_FAILURE_TRACEBACK_FRAMES:
        frame = trace.tb_frame
        frames.append({
            "file": bounded_literal(
                frame.f_code.co_filename, MAX_FAILURE_MESSAGE_BYTES
            )["text"],
            "function": bounded_literal(
                frame.f_code.co_name, MAX_FAILURE_MESSAGE_BYTES
            )["text"],
            "line": trace.tb_lineno,
        })
        trace = trace.tb_next
    lines = ["Traceback (most recent call last):"]
    for frame in frames:
        lines.append(
            '  File "' + frame["file"] + '", line '
            + str(frame["line"]) + ", in " + frame["function"]
        )
    if trace is not None:
        lines.append("  ... additional traceback frames omitted")
    lines.append(qualified + ": " + bounded_message["text"])
    return {
        "activation_stage": stage,
        "error_type": kind.__qualname__,
        "error_class": qualified,
        "error_message": bounded_message["text"],
        "error_message_detail": bounded_message,
        "error_traceback": bounded_literal(
            "\n".join(lines), MAX_FAILURE_TRACEBACK_BYTES
        ),
        "traceback_frames": frames,
        "traceback_frames_truncated": trace is not None,
    }


def worker_quote(value):
    require(type(value) is str, "quote only canonical worker strings")
    output = ['"']
    escapes = {
        "\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f",
        "\n": "\\n", "\r": "\\r", "\t": "\\t",
    }
    for character in value:
        if character in escapes:
            output.append(escapes[character])
        elif ord(character) < 32:
            output.append("\\u" + format(ord(character), "04x"))
        elif ord(character) > 127:
            point = ord(character)
            if point <= 0xffff:
                output.append("\\u" + format(point, "04x"))
            else:
                point -= 0x10000
                output.append(
                    "\\u" + format(0xd800 + (point >> 10), "04x")
                )
                output.append(
                    "\\u" + format(0xdc00 + (point & 0x3ff), "04x")
                )
        else:
            output.append(character)
    output.append('"')
    return "".join(output)


def worker_canonical(value):
    def encode(item, depth):
        require(depth <= 64, "reject excessive canonical worker nesting")
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if type(item) is str:
            return worker_quote(item)
        if type(item) in (tuple, list):
            return "[" + ",".join(
                encode(child, depth + 1) for child in item
            ) + "]"
        if type(item) is dict:
            require(all(type(key) is str for key in item),
                    "reject noncanonical actual worker keys")
            return "{" + ",".join(
                worker_quote(key) + ":" + encode(item[key], depth + 1)
                for key in sorted(item)
            ) + "}"
        raise CampaignError(
            "reject unsupported actual worker evidence: "
            + type(item).__name__
        )
    return (encode(value, 0) + "\n").encode("ascii")


def worker(args, *, bootstrap_hook=None):
    stage = "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
    suite_name = None
    suite_count = None
    installed = False
    imported = False
    synthetic = bootstrap_hook is not None
    try:
        require(type(args) is dict,
                "reject noncanonical worker bootstrap arguments")
        suite_name = args.get("--suite")
        suite_count = dict(SUITES).get(suite_name)
        if bootstrap_hook is not None:
            require(callable(bootstrap_hook),
                    "reject a noncallable source-only bootstrap control")
            bootstrap_hook()
        stage = "VERIFY_ACTIVE_FROZEN_CONTEXT"
        state = verify(args["--source-sha256"], args["--protocol-sha256"],
                       args["--contract-sha256"], active=True)
        producer = state["producer"]
        stage = "VALIDATE_PINNED_WORKER_AUTHORITY"
        require(args.get("--family") == FAMILY
                and args.get("--label") == LABEL
                and args.get("--suite") in dict(SUITES)
                and args.get("--build-receipt-sha256") == V13[3][1]
                and args.get("--root-receipt-sha256") == V13[4][1]
                and args.get("--producer-source-sha256") == PRODUCER[0][1]
                and args.get("--guard-source-sha256") == GUARD[0][1]
                and args.get("--adapter-sha256") == CLEAN_ADAPTER[1],
                "require independent actual worker and build authority")
        stage = "READ_AUTHENTICATED_ACTIVE_RECOVERY_JOURNAL"
        journal = read_live_journal(
            producer, args["--recovery-journal-sha256"]
        )
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_ENGINE"
        engine = active_owner(
            "engine", journal["roles"]["engine"]["stage"]
        )
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_BRIDGE"
        bridge = active_owner(
            "bridge", journal["roles"]["bridge"]["stage"]
        )
        stage = "AUTHENTICATE_ACTIVE_GUARD_CLEAN_ADAPTER"
        active_owner("adapter", journal["roles"]["adapter"]["stage"])
        stage = "VERIFY_CLEAN_PRE_GUARD_MODULE_STATE"
        clean()
        stage = "LOAD_IMMUTABLE_FIRST_PARTY_RUNTIME_GUARD"
        guard = load(GUARD[0], "_rebar_zig_v5_immutable_guard")
        stage = "CONSTRUCT_IMMUTABLE_RUNTIME_POLICY"
        policy = guard.RuntimePolicy()
        stage = "INSTALL_IMMUTABLE_RUNTIME_GUARD"
        policy.install()
        installed = True
        stage = "PREPARE_AUTHENTICATED_FIRST_PARTY_NATIVE_FAMILY"
        policy.prepare_family(
            FAMILY, bridge_owner=bridge, engine_owner=engine
        )
        stage = "AUTHENTICATE_GUARDED_FIRST_PARTY_NAMESPACE"
        namespace = authenticated_first_party_namespace()
        stage = "PREPEND_AUTHENTICATED_ISOLATED_FIRST_PARTY_ROOT"
        prepend_authenticated_first_party_namespace(namespace)
        stage = "VERIFY_RUNTIME_GUARD_BEFORE_CANDIDATE_IMPORT"
        require(
            installed
            and policy.installed
            and policy.prepared_family == FAMILY
            and sys.path[0] == ROOT
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "require genuine strict guard and authenticated namespace "
            "before the sole first-party candidate import",
        )
        stage = "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE"
        candidate = importlib.import_module("candidates.zig_candidate")
        imported = True
        stage = "BIND_SELECTED_FIRST_PARTY_CANDIDATE"
        policy.bind_selected(candidate, FAMILY)
        stage = "BUILD_IMMUTABLE_FIRST_PARTY_FAMILY_SPEC"
        base = producer.family_spec(FAMILY)
        source_owners = (
            (ORIGINAL_ADAPTER[0], CLEAN_ADAPTER[1], CLEAN_ADAPTER[2]),
            (ENGINE_SOURCE[0], ENGINE_SOURCE[1], ENGINE_SOURCE[2]),
            (BRIDGE_SOURCE[0], BRIDGE_SOURCE[1], BRIDGE_SOURCE[2]),
        )
        selected = producer.FamilySpec(
            base.name, base.module, base.adapter_relative,
            base.bridge_module, base.engine_relative,
            base.bridge_relative, source_owners, False, False,
        )
        stage = "VERIFY_GUARDED_FIRST_PARTY_FAMILY_IDENTITY"
        require(producer.family_spec(FAMILY) is base
                and base.owned_ctypes is True
                and selected.owned_ctypes is False
                and producer.require_selected(selected) is candidate
                and policy.selected is candidate
                and sys.modules.get("re") is candidate,
                "preserve the immutable producer and exact first-party alias")
        pins = {
            "source": CLEAN_ADAPTER[1],
            "native_engine": NATIVE["engine"][0],
            "native_bridge": NATIVE["bridge"][0],
        }
        source_pins = {
            path: value for path, value, _ in source_owners
        }
        stage = "RESOLVE_IMMUTABLE_ORIGINAL_SUITE"
        suite = producer.suite_spec(args["--suite"])
        suite_name, suite_count = suite.name, suite.case_count
        if suite.name == "original_bounded_v5":
            stage = "OBSERVE_COMPLETE_UPSTREAM_ORIGINAL_SUITE"
            observation = producer.observe_original_upstream(
                suite, selected, pins, source_pins
            )
        elif suite.name == "subinterpreter_v2":
            stage = "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
            observation = producer.observe_subinterpreters(
                suite, selected, pins, source_pins,
                producer_sha256=PRODUCER[0][1],
            )
        else:
            stage = "OBSERVE_COMPLETE_DIRECT_ORIGINAL_SUITE"
            observation = producer.observe_direct_suite(
                suite, selected, pins, source_pins, state["manifest"]
            )
        stage = "VALIDATE_COMPLETE_ORIGINAL_SUITE_OBSERVATION"
        require(type(observation) is dict
                and observation.get("suite") == suite.name
                and observation.get("candidate_family") == FAMILY
                and observation.get("case_execution_denominator")
                == suite.case_count
                and observation.get("actual_candidate_workers") == 1
                and observation.get("hidden_cases_read") == 0
                and observation.get("benchmark_files_read") == 0
                and observation.get("holdout") == "NOT OPENED",
                "reject omitted or fabricated genuine original records")
        return {
            "schema": SCHEMA + "-actual-suite-worker",
            "status": observation.get("status"),
            "family": FAMILY,
            "label": LABEL,
            "suite": suite.name,
            "case_execution_denominator": suite.case_count,
            "complete_actual_observation": observation,
            "activation_stage": "COMPLETE_ORIGINAL_OBSERVATION",
            "guard_installed_before_candidate_import": True,
            "candidate_imported": True,
            "actual_candidate_workers": 1,
            "synthetic_control": False,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }
    except BaseException as error:
        details = getattr(error, "details", None)
        return {
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "family": FAMILY,
            "label": LABEL,
            "suite": suite_name,
            "case_execution_denominator": suite_count,
            **failure_details(error, stage),
            "complete_actual_suite_failure_details": details,
            "guard_installed_before_candidate_import": installed,
            "candidate_imported": imported,
            "actual_candidate_workers": 0 if synthetic else 1,
            "synthetic_control": synthetic,
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }

def stream(raw, maximum):
    require(type(raw) is bytes and len(raw) <= maximum,
            "reject omitted or unbounded actual worker output")
    base64 = __import__("base64")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "bytes": len(raw), "sha256": digest(raw), "complete": True}


def command(args, suite, journal_sha):
    options = ["--source-sha256", "--protocol-sha256", "--contract-sha256"]
    argv = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SELF, "--worker"]
    for key in options:
        argv.extend((key, args[key]))
    for key, value in (
            ("--family", FAMILY), ("--label", LABEL), ("--suite", suite),
            ("--build-receipt-sha256", V13[3][1]),
            ("--root-receipt-sha256", V13[4][1]),
            ("--producer-source-sha256", PRODUCER[0][1]),
            ("--guard-source-sha256", GUARD[0][1]),
            ("--adapter-sha256", CLEAN_ADAPTER[1]),
            ("--recovery-journal-sha256", journal_sha)):
        argv.extend((key, value))
    return argv


def public_literal_stderr(row):
    require(type(row) is dict,
            "reject a fabricated worker literal-stderr row")
    excerpt = row.get("stderr_literal_excerpt")
    require(type(excerpt) is dict
            and excerpt.get("limit_bytes") == MAX_PUBLIC_STDERR_BYTES,
            "reject omitted or unbounded worker literal stderr")
    owner = row.get("stderr")
    if excerpt.get("status") == "NOT AVAILABLE":
        require(owner is None
                and excerpt.get("text") is None
                and excerpt.get("total_bytes") == "NOT MEASURED"
                and excerpt.get("captured_bytes") == 0
                and excerpt.get("sha256") == "NOT MEASURED"
                and type(excerpt.get("reason")) is dict,
                "reject invented unavailable actual worker stderr")
        return excerpt
    require(excerpt.get("status") == "CAPTURED"
            and type(owner) is dict
            and type(excerpt.get("text")) is str
            and type(excerpt.get("total_bytes")) is int
            and type(excerpt.get("captured_bytes")) is int
            and 0 <= excerpt["captured_bytes"]
            <= min(MAX_PUBLIC_STDERR_BYTES, excerpt["total_bytes"])
            and excerpt.get("truncated")
            is (excerpt["total_bytes"] > MAX_PUBLIC_STDERR_BYTES)
            and excerpt["total_bytes"] == owner.get("bytes")
            and excerpt.get("sha256") == owner.get("sha256")
            and owner.get("complete") is True,
            "reject omitted, altered, unbounded, or crossed literal stderr")
    return excerpt


def public_stream_owner(value):
    if value is None:
        return None
    require(type(value) is dict
            and type(value.get("bytes")) is int
            and value["bytes"] >= 0
            and value.get("complete") is True,
            "reject an incomplete public worker stream identity")
    return {
        "bytes": value["bytes"],
        "sha256": pin(value.get("sha256"), "complete worker stream"),
        "complete": True,
        "complete_payload_preserved_in_actual_archive": True,
    }


def public_campaign_diagnostics(report):
    rows = report.get("complete_original_suite_workers")
    require(type(rows) is list and len(rows) == len(SUITES)
            and all(type(row) is dict for row in rows)
            and tuple(
                (row.get("suite"), row.get("case_execution_denominator"))
                for row in rows
            ) == SUITES,
            "reject omitted, reordered, or miscounted public suite diagnostics")
    require(all(row.get("timed_out") is True
                or row.get("timed_out") is False for row in rows)
            and all(row.get("timeout_seconds") == SUITE_TIMEOUT_SECONDS
                    for row in rows)
            and all(
                row.get("timeout_classification")
                == ("INFRASTRUCTURE FAILURE"
                    if row["timed_out"] else "NOT TIMED OUT")
                for row in rows
            )
            and all(
                not row["timed_out"]
                or (row.get("status") == "FAIL"
                    and row.get("infrastructure_failure") is True)
                for row in rows
            ),
            "reject an omitted, weakened, or falsely passing suite timeout")
    timed_out = [
        row["suite"] for row in rows if row["timed_out"]
    ]
    infrastructure = [
        row["suite"] for row in rows
        if row.get("infrastructure_failure") is True
    ]
    failures = [
        row["suite"] for row in rows if row.get("status") != "PASS"
    ]
    require(report.get("case_execution_denominator") == 31237
            and report.get("suite_count") == 13
            and report.get("all_original_suites_attempted") is True
            and report.get("per_suite_timeout_seconds")
            == SUITE_TIMEOUT_SECONDS
            and report.get("maximum_serial_worker_timeout_seconds")
            == MAX_SERIAL_SUITE_TIMEOUT_SECONDS
            and report.get("timeout_classification")
            == "INFRASTRUCTURE FAILURE"
            and report.get("timeout_count") == len(timed_out)
            and report.get("timed_out_suites") == timed_out
            and report.get("infrastructure_failure_count")
            == len(infrastructure)
            and report.get("infrastructure_failure_suites")
            == infrastructure
            and report.get("failed_suites") == failures,
            "reject inconsistent public timeout, failure, or suite totals")
    diagnostics = []
    for row in rows:
        worker = row.get("complete_actual_worker")
        if type(worker) is not dict:
            worker = {}
        observation = worker.get("complete_actual_observation")
        if type(observation) is not dict:
            observation = {}
        mismatch_count = observation.get("mismatch_count")
        if type(mismatch_count) is not int:
            mismatch_count = "NOT MEASURED"
        diagnostics.append({
            "suite": row["suite"],
            "case_execution_denominator":
                row["case_execution_denominator"],
            "status": row.get("status"),
            "infrastructure_failure":
                row.get("infrastructure_failure") is True,
            "pid": row.get("pid"),
            "returncode": row.get("returncode"),
            "timed_out": row["timed_out"],
            "timeout_seconds": row["timeout_seconds"],
            "timeout_classification": row["timeout_classification"],
            "error_type": row.get("error_type", worker.get("error_type")),
            "error_message":
                row.get("error_message", worker.get("error_message")),
            "actual_worker_schema": worker.get("schema"),
            "complete_actual_suite_failure_details":
                worker.get("complete_actual_suite_failure_details"),
            "observed_semantic_mismatch_count": mismatch_count,
            "activation_stage":
                row.get("activation_stage", worker.get("activation_stage")),
            "error_class":
                row.get("error_class", worker.get("error_class")),
            "error_message_detail":
                row.get("error_message_detail",
                        worker.get("error_message_detail")),
            "error_traceback":
                row.get("error_traceback", worker.get("error_traceback")),
            "traceback_frames":
                row.get("traceback_frames", worker.get("traceback_frames")),
            "traceback_frames_truncated":
                row.get("traceback_frames_truncated",
                        worker.get("traceback_frames_truncated")),
            "guard_installed_before_candidate_import":
                worker.get("guard_installed_before_candidate_import"),
            "candidate_imported": worker.get("candidate_imported"),
            "stdout": public_stream_owner(row.get("stdout")),
            "stderr": public_stream_owner(row.get("stderr")),
            "stderr_literal_excerpt": public_literal_stderr(row),
        })
    return {
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "unique_candidate_worker_count":
            report["unique_candidate_worker_count"],
        "completed_suite_count": report["completed_suite_count"],
        "verified_passing_case_count":
            report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "observed_semantic_mismatch_lower_bound":
            report["observed_semantic_mismatch_lower_bound"],
        "failed_suites": failures,
        "infrastructure_failure_count": len(infrastructure),
        "infrastructure_failure_suites": infrastructure,
        "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
        "maximum_serial_worker_timeout_seconds":
            MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
        "all_original_suites_attempted": True,
        "timeout_classification": "INFRASTRUCTURE FAILURE",
        "timeout_count": len(timed_out),
        "timed_out_suites": timed_out,
        "original_suite_diagnostics": diagnostics,
    }




def synthetic_first_party_namespace_controls():
    before = tuple(sys.path)
    marker = object()
    cache = sys.path_importer_cache.get(ROOT, marker)
    checks = 0
    try:
        require(
            ROOT not in sys.path
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "require an untouched isolated source-only namespace",
        )
        owner = authenticated_first_party_namespace()
        prepend_authenticated_first_party_namespace(owner)
        finder = importlib._bootstrap_external.PathFinder
        package = finder.find_spec("candidates", None)
        candidate = finder.find_spec(
            "candidates.zig_candidate", [ROOT + "/candidates"]
        )
        require(
            sys.path[0] == ROOT
            and tuple(sys.path[1:]) == before
            and package is not None
            and tuple(package.submodule_search_locations or ())
            == (ROOT + "/candidates",)
            and candidate is not None
            and candidate.origin
            == ROOT + "/candidates/zig_candidate.py"
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "reject an unimportable or imported first-party namespace",
        )
        checks += 1
        for name in (
            "re",
            "_sre",
            "ctypes",
            "candidates",
            "candidates.zig_candidate",
            "candidates.rust_candidate",
        ):
            checks += reject(
                lambda item=name: builtins.__import__(item),
                "namespace repair bypassed strict source guard: " + name,
            )
        checks += reject(
            lambda: authenticated_first_party_namespace(
                ROOT + "/candidates"
            ),
            "crossed canonical first-party repository root",
        )
        require(
            "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "reject side effects from namespace hostile controls",
        )
    finally:
        sys.path[:] = before
        if cache is marker:
            sys.path_importer_cache.pop(ROOT, None)
        else:
            sys.path_importer_cache[ROOT] = cache
    require(
        tuple(sys.path) == before
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "require complete source-only path and module restoration",
    )
    return checks + 1

def synthetic_evidence_controls(producer):
    def before_active_context():
        raise CampaignError(
            "synthetic PRE-TRY first-party bootstrap exception"
        )

    result = worker(
        {"--suite": SUITES[0][0]},
        bootstrap_hook=before_active_context,
    )
    require(
        result.get("schema") == SCHEMA + "-actual-worker-failure"
        and result.get("status") == "FAIL"
        and result.get("suite") == SUITES[0][0]
        and result.get("case_execution_denominator") == SUITES[0][1]
        and result.get("activation_stage")
        == "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
        and result.get("error_type") == "CampaignError"
        and result.get("error_class") == __name__ + ".CampaignError"
        and "synthetic PRE-TRY" in result.get("error_message", "")
        and result.get("guard_installed_before_candidate_import") is False
        and result.get("candidate_imported") is False
        and result.get("actual_candidate_workers") == 0
        and result.get("synthetic_control") is True
        and type(result.get("error_traceback")) is dict
        and result["error_traceback"].get("limit_bytes")
        == MAX_FAILURE_TRACEBACK_BYTES
        and "before_active_context"
        in result["error_traceback"].get("text", "")
        and len(result.get("traceback_frames", []))
        <= MAX_FAILURE_TRACEBACK_FRAMES
        and worker_canonical(result) == producer.canonical(result),
        "reject uncaught, fabricated, native-running, or "
        "noncanonical pre-context bootstrap exception",
    )
    sample = {
        "ascii": "first-party canonical evidence",
        "control": "\n\t\b",
        "nested": [None, True, False, -1, {"z": "quoted \" value"}],
    }
    require(worker_canonical(sample) == producer.canonical(sample),
            "reject producer-independent canonical worker serialization")
    require(
        worker_canonical({
            "unicode": "first-party \u00e9 \U0001f9ea",
        })
        == (
            b'{"unicode":"first-party '
            b'\\u00e9 \\ud83e\\uddea"}\n'
        ),
        "reject first-party Unicode escaping without lazy codec imports",
    )
    raw = (
        b"FIRST-PARTY SYNTHETIC STDERR: "
        b"visible before archive inflation\n"
    )
    excerpt = literal_stderr(raw)
    stderr = {
        "bytes": len(raw),
        "sha256": digest(raw),
        "complete": True,
    }
    rows = []
    for suite_name, case_count in SUITES:
        synthetic_failure = dict(result)
        synthetic_failure["suite"] = suite_name
        synthetic_failure["case_execution_denominator"] = case_count
        rows.append({
            "suite": suite_name,
            "case_execution_denominator": case_count,
            "status": "FAIL",
            "infrastructure_failure": True,
            "pid": None,
            "returncode": None,
            "timed_out": False,
            "timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "timeout_classification": "NOT TIMED OUT",
            "stderr": dict(stderr),
            "stderr_literal_excerpt": dict(excerpt),
            "complete_actual_worker": synthetic_failure,
        })
    suite_names = [name for name, _ in SUITES]
    report = {
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "all_original_suites_attempted": True,
        "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
        "maximum_serial_worker_timeout_seconds":
            MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
        "timeout_classification": "INFRASTRUCTURE FAILURE",
        "timeout_count": 0,
        "timed_out_suites": [],
        "infrastructure_failure_count": 13,
        "infrastructure_failure_suites": suite_names,
        "failed_suites": suite_names,
        "actual_candidate_workers": 0,
        "unique_candidate_worker_count": 0,
        "completed_suite_count": 0,
        "verified_passing_case_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "observed_semantic_mismatch_lower_bound": 0,
        "complete_original_suite_workers": rows,
    }
    visible = public_campaign_diagnostics(report)
    require(
        visible.get("semantic_mismatch_count") == "NOT MEASURED"
        and visible.get("actual_candidate_workers") == 0
        and visible.get("infrastructure_failure_count") == 13
        and len(visible.get("original_suite_diagnostics", [])) == 13
        and all(
            item.get("activation_stage")
            == "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
            and item.get("stderr_literal_excerpt", {}).get("status")
            == "CAPTURED"
            and "FIRST-PARTY SYNTHETIC STDERR"
            in item["stderr_literal_excerpt"].get("text", "")
            and item["stderr_literal_excerpt"].get("sha256")
            == digest(raw)
            for item in visible["original_suite_diagnostics"]
        ),
        "reject missing literal stderr or bootstrap stage for any suite",
    )
    for suffix in ("durable-publication-receipt", "published-actual-result"):
        fixture = {
            "schema": SCHEMA + "-" + suffix,
            "synthetic_control": True,
            **visible,
        }
        encoded = producer.canonical(fixture)
        parsed = producer.JsonReader(encoded).parse()
        require(
            parsed == fixture
            and b"FIRST-PARTY SYNTHETIC STDERR" in encoded
            and b"PRE_ACTIVE_CONTEXT_BOOTSTRAP" in encoded
            and len(parsed.get("original_suite_diagnostics", [])) == 13,
            "reject invisible literal stderr in synthetic public evidence",
        )
    oversized = literal_stderr(
        b"x" * (MAX_PUBLIC_STDERR_BYTES + 17)
    )
    require(
        oversized.get("truncated") is True
        and oversized.get("captured_bytes") == MAX_PUBLIC_STDERR_BYTES
        and oversized.get("total_bytes") == MAX_PUBLIC_STDERR_BYTES + 17,
        "reject unbounded actual literal-stderr publication",
    )
    crossed = dict(rows[0])
    crossed["stderr_literal_excerpt"] = dict(excerpt)
    crossed["stderr_literal_excerpt"]["sha256"] = digest(b"crossed")
    checks = reject(
        lambda: public_literal_stderr(crossed),
        "crossed actual literal stderr",
    )
    return checks + 4

def publish_campaign(report, producer):
    require(type(report) is dict
            and report.get("schema")
            == SCHEMA + "-complete-actual-original-campaign"
            and report.get("all_three_original_targets_restored") is True
            and report.get("candidate_qualified") is False
            and report.get("supplemental_candidate_matching") == "NOT RUN"
            and report.get("holdout") == "NOT OPENED",
            "refuse to publish an incomplete or falsely qualified campaign")
    diagnostics = public_campaign_diagnostics(report)
    for role in ROLES:
        target_identity(role, ORIGINALS[role])
    plain = producer.canonical(report)
    require(0 < len(plain) <= 256 * 1024 * 1024,
            "bound every actual retained original case and worker record")
    zlib = __import__("zlib")
    compressor = zlib.compressobj(
        9, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
    compressed = compressor.compress(plain) + compressor.flush()
    require(compressed[:3] == b"\x1f\x8b\x08"
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "require one reproducible zero-time gzip evidence member")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    restored = decoder.decompress(compressed, len(plain) + 1)
    restored += decoder.flush()
    require(decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail and restored == plain,
            "reject truncated, concatenated, or altered actual results")
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(ROOT + "/oracle/phase2/evidence", directory_flags)
    try:
        info = os.fstat(directory)
        require(stat.S_ISDIR(info.st_mode)
                and info.st_dev == DEVICE and info.st_uid == os.geteuid(),
                "reject a substituted actual evidence directory")
        suffix = "success" if report["original_campaign_passed"] else "failures"
        stem = "repaired-zig-original-campaign-v8-" + LABEL + "-" + suffix
        archive = exclusive(directory, stem + ".json.gz", compressed)
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": report["status"],
            "original_campaign_passed": report["original_campaign_passed"],
            "candidate_qualified": False,
            "family": FAMILY,
            "label": LABEL,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            **diagnostics,
            "archive": archive,
            "uncompressed_bytes": len(plain),
            "uncompressed_sha256": digest(plain),
            "all_three_original_targets_restored": True,
            "supplemental_candidate_matching": "NOT RUN",
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
        published = exclusive(
            directory, stem + "-publication-receipt.json",
            producer.canonical(receipt))
    finally:
        os.close(directory)
    return {"schema": SCHEMA + "-published-actual-result",
            "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": report["status"],
            "original_campaign_passed": report["original_campaign_passed"],
            "candidate_qualified": False,
            "family": FAMILY, "label": LABEL,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            **diagnostics,
            "archive": archive, "publication_receipt": published,
            "all_three_original_targets_restored": True,
            "supplemental_candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "winner_selected": False}


def campaign(args):
    state = verify(args["--source-sha256"], args["--protocol-sha256"],
                   args["--contract-sha256"])
    require(args.get("--family") == FAMILY and args.get("--label") == LABEL
            and args.get("--build-receipt-sha256") == V13[3][1]
            and args.get("--root-receipt-sha256") == V13[4][1]
            and args.get("--producer-source-sha256") == PRODUCER[0][1]
            and args.get("--guard-source-sha256") == GUARD[0][1]
            and args.get("--adapter-sha256") == CLEAN_ADAPTER[1],
            "reject an unauthorized actual native activation")
    require(os.environ.get("LOCPATH") == EXTERNAL_LOCPATH,
            "require the exact independently provisioned original locale "
            "before any native replacement")
    subprocess = __import__("subprocess")
    producer = state["producer"]
    recovery_fd = lock_fd = candidate_fd = None
    rows, restored, primary = [], None, None
    try:
        recovery_fd, lock_fd, candidate_fd, journal = prepare(state)
        journal_sha = journal["published_journal"]["sha256"]
        env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C",
               "LOCPATH": os.environ["LOCPATH"],
               "PYTHONDONTWRITEBYTECODE": "1"}
        for name, count in SUITES:
            try:
                child = subprocess.Popen(
                    command(args, name, journal_sha),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, cwd=ROOT, env=env)
                timeout = False
                try:
                    stdout, stderr = child.communicate(timeout=SUITE_TIMEOUT_SECONDS)
                except subprocess.TimeoutExpired:
                    timeout = True
                    child.kill()
                    stdout, stderr = child.communicate()
                row = {"suite": name, "case_execution_denominator": count,
                       "pid": child.pid, "returncode": child.returncode,
                       "timed_out": timeout,
                       "timeout_seconds": SUITE_TIMEOUT_SECONDS,
                       "timeout_classification": (
                           "INFRASTRUCTURE FAILURE"
                           if timeout else "NOT TIMED OUT"),
                       "stdout": stream(stdout, 64 * 1024 * 1024),
                       "stderr": stream(stderr, 8 * 1024 * 1024),
                       "stderr_literal_excerpt": literal_stderr(stderr),
                       "status": "FAIL", "infrastructure_failure": True}
                if not timeout and child.returncode == 0 and stdout:
                    try:
                        observed = producer.JsonReader(stdout).parse()
                        require(observed.get("schema") in {
                            SCHEMA + "-actual-suite-worker",
                            SCHEMA + "-actual-worker-failure"}
                            and observed.get("suite") == name
                            and observed.get("case_execution_denominator") == count
                            and observed.get("actual_candidate_workers") == 1
                            and observed.get("synthetic_control") is False
                            and observed.get("hidden_cases_read") == 0,
                            "reject crossed actual original worker output")
                        row["complete_actual_worker"] = observed
                        row["status"] = observed["status"]
                        row["infrastructure_failure"] = (
                            observed["schema"] == SCHEMA + "-actual-worker-failure")
                    except BaseException as error:
                        row.update(failure_details(
                            error, "VALIDATE_ACTUAL_WORKER_JSON"
                        ))
            except BaseException as error:
                row = {
                    "suite": name,
                    "case_execution_denominator": count,
                    "status": "FAIL",
                    "infrastructure_failure": True,
                    "timed_out": False,
                    "timeout_seconds": SUITE_TIMEOUT_SECONDS,
                    "timeout_classification": "NOT TIMED OUT",
                    "stderr_literal_excerpt": literal_stderr(
                        None,
                        "ACTUAL STDERR NOT AVAILABLE AFTER PROCESS "
                        "START OR CAPTURE FAILURE",
                    ),
                    **failure_details(
                        error, "CONTROLLER_PROCESS_START_OR_CAPTURE"
                    ),
                }
            rows.append(row)
    except BaseException as error:
        primary = error
    finally:
        if candidate_fd is not None:
            try:
                with CriticalSignals():
                    restored = restore(candidate_fd, journal)
            except BaseException as error:
                if primary is None:
                    primary = error
            finally:
                os.close(candidate_fd)
        if lock_fd is not None:
            os.close(lock_fd)
        if recovery_fd is not None:
            os.close(recovery_fd)
    if primary is not None:
        raise CampaignError("actual three-role campaign/recovery failed: "
                            + type(primary).__qualname__ + ": "
                            + str(primary)) from primary
    require(len(rows) == 13
            and tuple(row["suite"] for row in rows) == tuple(x for x, _ in SUITES)
            and sum(row["case_execution_denominator"] for row in rows) == 31237
            and restored is not None and len(restored) == 3,
            "require all actual original workers and three restored owners")
    pids = [row["pid"] for row in rows if type(row.get("pid")) is int]
    failure = [row for row in rows if row["status"] != "PASS"]
    infrastructure = [row for row in rows if row["infrastructure_failure"]]
    observed_mismatches = 0
    passes = 0
    complete_original_suites = 0
    for row in rows:
        observed = row.get("complete_actual_worker", {})
        observation = observed.get("complete_actual_observation", {})
        if type(observation.get("mismatch_count")) is int:
            observed_mismatches += observation["mismatch_count"]
        if (observed.get("schema") == SCHEMA + "-actual-suite-worker"
                and type(observation) is dict
                and observation.get("case_execution_denominator")
                == row["case_execution_denominator"]
                and observation.get("actual_candidate_case_count")
                == row["case_execution_denominator"]):
            complete_original_suites += 1
        if row["status"] == "PASS":
            passes += row["case_execution_denominator"]
    passed = (not failure and not infrastructure
              and len(set(pids)) == len(pids) == 13
              and complete_original_suites == 13 and passes == 31237)
    mismatch_count = (observed_mismatches
                      if complete_original_suites == 13
                      else "NOT MEASURED")
    report = {"schema": SCHEMA + "-complete-actual-original-campaign",
            "status": "PASS" if passed else "FAIL",
            "family": FAMILY, "label": LABEL,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "case_execution_denominator": 31237, "suite_count": 13,
            "actual_candidate_workers": len(pids),
            "unique_candidate_worker_count": len(set(pids)),
            "completed_suite_count": complete_original_suites,
            "verified_passing_case_count": passes,
            "semantic_mismatch_count": mismatch_count,
            "observed_semantic_mismatch_lower_bound": observed_mismatches,
            "infrastructure_failure_count": len(infrastructure),
            "infrastructure_failure_suites": [
                row["suite"] for row in infrastructure
            ],
            "failed_suites": [
                row["suite"] for row in failure
            ],
            "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "maximum_serial_worker_timeout_seconds":
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
            "all_original_suites_attempted": len(rows) == 13,
            "timeout_classification": "INFRASTRUCTURE FAILURE",
            "timeout_count": sum(
                row.get("timed_out") is True for row in rows),
            "timed_out_suites": [
                row["suite"] for row in rows
                if row.get("timed_out") is True
            ],
            "complete_original_suite_workers": rows,
            "all_three_original_targets_restored": True,
            "restored_original_roles": restored,
            "supplemental_candidate_matching": "NOT RUN",
            "supplemental_cases_counted_in_original_denominator": False,
            "original_campaign_passed": passed,
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "timing_trials_run": 0, "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "winner_selected": False}
    return publish_campaign(report, producer)


def recover(args):
    state = verify(args["--source-sha256"], args["--protocol-sha256"],
                   args["--contract-sha256"], active=True)
    require(args.get("--family") == FAMILY
            and args.get("--label") == LABEL
            and args.get("--build-receipt-sha256") == V13[3][1]
            and args.get("--root-receipt-sha256") == V13[4][1]
            and args.get("--producer-source-sha256") == PRODUCER[0][1]
            and args.get("--guard-source-sha256") == GUARD[0][1]
            and args.get("--adapter-sha256") == CLEAN_ADAPTER[1],
            "reject recovery without all original independent caller pins")
    recovery_fd, lock_fd = recovery_directory(False)
    candidate_fd = None
    try:
        journal = read_live_journal(
            state["producer"], args["--recovery-journal-sha256"])
        candidate_fd = candidate_directory()
        with CriticalSignals():
            restored = restore(candidate_fd, journal)
    finally:
        if candidate_fd is not None:
            os.close(candidate_fd)
        os.close(lock_fd)
        os.close(recovery_fd)
    require(len(restored) == 3,
            "reject incomplete actual three-role original-inode recovery")
    return {
        "schema": SCHEMA + "-exact-three-role-recovery",
        "status": "PASS",
        "family": FAMILY,
        "label": LABEL,
        "restored_original_role_count": 3,
        "restored_original_roles": restored,
        "actual_candidate_workers": 0,
        "candidate_matching": "NOT RUN BY RECOVERY",
        "candidate_qualified": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "timing_trials_run": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }


def parse(arguments):
    modes = {"--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover"}
    selected = [item for item in arguments if item in modes]
    require(len(selected) == 1, "select exactly one independently pinned action")
    mode, args, index = selected[0], {}, 0
    allowed = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        "--family", "--label", "--suite", "--build-receipt-sha256",
        "--root-receipt-sha256", "--producer-source-sha256",
        "--guard-source-sha256", "--adapter-sha256",
        "--recovery-journal-sha256",
    }
    while index < len(arguments):
        key = arguments[index]
        if key in modes:
            require(key == mode, "reject conflicting campaign actions")
            index += 1
            continue
        require(key in allowed and key not in args
                and index + 1 < len(arguments),
                "reject a missing or duplicated independent caller pin")
        args[key] = arguments[index + 1]
        index += 2
    source_keys = {"--source-sha256", "--protocol-sha256"}
    if mode == "--render-contract":
        require(set(args) == source_keys, "forbid actual render authority")
    elif mode in {"--self-test", "--verify-frozen-context"}:
        require(set(args) == source_keys | {"--contract-sha256"},
                "forbid native activation during source verification")
    else:
        expected = source_keys | {
            "--contract-sha256", "--family", "--label",
            "--build-receipt-sha256", "--root-receipt-sha256",
            "--producer-source-sha256", "--guard-source-sha256",
            "--adapter-sha256",
        }
        if mode == "--worker":
            expected |= {"--suite", "--recovery-journal-sha256"}
        elif mode == "--recover":
            expected |= {"--recovery-journal-sha256"}
        require(set(args) == expected, "require every actual observer/build pin")
    return mode, args


def main():
    mode, args = parse(list(sys.argv[1:]))
    if mode in {"--self-test", "--verify-frozen-context", "--render-contract"}:
        result = source_mode(mode, args)
        producer = load(PRODUCER[0], "_rebar_guard_clean_zig_v5_output")
        output = producer.canonical(result)
    elif mode == "--worker":
        result = worker(args)
        output = worker_canonical(result)
    elif mode == "--recover":
        result = recover(args)
        producer = load(PRODUCER[0], "_rebar_guard_clean_zig_v5_output")
        output = producer.canonical(result)
    else:
        result = campaign(args)
        producer = load(PRODUCER[0], "_rebar_guard_clean_zig_v5_output")
        output = producer.canonical(result)
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        sys.stderr.write("first-party guard-clean Zig original campaign rejected: "
                         + type(error).__qualname__ + ": " + str(error) + "\n")
        raise SystemExit(1) from error
