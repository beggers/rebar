#!/usr/bin/env python3
"""Report the real C11 matching improvement without inventing speed or history."""

from __future__ import annotations

import _io
import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v98.py"
OUTPUT = "docs/evidence/candidate-current-overview-v98"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v98"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 348
HISTORY_FLOOR = 353

V97 = {
    "source": (
        "tools/render_candidate_current_overview_v97.py",
        "f83e055e2392a1efa193b1726ce9044bfdeadc4236103927be4ed8f2f6b060b9",
        65091,
        431237,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v97.inputs.json",
        "ebc81ead0b0741e02fdeef13ab9e740877ee1d2dc7d06ec25347a145f98ad916",
        25586,
        431238,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v97.summary.json",
        "ba4ae8d609b94719dc37ff702d5461763ecba8bee94214961e096ee702636c24",
        4058579,
        431247,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v97.svg",
        "5c8dc279ee76655aa305ee2cb02ae92ea82b5ad36273cdd39a32f2f7ffcda13b",
        9860,
        431276,
    ),
}

C11_SOURCE = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v11.py",
        "b2871592ad3c2138e4a7a9dbea034fc50c699fb34c44f6ff6185087a144e52c2",
        128680,
        431190,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V11.md",
        "cfddebcfb5b481a495b86ed7958f2563ad5ffecc3aebcc94820cae5e0612ed39",
        10493,
        525492,
    ),
    "contract": (
        "oracle/phase2/repaired-c-original-campaign-v11.json",
        "e2396ea5a51fbe6ad0b34f2831461d3c6c362d4076a931791ce23820ca810b93",
        58479,
        525493,
    ),
}

C11_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v11-c-phase2-v21-c-original-match-"
    "semantics-original-p0-v11-failures-publication-receipt.json",
    "3db5daf9352f5c9837f4f7134bead6c0a05b2bddf9815a9cf134ea953b0ecd3e",
    10404,
    525589,
)

HISTORICAL_C10 = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v10.py",
        "ad8b8451847b3e5c566c141e829bdf6eecea8ae9f502b608288449022c83c790",
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V10.md",
        "ba673181c02daf3a572e3569283a5a4c490ed04e7cd76927e3f2fe1430630179",
    ),
    "contract": (
        "oracle/phase2/repaired-c-original-campaign-v10.json",
        "2aad4885fe80b93f61f59c28ed6969fbcf16dda0b8a3457c71b449a9972bb595",
    ),
}
HISTORICAL_C10_RECEIPT_SHA256 = (
    "c5c85f828da7e960c90a23b1eb4d74c30a671d030de04ef61b0e4d00d7e5433a"
)

HISTORICAL_ZIG14 = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v14.py",
        "8757ff2fdda5e8e60ee694b0d803018ddf33ea7266b8d7a5eff6d52d0866569d",
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V14.md",
        "691ab654b88ed30f6cd0729d987415162708fdfb90c36d91bf41dcefdbb5fcef",
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v14.json",
        "1c7326dc2f63635f3e32ec0558b51f21c952d51480f336e3b0d4d49e38428a0a",
    ),
}
HISTORICAL_ZIG14_RECEIPT_SHA256 = (
    "2d1bad717e782b7ed3e0af856f8687e9a29abc93ebf1553adc6d65f668aa5c65"
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

V97_SNAPSHOT_SHA256 = (
    "1e1e15b036093f2d0eaf542fb70e12807a067a13118478a5884c921045044548"
)
V97_SNAPSHOT_BYTES = 19188
V97_HISTORICAL_POOLS = (
    (
        "lossless_actual_outcome_evidence_pool", 33507,
        "8adefd9ea0901086064674c4a9ba1300792a15ba381ffe93a0ef85c372dd345a", 1,
    ),
    (
        "lossless_family_evidence_pool", 126464,
        "5e82ece260c65c1b651512bf82cc952f6b5c9219e2baf5526148fc254b9a0570", 9,
    ),
    (
        "lossless_v87_rust_actual_build_evidence_pool", 11169,
        "7dadc62631aa838cfaa2a0c96d978b1457de11a4d3501fc2a6b456b319a30c21", 1,
    ),
    (
        "lossless_v87_source_evidence_pool", 71364,
        "c4acf498232c0e95b3bb6c7425acb2258915e9fc369e66bd27b8e6bfd8c389ff", 6,
    ),
    (
        "lossless_v88_c_actual_build_evidence_pool", 14406,
        "264678f27d7ee4d2965d42f3129941ee49a5b041f66b16d090e629675bd3dd00", 1,
    ),
    (
        "lossless_v88_c_source_evidence_pool", 19315,
        "2818bd96e62af5aa82b3ee0e0f03f8cbe56ac54955599e32379755e8dd366d1b", 1,
    ),
    (
        "lossless_v88_captured_actual_build_evidence_pool", 11916,
        "01ee89ebdcf462cc2fc61721110bc94d4177deb1949e66d6c350909992cc58e9", 1,
    ),
    (
        "lossless_v88_captured_source_evidence_pool", 19857,
        "ea9c5c1778e361c58e684e2d5e139a276af7751887f8a0e671df260080e2afa9", 1,
    ),
    (
        "lossless_v89_original_campaign_receipt_reference_pool", 19205,
        "5627d67752d6efaefea4c77d2904c32d568b32eaeed06ad721727f3753f632d7", 3,
    ),
    (
        "lossless_v90_zig_v10_original_campaign_evidence_pool", 137388,
        "28e58f4d3ce45cf90eaac4e5e6698c603fd6b128b6ca6b799d79e200884d432f", 1,
    ),
    (
        "lossless_v91_rust_v20_original_campaign_evidence_pool", 83702,
        "8346e978978f837f092f2030f26522847cbbd5f473da96eab062212304d52a18", 1,
    ),
    (
        "lossless_v92_zig_v12_original_campaign_evidence_pool", 135207,
        "38e9595f620c3de41d18bafd39ad7711e222dc8d913a488ec095cb9bd76166f5", 1,
    ),
    (
        "lossless_v93_c_v9_original_campaign_evidence_pool", 45248,
        "7b189ab906dbe14af8fd149de69f6275aa0d1c1e0bf5948ff88f9ff5cfff7ed9", 1,
    ),
    (
        "lossless_v94_zig_v13_original_campaign_evidence_pool", 205726,
        "f983fc7ccee47fc606cc4d4235b43d742d7417a19653fc4929a8551400cffc2a", 1,
    ),
    (
        "lossless_v95_rust_v22_original_campaign_evidence_pool", 138081,
        "7b32e4d599c2a6d8e0f44cead35b5732f32da47b75eb5308b4b26094d8503690", 1,
    ),
    (
        "lossless_v96_c_v10_and_zig_v14_public_evidence_pool", 108611,
        "f691bd6fc89e4a7da2fa5e01ea712f160d70ba6bce68f86b75160a1f26045c76", 2,
    ),
    (
        "lossless_zig_actual_build_evidence_pool", 248256,
        "437c0d0f2f80e841fa7091d50b2094f9054e82c0e792f5db9de817cf2609dcae", 1,
    ),
    (
        "lossless_zig_source_evidence_pool", 23792,
        "1c4694aae8738a74713ddca5f9e88a83b4fdc0c81ddeac7bbfa30eb5db65f029", 1,
    ),
)
POOL_KEY = "lossless_v98_c_v11_complete_public_evidence_pool"
C_LATEST_KEY = "c_v11_actual_original_campaign"
VISIBLE_FOOTER = (
    "observed C11 failing records preserved; historical losses not repaired; "
    "no speed claims; no winner"
)
VISIBLE_POLICY = (
    "ALL 606 OBSERVED C11 RECORDS PRESERVED; HISTORICAL C10 "
    "COMPLETENESS NOT ESTABLISHED BY THIS GRAPH"
)
HISTORICAL_C10_RECORD_STATUS = (
    "EARLIER RECORDED AUDIT ONLY; NOT INDEPENDENTLY ESTABLISHED BY THIS GRAPH"
)
FORBIDDEN_VISIBLE_PHRASES = (
    "all " + "historical observed losses preserved",
    "all " + "historical failures preserved",
    "all " + "historical differences preserved",
    "all " + "historical individual failures preserved",
    "all " + "historical failing examples preserved",
    "all " + "historical counterexamples preserved",
    "every " + "historical loss preserved",
    "historical " + "c10 individual records fully preserved",
    "historical " + "c10 missing records repaired",
    "514 " + "historical records reconstructed",
    "all " + "observed losses preserved",
    "all " + "individual failing examples preserved",
    "all " + "11 source-canonical",
    "11 " + "source-canonical vectors",
    "all " + "completed vectors source-canonical",
    "public-surface " + "source digest verified",
    "public " + "surface source digest verified",
    "fully " + "compatible c candidate",
    "c " + "candidate qualified",
)

C11_RECEIPT_KEYS = frozenset({
    "actual_c21_build_receipt_sha256",
    "actual_c21_root_receipt_sha256",
    "actual_candidate_workers",
    "actual_worker_process_ids",
    "actual_worker_process_ids_are_distinct",
    "all_observed_semantic_mismatch_records_preserved",
    "archive",
    "attempted_suite_count",
    "benchmark_files_read",
    "candidate_execution_failure_count",
    "candidate_qualified",
    "candidate_status",
    "case_execution_denominator",
    "clock_samples",
    "complete_counterexample_archive",
    "complete_mismatch_chunk_count",
    "complete_mismatch_suite_count",
    "complete_mismatch_suite_vector_fingerprints",
    "complete_observed_semantic_mismatch_record_count",
    "completed_suite_count",
    "contract_sha256",
    "corrected_source_sha256",
    "counterexample_normalization_before_original_comparison",
    "counterexample_preview_only",
    "expanded_holdout_proposed_case_count",
    "family",
    "hidden_cases_read",
    "holdout",
    "infrastructure_failure_count",
    "label",
    "memory",
    "named_private_waiver_count",
    "native_bridge_sha256",
    "native_engine_sha256",
    "observed_semantic_mismatch_lower_bound",
    "original_native_inode_restored",
    "original_source_targets_modified",
    "performance",
    "preserved_actual_v10_failure_receipt_sha256",
    "preserved_actual_v6_failure_receipt_sha256",
    "preserved_actual_v7_failure_receipt_sha256",
    "preserved_actual_v9_failure_receipt_sha256",
    "protocol_sha256",
    "publication_pass_means",
    "publication_status",
    "schema",
    "semantic_mismatch_count",
    "separate_reference_case_count",
    "separate_reference_cases_counted_as_candidate_cases",
    "source_sha256",
    "status",
    "successfully_returned_guarded_interpreter_creations",
    "suite_count",
    "suite_outcomes",
    "timing_trials_run",
    "transient_physical_interpreter_creations",
    "unchanged_adapter_sha256",
    "uncompressed_bytes",
    "uncompressed_sha256",
    "undefined_behavior",
    "verified_passing_case_count",
    "version",
    "winner_selected",
    "worker_timeout_count",
    "worker_timeout_seconds",
    "zero_returned_creations_proves_zero_physical_creations",
})
C11_ROW_KEYS = frozenset({
    "actual_candidate_workers",
    "case_execution_denominator",
    "error_type",
    "failure_class",
    "failure_phase",
    "mismatch_count",
    "plain_failure_diagnostic",
    "status",
    "suite",
    "worker_process_id",
})
C11_VECTOR_KEYS = frozenset({
    "all_observed_records_preserved",
    "case_execution_denominator",
    "complete_chunk_count",
    "complete_record_count",
    "complete_vector_sha256",
    "suite",
})
C11_ARCHIVE_KEYS = frozenset({
    "bytes",
    "device",
    "directory_fsync_completed",
    "exclusive_creation",
    "file_fsync_completed",
    "inode",
    "mode",
    "nlink",
    "path",
    "sha256",
})
EXPECTED_WORKER_IDS = (81, 83, 84, 85, 86, 87, 88, 89, 90, 91, 188, 189, 190)
EXPECTED_MISMATCHES = {
    "managed_v1": (16, 1, "3488267b9c2a5aff58a0917adb142d26d482526536b71ceb8e3a39e5d5ed4352"),
    "public_types_v1": (248, 8, "b278976e7d01f2c56359bcdc442fefa1ee6cef899275f1cf5ef00de2fd7e2eff"),
    "substitution_v2": (224, 7, "2ba4b132a4f84ba43fb1a87b1b5c0ab2c8cceffc8f5937bebc285af9da11044a"),
    "public_surface_v19": (114, 4, "443312e6ef63ea99dcf0553ec2e251a40f7221f75697139d85c52084cd0fee22"),
    "pep688_v4": (4, 1, "9377c56ba63c694fd0ce4839ad802cbc1e821ce708c4fbde5f5d7c8d7e5c26cc"),
}
EMPTY_VECTOR_SHA256 = (
    "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
)

FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp",
    "os.fork", "os.forkpty", "ctypes.dlopen", "ctypes.dlsym",
    "socket.__new__", "socket.connect", "socket.bind", "socket.sendto",
    "os.remove", "os.rename", "os.rmdir", "os.mkdir",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "re", "_sre", "ctypes", "subprocess", "multiprocessing",
    "socket", "time", "gzip", "bz2", "lzma", "tarfile", "zipfile",
    "candidates", "rebar",
})
ORIGINAL_OS_WRITE = os.write
ORIGINAL_OS_WRITEV = getattr(os, "writev", None)
ORIGINAL_FILEIO = _io.FileIO


