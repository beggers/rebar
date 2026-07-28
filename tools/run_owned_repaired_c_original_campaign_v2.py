#!/usr/bin/env python3
"""Safely recover the original native inode around the frozen C P0 campaign."""

from __future__ import annotations

import argparse
import base64
import builtins
import contextlib
import copy
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
from typing import Any, Iterator, Mapping, Sequence


ROOT = Path("/home/dev-user/src/rebar")
SOURCE_RELATIVE = "tools/run_owned_repaired_c_original_campaign_v2.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V2.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-c-original-campaign-v2.json"
SCHEMA = "rebar-owned-repaired-c-original-campaign-v2"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62")
PHASE_ONE = (
    "oracle/phase1/p0-completeness-v1.json",
    "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
)
ORIGINAL = {
    "source": (
        "tools/run_owned_six_family_original_p0_producer_v3.py",
        "7415192cf5ad83ca643c2c8aaa58222394d62f98bc35f15c301007947b46b23c",
    ),
    "protocol": (
        "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V3.md",
        "88fef0ad32b43697edc48d921bb8d5c086c24125ca7f4934834f311e8d65bb76",
    ),
    "contract": (
        "oracle/phase2/six-family-p0-producer-v3.json",
        "47b3f6c1850cab7190c095fdb4384fd70813c8d27d43dfbbf2960d58a816efb1",
    ),
}
BUILD = {
    "source": (
        "tools/reproduce_owned_native_source_build_v8.py",
        "afc4f8070cb3c1bccf312b77b019cbb6d71f8dcf976f4a2e921e18cc7c063dd4",
    ),
    "protocol": (
        "oracle/phase2/NATIVE-SOURCE-BUILD-V8.md",
        "376aae2bdcbeb0c399369c2a15e7e39efb2b1bcce53129a20c229fbbb995cda2",
    ),
    "contract": (
        "oracle/phase2/native-source-build-v8.json",
        "7f463b70367156d65e73b561629bd1e14ae265b2273afae9b0a984608492019b",
    ),
}
ACTIVATION = {
    "source": (
        "tools/activate_verified_native_candidate_v5.py",
        "bdfcb93e4ac3f436474cf82725165c92b61c8982efff0bf113900cbce3e8aff5",
    ),
    "protocol": (
        "oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V5.md",
        "4693558f9796a0fbf38326fda3a86b2cf19348598b21eab60610df6ee7f241bc",
    ),
    "contract": (
        "oracle/phase2/verified-native-activation-v5.json",
        "a580c6b745c867a69f1f017506c1feec8310aa3070bfd58abd006740b01948da",
    ),
}
FROZEN_CAMPAIGN = {
    "worker": (
        "tools/run_frozen_p0_candidate_worker_v7.py",
        "855c59acdc0b5270493ece8fc39548a89e0febf94d6b186ac9f0e5a50754f68f",
    ),
    "runner": (
        "tools/run_frozen_p0_candidate_v9.py",
        "1511dac06dab5ce319b4dd09cb6f8c5a12160c48cc0dbbdfa7e7fe3f0d426702",
    ),
    "protocol": (
        "oracle/phase2/P0-CANDIDATE-PROTOCOL-V9.md",
        "afbb933eb022efaca7cb9604bc1614d3d2de7e3faf33f446234f725cd331771f",
    ),
    "contract": (
        "oracle/phase2/p0-candidate-protocol-v9.json",
        "a9609b0576aab4e0ea7ff6f9ae2a466c0d77d0af134a7f0bddf83ed01f61d631",
    ),
}
V19 = {
    "source": (
        "tools/render_candidate_current_overview_v19.py",
        "8144272f7c91e3821306a4d3963c8e201c68b275cecacf80d5000dd98c502494",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v19.inputs.json",
        "8f1eb51ff477f0b59934ee503d9bf795f472fd6674180e2af244c7ad4504560c",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v19.json",
        "504de87d091c555eb53d664fbfaaa70660ff4dd2f9abc22803246f8a5e18287f",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v19.svg",
        "7dea68622d7c360f9d2af83f97d76210889b2aeda6662e06178009a1127cf3d6",
    ),
}
V20: dict[str, tuple[str, str]] = {
    "source": (
        "tools/render_candidate_current_overview_v20.py",
        "3f4b63de113743204f2b6736c5486e9160f4f4c029575052676f68943a3210d2",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v20.inputs.json",
        "bf09019d4a8df9ab5519a0b6bbbe9c4aaa8574dbcc4a9eafc1b424ba1961f021",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v20.json",
        "89e89c27a9295bc5c2f0ddb1141bb9969b1fda32a82c546e4afd55bc9c758544",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v20.svg",
        "44d62f5c497178a404950d7e71d604aafcf41349f621396bf32f2112fa685061",
    ),
}
V21: dict[str, tuple[str, str]] = {
    "source": (
        "tools/render_candidate_current_overview_v21.py",
        "617a64691bf9da7730e44bfed96fe20dbd9c8e38b575e0daf8a3432dbf2625e9",
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v21.inputs.json",
        "704b2e07e32260ac741b0a914e2ae04a3deb583de317ba170432f85126af5139",
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v21.json",
        "d2143b09bbf35a7a83977c08a35f6a0c87435a50e478df517099aa719e8fa28c",
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v21.svg",
        "ba7b82d7552603eb836a0c18e47546390c4e1398bbb74951616e309135b9ce5c",
    ),
}

FAMILY = "c"
CAMPAIGN_LABEL = "phase2-v9-original-p0"
SUITES: tuple[tuple[str, int], ...] = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
SUITE_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVER_COUNT = 13
V19_EVIDENCE_COUNT = 71
V19_REFERENCE_COUNT = 76
V20_EVIDENCE_COUNT = 73
V20_REFERENCE_COUNT = 78
V21_EVIDENCE_COUNT = 103
V21_REFERENCE_COUNT = 108
PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT = 30
SOURCE_FAMILY_COUNT = 6
SOURCE_OWNER_COUNT = 25
BUILD_LABEL = "phase2-v8"
BUILD_ROOT = "/tmp/rebar-phase2-native-build-v8-c-3cgv5w3k"
BUILD_ARCHIVE = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8.json.gz",
    "69a795af6c407c0719b68dfa9fd4cb6dcfca2595271f72b83bc43678521f2598",
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v8-c-phase2-v8-publication-receipt.json",
    "3b0983af9729b3150ae239a83dd0fdb37c6e790b3c03ebea48c77215f51456b8",
)
NATIVE_PATH = "candidates/_vm_native.cpython-314-x86_64-linux-gnu.so"
NATIVE_SHA256 = "60e50499c34267927e8d312908d7d86b536106b32f418f76453833df7e91694f"
NATIVE_BYTES = 163136
ORIGINAL_NATIVE_SHA256 = "075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd"
ORIGINAL_NATIVE_BYTES = 149976
ORIGINAL_NATIVE_DEVICE = 2064
ORIGINAL_NATIVE_INODE = 430300
ORIGINAL_NATIVE_MODE = 0o755
ADAPTER = (
    "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707,
)
ORIGINAL_C = (
    "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185,
)
DERIVED_C_SHA256 = "f44694759174c1c3975423e07095ae91a853e66242c4e55d11836df03a730c4d"
DERIVED_C_BYTES = 218308
EVIDENCE = "oracle/phase2/evidence"
ACTIVATION_PREFIX = "rebar-phase2-native-activation-v5-c-"
MAX_SOURCE = 8 * 1024 * 1024
MAX_ARCHIVE = 128 * 1024 * 1024
MAX_REPORT = 32 * 1024 * 1024
MAX_STDERR = 8 * 1024 * 1024
MAX_ERROR = 64 * 1024
RUNNER_TIMEOUT_SECONDS = 14 * 3600


class CampaignError(Exception):
    """A frozen, original, safely recovered C campaign was not proven."""


class SourceEffect(CampaignError):
    """Synthetic source-only validation attempted an external effect."""


def require(condition: Any, message: str) -> None:
    if condition is not True:
        raise CampaignError(message)


def sha256(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only exact complete owner bytes")
    return hashlib.sha256(raw).hexdigest()


def checked_digest(value: Any, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require an exact independently released SHA-256: " + name)
    return value


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=True, allow_nan=False,
                           sort_keys=True, separators=(",", ":"))
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, UnicodeError, OverflowError,
            RecursionError) as error:
        raise CampaignError("reject noncanonical original campaign evidence") from error


