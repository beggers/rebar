#!/usr/bin/env python3
"""Freeze a plain-language, correctness-gated Rust-versus-Python speed graph."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/render_owned_corrected_rust_speed_headline_v106.py"
PROTOCOL = "oracle/phase2/RUST-CORRECTED-SPEED-HEADLINE-V106.md"
CONTRACT = "oracle/phase2/rust-corrected-speed-headline-v106.json"
OUTPUT = "docs/evidence/candidate-current-overview-v106"
TITLE = "How fast are the different versions?"
VERSION = 106
ORIGINAL = 31_237
PUBLIC = 10_434
PRACTICE = 416
PAIRS = 1_664
SPEEDUP = 1.2424347186648022
LOWER = 1.189358106927207
UPPER = 1.301024782265517
ENGINE = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
BRIDGE = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
ADAPTER = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
BUILD = "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749"
PRIVATE_ROOT = "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c"
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756)
ORIGINAL_PASS = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-"
    "v33-rust-full-public-semantic-source-root-provenance-original-p0-v28-"
    "publication-receipt.json",
    "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064", 12067,
)
PUBLIC_PASS = (
    "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-"
    "v5-run-001-publication-receipt.json",
    "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889,
)
AUDIT = (
    "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json",
    "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203", 16427,
)
PERFORMANCE = (
    "oracle/phase2/evidence/rust-corrected-public-performance-v4-v33-corrected-"
    "performance-run-001-publication-receipt.json",
    "db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3", 118943,
)
SUMMARY = (
    "experiments/rust_corrected_public_performance_v4/v33-corrected-performance-"
    "run-001/public-416-performance-summary.raw.json",
    "7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef", 102598,
)
RAW_PAIRS = (
    "experiments/rust_corrected_public_performance_v4/v33-corrected-performance-"
    "run-001/public-416-paired-timing.raw.json",
    "2677471e5cd835b2cbf63ef2bc3e22c2069ef24953be98fa7dae1930ea980a26", 504758,
)
V4 = {
    "source": (
        "tools/run_owned_corrected_rust_public_performance_v4.py",
        "5f6b6377603098d4a229f32398cf1ea46db1bd442b364b9da78ded3a1cbe93d6", 155445,
    ),
    "protocol": (
        "oracle/phase2/RUST-CORRECTED-PUBLIC-PERFORMANCE-V4.md",
        "01bbea03b8187a457341d41866d6696778c2f2b7c11586b31cbf517c1b5be47b", 6781,
    ),
    "contract": (
        "oracle/phase2/rust-corrected-public-performance-v4.json",
        "45c8015b2a6c43a730ee759968d30f6210d494d4f95af2a6bb5ffbcf75756f7d", 42062,
    ),
}
V105 = {
    "source": (
        "tools/render_rust_same_build_correctness_overview_v105.py",
        "b2a491186f22790540ea38e13d87cce2e11ad89b5895fb21675dee6d64d2a873", 58666,
    ),
    "protocol": (
        "oracle/phase2/RUST-SAME-BUILD-CORRECTNESS-OVERVIEW-V105.md",
        "0c4f4eba1a995ee11b6db62a042319ad321409083f4ee22fcd31a265fc269051", 4483,
    ),
    "contract": (
        "oracle/phase2/rust-same-build-correctness-overview-v105.json",
        "fcce1741072f458ba45614b7b64009bb262e1ceb42be44edd2b3fb096f16ee32", 5799,
    ),
}
HISTORY = {
    "v26": {
        "summary": (
            "experiments/rust_native_architecture_public_v2/v26-anchor-public-"
            "run-001/public-416-performance-summary.raw.json",
            "33619312085764d72b9b9b6ae43cb021fb54b88d64a272ce5c183826a7a00d5e", 26200,
        ),
        "receipt": (
            "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-"
            "v26-anchor-public-run-001-publication-receipt.json",
            "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906,
        ),
        "speedup": 1.2520878685068846, "faster": 247, "slower": 169,
        "regressions": 11,
    },
    "v27": {
        "summary": (
            "experiments/rust_native_architecture_public_v2/v27-compiler-public-"
            "run-001/public-416-performance-summary.raw.json",
            "ce2d8c94d739c5f2d87f2fa65c19ef9301ee62cac7e2233b654ba25094d9e50b", 53579,
        ),
        "receipt": (
            "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-"
            "v27-compiler-public-run-001-publication-receipt.json",
            "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330,
        ),
        "speedup": 0.7967512788167544, "faster": 138, "slower": 278,
        "regressions": 143,
    },
    "v28": {
        "summary": (
            "experiments/rust_native_architecture_public_v3/v28-combined-public-"
            "run-001/public-416-performance-summary.raw.json",
            "add311f5c6734505b733988bbce0b14fccd410aa8462c17fe05f3cb4fb99f414", 25640,
        ),
        "receipt": (
            "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-"
            "v28-combined-public-run-001-publication-receipt.json",
            "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372,
        ),
        "speedup": 1.2298384265743338, "faster": 208, "slower": 208,
        "regressions": 8,
    },
}
INODES = {
    GOAL[0]: 31364044, ORIGINAL_PASS[0]: 526161, PUBLIC_PASS[0]: 525451,
    AUDIT[0]: 525089, PERFORMANCE[0]: 526289, SUMMARY[0]: 526288,
    RAW_PAIRS[0]: 526285, V4["source"][0]: 430685,
    V4["protocol"][0]: 525600, V4["contract"][0]: 525601,
    V105["source"][0]: 430849, V105["protocol"][0]: 526092,
    V105["contract"][0]: 526176,
    HISTORY["v26"]["summary"][0]: 525332,
    HISTORY["v26"]["receipt"][0]: 525333,
    HISTORY["v27"]["summary"][0]: 525425,
    HISTORY["v27"]["receipt"][0]: 525426,
    HISTORY["v28"]["summary"][0]: 525922,
    HISTORY["v28"]["receipt"][0]: 525923,
}


class Rejected(ValueError):
    """Immutable measurements, an explicit source boundary, or graph truth changed."""


def require(condition: object, reason: str) -> None:
    if condition is not True:
        raise Rejected(reason)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("ascii")


def unique(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(type(key) is str and key not in result,
                "reject repeated measurement fields")
        result[key] = value
    return result


def document(value: bytes, label: str) -> dict:
    try:
        parsed = json.loads(value, object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                Rejected("reject nonfinite measurement")))
    except (TypeError, ValueError, UnicodeError) as failure:
        raise Rejected("reject malformed measurement: " + label) from failure
    require(type(parsed) is dict and canonical(parsed) == value,
            "reject incomplete or noncanonical measurement: " + label)
    return parsed


def fingerprint(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require a complete independent SHA-256: " + label)
    return value


def same(value: object, expected: dict, label: str) -> None:
    require(type(value) is dict, "require an authenticated object: " + label)
    for key, item in expected.items():
        require(value.get(key) == item,
                "the frozen evidence changed: " + label + ": " + key)


def owners() -> tuple[tuple[str, str, int], ...]:
    historical = tuple(owner for entry in HISTORY.values()
                       for owner in (entry["summary"], entry["receipt"]))
    return (GOAL, ORIGINAL_PASS, PUBLIC_PASS, AUDIT, PERFORMANCE, SUMMARY,
            RAW_PAIRS, *V4.values(), *V105.values(), *historical)


class SourceWall:
    """Allow exact immutable plaintext owners and root-only exclusive V106 outputs."""

    def __init__(self, mode: str, approved: tuple[tuple[str, str, int], ...]):
        self.mode = mode
        self.approved = frozenset(os.path.join(ROOT, item[0]) for item in approved)
        self.outputs = frozenset(os.path.join(ROOT, OUTPUT + suffix)
                                 for suffix in (".svg", ".inputs.json", ".json"))

    def check(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            flags = arguments[2] if len(arguments) > 2 and type(arguments[2]) is int else 0
            require(type(path) is str, "reject descriptor or non-owned file access")
            writes = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT
                                   | os.O_APPEND | os.O_TRUNC))
            if writes:
                mandatory = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                require(self.mode == "graph" and path in self.outputs
                        and flags & mandatory == mandatory,
                        "reject source-mode, existing-file, or unrelated mutation")
            else:
                require(path in self.approved and flags & os.O_NOFOLLOW != 0,
                        "reject hidden proposal, private root, candidate, or archive")
            return
        if (event.startswith(("subprocess.", "socket.", "ctypes.", "os.exec", "os.spawn"))
                or event in {"os.system", "os.fork", "os.posix_spawn", "os.mkdir",
                             "os.remove", "os.rename", "os.rmdir", "os.chdir", "os.chmod",
                             "os.link", "os.symlink", "os.truncate", "os.putenv",
                             "time.time", "time.monotonic", "time.perf_counter",
                             "_thread.start_new_thread"}):
            raise Rejected("reject execution, network, clock, thread, or mutation")
        if event == "import" and arguments:
            name = arguments[0]
            require(not (type(name) is str and
                         (name in {"re", "_sre", "regex", "re2", "ctypes", "gzip"}
                          or name.startswith(("candidates.", "rebar.")))),
                    "reject matcher, candidate, native, or archive import")


def read(owner: tuple[str, str, int], approved: tuple[tuple[str, str, int], ...]
         ) -> tuple[dict, bytes]:
    require(owner in approved, "reject an unapproved evidence owner")
    relative, expected, count = owner
    descriptor = os.open(os.path.join(ROOT, relative),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_uid == os.getuid() and before.st_nlink == 1
                and before.st_size == count and before.st_dev == 2064
                and (relative not in INODES or before.st_ino == INODES[relative]),
                "immutable owner identity, inode, or mode changed: " + relative)
        blocks = []
        while True:
            block = os.read(descriptor, 1_048_576)
            if not block:
                break
            blocks.append(block)
        value = b"".join(blocks)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_uid, before.st_nlink,
                 before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                == (after.st_dev, after.st_ino, after.st_uid, after.st_nlink,
                    after.st_size, after.st_mtime_ns, after.st_ctime_ns)
                and digest(value) == expected,
                "the complete immutable owner changed: " + relative)
        return ({"path": relative, "sha256": expected, "bytes": count,
                 "device": after.st_dev, "inode": after.st_ino, "uid": after.st_uid,
                 "mode": "0600", "nlink": after.st_nlink}, value)
    finally:
        os.close(descriptor)


def source_effects() -> dict:
    return {
        "candidate_source_owners_opened_by_graph": 0,
        "candidate_workers_started_by_graph": 0,
        "reference_workers_started_by_graph": 0,
        "compiler_processes_started_by_graph": 0,
        "native_binary_files_opened_by_graph": 0,
        "native_binary_metadata_probes_by_graph": 0,
        "native_libraries_loaded_by_graph": 0,
        "private_build_roots_opened_by_graph": 0,
        "private_build_roots_statted_by_graph": 0,
        "compressed_archives_opened_by_graph": 0,
        "compressed_archives_statted_by_graph": 0,
        "compressed_archives_inflated_by_graph": 0,
        "raw_public_case_archives_opened_by_graph": 0,
        "raw_public_case_archives_statted_by_graph": 0,
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "seed_files_opened_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_holdout_opened": False,
        "clock_samples_by_graph": 0,
        "timing_trials_run_by_graph": 0,
    }


def verify_original(value: dict) -> None:
    same(value, {
        "status": "PASS", "publication_status": "PASS", "family": "rust",
        "candidate_status": "PASS", "candidate_original_oracle_pass": True,
        "original_suite_correctness_qualified": True, "candidate_qualified": False,
        "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
        "suite_count": 13, "completed_suite_count": 13,
        "actual_candidate_workers": 13, "distinct_worker_process_id_count": 13,
        "infrastructure_failure_count": 0,
        "all_original_observation_vectors_complete": True,
        "actual_v28_build_receipt_sha256": BUILD,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "actual same-build 31,237/31,237 original PASS")
    for fields, expected in (
        (("native_engine_sha256", "actual_v33_native_engine_sha256"), ENGINE),
        (("native_bridge_sha256", "actual_v33_native_bridge_sha256"), BRIDGE),
        (("corrected_public_adapter_sha256", "v33_adapter_sha256",
          "actual_v33_adapter_sha256"), ADAPTER),
    ):
        found = [value[item] for item in fields if item in value]
        require(bool(found) and all(item == expected for item in found),
                "the original PASS must use the exact engine, bridge, and adapter")
    suites = value.get("suite_integrity")
    workers = value.get("actual_worker_process_ids")
    require(type(suites) is list and len(suites) == 13 and type(workers) is list
            and len(workers) == 13 and len(set(workers)) == 13,
            "require thirteen actual independent original correctness workers")
    require(sum(item.get("case_execution_denominator", 0) for item in suites) == ORIGINAL
            and all(item.get("verified_passing_case_count")
                    == item.get("case_execution_denominator")
                    and item.get("mismatch_count") == 0
                    and item.get("fully_observed") is True
                    and item.get("pid") in workers for item in suites),
            "preserve every original same-build correctness result")


def verify_history(state: dict) -> None:
    receipt_history = state["performance"].get("historical_public_performance")
    embedded_history = state["summary"].get("historical_v26_v27_v28")
    require(receipt_history == embedded_history,
            "the corrected receipt and corrected summary disagree about history")
    for label, expected in HISTORY.items():
        receipt = state["history"][label]["receipt"]
        summary = state["history"][label]["summary"]
        require(digest(canonical(receipt)) == expected["receipt"][1]
                and digest(canonical(summary)) == expected["summary"][1],
                "the complete independently authenticated history changed: " + label)
        same(receipt, {
            "status": "PASS", "candidate_qualified": False,
            "public_10434_case_count": PUBLIC,
            "public_10434_correctness_status": "FAIL",
            "public_10434_mismatch_count": 1145,
            "public_416_timing_status": "PASS", "paired_row_count": PAIRS,
            "qualified_independent_family_count": 0,
            "winner_selected": False,
        }, "historical " + label + " is an explicitly failed experiment")
        require(receipt.get("performance_summary") == summary,
                "the historical publication omitted measured results: " + label)
        same(summary, {
            "case_count": PRACTICE, "paired_row_count": PAIRS,
            "geomean_speedup_vs_stdlib": expected["speedup"],
            "faster_case_count": expected["faster"],
            "slower_case_count": expected["slower"], "equal_case_count": 0,
            "regression_over_20_percent_count": expected["regressions"],
        }, "historical speed and every loss: " + label)
        embedded = embedded_history.get(label)
        same(embedded, {"case_count": PRACTICE, "paired_row_count": PAIRS,
                        "faster_case_count": expected["faster"],
                        "regression_over_20_percent_count": expected["regressions"],
                        "summary_sha256": expected["summary"][1]},
             "corrected publication historical measurement: " + label)
        require(float(embedded["geomean_speedup_vs_stdlib_display"])
                == expected["speedup"],
                "the corrected publication historical speed changed: " + label)


def verify(state: dict) -> None:
    for label, owner in (("original", ORIGINAL_PASS), ("public", PUBLIC_PASS),
                         ("audit", AUDIT), ("performance", PERFORMANCE),
                         ("summary", SUMMARY), ("pairs", RAW_PAIRS),
                         ("v4_contract", V4["contract"]),
                         ("v105_contract", V105["contract"])):
        require(digest(canonical(state[label])) == owner[1],
                "the complete authenticated owner changed: " + label)
    require(digest(state["goal"]) == GOAL[1], "the immutable user goal changed")
    verify_original(state["original"])
    same(state["public"], {
        "status": "PASS", "candidate_status": "PASS",
        "public_10434_correctness_status": "PASS",
        "public_10434_case_count": PUBLIC,
        "public_10434_verified_passing_case_count": PUBLIC,
        "public_10434_mismatch_count": 0,
        "v33_native_engine_sha256": ENGINE, "v33_native_bridge_sha256": BRIDGE,
        "v33_adapter_sha256": ADAPTER,
        "v33_publication_sha256": BUILD, "v33_root_sha256": PRIVATE_ROOT,
        "v5_static_pass_sha256": AUDIT[1], "candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "hidden_cases_read": 0, "winner_selected": False,
    }, "actual same-build 10,434/10,434 broader public PASS")
    same(state["audit"], {
        "status": "PASS", "audited_family": "rust", "finding_count": 0,
        "findings": [], "external_regex_libraries": 0,
        "external_regex_packages": 0, "external_regex_symbols": 0,
        "cross_family_dependencies": 0,
        "clean_candidate_source_static_non_delegation": "PASS",
        "clean_candidate_native_elf_static_non_delegation": "PASS",
        "candidate_qualified": False, "candidate_executions": 0,
        "native_library_loads": 0,
        "runtime_non_delegation": "NOT ESTABLISHED; STATIC SOURCE AND ELF AUDIT ONLY",
        "winner_selected": False,
    }, "the static-only first-party audit")
    same(state["v4_contract"], {
        "schema": "rebar-owned-corrected-rust-public-performance-v4-source-freeze",
        "candidate_qualified": False, "qualified_independent_family_count": 0,
        "winner_selected": False,
    }, "the actually frozen V4 public-performance controller")
    same(state["v105_contract"], {
        "schema": "rebar-rust-same-build-correctness-overview-v105-source-freeze",
        "version": 105, "candidate_qualified": False,
        "qualified_candidate_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "winner_selected": False,
    }, "the frozen same-build correctness predecessor")
    receipt = state["performance"]
    same(receipt, {
        "schema": "rebar-owned-corrected-rust-public-performance-v4-durable-publication-receipt",
        "status": "PASS", "architecture": "v33",
        "performance_evidence_scope": "CORRECTNESS-GATED PUBLIC 416 ONLY",
        "public_416_timing_status": "PASS", "paired_row_count": PAIRS,
        "worker_process_count": 12,
        "exact_v33_original_31237_case_count": ORIGINAL,
        "exact_v33_original_31237_correctness_status": "PASS",
        "exact_v33_original_31237_mismatch_count": 0,
        "public_10434_case_count": PUBLIC,
        "public_10434_correctness_status": "PASS",
        "public_10434_mismatch_count": 0,
        "native_engine_sha256": ENGINE, "native_bridge_sha256": BRIDGE,
        "corrected_adapter_sha256": ADAPTER,
        "source_sha256": V4["source"][1],
        "protocol_sha256": V4["protocol"][1],
        "contract_sha256": V4["contract"][1],
        "v33_exact_original_pass_sha256": ORIGINAL_PASS[1],
        "v33_public_pass_sha256": PUBLIC_PASS[1],
        "v5_static_pass_sha256": AUDIT[1],
        "v33_publication_sha256": BUILD, "v33_root_sha256": PRIVATE_ROOT,
        "candidate_qualified": False, "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "static_non_delegation": "PASS; SOURCE/ELF STATIC AUDIT ONLY",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "proposal_content_open_count": 0, "proposal_metadata_probe_count": 0,
        "controller_final_holdout_content_open_count": 0,
        "hidden_case_files_generated": 0, "hidden_cases_read": 0,
        "canonical_candidate_modified": False, "winner_selected": False,
    }, "the actual correctness-gated V4 public-performance publication")
    same(receipt.get("public_416_correctness_gate"), {
        "status": "PASS", "case_count": PRACTICE, "mismatch_count": 0,
        "all_mismatches": [], "completed_before_any_timing": True,
    }, "the actual practice correctness gate")
    worker_ids = receipt.get("worker_process_ids")
    require(type(worker_ids) is list and len(worker_ids) == 12
            and len(set(worker_ids)) == 12
            and all(type(value) is int and value > 0 for value in worker_ids),
            "the actual performance run requires twelve distinct real workers")
    summary = state["summary"]
    require(receipt.get("performance_summary") == summary,
            "the complete independently authenticated V4 speed summary changed")
    same(summary, {
        "schema": "rebar-owned-corrected-rust-public-performance-v4-actual-public-performance-summary",
        "status": "PASS", "case_count": PRACTICE, "paired_rounds": 4,
        "paired_row_count": PAIRS, "raw_pair_count": PAIRS,
        "geomean_speedup_vs_stdlib": SPEEDUP,
        "faster_case_count": 252, "slower_case_count": 164,
        "equal_case_count": 0, "regression_over_20_percent_count": 14,
        "correctness_checks_per_engine_per_pair": 5,
        "counterbalanced_process_order": True, "equal_case_weight": True,
        "iterations": 3, "warmups": 1,
    }, "all actual corrected Rust speed results and losses")
    same(summary.get("confidence_interval_95"),
         {"lower": LOWER, "upper": UPPER, "resamples": 400},
         "the actual 95 percent uncertainty interval")
    same(summary.get("identical_process_environment"),
         {"LC_ALL": "C", "PATH": "/usr/bin:/bin",
          "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
          "PYTHONMALLOC": "malloc"}, "the same controlled worker environment")
    ratios = summary.get("case_ratios")
    rankings = summary.get("ranked_cases_by_speedup")
    regressions = summary.get("all_regressions_over_20_percent")
    require(type(ratios) is dict and len(ratios) == PRACTICE
            and type(rankings) is list and len(rankings) == PRACTICE
            and type(regressions) is list and len(regressions) == 14
            and len({item.get("case") for item in rankings}) == PRACTICE
            and len({item.get("case") for item in regressions}) == 14,
            "retain every measured case and all fourteen severe regressions")
    require(sum(value > 1.0 for value in ratios.values()) == 252
            and sum(value < 1.0 for value in ratios.values()) == 164
            and all(type(value) is float and value > 0.0
                    for value in ratios.values())
            and all(type(item.get("case")) is str
                    and item["case"] in ratios
                    and item.get("speedup_vs_stdlib") == ratios[item["case"]]
                    for item in rankings),
            "preserve all 252 faster cases and all 164 slower cases")
    for item in regressions:
        same(item, {"case": item.get("case"), "cohort": item.get("cohort"),
                    "operation": item.get("operation"),
                    "baseline_elapsed_ns": item.get("baseline_elapsed_ns"),
                    "rust_elapsed_ns": item.get("rust_elapsed_ns"),
                    "slowdown_ratio": item.get("slowdown_ratio")},
             "a complete actual >20% regression row")
        require(type(item.get("case")) is str and item["case"] in ratios
                and type(item.get("cohort")) is str
                and type(item.get("operation")) is str
                and type(item.get("baseline_elapsed_ns")) is int
                and type(item.get("rust_elapsed_ns")) is int
                and type(item.get("slowdown_ratio")) is float
                and item["slowdown_ratio"] > 1.2
                and item["rust_elapsed_ns"] / item["baseline_elapsed_ns"]
                    == item["slowdown_ratio"]
                and ratios[item["case"]] < 1.0,
                "never erase or misstate a real corrected Rust regression")
    pairs = state["pairs"]
    same(pairs, {
        "schema": "rebar-owned-corrected-rust-public-performance-v4-paired-rows",
        "matrix_sha256": summary["matrix_sha256"],
        "rows_sha256": "02ded9a1726683ff3b369730c52b29f00decdc012941b8002d2dd379720d6529",
    }, "all 1,664 actual paired timing observations")
    raw = pairs.get("rows")
    require(type(raw) is list and len(raw) == PAIRS
            and digest(canonical(raw)) == pairs["rows_sha256"]
            and len({item.get("case") for item in raw}) == PRACTICE
            and sum(item.get("pair_order") == ["stdlib", "rust"] for item in raw) == 832
            and sum(item.get("pair_order") == ["rust", "stdlib"] for item in raw) == 832,
            "authenticate every counterbalanced actual timing pair")
    cases = {}
    for row in raw:
        require(type(row.get("baseline_elapsed_ns")) is int
                and row["baseline_elapsed_ns"] > 0
                and type(row.get("rust_elapsed_ns")) is int
                and row["rust_elapsed_ns"] > 0
                and row.get("case") in ratios
                and row.get("correctness_checks_per_engine") == 5
                and row.get("iterations") == 3
                and row.get("round") in (0, 1, 2, 3),
                "require a genuine positive paired timing observation")
        cases[row["case"]] = cases.get(row["case"], 0) + 1
    require(len(cases) == PRACTICE and all(value == 4 for value in cases.values()),
            "each of the 416 practice tasks requires four actual paired rounds")
    memory = summary.get("memory_summary")
    require(receipt.get("memory_summary") == memory,
            "the actual speed and publication memory measurements disagree")
    same(memory.get("rust"), {"tracemalloc_peak_bytes": 111026,
                               "maximum_rss_kib": 44032,
                               "public_case_executions": 1248,
                               "allocated_blocks_delta": 789},
         "the actual Rust memory measurement")
    same(memory.get("stdlib"), {"tracemalloc_peak_bytes": 181952,
                                 "maximum_rss_kib": 44032,
                                 "public_case_executions": 1248,
                                 "allocated_blocks_delta": 1090},
         "the actual Python baseline memory measurement")
    verify_history(state)


def historical_rows(state: dict) -> list[dict]:
    return [{
        "version": label.upper(), "label": label.upper() + " earlier experiment",
        "speed_relative_to_python": expected["speedup"],
        "practice_case_count": PRACTICE,
        "faster_case_count": expected["faster"],
        "slower_case_count": expected["slower"],
        "regression_over_20_percent_count": expected["regressions"],
        "full_public_correctness_status": "FAIL",
        "full_public_mismatch_count": 1145,
        "candidate_qualified": False,
        "summary": state["metadata"][expected["summary"][0]],
        "receipt": state["metadata"][expected["receipt"][0]],
    } for label, expected in HISTORY.items()]


def slower_rows(state: dict) -> list[dict]:
    return [{"case": row["case"], "cohort": row["cohort"],
             "operation": row["operation"],
             "speedup_vs_stdlib": row["speedup_vs_stdlib"]}
            for row in state["summary"]["ranked_cases_by_speedup"]
            if row["speedup_vs_stdlib"] < 1.0]


def measurement(state: dict) -> dict:
    return {
        "scope": "CORRECTNESS-GATED PUBLIC 416 ONLY; NOT THE FINAL BENCHMARK",
        "python_baseline_speed": 1.0,
        "rust_fully_correct_speed": SPEEDUP,
        "confidence_interval_95": {"lower": LOWER, "upper": UPPER},
        "practice_case_count": PRACTICE, "paired_timing_row_count": PAIRS,
        "paired_rounds_per_case": 4,
        "faster_case_count": 252, "slower_case_count": 164,
        "equal_case_count": 0, "regression_over_20_percent_count": 14,
        "all_regressions_over_20_percent":
            state["summary"]["all_regressions_over_20_percent"],
        "all_164_slower_cases": slower_rows(state),
        "rust_peak_traced_memory_bytes": 111026,
        "python_peak_traced_memory_bytes": 181952,
        "rust_maximum_rss_kib": 44032,
        "python_maximum_rss_kib": 44032,
        "memory_public_case_executions_per_engine": 1248,
        "historical_experiments": historical_rows(state),
    }


def freeze(state: dict) -> dict:
    return {
        "schema": "rebar-owned-corrected-rust-speed-headline-v106-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; FRIENDLY SPEED GRAPH NOT RENDERED",
        "title": TITLE, "goal_sha256": GOAL[1],
        "source": state["metadata"][SOURCE],
        "protocol": state["metadata"][PROTOCOL],
        "previous_v105_source_freeze": {
            label: state["metadata"][owner[0]] for label, owner in V105.items()
        },
        "actual_v4_public_performance_source_freeze": {
            label: state["metadata"][owner[0]] for label, owner in V4.items()
        },
        "actual_original_pass": state["metadata"][ORIGINAL_PASS[0]],
        "actual_broader_public_pass": state["metadata"][PUBLIC_PASS[0]],
        "actual_static_audit": state["metadata"][AUDIT[0]],
        "actual_corrected_performance_receipt": state["metadata"][PERFORMANCE[0]],
        "actual_complete_performance_summary": state["metadata"][SUMMARY[0]],
        "actual_all_1664_paired_rows": state["metadata"][RAW_PAIRS[0]],
        "same_build": {"native_engine_sha256": ENGINE,
                        "native_bridge_sha256": BRIDGE,
                        "complete_adapter_sha256": ADAPTER,
                        "build_publication_sha256": BUILD,
                        "original_case_count": ORIGINAL,
                        "original_mismatch_count": 0,
                        "broader_public_case_count": PUBLIC,
                        "broader_public_mismatch_count": 0},
        "actual_measurement": measurement(state),
        "graph_publication": {
            "authorization": "ROOT ONLY AFTER SOURCE, PROTOCOL, AND CONTRACT COMMIT AND PUSH",
            "svg": OUTPUT + ".svg", "inputs": OUTPUT + ".inputs.json",
            "summary": OUTPUT + ".json", "actual_graph_rendered": False,
            "existing_graphs_mutated": False,
        },
        **source_effects(),
        "candidate_qualified": False, "qualified_candidate_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "runtime_non_delegation": "NOT ESTABLISHED; STATIC AUDIT ONLY",
        "final_benchmark_measured": False,
        "undefined_behavior": "NOT MEASURED", "winner_selected": False,
    }


def escape(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def image(state: dict) -> bytes:
    regressions = state["summary"]["all_regressions_over_20_percent"]
    description = (
        "Python is the 1.00-times baseline. Fully correct Rust is 1.24 times "
        "as fast, with an observed 1.19 to 1.30 range. It passed 31,237 original "
        "checks and 10,434 separate broader checks. It was faster on 252 of 416 "
        "practice tasks, slower on 164, including 14 shown below that were over "
        "20 percent slower. Earlier V26, V27, and V28 results are 1.25, 0.80, "
        "and 1.23 times baseline but failed 1,145 broader checks. Rust traced "
        "111,026 peak bytes versus Python 181,952; process peaks were equal. "
        "This is a public practice result, not a final qualification or winner."
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1420" '
        'viewBox="0 0 1500 1420" role="img" aria-labelledby="title description">',
        '<title id="title">How fast are the different versions?</title>',
        '<desc id="description">' + escape(description) + '</desc>',
        '<rect width="1500" height="1420" rx="26" fill="#f8fafc"/>',
        '<text x="64" y="90" fill="#0f172a" font-size="42" '
        'font-family="system-ui,sans-serif" font-weight="760">'
        'How fast are the different versions?</text>',
        '<text x="67" y="128" fill="#475569" font-size="20" '
        'font-family="system-ui,sans-serif">'
        'Python is 1.00×. Longer bars mean faster. Each version ran the same 416 public tasks.</text>',
        '<rect x="62" y="161" width="1376" height="489" rx="20" '
        'fill="#ffffff" stroke="#e2e8f0"/>',
        '<text x="92" y="207" fill="#334155" font-size="15" '
        'font-family="system-ui,sans-serif" font-weight="700">VERSION</text>',
        '<text x="587" y="207" fill="#334155" font-size="15" '
        'font-family="system-ui,sans-serif" font-weight="700">SPEED COMPARED WITH PYTHON</text>',
        '<line x1="987" y1="224" x2="987" y2="590" stroke="#94a3b8" '
        'stroke-width="2" stroke-dasharray="6 5"/>',
        '<text x="956" y="612" fill="#475569" font-size="14" '
        'font-family="system-ui,sans-serif">1.00×</text>',
    ]
    rows = (
        ("Rust — fully correct", SPEEDUP, "#059669", "#d1fae5",
         "PASSED ALL ORIGINAL + BROADER CHECKS", True),
        ("Python — original", 1.0, "#64748b", "#f1f5f9",
         "REFERENCE VERSION", False),
        ("V26 — earlier experiment", HISTORY["v26"]["speedup"], "#d97706", "#fff7ed",
         "FAILED 1,145 BROADER CHECKS", False),
        ("V27 — earlier experiment", HISTORY["v27"]["speedup"], "#d97706", "#fff7ed",
         "FAILED 1,145 BROADER CHECKS", False),
        ("V28 — earlier experiment", HISTORY["v28"]["speedup"], "#d97706", "#fff7ed",
         "FAILED 1,145 BROADER CHECKS", False),
    )
    for index, (label, ratio, color, background, note, highlight) in enumerate(rows):
        top = 229 + index * 74
        parts += [
            f'<rect x="77" y="{top}" width="1346" height="66" rx="12" '
            f'fill="{background}"/>',
            f'<text x="96" y="{top + 26}" fill="#0f172a" font-size="17" '
            f'font-family="system-ui,sans-serif" font-weight="'
            f'{"740" if highlight else "620"}">{escape(label)}</text>',
            f'<text x="97" y="{top + 48}" fill="{color}" font-size="11" '
            'font-family="system-ui,sans-serif" font-weight="720">'
            f'{escape(note)}</text>',
            f'<rect x="588" y="{top + 12}" width="{round(ratio * 399)}" '
            f'height="30" rx="7" fill="{color}"/>',
            f'<text x="{602 + round(ratio * 399)}" y="{top + 35}" '
            'fill="#0f172a" font-size="21" '
            f'font-family="system-ui,sans-serif" font-weight="740">{ratio:.2f}×</text>',
        ]
    parts += [
        '<rect x="62" y="675" width="670" height="158" rx="18" '
        'fill="#ecfdf5" stroke="#a7f3d0"/>',
        '<text x="86" y="715" fill="#065f46" font-size="21" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'Fully correct Rust: about 24% faster overall</text>',
        '<text x="88" y="751" fill="#064e3b" font-size="18" '
        'font-family="system-ui,sans-serif">'
        'Typical measured range: 1.19× to 1.30× Python</text>',
        '<text x="88" y="785" fill="#065f46" font-size="15" '
        'font-family="system-ui,sans-serif">'
        '252 tasks faster · 164 slower · 14 more than 20% slower</text>',
        '<text x="88" y="812" fill="#065f46" font-size="13" '
        'font-family="system-ui,sans-serif">'
        '31,237 / 31,237 original + 10,434 / 10,434 broader checks passed</text>',
        '<rect x="752" y="675" width="686" height="158" rx="18" '
        'fill="#eff6ff" stroke="#bfdbfe"/>',
        '<text x="777" y="715" fill="#1e3a8a" font-size="21" '
        'font-family="system-ui,sans-serif" font-weight="750">Memory used</text>',
        '<text x="778" y="751" fill="#1e40af" font-size="18" '
        'font-family="system-ui,sans-serif">'
        'Tracked peak: Rust 111,026 bytes · Python 181,952 bytes</text>',
        '<text x="778" y="785" fill="#1e40af" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'Whole-process peak: both 44,032 KiB</text>',
        '<text x="778" y="812" fill="#1e40af" font-size="13" '
        'font-family="system-ui,sans-serif">'
        'Same 1,248 public executions were profiled for each version.</text>',
        '<rect x="62" y="856" width="1376" height="392" rx="20" '
        'fill="#ffffff" stroke="#e2e8f0"/>',
        '<text x="87" y="897" fill="#0f172a" font-size="22" '
        'font-family="system-ui,sans-serif" font-weight="750">'
        'Every task where fully correct Rust was more than 20% slower</text>',
        '<text x="89" y="928" fill="#475569" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'All 14 are shown. All 164 slower tasks remain in the accompanying data.</text>',
    ]
    for index, row in enumerate(regressions):
        column = index // 7
        line = index % 7
        x = 90 + column * 680
        y = 969 + line * 37
        short_case = row["case"].rsplit(".", 1)[-1]
        label = f'#{short_case}  {row["operation"]}'
        ratio = f'{row["slowdown_ratio"]:.2f}× slower'
        parts += [
            f'<text x="{x}" y="{y}" fill="#334155" font-size="15" '
            f'font-family="system-ui,sans-serif">{escape(label)}</text>',
            f'<text x="{x + 445}" y="{y}" fill="#b45309" font-size="15" '
            f'font-family="system-ui,sans-serif" font-weight="700">{escape(ratio)}</text>',
        ]
    parts += [
        '<rect x="62" y="1268" width="1376" height="107" rx="16" '
        'fill="#fff7ed" stroke="#fed7aa"/>',
        '<text x="87" y="1307" fill="#9a3412" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="720">'
        'The earlier experiments are not fully correct. This is not a final winner.</text>',
        '<text x="88" y="1341" fill="#7c2d12" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'Public practice only · no hidden final test opened · runtime independence not yet established</text>',
        '</svg>\n',
    ]
    return "".join(parts).encode("utf-8")


def graph(state: dict, source_sha: str, source_bytes: int,
          contract_sha: str, contract_bytes: int) -> dict:
    measured = measurement(state)
    common = {
        "version": VERSION, "title": TITLE, "goal_sha256": GOAL[1],
        "python": "3.14.6", "actual_current_graph_predecessor_version": 105,
        "source": {"path": SOURCE, "sha256": source_sha, "bytes": source_bytes},
        "protocol": state["metadata"][PROTOCOL],
        "contract": {"path": CONTRACT, "sha256": contract_sha, "bytes": contract_bytes},
        "actual_original_pass": state["metadata"][ORIGINAL_PASS[0]],
        "actual_broader_public_pass": state["metadata"][PUBLIC_PASS[0]],
        "actual_corrected_performance_receipt": state["metadata"][PERFORMANCE[0]],
        "actual_complete_performance_summary": state["metadata"][SUMMARY[0]],
        "actual_all_1664_paired_rows": state["metadata"][RAW_PAIRS[0]],
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE,
        "same_exact_native_bridge_sha256": BRIDGE,
        "same_exact_complete_adapter_sha256": ADAPTER,
        "original_case_execution_denominator": ORIGINAL,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "broader_public_counted_in_original_denominator": False,
        "measurement": measured,
        "baseline_speed_relative_to_python": 1.0,
        "rust_fully_correct_speed_relative_to_python": SPEEDUP,
        "confidence_interval_95_lower": LOWER,
        "confidence_interval_95_upper": UPPER,
        "faster_case_count": 252, "slower_case_count": 164,
        "regression_over_20_percent_count": 14,
        "all_regressions_over_20_percent": measured["all_regressions_over_20_percent"],
        "all_164_slower_cases": measured["all_164_slower_cases"],
        "historical_experiments": measured["historical_experiments"],
        "rust_peak_traced_memory_bytes": 111026,
        "python_peak_traced_memory_bytes": 181952,
        "rust_maximum_rss_kib": 44032,
        "python_maximum_rss_kib": 44032,
        "memory_public_case_executions_per_engine": 1248,
        **source_effects(),
        "static_first_party_non_delegation": "PASS; STATIC AUDIT ONLY",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "final_benchmark_measured": False,
        "winner_selected": False,
    }
    inputs = {**common,
              "schema": "rebar-candidate-corrected-rust-speed-headline-v106-inputs"}
    summary = {**common,
               "schema": "rebar-candidate-corrected-rust-speed-headline-v106-summary",
               "status": "PASS",
               "status_scope": "AUTHENTICATED SAME-BUILD PUBLIC PRACTICE GRAPH ONLY",
               "candidate_original_oracle_pass": True,
               "original_suite_correctness_qualified": True,
               "broader_public_correctness_pass": True,
               "all_regression_rows_preserved": True,
               "all_slower_case_rows_preserved": True,
               "historical_experiments_correctness_qualified": False,
               "historical_v26_public_mismatch_count": 1145,
               "historical_v27_public_mismatch_count": 1145,
               "historical_v28_public_mismatch_count": 1145}
    return {"svg": image(state), "inputs": canonical(inputs),
            "summary": canonical(summary)}


def validate_graph(state: dict, value: dict, source_sha: str, source_bytes: int,
                   contract_sha: str, contract_bytes: int) -> None:
    require(value == graph(state, source_sha, source_bytes, contract_sha, contract_bytes),
            "the complete public speed graph is not deterministic")
    inputs = document(value["inputs"], "speed graph inputs")
    summary = document(value["summary"], "speed graph publication")
    same(summary, {
        "version": VERSION, "title": TITLE,
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE,
        "same_exact_native_bridge_sha256": BRIDGE,
        "same_exact_complete_adapter_sha256": ADAPTER,
        "original_case_execution_denominator": ORIGINAL,
        "original_verified_passing_case_count": ORIGINAL,
        "original_semantic_mismatch_count": 0,
        "broader_public_case_execution_denominator": PUBLIC,
        "broader_public_verified_passing_case_count": PUBLIC,
        "broader_public_semantic_mismatch_count": 0,
        "broader_public_counted_in_original_denominator": False,
        "baseline_speed_relative_to_python": 1.0,
        "rust_fully_correct_speed_relative_to_python": SPEEDUP,
        "confidence_interval_95_lower": LOWER,
        "confidence_interval_95_upper": UPPER,
        "faster_case_count": 252, "slower_case_count": 164,
        "regression_over_20_percent_count": 14,
        "rust_peak_traced_memory_bytes": 111026,
        "python_peak_traced_memory_bytes": 181952,
        "rust_maximum_rss_kib": 44032,
        "python_maximum_rss_kib": 44032,
        "memory_public_case_executions_per_engine": 1248,
        "candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout_proposal_files_opened_by_graph": 0,
        "holdout_proposal_files_statted_by_graph": 0,
        "holdout_cases_opened_by_graph": 0,
        "hidden_cases_read_by_graph": 0,
        "final_benchmark_measured": False,
        "winner_selected": False,
        "all_regression_rows_preserved": True,
        "all_slower_case_rows_preserved": True,
        "historical_experiments_correctness_qualified": False,
    }, "never exaggerate, hide losses, or imply final candidate qualification")
    require(inputs["measurement"] == summary["measurement"]
            and inputs["all_164_slower_cases"] == slower_rows(state)
            and len(inputs["all_164_slower_cases"]) == 164
            and inputs["all_regressions_over_20_percent"]
                == state["summary"]["all_regressions_over_20_percent"]
            and len(inputs["all_regressions_over_20_percent"]) == 14
            and inputs["historical_experiments"] == historical_rows(state),
            "preserve every corrected loss and every disqualified historical row")
    required = (
        "How fast are the different versions?", "Python is 1.00×",
        "Rust — fully correct", "Python — original",
        "V26 — earlier experiment", "V27 — earlier experiment",
        "V28 — earlier experiment", "PASSED ALL ORIGINAL + BROADER CHECKS",
        "FAILED 1,145 BROADER CHECKS", "1.24×", "1.25×", "0.80×", "1.23×",
        "1.19× to 1.30×", "252 tasks faster · 164 slower · 14 more than 20% slower",
        "31,237 / 31,237 original + 10,434 / 10,434 broader checks passed",
        "Rust 111,026 bytes · Python 181,952 bytes", "both 44,032 KiB",
        "All 14 are shown. All 164 slower tasks remain in the accompanying data.",
        "no hidden final test opened", "runtime independence not yet established",
        "not a final winner", 'role="img"', 'aria-labelledby="title description"',
    )
    for item in required:
        require(item.encode("utf-8") in value["svg"],
                "the clear accessible chart omitted: " + item)
    for regression in state["summary"]["all_regressions_over_20_percent"]:
        short_case = regression["case"].rsplit(".", 1)[-1]
        require(("#" + short_case).encode("ascii") in value["svg"]
                and regression["operation"].encode("ascii") in value["svg"],
                "the visible chart concealed a >20% regression")
    for forbidden in (b"141557760", b"141,557,760", b"226492416", b"226,492,416"):
        require(all(forbidden not in value[item] for item in ("svg", "inputs", "summary")),
                "never disclose or inspect retired/final proposal details")


def different(value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is float:
        return value + 0.125
    if type(value) is str:
        return value + " CHANGED"
    if type(value) is list:
        return value + ["CHANGED"]
    if type(value) is dict:
        return {**value, "__v106_hostile": True}
    if value is None:
        return "CHANGED"
    raise Rejected("unsupported adversarial speed graph field")


def controls(state: dict, result: dict, source_sha: str, source_bytes: int,
             contract_sha: str, contract_bytes: int) -> int:
    observed = []

    def reject_context(label: str, action) -> None:
        changed = copy.deepcopy(state)
        action(changed)
        try:
            verify(changed)
        except (Rejected, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):
            observed.append(label)
            return
        raise Rejected("unsafe speed evidence was accepted: " + label)

    for owner in ("original", "public", "audit", "performance", "summary",
                  "pairs", "v4_contract", "v105_contract"):
        for key in sorted(state[owner]):
            reject_context(owner + " changed " + key,
                           lambda hostile, name=owner, field=key:
                           hostile[name].__setitem__(field,
                                                      different(hostile[name][field])))
    for label in HISTORY:
        for owner in ("summary", "receipt"):
            for key in sorted(state["history"][label][owner]):
                reject_context(label + " " + owner + " changed " + key,
                               lambda hostile, version=label, name=owner, field=key:
                               hostile["history"][version][name].__setitem__(
                                   field,
                                   different(hostile["history"][version][name][field])))
    for index in range(14):
        reject_context("suppressed actual severe regression " + str(index),
                       lambda hostile, position=index:
                       hostile["summary"]["all_regressions_over_20_percent"].pop(position))
    for case in state["summary"]["case_ratios"]:
        reject_context("changed measured case " + case,
                       lambda hostile, name=case:
                       hostile["summary"]["case_ratios"].__setitem__(
                           name, different(hostile["summary"]["case_ratios"][name])))

    def reject_output(label: str, owner: str, field: str, replacement: object) -> None:
        changed = dict(result)
        payload = document(changed[owner], "hostile graph output")
        payload[field] = replacement
        changed[owner] = canonical(payload)
        try:
            validate_graph(state, changed, source_sha, source_bytes,
                           contract_sha, contract_bytes)
        except (Rejected, ValueError, TypeError, KeyError, IndexError):
            observed.append(label)
            return
        raise Rejected("dishonest speed graph output was accepted: " + label)

    for owner in ("inputs", "summary"):
        for key, replacement in (
            ("title", "Which implementation won?"),
            ("baseline_speed_relative_to_python", 0.9),
            ("rust_fully_correct_speed_relative_to_python", 2.0),
            ("confidence_interval_95_lower", 1.5),
            ("confidence_interval_95_upper", 3.0),
            ("faster_case_count", 416), ("slower_case_count", 0),
            ("regression_over_20_percent_count", 0),
            ("all_164_slower_cases", []),
            ("all_regressions_over_20_percent", []),
            ("historical_experiments", []),
            ("original_case_execution_denominator", ORIGINAL + PUBLIC),
            ("broader_public_case_execution_denominator", PUBLIC - 1),
            ("rust_peak_traced_memory_bytes", 1),
            ("python_maximum_rss_kib", 1),
            ("runtime_non_delegation", "ESTABLISHED"),
            ("candidate_qualified", True),
            ("qualified_independent_family_count", 3),
            ("final_benchmark_measured", True),
            ("holdout_proposal_files_opened_by_graph", 1),
            ("holdout_proposal_files_statted_by_graph", 1),
            ("hidden_cases_read_by_graph", 1),
            ("winner_selected", True),
        ):
            reject_output(owner + " dishonestly changed " + key,
                          owner, key, replacement)
    wall = state["wall"]

    def reject_wall(label: str, event: str, arguments: tuple) -> None:
        try:
            wall.check(event, arguments)
        except Rejected:
            observed.append(label)
            return
        raise Rejected("the public-only source wall accepted " + label)

    for label, path in (
        ("candidate adapter", ROOT + "/candidates/rust_candidate.py"),
        ("native engine", ROOT + "/candidates/_rust_engine.so"),
        ("native bridge", ROOT + "/candidates/_rust_bridge.so"),
        ("private root", "/tmp/rebar-phase2-native-build-v33-private"),
        ("retired proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json"),
        ("successor proposal", ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"),
        ("secret seed", ROOT + "/oracle/phase3/final.seed"),
        ("hidden cases", ROOT + "/oracle/phase3/final-hidden.json"),
        ("compressed original archive", ROOT + "/oracle/phase2/evidence/original.json.gz"),
    ):
        reject_wall(label, "open", (path, None, os.O_RDONLY | os.O_NOFOLLOW))
    for label, event, arguments in (
        ("candidate process", "subprocess.Popen", (PYTHON,)),
        ("native load", "ctypes.dlopen", ("engine.so",)),
        ("candidate import", "import", ("candidates.rust_candidate",)),
        ("regex import", "import", ("re",)),
        ("archive import", "import", ("gzip",)),
        ("clock", "time.perf_counter", ()),
        ("network", "socket.connect", ("example.invalid",)),
        ("thread", "_thread.start_new_thread", ()),
        ("destructive rename", "os.rename", ("old", "new")),
    ):
        reject_wall(label, event, arguments)
    require(len(observed) >= 800,
            "require comprehensive hostile speed, correctness, history, and wall controls")
    return len(observed)


def exclusive(relative: str, value: bytes) -> None:
    descriptor = os.open(os.path.join(ROOT, relative),
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        position = 0
        while position < len(value):
            wrote = os.write(descriptor, value[position:])
            require(wrote > 0, "exclusive V106 graph publication stopped")
            position += wrote
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require the actual committed-and-pushed V106 source: " + label)
    return value


def arguments() -> argparse.Namespace:
    switches = [item for item in sys.argv[1:] if item.startswith("--")]
    require(len(switches) == len(set(switches)), "reject repeated graph modes or evidence pins")
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render-graph", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--source-bytes", required=True, type=int)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--protocol-bytes", required=True, type=int)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--contract-bytes", type=int)
    parser.add_argument("--v105-source-sha256", required=True)
    parser.add_argument("--v105-protocol-sha256", required=True)
    parser.add_argument("--v105-contract-sha256", required=True)
    parser.add_argument("--v4-source-sha256", required=True)
    parser.add_argument("--v4-protocol-sha256", required=True)
    parser.add_argument("--v4-contract-sha256", required=True)
    parser.add_argument("--performance-receipt-sha256", required=True)
    parser.add_argument("--performance-summary-sha256", required=True)
    parser.add_argument("--paired-rows-sha256", required=True)
    parser.add_argument("--original-receipt-sha256", required=True)
    parser.add_argument("--public-receipt-sha256", required=True)
    parser.add_argument("--audit-receipt-sha256", required=True)
    for label in HISTORY:
        parser.add_argument("--" + label + "-summary-sha256", required=True)
        parser.add_argument("--" + label + "-receipt-sha256", required=True)
    parser.add_argument("--root-authorized", action="store_true")
    parser.add_argument("--frozen-committed-pushed", action="store_true")
    parser.add_argument("--frozen-commit")
    parser.add_argument("--pushed-commit")
    result = parser.parse_args()
    if result.render_contract:
        require(result.contract_sha256 is None and result.contract_bytes is None
                and result.root_authorized is False
                and result.frozen_committed_pushed is False
                and result.frozen_commit is None and result.pushed_commit is None,
                "render only an unsigned prospective V106 source freeze")
    elif result.render_graph:
        require(result.contract_sha256 is not None and result.contract_bytes is not None
                and result.root_authorized is True
                and result.frozen_committed_pushed is True
                and commit(result.frozen_commit, "frozen commit")
                    == commit(result.pushed_commit, "pushed commit"),
                "only root may render after the complete source freeze is committed and pushed")
    else:
        require(result.contract_sha256 is not None and result.contract_bytes is not None
                and result.root_authorized is False
                and result.frozen_committed_pushed is False
                and result.frozen_commit is None and result.pushed_commit is None,
                "source-only verification cannot possess graph publication authority")
    return result


def context(options: argparse.Namespace) -> dict:
    source = (SOURCE, fingerprint(options.source_sha256, "V106 graph renderer"),
              options.source_bytes)
    protocol = (PROTOCOL, fingerprint(options.protocol_sha256, "V106 graph protocol"),
                options.protocol_bytes)
    require(1 <= options.source_bytes <= 262_144
            and 1 <= options.protocol_bytes <= 65_536,
            "independently pin the complete V106 source and protocol bytes")
    for prefix, collection in (("v105", V105), ("v4", V4)):
        for label, owner in collection.items():
            require(getattr(options, prefix + "_" + label + "_sha256") == owner[1],
                    "an independently caller-pinned predecessor changed: "
                    + prefix + " " + label)
    for name, owner in (("performance_receipt", PERFORMANCE),
                        ("performance_summary", SUMMARY), ("paired_rows", RAW_PAIRS),
                        ("original_receipt", ORIGINAL_PASS),
                        ("public_receipt", PUBLIC_PASS), ("audit_receipt", AUDIT)):
        require(getattr(options, name + "_sha256") == owner[1],
                "the independently caller-pinned actual evidence changed: " + name)
    for label, values in HISTORY.items():
        for kind in ("summary", "receipt"):
            require(getattr(options, label + "_" + kind + "_sha256") == values[kind][1],
                    "the independently caller-pinned earlier experiment changed: "
                    + label + " " + kind)
    approved = (*owners(), source, protocol)
    actual_contract = None
    if options.contract_sha256 is not None:
        require(type(options.contract_bytes) is int
                and 1 <= options.contract_bytes <= 262_144,
                "independently pin the complete V106 contract byte size")
        actual_contract = (CONTRACT,
                           fingerprint(options.contract_sha256, "V106 graph contract"),
                           options.contract_bytes)
        approved = (*approved, actual_contract)
    mode = "contract" if options.render_contract else (
        "graph" if options.render_graph else "source")
    wall = SourceWall(mode, approved)
    sys.addaudithook(wall.check)
    metadata, raw = {}, {}
    for owner in approved:
        identity, value = read(owner, approved)
        metadata[owner[0]], raw[owner[0]] = identity, value
    state = {
        "options": options, "wall": wall, "metadata": metadata,
        "goal": raw[GOAL[0]],
        "original": document(raw[ORIGINAL_PASS[0]], "actual original PASS"),
        "public": document(raw[PUBLIC_PASS[0]], "actual public PASS"),
        "audit": document(raw[AUDIT[0]], "actual static audit"),
        "performance": document(raw[PERFORMANCE[0]], "actual corrected performance"),
        "summary": document(raw[SUMMARY[0]], "all corrected performance results"),
        "pairs": document(raw[RAW_PAIRS[0]], "all actual paired timing rows"),
        "v4_contract": document(raw[V4["contract"][0]], "V4 source freeze"),
        "v105_contract": document(raw[V105["contract"][0]], "V105 source freeze"),
        "history": {label: {
            kind: document(raw[entry[kind][0]], label + " historical " + kind)
            for kind in ("summary", "receipt")
        } for label, entry in HISTORY.items()},
    }
    if actual_contract is not None:
        state["contract_document"] = document(raw[CONTRACT], "V106 source freeze")
    verify(state)
    if actual_contract is not None:
        require(state["contract_document"] == freeze(state),
                "reject a stale or incomplete user-friendly V106 source freeze")
    return state


def report(state: dict, hostile: int) -> dict:
    options = state["options"]
    return {
        "schema": "rebar-owned-corrected-rust-speed-headline-v106-source-result",
        "version": VERSION, "status": "PASS", "title": TITLE,
        "mode": "SELF-TEST" if options.self_test else (
            "GRAPH RENDER" if options.render_graph else "FROZEN CONTEXT"),
        "same_exact_rust_build_verified": True,
        "same_exact_native_engine_sha256": ENGINE,
        "same_exact_native_bridge_sha256": BRIDGE,
        "same_exact_complete_adapter_sha256": ADAPTER,
        "original_verified_passing_case_count": ORIGINAL,
        "broader_public_verified_passing_case_count": PUBLIC,
        "baseline_speed_relative_to_python": 1.0,
        "rust_fully_correct_speed_relative_to_python": SPEEDUP,
        "confidence_interval_95": {"lower": LOWER, "upper": UPPER},
        "faster_case_count": 252, "slower_case_count": 164,
        "regression_over_20_percent_count": 14,
        "all_regression_rows_preserved": True,
        "all_slower_case_rows_preserved": True,
        "rust_peak_traced_memory_bytes": 111026,
        "python_peak_traced_memory_bytes": 181952,
        "rust_maximum_rss_kib": 44032, "python_maximum_rss_kib": 44032,
        "hostile_controls_rejected": hostile,
        **source_effects(),
        "candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "final_benchmark_measured": False, "winner_selected": False,
    }


def main() -> int:
    options = arguments()
    require(sys.executable == PYTHON and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.flags.dont_write_bytecode == 1,
            "require the pinned isolated, no-site CPython 3.14.6 executable")
    state = context(options)
    if options.render_contract:
        os.write(1, canonical(freeze(state)))
        return 0
    assets = graph(state, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    validate_graph(state, assets, options.source_sha256, options.source_bytes,
                   options.contract_sha256, options.contract_bytes)
    rejected = (controls(state, assets, options.source_sha256, options.source_bytes,
                         options.contract_sha256, options.contract_bytes)
                if options.self_test else 0)
    if options.render_graph:
        for label, extension in (("svg", ".svg"), ("inputs", ".inputs.json"),
                                 ("summary", ".json")):
            exclusive(OUTPUT + extension, assets[label])
    result = report(state, rejected)
    if options.render_graph:
        result.update({label + "_sha256": digest(value)
                       for label, value in assets.items()})
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Rejected, OSError, ValueError, TypeError, KeyError, IndexError,
            ZeroDivisionError) as failure:
        print("corrected-rust-speed-headline-v106: " + str(failure), file=sys.stderr)
        raise SystemExit(1)
