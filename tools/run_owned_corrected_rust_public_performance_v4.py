#!/usr/bin/env python3
"""Freeze and, only after root authorization, compare isolated Rust builds.

Every source-only mode installs a physical deny-default wall before inspecting
an explicitly listed public owner.  It cannot import a matcher, open any
candidate/native/final file, run a process, generate code, mutate a file, or
sample a clock.  The separately authorized actual operation uses a fresh
private overlay; no canonical candidate is ever activated or rewritten.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("the native public gate source imported a matching engine")

import _io
import builtins
import hashlib
import io
import os
import stat
import time


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
PRIVATE_DEVICE = 2049
SOURCE = "tools/run_owned_corrected_rust_public_performance_v4.py"
PROTOCOL = "oracle/phase2/RUST-CORRECTED-PUBLIC-PERFORMANCE-V4.md"
CONTRACT = "oracle/phase2/rust-corrected-public-performance-v4.json"
SCHEMA = "rebar-owned-corrected-rust-public-performance-v4"
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
MAX_PROCESS_BYTES = 128 * 1024 * 1024
MAX_JSON_DEPTH = 80
MAX_JSON_ITEMS = 600_000
PUBLIC_CORRECTNESS_CASES = 10_434
PUBLIC_PROFILE_CASES = 416
PUBLIC_PAIRED_ROUNDS = 4
PUBLIC_PAIRED_ROWS = 1_664
PUBLIC_ITERATIONS = 3
PUBLIC_WARMUPS = 1
PUBLIC_PROFILE_PASSES = 3
PUBLIC_CORRECTNESS_SEED = 5928217332825411634
PUBLIC_PROFILE_SEED = 5932739705720426289
PUBLIC_CORRECTNESS_MATRIX = "0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d"
PUBLIC_PROFILE_MATRIX = "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
ADAPTER_SHA256 = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31_934
BRIDGE_SHA256 = "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"
BRIDGE_BYTES = 148_720
V26_ENGINE_SHA256 = "fde7b6a6193cd3877753e0f119d29727014b836b2aa2e4c07bdcec0c9f29c102"
V27_ENGINE_SHA256 = "04492763937d0631f162514098ce5d3148e71de21fe7b4cd3f5f876b634f5876"
V28_ENGINE_SHA256 = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
V28_BRIDGE_SHA256 = "831d48942d04bd211e42702abbb19789ddead6564df4f817ea35900bf3931d82"
V28_ENGINE_BYTES = 672_424
V28_BRIDGE_BYTES = 148_592
V33_ADAPTER_SHA256 = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
V33_ADAPTER_BYTES = 34_039
V33_ENGINE_SHA256 = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
V33_ENGINE_BYTES = 672_440
V33_BRIDGE_SHA256 = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
V33_BRIDGE_BYTES = 148_728
V33_PUBLIC_PASS_SHA256 = "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9"
V33_EXACT_ORIGINAL_PASS_SHA256 = "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064"
HISTORICAL_V30_ORIGINAL_PASS_SHA256 = "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5"
V33_STATIC_PASS_SHA256 = "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203"
V33_ROOT_PATH = "/tmp/rebar-phase2-native-build-v9-rust-zy4tpbu8"
V33_ROOT_INODE = 11677247

# role, exact relative public owner, complete SHA-256, byte length, inode.
OWNERS = (
    ("previous_gate_v2_source", "tools/run_owned_rust_native_architecture_public_gate_v2.py", "96f7770f9b5eec4a093435f94e1a6158b78bcdbba045cb76386018a298103a1d", 89208, 430802),
    ("previous_gate_v2_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V2.md", "dfc84515df187cc0c7318eb9d36d33ad8472a6df02864c7297ada546a60446a8", 5053, 525228),
    ("previous_gate_v2_contract", "oracle/phase2/rust-native-architecture-public-gate-v2.json", "aca87ed3450127bc7afc3829bea37ac4087b41a2e2be84d39f80244d3748ef17", 19717, 525234),
    ("previous_gate_v2_actual_v26", "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-publication-receipt.json", "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906, 525333),
    ("previous_gate_v2_actual_v27", "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-publication-receipt.json", "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330, 525426),
    ("v28_source", "tools/reproduce_owned_rust_combined_source_build_v28.py", "4a1d2a1a4362fc791ddba601bcc6ac27d6338ad86d1ec6e62a057e80e1649de6", 108883, 430798),
    ("v28_protocol", "oracle/phase2/RUST-COMBINED-SOURCE-BUILD-V28.md", "1e319e4551535b5a5a78bbd751959c042e38514998ffcce14791df38eef1d519", 8410, 525227),
    ("v28_contract", "oracle/phase2/rust-combined-source-build-v28.json", "826e7d62a124491662506dee74076001080fad6b383bef9c951b24413b1da2fa", 27362, 525232),
    ("v28_publication", "oracle/phase2/evidence/native-source-build-v28-rust-phase2-v28-rust-combined-source-root-provenance-publication-receipt.json", "14b4e8ff5762269bf79a61f517b41b7b590497b4bb3b3262b53adf501c0b1a3a", 2384, 525540),
    ("v28_root", "oracle/phase2/evidence/native-source-build-v28-rust-phase2-v28-rust-combined-source-root-provenance-root-provenance-receipt.json", "01fcb306535d0f86e6ef2aaa27173cc333d16be0360e53581d7c3f83264b9484", 70622, 525541),
    ("previous_gate_v1_source", "tools/run_owned_rust_native_architecture_public_gate_v1.py", "e33fb00156d5e68666ca6a27e4443329119c0cdc66b580b921666524a2c7da22", 80785, 430772),
    ("previous_gate_v1_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V1.md", "3b95c9303addfe3c3f452e7498982783e8f7d8629d21b75a3c97b09aab64b528", 4271, 525176),
    ("previous_gate_v1_contract", "oracle/phase2/rust-native-architecture-public-gate-v1.json", "28b0387c55e9b6a78dfcc6003281c72f269bb6091db84d2273708deb4390a2c1", 17466, 525180),
    ("previous_gate_v1_actual_failure", "oracle/phase2/evidence/rust-native-architecture-public-gate-v1-v26-anchor-public-run-001-preexecution-failure.json", "3d46998a4ca70d50c06a7aa56daab7bf9312a9f42e816e0abf9fc1482ef55153", 1178, 525210),
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_p0", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("actual_original_v25_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json", "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("public_correctness_evidence_source", "tools/run_rust_public_correctness_evidence_v2.py", "e24a630c2ac60c49dd4ac707f80afc07a2516629e47c7b15fd4e7dca75102281", 56423, 429551),
    ("public_correctness_evidence_protocol", "oracle/phase3/RUST-PUBLIC-CORRECTNESS-EVIDENCE-V2.md", "edfac4466b60ec287b29eea2c881cce65e20d21576b3652723b9fae1666e1fb4", 6710, 525990),
    ("public_correctness_evidence_contract", "oracle/phase3/rust-public-correctness-evidence-v2.json", "3feeda3933ec0c54e76780da8f78c73ba07a951aa48ee3ff50007b6888569c73", 2634, 525989),
    ("public_correctness_source", "tools/rust_public_practice_benchmark_v2.py", "a3d7e70343d231bf433fbad6a6669025a970d83691c49cb9f434a186aef3d9e6", 112729, 429259),
    ("public_correctness_protocol", "oracle/phase3/RUST-PUBLIC-PRACTICE-BENCHMARK-V2.md", "4040c458119a6d347c1eb876e1120a4400f76b8f16611d21de15371b50508586", 8982, 525935),
    ("public_correctness_contract", "oracle/phase3/rust-public-practice-benchmark-v2.json", "7c4120c549a006cc162abb545032e1808637cf3c088f4a21023d5c99fb351e4a", 10117, 525936),
    ("public_profile_v1_source", "tools/rust_public_profile_v1.py", "ada1e9cfc8684ecb4fcf9294057347018b6058fc1619ae9de6a8b31097aa1562", 79693, 429476),
    ("public_profile_v1_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V1.md", "6664f17ddd65c1953782f43b7fe1fa01427f1f510adfbad86fe8efdb135829ba", 5281, 525927),
    ("public_profile_v1_contract", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("public_profile_v2_source", "tools/rust_public_profile_v2.py", "a4eb77c29e06b1a77152ebb2275525bfd75b3fa26fd25f100059c79cfb39437a", 31941, 429686),
    ("public_profile_v2_protocol", "oracle/phase3/RUST-PUBLIC-PROFILE-V2.md", "aa96b3a2132be6557020a753da8e57e1c210b1a9b9216b6a015f36715e208b9d", 3128, 526049),
    ("public_profile_v2_contract", "oracle/phase3/rust-public-profile-v2.json", "9687806994bcbb401ed89cba11197b79a491da023b95be89e1686a7c6cccafea", 3926, 526050),
    ("previous_public_stdlib_observations", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("previous_public_rust_observations", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("previous_public_paired_timings", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("previous_public_v2_summary", "oracle/phase3/evidence/rust-public-profile-v2-complete-summary-v1.json", "1f2dcbdabfd8e7c054996fc044fcaa32bebf86f5a12e5486398a720833ea5e18", 509123, 524847),
    ("previous_public_v2_receipt", "oracle/phase3/evidence/rust-public-profile-v2-run-001-publication-receipt.json", "dc3cf00d5cf070cd7b922b8aef8b21a59e9d7eae4ab0655b7a02898e2975ce8e", 757, 524844),
    ("v26_source", "tools/reproduce_owned_rust_anchor_source_build_v26.py", "7a276a4bf675f818cfe3716aad13c5e741f4a45709e899c82af36e2b4cb10e66", 112085, 430771),
    ("v26_protocol", "oracle/phase2/RUST-ANCHOR-SOURCE-BUILD-V26.md", "06ffb539e1f9e2bf7350b1d27478c988dd7c429f2ee295e40181b9320b3e3fd3", 7578, 524812),
    ("v26_contract", "oracle/phase2/rust-anchor-source-build-v26.json", "ea213e235fb56ca4235763643d5569ebb1b63c45678363efe322a525eef65924", 21189, 524863),
    ("v26_publication", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-publication-receipt.json", "8a0e9d70dab2a3e1f3738d6e0e1a4716b78e0a1b329ce3b16010bd94b6598cd6", 5075, 524963),
    ("v26_root", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-root-provenance-receipt.json", "aaed35f9fe86090d75ce2162bae7902910461a7b4e731c22eba275406f328ba1", 76442, 524964),
    ("v27_source", "tools/reproduce_owned_rust_compiler_fastpath_source_build_v27.py", "4ac3123d83db6858a9fddd311b3b7ac7966e29aede6e786594c7d956e2bf9e8e", 245008, 429062),
    ("v27_protocol", "oracle/phase2/RUST-COMPILER-FASTPATH-SOURCE-BUILD-V27.md", "43b81f47a196d3db0972269d6fba4d94b4437cb59a1c5a3648d8d45f5939fa5f", 5810, 524809),
    ("v27_contract", "oracle/phase2/rust-compiler-fastpath-source-build-v27.json", "a2ffa190a8fd15ec3bcf82f0e1eedc5eb4b919af8c6b3fbf99cf54a525604a41", 617433, 524861),
    ("v27_publication", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-publication-receipt.json", "7fcbe3e07885f2a488ed1b3c79bc02888ad22dd2b21179081b3cecfc7b464c99", 6444, 524869),
    ("v27_root", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-root-provenance-receipt.json", "c6958056757ab6145d613490db1a21165714dcb89c61e6d3bdf52500fad221b0", 64122, 524870),
    ("v3_gate_source", "tools/run_owned_rust_native_architecture_public_gate_v3.py", "12d0ae388cd2841d0cb091e7da88859a772a3b3c293f18938b488196a32c5eab", 106590, 431279),
    ("v3_gate_protocol", "oracle/phase2/RUST-NATIVE-ARCHITECTURE-PUBLIC-GATE-V3.md", "fdf695478fc1b542026c2b98ba94524df254aea84b46ebab568a98050474cae4", 5911, 525630),
    ("v3_gate_contract", "oracle/phase2/rust-native-architecture-public-gate-v3.json", "80a350478ae4dbf4d745683974b4c60630d900d2e3f97d59cf391bfb1d8358a0", 26615, 525842),
    ("v28_public_gate", "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-v28-combined-public-run-001-publication-receipt.json", "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372, 525923),
    ("v26_public_summary", "experiments/rust_native_architecture_public_v2/v26-anchor-public-run-001/public-416-performance-summary.raw.json", "33619312085764d72b9b9b6ae43cb021fb54b88d64a272ce5c183826a7a00d5e", 26200, 525332),
    ("v27_public_summary", "experiments/rust_native_architecture_public_v2/v27-compiler-public-run-001/public-416-performance-summary.raw.json", "ce2d8c94d739c5f2d87f2fa65c19ef9301ee62cac7e2233b654ba25094d9e50b", 53579, 525425),
    ("v28_public_summary", "experiments/rust_native_architecture_public_v3/v28-combined-public-run-001/public-416-performance-summary.raw.json", "add311f5c6734505b733988bbce0b14fccd410aa8462c17fe05f3cb4fb99f414", 25640, 525922),
    ("v33_source", "tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py", "31251c3aa6006108ba1a5b5e7b5a07147d9b8ccf76123f4aa08ecffb20c91c63", 172881, 429226),
    ("v33_protocol", "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md", "c73843e1705beb24e4ced9ab3d9fa95da7420c5d24cd8f6ffaeeb747aa382071", 7434, 524906),
    ("v33_contract", "oracle/phase2/rust-full-public-semantic-source-build-v33.json", "bb7d338cb766b7f1ff52e616355d5d5cddb00849532e42755b31a9bf09119337", 56235, 525061),
    ("v33_publication", "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-publication-receipt.json", "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749", 6696, 525066),
    ("v33_root", "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-root-provenance-receipt.json", "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c", 80421, 525067),
    ("v33_full_public_source", "tools/run_owned_rust_full_public_correctness_v5.py", "97d36e9448336d3cfa732324779c14959bf739a8e6daa556d839e0ecdd0d0602", 83637, 430313),
    ("v33_full_public_protocol", "oracle/phase2/RUST-FULL-PUBLIC-CORRECTNESS-V5.md", "066f3e4663bb19612b795f797144c0098bf2d998455d3c0b4c814186d0204bd0", 6570, 525361),
    ("v33_full_public_contract", "oracle/phase2/rust-full-public-correctness-v5.json", "fd10e77356945e7544d5b5b91d7a95f95c173384e152506e02c11240b58eb52c", 31041, 525365),
    ("v33_public_pass", "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-publication-receipt.json", V33_PUBLIC_PASS_SHA256, 6889, 525451),
    ("v28_exact_original_source", "tools/run_owned_repaired_rust_original_campaign_v28.py", "462cdd40dc2b9afea685327e882fbd53239e75c86b7f5bc4231e962c3c968f37", 123289, 430834),
    ("v28_exact_original_protocol", "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V28.md", "8252325bc228f26130cdc301ed06661a737ed70e0ecea42cb99ac1864be1ea55", 9768, 526094),
    ("v28_exact_original_contract", "oracle/phase2/repaired-rust-original-campaign-v28.json", "b049a76b4d8cb1501f65bdd724aab414d85c3516dc13825dd0d76d451db20683", 29027, 526114),
    ("v28_exact_original_entry_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v28-exact-reproduction-failure.json", "c552d72cc3544c65a5811515853d966d402e9a654846082a4bfc7244caa9ea80", 1027, 526147),
    ("v28_exact_original_worker_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v28-unrecorded-worker-failure.json", "5f72042155383ae3e8deeefc8e97cb418e0457088aed84518e9552511daa9ece", 275, 526135),
    ("v33_exact_original_pass", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-original-p0-v28-publication-receipt.json", V33_EXACT_ORIGINAL_PASS_SHA256, 12067, 526161),
    ("v26_original_pass", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v30-rust-complete-semantic-source-root-provenance-original-p0-v26-publication-receipt.json", HISTORICAL_V30_ORIGINAL_PASS_SHA256, 12055, 525046),
    ("static_audit_source", "tools/audit_clean_rust_runtime_non_delegation_v5.py", "5ab79fc493f1b798d1020311dddf7a061e5b272d3c6f2c10e19127311b57b542", 86600, 428898),
    ("static_audit_protocol", "oracle/phase2/RUST-CLEAN-NON-DELEGATION-V5.md", "4efa6122a16c438224f226f468d0654473df489fa338f2539ae22411ce4d01fa", 5918, 525041),
    ("static_audit_contract", "oracle/phase2/rust-clean-non-delegation-v5.json", "605e0a55f57d1e5c9061bcefe9323bf4de62905c92ca9a29021a79503546cd57", 6150, 525047),
    ("static_audit_pass", "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json", V33_STATIC_PASS_SHA256, 16427, 525089),
)

# role, path, sha256, byte length, inode, exact permission.
CANONICAL_ORIGINALS = (
    ("rust_source", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096, 0o600),
    ("rust_search_source", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682, 0o600),
    ("rust_bridge_source", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054, 0o600),
    ("rust_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100, 0o600),
    ("rust_engine", "candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", 660440, 430563, 0o755),
    ("rust_bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", 144992, 430629, 0o755),
)


class GateError(Exception):
    """Reject substituted public evidence or an unsafe architecture run."""


def require(value: object, message: str) -> None:
    if value is not True:
        raise GateError(message)


def digest(value: bytes) -> str:
    require(type(value) is bytes, "hash only complete actual bytes")
    return hashlib.sha256(value).hexdigest()


def check_sha(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(item in "0123456789abcdef" for item in value),
            "require an exact lowercase SHA-256: " + label)
    assert isinstance(value, str)
    return value


def check_commit(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(item in "0123456789abcdef" for item in value),
            "require an exact 40-character lowercase Git commit: " + label)
    assert isinstance(value, str)
    return value


def quoted(value: str) -> str:
    require(type(value) is str, "require an actual JSON string")
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    pieces = ['"']
    for item in value:
        point = ord(item)
        require(not 0xD800 <= point <= 0xDFFF, "reject unpaired Unicode surrogates")
        pieces.append(escapes.get(item, "\\u" + format(point, "04x")
                                  if point < 32 else item))
    pieces.append('"')
    return "".join(pieces)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "reject unbounded canonical JSON depth")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quoted(value)
    if type(value) is int:
        return str(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value), "reject nontext JSON keys")
        return "{" + ",".join(quoted(key) + ":" + canonical(value[key], depth + 1)
                                for key in sorted(value)) + "}"
    raise GateError("reject unsupported, floating, or nonfinite source evidence")


def document(value: object) -> bytes:
    return (canonical(value) + "\n").encode("utf-8")


class StrictJSON:
    """Bounded strict parser that never imports CPython's regex engine."""

    def __init__(self, raw: bytes) -> None:
        require(type(raw) is bytes and 0 < len(raw) <= MAX_OWNER_BYTES,
                "reject unbounded frozen public evidence")
        self.text = raw.decode("utf-8", "strict")
        self.index = 0
        self.items = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"', "require a JSON string")
        self.index += 1
        output: list[str] = []
        escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                   "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            item = self.text[self.index]
            self.index += 1
            if item == '"':
                return "".join(output)
            if item != "\\":
                require(ord(item) >= 32 and not 0xD800 <= ord(item) <= 0xDFFF,
                        "reject malformed raw JSON characters")
                output.append(item)
                continue
            require(self.index < len(self.text), "reject incomplete JSON escape")
            escaped = self.text[self.index]
            self.index += 1
            if escaped != "u":
                require(escaped in escapes, "reject unknown JSON escape")
                output.append(escapes[escaped])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(char in "0123456789abcdefABCDEF" for char in digits),
                    "reject malformed escaped Unicode")
            self.index += 4
            point = int(digits, 16)
            if 0xD800 <= point <= 0xDBFF:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "reject unpaired high surrogate")
                digits = self.text[self.index + 2:self.index + 6]
                require(len(digits) == 4
                        and all(char in "0123456789abcdefABCDEF" for char in digits),
                        "reject malformed escaped low surrogate")
                low = int(digits, 16)
                require(0xDC00 <= low <= 0xDFFF, "reject unpaired high surrogate")
                self.index += 6
                output.append(chr(0x10000 + ((point - 0xD800) << 10)
                                  + low - 0xDC00))
            else:
                require(not 0xDC00 <= point <= 0xDFFF,
                        "reject unpaired low surrogate")
                output.append(chr(point))
        raise GateError("reject an unterminated JSON string")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "reject an incomplete JSON number")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "reject a leading-zero JSON integer")
        else:
            require(self.text[self.index] in "123456789", "reject malformed JSON")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fractional = self.text[self.index:self.index + 1] == "."
        if fractional:
            self.index += 1
            digits = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > digits, "reject an incomplete JSON decimal")
        require(self.index - start <= 128, "reject an oversized JSON number")
        require(self.text[self.index:self.index + 1] not in ("e", "E"),
                "reject unbounded or nonfinite exponential frozen evidence")
        token = self.text[start:self.index]
        if not fractional:
            return int(token)
        value = float(token)
        require(value == value and -1e300 < value < 1e300,
                "reject a nonfinite frozen public decimal")
        return value

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "reject unbounded JSON depth")
        self.whitespace()
        require(self.index < len(self.text), "reject missing JSON values")
        item = self.text[self.index]
        if item == '"':
            return self.string()
        if item == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "reject duplicate JSON key: " + key)
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject an oversized JSON object")
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "reject missing JSON object colon")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "reject malformed JSON object")
        if item == "[":
            self.index += 1
            result: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result
            while True:
                self.items += 1
                require(self.items <= MAX_JSON_ITEMS, "reject an oversized JSON array")
                result.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result
                require(separator == ",", "reject malformed JSON array")
        if item == "-" or item in "0123456789":
            return self.number()
        for literal, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.index):
                self.index += len(literal)
                return value
        raise GateError("reject malformed or nonfinite frozen JSON")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "reject trailing frozen JSON data")
        return result