def strict_document(raw: bytes, name: str) -> dict[str, Any]:
    def pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in values:
            require(type(key) is str and key not in result,
                    "reject duplicate keys in " + name)
            result[key] = value
        return result

    def invalid(value: str) -> Any:
        raise CampaignError("reject nonfinite JSON in " + name)

    try:
        document = json.loads(raw, object_pairs_hook=pairs,
                              parse_constant=invalid)
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise CampaignError("reject invalid complete JSON: " + name) from error
    require(type(document) is dict and canonical(document) == raw,
            "require exact canonical bytes: " + name)
    return document


def bounded_error(error: BaseException) -> str:
    raw = str(error).encode("utf-8", "backslashreplace")
    if len(raw) > MAX_ERROR:
        raw = raw[:MAX_ERROR] + b" [error summary truncated]"
    return raw.decode("utf-8", "replace")


def checked_label(value: Any) -> str:
    require(type(value) is str and 0 < len(value) <= 48
            and all(part.isascii() and (part.isalnum() or part in "-_")
                    for part in value),
            "require one complete safe recovered campaign label")
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and "\\" not in value
            and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, linked, escaping, or ambiguous owner")
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == str(ROOT / SOURCE_RELATIVE),
            "run only the genuine isolated, bytecode-free CPython 3.14.6 controller")


def read_owner(relative: str, expected: str, *, maximum: int = MAX_SOURCE,
               size: int | None = None, private: bool = False,
               ) -> tuple[bytes, dict[str, Any]]:
    relative = checked_relative(relative)
    checked_digest(expected, relative)
    require(type(maximum) is int and maximum > 0,
            "require a complete bounded recovered-campaign owner")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0)
    descriptors: list[int] = []
    try:
        parent = os.open(str(ROOT), directory_flags)
        descriptors.append(parent)
        pieces = relative.split("/")
        for piece in pieces[:-1]:
            parent = os.open(piece, directory_flags, dir_fd=parent)
            descriptors.append(parent)
        descriptor = os.open(pieces[-1], flags, dir_fd=parent)
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        visible = os.stat(pieces[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode)
                and before.st_nlink == 1
                and (before.st_dev, before.st_ino, before.st_size)
                == (visible.st_dev, visible.st_ino, visible.st_size)
                and 0 < before.st_size <= maximum,
                "reject an absent, linked, replaced, or oversized owner: " + relative)
        if size is not None:
            require(before.st_size == size, "reject changed owner size: " + relative)
        if private:
            require(stat.S_IMODE(before.st_mode) == 0o600,
                    "require an exact owner-only original evidence file")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            require(type(chunk) is bytes and bool(chunk),
                    "reject truncated original owner bytes")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject hidden extra owner bytes")
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size,
                 before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns)
                and sha256(raw) == expected,
                "reject concurrently changed or incorrectly pinned owner: " + relative)
        return raw, {
            "relative": relative, "sha256": expected,
            "bytes": after.st_size, "device": after.st_dev,
            "inode": after.st_ino, "mode": stat.S_IMODE(after.st_mode),
        }
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def load_frozen(relative: str, expected: str, name: str) -> types.ModuleType:
    raw, _ = read_owner(relative, expected)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / relative)
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


@contextlib.contextmanager
def source_only_wall() -> Iterator[dict[str, int]]:
    effects = {name: 0 for name in (
        "file_reads", "file_writes", "candidate_imports", "candidate_workers",
        "reference_workers", "native_activations", "native_recoveries",
        "native_libraries_loaded", "source_builds", "network_requests",
        "threads_started", "clock_samples", "hidden_cases_read",
        "benchmark_files_read", "blocked_reads", "blocked_writes",
        "blocked_processes", "blocked_imports", "blocked_threads",
        "blocked_network", "blocked_clocks",
    )}
    previous: list[tuple[Any, str, Any]] = []

    def block(owner: Any, attribute: str, counter: str) -> None:
        if not hasattr(owner, attribute):
            return
        original = getattr(owner, attribute)

        def forbidden(*args: Any, **kwargs: Any) -> Any:
            effects[counter] += 1
            raise SourceEffect("source-only campaign blocks " + attribute)

        previous.append((owner, attribute, original))
        setattr(owner, attribute, forbidden)

    try:
        for owner, name in ((builtins, "open"), (io, "open"),
                            (os, "open"), (os, "read"), (os, "stat"),
                            (os, "lstat"), (os, "scandir"),
                            (Path, "open"), (Path, "read_bytes")):
            block(owner, name, "blocked_reads")
        for owner, name in ((os, "write"), (os, "unlink"), (os, "replace"),
                            (os, "rename"), (os, "mkdir"), (os, "fsync"),
                            (Path, "write_bytes"), (Path, "write_text"),
                            (tempfile, "mkdtemp"), (tempfile, "mkstemp")):
            block(owner, name, "blocked_writes")
        block(importlib, "import_module", "blocked_imports")
        block(subprocess, "Popen", "blocked_processes")
        block(subprocess, "run", "blocked_processes")
        block(threading.Thread, "start", "blocked_threads")
        block(socket, "create_connection", "blocked_network")
        block(socket.socket, "connect", "blocked_network")
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns"):
            block(time, name, "blocked_clocks")
        yield effects
    finally:
        for owner, name, original in reversed(previous):
            setattr(owner, name, original)


def synthetic_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-synthetic-source-contract",
        "family": FAMILY,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "suite_ids": [name for name, _ in SUITES],
        "original_producer_sha256": ORIGINAL["source"][1],
        "original_c_source_sha256": ORIGINAL_C[1],
        "separately_derived_c_source_sha256": DERIVED_C_SHA256,
        "separately_derived_c_source_bytes": DERIVED_C_BYTES,
        "original_native_sha256": ORIGINAL_NATIVE_SHA256,
        "original_native_bytes": ORIGINAL_NATIVE_BYTES,
        "original_native_device": ORIGINAL_NATIVE_DEVICE,
        "original_native_inode": ORIGINAL_NATIVE_INODE,
        "original_native_mode_octal": "0755",
        "repaired_native_sha256": NATIVE_SHA256,
        "repaired_native_bytes": NATIVE_BYTES,
        "frozen_build_label": BUILD_LABEL,
        "frozen_build_root": BUILD_ROOT,
        "frozen_build_archive_sha256": BUILD_ARCHIVE[1],
        "frozen_build_receipt_sha256": BUILD_RECEIPT[1],
        "v5_activation_sha256": ACTIVATION["source"][1],
        "v9_original_runner_sha256": FROZEN_CAMPAIGN["runner"][1],
        "v7_original_worker_sha256": FROZEN_CAMPAIGN["worker"][1],
        "v19_historical_evidence_owner_count": V19_EVIDENCE_COUNT,
        "v19_historical_reference_path_count": V19_REFERENCE_COUNT,
        "v20_historical_evidence_owner_count": V20_EVIDENCE_COUNT,
        "v20_historical_reference_path_count": V20_REFERENCE_COUNT,
        "v21_historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "v21_historical_reference_path_count": V21_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "frozen_campaign_label": CAMPAIGN_LABEL,
        "v3_original_producer_protocol_sha256": ORIGINAL["protocol"][1],
        "v3_original_producer_contract_sha256": ORIGINAL["contract"][1],
        "v21_overview_summary_sha256": V21["summary"][1],
        "outer_recovery_required": True,
        "skip_duplicate_existing_restoration_receipt": True,
        "maximum_public_report_bytes": MAX_REPORT,
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "candidate_workers": 0,
        "native_activations": 0,
        "native_recoveries": 0,
        "source_builds": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def validate_synthetic(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(synthetic_contract()),
            "reject any changed original suite, evidence, inode, or recovery rule")
    require(len(SUITES) == SUITE_COUNT
            and len({name for name, _ in SUITES}) == SUITE_COUNT
            and sum(count for _, count in SUITES) == CASE_COUNT,
            "preserve all thirteen unchanged original correctness suites")
    return value


