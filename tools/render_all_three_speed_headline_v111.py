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
SOURCE = "tools/render_all_three_speed_headline_v111.py"
PROTOCOL = "oracle/phase2/ALL-THREE-SPEED-HEADLINE-V111.md"
CONTRACT = "oracle/phase2/all-three-speed-headline-v111.json"
OUTPUT = "docs/evidence/candidate-current-overview-v111"
TITLE = "How fast are the different versions?"
VERSION = 111
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
ZIG_PASS = (
    "oracle/phase2/evidence/repaired-zig-original-campaign-v18-phase2-v18-"
    "zig-final-original-p0-v18-success-publication-receipt.json",
    "b2762eaea6dd505aa34bd446996b0464b7a0e057e7fb7162355885e065e19bd0",
    20_905,
)
C_RESULT = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v16-c-phase2-v24-"
    "c-final-public-semantics-original-p0-v16-results-publication-receipt.json",
    "34f1b7ccd9fe06408cdc6094f86bf98f4776bc7716ad970264bfbbda0d1280f2", 10_657,
)
C_PREVIOUS = (
    "oracle/phase2/evidence/repaired-c-original-campaign-v15-c-phase2-v23-"
    "c-complete-semantics-original-p0-v15-failures-publication-receipt.json",
    "6adea6a4da59bb0c63c54006991257b46149c4447a82bb1cd6b8810e6bee5b43", 10_888,
)
RUST_V35_BUILD = (
    "oracle/phase2/evidence/native-source-build-v35-rust-phase2-v35-rust-"
    "optimized-safe-source-root-provenance-publication-receipt.json",
    "442fba9a323d527977b3b19b9cb733d81a63d93adf6f4e9f25510f01ae5b4a2e", 9_669,
)

