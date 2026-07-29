#!/usr/bin/env python3
"""Freeze a from-scratch C build with genuine, recoverable root provenance."""

from __future__ import annotations

import sys

if "re" in sys.modules or "_sre" in sys.modules or "regex" in sys.modules:
    raise SystemExit("a first-party C source freeze must not load a matcher")

import ast
import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
SCHEMA = "rebar-phase2-owned-c-subject-buffer-source-build-v18"
VERSION = 18
FAMILY = "c"
SOURCE_PATH = "tools/reproduce_owned_c_subject_buffer_source_build_v18.py"
PROTOCOL_PATH = "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V18.md"
CONTRACT_PATH = "oracle/phase2/c-subject-buffer-source-build-v18.json"
EVIDENCE_PATH = "oracle/phase2/evidence"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
MAX_OWNER_BYTES = 4 * 1024 * 1024
GRAPH_VERSION = 86
EVIDENCE_FLOOR = 277
HISTORY_FLOOR = 282
ROOT_PREFIX = "rebar-phase2-native-build-v8-c-"
BUILD_LABEL = "phase2-v18-c-subject-buffer-root-provenance"
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "build_c_extension",
    "extension_dynamic", "extension_symbols", "extension_sections",
    "extension_notes",
)
C_TOOLCHAINS = {
    "python": (
        PYTHON,
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32387816, "CPython 3.14.6", True,
    ),
    "python_header": (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "include/python3.14/Python.h",
        "e39aad93d70c3ea1a63b77ec5795ff59a5c177745aedace6f83bbf4275a20d9f",
        4399, "CPython 3.14.6", False,
    ),
    "python_patchlevel": (
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "include/python3.14/patchlevel.h",
        "1c61b149e1ce72a7f6328c58057970d37fcafb02bec805be071dc0ed4cf39a95",
        1773, "CPython 3.14.6", False,
    ),
    "gcc": (
        "/usr/bin/x86_64-linux-gnu-gcc-13",
        "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        1023032, "GCC 13", True,
    ),
    "readelf": (
        "/usr/bin/x86_64-linux-gnu-readelf",
        "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        789280, "GNU readelf", True,
    ),
}
QUALIFICATION_BLOCKERS = (
    "ORIGINAL_31237_CANDIDATE_GATE_NOT_PASSED",
    "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
    "PUBLIC_IMPORT_FAIL",
    "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
    "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
)


def owner(role: str, path: str, fingerprint: str, size: int,
          inode: int) -> tuple[object, ...]:
    return (role, path, fingerprint, size, DEVICE, inode)


GOAL = owner(
    "goal", "GOAL.md",
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
    3756, 31364044,
)
P0_V4 = {
    "source": owner(
        "phase1_v4_source", "tools/verify_owned_p0_completeness_v4.py",
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
        29094, 428927,
    ),
    "protocol": owner(
        "phase1_v4_protocol", "oracle/phase1/P0-COMPLETENESS-V4.md",
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
        4261, 524712,
    ),
    "contract": owner(
        "phase1_v4_contract", "oracle/phase1/p0-completeness-v4.json",
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
        34875, 524713,
    ),
}
PRODUCER_V5 = {
    "source": owner(
        "producer_v5_source", "tools/run_owned_six_family_original_p0_producer_v5.py",
        "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
        102286, 431370,
    ),
    "protocol": owner(
        "producer_v5_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
        "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
        5270, 524884,
    ),
    "contract": owner(
        "producer_v5_contract", "oracle/phase2/six-family-p0-producer-v5.json",
        "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
        21036, 524885,
    ),
}
C16 = {
    "source": owner(
        "c_v16_source", "tools/reproduce_owned_c_subject_buffer_source_build_v16.py",
        "655b1c72c66fe9bfd06d96c7daeca3d2eb4817a5e28fdbbd737bbfd59713aa90",
        79602, 430076,
    ),
    "protocol": owner(
        "c_v16_protocol", "oracle/phase2/C-SUBJECT-BUFFER-SOURCE-BUILD-V16.md",
        "19b9ef86be5ce0c77c0addc40cfdefbbfb05102adfdd7baa38b39d62b08497a9",
        4778, 524731,
    ),
    "contract": owner(
        "c_v16_contract", "oracle/phase2/c-subject-buffer-source-build-v16.json",
        "7ea6bbe9a72a95e905e21cd1c45ac9a5b25620980f40d1ea141163642142a3c7",
        12543, 524732,
    ),
}
CANONICAL_C = owner(
    "canonical_c_engine", "candidates/_vm_native.c",
    "bc937bdd3945a111d7929439dfd4a660a55b70593b19ee807c82325d9e6f1e55",
    218185, 428072,
)
C_ADAPTER = owner(
    "canonical_c_adapter", "candidates/vm_candidate.py",
    "b37d3e634b10c37ded2de3c59af9ef477e1d12125ab1b52cfc57915305ff7096",
    60707, 428074,
)
C_FEATURE = {
    "source": owner(
        "c_subject_feature_source", "tools/apply_owned_c_subject_buffer_ownership_v1.py",
        "8262295a9e84c5fa30fe4e83102236fbaa233c914fb0c570d5fce3cdaf8605d2",
        80090, 428938,
    ),
    "protocol": owner(
        "c_subject_feature_protocol", "oracle/phase2/C-SUBJECT-BUFFER-OWNERSHIP-V1.md",
        "997af2edeced019663886aa7e20873506e4b13ee361bf5ce8d533e3ad2ea7393",
        5527, 524724,
    ),
    "contract": owner(
        "c_subject_feature_contract", "oracle/phase2/c-subject-buffer-ownership-v1.json",
        "b2ef8b9f5f9c7262be0e639d17436d0e1e8637d5649741bf2aa1538ebef3eb6a",
        12435, 524726,
    ),
    "variant": owner(
        "c_subject_feature_variant",
        "candidates/c/variants/subject_buffer_ownership_v1/vm_native.c",
        "8131aea768a122308716b8a67903794aa03f2fed2e2022f53bb6aa7b7e10e962",
        222212, 524723,
    ),
}
GRAPH = {
    "source": owner(
        "v86_graph_source", "tools/render_candidate_current_overview_v86.py",
        "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d",
        75354, 431699,
    ),
    "inputs": owner(
        "v86_graph_inputs", "docs/evidence/candidate-current-overview-v86.inputs.json",
        "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c",
        1345744, 430944,
    ),
    "summary": owner(
        "v86_graph_summary", "docs/evidence/candidate-current-overview-v86.json",
        "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc",
        4128155, 431704,
    ),
    "svg": owner(
        "v86_graph_svg", "docs/evidence/candidate-current-overview-v86.svg",
        "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55",
        6214, 431705,
    ),
}
C16_RECEIPT = owner(
    "c_v16_actual_build_receipt",
    "oracle/phase2/evidence/native-source-build-v16-c-phase2-v16-c-"
    "subject-buffer-original-p0-publication-receipt.json",
    "16794f5b1487b76a909a176948f4bbac8ed3108768f3127e27c44f9f392ae3d6",
    2671, 524751,
)
RUST19 = {
    "source": owner(
        "rust_v19_source", "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py",
        "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c",
        88532, 430955,
    ),
    "protocol": owner(
        "rust_v19_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md",
        "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5",
        5808, 524752,
    ),
    "contract": owner(
        "rust_v19_contract", "oracle/phase2/rust-buffer-shape-source-build-v19.json",
        "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46",
        14975, 524753,
    ),
}
RUST19_BUILD_RECEIPT = owner(
    "rust_v19_actual_build_receipt",
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-"
    "rust-buffer-shape-root-provenance-publication-receipt.json",
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc",
    3486, 524773,
)
RUST19_ROOT_RECEIPT = owner(
    "rust_v19_actual_root_receipt",
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-"
    "rust-buffer-shape-root-provenance-root-provenance-receipt.json",
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99",
    4367, 524774,
)
RUST15_FAILURE = owner(
    "rust_v15_actual_failure_receipt",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v15-rust-"
    "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v15-"
    "failures-publication-receipt.json",
    "5b1cfdc72f88c3a847f65f5a06da77cd27557ca2c2306320b6c8d44a91e28578",
    18510, 525117,
)
FUZZ_REFERENCE = {
    "source": owner(
        "fuzz_v3_source", "tools/run_owned_differential_fuzz_reference_v3.py",
        "9367bf224996296a9c8a0e01040d0776b292984e1a8b7a6362c8e943c27438ac",
        43757, 432216,
    ),
    "protocol": owner(
        "fuzz_v3_protocol", "oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md",
        "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6",
        3929, 525081,
    ),
    "contract": owner(
        "fuzz_v3_contract", "oracle/phase1/p0-differential-fuzz-reference-v3.json",
        "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
        5288, 525082,
    ),
    "aggregate": owner(
        "fuzz_v3_actual_reference",
        "oracle/phase1/evidence/differential-fuzz-reference-v3-"
        "cpython-3146-two-worker-8244-v3/two-independent-reference-result.json",
        "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096",
        3658, 524707,
    ),
    "reference_a": owner(
        "fuzz_v3_reference_a",
        "oracle/phase1/evidence/differential-fuzz-reference-v3-"
        "cpython-3146-two-worker-8244-v3/reference-1.json",
        "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        270, 524693,
    ),
    "reference_b": owner(
        "fuzz_v3_reference_b",
        "oracle/phase1/evidence/differential-fuzz-reference-v3-"
        "cpython-3146-two-worker-8244-v3/reference-2.json",
        "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce",
        270, 524692,
    ),
}
PROPOSAL = {
    "source": owner(
        "expanded_proposal_source", "tools/verify_expanded_sealed_holdout_v1.py",
        "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309",
        27311, 428806,
    ),
    "protocol": owner(
        "expanded_proposal_protocol", "oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md",
        "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4",
        13237, 524760,
    ),
    "contract": owner(
        "expanded_proposal_contract", "oracle/phase3/expanded-sealed-holdout-v1.json",
        "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76",
        6628, 524761,
    ),
}
_ROOT_CAPTURE: dict[str, object] | None = None