def self_test() -> dict[str, Any]:
    accepted = 0
    rejected = 0
    with source_only_wall() as effects:
        contract = validate_synthetic(synthetic_contract())
        accepted += 1
        for key, changed in (
            ("schema", SCHEMA), ("family", "rust"), ("suite_count", 12),
            ("case_execution_denominator", 31236),
            ("named_private_waiver_count", 12),
            ("original_producer_sha256", "0" * 64),
            ("original_c_source_sha256", DERIVED_C_SHA256),
            ("separately_derived_c_source_sha256", ORIGINAL_C[1]),
            ("separately_derived_c_source_bytes", ORIGINAL_C[2]),
            ("original_native_sha256", NATIVE_SHA256),
            ("original_native_bytes", NATIVE_BYTES),
            ("original_native_device", ORIGINAL_NATIVE_DEVICE + 1),
            ("original_native_inode", ORIGINAL_NATIVE_INODE + 1),
            ("original_native_mode_octal", "0700"),
            ("repaired_native_sha256", ORIGINAL_NATIVE_SHA256),
            ("repaired_native_bytes", ORIGINAL_NATIVE_BYTES),
            ("frozen_build_label", "phase2-v7"),
            ("frozen_build_root", "/tmp/rebar-phase2-native-build-v8-c-forged"),
            ("frozen_build_archive_sha256", BUILD_RECEIPT[1]),
            ("frozen_build_receipt_sha256", BUILD_ARCHIVE[1]),
            ("v5_activation_sha256", "0" * 64),
            ("v9_original_runner_sha256", FROZEN_CAMPAIGN["worker"][1]),
            ("v7_original_worker_sha256", FROZEN_CAMPAIGN["runner"][1]),
            ("v19_historical_evidence_owner_count", 73),
            ("v19_historical_reference_path_count", 78),
            ("v20_historical_evidence_owner_count", 71),
            ("v20_historical_reference_path_count", 76),
            ("v21_historical_evidence_owner_count", V20_EVIDENCE_COUNT),
            ("v21_historical_reference_path_count", V20_REFERENCE_COUNT),
            ("preserved_failed_campaign_evidence_owner_count", 29),
            ("frozen_campaign_label", "phase2-v8-original-p0"),
            ("v3_original_producer_protocol_sha256", "0" * 64),
            ("v3_original_producer_contract_sha256", "0" * 64),
            ("v21_overview_summary_sha256", V20["summary"][1]),
            ("outer_recovery_required", False),
            ("skip_duplicate_existing_restoration_receipt", False),
            ("maximum_public_report_bytes", MAX_REPORT + 1),
            ("candidate_correctness", "PASS"),
            ("qualified_candidate_count", 1),
            ("candidate_workers", 1), ("native_activations", 1),
            ("native_recoveries", 1), ("source_builds", 1),
            ("clock_samples", 1), ("hidden_cases_read", 1),
            ("benchmark_files_read", 1), ("timing_trials_run", 1),
            ("performance", "PASS"), ("memory", "PASS"),
            ("holdout", "OPEN"), ("winner_selected", True),
        ):
            hostile = copy.deepcopy(contract)
            hostile[key] = changed
            try:
                validate_synthetic(hostile)
            except CampaignError:
                rejected += 1
            else:
                raise CampaignError("accepted altered source-only control: " + key)
        for index, (name, _) in enumerate(SUITES):
            hostile = copy.deepcopy(contract)
            hostile["suite_ids"][index] = name + "-forged"
            try:
                validate_synthetic(hostile)
            except CampaignError:
                rejected += 1
            else:
                raise CampaignError("accepted an altered original suite")
        for invalid in (None, [], {}, True, 0, "forged"):
            try:
                validate_synthetic(invalid)
            except (CampaignError, TypeError, AttributeError):
                rejected += 1
            else:
                raise CampaignError("accepted an invalid source-only contract")
        probes = (
            ("blocked_reads", lambda: builtins.open("/tmp/rebar-campaign-forbidden", "rb")),
            ("blocked_reads", lambda: os.open("/tmp/rebar-campaign-forbidden", os.O_RDONLY)),
            ("blocked_writes", lambda: os.write(-1, b"forbidden")),
            ("blocked_processes", lambda: subprocess.run(("forbidden-original-campaign",))),
            ("blocked_imports", lambda: importlib.import_module("candidates.vm_candidate")),
            ("blocked_threads", lambda: threading.Thread(target=lambda: None).start()),
            ("blocked_network", lambda: socket.create_connection(("127.0.0.1", 1))),
            ("blocked_clocks", lambda: time.perf_counter_ns()),
        )
        for counter, probe in probes:
            before = effects[counter]
            try:
                probe()
            except SourceEffect:
                require(effects[counter] == before + 1,
                        "authenticate the exact blocked source-only operation")
                rejected += 1
            else:
                raise CampaignError("failed to block a recovered-campaign effect")
        require(rejected >= 60,
                "require substantial hostile original-source recovery controls")
        observed = dict(effects)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "synthetic_only": True,
        "accepted_synthetic_controls": accepted,
        "rejected_hostile_controls": rejected,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "v19_historical_evidence_owner_count": V19_EVIDENCE_COUNT,
        "v19_historical_reference_path_count": V19_REFERENCE_COUNT,
        "historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "historical_authenticated_reference_count": V21_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "original_producer_sha256": ORIGINAL["source"][1],
        "original_producer_protocol_sha256": ORIGINAL["protocol"][1],
        "original_producer_document_sha256": ORIGINAL["contract"][1],
        "source_only_effects": observed,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_activations": 0,
        "actual_native_recoveries": 0,
        "actual_source_builds": 0,
        "actual_candidate_imports": 0,
        "clock_samples": 0, "hidden_cases_read": 0,
        "benchmark_files_read": 0, "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def mapped(mapping: Mapping[str, tuple[str, str]]) -> dict[str, Any]:
    return {key: {"path": value[0], "sha256": value[1]}
            for key, value in mapping.items()}


def released_v20() -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for key, (relative, fingerprint) in V20.items():
        checked_relative(relative)
        result[key] = (relative, checked_digest(
            fingerprint, "coordinator-pushed V20 " + key))
    require(set(result) == {"source", "inputs", "summary", "svg"},
            "require all four separately pushed V20 overview owners")
    return result


def original_target(module: types.ModuleType) -> dict[str, Any]:
    observed = module.current_target()
    require(type(observed) is tuple and len(observed) == 2,
            "never activate without the pre-existing real user-owned C target")
    raw, owner = observed
    require(type(raw) is bytes and len(raw) == ORIGINAL_NATIVE_BYTES
            and sha256(raw) == ORIGINAL_NATIVE_SHA256
            and type(owner) is dict
            and owner.get("sha256") == ORIGINAL_NATIVE_SHA256
            and owner.get("bytes") == ORIGINAL_NATIVE_BYTES
            and owner.get("device") == ORIGINAL_NATIVE_DEVICE
            and owner.get("inode") == ORIGINAL_NATIVE_INODE
            and owner.get("mode") == ORIGINAL_NATIVE_MODE
            and owner.get("nlink") == 1,
            "preserve the exact existing device, inode, content, size and 0755 mode")
    return owner


def activation_arguments() -> list[str]:
    return [
        "--activate",
        "--activation-source-sha256", ACTIVATION["source"][1],
        "--activation-protocol-sha256", ACTIVATION["protocol"][1],
        "--activation-contract-sha256", ACTIVATION["contract"][1],
        "--build-source-sha256", BUILD["source"][1],
        "--build-protocol-sha256", BUILD["protocol"][1],
        "--build-contract-sha256", BUILD["contract"][1],
        "--family", FAMILY, "--build-label", BUILD_LABEL,
        "--build-root", BUILD_ROOT,
        "--build-report-sha256", BUILD_ARCHIVE[1],
        "--build-receipt-sha256", BUILD_RECEIPT[1],
        "--native-sha256", NATIVE_SHA256,
        "--native-bytes", str(NATIVE_BYTES),
        "--owned-source-sha256", ORIGINAL_C[0] + "=" + ORIGINAL_C[1],
        "--owned-source-sha256", ADAPTER[0] + "=" + ADAPTER[1],
    ]


