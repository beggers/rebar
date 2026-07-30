#!/usr/bin/env python3
"""Freeze the measured Zig finalizer correction without running a matcher."""

from __future__ import annotations

import _thread
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
SELF = "tools/apply_owned_zig_deallocator_setattr_source_repair_v2.py"
PROTOCOL = "oracle/phase2/ZIG-DEALLOCATOR-SETATTR-SOURCE-REPAIR-V2.md"
CONTRACT = "oracle/phase2/zig-deallocator-setattr-source-repair-v2.json"
SCHEMA = "rebar-owned-zig-deallocator-setattr-source-repair-v2"
LABEL = "phase2-v13-zig-guard-clean-lifetime-setattr-v2-source-repair"
DEVICE = 2064
MAX_OWNER_BYTES = 8 * 1024 * 1024
GOAL = (
    "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756,
    31364044,
)
V1 = (
    (
        "tools/apply_owned_zig_deallocator_lifetime_source_repair_v1.py",
        "2d2be05fb04d43c453b7e4cd47dc8f55542eeb06b18058c996751b7e8a476e4e",
        85494,
        430556,
    ),
    (
        "oracle/phase2/ZIG-DEALLOCATOR-LIFETIME-SOURCE-REPAIR-V1.md",
        "88dbdad010617a1930bb7e701b8dca02078ab8b6310257bf7f404fc540f3a1bb",
        7910,
        525011,
    ),
    (
        "oracle/phase2/zig-deallocator-lifetime-source-repair-v1.json",
        "2021cca12e9c04ab421dca4fd7cc81e23ffe3b649317eb184dba21e47c6aad4e",
        17782,
        525014,
    ),
)
V13 = (
    (
        "tools/run_owned_repaired_zig_original_campaign_v13.py",
        "fa46d4029f5590adceb22bfe4e612248da5f7f90ed6362d58faa5b631fee7ff8",
        246570,
        430932,
    ),
    (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md",
        "6b42893161e37baec1695aefb414fb7179b778f2164018b024bd68b3c9bb5c2c",
        9553,
        525201,
    ),
    (
        "oracle/phase2/repaired-zig-original-campaign-v13.json",
        "327b14096e36c7a2e4cab977a452fc2477fbf148396f50433cbf1dc8aba31a3f",
        106084,
        525206,
    ),
)
ACTUAL_V13 = (
    "oracle/phase2/evidence/"
    "repaired-zig-original-campaign-v13-"
    "phase2-v13-zig-guard-clean-lifetime-v1-"
    "original-p0-v13-failures-publication-receipt.json",
    "b3443a647c638cbbbe7905a2c668a734770f38cb678f06a387af497917fc4bca",
    78911,
    525299,
)
LIFETIME_INPUT = (
    "candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/"
    "zig_candidate.py",
    "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50",
    67294,
    525010,
)
PROSPECTIVE_VARIANT = (
    "candidates/zig/variants/"
    "scanner_phrase_guard_clean_lifetime_setattr_v2/zig_candidate.py"
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
PASSING = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
MISMATCHES = (
    ("scanner_verbose_v1", 620),
    ("public_types_v1", 248),
    ("substitution_v2", 64),
    ("shape_v2", 672),
    ("public_surface_v19", 96),
)
OLD_DEALLOCATOR = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            self._handle = None\n"
    "            _free(handle)\n"
)
NEW_DEALLOCATOR = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr, "
    "_setattr=object.__setattr__):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            _setattr(self, \"_handle\", None)\n"
    "            _free(handle)\n"
)
ZERO_KEYS = (
    "actual_candidate_imports",
    "actual_candidate_workers",
    "actual_reference_workers",
    "benchmark_files_opened",
    "candidate_processes_started",
    "canonical_targets_modified",
    "clock_samples",
    "compiler_processes_started",
    "files_written",
    "holdout_files_opened",
    "matching_archives_inflated",
    "matching_archives_opened",
    "native_activations",
    "native_libraries_loaded",
    "native_owner_preloads",
    "network_requests",
    "private_roots_opened",
    "private_snapshots_opened",
    "recovery_journals_created",
    "recovery_roots_created",
    "subinterpreter_case_executions",
    "subinterpreter_guards_installed",
    "subinterpreters_created",
    "threads_started",
    "timing_trials_run",
)
CALLER_PINS = (
    ("--v1-source-sha256", V1[0][1]),
    ("--v1-protocol-sha256", V1[1][1]),
    ("--v1-contract-sha256", V1[2][1]),
    ("--v13-source-sha256", V13[0][1]),
    ("--v13-protocol-sha256", V13[1][1]),
    ("--v13-contract-sha256", V13[2][1]),
    ("--receipt-sha256", ACTUAL_V13[1]),
    ("--adapter-sha256", LIFETIME_INPUT[1]),
)
BLOCKED_IMPORTS = frozenset({
    "_interpreters", "_sre", "concurrent", "ctypes", "gzip", "json",
    "multiprocessing", "pathlib", "pytest", "re", "re2", "regex",
    "socket", "ssl", "subprocess", "tempfile", "threading", "time",
    "unittest",
})
MUTATING_OPEN_FLAGS = (
    os.O_CREAT
    | os.O_TRUNC
    | os.O_APPEND
    | getattr(os, "O_TMPFILE", 0)
)
REAL_OPEN = os.open
ACTIVE_WALL = None


class CampaignError(Exception):
    """An authentic source, measured failure, or source boundary changed."""


class SyntheticReleaseError(Exception):
    """A locally manufactured native-release failure; never suppress it."""


class SyntheticSetterError(Exception):
    """The ordinary public setter must never run during finalization."""


def require(condition, message):
    if condition is not True:
        raise CampaignError(message)


def pin(value, label):
    require(
        type(value) is str
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value),
        "reject an incomplete " + label + " SHA-256",
    )
    return value


def digest(data):
    require(type(data) is bytes, "hash only complete first-party bytes")
    return hashlib.sha256(data).hexdigest()


def relative(path):
    require(
        type(path) is str
        and bool(path)
        and not path.startswith("/")
        and "\\" not in path
        and "\x00" not in path
        and all(part not in ("", ".", "..") for part in path.split("/")),
        "reject a noncanonical first-party owner path",
    )
    return path


def record(owner):
    return {
        "path": owner[0],
        "sha256": owner[1],
        "bytes": owner[2],
        "device": DEVICE,
        "inode": owner[3],
        "mode": "0600",
        "nlink": 1,
    }


def read_owner(owner):
    require(
        type(owner) is tuple
        and len(owner) == 4
        and relative(owner[0]) == owner[0]
        and bool(pin(owner[1], owner[0]))
        and type(owner[2]) is int
        and 0 < owner[2] <= MAX_OWNER_BYTES
        and type(owner[3]) is int
        and owner[3] > 0,
        "reject an incomplete physical source owner",
    )
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    fd = REAL_OPEN(ROOT + "/" + owner[0], flags)
    try:
        before = os.fstat(fd)
        require(
            stat.S_ISREG(before.st_mode)
            and before.st_dev == DEVICE
            and before.st_ino == owner[3]
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_size == owner[2],
            "reject a substituted source owner: " + owner[0],
        )
        pieces = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(fd, min(remaining, 262144))
            require(bool(chunk), "reject truncated source: " + owner[0])
            pieces.append(chunk)
            remaining -= len(chunk)
        require(not os.read(fd, 1), "reject extended source: " + owner[0])
        data = b"".join(pieces)
        after = os.fstat(fd)
        require(
            digest(data) == owner[1]
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
            "reject a changed complete first-party source: " + owner[0],
        )
        return data
    finally:
        os.close(fd)