class GateError(Exception):
    """Reject a borrowed source, false root, unsafe effect, or hidden holdout."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise GateError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash complete, first-party source bytes only")
    return hashlib.sha256(value).hexdigest()


def checked_hash(value: object, role: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "require an exact lowercase SHA-256: " + role)
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True
            and os.path.realpath(sys.executable) == PYTHON
            and os.path.abspath(__file__) == ROOT + "/" + SOURCE_PATH
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE_PATH
            and "re" not in sys.modules and "_sre" not in sys.modules
            and "regex" not in sys.modules
            and not any(name == "candidates" or name.startswith("candidates.")
                        for name in sys.modules),
            "require isolated CPython 3.14.6 without any imported matcher")


def bootstrap_rust19() -> dict[str, object]:
    row = RUST19["source"]
    role, relative, fingerprint, size, device, inode = row
    require(role == "rust_v19_source" and device == DEVICE
            and relative == "tools/reproduce_owned_rust_buffer_shape_source_build_v19.py"
            and not relative.startswith("/") and ".." not in relative.split("/")
            and type(size) is int and 0 < size <= MAX_OWNER_BYTES,
            "bootstrap only the committed matcher-free Rust V19 source kernel")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        first = os.fstat(descriptor)
        require(stat.S_ISREG(first.st_mode)
                and stat.S_IMODE(first.st_mode) == 0o600
                and first.st_uid == os.geteuid() and first.st_nlink == 1
                and (first.st_dev, first.st_ino, first.st_size)
                    == (device, inode, size),
                "reject an unsafe or substituted matcher-free V19 bootstrap")
        remaining = size
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(262144, remaining))
            require(type(block) is bytes and len(block) > 0,
                    "reject a truncated first-party V19 bootstrap")
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject extra first-party V19 bootstrap bytes")
        after = os.fstat(descriptor)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns, first.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject a changed or swapped first-party V19 bootstrap")
    finally:
        os.close(descriptor)
    raw = b"".join(blocks)
    require(digest(raw) == fingerprint,
            "reject the wrong first-party Rust V19 source digest")
    namespace: dict[str, object] = {
        "__name__": "_rebar_c_v18_matcher_free_v19_source_kernel",
        "__file__": ROOT + "/" + relative,
        "__package__": None,
    }
    exec(compile(raw, namespace["__file__"], "exec", dont_inherit=True),
         namespace)
    require(namespace.get("SCHEMA")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v19"
            and namespace.get("VERSION") == 19
            and namespace.get("PYTHON") == PYTHON
            and namespace.get("PYTHON_SHA256") == PYTHON_SHA256
            and callable(namespace.get("load_v18"))
            and "re" not in sys.modules and "_sre" not in sys.modules,
            "authenticate the genuine regex-free provenance and JSON kernel")
    base = namespace["load_v18"]()
    require(type(base) is dict
            and base.get("SCHEMA")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v18"
            and base.get("PYTHON") == PYTHON
            and base.get("PYTHON_SHA256") == PYTHON_SHA256
            and base.get("_WALL_ENABLED") is False,
            "derive only the independently frozen matcher-free audit kernel")
    rows: list[tuple[object, ...]] = [
        GOAL, CANONICAL_C, C_ADAPTER, C16_RECEIPT,
        RUST19_BUILD_RECEIPT, RUST19_ROOT_RECEIPT, RUST15_FAILURE,
    ]
    for group in (
        P0_V4, PRODUCER_V5, C16, C_FEATURE, GRAPH, RUST19,
        FUZZ_REFERENCE, PROPOSAL,
    ):
        rows.extend(group.values())
    allowed = {ROOT + "/" + SOURCE_PATH,
               ROOT + "/" + PROTOCOL_PATH,
               ROOT + "/" + CONTRACT_PATH}
    allowed.update(ROOT + "/" + row[1] for row in rows)
    require(len(allowed) == len(rows) + 3,
            "reject repeated or hidden first-party source-freeze owners")
    require(not any(
        path.endswith((".so", ".gz", ".xz", ".tar", ".zip", ".zst"))
        for path in allowed
    ), "never admit a native, archive, generated benchmark, or hidden holdout")
    base["_ALLOWLIST"] = frozenset(allowed)
    base["no_matching_imports"]()
    return base


def encoded(base: dict[str, object], value: object) -> bytes:
    return (base["canonical"](value) + "\n").encode("ascii")


def document(base: dict[str, object], raw: bytes, label: str,
             *, canonical_required: bool = True) -> dict[str, object]:
    value = base["StrictJSON"](raw).decode()
    require(type(value) is dict
            and (not canonical_required or encoded(base, value) == raw),
            "require complete, canonical, duplicate-free JSON: " + label)
    return value


def row_document(row: tuple[object, ...]) -> dict[str, object]:
    return {
        "path": row[1], "sha256": row[2], "bytes": row[3],
        "device": row[4], "inode": row[5], "mode": "0600", "nlink": 1,
    }


def public_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def row_group(rows: dict[str, tuple[object, ...]]) -> dict[str, object]:
    return {role: row_document(row) for role, row in sorted(rows.items())}


def planned_toolchains() -> list[dict[str, object]]:
    return [{
        "role": role,
        "path": item[0],
        "sha256": item[1],
        "bytes": item[2],
        "version": item[3],
        "executable": item[4],
        "verification_status": "NOT RUN; EXPLICIT BUILD ONLY",
    } for role, item in sorted(C_TOOLCHAINS.items())]


def boundary() -> dict[str, object]:
    return {
        "actual_candidate_workers": 0,
        "actual_compiler_process_count": 0,
        "actual_reference_workers": 0,
        "actual_root_descriptor_opens": 0,
        "archive_bytes_read": 0,
        "archive_inflations": 0,
        "archive_opens": 0,
        "benchmark_files_read": 0,
        "candidate_build": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_imports": 0,
        "candidate_matching": "NOT RUN",
        "candidate_processes_started": 0,
        "candidate_qualified": False,
        "canonical_source_mutations": 0,
        "clock_samples": 0,
        "compiler_processes_started": 0,
        "confidence_intervals": "NOT MEASURED",
        "final_holdout_case_count": "NOT GENERATED",
        "final_holdout_case_status": "NOT GENERATED; NOT OPENED",
        "final_holdout_protocol": "NOT FROZEN",
        "hidden_cases_read": 0,
        "holdout": "NOT OPENED",
        "memory": "NOT MEASURED",
        "native_activations": 0,
        "native_libraries_loaded": 0,
        "network_requests": 0,
        "performance": "NOT MEASURED",
        "private_root_path": "NOT MEASURED",
        "private_roots_created": 0,
        "proposed_final_holdout_case_count": 14155776,
        "published_graph_final_comparison_planned_case_count": 4194304,
        "qualified_candidate_count": 0,
        "root_provenance": "NOT MEASURED",
        "root_provenance_receipts_written": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "threads_started": 0,
        "toolchain_files_authenticated": 0,
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def validate_p0(value: dict[str, object]) -> None:
    gate = value.get("phase_gate")
    qualification = value.get("candidate_qualification_gate")
    require(value.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and value.get("version") == 4
            and value.get("original_case_execution_denominator") == 31237
            and value.get("original_suite_count") == 13
            and type(gate) is dict and gate.get("status") == "PASS"
            and gate.get("candidate_evaluation_authorized") is True
            and gate.get("native_build_authorized") is True
            and gate.get("final_holdout_authorized") is False
            and gate.get("performance_oracle_authorized") is False
            and gate.get("qualified_candidate_count") == 0
            and type(qualification) is dict
            and qualification.get("status") == "BLOCKED"
            and qualification.get("blockers") == list(QUALIFICATION_BLOCKERS)
            and qualification.get("final_holdout_opened") is False
            and qualification.get("qualified_candidate_count") == 0
            and qualification.get("runtime_no_delegation") == "NOT ESTABLISHED",
            "require actual passing phase-one readiness without candidate qualification")


def validate_producer(value: dict[str, object]) -> None:
    require(value.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
            and value.get("version") == 5
            and value.get("family_count") == 6
            and value.get("case_execution_denominator") == 31237
            and value.get("suite_count") == 13
            and value.get("named_private_waiver_count") == 13
            and value.get("supplemental_case_count") == 8244
            and value.get("supplemental_cases_counted_in_original_denominator") is False
            and value.get("qualified_candidate_count") == 0
            and value.get("holdout") == "NOT OPENED"
            and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and value.get("performance") == "NOT MEASURED"
            and value.get("winner_selected") is False,
            "preserve the current original producer and six independent families")


def validate_fuzz(value: dict[str, object]) -> None:
    workers = value.get("workers")
    require(value.get("schema")
            == "rebar-owned-differential-fuzz-reference-v3-actual-reference"
            and value.get("status") == "PASS"
            and value.get("corpus_sha256")
                == "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2"
            and type(workers) is list and len(workers) == 2
            and value.get("holdout") == "NOT OPENED"
            and value.get("performance") == "NOT MEASURED",
            "require both real separately published 8,244-case reference checks")
    identities: set[int] = set()
    for index, worker in enumerate(workers):
        expected = FUZZ_REFERENCE["reference_a" if index == 0 else "reference_b"]
        result = worker.get("result") if type(worker) is dict else None
        require(type(worker) is dict
                and worker.get("role")
                    == ("independent-reference-a" if index == 0
                        else "independent-reference-b")
                and type(worker.get("pid")) is int
                and worker["pid"] > 0 and worker["pid"] not in identities
                and worker.get("case_count") == 8244
                and worker.get("passed") == 8244
                and worker.get("failed") == 0
                and worker.get("exit_code") == 0
                and worker.get("module") == "re"
                and type(result) is dict
                and result.get("path") == ROOT + "/" + expected[1]
                and result.get("sha256") == expected[2]
                and result.get("bytes") == expected[3]
                and result.get("device") == expected[4]
                and result.get("inode") == expected[5],
                "preserve two distinct Python-reference processes, not candidate passes")
        identities.add(worker["pid"])


def validate_feature(value: dict[str, object]) -> None:
    complete = value.get("complete_first_party_c_variant")
    originals = value.get("original_first_party_c_owners")
    delegation = value.get("delegation_policy")
    owner_record = complete.get("owner") if type(complete) is dict else None
    require(value.get("schema") == "rebar-phase2-owned-c-subject-buffer-ownership-v1"
            and value.get("version") == 1 and value.get("family") == FAMILY
            and value.get("source")
                == {"path": C_FEATURE["source"][1],
                    "sha256": C_FEATURE["source"][2]}
            and value.get("protocol")
                == {"path": C_FEATURE["protocol"][1],
                    "sha256": C_FEATURE["protocol"][2]}
            and type(complete) is dict
            and complete.get("independent_parser_compiler_executor_and_engine") is True
            and complete.get("candidate_qualified") is False
            and owner_record == public_document(C_FEATURE["variant"])
            and type(originals) is dict
            and originals.get("combined_native_engine_and_python_bridge")
                == public_document(CANONICAL_C)
            and originals.get("unchanged_public_python_adapter")
                == public_document(C_ADAPTER)
            and originals.get("canonical_adapter_modified") is False
            and originals.get("canonical_engine_modified") is False
            and originals.get("canonical_native_loaded") is False
            and type(delegation) is dict
            and delegation.get("cpython_regular_expression_engine") == "FORBIDDEN"
            and delegation.get("external_regular_expression_packages") == "FORBIDDEN"
            and delegation.get("other_candidate_parser_compiler_executor_or_engine")
                == "FORBIDDEN"
            and delegation.get("candidate_fallback") == "FORBIDDEN"
            and delegation.get("hardcoded_oracle_answers") == "FORBIDDEN"
            and delegation.get("runtime_non_delegation") == "NOT ESTABLISHED",
            "authenticate the complete independently owned first-party C engine")


def validate_c16_contract(value: dict[str, object]) -> None:
    feature = value.get("owned_first_party_subject_buffer_feature")
    originals = value.get("canonical_c_source_owners")
    policy = value.get("future_build_policy")
    require(value.get("schema")
            == "rebar-phase2-owned-c-subject-buffer-source-build-v16-source-freeze"
            and value.get("version") == 16 and value.get("family") == FAMILY
            and value.get("source")
                == {"path": C16["source"][1], "sha256": C16["source"][2]}
            and value.get("protocol")
                == {"path": C16["protocol"][1], "sha256": C16["protocol"][2]}
            and type(feature) is dict
            and feature.get("complete_native_variant_sha256")
                == C_FEATURE["variant"][2]
            and feature.get("complete_native_variant_bytes")
                == C_FEATURE["variant"][3]
            and feature.get("derived_from_canonical_owned_c") is True
            and type(originals) is dict
            and originals.get("combined_native_source", {}).get("sha256")
                == CANONICAL_C[2]
            and originals.get("python_adapter", {}).get("sha256") == C_ADAPTER[2]
            and originals.get("original_source_modified") is False
            and originals.get("original_adapter_modified") is False
            and type(policy) is dict
            and policy.get("phase_names") == list(PHASES)
            and policy.get("phase_count") == 2
            and policy.get("process_names_per_phase") == list(PROCESS_NAMES)
            and policy.get("compiler_process_count_per_phase") == 7
            and policy.get("total_compiler_process_count") == 14
            and policy.get("private_root_prefix") == ROOT_PREFIX
            and policy.get("variant_source_sha256") == C_FEATURE["variant"][2]
            and policy.get("adapter_source_sha256") == C_ADAPTER[2]
            and policy.get("external_regex_engine") == "FORBIDDEN"
            and policy.get("stdlib_regex_engine") == "FORBIDDEN"
            and policy.get("cross_candidate_engine") == "FORBIDDEN"
            and policy.get("fallback") == "FORBIDDEN",
            "derive C V18 from the authenticated genuine C V16 build kernel")


def validate_c16_receipt(value: dict[str, object]) -> None:
    archive = value.get("archive_publication")
    require(value.get("schema")
            == "rebar-phase2-owned-c-subject-buffer-source-build-v16-"
               "durable-publication-receipt"
            and value.get("status") == "PASS"
            and value.get("build_status") == "PASS"
            and value.get("family") == FAMILY
            and value.get("source_sha256") == C16["source"][2]
            and value.get("protocol_sha256") == C16["protocol"][2]
            and value.get("contract_sha256") == C16["contract"][2]
            and value.get("expected_compiler_process_count") == 14
            and value.get("actual_compiler_process_count") == 14
            and value.get("variant_source_sha256") == C_FEATURE["variant"][2]
            and value.get("variant_source_bytes") == C_FEATURE["variant"][3]
            and value.get("original_source_sha256") == CANONICAL_C[2]
            and value.get("adapter_source_sha256") == C_ADAPTER[2]
            and type(archive) is dict
            and archive.get("sha256")
                == "45cf839dd4fcb7615d70af79bc38b4695911159b109c9a79fd1d7d037b338f55"
            and archive.get("bytes") == 37795
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and value.get("candidate_correctness") == "NOT MEASURED"
            and value.get("candidate_processes_started") == 0
            and value.get("native_libraries_loaded") == 0
            and value.get("holdout") == "NOT OPENED"
            and "root_provenance_status" not in value
            and "root" not in value,
            "preserve the actual 14-role C V16 build without inventing root provenance")


def validate_rust19_receipts(build: dict[str, object],
                             root: dict[str, object]) -> None:
    observed_root = root.get("root")
    require(build.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-"
               "durable-publication-receipt"
            and build.get("status") == "PASS"
            and build.get("build_status") == "PASS"
            and build.get("family") == "rust"
            and build.get("source_sha256") == RUST19["source"][2]
            and build.get("protocol_sha256") == RUST19["protocol"][2]
            and build.get("contract_sha256") == RUST19["contract"][2]
            and build.get("expected_actual_compiler_process_count") == 28
            and build.get("actual_compiler_process_count") == 28
            and build.get("candidate_matching") == "NOT RUN"
            and build.get("candidate_qualified") is False
            and build.get("holdout") == "NOT OPENED"
            and root.get("schema")
                == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-"
                   "durable-root-provenance-receipt"
            and root.get("status") == "PASS" and root.get("version") == 19
            and root.get("family") == "rust"
            and root.get("source_sha256") == RUST19["source"][2]
            and root.get("protocol_sha256") == RUST19["protocol"][2]
            and root.get("contract_sha256") == RUST19["contract"][2]
            and root.get("canonical_build_receipt_sha256")
                == RUST19_BUILD_RECEIPT[2]
            and root.get("actual_compiler_process_count") == 28
            and root.get("actual_source_phase_count") == 2
            and type(observed_root) is dict
            and observed_root.get("prefix") == "rebar-phase2-native-build-v9-rust-"
            and observed_root.get("mode") == "0700"
            and observed_root.get("phase_count") == 2
            and observed_root.get("nofollow_directory_descriptor") is True
            and observed_root.get("descriptor_opened_during_live_verification") is True
            and observed_root.get("directory_scanned") is False
            and root.get("candidate_matching") == "NOT RUN"
            and root.get("candidate_qualified") is False
            and root.get("holdout") == "NOT OPENED",
            "preserve the actual independently built Rust root using receipts only")


def validate_rust15_failure(value: dict[str, object]) -> None:
    require(value.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v15-"
               "durable-publication-receipt"
            and value.get("status") == "PASS"
            and value.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and value.get("family") == "rust"
            and value.get("candidate_status") == "FAIL"
            and value.get("suite_count") == 13
            and value.get("started_suite_count") == 13
            and value.get("completed_suite_count") == 8
            and value.get("infrastructure_failure_count") == 5
            and value.get("verified_passing_case_count") == 12942
            and value.get("semantic_mismatch_count") == "NOT MEASURED"
            and value.get("actual_candidate_workers") == 13
            and value.get("worker_failure_capture_count") == 5
            and value.get("holdout") == "NOT OPENED"
            and value.get("performance") == "NOT MEASURED"
            and value.get("winner_selected") is False,
            "preserve every actual latest Rust failure without inventing mismatches")


def validate_proposal(value: dict[str, object]) -> None:
    forbidden = value.get("prohibited_matcher_delegates")
    require(value.get("schema") == "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
            and value.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
            and value.get("final_protocol_status") == "NOT FROZEN"
            and value.get("generator_status") == "NOT FROZEN"
            and value.get("case_status") == "NOT GENERATED; NOT OPENED"
            and value.get("secret_status") == "NOT GENERATED"
            and value.get("timing_status") == "NOT RUN; NOT MEASURED"
            and value.get("memory_status") == "NOT RUN; NOT MEASURED"
            and value.get("winner_status") == "NOT SELECTED"
            and value.get("runtime_independence_status") == "NOT ESTABLISHED"
            and value.get("qualified_independent_family_count") == 0
            and value.get("minimum_qualified_independent_family_count") == 3
            and value.get("case_count") == 14155776
            and value.get("preserved_previous_proposal_case_count") == 4194304
            and value.get("operation_count") == 36
            and value.get("pattern_family_count") == 24
            and value.get("participant_count") == 4
            and value.get("paired_round_count") == 24
            and value.get("individually_correctness_gated_timed_observation_count")
                == 1358954496
            and type(forbidden) is list
            and {"stdlib_re", "stdlib__sre", "PCRE", "PCRE2", "RE2",
                 "Rust_regex", "another_candidate", "external_process_matcher",
                 "network_matcher", "cached_oracle_answers", "hidden_fallback"}
                <= set(forbidden),
            "preserve the 14,155,776-case proposal without generating or opening it")


def validate_graph(summary: dict[str, object], inputs: dict[str, object],
                   c_receipt: dict[str, object],
                   rust_failure: dict[str, object]) -> None:
    require(summary.get("schema")
            == "rebar-candidate-current-overview-v86-summary"
            and summary.get("version") == GRAPH_VERSION
            and summary.get("status") == "PASS"
            and inputs.get("schema")
                == "rebar-candidate-current-overview-v86-inputs"
            and inputs.get("version") == GRAPH_VERSION
            and summary.get("source") == public_document(GRAPH["source"])
            and summary.get("inputs") == public_document(GRAPH["inputs"])
            and summary.get("svg") == public_document(GRAPH["svg"]),
            "bind the four actual pushed V86 graph owners, never an obsolete graph")
    for observed in (summary, inputs):
        require(observed.get("actual_current_graph_predecessor_version") == 85
                and observed.get("authenticated_evidence_owner_lower_bound")
                    == EVIDENCE_FLOOR
                and observed.get("authenticated_history_reference_lower_bound")
                    == HISTORY_FLOOR
                and observed.get("full_case_denominator") == 31237
                and observed.get("suite_count") == 13
                and observed.get("private_waiver_count") == 13
                and observed.get("phase1_v4_oracle_readiness_status") == "PASS"
                and observed.get("candidate_qualification_status") == "BLOCKED"
                and observed.get("qualified_candidate_count") == 0
                and observed.get("actual_c_v4_original_campaign_status") == "FAIL"
                and observed.get("actual_c_semantic_mismatch_count") == 1230
                and observed.get("actual_c_verified_passing_case_count") == 7325
                and observed.get("c_native_build_v16_status") == "PASS"
                and observed.get("c_native_build_v16_compiler_process_count") == 14
                and observed.get("c_native_build_v16_matching_status") == "NOT RUN"
                and observed.get("c_native_build_v16_archive_opened_by_graph") is False
                and observed.get("rust_v15_original_campaign_candidate_matching")
                    == "FAIL"
                and observed.get("rust_v15_original_campaign_completed_suite_count")
                    == 8
                and observed.get("rust_v15_original_campaign_infrastructure_failure_count")
                    == 5
                and observed.get("rust_v15_original_campaign_verified_passing_case_count")
                    == 12942
                and observed.get("rust_v15_original_campaign_semantic_mismatch_count")
                    == "NOT MEASURED"
                and observed.get("rust_v15_original_campaign_actual_worker_count") == 13
                and observed.get("rust_v15_original_campaign_outcome_receipt_sha256")
                    == RUST15_FAILURE[2]
                and observed.get("rust_v15_original_campaign_underlying_original_failure_cause")
                    == "NOT ESTABLISHED"
                and observed.get("rust_v15_original_campaign_pattern_destructor_proven_failure_cause")
                    is False
                and observed.get("final_comparison_planned_case_count") == 4194304
                and observed.get("final_comparison_cases_generated") is False
                and observed.get("final_holdout_opened") is False
                and observed.get("runtime_no_delegation") == "NOT ESTABLISHED"
                and observed.get("performance") == "NOT MEASURED",
                "preserve genuine V86 results, losses, root limits, and unopened holdout")
    require(summary.get("candidate_qualification_blockers")
            == list(QUALIFICATION_BLOCKERS),
            "preserve all seven independent candidate-qualification blockers")
    observed_build = summary.get("c_native_build_v16_actual_build")
    observed_rust = summary.get("actual_rust_v15_original_campaign")
    require(type(observed_build) is dict
            and observed_build.get("complete_durable_publication_receipt") == c_receipt
            and type(observed_rust) is dict
            and observed_rust.get("candidate_status") == "FAIL"
            and observed_rust.get("completed_suite_count") == 8
            and observed_rust.get("infrastructure_failure_count") == 5
            and observed_rust.get("verified_passing_case_count") == 12942
            and observed_rust.get("semantic_mismatch_count") == "NOT MEASURED"
            and observed_rust.get("receipt_owner", {}).get("sha256")
                == RUST15_FAILURE[2]
            and observed_rust.get("publication_status") == "PASS"
            and observed_rust.get("publication_pass_means")
                == "DURABLE PUBLICATION ONLY"
            and rust_failure.get("candidate_status") == "FAIL",
            "bind the graph to complete genuine C and latest Rust failure receipts")


def collect_context(base: dict[str, object], source_pin: str,
                    protocol_pin: str, contract_pin: str | None = None
                    ) -> tuple[dict[str, object], dict[str, object]]:
    checked_hash(source_pin, "C V18 source")
    checked_hash(protocol_pin, "C V18 protocol")
    source_raw, source_info = base["read_self"](SOURCE_PATH, source_pin)
    protocol_raw, protocol_info = base["read_self"](PROTOCOL_PATH, protocol_pin)
    require(source_raw.endswith(b"\n") and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n")
            and not protocol_raw.endswith(b"\n\n"),
            "require complete first-party V18 source and protocol owners")
    base["read_exact"](GOAL)
    groups: dict[str, dict[str, bytes]] = {}
    for name, rows in (
        ("phase1", P0_V4), ("producer", PRODUCER_V5), ("c16", C16),
        ("feature", C_FEATURE), ("graph", GRAPH), ("rust19", RUST19),
        ("fuzz", FUZZ_REFERENCE), ("proposal", PROPOSAL),
    ):
        groups[name] = {role: base["read_exact"](row)
                        for role, row in rows.items()}
    original = base["read_exact"](CANONICAL_C)
    adapter = base["read_exact"](C_ADAPTER)
    validate_p0(document(base, groups["phase1"]["contract"], "frozen P0 V4"))
    validate_producer(document(base, groups["producer"]["contract"], "producer V5"))
    fuzz = document(base, groups["fuzz"]["aggregate"], "two actual fuzz references")
    validate_fuzz(fuzz)
    feature = document(base, groups["feature"]["contract"], "first-party C feature")
    validate_feature(feature)
    variant = groups["feature"]["variant"]
    require(digest(original) == CANONICAL_C[2]
            and digest(adapter) == C_ADAPTER[2]
            and digest(variant) == C_FEATURE["variant"][2]
            and len(variant) == C_FEATURE["variant"][3],
            "bind exact canonical C, genuine adapter, and complete owned variant")
    c16_contract = document(base, groups["c16"]["contract"], "frozen C V16")
    validate_c16_contract(c16_contract)
    c_receipt = document(base, base["read_exact"](C16_RECEIPT),
                         "actual small C V16 build receipt")
    validate_c16_receipt(c_receipt)
    rust_build = document(base, base["read_exact"](RUST19_BUILD_RECEIPT),
                          "actual small Rust V19 build receipt")
    rust_root = document(base, base["read_exact"](RUST19_ROOT_RECEIPT),
                         "actual small Rust V19 root receipt")
    validate_rust19_receipts(rust_build, rust_root)
    rust_failure = document(base, base["read_exact"](RUST15_FAILURE),
                            "actual small guarded Rust V15 failure receipt")
    validate_rust15_failure(rust_failure)
    summary = document(base, groups["graph"]["summary"], "complete V86 summary")
    inputs = document(base, groups["graph"]["inputs"], "complete V86 inputs")
    validate_graph(summary, inputs, c_receipt, rust_failure)
    require(b"<svg" in groups["graph"]["svg"]
            and b"</svg>" in groups["graph"]["svg"],
            "authenticate the complete actual committed V86 evidence graph")
    proposal = document(base, groups["proposal"]["contract"],
                        "unopened expanded comparison proposal",
                        canonical_required=False)
    validate_proposal(proposal)
    rust_contract = document(base, groups["rust19"]["contract"],
                             "immutable first-party Rust V19 source freeze")
    require(rust_contract.get("schema")
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-source-freeze"
            and rust_contract.get("version") == 19
            and rust_contract.get("family") == "rust",
            "authenticate Rust provenance without reusing its matching engine")
    result: dict[str, object] = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "version": VERSION,
        "status": "PASS",
        "family": FAMILY,
        "source": source_info,
        "protocol": protocol_info,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_graph_owner_count": 4,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "historical_c_candidate_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "historical_c_v16_build_status": "PASS",
        "historical_c_v16_actual_compiler_process_count": 14,
        "historical_c_v16_root_provenance": "NOT MEASURED",
        "latest_rust_candidate_status": "FAIL",
        "latest_rust_original_attempted_suite_count": 13,
        "latest_rust_original_completed_suite_count": 8,
        "latest_rust_original_infrastructure_failure_count": 5,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_semantic_mismatch_count": "NOT MEASURED",
        "latest_rust_failure_cause": "NOT ESTABLISHED",
        "actual_rust_v19_compiler_process_count": 28,
        "actual_rust_v19_root_provenance": "PASS",
        "phase1_v4_readiness": "PASS",
        "candidate_qualification": "BLOCKED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_case_count_per_worker": 8244,
        "supplemental_reference_worker_count": 2,
        "future_phase_count": 2,
        "future_compiler_process_count_per_phase": 7,
        "future_total_compiler_process_count": 14,
        **boundary(),
    }
    state = {
        "source_info": source_info,
        "protocol_info": protocol_info,
        "original": original,
        "adapter": adapter,
        "variant": variant,
        "c16_contract": c16_contract,
        "c16_receipt": c_receipt,
        "rust19_build_receipt": rust_build,
        "rust19_root_receipt": rust_root,
        "rust15_failure": rust_failure,
        "fuzz": fuzz,
        "summary": summary,
        "inputs": inputs,
        "proposal": proposal,
    }
    expected = contract_document(source_pin, protocol_pin, state)
    if contract_pin is not None:
        checked_hash(contract_pin, "C V18 contract")
        contract_raw, contract_info = base["read_self"](CONTRACT_PATH, contract_pin)
        require(contract_raw == encoded(base, expected)
                and document(base, contract_raw, "complete C V18 contract") == expected,
                "reject an altered or incomplete C V18 provenance contract")
        result["contract"] = contract_info
    base["no_matching_imports"]()
    return result, state


def contract_document(source_pin: str, protocol_pin: str,
                      state: dict[str, object]) -> dict[str, object]:
    checked_hash(source_pin, "C V18 source")
    checked_hash(protocol_pin, "C V18 protocol")
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "phase": "SOURCE FREEZE; FIRST-PARTY C ROOT PROVENANCE NOT BUILT OR RUN",
        "family": FAMILY,
        "source": {
            "path": SOURCE_PATH, "sha256": source_pin,
            "bytes": state["source_info"]["bytes"],
        },
        "protocol": {
            "path": PROTOCOL_PATH, "sha256": protocol_pin,
            "bytes": state["protocol_info"]["bytes"],
        },
        "goal": row_document(GOAL),
        "pinned_cpython": {
            "implementation": "CPython", "version": "3.14.6",
            "executable": PYTHON, "sha256": PYTHON_SHA256,
            "isolated": True, "bytecode": False,
        },
        "published_current_graph": {
            "version": GRAPH_VERSION,
            "owner_count": 4,
            "owners": row_group(GRAPH),
            "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
            "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
            "lower_bounds_are_not_a_repository_census": True,
            "final_comparison_planned_case_count": 4194304,
            "final_comparison_cases_generated": False,
            "final_holdout_opened": False,
        },
        "phase1_v4_readiness": {
            "owners": row_group(P0_V4),
            "status": "PASS",
            "status_scope": "PHASE 1 PYTHON-ORACLE READINESS ONLY",
            "candidate_qualification_status": "BLOCKED",
            "qualification_blockers": list(QUALIFICATION_BLOCKERS),
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_reference_worker_count": 2,
            "supplemental_case_count_per_reference": 8244,
            "supplemental_added_to_original_denominator": False,
        },
        "frozen_original_producer": {
            "version": 5, "owners": row_group(PRODUCER_V5),
            "family_count": 6,
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
        },
        "independent_actual_differential_reference": {
            "owners": row_group(FUZZ_REFERENCE),
            "status": "PASS",
            "reference_worker_count": 2,
            "case_count_per_reference": 8244,
            "candidate_fuzz_status": "NOT RUN",
            "supplemental_added_to_original_denominator": False,
        },
        "immutable_first_party_c_v16": {
            "owners": row_group(C16),
            "version": 16,
            "source_modified": False,
            "previous_actual_build_receipt": row_document(C16_RECEIPT),
            "previous_build_status": "PASS",
            "previous_actual_compiler_process_count": 14,
            "previous_archive_metadata_attested_by_small_receipt_only": {
                "path": state["c16_receipt"]["archive_relative"],
                "sha256": state["c16_receipt"]["archive_sha256"],
                "bytes": state["c16_receipt"]["archive_bytes"],
                "archive_opened": False,
                "archive_hash_recomputed": False,
                "archive_bytes_read": 0,
            },
            "previous_private_root_path": "NOT MEASURED",
            "previous_private_root_device": "NOT MEASURED",
            "previous_private_root_inode": "NOT MEASURED",
            "previous_private_root_provenance": "NOT ESTABLISHED",
            "previous_private_root_scanned": False,
            "previous_phase_artifact_hashes": "NOT MEASURED",
            "previous_candidate_matching": "NOT RUN",
        },
        "independent_owned_c_engine": {
            "feature_owners": row_group(C_FEATURE),
            "canonical_native_source": row_document(CANONICAL_C),
            "canonical_python_adapter": row_document(C_ADAPTER),
            "complete_variant_sha256": C_FEATURE["variant"][2],
            "complete_variant_bytes": C_FEATURE["variant"][3],
            "independent_parser_compiler_executor_and_engine": True,
            "canonical_source_modified": False,
            "canonical_adapter_modified": False,
            "stdlib_regex_engine": "FORBIDDEN",
            "external_regex_engine": "FORBIDDEN",
            "other_candidate_engine": "FORBIDDEN",
            "matching_fallback": "FORBIDDEN",
            "hardcoded_oracle_answers": "FORBIDDEN",
            "installed_native_loading": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "historical_c_correctness": {
            "status": "FAIL",
            "semantic_mismatch_count": 1230,
            "verified_passing_case_count": 7325,
            "case_execution_denominator": 31237,
            "replacement_qualified": False,
        },
        "preserved_latest_rust_correctness": {
            "actual_small_failure_receipt": row_document(RUST15_FAILURE),
            "candidate_status": "FAIL",
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "attempted_suite_count": 13,
            "completed_suite_count": 8,
            "infrastructure_failure_count": 5,
            "verified_passing_case_count": 12942,
            "semantic_mismatch_count": "NOT MEASURED",
            "underlying_failure_cause": "NOT ESTABLISHED",
            "destructor_warning_proven_as_failure_cause": False,
            "archive_opened": False,
            "candidate_qualified": False,
        },
        "preserved_independent_rust_build": {
            "source_owners": row_group(RUST19),
            "actual_build_receipt": row_document(RUST19_BUILD_RECEIPT),
            "actual_root_receipt": row_document(RUST19_ROOT_RECEIPT),
            "actual_build_status": "PASS",
            "actual_compiler_process_count": 28,
            "actual_root_provenance": "PASS",
            "existing_rust_root_opened": False,
            "existing_rust_root_scanned": False,
            "historical_build_archive_opened": False,
            "rust_engine_reused_by_c": False,
            "candidate_matching": "NOT RUN",
        },
        "preserved_expanded_final_comparison_proposal": {
            "owners": row_group(PROPOSAL),
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "case_count": 14155776,
            "previous_proposal_case_count": 4194304,
            "operation_count": 36,
            "pattern_family_count": 24,
            "paired_round_count": 24,
            "minimum_qualified_independent_family_count": 3,
            "qualified_independent_family_count": 0,
            "final_protocol": "NOT FROZEN",
            "generator": "NOT FROZEN",
            "cases": "NOT GENERATED; NOT OPENED",
            "secret": "NOT GENERATED",
            "timing": "NOT RUN; NOT MEASURED",
            "memory": "NOT RUN; NOT MEASURED",
            "winner": "NOT SELECTED",
            "runtime_independence": "NOT ESTABLISHED",
        },
        "future_first_party_root_provenance_build": {
            "authorization": "EXPLICIT FUTURE --build ONLY",
            "unique_label": BUILD_LABEL,
            "root_parent": "/tmp",
            "exact_owned_private_root_prefix": ROOT_PREFIX,
            "private_root_path": "NOT MEASURED",
            "private_root_device": "NOT MEASURED",
            "private_root_inode": "NOT MEASURED",
            "private_root_uid": "NOT MEASURED",
            "private_root_mode": "0700",
            "root_capture_flags": "O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW",
            "root_capture_origin":
                "ACTUAL verify_reproducibility(v8,v7,workdir,phases,steps) CALLBACK",
            "tmp_directory_scanning": "FORBIDDEN",
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "source_owners_per_phase": 2,
            "private_source_overlay_count": 2,
            "process_roles_per_phase": list(PROCESS_NAMES),
            "compiler_process_count_per_phase": 7,
            "expected_actual_compiler_process_count": 14,
            "canonical_native_source_sha256": CANONICAL_C[2],
            "canonical_adapter_sha256": C_ADAPTER[2],
            "complete_variant_sha256": C_FEATURE["variant"][2],
            "complete_variant_bytes": C_FEATURE["variant"][3],
            "pinned_toolchain_owners": planned_toolchains(),
            "pinned_toolchain_owner_count": 5,
            "toolchain_authentication":
                "COMPLETE SHA-256 AND FILE IDENTITY BEFORE ANY COMPILER PROCESS",
            "source_and_adapter_token_audits": "MANDATORY FIRST-PARTY V4 AUDITS",
            "compare_complete_independent_owned_extension_elf": True,
            "output_name": "_vm_native.cpython-314-x86_64-linux-gnu.so",
            "root_receipt_exclusive_creation": "O_CREAT | O_EXCL | O_NOFOLLOW",
            "root_receipt_file_fsync": True,
            "root_receipt_directory_fsync": True,
            "additional_root_receipt_count": 1,
            "native_activation": "FORBIDDEN",
            "matching_or_candidate_workers": "FORBIDDEN",
            "holdout": "FORBIDDEN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "build_pass_means": "REPRODUCIBLE COMPILATION AND ROOT PROVENANCE ONLY",
        },
        "source_only_effects": boundary(),
    }


def synthetic_root_plan() -> dict[str, object]:
    phases: list[dict[str, object]] = []
    for index, phase in enumerate(PHASES):
        phases.append({
            "name": phase,
            "device": 2049,
            "inode": 8100 + index,
            "mode": "0700",
            "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL PHASE",
            "source_owners": [{
                "role": "variant" if role == 0 else "adapter",
                "sha256": C_FEATURE["variant"][2] if role == 0 else C_ADAPTER[2],
                "bytes": C_FEATURE["variant"][3] if role == 0 else C_ADAPTER[3],
                "device": 2049,
                "inode": 9100 + index * 2 + role,
                "mode": "0600",
                "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL SOURCE",
            } for role in range(2)],
            "native_output": {
                "file_name": "_vm_native.cpython-314-x86_64-linux-gnu.so",
                "sha256": format(70, "064x"),
                "bytes": 7000,
                "device": 2049,
                "inode": 9200 + index,
                "mode": "0755",
                "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL NATIVE",
            },
        })
    processes = [{
        "phase": PHASES[index // len(PROCESS_NAMES)],
        "name": PROCESS_NAMES[index % len(PROCESS_NAMES)],
        "pid": 10100 + index,
        "exit_status": 0,
        "working_directory": "<FRESH_PRIVATE_TMP>/"
            + PHASES[index // len(PROCESS_NAMES)],
        "evidence_kind": "SYNTHETIC CONTROL; NOT A REAL PROCESS",
    } for index in range(14)]
    return {
        "schema": SCHEMA + "-synthetic-root-control",
        "graph_version": GRAPH_VERSION,
        "root_path": "/tmp/" + ROOT_PREFIX + "SYNTHETIC_CONTROL",
        "root_device": 2049,
        "root_inode": 8000,
        "root_uid": os.geteuid(),
        "root_mode": "0700",
        "root_evidence_kind": "SYNTHETIC CONTROL; NOT A REAL ROOT",
        "phase_count": 2,
        "expected_process_count": 14,
        "phases": phases,
        "processes": processes,
        "actual_root_descriptor_opens": 0,
        "actual_compiler_process_count": 0,
        "candidate_workers_started": 0,
        "archive_opens": 0,
        "native_libraries_loaded": 0,
        "holdout": "NOT OPENED",
    }


def validate_synthetic_root(plan: object) -> dict[str, object]:
    require(type(plan) is dict
            and plan.get("schema") == SCHEMA + "-synthetic-root-control"
            and plan.get("graph_version") == GRAPH_VERSION
            and plan.get("root_path")
                == "/tmp/" + ROOT_PREFIX + "SYNTHETIC_CONTROL"
            and plan.get("root_device") == 2049
            and plan.get("root_inode") == 8000
            and plan.get("root_uid") == os.geteuid()
            and plan.get("root_mode") == "0700"
            and plan.get("root_evidence_kind")
                == "SYNTHETIC CONTROL; NOT A REAL ROOT"
            and plan.get("phase_count") == 2
            and plan.get("expected_process_count") == 14
            and plan.get("actual_root_descriptor_opens") == 0
            and plan.get("actual_compiler_process_count") == 0
            and plan.get("candidate_workers_started") == 0
            and plan.get("archive_opens") == 0
            and plan.get("native_libraries_loaded") == 0
            and plan.get("holdout") == "NOT OPENED",
            "reject a forged actual root, candidate, archive, or compiler")
    phases = plan.get("phases")
    processes = plan.get("processes")
    require(type(phases) is list and len(phases) == 2
            and type(processes) is list and len(processes) == 14,
            "require precisely two synthetic phases and fourteen synthetic roles")
    sources: set[tuple[int, int]] = set()
    outputs: set[tuple[int, int]] = set()
    for index, phase in enumerate(phases):
        require(type(phase) is dict and phase.get("name") == PHASES[index]
                and phase.get("device") == 2049
                and phase.get("inode") == 8100 + index
                and phase.get("mode") == "0700"
                and phase.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL PHASE",
                "reject a borrowed or unsafe synthetic C phase")
        observed_sources = phase.get("source_owners")
        require(type(observed_sources) is list and len(observed_sources) == 2,
                "require both distinctly synthetic first-party C input roles")
        for role, item in enumerate(observed_sources):
            expected = C_FEATURE["variant"] if role == 0 else C_ADAPTER
            pair = ((item.get("device"), item.get("inode"))
                    if type(item) is dict else None)
            require(type(item) is dict
                    and item.get("role") == ("variant" if role == 0 else "adapter")
                    and item.get("sha256") == expected[2]
                    and item.get("bytes") == expected[3]
                    and item.get("device") == 2049
                    and item.get("inode") == 9100 + index * 2 + role
                    and item.get("mode") == "0600"
                    and item.get("evidence_kind")
                        == "SYNTHETIC CONTROL; NOT A REAL SOURCE"
                    and pair not in sources,
                    "reject a fake, reused, or external C source owner")
            assert pair is not None
            sources.add(pair)
        native = phase.get("native_output")
        identity = ((native.get("device"), native.get("inode"))
                    if type(native) is dict else None)
        require(type(native) is dict
                and native.get("file_name")
                    == "_vm_native.cpython-314-x86_64-linux-gnu.so"
                and native.get("sha256") == format(70, "064x")
                and native.get("bytes") == 7000
                and native.get("device") == 2049
                and native.get("inode") == 9200 + index
                and native.get("mode") == "0755"
                and native.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL NATIVE"
                and identity not in outputs,
                "reject an invented, borrowed, or aliased synthetic C extension")
        assert identity is not None
        outputs.add(identity)
    pids: set[int] = set()
    for index, process in enumerate(processes):
        phase = PHASES[index // len(PROCESS_NAMES)]
        require(type(process) is dict
                and process.get("phase") == phase
                and process.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                and process.get("pid") == 10100 + index
                and process["pid"] not in pids
                and process.get("exit_status") == 0
                and process.get("working_directory")
                    == "<FRESH_PRIVATE_TMP>/" + phase
                and process.get("evidence_kind")
                    == "SYNTHETIC CONTROL; NOT A REAL PROCESS",
                "reject reordered, duplicated, foreign, or actual C process roles")
        pids.add(process["pid"])
    return {
        "status": "PASS",
        "synthetic_only": True,
        "synthetic_phase_count": 2,
        "synthetic_source_owner_count": len(sources),
        "synthetic_native_owner_count": len(outputs),
        "synthetic_process_role_count": len(pids),
        "actual_root_descriptor_opens": 0,
        "actual_compiler_process_count": 0,
    }


def checked_label(value: object) -> str:
    require(type(value) is str and 0 < len(value) <= 80
            and all(char.isascii() and (char.isalnum() or char in "-_")
                    for char in value),
            "require a bounded, canonical, unique first-party C V18 label")
    return value


def evidence_names(label: str, *, failure: bool) -> tuple[str, str]:
    require(label == BUILD_LABEL and type(failure) is bool,
            "require the one independently authorized C V18 outcome")
    stem = "native-source-build-v18-c-" + checked_label(label)
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def root_receipt_name(label: str) -> str:
    require(label == BUILD_LABEL,
            "bind root provenance to the single frozen C V18 label")
    return "native-source-build-v18-c-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def self_test(base: dict[str, object], source_pin: str,
              protocol_pin: str, contract_pin: str) -> dict[str, object]:
    context, _state = collect_context(base, source_pin, protocol_pin, contract_pin)
    plan = synthetic_root_plan()
    positive = 0
    rejected = 0

    def reject(operation: object, label: str) -> None:
        nonlocal rejected
        try:
            operation()
        except (GateError, Exception):
            rejected += 1
            return
        raise GateError("accepted a hostile C V18 source-only control: " + label)

    proof = validate_synthetic_root(plan)
    require(proof.get("synthetic_process_role_count") == 14
            and proof.get("synthetic_source_owner_count") == 4
            and proof.get("synthetic_native_owner_count") == 2,
            "authenticate a synthetic-only complete C root and process schedule")
    positive += 1
    require(context.get("latest_rust_original_infrastructure_failure_count") == 5
            and context.get("historical_c_v16_root_provenance") == "NOT MEASURED"
            and context.get("proposed_final_holdout_case_count") == 14155776
            and context.get("published_graph_final_comparison_planned_case_count")
                == 4194304
            and context.get("final_holdout_case_count") == "NOT GENERATED",
            "preserve actual latest losses, old root limitations, and sealed proposal")
    positive += 1
    for key, replacement in (
        ("graph_version", 67),
        ("root_path", "/tmp/borrowed-root"),
        ("root_device", DEVICE),
        ("root_inode", 0),
        ("root_uid", -1),
        ("root_mode", "0755"),
        ("root_evidence_kind", "ACTUAL ROOT"),
        ("phase_count", 1),
        ("expected_process_count", 13),
        ("actual_root_descriptor_opens", 1),
        ("actual_compiler_process_count", 1),
        ("candidate_workers_started", 1),
        ("archive_opens", 1),
        ("native_libraries_loaded", 1),
        ("holdout", "OPENED"),
    ):
        changed = base["clone"](plan)
        changed[key] = replacement
        reject(lambda value=changed: validate_synthetic_root(value), key)
    for index in range(2):
        for key, replacement in (
            ("name", "borrowed"), ("inode", 0),
            ("mode", "0755"), ("evidence_kind", "ACTUAL PHASE"),
        ):
            changed = base["clone"](plan)
            changed["phases"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(value), key)
        for role in range(2):
            for key, replacement in (
                ("sha256", "0" * 64), ("inode", 0),
                ("mode", "0644"),
                ("evidence_kind", "ACTUAL SOURCE"),
            ):
                changed = base["clone"](plan)
                changed["phases"][index]["source_owners"][role][key] = replacement
                reject(lambda value=changed: validate_synthetic_root(value),
                       "source:" + str(role) + ":" + key)
        for key, replacement in (
            ("sha256", "0" * 64), ("inode", 0),
            ("file_name", "external_regex.so"), ("mode", "0644"),
            ("evidence_kind", "ACTUAL NATIVE"),
        ):
            changed = base["clone"](plan)
            changed["phases"][index]["native_output"][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(value),
                   "native:" + key)
    for index in range(14):
        for key, replacement in (
            ("name", "build_external_regex"), ("phase", "borrowed-phase"),
            ("pid", 0), ("exit_status", 1),
            ("evidence_kind", "ACTUAL COMPILER"),
        ):
            changed = base["clone"](plan)
            changed["processes"][index][key] = replacement
            reject(lambda value=changed: validate_synthetic_root(value),
                   "process:" + str(index) + ":" + key)
    for value in ("", "../escape", "/tmp/private", "wrong label", "x" * 81):
        reject(lambda item=value: checked_label(item), "unsafe evidence label")
    for failed in (False, True):
        archive, receipt = evidence_names(BUILD_LABEL, failure=failed)
        require(archive.startswith("native-source-build-v18-c-")
                and archive.endswith(".json.gz")
                and receipt.endswith("-publication-receipt.json")
                and ("-failures" in archive) is failed,
                "retain distinct future C V18 success and failure publications")
        positive += 1
    probes = (
        ("unlisted-file", lambda: builtins.open("/etc/hosts", "rb")),
        ("tmp-root-scan", lambda: builtins.open("/tmp", "rb")),
        ("old-c-build-archive", lambda: builtins.open(
            ROOT + "/oracle/phase2/evidence/native-source-build-v16-c-"
            "phase2-v16-c-subject-buffer-original-p0.json.gz", "rb")),
        ("old-rust-build-archive", lambda: builtins.open(
            ROOT + "/oracle/phase2/evidence/native-source-build-v19-rust-"
            "phase2-v19-rust-buffer-shape-root-provenance.json.gz", "rb")),
        ("hidden-holdout", lambda: builtins.open(
            ROOT + "/benchmarks/holdout.json", "rb")),
        ("source-mutation", lambda: builtins.open(ROOT + "/" + SOURCE_PATH, "w")),
        ("stdlib-regex", lambda: sys.audit("import", "re", None, None, None, None)),
        ("cpython-matcher", lambda: sys.audit("import", "_sre", None, None, None, None)),
        ("external-regex", lambda: sys.audit("import", "regex", None, None, None, None)),
        ("candidate-import", lambda: sys.audit(
            "import", "candidates.vm_candidate", None, None, None, None)),
        ("native-load", lambda: sys.audit("ctypes.dlopen", "foreign.so")),
        ("compiler", lambda: sys.audit("subprocess.Popen", "gcc", (), None, None)),
        ("network", lambda: sys.audit("socket.__new__", None, 2, 1, 0)),
        ("thread", lambda: sys.audit("threading.Thread.start", None)),
        ("clock", lambda: sys.audit("time.perf_counter")),
        ("temporary-root", lambda: sys.audit("tempfile.mkdtemp", "/tmp/forbidden")),
        ("filesystem-rename", lambda: sys.audit("os.rename", "a", "b", -1, -1)),
        ("archive-inflation", lambda: sys.audit("gzip.decompress", b"forbidden")),
        ("foreign-execution", lambda: sys.audit("exec", "forbidden")),
        ("foreign-compilation", lambda: sys.audit(
            "compile", b"forbidden", "foreign.py")),
    )
    for name, operation in probes:
        reject(operation, "physically-block:" + name)
    for category in (
        "filesystem", "matching_import", "native", "process", "network",
        "thread", "clock", "temporary", "archive", "dynamic_execution",
    ):
        require(base["_BLOCKED"].get(category, 0) >= 1,
                "physically exercise the source-only effect wall: " + category)
    require(rejected >= 120,
            "require complete C root, source, extension, process, and effect controls")
    base["no_matching_imports"]()
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "version": VERSION,
        "status": "PASS",
        "family": FAMILY,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_positive_control_count": positive,
        "rejected_hostile_controls": rejected,
        "blocked_effect_attempts": dict(base["_BLOCKED"]),
        "synthetic_control_proof": proof,
        "authenticated_current_graph_version": GRAPH_VERSION,
        "authenticated_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "authenticated_history_reference_lower_bound": HISTORY_FLOOR,
        "historical_c_v16_build_status": "PASS",
        "historical_c_v16_compiler_process_count": 14,
        "historical_c_v16_root_provenance": "NOT MEASURED",
        "latest_rust_candidate_status": "FAIL",
        "latest_rust_completed_suite_count": 8,
        "latest_rust_infrastructure_failure_count": 5,
        "latest_rust_verified_passing_case_count": 12942,
        "latest_rust_semantic_mismatch_count": "NOT MEASURED",
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_reference_case_count_per_worker": 8244,
        "supplemental_reference_worker_count": 2,
        "future_total_compiler_process_count": 14,
        **boundary(),
    }


def assert_fresh_root_receipt(label: str) -> None:
    absolute = ROOT + "/" + EVIDENCE_PATH + "/" + root_receipt_name(label)
    try:
        os.lstat(absolute)
    except FileNotFoundError:
        return
    raise GateError("reject a pre-existing or borrowed C V18 root receipt")


def capture_root_descriptor(v8: object, workdir: str,
                            phases: list[object]) -> tuple[int, dict[str, object]]:
    v8.checked_workdir(workdir, FAMILY)
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) \
        | getattr(os, "O_NOFOLLOW", 0)
    root_fd = os.open(workdir, directory_flags)
    try:
        observed = os.fstat(root_fd)
        named = os.stat(workdir, follow_symlinks=False)
        require(workdir.startswith("/tmp/" + ROOT_PREFIX)
                and stat.S_ISDIR(observed.st_mode)
                and stat.S_IMODE(observed.st_mode) == 0o700
                and observed.st_uid == os.geteuid()
                and (observed.st_dev, observed.st_ino)
                    == (named.st_dev, named.st_ino)
                and type(phases) is list and len(phases) == 2,
                "capture the actual no-follow owner-private C build root")
        roots: set[tuple[int, int]] = set()
        source_ids: set[tuple[int, int]] = set()
        output_ids: set[tuple[int, int]] = set()
        output_hashes: set[str] = set()
        records: list[dict[str, object]] = []
        for index, phase in enumerate(phases):
            require(type(phase) is dict and phase.get("name") == PHASES[index],
                    "bind exactly the two completed first-party C build phases")
            phase_fd = os.open(PHASES[index], directory_flags, dir_fd=root_fd)
            try:
                info = os.fstat(phase_fd)
                identity = info.st_dev, info.st_ino
                require(stat.S_ISDIR(info.st_mode)
                        and stat.S_IMODE(info.st_mode) == 0o700
                        and info.st_uid == os.geteuid()
                        and identity not in roots,
                        "reject an aliased, unsafe, or borrowed C build phase")
                roots.add(identity)
                observed_sources = phase.get("fresh_source_owners")
                require(type(observed_sources) is dict
                        and set(observed_sources) == {CANONICAL_C[1], C_ADAPTER[1]},
                        "require both actual complete first-party C source owners")
                source_fd = os.open("source", directory_flags, dir_fd=phase_fd)
                try:
                    source_info = os.fstat(source_fd)
                    require(stat.S_ISDIR(source_info.st_mode)
                            and stat.S_IMODE(source_info.st_mode) == 0o700
                            and source_info.st_uid == os.geteuid(),
                            "capture only a genuinely private phase source directory")
                    candidates_fd = os.open(
                        "candidates", directory_flags, dir_fd=source_fd,
                    )
                    try:
                        candidates_info = os.fstat(candidates_fd)
                        require(stat.S_ISDIR(candidates_info.st_mode)
                                and stat.S_IMODE(candidates_info.st_mode) == 0o700
                                and candidates_info.st_uid == os.geteuid(),
                                "require the genuine owned C candidate-source directory")
                        captured_sources: list[dict[str, object]] = []
                        for relative, filename, expected, role in (
                            (CANONICAL_C[1], "_vm_native.c", C_FEATURE["variant"],
                             "variant"),
                            (C_ADAPTER[1], "vm_candidate.py", C_ADAPTER, "adapter"),
                        ):
                            recorded = observed_sources[relative]
                            require(type(recorded) is dict
                                    and recorded.get("sha256") == expected[2]
                                    and recorded.get("bytes") == expected[3],
                                    "bind the phase to exact owned C source bytes")
                            fd = os.open(filename, file_flags, dir_fd=candidates_fd)
                            try:
                                actual = os.fstat(fd)
                                pair = actual.st_dev, actual.st_ino
                                require(stat.S_ISREG(actual.st_mode)
                                        and stat.S_IMODE(actual.st_mode) == 0o600
                                        and actual.st_uid == os.geteuid()
                                        and actual.st_nlink == 1
                                        and (actual.st_dev, actual.st_ino,
                                             actual.st_size)
                                            == (recorded.get("device"),
                                                recorded.get("inode"),
                                                recorded.get("bytes"))
                                        and pair not in source_ids,
                                        "reject a reused or substituted private C input")
                                source_ids.add(pair)
                                captured_sources.append({
                                    "role": role,
                                    "relative_path": relative,
                                    "absolute_path": workdir + "/" + PHASES[index]
                                        + "/source/" + relative,
                                    "sha256": recorded["sha256"],
                                    "bytes": actual.st_size,
                                    "device": actual.st_dev,
                                    "inode": actual.st_ino,
                                    "uid": actual.st_uid,
                                    "mode": format(stat.S_IMODE(actual.st_mode), "04o"),
                                    "nlink": actual.st_nlink,
                                    "hash_provenance":
                                        "COMPLETE EXCLUSIVE FIRST-PARTY SOURCE SNAPSHOT",
                                })
                            finally:
                                os.close(fd)
                    finally:
                        os.close(candidates_fd)
                finally:
                    os.close(source_fd)
                outputs = phase.get("native_outputs")
                extension = outputs.get("extension") if type(outputs) is dict else None
                require(type(extension) is dict
                        and extension.get("file_name") == v8.EXTENSION_NAME
                        and type(extension.get("sha256")) is str
                        and type(extension.get("size_bytes")) is int,
                        "require the genuine C-only owned extension output role")
                checked_hash(extension["sha256"], "actual C extension")
                native_fd = os.open("native", directory_flags, dir_fd=phase_fd)
                try:
                    native_info = os.fstat(native_fd)
                    require(stat.S_ISDIR(native_info.st_mode)
                            and stat.S_IMODE(native_info.st_mode) == 0o700
                            and native_info.st_uid == os.geteuid(),
                            "capture only the actual private C native output directory")
                    extension_fd = os.open(
                        v8.EXTENSION_NAME, file_flags, dir_fd=native_fd,
                    )
                    try:
                        artifact = os.fstat(extension_fd)
                        pair = artifact.st_dev, artifact.st_ino
                        require(stat.S_ISREG(artifact.st_mode)
                                and stat.S_IMODE(artifact.st_mode)
                                    in (0o700, 0o755)
                                and artifact.st_uid == os.geteuid()
                                and artifact.st_nlink == 1
                                and (artifact.st_dev, artifact.st_ino,
                                     artifact.st_size)
                                    == (extension.get("device"),
                                        extension.get("inode"),
                                        extension.get("size_bytes"))
                                and pair not in output_ids,
                                "reject a borrowed, aliased, or loaded C extension")
                        output_ids.add(pair)
                        output_hashes.add(extension["sha256"])
                        native_record = {
                            "role": "extension",
                            "file_name": v8.EXTENSION_NAME,
                            "absolute_path": workdir + "/" + PHASES[index]
                                + "/native/" + v8.EXTENSION_NAME,
                            "sha256": extension["sha256"],
                            "bytes": artifact.st_size,
                            "device": artifact.st_dev,
                            "inode": artifact.st_ino,
                            "uid": artifact.st_uid,
                            "mode": format(stat.S_IMODE(artifact.st_mode), "04o"),
                            "nlink": artifact.st_nlink,
                            "hash_provenance":
                                "COMPLETE ORIGINAL FIRST-PARTY ELF VERIFICATION",
                            "native_loaded": False,
                        }
                    finally:
                        os.close(extension_fd)
                finally:
                    os.close(native_fd)
                records.append({
                    "name": PHASES[index],
                    "absolute_path": workdir + "/" + PHASES[index],
                    "device": info.st_dev,
                    "inode": info.st_ino,
                    "uid": info.st_uid,
                    "mode": format(stat.S_IMODE(info.st_mode), "04o"),
                    "source_owners": captured_sources,
                    "native_output": native_record,
                })
            finally:
                os.close(phase_fd)
        require(len(roots) == 2 and len(source_ids) == 4
                and len(output_ids) == 2 and len(output_hashes) == 1,
                "prove two actual independent phases, four sources, and equal C ELFs")
        return root_fd, {
            "path": workdir,
            "prefix": ROOT_PREFIX,
            "device": observed.st_dev,
            "inode": observed.st_ino,
            "uid": observed.st_uid,
            "mode": format(stat.S_IMODE(observed.st_mode), "04o"),
            "nofollow_directory_descriptor": True,
            "descriptor_opened_during_live_verification": True,
            "directory_scanned": False,
            "phase_count": 2,
            "distinct_source_owner_count": 4,
            "distinct_native_owner_count": 2,
            "byte_identical_native_output": True,
            "phases": records,
        }
    except BaseException:
        os.close(root_fd)
        raise


def publish_build_report(module: object, kernel: object,
                         original_report: dict[str, object],
                         label: str,
                         state: dict[str, object]) -> dict[str, object]:
    require(type(original_report) is dict
            and original_report.get("schema") == SCHEMA + "-actual-native-build"
            and original_report.get("version") == VERSION
            and original_report.get("status") in {"PASS", "FAIL"}
            and original_report.get("family") == FAMILY
            and original_report.get("label") == BUILD_LABEL
            and label == BUILD_LABEL,
            "publish only the complete genuine first-party C V18 build outcome")
    runtime = state.get("runtime_state")
    require(type(runtime) is dict,
            "retain actual source-audit and compiler-authentication state")
    if original_report.get("status") == "PASS":
        require(runtime.get("toolchain_audit_status") == "PASS"
                and type(runtime.get("authenticated_toolchains")) is list
                and len(runtime["authenticated_toolchains"]) == 5
                and runtime.get("source_audit_status") == "PASS"
                and runtime.get("adapter_audit_status") == "PASS",
                "reject an actual C PASS without all five toolchain and source audits")
    report = dict(original_report)
    require(report.get("current_rust_semantic_mismatch_count") == 1440
            and report.get("current_rust_verified_passing_case_count") == 14853,
            "retain the original C16 historical Rust V10 report before relabeling")
    report.update({
        "historical_rust_v10_candidate_status": "FAIL",
        "historical_rust_v10_semantic_mismatch_count": 1440,
        "historical_rust_v10_verified_passing_case_count": 14853,
        "current_rust_candidate_status": "FAIL",
        "current_rust_attempted_suite_count": 13,
        "current_rust_completed_suite_count": 8,
        "current_rust_infrastructure_failure_count": 5,
        "current_rust_verified_passing_case_count": 12942,
        "current_rust_semantic_mismatch_count": "NOT MEASURED",
        "current_rust_underlying_failure_cause": "NOT ESTABLISHED",
        "current_rust_failure_receipt_sha256": RUST15_FAILURE[2],
        "toolchain_audit_status": runtime.get(
            "toolchain_audit_status", "NOT ESTABLISHED",
        ),
        "authenticated_toolchain_owners": runtime.get(
            "authenticated_toolchains", [],
        ),
        "published_graph_final_comparison_planned_case_count": 4194304,
        "proposed_final_holdout_case_count": 14155776,
        "proposed_final_holdout_status": "NOT GENERATED; NOT OPENED",
    })
    archive_name, receipt_name = evidence_names(
        label, failure=report["status"] == "FAIL",
    )
    directory = module.ROOT / EVIDENCE_PATH
    kernel.mkdir_private(directory)
    plain = module.canonical(report)
    require(type(plain) is bytes and 0 < len(plain) <= module.REPORT_LIMIT,
            "bound the genuine complete current-evidence C build report")
    compressed = module.gzip.compress(plain, compresslevel=9, mtime=0)
    require(type(compressed) is bytes
            and 0 < len(compressed) <= module.ARCHIVE_LIMIT,
            "bound the complete deterministic C V18 evidence archive")
    archive = kernel.write_fresh(
        directory / archive_name, compressed, synchronize=True,
    )
    archive_sync = kernel.fsync_directory(directory)
    require(type(archive) is dict
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and type(archive_sync) is dict
            and archive_sync.get("completed") is True,
            "exclusively create and durably synchronize the actual C build archive")
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means": "DURABLE BUILD PUBLICATION ONLY",
        "build_status": report["status"],
        "family": FAMILY,
        "label": label,
        "source_sha256": report["source_sha256"],
        "protocol_sha256": report["protocol_sha256"],
        "contract_sha256": report["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "archive_bytes": archive["bytes"],
        "archive_publication": archive,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "published_overview_version": GRAPH_VERSION,
        "published_overview_sha256": GRAPH["summary"][2],
        "published_graph_final_comparison_planned_case_count": 4194304,
        "proposed_final_holdout_case_count": 14155776,
        "proposed_final_holdout_status": "NOT GENERATED; NOT OPENED",
        "variant_source_sha256": C_FEATURE["variant"][2],
        "variant_source_bytes": C_FEATURE["variant"][3],
        "original_source_sha256": CANONICAL_C[2],
        "adapter_source_sha256": C_ADAPTER[2],
        "expected_source_apply_count": 2,
        "actual_source_apply_count": report.get("source_apply_count", 0),
        "expected_compiler_process_count": 14,
        "actual_compiler_process_count":
            report.get("actual_compiler_process_count", 0),
        "toolchain_audit_status": report["toolchain_audit_status"],
        "authenticated_toolchain_owner_count": len(
            report["authenticated_toolchain_owners"],
        ),
        "authenticated_toolchain_owners": report[
            "authenticated_toolchain_owners"
        ],
        "historical_c_candidate_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "historical_rust_v10_candidate_status": "FAIL",
        "historical_rust_v10_semantic_mismatch_count": 1440,
        "historical_rust_v10_verified_passing_case_count": 14853,
        "current_rust_candidate_status": "FAIL",
        "current_rust_attempted_suite_count": 13,
        "current_rust_completed_suite_count": 8,
        "current_rust_infrastructure_failure_count": 5,
        "current_rust_verified_passing_case_count": 12942,
        "current_rust_semantic_mismatch_count": "NOT MEASURED",
        "current_rust_underlying_failure_cause": "NOT ESTABLISHED",
        "current_rust_failure_receipt_sha256": RUST15_FAILURE[2],
        "historical_archives_opened": 0,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_imports": 0,
        "candidate_processes_started": 0,
        "native_libraries_loaded": 0,
        "installed_native_read": False,
        "installed_native_activated": False,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
        "receipt_self_publication": "NOT CLAIMED",
    }
    receipt_raw = module.canonical(receipt)
    require(type(receipt_raw) is bytes
            and 0 < len(receipt_raw) <= module.OWNER_LIMIT,
            "bound the genuine latest-evidence C V18 build receipt")
    published = kernel.write_fresh(
        directory / receipt_name, receipt_raw, synchronize=True,
    )
    receipt_sync = kernel.fsync_directory(directory)
    require(type(published) is dict
            and published.get("exclusive_creation") is True
            and published.get("file_fsync_completed") is True
            and type(receipt_sync) is dict
            and receipt_sync.get("completed") is True,
            "exclusively and durably publish the actual corrected C V18 receipt")
    return {
        "schema": SCHEMA + "-published-build",
        "version": VERSION,
        "status": report["status"],
        "family": FAMILY,
        "label": label,
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": archive["sha256"],
        "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
        "receipt_sha256": published["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": report["status"] == "FAIL",
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def publish_root_provenance(base: dict[str, object], module: object,
                            state: dict[str, object], result: dict[str, object],
                            options: dict[str, object]) -> dict[str, object]:
    require(result.get("status") == "PASS"
            and result.get("family") == FAMILY
            and result.get("label") == BUILD_LABEL
            and type(_ROOT_CAPTURE) is dict,
            "publish C provenance only after the actual successful native build")
    captured = _ROOT_CAPTURE
    assert isinstance(captured, dict)
    require(captured.get("unique_process_count") == 14
            and captured.get("phase_count") == 2
            and captured.get("source_audit_status") == "PASS"
            and captured.get("adapter_audit_status") == "PASS",
            "require both exact C source audits and all actual compiler roles")
    runtime_state = state.get("runtime_state")
    kernel = runtime_state.get("kernel") if type(runtime_state) is dict else None
    require(kernel is not None,
            "retain the immutable authenticated first-party C build kernel")
    build_relative = result.get("receipt_relative")
    build_hash = result.get("receipt_sha256")
    require(build_relative
            == EVIDENCE_PATH + "/" + evidence_names(BUILD_LABEL, failure=False)[1],
            "bind root provenance to the one newly published C V18 build receipt")
    checked_hash(build_hash, "actual C V18 build receipt")
    actual_path = ROOT + "/" + build_relative
    seen = os.stat(actual_path, follow_symlinks=False)
    require(stat.S_ISREG(seen.st_mode)
            and stat.S_IMODE(seen.st_mode) == 0o600
            and seen.st_uid == os.geteuid() and seen.st_nlink == 1,
            "bind the actual exclusive owner-private C V18 build receipt")
    row = ("actual_c_v18_build_receipt", build_relative, build_hash,
           seen.st_size, seen.st_dev, seen.st_ino)
    base["_ALLOWLIST"] = frozenset(set(base["_ALLOWLIST"]) | {actual_path})
    receipt = document(base, base["read_exact"](row),
                       "genuine newly published C V18 build receipt")
    require(receipt.get("schema") == SCHEMA + "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("source_sha256") == options["source_sha256"]
            and receipt.get("protocol_sha256") == options["protocol_sha256"]
            and receipt.get("contract_sha256") == options["contract_sha256"]
            and receipt.get("variant_source_sha256") == C_FEATURE["variant"][2]
            and receipt.get("variant_source_bytes") == C_FEATURE["variant"][3]
            and receipt.get("adapter_source_sha256") == C_ADAPTER[2]
            and receipt.get("actual_source_apply_count") == 2
            and receipt.get("expected_source_apply_count") == 2
            and receipt.get("actual_compiler_process_count") == 14
            and receipt.get("expected_compiler_process_count") == 14
            and receipt.get("toolchain_audit_status") == "PASS"
            and receipt.get("authenticated_toolchain_owner_count") == 5
            and receipt.get("authenticated_toolchain_owners")
                == captured.get("authenticated_toolchains")
            and receipt.get("current_rust_candidate_status") == "FAIL"
            and receipt.get("current_rust_attempted_suite_count") == 13
            and receipt.get("current_rust_completed_suite_count") == 8
            and receipt.get("current_rust_infrastructure_failure_count") == 5
            and receipt.get("current_rust_verified_passing_case_count") == 12942
            and receipt.get("current_rust_semantic_mismatch_count") == "NOT MEASURED"
            and receipt.get("current_rust_underlying_failure_cause")
                == "NOT ESTABLISHED"
            and receipt.get("current_rust_failure_receipt_sha256")
                == RUST15_FAILURE[2]
            and receipt.get("historical_rust_v10_semantic_mismatch_count") == 1440
            and receipt.get("historical_rust_v10_verified_passing_case_count") == 14853
            and receipt.get("published_graph_final_comparison_planned_case_count")
                == 4194304
            and receipt.get("proposed_final_holdout_case_count") == 14155776
            and receipt.get("proposed_final_holdout_status")
                == "NOT GENERATED; NOT OPENED"
            and receipt.get("archive_relative") == result.get("archive_relative")
            and receipt.get("archive_sha256") == result.get("archive_sha256")
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("holdout") == "NOT OPENED",
            "authenticate the actual canonical C V18 build before claiming a root")
    record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means":
            "DURABLE REPRODUCIBLE FIRST-PARTY C BUILD ROOT PROVENANCE ONLY",
        "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "frozen_graph_version": GRAPH_VERSION,
        "frozen_graph_summary_sha256": GRAPH["summary"][2],
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": build_relative,
        "canonical_build_receipt_sha256": build_hash,
        "canonical_build_receipt_bytes": seen.st_size,
        "canonical_build_receipt_device": seen.st_dev,
        "canonical_build_receipt_inode": seen.st_ino,
        "root": captured["root"],
        "actual_compiler_process_count": 14,
        "expected_compiler_process_count": 14,
        "actual_source_phase_count": 2,
        "distinct_actual_phase_source_owner_count": 4,
        "distinct_actual_native_extension_count": 2,
        "subject_buffer_source_overlay_apply_count": 2,
        "toolchain_audit_status": "PASS",
        "authenticated_toolchain_owner_count": 5,
        "authenticated_toolchain_owners": captured[
            "authenticated_toolchains"
        ],
        "native_source_delegation_audit": "PASS",
        "python_adapter_delegation_audit": "PASS",
        "historical_c_candidate_status": "FAIL",
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "current_rust_candidate_status": "FAIL",
        "current_rust_attempted_suite_count": 13,
        "current_rust_completed_suite_count": 8,
        "current_rust_infrastructure_failure_count": 5,
        "current_rust_verified_passing_case_count": 12942,
        "current_rust_semantic_mismatch_count": "NOT MEASURED",
        "current_rust_underlying_failure_cause": "NOT ESTABLISHED",
        "current_rust_failure_receipt_sha256": RUST15_FAILURE[2],
        "historical_rust_v10_semantic_mismatch_count": 1440,
        "historical_rust_v10_verified_passing_case_count": 14853,
        "published_graph_final_comparison_planned_case_count": 4194304,
        "proposed_final_holdout_case_count": 14155776,
        "proposed_final_holdout_status": "NOT GENERATED; NOT OPENED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "canonical_sources_modified": False,
        "tmp_directory_scanned": False,
        "historical_archives_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    raw = encoded(base, record)
    require(0 < len(raw) <= MAX_OWNER_BYTES,
            "bound the complete actual exclusive C root-provenance receipt")
    destination = module.ROOT / EVIDENCE_PATH / root_receipt_name(BUILD_LABEL)
    published = kernel.write_fresh(destination, raw, synchronize=True)
    directory = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(published.get("sha256") == digest(raw)
            and published.get("bytes") == len(raw)
            and published.get("exclusive_creation") is True
            and published.get("file_fsync_completed") is True
            and directory.get("completed") is True,
            "exclusively publish and durably sync the one real C root receipt")
    return {
        **result,
        "root_provenance_status": "PASS",
        "root_provenance_receipt_relative":
            EVIDENCE_PATH + "/" + root_receipt_name(BUILD_LABEL),
        "root_provenance_receipt_sha256": published["sha256"],
        "root_provenance_receipt_bytes": published["bytes"],
        "root_provenance_receipt_device": published["device"],
        "root_provenance_receipt_inode": published["inode"],
        "root_provenance_directory_fsync": directory,
        "actual_compiler_process_count": 14,
        "actual_private_phase_count": 2,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "holdout": "NOT OPENED",
    }


def run_build(base: dict[str, object], options: dict[str, object]) -> dict[str, object]:
    global _ROOT_CAPTURE
    require(options.get("mode") == "--build"
            and options.get("family") == FAMILY
            and options.get("label") == BUILD_LABEL
            and _ROOT_CAPTURE is None
            and base.get("_WALL_ENABLED") is False,
            "require one explicitly authorized first-party C V18 provenance build")
    context, state = collect_context(
        base, options["source_sha256"], options["protocol_sha256"],
        options["contract_sha256"],
    )
    require(context.get("status") == "PASS"
            and options.get("phase1_v4_source_sha256") == P0_V4["source"][2]
            and options.get("phase1_v4_protocol_sha256") == P0_V4["protocol"][2]
            and options.get("phase1_v4_contract_sha256") == P0_V4["contract"][2]
            and options.get("proposal_contract_sha256") == PROPOSAL["contract"][2],
            "independently authorize exact P0 V4 and preserve the sealed proposal")
    raw = base["read_exact"](C16["source"])
    import types

    name = "_rebar_c_v18_explicit_first_party_c16_kernel"
    require(name not in sys.modules,
            "reject a reused or substituted first-party C native compiler kernel")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + C16["source"][1]
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(module.SCHEMA
                == "rebar-phase2-owned-c-subject-buffer-source-build-v16"
                and module.VERSION == 16 and module.FAMILY == FAMILY
                and tuple(module.PHASES) == PHASES
                and tuple(module.PROCESS_NAMES) == PROCESS_NAMES
                and module.ORIGINAL_C[0] == CANONICAL_C[1]
                and module.ORIGINAL_C[1] == CANONICAL_C[2]
                and module.ADAPTER[0] == C_ADAPTER[1]
                and module.ADAPTER[1] == C_ADAPTER[2]
                and module.FEATURE["variant"][0] == C_FEATURE["variant"][1]
                and module.FEATURE["variant"][1] == C_FEATURE["variant"][2],
                "load only the immutable complete C16 compiler and actual C adapter")
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SELF = SOURCE_PATH
        module.PROTOCOL = PROTOCOL_PATH
        module.CONTRACT = CONTRACT_PATH
        module.GRAPH_VERSION = GRAPH_VERSION
        module.GRAPH = {
            role: (row[1], row[2], row[3], row[5])
            for role, row in GRAPH.items()
        }
        state["runtime_state"] = {}

        def verified_context(source_pin: str, protocol_pin: str,
                             contract_pin: str | None = None) -> dict[str, object]:
            require((source_pin, protocol_pin, contract_pin)
                    == (options["source_sha256"], options["protocol_sha256"],
                        options["contract_sha256"]),
                    "reject substituted C V18 source, protocol, or contract authority")
            return {"derived": state["variant"]}

        original_loader = module.load_source

        def audited_loader(row: object, module_name: str) -> object:
            loaded = original_loader(row, module_name)
            if row == module.KERNEL["v7"]:
                original_kernel = loaded.load_frozen_v4

                def audited_kernel() -> object:
                    kernel = original_kernel()
                    actual_toolchains: list[dict[str, object]] = []
                    for role, expected in sorted(C_TOOLCHAINS.items()):
                        path, fingerprint, size, version, executable = expected
                        require(kernel.EXPECTED_TOOLCHAINS.get(role) == expected,
                                "reject a changed pinned first-party C toolchain: "
                                + role)
                        observed, retained = kernel.authenticate_file(
                            kernel.Path(path), expected=fingerprint,
                            maximum=kernel.MAX_BINARY_BYTES,
                            exact_size=size, capture=False,
                        )
                        require(type(observed) is dict and retained is None
                                and observed.get("path") == path
                                and observed.get("sha256") == fingerprint
                                and observed.get("size_bytes") == size
                                and observed.get("executable") is executable
                                and type(observed.get("device")) is int
                                and type(observed.get("inode")) is int,
                                "reject the actual unsafe or changed C toolchain: "
                                + role)
                        actual_toolchains.append({
                            "role": role,
                            "path": observed["path"],
                            "sha256": observed["sha256"],
                            "bytes": observed["size_bytes"],
                            "device": observed["device"],
                            "inode": observed["inode"],
                            "version": version,
                            "executable": observed["executable"],
                        })
                    require(len(actual_toolchains) == 5,
                            "authenticate every actual first-party C build toolchain")
                    state["runtime_state"]["toolchain_audit_status"] = "PASS"
                    state["runtime_state"]["authenticated_toolchains"] = (
                        actual_toolchains
                    )
                    native_audit = kernel.audit_native_source(
                        state["variant"], family=FAMILY, location=CANONICAL_C[1],
                    )
                    adapter_audit = kernel.audit_python_source(
                        state["adapter"], family=FAMILY, location=C_ADAPTER[1],
                    )
                    require(type(native_audit) is dict
                            and native_audit.get("path") == CANONICAL_C[1]
                            and type(native_audit.get("native_identifier_count")) is int
                            and native_audit["native_identifier_count"] > 0
                            and native_audit.get("external_regex_dependency_count") == 0
                            and native_audit.get("cross_family_dependency_count") == 0
                            and type(adapter_audit) is dict
                            and adapter_audit.get("path") == C_ADAPTER[1]
                            and adapter_audit.get("own_native_bridge") == "_vm_native"
                            and adapter_audit.get("external_regex_dependency_count") == 0
                            and adapter_audit.get("cross_family_dependency_count") == 0,
                            "require independent first-party C and adapter token audits")
                    state["runtime_state"]["kernel"] = kernel
                    state["runtime_state"]["source_audit_status"] = "PASS"
                    state["runtime_state"]["adapter_audit_status"] = "PASS"
                    return kernel

                loaded.load_frozen_v4 = audited_kernel
            return loaded

        original_verifier = module.verify_reproducibility

        def verify_actual_phases(v8: object, v7: object, workdir: str,
                                 phases: list[object],
                                 steps: list[object]) -> dict[str, object]:
            global _ROOT_CAPTURE
            require(_ROOT_CAPTURE is None
                    and type(steps) is list and len(steps) == 14,
                    "require one actual complete fourteen-role C V18 build")
            pids: set[int] = set()
            for index, step in enumerate(steps):
                phase = PHASES[index // len(PROCESS_NAMES)]
                require(type(step) is dict
                        and step.get("name")
                            == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                        and ("phase" not in step or step.get("phase") == phase)
                        and type(step.get("pid")) is int
                        and step["pid"] > 0 and step["pid"] not in pids
                        and step.get("exit_status") == 0
                        and step.get("working_directory")
                            == "<FRESH_PRIVATE_TMP>/" + phase,
                        "reject fake, failed, borrowed, or duplicate C compiler roles")
                pids.add(step["pid"])
            descriptor, root = capture_root_descriptor(v8, workdir, phases)
            try:
                proof = original_verifier(v8, v7, workdir, phases, steps)
                require(type(proof) is dict
                        and proof.get("status") == "PASS"
                        and proof.get("unique_process_count") == 14
                        and proof.get("source_apply_count") == 2
                        and proof.get("independent_source_owner_count") == 4
                        and proof.get("byte_identical") is True
                        and proof.get("native_libraries_loaded") == 0
                        and proof.get("candidate_workers_started") == 0,
                        "preserve the actual unchanged first-party C ELF verification")
                info = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(stat.S_ISDIR(info.st_mode)
                        and stat.S_IMODE(info.st_mode) == 0o700
                        and info.st_uid == os.geteuid()
                        and (info.st_dev, info.st_ino)
                            == (root["device"], root["inode"])
                        and (named.st_dev, named.st_ino)
                            == (root["device"], root["inode"]),
                        "reject a C provenance root swapped during ELF verification")
                runtime_state = state["runtime_state"]
                require(runtime_state.get("source_audit_status") == "PASS"
                        and runtime_state.get("adapter_audit_status") == "PASS"
                        and runtime_state.get("toolchain_audit_status") == "PASS"
                        and type(runtime_state.get("authenticated_toolchains")) is list
                        and len(runtime_state["authenticated_toolchains"]) == 5,
                        "reject C provenance without first-party source and toolchain audits")
                _ROOT_CAPTURE = {
                    "root": root,
                    "phase_count": 2,
                    "unique_process_count": len(pids),
                    "compiler_process_ids": sorted(pids),
                    "source_audit_status": "PASS",
                    "adapter_audit_status": "PASS",
                    "toolchain_audit_status": "PASS",
                    "authenticated_toolchains": runtime_state[
                        "authenticated_toolchains"
                    ],
                    "original_reproducibility": "PASS",
                }
                return proof
            finally:
                os.close(descriptor)

        module.verify_context = verified_context
        module.load_source = audited_loader
        module.evidence_names = evidence_names
        module.publish_report = lambda kernel, report, label: publish_build_report(
            module, kernel, report, label, state,
        )
        module.verify_reproducibility = verify_actual_phases
        assert_fresh_root_receipt(BUILD_LABEL)
        forwarded = types.SimpleNamespace(
            build=True,
            source_sha256=options["source_sha256"],
            protocol_sha256=options["protocol_sha256"],
            contract_sha256=options["contract_sha256"],
            family=FAMILY,
            label=BUILD_LABEL,
            owned_source_sha256=options["owned_source_sha256"],
            variant_source_sha256=options["variant_source_sha256"],
        )
        result = module.run_build(forwarded)
        require(type(result) is dict and result.get("family") == FAMILY,
                "require a genuinely durable first-party C V18 build result")
        if result.get("status") != "PASS":
            require(result.get("failure_preserved") is True,
                    "preserve the real failed build without fabricating C root proof")
            return result
        return publish_root_provenance(base, module, state, result, options)
    finally:
        sys.modules.pop(name, None)


def parse_cli(values: list[str]) -> dict[str, object]:
    require(type(values) is list and all(type(value) is str for value in values),
            "require exact independently specified C V18 command arguments")
    modes = ("--self-test", "--verify-frozen-context", "--render-contract", "--build")
    chosen = [mode for mode in modes if mode in values]
    require(len(chosen) == 1 and values.count(chosen[0]) == 1,
            "require exactly one independently authorized C V18 operation")
    mode = chosen[0]
    result: dict[str, object] = {"mode": mode, "owned_source_sha256": []}
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--family": "family",
        "--label": "label",
        "--variant-source-sha256": "variant_source_sha256",
        "--variant-source-bytes": "variant_source_bytes",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
        "--proposal-contract-sha256": "proposal_contract_sha256",
    }
    index = 0
    while index < len(values):
        flag = values[index]
        if flag == mode:
            index += 1
            continue
        if flag == "--owned-source-sha256":
            require(index + 1 < len(values),
                    "reject an incomplete first-party C source pin")
            result["owned_source_sha256"].append(values[index + 1])
            index += 2
            continue
        require(flag in mapping and index + 1 < len(values),
                "reject abbreviated, unknown, or incomplete C V18 authority")
        name = mapping[flag]
        require(name not in result,
                "reject repeated first-party C build authority: " + flag)
        value: object = values[index + 1]
        if name.endswith("_bytes"):
            require(value.isascii() and value.isdecimal(),
                    "require exact positive C source byte counts")
            value = int(value)
        result[name] = value
        index += 2
    for name in ("source_sha256", "protocol_sha256"):
        require(name in result, "independently pin C V18 source and protocol")
        checked_hash(result[name], name)
    if mode == "--render-contract":
        require("contract_sha256" not in result,
                "render a canonical contract before its fingerprint exists")
    else:
        require("contract_sha256" in result,
                "independently pin the complete C V18 machine contract")
        checked_hash(result["contract_sha256"], "C V18 contract")
    build_only = (
        "family", "label", "variant_source_sha256", "variant_source_bytes",
        "phase1_v4_source_sha256", "phase1_v4_protocol_sha256",
        "phase1_v4_contract_sha256", "proposal_contract_sha256",
    )
    if mode != "--build":
        require(not result["owned_source_sha256"]
                and all(name not in result for name in build_only),
                "source-only verification never authorizes a build or native root")
        return result
    expected_sources = {
        CANONICAL_C[1] + "=" + CANONICAL_C[2],
        C_ADAPTER[1] + "=" + C_ADAPTER[2],
    }
    require(result.get("family") == FAMILY
            and result.get("label") == BUILD_LABEL
            and checked_label(BUILD_LABEL) == BUILD_LABEL
            and result.get("variant_source_sha256") == C_FEATURE["variant"][2]
            and result.get("variant_source_bytes") == C_FEATURE["variant"][3]
            and type(result.get("owned_source_sha256")) is list
            and len(result["owned_source_sha256"]) == 2
            and set(result["owned_source_sha256"]) == expected_sources,
            "independently caller-pin the exact C family, native, adapter, and variant")
    for key, expected in (
        ("phase1_v4_source_sha256", P0_V4["source"][2]),
        ("phase1_v4_protocol_sha256", P0_V4["protocol"][2]),
        ("phase1_v4_contract_sha256", P0_V4["contract"][2]),
        ("proposal_contract_sha256", PROPOSAL["contract"][2]),
    ):
        require(result.get(key) == expected,
                "independently pin current P0 V4 and the unopened public proposal")
    return result


def main() -> int:
    try:
        verify_runtime()
        base = bootstrap_rust19()
        options = parse_cli(list(sys.argv[1:]))
        mode = options["mode"]
        if mode != "--build":
            base["install_wall"]()
        if mode == "--render-contract":
            _context, state = collect_context(
                base, options["source_sha256"], options["protocol_sha256"],
            )
            result = contract_document(
                options["source_sha256"], options["protocol_sha256"], state,
            )
        elif mode == "--verify-frozen-context":
            result, _state = collect_context(
                base, options["source_sha256"], options["protocol_sha256"],
                options["contract_sha256"],
            )
        elif mode == "--self-test":
            result = self_test(
                base, options["source_sha256"], options["protocol_sha256"],
                options["contract_sha256"],
            )
        else:
            result = run_build(base, options)
        raw = encoded(base, result)
        require(0 < len(raw) <= MAX_OWNER_BYTES,
                "bound the complete canonical C V18 source-only result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if mode == "--render-contract" or result.get("status") == "PASS" else 1
    except (GateError, Exception) as error:
        result = {
            "schema": SCHEMA + "-entry-failure",
            "version": VERSION,
            "status": "FAIL",
            "family": FAMILY,
            "error_type": type(error).__name__,
            "error_message": str(error)[:8192],
            **boundary(),
        }
        try:
            if "base" in locals():
                sys.stdout.buffer.write(encoded(base, result))
                sys.stdout.buffer.flush()
            else:
                sys.stdout.write(
                    '{"schema":"' + SCHEMA
                    + '-entry-failure","status":"FAIL","error_type":"'
                    + type(error).__name__ + '"}\n'
                )
                sys.stdout.flush()
        except (OSError, TypeError, ValueError):
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