def expected_machine_contract(options: argparse.Namespace,
                              producer: types.ModuleType) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-source-freeze", "version": 2,
        "goal": {"path": GOAL[0], "sha256": GOAL[1]},
        "pinned_runtime": {"path": PYTHON, "sha256": PYTHON_SHA256,
                           "version": "3.14.6", "isolated": True,
                           "bytecode_writes": False},
        "phase_one": {"path": PHASE_ONE[0], "sha256": PHASE_ONE[1]},
        "campaign_source": {"path": SOURCE_RELATIVE,
                            "sha256": options.source_sha256},
        "campaign_protocol": {"path": PROTOCOL_RELATIVE,
                              "sha256": options.protocol_sha256},
        "original_evaluator": mapped(ORIGINAL),
        "frozen_v8_build": mapped(BUILD),
        "frozen_v5_activation": mapped(ACTIVATION),
        "frozen_original_v9_campaign": mapped(FROZEN_CAMPAIGN),
        "preserved_v19_overview": mapped(V19),
        "published_v20_overview": mapped(released_v20()),
        "published_v21_overview": mapped(V21),
        "actual_build": {
            "family": FAMILY, "label": BUILD_LABEL,
            "private_root": BUILD_ROOT,
            "archive": {"path": BUILD_ARCHIVE[0],
                        "sha256": BUILD_ARCHIVE[1]},
            "receipt": {"path": BUILD_RECEIPT[0],
                        "sha256": BUILD_RECEIPT[1]},
            "repaired_native_sha256": NATIVE_SHA256,
            "repaired_native_bytes": NATIVE_BYTES,
            "fresh_phase_count": 2, "actual_compiler_process_count": 14,
        },
        "original_native": {
            "path": NATIVE_PATH, "sha256": ORIGINAL_NATIVE_SHA256,
            "bytes": ORIGINAL_NATIVE_BYTES,
            "device": ORIGINAL_NATIVE_DEVICE, "inode": ORIGINAL_NATIVE_INODE,
            "mode_octal": "0755", "hardlink_count": 1,
        },
        "original_c_family": {
            "name": FAMILY,
            "original_source": {"path": ORIGINAL_C[0],
                                "sha256": ORIGINAL_C[1],
                                "bytes": ORIGINAL_C[2]},
            "adapter": {"path": ADAPTER[0], "sha256": ADAPTER[1],
                        "bytes": ADAPTER[2]},
            "separate_derived_sha256": DERIVED_C_SHA256,
            "separate_derived_bytes": DERIVED_C_BYTES,
            "original_family_spec_unchanged": True,
            "stdlib_regex_delegation_allowed": False,
            "external_regex_package_allowed": False,
            "cross_candidate_engine_allowed": False,
        },
        "original_suites": [producer.suite_protocol(suite)
                            for suite in producer.SUITES],
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "history": {
            "v19_repository_evidence_owner_count": V19_EVIDENCE_COUNT,
            "v19_authenticated_reference_path_count": V19_REFERENCE_COUNT,
            "v20_repository_evidence_owner_count": V20_EVIDENCE_COUNT,
            "v20_authenticated_reference_path_count": V20_REFERENCE_COUNT,
            "v21_repository_evidence_owner_count": V21_EVIDENCE_COUNT,
            "v21_authenticated_reference_path_count": V21_REFERENCE_COUNT,
            "preserved_failed_campaign_evidence_owner_count":
                PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
            "first_party_family_count": SOURCE_FAMILY_COUNT,
            "first_party_source_owner_count": SOURCE_OWNER_COUNT,
        },
        "recovery": {
            "exclusive_v5_activation": True,
            "durable_journal_before_promotion": True,
            "outer_finally_covers_prevalidation_and_subprocess": True,
            "preserve_existing_original_inode": True,
            "preserve_original_mode_octal": "0755",
            "skip_duplicate_exclusive_restoration_receipt": True,
            "verify_original_before_evidence_publication": True,
            "all_original_suite_archives_preserved": True,
            "unobserved_matching_and_mismatches": "NOT MEASURED",
            "frozen_campaign_label": CAMPAIGN_LABEL,
            "maximum_public_report_bytes": MAX_REPORT,
        },
        "phase_boundary": {
            "candidate_correctness": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_native_activations": 0,
            "actual_native_recoveries": 0,
            "actual_source_builds": 0,
            "clock_samples": 0, "hidden_cases_read": 0,
            "benchmark_files_read": 0, "timing_trials_run": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        },
    }