AUDITED_V30_ENGINE = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
AUDITED_V30_BRIDGE = "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256"
AUDITED_V30_BRIDGE_SOURCE = "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
AUDITED_V30_ADAPTER = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
AUDITED_V30_BUILD = "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd"
AUDITED_V30_ROOT = "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404"
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
FALSIFIED_V106 = {
    "source": (
        "tools/render_owned_corrected_rust_speed_headline_v106.py",
        "ece411aedf9f08f853a4c518aa96c3e421f222c5f270f73a7d1176e57c1c3799",
        66_496,
    ),
    "protocol": (
        "oracle/phase2/RUST-CORRECTED-SPEED-HEADLINE-V106.md",
        "f2809d3bdbdee7acdd05a91f01699be15f8e910ff05581fb0b8ecbfcb7348300",
        4_460,
    ),
    "contract": (
        "oracle/phase2/rust-corrected-speed-headline-v106.json",
        "8080aac97c91bb4d1734d177ddad6af05b2840821ed4f698b25760cf8ef95dc2",
        37_241,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v106.inputs.json",
        "68f778d9ed6762b089806e7de36fc11737f7f5840c19446f7888abb9206b7659",
        66_463,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v106.json",
        "564a4f4cb94474699a44be566bf89189b7bc302a1962aed902c9ab3fdb678cb6",
        66_930,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v106.svg",
        "8df281d8870b683eb7c5520ca414e0c2ebec7170e293456f87a08abb9ea651d7",
        9_963,
    ),
}
FALSIFIED_V107 = {
    "source": (
        "tools/render_updated_correctness_headline_v107.py",
        "63aff115b24eeb7066e71ea7ee093a740b2a6a39a1fae0994908e7fa43ac9eea",
        63_064,
    ),
    "protocol": (
        "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V107.md",
        "205ecfdab25feaebd03333fe0ac2e48bda527c46d879870162a7afd85df6317c",
        3_664,
    ),
    "contract": (
        "oracle/phase2/updated-correctness-headline-v107.json",
        "64d08dfdfd09334d0d852a20c4056a4ad62bf4644189fe09d503d202e0436367",
        7_064,
    ),
}
CORRECTED_V108 = {
    "source": (
        "tools/render_updated_correctness_headline_v108.py",
        "b9b1d0a268595d70b49ad40cc05ebb833ed99c5d6976ca9b8c4bbbafe7cba6fd",
        76_015,
    ),
    "protocol": (
        "oracle/phase2/UPDATED-CORRECTNESS-HEADLINE-V108.md",
        "40195e9db372ab3ea3ba8aa9a4b2e2ad4112e77af935e21eae80f2bf991d7e29",
        4_630,
    ),
    "contract": (
        "oracle/phase2/updated-correctness-headline-v108.json",
        "1fe218a2638d91b36cdba79f7753f3f4ecc21ea86ad3a5111f8e6c6a27ca42d8",
        9_131,
    ),
}
PRESERVED_STALE_V109 = {
    "source": ("tools/render_truthful_current_speed_headline_v109.py",
               "7a948f616a8c5670fa668c31e83c5b9b247888f7b3d3fe0d88d6424394f47193", 90_158),
    "protocol": ("oracle/phase2/TRUTHFUL-CURRENT-SPEED-HEADLINE-V109.md",
                 "7bda6c8c4b36252e5e6ff795b14873044d89b4ec1c4f8629991b6e0097f7f0f1", 5_393),
    "contract": ("oracle/phase2/truthful-current-speed-headline-v109.json",
                 "1c3442d1747be098fed4a53a5bc6c61320d3f24de9b21ee59ebf9b5cbb3a34f3", 42_490),
}
CURRENT_V110 = {
    "source": ("tools/render_all_three_correctness_headline_v110.py",
               "102b5c2926eb0895e0cd8994865eaf16ac1cb822ebba8dfb9e7b681787d93b6f", 54_155),
    "protocol": ("oracle/phase2/ALL-THREE-CORRECTNESS-HEADLINE-V110.md",
                 "e0b15118cbad61e6b6384934a752fcd0ec97f41c4b08e5871c29f8c8b1d1469e", 3_081),
    "contract": ("oracle/phase2/all-three-correctness-headline-v110.json",
                 "d7072a1877714ca5f7ab26b14531fbfb6f37c297dc15b2358afb12ffb6d56fd7", 10_922),
    "inputs": ("docs/evidence/candidate-current-overview-v110.inputs.json",
               "36eb4e14d462f9d6445df08ce926a56453cbe5bbabc2a1c2fb560059fb8cee9f", 10_893),
    "summary": ("docs/evidence/candidate-current-overview-v110.json",
                "dfe21e7dd1a34e6c2d6137c74027a46941f213f9af7bfba541fca24da0b46343", 41_692),
    "svg": ("docs/evidence/candidate-current-overview-v110.svg",
            "6235f11ec835369640297a5590e891a8913a4ae4997fc2423f0aa6966a1bbe1d", 6_716),
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
    AUDIT[0]: 525089, ZIG_PASS[0]: 526565, C_RESULT[0]: 525275,
    C_PREVIOUS[0]: 526500, RUST_V35_BUILD[0]: 526741,
    PRESERVED_STALE_V109["source"][0]: 431842,
    PRESERVED_STALE_V109["protocol"][0]: 526661,
    PRESERVED_STALE_V109["contract"][0]: 526679,
    CURRENT_V110["source"][0]: 431872, CURRENT_V110["protocol"][0]: 526734,
    CURRENT_V110["contract"][0]: 526739, CURRENT_V110["inputs"][0]: 431885,
    CURRENT_V110["summary"][0]: 431886, CURRENT_V110["svg"][0]: 431884,
    PERFORMANCE[0]: 526289, SUMMARY[0]: 526288,
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
    FALSIFIED_V106["source"][0]: 431461,
    FALSIFIED_V106["protocol"][0]: 526350,
    FALSIFIED_V106["contract"][0]: 526351,
    FALSIFIED_V106["inputs"][0]: 431747,
    FALSIFIED_V106["summary"][0]: 431748,
    FALSIFIED_V106["svg"][0]: 431745,
    FALSIFIED_V107["source"][0]: 431578,
    FALSIFIED_V107["protocol"][0]: 526409,
    FALSIFIED_V107["contract"][0]: 526418,
    CORRECTED_V108["source"][0]: 431808,
    CORRECTED_V108["protocol"][0]: 526622,
    CORRECTED_V108["contract"][0]: 526624,
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
    return (GOAL, ORIGINAL_PASS, PUBLIC_PASS, AUDIT, ZIG_PASS, C_RESULT,
            C_PREVIOUS, RUST_V35_BUILD, PERFORMANCE, SUMMARY, RAW_PAIRS,
            *V4.values(), *V105.values(), *FALSIFIED_V106.values(),
            *FALSIFIED_V107.values(), *CORRECTED_V108.values(),
            *PRESERVED_STALE_V109.values(), *CURRENT_V110.values(), *historical)


class SourceWall:
    """Allow exact immutable plaintext owners and root-only exclusive V111 outputs."""

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


def verify_historical_v30_audit(audit: dict) -> None:
    same(audit, {
        "schema": "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit",
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
    }, "older V30-only static audit never establishes current V33 independence")
    proof = audit.get("authenticated_v30")
    same(proof, {
        "actual_compiler_process_count": 28,
        "actual_completed_phase_count": 2,
        "actual_private_native_owner_count": 4,
        "actual_private_source_owner_count": 18,
        "external_cargo_dependencies": 0,
    }, "explicitly bind the older V30 build actually inspected")
    same(proof.get("publication_owner"), {"sha256": AUDITED_V30_BUILD},
         "authenticate the older V30 build publication")
    same(proof.get("root_provenance_owner"), {"sha256": AUDITED_V30_ROOT},
         "authenticate the older V30 root without opening it")
    phases = audit.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "authenticate both older V30 inspection phases")
    for number, phase in enumerate(phases):
        same(phase, {
            "private_native_owner_count": 2,
            "private_source_owner_count": 9,
            "external_regex_packages": 0,
        }, "older V30 inspection phase " + str(number))
        binaries = phase.get("native_outputs")
        require(type(binaries) is list and len(binaries) == 2,
                "require the two audited older V30 native binaries")
        observed = {}
        for binary in binaries:
            require(type(binary) is dict, "reject an incomplete older V30 binary")
            details, owner = binary.get("audit"), binary.get("owner")
            require(type(details) is dict and type(owner) is dict,
                    "reject a missing older V30 native inspection")
            role = details.get("role")
            require(role in {"engine", "bridge"} and role not in observed,
                    "reject an omitted or duplicate older V30 native role")
            observed[role] = owner.get("sha256")
        require(observed == {"engine": AUDITED_V30_ENGINE,
                             "bridge": AUDITED_V30_BRIDGE},
                "the audited V30 binaries differ from the passing V33 build")
        sources = phase.get("sources")
        require(type(sources) is dict,
                "bind the audited older V30 Python and bridge source")
        adapter = sources.get("candidates/rust_candidate.py")
        bridge_source = sources.get("candidates/rust/py_bridge.c")
        require(type(adapter) is dict and type(bridge_source) is dict,
                "reject an omitted older V30 source")
        same(adapter.get("owner"), {"sha256": AUDITED_V30_ADAPTER},
             "bind the audited older V30 Python interface")
        same(bridge_source.get("owner"), {"sha256": AUDITED_V30_BRIDGE_SOURCE},
             "bind the audited older V30 native bridge source")
    require(AUDITED_V30_ENGINE != ENGINE and AUDITED_V30_BRIDGE != BRIDGE
            and AUDITED_V30_ADAPTER != ADAPTER and AUDITED_V30_BUILD != BUILD
            and AUDITED_V30_ROOT != PRIVATE_ROOT,
            "never transfer older V30 static or live independence to V33")