def dynamic_owner(path, expected):
    relative(path)
    pin(expected, path)
    info = os.stat(ROOT + "/" + path, follow_symlinks=False)
    owner = (path, expected, info.st_size, info.st_ino)
    read_owner(owner)
    return owner


def load_owner(owner, name):
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[0]
    exec(
        compile(read_owner(owner), module.__file__, "exec", dont_inherit=True),
        module.__dict__,
    )
    require(module.__name__ == name, "reject substituted source module")
    return module


def clean():
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
            item == "candidates" or item.startswith("candidates.")
            for item in sys.modules
        ),
        "require clean isolated pinned Python and no candidate or matcher",
    )


class SourceWall:
    """Deny physical matching, native loading, processes, archives and writes."""

    def __init__(self):
        self.allowed = {
            ROOT + "/" + path
            for path in (SELF, PROTOCOL, CONTRACT)
        }
        self.allow_owners((GOAL, *V1, *V13, ACTUAL_V13, LIFETIME_INPUT))
        self.saved = {}
        self.active = False
        self.denials = 0

    def allow_owners(self, owners):
        for owner in owners:
            require(
                type(owner) is tuple and len(owner) == 4,
                "reject an unauthenticated expanded source allowlist",
            )
            self.allowed.add(ROOT + "/" + relative(owner[0]))

    def allow_suite(self, suite):
        self.allowed.add(ROOT + "/" + relative(suite.source_relative))

    def deny(self, reason):
        self.denials += 1
        raise CampaignError("source-only wall rejected " + reason)

    def imported(self, name, globals=None, locals=None, fromlist=(), level=0):
        if (
            type(name) is not str
            or name.split(".", 1)[0] in BLOCKED_IMPORTS
            or name == "candidates"
            or name.startswith("candidates.")
            or name == "performance"
            or name.startswith("performance.")
        ):
            self.deny("candidate, matching, native, process or timing import")
        return self.saved["import"](name, globals, locals, fromlist, level)

    def opened(self, path, flags, mode=0o777, *, dir_fd=None):
        if (
            dir_fd is not None
            or type(path) is not str
            or path not in self.allowed
            or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        ):
            self.deny("unlisted, native, archive, holdout or write open")
        return self.saved["open"](path, flags, mode)

    def blocked(self, *args, **kwargs):
        self.deny("source mutation, process, native load, thread or network")

    def audit(self, event, args):
        if not self.active:
            return
        if event == "open":
            if len(args) < 3:
                self.deny("incomplete physical open audit")
            path, mode, flags = args[:3]
            if (
                type(path) is not str
                or path not in self.allowed
                or (mode is not None and mode not in ("r", "rb"))
                or type(flags) is not int
                or flags & os.O_ACCMODE != os.O_RDONLY
                or flags & MUTATING_OPEN_FLAGS
            ):
                label = path if type(path) is str else repr(path)
                self.deny("non-read-only physical owner: " + label)
        elif event == "import":
            name = args[0] if args else None
            if (
                type(name) is not str
                or name.split(".", 1)[0] in BLOCKED_IMPORTS
                or name == "candidates"
                or name.startswith("candidates.")
                or name == "performance"
                or name.startswith("performance.")
            ):
                self.deny("direct matcher, candidate, or timing import audit")
        elif (
            event.startswith((
                "ctypes.", "subprocess.", "socket.", "os.",
                "_thread.start", "_interpreters.",
            ))
            or event in {
                "cpython.PyInterpreterState_New",
            }
        ):
            self.deny(
                "filesystem mutation, native loading, worker, or interpreter"
            )

    def __enter__(self):
        global ACTIVE_WALL
        require(ACTIVE_WALL is None, "reject nested source-only walls")
        self.saved["import"] = builtins.__import__
        self.saved["builtin_open"] = builtins.open
        self.saved["open"] = os.open
        builtins.__import__ = self.imported
        builtins.open = self.blocked
        os.open = self.opened
        for name in (
            "system", "popen", "fork", "mkdir", "makedirs", "rename",
            "replace", "unlink", "remove", "rmdir", "link", "symlink",
            "chdir", "putenv", "unsetenv", "posix_spawn", "posix_spawnp",
            "chmod", "fchmod", "chown", "fchown", "lchown", "utime",
            "truncate", "ftruncate", "chflags", "forkpty", "listdir",
            "scandir",
        ):
            if hasattr(os, name):
                self.saved["os." + name] = getattr(os, name)
                setattr(os, name, self.blocked)
        sys.addaudithook(self.audit)
        ACTIVE_WALL = self
        self.active = True
        return self

    def __exit__(self, kind, value, traceback):
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


def exact_excerpt(row):
    excerpt = row.get("stderr_literal_excerpt")
    stream = row.get("stderr")
    require(
        type(excerpt) is dict
        and type(stream) is dict
        and excerpt.get("status") == "CAPTURED"
        and excerpt.get("encoding") == "UTF-8; INVALID BYTES BACKSLASH-ESCAPED"
        and excerpt.get("limit_bytes") == 4096
        and type(excerpt.get("captured_bytes")) is int
        and 0 < excerpt["captured_bytes"] <= 4096
        and excerpt.get("total_bytes") == stream.get("bytes")
        and excerpt.get("sha256") == stream.get("sha256")
        and excerpt.get("truncated")
        is (excerpt["captured_bytes"] < excerpt["total_bytes"])
        and type(excerpt.get("text")) is str,
        "reject the complete, genuinely captured V13 stderr excerpt",
    )
    text = excerpt["text"]
    require(
        "Exception ignored while calling deallocator" in text
        and "line 1086, in __del__" in text
        and "line 1079, in __setattr__" in text
        and "TypeError: argument of type 'NoneType' is not a container or iterable"
        in text,
        "reject or suppress the measured V13 finalizer-to-setter failure",
    )