def json_object(raw: bytes, role: str) -> dict:
    try:
        result = StrictJSON(raw).decode()
    except GateError as error:
        raise GateError(role + ": " + str(error)) from error
    require(type(result) is dict, "require a complete JSON object: " + role)
    assert isinstance(result, dict)
    return result


def no_matching_imports() -> None:
    forbidden = ("re", "_sre", "regex", "_regex", "re2", "pcre", "pcre2",
                 "oniguruma", "sre_compile", "sre_parse", "ctypes", "candidates",
                 "rebar", "subprocess", "socket", "threading", "multiprocessing",
                 "concurrent.interpreters")
    require(not any(name == item or name.startswith(item + ".")
                    for name in sys.modules for item in forbidden),
            "source-only gate imported a matcher, candidate, native loader, or worker")


class SourceWall:
    """Physically deny all paths except the exact frozen public source owners."""

    def __init__(self) -> None:
        self.allowed = frozenset((ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
                                  ROOT + "/" + CONTRACT)
                                 + tuple(ROOT + "/" + row[1] for row in OWNERS))
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.holdout_content_open_count = 0
        self.native_content_open_count = 0
        self.candidate_content_open_count = 0
        self.write_count = 0
        self.process_count = 0
        self.clock_samples = 0
        self.installed = False
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise GateError("native architecture source wall rejected " + category)

    def approved_read(self, path: object) -> bool:
        if type(path) is not str or path not in self.allowed:
            return False
        assert isinstance(path, str)
        return (path.startswith(ROOT + "/") and path == os.path.normpath(path)
                and not any(item in (".", "..") for item in path.split("/"))
                and not path.endswith((".so", ".gz", ".er"))
                and "/candidates/" not in path
                and not any(token in path.lower()
                            for token in ("holdout", "hidden", "sealed", "proposal")))

    def audit(self, event: str, args: tuple) -> None:
        if event == "open":
            path = args[0] if args else None
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else None
            forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                         | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
            if (self.approved_read(path) and type(flags) is int
                    and not flags & forbidden
                    and bool(flags & getattr(os, "O_NOFOLLOW", 0))
                    and not (type(mode) is str and any(char in mode for char in "wax+"))):
                return
            if type(path) is str and any(token in path.lower()
                                         for token in ("holdout", "hidden", "sealed",
                                                       "proposal")):
                self.deny("unopened-final-holdout-content-open")
            self.deny("unowned-candidate-native-public-or-write-open")
        if (event in ("import", "exec", "compile", "marshal.loads", "os.system",
                      "os.fork", "os.posix_spawn", "os.posix_spawnp", "os.mkdir",
                      "os.rename", "os.replace", "os.remove", "os.unlink",
                      "os.rmdir", "os.chmod", "os.chown", "os.urandom",
                      "os.getrandom", "_interpreters.create", "_interpreters.exec",
                      "cpython.PyInterpreterState_New", "code.__new__")
                or event.startswith(("subprocess.", "socket.", "ctypes.",
                                     "threading.", "multiprocessing.", "tempfile.",
                                     "time.", "os.exec", "os.spawn"))):
            self.deny("candidate-native-process-clock-mutation-or-dynamic-code")

    def forbidden(self, category: str):
        def reject(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return reject

    def guarded_open(self, path: object, flags: object,
                     mode: int = 0o777, *, dir_fd: object = None) -> int:
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                     | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
                     | getattr(os, "O_DIRECTORY", 0))
        if (dir_fd is not None or not self.approved_read(path)
                or type(flags) is not int or bool(flags & forbidden)
                or not flags & getattr(os, "O_NOFOLLOW", 0)):
            self.deny("unowned-destructive-or-symlink-os-open")
        assert isinstance(path, str) and isinstance(flags, int)
        descriptor = self.native_open(path, flags, mode)
        require(type(descriptor) is int and descriptor >= 0
                and descriptor not in self.live,
                "reject a repeated or invalid source descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (type(descriptor) is not int or descriptor not in self.live
                or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES):
            self.deny("foreign-or-unbounded-descriptor-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.native_read(descriptor, count)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign-descriptor-metadata")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign-descriptor-close")
        self.live.remove(descriptor)
        self.native_close(descriptor)

    def install(self) -> None:
        require(not self.installed, "install the source wall exactly once")
        sys.addaudithook(self.audit)
        builtins.open = self.forbidden("builtins-open")
        _io.open = self.forbidden("direct-_io-open")
        _io.FileIO = self.forbidden("direct-_io-fileio")
        io.open = self.forbidden("direct-io-open")
        io.FileIO = self.forbidden("direct-io-fileio")
        for module in (_io, io):
            if hasattr(module, "open_code"):
                setattr(module, "open_code", self.forbidden("direct-open-code"))
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        for name in ("write", "fsync", "fdopen", "dup", "dup2", "stat", "lstat",
                     "readlink", "listdir", "scandir", "walk", "fwalk", "access",
                     "fork", "posix_spawn", "posix_spawnp", "system", "mkdir",
                     "makedirs", "remove", "unlink", "rename", "replace", "rmdir",
                     "chmod", "chown", "urandom", "getrandom"):
            if hasattr(os, name):
                setattr(os, name, self.forbidden("direct-os-" + name))
        for name in ("time", "time_ns", "monotonic", "monotonic_ns",
                     "perf_counter", "perf_counter_ns", "process_time",
                     "process_time_ns", "thread_time", "thread_time_ns",
                     "clock_gettime", "clock_gettime_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.forbidden("clock-" + name))
        self.installed = True


def read_owner(wall: SourceWall | None, row: tuple) -> bytes:
    role, relative, expected, count, inode = row
    check_sha(expected, relative)
    require(type(role) is str and type(relative) is str and type(count) is int
            and 0 < count <= MAX_OWNER_BYTES and type(inode) is int and inode > 0,
            "reject an incomplete pinned public owner")
    path = ROOT + "/" + relative
    require(wall is None or wall.installed and wall.approved_read(path),
            "install the physical source wall before opening public owners")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject a substituted frozen public owner: " + role)
        remaining = count
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block),
                    "reject a truncated public owner: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"", "reject a grown public owner")
        after = os.fstat(descriptor)
        require(all(getattr(before, name) == getattr(after, name)
                    for name in ("st_dev", "st_ino", "st_size", "st_nlink",
                                 "st_mtime_ns", "st_ctime_ns")),
                "reject a concurrently altered public owner: " + role)
        result = b"".join(blocks)
        require(digest(result) == expected, "reject altered public owner: " + role)
        return result
    finally:
        os.close(descriptor)


def dynamic_owner(wall: SourceWall | None, role: str,
                  relative: str, expected: str) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject an unrelated dynamic public architecture owner")
    check_sha(expected, relative)
    path = ROOT + "/" + relative
    require(wall is None or wall.installed and wall.approved_read(path),
            "install the wall before inspecting its own source")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
                and info.st_dev == DEVICE and info.st_nlink == 1
                and info.st_uid == os.geteuid()
                and 0 < info.st_size <= MAX_OWNER_BYTES,
                "reject a replaced live public architecture owner")
        return role, relative, expected, info.st_size, info.st_ino
    finally:
        os.close(descriptor)


def owner_pin(row: tuple) -> dict:
    role, relative, sha256, size, inode = row
    return {"role": role, "path": relative, "sha256": sha256, "bytes": size,
            "device": DEVICE, "inode": inode, "mode": "0600", "nlink": 1}


WORKER_BOOTSTRAP = r'''
import hashlib
import os
from pathlib import Path
import sys
import types

overlay, harness, source_hash, role, engine, mode = sys.argv[1:]
if not overlay.startswith('/tmp/rebar-rust-corrected-performance-v4-'):
    raise RuntimeError('reject nonexclusive public architecture overlay')
if harness not in ('rust_public_practice_benchmark_v2.py', 'rust_public_profile_v1.py'):
    raise RuntimeError('reject unapproved public architecture worker harness')
path = os.path.join(overlay, 'tools', harness)
descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
try:
    chunks = []
    while True:
        chunk = os.read(descriptor, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    payload = b''.join(chunks)
finally:
    os.close(descriptor)
if hashlib.sha256(payload).hexdigest() != source_hash:
    raise RuntimeError('reject altered unchanged public architecture harness')
sys.path[:] = [overlay] + [item for item in sys.path
                            if item != '/home/dev-user/src/rebar']
namespace = {'__name__': '_rebar_owned_public_worker', '__file__': path,
             '__package__': None}
exec(compile(payload, path, 'exec'), namespace)
namespace['ROOT'] = Path(overlay)
sys.path[:] = [overlay] + [item for item in sys.path
                            if item not in (overlay, '/home/dev-user/src/rebar')]
namespace['verify_pinned_runtime']()
forbidden_roots = ('re', '_sre', 'regex', '_regex', 're2', 'pcre', 'pcre2',
                   'oniguruma', 'sre_compile', 'sre_parse', 'sre_constants')
preexisting_reference_modules = {name for name in sys.modules
                                 if name.split('.')[0] in forbidden_roots}
if mode == 'observe':
    result = namespace['observe_worker'](role, engine)
elif mode == 'timing':
    result = namespace['timing_worker'](role, engine)
elif mode == 'profile':
    result = namespace['profile_worker'](role, engine)
else:
    raise RuntimeError('reject an unapproved public architecture worker mode')
if engine == 'rust':
    introduced = {name for name in sys.modules
                  if name.split('.')[0] in forbidden_roots}
    if not introduced.issubset(preexisting_reference_modules):
        raise RuntimeError('a candidate imported an external matching engine')
    for name, module in tuple(sys.modules.items()):
        if name == 'candidates' or name.startswith('candidates.'):
            for value in vars(module).values():
                if isinstance(value, types.ModuleType):
                    root = value.__name__.split('.')[0]
                    if root in forbidden_roots:
                        raise RuntimeError('a candidate owns an external matching engine')
sys.stdout.buffer.write(namespace['canonical'](result))
'''.strip()