def verify_preserved_falsification(state: dict) -> None:
    previous = state["falsified_v106"]
    for key in ("source", "protocol", "svg"):
        require(digest(previous[key]) == FALSIFIED_V106[key][1],
                "preserve the invalidated V106 owner: " + key)
    for key in ("contract", "inputs", "summary"):
        require(digest(canonical(previous[key])) == FALSIFIED_V106[key][1],
                "preserve the invalidated V106 graph evidence: " + key)
    same(previous["contract"], {
        "schema": "rebar-owned-corrected-rust-speed-headline-v106-source-freeze",
        "version": 106,
    }, "preserve rather than rewrite the invalidated V106 freeze")
    same(previous["contract"].get("same_build"), {
        "native_engine_sha256": ENGINE,
        "native_bridge_sha256": BRIDGE,
        "complete_adapter_sha256": ADAPTER,
    }, "the invalidated V106 graph described current V33")
    same(previous["contract"].get("actual_static_audit"), {"sha256": AUDIT[1]},
         "the invalidated V106 freeze cited the older V30 audit")
    for key in ("inputs", "summary"):
        same(previous[key], {
            "version": 106,
            "static_first_party_non_delegation": "PASS; STATIC AUDIT ONLY",
            "same_exact_native_engine_sha256": ENGINE,
            "same_exact_native_bridge_sha256": BRIDGE,
            "same_exact_complete_adapter_sha256": ADAPTER,
            "rust_fully_correct_speed_relative_to_python": SPEEDUP,
        }, "preserve the exact V106 older-audit attribution falsified by V111")
    require(previous["svg"].startswith(b"<svg ")
            and b"How fast are the different versions?" in previous["svg"],
            "preserve the complete invalidated but immutable historical V106 SVG")
    prior = state["falsified_v107"]
    for key in ("source", "protocol"):
        require(digest(prior[key]) == FALSIFIED_V107[key][1],
                "preserve invalidated V107 immutable history: " + key)
    require(digest(canonical(prior["contract"])) == FALSIFIED_V107["contract"][1],
            "preserve the invalidated V107 source freeze")
    same(prior["contract"], {
        "schema": "rebar-updated-correctness-headline-v107-source-freeze",
        "version": 107,
    }, "preserve the exact prior falsified correctness freeze")
    same(prior["contract"].get("headline"), {
        "static_first_party_audit_status": "PASS",
        "external_regex_engine_count": 0,
        "external_regex_package_count": 0,
        "external_regex_symbol_count": 0,
    }, "preserve the false V107 audit attribution without repeating it")
    corrected = state["corrected_v108"]
    for key in ("source", "protocol"):
        require(digest(corrected[key]) == CORRECTED_V108[key][1],
                "preserve corrected V108 immutable history: " + key)
    require(digest(canonical(corrected["contract"])) == CORRECTED_V108["contract"][1],
            "authenticate the corrected V108 source freeze")
    same(corrected["contract"], {
        "schema": "rebar-updated-correctness-headline-v108-source-freeze",
        "version": 108,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v107_static_claim_falsified": True,
    }, "require the corrected V108 distinction between old V30 and current V33")
    same(corrected["contract"].get("historical_v30_audited_build"), {
        "engine_sha256": AUDITED_V30_ENGINE,
        "bridge_sha256": AUDITED_V30_BRIDGE,
        "adapter_sha256": AUDITED_V30_ADAPTER,
        "publication_sha256": AUDITED_V30_BUILD,
        "root_sha256": AUDITED_V30_ROOT,
    }, "require the exact already-corrected V30 source identities")