def load_context(options: argparse.Namespace,
                 ) -> tuple[dict[str, Any], dict[str, types.ModuleType]]:
    verify_runtime()
    v20 = released_v20()
    owners: dict[str, dict[str, Any]] = {}
    for relative, fingerprint in (
        (SOURCE_RELATIVE, options.source_sha256),
        (PROTOCOL_RELATIVE, options.protocol_sha256),
        (CONTRACT_RELATIVE, options.contract_sha256),
        GOAL, PHASE_ONE, BUILD_ARCHIVE, BUILD_RECEIPT,
    ):
        maximum = MAX_ARCHIVE if relative == BUILD_ARCHIVE[0] else MAX_SOURCE
        private = relative in (BUILD_ARCHIVE[0], BUILD_RECEIPT[0])
        _, owners[relative] = read_owner(relative, fingerprint,
                                         maximum=maximum, private=private)
    for mapping in (ORIGINAL, BUILD, ACTIVATION, FROZEN_CAMPAIGN,
                    V19, v20, V21):
        for relative, fingerprint in mapping.values():
            _, owners[relative] = read_owner(relative, fingerprint)
    for relative, fingerprint, size in (ORIGINAL_C, ADAPTER):
        _, owners[relative] = read_owner(relative, fingerprint, size=size)
    original = load_frozen(ORIGINAL["source"][0], ORIGINAL["source"][1],
                           "_rebar_recovered_original_six_family_producer_v3")
    require(original.SCHEMA == "rebar-owned-six-family-original-p0-producer-v3"
            and [(suite.name, suite.case_count) for suite in original.SUITES]
            == list(SUITES),
            "load only the corrected, exact complete original V3 P0 evaluator")
    spec = original.family_spec(FAMILY)
    require(tuple(spec.source_owners) == (ADAPTER, ORIGINAL_C)
            and spec.combined_native is True,
            "never substitute derived bytes for the original C FamilySpec")
    contract_raw, _ = read_owner(CONTRACT_RELATIVE, options.contract_sha256)
    document = strict_document(contract_raw, "recovered original V2 machine contract")
    require(canonical(document)
            == canonical(expected_machine_contract(options, original)),
            "reject an altered V3, V9, V21, original user inode, or recovery contract")
    v19_raw, _ = read_owner(V19["summary"][0], V19["summary"][1])
    old = strict_document(v19_raw, "preserved actual V19 overview")
    require(old.get("status") == "PASS"
            and old.get("repository_evidence_owner_count") == V19_EVIDENCE_COUNT
            and old.get("suite_count") == SUITE_COUNT
            and old.get("full_case_denominator") == CASE_COUNT,
            "never recount, rewrite, or replace actual V19 evidence")
    v20_raw, _ = read_owner(v20["summary"][0], v20["summary"][1])
    previous = strict_document(v20_raw, "preserved actual-build V20 overview")
    require(previous.get("schema") == "rebar-candidate-current-overview-v20-summary"
            and previous.get("status") == "PASS"
            and previous.get("repository_evidence_owner_count") == V20_EVIDENCE_COUNT
            and previous.get("authenticated_digest_addressed_history_paths")
            == V20_REFERENCE_COUNT
            and previous.get("suite_count") == SUITE_COUNT
            and previous.get("full_case_denominator") == CASE_COUNT,
            "preserve the genuine separately pushed 73/78 V20 history")
    v21_raw, _ = read_owner(V21["summary"][0], V21["summary"][1])
    current = strict_document(v21_raw, "published corrected V21 overview")
    require(current.get("schema") == "rebar-candidate-current-overview-v21-summary"
            and current.get("status") == "PASS"
            and current.get("repository_evidence_owner_count") == V21_EVIDENCE_COUNT
            and current.get("authenticated_digest_addressed_history_paths")
            == V21_REFERENCE_COUNT
            and current.get("suite_count") == SUITE_COUNT
            and current.get("full_case_denominator") == CASE_COUNT
            and current.get("qualified_candidate_count") == 0
            and current.get("clock_samples") == 0
            and current.get("hidden_cases_read") == 0
            and current.get("timing_trials_run") == 0
            and current.get("performance") == "NOT MEASURED"
            and current.get("memory") == "NOT MEASURED"
            and current.get("final_holdout_opened") is False
            and current.get("winner_selected") is False,
            "preserve all 103 actual V21 owners and 108 authenticated paths")
    snapshot = current.get("snapshot")
    require(type(snapshot) is dict
            and snapshot.get("all_actual_candidate_and_native_evidence_owner_count")
            == V21_EVIDENCE_COUNT
            and snapshot.get("all_digest_addressed_history_path_count")
            == V21_REFERENCE_COUNT,
            "preserve genuine whole-history V21 evidence and reference denominators")
    inputs_raw, _ = read_owner(V21["inputs"][0], V21["inputs"][1])
    inputs = strict_document(inputs_raw, "published corrected V21 inputs")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v21-inputs"
            and inputs.get("version") == 21
            and inputs.get("repository_evidence_owner_count") == V21_EVIDENCE_COUNT
            and inputs.get("all_digest_addressed_history_path_count")
            == V21_REFERENCE_COUNT
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("full_case_denominator") == CASE_COUNT
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("final_holdout_opened") is False
            and inputs.get("performance") == "NOT MEASURED"
            and inputs.get("memory") == "NOT MEASURED"
            and inputs.get("winner_selected") is False,
            "reject altered V21 source inputs, denominators, or measured claims")
    producer_options = original.parse_arguments([
        "--verify-frozen-context",
        "--source-sha256", ORIGINAL["source"][1],
        "--protocol-sha256", ORIGINAL["protocol"][1],
        "--document-sha256", ORIGINAL["contract"][1],
    ])
    producer_context = original.verify_frozen_context(producer_options)
    require(producer_context.get("status") == "PASS"
            and producer_context.get("read_only") is True
            and producer_context.get("suite_count") == SUITE_COUNT
            and producer_context.get("case_execution_denominator") == CASE_COUNT
            and producer_context.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and producer_context.get("total_distinct_historical_evidence_owner_count")
            == V21_EVIDENCE_COUNT
            and producer_context.get("total_authenticated_historical_reference_path_count")
            == V21_REFERENCE_COUNT
            and producer_context.get("new_repaired_c_campaign_evidence_owner_count")
            == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
            and producer_context.get("actual_candidate_workers") == 0
            and producer_context.get("actual_native_activations") == 0
            and producer_context.get("clock_samples") == 0,
            "independently verify genuine V3 only while original inode is restored")
    worker = load_frozen(FROZEN_CAMPAIGN["worker"][0],
                         FROZEN_CAMPAIGN["worker"][1],
                         "_rebar_recovered_original_frozen_worker_v7")
    runner = load_frozen(FROZEN_CAMPAIGN["runner"][0],
                         FROZEN_CAMPAIGN["runner"][1],
                         "_rebar_recovered_original_frozen_runner_v9")
    require(worker.SCHEMA == "rebar-frozen-python-re-p0-candidate-worker-v7"
            and runner.SCHEMA == "rebar-frozen-python-re-p0-candidate-v9"
            and worker.RUNNER_SCHEMA == runner.SCHEMA
            and tuple(worker.SUITES) == SUITES
            and tuple(runner.SUITES) == SUITES,
            "freeze the exact corrected full-original V7 worker and V9 runner")
    runner_options = runner.parse_arguments([
        "--verify-frozen-context",
        "--source-sha256", FROZEN_CAMPAIGN["runner"][1],
        "--worker-source-sha256", FROZEN_CAMPAIGN["worker"][1],
        "--protocol-sha256", FROZEN_CAMPAIGN["protocol"][1],
        "--document-sha256", FROZEN_CAMPAIGN["contract"][1],
        "--producer-source-sha256", ORIGINAL["source"][1],
        "--producer-protocol-sha256", ORIGINAL["protocol"][1],
        "--producer-document-sha256", ORIGINAL["contract"][1],
    ])
    runner_context = runner.verify_frozen_context(runner_options)
    require(runner_context.get("status") == "PASS"
            and runner_context.get("read_only") is True
            and runner_context.get("suite_count") == SUITE_COUNT
            and runner_context.get("case_execution_denominator") == CASE_COUNT
            and runner_context.get("historical_evidence_owner_count")
            == V21_EVIDENCE_COUNT
            and runner_context.get("historical_authenticated_reference_count")
            == V21_REFERENCE_COUNT
            and runner_context.get("preserved_failed_campaign_evidence_owner_count")
            == PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT
            and runner_context.get("original_producer_sha256")
            == ORIGINAL["source"][1]
            and runner_context.get("original_producer_protocol_sha256")
            == ORIGINAL["protocol"][1]
            and runner_context.get("original_producer_document_sha256")
            == ORIGINAL["contract"][1]
            and runner_context.get("actual_candidate_workers") == 0
            and runner_context.get("actual_native_activations") == 0
            and runner_context.get("clock_samples") == 0,
            "verify genuine V9 and its nested V3 before any native promotion")
    activation = load_frozen(ACTIVATION["source"][0],
                             ACTIVATION["source"][1],
                             "_rebar_recovered_exact_native_activation_v5")
    require(activation.SCHEMA == "rebar-phase2-verified-native-activation-v5"
            and activation.ACTIVATION_PREFIX == ACTIVATION_PREFIX,
            "never invoke a legacy or substituted native activator")
    existing = original_target(activation)
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "read-only context must never import, run, or activate a candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "read_only": True,
        "frozen_owners": owners,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "original_producer_sha256": ORIGINAL["source"][1],
        "original_producer_protocol_sha256": ORIGINAL["protocol"][1],
        "original_producer_document_sha256": ORIGINAL["contract"][1],
        "original_c_source_sha256": ORIGINAL_C[1],
        "separately_derived_c_source_sha256": DERIVED_C_SHA256,
        "v19_historical_evidence_owner_count": V19_EVIDENCE_COUNT,
        "v19_historical_reference_path_count": V19_REFERENCE_COUNT,
        "v20_historical_evidence_owner_count": V20_EVIDENCE_COUNT,
        "v20_historical_reference_path_count": V20_REFERENCE_COUNT,
        "historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "historical_authenticated_reference_count": V21_REFERENCE_COUNT,
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "actual_passed_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_passed_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_repaired_native_sha256": NATIVE_SHA256,
        "actual_repaired_native_bytes": NATIVE_BYTES,
        "preserved_original_user_target": existing,
        "v3_frozen_context_verified_before_activation": True,
        "v9_frozen_context_verified_before_activation": True,
        "actual_candidate_workers": 0,
        "actual_reference_workers": 0,
        "actual_native_activations": 0,
        "actual_native_recoveries": 0,
        "actual_source_builds": 0,
        "actual_candidate_imports": 0,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "candidate_correctness": "NOT MEASURED",
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    return result, {"activation": activation, "runner": runner,
                    "worker": worker, "original": original}

def verify_frozen_context(options: argparse.Namespace) -> dict[str, Any]:
    context, _ = load_context(options)
    return context


def private_activation_roots() -> set[str]:
    result: set[str] = set()
    with os.scandir("/tmp") as entries:
        for entry in entries:
            if (entry.name.startswith(ACTIVATION_PREFIX)
                    and entry.is_dir(follow_symlinks=False)):
                path = "/tmp/" + entry.name
                if len(path) <= 512:
                    result.add(path)
    return result