class GraphBase:
    """Small exact-evidence base that never executes historical candidate builders."""

    OWNER_LIMIT = OWNER_LIMIT

    @staticmethod
    def need(value: object, reason: str) -> None:
        if value is not True:
            raise ValueError(reason)

    @staticmethod
    def checked(value: object, label: str) -> str:
        GraphBase.need(
            type(value) is str
            and len(value) == 64
            and all(character in "0123456789abcdef" for character in value),
            "require the exact caller-supplied SHA-256 for " + label,
        )
        assert isinstance(value, str)
        return value

    @staticmethod
    def digest(raw: bytes) -> str:
        GraphBase.need(type(raw) is bytes, "hash only complete evidence bytes")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def canonical(value: object) -> bytes:
        try:
            return (
                json.dumps(
                    value,
                    ensure_ascii=True,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            ).encode("ascii")
        except (TypeError, ValueError, UnicodeError, OverflowError, RecursionError) as error:
            raise ValueError("reject noncanonical complete V98 evidence") from error

    @staticmethod
    def document(raw: bytes, label: str) -> dict:
        def unique(pairs: list[tuple[str, object]]) -> dict:
            result: dict[str, object] = {}
            for key, value in pairs:
                GraphBase.need(key not in result, "reject duplicate JSON key in " + label)
                result[key] = value
            return result

        try:
            value = json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=unique,
                parse_constant=lambda item: (_ for _ in ()).throw(
                    ValueError("reject nonfinite JSON in " + label + ": " + item)
                ),
            )
        except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
            raise ValueError("reject incomplete or malformed " + label) from error
        GraphBase.need(
            type(value) is dict and GraphBase.canonical(value) == raw,
            "authenticate every exact canonical byte of " + label,
        )
        assert isinstance(value, dict)
        return value

    @staticmethod
    def pin(path: str, fingerprint: str, size: int) -> dict:
        GraphBase.checked(fingerprint, path)
        GraphBase.need(
            type(path) is str
            and path != ""
            and not path.startswith("/")
            and ".." not in path.split("/")
            and type(size) is int
            and 0 < size <= OWNER_LIMIT,
            "require a bounded, repository-relative exact V98 owner: " + str(path),
        )
        return {"path": path, "sha256": fingerprint, "bytes": size}

    @staticmethod
    def read_owner(
        path: str,
        expected: str,
        size: int,
        *,
        private: bool = False,
    ) -> tuple[bytes, dict]:
        GraphBase.checked(expected, path)
        GraphBase.need(
            type(path) is str
            and path in {SELF, INPUT_PATH, SUMMARY_PATH, SVG_PATH}
            and type(size) is int
            and 0 < size <= OWNER_LIMIT,
            "reject an unbounded or unauthorized V98 own-source/output owner",
        )
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        handle = os.open(str(ROOT / path), flags)
        try:
            before = os.fstat(handle)
            GraphBase.need(
                stat.S_ISREG(before.st_mode)
                and before.st_uid == os.geteuid()
                and before.st_dev == 2064
                and before.st_size == size
                and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600,
                "reject a substituted complete V98 source/output owner",
            )
            remaining = size
            chunks: list[bytes] = []
            while remaining:
                chunk = os.read(handle, min(remaining, 262144))
                GraphBase.need(bool(chunk), "reject a truncated complete V98 owner")
                chunks.append(chunk)
                remaining -= len(chunk)
            GraphBase.need(not os.read(handle, 1), "reject an extended V98 owner")
            raw = b"".join(chunks)
            after = os.fstat(handle)
            GraphBase.need(
                GraphBase.digest(raw) == expected
                and (
                    before.st_dev, before.st_ino, before.st_size, before.st_nlink,
                    before.st_mtime_ns, before.st_ctime_ns,
                ) == (
                    after.st_dev, after.st_ino, after.st_size, after.st_nlink,
                    after.st_mtime_ns, after.st_ctime_ns,
                ),
                "reject changed bytes in a complete V98 source/output owner",
            )
            return raw, GraphBase.pin(path, expected, size)
        finally:
            os.close(handle)

    @staticmethod
    def runtime() -> None:
        GraphBase.need(
            os.path.realpath(sys.executable) == PYTHON
            and sys.implementation.name == "cpython"
            and sys.implementation.cache_tag == "cpython-314"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.dont_write_bytecode is True,
            "require the pinned isolated stable CPython 3.14.6 baseline",
        )


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject an unbounded complete V98 plaintext owner: " + label)
    if (
        not isinstance(relative, str)
        or relative.startswith("/")
        or ".." in relative.split("/")
        or relative.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
    ):
        raise ValueError("reject a compressed, private, native, or escaped V98 owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / relative), flags)
    try:
        before = os.fstat(handle)
        if not (
            stat.S_ISREG(before.st_mode)
            and before.st_uid == os.geteuid()
            and before.st_dev == 2064
            and before.st_ino == inode
            and before.st_size == size
            and before.st_nlink == 1
            and stat.S_IMODE(before.st_mode) == 0o600
        ):
            raise ValueError("reject a substituted complete V98 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject a truncated complete V98 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject an extended complete V98 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev, before.st_ino, before.st_size, before.st_nlink,
            before.st_mtime_ns, before.st_ctime_ns,
        ) != (
            after.st_dev, after.st_ino, after.st_size, after.st_nlink,
            after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ValueError("reject a changed complete V98 owner: " + label)
        return raw
    finally:
        os.close(handle)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V98 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V98 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V98 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V98 rejected inherited descriptors and unknown owners")
    if mode not in (None, "r", "rb"):
        raise ValueError("V98 source mode cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V98 source mode cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V98 rejected a private root or unopened holdout")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V98 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v98." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
        or "/holdout/" in normalized
        or "/candidates/" in normalized
    ):
        raise ValueError(
            "V98 rejected graph output, archive, candidate, or holdout: "
            + normalized
        )


def reject_descriptor_write(*arguments: object, **keywords: object) -> int:
    raise ValueError("V98 source-only operation rejected direct descriptor writing")


def guarded_fileio(
    file: object,
    mode: str = "r",
    closefd: bool = True,
    opener: object = None,
) -> object:
    if (
        type(file) is int
        or not isinstance(mode, str)
        or any(flag in mode for flag in ("w", "a", "x", "+"))
        or opener is not None
    ):
        raise ValueError("V98 source-only operation rejected direct _io writing")
    return ORIGINAL_FILEIO(file, mode, closefd)


def install_source_wall() -> None:
    sys.addaudithook(audit_wall)
    os.write = reject_descriptor_write
    if ORIGINAL_OS_WRITEV is not None:
        os.writev = reject_descriptor_write
    _io.FileIO = guarded_fileio
    io.FileIO = guarded_fileio


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V97["source"], "whole immutable published V97 renderer")
    previous = types.ModuleType("_rebar_exact_published_source_graph_v97")
    previous.__file__ = str(ROOT / V97["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    chain: tuple = ()
    base = GraphBase()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v97"
        and previous.SELF == V97["source"][0]
        and tuple(previous.SUITES) == SUITES
        and len(SUITES) == 13
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 0,
        "authenticate V97 source without executing historical candidate builders",
    )
    return previous, chain, base


def previous_pools(previous: types.ModuleType, chain: tuple) -> tuple:
    pools = V97_HISTORICAL_POOLS
    if len(pools) != 18 or len({item[0] for item in pools}) != 18:
        raise ValueError("require all eighteen exact complete V97 historical pools")
    return pools


def validate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and value.get("schema") == "rebar-candidate-current-overview-v97-summary"
        and value.get("version") == 97
        and value.get("status") == "PASS"
        and value.get("authenticated_evidence_owner_lower_bound") == 344
        and value.get("authenticated_history_reference_lower_bound") == 349
        and value.get("lossless_previous_v96_proof_pool_count") == 18
        and value.get("lossless_v96_all_eighteen_previous_pool_identity_status")
        == "PASS"
        and value.get("lossless_v96_snapshot_identity_status") == "PASS"
        and value.get("lossless_v96_family_identity_status") == "PASS"
        and value.get("v96_visible_footer_status")
        == "REJECTED; OVERBROAD COMPLETENESS CLAIM"
        and value.get("v96_rejected_svg_sha256")
        == "ec8ffd566b7da826441383c1fd44944189c153ffde252b9c8340e3e041770dcd"
        and value.get("original_case_execution_denominator") == CASE_COUNT
        and value.get("original_suite_count") == 13
        and value.get("named_private_waiver_count") == 13
        and value.get("separate_additional_reference_case_count")
        == SUPPLEMENTAL_CASE_COUNT
        and value.get("additional_cases_included_in_original_denominator") is False
        and value.get("rust_v22_original_campaign_verified_passing_case_count")
        == 14725
        and value.get("c_v10_original_campaign_verified_passing_case_count") == 13606
        and value.get("c_v10_original_campaign_observed_mismatch_lower_bound") == 606
        and value.get("c_v10_original_campaign_individual_mismatch_vector_count")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_complete_individual_mismatch_vectors")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_semantic_mismatch_count")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_candidate_execution_failure_count") == 5
        and value.get("c_v10_original_campaign_infrastructure_failure_count") == 0
        and value.get("c_v10_original_campaign_completed_suite_count") == 8
        and value.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and value.get("zig_v13_original_campaign_cleanup_warning_worker_count") == 13
        and value.get("zig_v14_controller_failure_candidate_worker_count")
        == "NOT MEASURED"
        and value.get("zig_v14_controller_failure_corrected_warning_count")
        == "NOT MEASURED"
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("expanded_holdout_final_protocol_status") == "NOT FROZEN"
        and value.get("expanded_holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and value.get("final_holdout_opened") is False
        and value.get("winner_selected") is False,
        "preserve the exact published V97, rejected V96, and unrepaired C10 history",
    )
    assert isinstance(value, dict)
    snapshot = value.get("snapshot")
    whole = base.canonical(snapshot)
    base.need(
        type(snapshot) is dict
        and snapshot.get("schema")
        == "rebar-candidate-current-overview-v97-compact-current-snapshot"
        and snapshot.get("version") == 97
        and len(whole) == V97_SNAPSHOT_BYTES
        and base.digest(whole) == V97_SNAPSHOT_SHA256,
        "authenticate every byte of the complete published V97 snapshot",
    )
    for key, size, expected, count in previous_pools(previous, chain):
        pool = value.get(key)
        raw = base.canonical(pool)
        base.need(
            type(pool) is dict
            and len(raw) == size
            and base.digest(raw) == expected
            and type(pool.get("entries")) is dict
            and len(pool["entries"]) == count,
            "retain the complete immutable historical V97 proof pool: " + key,
        )
    headline = value.get("headline")
    families = value.get("families")
    latest = value.get("latest_original_campaigns")
    base.need(
        type(headline) is dict
        and headline.get("verified_original_checks_by_candidate") == {
            "c": 13606,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 14725,
            "zig": 4607,
        }
        and headline.get("individual_failing_examples_fully_recorded") is False
        and type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and type(latest) is dict
        and set(latest) == {"rust", "c", "zig"}
        and latest["rust"].get("verified_passing_case_count") == 14725
        and latest["c"].get("verified_passing_case_count") == 13606
        and latest["zig"].get("verified_passing_case_count") == 4607,
        "preserve the exact V97 original denominator, families, and real campaigns",
    )
    return value


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    raw_assets: dict[str, bytes] = {}
    for role in ("inputs", "summary", "svg"):
        item = V97[role]
        raw_assets[role] = read_fixed(item, "whole immutable published V97 " + role)
    old = base.document(raw_assets["summary"], "whole immutable V97 summary")
    inputs = base.document(raw_assets["inputs"], "whole immutable V97 inputs")
    validate_previous(previous, chain, base, old)
    base.need(
        old.get("source")
        == base.pin(V97["source"][0], V97["source"][1], V97["source"][2])
        and old.get("inputs")
        == base.pin(V97["inputs"][0], V97["inputs"][1], V97["inputs"][2])
        and old.get("svg")
        == base.pin(V97["svg"][0], V97["svg"][1], V97["svg"][2])
        and inputs.get("schema")
        == "rebar-candidate-current-overview-v97-inputs"
        and inputs.get("version") == 97
        and base.canonical(inputs.get("snapshot"))
        == base.canonical(old["snapshot"])
        and base.canonical(inputs.get("headline"))
        == base.canonical(old["headline"])
        and previous.validate_visible_language(base, raw_assets["svg"])
        == raw_assets["svg"],
        "authenticate all four exact V97 owners without candidate-source access",
    )
    previous.validate_machine_language(base, old["headline"], old["snapshot"])
    predecessor = old.get("previous_overview")
    base.need(
        type(predecessor) is dict
        and set(predecessor) == set(previous.V96)
        and all(
            predecessor.get(role) == base.pin(item[0], item[1], item[2])
            for role, item in previous.V96.items()
        ),
        "preserve all exact rejected V96 predecessors without rerunning their graph",
    )
    return old