def validate_previous_public_gate(payloads: dict[str, bytes]) -> dict:
    source = next(row for row in OWNERS if row[0] == "previous_gate_v2_source")
    protocol = next(row for row in OWNERS if row[0] == "previous_gate_v2_protocol")
    contract = next(row for row in OWNERS if row[0] == "previous_gate_v2_contract")
    frozen = json_object(payloads["previous_gate_v2_contract"], "immutable V2 public gate")
    require(frozen.get("schema")
            == "rebar-owned-rust-native-architecture-public-gate-v2-source-freeze"
            and frozen.get("source_sha256") == source[2]
            and frozen.get("protocol_sha256") == protocol[2]
            and frozen.get("candidate_qualified") is False
            and frozen.get("winner_selected") is False
            and frozen.get("current_final_holdout")
            == "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "preserve the immutable V2 architecture comparison source freeze")
    published = {}
    expected = {"v26": (247, 11), "v27": (138, 143)}
    for version in ("v26", "v27"):
        owner = "previous_gate_v2_actual_" + version
        actual = json_object(payloads[owner], "published V2 " + version)
        gate = actual.get("public_416_correctness_gate")
        performance = actual.get("performance_summary")
        faster, regressions = expected[version]
        require(actual.get("schema")
                == "rebar-owned-rust-native-architecture-public-gate-v2-durable-publication-receipt"
                and actual.get("status") == "PASS"
                and actual.get("architecture") == version
                and actual.get("source_sha256") == source[2]
                and actual.get("protocol_sha256") == protocol[2]
                and actual.get("contract_sha256") == contract[2]
                and actual.get("public_10434_correctness_status") == "FAIL"
                and actual.get("public_10434_case_count") == PUBLIC_CORRECTNESS_CASES
                and actual.get("public_10434_mismatch_count") == 1145
                and type(gate) is dict and gate.get("status") == "PASS"
                and gate.get("case_count") == PUBLIC_PROFILE_CASES
                and gate.get("mismatch_count") == 0
                and actual.get("paired_row_count") == PUBLIC_PAIRED_ROWS
                and type(performance) is dict
                and performance.get("case_count") == PUBLIC_PROFILE_CASES
                and performance.get("paired_row_count") == PUBLIC_PAIRED_ROWS
                and performance.get("faster_case_count") == faster
                and performance.get("regression_over_20_percent_count") == regressions
                and actual.get("canonical_candidate_modified") is False
                and actual.get("candidate_qualified") is False
                and actual.get("winner_selected") is False
                and actual.get("hidden_cases_read") == 0,
                "preserve complete actual V2 public correctness and paired evidence")
        published[version] = {"receipt_sha256": digest(payloads[owner]),
                              "public_10434_mismatch_count": 1145,
                              "public_416_case_count": PUBLIC_PROFILE_CASES,
                              "paired_row_count": PUBLIC_PAIRED_ROWS,
                              "faster_case_count": faster,
                              "regression_over_20_percent_count": regressions,
                              "geomean_speedup_display": format(
                                  performance["geomean_speedup_vs_stdlib"], ".17g")}
    return {"source_sha256": source[2], "protocol_sha256": protocol[2],
            "contract_sha256": contract[2], "actual_public_results": published,
            "candidate_qualified": False, "winner_selected": False}


def validate_previous_gate(payloads: dict[str, bytes]) -> dict:
    previous = json_object(payloads["previous_gate_v1_contract"],
                           "immutable failed V1 public gate contract")
    failure = json_object(payloads["previous_gate_v1_actual_failure"],
                          "actual V1 preexecution failure")
    source = next(row for row in OWNERS if row[0] == "previous_gate_v1_source")
    protocol = next(row for row in OWNERS if row[0] == "previous_gate_v1_protocol")
    contract = next(row for row in OWNERS if row[0] == "previous_gate_v1_contract")
    require(previous.get("schema")
            == "rebar-owned-rust-native-architecture-public-gate-v1-source-freeze"
            and previous.get("source_sha256") == source[2]
            and previous.get("protocol_sha256") == protocol[2]
            and previous.get("candidate_qualified") is False
            and previous.get("winner_selected") is False
            and previous.get("current_final_holdout")
            == "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "preserve the complete immutable failed predecessor source freeze")
    prior_search = [row for row in previous.get("canonical_candidates", ())
                    if type(row) is dict and row.get("role") == "rust_search_source"]
    require(len(prior_search) == 1
            and prior_search[0].get("path")
            == "candidates/rust/src/search_acceleration.rs"
            and prior_search[0].get("sha256")
            == "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"
            and prior_search[0].get("bytes") == 14773
            and prior_search[0].get("device") == DEVICE
            and prior_search[0].get("inode") == 429682,
            "preserve the exact failed V1 nonexistent canonical-source claim")
    require(failure.get("schema")
            == "rebar-rust-native-architecture-public-gate-v1-preexecution-failure"
            and failure.get("status") == "FAIL"
            and failure.get("architecture") == "v26"
            and failure.get("session") == "v26-anchor-public-run-001"
            and failure.get("source_sha256") == source[2]
            and failure.get("protocol_sha256") == protocol[2]
            and failure.get("contract_sha256") == contract[2]
            and check_commit(failure.get("frozen_commit"), "failed V1 frozen commit")
            == "38a0ad686c6ff7443ebff61356418ef4becb1cc9"
            and failure.get("candidate_workers_started") == 0
            and failure.get("paired_row_count") == 0
            and failure.get("canonical_candidate_modified") is False
            and failure.get("candidate_qualified") is False
            and failure.get("winner_selected") is False
            and failure.get("public_10434_correctness") == "NOT RUN"
            and failure.get("public_416_correctness") == "NOT RUN"
            and failure.get("hidden_case_files_generated") == 0
            and failure.get("hidden_cases_read") == 0
            and failure.get("current_final_holdout")
            == "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
            and type(failure.get("error")) is str
            and "search_acceleration.rs" in failure["error"],
            "preserve the exact complete fail-closed preexecution predecessor")
    return {"source_sha256": source[2], "protocol_sha256": protocol[2],
            "contract_sha256": contract[2],
            "failure_receipt_sha256": digest(payloads["previous_gate_v1_actual_failure"]),
            "frozen_commit": failure["frozen_commit"],
            "failure_status": "FAIL", "candidate_workers_started": 0,
            "paired_row_count": 0,
            "incorrect_canonical_search_path": prior_search[0]["path"],
            "root_cause": "NONEXISTENT CANONICAL SEARCH SOURCE PATH"}


def validate_search_identity(row: object, provenance: str) -> dict:
    require(type(row) is dict, "require a complete canonical search owner: " + provenance)
    assert isinstance(row, dict)
    require(row.get("path") == "candidates/rust/src/search.rs"
            and row.get("sha256")
            == "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe"
            and row.get("bytes") == 14773 and row.get("device") == DEVICE
            and row.get("inode") == 429682 and row.get("mode") == "0600"
            and row.get("nlink") == 1,
            "reject absent, incorrect, or substituted canonical search owner: "
            + provenance)
    return {"path": row["path"], "sha256": row["sha256"], "bytes": row["bytes"],
            "device": row["device"], "inode": row["inode"],
            "mode": row["mode"], "nlink": row["nlink"]}


def validate_canonical_search_provenance(payloads: dict[str, bytes]) -> dict:
    root = json_object(payloads["v26_root"], "actual V26 canonical source provenance")
    for field in ("actual_original_source_identities_before",
                  "actual_original_source_identities_after"):
        owners = root.get(field)
        require(type(owners) is dict,
                "reject missing receipt-authenticated V26 canonical source owners")
        validate_search_identity(owners.get("candidates/rust/src/search.rs"),
                                 "V26 actual root " + field)
    contract = json_object(payloads["v27_contract"], "V27 canonical source contract")
    rows = contract.get("authenticated_first_party_source_owners")
    require(type(rows) is list, "require authenticated V27 canonical source owners")
    matches = [row for row in rows if type(row) is dict
               and row.get("path") == "candidates/rust/src/search.rs"]
    require(len(matches) == 1,
            "require exactly one authenticated V27 canonical search source")
    original = validate_search_identity(matches[0], "V27 complete build contract")
    canonical_rows = [row for row in CANONICAL_ORIGINALS
                      if row[0] == "rust_search_source"]
    require(len(canonical_rows) == 1,
            "require exactly one corrected live canonical search source")
    role, path, sha256, size, inode, mode = canonical_rows[0]
    require(role == "rust_search_source"
            and {"path": path, "sha256": sha256, "bytes": size, "device": DEVICE,
                 "inode": inode, "mode": format(mode, "04o"), "nlink": 1}
            == original,
            "require the live canonical snapshot to match both real public receipts")
    return {"canonical_search": original,
            "v26_root_receipt_sha256": digest(payloads["v26_root"]),
            "v27_contract_sha256": digest(payloads["v27_contract"]),
            "receipt_authentications": 3,
            "candidate_content_open_count": 0,
            "corrected_nonexistent_v1_path": "candidates/rust/src/search_acceleration.rs"}


def validate_public_context(payloads: dict[str, bytes]) -> dict:
    original = json_object(payloads["original_p0"], "original P0")
    require(original.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and original.get("status") == "PASS"
            and original.get("original_case_execution_denominator") == 31237
            and original.get("original_suite_count") == 13
            and original.get("qualified_candidate_count") == 0,
            "preserve the original 31,237-case failed qualification boundary")
    failure = json_object(payloads["actual_original_v25_failure"], "actual V25")
    require(failure.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and failure.get("status") == "PASS"
            and failure.get("publication_status") == "PASS"
            and failure.get("candidate_status") == "FAIL"
            and failure.get("case_execution_denominator") == 31237
            and failure.get("completed_suite_count") == 13
            and failure.get("actual_candidate_workers") == 13
            and failure.get("semantic_mismatch_count") == 1352
            and failure.get("verified_passing_case_count") == 15877
            and failure.get("candidate_qualified") is False
            and failure.get("holdout") == "NOT OPENED",
            "preserve all actual failed original-correctness evidence")
    failing = {row["suite"]: row["mismatch_count"]
               for row in failure["suite_integrity"] if row["mismatch_count"]}
    require(failing == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve the exact 1,352 published original-suite mismatches")
    practice = json_object(payloads["public_correctness_contract"], "public 10,434")
    evidence = json_object(payloads["public_correctness_evidence_contract"],
                           "public correctness evidence")
    profile1 = json_object(payloads["public_profile_v1_contract"], "public 416 v1")
    profile2 = json_object(payloads["public_profile_v2_contract"], "public 416 v2")
    require(practice.get("case_count") == PUBLIC_CORRECTNESS_CASES
            and practice.get("published_seed") == PUBLIC_CORRECTNESS_SEED
            and practice.get("dataset_count") == 94
            and practice.get("operation_count") == 111
            and evidence.get("case_count") == PUBLIC_CORRECTNESS_CASES,
            "preserve the exact frozen balanced 10,434-case public matrix")
    for name, contract in (("v1", profile1), ("v2", profile2)):
        require(contract.get("case_count") == PUBLIC_PROFILE_CASES
                and contract.get("dataset_count") == 16
                and contract.get("operation_count") == 26
                and contract.get("published_seed") == PUBLIC_PROFILE_SEED
                and contract.get("matrix_sha256") == PUBLIC_PROFILE_MATRIX,
                "preserve the exact frozen 416-case public profiler " + name)
    prior = json_object(payloads["previous_public_v2_receipt"], "prior public receipt")
    require(prior.get("status") == "PASS", "authenticate the prior public profile")
    return {"original_case_denominator": 31237,
            "original_mismatch_count": 1352,
            "original_failing_suites": failing,
            "public_correctness_case_count": PUBLIC_CORRECTNESS_CASES,
            "public_profile_case_count": PUBLIC_PROFILE_CASES,
            "public_profile_paired_row_count": PUBLIC_PAIRED_ROWS}


def validate_architecture(payloads: dict[str, bytes], version: str) -> dict:
    require(version in ("v26", "v27"), "reject an unknown native architecture")
    publication = json_object(payloads[version + "_publication"], version + " publication")
    root = json_object(payloads[version + "_root"], version + " root provenance")
    source = next(row for row in OWNERS if row[0] == version + "_source")
    protocol = next(row for row in OWNERS if row[0] == version + "_protocol")
    contract = next(row for row in OWNERS if row[0] == version + "_contract")
    schema_part = "anchor" if version == "v26" else "compiler-fastpath"
    require(publication.get("schema")
            == "rebar-phase2-owned-rust-" + schema_part + "-source-build-"
            + version + "-durable-publication-receipt"
            and publication.get("status") == "PASS"
            and publication.get("build_status") == "PASS"
            and root.get("schema")
            == "rebar-phase2-owned-rust-" + schema_part + "-source-build-"
            + version + "-durable-root-provenance-receipt"
            and root.get("status") == "PASS",
            "require a complete successful independently built native architecture")
    for record in (publication, root):
        require(record.get("source_sha256") == source[2]
                and record.get("protocol_sha256") == protocol[2]
                and record.get("contract_sha256") == contract[2]
                and record.get("corrected_public_adapter_sha256") == ADAPTER_SHA256
                and record.get("runtime_non_delegation") == "NOT ESTABLISHED"
                and record.get("candidate_qualified") is False
                and record.get("holdout") == "NOT OPENED",
                "preserve exact source-build provenance and its qualification limits")
    tree = root.get("root")
    expected_root = ("/tmp/rebar-phase2-native-build-v9-rust-b3xca14k", 11676933)
    if version == "v27":
        expected_root = ("/tmp/rebar-phase2-native-build-v9-rust-uxfnwja4", 11676854)
    require(type(tree) is dict and tree.get("path") == expected_root[0]
            and tree.get("device") == PRIVATE_DEVICE
            and tree.get("inode") == expected_root[1]
            and tree.get("mode") == "0700"
            and tree.get("phase_count") == 2
            and tree.get("directory_scanned") is False
            and type(tree.get("phases")) is list and len(tree["phases"]) == 2,
            "reject substituted independent private native build roots")
    engine_sha = V26_ENGINE_SHA256 if version == "v26" else V27_ENGINE_SHA256
    expected_size = 672664 if version == "v26" else 658120
    for index, phase in enumerate(tree["phases"]):
        name = ("reference-a", "reference-b")[index]
        require(type(phase) is dict and phase.get("name") == name
                and phase.get("absolute_path") == tree["path"] + "/" + name
                and phase.get("device") == PRIVATE_DEVICE
                and phase.get("mode") == "0700"
                and type(phase.get("native_outputs")) is list
                and len(phase["native_outputs"]) == 2,
                "reject an incomplete independently reproduced native phase")
        for output in phase["native_outputs"]:
            require(type(output) is dict and output.get("role") in ("engine", "bridge")
                    and output.get("device") == PRIVATE_DEVICE
                    and output.get("nlink") == 1
                    and output.get("absolute_path") == phase["absolute_path"]
                    + "/native/" + output.get("file_name", ""),
                    "reject a substituted root-authenticated native output")
            if output["role"] == "engine":
                require(output.get("file_name") == "_rust_engine.so"
                        and output.get("sha256") == engine_sha
                        and output.get("bytes") == expected_size
                        and output.get("mode") == "0600",
                        "reject a substituted first-party native Rust engine")
            else:
                require(output.get("file_name")
                        == "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
                        and output.get("sha256") == BRIDGE_SHA256
                        and output.get("bytes") == BRIDGE_BYTES
                        and output.get("mode") == "0700",
                        "reject a substituted first-party CPython native bridge")
        require({row["role"] for row in phase["native_outputs"]}
                == {"engine", "bridge"},
                "require both independently reproduced native artifacts")
    return {"version": version, "publication_sha256": digest(payloads[version + "_publication"]),
            "root_receipt_sha256": digest(payloads[version + "_root"]),
            "source_sha256": source[2], "protocol_sha256": protocol[2],
            "contract_sha256": contract[2], "root": tree,
            "engine_sha256": engine_sha, "engine_bytes": expected_size,
            "bridge_sha256": BRIDGE_SHA256, "adapter_sha256": ADAPTER_SHA256}


def validate_combined_architecture(payloads: dict[str, bytes]) -> dict:
    version = "v28"
    source = next(row for row in OWNERS if row[0] == version + "_source")
    protocol = next(row for row in OWNERS if row[0] == version + "_protocol")
    contract = next(row for row in OWNERS if row[0] == version + "_contract")
    publication = json_object(payloads[version + "_publication"], "V28 build publication")
    receipt = json_object(payloads[version + "_root"], "V28 actual root provenance")
    for name, value in (("publication", publication), ("root", receipt)):
        expected_schema = "rebar-phase2-owned-rust-combined-source-build-v28-durable-"
        expected_schema += "publication-receipt" if name == "publication" \
            else "root-provenance-receipt"
        require(value.get("schema") == expected_schema
                and value.get("status") == "PASS"
                and value.get("version") == 28
                and value.get("source_sha256") == source[2]
                and value.get("protocol_sha256") == protocol[2]
                and value.get("contract_sha256") == contract[2]
                and value.get("corrected_public_adapter_sha256") == ADAPTER_SHA256
                and value.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
                and value.get("combined_engine_source_sha256")
                == "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
                and value.get("combined_engine_source_bytes") == 189423
                and value.get("combined_search_source_sha256")
                == "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
                and value.get("combined_search_source_bytes") == 24305
                and value.get("safe_no_external_introspection_bridge_sha256")
                == "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7"
                and value.get("safe_no_external_introspection_bridge_bytes") == 177146
                and value.get("runtime_non_delegation") == "NOT ESTABLISHED"
                and value.get("strict_audit_finding_count") == 1
                and value.get("candidate_qualified") is False
                and value.get("winner_selected") is False
                and value.get("holdout") == "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
                and value.get("hidden_cases_generated") == 0,
                "reject substituted independently built clean-bridge V28 " + name)
    require(publication.get("build_status") == "PASS"
            and publication.get("actual_completed_phase_count") == 2
            and publication.get("actual_compiler_process_count") == 28
            and receipt.get("actual_source_phase_count") == 2
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("cross_phase_complete_bridge_elf_byte_identical") is True
            and receipt.get("cross_phase_complete_engine_elf_byte_identical") is True,
            "require both exact independently reproduced clean-bridge native builds")
    root = receipt.get("root")
    require(type(root) is dict
            and root.get("path") == "/tmp/rebar-phase2-native-build-v9-rust-3pcdkco3"
            and root.get("device") == PRIVATE_DEVICE
            and root.get("inode") == 11677015 and root.get("mode") == "0700"
            and root.get("phase_count") == 2 and root.get("uid") == os.geteuid(),
            "reject the exact authenticated V28 independent private build root")
    outputs = receipt.get("actual_reproduced_native_outputs")
    require(type(outputs) is dict and set(outputs) == {"bridge", "engine"},
            "require exact complete independently reproduced V28 binaries")
    expected = {"engine": ("_rust_engine.so", V28_ENGINE_SHA256, V28_ENGINE_BYTES),
                "bridge": ("_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                           V28_BRIDGE_SHA256, V28_BRIDGE_BYTES)}
    for role, (file_name, sha256, count) in expected.items():
        output = outputs.get(role)
        require(type(output) is dict and output.get("file_name") == file_name
                and output.get("sha256") == sha256
                and output.get("size_bytes") == count
                and output.get("fresh_independent_inode_count") == 2
                and output.get("reproduced_in_two_fresh_directories") is True,
                "reject an unproven independently reproduced V28 " + role)
        audit = output.get("audit")
        require(type(audit) is dict and audit.get("role") == role
                and audit.get("external_regex_dependency_count") == 0
                and audit.get("cross_family_dependency_count") == 0,
                "reject a V28 external regex engine or cross-candidate dependency")
        if role == "bridge":
            require(audit.get("runpath") == ["$ORIGIN"]
                    and "_rust_engine.so" in audit.get("needed", ())
                    and V28_BRIDGE_SHA256 != BRIDGE_SHA256,
                    "require the genuinely new clean first-party bridge binary")
    phases = []
    for name in ("reference-a", "reference-b"):
        phase_path = root["path"] + "/" + name
        native_outputs = []
        for role, (file_name, sha256, count) in expected.items():
            native_outputs.append({"absolute_path": phase_path + "/native/" + file_name,
                                   "bytes": count, "device": PRIVATE_DEVICE,
                                   "file_name": file_name,
                                   "inode": None,
                                   "inode_provenance": "VERIFY LIVE EXACT DESCRIPTOR; NOT PRESENT IN ROOT RECEIPT",
                                   "mode": "0600" if role == "engine" else "0700",
                                   "nlink": 1, "role": role, "sha256": sha256})
        phases.append({"absolute_path": phase_path, "device": PRIVATE_DEVICE,
                       "inode": None, "mode": "0700", "name": name,
                       "native_outputs": native_outputs})
    tree = dict(root)
    tree["phases"] = phases
    private = receipt.get("actual_private_source_owners")
    require(type(private) is list and len(private) == 2,
            "require both real V28 independently corrected private adapter phases")
    adapter = None
    for index, phase in enumerate(private):
        name = ("reference-a", "reference-b")[index]
        row = phase.get("owners", {}).get("candidates/rust_candidate.py")
        require(phase.get("phase") == name and type(row) is dict
                and row.get("path") == "<FRESH_PRIVATE_TMP>/" + name
                + "/source/candidates/rust_candidate.py"
                and row.get("sha256") == ADAPTER_SHA256
                and row.get("bytes") == ADAPTER_BYTES
                and row.get("device") == PRIVATE_DEVICE
                and row.get("exclusive_creation") is True
                and row.get("same_inode_readback_verified") is True
                and type(row.get("source_overlay")) is dict
                and row["source_overlay"].get("canonical_candidate_modified") is False
                and row["source_overlay"].get("candidate_original_modified") is False
                and row["source_overlay"].get("derived_source_sha256") == ADAPTER_SHA256,
                "reject the exact clean-bridge V28 independent corrected adapter")
        if index == 0:
            adapter = {"path": root["path"] + "/" + name
                       + "/source/candidates/rust_candidate.py",
                       "sha256": ADAPTER_SHA256, "bytes": ADAPTER_BYTES,
                       "device": PRIVATE_DEVICE, "inode": row["inode"],
                       "mode": "0600", "nlink": 1,
                       "source_root_receipt_sha256": digest(payloads[version + "_root"])}
    assert isinstance(adapter, dict)
    return {"version": version, "publication_sha256": digest(payloads[version + "_publication"]),
            "root_receipt_sha256": digest(payloads[version + "_root"]),
            "source_sha256": source[2], "protocol_sha256": protocol[2],
            "contract_sha256": contract[2], "root": tree,
            "engine_sha256": V28_ENGINE_SHA256, "engine_bytes": V28_ENGINE_BYTES,
            "bridge_sha256": V28_BRIDGE_SHA256, "bridge_bytes": V28_BRIDGE_BYTES,
            "adapter_sha256": ADAPTER_SHA256,
            "private_corrected_adapter": adapter,
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0,
            "clean_bridge_distinct_from_previous_bridge": True}


def validate_adapter_provenance(payloads: dict[str, bytes], v26: dict) -> dict:
    receipt = json_object(payloads["v26_root"], "independent V26 adapter provenance")
    private = receipt.get("actual_private_source_owners")
    require(type(private) is list and len(private) == 2,
            "require actual corrected first-party adapter phase provenance")
    actual = None
    for index, phase in enumerate(private):
        name = ("reference-a", "reference-b")[index]
        require(type(phase) is dict and phase.get("phase") == name
                and type(phase.get("owners")) is dict,
                "reject incomplete corrected private adapter provenance")
        row = phase["owners"].get("candidates/rust_candidate.py")
        require(type(row) is dict and type(row.get("path")) is str,
                "require exactly one corrected phase adapter")
        overlay = row.get("source_overlay")
        require(row.get("path") == "<FRESH_PRIVATE_TMP>/" + name
                + "/source/candidates/rust_candidate.py"
                and row.get("sha256") == ADAPTER_SHA256
                and row.get("bytes") == ADAPTER_BYTES
                and row.get("device") == PRIVATE_DEVICE
                and row.get("exclusive_creation") is True
                and row.get("same_inode_readback_verified") is True
                and type(overlay) is dict
                and overlay.get("status") == "PASS"
                and overlay.get("canonical_candidate_modified") is False
                and overlay.get("candidate_original_modified") is False
                and overlay.get("derived_source_sha256") == ADAPTER_SHA256
                and overlay.get("source_apply_count") == 1,
                "reject a substituted corrected independent adapter owner")
        if index == 0:
            actual = {"path": v26["root"]["path"] + "/" + name
                      + "/source/candidates/rust_candidate.py",
                      "sha256": ADAPTER_SHA256, "bytes": ADAPTER_BYTES,
                      "device": PRIVATE_DEVICE, "inode": row["inode"],
                      "mode": "0600", "nlink": 1,
                      "source_root_receipt_sha256": digest(payloads["v26_root"])}
    assert isinstance(actual, dict)
    return actual


def validate_historical_performance(payloads: dict[str, bytes]) -> dict:
    expected = {"v26": (247, 11), "v27": (138, 143), "v28": (208, 8)}
    preserved = {}
    for version, (faster, regressions) in expected.items():
        summary = json_object(payloads[version + "_public_summary"],
                              version + " complete immutable public performance")
        confidence = summary.get("confidence_interval_95")
        require(summary.get("case_count") == PUBLIC_PROFILE_CASES
                and summary.get("paired_row_count") == PUBLIC_PAIRED_ROWS
                and summary.get("faster_case_count") == faster
                and summary.get("regression_over_20_percent_count") == regressions
                and type(summary.get("geomean_speedup_vs_stdlib")) is float
                and summary["geomean_speedup_vs_stdlib"] > 0
                and type(confidence) is dict and confidence.get("resamples") == 400
                and type(confidence.get("lower")) is float
                and type(confidence.get("upper")) is float
                and 0 < confidence["lower"] <= confidence["upper"],
                "preserve every complete measured 416-case historical timing summary")
        preserved[version] = {
            "summary_sha256": digest(payloads[version + "_public_summary"]),
            "case_count": PUBLIC_PROFILE_CASES,
            "paired_row_count": PUBLIC_PAIRED_ROWS,
            "faster_case_count": faster,
            "regression_over_20_percent_count": regressions,
            "geomean_speedup_vs_stdlib_display":
                format(summary["geomean_speedup_vs_stdlib"], ".17g"),
            "confidence_interval_95_lower_display":
                format(confidence["lower"], ".17g"),
            "confidence_interval_95_upper_display":
                format(confidence["upper"], ".17g"),
        }
    # The fully authenticated receipt contains tiny measured floats written in
    # scientific notation; never weaken the intentionally bounded source parser.
    v28 = payloads["v28_public_gate"]
    markers = (
        b'"schema":"rebar-owned-rust-native-architecture-public-gate-v3-'
        b'durable-publication-receipt"',
        b'"architecture":"v28"',
        b'"public_10434_correctness_status":"FAIL"',
        b'"public_10434_mismatch_count":1145',
        b'"public_416_correctness_gate":{"all_mismatches":[],"baseline_pid":83,'
        b'"case_count":416,"mismatch_count":0,"rust_pid":84,"status":"PASS"}',
        b'"paired_row_count":1664',
        b'"faster_case_count":208',
        b'"regression_over_20_percent_count":8',
        b'"candidate_qualified":false',
    )
    require(all(marker in v28 for marker in markers),
            "preserve actual V28 full-public FAIL and complete 416-case timing evidence")
    preserved["v28"]["publication_receipt_sha256"] = digest(payloads["v28_public_gate"])
    return preserved


def validate_corrected_v33(payloads: dict[str, bytes]) -> dict:
    publication = json_object(payloads["v33_publication"], "actual V33 native publication")
    receipt = json_object(payloads["v33_root"], "actual V33 live root provenance")
    public = json_object(payloads["v33_public_pass"], "actual V33 full public PASS")
    original = json_object(payloads["v26_original_pass"],
                           "historical V30 native-build 31237-case original PASS")
    exact_original = json_object(payloads["v33_exact_original_pass"],
                                 "exact same V33 native-build 31237-case original PASS")
    entry_failure = json_object(payloads["v28_exact_original_entry_failure"],
                                "immutable original V28 preworker entry failure")
    worker_failure = json_object(payloads["v28_exact_original_worker_failure"],
                                 "immutable original V28 unrecorded-worker failure")
    static = json_object(payloads["static_audit_pass"], "actual zero-finding static audit")
    source = next(row for row in OWNERS if row[0] == "v33_source")
    protocol = next(row for row in OWNERS if row[0] == "v33_protocol")
    contract = next(row for row in OWNERS if row[0] == "v33_contract")
    for name, item in (("publication", publication), ("root", receipt)):
        require(item.get("schema")
                == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-"
                + ("publication-receipt" if name == "publication"
                   else "root-provenance-receipt")
                and item.get("status") == "PASS"
                and item.get("source_sha256") == source[2]
                and item.get("protocol_sha256") == protocol[2]
                and item.get("contract_sha256") == contract[2]
                and item.get("corrected_public_adapter_sha256") == V33_ADAPTER_SHA256
                and item.get("corrected_public_adapter_bytes") == V33_ADAPTER_BYTES
                and item.get("actual_compiler_process_count") == 28,
                "authenticate both actual immutable corrected V33 native receipts")
    require(publication.get("build_status") == "PASS"
            and publication.get("actual_completed_phase_count") == 2
            and receipt.get("canonical_build_status") == "PASS"
            and receipt.get("actual_source_phase_count") == 2
            and receipt.get("canonical_build_receipt_sha256")
            == digest(payloads["v33_publication"]),
            "require an actually successful independent 28-process V33 native build")
    tree = receipt.get("root")
    require(type(tree) is dict and tree.get("path") == V33_ROOT_PATH
            and tree.get("device") == PRIVATE_DEVICE
            and tree.get("inode") == V33_ROOT_INODE and tree.get("mode") == "0700"
            and tree.get("phase_count") == 2
            and tree.get("directory_scanned") is False
            and type(tree.get("phases")) is list and len(tree["phases"]) == 2,
            "require the exact live actual corrected V33 private native root")
    for index, phase in enumerate(tree["phases"]):
        name = ("reference-a", "reference-b")[index]
        require(type(phase) is dict and phase.get("name") == name
                and phase.get("absolute_path") == V33_ROOT_PATH + "/" + name
                and phase.get("device") == PRIVATE_DEVICE
                and phase.get("mode") == "0700"
                and type(phase.get("native_outputs")) is list
                and len(phase["native_outputs"]) == 2,
                "authenticate both exact corrected independently reproduced phases")
        for artifact in phase["native_outputs"]:
            role = artifact.get("role")
            values = ((V33_ENGINE_SHA256, V33_ENGINE_BYTES, "0600")
                      if role == "engine" else
                      (V33_BRIDGE_SHA256, V33_BRIDGE_BYTES, "0700"))
            require(role in ("engine", "bridge")
                    and artifact.get("sha256") == values[0]
                    and artifact.get("bytes") == values[1]
                    and artifact.get("mode") == values[2]
                    and artifact.get("device") == PRIVATE_DEVICE
                    and type(artifact.get("inode")) is int and artifact["inode"] > 0
                    and artifact.get("nlink") == 1,
                    "reject substituted corrected V33 first-party native ELF identity")
    private = receipt.get("actual_private_source_owners")
    require(type(private) is list and len(private) == 2,
            "require both actual privately corrected V33 source-owner phases")
    private_adapter = None
    for index, phase in enumerate(private):
        name = ("reference-a", "reference-b")[index]
        owner = phase.get("owners", {}).get("candidates/rust_candidate.py")
        require(phase.get("phase") == name and type(owner) is dict
                and owner.get("path") == "<FRESH_PRIVATE_TMP>/" + name
                + "/source/candidates/rust_candidate.py"
                and owner.get("sha256") == V33_ADAPTER_SHA256
                and owner.get("bytes") == V33_ADAPTER_BYTES
                and owner.get("device") == PRIVATE_DEVICE
                and type(owner.get("inode")) is int
                and owner.get("exclusive_creation") is True
                and owner.get("same_inode_readback_verified") is True
                and owner.get("source_overlay", {}).get("derived_source_sha256")
                == V33_ADAPTER_SHA256,
                "authenticate both seven-repair corrected private V33 adapters")
        if index == 0:
            private_adapter = {
                "path": V33_ROOT_PATH + "/" + name
                        + "/source/candidates/rust_candidate.py",
                "sha256": V33_ADAPTER_SHA256, "bytes": V33_ADAPTER_BYTES,
                "device": PRIVATE_DEVICE, "inode": owner["inode"],
                "mode": "0600", "nlink": 1,
                "source_root_receipt_sha256": digest(payloads["v33_root"]),
            }
    require(public.get("schema")
            == "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt"
            and public.get("status") == "PASS"
            and public.get("candidate_status") == "PASS"
            and public.get("public_10434_correctness_status") == "PASS"
            and public.get("public_10434_case_count") == PUBLIC_CORRECTNESS_CASES
            and public.get("public_10434_mismatch_count") == 0
            and public.get("v33_native_engine_sha256") == V33_ENGINE_SHA256
            and public.get("v33_native_bridge_sha256") == V33_BRIDGE_SHA256
            and public.get("v33_adapter_sha256") == V33_ADAPTER_SHA256
            and public.get("v33_publication_sha256") == digest(payloads["v33_publication"])
            and public.get("v33_root_sha256") == digest(payloads["v33_root"])
            and public.get("v5_static_pass_sha256") == V33_STATIC_PASS_SHA256
            and public.get("candidate_qualified") is False,
            "require the actual full 10434-case corrected V33 zero-mismatch PASS")
    require(original.get("candidate_status") == "PASS"
            and original.get("candidate_original_oracle_pass") is True
            and original.get("case_execution_denominator") == 31237
            and original.get("verified_passing_case_count") == 31237
            and original.get("semantic_mismatch_count") == 0
            and original.get("completed_suite_count") == 13
            and original.get("actual_v26_build_source_sha256")
            == "dd0ed268775537b985a060e5f608c6bc2730f86922ad20ee78cff19e4c387a1d"
            and original.get("actual_v26_build_contract_sha256")
            == "38e0a8f44cf1e3f68abb643b004f7f47350e743f5c3f1994d101b02e5ebc1956"
            and original.get("combined_bridge_source_sha256")
            == "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
            and original.get("corrected_public_adapter_sha256") == ADAPTER_SHA256
            and original.get("corrected_public_adapter_bytes") == ADAPTER_BYTES,
            "preserve the actual 31237/31237 PASS of V30, not the later V33 binary")
    suites = exact_original.get("suite_integrity")
    require(exact_original.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v28-durable-publication-receipt"
            and exact_original.get("status") == "PASS"
            and exact_original.get("publication_status") == "PASS"
            and exact_original.get("candidate_status") == "PASS"
            and exact_original.get("candidate_original_oracle_pass") is True
            and exact_original.get("case_execution_denominator") == 31237
            and exact_original.get("verified_passing_case_count") == 31237
            and exact_original.get("semantic_mismatch_count") == 0
            and exact_original.get("completed_suite_count") == 13
            and exact_original.get("actual_candidate_workers") == 13
            and exact_original.get("distinct_worker_process_id_count") == 13
            and exact_original.get("infrastructure_failure_count") == 0
            and exact_original.get("actual_v28_build_source_sha256") == source[2]
            and exact_original.get("actual_v28_build_protocol_sha256") == protocol[2]
            and exact_original.get("actual_v28_build_contract_sha256") == contract[2]
            and exact_original.get("actual_v28_build_receipt_sha256")
            == digest(payloads["v33_publication"])
            and exact_original.get("actual_v28_build_private_root") == V33_ROOT_PATH
            and exact_original.get("actual_v28_build_private_root_inode") == V33_ROOT_INODE
            and exact_original.get("actual_v28_compiler_process_count") == 28
            and exact_original.get("combined_bridge_source_sha256")
            == "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
            and exact_original.get("combined_bridge_source_bytes") == 178472
            and exact_original.get("corrected_public_adapter_sha256") == V33_ADAPTER_SHA256
            and exact_original.get("corrected_public_adapter_bytes") == V33_ADAPTER_BYTES
            and exact_original.get("native_engine_sha256") == V33_ENGINE_SHA256
            and exact_original.get("native_bridge_sha256") == V33_BRIDGE_SHA256
            and exact_original.get("campaign_source_sha256")
            == next(row[2] for row in OWNERS if row[0] == "v28_exact_original_source")
            and exact_original.get("campaign_protocol_sha256")
            == next(row[2] for row in OWNERS if row[0] == "v28_exact_original_protocol")
            and exact_original.get("campaign_contract_sha256")
            == next(row[2] for row in OWNERS if row[0] == "v28_exact_original_contract")
            and exact_original.get("all_original_suite_rows_validated_before_publication")
            is True
            and exact_original.get("all_original_observation_vectors_complete") is True
            and type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_denominator", 0)
                    for item in suites if type(item) is dict) == 31237
            and all(type(item) is dict and item.get("mismatch_count") == 0
                    and item.get("fully_observed") is True for item in suites),
            "require actual exact same V33 engine, bridge, adapter and 31237-case PASS")
    require(entry_failure.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v28-entry-failure"
            and entry_failure.get("status") == "FAIL"
            and entry_failure.get("actual_candidate_workers_started") == 0
            and entry_failure.get("actual_clock_samples") == 0
            and worker_failure.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v28-unrecorded-worker-failure"
            and worker_failure.get("status") == "FAIL"
            and worker_failure.get("exit_code") == 2
            and worker_failure.get("candidate_qualified") is False,
            "preserve both immutable failed V28 original attempts before genuine success")
    require(static.get("schema")
            == "rebar-phase2-clean-first-party-rust-non-delegation-v5-root-static-audit"
            and static.get("status") == "PASS" and static.get("finding_count") == 0
            and static.get("external_regex_packages") == 0
            and static.get("external_regex_libraries") == 0
            and static.get("external_regex_symbols") == 0
            and static.get("cross_family_dependencies") == 0
            and static.get("candidate_qualified") is False,
            "preserve the exact immutable first-party zero-external-dependency static PASS")
    assert isinstance(private_adapter, dict)
    return {"version": "v33", "publication_sha256": digest(payloads["v33_publication"]),
            "root_receipt_sha256": digest(payloads["v33_root"]),
            "source_sha256": source[2], "protocol_sha256": protocol[2],
            "contract_sha256": contract[2], "root": tree,
            "engine_sha256": V33_ENGINE_SHA256, "engine_bytes": V33_ENGINE_BYTES,
            "bridge_sha256": V33_BRIDGE_SHA256, "bridge_bytes": V33_BRIDGE_BYTES,
            "adapter_sha256": V33_ADAPTER_SHA256,
            "private_corrected_adapter": private_adapter,
            "public_pass_receipt_sha256": digest(payloads["v33_public_pass"]),
            "public_case_count": PUBLIC_CORRECTNESS_CASES,
            "public_mismatch_count": 0,
            "historical_v30_original_pass_receipt_sha256":
                digest(payloads["v26_original_pass"]),
            "historical_v30_original_case_count": 31237,
            "historical_v30_original_mismatch_count": 0,
            "historical_v30_original_adapter_sha256": ADAPTER_SHA256,
            "historical_v30_original_bridge_source_sha256":
                "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55",
            "exact_v33_original_pass_receipt_sha256":
                digest(payloads["v33_exact_original_pass"]),
            "exact_v33_original_correctness": "PASS",
            "exact_v33_original_case_count": 31237,
            "exact_v33_original_mismatch_count": 0,
            "exact_v33_original_completed_suite_count": 13,
            "preserved_original_entry_failure_sha256":
                digest(payloads["v28_exact_original_entry_failure"]),
            "preserved_original_worker_failure_sha256":
                digest(payloads["v28_exact_original_worker_failure"]),
            "static_pass_receipt_sha256": digest(payloads["static_audit_pass"]),
            "external_regex_dependency_count": 0,
            "cross_family_dependency_count": 0}


def architecture_freeze(payloads: dict[str, bytes], source_pin: str,
                        protocol_pin: str) -> dict:
    actual_previous = validate_previous_public_gate(payloads)
    predecessor = validate_previous_gate(payloads)
    search_provenance = validate_canonical_search_provenance(payloads)
    public = validate_public_context(payloads)
    v26 = validate_architecture(payloads, "v26")
    v27 = validate_architecture(payloads, "v27")
    v28 = validate_combined_architecture(payloads)
    v33 = validate_corrected_v33(payloads)
    historical = validate_historical_performance(payloads)
    adapter = validate_adapter_provenance(payloads, v26)
    return {"schema": SCHEMA + "-source-freeze", "python": "3.14.6",
            "python_executable": PYTHON, "python_sha256": PYTHON_SHA256,
            "source_sha256": source_pin, "protocol_sha256": protocol_pin,
            "published_owners": [owner_pin(row) for row in OWNERS],
            "immutable_v2_actual_public_comparisons": actual_previous,
            "immutable_failed_v1_predecessor": predecessor,
            "receipt_authenticated_canonical_search": search_provenance,
            "public_context": public,
            "architectures": {"v26": v26, "v27": v27, "v28": v28, "v33": v33},
            "private_corrected_adapter": adapter,
            "v33_private_corrected_adapter": v33["private_corrected_adapter"],
            "v33_full_public_correctness": {
                "status": "PASS", "case_count": 10434, "mismatch_count": 0,
                "receipt_sha256": v33["public_pass_receipt_sha256"],
            },
            "historical_v30_original_correctness": {
                "status": "PASS", "native_build_version": 30,
                "case_count": 31237, "mismatch_count": 0,
                "adapter_sha256": ADAPTER_SHA256,
                "receipt_sha256": v33["historical_v30_original_pass_receipt_sha256"],
            },
            "exact_v33_original_correctness": {
                "status": "PASS", "native_build_version": 33,
                "campaign_version": 28, "case_count": 31237,
                "mismatch_count": 0, "completed_suite_count": 13,
                "actual_candidate_workers": 13,
                "engine_sha256": V33_ENGINE_SHA256,
                "bridge_sha256": V33_BRIDGE_SHA256,
                "adapter_sha256": V33_ADAPTER_SHA256,
                "receipt_sha256": v33["exact_v33_original_pass_receipt_sha256"],
                "preserved_entry_failure_sha256":
                    v33["preserved_original_entry_failure_sha256"],
                "preserved_worker_failure_sha256":
                    v33["preserved_original_worker_failure_sha256"],
            },
            "zero_finding_static_source_elf_audit": {
                "status": "PASS", "finding_count": 0,
                "external_regex_packages": 0,
                "external_regex_libraries": 0,
                "external_regex_symbols": 0,
                "receipt_sha256": v33["static_pass_receipt_sha256"],
            },
            "preserved_v26_v27_v28_actual_public_performance": historical,
            "canonical_candidates": [
                {"role": role, "path": path, "sha256": sha, "bytes": size,
                 "device": DEVICE, "inode": inode, "mode": format(mode, "04o")}
                for role, path, sha, size, inode, mode in CANONICAL_ORIGINALS
            ],
            "worker_bootstrap_sha256": digest(WORKER_BOOTSTRAP.encode("utf-8")),
            "public_correctness": {"case_count": PUBLIC_CORRECTNESS_CASES,
                                    "published_seed": PUBLIC_CORRECTNESS_SEED,
                                    "matrix_sha256": PUBLIC_CORRECTNESS_MATRIX,
                                    "preserve_all_mismatches": True},
            "public_profile": {"case_count": PUBLIC_PROFILE_CASES,
                               "published_seed": PUBLIC_PROFILE_SEED,
                               "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                               "paired_rounds": PUBLIC_PAIRED_ROUNDS,
                               "paired_row_count": PUBLIC_PAIRED_ROWS,
                               "iterations": PUBLIC_ITERATIONS,
                               "warmups": PUBLIC_WARMUPS,
                               "profile_passes": PUBLIC_PROFILE_PASSES,
                               "timing_requires_complete_416_case_parity": True,
                               "timing_after_10434_failure": "FORBIDDEN",
                               "all_10434_public_cases_previously_passed": True,
                               "historical_v30_31237_original_cases_passed": True,
                               "exact_v33_original_case_execution_status": "PASS",
                               "exact_v33_original_case_count": 31237,
                               "exact_v33_original_mismatch_count": 0,
                               "same_worker_environment_for_both_engines": True,
                               "counterbalanced_process_order": True,
                               "equal_case_weight": True,
                               "bootstrap_resamples": 400,
                               "bootstrap_confidence_percent": 95,
                               "benchmark_detection_forbidden": True},
            "runtime_non_delegation": "STATIC PASS; RUNTIME NOT ESTABLISHED",
            "candidate_qualified": False,
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "winner_selected": False,
            "holdout_scope": "ONLY THIS FROZEN CONTROLLER AND ITS AUTHORIZED WORKERS",
            "other_agent_historical_holdout_access": "NOT ATTESTED",
            "controller_final_holdout_content_open_count": 0,
            "proposal_content_open_count": 0,
            "proposal_metadata_probe_count": 0,
            "hidden_case_files_generated": 0,
            "hidden_cases_read": 0,
            "current_final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "retired_v2_proposal_status": "COMPROMISED; RETIRED; NOT ACCESSED BY THIS CONTROLLER",
            "final_holdout_case_status": "NOT GENERATED; INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "sealed_final_protocol_status": "NOT FROZEN",
            "performance": NOT_MEASURED,
            "native_cpu_samples": NOT_MEASURED,
            "memory": NOT_MEASURED}


def load_context(wall: SourceWall | None, source_pin: str, protocol_pin: str,
                 contract_pin: str | None) -> tuple[dict[str, bytes], dict]:
    rows = dict((row[0], row) for row in OWNERS)
    require(len(rows) == len(OWNERS), "reject duplicated frozen public owner roles")
    payloads = {role: read_owner(wall, row) for role, row in rows.items()}
    source_row = dynamic_owner(wall, "gate_source", SOURCE, source_pin)
    protocol_row = dynamic_owner(wall, "gate_protocol", PROTOCOL, protocol_pin)
    payloads["gate_source"] = read_owner(wall, source_row)
    payloads["gate_protocol"] = read_owner(wall, protocol_row)
    freeze = architecture_freeze(payloads, source_pin, protocol_pin)
    if contract_pin is not None:
        contract_row = dynamic_owner(wall, "gate_contract", CONTRACT, contract_pin)
        contract_raw = read_owner(wall, contract_row)
        require(contract_raw == document(freeze),
                "reject a noncanonical or substituted public architecture contract")
        payloads["gate_contract"] = contract_raw
    return payloads, freeze


def wall_summary(wall: SourceWall) -> dict:
    require(wall.installed and not wall.live,
            "source-only public gate leaked an owned descriptor")
    no_matching_imports()
    require(wall.holdout_content_open_count == 0
            and wall.native_content_open_count == 0
            and wall.candidate_content_open_count == 0
            and wall.write_count == 0 and wall.process_count == 0
            and wall.clock_samples == 0,
            "source-only public gate crossed a physical isolation boundary")
    return {"physical_source_wall": "PASS", "candidate_content_open_count": 0,
            "native_content_open_count": 0, "process_count": 0,
            "clock_samples": 0, "write_count": 0,
            "controller_final_holdout_content_open_count": 0,
            "proposal_content_open_count": 0,
            "proposal_metadata_probe_count": 0,
            "hidden_case_files_generated": 0, "hidden_cases_read": 0,
            "current_final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "holdout_scope": "ONLY THIS FROZEN CONTROLLER AND ITS AUTHORIZED WORKERS",
            "other_agent_historical_holdout_access": "NOT ATTESTED"}


def test_rejection(wall: SourceWall, name: str, callback) -> None:
    try:
        callback()
    except (GateError, OSError, ValueError, TypeError, ImportError):
        return
    raise GateError("source wall accepted forbidden action: " + name)


def source_self_test(wall: SourceWall, freeze: dict) -> dict:
    require(check_commit("a" * 40, "valid Git commit") == "a" * 40,
            "accept a genuine complete 40-character Git commit")
    test_rejection(wall, "64-character Git commit", lambda: check_commit(
        "a" * 64, "invalid Git commit"))
    incorrect = dict(freeze["receipt_authenticated_canonical_search"]
                     ["canonical_search"])
    incorrect["path"] = "candidates/rust/src/search_acceleration.rs"
    test_rejection(wall, "historical nonexistent V1 canonical search", lambda:
                   validate_search_identity(incorrect, "hostile absent-source control"))
    require(validate_search_identity(
        freeze["receipt_authenticated_canonical_search"]["canonical_search"],
        "receipt-authenticated real canonical search")["path"]
        == "candidates/rust/src/search.rs",
        "accept the actual canonical source using only authenticated public receipts")
    test_rejection(wall, "substituted old V26/V27 bridge for clean V28", lambda:
                   require(freeze["architectures"]["v28"]["bridge_sha256"]
                           == BRIDGE_SHA256,
                           "reject the old bridge for the distinct V28 architecture"))
    test_rejection(wall, "canonical candidate open", lambda: os.open(
        ROOT + "/candidates/rust_candidate.py",
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)))
    test_rejection(wall, "native engine open", lambda: os.open(
        ROOT + "/candidates/_rust_engine.so",
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)))
    test_rejection(wall, "private artifact open", lambda: os.open(
        freeze["architectures"]["v27"]["root"]["phases"][0]
        ["native_outputs"][0]["absolute_path"],
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)))
    test_rejection(wall, "sealed content open", lambda: os.open(
        ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json",
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)))
    test_rejection(wall, "proposal metadata probe", lambda: os.stat(
        ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json"))
    test_rejection(wall, "substituted historical adapter for corrected V33", lambda:
                   require(freeze["architectures"]["v33"]["adapter_sha256"]
                           == ADAPTER_SHA256,
                           "reject the four-repair adapter for the seven-repair V33 candidate"))
    test_rejection(wall, "builtins candidate open", lambda: builtins.open(
        ROOT + "/candidates/rust_candidate.py", "rb"))
    test_rejection(wall, "direct io open", lambda: io.open(ROOT + "/GOAL.md", "rb"))
    test_rejection(wall, "candidate import audit", lambda: sys.audit(
        "import", "candidates.rust_candidate", None, None, None, None))
    test_rejection(wall, "worker audit", lambda: sys.audit("subprocess.Popen", []))
    test_rejection(wall, "dynamic compile audit", lambda: sys.audit(
        "compile", b"1", "<forbidden>"))
    test_rejection(wall, "native loader audit", lambda: sys.audit(
        "ctypes.dlopen", "forbidden.so"))
    test_rejection(wall, "timing", lambda: time.perf_counter_ns())
    test_rejection(wall, "filesystem mutation", lambda: os.mkdir(
        ROOT + "/experiments/forbidden-native-public-gate"))
    test_rejection(wall, "duplicate JSON", lambda: json_object(
        b'{"a":1,"a":2}', "duplicate"))
    test_rejection(wall, "nonfinite JSON", lambda: json_object(
        b'{"a":1e999}', "nonfinite"))
    test_rejection(wall, "wrong architecture", lambda: validate_architecture(
        {}, "v29"))
    summary = wall_summary(wall)
    summary.update({"schema": SCHEMA + "-source-self-test", "status": "PASS",
                    "self_test_rejection_count": 20,
                    "public_case_counts": [PUBLIC_CORRECTNESS_CASES,
                                           PUBLIC_PROFILE_CASES],
                    "paired_row_count": PUBLIC_PAIRED_ROWS,
                    "runtime_non_delegation": freeze["runtime_non_delegation"],
                    "candidate_qualified": False,
                    "blocked_categories": dict(sorted(wall.blocked.items()))})
    return summary


def exact_file(path: str, *, expected_sha: str, expected_bytes: int,
               device: int, inode: int | None, mode: int, role: str) -> bytes:
    require(type(path) is str and path.startswith((ROOT + "/", "/tmp/"))
            and "/../" not in path, "reject an unowned actual file path")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == mode
                and before.st_dev == device
                and (inode is None and before.st_ino > 0 or before.st_ino == inode)
                and before.st_size == expected_bytes and before.st_nlink == 1
                and before.st_uid == os.geteuid(),
                "reject a substituted actual artifact: " + role)
        blocks = []
        while True:
            block = os.read(descriptor, 65536)
            if not block:
                break
            blocks.append(block)
        payload = b"".join(blocks)
        after = os.fstat(descriptor)
        require(len(payload) == expected_bytes and digest(payload) == expected_sha
                and all(getattr(before, field) == getattr(after, field)
                        for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                      "st_mtime_ns", "st_ctime_ns")),
                "reject altered or concurrent actual artifact: " + role)
        return payload
    finally:
        os.close(descriptor)