def candidate_journal(activation: types.ModuleType,
                      root: str) -> dict[str, Any] | None:
    try:
        raw, owner = activation.read_owned(
            root, "recovery-journal.json", None,
            maximum=MAX_SOURCE, private=True,
        )
    except (FileNotFoundError, NotADirectoryError):
        return None
    journal = activation.strict_document(
        raw, "actual recorded V5 recovery journal", canonical_required=True,
    )
    require(journal.get("schema") == activation.SCHEMA + "-recovery-journal"
            and journal.get("status") == "PREPARED"
            and journal.get("version") == 5
            and journal.get("family") == FAMILY
            and journal.get("activation_root") == root
            and journal.get("target") == NATIVE_PATH
            and journal.get("expected_promoted_sha256") == NATIVE_SHA256
            and journal.get("expected_promoted_bytes") == NATIVE_BYTES
            and journal.get("expected_promoted_mode") == ORIGINAL_NATIVE_MODE
            and journal.get("build_archive_sha256") == BUILD_ARCHIVE[1]
            and journal.get("build_receipt_sha256") == BUILD_RECEIPT[1]
            and journal.get("activation_source_sha256") == ACTIVATION["source"][1]
            and journal.get("activation_protocol_sha256") == ACTIVATION["protocol"][1]
            and journal.get("activation_contract_sha256") == ACTIVATION["contract"][1]
            and journal.get("build_source_sha256") == BUILD["source"][1]
            and journal.get("build_protocol_sha256") == BUILD["protocol"][1]
            and journal.get("build_contract_sha256") == BUILD["contract"][1],
            "reject a foreign, fabricated, cross-build, or cross-target journal")
    original = journal.get("original")
    require(type(original) is dict
            and original.get("sha256") == ORIGINAL_NATIVE_SHA256
            and original.get("bytes") == ORIGINAL_NATIVE_BYTES
            and original.get("device") == ORIGINAL_NATIVE_DEVICE
            and original.get("inode") == ORIGINAL_NATIVE_INODE
            and original.get("mode") == ORIGINAL_NATIVE_MODE
            and original.get("nlink") == 1,
            "never recover a changed or unrelated original user inode")
    return {"root": root, "owner": owner, "document": journal}


def discover_journal(activation: types.ModuleType, before: set[str],
                     result: dict[str, Any] | None,
                     ) -> dict[str, Any] | None:
    if type(result) is dict and type(result.get("activation_root")) is str:
        return candidate_journal(activation, result["activation_root"])
    found: list[dict[str, Any]] = []
    for root in sorted(private_activation_roots() - before):
        try:
            actual = candidate_journal(activation, root)
        except (CampaignError, activation.ActivationError, OSError,
                ValueError, UnicodeError):
            continue
        if actual is not None:
            found.append(actual)
    require(len(found) <= 1,
            "never recover an ambiguous or unrelated concurrently created journal")
    return found[0] if found else None


def recovery_arguments(root: str, journal_sha256: str,
                       *, mode: str = "recover") -> dict[str, Any]:
    require(mode in ("recover", "restore"),
            "require a genuine frozen V5 journal recovery mode")
    return {
        "mode": mode, "family": FAMILY,
        "activation_root": root,
        "recovery_journal_sha256": checked_digest(journal_sha256, "actual journal"),
        "activation_source_sha256": ACTIVATION["source"][1],
        "activation_protocol_sha256": ACTIVATION["protocol"][1],
        "activation_contract_sha256": ACTIVATION["contract"][1],
        "build_source_sha256": BUILD["source"][1],
        "build_protocol_sha256": BUILD["protocol"][1],
        "build_contract_sha256": BUILD["contract"][1],
    }


def restoration_receipt(activation: types.ModuleType,
                        actual: dict[str, Any]) -> dict[str, Any] | None:
    try:
        raw, owner = activation.read_owned(
            actual["root"], "restoration-receipt.json", None,
            maximum=MAX_SOURCE, private=True,
        )
    except (FileNotFoundError, NotADirectoryError):
        return None
    report = activation.strict_document(
        raw, "genuine original V5 restoration receipt", canonical_required=True,
    )
    require(report.get("schema") == activation.SCHEMA + "-actual-restoration"
            and report.get("status") == "PASS"
            and report.get("version") == 5
            and report.get("family") == FAMILY
            and report.get("activation_root") == actual["root"]
            and report.get("target") == NATIVE_PATH
            and report.get("group_atomic") is False
            and activation.exact_owner_pair(
                actual["owner"], report.get("recovery_journal"))
            and activation.same_owner(
                report.get("original"), actual["document"].get("original")),
            "authenticate the pre-existing exclusive real restoration receipt")
    original_target(activation)
    return {"owner": owner, "report": report,
            "route": "existing-authenticated-restoration-receipt"}