def validate_c_contract(base: types.ModuleType, value: object) -> dict:
    base.need(type(value) is dict, "require the complete genuine C11 source contract")
    assert isinstance(value, dict)
    policy = value.get("actual_operation_policy")
    phase = value.get("phase_one_v4")
    preserved = value.get("preserved_actual_c_v10_campaign")
    lossless = value.get("lossless_original_counterexample_evidence")
    holdout = value.get("expanded_holdout")
    source = value.get("source")
    protocol = value.get("protocol")
    wall = value.get("source_wall")
    effects = value.get("source_only_effects")
    base.need(
        value.get("schema") == "rebar-owned-repaired-c-original-campaign-v11-source-freeze"
        and value.get("version") == 11
        and value.get("family") == "c"
        and value.get("label") == "phase2-v21-c-original-match-semantics-original-p0-v11"
        and value.get("status") == "SOURCE FROZEN; ACTUAL C21 V11 ORIGINAL CAMPAIGN NOT RUN"
        and value.get("candidate_correctness") == "NOT MEASURED"
        and value.get("candidate_qualification") == "NOT ESTABLISHED"
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("holdout") == "NOT OPENED"
        and value.get("winner_selected") is False
        and type(source) is dict
        and source.get("path") == C11_SOURCE["source"][0]
        and source.get("sha256") == C11_SOURCE["source"][1]
        and source.get("bytes") == C11_SOURCE["source"][2]
        and type(protocol) is dict
        and protocol.get("path") == C11_SOURCE["protocol"][0]
        and protocol.get("sha256") == C11_SOURCE["protocol"][1]
        and protocol.get("bytes") == C11_SOURCE["protocol"][2]
        and type(phase) is dict
        and phase.get("original_case_execution_denominator") == CASE_COUNT
        and phase.get("original_suite_count") == 13
        and phase.get("named_private_waiver_count") == 13
        and phase.get("separate_reference_case_count") == SUPPLEMENTAL_CASE_COUNT
        and phase.get("separate_reference_cases_counted_in_original_denominator")
        is False
        and type(holdout) is dict
        and holdout.get("proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and holdout.get("final_protocol_status") == "NOT FROZEN"
        and holdout.get("case_status") == "NOT GENERATED; NOT OPENED"
        and holdout.get("source_mode_holdout_files_read") == 0,
        "reject a substituted C11 contract, false qualification, or opened holdout",
    )
    base.need(
        type(policy) is dict
        and policy.get("all_original_candidate_cases_required") == CASE_COUNT
        and policy.get("all_original_suite_workers_required") == 13
        and policy.get("distinct_worker_process_count_required") == 13
        and policy.get("all_observed_mismatch_records_preserved") is True
        and policy.get("exact_semantic_mismatch_total_requires_all_13_complete_suites")
        is True
        and policy.get("cross_candidate_engine") == "FORBIDDEN"
        and policy.get("external_regex_package") == "FORBIDDEN"
        and policy.get("fallback") == "FORBIDDEN"
        and policy.get("standard_library_engine") == "FORBIDDEN"
        and policy.get("source_mode_archive_physically_denied") is True
        and policy.get("source_mode_candidate_paths_physically_denied") is True
        and policy.get("source_mode_holdout_physically_denied") is True
        and policy.get("source_mode_native_physically_denied") is True
        and policy.get("previous_actual_v10_receipt_sha256")
        == HISTORICAL_C10_RECEIPT_SHA256
        and policy.get("previous_actual_v10_verified_passing_case_count") == 13606
        and policy.get("previous_actual_v10_semantic_mismatch_lower_bound") == 606
        and policy.get("previous_actual_v10_completed_original_suites") == 8
        and policy.get("previous_actual_v10_original_candidate_execution_failures") == 5
        and policy.get("previous_actual_v10_archived_recorded_counterexamples") == 92
        and policy.get("previous_actual_v10_archived_missing_counterexamples") == 514
        and policy.get("previous_actual_v10_exact_total_semantic_mismatches")
        == "NOT MEASURED"
        and policy.get("previous_actual_v10_missing_counterexample_status")
        == "NOT RECORDED; NEVER FABRICATED",
        "preserve the recorded historical C10 audit without claiming graph proof",
    )
    base.need(
        type(preserved) is dict
        and preserved.get("verified_passing_case_count") == 13606
        and preserved.get("observed_semantic_mismatch_lower_bound") == 606
        and preserved.get("archived_recorded_counterexamples") == 92
        and preserved.get("archived_missing_counterexamples") == 514
        and preserved.get("archived_missing_counterexample_status")
        == "NOT RECORDED; NEVER FABRICATED"
        and preserved.get("forensic_observation")
        == "INDEPENDENT READ-ONLY FULL-ARCHIVE AUDIT; NOT REOPENED"
        and preserved.get("full_archive_opened_in_source_mode") is False
        and type(preserved.get("actual_failure_receipt")) is dict
        and preserved["actual_failure_receipt"].get("sha256")
        == HISTORICAL_C10_RECEIPT_SHA256
        and type(lossless) is dict
        and lossless.get("previous_actual_v10_archived_recorded_counterexamples") == 92
        and lossless.get("previous_actual_v10_archived_missing_counterexamples") == 514
        and lossless.get("previous_actual_v10_missing_counterexample_status")
        == "NOT RECORDED; NEVER FABRICATED"
        and lossless.get("historical_compressed_archives_opened") == 0
        and type(wall) is dict
        and wall.get("compressed_archive_allowed") is False
        and wall.get("canonical_candidate_sources_allowed") is False
        and wall.get("holdout_allowed") is False
        and wall.get("native_binary_allowed") is False
        and type(effects) is dict
        and effects.get("actual_archives_opened") == 0
        and effects.get("actual_candidate_source_owners_opened") == 0
        and effects.get("actual_candidate_workers") == 0
        and effects.get("actual_holdout_cases_read") == 0
        and effects.get("actual_reference_workers") == 0,
        "retain the immutable prior audit as reported history, never a new archive read",
    )
    return value


def validate_c_receipt(
    base: types.ModuleType,
    value: object,
    contract: object,
) -> dict:
    validate_c_contract(base, contract)
    base.need(
        type(value) is dict and set(value) == C11_RECEIPT_KEYS,
        "require every exact field of the genuine small C11 durable receipt",
    )
    assert isinstance(value, dict)
    rows = value.get("suite_outcomes")
    vectors = value.get("complete_mismatch_suite_vector_fingerprints")
    archive = value.get("archive")
    base.need(
        value.get("schema")
        == "rebar-owned-repaired-c-original-campaign-v11-durable-publication-receipt"
        and value.get("version") == 11
        and value.get("status") == "PASS"
        and value.get("publication_status") == "PASS"
        and value.get("publication_pass_means") == "DURABLE CORRECTNESS PUBLICATION ONLY"
        and value.get("family") == "c"
        and value.get("label") == "phase2-v21-c-original-match-semantics-original-p0-v11"
        and value.get("source_sha256") == C11_SOURCE["source"][1]
        and value.get("protocol_sha256") == C11_SOURCE["protocol"][1]
        and value.get("contract_sha256") == C11_SOURCE["contract"][1]
        and value.get("preserved_actual_v10_failure_receipt_sha256")
        == HISTORICAL_C10_RECEIPT_SHA256
        and value.get("case_execution_denominator") == CASE_COUNT
        and value.get("suite_count") == 13
        and value.get("attempted_suite_count") == 13
        and value.get("actual_candidate_workers") == 13
        and value.get("actual_worker_process_ids") == list(EXPECTED_WORKER_IDS)
        and value.get("actual_worker_process_ids_are_distinct") is True
        and value.get("verified_passing_case_count") == 16262
        and value.get("completed_suite_count") == 11
        and value.get("candidate_execution_failure_count") == 2
        and value.get("infrastructure_failure_count") == 0
        and value.get("worker_timeout_count") == 0
        and value.get("observed_semantic_mismatch_lower_bound") == 606
        and value.get("complete_observed_semantic_mismatch_record_count") == 606
        and value.get("complete_mismatch_chunk_count") == 21
        and value.get("complete_mismatch_suite_count") == 11
        and value.get("all_observed_semantic_mismatch_records_preserved") is True
        and value.get("semantic_mismatch_count") == "NOT MEASURED"
        and value.get("counterexample_preview_only") is False
        and value.get("counterexample_normalization_before_original_comparison")
        is False
        and value.get("candidate_status") == "FAIL"
        and value.get("candidate_qualified") is False
        and value.get("named_private_waiver_count") == 13
        and value.get("separate_reference_case_count") == SUPPLEMENTAL_CASE_COUNT
        and value.get("separate_reference_cases_counted_as_candidate_cases") is False
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("holdout") == "NOT OPENED"
        and value.get("hidden_cases_read") == 0
        and value.get("benchmark_files_read") == 0
        and value.get("clock_samples") == 0
        and value.get("timing_trials_run") == 0
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("winner_selected") is False
        and value.get("original_source_targets_modified") == 0
        and value.get("original_native_inode_restored") is True
        and value.get("transient_physical_interpreter_creations") == "NOT MEASURED"
        and value.get("successfully_returned_guarded_interpreter_creations")
        == "NOT MEASURED"
        and value.get("zero_returned_creations_proves_zero_physical_creations")
        is False,
        "reject false C11 completion, qualification, timing, loss totals, or holdout",
    )
    base.need(
        type(archive) is dict
        and set(archive) == C11_ARCHIVE_KEYS
        and archive.get("path")
        == "oracle/phase2/evidence/"
        "repaired-c-original-campaign-v11-c-phase2-v21-c-original-match-"
        "semantics-original-p0-v11-failures.json.gz"
        and archive.get("sha256")
        == "2d580a5d321767b1753a645961d717cbc4345f1151c7a0d34304d6e6579cc609"
        and archive.get("bytes") == 195101
        and archive.get("device") == 2064
        and archive.get("inode") == 525588
        and archive.get("mode") == "0600"
        and archive.get("nlink") == 1
        and archive.get("exclusive_creation") is True
        and archive.get("file_fsync_completed") is True
        and archive.get("directory_fsync_completed") is True,
        "retain only receipt-bound C11 archive metadata; never open or stat the archive",
    )
    base.need(
        type(rows) is list
        and len(rows) == 13
        and type(vectors) is list
        and len(vectors) == 11,
        "require all 13 real original C workers and all 11 complete result vectors",
    )
    vector_by_suite: dict[str, dict] = {}
    for vector in vectors:
        base.need(
            type(vector) is dict
            and set(vector) == C11_VECTOR_KEYS
            and type(vector.get("suite")) is str
            and vector["suite"] not in vector_by_suite
            and vector.get("all_observed_records_preserved") is True
            and type(vector.get("case_execution_denominator")) is int
            and type(vector.get("complete_chunk_count")) is int
            and type(vector.get("complete_record_count")) is int
            and vector["complete_chunk_count"] >= 0
            and vector["complete_record_count"] >= 0
            and type(vector.get("complete_vector_sha256")) is str
            and len(vector["complete_vector_sha256"]) == 64,
            "reject an absent, duplicate, partial, or invented C11 result vector",
        )
        vector_by_suite[vector["suite"]] = vector
    pass_count = 0
    incomplete_count = 0
    mismatch_suite_count = 0
    verified = 0
    observed = 0
    workers: list[int] = []
    for index, (name, denominator) in enumerate(SUITES):
        row = rows[index]
        base.need(
            type(row) is dict
            and set(row) == C11_ROW_KEYS
            and row.get("suite") == name
            and row.get("case_execution_denominator") == denominator
            and row.get("actual_candidate_workers") == 1
            and row.get("worker_process_id") == EXPECTED_WORKER_IDS[index],
            "reject an omitted, reordered, invented, or shared C11 worker: " + name,
        )
        workers.append(row["worker_process_id"])
        if name in ("original_bounded_v5", "subinterpreter_v2"):
            base.need(
                row.get("status") == "FAIL"
                and row.get("failure_class") == "CANDIDATE EXECUTION FAILURE"
                and row.get("mismatch_count") == "NOT MEASURED"
                and type(row.get("plain_failure_diagnostic")) is str
                and bool(row["plain_failure_diagnostic"])
                and name not in vector_by_suite,
                "do not turn a genuine incomplete C11 group into a measured result",
            )
            incomplete_count += 1
            continue
        vector = vector_by_suite.get(name)
        base.need(
            type(vector) is dict
            and vector["case_execution_denominator"] == denominator,
            "require the exact complete digest-bound C11 vector for " + name,
        )
        if name in EXPECTED_MISMATCHES:
            count, chunks, digest = EXPECTED_MISMATCHES[name]
            base.need(
                row.get("status") == "FAIL"
                and row.get("failure_class") == "SEMANTIC MISMATCH"
                and row.get("mismatch_count") == count
                and vector["complete_record_count"] == count
                and vector["complete_chunk_count"] == chunks
                and vector["complete_vector_sha256"] == digest,
                "preserve every complete observed C11 mismatch in " + name,
            )
            mismatch_suite_count += 1
            observed += count
        else:
            base.need(
                row.get("status") == "PASS"
                and row.get("failure_class") == "PASS"
                and row.get("mismatch_count") == 0
                and row.get("plain_failure_diagnostic") == ""
                and vector["complete_record_count"] == 0
                and vector["complete_chunk_count"] == 0
                and vector["complete_vector_sha256"] == EMPTY_VECTOR_SHA256,
                "count only an actually passing fully completed C11 suite: " + name,
            )
            pass_count += 1
            verified += denominator
    base.need(
        len(set(workers)) == 13
        and tuple(workers) == EXPECTED_WORKER_IDS
        and pass_count == 6
        and incomplete_count == 2
        and mismatch_suite_count == 5
        and verified == 16262
        and observed == 606
        and sum(vector["complete_record_count"] for vector in vectors) == 606
        and sum(vector["complete_chunk_count"] for vector in vectors) == 21
        and set(vector_by_suite)
        == {name for name, _ in SUITES}
        - {"original_bounded_v5", "subinterpreter_v2"},
        "derive C11 headline counts only from all real original rows and vectors",
    )
    return value


def load_new_evidence(base: types.ModuleType) -> tuple[dict, dict, dict]:
    source_raw = read_fixed(C11_SOURCE["source"], "complete C11 campaign controller")
    protocol_raw = read_fixed(C11_SOURCE["protocol"], "complete frozen C11 protocol")
    contract_raw = read_fixed(C11_SOURCE["contract"], "complete frozen C11 contract")
    receipt_raw = read_fixed(C11_RECEIPT, "complete real C11 publication receipt")
    base.need(
        len(source_raw) == C11_SOURCE["source"][2]
        and len(protocol_raw) == C11_SOURCE["protocol"][2]
        and b"92 individual examples" in protocol_raw
        and b"remaining 514" in protocol_raw
        and b"never opens, inflates" in protocol_raw,
        "authenticate the complete C11 controller and prior-audit-only protocol",
    )
    contract = base.document(contract_raw, "whole immutable C11 source contract")
    receipt = base.document(receipt_raw, "whole actual C11 publication receipt")
    validate_c_contract(base, contract)
    validate_c_receipt(base, receipt, contract)
    base.need(
        base.canonical(contract) == contract_raw
        and base.canonical(receipt) == receipt_raw,
        "retain every exact canonical byte of actual C11 public evidence",
    )
    facts = {
        "schema": SCHEMA + "-validated-c11-original-outcome-v1",
        "family": "c",
        "display_name": "C",
        "candidate_status": "FAIL",
        "candidate_qualified": False,
        "case_execution_denominator": CASE_COUNT,
        "attempted_suite_count": 13,
        "actual_candidate_worker_count": 13,
        "actual_worker_process_ids": list(EXPECTED_WORKER_IDS),
        "unique_candidate_worker_count": 13,
        "completed_suite_count": 11,
        "clean_suite_count": 6,
        "mismatch_suite_count": 5,
        "candidate_execution_failure_count": 2,
        "infrastructure_failure_count": 0,
        "worker_timeout_count": 0,
        "verified_passing_case_count": 16262,
        "observed_semantic_mismatch_lower_bound": 606,
        "complete_observed_individual_mismatch_record_count": 606,
        "complete_observed_mismatch_chunk_count": 21,
        "complete_observed_mismatch_vector_count": 11,
        "source_canonical_completed_suite_vector_count": 10,
        "transport_only_completed_suite_vector_count": 1,
        "transport_only_completed_suite_name": "public_surface_v19",
        "transport_only_observed_individual_mismatch_record_count": 114,
        "transport_only_observed_mismatch_chunk_count": 4,
        "transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "all_observed_c11_individual_mismatch_records_preserved": True,
        "aggregate_semantic_mismatch_count": "NOT MEASURED",
        "incomplete_original_suite_names": [
            "original_bounded_v5", "subinterpreter_v2"
        ],
        "complete_original_suite_rows": copy.deepcopy(receipt["suite_outcomes"]),
        "complete_observed_vector_fingerprints": copy.deepcopy(
            receipt["complete_mismatch_suite_vector_fingerprints"]
        ),
        "historical_c10_audit_recorded_counterexample_count": 92,
        "historical_c10_audit_unrecorded_counterexample_count": 514,
        "historical_c10_audit_evidence_status": HISTORICAL_C10_RECORD_STATUS,
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "archive_metadata_only": True,
        "compressed_archive_opened_by_graph": False,
        "compressed_archive_statted_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "source_sha256": C11_SOURCE["source"][1],
        "protocol_sha256": C11_SOURCE["protocol"][1],
        "contract_sha256": C11_SOURCE["contract"][1],
        "complete_plaintext_receipt_sha256": C11_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C11_RECEIPT[2],
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
    }
    return contract, receipt, facts


def make_evidence_pool(
    base: types.ModuleType,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> dict:
    proof = {
        "schema": SCHEMA + "-complete-c11-public-evidence-v1",
        "family": "c",
        "complete_first_party_source_owner_count": 3,
        "complete_first_party_source_owners": [
            base.pin(item[0], item[1], item[2])
            for item in C11_SOURCE.values()
        ],
        "complete_source_contract": copy.deepcopy(contract),
        "complete_source_contract_embedded": True,
        "complete_source_contract_sha256": C11_SOURCE["contract"][1],
        "complete_source_contract_bytes": C11_SOURCE["contract"][2],
        "complete_plaintext_receipt": copy.deepcopy(receipt),
        "complete_plaintext_receipt_embedded": True,
        "complete_plaintext_receipt_sha256": C11_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C11_RECEIPT[2],
        "validated_campaign_outcome": copy.deepcopy(facts),
        "complete_observed_c11_individual_records_only": True,
        "source_canonical_completed_suite_vector_count": 10,
        "transport_only_completed_suite_vector_count": 1,
        "transport_only_completed_suite_name": "public_surface_v19",
        "transport_only_observed_individual_mismatch_record_count": 114,
        "transport_only_observed_mismatch_chunk_count": 4,
        "transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "historical_c10_audit_evidence_status": HISTORICAL_C10_RECORD_STATUS,
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "compressed_archive_opened_by_graph": False,
        "compressed_archive_statted_by_graph": False,
        "private_build_root_opened_by_graph": False,
        "candidate_workers_started_by_graph": 0,
    }
    return {
        "schema": SCHEMA + "-lossless-c11-public-evidence-pool-v1",
        "entries": {C11_RECEIPT[1]: proof},
    }


def validate_evidence_pool(
    base: types.ModuleType,
    pool: object,
    contract: dict,
    receipt: dict,
    facts: dict,
) -> dict:
    validate_c_receipt(base, receipt, contract)
    expected = make_evidence_pool(base, contract, receipt, facts)
    base.need(
        type(pool) is dict
        and pool.get("schema") == expected["schema"]
        and type(pool.get("entries")) is dict
        and set(pool["entries"]) == {C11_RECEIPT[1]}
        and base.canonical(pool) == base.canonical(expected),
        "preserve every exact actual C11 receipt, contract, vector, and proof byte",
    )
    return pool


def evidence_reference(base: types.ModuleType, proof: dict) -> dict:
    raw = base.canonical(proof)
    return {
        "schema": SCHEMA + "-complete-public-evidence-reference-v1",
        "family": "c",
        "complete_first_party_source_owner_count": 3,
        "complete_plaintext_receipt_sha256": C11_RECEIPT[1],
        "complete_plaintext_receipt_bytes": C11_RECEIPT[2],
        "complete_reference_sha256": base.digest(raw),
        "complete_reference_canonical_bytes": len(raw),
    }


def resolve_reference(
    base: types.ModuleType,
    pool: dict,
    reference: object,
) -> dict:
    base.need(type(reference) is dict, "require the exact C11 evidence reference")
    assert isinstance(reference, dict)
    proof = pool.get("entries", {}).get(C11_RECEIPT[1])
    base.need(
        type(proof) is dict
        and base.canonical(reference)
        == base.canonical(evidence_reference(base, proof)),
        "reject substituted, missing, or mismatched complete C11 public evidence",
    )
    return proof


def validate_visible_language(base: types.ModuleType, raw: object) -> bytes:
    base.need(
        type(raw) is bytes and 0 < len(raw) <= OWNER_LIMIT,
        "reject absent or unbounded V98 public language",
    )
    assert isinstance(raw, bytes)
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ValueError("reject inaccessible non-UTF-8 V98 public language") from error
    normalized = " ".join(text.casefold().split())
    base.need(
        text.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        and '<title id="title">' in text
        and '<desc id="description">' in text
        and VISIBLE_FOOTER in text
        and "31,237 / 31,237 (100%)" in text
        and "16,262 / 31,237 (52.1%)" in text
        and "14,725 / 31,237 (47.1%)" in text
        and "4,607 / 31,237 (14.7%)" in text
        and "606 current c11 examples" in normalized
        and "21 recorded chunks" in normalized
        and "11 completed groups" in normalized
        and "10 source-canonical" in normalized
        and "1 transport-only" in normalized
        and "114 records" in normalized
        and "source digest not provided by the original observer" in normalized
        and "two incomplete original groups" in normalized
        and "zero infrastructure failures" in normalized
        and "zero timeouts" in normalized
        and "earlier c10 audit reported 92 recorded" in normalized
        and "514 not recorded" in normalized
        and "not independently established by this graph" in normalized
        and "historical losses not repaired" in normalized
        and "not measured" in normalized
        and "not frozen" in normalized
        and "not generated" in normalized
        and "not opened" in normalized
        and "no winner" in normalized,
        "require honest, plain, accessible current C11 and unrepaired C10 disclosures",
    )
    for phrase in FORBIDDEN_VISIBLE_PHRASES:
        base.need(
            phrase not in normalized,
            "reject false historical completeness, candidate qualification, or speed",
        )
    return raw


def validate_machine_language(
    base: types.ModuleType,
    headline: object,
    snapshot: object,
) -> None:
    base.need(
        type(headline) is dict
        and type(snapshot) is dict
        and headline.get("public_reporting_integrity") == VISIBLE_POLICY
        and headline.get("original_python_check_count") == CASE_COUNT
        and headline.get("verified_original_checks_by_candidate") == {
            "c": 16262,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 14725,
            "zig": 4607,
        }
        and headline.get("c_current_verified_original_checks") == 16262
        and headline.get("c_current_complete_observed_individual_mismatch_records")
        == 606
        and headline.get("c_current_complete_observed_mismatch_chunks") == 21
        and headline.get("c_current_source_canonical_completed_suite_vector_count")
        == 10
        and headline.get("c_current_transport_only_completed_suite_vector_count")
        == 1
        and headline.get("c_current_transport_only_completed_suite_name")
        == "public_surface_v19"
        and headline.get("c_current_transport_only_observed_individual_mismatch_record_count")
        == 114
        and headline.get("c_current_transport_only_original_source_vector_sha256")
        == "NOT PROVIDED BY THE ORIGINAL OBSERVER"
        and headline.get("c_current_completed_original_suite_count") == 11
        and headline.get("c_current_candidate_worker_count") == 13
        and headline.get("c_incomplete_candidate_worker_count") == 2
        and headline.get("c_infrastructure_failure_count") == 0
        and headline.get("c_worker_timeout_count") == 0
        and headline.get("c_complete_mismatch_total") == "NOT MEASURED"
        and headline.get("c_current_observed_individual_records_preserved") is True
        and headline.get("historical_c10_audit_evidence_status")
        == HISTORICAL_C10_RECORD_STATUS
        and headline.get("historical_c10_records_independently_established_by_graph")
        is False
        and headline.get("historical_c10_records_repaired") is False
        and headline.get("historical_c10_audit_recorded_counterexample_count") == 92
        and headline.get("historical_c10_audit_unrecorded_counterexample_count") == 514
        and headline.get("bars_measure")
        == "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED"
        and headline.get("speed_relative_to_python") == "NOT MEASURED"
        and headline.get("performance") == "NOT MEASURED"
        and headline.get("memory") == "NOT MEASURED"
        and headline.get("fully_compatible_candidate_count") == 0
        and headline.get("winner_selected") is False
        and snapshot.get("public_reporting_integrity") == VISIBLE_POLICY
        and snapshot.get("c_v11_original_campaign_verified_passing_case_count")
        == 16262
        and snapshot.get("c_v11_original_campaign_complete_observed_individual_mismatch_record_count")
        == 606
        and snapshot.get("c_v11_original_campaign_complete_observed_mismatch_chunk_count")
        == 21
        and snapshot.get("c_v11_original_campaign_source_canonical_completed_suite_vector_count")
        == 10
        and snapshot.get("c_v11_original_campaign_transport_only_completed_suite_vector_count")
        == 1
        and snapshot.get("c_v11_original_campaign_transport_only_completed_suite_name")
        == "public_surface_v19"
        and snapshot.get("c_v11_original_campaign_transport_only_observed_individual_mismatch_record_count")
        == 114
        and snapshot.get("c_v11_original_campaign_transport_only_original_source_vector_sha256")
        == "NOT PROVIDED BY THE ORIGINAL OBSERVER"
        and snapshot.get("c_v11_original_campaign_semantic_mismatch_count")
        == "NOT MEASURED"
        and snapshot.get("historical_c10_audit_evidence_status")
        == HISTORICAL_C10_RECORD_STATUS
        and snapshot.get("historical_c10_records_independently_established_by_graph")
        is False
        and snapshot.get("historical_c10_records_repaired") is False
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("winner_selected") is False,
        "reject fabricated C11 totals, historical recovery, benchmarks, or winner",
    )
    assert isinstance(headline, dict)
    assert isinstance(snapshot, dict)
    for text in (
        headline["public_reporting_integrity"],
        headline["historical_c10_audit_evidence_status"],
        snapshot["public_reporting_integrity"],
        snapshot["historical_c10_audit_evidence_status"],
    ):
        normalized = " ".join(text.casefold().split())
        for phrase in FORBIDDEN_VISIBLE_PHRASES:
            base.need(
                phrase not in normalized,
                "reject false machine-readable historical loss or qualification",
            )


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "All 13 original groups passed", "BASELINE", "#34d399"),
        (
            "C", 16262,
            "6 passed; 5 differ; 2 incomplete; all 606 current C11 examples recorded",
            "NOT YET COMPATIBLE", "#fbbf24",
        ),
        (
            "Rust", 14725,
            "9 passed; 3 differ; 1 incomplete; captured failed-worker warnings remain",
            "NOT YET COMPATIBLE", "#fb7185",
        ),
        (
            "Zig", 4607,
            "Earlier result only; 13 workers warned; newer run stopped before matching",
            "NOT YET COMPATIBLE", "#fbbf24",
        ),
        ("C++", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Go", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Fortran", None, "Independent builds disagreed; matching not measured", "BUILD FAILED", "#fb7185"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1560" height="1276" '
        'viewBox="0 0 1560 1276" role="img" aria-labelledby="title description">',
        '<title id="title">Actual progress toward a faster Python re</title>',
        '<desc id="description">Bars show confirmed correct original Python '
        'regular-expression checks, not speed. Python passes 31,237 out of '
        '31,237, or 100 percent. C passes 16,262, or 52.1 percent; Rust '
        'passes 14,725, or 47.1 percent; Zig passes 4,607, or 14.7 percent. '
        'Thirteen real C workers attempted the original groups; 11 completed '
        'groups. All 606 current C11 examples are preserved in 21 recorded '
        'chunks. There are 10 source-canonical completed vectors and '
        '1 transport-only public-surface vector with 114 records; source '
        'digest not provided by the original observer. Two incomplete '
        'original groups remain, with zero '
        'infrastructure failures and zero timeouts. An earlier C10 audit '
        'reported 92 recorded and 514 not recorded; those audit counts are '
        'not independently established by this graph and historical losses '
        'are not repaired. The speed, memory and runtime independence are '
        'not measured or not established. The proposed 14,155,776-case '
        'comparison is not frozen, not generated, and not opened. No '
        'fully compatible candidate and no winner.</desc>',
        '<rect width="1560" height="1276" rx="24" fill="#0b1220"/>',
        '<text x="48" y="66" fill="#f8fafc" font-size="32" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Building a faster Python re, from scratch</text>',
        '<text x="49" y="103" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">C improved; no fully compatible '
        'replacement; speed not measured; no winner</text>',
        '<rect x="46" y="126" width="1468" height="82" rx="13" fill="#172338"/>',
        '<text x="66" y="157" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'These bars show correctness against Python, not speed.</text>',
        '<text x="66" y="185" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">Every bar uses the same 31,237 '
        'original checks. Failures, incomplete groups and unmeasured checks '
        'are never counted as passing.</text>',
        '<text x="50" y="247" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="159" y="247" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL PYTHON CHECKS CONFIRMED</text>',
        '<text x="730" y="247" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'WHAT THE ACTUAL RUN RECORDED</text>',
        '<text x="1291" y="247" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">SPEED</text>',
        '<text x="1510" y="247" text-anchor="end" fill="#94a3b8" '
        'font-size="12" font-family="system-ui,sans-serif" '
        'font-weight="690">RESULT</text>',
        '<line x1="46" y1="265" x2="1514" y2="265" stroke="#334155"/>',
    ]
    for index, (name, passed, details, result, colour) in enumerate(rows):
        y = 308 + 68 * index
        parts.append(
            f'<text x="51" y="{y}" fill="#f8fafc" font-size="16" '
            f'font-family="system-ui,sans-serif" font-weight="670">{name}</text>'
        )
        parts.append(
            f'<rect x="158" y="{y - 16}" width="314" height="20" '
            'rx="6" fill="#1e293b"/>'
        )
        if passed is None:
            label = "NOT MEASURED"
        else:
            width = max(3, round(314 * passed / CASE_COUNT))
            percent = "100%" if passed == CASE_COUNT else f"{100 * passed / CASE_COUNT:.1f}%"
            parts.append(
                f'<rect x="158" y="{y - 16}" width="{width}" height="20" '
                f'rx="6" fill="{colour}"/>'
            )
            label = f"{passed:,} / {CASE_COUNT:,} ({percent})"
        parts.append(
            f'<text x="483" y="{y}" fill="#e2e8f0" font-size="12" '
            f'font-family="system-ui,sans-serif">{label}</text>'
        )
        parts.append(
            f'<text x="730" y="{y}" fill="#cbd5e1" font-size="10" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1291" y="{y}" fill="#94a3b8" font-size="11" '
            'font-family="system-ui,sans-serif">NOT MEASURED</text>'
        )
        parts.append(
            f'<text x="1510" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="10" font-family="system-ui,sans-serif" '
            f'font-weight="730">{result}</text>'
        )
    parts.extend((
        '<line x1="46" y1="757" x2="1514" y2="757" stroke="#334155"/>',
        '<text x="51" y="789" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'What the new C run actually established</text>',
        '<text x="51" y="819" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">13 real workers; 11 completed '
        'groups; all 606 current C11 examples preserved in 21 recorded '
        'chunks.</text>',
        '<text x="51" y="847" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">10 source-canonical vectors; '
        '1 transport-only public-surface vector; 114 records; source digest '
        'not provided by the original observer.</text>',
        '<text x="51" y="875" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">Two incomplete original groups; '
        'zero infrastructure failures; zero timeouts. The complete overall '
        'failure total remains NOT MEASURED.</text>',
        '<rect x="46" y="902" width="1468" height="104" rx="13" fill="#172338"/>',
        '<text x="66" y="934" fill="#f8fafc" font-size="15" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'History stays honest</text>',
        '<text x="66" y="961" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">Earlier C10 audit reported '
        '92 recorded / 514 not recorded; not independently established '
        'by this graph.</text>',
        '<text x="66" y="986" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">Historical losses not repaired. '
        'The new 606 recorded examples apply only to the new C11 run.</text>',
        '<rect x="46" y="1026" width="1468" height="108" rx="13" fill="#172338"/>',
        '<text x="66" y="1058" fill="#f8fafc" font-size="15" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Future speed comparison: proposed 14,155,776 cases</text>',
        '<text x="66" y="1086" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">NOT FROZEN; NOT GENERATED; '
        'NOT OPENED; NOT RUN. Speed, memory, confidence and rankings: '
        'NOT MEASURED.</text>',
        '<text x="66" y="1111" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The separate 8,244 reference '
        'checks are not added to the 31,237 original checks.</text>',
        '<text x="51" y="1173" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The C improvement is real. '
        'Compatibility, speed and a winner are not established.</text>',
        '<text x="51" y="1204" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">Overview 98; '
        + VISIBLE_FOOTER
        + "</text>",
        "</svg>",
        "",
    ))
    return "\n".join(parts).encode("utf-8")


def changes() -> dict:
    return {
        "actual_current_graph_predecessor_version": 97,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v98_new_directly_authenticated_evidence_owner_count": 4,
        "lossless_previous_v97_proof_pool_count": 18,
        "lossless_v97_all_eighteen_previous_pool_identity_status": "PASS",
        "lossless_v97_snapshot_identity_status": "PASS",
        "lossless_v97_family_identity_status": "PASS",
        "lossless_v98_complete_c11_public_receipt_count": 1,
        "lossless_v98_complete_c11_source_owner_count": 3,
        "v96_visible_footer_status": "REJECTED; OVERBROAD COMPLETENESS CLAIM",
        "v96_rejected_svg_sha256":
        "ec8ffd566b7da826441383c1fd44944189c153ffde252b9c8340e3e041770dcd",
        "v96_rejected_svg_bytes": 9633,
        "public_reporting_integrity": VISIBLE_POLICY,
        "published_c_suite_outcomes_preserved": True,
        "published_c_suite_outcome_count": 13,
        "individual_failing_examples_fully_recorded": False,
        "c_v11_all_observed_individual_mismatch_records_preserved": True,
        "c_v11_original_campaign_actual_worker_count": 13,
        "c_v11_original_campaign_distinct_worker_count": 13,
        "c_v11_original_campaign_attempted_suite_count": 13,
        "c_v11_original_campaign_clean_suite_count": 6,
        "c_v11_original_campaign_mismatch_suite_count": 5,
        "c_v11_original_campaign_completed_suite_count": 11,
        "c_v11_original_campaign_candidate_execution_failure_count": 2,
        "c_v11_original_campaign_infrastructure_failure_count": 0,
        "c_v11_original_campaign_worker_timeout_count": 0,
        "c_v11_original_campaign_verified_passing_case_count": 16262,
        "c_v11_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v11_original_campaign_complete_observed_individual_mismatch_record_count":
        606,
        "c_v11_original_campaign_complete_observed_mismatch_chunk_count": 21,
        "c_v11_original_campaign_complete_observed_mismatch_vector_count": 11,
        "c_v11_original_campaign_source_canonical_completed_suite_vector_count": 10,
        "c_v11_original_campaign_transport_only_completed_suite_vector_count": 1,
        "c_v11_original_campaign_transport_only_completed_suite_name":
        "public_surface_v19",
        "c_v11_original_campaign_transport_only_observed_individual_mismatch_record_count":
        114,
        "c_v11_original_campaign_transport_only_observed_mismatch_chunk_count": 4,
        "c_v11_original_campaign_transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "c_v11_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v11_original_campaign_candidate_status": "FAIL",
        "c_v11_original_campaign_candidate_qualified": False,
        "c_v11_original_campaign_incomplete_suite_names": [
            "original_bounded_v5", "subinterpreter_v2"
        ],
        "c_v11_verified_passing_case_increase_from_v97": 2656,
        "historical_c10_audit_recorded_counterexample_count": 92,
        "historical_c10_audit_unrecorded_counterexample_count": 514,
        "historical_c10_audit_evidence_status": HISTORICAL_C10_RECORD_STATUS,
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "timing_trials_run": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_source_owners_opened_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def build(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin every byte of the complete immutable V98 renderer",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable V98 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V97.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete actual published V97 " + role,
        )
    for role, item in C11_SOURCE.items():
        base.need(
            getattr(options, "c_" + role + "_sha256") == item[1],
            "caller-pin the complete genuine C11 " + role,
        )
    for role, item in HISTORICAL_C10.items():
        base.need(
            getattr(options, "historical_c_" + role + "_sha256") == item[1]
            and previous.C_SOURCE[role][0] == item[0]
            and previous.C_SOURCE[role][1] == item[1],
            "caller-pin the unchanged historical C10 " + role,
        )
    for role, item in HISTORICAL_ZIG14.items():
        base.need(
            getattr(options, "historical_zig_" + role + "_sha256") == item[1]
            and previous.ZIG14_SOURCE[role][0] == item[0]
            and previous.ZIG14_SOURCE[role][1] == item[1],
            "caller-pin the unchanged historical Zig14 " + role,
        )
    base.need(
        options.c_receipt_sha256 == C11_RECEIPT[1]
        and options.historical_c_receipt_sha256 == HISTORICAL_C10_RECEIPT_SHA256
        and options.historical_zig_controller_receipt_sha256
        == HISTORICAL_ZIG14_RECEIPT_SHA256
        and previous.C_RECEIPT[1] == HISTORICAL_C10_RECEIPT_SHA256
        and previous.ZIG14_RECEIPT[1] == HISTORICAL_ZIG14_RECEIPT_SHA256,
        "caller-pin the genuine new C11 and both immutable historic receipts",
    )
    old = authenticate_previous(previous, chain, base)
    contract, receipt, facts = load_new_evidence(base)
    pool = make_evidence_pool(base, contract, receipt, facts)
    validate_evidence_pool(base, pool, contract, receipt, facts)
    proof = pool["entries"][C11_RECEIPT[1]]
    reference = evidence_reference(base, proof)
    base.need(
        base.canonical(resolve_reference(base, pool, reference))
        == base.canonical(proof)
        and base.canonical(proof["validated_campaign_outcome"])
        == base.canonical(facts)
        and old["c_v10_original_campaign_individual_mismatch_vector_count"]
        == "NOT MEASURED"
        and old["c_v10_original_campaign_complete_individual_mismatch_vectors"]
        == "NOT MEASURED",
        "keep exact current C11 proof separate from unrepaired historical C10",
    )
    delta = changes()
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V97.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 98,
        "previous_complete_snapshot_sha256": V97_SNAPSHOT_SHA256,
        "previous_complete_snapshot_canonical_bytes": V97_SNAPSHOT_BYTES,
        "previous_complete_overview_sha256": V97["summary"][1],
        "previous_complete_overview_bytes": V97["summary"][2],
        **copy.deepcopy(delta),
    })
    headline = copy.deepcopy(old["headline"])
    headline.update({
        "public_reporting_integrity": VISIBLE_POLICY,
        "verified_original_checks_by_candidate": {
            "c": 16262,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 14725,
            "zig": 4607,
        },
        "c_current_verified_original_checks": 16262,
        "c_previous_verified_original_checks": 13606,
        "c_verified_check_change_from_previous_graph": 2656,
        "c_current_candidate_worker_count": 13,
        "c_current_completed_original_suite_count": 11,
        "c_incomplete_candidate_worker_count": 2,
        "c_infrastructure_failure_count": 0,
        "c_worker_timeout_count": 0,
        "c_observed_mismatch_lower_bound": 606,
        "c_current_complete_observed_individual_mismatch_records": 606,
        "c_current_complete_observed_mismatch_chunks": 21,
        "c_current_complete_observed_mismatch_vector_count": 11,
        "c_current_source_canonical_completed_suite_vector_count": 10,
        "c_current_transport_only_completed_suite_vector_count": 1,
        "c_current_transport_only_completed_suite_name": "public_surface_v19",
        "c_current_transport_only_observed_individual_mismatch_record_count": 114,
        "c_current_transport_only_observed_mismatch_chunk_count": 4,
        "c_current_transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "c_current_observed_individual_records_preserved": True,
        "c_complete_mismatch_total": "NOT MEASURED",
        "individual_failing_examples_fully_recorded": False,
        "historical_c10_audit_recorded_counterexample_count": 92,
        "historical_c10_audit_unrecorded_counterexample_count": 514,
        "historical_c10_audit_evidence_status": HISTORICAL_C10_RECORD_STATUS,
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "bars_measure": "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED",
        "speed_relative_to_python": "NOT MEASURED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "fully_compatible_candidate_count": 0,
        "winner_selected": False,
    })
    validate_machine_language(base, headline, snapshot)
    svg_raw = validate_visible_language(base, make_svg())
    inputs = {
        "schema": SCHEMA + "-inputs",
        "version": 98,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": copy.deepcopy(predecessor),
        "headline": copy.deepcopy(headline),
        "snapshot": copy.deepcopy(snapshot),
        "complete_original_suites": [
            {"suite": suite, "case_execution_denominator": count}
            for suite, count in SUITES
        ],
        **copy.deepcopy(delta),
    }
    inputs_raw = base.canonical(inputs)
    families = copy.deepcopy(old["families"])
    c_family = families[2]
    base.need(c_family.get("family") == "c", "retain the exact first-party C family")
    c_family.update({
        "actual_candidate_workers": 13,
        "current_original_campaign_candidate_status": "FAIL",
        "current_original_campaign_candidate_worker_count": 13,
        "current_original_campaign_infrastructure_failure_count": 0,
        "current_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "current_original_campaign_verified_passing_case_count": 16262,
        "c_v11_actual_original_campaign": copy.deepcopy(reference),
        "c_v11_observed_individual_mismatch_records": 606,
        "c_v11_observed_individual_mismatch_chunks": 21,
        "c_v11_observed_individual_records_preserved": True,
        "c_v11_source_canonical_completed_suite_vector_count": 10,
        "c_v11_transport_only_completed_suite_vector_count": 1,
        "c_v11_transport_only_completed_suite_name": "public_surface_v19",
        "c_v11_transport_only_observed_individual_mismatch_record_count": 114,
        "c_v11_transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "correctness": "FAILED; NOT QUALIFIED",
        "performance": "NOT MEASURED",
        "qualified": False,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
    })
    latest = copy.deepcopy(old["latest_original_campaigns"])
    latest["c"] = copy.deepcopy(facts)
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 98,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v97_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v97_snapshot_canonical_sha256": V97_SNAPSHOT_SHA256,
        "previous_v97_snapshot_canonical_bytes": V97_SNAPSHOT_BYTES,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        "preserved_v97_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": latest,
        C_LATEST_KEY: copy.deepcopy(reference),
        POOL_KEY: pool,
        **copy.deepcopy(delta),
    })
    for key, size, expected, count in previous_pools(previous, chain):
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == expected
            and raw == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "preserve every complete immutable V97 history pool: " + key,
        )
    validate_evidence_pool(base, summary[POOL_KEY], contract, receipt, facts)
    base.need(
        base.canonical(summary["previous_v97_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v96_snapshot"])
        == base.canonical(old["previous_v96_snapshot"])
        and base.canonical(summary["previous_v95_snapshot"])
        == base.canonical(old["previous_v95_snapshot"])
        and base.canonical(summary["previous_v94_snapshot"])
        == base.canonical(old["previous_v94_snapshot"])
        and base.canonical(summary["preserved_v97_latest_original_campaigns"])
        == base.canonical(old["latest_original_campaigns"])
        and summary["rust_v22_original_campaign_verified_passing_case_count"] == 14725
        and summary["zig_v13_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v13_original_campaign_cleanup_warning_worker_count"] == 13
        and summary["c_v10_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v10_original_campaign_observed_mismatch_lower_bound"] == 606
        and summary["c_v10_original_campaign_individual_mismatch_vector_count"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_complete_individual_mismatch_vectors"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_candidate_execution_failure_count"] == 5
        and summary["c_v10_original_campaign_completed_suite_count"] == 8
        and summary["v96_visible_footer_status"]
        == "REJECTED; OVERBROAD COMPLETENESS CLAIM"
        and summary["historical_c10_records_independently_established_by_graph"]
        is False
        and summary["historical_c10_records_repaired"] is False
        and summary["c_v11_original_campaign_verified_passing_case_count"] == 16262
        and summary["c_v11_original_campaign_complete_observed_individual_mismatch_record_count"]
        == 606
        and summary["c_v11_original_campaign_complete_observed_mismatch_chunk_count"]
        == 21
        and summary["c_v11_original_campaign_source_canonical_completed_suite_vector_count"]
        == 10
        and summary["c_v11_original_campaign_transport_only_completed_suite_vector_count"]
        == 1
        and summary["c_v11_original_campaign_transport_only_completed_suite_name"]
        == "public_surface_v19"
        and summary["c_v11_original_campaign_transport_only_observed_individual_mismatch_record_count"]
        == 114
        and summary["c_v11_original_campaign_transport_only_original_source_vector_sha256"]
        == "NOT PROVIDED BY THE ORIGINAL OBSERVER"
        and summary["c_v11_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False
        and summary["winner_selected"] is False,
        "retain exact V97 history while reporting only the real new C11 improvement",
    )
    resolved = resolve_reference(base, summary[POOL_KEY], summary[C_LATEST_KEY])
    base.need(
        base.canonical(resolved["validated_campaign_outcome"])
        == base.canonical(summary["latest_original_campaigns"]["c"]),
        "bind the latest original C campaign to its complete durable public evidence",
    )
    validate_machine_language(base, summary["headline"], summary["snapshot"])
    assets = {
        INPUT_PATH: inputs_raw,
        SUMMARY_PATH: base.canonical(summary),
        SVG_PATH: svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized complete V98 graph evidence: " + path,
        )
    return snapshot, assets


def result_payload(
    base: types.ModuleType,
    options: argparse.Namespace,
    assets: dict[str, bytes],
    outputs_written: bool,
    additional: dict | None = None,
) -> dict:
    result = {
        "schema": SCHEMA + (
            "-published" if outputs_written else "-source-only-frozen-context"
        ),
        "version": 98,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "actual_current_graph_predecessor_version": 97,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v98_new_directly_authenticated_evidence_owner_count": 4,
        "lossless_previous_v97_proof_pool_count": 18,
        "lossless_v97_all_eighteen_previous_pool_identity_status": "PASS",
        "lossless_v97_snapshot_identity_status": "PASS",
        "lossless_v97_family_identity_status": "PASS",
        "lossless_v98_complete_c11_public_receipt_count": 1,
        "lossless_v98_complete_c11_source_owner_count": 3,
        "v96_visible_footer_status": "REJECTED; OVERBROAD COMPLETENESS CLAIM",
        "v96_rejected_svg_sha256":
        "ec8ffd566b7da826441383c1fd44944189c153ffde252b9c8340e3e041770dcd",
        "v96_rejected_svg_bytes": 9633,
        "public_reporting_integrity": VISIBLE_POLICY,
        "individual_failing_examples_fully_recorded": False,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v22_original_campaign_observed_mismatch_lower_bound": 2018,
        "rust_v22_original_campaign_complete_failure_worker_warning_count": 16,
        "c_v10_original_campaign_verified_passing_case_count": 13606,
        "c_v10_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v10_original_campaign_individual_mismatch_vector_count": "NOT MEASURED",
        "c_v10_original_campaign_complete_individual_mismatch_vectors":
        "NOT MEASURED",
        "c_v10_original_campaign_candidate_execution_failure_count": 5,
        "c_v10_original_campaign_completed_suite_count": 8,
        "historical_c10_audit_recorded_counterexample_count": 92,
        "historical_c10_audit_unrecorded_counterexample_count": 514,
        "historical_c10_audit_evidence_status": HISTORICAL_C10_RECORD_STATUS,
        "historical_c10_records_independently_established_by_graph": False,
        "historical_c10_records_repaired": False,
        "c_v11_actual_publication_receipt_sha256": C11_RECEIPT[1],
        "c_v11_original_campaign_actual_worker_count": 13,
        "c_v11_original_campaign_distinct_worker_count": 13,
        "c_v11_original_campaign_clean_suite_count": 6,
        "c_v11_original_campaign_mismatch_suite_count": 5,
        "c_v11_original_campaign_completed_suite_count": 11,
        "c_v11_original_campaign_candidate_execution_failure_count": 2,
        "c_v11_original_campaign_infrastructure_failure_count": 0,
        "c_v11_original_campaign_worker_timeout_count": 0,
        "c_v11_original_campaign_verified_passing_case_count": 16262,
        "c_v11_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v11_original_campaign_complete_observed_individual_mismatch_record_count":
        606,
        "c_v11_original_campaign_complete_observed_mismatch_chunk_count": 21,
        "c_v11_original_campaign_complete_observed_mismatch_vector_count": 11,
        "c_v11_original_campaign_source_canonical_completed_suite_vector_count": 10,
        "c_v11_original_campaign_transport_only_completed_suite_vector_count": 1,
        "c_v11_original_campaign_transport_only_completed_suite_name":
        "public_surface_v19",
        "c_v11_original_campaign_transport_only_observed_individual_mismatch_record_count":
        114,
        "c_v11_original_campaign_transport_only_observed_mismatch_chunk_count": 4,
        "c_v11_original_campaign_transport_only_original_source_vector_sha256":
        "NOT PROVIDED BY THE ORIGINAL OBSERVER",
        "c_v11_all_observed_individual_mismatch_records_preserved": True,
        "c_v11_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v11_original_campaign_candidate_status": "FAIL",
        "c_v11_original_campaign_candidate_qualified": False,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v14_controller_failure_candidate_worker_count": "NOT MEASURED",
        "zig_v14_controller_failure_corrected_warning_count": "NOT MEASURED",
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": outputs_written,
    }
    if additional:
        result.update(additional)
    return result


def forge_removed_visible_phrase(
    base: types.ModuleType,
    original: bytes,
    phrase: str,
) -> bytes:
    folded = original.lower()
    needle = phrase.encode("ascii").lower()
    base.need(needle in folded, "exercise a genuine visible V98 disclosure: " + phrase)
    pieces: list[bytes] = []
    start = 0
    while True:
        position = folded.find(needle, start)
        if position < 0:
            pieces.append(original[start:])
            break
        pieces.extend((original[start:position], b"REMOVED"))
        start = position + len(needle)
    return b"".join(pieces)


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    _, assets = build(previous, chain, base, options)
    old = authenticate_previous(previous, chain, base)
    document = base.document(assets[SUMMARY_PATH], "whole source-only V98 summary")
    headline = document["headline"]
    snapshot = document["snapshot"]
    contract, receipt, facts = load_new_evidence(base)
    pool = document[POOL_KEY]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            if not callable(callback):
                raise ValueError("require a callable V98 hostile control")
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V98 accepted misleading evidence: " + label)

    for phrase in FORBIDDEN_VISIBLE_PHRASES:
        forged = assets[SVG_PATH].replace(
            VISIBLE_FOOTER.encode("utf-8"), phrase.encode("utf-8")
        )
        reject(
            "false universal historical preservation: " + phrase,
            lambda raw=forged: validate_visible_language(base, raw),
        )
        forged_headline = dict(headline)
        forged_snapshot = dict(snapshot)
        forged_headline["public_reporting_integrity"] = phrase
        forged_snapshot["public_reporting_integrity"] = phrase
        reject(
            "false machine-readable historical preservation: " + phrase,
            lambda head=forged_headline, snap=forged_snapshot:
            validate_machine_language(base, head, snap),
        )
    for phrase in (
        "31,237 / 31,237 (100%)",
        "16,262 / 31,237 (52.1%)",
        "14,725 / 31,237 (47.1%)",
        "4,607 / 31,237 (14.7%)",
        "606 current C11 examples",
        "21 recorded chunks",
        "11 completed groups",
        "10 source-canonical",
        "1 transport-only",
        "114 records",
        "source digest not provided by the original observer",
        "two incomplete original groups",
        "zero infrastructure failures",
        "zero timeouts",
        "earlier C10 audit reported 92 recorded",
        "514 not recorded",
        "not independently established by this graph",
        "historical losses not repaired",
        "NOT MEASURED",
        "NOT FROZEN",
        "NOT GENERATED",
        "NOT OPENED",
        "no winner",
    ):
        forged = forge_removed_visible_phrase(base, assets[SVG_PATH], phrase)
        reject(
            "removed genuine visible disclosure: " + phrase,
            lambda raw=forged: validate_visible_language(base, raw),
        )
    for key, wrong in (
        ("public_reporting_integrity", "ALL HISTORICAL LOSSES PRESERVED"),
        ("original_python_check_count", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("verified_original_checks_by_candidate", {"c": 31237}),
        ("c_current_verified_original_checks", 31237),
        ("c_current_complete_observed_individual_mismatch_records", 92),
        ("c_current_complete_observed_mismatch_chunks", 1),
        ("c_current_source_canonical_completed_suite_vector_count", 11),
        ("c_current_transport_only_completed_suite_vector_count", 0),
        ("c_current_transport_only_completed_suite_name", "managed_v1"),
        ("c_current_transport_only_observed_individual_mismatch_record_count", 0),
        ("c_current_transport_only_original_source_vector_sha256", "0" * 64),
        ("c_current_completed_original_suite_count", 13),
        ("c_current_candidate_worker_count", 11),
        ("c_incomplete_candidate_worker_count", 0),
        ("c_infrastructure_failure_count", 2),
        ("c_worker_timeout_count", 2),
        ("c_complete_mismatch_total", 606),
        ("c_current_observed_individual_records_preserved", False),
        ("historical_c10_audit_evidence_status", "INDEPENDENTLY PROVEN BY GRAPH"),
        ("historical_c10_records_independently_established_by_graph", True),
        ("historical_c10_records_repaired", True),
        ("historical_c10_audit_recorded_counterexample_count", 606),
        ("historical_c10_audit_unrecorded_counterexample_count", 0),
        ("bars_measure", "SPEED"),
        ("speed_relative_to_python", "1.5x"),
        ("performance", "FASTER"),
        ("memory", "FASTER"),
        ("fully_compatible_candidate_count", 1),
        ("winner_selected", True),
    ):
        forged = dict(headline)
        forged[key] = wrong
        reject(
            "fabricated current or historical public headline " + key,
            lambda head=forged: validate_machine_language(base, head, snapshot),
        )
    for key, wrong in (
        ("public_reporting_integrity", "ALL HISTORICAL LOSSES PRESERVED"),
        ("c_v11_original_campaign_verified_passing_case_count", 31237),
        ("c_v11_original_campaign_complete_observed_individual_mismatch_record_count", 92),
        ("c_v11_original_campaign_complete_observed_mismatch_chunk_count", 1),
        ("c_v11_original_campaign_source_canonical_completed_suite_vector_count", 11),
        ("c_v11_original_campaign_transport_only_completed_suite_vector_count", 0),
        ("c_v11_original_campaign_transport_only_completed_suite_name", "managed_v1"),
        ("c_v11_original_campaign_transport_only_observed_individual_mismatch_record_count", 0),
        ("c_v11_original_campaign_transport_only_original_source_vector_sha256", "0" * 64),
        ("c_v11_original_campaign_semantic_mismatch_count", 606),
        ("historical_c10_audit_evidence_status", "INDEPENDENTLY PROVEN BY GRAPH"),
        ("historical_c10_records_independently_established_by_graph", True),
        ("historical_c10_records_repaired", True),
        ("qualified_candidate_count", 1),
        ("performance", "FASTER"),
        ("winner_selected", True),
    ):
        forged = dict(snapshot)
        forged[key] = wrong
        reject(
            "fabricated current or historical public snapshot " + key,
            lambda snap=forged: validate_machine_language(base, headline, snap),
        )
    for key in sorted(C11_RECEIPT_KEYS):
        forged = dict(receipt)
        forged.pop(key)
        reject(
            "omitted exact genuine C11 receipt field " + key,
            lambda value=forged: validate_c_receipt(base, value, contract),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("version", 10),
        ("status", "FAIL"),
        ("publication_status", "FAIL"),
        ("publication_pass_means", "CANDIDATE CORRECTNESS"),
        ("family", "zig"),
        ("source_sha256", "0" * 64),
        ("protocol_sha256", "0" * 64),
        ("contract_sha256", "0" * 64),
        ("preserved_actual_v10_failure_receipt_sha256", "0" * 64),
        ("case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("suite_count", 11),
        ("attempted_suite_count", 11),
        ("actual_candidate_workers", 11),
        ("actual_worker_process_ids", list(EXPECTED_WORKER_IDS[:-1])),
        ("actual_worker_process_ids_are_distinct", False),
        ("verified_passing_case_count", 31237),
        ("completed_suite_count", 13),
        ("candidate_execution_failure_count", 0),
        ("infrastructure_failure_count", 2),
        ("worker_timeout_count", 2),
        ("observed_semantic_mismatch_lower_bound", 92),
        ("complete_observed_semantic_mismatch_record_count", 92),
        ("complete_mismatch_chunk_count", 1),
        ("complete_mismatch_suite_count", 13),
        ("all_observed_semantic_mismatch_records_preserved", False),
        ("semantic_mismatch_count", 606),
        ("counterexample_preview_only", True),
        ("counterexample_normalization_before_original_comparison", True),
        ("candidate_status", "PASS"),
        ("candidate_qualified", True),
        ("named_private_waiver_count", 0),
        ("separate_reference_case_count", 0),
        ("separate_reference_cases_counted_as_candidate_cases", True),
        ("expanded_holdout_proposed_case_count", 0),
        ("holdout", "OPENED"),
        ("hidden_cases_read", 1),
        ("benchmark_files_read", 1),
        ("clock_samples", 1),
        ("timing_trials_run", 1),
        ("performance", "FASTER"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("winner_selected", True),
        ("original_source_targets_modified", 1),
        ("original_native_inode_restored", False),
        ("transient_physical_interpreter_creations", 0),
        ("successfully_returned_guarded_interpreter_creations", 0),
        ("zero_returned_creations_proves_zero_physical_creations", True),
    ):
        forged = dict(receipt)
        forged[key] = wrong
        reject(
            "invented exact actual C11 receipt field " + key,
            lambda value=forged: validate_c_receipt(base, value, contract),
        )
    for index, (suite, _) in enumerate(SUITES):
        for key in sorted(C11_ROW_KEYS):
            forged = dict(receipt)
            rows = list(receipt["suite_outcomes"])
            row = dict(rows[index])
            row.pop(key)
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "omitted actual original C11 worker " + suite + ":" + key,
                lambda value=forged: validate_c_receipt(base, value, contract),
            )
        for key, wrong in (
            ("suite", "invented"),
            ("case_execution_denominator", 0),
            ("actual_candidate_workers", 0),
            ("worker_process_id", 0),
            ("status", "invented"),
            ("failure_class", "invented"),
            ("mismatch_count", -1),
        ):
            forged = dict(receipt)
            rows = list(receipt["suite_outcomes"])
            row = dict(rows[index])
            row[key] = wrong
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "changed actual original C11 worker " + suite + ":" + key,
                lambda value=forged: validate_c_receipt(base, value, contract),
            )
    for index, vector in enumerate(receipt["complete_mismatch_suite_vector_fingerprints"]):
        suite = vector["suite"]
        for key in sorted(C11_VECTOR_KEYS):
            forged = dict(receipt)
            vectors = list(receipt["complete_mismatch_suite_vector_fingerprints"])
            forged_vector = dict(vectors[index])
            forged_vector.pop(key)
            vectors[index] = forged_vector
            forged["complete_mismatch_suite_vector_fingerprints"] = vectors
            reject(
                "omitted complete observed C11 vector " + suite + ":" + key,
                lambda value=forged: validate_c_receipt(base, value, contract),
            )
        for key, wrong in (
            ("suite", "invented"),
            ("case_execution_denominator", 0),
            ("all_observed_records_preserved", False),
            ("complete_chunk_count", -1),
            ("complete_record_count", -1),
            ("complete_vector_sha256", "0" * 64),
        ):
            forged = dict(receipt)
            vectors = list(receipt["complete_mismatch_suite_vector_fingerprints"])
            forged_vector = dict(vectors[index])
            forged_vector[key] = wrong
            vectors[index] = forged_vector
            forged["complete_mismatch_suite_vector_fingerprints"] = vectors
            reject(
                "changed complete observed C11 vector " + suite + ":" + key,
                lambda value=forged: validate_c_receipt(base, value, contract),
            )
    for key in sorted(C11_ARCHIVE_KEYS):
        forged = dict(receipt)
        archive = dict(receipt["archive"])
        archive.pop(key)
        forged["archive"] = archive
        reject(
            "omitted receipt-only C11 archive metadata " + key,
            lambda value=forged: validate_c_receipt(base, value, contract),
        )
    for key, wrong in (
        ("schema", "invented"),
        ("version", 10),
        ("family", "rust"),
        ("status", "PASS"),
        ("candidate_correctness", "PASS"),
        ("candidate_qualification", "QUALIFIED"),
        ("qualified_candidate_count", 1),
        ("runtime_non_delegation", "PASS"),
        ("performance", "FASTER"),
        ("memory", "FASTER"),
        ("undefined_behavior", "PASS"),
        ("holdout", "OPENED"),
        ("winner_selected", True),
    ):
        forged = dict(contract)
        forged[key] = wrong
        reject(
            "fabricated complete C11 source contract " + key,
            lambda value=forged: validate_c_contract(base, value),
        )
    for key, wrong in (
        ("all_original_candidate_cases_required", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("all_original_suite_workers_required", 11),
        ("distinct_worker_process_count_required", 11),
        ("all_observed_mismatch_records_preserved", False),
        ("exact_semantic_mismatch_total_requires_all_13_complete_suites", False),
        ("cross_candidate_engine", "ALLOWED"),
        ("external_regex_package", "ALLOWED"),
        ("fallback", "ALLOWED"),
        ("standard_library_engine", "ALLOWED"),
        ("source_mode_archive_physically_denied", False),
        ("source_mode_candidate_paths_physically_denied", False),
        ("source_mode_holdout_physically_denied", False),
        ("source_mode_native_physically_denied", False),
        ("previous_actual_v10_receipt_sha256", "0" * 64),
        ("previous_actual_v10_verified_passing_case_count", 16262),
        ("previous_actual_v10_semantic_mismatch_lower_bound", 0),
        ("previous_actual_v10_completed_original_suites", 13),
        ("previous_actual_v10_original_candidate_execution_failures", 0),
        ("previous_actual_v10_archived_recorded_counterexamples", 606),
        ("previous_actual_v10_archived_missing_counterexamples", 0),
        ("previous_actual_v10_exact_total_semantic_mismatches", 606),
        ("previous_actual_v10_missing_counterexample_status", "RECOVERED"),
    ):
        forged = dict(contract)
        policy = dict(contract["actual_operation_policy"])
        policy[key] = wrong
        forged["actual_operation_policy"] = policy
        reject(
            "fabricated prior-audit C11 preservation policy " + key,
            lambda value=forged: validate_c_contract(base, value),
        )
    for key, size, expected, count in previous_pools(previous, chain):
        forged = dict(old)
        forged.pop(key)
        reject(
            "omitted complete V97 historical proof pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
        forged = dict(old)
        previous_pool = dict(old[key])
        previous_pool["entries"] = {}
        forged[key] = previous_pool
        reject(
            "discarded complete V97 historical proof pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for key, wrong in (
        ("version", 96),
        ("authenticated_evidence_owner_lower_bound", 343),
        ("authenticated_history_reference_lower_bound", 348),
        ("lossless_previous_v96_proof_pool_count", 17),
        ("v96_visible_footer_status", "PASS"),
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("c_v10_original_campaign_verified_passing_case_count", 16262),
        ("c_v10_original_campaign_individual_mismatch_vector_count", 92),
        ("c_v10_original_campaign_complete_individual_mismatch_vectors", True),
        ("c_v10_original_campaign_semantic_mismatch_count", 606),
        ("c_v10_original_campaign_candidate_execution_failure_count", 0),
        ("c_v10_original_campaign_completed_suite_count", 13),
        ("rust_v22_original_campaign_verified_passing_case_count", 16262),
        ("zig_v13_original_campaign_verified_passing_case_count", 16262),
        ("zig_v14_controller_failure_candidate_worker_count", 13),
        ("qualified_candidate_count", 1),
        ("runtime_no_delegation", "PASS"),
        ("performance", "FASTER"),
        ("memory", "FASTER"),
        ("expanded_holdout_case_status", "OPENED"),
        ("winner_selected", True),
    ):
        forged = dict(old)
        forged[key] = wrong
        reject(
            "fabricated immutable published V97 predecessor " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    forged_pool = dict(pool)
    forged_pool["entries"] = {}
    reject(
        "discarded actual complete C11 proof",
        lambda value=forged_pool: validate_evidence_pool(
            base, value, contract, receipt, facts
        ),
    )
    for key in (
        "complete_source_contract",
        "complete_plaintext_receipt",
        "validated_campaign_outcome",
        "source_canonical_completed_suite_vector_count",
        "transport_only_completed_suite_vector_count",
        "transport_only_completed_suite_name",
        "transport_only_observed_individual_mismatch_record_count",
        "transport_only_original_source_vector_sha256",
        "historical_c10_audit_evidence_status",
        "historical_c10_records_independently_established_by_graph",
        "historical_c10_records_repaired",
    ):
        forged_pool = copy.deepcopy(pool)
        forged_pool["entries"][C11_RECEIPT[1]].pop(key)
        reject(
            "omitted complete C11 proof field " + key,
            lambda value=forged_pool: validate_evidence_pool(
                base, value, contract, receipt, facts
            ),
        )
    reference = document[C_LATEST_KEY]
    for key, wrong in (
        ("schema", "invented"),
        ("family", "zig"),
        ("complete_first_party_source_owner_count", 2),
        ("complete_plaintext_receipt_sha256", "0" * 64),
        ("complete_plaintext_receipt_bytes", 1),
        ("complete_reference_sha256", "0" * 64),
        ("complete_reference_canonical_bytes", 1),
    ):
        forged = dict(reference)
        forged[key] = wrong
        reject(
            "substituted complete C11 proof reference " + key,
            lambda value=forged: resolve_reference(base, pool, value),
        )
    for event, arguments in (
        ("subprocess.Popen", ("candidate",)),
        ("os.posix_spawn", ("candidate",)),
        ("os.fork", ()),
        ("ctypes.dlopen", ("candidate.so",)),
        ("socket.connect", ("holdout",)),
        ("os.remove", (str(ROOT / "GOAL.md"),)),
        ("os.rename", (str(ROOT / "GOAL.md"), str(ROOT / "invented"))),
        ("os.mkdir", (str(ROOT / "private"),)),
        ("import", ("re", None, None, None, None)),
        ("import", ("_sre", None, None, None, None)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("candidates.vm_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
        ("open", (str(ROOT / INPUT_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / "performance/holdout.json"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "private.json.gz"), None, os.O_RDONLY)),
        ("open", (str(ROOT / C11_RECEIPT[0].replace("-publication-receipt.json", ".json.gz")), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/_c_probe.so"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/vm_candidate.py"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "invented-file"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("open", ("/tmp/private-root", None, os.O_RDONLY)),
        ("open", (1, "wb", os.O_WRONLY)),
    ):
        reject(
            "forbidden source-only effect " + event,
            lambda name=event, values=arguments: audit_wall(name, values),
        )
    for label, callback in (
        ("direct stdout descriptor", lambda: os.write(1, b"forged")),
        ("direct stderr descriptor", lambda: os.write(2, b"forged")),
        ("direct output FileIO", lambda: _io.FileIO(str(ROOT / INPUT_PATH), "wb")),
        ("direct SVG FileIO", lambda: io.FileIO(str(ROOT / SVG_PATH), "wb")),
        ("inherited stdout FileIO", lambda: _io.FileIO(1, "w", closefd=False)),
        ("inherited stderr FileIO", lambda: io.FileIO(2, "w", closefd=False)),
    ):
        reject(label, callback)
    if ORIGINAL_OS_WRITEV is not None:
        reject("direct stdout writev", lambda: os.writev(1, [b"forged"]))
    base.need(
        rejected >= 550,
        "require comprehensive genuinely executed candidate-free C11 hostile controls",
    )
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "historical_v97_recorded_rejected_hostile_control_count": 14757,
        "historical_v97_hostile_controls_reexecuted_by_graph": False,
        "historical_v97_hostile_controls_rerun_status":
        "NOT RERUN; CANDIDATE SOURCE ACCESS PHYSICALLY DENIED",
        "inherited_rejected_hostile_control_count": 0,
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": rejected,
    })


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only a bounded exclusively created V98 public evidence owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "write complete V98 evidence")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate every exclusively created V98 graph byte",
        )
    finally:
        os.close(handle)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "reauthenticate every exclusively created V98 byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V97:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in C11_SOURCE:
        parser.add_argument("--c-" + role + "-sha256", required=True)
    for role in HISTORICAL_C10:
        parser.add_argument("--historical-c-" + role + "-sha256", required=True)
    for role in HISTORICAL_ZIG14:
        parser.add_argument("--historical-zig-" + role + "-sha256", required=True)
    parser.add_argument("--c-receipt-sha256", required=True)
    parser.add_argument("--historical-c-receipt-sha256", required=True)
    parser.add_argument("--historical-zig-controller-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        if not options.render:
            install_source_wall()
        previous, chain, base = load_previous()
        if options.self_test:
            result = self_test(previous, chain, base, options)
        else:
            _, assets = build(previous, chain, base, options)
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = result_payload(base, options, assets, bool(options.render))
            if options.render_preview:
                result["schema"] = SCHEMA + "-source-only-render-preview"
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V98 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