def snapshot_canonical() -> list[dict]:
    result = []
    for role, relative, expected, count, inode, mode in CANONICAL_ORIGINALS:
        exact_file(ROOT + "/" + relative, expected_sha=expected,
                   expected_bytes=count, device=DEVICE, inode=inode,
                   mode=mode, role="canonical " + role)
        result.append({"role": role, "path": relative, "sha256": expected,
                       "bytes": count, "device": DEVICE, "inode": inode,
                       "mode": format(mode, "04o")})
    return result


def exclusive_write(path: str, payload: bytes, mode: int = 0o600) -> dict:
    require(type(path) is str and type(payload) is bytes
            and path.startswith((ROOT + "/experiments/rust_corrected_public_performance_v4/",
                                 ROOT + "/oracle/phase2/evidence/",
                                 "/tmp/rebar-rust-corrected-performance-v4-"))
            and "/../" not in path,
            "reject an unapproved nonexclusive public architecture output")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                         | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0), mode)
    try:
        view = memoryview(payload)
        while view:
            count = os.write(descriptor, view)
            require(type(count) is int and count > 0,
                    "reject an incomplete exclusive public output write")
            view = view[count:]
        os.fsync(descriptor)
        info = os.fstat(descriptor)
        require(stat.S_ISREG(info.st_mode)
                and stat.S_IMODE(info.st_mode) == mode
                and info.st_nlink == 1 and info.st_size == len(payload),
                "reject substituted exclusive public architecture output")
        return {"path": path, "sha256": digest(payload), "bytes": len(payload),
                "device": info.st_dev, "inode": info.st_ino,
                "mode": format(mode, "04o")}
    finally:
        os.close(descriptor)