def validate_v13_publication(receipt, campaign):
    require(
        type(receipt) is dict
        and receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v13-"
           "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and receipt.get("source_sha256") == V13[0][1]
        and receipt.get("protocol_sha256") == V13[1][1]
        and receipt.get("contract_sha256") == V13[2][1]
        and receipt.get("family") == "zig"
        and receipt.get("label")
        == "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13"
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
        == [name for name, _ in MISMATCHES] + ["subinterpreter_v2"]
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("original_campaign_passed") is False
        and receipt.get("all_three_original_targets_restored") is True
        and receipt.get("per_suite_timeout_seconds") == 120
        and receipt.get("maximum_serial_worker_timeout_seconds") == 1560
        and receipt.get("timeout_count") == 0
        and receipt.get("timed_out_suites") == []
        and receipt.get("timeout_classification") == "INFRASTRUCTURE FAILURE"
        and receipt.get("supplemental_candidate_matching") == "NOT RUN"
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("undefined_behavior") == "NOT MEASURED"
        and receipt.get("winner_selected") is False
        and receipt.get("uncompressed_bytes") == 192348645
        and receipt.get("uncompressed_sha256")
        == "864ffdf6c1a565062b32099ca1717ad5f676d8c3c5e7851ef8d20bd504a936c6",
        "reject, suppress, or exaggerate the genuine V13 candidate failure",
    )
    archive = receipt.get("archive")
    require(
        type(archive) is dict
        and set(archive) == {
            "name", "sha256", "bytes", "device", "inode", "mode",
            "nlink", "uid",
        }
        and archive.get("name")
        == "repaired-zig-original-campaign-v13-"
           "phase2-v13-zig-guard-clean-lifetime-v1-"
           "original-p0-v13-failures.json.gz"
        and archive.get("sha256")
        == "2d277e78ba5c87f9e1566e968369754290d848fd5f58b6adafc8b840c05908da"
        and archive.get("bytes") == 5615638
        and archive.get("device") == DEVICE
        and archive.get("inode") == 525298
        and archive.get("mode") == 0o600
        and archive.get("nlink") == 1
        and archive.get("uid") == os.geteuid(),
        "reject the exact V13 archive metadata without opening the archive",
    )
    rows = receipt.get("original_suite_diagnostics")
    require(
        type(rows) is list
        and len(rows) == 13
        and tuple(
            (row.get("suite"), row.get("case_execution_denominator"))
            for row in rows
        ) == SUITES
        and all(type(row.get("pid")) is int and row["pid"] > 0 for row in rows)
        and len({row["pid"] for row in rows}) == 13
        and all(
            row.get("returncode") == 0
            and row.get("guard_installed_before_candidate_import") is True
            and row.get("candidate_imported") is True
            and row.get("timed_out") is False
            and row.get("timeout_classification") == "NOT TIMED OUT"
            and row.get("timeout_seconds") == 120
            for row in rows
        ),
        "require all 13 distinct, genuinely guarded V13 candidate workers",
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
        passing == PASSING
        and sum(count for _, count in passing) == 4607
        and measured == MISMATCHES
        and sum(count for _, count in measured) == 1700,
        "preserve all seven actual passes and all five genuine V13 losses",
    )
    for row in rows:
        for key in ("stdout", "stderr"):
            stream = row.get(key)
            require(
                type(stream) is dict
                and type(stream.get("bytes")) is int
                and stream["bytes"] > 0
                and stream.get("complete") is True
                and stream.get("complete_payload_preserved_in_actual_archive")
                is True
                and bool(pin(stream.get("sha256"), "actual " + key)),
                "reject complete actual V13 worker stream metadata",
            )
        exact_excerpt(row)
    require(
        sum(row["stdout"]["bytes"] for row in rows) == 82236727
        and sum(row["stderr"]["bytes"] for row in rows) == 428866
        and sum(
            row["stderr_literal_excerpt"]["captured_bytes"] for row in rows
        ) == 53211
        and len({row["stdout"]["sha256"] for row in rows}) == 13
        and len({row["stderr"]["sha256"] for row in rows}) == 13,
        "preserve complete genuine stream identities and all warning bytes",
    )
    failed = [row for row in rows if row.get("suite") == "subinterpreter_v2"]
    require(len(failed) == 1, "require the genuine failed child lifecycle")
    row = failed[0]
    nested = row.get("complete_actual_suite_failure_details")
    original = (
        nested.get("complete_original_failure_details")
        if type(nested) is dict else None
    )
    require(
        row.get("status") == "FAIL"
        and row.get("infrastructure_failure") is True
        and row.get("actual_worker_schema")
        == "rebar-owned-repaired-zig-original-campaign-v13-actual-worker-failure"
        and row.get("activation_stage")
        == "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
        and row.get("error_type") == "ActualSuiteFailure"
        and row.get("error_message")
        == "preserve the actual guarded original child lifecycle failure"
        and row.get("observed_semantic_mismatch_count") == "NOT MEASURED"
        and type(nested) is dict
        and nested.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-genuine-nested-failure"
        and nested.get("status") == "FAIL"
        and nested.get("error_type") == "ActualSuiteFailure"
        and nested.get("error_message")
        == "retain every genuine failed private-interpreter call and cleanup"
        and nested.get("guard_source_sha256") == campaign.GUARD_V2[0][1]
        and nested.get("guard_protocol_sha256") == campaign.GUARD_V2[1][1]
        and nested.get("guard_contract_sha256") == campaign.GUARD_V2[2][1]
        and nested.get("actual_child_guards_installed") == 0
        and nested.get("actual_candidate_subprocesses") == 0
        and nested.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and nested.get("expected_interpreters_created") == 11
        and nested.get("expected_case_interpreter_exec_calls") == 394
        and nested.get("hidden_cases_read") == 0
        and nested.get("benchmark_files_read") == 0
        and nested.get("clock_samples") == 0
        and nested.get("timing_trials_run") == 0
        and nested.get("holdout") == "NOT OPENED"
        and nested.get("performance") == "NOT MEASURED"
        and nested.get("winner_selected") is False
        and type(original) is dict
        and original.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v4-genuine-nested-failure"
        and original.get("status") == "FAIL"
        and original.get("active_phase")
        == "create-genuine-owned-interpreter-A"
        and original.get("error_type") == "GuardError"
        and original.get("error_message")
        == "runtime guard blocked missing-or-fabricated-native-child-creation"
        and original.get("actual_prepared_interpreter_ids") == []
        and original.get("actual_case_interpreter_exec_calls") == 0
        and original.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and original.get("actual_initialization_interpreter_exec_calls") == 0
        and original.get("actual_interpreters_created") == 0
        and original.get("actual_interpreters_destroyed") == 0
        and original.get("completed_a_records") == []
        and original.get("completed_b_records") == [],
        "never invent a real interpreter, installed child guard, or match",
    )
    return {
        "passing_suites": passing,
        "semantic_failures": measured,
        "warning_suites": tuple(row["suite"] for row in rows),
        "stdout_bytes": 82236727,
        "stderr_bytes": 428866,
        "captured_warning_bytes": 53211,
        "original_subinterpreter_failure": original,
    }


def prove_setattr_adapter(original, corrected, predecessor):
    require(
        type(original) is bytes
        and len(original) == LIFETIME_INPUT[2]
        and digest(original) == LIFETIME_INPUT[1],
        "require the complete exactly frozen V1 lifetime adapter",
    )
    old = OLD_DEALLOCATOR.encode("utf-8")
    new = NEW_DEALLOCATOR.encode("utf-8")
    require(
        original.count(old) == 1
        and original.count(b"    def __del__(") == 1
        and type(corrected) is bytes
        and corrected.count(new) == 1
        and corrected.count(b"    def __del__(") == 1
        and original.replace(old, new, 1) == corrected,
        "reject any change beyond the one authenticated finalizer block",
    )
    original_tree = ast.parse(original.decode("utf-8", "strict"))
    corrected_tree = ast.parse(corrected.decode("utf-8", "strict"))
    old_pattern, old_method = predecessor.pattern_node(
        original_tree, "published V13 lifetime",
    )
    new_pattern, new_method = predecessor.pattern_node(
        corrected_tree, "prospective cached-setter lifetime",
    )
    old_snippet = ast.parse("class Pattern:\n" + OLD_DEALLOCATOR).body[0].body[0]
    new_snippet = ast.parse("class Pattern:\n" + NEW_DEALLOCATOR).body[0].body[0]
    require(
        ast.dump(old_method, include_attributes=False)
        == ast.dump(old_snippet, include_attributes=False)
        and ast.dump(new_method, include_attributes=False)
        == ast.dump(new_snippet, include_attributes=False),
        "reject changed exact finalizer defaults, assignment or release order",
    )
    args = new_method.args
    require(
        [item.arg for item in args.args]
        == ["self", "_free", "_getattr", "_setattr"]
        and not args.posonlyargs
        and not args.kwonlyargs
        and args.vararg is None
        and args.kwarg is None
        and len(args.defaults) == 3
        and isinstance(args.defaults[0], ast.Attribute)
        and isinstance(args.defaults[0].value, ast.Name)
        and args.defaults[0].value.id == "_zig_bridge"
        and args.defaults[0].attr == "free"
        and isinstance(args.defaults[1], ast.Name)
        and args.defaults[1].id == "getattr"
        and isinstance(args.defaults[2], ast.Attribute)
        and isinstance(args.defaults[2].value, ast.Name)
        and args.defaults[2].value.id == "object"
        and args.defaults[2].attr == "__setattr__"
        and not any(
            isinstance(item, (ast.Try, ast.TryStar, ast.ExceptHandler))
            for item in ast.walk(new_method)
        ),
        "require the genuine early-bound bridge, getattr and object setter",
    )
    setters_before = [
        item for item in old_pattern.body
        if isinstance(item, ast.FunctionDef) and item.name == "__setattr__"
    ]
    setters_after = [
        item for item in new_pattern.body
        if isinstance(item, ast.FunctionDef) and item.name == "__setattr__"
    ]
    require(
        len(setters_before) == len(setters_after) == 1
        and ast.dump(setters_before[0], include_attributes=False)
        == ast.dump(setters_after[0], include_attributes=False),
        "reject changed public Pattern attribute behavior",
    )
    index = next(
        index for index, node in enumerate(old_pattern.body)
        if node is old_method
    )
    old_pattern.body[index] = new_method
    require(
        ast.dump(original_tree, include_attributes=False)
        == ast.dump(corrected_tree, include_attributes=False),
        "reject any changed parser, compiler, matcher, scanner or bridge",
    )
    return {
        "original_destructor_count": 1,
        "corrected_destructor_count": 1,
        "changed_source_block_count": 1,
        "changed_ast_node_count": 1,
        "complete_other_ast_unchanged": True,
        "matcher_parser_compiler_scanner_changed": False,
        "public_pattern_setter_changed": False,
        "instance_slots_changed": False,
        "bridge_or_native_source_changed": False,
        "native_release_default": "_zig_bridge.free",
        "attribute_lookup_default": "getattr",
        "attribute_write_default": "object.__setattr__",
        "bypasses_module_global_pattern_methods": True,
        "bypasses_user_defined_pattern_setter": True,
        "release_handle_cleared_before_call": True,
        "release_error_suppressed": False,
        "reentrant_release_is_at_most_once": True,
        "half_initialized_instance_supported": True,
    }