def run_original_runner(label: str,
                        actual: dict[str, Any]) -> dict[str, Any]:
    root = actual["root"]
    activation = actual["activation_module"]
    report_raw, activation_report = activation.read_owned(
        root, "activation-report.json", None, maximum=MAX_SOURCE, private=True,
    )
    receipt_raw, activation_receipt = activation.read_owned(
        root, "activation-receipt.json", None, maximum=MAX_SOURCE, private=True,
    )
    report = activation.strict_document(
        report_raw, "actual genuine V5 activation report", canonical_required=True,
    )
    receipt = activation.strict_document(
        receipt_raw, "actual genuine V5 activation receipt", canonical_required=True,
    )
    require(report.get("schema") == activation.SCHEMA + "-actual-activation"
            and report.get("status") == "PASS"
            and report.get("activation_root") == root
            and receipt.get("schema") == activation.SCHEMA + "-durable-activation-receipt"
            and receipt.get("status") == "PASS"
            and activation.exact_owner_pair(
                actual["owner"], report.get("recovery_journal"))
            and activation.exact_owner_pair(
                actual["owner"], receipt.get("recovery_journal"))
            and activation.exact_owner_pair(
                activation_report, receipt.get("activation_report")),
            "independently bind actual activation report, receipt, and journal")
    arguments = [
        PYTHON, "-I", "-B", str(ROOT / FROZEN_CAMPAIGN["runner"][0]),
        "--run", "--candidate", FAMILY, "--label", checked_label(label),
        "--build-label", BUILD_LABEL, "--activation-root", root,
        "--source-sha256", FROZEN_CAMPAIGN["runner"][1],
        "--worker-source-sha256", FROZEN_CAMPAIGN["worker"][1],
        "--protocol-sha256", FROZEN_CAMPAIGN["protocol"][1],
        "--document-sha256", FROZEN_CAMPAIGN["contract"][1],
        "--producer-source-sha256", ORIGINAL["source"][1],
        "--producer-protocol-sha256", ORIGINAL["protocol"][1],
        "--producer-document-sha256", ORIGINAL["contract"][1],
        "--build-archive-sha256", BUILD_ARCHIVE[1],
        "--build-receipt-sha256", BUILD_RECEIPT[1],
        "--activation-source-sha256", ACTIVATION["source"][1],
        "--activation-protocol-sha256", ACTIVATION["protocol"][1],
        "--activation-contract-sha256", ACTIVATION["contract"][1],
        "--activation-report-sha256", activation_report["sha256"],
        "--activation-receipt-sha256", activation_receipt["sha256"],
        "--recovery-journal-sha256", actual["owner"]["sha256"],
        "--native-engine-sha256", NATIVE_SHA256,
        "--native-bridge-sha256", NATIVE_SHA256,
    ]
    child = subprocess.Popen(arguments, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=RUNNER_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    require(type(stdout) is bytes and type(stderr) is bytes,
            "capture both complete genuine frozen aggregate process streams")
    require(len(stdout) <= MAX_REPORT and len(stderr) <= MAX_STDERR,
            "reject oversized original aggregate streams without claiming success")
    process = {
        "returncode": child.returncode, "timed_out": timed_out,
        "stdout_base64": base64.b64encode(stdout).decode("ascii"),
        "stdout_bytes": len(stdout), "stdout_sha256": sha256(stdout),
        "stderr_base64": base64.b64encode(stderr).decode("ascii"),
        "stderr_bytes": len(stderr), "stderr_sha256": sha256(stderr),
        "actual_aggregate_processes": 1,
    }
    return {"process": process, "stdout": stdout}


def authenticate_original_campaign(
    worker: types.ModuleType, runner: types.ModuleType,
    result: dict[str, Any], label: str,
) -> dict[str, Any]:
    process = result["process"]
    publication = strict_document(result["stdout"], "complete genuine V8 runner stdout")
    status = publication.get("status")
    require(publication.get("schema")
            == "rebar-frozen-python-re-p0-candidate-v9-published-complete-candidate"
            and status in ("PASS", "FAIL")
            and publication.get("candidate_family") == FAMILY
            and publication.get("label") == label
            and publication.get("suite_count") == SUITE_COUNT
            and publication.get("case_execution_denominator") == CASE_COUNT
            and publication.get("completed_suite_count") == SUITE_COUNT
            and publication.get("restoration_status") == "PASS"
            and publication.get("candidate_qualified") is (status == "PASS")
            and process["timed_out"] is False
            and process["returncode"] == (0 if status == "PASS" else 1)
            and publication.get("performance") == "NOT MEASURED"
            and publication.get("memory") == "NOT MEASURED"
            and publication.get("holdout") == "NOT OPENED"
            and publication.get("winner_selected") is False,
            "never turn a partial original campaign or failed recovery into a pass")
    archive = publication.get("archive")
    receipt = publication.get("receipt")
    require(type(archive) is dict and type(receipt) is dict,
            "require separately owned complete original campaign evidence")
    stem = EVIDENCE + "/frozen-p0-candidate-v9-c-" + checked_label(label)
    if status == "FAIL":
        stem += "-failures"
    compressed, archive_owner = worker.read_owner(
        stem + ".json.gz", archive.get("sha256"),
        maximum=worker.MAX_COMPRESSED_SUITE_BYTES,
        size=archive.get("size_bytes"), private=True,
    )
    receipt_raw, receipt_owner = worker.read_owner(
        stem + "-publication-receipt.json", receipt.get("sha256"),
        maximum=worker.MAX_SOURCE_BYTES,
        size=receipt.get("size_bytes"), private=True,
    )
    require((archive_owner["device"], archive_owner["inode"])
            != (receipt_owner["device"], receipt_owner["inode"]),
            "preserve two independently authenticated original campaign owners")
    receipt_document = worker.exact_json(
        receipt_raw, "genuine original aggregate durable receipt",
    )
    require(receipt_document.get("schema")
            == runner.SCHEMA + "-durable-publication-receipt"
            and receipt_document.get("status") == "PASS"
            and receipt_document.get("candidate_status") == status
            and receipt_document.get("candidate_family") == FAMILY
            and receipt_document.get("label") == label
            and receipt_document.get("suite_count") == SUITE_COUNT
            and receipt_document.get("case_execution_denominator") == CASE_COUNT
            and receipt_document.get("completed_suite_count") == SUITE_COUNT,
            "authenticate the complete original suite aggregate publication")
    chunks: list[bytes] = []
    expanded_size = 0
    with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as source:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            expanded_size += len(chunk)
            require(expanded_size <= MAX_REPORT,
                    "reject oversized original aggregate data while streaming")
            chunks.append(chunk)
    expanded = b"".join(chunks)
    require(0 < len(expanded) == expanded_size
            and len(expanded) == receipt_document.get("uncompressed_bytes")
            and sha256(expanded) == receipt_document.get("uncompressed_sha256"),
            "authenticate the complete bounded original aggregate without truncation")
    full = worker.exact_json(expanded, "complete original thirteen-suite report")
    require(full.get("status") == status
            and full.get("suite_count") == SUITE_COUNT
            and full.get("case_execution_denominator") == CASE_COUNT
            and full.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and full.get("completed_suite_count") == SUITE_COUNT
            and full.get("original_producer_sha256") == ORIGINAL["source"][1]
            and full.get("nested_producer_sha256") == ORIGINAL["source"][1]
            and full.get("original_c_source_sha256") == ORIGINAL_C[1]
            and full.get("derived_c_source_sha256") == DERIVED_C_SHA256
            and full.get("actual_v8_build_archive_sha256") == BUILD_ARCHIVE[1]
            and full.get("actual_v8_build_receipt_sha256") == BUILD_RECEIPT[1]
            and full.get("original_producer_protocol_sha256")
            == ORIGINAL["protocol"][1]
            and full.get("original_producer_document_sha256")
            == ORIGINAL["contract"][1]
            and full.get("historical_evidence_owner_count") == V21_EVIDENCE_COUNT
            and full.get("historical_authenticated_reference_count")
            == V21_REFERENCE_COUNT
            and full.get("candidate_qualified") is (status == "PASS")
            and (status != "PASS" or (
                full.get("verified_passing_case_count") == CASE_COUNT
                and full.get("semantic_mismatch_count") == 0
                and full.get("infrastructure_failure_count") == 0
                and full.get("all_original_suite_evidence_preserved") is True
            )),
            "retain the corrected genuine V21-bound V3 original suite evaluator")
    rows = full.get("suite_results")
    require(type(rows) is list and len(rows) == SUITE_COUNT
            and [row.get("suite") for row in rows]
            == [name for name, _ in SUITES],
            "never omit, replace, reorder, or supplement any original suite")
    verified: list[dict[str, Any]] = []
    for suite, row in zip(SUITES, rows, strict=True):
        name, count = suite
        require(row.get("case_execution_denominator") == count,
                "preserve the exact original suite denominator")
        if row.get("all_original_records_and_mismatches_preserved") is not True:
            require(row.get("status") == "FAIL"
                    and row.get("failure_class") == "INFRASTRUCTURE FAILURE",
                    "never conceal an actual original-suite infrastructure failure")
            verified.append({"suite": name, "status": "FAIL",
                             "failure_class": "INFRASTRUCTURE FAILURE"})
            continue
        reconstructed = {
            "schema": worker.SCHEMA + "-published-original-suite",
            "status": row.get("status"), "candidate_family": FAMILY,
            "label": label, "suite": name,
            "case_execution_denominator": count,
            "mismatch_count": row.get("mismatch_count"),
            "archive": row.get("suite_archive"),
            "receipt": row.get("suite_receipt"),
            "uncompressed_sha256": row.get("uncompressed_sha256"),
            "uncompressed_bytes": row.get("uncompressed_bytes"),
            "all_original_records_and_mismatches_preserved": True,
            "original_producer_sha256": ORIGINAL["source"][1],
            "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        }
        evidence = runner.verify_streamed_suite(worker, reconstructed, suite, label)
        verified.append({
            "suite": name, "status": row.get("status"),
            "case_execution_denominator": count,
            "mismatch_count": row.get("mismatch_count"),
            "failure_class": row.get("failure_class"),
            "archive": evidence["archive"], "receipt": evidence["receipt"],
            "uncompressed_bytes": evidence["uncompressed_bytes"],
            "uncompressed_sha256": evidence["uncompressed_sha256"],
        })
    return {"publication": publication, "archive": archive_owner,
            "receipt": receipt_owner, "full_report": full,
            "verified_original_suites": verified, "process": process}


def require_fresh_campaign(label: str) -> None:
    require(checked_label(label) == CAMPAIGN_LABEL,
            "authorize exactly the one frozen V9 original-correctness label")
    stems = (
        EVIDENCE + "/frozen-p0-candidate-v9-c-" + label,
        EVIDENCE + "/frozen-p0-candidate-v9-c-" + label + "-failures",
        EVIDENCE + "/repaired-c-original-campaign-v2-c-" + label,
        EVIDENCE + "/repaired-c-original-campaign-v2-c-" + label + "-failures",
    )
    expected = [stem + suffix for stem in stems
                for suffix in (".json.gz", "-publication-receipt.json")]
    for name, _ in SUITES:
        archive, receipt = (
            EVIDENCE + "/frozen-p0-candidate-worker-v7-c-"
            + label + "-" + name + ".json.gz",
            EVIDENCE + "/frozen-p0-candidate-worker-v7-c-"
            + label + "-" + name + "-publication-receipt.json",
        )
        expected.extend((archive, receipt))
    for relative in expected:
        try:
            os.stat(str(ROOT / relative), follow_symlinks=False)
        except FileNotFoundError:
            continue
        raise CampaignError(
            "never replace or reuse existing original evidence: " + relative
        )

def preserve_report(worker: types.ModuleType, report: dict[str, Any],
                    label: str) -> dict[str, Any]:
    require(report.get("status") in ("PASS", "FAIL")
            and report.get("original_native_restored") is True,
            "never publish before the exact original user target is restored")
    compressed, expanded_sha, expanded_bytes = worker.stream_gzip(report)
    require(expanded_bytes <= MAX_REPORT,
            "bound the complete truthful outer recovered campaign report")
    stem = EVIDENCE + "/repaired-c-original-campaign-v2-c-" + label
    if report["status"] == "FAIL":
        stem += "-failures"
    archive = worker.create_private_owner(stem + ".json.gz", compressed)
    receipt_raw = canonical({
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS", "candidate_status": report["status"],
        "family": FAMILY, "label": label,
        "archive": archive,
        "uncompressed_sha256": expanded_sha,
        "uncompressed_bytes": expanded_bytes,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "original_native_restored": True,
        "historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "historical_authenticated_reference_count": V21_REFERENCE_COUNT,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    })
    receipt = worker.create_private_owner(
        stem + "-publication-receipt.json", receipt_raw,
    )
    return {
        "schema": SCHEMA + "-published-recovered-campaign",
        "status": report["status"], "family": FAMILY, "label": label,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        "archive": archive, "receipt": receipt,
        "original_native_restored": True,
        "original_native_sha256": ORIGINAL_NATIVE_SHA256,
        "original_native_inode": ORIGINAL_NATIVE_INODE,
        "original_native_mode_octal": "0755",
        "historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "historical_authenticated_reference_count": V21_REFERENCE_COUNT,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0, "performance": "NOT MEASURED",
        "memory": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def run_campaign(options: argparse.Namespace) -> dict[str, Any]:
    context, modules = load_context(options)
    activation = modules["activation"]
    runner = modules["runner"]
    worker = modules["worker"]
    label = checked_label(options.label)
    require_fresh_campaign(label)
    baseline = original_target(activation)
    before = private_activation_roots()
    activated: dict[str, Any] | None = None
    journal: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None
    runner_result: dict[str, Any] | None = None
    restored: dict[str, Any] | None = None
    failure: dict[str, Any] | None = None
    try:
        parsed = activation.parse_arguments(activation_arguments())
        actual_build = activation.authenticate_v8_evidence(parsed)
        require(actual_build["native_sha256"] == NATIVE_SHA256
                and actual_build["native_size"] == NATIVE_BYTES,
                "reverify complete actual native evidence before promotion")
        activated = activation.activate(parsed)
        require(type(activated) is dict
                and activated.get("schema") == activation.SCHEMA + "-actual-activation"
                and activated.get("status") == "PASS"
                and activated.get("family") == FAMILY
                and activated.get("group_atomic") is False
                and activation.same_owner(activated.get("original"), baseline),
                "require the real independently frozen single-target V5 activation")
        journal = discover_journal(activation, before, activated)
        require(type(journal) is dict
                and activation.exact_owner_pair(
                    journal["owner"], activated.get("recovery_journal")),
                "capture only the actual activation's durable V5 recovery journal")
        journal["activation_module"] = activation
        runner_result = run_original_runner(label, journal)
        observed = authenticate_original_campaign(
            worker, runner, runner_result, label,
        )
    except BaseException as error:
        failure = {
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "traceback": traceback.format_exception(
                type(error), error, error.__traceback__,
            ),
            "actual_aggregate_process": (
                runner_result.get("process")
                if type(runner_result) is dict else None
            ),
        }
    finally:
        if journal is None:
            journal = discover_journal(activation, before, activated)
        if journal is not None:
            existing = restoration_receipt(activation, journal)
            if existing is not None:
                restored = existing
            else:
                intention = activation.validate_intention(
                    journal["root"], "stage-intent.json",
                    journal["owner"]["sha256"], "create-adjacent-stage",
                )
                if intention is not None:
                    actual = activation.recover(recovery_arguments(
                        journal["root"], journal["owner"]["sha256"],
                    ))
                    require(type(actual) is dict
                            and actual.get("schema")
                            == activation.SCHEMA + "-actual-restoration"
                            and actual.get("status") == "PASS"
                            and actual.get("route") == "reportless-recovery",
                            "recover the authenticated original inode in outer finally")
                    restored = restoration_receipt(activation, journal)
                    require(restored is not None,
                            "preserve the actual outer durable recovery receipt")
                else:
                    restored = {"route": "journal-before-any-native-mutation",
                                "owner": None, "report": None}
        require(original_target(activation) == baseline,
                "never publish until the exact original 0755 user inode is restored")
    if observed is None:
        require(type(failure) is dict,
                "never fabricate an unobserved actual C matching campaign")
        report = {
            "schema": SCHEMA + "-actual-recovered-campaign",
            "status": "FAIL", "family": FAMILY, "label": label,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "completed_suite_count": "NOT MEASURED",
            "verified_passing_case_count": "NOT MEASURED",
            "semantic_mismatch_count": "NOT MEASURED",
            "infrastructure_failure_count": 1,
            "candidate_qualified": False,
            "all_original_suite_evidence_preserved": False,
            "failure": failure,
        }
    else:
        full = observed["full_report"]
        report = {
            "schema": SCHEMA + "-actual-recovered-campaign",
            "status": full["status"], "family": FAMILY, "label": label,
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "completed_suite_count": full["completed_suite_count"],
            "verified_passing_case_count": full["verified_passing_case_count"],
            "semantic_mismatch_count": full["semantic_mismatch_count"],
            "infrastructure_failure_count": full["infrastructure_failure_count"],
            "candidate_qualified": full["candidate_qualified"],
            "all_original_suite_evidence_preserved": full[
                "all_original_suite_evidence_preserved"],
            "original_suite_results": observed["verified_original_suites"],
            "original_aggregate_archive": observed["archive"],
            "original_aggregate_receipt": observed["receipt"],
            "original_aggregate_process": observed["process"],
            "failure": failure,
        }
    report.update({
        "original_producer_sha256": ORIGINAL["source"][1],
        "original_producer_protocol_sha256": ORIGINAL["protocol"][1],
        "original_producer_document_sha256": ORIGINAL["contract"][1],
        "preserved_failed_campaign_evidence_owner_count":
            PRESERVED_FAILED_CAMPAIGN_OWNER_COUNT,
        "original_c_source_sha256": ORIGINAL_C[1],
        "derived_c_source_sha256": DERIVED_C_SHA256,
        "actual_build_archive_sha256": BUILD_ARCHIVE[1],
        "actual_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_repaired_native_sha256": NATIVE_SHA256,
        "original_native_restored": True,
        "original_native_owner": baseline,
        "recovery": restored,
        "v19_historical_evidence_owner_count": V19_EVIDENCE_COUNT,
        "v19_historical_reference_path_count": V19_REFERENCE_COUNT,
        "historical_evidence_owner_count": V21_EVIDENCE_COUNT,
        "historical_authenticated_reference_count": V21_REFERENCE_COUNT,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    })
    return preserve_report(worker, report, label)


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--run", action="store_true")
    parser.add_argument("--candidate", choices=(FAMILY,))
    parser.add_argument("--label")
    parser.add_argument("--source-sha256")
    parser.add_argument("--protocol-sha256")
    parser.add_argument("--contract-sha256")
    options = parser.parse_args(arguments)
    pins = ("source_sha256", "protocol_sha256", "contract_sha256")
    if options.self_test:
        require(all(getattr(options, key) is None
                    for key in (*pins, "candidate", "label")),
                "source-only controls cannot authorize any actual campaign")
        return options
    for key in pins:
        checked_digest(getattr(options, key), key)
    if options.verify_frozen_context:
        require(options.candidate is None and options.label is None,
                "a read-only context cannot select, activate, or run a candidate")
        return options
    require(options.candidate == FAMILY, "run only the actual owned C candidate")
    require(checked_label(options.label) == CAMPAIGN_LABEL,
            "run only the exact frozen V9 original-correctness campaign label")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    try:
        verify_runtime()
        options = parse_arguments(arguments)
        if options.self_test:
            result = self_test()
        elif options.verify_frozen_context:
            result = verify_frozen_context(options)
        else:
            result = run_campaign(options)
        raw = canonical(result)
        require(len(raw) <= MAX_REPORT,
                "never emit an unbounded recovered campaign summary")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") == "PASS" else 1
    except BaseException as error:
        result = {
            "schema": SCHEMA + "-gate-failure", "status": "FAIL",
            "error_type": type(error).__qualname__,
            "error_message": bounded_error(error),
            "actual_candidate_workers": 0,
            "actual_reference_workers": 0,
            "actual_native_activations": 0,
            "actual_native_recoveries": 0,
            "actual_source_builds": 0,
            "actual_candidate_imports": 0,
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "clock_samples": 0, "timing_trials_run": 0,
            "candidate_correctness": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "holdout": "NOT OPENED", "winner_selected": False,
        }
        sys.stdout.buffer.write(canonical(result))
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