def verify_preserved_v109_and_current_v110(state: dict) -> None:
    stale = state["preserved_stale_v109"]
    for key in ("source", "protocol"):
        require(digest(stale[key]) == PRESERVED_STALE_V109[key][1],
                "preserve immutable stale V109 speed owner: " + key)
    require(digest(canonical(stale["contract"])) == PRESERVED_STALE_V109["contract"][1],
            "preserve the unchanged stale V109 speed freeze")
    same(stale["contract"], {
        "schema": "rebar-owned-truthful-current-speed-headline-v109-source-freeze",
        "version": 109,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
    }, "preserve V109 audit correction while falsifying its outdated C status")
    same(stale["contract"].get("actual_measurement"), {
        "c_original_correctness_status": "FAIL",
        "c_verified_original_case_count": 22_798,
        "c_observed_difference_count": 224,
    }, "preserve, rather than publish, the now-false historical V109 C claim")
    current = state["current_v110"]
    for key in ("source", "protocol", "svg"):
        require(digest(current[key]) == CURRENT_V110[key][1],
                "preserve immutable all-three V110 evidence: " + key)
    for key in ("contract", "inputs", "summary"):
        require(digest(canonical(current[key])) == CURRENT_V110[key][1],
                "preserve complete truthful V110 correctness graph: " + key)
    same(current["contract"], {
        "schema": "rebar-all-three-correctness-headline-v110-source-freeze",
        "version": 110,
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
    }, "bind the current independently authenticated all-three original PASS graph")
    for key in ("inputs", "summary"):
        same(current[key], {
            "version": 110,
            "rust_original_verified_passing_case_count": ORIGINAL,
            "rust_public_verified_passing_case_count": PUBLIC,
            "zig_original_verified_passing_case_count": ORIGINAL,
            "c_original_verified_passing_case_count": ORIGINAL,
            "c_original_semantic_mismatch_count": 0,
            "previous_c_verified_passing_case_count": 22_798,
            "previous_c_semantic_mismatch_count": 224,
            "historical_c_verified_passing_case_count": 16_413,
            "historical_c_semantic_mismatch_count": 606,
            "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
            "qualified_candidate_count": 0, "winner_selected": False,
        }, "never revert the current actual C PASS to an older historical failure")
    require(b"Rust, Zig, and C all pass the original Python tests" in current["svg"],
            "preserve the actual accessible V110 all-three overview")

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
                         ("audit", AUDIT), ("zig", ZIG_PASS), ("c_result", C_RESULT),
                         ("c_previous", C_PREVIOUS), ("rust_v35", RUST_V35_BUILD),
                         ("performance", PERFORMANCE),
                         ("summary", SUMMARY), ("pairs", RAW_PAIRS),
                         ("v4_contract", V4["contract"]),
                         ("v105_contract", V105["contract"])):
        require(digest(canonical(state[label])) == owner[1],
                "the complete authenticated owner changed: " + label)
    require(digest(state["goal"]) == GOAL[1], "the immutable user goal changed")
    verify_preserved_falsification(state)
    verify_preserved_v109_and_current_v110(state)
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
    verify_historical_v30_audit(state["audit"])
    same(state["zig"], {
        "status": "PASS", "family": "zig", "candidate_status": "PASS",
        "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
        "actual_candidate_workers": 13, "unique_candidate_worker_count": 13,
        "performance": "NOT MEASURED", "winner_selected": False,
    }, "Zig passes every original check but its speed remains NOT MEASURED")
    same(state["c_result"], {
        "schema": "rebar-owned-repaired-c-original-campaign-v16-durable-publication-receipt",
        "status": "PASS", "family": "c", "candidate_status": "PASS",
        "candidate_qualified": False, "case_execution_denominator": ORIGINAL,
        "verified_passing_case_count": ORIGINAL, "semantic_mismatch_count": 0,
        "actual_candidate_workers": 13, "completed_suite_count": 13,
        "infrastructure_failure_count": 0, "performance": "NOT MEASURED",
        "winner_selected": False,
    }, "C passes every original Python check while its speed remains NOT MEASURED")
    c_workers = state["c_result"].get("suite_outcomes")
    require(type(c_workers) is list and len(c_workers) == 13
            and sum(row.get("case_execution_denominator", 0) for row in c_workers) == ORIGINAL
            and all(row.get("status") == "PASS" and row.get("mismatch_count") == 0
                    for row in c_workers),
            "preserve all thirteen genuine independently passing C worker groups")
    same(state["c_previous"], {"status": "PASS", "family": "c",
         "candidate_status": "FAIL", "verified_passing_case_count": 22_798,
         "semantic_mismatch_count": 224, "completed_suite_count": 13},
         "preserve the previous complete C run and all 224 actual differences")
    same(state["rust_v35"], {
        "schema": "rebar-phase2-owned-rust-optimized-safe-source-build-v35-durable-publication-receipt",
        "status": "PASS", "version": 35, "family": "rust", "build_status": "PASS",
        "actual_compiler_process_count": 28, "actual_completed_phase_count": 2,
        "candidate_correctness": "NOT MEASURED", "candidate_matching": "NOT RUN",
        "proposed_v35_correctness": "NOT MEASURED",
        "proposed_v35_performance": "NOT MEASURED",
        "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "latest_public_v33_geomean_decimal": "1.2424347186648022",
        "latest_public_v33_performance_receipt_sha256": PERFORMANCE[1],
        "candidate_qualified": False, "winner_selected": False,
    }, "never assign measured older V33 results to the newly built untested Rust V35")
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
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "current_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "zig_original_correctness_status": "PASS",
        "zig_verified_original_case_count": ORIGINAL,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_original_correctness_status": "PASS",
        "c_verified_original_case_count": ORIGINAL,
        "c_observed_difference_count": 0,
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
    }