def original_targets(campaign):
    roles = campaign.ORIGINALS
    require(
        type(roles) is dict and set(roles) == {"adapter", "bridge", "engine"},
        "reject the exact three authentic original Zig physical owners",
    )
    results = []
    for role in ("adapter", "bridge", "engine"):
        expected = roles[role]
        path = expected.get("relative")
        relative(path)
        info = os.stat(ROOT + "/" + path, follow_symlinks=False)
        require(
            stat.S_ISREG(info.st_mode)
            and info.st_dev == expected.get("device") == DEVICE
            and info.st_ino == expected.get("inode")
            and info.st_size == expected.get("bytes")
            and info.st_uid == expected.get("uid") == os.geteuid()
            and info.st_nlink == expected.get("nlink") == 1
            and stat.S_IMODE(info.st_mode) == expected.get("mode")
            and bool(pin(expected.get("sha256"), role + " original owner")),
            "reject a changed or unrestored exact original Zig " + role,
        )
        results.append({
            "role": role,
            "path": path,
            "sha256": expected["sha256"],
            "bytes": expected["bytes"],
            "device": expected["device"],
            "inode": expected["inode"],
            "mode": format(expected["mode"], "04o"),
            "nlink": 1,
            "identity_verified_without_opening": True,
        })
    return results


def context(source_sha, protocol_sha, args, wall):
    clean()
    for option, expected in CALLER_PINS:
        require(
            pin(args.get(option), option) == expected,
            "reject an independent " + option + " caller pin",
        )
    source = dynamic_owner(SELF, source_sha)
    protocol = dynamic_owner(PROTOCOL, protocol_sha)
    read_owner(GOAL)
    previous = load_owner(V1[0], "_rebar_zig_setattr_v2_exact_lifetime_v1")
    require(
        previous.SELF == V1[0][0]
        and previous.PROTOCOL == V1[1][0]
        and previous.CONTRACT == V1[2][0]
        and previous.LIFETIME_ADAPTER == LIFETIME_INPUT
        and previous.REPAIRED_DEALLOCATOR == OLD_DEALLOCATOR
        and previous.SUITES == SUITES,
        "reject the exact published V1 first-party lifetime implementation",
    )
    wall.allow_owners(previous.owners())
    immutable = load_owner(
        previous.PRODUCER[0], "_rebar_zig_setattr_v2_immutable_v5_json",
    )
    require(
        immutable.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
        and immutable.CASE_DENOMINATOR == 31237
        and immutable.SUITE_COUNT == 13
        and immutable.PRIVATE_WAIVER_COUNT == 13
        and immutable.ORIGINAL_OBLIGATION_COUNT == 73
        and immutable.ORIGINAL_CROSSWALK_COUNT == 34
        and immutable.SUPPLEMENTAL_CASE_COUNT == 8244
        and tuple((row.name, row.case_count) for row in immutable.SUITES)
        == SUITES,
        "reject the exact frozen independent original Python correctness oracle",
    )
    for suite in immutable.SUITES:
        wall.allow_suite(suite)
    previous_state = previous.verify(V1[0][1], V1[1][1], V1[2][1])
    campaign = load_owner(V13[0], "_rebar_zig_setattr_v2_exact_campaign_v13")
    require(
        campaign.SELF == V13[0][0]
        and campaign.PROTOCOL == V13[1][0]
        and campaign.CONTRACT == V13[2][0]
        and campaign.LIFETIME_FREEZE == V1
        and campaign.LIFETIME_ADAPTER == LIFETIME_INPUT
        and campaign.SUITES == SUITES,
        "reject the exact frozen V13 genuinely guarded first-party campaign",
    )
    wall.allow_owners(campaign.owners(active=False))
    campaign_state = campaign.verify(
        V13[0][1], V13[1][1], V13[2][1], active=False,
    )
    require(
        campaign_state["proof"]["complete_other_ast_unchanged"] is True
        and campaign_state["proof"]["changed_ast_node_count"] == 1
        and campaign_state["proof"]["release_handle_cleared_before_call"]
        is True
        and campaign_state["guard_implementation"].CREATE_EVENT
        == "cpython.PyInterpreterState_New"
        and campaign_state["guard_implementation"].RuntimePolicy.prepare_family
        is campaign_state["guard_implementation"].BASE.RuntimePolicy.prepare_family
        and campaign_state["guard_implementation"].RuntimePolicy
        .prepare_family.__globals__
        is campaign_state["guard_implementation"].BASE.__dict__,
        "reject the real unchanged inherited V3 interpreter-guard identity",
    )
    raw_receipt = read_owner(ACTUAL_V13)
    producer = campaign_state["producer"]
    receipt = producer.JsonReader(raw_receipt).parse()
    require(
        producer.canonical(receipt) == raw_receipt,
        "reject a noncanonical or altered actual V13 plaintext receipt",
    )
    actual = validate_v13_publication(receipt, campaign)
    original = read_owner(LIFETIME_INPUT)
    corrected = original.replace(
        OLD_DEALLOCATOR.encode("utf-8"),
        NEW_DEALLOCATOR.encode("utf-8"),
        1,
    )
    proof = prove_setattr_adapter(original, corrected, previous)
    targets = original_targets(campaign)
    clean()
    return {
        "source": source,
        "protocol": protocol,
        "previous": previous,
        "previous_state": previous_state,
        "campaign": campaign,
        "campaign_state": campaign_state,
        "producer": producer,
        "receipt": receipt,
        "actual": actual,
        "original": original,
        "corrected": corrected,
        "proof": proof,
        "original_targets": targets,
    }


