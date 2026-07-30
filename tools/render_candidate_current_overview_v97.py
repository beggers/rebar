#!/usr/bin/env python3
"""Report recorded Python re compatibility without claiming missing examples."""

from __future__ import annotations

import _io
import argparse
import copy
import hashlib
import io
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v97.py"
OUTPUT = "docs/evidence/candidate-current-overview-v97"
INPUT_PATH = OUTPUT + ".inputs.json"
SUMMARY_PATH = OUTPUT + ".summary.json"
SVG_PATH = OUTPUT + ".svg"
SCHEMA = "rebar-candidate-current-overview-v97"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
OWNER_LIMIT = 4 * 1024 * 1024
CASE_COUNT = 31237
SUPPLEMENTAL_CASE_COUNT = 8244
HOLDOUT_PROPOSAL_COUNT = 14155776
HISTORICAL_HOLDOUT_PROPOSAL_COUNT = 4194304
EVIDENCE_FLOOR = 344
HISTORY_FLOOR = 349

V96 = {
    "source": (
        "tools/render_candidate_current_overview_v96.py",
        "9bb191556152393b650b75c0c4e3d584b6df9f3d060571789c1a89411011fd51",
        115087,
        429954,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v96.inputs.json",
        "71cc5d77f66901d24c3d8c8db58f2cdc545634ec5da8ff0aaf9f630f3bafde7f",
        28556,
        431191,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v96.summary.json",
        "b5f7b35e9ec47e4d0793c0b5b38372c391ec1f3aaca37b80655802aa9c2f1ca2",
        4025741,
        431231,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v96.svg",
        "ec8ffd566b7da826441383c1fd44944189c153ffde252b9c8340e3e041770dcd",
        9633,
        431232,
    ),
}

C_SOURCE = {
    "source": (
        "tools/run_owned_repaired_c_original_campaign_v10.py",
        "ad8b8451847b3e5c566c141e829bdf6eecea8ae9f502b608288449022c83c790",
        50278,
        430925,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V10.md",
        "ba673181c02daf3a572e3569283a5a4c490ed04e7cd76927e3f2fe1430630179",
        5941,
        525204,
    ),
    "contract": (
        "oracle/phase2/repaired-c-original-campaign-v10.json",
        "2aad4885fe80b93f61f59c28ed6969fbcf16dda0b8a3457c71b449a9972bb595",
        44516,
        525205,
    ),
}

C_RECEIPT = (
    "oracle/phase2/evidence/"
    "repaired-c-original-campaign-v10-c-phase2-v21-c-original-match-"
    "semantics-original-p0-v10-failures-publication-receipt.json",
    "c5c85f828da7e960c90a23b1eb4d74c30a671d030de04ef61b0e4d00d7e5433a",
    7247,
    525475,
)

ZIG14_SOURCE = {
    "source": (
        "tools/run_owned_repaired_zig_original_campaign_v14.py",
        "8757ff2fdda5e8e60ee694b0d803018ddf33ea7266b8d7a5eff6d52d0866569d",
        49601,
        431103,
    ),
    "protocol": (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V14.md",
        "691ab654b88ed30f6cd0729d987415162708fdfb90c36d91bf41dcefdbb5fcef",
        7539,
        525386,
    ),
    "contract": (
        "oracle/phase2/repaired-zig-original-campaign-v14.json",
        "1c7326dc2f63635f3e32ec0558b51f21c952d51480f336e3b0d4d49e38428a0a",
        31103,
        525387,
    ),
}

ZIG14_RECEIPT = (
    "oracle/phase2/evidence/"
    "zig-original-campaign-v14-setter-safe-prepublication-controller-failure.json",
    "2d1bad717e782b7ed3e0af856f8687e9a29abc93ebf1553adc6d65f668aa5c65",
    5474,
    525461,
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

V96_PUBLIC_POOL = (
    "lossless_v96_c_v10_and_zig_v14_public_evidence_pool",
    108611,
    "f691bd6fc89e4a7da2fa5e01ea712f160d70ba6bce68f86b75160a1f26045c76",
    2,
)
V96_SNAPSHOT_SHA256 = (
    "20de694f14e65bc2a11ea349da97176daf255593e6d6608f5b9cf89bf151c730"
)
V96_SNAPSHOT_BYTES = 18491

VISIBLE_FOOTER = (
    "recorded suite outcomes preserved; individual failing examples not fully "
    "recorded; no speed claims; no winner"
)
VISIBLE_POLICY = (
    "PUBLISHED SUITE OUTCOMES PRESERVED; INDIVIDUAL FAILING EXAMPLES "
    "ARE NOT ALL RECORDED"
)
FORBIDDEN_VISIBLE_PHRASES = (
    "all " + "observed losses preserved",
    "all " + "observed failures preserved",
    "all " + "observed differences preserved",
    "all " + "individual failures preserved",
    "all " + "individual failing examples preserved",
    "all " + "individual counterexamples preserved",
    "all " + "counterexamples preserved",
    "all " + "failing vectors preserved",
    "every " + "observed failure preserved",
    "every " + "individual mismatch preserved",
    "complete " + "individual mismatch records",
)

FORBIDDEN_EVENTS = frozenset({
    "subprocess.Popen",
    "os.system",
    "os.posix_spawn",
    "os.posix_spawnp",
    "os.fork",
    "os.forkpty",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "socket.__new__",
    "socket.connect",
    "socket.bind",
    "socket.sendto",
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.mkdir",
})
FORBIDDEN_IMPORTS = frozenset({
    "regex",
    "re",
    "_sre",
    "ctypes",
    "subprocess",
    "multiprocessing",
    "socket",
    "time",
    "gzip",
    "bz2",
    "lzma",
    "tarfile",
    "zipfile",
    "candidates",
    "rebar",
})
ORIGINAL_OS_WRITE = os.write
ORIGINAL_OS_WRITEV = getattr(os, "writev", None)
ORIGINAL_FILEIO = _io.FileIO


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject an unbounded V97 public plaintext owner: " + label)
    if (
        not isinstance(relative, str)
        or relative.startswith("/")
        or ".." in relative.split("/")
        or relative.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
    ):
        raise ValueError("reject a private, native, or compressed V97 owner")
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
            raise ValueError("reject a substituted complete V97 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject a truncated complete V97 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject an extended complete V97 owner: " + label)
        raw = b"".join(chunks)
        after = os.fstat(handle)
        if hashlib.sha256(raw).hexdigest() != expected or (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_nlink,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_nlink,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError("reject a changed complete V97 owner: " + label)
        return raw
    finally:
        os.close(handle)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V97 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V97 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V97 rejected an unauthenticated file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V97 rejected inherited descriptors and unknown owners")
    if mode not in (None, "r", "rb"):
        raise ValueError("V97 source-only operation cannot open writable files")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V97 source-only operation cannot create or change files")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V97 rejected a private root or unopened holdout")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V97 rejected an escaped relative evidence owner")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so", ".dylib"))
        or "candidate-current-overview-v97." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
        or "/holdout/" in normalized
    ):
        raise ValueError("V97 rejected graph output, archive, native, or holdout")