def freeze(state: dict) -> dict:
    return {
        "schema": "rebar-owned-all-three-speed-headline-v111-source-freeze",
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
        "falsified_v106_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in FALSIFIED_V106.items()
        },
        "falsified_v107_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in FALSIFIED_V107.items()
        },
        "corrected_v108_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in CORRECTED_V108.items()
        },
        "actual_original_pass": state["metadata"][ORIGINAL_PASS[0]],
        "actual_broader_public_pass": state["metadata"][PUBLIC_PASS[0]],
        "historical_v30_only_static_audit": state["metadata"][AUDIT[0]],
        "actual_zig_original_pass": state["metadata"][ZIG_PASS[0]],
        "actual_c_original_pass": state["metadata"][C_RESULT[0]],
        "preserved_previous_c_original_failure": state["metadata"][C_PREVIOUS[0]],
        "latest_rust_v35_source_build": state["metadata"][RUST_V35_BUILD[0]],
        "preserved_stale_v109_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in PRESERVED_STALE_V109.items()
        },
        "current_v110_all_three_correctness_graph": {
            label: state["metadata"][owner[0]]
            for label, owner in CURRENT_V110.items()
        },
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
        "historical_v30_audited_build": {
            "native_engine_sha256": AUDITED_V30_ENGINE,
            "native_bridge_sha256": AUDITED_V30_BRIDGE,
            "complete_adapter_sha256": AUDITED_V30_ADAPTER,
            "build_publication_sha256": AUDITED_V30_BUILD,
            "root_sha256": AUDITED_V30_ROOT,
        },
        "historical_v30_audit_build_differs_from_current_v33": True,
        "historical_v30_static_first_party_non_delegation": "PASS",
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
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
        "runtime_non_delegation": "NOT ESTABLISHED",
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
        "The passing current Rust build has no matching static or live "
        "independence proof; only an older Rust build was inspected. Zig and "
        "C each pass all original tests, but their speed is not measured. "
        "A newer Rust V35 build has not been tested for correctness or speed. "
        "This is public practice, not a final qualification or winner."
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
        ("Rust V33 — fully correct", SPEEDUP, "#059669", "#d1fae5",
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
        'Measured 95% range: 1.19× to 1.30× Python</text>',
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
        '<rect x="62" y="1268" width="1376" height="128" rx="16" '
        'fill="#fff7ed" stroke="#fed7aa"/>',
        '<text x="87" y="1307" fill="#9a3412" font-size="17" '
        'font-family="system-ui,sans-serif" font-weight="720">'
        'The earlier experiments are not fully correct. This is not a final winner.</text>',
        '<text x="88" y="1341" fill="#7c2d12" font-size="15" '
        'font-family="system-ui,sans-serif">'
        'Public practice only · no hidden final test opened · no final winner</text>',
        '<text x="88" y="1370" fill="#9a3412" font-size="14" '
        'font-family="system-ui,sans-serif" font-weight="700">'
        'Current Rust static and live independence: NOT ESTABLISHED · '
        'Zig and C speed: NOT MEASURED · Newer Rust V35: NOT MEASURED</text>',
        '</svg>\n',
    ]
    return "".join(parts).encode("utf-8")