def contract_value(state):
    actual = state["actual"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": 2,
        "status": (
            "SOURCE FROZEN; SETTER-SAFE ZIG VARIANT NOT MATERIALIZED OR RUN"
        ),
        "family": "zig",
        "label": LABEL,
        "source": record(state["source"]),
        "protocol": record(state["protocol"]),
        "goal": record(GOAL),
        "pinned_cpython": {
            "path": PYTHON,
            "version": "3.14.6",
            "sha256": (
                "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
            ),
            "isolated": True,
            "bytecode_writes": False,
        },
        "authenticated_v1_lifetime_repair": {
            "owners": [record(owner) for owner in V1],
            "source_freeze_schema": (
                "rebar-owned-zig-deallocator-lifetime-source-repair-v1-"
                "source-freeze"
            ),
            "version": 1,
            "whole_frozen_contract_verified": True,
            "actual_input_adapter": record(LIFETIME_INPUT),
            "original_destructor": OLD_DEALLOCATOR,
            "reproduces_actual_setter_failure": True,
            "source_modified": False,
        },
        "authenticated_v13_original_campaign": {
            "owners": [record(owner) for owner in V13],
            "source_freeze_schema": (
                "rebar-owned-repaired-zig-original-campaign-v13-"
                "guarded-lifetime-source-freeze"
            ),
            "version": 13,
            "whole_frozen_contract_verified": True,
            "real_v3_guard_preserved": True,
            "exact_v2_guard_function_and_globals_preserved": True,
            "original_canonical_target_identities": state["original_targets"],
            "canonical_target_bytes_opened": 0,
            "source_modified": False,
            "candidate_run_by_this_source_freeze": False,
        },
        "actual_v13_failure": {
            "public_plaintext_receipt": record(ACTUAL_V13),
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "candidate_qualified": False,
            "original_campaign_passed": False,
            "all_original_suites_attempted": True,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "actual_candidate_workers": 13,
            "unique_candidate_worker_count": 13,
            "completed_suite_count": 12,
            "verified_passing_suite_count": 7,
            "verified_passing_case_count": 4607,
            "verified_passing_suites": [
                {"suite": name, "cases": count}
                for name, count in actual["passing_suites"]
            ],
            "completed_semantic_failure_count": 5,
            "completed_semantic_failures": [
                {"suite": name, "observed_semantic_mismatch_count": count}
                for name, count in actual["semantic_failures"]
            ],
            "observed_semantic_mismatch_lower_bound": 1700,
            "semantic_mismatch_count": "NOT MEASURED",
            "infrastructure_failure_count": 1,
            "complete_actual_stdout_bytes": actual["stdout_bytes"],
            "complete_actual_stderr_bytes": actual["stderr_bytes"],
            "captured_warning_excerpt_bytes": actual["captured_warning_bytes"],
            "observed_warning_suite_count": 13,
            "observed_passing_suite_warning_count": 7,
            "warning_suite_names": list(actual["warning_suites"]),
            "literal_warning": "Exception ignored while calling deallocator",
            "finalizer_source_line": 1086,
            "setter_source_line": 1079,
            "literal_error": (
                "TypeError: argument of type 'NoneType' "
                "is not a container or iterable"
            ),
            "warning_after_setter_repair": "NOT MEASURED",
            "matching_archive_opened": False,
            "separate_actual_subinterpreter_failure": {
                "suite": "subinterpreter_v2",
                "activation_stage": (
                    "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
                ),
                "outer_error_type": "ActualSuiteFailure",
                "nested_error_type": "ActualSuiteFailure",
                "actual_child_guards_installed": 0,
                "original_active_phase": (
                    "create-genuine-owned-interpreter-A"
                ),
                "original_error_type": "GuardError",
                "original_error_message": (
                    "runtime guard blocked "
                    "missing-or-fabricated-native-child-creation"
                ),
                "actual_prepared_interpreter_ids": [],
                "actual_case_interpreter_exec_calls": 0,
                "actual_initialization_interpreter_exec_calls": 0,
                "actual_guard_cleanup_interpreter_exec_calls": 0,
                "actual_interpreters_created": 0,
                "actual_interpreters_destroyed": 0,
                "expected_interpreters_created": 11,
                "expected_case_interpreter_exec_calls": 394,
                "semantic_mismatch_count": "NOT MEASURED",
                "setter_repair_fixes_child_bootstrap": "NOT ESTABLISHED",
            },
        },
        "original_oracle": {
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
        "first_party_setter_repair": {
            "published_v13_lifetime_input": record(LIFETIME_INPUT),
            "prospective_variant": {
                "path": PROSPECTIVE_VARIANT,
                "sha256": digest(state["corrected"]),
                "bytes": len(state["corrected"]),
                "physical_status": "NOT MATERIALIZED",
                "device": "NOT CREATED",
                "inode": "NOT CREATED",
            },
            "original_destructor": OLD_DEALLOCATOR,
            "corrected_destructor": NEW_DEALLOCATOR,
            **state["proof"],
            "complete_byte_replacement_proven_in_memory": True,
            "prospective_variant_written": False,
            "candidate_imported": False,
            "native_bridge_loaded": False,
            "native_library_opened": False,
            "candidate_built": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": "NOT MEASURED",
            "candidate_qualified": False,
            "external_regex_dependency_added": False,
            "stdlib_regex_fallback_added": False,
            "cross_candidate_engine_added": False,
        },
        "expanded_sealed_holdout_proposal": {
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
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
        },
        "source_verifier": {
            "allowed_actions": [
                "--self-test",
                "--verify-frozen-context",
                "--render-contract",
            ],
            "independent_caller_pin_count": len(CALLER_PINS),
            "candidate_execution_action_exists": False,
            "native_build_action_exists": False,
            "candidate_install_action_exists": False,
            "physical_source_wall_required": True,
            "physical_open_audit_validates_owner_mode_and_flags": True,
            "direct_io_write_bypass_forbidden": True,
            "direct_import_audit_enforced": True,
            "all_os_audit_events_forbidden": True,
            "synthetic_mutation_controls_never_attempt_real_writes": True,
            "complete_candidate_namespace_import_forbidden": True,
            "stdlib_regex_engine_import_forbidden": True,
            "native_dynamic_loading_forbidden": True,
            "candidate_processes_forbidden": True,
            "private_roots_forbidden": True,
            "matching_archives_forbidden": True,
            "holdout_cases_forbidden": True,
            "all_filesystem_writes_forbidden": True,
            "synthetic_destructor_controls_run_only_in_self_test": True,
            "frozen_predecessor_source_executed_as_candidate": False,
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
            require(self.owner is not None, "require synthetic reentry owner")
            self.owner.__del__()
        if self.failure:
            raise SyntheticReleaseError("genuine synthetic release failure")


def synthetic_pattern(block, *, reenter=False, failure=False):
    require(
        block == OLD_DEALLOCATOR or block == NEW_DEALLOCATOR,
        "reject execution of an unauthenticated synthetic finalizer",
    )
    release = SyntheticRelease(reenter=reenter, failure=failure)
    setter_calls = []
    bridge = types.SimpleNamespace(free=release)
    namespace = {
        "__name__": "_rebar_zig_setattr_v2_synthetic",
        "__builtins__": builtins.__dict__,
        "_zig_bridge": bridge,
        "getattr": builtins.getattr,
        "object": object,
        "_PATTERN_METHODS": ("search", "match"),
        "setter_calls": setter_calls,
        "SyntheticSetterError": SyntheticSetterError,
    }
    source = (
        "class SyntheticPattern:\n"
        "    __slots__ = ('_handle',)\n"
        "    def __setattr__(self, name, value):\n"
        "        setter_calls.append((name, value))\n"
        "        if name in _PATTERN_METHODS:\n"
        "            raise SyntheticSetterError('readonly method')\n"
        "        raise SyntheticSetterError('public setter was invoked')\n"
        + block
    )
    tree = ast.parse(source)
    methods = [
        node for node in tree.body[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "__del__"
    ]
    expected = ast.parse("class Pattern:\n" + block).body[0].body[0]
    require(
        len(methods) == 1
        and ast.dump(methods[0], include_attributes=False)
        == ast.dump(expected, include_attributes=False),
        "reject modified synthetic finalizer source",
    )
    exec(
        compile(
            source, "<first-party-synthetic-zig-setattr-v2>", "exec",
            dont_inherit=True,
        ),
        namespace,
    )
    pattern = namespace["SyntheticPattern"]
    expected_defaults = (
        (release, builtins.getattr, object.__setattr__)
        if block == NEW_DEALLOCATOR else (release, builtins.getattr)
    )
    require(
        pattern.__del__.__defaults__ == expected_defaults
        and pattern.__del__.__defaults__[0] is bridge.free
        and pattern.__del__.__defaults__[1] is builtins.getattr
        and (
            block == OLD_DEALLOCATOR
            or pattern.__del__.__defaults__[2] is object.__setattr__
        ),
        "reject definition-time first-party release and exact object setter",
    )
    return pattern, release, namespace, setter_calls


def synthetic_lifecycle_controls():
    checks = 0

    pattern, release, namespace, setters = synthetic_pattern(OLD_DEALLOCATOR)
    legacy = pattern.__new__(pattern)
    object.__setattr__(legacy, "_handle", 43)
    namespace["_PATTERN_METHODS"] = None
    try:
        legacy.__del__()
    except TypeError as error:
        require(
            "NoneType" in str(error)
            and ("container" in str(error) or "iterable" in str(error)),
            "reject a synthetic reproduction of the measured V13 failure",
        )
    else:
        raise CampaignError("failed to reproduce the actual unsafe V1 setter")
    require(
        setters == [("_handle", None)]
        and release.calls == []
        and object.__getattribute__(legacy, "_handle") == 43,
        "reject the actual old finalizer's public-setter and missed-release path",
    )
    object.__setattr__(legacy, "_handle", None)
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(NEW_DEALLOCATOR)
    target = pattern.__new__(pattern)
    object.__setattr__(target, "_handle", 71)
    namespace["_PATTERN_METHODS"] = None
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    namespace["object"] = None
    target.__del__()
    require(
        release.calls == [71]
        and setters == []
        and object.__getattribute__(target, "_handle") is None
        and pattern.__del__.__defaults__
        == (release, builtins.getattr, object.__setattr__),
        "reject cleanup with all real teardown-sensitive globals destroyed",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [71] and setters == [],
        "reject double release or an overridden public setter",
    )
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(NEW_DEALLOCATOR)
    partial = pattern.__new__(pattern)
    namespace["_PATTERN_METHODS"] = None
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    namespace["object"] = None
    partial.__del__()
    partial.__del__()
    require(
        release.calls == []
        and setters == []
        and not hasattr(partial, "_handle"),
        "reject a partially initialized source-only synthetic pattern",
    )
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(NEW_DEALLOCATOR)
    namespace["_PATTERN_METHODS"] = None
    for value in (None, 0, False):
        target = pattern.__new__(pattern)
        object.__setattr__(target, "_handle", value)
        target.__del__()
    require(
        release.calls == [] and setters == [],
        "reject release or public writes for an absent or false native handle",
    )
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(
        NEW_DEALLOCATOR, reenter=True,
    )
    target = pattern.__new__(pattern)
    object.__setattr__(target, "_handle", 103)
    release.owner = target
    namespace["_PATTERN_METHODS"] = None
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    namespace["object"] = None
    target.__del__()
    release.owner = None
    require(
        release.calls == [103]
        and setters == []
        and object.__getattribute__(target, "_handle") is None,
        "reject a reentrant native double release",
    )
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(
        NEW_DEALLOCATOR, failure=True,
    )
    target = pattern.__new__(pattern)
    object.__setattr__(target, "_handle", 149)
    namespace["_PATTERN_METHODS"] = None
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    namespace["object"] = None
    try:
        target.__del__()
    except SyntheticReleaseError as error:
        require(
            str(error) == "genuine synthetic release failure",
            "reject altered genuine native-release errors",
        )
    else:
        raise CampaignError("suppressed a genuine native-release error")
    require(
        release.calls == [149]
        and setters == []
        and object.__getattribute__(target, "_handle") is None,
        "reject ownership remaining live when a genuine release fails",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [149] and setters == [],
        "reject retrying or hiding a failed genuine native release",
    )
    checks += 1

    pattern, release, namespace, setters = synthetic_pattern(NEW_DEALLOCATOR)
    namespace["_PATTERN_METHODS"] = None
    namespace["_zig_bridge"] = types.SimpleNamespace(
        free=lambda handle: (_ for _ in ()).throw(
            SyntheticReleaseError("poisoned module bridge"),
        ),
    )
    namespace["getattr"] = lambda *args: (_ for _ in ()).throw(
        SyntheticReleaseError("poisoned module getattr"),
    )
    namespace["object"] = types.SimpleNamespace(
        __setattr__=lambda *args: (_ for _ in ()).throw(
            SyntheticSetterError("poisoned module object"),
        ),
    )
    target = pattern.__new__(pattern)
    object.__setattr__(target, "_handle", 211)
    target.__del__()
    require(
        release.calls == [211]
        and setters == []
        and object.__getattribute__(target, "_handle") is None
        and pattern.__del__.__defaults__
        == (release, builtins.getattr, object.__setattr__),
        "reject rebound bridge, lookup, object, or user-defined setter",
    )
    checks += 1
    return checks


def reject(operation, label):
    try:
        operation()
    except (
        CampaignError, OSError, ImportError, SyntaxError, ValueError,
        TypeError, AttributeError, KeyError,
    ):
        return 1
    raise CampaignError("accepted hostile source-only control: " + label)


def cloned(value, producer):
    return producer.JsonReader(producer.canonical(value)).parse()


def mutated_receipt(state, field, value):
    altered = cloned(state["receipt"], state["producer"])
    altered[field] = value
    return altered


def mutated_row(state, suite, field, value, *, nested=False, original=False):
    altered = cloned(state["receipt"], state["producer"])
    rows = altered["original_suite_diagnostics"]
    selected = [row for row in rows if row["suite"] == suite]
    require(len(selected) == 1, "require one authentic poisoned-control row")
    target = selected[0]
    if nested:
        target = target["complete_actual_suite_failure_details"]
        if original:
            target = target["complete_original_failure_details"]
    target[field] = value
    return altered


def hostile_source_controls(state, wall):
    checks = 0
    goal_path = ROOT + "/" + GOAL[0]
    source_path = ROOT + "/" + SELF
    input_path = ROOT + "/" + LIFETIME_INPUT[0]
    valid_read_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    before = wall.denials
    sys.audit("open", goal_path, None, valid_read_flags)
    sys.audit("open", source_path, "r", os.O_RDONLY)
    require(
        wall.denials == before,
        "reject an authenticated immutable read-only open audit",
    )
    checks += 1
    for args, label in (
        (
            (goal_path, "w", os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
            "direct _io goal write and truncate",
        ),
        (
            (source_path, "w", os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
            "direct _io frozen-source write and truncate",
        ),
        (
            (input_path, "w", os.O_WRONLY | os.O_CREAT | os.O_TRUNC),
            "direct _io authentic lifetime-input write",
        ),
        (
            (goal_path, None, os.O_RDONLY | os.O_TRUNC),
            "mode-less descriptor truncation",
        ),
        (
            (source_path, "r+", os.O_RDWR),
            "read-write immutable source descriptor",
        ),
        (
            (input_path, "a", os.O_WRONLY | os.O_CREAT | os.O_APPEND),
            "direct append to the actual first-party source",
        ),
        (
            (source_path, "x", os.O_WRONLY | os.O_CREAT | os.O_EXCL),
            "exclusive immutable-source creation",
        ),
        (
            (source_path, "r", "0"),
            "noninteger physical open flags",
        ),
        (
            (source_path, "r"),
            "missing physical open flags",
        ),
        (
            (source_path, object(), os.O_RDONLY),
            "forged physical open mode",
        ),
        (
            (source_path, None, os.O_RDWR),
            "mode-less read-write file descriptor",
        ),
    ):
        checks += reject(
            lambda values=args: sys.audit("open", *values),
            "synthetic physical audit: " + label,
        )
    for name in (
        "re", "_sre", "regex", "re2", "ctypes", "subprocess",
        "gzip", "candidates", "candidates.zig_candidate",
        "candidates._zig_bridge", "performance.final_holdout",
    ):
        checks += reject(
            lambda item=name: sys.audit(
                "import", item, None, None, None, None,
            ),
            "direct importlib audit bypass " + name,
        )
    for event, args, label in (
        ("os.chmod", (goal_path, 0o600, -1), "goal permission mutation"),
        ("os.chown", (goal_path, os.geteuid(), -1, -1), "goal owner mutation"),
        ("os.utime", (goal_path, None, None, -1), "goal timestamp mutation"),
        ("os.truncate", (goal_path, 0), "goal content truncation"),
        ("os.rename", (source_path, goal_path, -1, -1), "source replacement"),
        ("os.remove", (goal_path, -1), "goal removal"),
        ("os.mkdir", ("/tmp/rebar-zig-setattr-v2-forbidden", 0o700, -1),
         "private recovery root creation"),
        ("os.rmdir", ("/tmp/rebar-zig-setattr-v2-forbidden", -1),
         "private recovery root deletion"),
        ("os.link", (source_path, goal_path, -1, -1), "source hard-link"),
        ("os.symlink", (source_path, goal_path, -1), "source symbolic link"),
        ("os.forkpty", (), "unattested child process"),
        ("os.listdir", ("/tmp",), "private-root enumeration"),
        ("os.scandir", ("/tmp",), "private-root scanner"),
    ):
        checks += reject(
            lambda item=event, values=args: sys.audit(item, *values),
            "synthetic physical mutation audit: " + label,
        )
    for name in sorted(BLOCKED_IMPORTS | {
        "candidates", "candidates.zig_candidate", "candidates.rust_candidate",
        "candidates._zig_bridge", "performance.final_holdout",
    }):
        checks += reject(
            lambda item=name: builtins.__import__(item),
            "forbidden candidate, matcher or timing import " + name,
        )
    forbidden = (
        ROOT + "/candidates/zig_candidate.py",
        ROOT + "/candidates/rust_candidate.py",
        ROOT + "/candidates/_zig_probe.so",
        ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ROOT + "/" + PROSPECTIVE_VARIANT,
        ROOT + "/oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v13-"
        "phase2-v13-zig-guard-clean-lifetime-v1-"
        "original-p0-v13-failures.json.gz",
        ROOT + "/performance/final-holdout.json",
        ROOT + "/performance/v9/holdout-cases.json",
        ROOT + "/README.md",
        "/tmp/rebar-phase2-repaired-zig-original-campaign-v13-"
        "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13",
    )
    for path in forbidden:
        checks += reject(
            lambda item=path: os.open(item, os.O_RDONLY),
            "forbidden source-only physical owner " + path,
        )
    for operation, label in (
        (lambda: os.open(ROOT + "/" + SELF, os.O_WRONLY), "source mutation"),
        (
            lambda: os.open(ROOT + "/" + LIFETIME_INPUT[0], os.O_RDWR),
            "actual first-party lifetime adapter mutation",
        ),
        (
            lambda: builtins.open(ROOT + "/" + CONTRACT, "w"),
            "canonical contract mutation",
        ),
        (
            lambda: os.mkdir("/tmp/rebar-zig-setattr-v2-forbidden"),
            "temporary or private root creation",
        ),
        (lambda: sys.audit("ctypes.dlopen", "forbidden"), "native loading"),
        (
            lambda: sys.audit("ctypes.dlsym", None, "rebar_zig_compile"),
            "native matching lookup",
        ),
        (
            lambda: sys.audit("subprocess.Popen", "zig", [], None, None),
            "compiler or candidate worker creation",
        ),
        (lambda: sys.audit("socket.connect", None, None), "network access"),
        (
            lambda: sys.audit("cpython.PyInterpreterState_New", None),
            "real child-interpreter creation",
        ),
        (lambda: pin("x" * 63, "malformed"), "incomplete source digest"),
        (lambda: relative("../holdout"), "escaped physical owner"),
    ):
        checks += reject(operation, label)
    previous = state["previous"]
    original = state["original"]
    corrected = state["corrected"]
    replacements = (
        (
            b"_setattr=object.__setattr__",
            b"_setattr=getattr",
            "foreign or late-bound attribute writer",
        ),
        (
            b"_free=_zig_bridge.free",
            b"_free=getattr",
            "borrowed first-party release callable",
        ),
        (
            b"_getattr=getattr",
            b"_getattr=None",
            "poisoned attribute lookup default",
        ),
        (
            b'            _setattr(self, "_handle", None)\n'
            b"            _free(handle)\n",
            b"            _free(handle)\n"
            b'            _setattr(self, "_handle", None)\n',
            "native release before clearing ownership",
        ),
        (
            b'            _setattr(self, "_handle", None)\n',
            b"            self._handle = None\n",
            "reintroduced shutdown-sensitive public setter",
        ),
        (
            b"            _free(handle)\n",
            b"            try:\n"
            b"                _free(handle)\n"
            b"            except Exception:\n"
            b"                pass\n",
            "swallowed genuine release failure",
        ),
        (
            b'__slots__ = ("pattern", "flags", "groups", "_groupindex", '
            b'"_handle",\n',
            b'__slots__ = ("pattern", "flags", "groups", "_groupindex", '
            b'"_borrow",\n',
            "changed complete Pattern instance storage",
        ),
        (b"class Scanner:", b"class ScanneR:", "changed first-party scanner"),
        (
            b"from candidates import _zig_bridge\n",
            b"from candidates import _rust_bridge\n",
            "cross-candidate native engine",
        ),
    )
    for old, new, label in replacements:
        require(corrected.count(old) == 1, "missing poison control: " + label)
        changed = corrected.replace(old, new, 1)
        checks += reject(
            lambda value=changed: prove_setattr_adapter(
                original, value, previous,
            ),
            label,
        )
    checks += reject(
        lambda: prove_setattr_adapter(
            original + b"\n", corrected, previous,
        ),
        "altered complete published V13 input adapter",
    )
    checks += reject(
        lambda: prove_setattr_adapter(
            original,
            corrected + b"\ndef __del__(self):\n    return None\n",
            previous,
        ),
        "duplicate or foreign finalizer",
    )
    for mode in (
        "--run", "--worker", "--recover", "--build", "--apply",
        "--install", "--benchmark", "--generate", "--open-holdout",
    ):
        checks += reject(
            lambda selected=mode: parse([selected]),
            "unauthorized actual source-repair action " + mode,
        )
    campaign = state["campaign"]
    for field, value in (
        ("status", "FAIL"),
        ("publication_pass_means", "CANDIDATE QUALIFICATION"),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("original_campaign_passed", True),
        ("case_execution_denominator", 31238),
        ("suite_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", 4608),
        ("observed_semantic_mismatch_lower_bound", 1699),
        ("semantic_mismatch_count", 0),
        ("infrastructure_failure_count", 0),
        ("unique_candidate_worker_count", 12),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("timing_trials_run", 1),
        ("all_three_original_targets_restored", False),
        ("holdout", "OPENED"),
        ("performance", "1.5x"),
        ("winner_selected", True),
    ):
        checks += reject(
            lambda key=field, replacement=value: validate_v13_publication(
                mutated_receipt(state, key, replacement), campaign,
            ),
            "fabricated measured V13 result " + field,
        )
    for suite, field, value, nested, original_detail, label in (
        (
            "original_bounded_v5", "pid", 83, False, False,
            "duplicate real worker identity",
        ),
        (
            "original_bounded_v5", "guard_installed_before_candidate_import",
            False, False, False, "removed genuine guard-before-import proof",
        ),
        (
            "scanner_verbose_v1", "observed_semantic_mismatch_count", 619,
            False, False, "suppressed genuine scanner failure",
        ),
        (
            "subinterpreter_v2", "observed_semantic_mismatch_count", 0,
            False, False, "invented completed child matching",
        ),
        (
            "subinterpreter_v2", "actual_child_guards_installed", 1,
            True, False, "invented a real installed V13 child guard",
        ),
        (
            "subinterpreter_v2", "actual_interpreters_created", 1,
            True, True, "invented a genuine child interpreter",
        ),
        (
            "subinterpreter_v2", "actual_case_interpreter_exec_calls", 1,
            True, True, "invented a genuine child regex execution",
        ),
    ):
        checks += reject(
            lambda name=suite, key=field, replacement=value,
            deeper=nested, innermost=original_detail: validate_v13_publication(
                mutated_row(
                    state, name, key, replacement,
                    nested=deeper, original=innermost,
                ),
                campaign,
            ),
            label,
        )
    no_warning = cloned(state["receipt"], state["producer"])
    no_warning["original_suite_diagnostics"][0]["stderr_literal_excerpt"][
        "text"
    ] = "warning intentionally suppressed"
    checks += reject(
        lambda: validate_v13_publication(no_warning, campaign),
        "suppressed genuine published finalizer-to-setter warning",
    )
    changed_archive = cloned(state["receipt"], state["producer"])
    changed_archive["archive"]["bytes"] += 1
    checks += reject(
        lambda: validate_v13_publication(changed_archive, campaign),
        "fabricated immutable matching archive metadata",
    )
    checks += synthetic_lifecycle_controls()
    require(
        checks >= 80 and wall.denials >= 40,
        "reject incomplete source, physical, publication and lifecycle controls",
    )
    clean()
    return checks


def parse(arguments):
    modes = frozenset({
        "--self-test", "--verify-frozen-context", "--render-contract",
    })
    selected = [argument for argument in arguments if argument in modes]
    require(
        len(selected) == 1,
        "select exactly one physically source-only finalizer action",
    )
    mode = selected[0]
    allowed = {
        "--source-sha256", "--protocol-sha256", "--contract-sha256",
        *(name for name, _ in CALLER_PINS),
    }
    result = {}
    index = 0
    while index < len(arguments):
        key = arguments[index]
        if key in modes:
            require(key == mode, "reject conflicting source-only actions")
            index += 1
            continue
        require(
            key in allowed and key not in result and index + 1 < len(arguments),
            "reject missing, duplicated or unsupported source-repair pins",
        )
        result[key] = arguments[index + 1]
        index += 2
    required = {
        "--source-sha256", "--protocol-sha256",
        *(name for name, _ in CALLER_PINS),
    }
    if mode != "--render-contract":
        required.add("--contract-sha256")
    require(
        set(result) == required,
        "require every independent V1, V13, receipt and input caller pin",
    )
    return mode, result


def source_mode(mode, args):
    with SourceWall() as wall:
        state = context(
            pin(args["--source-sha256"], "V2 source"),
            pin(args["--protocol-sha256"], "V2 protocol"),
            args,
            wall,
        )
        producer = state["producer"]
        if mode == "--render-contract":
            return producer.canonical(contract_value(state))
        contract_owner = dynamic_owner(
            CONTRACT, pin(args["--contract-sha256"], "V2 contract"),
        )
        raw = read_owner(contract_owner)
        document = producer.JsonReader(raw).parse()
        require(
            document == contract_value(state)
            and producer.canonical(document) == raw,
            "reject a noncanonical or weakened setter-safe V2 contract",
        )
        controls = (
            hostile_source_controls(state, wall)
            if mode == "--self-test" else 0
        )
        clean()
        result = {
            "schema": SCHEMA + (
                "-source-self-test"
                if mode == "--self-test"
                else "-verified-frozen-context"
            ),
            "status": "PASS",
            "family": "zig",
            "label": LABEL,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "v1_source_sha256": V1[0][1],
            "v1_protocol_sha256": V1[1][1],
            "v1_contract_sha256": V1[2][1],
            "v13_source_sha256": V13[0][1],
            "v13_protocol_sha256": V13[1][1],
            "v13_contract_sha256": V13[2][1],
            "actual_v13_receipt_sha256": ACTUAL_V13[1],
            "actual_v13_receipt_status": "PASS",
            "actual_v13_publication_pass_means": "DURABLE PUBLICATION ONLY",
            "actual_v13_candidate_status": "FAIL",
            "actual_v13_candidate_qualified": False,
            "actual_v13_candidate_workers": 13,
            "actual_v13_unique_candidate_workers": 13,
            "actual_v13_completed_suite_count": 12,
            "actual_v13_verified_passing_suite_count": 7,
            "actual_v13_verified_passing_case_count": 4607,
            "actual_v13_semantic_failure_count": 5,
            "actual_v13_semantic_mismatch_lower_bound": 1700,
            "actual_v13_semantic_mismatch_count": "NOT MEASURED",
            "actual_v13_warning_suite_count": 13,
            "actual_v13_warning_in_all_passing_suites": True,
            "actual_v13_complete_stderr_bytes": 428866,
            "actual_v13_infrastructure_failure_count": 1,
            "actual_v13_child_guards_installed": 0,
            "actual_v13_interpreters_created": 0,
            "actual_v13_child_case_executions": 0,
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_obligation_count": 73,
            "original_crosswalk_count": 34,
            "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_candidate_matching": "NOT RUN",
            "actual_v13_lifetime_adapter_sha256": LIFETIME_INPUT[1],
            "prospective_setter_adapter_sha256": digest(state["corrected"]),
            "prospective_setter_adapter_bytes": len(state["corrected"]),
            "prospective_setter_adapter_status": "NOT MATERIALIZED",
            "changed_finalizer_count": 1,
            "other_ast_unchanged": True,
            "public_pattern_setter_changed": False,
            "early_bound_object_setattr": True,
            "physical_open_audit_validates_owner_mode_and_flags": True,
            "direct_io_write_bypass_forbidden": True,
            "direct_import_audit_enforced": True,
            "all_os_audit_events_forbidden": True,
            "user_defined_setter_invoked_in_synthetic_repair": False,
            "module_globals_destroyed_in_synthetic_control": True,
            "clear_before_release": True,
            "release_errors_suppressed": False,
            "synthetic_lifecycle_controls": (
                "PASS" if mode == "--self-test" else "NOT RUN"
            ),
            "source_only_hostile_controls": controls,
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
        return producer.canonical(result)


def main():
    mode, args = parse(list(sys.argv[1:]))
    output = source_mode(mode, args)
    require(type(output) is bytes and bool(output), "reject incomplete output")
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
            "first-party Zig cached-setter source repair rejected: "
            + type(error).__qualname__
            + ": "
            + str(error)
            + "\n"
        )
        raise SystemExit(1) from error
