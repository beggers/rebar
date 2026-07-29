#!/usr/bin/env python3
"""Freeze C16's guarded original campaign without guessing its build root.

Only matcher-safe standard-library modules are imported.  Every operational
mode fails closed until an independently published C16 root-provenance receipt
exists.  Source modes physically prohibit candidate, native, archive, private
root, process, clock, network, and workspace-mutation operations.
"""

from __future__ import annotations

import builtins
import hashlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/run_owned_repaired_c_original_campaign_v5.py"
PROTOCOL = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V5.md"
CONTRACT = "oracle/phase2/repaired-c-original-campaign-v5.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v5"
LABEL = "phase2-v16-c-subject-buffer-original-p0-v5"
DEVICE = 2064
MAX_OWNER = 8 * 1024 * 1024
ORIGINAL_CASES = 31237
SUPPLEMENTAL_CASES = 8244
PRIVATE_WAIVERS = 13
FAMILY_COUNT = 6
ROOT_PROVENANCE = "NOT ESTABLISHED"
RUN_BLOCKER = (
    "the existing C16 private root and both native phase owners are not established; "
    "require a separately published version-18 subject-buffer source-build receipt "
    "and an independently pinned version-18 root-provenance receipt"
)

GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
    31364044,
)
P0 = (
    (
        "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094,
        428927,
    ),
    (
        "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261,
        524712,
    ),
    (
        "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875,
        524713,
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
GUARD = (
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
FEATURE = (
    (
        "tools/apply_owned_c_subject_buffer_ownership_v1.py",
        "8262295a9e84c5fa30fe4e83102236fbaa233c914fb0c570d5fce3cdaf8605d2",
        80090,
        428938,
    ),
    (
        "oracle/phase2/C-SUBJECT-BUFFER-OWNERSHIP-V1.md",
        "997af2edeced019663886aa7e20873506e4b13ee361bf5ce8d533e3ad2ea7393",
        5527,
        524724,
    ),
    (
        "oracle/phase2/c-subject-buffer-ownership-v1.json",
        "b2ef8b9f5f9c7262be0e639d17436d0e1e8637d5649741bf2aa1538ebef3eb6a",
        12435,
        524726,
    ),
)
BUILD = (
    (
        "tools/reproduce_owned_c_subject_buffer_source_build_v16.py",
        "655b1c72c66fe9bfd06d96c7daeca3d2eb4817a5e28fdbbd737bbfd59713aa90",
        79602,
        430076,
    ),
    (
        "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V16.md",
        "19b9ef86be5ce0c77c0addc40cfdefbbfb05102adfdd7baa38b39d62b08497a9",
        4778,
        524731,
    ),
    (
        "oracle/phase2/c-subject-buffer-source-build-v16.json",
        "7ea6bbe9a72a95e905e21cd1c45ac9a5b25620980f40d1ea141163642142a3c7",
        12543,
        524732,
    ),
    (
        "oracle/phase2/evidence/native-source-build-v16-c-phase2-v16-c-"
        "subject-buffer-original-p0-publication-receipt.json",
        "16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6",
        2671,
        524751,
    ),
)
CURRENT_C15 = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v4-c-phase2-v15-"
    "c-pickle-original-p0-failures-publication-receipt.json",
    "c4099d537475b250e15c6d696fead132889422aa3cfe445d86e27c5cc19f2ba9",
    3482,
    524641,
)
HISTORICAL_C10 = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v3-c-phase2-v10-"
    "live-original-p0-failures-publication-receipt.json",
    "f3383b6c00ab28d4466332b99c759e981b423a9f427757b0524f7a85f0cf253d",
    1039,
    524605,
)
GRAPH = (
    (
        "tools/render_candidate_current_overview_v86.py",
        "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d",
        75354,
        431699,
    ),
    (
        "docs/evidence/candidate-current-overview-v86.inputs.json",
        "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c",
        1345744,
        430944,
    ),
    (
        "docs/evidence/candidate-current-overview-v86.json",
        "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc",
        4128155,
        431704,
    ),
    (
        "docs/evidence/candidate-current-overview-v86.svg",
        "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55",
        6214,
        431705,
    ),
)

SUITES = (
    ("original_bounded_v5", 151, 0),
    ("public_v3", 864, 0),
    ("scanner_v3", 1024, 0),
    ("buffer_v3", 768, 0),
    ("managed_v1", 1024, 0),
    ("scanner_verbose_v1", 2854, 0),
    ("public_types_v1", 6912, 248),
    ("substitution_v2", 5120, 224),
    ("shape_v2", 10240, 672),
    ("public_surface_v19", 1376, 114),
    ("subinterpreter_v2", 128, 0),
    ("pep688_v4", 264, 4),
    ("threaded_pattern_v1", 512, 0),
)
HISTORICAL_WORKERS = (
    (
        "original_bounded_v5",
        "544118457b826d54a202393580700774690c2e31316b38ee391136fc49562cf7",
        1471,
        524577,
    ),
    (
        "public_v3",
        "fe18dc65418a91381726f94e10856fe006865df97b707df1a09be60e86476ef2",
        1454,
        524579,
    ),
    (
        "scanner_v3",
        "9085bbce1de494fbaaa403b3b6f42cd4766b9badb0b778cdc53f1e322ac23815",
        1457,
        524581,
    ),
    (
        "buffer_v3",
        "064a93944c6e2bcd2826716c3e3b6152805b2cf58da5133058bd571e3c401461",
        1453,
        524583,
    ),
    (
        "managed_v1",
        "098ef746d6e3d4d7694c5430a6e2221afec2d07af858d1845c2602b5e6fe1ee8",
        1458,
        524585,
    ),
    (
        "scanner_verbose_v1",
        "105a620928b39f8f5464a95949398efd8464981ca37b7661b941be84e97cd307",
        1473,
        524587,
    ),
    (
        "public_types_v1",
        "5548f27728cfb8e9d941aa9a3d6c4220d889d82707384d73f41f5a2ec92e3964",
        1471,
        524589,
    ),
    (
        "substitution_v2",
        "6897346db1cfe6f53bd6bce2a70f2b2bab4b46759fc5dee18c9f2d978c36dffe",
        1471,
        524591,
    ),
    (
        "shape_v2",
        "58662aeb28cead53a4b87b1da04afb8ac8ece1b5cbb9edce79b2f37115469916",
        1458,
        524593,
    ),
    (
        "public_surface_v19",
        "998cba40fd46931d75b5766b419ec19656e606f9166e03321188ce158becf824",
        1476,
        524595,
    ),
    (
        "subinterpreter_v2",
        "0eb401ac4261252c35c134fc021388abd5f1ec1c1686e5b06675a0189f8fab5d",
        1470,
        524597,
    ),
    (
        "pep688_v4",
        "9dfb20f4b97fa631bbcb3885f0a10109f9a5701de84805d2edd37dc9948e7a6a",
        1453,
        524599,
    ),
    (
        "threaded_pattern_v1",
        "a686d871de56e5728550079274618e19118d9aca5dc606d99230578253d39185",
        1474,
        524601,
    ),
)
WORKER_PREFIX = (
    "oracle/phase2/evidence/frozen-p0-candidate-worker-v7-c-phase2-v10-"
    "live-original-p0-"
)
STATIC_OWNERS = (
    (GOAL,)
    + P0
    + PRODUCER
    + GUARD
    + FEATURE
    + BUILD
    + (CURRENT_C15, HISTORICAL_C10)
    + tuple(
        (WORKER_PREFIX + name + "-publication-receipt.json", digest, size, inode)
        for name, digest, size, inode in HISTORICAL_WORKERS
    )
    + GRAPH
)
OWNED_PATHS = frozenset(owner[0] for owner in STATIC_OWNERS) | {
    SOURCE,
    PROTOCOL,
    CONTRACT,
}


class CampaignError(Exception):
    """An exact first-party source owner or source-only policy was rejected."""


def need(condition: object, reason: str) -> None:
    if not condition:
        raise CampaignError(reason)


def exact_digest(value: object, role: str) -> str:
    need(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "require an exact lowercase SHA-256: " + role,
    )
    return value


def matcher_free() -> None:
    need(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and os.path.abspath(sys.executable) == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True,
        "require the pinned, matcher-clean CPython 3.14.6 -I -B -S",
    )
    need(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "never preload Python re, _sre, or a candidate before its guard",
    )


class SourceWall:
    """Physically allow only pinned read-only repository source owners."""

    DENIED_MODULES = frozenset(
        {
            "re",
            "_sre",
            "regex",
            "pcre",
            "pcre2",
            "re2",
            "oniguruma",
            "hyperscan",
            "ctypes",
            "cffi",
            "subprocess",
            "socket",
            "threading",
            "multiprocessing",
            "asyncio",
            "time",
            "gzip",
            "zipfile",
            "tarfile",
            "lzma",
            "bz2",
            "argparse",
            "pathlib",
            "candidates",
        }
    )

    def __init__(self) -> None:
        self.originals: list[tuple[object, str, object]] = []
        self.blocked: dict[str, int] = {}
        self.read_count = 0
        self.allowed = frozenset(ROOT + "/" + item for item in OWNED_PATHS)

    def reject(self, role: str) -> None:
        self.blocked[role] = self.blocked.get(role, 0) + 1
        raise CampaignError("source-only operation physically denied: " + role)

    def patch(self, module: object, name: str, replacement: object) -> None:
        if hasattr(module, name):
            previous = getattr(module, name)
            self.originals.append((module, name, previous))
            setattr(module, name, replacement)

    def enter_open(self, path: object, flags: object, mode: int = 0o777, **kw: object) -> int:
        if (
            type(path) is not str
            or path not in self.allowed
            or type(flags) is not int
            or flags & os.O_ACCMODE != os.O_RDONLY
            or flags
            & (
                getattr(os, "O_CREAT", 0)
                | getattr(os, "O_EXCL", 0)
                | getattr(os, "O_TRUNC", 0)
                | getattr(os, "O_APPEND", 0)
                | getattr(os, "O_TMPFILE", 0)
            )
            or not flags & getattr(os, "O_NOFOLLOW", 0)
            or kw.get("dir_fd") is not None
        ):
            self.reject("unsafe file, archive, native, private root, or workspace write")
        original = next(
            item for module, name, item in self.originals if module is os and name == "open"
        )
        self.read_count += 1
        return original(path, flags, mode, **kw)

    def enter_import(
        self,
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: object = (),
        level: int = 0,
    ) -> object:
        first = name.split(".", 1)[0]
        if first in self.DENIED_MODULES:
            self.reject("candidate, matcher, native loader, clock, or archive import: " + name)
        original = next(
            item
            for module, attr, item in self.originals
            if module is builtins and attr == "__import__"
        )
        return original(name, globals, locals, fromlist, level)

    def denied_callable(self, role: str) -> object:
        def blocked(*args: object, **kwargs: object) -> object:
            del args, kwargs
            self.reject(role)

        return blocked

    def __enter__(self) -> "SourceWall":
        self.patch(os, "open", self.enter_open)
        self.patch(builtins, "__import__", self.enter_import)
        self.patch(builtins, "open", self.denied_callable("unverified Python file open"))
        for name, role in (
            ("stat", "path or private-root stat"),
            ("lstat", "native or private-root lstat"),
            ("listdir", "private-root directory listing"),
            ("scandir", "private-root directory scan"),
            ("mkdir", "workspace or private-root creation"),
            ("makedirs", "workspace or private-root creation"),
            ("unlink", "workspace or evidence removal"),
            ("remove", "workspace or evidence removal"),
            ("replace", "candidate or evidence replacement"),
            ("rename", "candidate or evidence rename"),
            ("link", "native or evidence hard link"),
            ("symlink", "native or evidence symbolic link"),
            ("chmod", "native or workspace mode mutation"),
            ("chown", "native or workspace ownership mutation"),
            ("chdir", "working-directory mutation"),
            ("putenv", "process-environment mutation"),
            ("unsetenv", "process-environment mutation"),
            ("system", "candidate, worker, or compiler process"),
            ("fork", "candidate, worker, or compiler process"),
            ("posix_spawn", "candidate, worker, or compiler process"),
            ("posix_spawnp", "candidate, worker, or compiler process"),
            ("pipe", "candidate worker or interpreter pipe"),
            ("fsync", "journal, evidence, or native activation"),
            ("times", "process or benchmark clock"),
        ):
            self.patch(os, name, self.denied_callable(role))
        return self

    def __exit__(self, kind: object, value: object, trace: object) -> bool:
        del kind, value, trace
        while self.originals:
            module, name, previous = self.originals.pop()
            setattr(module, name, previous)
        return False


def read_owner(owner: tuple, *, maximum: int = MAX_OWNER) -> bytes:
    need(type(owner) is tuple and len(owner) == 4, "require one exact immutable owner")
    relative, fingerprint, count, inode = owner
    need(
        type(relative) is str
        and relative in OWNED_PATHS
        and relative not in {SOURCE, PROTOCOL, CONTRACT}
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and "holdout" not in relative.lower()
        and "benchmark" not in relative.lower()
        and not relative.endswith((".gz", ".so", ".zip", ".tar", ".xz")),
        "reject an unowned source, candidate, native, archive, or holdout",
    )
    exact_digest(fingerprint, relative)
    need(
        type(count) is int
        and 0 < count <= maximum
        and type(inode) is int
        and inode > 0,
        "reject an unbounded or substituted immutable owner: " + relative,
    )
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == count
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600,
            "reject substituted source-owner identity: " + relative,
        )
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            chunk = os.read(descriptor, min(remaining, 262144))
            need(bool(chunk), "reject a truncated source owner: " + relative)
            chunks.append(chunk)
            remaining -= len(chunk)
        need(not os.read(descriptor, 1), "reject trailing source-owner bytes: " + relative)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        need(
            hashlib.sha256(payload).hexdigest() == fingerprint
            and (
                before.st_dev,
                before.st_ino,
                before.st_size,
                before.st_mtime_ns,
                before.st_ctime_ns,
                before.st_nlink,
            )
            == (
                after.st_dev,
                after.st_ino,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
                after.st_nlink,
            ),
            "reject changed or incorrectly hashed source: " + relative,
        )
        return payload
    finally:
        os.close(descriptor)