def graph(state: dict, source_sha: str, source_bytes: int,
          contract_sha: str, contract_bytes: int) -> dict:
    measured = measurement(state)
    common = {
        "version": VERSION, "title": TITLE, "goal_sha256": GOAL[1],
        "python": "3.14.6", "actual_current_graph_predecessor_version": 108,
        "source": {"path": SOURCE, "sha256": source_sha, "bytes": source_bytes},
        "protocol": state["metadata"][PROTOCOL],
        "contract": {"path": CONTRACT, "sha256": contract_sha, "bytes": contract_bytes},
        "actual_original_pass": state["metadata"][ORIGINAL_PASS[0]],
        "actual_broader_public_pass": state["metadata"][PUBLIC_PASS[0]],
        "historical_v30_only_static_audit": state["metadata"][AUDIT[0]],
        "actual_zig_original_pass": state["metadata"][ZIG_PASS[0]],
        "actual_c_original_pass": state["metadata"][C_RESULT[0]],
        "preserved_previous_c_original_failure": state["metadata"][C_PREVIOUS[0]],
        "latest_rust_v35_source_build": state["metadata"][RUST_V35_BUILD[0]],
        "preserved_stale_v109_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in PRESERVED_STALE_V109.items()
        },
        "current_v110_all_three_correctness_graph": {
            label: state["metadata"][owner[0]]
            for label, owner in CURRENT_V110.items()
        },
        "falsified_v106_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in FALSIFIED_V106.items()
        },
        "falsified_v107_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in FALSIFIED_V107.items()
        },
        "corrected_v108_frozen_history": {
            label: state["metadata"][owner[0]]
            for label, owner in CORRECTED_V108.items()
        },
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
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "zig_original_correctness_status": "PASS",
        "zig_verified_original_case_count": ORIGINAL,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_original_correctness_status": "PASS",
        "c_verified_original_case_count": ORIGINAL,
        "c_observed_difference_count": 0,
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
        "candidate_qualified": False,
        "qualified_independent_family_count": 0,
        "minimum_qualified_independent_family_count": 3,
        "final_benchmark_measured": False,
        "winner_selected": False,
    }
    inputs = {**common,
              "schema": "rebar-candidate-all-three-speed-headline-v111-inputs"}
    summary = {**common,
               "schema": "rebar-candidate-all-three-speed-headline-v111-summary",
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
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "zig_original_correctness_status": "PASS",
        "zig_verified_original_case_count": ORIGINAL,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_original_correctness_status": "PASS",
        "c_verified_original_case_count": ORIGINAL,
        "c_observed_difference_count": 0,
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
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
    same(summary.get("measurement"), {
        "current_v33_static_first_party_non_delegation": "NOT ESTABLISHED",
        "current_v33_external_regex_engine_count": "NOT ESTABLISHED",
        "current_v33_external_regex_package_count": "NOT ESTABLISHED",
        "current_v33_external_regex_symbol_count": "NOT ESTABLISHED",
        "current_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_audit_build_differs_from_current_v33": True,
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
    }, "never transfer the older V30 audit or invent unmeasured engine speeds")
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
        "Rust V33 — fully correct", "Python — original",
        "V26 — earlier experiment", "V27 — earlier experiment",
        "V28 — earlier experiment", "PASSED ALL ORIGINAL + BROADER CHECKS",
        "FAILED 1,145 BROADER CHECKS", "1.24×", "1.25×", "0.80×", "1.23×",
        "1.19× to 1.30×", "252 tasks faster · 164 slower · 14 more than 20% slower",
        "31,237 / 31,237 original + 10,434 / 10,434 broader checks passed",
        "Rust 111,026 bytes · Python 181,952 bytes", "both 44,032 KiB",
        "All 14 are shown. All 164 slower tasks remain in the accompanying data.",
        "no hidden final test opened", "no final winner",
        "Current Rust static and live independence: NOT ESTABLISHED",
        "Zig and C speed: NOT MEASURED",
        "Newer Rust V35: NOT MEASURED",
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
        return {**value, "__v111_hostile": True}
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

    for owner in ("original", "public", "audit", "zig", "c_result",
                  "c_previous", "rust_v35", "performance", "summary",
                  "pairs", "v4_contract", "v105_contract"):
        for key in sorted(state[owner]):
            reject_context(owner + " changed " + key,
                           lambda hostile, name=owner, field=key:
                           hostile[name].__setitem__(field,
                                                      different(hostile[name][field])))
    for previous, owner_names in (
        ("falsified_v106", ("contract", "inputs", "summary")),
        ("falsified_v107", ("contract",)),
        ("corrected_v108", ("contract",)),
        ("preserved_stale_v109", ("contract",)),
        ("current_v110", ("contract", "inputs", "summary")),
    ):
        for owner in owner_names:
            for key in sorted(state[previous][owner]):
                reject_context(
                    previous + " " + owner + " changed " + key,
                    lambda hostile, collection=previous, name=owner, field=key:
                        hostile[collection][name].__setitem__(
                            field, different(hostile[collection][name][field])))
    for previous, owner_names in (
        ("falsified_v106", ("source", "protocol", "svg")),
        ("falsified_v107", ("source", "protocol")),
        ("corrected_v108", ("source", "protocol")),
        ("preserved_stale_v109", ("source", "protocol")),
        ("current_v110", ("source", "protocol", "svg")),
    ):
        for owner in owner_names:
            reject_context(
                previous + " changed preserved bytes " + owner,
                lambda hostile, collection=previous, name=owner:
                    hostile[collection].__setitem__(
                        name, hostile[collection][name] + b"CHANGED"))
    for phase in range(2):
        for native, replacement in ((0, ENGINE), (1, BRIDGE)):
            reject_context(
                "older V30 inspection phase " + str(phase)
                + " native binary falsely attributed to current V33",
                lambda hostile, index=phase, role=native, current=replacement:
                    hostile["audit"]["phases"][index]["native_outputs"]
                           [role]["owner"].__setitem__("sha256", current))
        reject_context(
            "older V30 inspection phase " + str(phase)
            + " adapter falsely attributed to current V33",
            lambda hostile, index=phase:
                hostile["audit"]["phases"][index]["sources"]
                       ["candidates/rust_candidate.py"]["owner"].__setitem__(
                           "sha256", ADAPTER))
    for key, replacement in (("publication_owner", BUILD),
                             ("root_provenance_owner", PRIVATE_ROOT)):
        reject_context(
            "older V30 " + key + " falsely attributed to current V33",
            lambda hostile, name=key, current=replacement:
                hostile["audit"]["authenticated_v30"][name].__setitem__(
                    "sha256", current))
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
            ("static_first_party_non_delegation", "PASS"),
            ("historical_v30_static_first_party_non_delegation", "FAIL"),
            ("historical_v30_audit_build_differs_from_current_v33", False),
            ("superseded_v106_static_claim_falsified", False),
            ("superseded_v107_static_claim_falsified", False),
            ("current_v33_external_regex_engine_count", 0),
            ("current_v33_external_regex_package_count", 0),
            ("current_v33_external_regex_symbol_count", 0),
            ("zig_original_correctness_status", "FAIL"),
            ("zig_verified_original_case_count", 18_056),
            ("zig_speed_relative_to_python", 1.5),
            ("c_original_correctness_status", "FAIL"),
            ("c_verified_original_case_count", 22_798),
            ("c_observed_difference_count", 224),
            ("latest_rust_v35_original_correctness", "PASS"),
            ("latest_rust_v35_speed_relative_to_python", 1.50),
            ("latest_rust_v35_static_first_party_non_delegation", "PASS"),
            ("latest_rust_v35_live_runtime_non_delegation", "ESTABLISHED"),
            ("v109_stale_c_correctness_claim_falsified", False),
            ("c_speed_relative_to_python", 1.5),
            ("final_hidden_speed", "1.5x"),
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
            require(wrote > 0, "exclusive V111 graph publication stopped")
            position += wrote
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require the actual committed-and-pushed V111 source: " + label)
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
                "render only an unsigned prospective V111 source freeze")
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
    source = (SOURCE, fingerprint(options.source_sha256, "V111 graph renderer"),
              options.source_bytes)
    protocol = (PROTOCOL, fingerprint(options.protocol_sha256, "V111 graph protocol"),
                options.protocol_bytes)
    require(1 <= options.source_bytes <= 262_144
            and 1 <= options.protocol_bytes <= 65_536,
            "independently pin the complete V111 source and protocol bytes")
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
                "independently pin the complete V111 contract byte size")
        actual_contract = (CONTRACT,
                           fingerprint(options.contract_sha256, "V111 graph contract"),
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
        "audit": document(raw[AUDIT[0]], "historical V30-only static audit"),
        "zig": document(raw[ZIG_PASS[0]], "current Zig original PASS; speed NOT MEASURED"),
        "c_result": document(raw[C_RESULT[0]], "current C original PASS; speed NOT MEASURED"),
        "c_previous": document(raw[C_PREVIOUS[0]], "historical complete C FAIL; all 224 preserved"),
        "rust_v35": document(raw[RUST_V35_BUILD[0]],
                              "latest Rust V35 source build; matching and speed NOT MEASURED"),
        "preserved_stale_v109": {
            key: (document(raw[owner[0]], "preserved stale V109 " + key)
                  if key == "contract" else raw[owner[0]])
            for key, owner in PRESERVED_STALE_V109.items()
        },
        "current_v110": {
            key: (document(raw[owner[0]], "current all-three V110 " + key)
                  if key in {"contract", "inputs", "summary"} else raw[owner[0]])
            for key, owner in CURRENT_V110.items()
        },
        "performance": document(raw[PERFORMANCE[0]], "actual corrected performance"),
        "summary": document(raw[SUMMARY[0]], "all corrected performance results"),
        "pairs": document(raw[RAW_PAIRS[0]], "all actual paired timing rows"),
        "v4_contract": document(raw[V4["contract"][0]], "V4 source freeze"),
        "v105_contract": document(raw[V105["contract"][0]], "V105 source freeze"),
        "falsified_v106": {
            key: (document(raw[owner[0]], "falsified V106 " + key)
                  if key in {"contract", "inputs", "summary"}
                  else raw[owner[0]])
            for key, owner in FALSIFIED_V106.items()
        },
        "falsified_v107": {
            key: (document(raw[owner[0]], "falsified V107 " + key)
                  if key == "contract" else raw[owner[0]])
            for key, owner in FALSIFIED_V107.items()
        },
        "corrected_v108": {
            key: (document(raw[owner[0]], "corrected V108 " + key)
                  if key == "contract" else raw[owner[0]])
            for key, owner in CORRECTED_V108.items()
        },
        "history": {label: {
            kind: document(raw[entry[kind][0]], label + " historical " + kind)
            for kind in ("summary", "receipt")
        } for label, entry in HISTORY.items()},
    }
    if actual_contract is not None:
        state["contract_document"] = document(raw[CONTRACT], "V111 source freeze")
    verify(state)
    if actual_contract is not None:
        require(state["contract_document"] == freeze(state),
                "reject a stale or incomplete user-friendly V111 source freeze")
    return state