def reject_descriptor_write(*arguments: object, **keywords: object) -> int:
    raise ValueError("V97 source-only operation rejected direct descriptor writing")


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
        raise ValueError("V97 source-only operation rejected direct _io writing")
    return ORIGINAL_FILEIO(file, mode, closefd)


def install_source_wall() -> None:
    sys.addaudithook(audit_wall)
    os.write = reject_descriptor_write
    if ORIGINAL_OS_WRITEV is not None:
        os.writev = reject_descriptor_write
    _io.FileIO = guarded_fileio
    io.FileIO = guarded_fileio


def load_previous() -> tuple[types.ModuleType, tuple, types.ModuleType]:
    raw = read_fixed(V96["source"], "whole immutable published V96 renderer")
    previous = types.ModuleType("_rebar_exact_published_source_graph_v96")
    previous.__file__ = str(ROOT / V96["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    chain = previous.load_previous()
    base = chain[-1]
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v96"
        and previous.SELF == V96["source"][0]
        and tuple(previous.SUITES) == SUITES
        and len(SUITES) == 13
        and sum(count for _, count in SUITES) == CASE_COUNT
        and len(chain) == 3,
        "require official isolated Python, complete V96 history, and original cases",
    )
    return previous, chain, base


def previous_options(previous: types.ModuleType) -> argparse.Namespace:
    pins: dict[str, object] = {
        "source_sha256": V96["source"][1],
        "source_bytes": V96["source"][2],
        "c_receipt_sha256": previous.C_RECEIPT[1],
        "zig_controller_receipt_sha256": previous.ZIG14_RECEIPT[1],
    }
    for role, item in previous.V95.items():
        pins["previous_" + role + "_sha256"] = item[1]
    for role, item in previous.C_SOURCE.items():
        pins["c_" + role + "_sha256"] = item[1]
    for role, item in previous.ZIG14_SOURCE.items():
        pins["zig_" + role + "_sha256"] = item[1]
    return argparse.Namespace(**pins)


def previous_pools(previous: types.ModuleType, chain: tuple) -> tuple:
    pools = tuple(previous.previous_pools(chain[0], chain[1])) + (V96_PUBLIC_POOL,)
    if len(pools) != 18 or len({item[0] for item in pools}) != 18:
        raise ValueError("require all eighteen exact complete V96 evidence pools")
    return pools


def validate_visible_language(base: types.ModuleType, raw: object) -> bytes:
    base.need(
        type(raw) is bytes and 0 < len(raw) <= OWNER_LIMIT,
        "reject absent or unbounded public V97 visible language",
    )
    assert isinstance(raw, bytes)
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ValueError("reject non-UTF-8 V97 accessible public language") from error
    normalized = " ".join(text.casefold().split())
    base.need(
        text.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        and '<title id="title">' in text
        and '<desc id="description">' in text
        and VISIBLE_FOOTER in text
        and "individual failing examples are not all recorded" in normalized
        and "published suite outcomes" in normalized
        and "606" in normalized
        and "observed lower bound" in normalized
        and "13,606 / 31,237 (43.6%)" in text
        and "not measured" in normalized
        and "not frozen" in normalized
        and "not generated" in normalized
        and "not opened" in normalized
        and "no winner" in normalized,
        "require plain, complete, honest, and accessible V97 graph disclosures",
    )
    for phrase in FORBIDDEN_VISIBLE_PHRASES:
        base.need(
            phrase not in normalized,
            "reject a misleading unrecorded-counterexample completeness claim",
        )
    return raw


def validate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    value: object,
) -> dict:
    base.need(
        type(value) is dict
        and value.get("schema") == "rebar-candidate-current-overview-v96-summary"
        and value.get("version") == 96
        and value.get("status") == "PASS"
        and value.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
        and value.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
        and value.get("original_case_execution_denominator") == CASE_COUNT
        and value.get("original_suite_count") == 13
        and value.get("named_private_waiver_count") == 13
        and value.get("separate_additional_reference_case_count")
        == SUPPLEMENTAL_CASE_COUNT
        and value.get("additional_cases_included_in_original_denominator") is False
        and value.get("qualified_candidate_count") == 0
        and value.get("runtime_no_delegation") == "NOT ESTABLISHED"
        and value.get("performance") == "NOT MEASURED"
        and value.get("memory") == "NOT MEASURED"
        and value.get("undefined_behavior") == "NOT MEASURED"
        and value.get("expanded_holdout_proposed_case_count") == HOLDOUT_PROPOSAL_COUNT
        and value.get("preserved_previous_holdout_proposal_case_count")
        == HISTORICAL_HOLDOUT_PROPOSAL_COUNT
        and value.get("expanded_holdout_final_protocol_status") == "NOT FROZEN"
        and value.get("expanded_holdout_case_status") == "NOT GENERATED; NOT OPENED"
        and value.get("final_holdout_opened") is False
        and value.get("winner_selected") is False,
        "retain the exact V96 experiment, full original denominator, and sealed holdout",
    )
    assert isinstance(value, dict)
    base.need(
        value.get("rust_v22_original_campaign_verified_passing_case_count") == 14725
        and value.get("rust_v22_original_campaign_observed_mismatch_lower_bound")
        == 2018
        and value.get("rust_v22_original_campaign_complete_failure_worker_warning_count")
        == 16
        and value.get("rust_v22_original_campaign_all_worker_warning_count")
        == "NOT MEASURED"
        and value.get("c_v9_original_campaign_verified_passing_case_count") == 13606
        and value.get("c_v9_original_campaign_observed_mismatch_lower_bound") == 492
        and value.get("c_v9_original_campaign_candidate_execution_failure_count") == 6
        and value.get("c_v10_original_campaign_verified_passing_case_count") == 13606
        and value.get("c_v10_original_campaign_observed_mismatch_lower_bound") == 606
        and value.get("c_v10_original_campaign_semantic_mismatch_count")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_individual_mismatch_vector_count")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_complete_individual_mismatch_vectors")
        == "NOT MEASURED"
        and value.get("c_v10_original_campaign_candidate_execution_failure_count") == 5
        and value.get("c_v10_original_campaign_infrastructure_failure_count") == 0
        and value.get("c_v10_original_campaign_completed_suite_count") == 8
        and value.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and value.get("zig_v13_original_campaign_observed_mismatch_lower_bound") == 1700
        and value.get("zig_v13_original_campaign_cleanup_warning_worker_count") == 13
        and value.get("zig_v14_controller_failure_candidate_worker_count")
        == "NOT MEASURED"
        and value.get("zig_v14_controller_failure_corrected_warning_count")
        == "NOT MEASURED"
        and value.get("lossless_previous_v95_proof_pool_count") == 17
        and value.get("lossless_v95_all_seventeen_previous_pool_identity_status")
        == "PASS"
        and value.get("lossless_v96_complete_public_receipt_count") == 2
        and value.get("lossless_v96_complete_source_owner_count") == 6
        and value.get("lossless_v96_c_v10_complete_original_suite_count") == 13
        and value.get("lossless_v96_zig_v14_controller_matching_claimed") is False,
        "preserve every genuine C, Rust, and Zig outcome without inventing examples",
    )
    snapshot = value.get("snapshot")
    raw = base.canonical(snapshot)
    base.need(
        type(snapshot) is dict
        and snapshot.get("schema")
        == "rebar-candidate-current-overview-v96-compact-current-snapshot"
        and snapshot.get("version") == 96
        and len(raw) == V96_SNAPSHOT_BYTES
        and base.digest(raw) == V96_SNAPSHOT_SHA256,
        "preserve every exact byte of the complete V96 snapshot",
    )
    for key, size, expected, count in previous_pools(previous, chain):
        pool = value.get(key)
        whole = base.canonical(pool)
        base.need(
            type(pool) is dict
            and len(whole) == size
            and base.digest(whole) == expected
            and type(pool.get("entries")) is dict
            and len(pool["entries"]) == count,
            "preserve the entire immutable V96 historical evidence pool: " + key,
        )
    families = value.get("families")
    latest = value.get("latest_original_campaigns")
    base.need(
        type(families) is list
        and len(families) == 7
        and [row.get("family") for row in families]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and families[0].get("correctness") == "BASELINE PASS"
        and type(latest) is dict
        and set(latest) == {"rust", "c", "zig"}
        and latest["rust"].get("verified_passing_case_count") == 14725
        and latest["rust"].get("observed_semantic_mismatch_lower_bound") == 2018
        and latest["c"].get("verified_passing_case_count") == 13606
        and latest["c"].get("observed_semantic_mismatch_lower_bound") == 606
        and latest["c"].get("candidate_execution_failure_count") == 5
        and latest["c"].get("infrastructure_failure_count") == 0
        and latest["zig"].get("verified_passing_case_count") == 4607
        and latest["zig"].get("observed_semantic_mismatch_lower_bound") == 1700
        and type(value.get("headline")) is dict
        and value["headline"].get("verified_original_checks_by_candidate")
        == {
            "c": 13606,
            "cpp": "NOT MEASURED",
            "fortran": "NOT MEASURED",
            "go": "NOT MEASURED",
            "rust": 14725,
            "zig": 4607,
        },
        "retain all six engine families and the real baseline-relative results",
    )
    return value


