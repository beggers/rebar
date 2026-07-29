#!/usr/bin/env python3
"""Show actual first-party results without treating source or builds as speed."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v87.py"
OUTPUT = "docs/evidence/candidate-current-overview-v87"
SCHEMA = "rebar-candidate-current-overview-v87"
OWNER_LIMIT = 4 * 1024 * 1024
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE_POOL_KEY = "lossless_v87_source_evidence_pool"
SOURCE_POOL_SCHEMA = SCHEMA + "-lossless-complete-source-pool-v1"
SOURCE_PROOF_SCHEMA = SCHEMA + "-complete-source-proof-v1"
SOURCE_REFERENCE_SCHEMA = SCHEMA + "-complete-source-reference-v1"
ACTUAL_KEY = "actual_rust_v20_literal_native_build"
ACTUAL_POOL_KEY = "lossless_v87_rust_actual_build_evidence_pool"
ACTUAL_POOL_SCHEMA = SCHEMA + "-lossless-complete-rust-build-pool-v1"
ACTUAL_REFERENCE_SCHEMA = SCHEMA + "-complete-rust-build-reference-v1"

V86 = {
    "source": (
        "tools/render_candidate_current_overview_v86.py",
        "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d",
        75354,
        431699,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v86.inputs.json",
        "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c",
        1345744,
        430944,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v86.json",
        "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc",
        4128155,
        431704,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v86.svg",
        "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55",
        6214,
        431705,
    ),
}

FEATURES = (
    (
        "rust_literal_v1",
        "First-party one-pass Rust literal source",
        {
            "source": (
                "tools/verify_owned_rust_literal_findall_source_v1.py",
                "21fb0878e344ead0bba49f932120a35a897ca44cfd7710287861ebc6415c555e",
                33883,
                429583,
            ),
            "protocol": (
                "oracle/phase2/RUST-LITERAL-FINDALL-ONE-PASS-V1.md",
                "842d51127db54a26d0dd9f874f38834f122f7888ea71c6f3fe77b8911bbd65d6",
                4515,
                525256,
            ),
            "contract": (
                "oracle/phase2/rust-literal-findall-one-pass-v1.json",
                "a2226d823610a578aeb65e9a51a2a33517348b6c51130ad89db840cc50833164",
                3167,
                525262,
            ),
            "variant": (
                "candidates/rust/variants/buffer_shape_pickle_findall_v1/py_bridge.c",
                "b707e924a23980385b0c5b0306daecd55bbb03d6f2511437f0532b6d39b2a112",
                178950,
                525253,
            ),
        },
    ),
    (
        "rust_diagnostic_v16",
        "Source-only Rust original-suite failure diagnostics",
        {
            "source": (
                "tools/run_owned_repaired_rust_original_campaign_v16.py",
                "4705f5afb0639812e4902a455c11cee469b78a2a8f78bd64e1bf3388390d060e",
                153060,
                429584,
            ),
            "protocol": (
                "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V16.md",
                "b168f394244c1f2e2f1051a0d9ed038fd11b596708667b9c8dc196b3f8f2c66f",
                13426,
                525263,
            ),
            "contract": (
                "oracle/phase2/repaired-rust-original-campaign-v16.json",
                "1879abea2cfc3665ec5e0eeb9549286f1d566806f4f49482064855199a86d46b",
                15406,
                525264,
            ),
        },
    ),
    (
        "expanded_holdout_v1",
        "Unopened 14,155,776-case comparison proposal",
        {
            "source": (
                "tools/verify_expanded_sealed_holdout_v1.py",
                "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
                27311,
                428806,
            ),
            "protocol": (
                "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
                "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
                13237,
                524760,
            ),
            "contract": (
                "oracle/phase3/expanded-sealed-holdout-v1.json",
                "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
                6628,
                524761,
            ),
        },
    ),
    (
        "rust_captured_v1",
        "Unbuilt first-party two-capture Rust source",
        {
            "source": (
                "tools/verify_owned_rust_captured_findall_source_v1.py",
                "61c4d4beda9baf82150a8ae5e47f78eb1363595a583f0317626e93beb5373832",
                59368,
                429082,
            ),
            "protocol": (
                "oracle/phase2/RUST-CAPTURED-FINDALL-ONE-PASS-V1.md",
                "ffcaeec11704a81a2fd5ca25d7fc746c8a66fab033bb1f108f0e6c19445079fe",
                5953,
                524771,
            ),
            "contract": (
                "oracle/phase2/rust-captured-findall-one-pass-v1.json",
                "ec396c100f606923f08d1969f283a9bb2bcf35dbf9edf9e9c5d2360057f9079b",
                5320,
                524780,
            ),
            "variant": (
                "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c",
                "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a",
                179520,
                524770,
            ),
        },
    ),
    (
        "rust_build_v20",
        "Frozen first-party Rust literal native build",
        {
            "source": (
                "tools/reproduce_owned_rust_literal_findall_source_build_v20.py",
                "e1c30d8713d1acafdffba28123966dc9814ea765b97cf3ad09da3ccf42c97b0e",
                122839,
                429585,
            ),
            "protocol": (
                "oracle/phase2/RUST-LITERAL-FINDALL-SOURCE-BUILD-V20.md",
                "3393f73b11c6ad38c9f8dffc9f36e02ba11da64997ef351220e600bbae975f86",
                6221,
                525265,
            ),
            "contract": (
                "oracle/phase2/rust-literal-findall-source-build-v20.json",
                "5b584cc225226928e22169903d1a7f8712039b4ae3d34dd5a634f8174f4d8eb0",
                17479,
                524764,
            ),
        },
    ),
    (
        "c_diagnostic_v5",
        "Source-only first-party C correctness diagnostics",
        {
            "source": (
                "tools/run_owned_repaired_c_original_campaign_v5.py",
                "a98e080fa3c9b556122316966723ea7f69589ffddd6293e1ebe199c0dde07810",
                50004,
                429083,
            ),
            "protocol": (
                "oracle/phase2/REPAIRED-C-ORIGINAL-CAMPAIGN-V5.md",
                "bec733d3181da1198fc44c6b22cb45d7df8a6721ef073e09cde7650c47453237",
                6313,
                524779,
            ),
            "contract": (
                "oracle/phase2/repaired-c-original-campaign-v5.json",
                "95de401d8a63a6a7272d86ef062c775100ce7305d74fec85be1ed7b0236381f2",
                8950,
                524786,
            ),
        },
    ),
)
FEATURE_BY_KEY = {item[0]: item for item in FEATURES}
PREDECESSOR = (
    "candidates/rust/variants/buffer_shape_pickle_v2/py_bridge.c",
    "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740",
    179961,
    525057,
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v20-rust-phase2-v20-rust-literal-findall-"
    "root-provenance-publication-receipt.json",
    "b9945838778c800f59a505021503655ea5bb4b3e11e1f0cf17f4be48cadde1b0",
    3498,
    524791,
)
ROOT_RECEIPT = (
    "oracle/phase2/evidence/"
    "native-source-build-v20-rust-phase2-v20-rust-literal-findall-"
    "root-provenance-root-provenance-receipt.json",
    "bb5bd524a7bd8c4b3845c9654e81981cb6136c4fcff7a5e52ca375ce75e745aa",
    5685,
    524792,
)
ARCHIVE_PATH = (
    "oracle/phase2/evidence/"
    "native-source-build-v20-rust-phase2-v20-rust-literal-findall-"
    "root-provenance.json.gz"
)
ARCHIVE_SHA256 = (
    "0edfe0559f45b00a295cce4094bc7ddc85acd87ef0f4205cdac8c8e3f970f883"
)
ENGINE_SHA256 = (
    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
)
NATIVE_BRIDGE_SHA256 = (
    "cbd3e7687dac3c2378d4136bb5f4aac322f72b485d6561bbf03fe4c2290b605b"
)


def read_fixed(item: tuple[str, str, int, int], label: str) -> bytes:
    relative, expected, size, inode = item
    if not (type(size) is int and 0 < size <= OWNER_LIMIT):
        raise ValueError("reject unbounded V87 owner: " + label)
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
            raise ValueError("reject replaced exact V87 owner: " + label)
        remaining = size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(handle, min(remaining, 262144))
            if not chunk:
                raise ValueError("reject truncated V87 owner: " + label)
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(handle, 1):
            raise ValueError("reject extended V87 owner: " + label)
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
            raise ValueError("reject changing exact V87 owner: " + label)
        return raw
    finally:
        os.close(handle)


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
})
FORBIDDEN_IMPORTS = frozenset({
    "regex", "ctypes", "subprocess", "multiprocessing", "socket", "time",
    "gzip", "bz2", "lzma", "tarfile", "zipfile",
})


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event in FORBIDDEN_EVENTS:
        raise ValueError("V87 source-only operation rejected " + event)
    if event == "import":
        name = arguments[0] if arguments else None
        if isinstance(name, str) and name.partition(".")[0] in FORBIDDEN_IMPORTS:
            raise ValueError("V87 source-only import rejected " + name)
        return
    if event != "open":
        return
    if len(arguments) < 3:
        raise ValueError("V87 rejected an unverifiable file open")
    path, mode, flags = arguments[:3]
    if not isinstance(path, str) or not isinstance(flags, int):
        raise ValueError("V87 rejected a descriptor or unverified open")
    if mode not in (None, "r", "rb"):
        raise ValueError("V87 source mode cannot open a writable file")
    if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
        os.O_CREAT | os.O_TRUNC | os.O_APPEND
    ):
        raise ValueError("V87 source mode cannot create or alter a file")
    normalized = os.path.normpath(path)
    if os.path.isabs(normalized):
        if normalized != str(ROOT) and not normalized.startswith(str(ROOT) + "/"):
            raise ValueError("V87 cannot open a private root or holdout")
    elif "/" in normalized or normalized in (".", ".."):
        raise ValueError("V87 cannot escape its authenticated directory")
    if (
        normalized.endswith((".gz", ".bz2", ".xz", ".zip", ".so"))
        or "candidate-current-overview-v87." in normalized
        or "/.git/" in normalized
        or "/__pycache__/" in normalized
        or "/performance/" in normalized
        or "/experiments/" in normalized
    ):
        raise ValueError("V87 cannot open archives, native code, or benchmarks")


def load_previous() -> tuple[
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    types.ModuleType,
    tuple,
    types.ModuleType,
]:
    raw = read_fixed(V86["source"], "complete published V86 renderer")
    previous = types.ModuleType("_rebar_exact_pushed_source_graph_v86")
    previous.__file__ = str(ROOT / V86["source"][0])
    previous.__package__ = ""
    exec(compile(raw, previous.__file__, "exec", dont_inherit=True), previous.__dict__)
    v85, v84, v83, v82, chain, base = previous.load_previous()
    base.runtime()
    base.need(
        os.path.realpath(sys.executable) == PYTHON
        and sys.implementation.name == "cpython"
        and sys.implementation.cache_tag == "cpython-314"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True
        and previous.SCHEMA == "rebar-candidate-current-overview-v86"
        and previous.SELF == V86["source"][0]
        and len(chain) == 15,
        "require the pinned isolated CPython and entire authentic V86 source chain",
    )
    return previous, v85, v84, v83, v82, chain, base


def authenticate_previous(
    previous: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
) -> tuple[dict, dict]:
    pins: dict[str, object] = {
        "source_sha256": V86["source"][1],
        "source_bytes": V86["source"][2],
        "root_receipt_sha256": previous.ROOT_RECEIPT[1],
        "build_receipt_sha256": previous.BUILD_RECEIPT[1],
    }
    for role, item in previous.V85.items():
        pins["previous_" + role + "_sha256"] = item[1]
    snapshot, assets = previous.build(
        v85, v84, v83, v82, chain, base, argparse.Namespace(**pins)
    )
    for role in ("inputs", "summary", "svg"):
        item = V86[role]
        base.need(
            assets[item[0]] == read_fixed(item, "complete pushed V86 " + role),
            "reconstruct every published V86 " + role + " byte",
        )
    old = base.document(assets[V86["summary"][0]], "complete pushed V86 summary")
    inputs = base.document(assets[V86["inputs"][0]], "complete pushed V86 inputs")
    base.need(
        old["snapshot"] == snapshot
        and old["schema"] == previous.SCHEMA + "-summary"
        and old["version"] == 86
        and inputs["version"] == 86
        and old["authenticated_evidence_owner_lower_bound"] == 277
        and old["authenticated_history_reference_lower_bound"] == 282
        and old["lossless_family_evidence_pool_entry_count"] == 9
        and old["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and old["lossless_zig_source_evidence_pool_entry_count"] == 1
        and old["lossless_zig_actual_build_evidence_pool_entry_count"] == 1
        and old["rust_v15_original_campaign_candidate_matching"] == "FAIL"
        and old["rust_v15_original_campaign_actual_worker_count"] == 13
        and old["rust_v15_original_campaign_completed_suite_count"] == 8
        and old["rust_v15_original_campaign_verified_passing_case_count"] == 12942
        and old["rust_v15_original_campaign_infrastructure_failure_count"] == 5
        and old["rust_v15_original_campaign_semantic_mismatch_count"]
        == "NOT MEASURED"
        and old["actual_c_semantic_mismatch_count"] == 1230
        and old["actual_zig_semantic_mismatch_count"] == 1764
        and old["zig_v13_first_party_source_build_actual_process_count"] == 26
        and old["zig_v13_first_party_source_build_actual_phase_count"] == 2
        and old["qualified_candidate_count"] == 0
        and old["runtime_no_delegation"] == "NOT ESTABLISHED"
        and old["performance"] == "NOT MEASURED"
        and old["final_holdout_opened"] is False,
        "preserve exact original compatibility failures and genuine V86 results",
    )
    history = {key: copy.deepcopy(old[key]) for key in v83.PROOF_KEYS}
    v83.validate_pool(base, old["lossless_family_evidence_pool"], history)
    v84.validate_actual_pool(
        base, old["lossless_actual_outcome_evidence_pool"], old[v84.ACTUAL_KEY]
    )
    v85.validate_zig_pool(
        base, old["lossless_zig_source_evidence_pool"], old[v85.ZIG_KEY]
    )
    zig_build = previous.resolve_build_reference(
        base,
        old["lossless_zig_actual_build_evidence_pool"],
        old[previous.BUILD_KEY],
    )
    previous.validate_build_pool(
        base, old["lossless_zig_actual_build_evidence_pool"], zig_build
    )
    rows = old["families"]
    base.need(
        type(rows) is list
        and [row.get("family") for row in rows]
        == ["python", "rust", "c", "zig", "cpp", "go", "fortran"]
        and rows[0]["correctness"] == "BASELINE PASS"
        and all(
            row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED"
            for row in rows[1:]
        )
        and rows[6]["build_status"] == "FAIL"
        and rows[6]["matching_test_status"] == "NOT MEASURED"
        and rows[6]["completed_source_build_count"] == 2,
        "retain the Python baseline, all six first-party families and Fortran failure",
    )
    return old, inputs


def feature_constants(raw: bytes, names: frozenset[str]) -> dict[str, bytes]:
    tree = ast.parse(raw, filename="<authenticated-first-party-source>")
    observed: dict[str, bytes] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in names:
            continue
        value = ast.literal_eval(node.value)
        if type(value) is not bytes or target.id in observed:
            raise ValueError("reject substituted first-party function constant")
        observed[target.id] = value
    if set(observed) != names:
        raise ValueError("reject omitted exact first-party function constants")
    return observed


def verify_single_function(
    base: types.ModuleType,
    before: bytes,
    after: bytes,
    constants: dict[str, bytes],
    old_key: str,
    new_key: str,
    label: str,
) -> None:
    start = constants["FUNCTION_START"]
    follow = constants["FUNCTION_FOLLOW"]
    base.need(
        before.count(start) == 1 and after.count(start) == 1,
        "require one complete first-party function: " + label,
    )
    old_start = before.index(start)
    new_start = after.index(start)
    old_end = before.find(follow, old_start)
    new_end = after.find(follow, new_start)
    base.need(
        old_end >= 0
        and new_end >= 0
        and before[old_start:old_end] == constants[old_key]
        and after[new_start:new_end] == constants[new_key]
        and before[:old_start] == after[:new_start]
        and before[old_end:] == after[new_end:],
        "preserve every predecessor byte outside the exact " + label,
    )


def validate_contract(
    base: types.ModuleType,
    key: str,
    document: object,
    raw: bytes,
) -> None:
    spec = FEATURE_BY_KEY[key][2]
    expected_raw = (
        (base.json.dumps(document, indent=2) + "\n").encode("utf-8")
        if key == "expanded_holdout_v1" and type(document) is dict
        else base.canonical(document)
    )
    base.need(
        type(document) is dict
        and expected_raw == raw
        and base.digest(raw) == spec["contract"][1],
        "reject any changed or incomplete complete source contract: " + key,
    )
    assert isinstance(document, dict)
    if key == "rust_literal_v1":
        variant = document["candidate_variant"]
        boundary = document["phase_boundary"]
        pilot = document["historical_practice_pilot"]
        base.need(
            document["schema"]
            == "rebar-phase2-owned-rust-literal-findall-one-pass-v1-source-freeze"
            and document["version"] == 1
            and document["status"]
            == "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED"
            and document["source"]["sha256"] == spec["source"][1]
            and document["protocol"]["sha256"] == spec["protocol"][1]
            and variant["sha256"] == spec["variant"][1]
            and variant["changed_function_count"] == 1
            and variant["native_build"] == "NOT RUN"
            and variant["matching"] == "NOT RUN"
            and variant["qualified"] is False
            and pilot["case_count"] == 864
            and pilot["literal_findall_case_count"] == 0
            and pilot["one_pass_variant_exercised"] is False
            and boundary["holdout_case_count"] == 4194304
            and boundary["winner_selected"] is False,
            "retain the literal freeze and its historical, not current, holdout",
        )
    elif key == "rust_diagnostic_v16":
        base.need(
            document["schema"]
            == "rebar-owned-repaired-rust-original-campaign-v16-recoverable-source-freeze"
            and document["version"] == 16
            and document["source_sha256"] == spec["source"][1]
            and document["protocol_sha256"] == spec["protocol"][1]
            and document["frozen_graph_version"] == 86
            and document["case_execution_denominator"] == 31237
            and document["suite_count"] == 13
            and document["supplemental_case_count"] == 8244
            and document["candidate_matching"] == "NOT RUN"
            and document["candidate_qualified"] is False
            and document["actual_candidate_workers_started"] == 0
            and document["actual_compiler_processes_started"] == 0
            and document["v15_actual_candidate_worker_count"] == 13
            and document["v15_actual_completed_suite_count"] == 8
            and document["v15_actual_verified_passing_case_count"] == 12942
            and document["v15_actual_infrastructure_failure_count"] == 5
            and document["v15_actual_semantic_mismatch_count"] == "NOT MEASURED"
            and document["qualified_candidate_count"] == 0
            and document["winner_selected"] is False,
            "reject any invented Rust V16 actual campaign or lost V15 failure",
        )
    elif key == "expanded_holdout_v1":
        base.need(
            len(document) == 71
            and document["schema"]
            == "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
            and document["proposal_status"] == "PRE-PHASE-3 PROPOSAL"
            and document["final_protocol_status"] == "NOT FROZEN"
            and document["generator_status"] == "NOT FROZEN"
            and document["secret_status"] == "NOT GENERATED"
            and document["case_status"] == "NOT GENERATED; NOT OPENED"
            and document["timing_status"] == "NOT RUN; NOT MEASURED"
            and document["memory_status"] == "NOT RUN; NOT MEASURED"
            and document["runtime_independence_status"] == "NOT ESTABLISHED"
            and document["winner_status"] == "NOT SELECTED"
            and document["qualified_independent_family_count"] == 0
            and document["minimum_qualified_independent_family_count"] == 3
            and document["preserved_previous_proposal_case_count"] == 4194304
            and document["case_count"] == 14155776
            and document["timed_case_count"] == 14155776
            and document["operation_count"] == 36
            and document["pattern_family_count"] == 24
            and document["subject_type_count"] == 4
            and document["lifecycle_count"] == 4
            and document["stratum_count"] == 13824
            and document["cases_per_stratum"] == 1024
            and 36 * 24 * 4 * 4 * 1024 == 14155776
            and document["original_p0_case_count"] == 31237
            and document["separate_differential_case_count"] == 8244,
            "reject any generated, sampled, opened, or miscounted final proposal",
        )
    elif key == "rust_captured_v1":
        variant = document["candidate_variant"]
        boundary = document["phase_boundary"]
        practice = document["historical_public_practice"]
        proposal = document["expanded_sealed_holdout_proposal"]
        base.need(
            document["schema"]
            == "rebar-phase2-owned-rust-captured-findall-one-pass-v1-source-freeze"
            and document["status"]
            == "SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED"
            and document["source"]["sha256"] == spec["source"][1]
            and document["protocol"]["sha256"] == spec["protocol"][1]
            and variant["sha256"] == spec["variant"][1]
            and variant["changed_function_count"] == 1
            and variant["specialized_capture_count"] == 2
            and variant["native_build"] == "NOT RUN"
            and variant["matching"] == "NOT RUN"
            and variant["qualified"] is False
            and practice["case_count"] == 864
            and practice["findall_case_count"] == 48
            and practice["materialized_capture_case_count"] == 44
            and practice["empty_capture_case_count"] == 4
            and practice["new_variant_exercised"] is False
            and practice["new_variant_timed"] is False
            and proposal["case_count"] == 14155776
            and proposal["case_status"] == "NOT GENERATED; NOT OPENED"
            and boundary["holdout_case_count"] == 14155776
            and boundary["candidate_workers_started"] == 0
            and boundary["winner_selected"] is False,
            "never mistake observed old cases for a built captured-search variant",
        )
    elif key == "rust_build_v20":
        effects = document["source_only_effects"]
        proposal = document["published_expanded_sealed_holdout_proposal"]
        history = document["historical_rust_results"]
        base.need(
            document["schema"]
            == "rebar-phase2-owned-rust-literal-findall-source-build-v20-source-freeze"
            and document["version"] == 20
            and document["source"]["sha256"] == spec["source"][1]
            and document["protocol"]["sha256"] == spec["protocol"][1]
            and proposal["case_count"] == 14155776
            and proposal["proposal_status"] == "PRE-PHASE-3 PROPOSAL"
            and proposal["final_protocol_status"] == "NOT FROZEN"
            and history["latest_guarded_completed_suite_count"] == 8
            and history["latest_guarded_verified_passing_case_count"] == 12942
            and history["latest_guarded_worker_failure_count"] == 5
            and effects["candidate_build"] == "NOT RUN"
            and effects["candidate_matching"] == "NOT RUN"
            and effects["actual_compiler_process_count"] == 0
            and effects["qualified_candidate_count"] == 0
            and effects["winner_selected"] is False,
            "keep a source-freeze contract distinct from the later real build",
        )
    elif key == "c_diagnostic_v5":
        base.need(
            document["schema"] == "rebar-owned-repaired-c-original-campaign-v5-source-freeze"
            and document["version"] == 5
            and document["status"]
            == "SOURCE FROZEN; ACTUAL C16 ORIGINAL CAMPAIGN NOT RUN"
            and document["source"]["sha256"] == spec["source"][1]
            and document["protocol"]["sha256"] == spec["protocol"][1]
            and document["expanded_holdout_proposal_case_count"] == 14155776
            and document["candidate_correctness"] == "NOT MEASURED"
            and document["runtime_non_delegation"] == "NOT ESTABLISHED"
            and document["qualified_candidate_count"] == 0
            and document["winner_selected"] is False,
            "reject any fabricated successful or timed C matching campaign",
        )
    else:
        base.need(False, "reject an unknown or unfrozen V87 feature")


def load_features(base: types.ModuleType) -> tuple[dict, dict]:
    documents: dict[str, dict] = {}
    source_bytes: dict[str, dict[str, bytes]] = {}
    unique: set[str] = set()
    for key, _, roles in FEATURES:
        source_bytes[key] = {}
        for role, item in roles.items():
            base.need(
                item[0] not in unique,
                "reject a duplicated feature evidence owner: " + item[0],
            )
            unique.add(item[0])
            source_bytes[key][role] = read_fixed(item, key + ":" + role)
        raw = source_bytes[key]["contract"]
        document = base.document(
            raw,
            "complete authentic " + key + " contract",
            exact=key != "expanded_holdout_v1",
        )
        validate_contract(base, key, document, raw)
        documents[key] = document
    base.need(len(unique) == 20, "authenticate exactly 20 distinct source owners")
    predecessor = read_fixed(PREDECESSOR, "authentic complete Rust V19 bridge")
    literal_raw = source_bytes["rust_literal_v1"]["variant"]
    literal = feature_constants(
        source_bytes["rust_literal_v1"]["source"],
        frozenset({"FUNCTION_START", "FUNCTION_FOLLOW", "ORIGINAL_FUNCTION", "ONE_PASS_FUNCTION"}),
    )
    verify_single_function(
        base, predecessor, literal_raw, literal,
        "ORIGINAL_FUNCTION", "ONE_PASS_FUNCTION", "Rust literal search",
    )
    one_pass = literal["ONE_PASS_FUNCTION"]
    base.need(
        one_pass.count(b"memmem(") == 1
        and one_pass.count(b"PyUnicode_Find(") == 1
        and one_pass.count(b"PyUnicode_FindChar(") == 1
        and b"PyUnicode_Count(" not in one_pass
        and one_pass.count(b"rust_subject_open(") == 1
        and one_pass.count(b"rust_findall_item(") == 1
        and one_pass.count(b"rust_list_append_owned(") == 1,
        "preserve the exact first-party one-pass literal engine and ownership",
    )
    captured = feature_constants(
        source_bytes["rust_captured_v1"]["source"],
        frozenset({"FUNCTION_START", "FUNCTION_FOLLOW", "ORIGINAL_FUNCTION", "CAPTURE_FUNCTION"}),
    )
    verify_single_function(
        base, literal_raw, source_bytes["rust_captured_v1"]["variant"], captured,
        "ORIGINAL_FUNCTION", "CAPTURE_FUNCTION", "Rust two-capture findall",
    )
    base.need(
        b"rust_list_append_owned(" in captured["CAPTURE_FUNCTION"]
        and b"PyTuple_New(2)" in captured["CAPTURE_FUNCTION"]
        and literal["ONE_PASS_FUNCTION"]
        in source_bytes["rust_captured_v1"]["variant"],
        "retain the unbuilt first-party capture change and exact one-pass ancestor",
    )
    return documents, source_bytes


def make_source_proof(base: types.ModuleType, key: str, document: dict) -> dict:
    _, label, roles = FEATURE_BY_KEY[key]
    proof = {
        "schema": SOURCE_PROOF_SCHEMA,
        "proof_key": key,
        "label": label,
        "complete_feature_contract": copy.deepcopy(document),
        "authenticated_source_owners": {
            role: base.synthetic_owner(item[:3], item[3])
            for role, item in roles.items()
        },
        "new_distinct_source_owner_count": len(roles),
    }
    if key == "expanded_holdout_v1":
        proof["complete_pretty_printed_contract_source"] = (
            base.json.dumps(document, indent=2) + "\n"
        )
    return proof


def make_source_pool(base: types.ModuleType, documents: dict) -> dict:
    entries: dict[str, dict] = {}
    for key, _, _ in FEATURES:
        proof = make_source_proof(base, key, documents[key])
        raw = base.canonical(proof)
        digest = base.digest(raw)
        base.need(digest not in entries, "reject a duplicate V87 source proof")
        entries[digest] = {
            "proof_key": key,
            "proof_schema": SOURCE_PROOF_SCHEMA,
            "canonical_sha256": digest,
            "canonical_bytes": len(raw),
            "complete_proof": proof,
        }
    pool = {
        "schema": SOURCE_POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": entries,
    }
    validate_source_pool(base, pool, documents)
    return pool


def validate_source_pool(base: types.ModuleType, pool: object, documents: dict) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == SOURCE_POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == len(FEATURES),
        "require one and only one complete canonical proof of every frozen feature",
    )
    assert isinstance(pool, dict)
    seen: set[str] = set()
    for digest, entry in pool["entries"].items():
        base.need(
            type(entry) is dict
            and set(entry) == {
                "proof_key", "proof_schema", "canonical_sha256",
                "canonical_bytes", "complete_proof",
            }
            and entry["proof_key"] in FEATURE_BY_KEY
            and entry["proof_key"] not in seen
            and entry["proof_schema"] == SOURCE_PROOF_SCHEMA
            and entry["canonical_sha256"] == digest
            and base.checked(digest, "complete V87 source evidence") == digest,
            "reject omitted, duplicated, foreign, or substituted V87 source proofs",
        )
        key = entry["proof_key"]
        expected = make_source_proof(base, key, documents[key])
        raw = base.canonical(expected)
        base.need(
            entry["canonical_bytes"] == len(raw)
            and base.digest(raw) == digest
            and base.canonical(entry["complete_proof"]) == raw,
            "recover every byte of the independently owned full proof: " + key,
        )
        seen.add(key)
    base.need(seen == set(FEATURE_BY_KEY), "retain all six whole source contracts")


def make_source_reference(base: types.ModuleType, pool: dict, key: str) -> dict:
    for digest, entry in pool["entries"].items():
        if entry["proof_key"] == key:
            return {
                "schema": SOURCE_REFERENCE_SCHEMA,
                "proof_key": key,
                "sha256": digest,
                "canonical_bytes": entry["canonical_bytes"],
            }
    base.need(False, "reject a missing whole source evidence reference: " + key)
    raise AssertionError("unreachable")


def resolve_source_reference(
    base: types.ModuleType, pool: dict, reference: object, key: str
) -> dict:
    base.need(
        key in FEATURE_BY_KEY
        and type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == SOURCE_REFERENCE_SCHEMA
        and reference["proof_key"] == key
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject a missing or swapped complete V87 source reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "complete V87 source reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == key
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"],
        "reject a fabricated V87 source proof digest",
    )
    proof = entry["complete_proof"]
    raw = base.canonical(proof)
    base.need(
        base.digest(raw) == digest
        and len(raw) == reference["canonical_bytes"]
        and proof.get("schema") == SOURCE_PROOF_SCHEMA,
        "reconstruct every byte of the frozen source proof: " + key,
    )
    return copy.deepcopy(proof)


def validate_actual_receipts(
    base: types.ModuleType, build: object, provenance: object
) -> None:
    base.need(
        type(build) is dict and len(build) == 60
        and type(provenance) is dict and len(provenance) == 62,
        "reject incomplete genuine V20 native-build publication receipts",
    )
    assert isinstance(build, dict) and isinstance(provenance, dict)
    v20 = FEATURE_BY_KEY["rust_build_v20"][2]
    literal = FEATURE_BY_KEY["rust_literal_v1"][2]
    proposal = FEATURE_BY_KEY["expanded_holdout_v1"][2]
    for name, receipt, schema in (
        (
            "publication", build,
            "rebar-phase2-owned-rust-literal-findall-source-build-v20-"
            "durable-publication-receipt",
        ),
        (
            "root provenance", provenance,
            "rebar-phase2-owned-rust-literal-findall-source-build-v20-"
            "durable-root-provenance-receipt",
        ),
    ):
        base.need(
            receipt["schema"] == schema
            and receipt["status"] == "PASS"
            and receipt["family"] == "rust"
            and receipt["label"]
            == "phase2-v20-rust-literal-findall-root-provenance"
            and receipt["source_sha256"] == v20["source"][1]
            and receipt["protocol_sha256"] == v20["protocol"][1]
            and receipt["contract_sha256"] == v20["contract"][1]
            and receipt["actual_compiler_process_count"] == 28
            and receipt["candidate_correctness"] == "NOT MEASURED"
            and receipt["candidate_matching"] == "NOT RUN"
            and receipt["candidate_qualified"] is False
            and receipt["candidate_workers_started"] == 0
            and receipt["native_libraries_loaded"] == 0
            and receipt["clock_samples"] == 0
            and receipt["holdout"] == "NOT OPENED"
            and receipt["performance"] == "NOT MEASURED"
            and receipt["memory"] == "NOT MEASURED"
            and receipt["undefined_behavior"] == "NOT MEASURED"
            and receipt["winner_selected"] is False,
            "reject a missing, fabricated, or qualifying V20 " + name + " receipt",
        )
    base.need(
        build["build_status"] == "PASS"
        and build["expected_actual_compiler_process_count"] == 28
        and build["candidate_imports"] == 0
        and build["candidate_processes_started"] == 0
        and build["hidden_cases_read"] == 0
        and build["timing_trials_run"] == 0
        and build["combined_bridge_sha256"] == literal["variant"][1]
        and build["combined_bridge_bytes"] == literal["variant"][2]
        and build["archive_relative"] == ARCHIVE_PATH
        and build["archive_sha256"] == ARCHIVE_SHA256
        and build["archive_bytes"] == 108498
        and build["global_evidence_owner_census"] == "NOT MEASURED"
        and build["global_history_reference_census"] == "NOT MEASURED"
        and build["prepublication_evidence_owner_lower_bound"] == 277
        and build["prepublication_history_reference_lower_bound"] == 282
        and build["new_actual_evidence_owner_count"] == 2
        and build["evidence_owner_lower_bound_after_publication"] == 279
        and build["history_reference_lower_bound_after_publication"] == 284,
        "preserve historical lower-bound semantics and actual V20 literal source",
    )
    base.need(
        provenance["version"] == 20
        and provenance["actual_source_phase_count"] == 2
        and provenance["expected_compiler_process_count"] == 28
        and provenance["canonical_build_status"] == "PASS"
        and provenance["canonical_build_receipt_relative"] == BUILD_RECEIPT[0]
        and provenance["canonical_build_receipt_sha256"] == BUILD_RECEIPT[1]
        and provenance["canonical_build_receipt_bytes"] == BUILD_RECEIPT[2]
        and provenance["canonical_build_receipt_device"] == 2064
        and provenance["canonical_build_receipt_inode"] == BUILD_RECEIPT[3]
        and provenance["canonical_build_archive_relative"] == ARCHIVE_PATH
        and provenance["canonical_build_archive_sha256"] == ARCHIVE_SHA256
        and provenance["canonical_build_archive_bytes"] == 108498
        and provenance["canonical_build_archive_opened"] is False
        and provenance["one_pass_literal_bridge_sha256"] == literal["variant"][1]
        and provenance["one_pass_literal_bridge_bytes"] == literal["variant"][2]
        and provenance["previous_bridge_sha256"] == PREDECESSOR[1]
        and provenance["previous_bridge_bytes"] == PREDECESSOR[2]
        and provenance["frozen_graph_version"] == 86
        and provenance["frozen_graph_summary_sha256"] == V86["summary"][1]
        and provenance["expanded_holdout_proposal_case_count"] == 14155776
        and provenance["expanded_holdout_proposal_source_sha256"]
        == proposal["source"][1]
        and provenance["expanded_holdout_proposal_protocol_sha256"]
        == proposal["protocol"][1]
        and provenance["expanded_holdout_proposal_contract_sha256"]
        == proposal["contract"][1]
        and provenance["expanded_holdout_cases_generated"] == 0
        and provenance["expanded_holdout_cases_opened"] == 0
        and provenance["historical_archives_opened"] == 0
        and provenance["tmp_directory_scanned"] is False,
        "authenticate actual private-root provenance solely from public receipt",
    )
    private = provenance["root"]
    base.need(
        type(private) is dict
        and private["phase_count"] == 2
        and private["device"] == 2049
        and private["mode"] == "0700"
        and private["directory_scanned"] is False
        and private["nofollow_directory_descriptor"] is True
        and type(private["phases"]) is list
        and len(private["phases"]) == 2,
        "preserve genuine root metadata without opening the private build root",
    )
    for phase, expected in zip(
        private["phases"], ("reference-a", "reference-b"), strict=True
    ):
        base.need(
            phase["name"] == expected and len(phase["native_outputs"]) == 2,
            "preserve both genuine independent first-party build phases",
        )
        roles = {item["role"]: item for item in phase["native_outputs"]}
        base.need(
            set(roles) == {"engine", "bridge"}
            and roles["engine"]["sha256"] == ENGINE_SHA256
            and roles["engine"]["bytes"] == 658344
            and roles["bridge"]["sha256"] == NATIVE_BRIDGE_SHA256
            and roles["bridge"]["bytes"] == 148792
            and roles["engine"]["native_loaded"] is False
            and roles["bridge"]["native_loaded"] is False,
            "retain genuine actual first-party native artifacts from receipts only",
        )


def make_actual_proof(base: types.ModuleType, build: dict, root: dict) -> dict:
    return {
        "schema": SCHEMA + "-complete-actual-rust-literal-build-v20",
        "version": 20,
        "complete_public_build_receipt": copy.deepcopy(build),
        "complete_public_root_provenance_receipt": copy.deepcopy(root),
        "build_receipt_owner": base.synthetic_owner(
            BUILD_RECEIPT[:3], BUILD_RECEIPT[3]
        ),
        "root_provenance_receipt_owner": base.synthetic_owner(
            ROOT_RECEIPT[:3], ROOT_RECEIPT[3]
        ),
        "actual_independent_phase_count": 2,
        "actual_compiler_process_count": 28,
        "actual_engine_sha256": ENGINE_SHA256,
        "actual_engine_bytes": 658344,
        "actual_bridge_sha256": NATIVE_BRIDGE_SHA256,
        "actual_bridge_bytes": 148792,
        "compiled_literal_variant_sha256": FEATURES[0][2]["variant"][1],
        "captured_variant_built": False,
        "compressed_archive_opened_by_graph": False,
        "private_root_opened_by_graph": False,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def make_actual_pool(base: types.ModuleType, proof: dict) -> dict:
    raw = base.canonical(proof)
    digest = base.digest(raw)
    pool = {
        "schema": ACTUAL_POOL_SCHEMA,
        "version": 1,
        "hash_algorithm": "sha256",
        "entries": {
            digest: {
                "proof_key": ACTUAL_KEY,
                "proof_schema": proof["schema"],
                "canonical_sha256": digest,
                "canonical_bytes": len(raw),
                "complete_proof": copy.deepcopy(proof),
            }
        },
    }
    validate_actual_pool(base, pool, proof)
    return pool


def validate_actual_pool(base: types.ModuleType, pool: object, proof: dict) -> None:
    base.need(
        type(pool) is dict
        and set(pool) == {"schema", "version", "hash_algorithm", "entries"}
        and pool["schema"] == ACTUAL_POOL_SCHEMA
        and pool["version"] == 1
        and pool["hash_algorithm"] == "sha256"
        and type(pool["entries"]) is dict
        and len(pool["entries"]) == 1,
        "require exactly one complete actual V20 build evidence owner",
    )
    assert isinstance(pool, dict)
    digest, entry = next(iter(pool["entries"].items()))
    raw = base.canonical(proof)
    base.need(
        type(entry) is dict
        and set(entry) == {
            "proof_key", "proof_schema", "canonical_sha256",
            "canonical_bytes", "complete_proof",
        }
        and entry["proof_key"] == ACTUAL_KEY
        and entry["proof_schema"] == proof["schema"]
        and entry["canonical_sha256"] == digest
        and base.checked(digest, "whole V20 actual evidence") == base.digest(raw)
        and entry["canonical_bytes"] == len(raw)
        and base.canonical(entry["complete_proof"]) == raw,
        "retain both complete real V20 receipts once without opening an archive",
    )


def make_actual_reference(base: types.ModuleType, pool: dict, proof: dict) -> dict:
    validate_actual_pool(base, pool, proof)
    raw = base.canonical(proof)
    return {
        "schema": ACTUAL_REFERENCE_SCHEMA,
        "proof_key": ACTUAL_KEY,
        "sha256": base.digest(raw),
        "canonical_bytes": len(raw),
    }


def resolve_actual_reference(
    base: types.ModuleType, pool: dict, reference: object
) -> dict:
    base.need(
        type(reference) is dict
        and set(reference) == {"schema", "proof_key", "sha256", "canonical_bytes"}
        and reference["schema"] == ACTUAL_REFERENCE_SCHEMA
        and reference["proof_key"] == ACTUAL_KEY
        and type(reference["canonical_bytes"]) is int
        and reference["canonical_bytes"] > 0,
        "reject a fabricated or missing whole actual V20 build reference",
    )
    assert isinstance(reference, dict)
    digest = base.checked(reference["sha256"], "whole V20 actual reference")
    entry = pool["entries"].get(digest)
    base.need(
        type(entry) is dict
        and entry.get("proof_key") == ACTUAL_KEY
        and entry.get("canonical_sha256") == digest
        and entry.get("canonical_bytes") == reference["canonical_bytes"],
        "reject swapped full V20 native-build evidence",
    )
    proof = entry["complete_proof"]
    raw = base.canonical(proof)
    base.need(
        len(raw) == reference["canonical_bytes"]
        and base.digest(raw) == digest,
        "reauthenticate both complete actual V20 receipts",
    )
    return copy.deepcopy(proof)


def make_svg() -> bytes:
    rows = (
        ("Python re", "The unchanged Python 3.14.6 reference", "BASELINE", "#34d399"),
        (
            "Rust",
            "8 of 13 groups passed; 5 failed. New literal engine built twice.",
            "BUILD PASS; TESTS FAIL",
            "#fbbf24",
        ),
        ("C", "1,230 observed differences from Python", "NOT COMPATIBLE", "#fb7185"),
        (
            "Zig",
            "1,764 observed differences; own engine also built twice",
            "NOT COMPATIBLE",
            "#fb7185",
        ),
        ("C++", "2,308 differences and five startup failures", "NOT COMPATIBLE", "#fb7185"),
        ("Go", "4,518 differences and four startup failures", "NOT COMPATIBLE", "#fb7185"),
        (
            "Fortran",
            "Built twice; the outputs disagree. Matching not measured.",
            "BUILD FAILED",
            "#fb7185",
        ),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="838" viewBox="0 0 1300 838" role="img" aria-labelledby="title description">',
        '<title id="title">Can a from-scratch replacement beat Python re?</title>',
        '<desc id="description">Unmodified Python is compared with six independently written regular-expression engines. None is fully compatible and no speed has been measured. The first-party Rust literal engine really built in two offline phases using 28 compiler and inspection steps, but the latest complete compatibility attempt still finished only 8 of 13 groups with 12,942 explicitly verified checks and five genuine failures. The newer captured-search variant is not built. Fortran was built twice, produced different native outputs and failed reproducibility. The 14,155,776-case final comparison is only a proposal: it has not been frozen, generated, opened or run.</desc>',
        '<rect width="1300" height="838" rx="20" fill="#0b1220"/>',
        '<text x="38" y="52" fill="#f8fafc" font-size="27" font-family="system-ui,sans-serif" font-weight="700">Building a faster Python re, from scratch</text>',
        '<text x="38" y="87" fill="#cbd5e1" font-size="17" font-family="system-ui,sans-serif">6 independent engines · 0 fully compatible · speed NOT MEASURED</text>',
        '<line x1="38" y1="109" x2="1262" y2="109" stroke="#334155"/>',
    ]
    for index, (name, detail, outcome, color) in enumerate(rows):
        y = 149 + index * 51
        parts.extend((
            f'<circle cx="48" cy="{y - 5}" r="6" fill="{color}"/>',
            f'<text x="66" y="{y}" fill="#f8fafc" font-size="16" font-family="system-ui,sans-serif" font-weight="650">{name}</text>',
            f'<text x="172" y="{y}" fill="#cbd5e1" font-size="14" font-family="system-ui,sans-serif">{detail}</text>',
            f'<text x="1248" y="{y}" text-anchor="end" fill="{color}" font-size="12" font-family="system-ui,sans-serif" font-weight="700">{outcome}</text>',
        ))
    parts.extend((
        '<line x1="38" y1="495" x2="1262" y2="495" stroke="#334155"/>',
        '<text x="38" y="529" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Compatibility: 31,237 original Python checks; 8,244 additional checks are counted separately.</text>',
        '<text x="38" y="560" fill="#fcd34d" font-size="14" font-family="system-ui,sans-serif">Rust: 12,942 verified original checks; 8 of 13 groups finished; 5 genuine failures.</text>',
        '<text x="38" y="590" fill="#93c5fd" font-size="14" font-family="system-ui,sans-serif">Rust literal engine: actually built twice using 28 first-party build steps. Build success is not a test pass.</text>',
        '<text x="38" y="620" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">New grouped-findall Rust source: not built, not tested, and not timed.</text>',
        '<text x="38" y="650" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Fortran: two actual builds disagreed. Its reproducibility failed; matching remains not measured.</text>',
        '<text x="38" y="680" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">No wrapped regex package, Python matcher, cross-engine fallback, or selected winner.</text>',
        '<text x="38" y="714" fill="#f8fafc" font-size="15" font-family="system-ui,sans-serif" font-weight="650">Planned final comparison: 14,155,776 cases.</text>',
        '<text x="38" y="744" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">Not frozen, not generated, not opened, and not run. Speed, memory, and confidence: NOT MEASURED.</text>',
        '<text x="38" y="774" fill="#cbd5e1" font-size="13" font-family="system-ui,sans-serif">The previous 4,194,304-case proposal is preserved only as historical evidence.</text>',
        '<text x="38" y="815" fill="#94a3b8" font-size="12" font-family="system-ui,sans-serif">Overview 87 · complete independently verifiable historical evidence · no winner.</text>',
        '</svg>',
        '',
    ))
    return "\n".join(parts).encode("utf-8")


def make_changes(source_refs: dict, actual_reference: dict) -> dict:
    return {
        "actual_current_graph_predecessor_version": 86,
        "authenticated_evidence_owner_lower_bound": 299,
        "authenticated_history_reference_lower_bound": 304,
        "v87_new_directly_authenticated_source_owner_count": 20,
        "v87_new_directly_authenticated_plaintext_build_owner_count": 2,
        "v87_new_source_experiment_count": 6,
        "expanded_holdout_proposal_status": "PRE-PHASE-3 PROPOSAL",
        "expanded_holdout_proposed_case_count": 14155776,
        "expanded_holdout_final_protocol_status": "NOT FROZEN",
        "expanded_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "preserved_previous_holdout_proposal_case_count": 4194304,
        "rust_literal_v20_actual_build_status": "PASS",
        "rust_literal_v20_actual_independent_phase_count": 2,
        "rust_literal_v20_actual_compiler_process_count": 28,
        "rust_literal_v20_actual_engine_sha256": ENGINE_SHA256,
        "rust_literal_v20_actual_native_bridge_sha256": NATIVE_BRIDGE_SHA256,
        "rust_literal_v20_actual_literal_variant_sha256": FEATURES[0][2]["variant"][1],
        "rust_literal_v20_candidate_matching": "NOT RUN",
        "rust_literal_v20_candidate_qualified": False,
        "rust_captured_findall_variant_build": "NOT RUN",
        "rust_captured_findall_variant_matching": "NOT RUN",
        "rust_captured_findall_historical_public_case_count": 48,
        "rust_captured_findall_historical_nonempty_case_count": 44,
        "rust_captured_findall_historical_empty_case_count": 4,
        "rust_captured_findall_variant_performance": "NOT MEASURED",
        "compressed_v20_archive_opened_by_graph": False,
        "private_v20_build_root_opened_by_graph": False,
        "global_evidence_owner_census": "NOT MEASURED",
        "global_history_reference_census": "NOT MEASURED",
        **copy.deepcopy(source_refs),
        ACTUAL_KEY: copy.deepcopy(actual_reference),
    }


def validate_new_families(
    base: types.ModuleType,
    v83: types.ModuleType,
    old: dict,
    families: object,
    source_pool: dict,
    source_documents: dict,
    actual_pool: dict,
    actual_proof: dict,
) -> None:
    base.need(
        type(families) is list and len(families) == 7,
        "reject an omitted baseline or independently written candidate family",
    )
    assert isinstance(families, list)
    for row, original in zip(families, old["families"], strict=True):
        base.need(
            type(row) is dict and row.get("family") == original["family"],
            "reject a swapped or duplicated first-party candidate family",
        )
        if row["family"] == "python":
            base.need(
                base.canonical(row) == base.canonical(original),
                "retain every byte of the genuine CPython baseline",
            )
            continue
        for proof_key in v83.PROOF_KEYS:
            base.need(
                base.canonical(row[proof_key])
                == base.canonical(original[proof_key]),
                "preserve all nine historical family references: " + proof_key,
            )
        for key, _, _ in FEATURES:
            proof = resolve_source_reference(base, source_pool, row.get(key), key)
            base.need(
                base.canonical(proof["complete_feature_contract"])
                == base.canonical(source_documents[key]),
                "resolve whole new feature in " + row["family"] + ":" + key,
            )
        observed = resolve_actual_reference(base, actual_pool, row.get(ACTUAL_KEY))
        base.need(
            base.canonical(observed) == base.canonical(actual_proof)
            and row["authenticated_evidence_owner_lower_bound"] == 299
            and row["authenticated_history_reference_lower_bound"] == 304
            and row["qualified"] is False
            and row["runtime_no_delegation"] == "NOT ESTABLISHED"
            and row["performance"] == "NOT MEASURED",
            "never qualify, benchmark, or replace real family outcomes",
        )
        restored = copy.deepcopy(row)
        for key, _, _ in FEATURES:
            restored.pop(key)
        restored.pop(ACTUAL_KEY)
        restored["authenticated_evidence_owner_lower_bound"] = original[
            "authenticated_evidence_owner_lower_bound"
        ]
        restored["authenticated_history_reference_lower_bound"] = original[
            "authenticated_history_reference_lower_bound"
        ]
        base.need(
            base.canonical(restored) == base.canonical(original),
            "restore every byte of the original V86 " + row["family"] + " row",
        )


def restore_historical_top(
    base: types.ModuleType, v83: types.ModuleType, summary: dict
) -> dict:
    restored: dict[str, dict] = {}
    pool = summary["lossless_family_evidence_pool"]
    for key in v83.PROOF_KEYS:
        restored[key] = v83.resolve_reference(base, pool, summary[key], key)
    return restored


def build(
    previous: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> tuple[dict, dict[str, bytes]]:
    base.need(
        options.source_sha256 is not None
        and type(options.source_bytes) is int
        and 0 < options.source_bytes <= OWNER_LIMIT,
        "caller-pin the complete stable V87 renderer source",
    )
    own, _ = base.read_owner(
        SELF,
        base.checked(options.source_sha256, "complete V87 renderer"),
        options.source_bytes,
        private=True,
    )
    for role, item in V86.items():
        base.need(
            getattr(options, "previous_" + role + "_sha256") == item[1],
            "caller-pin every complete authentic pushed V86 " + role,
        )
    for key, _, roles in FEATURES:
        for role, item in roles.items():
            base.need(
                getattr(options, key + "_" + role + "_sha256") == item[1],
                "caller-pin every current complete " + key + ":" + role,
            )
    base.need(
        options.build_receipt_sha256 == BUILD_RECEIPT[1]
        and options.root_receipt_sha256 == ROOT_RECEIPT[1],
        "caller-pin both genuine actual Rust V20 plaintext build receipts",
    )
    old, old_inputs = authenticate_previous(
        previous, v85, v84, v83, v82, chain, base
    )
    documents, _ = load_features(base)
    source_pool = make_source_pool(base, documents)
    source_refs = {
        key: make_source_reference(base, source_pool, key)
        for key, _, _ in FEATURES
    }
    build_raw = read_fixed(BUILD_RECEIPT, "actual whole V20 build receipt")
    root_raw = read_fixed(ROOT_RECEIPT, "actual whole V20 root receipt")
    actual_build = base.document(build_raw, "complete actual V20 build receipt")
    actual_root = base.document(root_raw, "complete actual V20 root receipt")
    validate_actual_receipts(base, actual_build, actual_root)
    actual_proof = make_actual_proof(base, actual_build, actual_root)
    actual_pool = make_actual_pool(base, actual_proof)
    actual_reference = make_actual_reference(base, actual_pool, actual_proof)
    changes = make_changes(source_refs, actual_reference)
    predecessor = {
        role: base.pin(item[0], item[1], item[2]) for role, item in V86.items()
    }
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(copy.deepcopy(changes))
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 87,
        "python": "3.14.6",
        "renderer": base.pin(SELF, options.source_sha256, len(own)),
        "previous_overview": predecessor,
        **copy.deepcopy(changes),
    })
    families = copy.deepcopy(old["families"])
    for row in families:
        if row["family"] == "python":
            continue
        row["authenticated_evidence_owner_lower_bound"] = 299
        row["authenticated_history_reference_lower_bound"] = 304
        row.update(copy.deepcopy(source_refs))
        row[ACTUAL_KEY] = copy.deepcopy(actual_reference)
    validate_new_families(
        base, v83, old, families, source_pool, documents, actual_pool, actual_proof
    )
    input_raw = base.canonical(inputs)
    svg_raw = make_svg()
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 87,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, options.source_sha256, len(own)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw)
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg_raw), len(svg_raw)),
        "previous_overview": predecessor,
        "snapshot": snapshot,
        "families": families,
        SOURCE_POOL_KEY: source_pool,
        "lossless_v87_source_evidence_pool_entry_count": len(FEATURES),
        "lossless_v87_source_references_per_family": len(FEATURES),
        ACTUAL_POOL_KEY: actual_pool,
        "lossless_v87_rust_actual_build_evidence_pool_entry_count": 1,
        "lossless_v87_rust_actual_build_references_per_family": 1,
        "lossless_v86_top_level_historical_proof_reference_count": len(
            v83.PROOF_KEYS
        ),
        "lossless_v86_top_level_reconstruction_status": "PASS",
        "lossless_v86_family_previous_byte_identity_status": "PASS",
        **copy.deepcopy(changes),
    })
    # V86 stored nine complete historical proofs both at the top level and
    # inside its immutable digest-addressed pool. Reference the existing pool
    # instead of copying those same complete bytes a second time. Every exact
    # historical document is reconstructed and checked below.
    for key in v83.PROOF_KEYS:
        summary[key] = v83.make_reference(
            base,
            old["lossless_family_evidence_pool"],
            old[key],
            key,
        )
    restored = restore_historical_top(base, v83, summary)
    for key in v83.PROOF_KEYS:
        base.need(
            base.canonical(restored[key]) == base.canonical(old[key]),
            "reconstruct the complete immutable V86 historical proof: " + key,
        )
    for pool_name in (
        "lossless_family_evidence_pool",
        "lossless_actual_outcome_evidence_pool",
        "lossless_zig_source_evidence_pool",
        "lossless_zig_actual_build_evidence_pool",
    ):
        base.need(
            base.canonical(summary[pool_name]) == base.canonical(old[pool_name]),
            "preserve every exact complete historical proof pool: " + pool_name,
        )
    for layer_name, layer in (
        ("summary", summary), ("snapshot", snapshot), ("inputs", inputs)
    ):
        base.need(
            layer["rust_v15_original_campaign_actual_worker_count"] == 13
            and layer["rust_v15_original_campaign_completed_suite_count"] == 8
            and layer["rust_v15_original_campaign_verified_passing_case_count"]
            == 12942
            and layer["rust_v15_original_campaign_infrastructure_failure_count"]
            == 5
            and layer["rust_v15_original_campaign_semantic_mismatch_count"]
            == "NOT MEASURED"
            and layer["expanded_holdout_proposed_case_count"] == 14155776
            and layer["expanded_holdout_final_protocol_status"] == "NOT FROZEN"
            and layer["expanded_holdout_case_status"]
            == "NOT GENERATED; NOT OPENED"
            and layer["rust_literal_v20_actual_build_status"] == "PASS"
            and layer["rust_literal_v20_actual_compiler_process_count"] == 28
            and layer["rust_literal_v20_candidate_matching"] == "NOT RUN"
            and layer["rust_literal_v20_candidate_qualified"] is False
            and layer["rust_captured_findall_variant_build"] == "NOT RUN"
            and layer["authenticated_evidence_owner_lower_bound"] == 299
            and layer["authenticated_history_reference_lower_bound"] == 304
            and layer["qualified_candidate_count"] == 0
            and layer["performance"] == "NOT MEASURED"
            and layer["final_holdout_opened"] is False,
            "retain actual results and unopened latest proposal in " + layer_name,
        )
        for key, _, _ in FEATURES:
            observed = resolve_source_reference(base, source_pool, layer[key], key)
            base.need(
                base.canonical(observed["complete_feature_contract"])
                == base.canonical(documents[key]),
                "retain full source reference in " + layer_name + ":" + key,
            )
        base.need(
            base.canonical(
                resolve_actual_reference(base, actual_pool, layer[ACTUAL_KEY])
            ) == base.canonical(actual_proof),
            "retain both complete actual build receipts in " + layer_name,
        )
    summary_raw = base.canonical(summary)
    assets = {
        OUTPUT + ".inputs.json": input_raw,
        OUTPUT + ".json": summary_raw,
        OUTPUT + ".svg": svg_raw,
    }
    for path, raw in assets.items():
        base.need(
            type(raw) is bytes and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
            "reject oversized complete V87 evidence BEFORE any publication: " + path,
        )
    return snapshot, assets


def self_test(
    previous: types.ModuleType,
    v85: types.ModuleType,
    v84: types.ModuleType,
    v83: types.ModuleType,
    v82: types.ModuleType,
    chain: tuple,
    base: types.ModuleType,
    options: argparse.Namespace,
) -> dict:
    inherited = previous.self_test(v85, v84, v83, v82, chain, base)
    base.need(
        inherited["status"] == "PASS"
        and inherited["version"] == 86
        and inherited["authenticated_evidence_owner_lower_bound"] == 277
        and inherited["authenticated_history_reference_lower_bound"] == 282
        and inherited["lossless_family_evidence_pool_entry_count"] == 9
        and inherited["lossless_actual_outcome_evidence_pool_entry_count"] == 1
        and inherited["lossless_zig_source_evidence_pool_entry_count"] == 1
        and inherited["lossless_zig_actual_build_evidence_pool_entry_count"] == 1
        and inherited["actual_v15_candidate_worker_count"] == 13
        and inherited["actual_v15_completed_suite_count"] == 8
        and inherited["actual_v15_verified_passing_case_count"] == 12942
        and inherited["actual_v15_infrastructure_failure_count"] == 5
        and inherited["qualified_candidate_count"] == 0
        and inherited["final_holdout_opened"] is False,
        "inherit the complete genuine V86 hostile controls and failed campaigns",
    )
    snapshot, assets = build(previous, v85, v84, v83, v82, chain, base, options)
    summary = base.document(assets[OUTPUT + ".json"], "complete in-memory V87")
    documents, sources = load_features(base)
    source_pool = summary[SOURCE_POOL_KEY]
    actual_pool = summary[ACTUAL_POOL_KEY]
    build_document = base.document(
        read_fixed(BUILD_RECEIPT, "complete V20 self-test receipt"),
        "actual V20 self-test build receipt",
    )
    root_document = base.document(
        read_fixed(ROOT_RECEIPT, "complete V20 self-test root receipt"),
        "actual V20 self-test root receipt",
    )
    rejected = 0

    def reject(label: str, callback: object) -> None:
        nonlocal rejected
        try:
            assert callable(callback)
            callback()
        except Exception:
            rejected += 1
        else:
            base.need(False, "V87 accepted fabricated evidence: " + label)

    for key, _, _ in FEATURES:
        raw = sources[key]["contract"]
        genuine = documents[key]
        for field in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(field)
            reject(
                "omitted complete contract " + key + ":" + field,
                lambda value=forged, role=key, original=raw: validate_contract(
                    base, role, value, original
                ),
            )
        reference = summary[key]
        for field, wrong in (
            ("schema", "invented-reference"),
            ("proof_key", "external-regex"),
            ("sha256", "0" * 64),
            ("canonical_bytes", 1),
        ):
            forged_reference = copy.deepcopy(reference)
            forged_reference[field] = wrong
            reject(
                "source proof reference " + key + ":" + field,
                lambda value=forged_reference, role=key: resolve_source_reference(
                    base, source_pool, value, role
                ),
            )
    for name, genuine, other in (
        ("build", build_document, root_document),
        ("root", root_document, build_document),
    ):
        for field in sorted(genuine):
            forged = copy.deepcopy(genuine)
            forged.pop(field)
            reject(
                "omitted actual " + name + " receipt field " + field,
                lambda value=forged, role=name, other_value=other:
                validate_actual_receipts(
                    base,
                    value if role == "build" else other_value,
                    value if role == "root" else other_value,
                ),
            )
        for field, wrong in (
            ("status", "FAIL"),
            ("source_sha256", "0" * 64),
            ("protocol_sha256", "0" * 64),
            ("contract_sha256", "0" * 64),
            ("actual_compiler_process_count", 27),
            ("candidate_matching", "PASS"),
            ("candidate_qualified", True),
            ("candidate_workers_started", 1),
            ("native_libraries_loaded", 1),
            ("clock_samples", 1),
            ("holdout", "OPENED"),
            ("performance", "1.5x"),
            ("winner_selected", True),
        ):
            forged = copy.deepcopy(genuine)
            forged[field] = wrong
            reject(
                "invented actual " + name + ":" + field,
                lambda value=forged, role=name, other_value=other:
                validate_actual_receipts(
                    base,
                    value if role == "build" else other_value,
                    value if role == "root" else other_value,
                ),
            )
    actual_reference = summary[ACTUAL_KEY]
    for field, wrong in (
        ("schema", "invented-actual"),
        ("proof_key", "captured-engine"),
        ("sha256", "0" * 64),
        ("canonical_bytes", 1),
    ):
        forged = copy.deepcopy(actual_reference)
        forged[field] = wrong
        reject(
            "invented actual build reference " + field,
            lambda value=forged: resolve_actual_reference(base, actual_pool, value),
        )
    control_old, _ = authenticate_previous(
        previous, v85, v84, v83, v82, chain, base
    )
    for index, original in enumerate(summary["families"]):
        if original["family"] == "python":
            continue
        for field, wrong in (
            ("qualified", True),
            ("runtime_no_delegation", "PASS"),
            ("performance", "1.5x"),
            ("authenticated_evidence_owner_lower_bound", 298),
            ("authenticated_history_reference_lower_bound", 305),
        ):
            forged_families = copy.deepcopy(summary["families"])
            forged_families[index][field] = wrong
            reject(
                "fabricated candidate " + original["family"] + ":" + field,
                lambda value=forged_families, prior=control_old: validate_new_families(
                    base, v83, prior, value, source_pool, documents, actual_pool,
                    make_actual_proof(base, build_document, root_document),
                ),
            )
    for event, arguments in (
        ("open", (str(ROOT / "secret.gz"), "rb", os.O_RDONLY)),
        ("open", (ARCHIVE_PATH, "rb", os.O_RDONLY)),
        ("open", ("/tmp/rebar-private-root", "rb", os.O_RDONLY)),
        ("open", (str(ROOT / (OUTPUT + ".json")), "rb", os.O_RDONLY)),
        ("open", (str(ROOT / "safe.json"), "wb", os.O_WRONLY | os.O_CREAT)),
        ("subprocess.Popen", ("candidate",)),
        ("ctypes.dlopen", ("foreign-regex.so",)),
        ("socket.connect", ("example.invalid",)),
        ("import", ("regex", None, None, None, None)),
        ("import", ("ctypes", None, None, None, None)),
        ("import", ("time", None, None, None, None)),
    ):
        reject(
            "forbidden source-only effect " + event,
            lambda operation=event, values=arguments: audit_wall(operation, values),
        )
    base.need(rejected >= 200, "require genuine lossless and hostile V87 controls")
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": 87,
        "status": "PASS",
        "source_sha256": options.source_sha256,
        "source_bytes": options.source_bytes,
        "inherited_rejected_hostile_control_count": inherited[
            "rejected_hostile_control_count"
        ],
        "new_rejected_hostile_control_count": rejected,
        "rejected_hostile_control_count": inherited[
            "rejected_hostile_control_count"
        ] + rejected,
        "summary_sha256": base.digest(assets[OUTPUT + ".json"]),
        "summary_bytes": len(assets[OUTPUT + ".json"]),
        "inputs_sha256": base.digest(assets[OUTPUT + ".inputs.json"]),
        "inputs_bytes": len(assets[OUTPUT + ".inputs.json"]),
        "svg_sha256": base.digest(assets[OUTPUT + ".svg"]),
        "svg_bytes": len(assets[OUTPUT + ".svg"]),
        "authenticated_evidence_owner_lower_bound": 299,
        "authenticated_history_reference_lower_bound": 304,
        "lossless_family_evidence_pool_entry_count": 9,
        "lossless_actual_outcome_evidence_pool_entry_count": 1,
        "lossless_zig_source_evidence_pool_entry_count": 1,
        "lossless_zig_actual_build_evidence_pool_entry_count": 1,
        "lossless_v87_source_evidence_pool_entry_count": 6,
        "lossless_v87_source_references_per_family": 6,
        "lossless_v87_rust_actual_build_evidence_pool_entry_count": 1,
        "lossless_v86_top_level_reconstruction_status": "PASS",
        "actual_v15_candidate_worker_count": 13,
        "actual_v15_completed_suite_count": 8,
        "actual_v15_verified_passing_case_count": 12942,
        "actual_v15_infrastructure_failure_count": 5,
        "actual_v20_build_status": "PASS",
        "actual_v20_compiler_process_count": 28,
        "actual_v20_independent_phase_count": 2,
        "actual_v20_candidate_matching": "NOT RUN",
        "captured_variant_native_build": "NOT RUN",
        "expanded_holdout_proposed_case_count": 14155776,
        "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "compressed_archives_opened_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "clock_samples_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "qualified_candidate_count": 0,
        "performance": "NOT MEASURED",
        "winner_selected": False,
        "outputs_written": False,
    }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg"}
        and type(raw) is bytes
        and 0 < len(raw) <= min(OWNER_LIMIT, base.OWNER_LIMIT),
        "publish only an explicitly authorized bounded complete V87 output",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            count = os.write(descriptor, remaining)
            base.need(type(count) is int and count > 0, "write every V87 output byte")
            remaining = remaining[count:]
        os.fsync(descriptor)
        actual = os.fstat(descriptor)
        base.need(
            actual.st_uid == os.geteuid()
            and actual.st_dev == 2064
            and actual.st_nlink == 1
            and actual.st_size == len(raw)
            and stat.S_IMODE(actual.st_mode) == 0o600,
            "authenticate each exclusively created complete V87 output",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / "docs/evidence"),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    actual, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(actual == raw, "recheck every complete published V87 output byte")


def parse(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    for role in V86:
        parser.add_argument("--previous-" + role + "-sha256", required=True)
    for key, _, roles in FEATURES:
        for role in roles:
            parser.add_argument(
                "--" + key.replace("_", "-") + "-" + role + "-sha256",
                dest=key + "_" + role + "_sha256",
                required=True,
            )
    parser.add_argument("--build-receipt-sha256", required=True)
    parser.add_argument("--root-receipt-sha256", required=True)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse(arguments)
    try:
        previous, v85, v84, v83, v82, chain, base = load_previous()
        if not options.render:
            sys.addaudithook(audit_wall)
        if options.self_test:
            result = self_test(
                previous, v85, v84, v83, v82, chain, base, options
            )
        else:
            snapshot, assets = build(
                previous, v85, v84, v83, v82, chain, base, options
            )
            if options.render:
                for path, raw in assets.items():
                    publish(base, path, raw)
            result = {
                "schema": SCHEMA + (
                    "-published" if options.render else "-source-only-frozen-context"
                ),
                "version": 87,
                "status": "PASS",
                "source_sha256": options.source_sha256,
                "source_bytes": options.source_bytes,
                "inputs_sha256": base.digest(assets[OUTPUT + ".inputs.json"]),
                "inputs_bytes": len(assets[OUTPUT + ".inputs.json"]),
                "summary_sha256": base.digest(assets[OUTPUT + ".json"]),
                "summary_bytes": len(assets[OUTPUT + ".json"]),
                "svg_sha256": base.digest(assets[OUTPUT + ".svg"]),
                "svg_bytes": len(assets[OUTPUT + ".svg"]),
                "authenticated_evidence_owner_lower_bound": 299,
                "authenticated_history_reference_lower_bound": 304,
                "lossless_family_evidence_pool_entry_count": 9,
                "lossless_actual_outcome_evidence_pool_entry_count": 1,
                "lossless_zig_source_evidence_pool_entry_count": 1,
                "lossless_zig_actual_build_evidence_pool_entry_count": 1,
                "lossless_v87_source_evidence_pool_entry_count": 6,
                "lossless_v87_source_references_per_family": 6,
                "lossless_v87_rust_actual_build_evidence_pool_entry_count": 1,
                "lossless_v86_top_level_reconstruction_status": "PASS",
                "actual_v15_candidate_worker_count": 13,
                "actual_v15_completed_suite_count": 8,
                "actual_v15_verified_passing_case_count": 12942,
                "actual_v15_infrastructure_failure_count": 5,
                "actual_v20_build_status": "PASS",
                "actual_v20_compiler_process_count": 28,
                "actual_v20_independent_phase_count": 2,
                "actual_v20_candidate_matching": "NOT RUN",
                "captured_variant_native_build": "NOT RUN",
                "expanded_holdout_proposed_case_count": 14155776,
                "expanded_holdout_status": "NOT FROZEN; NOT GENERATED; NOT OPENED",
                "compressed_archives_opened_by_graph": 0,
                "private_build_roots_opened_by_graph": 0,
                "candidate_workers_started_by_graph": 0,
                "compiler_processes_started_by_graph": 0,
                "clock_samples_by_graph": 0,
                "hidden_cases_read_by_graph": 0,
                "qualified_candidate_count": 0,
                "performance": "NOT MEASURED",
                "winner_selected": False,
                "outputs_written": bool(options.render),
                "snapshot_holdout_case_count": snapshot[
                    "expanded_holdout_proposed_case_count"
                ],
            }
        sys.stdout.buffer.write(base.canonical(result))
        return 0
    except Exception as error:
        sys.stderr.write("current V87 overview rejected: " + str(error) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