def report(state: dict, hostile: int) -> dict:
    options = state["options"]
    return {
        "schema": "rebar-owned-all-three-speed-headline-v111-source-result",
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
        "historical_v30_static_first_party_non_delegation": "PASS",
        "historical_v30_native_engine_sha256": AUDITED_V30_ENGINE,
        "historical_v30_native_bridge_sha256": AUDITED_V30_BRIDGE,
        "historical_v30_adapter_sha256": AUDITED_V30_ADAPTER,
        "historical_v30_audit_build_differs_from_current_v33": True,
        "static_first_party_non_delegation": "NOT ESTABLISHED",
        "superseded_v106_static_claim_falsified": True,
        "superseded_v107_static_claim_falsified": True,
        "zig_original_correctness_status": "PASS",
        "zig_verified_original_case_count": ORIGINAL,
        "zig_speed_relative_to_python": "NOT MEASURED",
        "c_original_correctness_status": "PASS",
        "c_verified_original_case_count": ORIGINAL,
        "c_observed_difference_count": 0,
        "c_speed_relative_to_python": "NOT MEASURED",
        "previous_c_verified_original_case_count": 22_798,
        "previous_c_observed_difference_count": 224,
        "v109_stale_c_correctness_claim_falsified": True,
        "latest_rust_build_version": "V35",
        "latest_rust_v35_original_correctness": "NOT MEASURED",
        "latest_rust_v35_speed_relative_to_python": "NOT MEASURED",
        "latest_rust_v35_static_first_party_non_delegation": "NOT ESTABLISHED",
        "latest_rust_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "final_hidden_speed": "NOT MEASURED",
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
        print("truthful-current-speed-headline-v111: " + str(failure), file=sys.stderr)
        raise SystemExit(1)