def load_harness(payload: bytes, overlay: str, basename: str):
    import pathlib
    import types

    path = overlay + "/tools/" + basename
    module = types.ModuleType("_rebar_owned_public_parent_" + basename.replace(".", "_"))
    module.__file__ = path
    module.__package__ = None
    previous = list(sys.path)
    try:
        sys.path[:] = [overlay] + [item for item in previous
                                   if item != ROOT and item != overlay]
        exec(compile(payload, path, "exec"), module.__dict__)
        module.ROOT = pathlib.Path(overlay)
        sys.path[:] = [overlay] + [item for item in sys.path
                                   if item != ROOT and item != overlay]
        module.verify_pinned_runtime()
        return module
    finally:
        # Parent must retain the overlay as entry zero for unchanged harness checks.
        sys.path[:] = [overlay] + [item for item in previous
                                   if item != ROOT and item != overlay]


def run_worker(overlay: str, basename: str, source_sha: str,
               role: str, engine: str, mode: str, request: dict | None = None):
    import json
    import subprocess

    require(engine in ("stdlib", "rust") and mode in ("observe", "timing", "profile")
            and basename in ("rust_public_practice_benchmark_v2.py",
                             "rust_public_profile_v1.py"),
            "reject an unapproved public architecture worker")
    payload = None if request is None else (
        json.dumps(request, ensure_ascii=True, allow_nan=False,
                   sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    require(payload is None or len(payload) <= MAX_PROCESS_BYTES,
            "reject an unbounded public architecture worker request")
    process = subprocess.Popen(
        [PYTHON, "-I", "-B", "-S", "-c", WORKER_BOOTSTRAP, overlay,
         basename, source_sha, role, engine, mode],
        stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=overlay,
        shell=False, close_fds=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1",
             "PYTHONHASHSEED": "0", "PYTHONMALLOC": "malloc"},
    )
    stdout, stderr = process.communicate(input=payload)
    require(process.returncode == 0 and not stderr
            and 0 < len(stdout) <= MAX_PROCESS_BYTES,
            "isolated public worker failed: " + role + "; stderr="
            + stderr[:4000].decode("utf-8", "replace"))
    result = json.loads(stdout.decode("utf-8"))
    require(type(result) is dict and result.get("status") == "PASS"
            and result.get("role") == role and result.get("engine") == engine
            and result.get("python") == "3.14.6"
            and type(result.get("pid")) is int,
            "reject a substituted isolated public architecture worker document")
    return result, stdout


def paired_summary(rows: list[dict]) -> dict:
    import math
    import random

    require(len(rows) == PUBLIC_PAIRED_ROWS,
            "require every correctness-gated public paired timing row")
    case_rows: dict[str, list[dict]] = {}
    for row in rows:
        case_rows.setdefault(row["case"], []).append(row)
    require(len(case_rows) == PUBLIC_PROFILE_CASES
            and all(len(values) == PUBLIC_PAIRED_ROUNDS
                    for values in case_rows.values()),
            "reject a missing or duplicated frozen public profile case")
    case_ratios = {}
    regressions = []
    for case, values in sorted(case_rows.items()):
        baseline = sum(item["baseline_elapsed_ns"] for item in values)
        rust = sum(item["rust_elapsed_ns"] for item in values)
        require(baseline > 0 and rust > 0, "reject a nonpositive paired interval")
        ratio = baseline / rust
        case_ratios[case] = ratio
        if rust > baseline * 1.2:
            regressions.append({"case": case, "cohort": values[0]["cohort"],
                                "operation": values[0]["operation"],
                                "baseline_elapsed_ns": baseline,
                                "rust_elapsed_ns": rust,
                                "slowdown_ratio": rust / baseline})
    values = list(case_ratios.values())
    geomean = math.exp(sum(math.log(value) for value in values) / len(values))
    rng = random.Random(PUBLIC_PROFILE_SEED ^ 0xA263_001)
    samples = []
    for _ in range(400):
        sample = [values[rng.randrange(len(values))] for _ in values]
        samples.append(math.exp(sum(math.log(value) for value in sample)
                                / len(sample)))
    samples.sort()
    by_cohort: dict[str, list[float]] = {}
    by_operation: dict[str, list[float]] = {}
    for case, value in case_ratios.items():
        row = case_rows[case][0]
        by_cohort.setdefault(row["cohort"], []).append(value)
        by_operation.setdefault(row["operation"], []).append(value)
    group = lambda grouped: {key: {"case_count": len(items),
                                  "geomean_speedup": math.exp(sum(map(math.log, items))
                                                                / len(items)),
                                  "faster_case_count": sum(item > 1 for item in items)}
                             for key, items in sorted(grouped.items())}
    cohorts = group(by_cohort)
    operations = group(by_operation)
    cohort_rankings = sorted(
        ({"cohort": name, **values} for name, values in cohorts.items()),
        key=lambda row: (-row["geomean_speedup"], row["cohort"]),
    )
    operation_rankings = sorted(
        ({"operation": name, **values} for name, values in operations.items()),
        key=lambda row: (-row["geomean_speedup"], row["operation"]),
    )
    case_rankings = sorted(
        ({"case": name, "speedup_vs_stdlib": value,
          "cohort": case_rows[name][0]["cohort"],
          "operation": case_rows[name][0]["operation"]}
         for name, value in case_ratios.items()),
        key=lambda row: (-row["speedup_vs_stdlib"], row["case"]),
    )
    return {"case_count": PUBLIC_PROFILE_CASES,
            "paired_row_count": PUBLIC_PAIRED_ROWS,
            "geomean_speedup_vs_stdlib": geomean,
            "confidence_interval_95": {"lower": samples[9],
                                         "upper": samples[389],
                                         "resamples": len(samples),
                                         "seed": PUBLIC_PROFILE_SEED ^ 0xA263_001},
            "faster_case_count": sum(value > 1 for value in values),
            "slower_case_count": sum(value < 1 for value in values),
            "equal_case_count": sum(value == 1 for value in values),
            "case_ratios": case_ratios,
            "all_regressions_over_20_percent": regressions,
            "regression_over_20_percent_count": len(regressions),
            "cohorts": cohorts, "operations": operations,
            "ranked_cohorts_by_geomean_speedup": cohort_rankings,
            "ranked_operations_by_geomean_speedup": operation_rankings,
            "ranked_cases_by_speedup": case_rankings,
            "top_20_faster_cases": case_rankings[:20],
            "bottom_20_slower_cases": list(reversed(case_rankings[-20:]))}


def actual_run(payloads: dict[str, bytes], freeze: dict, args: dict) -> dict:
    import json
    import tempfile

    architecture = args["--architecture"]
    require(architecture in ("v26", "v27", "v28"),
            "choose an exact independently built first-party architecture")
    session = args["--session"]
    require(type(session) is str and 1 <= len(session) <= 80
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in session)
            and session.startswith(architecture + "-")
            and not any(token in session for token in ("holdout", "hidden", "final", "sealed")),
            "require an exclusive architecture-prefixed public session")
    require(args["--root-authorized"] == "YES"
            and check_commit(args["--frozen-commit"], "frozen commit")
            == check_commit(args["--pushed-commit"], "pushed commit"),
            "require root authority and the identical already-pushed frozen commit")
    selected = freeze["architectures"][architecture]
    require(args["--v26-publication-sha256"] == freeze["architectures"]["v26"]["publication_sha256"]
            and args["--v26-root-sha256"] == freeze["architectures"]["v26"]["root_receipt_sha256"]
            and args["--v27-publication-sha256"] == freeze["architectures"]["v27"]["publication_sha256"]
            and args["--v27-root-sha256"] == freeze["architectures"]["v27"]["root_receipt_sha256"]
            and args["--v28-publication-sha256"] == freeze["architectures"]["v28"]["publication_sha256"]
            and args["--v28-root-sha256"] == freeze["architectures"]["v28"]["root_receipt_sha256"],
            "require explicit complete root authentication for all three build receipt pairs")
    canonical_before = snapshot_canonical()
    root = selected["root"]
    phase = root["phases"][0]
    root_info = os.stat(root["path"], follow_symlinks=False)
    require(stat.S_ISDIR(root_info.st_mode)
            and stat.S_IMODE(root_info.st_mode) == 0o700
            and root_info.st_dev == PRIVATE_DEVICE
            and root_info.st_ino == root["inode"]
            and root_info.st_uid == os.geteuid()
            and os.path.realpath(root["path"]) == root["path"],
            "reject a substituted live receipt-authenticated private build root")
    phase_info = os.stat(phase["absolute_path"], follow_symlinks=False)
    require(stat.S_ISDIR(phase_info.st_mode)
            and stat.S_IMODE(phase_info.st_mode) == 0o700
            and phase_info.st_dev == PRIVATE_DEVICE
            and phase_info.st_uid == os.geteuid()
            and (phase["inode"] is None or phase_info.st_ino == phase["inode"])
            and os.path.realpath(phase["absolute_path"]) == phase["absolute_path"],
            "reject a substituted live independently built native source phase")
    adapter_pin = selected.get("private_corrected_adapter",
                               freeze["private_corrected_adapter"])
    adapter = exact_file(adapter_pin["path"], expected_sha=adapter_pin["sha256"],
                         expected_bytes=adapter_pin["bytes"], device=adapter_pin["device"],
                         inode=adapter_pin["inode"], mode=0o600,
                         role="receipt-authenticated independent corrected adapter")
    artifact_payloads = {}
    for artifact in phase["native_outputs"]:
        artifact_payloads[artifact["role"]] = exact_file(
            artifact["absolute_path"], expected_sha=artifact["sha256"],
            expected_bytes=artifact["bytes"], device=artifact["device"],
            inode=artifact["inode"], mode=int(artifact["mode"], 8),
            role=architecture + " independent " + artifact["role"])
    overlay = tempfile.mkdtemp(prefix="rebar-rust-corrected-performance-v4-", dir="/tmp")
    require(os.path.realpath(overlay) == overlay
            and stat.S_IMODE(os.stat(overlay).st_mode) == 0o700,
            "require a genuinely fresh private native architecture overlay")
    os.mkdir(overlay + "/tools", 0o700)
    os.mkdir(overlay + "/candidates", 0o700)
    exclusive_write(overlay + "/candidates/__init__.py", b"", 0o600)
    exclusive_write(overlay + "/candidates/rust_candidate.py", adapter, 0o600)
    exclusive_write(overlay + "/candidates/_rust_engine.so",
                    artifact_payloads["engine"], 0o600)
    exclusive_write(overlay + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                    artifact_payloads["bridge"], 0o700)
    exclusive_write(overlay + "/tools/rust_public_practice_benchmark_v2.py",
                    payloads["public_correctness_source"], 0o600)
    exclusive_write(overlay + "/tools/rust_public_profile_v1.py",
                    payloads["public_profile_v1_source"], 0o600)

    parent = ROOT + "/experiments/rust_corrected_public_performance_v4"
    try:
        os.mkdir(parent, 0o700)
    except FileExistsError:
        info = os.stat(parent, follow_symlinks=False)
        require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "reject a substituted public architecture evidence directory")
    output = parent + "/" + session
    os.mkdir(output, 0o700)
    artifacts = []

    correctness_module = load_harness(payloads["public_correctness_source"], overlay,
                                      "rust_public_practice_benchmark_v2.py")
    originals = {}

    def isolated_correctness(role: str, engine: str, mode: str, **_kwargs):
        result, raw = run_worker(overlay, "rust_public_practice_benchmark_v2.py",
                                 next(row[2] for row in OWNERS
                                      if row[0] == "public_correctness_source"),
                                 architecture + "-" + role, engine, mode)
        originals[engine] = (result, raw)
        return result

    correctness_module.run_isolated_worker = isolated_correctness
    full = correctness_module.run_correctness_only()
    require(full.get("case_denominator") == PUBLIC_CORRECTNESS_CASES
            and full.get("actual_baseline_cases") == PUBLIC_CORRECTNESS_CASES
            and full.get("actual_rust_cases") == PUBLIC_CORRECTNESS_CASES
            and len(full.get("all_mismatches", ())) == full.get("mismatch_count"),
            "reject missing full-matrix public correctness cases or mismatches")
    for engine in ("stdlib", "rust"):
        artifacts.append(exclusive_write(output + "/public-10434-" + engine
                                        + ".correctness.raw.json", originals[engine][1]))
    artifacts.append(exclusive_write(output + "/public-10434-correctness.raw.json",
                                    document(full)))

    profile = load_harness(payloads["public_profile_v1_source"], overlay,
                           "rust_public_profile_v1.py")
    matrix = profile.build_public_matrix()
    profile.validate_public_matrix(matrix)
    require(len(matrix) == PUBLIC_PROFILE_CASES
            and profile.MATRIX_SHA256 == PUBLIC_PROFILE_MATRIX,
            "reject the complete unchanged 416-case public profile matrix")
    observations = {}
    for engine in ("stdlib", "rust"):
        result, raw = run_worker(overlay, "rust_public_profile_v1.py",
                                 next(row[2] for row in OWNERS
                                      if row[0] == "public_profile_v1_source"),
                                 architecture + "-public-416-observe-" + engine,
                                 engine, "observe")
        observations[engine] = result
        artifacts.append(exclusive_write(output + "/public-416-" + engine
                                        + ".correctness.raw.json", raw))
    require(observations["stdlib"]["pid"] != observations["rust"]["pid"]
            and len(observations["stdlib"]["records"]) == PUBLIC_PROFILE_CASES
            and len(observations["rust"]["records"]) == PUBLIC_PROFILE_CASES,
            "reject incomplete or nonisolated complete 416-case observations")
    mismatches = [{"case": baseline["case"],
                   "baseline_outcome": baseline["outcome"],
                   "rust_outcome": actual["outcome"]}
                  for baseline, actual in zip(observations["stdlib"]["records"],
                                              observations["rust"]["records"], strict=True)
                  if baseline != actual]
    profile_gate = {"status": "FAIL" if mismatches else "PASS",
                    "case_count": PUBLIC_PROFILE_CASES,
                    "mismatch_count": len(mismatches), "all_mismatches": mismatches,
                    "baseline_pid": observations["stdlib"]["pid"],
                    "rust_pid": observations["rust"]["pid"]}
    artifacts.append(exclusive_write(output + "/public-416-correctness-gate.raw.json",
                                    document(profile_gate)))
    rows = []
    profiles = {}
    summary = NOT_MEASURED
    if not mismatches:
        ids = [case["case"] for case in matrix]
        matrix_by_id = {case["case"]: case for case in matrix}
        for round_number in range(PUBLIC_PAIRED_ROUNDS):
            offset = (PUBLIC_PROFILE_SEED + round_number * 37) % len(ids)
            order = ids[offset:] + ids[:offset]
            if round_number % 2:
                order.reverse()
            request = {"schema": profile.SCHEMA + "-worker-request",
                       "published_seed": PUBLIC_PROFILE_SEED,
                       "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                       "expected_records_sha256": observations["stdlib"]["records_sha256"],
                       "expected_records": observations["stdlib"]["records"],
                       "round": round_number, "iterations": PUBLIC_ITERATIONS,
                       "warmups": PUBLIC_WARMUPS, "case_order": order}
            engines = ("stdlib", "rust") if round_number % 2 == 0 else ("rust", "stdlib")
            rounds = {}
            for engine in engines:
                result, raw = run_worker(
                    overlay, "rust_public_profile_v1.py",
                    next(row[2] for row in OWNERS if row[0] == "public_profile_v1_source"),
                    architecture + "-public-timing-" + format(round_number, "02d")
                    + "-" + engine, engine, "timing", request)
                rounds[engine] = result
                artifacts.append(exclusive_write(output + "/public-416-" + engine
                                                + "-round-" + format(round_number, "02d")
                                                + ".raw.json", raw))
            require(rounds["stdlib"]["pid"] != rounds["rust"]["pid"],
                    "reject a paired timing round sharing a candidate process")
            for baseline, actual in zip(rounds["stdlib"]["rows"],
                                        rounds["rust"]["rows"], strict=True):
                case = matrix_by_id[baseline["case"]]
                require(actual["case"] == baseline["case"]
                        and actual["round"] == baseline["round"] == round_number
                        and actual["position"] == baseline["position"]
                        and actual["iterations"] == baseline["iterations"]
                        == PUBLIC_ITERATIONS
                        and actual["expected_outcome_sha256"]
                        == baseline["expected_outcome_sha256"],
                        "reject a mismatched correctness-gated public timing pair")
                rows.append({"case": baseline["case"], "round": round_number,
                             "position": baseline["position"], "cohort": case["cohort"],
                             "operation": case["operation"], "pair_order": list(engines),
                             "baseline_pid": rounds["stdlib"]["pid"],
                             "rust_pid": rounds["rust"]["pid"],
                             "iterations": PUBLIC_ITERATIONS,
                             "correctness_checks_per_engine": baseline["correctness_checks"],
                             "baseline_elapsed_ns": baseline["elapsed_ns"],
                             "rust_elapsed_ns": actual["elapsed_ns"]})
        artifacts.append(exclusive_write(output + "/public-416-paired-timing.raw.json",
                                        profile.canonical({"schema": SCHEMA + "-paired-rows",
                                                           "rows": rows})))
        profile_request = {"schema": profile.SCHEMA + "-worker-request",
                           "published_seed": PUBLIC_PROFILE_SEED,
                           "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                           "expected_records_sha256": observations["stdlib"]["records_sha256"],
                           "expected_records": observations["stdlib"]["records"],
                           "profile_passes": PUBLIC_PROFILE_PASSES}
        for engine in ("stdlib", "rust"):
            result, raw = run_worker(
                overlay, "rust_public_profile_v1.py",
                next(row[2] for row in OWNERS if row[0] == "public_profile_v1_source"),
                architecture + "-public-profile-" + engine,
                engine, "profile", profile_request)
            profiles[engine] = result
            artifacts.append(exclusive_write(output + "/public-416-" + engine
                                            + "-memory-profile.raw.json", raw))
        summary = paired_summary(rows)
        # JSON floats are actual measured performance only, never source-gate evidence.
        artifacts.append(exclusive_write(
            output + "/public-416-performance-summary.raw.json",
            (json.dumps(summary, ensure_ascii=True, allow_nan=False,
                        sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")))
    canonical_after = snapshot_canonical()
    require(canonical_before == canonical_after,
            "a canonical candidate identity changed during isolated architecture use")
    full_pass = full["status"] == "PASS"
    result = {"schema": SCHEMA + "-durable-publication-receipt", "status": "PASS",
              "architecture": architecture, "session": session,
              "source_sha256": freeze["source_sha256"],
              "protocol_sha256": freeze["protocol_sha256"],
              "contract_sha256": args["--contract-sha256"],
              "frozen_commit": args["--frozen-commit"],
              "pushed_commit": args["--pushed-commit"],
              "root_authorization": "EXPLICIT",
              "architecture_publication_sha256": selected["publication_sha256"],
              "architecture_root_receipt_sha256": selected["root_receipt_sha256"],
              "engine_sha256": selected["engine_sha256"],
              "bridge_sha256": selected["bridge_sha256"],
              "adapter_sha256": ADAPTER_SHA256,
              "adapter_provenance_root_receipt_sha256": adapter_pin["source_root_receipt_sha256"],
              "private_overlay": overlay, "canonical_candidates_before": canonical_before,
              "canonical_candidates_after": canonical_after,
              "canonical_candidate_modified": False,
              "public_10434_correctness_status": full["status"],
              "public_10434_case_count": PUBLIC_CORRECTNESS_CASES,
              "public_10434_mismatch_count": full["mismatch_count"],
              "public_416_correctness_gate": profile_gate,
              "public_416_timing_status": "NOT RUN" if mismatches else "PASS",
              "paired_row_count": len(rows),
              "performance_evidence_scope":
              "NOT MEASURED" if mismatches else
              "CORRECTNESS-GATED PUBLIC 416 ONLY" if full_pass else
              "EXPLORATORY CORRECTNESS-GATED PUBLIC 416 ONLY; PUBLIC 10434 FAILED",
              "performance_summary": summary,
              "memory_profiles": profiles if profiles else NOT_MEASURED,
              "native_external_cpu_profiler": NOT_MEASURED,
              "artifacts": artifacts,
              "runtime_non_delegation": "NOT ESTABLISHED; V4 STRICT AUDIT FAIL 1",
              "candidate_qualified": False,
              "qualified_independent_family_count": 0,
              "minimum_qualified_independent_family_count": 3,
              "winner_selected": False,
              "holdout_scope": "ONLY THIS FROZEN CONTROLLER AND ITS AUTHORIZED WORKERS",
              "other_agent_historical_holdout_access": "NOT ATTESTED",
              "controller_final_holdout_content_open_count": 0,
              "hidden_case_files_generated": 0, "hidden_cases_read": 0,
              "current_final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
              "retired_v2_proposal_status": "COMPROMISED; RETIRED; NOT ACCESSED BY THIS CONTROLLER",
              "holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
              "final_holdout_case_status": "NOT GENERATED; REKEYED SUCCESSOR REQUIRED"}
    encoded = (json.dumps(result, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    receipt = exclusive_write(ROOT + "/oracle/phase2/evidence/"
                              + "rust-native-architecture-public-gate-v3-"
                              + session + "-publication-receipt.json", encoded)
    return {"schema": SCHEMA + "-actual-root-operation", "status": "PASS",
            "architecture": architecture, "session": session,
            "public_10434_correctness_status": full["status"],
            "public_10434_mismatch_count": full["mismatch_count"],
            "public_416_correctness_status": profile_gate["status"],
            "paired_row_count": len(rows),
            "candidate_qualified": False,
            "runtime_non_delegation": result["runtime_non_delegation"],
            "canonical_candidate_modified": False,
            "controller_final_holdout_content_open_count": 0,
            "hidden_case_files_generated": 0, "hidden_cases_read": 0,
            "current_final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED",
            "publication_receipt": receipt,
            "performance_summary": summary}


def corrected_actual_run(payloads: dict[str, bytes], freeze: dict, args: dict) -> dict:
    import json
    import tempfile

    architecture = args["--architecture"]
    session = args["--session"]
    require(architecture == "v33"
            and type(session) is str and 1 <= len(session) <= 80
            and all(char in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for char in session)
            and session.startswith("v33-corrected-performance-")
            and not any(token in session
                        for token in ("holdout", "hidden", "final", "sealed", "proposal")),
            "require an exclusive V33 public-only corrected-performance session")
    require(args["--root-authorized"] == "YES"
            and check_commit(args["--frozen-commit"], "frozen commit")
            == check_commit(args["--pushed-commit"], "pushed commit"),
            "root alone may run the exact committed and pushed corrected freeze")
    selected = freeze["architectures"]["v33"]
    require(args["--v26-publication-sha256"]
            == freeze["architectures"]["v26"]["publication_sha256"]
            and args["--v26-root-sha256"]
            == freeze["architectures"]["v26"]["root_receipt_sha256"]
            and args["--v27-publication-sha256"]
            == freeze["architectures"]["v27"]["publication_sha256"]
            and args["--v27-root-sha256"]
            == freeze["architectures"]["v27"]["root_receipt_sha256"]
            and args["--v28-publication-sha256"]
            == freeze["architectures"]["v28"]["publication_sha256"]
            and args["--v28-root-sha256"]
            == freeze["architectures"]["v28"]["root_receipt_sha256"]
            and args["--v33-publication-sha256"] == selected["publication_sha256"]
            and args["--v33-root-sha256"] == selected["root_receipt_sha256"]
            and args["--v33-public-pass-sha256"] == selected["public_pass_receipt_sha256"]
            and args["--v33-original-pass-sha256"]
            == selected["exact_v33_original_pass_receipt_sha256"]
            and args["--v26-original-pass-sha256"]
            == selected["historical_v30_original_pass_receipt_sha256"]
            and args["--static-pass-sha256"] == selected["static_pass_receipt_sha256"],
            "independently caller-pin historical comparisons, V33 PASS, original PASS, and audit")
    canonical_before = snapshot_canonical()
    root = selected["root"]
    phase = root["phases"][0]
    root_info = os.stat(root["path"], follow_symlinks=False)
    phase_info = os.stat(phase["absolute_path"], follow_symlinks=False)
    require(stat.S_ISDIR(root_info.st_mode)
            and stat.S_IMODE(root_info.st_mode) == 0o700
            and (root_info.st_dev, root_info.st_ino)
            == (PRIVATE_DEVICE, V33_ROOT_INODE)
            and root_info.st_uid == os.geteuid()
            and os.path.realpath(root["path"]) == V33_ROOT_PATH
            and stat.S_ISDIR(phase_info.st_mode)
            and stat.S_IMODE(phase_info.st_mode) == 0o700
            and (phase_info.st_dev, phase_info.st_ino)
            == (PRIVATE_DEVICE, phase["inode"])
            and phase_info.st_uid == os.geteuid()
            and os.path.realpath(phase["absolute_path"]) == phase["absolute_path"],
            "require exact live actual-root and phase identities before native/candidate access")
    adapter_pin = selected["private_corrected_adapter"]
    adapter = exact_file(adapter_pin["path"], expected_sha=adapter_pin["sha256"],
                         expected_bytes=adapter_pin["bytes"],
                         device=adapter_pin["device"], inode=adapter_pin["inode"],
                         mode=0o600, role="seven-repair actual private V33 adapter")
    artifact_payloads = {}
    for artifact in phase["native_outputs"]:
        artifact_payloads[artifact["role"]] = exact_file(
            artifact["absolute_path"], expected_sha=artifact["sha256"],
            expected_bytes=artifact["bytes"], device=artifact["device"],
            inode=artifact["inode"], mode=int(artifact["mode"], 8),
            role="complete actual V33 independent " + artifact["role"],
        )
    overlay = tempfile.mkdtemp(prefix="rebar-rust-corrected-performance-v4-",
                               dir="/tmp")
    require(os.path.realpath(overlay) == overlay
            and stat.S_IMODE(os.stat(overlay).st_mode) == 0o700,
            "require one genuinely fresh V33 first-party native-performance overlay")
    os.mkdir(overlay + "/tools", 0o700)
    os.mkdir(overlay + "/candidates", 0o700)
    exclusive_write(overlay + "/candidates/__init__.py", b"", 0o600)
    exclusive_write(overlay + "/candidates/rust_candidate.py", adapter, 0o600)
    exclusive_write(overlay + "/candidates/_rust_engine.so",
                    artifact_payloads["engine"], 0o600)
    exclusive_write(overlay + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
                    artifact_payloads["bridge"], 0o700)
    exclusive_write(overlay + "/tools/rust_public_profile_v1.py",
                    payloads["public_profile_v1_source"], 0o600)

    profile = load_harness(payloads["public_profile_v1_source"], overlay,
                           "rust_public_profile_v1.py")
    matrix = profile.build_public_matrix()
    profile.validate_public_matrix(matrix)
    require(len(matrix) == PUBLIC_PROFILE_CASES
            and profile.MATRIX_SHA256 == PUBLIC_PROFILE_MATRIX,
            "require every unchanged public 416-case standard-library comparison")
    harness_sha = next(row[2] for row in OWNERS
                       if row[0] == "public_profile_v1_source")
    observations = {}
    observation_raw = {}
    for engine in ("stdlib", "rust"):
        result, raw = run_worker(overlay, "rust_public_profile_v1.py", harness_sha,
                                 "v33-corrected-public-416-observe-" + engine,
                                 engine, "observe")
        observations[engine] = result
        observation_raw[engine] = raw
    require(observations["stdlib"]["pid"] != observations["rust"]["pid"]
            and len(observations["stdlib"]["records"]) == PUBLIC_PROFILE_CASES
            and len(observations["rust"]["records"]) == PUBLIC_PROFILE_CASES,
            "complete both isolated 416-case correctness vectors before any timing")
    mismatches = [{"case": baseline["case"],
                   "baseline_outcome": baseline["outcome"],
                   "rust_outcome": actual["outcome"]}
                  for baseline, actual in zip(observations["stdlib"]["records"],
                                              observations["rust"]["records"], strict=True)
                  if baseline != actual]
    require(not mismatches
            and observations["stdlib"]["records_sha256"]
            == observations["rust"]["records_sha256"],
            "reject any public mismatch before timing, profiling, or persistent output")

    parent = ROOT + "/experiments/rust_corrected_public_performance_v4"
    try:
        os.mkdir(parent, 0o700)
    except FileExistsError:
        parent_info = os.stat(parent, follow_symlinks=False)
        require(stat.S_ISDIR(parent_info.st_mode)
                and stat.S_IMODE(parent_info.st_mode) == 0o700
                and parent_info.st_uid == os.geteuid(),
                "reject an unsafe corrected-performance public output parent")
    output = parent + "/" + session
    os.mkdir(output, 0o700)
    artifacts = [exclusive_write(output + "/public-416-" + engine
                                 + ".correctness.raw.json", observation_raw[engine])
                 for engine in ("stdlib", "rust")]
    profile_gate = {"status": "PASS", "case_count": PUBLIC_PROFILE_CASES,
                    "mismatch_count": 0, "all_mismatches": [],
                    "baseline_pid": observations["stdlib"]["pid"],
                    "rust_pid": observations["rust"]["pid"],
                    "records_sha256": observations["stdlib"]["records_sha256"],
                    "completed_before_any_timing": True}
    artifacts.append(exclusive_write(output + "/public-416-correctness-gate.raw.json",
                                    document(profile_gate)))
    ids = [case["case"] for case in matrix]
    matrix_by_id = {case["case"]: case for case in matrix}
    rows = []
    worker_processes = [observations["stdlib"]["pid"], observations["rust"]["pid"]]
    for round_number in range(PUBLIC_PAIRED_ROUNDS):
        offset = (PUBLIC_PROFILE_SEED + round_number * 37) % len(ids)
        order = ids[offset:] + ids[:offset]
        if round_number % 2:
            order.reverse()
        request = {"schema": profile.SCHEMA + "-worker-request",
                   "published_seed": PUBLIC_PROFILE_SEED,
                   "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                   "expected_records_sha256": observations["stdlib"]["records_sha256"],
                   "expected_records": observations["stdlib"]["records"],
                   "round": round_number, "iterations": PUBLIC_ITERATIONS,
                   "warmups": PUBLIC_WARMUPS, "case_order": order}
        engines = (("stdlib", "rust") if round_number % 2 == 0
                   else ("rust", "stdlib"))
        rounds = {}
        for engine in engines:
            result, raw = run_worker(
                overlay, "rust_public_profile_v1.py", harness_sha,
                "v33-corrected-public-timing-" + format(round_number, "02d")
                + "-" + engine, engine, "timing", request,
            )
            rounds[engine] = result
            worker_processes.append(result["pid"])
            artifacts.append(exclusive_write(
                output + "/public-416-" + engine + "-round-"
                + format(round_number, "02d") + ".raw.json", raw,
            ))
        require(rounds["stdlib"]["pid"] != rounds["rust"]["pid"],
                "reject a paired process reuse or noncounterbalanced timing round")
        for baseline, actual in zip(rounds["stdlib"]["rows"],
                                    rounds["rust"]["rows"], strict=True):
            case = matrix_by_id[baseline["case"]]
            require(actual["case"] == baseline["case"]
                    and actual["round"] == baseline["round"] == round_number
                    and actual["position"] == baseline["position"]
                    and actual["iterations"] == baseline["iterations"]
                    == PUBLIC_ITERATIONS
                    and actual["expected_outcome_sha256"]
                    == baseline["expected_outcome_sha256"],
                    "reject a missing, substituted, or incorrectly gated public timing pair")
            rows.append({"case": baseline["case"], "round": round_number,
                         "position": baseline["position"], "cohort": case["cohort"],
                         "operation": case["operation"], "pair_order": list(engines),
                         "baseline_pid": rounds["stdlib"]["pid"],
                         "rust_pid": rounds["rust"]["pid"],
                         "iterations": PUBLIC_ITERATIONS,
                         "correctness_checks_per_engine": baseline["correctness_checks"],
                         "baseline_elapsed_ns": baseline["elapsed_ns"],
                         "rust_elapsed_ns": actual["elapsed_ns"]})
    require(len(rows) == PUBLIC_PAIRED_ROWS
            and sum(row["pair_order"][0] == "stdlib" for row in rows)
            == PUBLIC_PAIRED_ROWS // 2,
            "require all 1664 exactly balanced paired observations")
    paired_payload = profile.canonical({"schema": SCHEMA + "-paired-rows",
                                        "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                                        "rows_sha256": profile.digest(rows),
                                        "rows": rows})
    artifacts.append(exclusive_write(output + "/public-416-paired-timing.raw.json",
                                    paired_payload))
    profile_request = {"schema": profile.SCHEMA + "-worker-request",
                       "published_seed": PUBLIC_PROFILE_SEED,
                       "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                       "expected_records_sha256": observations["stdlib"]["records_sha256"],
                       "expected_records": observations["stdlib"]["records"],
                       "profile_passes": PUBLIC_PROFILE_PASSES}
    profiles = {}
    for engine in ("stdlib", "rust"):
        result, raw = run_worker(overlay, "rust_public_profile_v1.py", harness_sha,
                                 "v33-corrected-public-memory-" + engine,
                                 engine, "profile", profile_request)
        profiles[engine] = result
        worker_processes.append(result["pid"])
        artifacts.append(exclusive_write(output + "/public-416-" + engine
                                        + "-memory-profile.raw.json", raw))
    require(len(worker_processes) == 12 and len(set(worker_processes)) == 12,
            "require exactly twelve independent correctness, timing, and memory workers")
    memory = {}
    for engine in ("stdlib", "rust"):
        heap = profiles[engine].get("python_heap")
        require(type(heap) is dict and type(heap.get("maximum_rss_kib")) is int
                and heap["maximum_rss_kib"] > 0
                and type(heap.get("tracemalloc_peak_bytes")) is int
                and heap["tracemalloc_peak_bytes"] >= 0
                and profiles[engine].get("public_case_executions")
                == PUBLIC_PROFILE_CASES * PUBLIC_PROFILE_PASSES,
                "require complete equally configured genuine per-engine memory profiles")
        memory[engine] = {"maximum_rss_kib": heap["maximum_rss_kib"],
                          "tracemalloc_peak_bytes": heap["tracemalloc_peak_bytes"],
                          "allocated_blocks_delta": heap["allocated_blocks_delta"],
                          "public_case_executions": profiles[engine]["public_case_executions"],
                          "pid": profiles[engine]["pid"]}
    summary = paired_summary(rows)
    summary.update({"schema": SCHEMA + "-actual-public-performance-summary",
                    "status": "PASS", "matrix_sha256": PUBLIC_PROFILE_MATRIX,
                    "published_seed": PUBLIC_PROFILE_SEED,
                    "paired_rounds": PUBLIC_PAIRED_ROUNDS,
                    "iterations": PUBLIC_ITERATIONS, "warmups": PUBLIC_WARMUPS,
                    "equal_case_weight": True,
                    "counterbalanced_process_order": True,
                    "identical_process_environment": {
                        "PATH": "/usr/bin:/bin", "LC_ALL": "C",
                        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                        "PYTHONMALLOC": "malloc"},
                    "correctness_checks_per_engine_per_pair":
                        PUBLIC_ITERATIONS + PUBLIC_WARMUPS + 1,
                    "raw_pair_count": PUBLIC_PAIRED_ROWS,
                    "memory_summary": memory,
                    "historical_v26_v27_v28":
                        freeze["preserved_v26_v27_v28_actual_public_performance"]})
    artifacts.append(exclusive_write(
        output + "/public-416-performance-summary.raw.json",
        (json.dumps(summary, ensure_ascii=True, allow_nan=False,
                    sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"),
    ))
    canonical_after = snapshot_canonical()
    require(canonical_before == canonical_after,
            "a canonical candidate source/native identity changed during performance")
    result = {"schema": SCHEMA + "-durable-publication-receipt", "status": "PASS",
              "architecture": "v33", "session": session,
              "source_sha256": freeze["source_sha256"],
              "protocol_sha256": freeze["protocol_sha256"],
              "contract_sha256": args["--contract-sha256"],
              "frozen_commit": args["--frozen-commit"],
              "pushed_commit": args["--pushed-commit"],
              "root_authorization": "EXPLICIT",
              "v33_publication_sha256": selected["publication_sha256"],
              "v33_root_sha256": selected["root_receipt_sha256"],
              "v33_public_pass_sha256": selected["public_pass_receipt_sha256"],
              "v33_exact_original_pass_sha256":
                  selected["exact_v33_original_pass_receipt_sha256"],
              "historical_v30_v26_original_pass_sha256":
                  selected["historical_v30_original_pass_receipt_sha256"],
              "v5_static_pass_sha256": selected["static_pass_receipt_sha256"],
              "native_engine_sha256": V33_ENGINE_SHA256,
              "native_bridge_sha256": V33_BRIDGE_SHA256,
              "corrected_adapter_sha256": V33_ADAPTER_SHA256,
              "corrected_adapter_bytes": V33_ADAPTER_BYTES,
              "private_overlay": overlay,
              "canonical_candidates_before": canonical_before,
              "canonical_candidates_after": canonical_after,
              "canonical_candidate_modified": False,
              "public_10434_correctness_status": "PASS",
              "public_10434_case_count": PUBLIC_CORRECTNESS_CASES,
              "public_10434_mismatch_count": 0,
              "historical_v30_original_31237_correctness_status": "PASS",
              "historical_v30_original_31237_case_count": 31237,
              "historical_v30_original_31237_mismatch_count": 0,
              "exact_v33_original_31237_correctness_status": "PASS",
              "exact_v33_original_31237_case_count": 31237,
              "exact_v33_original_31237_mismatch_count": 0,
              "exact_v33_original_completed_suite_count": 13,
              "preserved_v28_original_entry_failure_sha256":
                  selected["preserved_original_entry_failure_sha256"],
              "preserved_v28_original_worker_failure_sha256":
                  selected["preserved_original_worker_failure_sha256"],
              "public_416_correctness_gate": profile_gate,
              "public_416_timing_status": "PASS",
              "paired_row_count": PUBLIC_PAIRED_ROWS,
              "worker_process_ids": worker_processes,
              "worker_process_count": len(worker_processes),
              "performance_evidence_scope": "CORRECTNESS-GATED PUBLIC 416 ONLY",
              "performance_summary": summary,
              "memory_profiles": profiles, "memory_summary": memory,
              "historical_public_performance":
                  freeze["preserved_v26_v27_v28_actual_public_performance"],
              "artifacts": artifacts,
              "static_non_delegation": "PASS; SOURCE/ELF STATIC AUDIT ONLY",
              "runtime_non_delegation": "NOT ESTABLISHED",
              "candidate_qualified": False,
              "qualified_independent_family_count": 0,
              "minimum_qualified_independent_family_count": 3,
              "winner_selected": False,
              "proposal_content_open_count": 0,
              "proposal_metadata_probe_count": 0,
              "controller_final_holdout_content_open_count": 0,
              "hidden_case_files_generated": 0, "hidden_cases_read": 0,
              "current_final_holdout": "INVALIDATED; REKEYED SUCCESSOR REQUIRED"}
    encoded = (json.dumps(result, ensure_ascii=True, allow_nan=False,
                          sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    receipt = exclusive_write(
        ROOT + "/oracle/phase2/evidence/rust-corrected-public-performance-v4-"
        + session + "-publication-receipt.json", encoded,
    )
    return {"schema": SCHEMA + "-actual-root-operation", "status": "PASS",
            "architecture": architecture, "session": session,
            "public_10434_correctness_status": "PASS",
            "historical_v30_original_31237_correctness_status": "PASS",
            "exact_v33_original_31237_correctness_status": "PASS",
            "public_416_correctness_status": "PASS",
            "paired_row_count": PUBLIC_PAIRED_ROWS,
            "worker_process_count": len(worker_processes),
            "candidate_qualified": False, "winner_selected": False,
            "proposal_content_open_count": 0,
            "proposal_metadata_probe_count": 0,
            "publication_receipt": receipt,
            "performance_summary": summary,
            "memory_summary": memory}


def parse_arguments(argv: list[str]) -> tuple[str, dict[str, str]]:
    require(bool(argv), "require one explicit source-only or authorized-root mode")
    mode = argv[0]
    require(mode in ("--render-contract", "--verify-source", "--verify-frozen-context",
                     "--self-test", "--run"),
            "reject an unknown native architecture public gate mode")
    require((len(argv) - 1) % 2 == 0, "require exact named option/value pairs")
    args = {}
    for index in range(1, len(argv), 2):
        name, value = argv[index:index + 2]
        require(name.startswith("--") and name not in args and bool(value),
                "reject duplicated or malformed public gate arguments")
        args[name] = value
    expected = {"--source-sha256", "--protocol-sha256"}
    if mode in ("--verify-source", "--verify-frozen-context", "--self-test", "--run"):
        expected.add("--contract-sha256")
    if mode == "--run":
        expected |= {"--architecture", "--session", "--root-authorized",
                     "--frozen-commit", "--pushed-commit",
                     "--v26-publication-sha256", "--v26-root-sha256",
                     "--v27-publication-sha256", "--v27-root-sha256",
                     "--v28-publication-sha256", "--v28-root-sha256",
                     "--v33-publication-sha256", "--v33-root-sha256",
                     "--v33-public-pass-sha256", "--v33-original-pass-sha256",
                     "--v26-original-pass-sha256",
                     "--static-pass-sha256"}
    require(set(args) == expected, "reject missing or unexpected public gate options")
    for key in expected:
        if key.endswith("-sha256"):
            check_sha(args[key], key)
        elif key.endswith("-commit"):
            check_commit(args[key], key)
    return mode, args


def main(argv: list[str]) -> int:
    require(sys.implementation.name == "cpython"
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.flags.no_site == 1
            and sys.dont_write_bytecode is True
            and os.path.abspath(sys.executable) == PYTHON
            and os.path.realpath(sys.executable) == PYTHON,
            "use only pinned isolated no-site CPython 3.14.6")
    no_matching_imports()
    mode, args = parse_arguments(argv)
    source_only = mode != "--run"
    wall = SourceWall() if source_only else None
    if wall is not None:
        wall.install()
    payloads, freeze = load_context(wall, args["--source-sha256"],
                                    args["--protocol-sha256"],
                                    args.get("--contract-sha256"))
    if mode == "--render-contract":
        assert wall is not None
        wall_summary(wall)
        sys.stdout.buffer.write(document(freeze))
    elif mode in ("--verify-source", "--verify-frozen-context"):
        assert wall is not None
        summary = wall_summary(wall)
        summary.update({"schema": SCHEMA + "-verified-source", "status": "PASS",
                        "source_sha256": args["--source-sha256"],
                        "protocol_sha256": args["--protocol-sha256"],
                        "contract_sha256": args["--contract-sha256"],
                        "published_owner_count": len(OWNERS),
                        "actual_native_architecture_count": 4,
                        "public_correctness_case_count": PUBLIC_CORRECTNESS_CASES,
                        "public_profile_case_count": PUBLIC_PROFILE_CASES,
                        "paired_row_count": PUBLIC_PAIRED_ROWS,
                        "runtime_non_delegation": freeze["runtime_non_delegation"],
                        "candidate_qualified": False})
        sys.stdout.buffer.write(document(summary))
    elif mode == "--self-test":
        assert wall is not None
        sys.stdout.buffer.write(document(source_self_test(wall, freeze)))
    else:
        sys.stdout.buffer.write((__import__("json").dumps(
            corrected_actual_run(payloads, freeze, args), ensure_ascii=True,
            allow_nan=False, sort_keys=True, separators=(",", ":"))
            + "\n").encode("ascii"))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (GateError, OSError, ValueError, TypeError, KeyError) as error:
        sys.stderr.write("native architecture public gate rejected: " + str(error) + "\n")
        raise SystemExit(2)