def authenticate_previous(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> dict:
    snapshot, assets = previous.build(*chain, previous_options(previous))
    for role in ("inputs", "summary", "svg"):
        item = V96[role]
        base.need(
            assets[item[0]] == read_fixed(item, "whole published V96 " + role),
            "retain every exact byte of the rejected published V96 " + role,
        )
    old = base.document(assets[V96["summary"][0]], "whole immutable V96 summary")
    validate_previous(previous, chain, base, old)
    base.need(
        base.canonical(snapshot) == base.canonical(old["snapshot"]),
        "retain the exact independently reconstructed V96 snapshot",
    )
    return old


def validate_machine_language(
    base: types.ModuleType,
    headline: object,
    snapshot: object,
) -> None:
    base.need(
        type(headline) is dict
        and type(snapshot) is dict
        and headline.get("public_reporting_integrity") == VISIBLE_POLICY
        and headline.get("published_c_suite_outcomes_preserved") is True
        and headline.get("individual_failing_examples_fully_recorded") is False
        and headline.get("c_individual_mismatch_vector_count") == "NOT MEASURED"
        and headline.get("c_complete_individual_mismatch_vectors") == "NOT MEASURED"
        and headline.get("c_observed_mismatch_lower_bound") == 606
        and headline.get("c_complete_mismatch_total") == "NOT MEASURED"
        and headline.get("bars_measure")
        == "VERIFIED ORIGINAL CORRECTNESS CHECKS; NOT SPEED"
        and headline.get("speed_relative_to_python") == "NOT MEASURED"
        and headline.get("performance") == "NOT MEASURED"
        and headline.get("fully_compatible_candidate_count") == 0
        and headline.get("winner_selected") is False
        and snapshot.get("public_reporting_integrity") == VISIBLE_POLICY
        and snapshot.get("published_c_suite_outcomes_preserved") is True
        and snapshot.get("individual_failing_examples_fully_recorded") is False
        and snapshot.get("c_v10_original_campaign_individual_mismatch_vector_count")
        == "NOT MEASURED"
        and snapshot.get("c_v10_original_campaign_complete_individual_mismatch_vectors")
        == "NOT MEASURED",
        "reject false machine-readable individual-counterexample completeness",
    )
    assert isinstance(headline, dict)
    assert isinstance(snapshot, dict)
    for text in (
        headline["public_reporting_integrity"],
        snapshot["public_reporting_integrity"],
    ):
        normalized = " ".join(text.casefold().split())
        for phrase in FORBIDDEN_VISIBLE_PHRASES:
            base.need(
                phrase not in normalized,
                "reject an overbroad machine-readable failure preservation claim",
            )


def make_svg() -> bytes:
    rows = (
        ("Python re", CASE_COUNT, "13 of 13 original groups passed", "BASELINE", "#34d399"),
        (
            "Rust",
            14725,
            "9 passed; 3 differ; 1 incomplete; 16 warnings in the captured failed worker",
            "NOT YET COMPATIBLE",
            "#fb7185",
        ),
        (
            "C",
            13606,
            "3 passed; 5 differ; 5 incomplete; observed lower bound: 606",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        (
            "Zig",
            4607,
            "Earlier result only; 13 workers warned; corrected rerun stopped early",
            "NOT YET COMPATIBLE",
            "#fbbf24",
        ),
        ("C++", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Go", None, "Full current matching result not measured", "NOT MEASURED", "#94a3b8"),
        ("Fortran", None, "Independent builds disagreed; matching not measured", "BUILD FAILED", "#fb7185"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1540" height="1150" '
        'viewBox="0 0 1540 1150" role="img" aria-labelledby="title description">',
        '<title id="title">Recorded progress toward a faster Python re</title>',
        '<desc id="description">Bars show verified matching checks against Python, '
        'not speed. Python passes all 31,237 original checks. Rust verifies '
        '14,725; C verifies 13,606; the earlier Zig run verifies 4,607. '
        'The published suite outcomes include all 13 C group results and an '
        'observed lower bound of 606 differences, but individual failing examples '
        'are not all recorded. The number and completeness of individually '
        'recorded examples are not measured by this graph. Five C candidate '
        'workers did not complete; zero infrastructure failures were observed. '
        'The corrected Zig run failed before matching, so corrected matching, '
        'workers, and cleanup remain not measured. Rust warning counts apply '
        'only to its captured failed worker. The separate 8,244 reference checks '
        'are excluded from the original denominator. The proposed '
        '14,155,776-case speed test is not frozen, not generated, and not opened. '
        'Speed, memory, confidence, and rankings are not measured. No winner.</desc>',
        '<rect width="1540" height="1150" rx="24" fill="#0b1220"/>',
        '<text x="48" y="66" fill="#f8fafc" font-size="32" '
        'font-family="system-ui,sans-serif" font-weight="740">'
        'Building a faster Python re, from scratch</text>',
        '<text x="49" y="103" fill="#cbd5e1" font-size="17" '
        'font-family="system-ui,sans-serif">Six independently written approaches; '
        'no fully compatible replacement; no measured speed; no winner</text>',
        '<rect x="46" y="126" width="1448" height="80" rx="13" fill="#172338"/>',
        '<text x="66" y="157" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'These bars show compatibility with Python, not speed.</text>',
        '<text x="66" y="184" fill="#cbd5e1" font-size="14" '
        'font-family="system-ui,sans-serif">Every bar uses the same 31,237 '
        'original checks. Failed, incomplete, and unmeasured checks are never '
        'counted as passing.</text>',
        '<text x="50" y="246" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">APPROACH</text>',
        '<text x="159" y="246" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'ORIGINAL PYTHON CHECKS CONFIRMED</text>',
        '<text x="724" y="246" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">'
        'WHAT WAS ACTUALLY RECORDED</text>',
        '<text x="1269" y="246" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif" font-weight="690">SPEED</text>',
        '<text x="1490" y="246" text-anchor="end" fill="#94a3b8" '
        'font-size="12" font-family="system-ui,sans-serif" '
        'font-weight="690">RESULT</text>',
        '<line x1="46" y1="264" x2="1494" y2="264" stroke="#334155"/>',
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
            f'<text x="724" y="{y}" fill="#cbd5e1" font-size="11" '
            f'font-family="system-ui,sans-serif">{details}</text>'
        )
        parts.append(
            f'<text x="1269" y="{y}" fill="#94a3b8" font-size="11" '
            'font-family="system-ui,sans-serif">NOT MEASURED</text>'
        )
        parts.append(
            f'<text x="1490" y="{y}" text-anchor="end" fill="{colour}" '
            f'font-size="10" font-family="system-ui,sans-serif" '
            f'font-weight="730">{result}</text>'
        )
    parts.extend((
        '<line x1="46" y1="757" x2="1494" y2="757" stroke="#334155"/>',
        '<text x="51" y="789" fill="#f8fafc" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'What the published reports can actually prove</text>',
        '<text x="51" y="817" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The C report preserves all 13 '
        'published suite outcomes. Its observed lower bound is 606 differences; '
        'individual failing examples are not all recorded.</text>',
        '<text x="51" y="845" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">Five C candidate workers did not '
        'finish. Individual counterexample completeness: NOT MEASURED. '
        'Infrastructure failures: 0.</text>',
        '<text x="51" y="873" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">The newer Zig controller stopped '
        'before matching; its corrected matching and cleanup are NOT MEASURED. '
        'The prior Zig and Rust results are unchanged.</text>',
        '<rect x="46" y="898" width="1448" height="119" rx="13" fill="#172338"/>',
        '<text x="66" y="931" fill="#f8fafc" font-size="16" '
        'font-family="system-ui,sans-serif" font-weight="680">'
        'Future speed comparison: proposed 14,155,776 cases</text>',
        '<text x="66" y="958" fill="#cbd5e1" font-size="13" '
        'font-family="system-ui,sans-serif">NOT FROZEN; NOT GENERATED; '
        'NOT OPENED; NOT RUN. Speed, memory, confidence, and rankings: '
        'NOT MEASURED.</text>',
        '<text x="66" y="987" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">The separate 8,244 reference '
        'checks are not added to the 31,237 original checks.</text>',
        '<text x="51" y="1054" fill="#cbd5e1" font-size="12" '
        'font-family="system-ui,sans-serif">Published suite outcomes are '
        'preserved; individual failing examples are not all recorded.</text>',
        '<text x="51" y="1084" fill="#94a3b8" font-size="12" '
        'font-family="system-ui,sans-serif">Overview 97; '
        + VISIBLE_FOOTER
        + "</text>",
        "</svg>",
        "",
    ))
    return "\n".join(parts).encode("utf-8")


def changes() -> dict:
    return {
        "actual_current_graph_predecessor_version": 96,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v97_new_directly_authenticated_evidence_owner_count": 0,
        "lossless_previous_v96_proof_pool_count": 18,
        "lossless_v96_all_eighteen_previous_pool_identity_status": "PASS",
        "lossless_v96_snapshot_identity_status": "PASS",
        "lossless_v96_family_identity_status": "PASS",
        "v96_visible_footer_status": "REJECTED; OVERBROAD COMPLETENESS CLAIM",
        "v96_rejected_svg_sha256": V96["svg"][1],
        "v96_rejected_svg_bytes": V96["svg"][2],
        "public_reporting_integrity": VISIBLE_POLICY,
        "published_c_suite_outcomes_preserved": True,
        "published_c_suite_outcome_count": 13,
        "individual_failing_examples_fully_recorded": False,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "c_v10_original_campaign_verified_passing_case_count": 13606,
        "c_v10_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v10_original_campaign_individual_mismatch_vector_count": "NOT MEASURED",
        "c_v10_original_campaign_complete_individual_mismatch_vectors": "NOT MEASURED",
        "c_v10_original_campaign_candidate_execution_failure_count": 5,
        "c_v10_original_campaign_infrastructure_failure_count": 0,
        "c_v10_original_campaign_completed_suite_count": 8,
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
        "caller-pin every byte of the immutable truthful V97 renderer",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "whole immutable truthful V97 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V96.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin the complete published V96 " + role,
        )
    for role, item in C_SOURCE.items():
        base.need(
            getattr(options, "c_" + role + "_sha256") == item[1],
            "caller-pin the complete original C V10 " + role,
        )
    for role, item in ZIG14_SOURCE.items():
        base.need(
            getattr(options, "zig_" + role + "_sha256") == item[1],
            "caller-pin the complete original Zig V14 " + role,
        )
    base.need(
        options.c_receipt_sha256 == C_RECEIPT[1]
        and options.zig_controller_receipt_sha256 == ZIG14_RECEIPT[1],
        "caller-pin the complete independently recorded C and Zig failure evidence",
    )
    old = authenticate_previous(previous, chain, base)
    evidence = previous.load_new_evidence(base)
    c_contract, c_receipt, c_facts, zig_contract, zig_receipt, zig_facts = evidence
    pool = old[previous.POOL_KEY]
    previous.validate_evidence_pool(base, pool, *evidence)
    c_proof = previous.resolve_reference(
        base, pool, old[previous.C_LATEST_KEY], "c"
    )
    zig_proof = previous.resolve_reference(
        base, pool, old[previous.ZIG_CONTROLLER_KEY], "zig"
    )
    base.need(
        base.canonical(c_proof["validated_campaign_outcome"])
        == base.canonical(c_facts)
        and base.canonical(zig_proof["validated_controller_outcome"])
        == base.canonical(zig_facts)
        and c_facts.get("verified_passing_case_count") == 13606
        and c_facts.get("observed_semantic_mismatch_lower_bound") == 606
        and c_facts.get("aggregate_semantic_mismatch_count") == "NOT MEASURED"
        and c_facts.get("individual_mismatch_vector_count") == "NOT MEASURED"
        and c_facts.get("complete_individual_mismatch_vectors") == "NOT MEASURED"
        and c_facts.get("candidate_execution_failure_count") == 5
        and c_facts.get("infrastructure_failure_count") == 0
        and c_facts.get("completed_suite_count") == 8
        and zig_facts.get("actual_candidate_worker_count") == "NOT MEASURED"
        and zig_facts.get("actual_verified_passing_case_count") == "NOT MEASURED"
        and zig_facts.get("corrected_finalizer_warning_count") == "NOT MEASURED",
        "retain authentic C lower-bound-only evidence and the unmatched Zig failure",
    )
    delta = changes()
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V96.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update({
        "schema": SCHEMA + "-compact-current-snapshot",
        "version": 97,
        "previous_complete_snapshot_sha256": V96_SNAPSHOT_SHA256,
        "previous_complete_snapshot_canonical_bytes": V96_SNAPSHOT_BYTES,
        "previous_complete_overview_sha256": V96["summary"][1],
        "previous_complete_overview_bytes": V96["summary"][2],
        **copy.deepcopy(delta),
    })
    headline = copy.deepcopy(old["headline"])
    headline.update({
        "public_reporting_integrity": VISIBLE_POLICY,
        "published_c_suite_outcomes_preserved": True,
        "published_c_suite_outcome_count": 13,
        "individual_failing_examples_fully_recorded": False,
        "c_individual_mismatch_vector_count": "NOT MEASURED",
        "c_complete_individual_mismatch_vectors": "NOT MEASURED",
        "c_complete_mismatch_total": "NOT MEASURED",
        "c_observed_mismatch_lower_bound": 606,
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
        "version": 97,
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
    base.need(
        base.canonical(families) == base.canonical(old["families"]),
        "preserve every original candidate family without inventing new evidence",
    )
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 97,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(INPUT_PATH, base.digest(inputs_raw), len(inputs_raw)),
        "svg": base.pin(SVG_PATH, base.digest(svg_raw), len(svg_raw)),
        "previous_overview": copy.deepcopy(predecessor),
        "previous_v96_snapshot": copy.deepcopy(old["snapshot"]),
        "previous_v96_snapshot_canonical_sha256": V96_SNAPSHOT_SHA256,
        "previous_v96_snapshot_canonical_bytes": V96_SNAPSHOT_BYTES,
        "snapshot": copy.deepcopy(snapshot),
        "headline": copy.deepcopy(headline),
        "families": families,
        "preserved_v96_latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        "latest_original_campaigns": copy.deepcopy(
            old["latest_original_campaigns"]
        ),
        **copy.deepcopy(delta),
    })
    for key, size, expected, count in previous_pools(previous, chain):
        raw = base.canonical(summary[key])
        base.need(
            len(raw) == size
            and base.digest(raw) == expected
            and raw == base.canonical(old[key])
            and len(summary[key]["entries"]) == count,
            "retain every complete authenticated V96 proof pool: " + key,
        )
    base.need(
        base.canonical(summary["previous_v96_snapshot"])
        == base.canonical(old["snapshot"])
        and base.canonical(summary["previous_v95_snapshot"])
        == base.canonical(old["previous_v95_snapshot"])
        and base.canonical(summary["previous_v94_snapshot"])
        == base.canonical(old["previous_v94_snapshot"])
        and base.canonical(summary["families"])
        == base.canonical(old["families"])
        and base.canonical(summary["latest_original_campaigns"])
        == base.canonical(old["latest_original_campaigns"])
        and base.canonical(summary["preserved_v96_latest_original_campaigns"])
        == base.canonical(old["latest_original_campaigns"])
        and summary["rust_v22_original_campaign_verified_passing_case_count"] == 14725
        and summary["rust_v22_original_campaign_observed_mismatch_lower_bound"] == 2018
        and summary["rust_v22_original_campaign_complete_failure_worker_warning_count"]
        == 16
        and summary["c_v10_original_campaign_verified_passing_case_count"] == 13606
        and summary["c_v10_original_campaign_observed_mismatch_lower_bound"] == 606
        and summary["c_v10_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_individual_mismatch_vector_count"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_complete_individual_mismatch_vectors"]
        == "NOT MEASURED"
        and summary["c_v10_original_campaign_candidate_execution_failure_count"] == 5
        and summary["c_v10_original_campaign_infrastructure_failure_count"] == 0
        and summary["zig_v13_original_campaign_verified_passing_case_count"] == 4607
        and summary["zig_v13_original_campaign_cleanup_warning_worker_count"] == 13
        and summary["zig_v14_controller_failure_candidate_worker_count"]
        == "NOT MEASURED"
        and summary["zig_v14_controller_failure_corrected_warning_count"]
        == "NOT MEASURED"
        and summary["authenticated_evidence_owner_lower_bound"] == EVIDENCE_FLOOR
        and summary["authenticated_history_reference_lower_bound"] == HISTORY_FLOOR
        and summary["qualified_candidate_count"] == 0
        and summary["runtime_no_delegation"] == "NOT ESTABLISHED"
        and summary["performance"] == "NOT MEASURED"
        and summary["memory"] == "NOT MEASURED"
        and summary["undefined_behavior"] == "NOT MEASURED"
        and summary["expanded_holdout_proposed_case_count"] == HOLDOUT_PROPOSAL_COUNT
        and summary["expanded_holdout_case_status"] == "NOT GENERATED; NOT OPENED"
        and summary["final_holdout_opened"] is False
        and summary["winner_selected"] is False,
        "retain every recorded outcome without implying missing individual examples",
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
            "reject oversized complete V97 graph evidence: " + path,
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
        "version": 97,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inputs_sha256": base.digest(assets[INPUT_PATH]),
        "inputs_bytes": len(assets[INPUT_PATH]),
        "summary_sha256": base.digest(assets[SUMMARY_PATH]),
        "summary_bytes": len(assets[SUMMARY_PATH]),
        "svg_sha256": base.digest(assets[SVG_PATH]),
        "svg_bytes": len(assets[SVG_PATH]),
        "actual_current_graph_predecessor_version": 96,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "v97_new_directly_authenticated_evidence_owner_count": 0,
        "lossless_previous_v96_proof_pool_count": 18,
        "lossless_v96_all_eighteen_previous_pool_identity_status": "PASS",
        "lossless_v96_snapshot_identity_status": "PASS",
        "lossless_v96_family_identity_status": "PASS",
        "v96_visible_footer_status": "REJECTED; OVERBROAD COMPLETENESS CLAIM",
        "v96_rejected_svg_sha256": V96["svg"][1],
        "v96_rejected_svg_bytes": V96["svg"][2],
        "public_reporting_integrity": VISIBLE_POLICY,
        "published_c_suite_outcomes_preserved": True,
        "published_c_suite_outcome_count": 13,
        "individual_failing_examples_fully_recorded": False,
        "original_case_execution_denominator": CASE_COUNT,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_additional_reference_case_count": SUPPLEMENTAL_CASE_COUNT,
        "additional_cases_included_in_original_denominator": False,
        "rust_v22_original_campaign_verified_passing_case_count": 14725,
        "rust_v22_original_campaign_observed_mismatch_lower_bound": 2018,
        "rust_v22_original_campaign_complete_failure_worker_warning_count": 16,
        "rust_v22_original_campaign_all_worker_warning_count": "NOT MEASURED",
        "c_v9_original_campaign_verified_passing_case_count": 13606,
        "c_v9_original_campaign_observed_mismatch_lower_bound": 492,
        "c_v9_original_campaign_candidate_execution_failure_count": 6,
        "c_v10_original_campaign_actual_worker_count": 13,
        "c_v10_original_campaign_clean_suite_count": 3,
        "c_v10_original_campaign_completed_suite_count": 8,
        "c_v10_original_campaign_mismatch_suite_count": 5,
        "c_v10_original_campaign_verified_passing_case_count": 13606,
        "c_v10_original_campaign_observed_mismatch_lower_bound": 606,
        "c_v10_original_campaign_semantic_mismatch_count": "NOT MEASURED",
        "c_v10_original_campaign_individual_mismatch_vector_count": "NOT MEASURED",
        "c_v10_original_campaign_complete_individual_mismatch_vectors": "NOT MEASURED",
        "c_v10_original_campaign_candidate_execution_failure_count": 5,
        "c_v10_original_campaign_infrastructure_failure_count": 0,
        "zig_v13_original_campaign_verified_passing_case_count": 4607,
        "zig_v13_original_campaign_observed_mismatch_lower_bound": 1700,
        "zig_v13_original_campaign_cleanup_warning_worker_count": 13,
        "zig_v14_controller_failure_attempt_count": 1,
        "zig_v14_controller_failure_pipeline_exit_code": 4,
        "zig_v14_controller_failure_candidate_status": "NOT MEASURED",
        "zig_v14_controller_failure_candidate_worker_count": "NOT MEASURED",
        "zig_v14_controller_failure_completed_suite_count": "NOT MEASURED",
        "zig_v14_controller_failure_verified_passing_case_count": "NOT MEASURED",
        "zig_v14_controller_failure_semantic_mismatch_count": "NOT MEASURED",
        "zig_v14_controller_failure_corrected_warning_count": "NOT MEASURED",
        "expanded_holdout_proposed_case_count": HOLDOUT_PROPOSAL_COUNT,
        "preserved_previous_holdout_proposal_case_count":
        HISTORICAL_HOLDOUT_PROPOSAL_COUNT,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
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


def self_test(
    previous: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    prior = previous.self_test(*chain, previous_options(previous))
    base.need(
        prior.get("status") == "PASS"
        and prior.get("version") == 96
        and prior.get("rejected_hostile_control_count") == 14408
        and prior.get("inherited_rejected_hostile_control_count") == 13771
        and prior.get("new_rejected_hostile_control_count") == 637
        and prior.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
        and prior.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
        and prior.get("lossless_previous_v95_proof_pool_count") == 17
        and prior.get("lossless_v95_all_seventeen_previous_pool_identity_status")
        == "PASS"
        and prior.get("rust_v22_original_campaign_verified_passing_case_count") == 14725
        and prior.get("c_v10_original_campaign_verified_passing_case_count") == 13606
        and prior.get("c_v10_original_campaign_observed_mismatch_lower_bound") == 606
        and prior.get("c_v10_original_campaign_complete_individual_mismatch_vectors")
        == "NOT MEASURED"
        and prior.get("zig_v13_original_campaign_verified_passing_case_count") == 4607
        and prior.get("zig_v14_controller_failure_candidate_worker_count")
        == "NOT MEASURED"
        and prior.get("qualified_candidate_count") == 0
        and prior.get("performance") == "NOT MEASURED"
        and prior.get("outputs_written") is False,
        "preserve every actual V96 hostile control and original experiment result",
    )
    _, assets = build(previous, chain, base, options)
    old = authenticate_previous(previous, chain, base)
    headline = base.document(assets[SUMMARY_PATH], "whole truthful V97 summary")["headline"]
    snapshot = base.document(assets[SUMMARY_PATH], "whole truthful V97 summary")["snapshot"]
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            if not callable(callback):
                raise ValueError("require a callable V97 hostile control")
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V97 accepted misleading evidence: " + label)

    for phrase in FORBIDDEN_VISIBLE_PHRASES:
        forged = assets[SVG_PATH].replace(
            VISIBLE_FOOTER.encode("utf-8"), phrase.encode("utf-8")
        )
        reject(
            "overbroad visible preservation claim",
            lambda raw=forged: validate_visible_language(base, raw),
        )
        forged_headline = dict(headline)
        forged_snapshot = dict(snapshot)
        forged_headline["public_reporting_integrity"] = phrase
        forged_snapshot["public_reporting_integrity"] = phrase
        reject(
            "overbroad machine-readable preservation claim",
            lambda head=forged_headline, snap=forged_snapshot:
            validate_machine_language(base, head, snap),
        )
    for phrase in (
        "individual failing examples are not all recorded",
        "published suite outcomes",
        "observed lower bound",
        "13,606 / 31,237 (43.6%)",
        "NOT MEASURED",
        "NOT FROZEN",
        "NOT GENERATED",
        "NOT OPENED",
        "no winner",
    ):
        original = assets[SVG_PATH]
        folded = original.lower()
        needle = phrase.encode("ascii").lower()
        base.need(
            needle in folded,
            "exercise a genuine visible V97 disclosure: " + phrase,
        )
        pieces = []
        start = 0
        while True:
            position = folded.find(needle, start)
            if position < 0:
                pieces.append(original[start:])
                break
            pieces.extend((original[start:position], b"REMOVED"))
            start = position + len(needle)
        forged = b"".join(pieces)
        reject(
            "removed genuine visible disclosure: " + phrase,
            lambda raw=forged: validate_visible_language(base, raw),
        )
    for key, wrong in (
        ("public_reporting_integrity", "invented complete preservation"),
        ("published_c_suite_outcomes_preserved", False),
        ("individual_failing_examples_fully_recorded", True),
        ("c_individual_mismatch_vector_count", 606),
        ("c_complete_individual_mismatch_vectors", True),
        ("c_observed_mismatch_lower_bound", 492),
        ("c_complete_mismatch_total", 606),
        ("bars_measure", "SPEED"),
        ("speed_relative_to_python", "1.5x"),
        ("performance", "FASTER"),
        ("fully_compatible_candidate_count", 1),
        ("winner_selected", True),
    ):
        forged = dict(headline)
        forged[key] = wrong
        reject(
            "fabricated public headline " + key,
            lambda head=forged: validate_machine_language(base, head, snapshot),
        )
    for key, wrong in (
        ("public_reporting_integrity", "invented complete preservation"),
        ("published_c_suite_outcomes_preserved", False),
        ("individual_failing_examples_fully_recorded", True),
        ("c_v10_original_campaign_individual_mismatch_vector_count", 606),
        ("c_v10_original_campaign_complete_individual_mismatch_vectors", True),
    ):
        forged = dict(snapshot)
        forged[key] = wrong
        reject(
            "fabricated public snapshot " + key,
            lambda snap=forged: validate_machine_language(base, headline, snap),
        )
    for key, size, expected, count in previous_pools(previous, chain):
        forged = dict(old)
        forged.pop(key)
        reject(
            "omitted complete V96 evidence pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
        forged = dict(old)
        pool = dict(old[key])
        pool["entries"] = {}
        forged[key] = pool
        reject(
            "discarded complete V96 evidence pool " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    for key, wrong in (
        ("version", 95),
        ("authenticated_evidence_owner_lower_bound", 343),
        ("authenticated_history_reference_lower_bound", 348),
        ("original_case_execution_denominator", CASE_COUNT + SUPPLEMENTAL_CASE_COUNT),
        ("rust_v22_original_campaign_verified_passing_case_count", 15749),
        ("c_v10_original_campaign_verified_passing_case_count", 31237),
        ("c_v10_original_campaign_observed_mismatch_lower_bound", 492),
        ("c_v10_original_campaign_semantic_mismatch_count", 606),
        ("c_v10_original_campaign_individual_mismatch_vector_count", 606),
        ("c_v10_original_campaign_complete_individual_mismatch_vectors", True),
        ("c_v10_original_campaign_infrastructure_failure_count", 5),
        ("zig_v13_original_campaign_verified_passing_case_count", 31237),
        ("zig_v14_controller_failure_candidate_worker_count", 13),
        ("zig_v14_controller_failure_corrected_warning_count", 0),
        ("qualified_candidate_count", 1),
        ("runtime_no_delegation", "PASS"),
        ("performance", "FASTER"),
        ("expanded_holdout_case_status", "OPENED"),
        ("winner_selected", True),
    ):
        forged = dict(old)
        forged[key] = wrong
        reject(
            "fabricated complete V96 predecessor " + key,
            lambda value=forged: validate_previous(previous, chain, base, value),
        )
    c_contract, c_receipt, c_facts, zig_contract, zig_receipt, zig_facts = (
        previous.load_new_evidence(base)
    )
    for index, (suite, _) in enumerate(SUITES):
        for key in sorted(previous.C_ROW_KEYS):
            forged = dict(c_receipt)
            rows = list(c_receipt["suite_outcomes"])
            row = dict(rows[index])
            row.pop(key)
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "omitted exact recorded C suite outcome " + suite + ":" + key,
                lambda value=forged: previous.validate_c_receipt(base, value),
            )
        for key, wrong in (
            ("suite", "invented"),
            ("case_execution_denominator", 0),
            ("worker_process_id", 0),
            ("mismatch_count", -1),
            ("failure_class", "invented"),
            ("plain_failure_diagnostic", "invented"),
        ):
            forged = dict(c_receipt)
            rows = list(c_receipt["suite_outcomes"])
            row = dict(rows[index])
            row[key] = wrong
            rows[index] = row
            forged["suite_outcomes"] = rows
            reject(
                "changed exact recorded C suite outcome " + suite + ":" + key,
                lambda value=forged: previous.validate_c_receipt(base, value),
            )
    for key, wrong in (
        ("candidate_status", "PASS"),
        ("actual_candidate_worker_count", 13),
        ("actual_completed_suite_count", 13),
        ("actual_verified_passing_case_count", 31237),
        ("actual_semantic_mismatch_count", 0),
        ("corrected_finalizer_warning_count", 0),
        ("failure_archive_created", True),
        ("success_receipt_created", True),
    ):
        forged = dict(zig_receipt)
        forged[key] = wrong
        reject(
            "invented Zig matching from a controller-only failure " + key,
            lambda value=forged: previous.validate_zig_controller(base, value),
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
        ("import", ("candidates.c_candidate", None, None, None, None)),
        ("import", ("gzip", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
        ("open", (str(ROOT / INPUT_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SUMMARY_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / SVG_PATH), None, os.O_RDONLY)),
        ("open", (str(ROOT / "performance/holdout.json"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "private.json.gz"), None, os.O_RDONLY)),
        ("open", (str(ROOT / "candidates/_zig_probe.so"), None, os.O_RDONLY)),
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
        rejected >= 300,
        "require complete inherited and new V97 visible-language hostile controls",
    )
    return result_payload(base, options, assets, False, {
        "schema": SCHEMA + "-source-only-self-test",
        "inherited_rejected_hostile_control_count":
        prior["rejected_hostile_control_count"],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count":
        prior["rejected_hostile_control_count"] + rejected,
    })


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {INPUT_PATH, SUMMARY_PATH, SVG_PATH}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only a bounded, exclusively created V97 public owner",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    handle = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(handle, remaining)
            base.need(type(count) is int and count > 0, "write complete V97 evidence")
            remaining = remaining[count:]
        os.fsync(handle)
        owner = os.fstat(handle)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_dev == 2064
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "authenticate every exclusively created V97 graph byte",
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
    base.need(actual == raw, "reauthenticate every complete final V97 graph byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-preview", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V96:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for role in C_SOURCE:
        parser.add_argument("--c-" + role + "-sha256", required=True)
    for role in ZIG14_SOURCE:
        parser.add_argument("--zig-" + role + "-sha256", required=True)
    parser.add_argument("--c-receipt-sha256", required=True)
    parser.add_argument("--zig-controller-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, chain, base = load_previous()
        if not options.render:
            install_source_wall()
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
        sys.stderr.write("current V97 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