def read_dynamic(relative: str, fingerprint: str) -> bytes:
    need(relative in {SOURCE, PROTOCOL, CONTRACT}, "reject a dynamic candidate or root owner")
    exact_digest(fingerprint, relative)
    descriptor = os.open(
        ROOT + "/" + relative,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        need(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
            and 0 < before.st_size <= MAX_OWNER,
            "reject a substituted version-five source owner: " + relative,
        )
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            item = os.read(descriptor, min(remaining, 262144))
            need(bool(item), "reject a truncated version-five owner: " + relative)
            chunks.append(item)
            remaining -= len(item)
        need(not os.read(descriptor, 1), "reject a changed version-five owner: " + relative)
        payload = b"".join(chunks)
        after = os.fstat(descriptor)
        need(
            hashlib.sha256(payload).hexdigest() == fingerprint
            and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
            "reject a modified or falsely pinned version-five owner: " + relative,
        )
        return payload
    finally:
        os.close(descriptor)


def load_producer(raw: bytes) -> types.ModuleType:
    need(
        hashlib.sha256(raw).hexdigest() == PRODUCER[0][1],
        "require the exact unmodified version-five original-suite producer",
    )
    matcher_free()
    module = types.ModuleType("_rebar_owned_c16_frozen_original_producer_v5")
    module.__file__ = ROOT + "/" + PRODUCER[0][0]
    module.__package__ = ""
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(
        module.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
        and module.CASE_DENOMINATOR == ORIGINAL_CASES
        and module.SUITE_COUNT == len(SUITES)
        and module.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVERS
        and module.SUPPLEMENTAL_CASE_COUNT == SUPPLEMENTAL_CASES
        and callable(module.canonical)
        and callable(module.JsonReader)
        and callable(module.validate_p0)
        and callable(module.validate_runtime_guard_v2),
        "reject a substituted or weakened original V5 producer",
    )
    matcher_free()
    return module


def parse_document(producer: types.ModuleType, raw: bytes, role: str) -> dict:
    try:
        value = producer.JsonReader(raw).parse()
    except Exception as error:
        raise CampaignError("reject malformed bounded " + role + ": " + str(error)) from error
    need(type(value) is dict, "require a complete machine document: " + role)
    return value


def owner_record(item: tuple) -> dict:
    return {"path": item[0], "sha256": item[1], "bytes": item[2]}


def validate_history(producer: types.ModuleType, raw_by_path: dict[str, bytes]) -> dict:
    previous = parse_document(producer, raw_by_path[CURRENT_C15[0]], "actual C15 failure receipt")
    need(
        previous.get("schema") == "rebar-owned-repaired-c-original-campaign-v4-durable-publication-receipt"
        and previous.get("status") == "PASS"
        and previous.get("publication_status") == "PASS"
        and previous.get("candidate_status") == "FAIL"
        and previous.get("candidate_qualified") is False
        and previous.get("label") == "phase2-v15-c-pickle-original-p0"
        and previous.get("suite_count") == len(SUITES)
        and previous.get("completed_suite_count") == len(SUITES)
        and previous.get("case_execution_denominator") == ORIGINAL_CASES
        and previous.get("semantic_mismatch_count") == 1230
        and previous.get("verified_passing_case_count") == 7325
        and previous.get("actual_candidate_workers") == len(SUITES)
        and previous.get("infrastructure_failure_count") == 0
        and previous.get("candidate_execution_failure_count") == 0
        and previous.get("named_private_waiver_count") == PRIVATE_WAIVERS
        and previous.get("original_source_targets_modified") == 0
        and previous.get("hidden_cases_read") == 0
        and previous.get("benchmark_files_read") == 0
        and previous.get("timing_trials_run") == 0
        and previous.get("holdout") == "NOT OPENED"
        and previous.get("performance") == "NOT MEASURED"
        and previous.get("winner_selected") is False,
        "reject the actual separately published C15 failure or misreport a receipt as candidate success",
    )
    old = parse_document(producer, raw_by_path[HISTORICAL_C10[0]], "historical C10 failure receipt")
    need(
        old.get("schema") == "rebar-owned-repaired-c-original-campaign-v3-durable-publication-receipt"
        and old.get("status") == "PASS"
        and old.get("candidate_status") == "FAIL"
        and old.get("label") == "phase2-v10-live-original-p0"
        and old.get("family") == "c"
        and old.get("case_execution_denominator") == ORIGINAL_CASES
        and old.get("suite_count") == len(SUITES)
        and old.get("original_native_restored") is True
        and old.get("holdout") == "NOT OPENED"
        and old.get("winner_selected") is False,
        "reject the separate historical C10 failure and restored native",
    )
    rows: list[dict] = []
    for (suite, count, differences), worker in zip(SUITES, HISTORICAL_WORKERS, strict=True):
        need(worker[0] == suite, "reject reordered or omitted historical C10 original suites")
        relative = WORKER_PREFIX + suite + "-publication-receipt.json"
        observed = parse_document(producer, raw_by_path[relative], "historical C10 suite " + suite)
        need(
            observed.get("schema") == "rebar-frozen-python-re-p0-candidate-worker-v7-durable-suite-publication-receipt"
            and observed.get("status") == "PASS"
            and observed.get("candidate_family") == "c"
            and observed.get("label") == "phase2-v10-live-original-p0"
            and observed.get("suite") == suite
            and observed.get("case_execution_denominator") == count
            and observed.get("phase_one_case_execution_denominator") == ORIGINAL_CASES
            and observed.get("mismatch_count") == differences
            and observed.get("candidate_status") == ("FAIL" if differences else "PASS")
            and observed.get("genuine_original_suite") is True
            and observed.get("all_original_records_and_mismatches_preserved") is True
            and observed.get("candidate_qualified") is False
            and observed.get("hidden_cases_read") == 0
            and observed.get("clock_samples") == 0
            and observed.get("timing_trials_run") == 0
            and observed.get("holdout") == "NOT OPENED"
            and observed.get("performance") == "NOT MEASURED"
            and observed.get("winner_selected") is False,
            "reject the independently preserved historical C10 suite: " + suite,
        )
        rows.append({"suite": suite, "case_execution_count": count, "mismatch_count": differences})
    need(
        sum(row["case_execution_count"] for row in rows) == ORIGINAL_CASES
        and sum(row["mismatch_count"] for row in rows) == 1262,
        "never mix the independently observed C10 and C15 failure denominators",
    )
    return {
        "c10": {
            "candidate_status": "FAIL",
            "mismatch_count": 1262,
            "suite_count": len(SUITES),
            "suite_results": rows,
            "aggregate_receipt": owner_record(HISTORICAL_C10),
        },
        "c15": {
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1230,
            "verified_passing_case_count": 7325,
            "actual_candidate_workers": len(SUITES),
            "infrastructure_failure_count": 0,
            "receipt": owner_record(CURRENT_C15),
        },
    }


def validate_build(producer: types.ModuleType, raw_by_path: dict[str, bytes]) -> dict:
    document = parse_document(producer, raw_by_path[BUILD[2][0]], "source-frozen C16 build contract")
    receipt = parse_document(producer, raw_by_path[BUILD[3][0]], "actual small C16 build receipt")
    policy = document.get("future_build_policy")
    need(
        document.get("schema") == "rebar-phase2-owned-c-subject-buffer-source-build-v16-source-freeze"
        and document.get("version") == 16
        and document.get("family") == "c"
        and type(policy) is dict
        and policy.get("private_root_prefix") == "rebar-phase2-native-build-v8-c-"
        and policy.get("phase_count") == 2
        and policy.get("phase_names") == ["reference-a", "reference-b"]
        and policy.get("total_compiler_process_count") == 14
        and policy.get("adapter_source_sha256")
        == "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
        and policy.get("variant_source_sha256")
        == "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962",
        "reject the exact first-party C16 source build, shared-prefix hazard, or two independent phases",
    )
    need(
        receipt.get("schema")
        == "rebar-phase2-owned-c-subject-buffer-source-build-v16-durable-publication-receipt"
        and receipt.get("version") == 16
        and receipt.get("family") == "c"
        and receipt.get("label") == "phase2-v16-c-subject-buffer-original-p0"
        and receipt.get("status") == "PASS"
        and receipt.get("build_status") == "PASS"
        and receipt.get("actual_compiler_process_count") == 14
        and receipt.get("expected_compiler_process_count") == 14
        and receipt.get("actual_source_apply_count") == 2
        and receipt.get("expected_source_apply_count") == 2
        and receipt.get("variant_source_sha256")
        == "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962"
        and receipt.get("variant_source_bytes") == 222212
        and receipt.get("adapter_source_sha256")
        == "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096"
        and receipt.get("original_source_sha256")
        == "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55"
        and receipt.get("candidate_correctness") == "NOT MEASURED"
        and receipt.get("candidate_imports") == 0
        and receipt.get("candidate_processes_started") == 0
        and receipt.get("native_libraries_loaded") == 0
        and receipt.get("installed_native_read") is False
        and receipt.get("installed_native_activated") is False
        and receipt.get("historical_archives_opened") == 0
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("winner_selected") is False,
        "reject the genuine already-published C16 build or misrepresent a build as matching correctness",
    )
    forbidden_root_fields = (
        "build_root",
        "root",
        "root_provenance",
        "root_provenance_receipt",
        "phase_a_native",
        "phase_b_native",
        "phase_a_native_sha256",
        "phase_b_native_sha256",
        "native_sha256",
    )
    need(
        all(receipt.get(name) is None for name in forbidden_root_fields),
        "do not reinterpret an unreviewed C16 build receipt as independent root provenance",
    )
    return {
        "status": "PASS",
        "actual_compiler_process_count": 14,
        "actual_source_apply_count": 2,
        "complete_native_variant_sha256": policy["variant_source_sha256"],
        "complete_native_variant_bytes": 222212,
        "unchanged_adapter_sha256": policy["adapter_source_sha256"],
        "build_receipt": owner_record(BUILD[3]),
        "private_root_prefix_is_shared_with_older_builds": True,
        "private_root_provenance": ROOT_PROVENANCE,
        "phase_native_provenance": ROOT_PROVENANCE,
        "archive_opened": False,
        "candidate_correctness": "NOT MEASURED",
    }


def validate_context(raw_by_path: dict[str, bytes], producer: types.ModuleType) -> dict:
    p0 = parse_document(producer, raw_by_path[P0[2][0]], "complete version-four Python reference")
    producer.validate_p0(p0)
    original = parse_document(producer, raw_by_path[PRODUCER[2][0]], "version-five original producer")
    need(
        original.get("schema") == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
        and original.get("version") == 5
        and original.get("case_execution_denominator") == ORIGINAL_CASES
        and original.get("suite_count") == len(SUITES)
        and original.get("named_private_waiver_count") == PRIVATE_WAIVERS
        and original.get("family_count") == FAMILY_COUNT
        and original.get("source_owner_count") == 25
        and original.get("supplemental_case_count") == SUPPLEMENTAL_CASES
        and original.get("supplemental_cases_counted_in_original_denominator") is False
        and original.get("candidate_matching") == "NOT RUN"
        and original.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and original.get("qualified_candidate_count") == 0
        and original.get("holdout") == "NOT OPENED",
        "reject a weakened original producer or merge the separate supplemental denominator",
    )
    original_suites = original.get("suites")
    need(type(original_suites) is list and len(original_suites) == len(SUITES), "require all 13 exact original suites")
    for observed, (name, count, _) in zip(original_suites, SUITES, strict=True):
        need(
            type(observed) is dict
            and observed.get("id") == name
            and observed.get("case_execution_count") == count,
            "reject an omitted, reordered, replaced, or weakened original suite: " + name,
        )
    c_family = [row for row in original.get("families", []) if row.get("name") == "c"]
    need(
        len(c_family) == 1
        and c_family[0].get("module") == "candidates.vm_candidate"
        and c_family[0].get("bridge_module") == "candidates._vm_native"
        and c_family[0].get("combined_native") is True
        and c_family[0].get("owned_ctypes") is False
        and c_family[0].get("adapter_relative") == "candidates/vm_candidate.py",
        "reject a borrowed, wrapped, dynamically loaded, or non-C original matcher",
    )
    guard = parse_document(producer, raw_by_path[GUARD[2][0]], "exact version-two runtime guard")
    producer.validate_runtime_guard_v2(guard)
    policy = guard.get("runtime_isolation_policy")
    nested = guard.get("subinterpreter_bootstrap")
    need(
        type(policy) is dict
        and policy.get("guard_installed_before_candidate_import") is True
        and policy.get("stdlib_re_engine") == "FORBIDDEN"
        and policy.get("stdlib_sre_engine") == "FORBIDDEN"
        and policy.get("external_regex_package") == "FORBIDDEN"
        and policy.get("cross_candidate_engine") == "FORBIDDEN"
        and policy.get("matching_fallback") == "FORBIDDEN"
        and type(nested) is dict
        and nested.get("original_case_count") == 128
        and nested.get("expected_interpreters_created") == 11
        and nested.get("expected_case_interpreter_exec_calls") == 394
        and nested.get("require_child_guard_before_candidate_import") is True,
        "reject matcher delegation, an unguarded candidate, or the real nested-interpreter obligation",
    )
    feature = parse_document(producer, raw_by_path[FEATURE[2][0]], "exact first-party subject ownership feature")
    need(
        feature.get("schema") == "rebar-phase2-owned-c-subject-buffer-ownership-v1"
        and feature.get("version") == 1
        and feature.get("family") == "c"
        and feature.get("source") == {"path": FEATURE[0][0], "sha256": FEATURE[0][1]}
        and feature.get("protocol") == {"path": FEATURE[1][0], "sha256": FEATURE[1][1]},
        "reject the original independently owned C subject-buffer feature",
    )
    graph = parse_document(producer, raw_by_path[GRAPH[2][0]], "complete actual version-86 overview")
    need(
        graph.get("schema") == "rebar-candidate-current-overview-v86-summary"
        and graph.get("version") == 86
        and graph.get("status") == "PASS"
        and graph.get("full_case_denominator") == ORIGINAL_CASES
        and graph.get("suite_count") == len(SUITES)
        and graph.get("private_waiver_count") == PRIVATE_WAIVERS
        and graph.get("qualified_candidate_count") == 0
        and graph.get("authenticated_evidence_owner_lower_bound") == 277
        and graph.get("authenticated_history_reference_lower_bound") == 282
        and graph.get("actual_candidate_imports") == 0
        and graph.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and graph.get("final_holdout_opened") is False
        and graph.get("performance") == "NOT MEASURED",
        "reject the actually pushed version-86 overview or silently replace its evidence denominator",
    )
    return {
        "history": validate_history(producer, raw_by_path),
        "build": validate_build(producer, raw_by_path),
        "overview": {
            "version": 86,
            "authenticated_evidence_owner_lower_bound": 277,
            "authenticated_history_reference_lower_bound": 282,
            "owners": [owner_record(item) for item in GRAPH],
        },
    }


def contract_document(context: dict, source_sha: str, protocol_sha: str) -> dict:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 5,
        "phase": "PHASE 2: CANDIDATES",
        "status": "SOURCE FROZEN; ACTUAL C16 ORIGINAL CAMPAIGN NOT RUN",
        "status_scope": "SOURCE-ONLY CORRECTNESS CAMPAIGN; NOT A CANDIDATE RESULT",
        "family": "c",
        "label": LABEL,
        "goal_sha256": GOAL[1],
        "source": {"path": SOURCE, "sha256": source_sha},
        "protocol": {"path": PROTOCOL, "sha256": protocol_sha},
        "pinned_cpython": {
            "path": PYTHON,
            "version": "3.14.6",
            "required_flags": ["-I", "-B", "-S"],
        },
        "phase_one": {
            "status": "PASS",
            "case_execution_denominator": ORIGINAL_CASES,
            "suite_count": len(SUITES),
            "named_private_waiver_count": PRIVATE_WAIVERS,
            "supplemental_case_count": SUPPLEMENTAL_CASES,
            "supplemental_cases_counted_in_original_denominator": False,
            "owners": [owner_record(item) for item in P0],
        },
        "original_producer": {
            "version": 5,
            "suite_count": len(SUITES),
            "case_execution_denominator": ORIGINAL_CASES,
            "suites": [
                {"suite": name, "case_execution_count": count}
                for name, count, _ in SUITES
            ],
            "owners": [owner_record(item) for item in PRODUCER],
        },
        "runtime_guard": {
            "version": 2,
            "guard_installed_before_candidate_import": True,
            "candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "nested_original_cases": 128,
            "required_child_interpreters": 11,
            "required_nested_case_executions": 394,
            "owners": [owner_record(item) for item in GUARD],
        },
        "first_party_feature": {
            "family": "c",
            "owners": [owner_record(item) for item in FEATURE],
            "variant_sha256": context["build"]["complete_native_variant_sha256"],
            "variant_bytes": context["build"]["complete_native_variant_bytes"],
            "adapter_sha256": context["build"]["unchanged_adapter_sha256"],
        },
        "actual_c16_build": context["build"],
        "preserved_actual_history": context["history"],
        "current_overview": context["overview"],
        "actual_run_authorization": {
            "status": "BLOCKED",
            "reason": RUN_BLOCKER,
            "c16_root_provenance": ROOT_PROVENANCE,
            "required_fresh_source_build_version": 18,
            "required_fresh_root_provenance_version": 18,
            "fresh_source_build": "NOT RUN",
            "fresh_root_provenance": "NOT PUBLISHED",
            "guessing_shared_build_root": "FORBIDDEN",
            "opening_build_archive": "FORBIDDEN",
            "opening_a_private_root_in_source_modes": "FORBIDDEN",
            "standard_library_engine": "FORBIDDEN",
            "external_regex_package": "FORBIDDEN",
            "another_candidate_engine": "FORBIDDEN",
            "fallback": "FORBIDDEN",
            "actual_run": "NOT AUTHORIZED",
        },
        "source_only_effects": {
            "actual_candidate_imports": 0,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_compiler_processes": 0,
            "actual_guard_installations": 0,
            "actual_native_libraries_loaded": 0,
            "actual_private_roots_opened": 0,
            "actual_archives_opened": 0,
            "actual_workspace_mutations": 0,
            "actual_network_requests": 0,
            "actual_clock_samples": 0,
            "actual_holdout_cases_read": 0,
        },
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualification": "BLOCKED",
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "supplemental_candidate_correctness": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "historical_holdout_case_count": 4194304,
        "expanded_holdout_proposal_case_count": 14155776,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def parse_options(arguments: list[str]) -> dict:
    need(type(arguments) is list and all(type(item) is str for item in arguments), "reject malformed campaign authorization")
    modes = ("--self-test", "--verify-frozen-context", "--render-contract")
    actual = ("--run", "--worker", "--recover")
    if any(item in actual for item in arguments):
        raise CampaignError(RUN_BLOCKER)
    need(
        sum(arguments.count(item) for item in modes) == 1,
        "select exactly one safe source-only mode",
    )
    mode = next(item for item in modes if item in arguments)
    need(arguments.count(mode) == 1, "reject duplicate source-only modes")
    allowed = {"--source-sha256", "--protocol-sha256", "--contract-sha256"}
    options: dict[str, str] = {"mode": mode}
    index = 0
    while index < len(arguments):
        item = arguments[index]
        if item == mode:
            index += 1
            continue
        need(
            item in allowed and item not in options and index + 1 < len(arguments),
            "reject private root, native, worker, archive, or ambiguous source authorization",
        )
        options[item] = exact_digest(arguments[index + 1], item)
        index += 2
    need("--source-sha256" in options and "--protocol-sha256" in options, "independently pin the exact source and protocol")
    if mode == "--render-contract":
        need("--contract-sha256" not in options, "contract rendering must not pre-authorize an actual owner")
    else:
        need("--contract-sha256" in options, "independently pin the exact frozen machine contract")
    return options


def rejected_control(label: str, action: object) -> str:
    try:
        action()
    except CampaignError:
        return label
    raise CampaignError("accepted forbidden source-only control: " + label)


def hostile_controls(wall: SourceWall) -> list[str]:
    controls: list[tuple[str, object]] = []
    for name in (
        "re",
        "_sre",
        "regex",
        "re2",
        "ctypes",
        "cffi",
        "subprocess",
        "socket",
        "threading",
        "multiprocessing",
        "time",
        "gzip",
        "zipfile",
        "tarfile",
        "candidates.vm_candidate",
        "candidates.rust_candidate",
    ):
        controls.append(("forbidden import " + name, lambda item=name: builtins.__import__(item)))
    controls.extend(
        (
            (
                "canonical installed native",
                lambda: os.open(
                    ROOT + "/candidates/_vm_native.cpython-314-x86_64-linux-gnu.so",
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                ),
            ),
            (
                "shared-prefix private build root",
                lambda: os.open(
                    "/tmp/rebar-phase2-native-build-v8-c-6khmorpw",
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                ),
            ),
            (
                "sealed C16 build archive",
                lambda: os.open(
                    ROOT
                    + "/oracle/phase2/evidence/native-source-build-v16-c-phase2-v16-c-"
                    + "subject-buffer-original-p0.json.gz",
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                ),
            ),
            (
                "unseen final holdout",
                lambda: os.open(
                    ROOT + "/performance/holdout/forbidden.json",
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                ),
            ),
            (
                "Python-level source-file open",
                lambda: builtins.open(ROOT + "/GOAL.md", "rb"),
            ),
            (
                "workspace creation",
                lambda: os.open(
                    ROOT + "/.rebar-c16-campaign-forbidden",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    0o600,
                ),
            ),
            ("private-root listing", lambda: os.listdir("/tmp")),
            ("native path stat", lambda: os.stat(ROOT + "/candidates/_vm_native.c")),
            ("candidate replacement", lambda: os.replace("forbidden-a", "forbidden-b")),
            ("worker process", lambda: os.system("false")),
            ("interpreter pipe", lambda: os.pipe()),
            ("native activation sync", lambda: os.fsync(0)),
            ("benchmark clock", lambda: os.times()),
            ("unproven actual campaign", lambda: parse_options(["--run"])),
            ("unproven actual worker", lambda: parse_options(["--worker"])),
            ("unproven recovery", lambda: parse_options(["--recover"])),
            (
                "caller-supplied guessed private root",
                lambda: parse_options(
                    [
                        "--verify-frozen-context",
                        "--build-root",
                        "/tmp/rebar-phase2-native-build-v8-c-6khmorpw",
                    ]
                ),
            ),
        )
    )
    rejected = [rejected_control(label, action) for label, action in controls]
    need(
        len(rejected) >= 30
        and len(wall.blocked) >= 10
        and sum(wall.blocked.values()) >= 25,
        "require physically denied candidate, archive, process, root, clock, and activation controls",
    )
    matcher_free()
    return rejected


def source_operation(options: dict) -> tuple[types.ModuleType, dict]:
    matcher_free()
    with SourceWall() as wall:
        own_source = read_dynamic(SOURCE, options["--source-sha256"])
        need(
            hashlib.sha256(own_source).hexdigest() == options["--source-sha256"],
            "reject the substituted complete C16 campaign source",
        )
        read_dynamic(PROTOCOL, options["--protocol-sha256"])
        raw_by_path = {item[0]: read_owner(item) for item in STATIC_OWNERS}
        producer = load_producer(raw_by_path[PRODUCER[0][0]])
        context = validate_context(raw_by_path, producer)
        expected = contract_document(
            context,
            options["--source-sha256"],
            options["--protocol-sha256"],
        )
        if options["mode"] != "--render-contract":
            raw_contract = read_dynamic(CONTRACT, options["--contract-sha256"])
            document = parse_document(producer, raw_contract, "independently pinned C16 V5 campaign contract")
            need(
                producer.canonical(document) == raw_contract and document == expected,
                "reject a changed, noncanonical, falsely qualifying, or unpinned C16 campaign contract",
            )
        rejected = hostile_controls(wall)
        observed = {
            "schema": SCHEMA
            + (
                "-self-test"
                if options["mode"] == "--self-test"
                else "-frozen-context"
            ),
            "status": "PASS",
            "source_sha256": options["--source-sha256"],
            "protocol_sha256": options["--protocol-sha256"],
            "contract_sha256": options.get("--contract-sha256"),
            "phase_one_readiness": "PASS",
            "original_case_execution_denominator": ORIGINAL_CASES,
            "original_suite_count": len(SUITES),
            "named_private_waiver_count": PRIVATE_WAIVERS,
            "supplemental_case_count": SUPPLEMENTAL_CASES,
            "supplemental_cases_counted_in_original_denominator": False,
            "original_producer_version": 5,
            "runtime_guard_version": 2,
            "overview_version": 86,
            "authenticated_evidence_owner_lower_bound": 277,
            "authenticated_history_reference_lower_bound": 282,
            "historical_c10_mismatch_count": 1262,
            "historical_c10_individually_authenticated_worker_count": len(SUITES),
            "historical_c15_mismatch_count": 1230,
            "historical_c15_verified_passing_case_count": 7325,
            "historical_c15_actual_candidate_workers": len(SUITES),
            "c16_build_status": "PASS",
            "c16_actual_compiler_process_count": 14,
            "c16_actual_source_apply_count": 2,
            "c16_root_provenance": ROOT_PROVENANCE,
            "required_fresh_source_build_version": 18,
            "fresh_source_build": "NOT RUN",
            "required_fresh_root_provenance_version": 18,
            "fresh_root_provenance": "NOT PUBLISHED",
            "c16_actual_campaign": "NOT RUN",
            "actual_run_authorization": "BLOCKED",
            "source_owner_read_count": wall.read_count,
            "rejected_hostile_control_count": len(rejected),
            "rejected_hostile_controls": rejected,
            "physically_blocked_controls": dict(wall.blocked),
            "actual_candidate_imports": 0,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_compiler_processes": 0,
            "actual_guard_installations": 0,
            "actual_native_libraries_loaded": 0,
            "actual_private_roots_opened": 0,
            "actual_archives_opened": 0,
            "actual_workspace_mutations": 0,
            "actual_network_requests": 0,
            "actual_clock_samples": 0,
            "actual_holdout_cases_read": 0,
            "candidate_matching": "NOT RUN",
            "candidate_qualification": "BLOCKED",
            "qualified_candidate_count": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "historical_holdout_case_count": 4194304,
            "expanded_holdout_proposal_case_count": 14155776,
            "holdout": "NOT OPENED",
            "winner_selected": False,
        }
    matcher_free()
    if options["mode"] == "--render-contract":
        return producer, expected
    return producer, observed


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_options(sys.argv[1:] if arguments is None else arguments)
        producer, result = source_operation(options)
        sys.stdout.buffer.write(producer.canonical(result))
        sys.stdout.buffer.flush()
        return 0
    except Exception as error:
        sys.stderr.write("C16 original campaign rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
