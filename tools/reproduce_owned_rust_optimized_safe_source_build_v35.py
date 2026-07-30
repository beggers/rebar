#!/usr/bin/env python3
"""Freeze and, only after root authorization, build full-public semantic Rust V35.

Every source gate installs an irreversible deny-default wall before opening an
owner. No final proposal is opened, stated, or inspected. The retired final is
INVALIDATED; REKEYED SUCCESSOR REQUIRED. Actual compilation is a separate,
caller-pinned, committed-and-pushed, root-only operation using the authentic
V16/V9/V7/V4 first-party 28-process offline compiler and ELF-audit kernel.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("the V35 first-party source boundary must not load a matcher")

import _io
import builtins
import hashlib
import io
import os
import stat
import time
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
DEVICE = 2064
SOURCE = "tools/reproduce_owned_rust_optimized_safe_source_build_v35.py"
PROTOCOL = "oracle/phase2/RUST-OPTIMIZED-SAFE-SOURCE-BUILD-V35.md"
CONTRACT = "oracle/phase2/rust-optimized-safe-source-build-v35.json"
SCHEMA = "rebar-phase2-owned-rust-optimized-safe-source-build-v35"
VERSION = 35
FAMILY = "rust"
LABEL = "phase2-v35-rust-optimized-safe-source-root-provenance"
FINAL_HOLDOUT_STATUS = "INVALIDATED; REKEYED SUCCESSOR REQUIRED"
CURRENT_PUBLIC_V3_STATUS = "PROPOSAL_NOT_FROZEN_NOT_GENERATED"
RETIRED_PROPOSAL = "oracle/phase3/expanded-sealed-holdout-v2.json"
RETIRED_PROPOSAL_SHA = "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
RETIRED_PROPOSAL_BYTES = 15561
RETIRED_PROPOSAL_INODE = 525920
RETIRED_PROPOSAL_CASE_COUNT = 141557760
BASE_ENGINE_SHA = "c627012d0ce8d1e2cc3c70301956a060eecc6656f82137b219e44ec905f235ee"
BASE_ENGINE_BYTES = 189423
SCOPED_ENGINE_SHA = "7412a997975aa42ec18249bc28d17e3c39223a4089bd23e3f7d2ab8112993b38"
SCOPED_ENGINE_BYTES = 189493
ENGINE_SHA = "7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136"
ENGINE_BYTES = 194276
SEARCH_SHA = "4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7"
SEARCH_BYTES = 24305
BASE_BRIDGE_SHA = "254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55"
BASE_BRIDGE_BYTES = 178270
BRIDGE_SHA = "f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e"
BRIDGE_BYTES = 178472
LITERAL_BRIDGE_SHA = "e4ee92d9d651600d94cf371f6437638b639b3418103cb20044fbdd26a60d5d57"
LITERAL_BRIDGE_BYTES = 180947
SAFE_BRIDGE_SHA = "c9b22c4443c36cc6e653af18fcd829561b7987df312368b30dfcbade254538f8"
SAFE_BRIDGE_BYTES = 182459
HISTORICAL_AUDITED_ENGINE_BINARY_SHA = "3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237"
HISTORICAL_AUDITED_BRIDGE_BINARY_SHA = "ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256"
EXACT_PREVIOUS_ENGINE_BINARY_SHA = "e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8"
EXACT_PREVIOUS_BRIDGE_BINARY_SHA = "ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000"
BASE_ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
BASE_ADAPTER_BYTES = 31934
ADAPTER_SHA = "f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227"
ADAPTER_BYTES = 34039
MAX_OWNER_BYTES = 2 * 1024 * 1024
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)

# role, exact workspace-relative path, complete SHA-256, bytes, device-2064 inode
CANONICAL_OWNERS = (
    ("cargo_lock", "candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167, 428098),
    ("cargo_manifest", "candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225, 428094),
    ("original_bridge", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054),
    ("original_engine", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096),
    ("original_newline", "candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416, 427958),
    ("original_search", "candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773, 429682),
    ("original_stack", "candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269, 428151),
    ("original_unicode", "candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989, 428152),
    ("original_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100),
)

# These are inspected only after every explicit root-only actual-build pin has
# passed.  No source gate may open or inspect either installed native file.
ACTUAL_RUNTIME_TARGETS = (
    ("original_engine_source", "candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967, 428096, 0o600),
    ("original_bridge_source", "candidates/rust/py_bridge.c", "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b", 175676, 419054, 0o600),
    ("original_public_adapter", "candidates/rust_candidate.py", "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b", 31151, 428100, 0o600),
    ("original_installed_engine", "candidates/_rust_engine.so", "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4", 660440, 430563, 0o755),
    ("original_installed_bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so", "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15", 144992, 430629, 0o755),
)

STATIC_OWNERS = CANONICAL_OWNERS + (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044),
    ("original_phase_one", "oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("anchor_transformer", "tools/apply_owned_rust_mandatory_anchor_search_v1.py", "d118af0c0da3b058fc8d40a59d47090a97fd8838fcbdb0fba36bcd0271da2eff", 74375, 429756),
    ("compiler_transformer", "tools/apply_owned_rust_compiler_allocation_fastpath_v1.py", "13ad7948ba05a057f1c93f404998d72217ad42a8a93da8d71f9a3f7b5a41d1bf", 75362, 429789),
    ("anchor_variant_engine", "candidates/rust/variants/mandatory_anchor_search_v1/lib.rs", "5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84", 189369, 526181),
    ("compiler_variant_engine", "candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs", "64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6", 178021, 526157),
    ("adapter_repair_source", "tools/apply_owned_rust_public_contract_source_repair_v3.py", "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060, 431033),
    ("adapter_repair_protocol", "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md", "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405, 524675),
    ("adapter_repair_contract", "oracle/phase2/rust-public-contract-source-repair-v3.json", "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817, 524678),
    ("combined_v2_source", "tools/apply_owned_rust_combined_search_compiler_fastpath_v2.py", "f8f2f7cf4e9339cf592048fd75cafe9a9d22d79c77137d1f8ab6d3b7493d976b", 89742, 430531),
    ("combined_v2_protocol", "oracle/phase2/RUST-COMBINED-SEARCH-COMPILER-FASTPATH-V2.md", "b612af3b53bb21b6f13b69db4c4197590a71af045fab14de250dad301a1794a1", 5577, 524866),
    ("combined_v2_contract", "oracle/phase2/rust-combined-search-compiler-fastpath-v2.json", "68f097d8433596fb45a9a9ca940eff68dcb8fe9f0d667a8c0ce9c5eb403196a6", 13914, 524939),
    ("combined_v2_application", "oracle/phase2/evidence/rust-combined-search-compiler-fastpath-v2-application.json", "1bce63305e04e4056ce3c660760a0bb8a3670a76aa528b9309232d0918c5061e", 2201, 525099),
    ("combined_v2_engine", "candidates/rust/variants/combined_search_compiler_fastpath_v2/lib.rs", BASE_ENGINE_SHA, BASE_ENGINE_BYTES, 525097),
    ("combined_v2_search", "candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs", SEARCH_SHA, SEARCH_BYTES, 525098),
    ("no_introspection_source", "tools/apply_owned_rust_no_external_introspection_v1.py", "68cafe6b6bdf336aff162f86c4c9ddc1aec7607e312c09b2a032e7462e466ec7", 61181, 430722),
    ("no_introspection_protocol", "oracle/phase2/RUST-NO-EXTERNAL-INTROSPECTION-V1.md", "15f068ecd0c1970d8bec1f9cb011072c09cb5d064938c24abe1088e4565268c3", 6240, 526268),
    ("no_introspection_contract", "oracle/phase2/rust-no-external-introspection-v1.json", "224e118a3878692552b31d588b38ea4953bee9c77c7853687b424360776b53d2", 5305, 526270),
    ("no_introspection_application", "oracle/phase2/evidence/rust-no-external-introspection-v1-application.json", "57e28ad65b538db5189f264904d303f37f13506022eae07b12185a52f2624a43", 1774, 524813),
    ("no_introspection_bridge", "candidates/rust/variants/no_external_introspection_v1/py_bridge.c", "2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7", 177146, 524811),
    ("ordering_source", "tools/apply_owned_rust_substitution_event_order_v2.py", "50489f3ce64e254364ab416c132045c1bdcafed8bf5393efc6afb4727323658e", 88530, 430898),
    ("ordering_protocol", "oracle/phase2/RUST-SUBSTITUTION-EVENT-ORDER-V2.md", "d1c30f4bf11682a09ed7a67d368585daf51168079cdbb22816f19889bd8d8cae", 11616, 525503),
    ("ordering_contract", "oracle/phase2/rust-substitution-event-order-v2.json", "de964c871ce364dce87e88fb97e151d0e8307199a50e24b35a8cbb4830fd7d00", 9407, 525522),
    ("ordering_application", "oracle/phase2/evidence/rust-substitution-event-order-v2-application.json", "51d783da90847820cff44fe0cdaf329200e35948798c34aa2fe9d371c7ca2fac", 2199, 525554),
    ("expand_source", "tools/apply_owned_rust_expand_probe_semantics_v1.py", "849a38fed6508b4e69ca049e46e932be65a98cbc49c0c3096e5edaf55ae75957", 65552, 430793),
    ("expand_protocol", "oracle/phase2/RUST-EXPAND-PROBE-SEMANTICS-V1.md", "e9eecf30afff954bfa1ceee79bef551f0cd31215de24e0d55a9f704adde559bf", 6545, 525224),
    ("expand_contract", "oracle/phase2/rust-expand-probe-semantics-v1.json", "e739146385553032f6f5705b4b43f230f4fe72070a0d4f636b86bbb66e4c1e14", 5270, 525225),
    ("expand_application", "oracle/phase2/evidence/rust-expand-probe-semantics-v1-application.json", "9eaff0631cb6aed1e8231d8dc9e1a346d2efb1cab88cb5b5cd686689f5a092b1", 1720, 525502),
    ("expand_bridge", "candidates/rust/variants/expand_probe_semantics_v1/py_bridge.c", "d0f0422a08592390619138d072cb831d6d446f38e2b67750798a221e7693d822", 178081, 525501),
    ("complete_v1_source", "tools/apply_owned_rust_complete_semantic_correction_v1.py", "15dc2a9836a0e75323935508efdf8d8af7414ea1e074e26a94bf7bb688f25627", 85883, 431405),
    ("complete_v1_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-CORRECTION-V1.md", "0e13cd5553dbae90abcfd732cda1e97e3ad2f4c2efa7e5e192304470053fe99b", 9023, 525840),
    ("complete_v1_contract", "oracle/phase2/rust-complete-semantic-correction-v1.json", "09e5847ff7139f8f6cbfef3abbc769b01f899cdc3b5259ef64c67fd74ebd6f25", 6634, 525841),
    ("complete_v1_failure", "oracle/phase2/evidence/rust-complete-semantic-correction-v1-preapplication-failure.json", "150e269c74f2f60b6fd188e5794d13a014b8e059cce91fa01ad59b2829b3f1c1", 883, 525938),
    ("complete_semantic_source", "tools/apply_owned_rust_complete_semantic_correction_v2.py", "dd80de72a2104703d8c36269cbef56e67231add6f31a7a8c8f7bf05aa5f0e807", 90354, 431596),
    ("complete_semantic_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-CORRECTION-V2.md", "aae4793c84f1f4d93806f2484047d3b1e2a7f544c25d02b08551f2d9f07f2936", 10629, 525979),
    ("complete_semantic_contract", "oracle/phase2/rust-complete-semantic-correction-v2.json", "25ae3e1a35fae2ace9533b14fdaf771c0270b50b5b93b5b702d683906ca2dbe3", 8308, 525985),
    ("complete_semantic_application", "oracle/phase2/evidence/rust-complete-semantic-correction-v2-application.json", "304396bb08709d63d0cb89e08d40e369a754f9e4352015955a33ab6fb99113cb", 2387, 526053),
    ("complete_semantic_bridge", "candidates/rust/variants/complete_semantic_correction_v2/py_bridge.c", BASE_BRIDGE_SHA, BASE_BRIDGE_BYTES, 526052),
    ("scanner_bridge_source", "tools/apply_owned_rust_complete_scanner_bridge_v1.py", "de9446d64c8aaf4253d2301118973e2c9de82b40dc52da9e2848e460685f1999", 88297, 429524),
    ("scanner_bridge_protocol", "oracle/phase2/RUST-COMPLETE-SCANNER-BRIDGE-V1.md", "1418606f649fa36e373b559ee7ba428bcb9a139ddb016b89fc903504c89106a2", 9872, 524936),
    ("scanner_bridge_contract", "oracle/phase2/rust-complete-scanner-bridge-v1.json", "e4b1b52fd9a8a9b3008672ceb6c685dc62dda60a217cdedf51841ca43300f7b7", 8013, 524969),
    ("scanner_bridge_application", "oracle/phase2/evidence/rust-complete-scanner-bridge-v1-application.json", "c665041fd03cb44cf29041a38848bdd3e61cee051f432e377a32d49a87537e97", 1031, 525190),
    ("scanner_bridge", "candidates/rust/variants/complete_scanner_bridge_v1/py_bridge.c", BRIDGE_SHA, BRIDGE_BYTES, 525163),
    ("comment_adapter_source", "tools/apply_owned_rust_corrected_comment_adapter_v1.py", "0f048599182b69965c88677cbfb9ccb162a9d9d943426d2b607503e48a797d69", 62699, 430272),
    ("comment_adapter_protocol", "oracle/phase2/RUST-CORRECTED-COMMENT-ADAPTER-V1.md", "e04e29068703fd8580beeeb2463df75ff7af68008f811e2e8a053cf4a91112f7", 8423, 525027),
    ("comment_adapter_contract", "oracle/phase2/rust-corrected-comment-adapter-v1.json", "ac99c411cd2cfcfcd66df63aff03c79ebedd9e41681b881eb78e7aa25252ee61", 5093, 525032),
    ("comment_adapter_v1_failure", "oracle/phase2/evidence/rust-corrected-comment-adapter-v1-preapplication-failure.json", "7bc692fcf17780ed05ca49c982536849212e1909f73337764b2392ea3ee9a37b", 902, 525290),
    ("comment_adapter_v2_source", "tools/apply_owned_rust_corrected_comment_adapter_v2.py", "209b05313a3cc7d58520f3979088a96d747c8e55e65f02313f64a33fe234795d", 65237, 430684),
    ("comment_adapter_v2_protocol", "oracle/phase2/RUST-CORRECTED-COMMENT-ADAPTER-V2.md", "cbbf0b168618767b27565b44c38c36a2dea85166d6050d6d3b4fab8f97937f5b", 9420, 525358),
    ("comment_adapter_v2_contract", "oracle/phase2/rust-corrected-comment-adapter-v2.json", "b9d7e7e4149591539e4682024b543fa69605e79a22e2a3397a244a25e6e0cc1a", 5762, 525396),
    ("comment_adapter_v2_application", "oracle/phase2/evidence/rust-corrected-comment-adapter-v2-application.json", "50c9d569d5c34118d7984e9d952b3cb99bb8cbb27e992caf786e626d383de6a8", 2162, 525455),
    ("comment_adapter", "candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py", ADAPTER_SHA, ADAPTER_BYTES, 525454),
    ("scoped_engine_source", "tools/apply_owned_rust_combined_scoped_unicode_engine_v1.py", "819b2a2576825e7bb84738564e432162063240ed09b9d3b8031c3815d2d17d16", 74851, 430270),
    ("scoped_engine_protocol", "oracle/phase2/RUST-COMBINED-SCOPED-UNICODE-ENGINE-V1.md", "6eba43efaa7019826806055ef2af6d0fe8cf180884f53baac0457d911ec9c36b", 5807, 524902),
    ("scoped_engine_contract", "oracle/phase2/rust-combined-scoped-unicode-engine-v1.json", "d5eb343f1ab16ace5d3ae9038a934d7a2dc5a22282e1e81f607234478c01a570", 9863, 525036),
    ("scoped_engine_application", "oracle/phase2/evidence/rust-combined-scoped-unicode-engine-v1-application.json", "776c7a631eb45edc4fa804bec1bb4e663f74ae18e5a1d5ccccbc0773545264df", 1091, 525399),
    ("scoped_engine", "candidates/rust/variants/combined_scoped_unicode_engine_v1/lib.rs", SCOPED_ENGINE_SHA, SCOPED_ENGINE_BYTES, 525398),
    ("literal_source", "tools/apply_owned_rust_exact_literal_fastpath_v1.py", "11f448875e70f5413731061b8b439c5caae9b5e212378febabbeb71fc7ea59e9", 59925, 430542),
    ("literal_protocol", "oracle/phase2/RUST-EXACT-LITERAL-FASTPATH-V1.md", "14b30b449c47c6b5935da16cf5723f2e6a505be294e4497d2c24bf10edc4ce57", 5289, 525191),
    ("literal_contract", "oracle/phase2/rust-exact-literal-fastpath-v1.json", "c0a76fb83774bd875759d24a31d255693c01ac12922029aefa8258ab8da86ac8", 7239, 525276),
    ("literal_application", "oracle/phase2/evidence/rust-exact-literal-fastpath-v1-application.json", "d44d99f74c402da804c93680a6e9d02a3e9029bdaca4047c56cd46c73850ccd8", 1605, 525960),
    ("literal_engine", "candidates/rust/variants/exact_literal_fastpath_v1/lib.rs", ENGINE_SHA, ENGINE_BYTES, 525959),
    ("v25_build_source", "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py", "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408", 186263, 429530),
    ("v25_build_protocol", "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md", "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85", 7140, 525993),
    ("v25_build_contract", "oracle/phase2/rust-capture-clamp-source-build-v25.json", "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a", 229419, 526066),
    ("v25_build_publication", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json", "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc", 5231, 526084),
    ("v25_build_root", "oracle/phase2/evidence/native-source-build-v25-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-root-provenance-receipt.json", "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2", 61798, 526085),
    ("v25_full_failure", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v25-rust-capture-clamp-v1-root-provenance-original-p0-v25-failures-publication-receipt.json", "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59", 11832, 524846),
    ("v26_build_source", "tools/reproduce_owned_rust_anchor_source_build_v26.py", "7a276a4bf675f818cfe3716aad13c5e741f4a45709e899c82af36e2b4cb10e66", 112085, 430771),
    ("v26_build_protocol", "oracle/phase2/RUST-ANCHOR-SOURCE-BUILD-V26.md", "06ffb539e1f9e2bf7350b1d27478c988dd7c429f2ee295e40181b9320b3e3fd3", 7578, 524812),
    ("v26_build_contract", "oracle/phase2/rust-anchor-source-build-v26.json", "ea213e235fb56ca4235763643d5569ebb1b63c45678363efe322a525eef65924", 21189, 524863),
    ("v26_build_publication", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-publication-receipt.json", "8a0e9d70dab2a3e1f3738d6e0e1a4716b78e0a1b329ce3b16010bd94b6598cd6", 5075, 524963),
    ("v26_build_root", "oracle/phase2/evidence/native-source-build-v26-rust-phase2-v26-rust-mandatory-anchor-root-provenance-root-provenance-receipt.json", "aaed35f9fe86090d75ce2162bae7902910461a7b4e731c22eba275406f328ba1", 76442, 524964),
    ("v27_build_source", "tools/reproduce_owned_rust_compiler_fastpath_source_build_v27.py", "4ac3123d83db6858a9fddd311b3b7ac7966e29aede6e786594c7d956e2bf9e8e", 245008, 429062),
    ("v27_build_protocol", "oracle/phase2/RUST-COMPILER-FASTPATH-SOURCE-BUILD-V27.md", "43b81f47a196d3db0972269d6fba4d94b4437cb59a1c5a3648d8d45f5939fa5f", 5810, 524809),
    ("v27_build_contract", "oracle/phase2/rust-compiler-fastpath-source-build-v27.json", "a2ffa190a8fd15ec3bcf82f0e1eedc5eb4b919af8c6b3fbf99cf54a525604a41", 617433, 524861),
    ("v27_build_publication", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-publication-receipt.json", "7fcbe3e07885f2a488ed1b3c79bc02888ad22dd2b21179081b3cecfc7b464c99", 6444, 524869),
    ("v27_build_root", "oracle/phase2/evidence/native-source-build-v27-rust-phase2-v27-rust-compiler-fast-v1-root-provenance-root-provenance-receipt.json", "c6958056757ab6145d613490db1a21165714dcb89c61e6d3bdf52500fad221b0", 64122, 524870),
    ("v28_build_source", "tools/reproduce_owned_rust_combined_source_build_v28.py", "4a1d2a1a4362fc791ddba601bcc6ac27d6338ad86d1ec6e62a057e80e1649de6", 108883, 430798),
    ("v28_build_protocol", "oracle/phase2/RUST-COMBINED-SOURCE-BUILD-V28.md", "1e319e4551535b5a5a78bbd751959c042e38514998ffcce14791df38eef1d519", 8410, 525227),
    ("v28_build_contract", "oracle/phase2/rust-combined-source-build-v28.json", "826e7d62a124491662506dee74076001080fad6b383bef9c951b24413b1da2fa", 27362, 525232),
    ("v28_build_publication", "oracle/phase2/evidence/native-source-build-v28-rust-phase2-v28-rust-combined-source-root-provenance-publication-receipt.json", "14b4e8ff5762269bf79a61f517b41b7b590497b4bb3b3262b53adf501c0b1a3a", 2384, 525540),
    ("v28_build_root", "oracle/phase2/evidence/native-source-build-v28-rust-phase2-v28-rust-combined-source-root-provenance-root-provenance-receipt.json", "01fcb306535d0f86e6ef2aaa27173cc333d16be0360e53581d7c3f83264b9484", 70622, 525541),
    ("v30_build_source", "tools/reproduce_owned_rust_complete_semantic_source_build_v30.py", "dd0ed268775537b985a060e5f608c6bc2730f86922ad20ee78cff19e4c387a1d", 138860, 431674),
    ("v30_build_protocol", "oracle/phase2/RUST-COMPLETE-SEMANTIC-SOURCE-BUILD-V30.md", "9f508fd651fa544ecea82487cb05bc94cce6aa1049ec676d257eb62fc73b3c61", 8746, 524934),
    ("v30_build_contract", "oracle/phase2/rust-complete-semantic-source-build-v30.json", "38e0a8f44cf1e3f68abb643b004f7f47350e743f5c3f1994d101b02e5ebc1956", 41458, 524935),
    ("v30_build_publication", "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-complete-semantic-source-root-provenance-publication-receipt.json", "c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd", 3438, 524977),
    ("v30_build_root", "oracle/phase2/evidence/native-source-build-v30-rust-phase2-v30-rust-complete-semantic-source-root-provenance-root-provenance-receipt.json", "26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404", 77160, 524978),
    ("v32_build_source", "tools/reproduce_owned_rust_full_public_semantic_source_build_v32.py", "19b4eb39ecadd0486b1385071716e78c6bf52f38b73bc54a3fd9bafc76106153", 164862, 430558),
    ("v32_build_protocol", "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V32.md", "cbfefb56f5c99209d30a5e7b368533554a9ce454db07acf42f274728ba0cb650", 6353, 525053),
    ("v32_build_contract", "oracle/phase2/rust-full-public-semantic-source-build-v32.json", "cf5c05d19a4b10ce3e4d32c326f63850a936d5e11c53f4a8d8a59fdcb90dec72", 53381, 525055),
    ("v32_build_failure", "oracle/phase2/evidence/native-source-build-v32-rust-full-public-preexecution-failure.json", "8adf8ae6fd08c0bf38df121ff6a2ea245ae69de19908a1effd0a50dbff809e85", 1113, 524905),
    ("v33_build_source", "tools/reproduce_owned_rust_full_public_semantic_source_build_v33.py", "31251c3aa6006108ba1a5b5e7b5a07147d9b8ccf76123f4aa08ecffb20c91c63", 172881, 429226),
    ("v33_build_protocol", "oracle/phase2/RUST-FULL-PUBLIC-SEMANTIC-SOURCE-BUILD-V33.md", "c73843e1705beb24e4ced9ab3d9fa95da7420c5d24cd8f6ffaeeb747aa382071", 7434, 524906),
    ("v33_build_contract", "oracle/phase2/rust-full-public-semantic-source-build-v33.json", "bb7d338cb766b7f1ff52e616355d5d5cddb00849532e42755b31a9bf09119337", 56235, 525061),
    ("v33_build_publication", "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-publication-receipt.json", "cfe1464e1e8ce96bfa514b15cf96879a0642686987159dd79c15f4d9db408749", 6696, 525066),
    ("v33_build_root", "oracle/phase2/evidence/native-source-build-v33-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-root-provenance-receipt.json", "7122c9bdff731be0f68602a4a216c1fa9700e6a78f9da9b534eeaef282c64c1c", 80421, 525067),
    ("v33_public_pass", "oracle/phase2/evidence/rust-full-public-correctness-v5-v33-full-public-v5-run-001-publication-receipt.json", "8e2343809a8d9226973b1b70ca9d7348f750573caa2729123afb007f02a03bd9", 6889, 525451),
    ("v26_original_pass", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v30-rust-complete-semantic-source-root-provenance-original-p0-v26-publication-receipt.json", "84804409997794ce7e8bfff67ca8ffdcada9651a1660bda2654742befbba20f5", 12055, 525046),
    ("v26_original_campaign_source", "tools/run_owned_repaired_rust_original_campaign_v26.py", "37d3edd69f93c33defaaeb8a1473e39b0563f06af57e6038340679dd8c61091d", 97746, 431629),
    ("v26_original_campaign_contract", "oracle/phase2/repaired-rust-original-campaign-v26.json", "8493afcb087e79b0b2419711746fb82dd5c09785fe086fa627ea99af41365eaa", 22874, 526048),
    ("v26_public_gate", "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v26-anchor-public-run-001-publication-receipt.json", "23baf96a92f4fd2bf2809730bed056606de0c9c350ed46eea31fa9bdff6a8d80", 40906, 525333),
    ("v27_public_gate", "oracle/phase2/evidence/rust-native-architecture-public-gate-v2-v27-compiler-public-run-001-publication-receipt.json", "a825c358434fb44ab9d52eb8021271115b12e41c58b26243c7770faf4d533449", 68330, 525426),
    ("v28_public_gate", "oracle/phase2/evidence/rust-native-architecture-public-gate-v3-v28-combined-public-run-001-publication-receipt.json", "c786b1216a58c4ac6a29363ce87d7741fb55fbb85f30665f795875bef244becb", 40372, 525923),
    ("strict_audit_source", "tools/audit_candidate_runtime_non_delegation_v4.py", "597f2f1156d773a42e32103ef7370e8552a416756910c013cdcd0cfc34d39b02", 121807, 429582),
    ("strict_audit_protocol", "oracle/phase2/RUNTIME-NON-DELEGATION-V4.md", "6c3bd6b2ccabe3ab240771d743afce5b32f1de17a510bedd835e867c5cea7826", 5325, 526087),
    ("strict_audit_contract", "oracle/phase2/runtime-non-delegation-v4.json", "edc3ac8866da7afb5934b56fbcbff38a908e5109f7975f998753b479aa7bc672", 7266, 526086),
    ("strict_audit_failure", "oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json", "c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19", 20985, 526140),
    ("public_profile", "oracle/phase3/rust-public-profile-v1.json", "b791b141eabbf6eb8a67484f5deb82bb41e324aedbdfe5b53a98ebc1553372c5", 1797, 525928),
    ("public_python", "experiments/rust_public_profile_v1/public-run-001/stdlib.correctness.raw.json", "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381", 445036, 526005),
    ("public_rust", "experiments/rust_public_profile_v1/public-run-001/rust.correctness.raw.json", "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0", 445394, 526006),
    ("public_paired", "experiments/rust_public_profile_v1/public-run-001/paired-timing.raw.json", "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85", 504907, 526015),
    ("public_graph", "docs/evidence/rust-public-practice-overall-v1.inputs.json", "ebcbce1c46a7c36be2b50e49c90e826f90b1822055c10fa89bf3984566be70fc", 16044, 429788),
    ("actual_v16_kernel", "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py", "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a", 134640, 431980),
    ("actual_v9_kernel", "tools/reproduce_owned_native_source_build_v9.py", "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f", 81124, 429976),
    ("actual_v7_kernel", "tools/reproduce_owned_native_source_build_v7.py", "20d8e43a9c70f585049f81d38f9085661b50e4bf754320a6abcd95d566d854a7", 300624, 431752),
    ("actual_v4_kernel", "tools/reproduce_owned_native_source_build_v4.py", "efb37ccca1524e98f32b734b600704a390bc55c73d374da61c089730aaff10b1", 136084, 431135),
)

STATIC_OWNERS = STATIC_OWNERS + (
    ("v34_predecessor_source", "tools/reproduce_owned_rust_exact_literal_source_build_v34.py", "a8b85c6245e78a9a872b28c8fa6e17d835cfe9dcc7eab3465b1524ef7698f645", 192639, 430815),
    ("v34_predecessor_protocol", "oracle/phase2/RUST-EXACT-LITERAL-SOURCE-BUILD-V34.md", "d8587f0f296a1def8197dcf4d721b1fbb947495205756a84db3740c7cdd80bb4", 5461, 525982),
    ("v34_predecessor_contract", "oracle/phase2/rust-exact-literal-source-build-v34.json", "c80339f6a189493999267f2d891b1b662de0643dfaa321aed131f38b65b01a03", 63409, 526059),
    ("literal_bridge_source", "tools/apply_owned_rust_literal_bridge_fastpath_v1.py", "e5745829c7e6099644218522e381b1d6dbfc49457546d10e4ef1f2dd39d10258", 62151, 430345),
    ("literal_bridge_protocol", "oracle/phase2/RUST-LITERAL-BRIDGE-FASTPATH-V1.md", "5ac3d86cb56b9497a465ef67ce28ee7be12020ed415a207bb92a561c9f1647f7", 5229, 526436),
    ("literal_bridge_contract", "oracle/phase2/rust-literal-bridge-fastpath-v1.json", "edc4ce1cb34667a449773548de46d48292b5bf61f9bd9f334bdc271c7bac0323", 8497, 526438),
    ("literal_bridge_application", "oracle/phase2/evidence/rust-literal-bridge-fastpath-v1-application.json", "48fbc982f5e490bc44e7fc0e2c0d25a88e2187371b75ed86ffc6042f41d185e6", 1082, 526544),
    ("literal_bridge", "candidates/rust/variants/literal_bridge_fastpath_v1/py_bridge.c", LITERAL_BRIDGE_SHA, LITERAL_BRIDGE_BYTES, 526538),
    ("handle_lease_source", "tools/apply_owned_rust_native_handle_lease_v1.py", "5c52dfec219a24a19d2771d1f6eb72fc08ab2e339249e32f2a627de017ab9cd7", 69830, 431766),
    ("handle_lease_protocol", "oracle/phase2/RUST-NATIVE-HANDLE-LEASE-V1.md", "719fa00528b423132eea0856b9047ecbef4fbde55e80edcfa950f346655357ec", 5907, 526588),
    ("handle_lease_contract", "oracle/phase2/rust-native-handle-lease-v1.json", "78d053d7663481b00bd63d1a8dd0c6fba008c260d1b486622da5d465c7e88370", 10757, 526604),
    ("handle_lease_application", "oracle/phase2/evidence/rust-native-handle-lease-v1-application.json", "8f3ad6bffcbbb2129a4a95bc12a0b9865b39f08d2c953ba5ce303a4a77743764", 1395, 526634),
    ("optimized_safe_bridge", "candidates/rust/variants/native_handle_lease_v1/py_bridge.c", SAFE_BRIDGE_SHA, SAFE_BRIDGE_BYTES, 526633),
    ("exact_v33_original_pass", "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-phase2-v33-rust-full-public-semantic-source-root-provenance-original-p0-v28-publication-receipt.json", "5204823a291ec01890913218582ff978cbe923dd5c787c8d6ae68a9790c43064", 12067, 526161),
    ("exact_v33_public_performance_receipt", "oracle/phase2/evidence/rust-corrected-public-performance-v4-v33-corrected-performance-run-001-publication-receipt.json", "db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3", 118943, 526289),
    ("exact_v33_public_performance_summary", "experiments/rust_corrected_public_performance_v4/v33-corrected-performance-run-001/public-416-performance-summary.raw.json", "7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef", 102598, 526288),
    ("historical_v30_static_audit", "oracle/phase2/evidence/rust-clean-non-delegation-v5-actual-source-audit.json", "a6962420b66e4e450abeddaef552a7f3d81e922ceb5254e00574609eabfc8203", 16427, 525089),
)

OWNER_BY_ROLE = {row[0]: row for row in STATIC_OWNERS}
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--build", "--run")
NOT_MEASURED = "NOT MEASURED"


class BuildFreezeError(Exception):
    """A complete V35 source owner, isolated gate, or actual build changed."""


def require(value: object, explanation: str) -> None:
    if value is not True:
        raise BuildFreezeError(explanation)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete immutable first-party bytes")
    return hashlib.sha256(raw).hexdigest()


def hash_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "require one independently pinned complete SHA-256: " + label)
    assert isinstance(value, str)
    return value


def commit_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 40
            and all(character in "0123456789abcdef" for character in value)
            and len(set(value)) > 1,
            "require one complete independently caller-pinned commit: " + label)
    assert isinstance(value, str)
    return value


def clean_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
        "ctypes", "subprocess", "socket", "threading", "multiprocessing",
        "concurrent.interpreters", "candidates", "rebar",
    )
    require(not any(name == root or name.startswith(root + ".")
                    for name in sys.modules for root in forbidden),
            "reject a candidate, regular-expression engine, loader, or worker")


class SourceWall:
    """Irreversible descriptor-only source isolation with no proposal metadata."""

    def __init__(self) -> None:
        require(len(OWNER_BY_ROLE) == len(STATIC_OWNERS),
                "every pinned source owner must have a distinct role")
        relatives = (SOURCE, PROTOCOL, CONTRACT) + tuple(row[1] for row in STATIC_OWNERS)
        require(len(relatives) == len(frozenset(relatives)),
                "reject duplicate or aliased pinned first-party source paths")
        self.allowed = frozenset(ROOT + "/" + path for path in relatives)
        self.dynamic = {
            ROOT + "/" + OWNER_BY_ROLE["anchor_transformer"][1]:
                OWNER_BY_ROLE["anchor_transformer"][2],
            ROOT + "/" + OWNER_BY_ROLE["compiler_transformer"][1]:
                OWNER_BY_ROLE["compiler_transformer"][2],
            ROOT + "/" + OWNER_BY_ROLE["combined_v2_source"][1]:
                OWNER_BY_ROLE["combined_v2_source"][2],
            ROOT + "/" + OWNER_BY_ROLE["literal_source"][1]:
                OWNER_BY_ROLE["literal_source"][2],
        }
        self.retired = ROOT + "/" + RETIRED_PROPOSAL
        self.live: set[int] = set()
        self.blocked: dict[str, int] = {}
        self.proposal_metadata_probes = 0
        self.proposal_content_opens = 0
        self.pending_name: str | None = None
        self.pending_code: object | None = None
        self.installed = False
        self._raw_open = os.open
        self._raw_read = os.read
        self._raw_fstat = os.fstat
        self._raw_stat = os.stat
        self._raw_lstat = os.lstat

    def deny(self, category: str, explanation: str) -> object:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise BuildFreezeError("the V35 irreversible source wall rejected " + explanation)

    def audit(self, event: str, arguments: tuple[object, ...]) -> None:
        if not self.installed:
            return
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            if type(path) is str and path == self.retired:
                self.deny("final_holdout", "content access to the invalidated V2 proposal")
            if type(flags) is not int:
                self.deny("foreign_read", "an unpinned descriptor or file mode")
            if flags & os.O_ACCMODE != os.O_RDONLY or flags & (
                os.O_CREAT | os.O_EXCL | os.O_TRUNC | os.O_APPEND
            ) or (getattr(os, "O_TMPFILE", 0)
                  and flags & os.O_TMPFILE == os.O_TMPFILE):
                self.deny("write", "a destructive, temporary, or writable source open")
            if type(mode) is str and any(character in mode for character in "wax+"):
                self.deny("write", "a writable source-mode file object")
            if type(path) is not str or path not in self.allowed:
                spelling = path.lower() if type(path) is str else "descriptor"
                if spelling.startswith("/tmp/"):
                    self.deny("private_root", "a private build root or installed runtime")
                if any(term in spelling for term in
                       ("holdout", "sealed", "hidden", "fixture", ".gz", "archive")):
                    self.deny("final_holdout", "a final case, hidden case, or archive")
                if spelling.endswith((".so", ".dll", ".dylib")):
                    self.deny("native", "an installed or private native binary")
                if "candidate" in spelling:
                    self.deny("candidate", "an unapproved candidate source or runtime")
                self.deny("foreign_read", "an unapproved source owner")
            if not flags & getattr(os, "O_NOFOLLOW", 0):
                self.deny("foreign_read", "a symlink-following source descriptor")
            return
        if event == "import":
            self.deny("candidate", "a late module, candidate, native, or regex import")
        if event == "compile":
            payload = arguments[0] if arguments else None
            filename = arguments[1] if len(arguments) > 1 else None
            if type(filename) is not str or filename != self.pending_name:
                self.deny("candidate", "compilation of unapproved executable source")
            if type(payload) is not bytes or digest(payload) != self.dynamic.get(filename):
                self.deny("candidate", "compilation of unauthenticated predecessor bytes")
            return
        if event == "exec":
            code = arguments[0] if arguments else None
            if code is not self.pending_code:
                self.deny("candidate", "execution of unapproved candidate or code")
            return
        if event.startswith(("subprocess.", "os.posix_spawn", "os.spawn", "os.exec",
                             "os.fork", "os.system", "_interpreters.", "threading.",
                             "_thread.", "cpython.PyInterpreterState_New")):
            self.deny("process", "a candidate, compiler, profiler, or worker")
        if event.startswith(("ctypes.", "os.dlopen", "marshal.loads")):
            self.deny("native", "a native binary, imported object, or code loader")
        if event.startswith("socket."):
            self.deny("network", "a socket or network request")
        if event.startswith(("os.mkdir", "os.rmdir", "os.remove", "os.unlink",
                             "os.rename", "os.replace", "os.chmod", "os.chown",
                             "os.link", "os.symlink", "os.truncate", "shutil.")):
            self.deny("write", "a workspace, candidate, or final-case mutation")
        if event in ("os.listdir", "os.scandir", "glob.glob"):
            self.deny("foreign_read", "a private root, workspace, or case enumeration")

    def read(self, descriptor: int, count: int, /) -> bytes:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign_read", "an inherited or unapproved source descriptor")
        return self._raw_read(descriptor, count)

    def fstat(self, descriptor: int, /) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("foreign_read", "metadata for an inherited or native descriptor")
        return self._raw_fstat(descriptor)

    def metadata(self, path: object, *args: object, **kwargs: object) -> os.stat_result:
        del path, args, kwargs
        return self.deny("final_holdout", "every direct metadata or proposal operation")

    def no_clock(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("clock", "a clock, timer, profiler, or sleep")

    def no_entropy(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("entropy", "randomness or generation of hidden cases")

    def no_direct_io(self, *_args: object, **_kwargs: object) -> object:
        return self.deny("foreign_read", "an unguarded Python file-object primitive")

    def install(self) -> None:
        require(self.installed is False, "the one-way V35 source wall was reused")
        sys.addaudithook(self.audit)
        self.installed = True
        os.read = self.read
        os.fstat = self.fstat
        os.stat = self.metadata
        os.lstat = self.metadata
        builtins.open = self.no_direct_io
        io.open = self.no_direct_io
        _io.open = self.no_direct_io
        if hasattr(os, "getrandom"):
            os.getrandom = self.no_entropy
        if hasattr(os, "urandom"):
            os.urandom = self.no_entropy
        for name in ("time", "time_ns", "clock_gettime", "clock_gettime_ns",
                     "clock_settime", "clock_settime_ns", "ctime", "gmtime",
                     "localtime", "strftime", "perf_counter", "perf_counter_ns",
                     "monotonic", "monotonic_ns", "process_time", "process_time_ns",
                     "thread_time", "thread_time_ns", "sleep"):
            if hasattr(time, name):
                setattr(time, name, self.no_clock)
        if hasattr(os, "times"):
            os.times = self.no_clock


def read_owner(wall: SourceWall, row: tuple[object, ...]) -> tuple[bytes, dict[str, object]]:
    require(type(row) is tuple and len(row) == 5, "require a complete frozen owner")
    role, relative, expected, count, inode = row
    require(type(role) is str and type(relative) is str and relative
            and not relative.startswith("/") and ".." not in relative.split("/")
            and type(count) is int and 0 < count <= MAX_OWNER_BYTES
            and type(inode) is int and inode > 0,
            "reject an altered first-party source owner identity")
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    wall.live.add(descriptor)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "a complete descriptor-pinned source owner changed: " + role)
        pieces: list[bytes] = []
        remaining = count
        while remaining:
            part = os.read(descriptor, min(remaining, 65536))
            require(type(part) is bytes and bool(part),
                    "a complete source owner was truncated: " + role)
            pieces.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a frozen source owner grew: " + role)
        after = os.fstat(descriptor)
        require(all(getattr(before, field) == getattr(after, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_nlink",
                                  "st_mtime_ns", "st_ctime_ns")),
                "a first-party owner changed during its complete descriptor read")
        raw = b"".join(pieces)
        require(digest(raw) == expected, "a complete source-owner digest changed: " + role)
        return raw, {"role": role, "path": relative, "sha256": expected,
                     "bytes": count, "device": before.st_dev, "inode": before.st_ino,
                     "mode": "0600", "uid": before.st_uid, "nlink": before.st_nlink}
    finally:
        wall.live.discard(descriptor)
        os.close(descriptor)


def live_owner(wall: SourceWall, role: str, relative: str,
               expected: str) -> tuple[bytes, dict[str, object]]:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject an unrelated or unauthenticated live V35 owner")
    hash_pin(expected, relative)
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    wall.live.add(descriptor)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
                and identity.st_nlink == 1 and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject a substituted independently pinned V35 live owner")
        pieces: list[bytes] = []
        remaining = identity.st_size
        while remaining:
            part = os.read(descriptor, min(65536, remaining))
            require(bool(part), "a complete caller-pinned V35 owner ended early")
            pieces.append(part)
            remaining -= len(part)
        require(os.read(descriptor, 1) == b"", "a caller-pinned V35 owner grew")
        after = os.fstat(descriptor)
        require(all(getattr(identity, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "a caller-pinned V35 owner changed during its descriptor read")
        raw = b"".join(pieces)
        require(digest(raw) == expected, "a caller-pinned V35 owner digest changed")
        return raw, {"role": role, "path": relative, "sha256": expected,
                     "bytes": identity.st_size, "device": identity.st_dev,
                     "inode": identity.st_ino, "mode": "0600", "uid": identity.st_uid,
                     "nlink": identity.st_nlink}
    finally:
        wall.live.discard(descriptor)
        os.close(descriptor)


def frozen_module(wall: SourceWall, role: str, payload: bytes) -> types.ModuleType:
    owner = OWNER_BY_ROLE[role]
    path = ROOT + "/" + owner[1]
    require(digest(payload) == owner[2] and len(payload) == owner[3]
            and wall.dynamic.get(path) == owner[2]
            and wall.pending_name is None and wall.pending_code is None,
            "execute only one complete independently pinned source transformer")
    name = "_rebar_v35_frozen_" + role
    require(name not in sys.modules, "reject a reused or substituted source transformer")
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    wall.pending_name = path
    try:
        code = compile(payload, path, "exec", dont_inherit=True)
        wall.pending_code = code
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    finally:
        wall.pending_name = None
        wall.pending_code = None
    clean_imports()
    return module


def public_document(parser: types.ModuleType, payload: bytes,
                    label: str) -> dict[str, object]:
    value = parser.StrictJSON(payload).document()
    require(type(value) is dict, "require one complete public JSON object: " + label)
    return value


def extract_adapter_literals(source: bytes) -> dict[str, bytes]:
    required = ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK", "OLD_ERROR_BLOCK",
                "V2_ERROR_BLOCK", "OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK",
                "V3_PATTERN_BLOCK")
    result: dict[str, bytes] = {}
    for name in required:
        marker = name.encode("ascii") + b' = b"""'
        require(source.count(marker) == 1,
                "require exactly one authenticated adapter repair literal: " + name)
        first = source.index(marker) + len(marker)
        last = source.find(b'"""', first)
        require(last >= first, "an authenticated adapter repair literal was truncated")
        result[name] = source[first:last]
    return result


def derive_adapter(original: bytes, repair: bytes) -> bytes:
    require(digest(original) == OWNER_BY_ROLE["original_adapter"][2]
            and len(original) == OWNER_BY_ROLE["original_adapter"][3]
            and digest(repair) == OWNER_BY_ROLE["adapter_repair_source"][2],
            "authenticate both complete immutable adapter-repair inputs")
    blocks = extract_adapter_literals(repair)
    fixed = original
    for before, after in (
        ("OLD_FLAG_BLOCK", "V2_FLAG_BLOCK"),
        ("OLD_ERROR_BLOCK", "V2_ERROR_BLOCK"),
        ("OLD_PATTERN_BLOCK", "V2_PATTERN_BLOCK"),
        ("V2_PATTERN_BLOCK", "V3_PATTERN_BLOCK"),
    ):
        previous, replacement = blocks[before], blocks[after]
        require(fixed.count(previous) == 1 and fixed.count(replacement) == 0,
                "each complete historical adapter repair must apply exactly once")
        fixed = fixed.replace(previous, replacement, 1)
    require(len(fixed) == BASE_ADAPTER_BYTES and digest(fixed) == BASE_ADAPTER_SHA,
            "reconstruct the exact independently frozen corrected public adapter")
    return fixed


def validate_bridge(payload: bytes, correction: dict[str, object],
                    application: dict[str, object]) -> None:
    legacy = OWNER_BY_ROLE["no_introspection_bridge"]
    require(len(payload) == legacy[3] and digest(payload) == legacy[2],
            "require the exact historical NO-EXTERNAL-INTROSPECTION bridge")
    require(correction.get("target_path") == legacy[1]
            and correction.get("target_sha256") == legacy[2]
            and correction.get("target_bytes") == legacy[3]
            and correction.get("deleted_private_function") == "rust_bound_get_signature"
            and correction.get("deleted_private_getset") == "__signature__"
            and correction.get("public_pattern_methods_use_native_descriptors") is True
            and correction.get("capture_clamp_correction_retained") is True,
            "preserve every independently frozen exact private-introspection correction")
    require(application.get("schema")
            == "rebar-owned-rust-no-external-introspection-v1-source-freeze-root-materialization"
            and application.get("status")
            == "PASS; EXACT PRIVATE INTROSPECTION REMOVED; NOT BUILT; NOT RUN"
            and application.get("source_sha256")
            == OWNER_BY_ROLE["no_introspection_source"][2]
            and application.get("protocol_sha256")
            == OWNER_BY_ROLE["no_introspection_protocol"][2]
            and application.get("contract_sha256")
            == OWNER_BY_ROLE["no_introspection_contract"][2]
            and application.get("target_path") == legacy[1]
            and application.get("target_sha256") == legacy[2]
            and application.get("target_bytes") == legacy[3]
            and application.get("capture_clamp_preserved") is True
            and application.get("public_native_descriptors_preserved") is True,
            "authenticate the exact exclusively materialized safe bridge receipt")
    require(b"rust_bound_get_signature" not in payload
            and b'PyImport_ImportModule("inspect")' not in payload
            and b'"__signature__"' not in payload
            and payload.count(b"PyDescr_NewMethod(") >= 1
            and payload.count(b"Py_CLEAR(method->signature)") == 2
            and payload.count(b"Py_VISIT(method->signature)") == 1,
            "reject any restored private introspection getter or lost native descriptor")
    for forbidden in (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")',
                      b'PyImport_ImportModule("inspect")', b"dlopen(", b"pcre2",
                      b"oniguruma", b"regex.compile"):
        require(forbidden not in payload,
                "reject delegated regular-expression matching in the complete safe bridge")


def validate_complete_bridge(parser: types.ModuleType,
                             originals: dict[str, bytes]) -> dict[str, object]:
    frozen = public_document(parser, originals["complete_semantic_contract"],
                             "complete committed semantic-correction V2 contract")
    application = public_document(parser, originals["complete_semantic_application"],
                                  "actual exclusively materialized V2 correction")
    correction = frozen.get("exact_complete_semantic_correction")
    partition = frozen.get("exact_disjoint_original_failure_partition")
    predecessors = frozen.get("authenticated_public_predecessors")
    require(frozen.get("schema")
            == "rebar-owned-rust-complete-semantic-correction-v2-source-freeze"
            and frozen.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["complete_semantic_source"][2]
            and frozen.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["complete_semantic_protocol"][2]
            and type(correction) is dict and type(partition) is dict
            and type(predecessors) is dict,
            "authenticate the independently committed complete semantic V2 triple")
    require(correction.get("input_path") == OWNER_BY_ROLE["expand_bridge"][1]
            and correction.get("input_sha256") == OWNER_BY_ROLE["expand_bridge"][2]
            and correction.get("input_bytes") == OWNER_BY_ROLE["expand_bridge"][3]
            and correction.get("target_path") == OWNER_BY_ROLE["complete_semantic_bridge"][1]
            and correction.get("target_sha256") == BASE_BRIDGE_SHA
            and correction.get("target_bytes") == BASE_BRIDGE_BYTES
            and correction.get("source_delta_bytes") == 189
            and correction.get("existing_expansion_correction_sites_preserved") == 2
            and correction.get("new_substitution_order_correction_sites") == 4
            and correction.get("noncallback_replacement_validated_before_subject") is True
            and correction.get("duplicate_subject_release_precluded") is True
            and correction.get("capture_clamp_correction_retained") is True
            and correction.get("no_external_introspection_correction_retained") is True
            and correction.get("stdlib_matching_delegation_added") is False
            and correction.get("external_regex_dependency_added") is False,
            "preserve clamp, no introspection, replacement order, and exact expand probes")
    require(partition.get("total_disjoint_original_failure_count") == 1352
            and partition.get("substitution_v2_failure_count") == 240
            and partition.get("shape_v2_ordering_failure_count") == 1024
            and partition.get("shape_v2_trailing_probe_failure_count") == 56
            and partition.get("shape_v2_malformed_expansion_failure_count") == 32
            and partition.get("shape_v2_failure_count") == 1112
            and partition.get("separate_ordering_probe_overlap_count") == 32
            and partition.get("overlap_included_in_total") is False,
            "preserve the exact disjoint 240+1024+56+32 original failure partition")
    for family, prefix in (("ordering", "ordering"), ("expand", "expand")):
        for kind in ("source", "protocol", "contract", "application"):
            require(predecessors.get(family + "_" + kind + "_sha256")
                    == OWNER_BY_ROLE[prefix + "_" + kind][2],
                    "authenticate every complete semantic predecessor: "
                    + family + "/" + kind)
    failed = public_document(parser, originals["complete_v1_failure"],
                             "immutable failed first root composition attempt")
    failed_contract = frozen.get("immutable_v1_preapplication_failure")
    require(failed.get("status") == "FAIL"
            and failed.get("candidate_source_variant_created") is False
            and type(failed_contract) is dict
            and failed_contract.get("receipt_sha256")
            == OWNER_BY_ROLE["complete_v1_failure"][2]
            and failed_contract.get("candidate_source_opened") is False
            and failed_contract.get("candidate_target_created") is False
            and failed_contract.get("v2_candidate_input_authorization_deferred_until_all_controls")
            is True,
            "preserve the immutable safe preapplication V1 failure")
    require(application.get("schema")
            == "rebar-owned-rust-complete-semantic-correction-v2-source-freeze-root-materialization"
            and application.get("status")
            == "PASS; ALL ORIGINAL FAILURES MODELED; NOT BUILT; NOT RUN"
            and application.get("source_sha256")
            == OWNER_BY_ROLE["complete_semantic_source"][2]
            and application.get("protocol_sha256")
            == OWNER_BY_ROLE["complete_semantic_protocol"][2]
            and application.get("contract_sha256")
            == OWNER_BY_ROLE["complete_semantic_contract"][2]
            and application.get("target_path")
            == OWNER_BY_ROLE["complete_semantic_bridge"][1]
            and application.get("target_sha256") == BASE_BRIDGE_SHA
            and application.get("target_bytes") == BASE_BRIDGE_BYTES
            and application.get("complete_disjoint_original_failure_count") == 1352
            and application.get("substitution_v2_failure_count") == 240
            and application.get("shape_v2_failure_count") == 1112
            and application.get("separate_ordering_probe_overlap_count") == 32
            and application.get("actual_root_hostile_controls_rejected") == 107
            and application.get("candidate_input_authorized_after_all_source_controls")
            is True
            and application.get("replacement_validated_before_subject") is True
            and application.get("existing_expansion_correction_preserved") is True
            and application.get("capture_clamp_preserved") is True
            and application.get("no_external_introspection_preserved") is True
            and application.get("effects", {}).get("candidate_executions") == 0
            and application.get("effects", {}).get("compiler_processes_started") == 0
            and application.get("effects", {}).get("clock_samples") == 0,
            "authenticate the actual deferred-authority exclusively materialized bridge")
    payload = originals["complete_semantic_bridge"]
    require(len(payload) == BASE_BRIDGE_BYTES and digest(payload) == BASE_BRIDGE_SHA
            and b"rust_bound_get_signature" not in payload
            and b'PyImport_ImportModule("inspect")' not in payload
            and b'"__signature__"' not in payload
            and payload.count(b"PyDescr_NewMethod(") >= 1
            and payload.count(b'"bad escape (end of pattern)"') >= 1
            and payload.count(b"PyObject *validation_arguments[3]") == 1
            and payload.count(b"if (subject_acquired) rust_subject_release(&subject);") == 2,
            "require the exact no-inspect, safe-clamp, order-and-expand corrected C bridge")
    for forbidden in (b'PyImport_ImportModule("re")', b'PyImport_ImportModule("_sre")',
                      b'PyImport_ImportModule("inspect")', b"dlopen(", b"pcre2",
                      b"oniguruma", b"regex.compile"):
        require(forbidden not in payload,
                "reject external matching delegation in the complete V2 bridge")
    return {"source_sha256": OWNER_BY_ROLE["complete_semantic_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["complete_semantic_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["complete_semantic_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["complete_semantic_application"][2],
            "bridge_sha256": BASE_BRIDGE_SHA, "bridge_bytes": BASE_BRIDGE_BYTES,
            "exact_disjoint_original_failure_partition": partition,
            "immutable_first_failed_root_attempt_sha256": OWNER_BY_ROLE["complete_v1_failure"][2],
            "candidate_correctness_after_correction": NOT_MEASURED,
            "candidate_matching": "NOT RUN", "candidate_qualified": False}


def validate_full_public_sources(parser: types.ModuleType,
                                 originals: dict[str, bytes]) -> dict[str, object]:
    scanner = public_document(parser, originals["scanner_bridge_contract"],
                              "independently frozen complete scanner bridge")
    scanner_application = public_document(parser, originals["scanner_bridge_application"],
                                          "actual complete scanner bridge materialization")
    scanner_correction = scanner.get("exact_complete_scanner_bridge_composition")
    scanner_partition = scanner.get("exact_targeted_public_partition")
    require(scanner.get("schema") == "rebar-owned-rust-complete-scanner-bridge-v1-source-freeze"
            and scanner.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["scanner_bridge_source"][2]
            and scanner.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["scanner_bridge_protocol"][2]
            and type(scanner_correction) is dict
            and scanner_correction.get("complete_input_sha256") == BASE_BRIDGE_SHA
            and scanner_correction.get("complete_input_bytes") == BASE_BRIDGE_BYTES
            and scanner_correction.get("target_sha256") == BRIDGE_SHA
            and scanner_correction.get("target_bytes") == BRIDGE_BYTES
            and scanner_correction.get("safe_capture_clamp_retained") is True
            and scanner_correction.get("no_external_introspection_retained") is True
            and scanner_correction.get("complete_substitution_core_byte_identical") is True
            and scanner_correction.get("complete_match_expand_byte_identical") is True
            and type(scanner_partition) is dict
            and scanner_partition.get("gross_targeted_public_mismatch_count") == 470
            and scanner_partition.get("named_unicode_comment_overlap_row_count") == 15
            and scanner_partition.get("scanner_only_independent_public_improvement_count")
            == 455,
            "authenticate all 470 scanner rows, 15 overlaps, and prior private corrections")
    require(scanner_application.get("schema")
            == "rebar-owned-rust-complete-scanner-bridge-v1-root-actual-application-receipt"
            and scanner_application.get("status") == "PASS"
            and scanner_application.get("controller_source_sha256")
            == OWNER_BY_ROLE["scanner_bridge_source"][2]
            and scanner_application.get("protocol_sha256")
            == OWNER_BY_ROLE["scanner_bridge_protocol"][2]
            and scanner_application.get("contract_sha256")
            == OWNER_BY_ROLE["scanner_bridge_contract"][2]
            and scanner_application.get("target_path") == OWNER_BY_ROLE["scanner_bridge"][1]
            and scanner_application.get("target_sha256") == BRIDGE_SHA
            and scanner_application.get("target_bytes") == BRIDGE_BYTES
            and scanner_application.get("complete_original_modeled_correction_count") == 1352
            and scanner_application.get("public_scanner_gross_modeled_correction_count") == 470
            and scanner_application.get("public_scanner_overlap_modeled_count") == 15
            and scanner_application.get("public_scanner_independent_modeled_correction_count")
            == 455
            and scanner_application.get("candidate_executions") == 0,
            "authenticate the actual exclusively materialized complete scanner bridge")

    scoped = public_document(parser, originals["scoped_engine_contract"],
                             "independently frozen scoped-unicode combined engine")
    scoped_application = public_document(parser, originals["scoped_engine_application"],
                                         "actual scoped combined engine materialization")
    scoped_correction = scoped.get("first_party_source_composition")
    scoped_model = scoped.get("independent_synthetic_differential_semantics")
    require(scoped.get("schema") == "rebar-owned-rust-combined-scoped-unicode-engine-v1-source-freeze"
            and scoped.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["scoped_engine_source"][2]
            and scoped.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["scoped_engine_protocol"][2]
            and type(scoped_correction) is dict
            and scoped_correction.get("combined_parent", {}).get("sha256") == BASE_ENGINE_SHA
            and scoped_correction.get("combined_corrected", {}).get("sha256")
                == SCOPED_ENGINE_SHA
            and scoped_correction.get("combined_corrected", {}).get("bytes")
                == SCOPED_ENGINE_BYTES
            and scoped_correction.get("combined_search_preserved", {}).get("sha256")
            == SEARCH_SHA
            and scoped_correction.get("mandatory_anchor_search_preserved") is True
            and scoped_correction.get("compiler_allocation_fastpath_preserved") is True
            and scoped_correction.get("external_rust_dependency_count") == 0
            and type(scoped_model) is dict
            and scoped_model.get("bounded_differential_case_count") == 17442
            and scoped_model.get("previously_unsound_cases_repaired") == 1882,
            "preserve the scoped correction, mandatory anchor, compiler fast path, and 17442 proofs")
    require(scoped_application.get("schema")
            == "rebar-owned-rust-combined-scoped-unicode-engine-v1-root-actual-application-receipt"
            and scoped_application.get("status") == "APPLIED"
            and scoped_application.get("controller_source_sha256")
            == OWNER_BY_ROLE["scoped_engine_source"][2]
            and scoped_application.get("protocol_sha256")
            == OWNER_BY_ROLE["scoped_engine_protocol"][2]
            and scoped_application.get("contract_sha256")
            == OWNER_BY_ROLE["scoped_engine_contract"][2]
            and scoped_application.get("target_path") == OWNER_BY_ROLE["scoped_engine"][1]
            and scoped_application.get("target_sha256") == SCOPED_ENGINE_SHA
            and scoped_application.get("target_bytes") == SCOPED_ENGINE_BYTES
            and scoped_application.get("targeted_public_mismatch_case_count") == 2
            and scoped_application.get("mandatory_anchor_search_preserved") is True
            and scoped_application.get("compiler_allocation_fastpath_preserved") is True
            and scoped_application.get("external_rust_dependency_count") == 0
            and scoped_application.get("candidate_executions") == 0,
            "authenticate the actual exclusive 7412 optimized/scoped Rust engine")

    failed_comment = public_document(parser, originals["comment_adapter_v1_failure"],
                                     "immutable rejected corrected-comment V1 root attempt")
    require(failed_comment.get("schema")
            == "rebar-owned-rust-corrected-comment-adapter-v1-root-preapplication-failure"
            and failed_comment.get("status") == "FAIL"
            and failed_comment.get("candidate_target_created") is False
            and failed_comment.get("candidate_source_materialized") is False
            and failed_comment.get("candidate_executions") == 0,
            "preserve the safe immutable premature-authorization V1 adapter failure")

    comment = public_document(parser, originals["comment_adapter_v2_contract"],
                              "complete corrected comment-adapter V2 frozen contract")
    comment_application = public_document(parser,
                                          originals["comment_adapter_v2_application"],
                                          "actual corrected comment-adapter V2 materialization")
    require(comment.get("schema") == "rebar-owned-rust-corrected-comment-adapter-v2-source-freeze"
            and comment.get("source_sha256") == OWNER_BY_ROLE["comment_adapter_v2_source"][2]
            and comment.get("protocol_sha256") == OWNER_BY_ROLE["comment_adapter_v2_protocol"][2]
            and comment.get("target_path") == OWNER_BY_ROLE["comment_adapter"][1]
            and comment.get("target_sha256") == ADAPTER_SHA
            and comment.get("target_bytes") == ADAPTER_BYTES
            and comment.get("private_corrected_adapter_sha256") == BASE_ADAPTER_SHA
            and comment.get("private_corrected_adapter_bytes") == BASE_ADAPTER_BYTES
            and comment.get("independent_comment_only_mismatch_count") == 297
            and comment.get("scanner_overlap_count") == 15
            and comment.get("substitution_overlap_count") == 12
            and comment.get("targeted_public_mismatch_count") == 324
            and comment.get("comment_repair_count") == 3,
            "preserve all 297 independent comment fixes and 15/12 explicitly separate overlaps")
    require(comment_application.get("schema")
            == "rebar-owned-rust-corrected-comment-adapter-v2-source-freeze-root-materialization"
            and comment_application.get("status")
            == "PASS; EXACT SEVEN CORRECTIONS; NOT BUILT; NOT RUN"
            and comment_application.get("source_sha256")
            == OWNER_BY_ROLE["comment_adapter_v2_source"][2]
            and comment_application.get("protocol_sha256")
            == OWNER_BY_ROLE["comment_adapter_v2_protocol"][2]
            and comment_application.get("contract_sha256")
            == OWNER_BY_ROLE["comment_adapter_v2_contract"][2]
            and comment_application.get("target_path") == OWNER_BY_ROLE["comment_adapter"][1]
            and comment_application.get("target_sha256") == ADAPTER_SHA
            and comment_application.get("target_bytes") == ADAPTER_BYTES
            and comment_application.get("independent_comment_only_mismatch_count") == 297
            and comment_application.get("scanner_overlap_count") == 15
            and comment_application.get("substitution_overlap_count") == 12
            and comment_application.get("targeted_public_mismatch_count") == 324
            and comment_application.get("effects", {}).get("candidate_executions") == 0
            and comment_application.get("effects", {}).get("proposals_opened") == 0,
            "authenticate the actual exclusively created 34039-byte V2 corrected adapter")
    bridge = originals["scanner_bridge"]
    engine = originals["scoped_engine"]
    adapter = originals["comment_adapter"]
    require(digest(bridge) == BRIDGE_SHA and len(bridge) == BRIDGE_BYTES
            and digest(engine) == SCOPED_ENGINE_SHA
            and len(engine) == SCOPED_ENGINE_BYTES
            and digest(adapter) == ADAPTER_SHA and len(adapter) == ADAPTER_BYTES
            and b"rust_bound_get_signature" not in bridge
            and b'PyImport_ImportModule("inspect")' not in bridge
            and b"PyLong_AsInt(" in bridge
            and b"has_scoped_category_prefix(root, global_flags)" in engine,
            "authenticate all three complete materialized first-party public-semantic overlays")
    return {"scanner_bridge_source_sha256": OWNER_BY_ROLE["scanner_bridge_source"][2],
            "scanner_bridge_protocol_sha256": OWNER_BY_ROLE["scanner_bridge_protocol"][2],
            "scanner_bridge_contract_sha256": OWNER_BY_ROLE["scanner_bridge_contract"][2],
            "scanner_bridge_application_sha256":
                OWNER_BY_ROLE["scanner_bridge_application"][2],
            "scoped_engine_source_sha256": OWNER_BY_ROLE["scoped_engine_source"][2],
            "scoped_engine_protocol_sha256": OWNER_BY_ROLE["scoped_engine_protocol"][2],
            "scoped_engine_contract_sha256": OWNER_BY_ROLE["scoped_engine_contract"][2],
            "scoped_engine_application_sha256":
                OWNER_BY_ROLE["scoped_engine_application"][2],
            "comment_adapter_source_sha256": OWNER_BY_ROLE["comment_adapter_v2_source"][2],
            "comment_adapter_protocol_sha256":
                OWNER_BY_ROLE["comment_adapter_v2_protocol"][2],
            "comment_adapter_contract_sha256": OWNER_BY_ROLE["comment_adapter_v2_contract"][2],
            "comment_adapter_application_sha256":
                OWNER_BY_ROLE["comment_adapter_v2_application"][2],
            "immutable_comment_v1_failure_sha256":
                OWNER_BY_ROLE["comment_adapter_v1_failure"][2],
            "targeted_public_mismatch_partition": {
                "scanner": 470, "substitution": 376,
                "comment": 297, "scoped_unicode": 2,
            },
            "scanner_comment_overlap_count": 15,
            "substitution_comment_overlap_count": 12,
            "gross_comment_modeled_count": 324,
            "candidate_executions": 0, "candidate_correctness": NOT_MEASURED}


def validate_exact_literal_sources(parser: types.ModuleType,
                                  literal: types.ModuleType,
                                  originals: dict[str, bytes]) -> dict[str, object]:
    freeze = public_document(parser, originals["literal_contract"],
                             "independently frozen exact-literal source experiment")
    applied = public_document(parser, originals["literal_application"],
                              "actual exclusive exact-literal source materialization")
    composition = freeze.get("first_party_source_composition")
    synthetic = freeze.get("independent_synthetic_semantics")
    require(freeze.get("schema")
                == "rebar-owned-rust-exact-literal-fastpath-v1-source-freeze"
            and freeze.get("source", {}).get("sha256")
                == OWNER_BY_ROLE["literal_source"][2]
            and freeze.get("protocol", {}).get("sha256")
                == OWNER_BY_ROLE["literal_protocol"][2]
            and type(composition) is dict and type(synthetic) is dict
            and composition.get("optimized_scoped_parent_sha256")
                == SCOPED_ENGINE_SHA
            and composition.get("optimized_scoped_parent_bytes")
                == SCOPED_ENGINE_BYTES
            and composition.get("target_path") == OWNER_BY_ROLE["literal_engine"][1]
            and composition.get("target_sha256") == ENGINE_SHA
            and composition.get("target_bytes") == ENGINE_BYTES
            and composition.get("unchanged_search_source_sha256") == SEARCH_SHA
            and composition.get("source_delta_bytes") == 4783
            and composition.get("plan_minimum_bytes") == 2
            and composition.get("plan_maximum_bytes") == 32
            and composition.get("case_sensitive_only") is True
            and composition.get("locale_sensitive_excluded") is True
            and composition.get("capturing_patterns_excluded") is True
            and composition.get("nonliteral_patterns_excluded") is True
            and composition.get("empty_and_singleton_patterns_excluded") is True
            and composition.get("unicode_two_and_four_byte_storage_excluded") is True
            and composition.get("existing_first_party_bounded_memchr_reused") is True
            and composition.get("matching_mode_count") == 3
            and composition.get("nonoverlapping_collection_retained") is True
            and composition.get("exact_scoped_unicode_correction_retained") is True
            and composition.get("mandatory_anchor_search_retained") is True
            and composition.get("compiler_allocation_fastpath_retained") is True
            and composition.get("external_regex_dependency_count") == 0
            and composition.get("stdlib_matching_delegation_count") == 0
            and synthetic.get("bounded_match_case_count") == 1009125
            and synthetic.get("bounded_collection_case_count") == 1345500
            and synthetic.get("bounded_window_count") == 336375
            and synthetic.get("successful_match_case_count") == 3855
            and synthetic.get("high_byte_case_count") == 951501
            and synthetic.get("excluded_expression_family_count") == 11
            and synthetic.get("candidate_executed") is False
            and synthetic.get("external_matcher_imported") is False,
            "preserve the exact complete first-party literal proof and all safe exclusions")
    created = applied.get("created", {})
    owner = created.get("engine", {}) if type(created) is dict else {}
    require(applied.get("schema")
                == "rebar-owned-rust-exact-literal-fastpath-v1-source-freeze-application"
            and applied.get("status") == "APPLIED"
            and applied.get("source_sha256") == OWNER_BY_ROLE["literal_source"][2]
            and applied.get("protocol_sha256") == OWNER_BY_ROLE["literal_protocol"][2]
            and applied.get("contract_sha256") == OWNER_BY_ROLE["literal_contract"][2]
            and owner.get("path") == OWNER_BY_ROLE["literal_engine"][1]
            and owner.get("sha256") == ENGINE_SHA
            and owner.get("bytes") == ENGINE_BYTES
            and owner.get("device") == DEVICE
            and owner.get("inode") == OWNER_BY_ROLE["literal_engine"][4]
            and owner.get("mode") == "0600" and owner.get("nlink") == 1
            and owner.get("exclusive_no_follow") is True
            and owner.get("fsync_completed") is True
            and applied.get("bounded_match_case_count") == 1009125
            and applied.get("bounded_collection_case_count") == 1345500
            and applied.get("external_regex_dependency_count") == 0
            and applied.get("stdlib_matching_delegation_count") == 0
            and applied.get("canonical_source_mutations") == 0
            and applied.get("candidate_executions") == 0
            and applied.get("proposal_files_opened") == 0,
            "authenticate the exact exclusively materialized first-party literal engine")
    require(literal.SCHEMA
                == "rebar-owned-rust-exact-literal-fastpath-v1-source-freeze"
            and literal.BASE_SHA256 == SCOPED_ENGINE_SHA
            and literal.BASE_BYTES == SCOPED_ENGINE_BYTES
            and literal.TARGET_SHA256 == ENGINE_SHA
            and literal.TARGET_BYTES == ENGINE_BYTES
            and callable(literal.derive_engine),
            "execute only the independently authenticated first-party literal transformer")
    derived = literal.derive_engine(originals["scoped_engine"])
    require(derived == originals["literal_engine"]
            and digest(derived) == ENGINE_SHA and len(derived) == ENGINE_BYTES
            and b"ExactLiteralPlan::new(&root, parser.groups)" in derived
            and b"search::next_singleton(values, needle[final_offset], cursor, stop)"
                in derived
            and b"has_scoped_category_prefix(root, global_flags)" in derived,
            "independently reproduce the exact 194276-byte optimized first-party engine")
    return {"source_sha256": OWNER_BY_ROLE["literal_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["literal_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["literal_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["literal_application"][2],
            "parent_engine_sha256": SCOPED_ENGINE_SHA,
            "parent_engine_bytes": SCOPED_ENGINE_BYTES,
            "engine_sha256": ENGINE_SHA, "engine_bytes": ENGINE_BYTES,
            "source_delta_bytes": 4783,
            "bounded_match_case_count": 1009125,
            "bounded_collection_case_count": 1345500,
            "external_regex_dependency_count": 0,
            "stdlib_matching_delegation_count": 0,
            "candidate_correctness": NOT_MEASURED,
            "performance": NOT_MEASURED}


def validate_optimized_safe_bridge(parser: types.ModuleType,
                                   originals: dict[str, bytes]) -> dict[str, object]:
    literal = public_document(parser, originals["literal_bridge_contract"],
                              "frozen independently written literal bridge acceleration")
    literal_applied = public_document(parser, originals["literal_bridge_application"],
                                      "actual exclusive accelerated bridge source")
    lease = public_document(parser, originals["handle_lease_contract"],
                            "frozen native-engine ownership and callback lease proof")
    lease_applied = public_document(parser, originals["handle_lease_application"],
                                    "actual exclusive ownership-safe accelerated bridge")
    literal_composition = literal.get("first_party_source_composition")
    literal_semantics = literal.get("independent_synthetic_semantics")
    require(literal.get("schema")
            == "rebar-owned-rust-literal-bridge-fastpath-v1-source-freeze"
            and literal.get("source", {}).get("sha256")
                == OWNER_BY_ROLE["literal_bridge_source"][2]
            and literal.get("protocol", {}).get("sha256")
                == OWNER_BY_ROLE["literal_bridge_protocol"][2]
            and type(literal_composition) is dict
            and type(literal_semantics) is dict
            and literal_composition.get("base_bridge_sha256") == BRIDGE_SHA
            and literal_composition.get("base_bridge_bytes") == BRIDGE_BYTES
            and literal_composition.get("target_path") == OWNER_BY_ROLE["literal_bridge"][1]
            and literal_composition.get("target_sha256") == LITERAL_BRIDGE_SHA
            and literal_composition.get("target_bytes") == LITERAL_BRIDGE_BYTES
            and literal_composition.get("independent_exact_literal_engine_sha256") == ENGINE_SHA
            and literal_composition.get("adaptive_first_or_last_anchor") is True
            and literal_composition.get("additional_python_rust_boundary_crossing_count") == 0
            and literal_composition.get("external_regex_dependency_count") == 0
            and literal_composition.get("stdlib_matching_delegation_count") == 0
            and literal_semantics.get("bounded_matching_case_count") == 1009125
            and literal_semantics.get("bounded_collection_case_count") == 1345500,
            "authenticate exact first-party bounded literal bridge source and synthetic proof")
    require(literal_applied.get("status") == "APPLIED"
            and literal_applied.get("source_sha256")
                == OWNER_BY_ROLE["literal_bridge_source"][2]
            and literal_applied.get("protocol_sha256")
                == OWNER_BY_ROLE["literal_bridge_protocol"][2]
            and literal_applied.get("contract_sha256")
                == OWNER_BY_ROLE["literal_bridge_contract"][2]
            and literal_applied.get("created", {}).get("path")
                == OWNER_BY_ROLE["literal_bridge"][1]
            and literal_applied.get("created", {}).get("sha256") == LITERAL_BRIDGE_SHA
            and literal_applied.get("created", {}).get("bytes") == LITERAL_BRIDGE_BYTES
            and literal_applied.get("created", {}).get("inode")
                == OWNER_BY_ROLE["literal_bridge"][4]
            and literal_applied.get("candidate_executions") == 0,
            "authenticate the actually materialized literal bridge and its exact inode")

    lease_composition = lease.get("first_party_source_composition")
    lease_semantics = lease.get("independent_synthetic_lifetime_semantics")
    require(lease.get("schema") == "rebar-owned-rust-native-handle-lease-v1-source-freeze"
            and lease.get("source", {}).get("sha256") == OWNER_BY_ROLE["handle_lease_source"][2]
            and lease.get("protocol", {}).get("sha256")
                == OWNER_BY_ROLE["handle_lease_protocol"][2]
            and type(lease_composition) is dict and type(lease_semantics) is dict
            and lease_composition.get("base_bridge_sha256") == LITERAL_BRIDGE_SHA
            and lease_composition.get("base_bridge_bytes") == LITERAL_BRIDGE_BYTES
            and lease_composition.get("target_path") == OWNER_BY_ROLE["optimized_safe_bridge"][1]
            and lease_composition.get("target_sha256") == SAFE_BRIDGE_SHA
            and lease_composition.get("target_bytes") == SAFE_BRIDGE_BYTES
            and lease_composition.get("independent_exact_literal_engine_sha256") == ENGINE_SHA
            and lease_composition.get("unchanged_corrected_adapter_sha256") == ADAPTER_SHA
            and lease_composition.get("private_capsule_destructor_owns_native_engine") is True
            and lease_composition.get("validated_native_handle_extraction_site_count") == 12
            and lease_composition.get("raw_integer_pointer_conversion_site_count") == 0
            and lease_composition.get("active_dispatch_strong_owner_lease") is True
            and lease_composition.get("callback_substitution_strong_owner_lease") is True
            and lease_composition.get("scanner_and_finditer_independent_owner_lease") is True
            and lease_composition.get("iterator_capsule_gc_referent_exposed") is False
            and lease_composition.get("existing_literal_acceleration_preserved") is True
            and lease_composition.get("added_source_external_regex_dependency_count") == 0
            and lease_composition.get("added_source_stdlib_matching_delegation_count") == 0
            and lease_composition.get("current_exact_static_source_and_elf_non_delegation")
                == "NOT ESTABLISHED"
            and lease_composition.get("current_exact_live_runtime_non_delegation")
                == "NOT ESTABLISHED"
            and lease_semantics.get("operation_callback_sequence_count") == 32768
            and lease_semantics.get("callback_finalization_case_count") == 103184
            and lease_semantics.get("scanner_and_finditer_lifetime_case_count") == 20656
            and lease_semantics.get("capsule_destructor_invocations_per_engine") == 1
            and lease_semantics.get("iterator_capsule_gc_traverse_visits") == 0,
            "authenticate complete source-only ownership, finalization, and scanner proofs")
    require(lease_applied.get("status") == "APPLIED"
            and lease_applied.get("source_sha256") == OWNER_BY_ROLE["handle_lease_source"][2]
            and lease_applied.get("protocol_sha256")
                == OWNER_BY_ROLE["handle_lease_protocol"][2]
            and lease_applied.get("contract_sha256")
                == OWNER_BY_ROLE["handle_lease_contract"][2]
            and lease_applied.get("created", {}).get("path")
                == OWNER_BY_ROLE["optimized_safe_bridge"][1]
            and lease_applied.get("created", {}).get("sha256") == SAFE_BRIDGE_SHA
            and lease_applied.get("created", {}).get("bytes") == SAFE_BRIDGE_BYTES
            and lease_applied.get("created", {}).get("inode")
                == OWNER_BY_ROLE["optimized_safe_bridge"][4]
            and lease_applied.get("base_bridge_sha256") == LITERAL_BRIDGE_SHA
            and lease_applied.get("candidate_executions") == 0
            and lease_applied.get("current_exact_static_source_and_elf_non_delegation")
                == "NOT ESTABLISHED"
            and lease_applied.get("current_exact_live_runtime_non_delegation")
                == "NOT ESTABLISHED",
            "authenticate the actual root-materialized ownership-safe accelerated bridge")
    payload = originals["optimized_safe_bridge"]
    require(len(payload) == SAFE_BRIDGE_BYTES and digest(payload) == SAFE_BRIDGE_SHA
            and payload.count(b"rust_literal_next_contiguous(") == 3
            and payload.count(b"static void rust_native_handle_destructor(") == 1
            and payload.count(b"rust_native_handle_owner(handle)") == 2
            and payload.count(b"iterator->handle_owner = Py_NewRef(handle_owner);") == 1
            and payload.count(b"Py_CLEAR(iterator->handle_owner);") == 1
            and payload.count(b"Py_VISIT(iterator->handle_owner)") == 0
            and payload.count(b"PyLong_AsVoidPtr(") == 0
            and payload.count(b"PyLong_FromVoidPtr(") == 0
            and b"rust_bound_get_signature" not in payload
            and b'PyImport_ImportModule("inspect")' not in payload
            and b'PyImport_ImportModule("re")' not in payload
            and b'PyImport_ImportModule("_sre")' not in payload,
            "retain exact literal acceleration, native ownership, and no-inspection bridge")

    exact_original = public_document(parser, originals["exact_v33_original_pass"],
                                     "complete original exact-V33 correctness receipt")
    exact_public = public_document(parser, originals["v33_public_pass"],
                                   "complete wider exact-V33 correctness receipt")
    speed = originals["exact_v33_public_performance_receipt"]
    summary = originals["exact_v33_public_performance_summary"]
    audit = public_document(parser, originals["historical_v30_static_audit"],
                            "historical earlier-V30 source and ELF audit only")
    require(exact_original.get("candidate_status") == "PASS"
            and exact_original.get("verified_passing_case_count") == 31237
            and exact_original.get("semantic_mismatch_count") == 0
            and exact_original.get("native_engine_sha256") == EXACT_PREVIOUS_ENGINE_BINARY_SHA
            and exact_original.get("native_bridge_sha256") == EXACT_PREVIOUS_BRIDGE_BINARY_SHA
            and exact_original.get("actual_v28_build_receipt_sha256")
                == OWNER_BY_ROLE["v33_build_publication"][2]
            and exact_public.get("public_10434_case_count") == 10434
            and exact_public.get("public_10434_mismatch_count") == 0
            and ('"v33_exact_original_pass_sha256":"'
                 + OWNER_BY_ROLE["exact_v33_original_pass"][2] + '"').encode() in speed
            and ('"v33_public_pass_sha256":"'
                 + OWNER_BY_ROLE["v33_public_pass"][2] + '"').encode() in speed
            and ('"v5_static_pass_sha256":"'
                 + OWNER_BY_ROLE["historical_v30_static_audit"][2] + '"').encode() in speed
            and b'"public_10434_case_count":10434' in speed
            and b'"public_10434_mismatch_count":0' in speed
            and b'"paired_row_count":1664' in speed
            and b'"status":"PASS"' in summary
            and b'"case_count":416' in summary
            and b'"faster_case_count":252' in summary
            and b'"slower_case_count":164' in summary
            and b'"regression_over_20_percent_count":14' in summary
            and b'"geomean_speedup_vs_stdlib":1.2424347186648022' in summary,
            "preserve exact same-build 31237/10434 successes and all 416 public losses")
    phases = audit.get("phases")
    require(audit.get("status") == "PASS" and type(phases) is list and len(phases) == 2
            and all(type(phase) is dict and type(phase.get("native_outputs")) is list
                    and {output.get("owner", {}).get("sha256")
                         for output in phase["native_outputs"]}
                    == {HISTORICAL_AUDITED_ENGINE_BINARY_SHA,
                        HISTORICAL_AUDITED_BRIDGE_BINARY_SHA}
                    for phase in phases)
            and EXACT_PREVIOUS_ENGINE_BINARY_SHA != HISTORICAL_AUDITED_ENGINE_BINARY_SHA
            and EXACT_PREVIOUS_BRIDGE_BINARY_SHA != HISTORICAL_AUDITED_BRIDGE_BINARY_SHA
            and audit.get("external_regex_packages") == 0
            and audit.get("external_regex_libraries") == 0,
            "never misattribute the old V30 source/ELF audit to exact V33 or proposed V35")

    return {
        "literal_bridge_source_sha256": OWNER_BY_ROLE["literal_bridge_source"][2],
        "literal_bridge_protocol_sha256": OWNER_BY_ROLE["literal_bridge_protocol"][2],
        "literal_bridge_contract_sha256": OWNER_BY_ROLE["literal_bridge_contract"][2],
        "literal_bridge_application_sha256": OWNER_BY_ROLE["literal_bridge_application"][2],
        "literal_bridge_sha256": LITERAL_BRIDGE_SHA,
        "literal_bridge_bytes": LITERAL_BRIDGE_BYTES,
        "handle_lease_source_sha256": OWNER_BY_ROLE["handle_lease_source"][2],
        "handle_lease_protocol_sha256": OWNER_BY_ROLE["handle_lease_protocol"][2],
        "handle_lease_contract_sha256": OWNER_BY_ROLE["handle_lease_contract"][2],
        "handle_lease_application_sha256": OWNER_BY_ROLE["handle_lease_application"][2],
        "optimized_safe_bridge_sha256": SAFE_BRIDGE_SHA,
        "optimized_safe_bridge_bytes": SAFE_BRIDGE_BYTES,
        "exact_previous_engine_binary_sha256": EXACT_PREVIOUS_ENGINE_BINARY_SHA,
        "exact_previous_bridge_binary_sha256": EXACT_PREVIOUS_BRIDGE_BINARY_SHA,
        "historically_audited_engine_binary_sha256": HISTORICAL_AUDITED_ENGINE_BINARY_SHA,
        "historically_audited_bridge_binary_sha256": HISTORICAL_AUDITED_BRIDGE_BINARY_SHA,
        "historical_v30_static_audit_sha256": OWNER_BY_ROLE["historical_v30_static_audit"][2],
        "historical_v30_audit_covers_exact_v33_or_proposed_v35": False,
        "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "exact_previous_original_case_count": 31237,
        "exact_previous_original_mismatch_count": 0,
        "exact_previous_wider_case_count": 10434,
        "exact_previous_wider_mismatch_count": 0,
        "exact_previous_public_case_count": 416,
        "exact_previous_public_paired_observation_count": 1664,
        "exact_previous_public_faster_case_count": 252,
        "exact_previous_public_slower_case_count": 164,
        "exact_previous_public_regression_over_20_percent_count": 14,
        "exact_previous_public_geomean_decimal": "1.2424347186648022",
        "proposed_v35_correctness": NOT_MEASURED,
        "proposed_v35_performance": NOT_MEASURED,
    }


def retired_metadata(wall: SourceWall) -> dict[str, object]:
    require(wall.proposal_metadata_probes == 0
            and wall.proposal_content_opens == 0,
            "perform no final-proposal content or metadata operations")
    return {
        "sha256_historical_independent_pin_not_read": RETIRED_PROPOSAL_SHA,
        "identity_scope": "HISTORICAL PIN ONLY; NO PROPOSAL OPEN OR STAT",
        "historical_proposed_case_count": RETIRED_PROPOSAL_CASE_COUNT,
        "metadata_probe_count": 0,
        "content_open_count_by_this_controller": 0,
        "hidden_cases_generated_by_this_controller": 0,
        "global_unopened_claim": False,
        "status": FINAL_HOLDOUT_STATUS,
        "reason": "RETIRED AFTER SOURCE-SCOPE ACCESS INCIDENT; NEVER A VALID FINAL",
        "replacement": "A FRESH REKEYED SUCCESSOR MUST BE INDEPENDENTLY FROZEN",
    }


def verify_history(parser: types.ModuleType,
                   originals: dict[str, bytes]) -> dict[str, object]:
    original = public_document(parser, originals["original_phase_one"], "frozen original P0")
    require(original.get("schema") == "rebar-cpython-re-p0-completeness-v4"
            and original.get("status") == "PASS"
            and original.get("original_case_execution_denominator") == 31237
            and original.get("original_suite_count") == 13
            and original.get("original_named_private_waiver_count") == 13
            and original.get("qualified_candidate_count") == 0,
            "preserve all 31237 original cases, 13 suites, and 13 private waivers")

    combined = public_document(parser, originals["combined_v2_contract"],
                               "independently frozen combined V2 source contract")
    require(combined.get("schema")
            == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and combined.get("version") == 2
            and combined.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["combined_v2_source"][2]
            and combined.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["combined_v2_protocol"][2]
            and combined.get("derived", {}).get("engine", {}).get("sha256") == BASE_ENGINE_SHA
            and combined.get("derived", {}).get("engine", {}).get("bytes") == BASE_ENGINE_BYTES
            and combined.get("derived", {}).get("search", {}).get("sha256") == SEARCH_SHA
            and combined.get("derived", {}).get("search", {}).get("bytes") == SEARCH_BYTES
            and combined.get("exact_commuting_composition", {}).get("replacement_count") == 7
            and combined.get("new_combined_synthetic_semantics", {})
                .get("combined_differential_case_count") == 111552,
            "authenticate exact complete V2 source, protocol, composition, and contract")
    application = public_document(parser, originals["combined_v2_application"],
                                  "actual exclusive combined V2 source application")
    created = application.get("created", {})
    require(application.get("schema")
            == "rebar-first-party-rust-combined-search-compiler-fastpath-v2-application"
            and application.get("status") == "APPLIED"
            and application.get("source_sha256") == OWNER_BY_ROLE["combined_v2_source"][2]
            and application.get("protocol_sha256") == OWNER_BY_ROLE["combined_v2_protocol"][2]
            and application.get("contract_sha256") == OWNER_BY_ROLE["combined_v2_contract"][2]
            and created.get("engine", {}).get("sha256") == BASE_ENGINE_SHA
            and created.get("engine", {}).get("bytes") == BASE_ENGINE_BYTES
            and created.get("engine", {}).get("inode")
            == OWNER_BY_ROLE["combined_v2_engine"][4]
            and created.get("search", {}).get("sha256") == SEARCH_SHA
            and created.get("search", {}).get("bytes") == SEARCH_BYTES
            and created.get("search", {}).get("inode")
            == OWNER_BY_ROLE["combined_v2_search"][4]
            and application.get("candidate_imports") == 0
            and application.get("compiler_processes_started") == 0
            and application.get("clock_samples") == 0,
            "authenticate both actually materialized V2 combined source owners")

    bridge = public_document(parser, originals["no_introspection_contract"],
                             "frozen private-introspection correction")
    bridge_application = public_document(parser, originals["no_introspection_application"],
                                         "actual exclusive private-getter correction")
    require(bridge.get("schema") == "rebar-owned-rust-no-external-introspection-v1-source-freeze"
            and bridge.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["no_introspection_source"][2]
            and bridge.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["no_introspection_protocol"][2],
            "authenticate the independent complete safe-bridge freeze triple")
    correction = bridge.get("exact_private_introspection_correction")
    require(type(correction) is dict, "require the complete safe bridge correction")
    validate_bridge(originals["no_introspection_bridge"], correction, bridge_application)
    complete_correction = validate_complete_bridge(parser, originals)
    full_public_correction = validate_full_public_sources(parser, originals)

    latest = public_document(parser, originals["v25_full_failure"],
                             "complete independently published V25 original correctness")
    require(latest.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v25-durable-publication-receipt"
            and latest.get("status") == "PASS"
            and latest.get("candidate_status") == "FAIL"
            and latest.get("semantic_mismatch_count") == 1352
            and latest.get("verified_passing_case_count") == 15877
            and latest.get("case_execution_denominator") == 31237
            and latest.get("completed_suite_count") == 13
            and latest.get("actual_candidate_workers") == 13
            and latest.get("distinct_worker_process_id_count") == 13
            and latest.get("infrastructure_failure_count") == 0,
            "preserve the real complete V25 FAIL-1352; publication PASS is not candidate PASS")
    suites = latest.get("suite_integrity")
    require(type(suites) is list and len(suites) == 13
            and sum(item.get("case_execution_denominator", 0) for item in suites
                    if type(item) is dict) == 31237
            and {item.get("suite"): item.get("mismatch_count") for item in suites
                 if type(item) is dict and item.get("mismatch_count", 0)}
            == {"substitution_v2": 240, "shape_v2": 1112},
            "preserve all thirteen genuine suites and both fully observed mismatch families")

    audit = public_document(parser, originals["strict_audit_failure"],
                            "complete actual strict V4 non-delegation failure")
    findings = audit.get("findings")
    require(audit.get("status") == "FAIL"
            and audit.get("finding_count") == 1 and type(findings) is list
            and len(findings) == 1
            and findings[0].get("code") == "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE"
            and findings[0].get("severity") == "FAIL"
            and findings[0].get("family") == FAMILY
            and findings[0].get("path") == "candidates/rust/py_bridge.c",
            "preserve the historical strict FAIL-1 without inventing a fresh audit PASS")

    previous: dict[str, dict[str, object]] = {}
    for version in (25, 26, 27, 28, 30):
        publication = public_document(parser, originals[f"v{version}_build_publication"],
                                      f"actual successful V{version} native publication")
        root = public_document(parser, originals[f"v{version}_build_root"],
                               f"actual successful V{version} private-root provenance")
        require(publication.get("status") == "PASS"
                and publication.get("build_status") == "PASS"
                and publication.get("actual_compiler_process_count") == 28
                and publication.get("actual_completed_phase_count") == 2
                and publication.get("corrected_public_adapter_sha256") == BASE_ADAPTER_SHA
                and publication.get("corrected_public_adapter_bytes") == BASE_ADAPTER_BYTES
                and publication.get("latest_v25_candidate_status", "FAIL") == "FAIL"
                and publication.get("latest_v25_semantic_mismatch_count", 1352) == 1352
                and root.get("status") == "PASS"
                and root.get("canonical_build_status") == "PASS"
                and root.get("canonical_build_receipt_sha256")
                == OWNER_BY_ROLE[f"v{version}_build_publication"][2]
                and root.get("actual_compiler_process_count") == 28
                and root.get("actual_source_phase_count") == 2
                and root.get("cross_phase_complete_bridge_elf_byte_identical") is True
                and root.get("cross_phase_complete_engine_elf_byte_identical") is True
                and root.get("corrected_public_adapter_sha256") == BASE_ADAPTER_SHA
                and root.get("corrected_public_adapter_bytes") == BASE_ADAPTER_BYTES,
                f"authenticate both actual complete independent successful V{version} receipts")
        previous[str(version)] = {
            "source_sha256": OWNER_BY_ROLE[f"v{version}_build_source"][2],
            "protocol_sha256": OWNER_BY_ROLE[f"v{version}_build_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE[f"v{version}_build_contract"][2],
            "publication_receipt_sha256": OWNER_BY_ROLE[f"v{version}_build_publication"][2],
            "root_provenance_receipt_sha256": OWNER_BY_ROLE[f"v{version}_build_root"][2],
            "actual_compiler_process_count": 28,
            "actual_independent_source_phase_count": 2,
            "cross_phase_complete_engine_elf_byte_identical": True,
            "cross_phase_complete_bridge_elf_byte_identical": True,
            "publication_status": "PASS; DURABLE PUBLICATION ONLY",
            "candidate_status": "NOT PROVEN BY NATIVE BUILD",
        }

    public_gates: dict[str, dict[str, object]] = {}
    for architecture in ("v26", "v27", "v28"):
        # These genuine complete public receipts contain floating timing data;
        # the intentionally integer-only source parser must never decode them.
        gate = originals[architecture + "_public_gate"]
        markers = (
            b'"schema":"rebar-owned-rust-native-architecture-public-gate-'
            + (b"v3" if architecture == "v28" else b"v2")
            + b'-durable-publication-receipt"',
            b'"architecture":"' + architecture.encode("ascii") + b'"',
            b'"public_10434_case_count":10434',
            b'"public_10434_correctness_status":"FAIL"',
            b'"public_10434_mismatch_count":1145',
            b'"public_416_correctness_gate":{"all_mismatches":[],"baseline_pid":83,'
            b'"case_count":416,"mismatch_count":0,"rust_pid":84,"status":"PASS"}',
            b'"candidate_qualified":false',
            b'"current_final_holdout":"' + FINAL_HOLDOUT_STATUS.encode("ascii") + b'"',
        )
        require(all(gate.count(marker) == 1 for marker in markers),
                "preserve the actual public 10434-case FAIL-1145 and public 416-case PASS")
        public_gates[architecture] = {
            "receipt_sha256": OWNER_BY_ROLE[architecture + "_public_gate"][2],
            "case_count": 10434, "candidate_status": "FAIL",
            "mismatch_count": 1145, "public_416_status": "PASS",
            "public_416_case_count": 416, "candidate_qualified": False,
        }

    passed = public_document(parser, originals["v26_original_pass"],
                             "actual complete V26 original-oracle PASS")
    passing_suites = passed.get("suite_integrity")
    require(passed.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v26-durable-publication-receipt"
            and passed.get("status") == "PASS"
            and passed.get("publication_status") == "PASS"
            and passed.get("candidate_status") == "PASS"
            and passed.get("candidate_original_oracle_pass") is True
            and passed.get("semantic_mismatch_count") == 0
            and passed.get("verified_passing_case_count") == 31237
            and passed.get("case_execution_denominator") == 31237
            and passed.get("completed_suite_count") == 13
            and passed.get("actual_candidate_workers") == 13
            and passed.get("distinct_worker_process_id_count") == 13
            and passed.get("infrastructure_failure_count") == 0
            and type(passing_suites) is list and len(passing_suites) == 13
            and sum(row.get("case_execution_denominator", 0)
                    for row in passing_suites if type(row) is dict) == 31237
            and all(type(row) is dict and row.get("mismatch_count") == 0
                    and row.get("fully_observed") is True for row in passing_suites)
            and passed.get("combined_bridge_source_sha256") == BASE_BRIDGE_SHA
            and passed.get("corrected_public_adapter_sha256") == BASE_ADAPTER_SHA,
            "preserve genuine V26 PASS of all 31237 original cases and 13 full suites")

    previous_freeze = public_document(parser, originals["v33_build_contract"],
                                      "complete independently frozen V33 native build")
    previous_build = public_document(parser, originals["v33_build_publication"],
                                     "actual successful first-party V33 native build")
    previous_root = public_document(parser, originals["v33_build_root"],
                                    "actual independently owned V33 build-root receipt")
    public_pass = public_document(parser, originals["v33_public_pass"],
                                  "actual complete 10434-case V33 public PASS")
    require(previous_freeze.get("schema")
                == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-source-freeze"
            and previous_freeze.get("source", {}).get("sha256")
                == OWNER_BY_ROLE["v33_build_source"][2]
            and previous_freeze.get("protocol", {}).get("sha256")
                == OWNER_BY_ROLE["v33_build_protocol"][2]
            and previous_freeze.get("candidate_sources", {})
                .get("combined_engine", {}).get("sha256") == SCOPED_ENGINE_SHA
            and previous_freeze.get("candidate_sources", {})
                .get("complete_scanner_bridge", {}).get("sha256") == BRIDGE_SHA
            and previous_freeze.get("candidate_sources", {})
                .get("corrected_comment_adapter", {}).get("sha256") == ADAPTER_SHA
            and previous_build.get("schema")
                == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-publication-receipt"
            and previous_build.get("status") == "PASS"
            and previous_build.get("build_status") == "PASS"
            and previous_build.get("actual_compiler_process_count") == 28
            and previous_build.get("actual_completed_phase_count") == 2
            and previous_build.get("combined_engine_source_sha256") == SCOPED_ENGINE_SHA
            and previous_build.get("corrected_public_adapter_sha256") == ADAPTER_SHA
            and previous_build.get("complete_scanner_bridge_sha256") == BRIDGE_SHA
            and previous_build.get("external_cargo_dependency_count") == 0
            and previous_root.get("schema")
                == "rebar-phase2-owned-rust-full-public-semantic-source-build-v33-durable-root-provenance-receipt"
            and previous_root.get("status") == "PASS"
            and previous_root.get("canonical_build_status") == "PASS"
            and previous_root.get("canonical_build_receipt_sha256")
                == OWNER_BY_ROLE["v33_build_publication"][2]
            and previous_root.get("actual_compiler_process_count") == 28
            and previous_root.get("actual_source_phase_count") == 2
            and public_pass.get("schema")
                == "rebar-owned-rust-full-public-correctness-v5-durable-publication-receipt"
            and public_pass.get("status") == "PASS"
            and public_pass.get("publication_status") == "PASS"
            and public_pass.get("candidate_status") == "PASS"
            and public_pass.get("public_10434_correctness_status") == "PASS"
            and public_pass.get("public_10434_case_count") == 10434
            and public_pass.get("public_10434_verified_passing_case_count") == 10434
            and public_pass.get("public_10434_mismatch_count") == 0
            and public_pass.get("public_api_operation_count") == 111
            and public_pass.get("v26_original_pass_sha256")
                == OWNER_BY_ROLE["v26_original_pass"][2]
            and public_pass.get("v33_source_sha256")
                == OWNER_BY_ROLE["v33_build_source"][2]
            and public_pass.get("v33_contract_sha256")
                == OWNER_BY_ROLE["v33_build_contract"][2]
            and public_pass.get("v33_publication_sha256")
                == OWNER_BY_ROLE["v33_build_publication"][2]
            and public_pass.get("v33_root_sha256")
                == OWNER_BY_ROLE["v33_build_root"][2]
            and public_pass.get("candidate_qualified") is False
            and public_pass.get("runtime_non_delegation") == "NOT ESTABLISHED",
            "preserve genuine V33 dual build and all 10434 public PASS rows without qualification")

    profile = public_document(parser, originals["public_profile"], "public-only profile")
    python = public_document(parser, originals["public_python"], "public Python observations")
    rust = public_document(parser, originals["public_rust"], "public Rust observations")
    paired = public_document(parser, originals["public_paired"], "public paired rows")
    rows = paired.get("rows")
    require(profile.get("case_count") == 416
            and python.get("status") == "PASS" and python.get("case_count") == 416
            and rust.get("status") == "PASS" and rust.get("case_count") == 416
            and type(rows) is list and len(rows) == 1664,
            "preserve all 416 public cases and all 1664 complete paired observations")
    graph = originals["public_graph"]
    for marker in (
        b'"public_correctness_case_count":416',
        b'"public_paired_observation_count":1664',
        b'"public_rust_faster_pair_count":723',
        b'"public_rust_slower_pair_count":937',
        b'"public_tied_pair_count":4',
        b'"public_equal_case_geometric_speedup":0.8485646292880136',
        b'"dense_prefix_public_equal_case_geometric_speedup":0.41613883193210616',
    ):
        require(marker in graph, "preserve the exact historical public-practice evidence")

    v26 = public_document(parser, originals["v26_build_contract"],
                           "complete independently frozen V26 build contract")
    v27 = public_document(parser, originals["v27_build_contract"],
                           "complete independently frozen V27 build contract")
    v28 = public_document(parser, originals["v28_build_contract"],
                           "complete independently frozen and actually built V28 contract")
    v30 = public_document(parser, originals["v30_build_contract"],
                           "complete actually passing V30 native source-build contract")
    v32 = public_document(parser, originals["v32_build_contract"],
                          "immutable rejected full-public semantic V32 build contract")
    v32_failure = public_document(parser, originals["v32_build_failure"],
                                  "actual V32 private-overlay preexecution rejection")
    require(v26.get("schema") == "rebar-phase2-owned-rust-anchor-source-build-v26-source-freeze"
            and v26.get("source", {}).get("sha256") == OWNER_BY_ROLE["v26_build_source"][2]
            and v26.get("protocol", {}).get("sha256") == OWNER_BY_ROLE["v26_build_protocol"][2]
            and v26.get("external_cargo_dependency_count") == 0
            and v26.get("canonical_original_rust_source_owner_count") == 9
            and v27.get("schema")
            == "rebar-phase2-owned-rust-compiler-fastpath-source-build-v27-source-freeze"
            and v27.get("source", {}).get("sha256") == OWNER_BY_ROLE["v27_build_source"][2]
            and v27.get("protocol", {}).get("sha256") == OWNER_BY_ROLE["v27_build_protocol"][2]
            and v27.get("frozen_offline_dual_phase_build", {}).get("phase_count") == 2
            and v27.get("frozen_offline_dual_phase_build", {})
                .get("external_cargo_dependency_count") == 0
            and v28.get("schema")
            == "rebar-phase2-owned-rust-combined-source-build-v28-source-freeze"
            and v28.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["v28_build_source"][2]
            and v28.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["v28_build_protocol"][2]
            and v28.get("candidate_sources", {}).get("combined_engine", {})
                .get("sha256") == BASE_ENGINE_SHA
            and v28.get("candidate_sources", {}).get("combined_search", {})
                .get("sha256") == SEARCH_SHA
            and v30.get("schema")
            == "rebar-phase2-owned-rust-complete-semantic-source-build-v30-source-freeze"
            and v30.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["v30_build_source"][2]
            and v30.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["v30_build_protocol"][2]
            and v30.get("candidate_sources", {}).get("combined_engine", {})
                .get("sha256") == BASE_ENGINE_SHA
            and v30.get("candidate_sources", {}).get("combined_search", {})
                .get("sha256") == SEARCH_SHA
            and v30.get("candidate_sources", {})
                .get("complete_semantic_correction_bridge", {}).get("sha256")
            == BASE_BRIDGE_SHA
            and v32.get("schema")
            == "rebar-phase2-owned-rust-full-public-semantic-source-build-v32-source-freeze"
            and v32.get("source", {}).get("sha256")
            == OWNER_BY_ROLE["v32_build_source"][2]
            and v32.get("protocol", {}).get("sha256")
            == OWNER_BY_ROLE["v32_build_protocol"][2]
            and v32.get("candidate_sources", {}).get("combined_engine", {})
                .get("sha256") == SCOPED_ENGINE_SHA
            and v32.get("candidate_sources", {}).get("complete_scanner_bridge", {})
                .get("sha256") == BRIDGE_SHA
            and v32.get("candidate_sources", {}).get("corrected_comment_adapter", {})
                .get("sha256") == ADAPTER_SHA
            and v32.get("preserved_original_31237_case_pass", {})
                .get("verified_passing_case_count") == 31237
            and v32.get("preserved_public_v28_1145_disjoint_partition", {})
                .get("mismatch_count") == 1145
            and v32_failure.get("schema")
            == "rebar-phase2-owned-rust-full-public-semantic-source-build-v32-preexecution-failure"
            and v32_failure.get("status") == "FAIL"
            and v32_failure.get("failure_phase")
            == "AUTHENTICATED_PRIVATE_OVERLAY_VALIDATION"
            and v32_failure.get("error")
            == "independently caller-pin both complete first-party private overlays"
            and v32_failure.get("source_sha256")
            == OWNER_BY_ROLE["v32_build_source"][2]
            and v32_failure.get("protocol_sha256")
            == OWNER_BY_ROLE["v32_build_protocol"][2]
            and v32_failure.get("contract_sha256")
            == OWNER_BY_ROLE["v32_build_contract"][2]
            and v32_failure.get("corrected_adapter_sha256") == ADAPTER_SHA
            and v32_failure.get("corrected_adapter_bytes") == ADAPTER_BYTES
            and v32_failure.get("inherited_kernel_adapter_sha256") == BASE_ADAPTER_SHA
            and v32_failure.get("inherited_kernel_adapter_bytes") == BASE_ADAPTER_BYTES
            and v32_failure.get("candidate_executions") == 0
            and v32_failure.get("compiler_processes_started") == 0
            and v32_failure.get("native_build_started") is False
            and v32_failure.get("final_proposal_reads") == 0,
            "anchor V26/V27/V28/V30 success and preserve exact safe immutable V32 rejection")

    manifest = originals["cargo_manifest"]
    lock = originals["cargo_lock"]
    require(manifest.count(b"[package]") == 1
            and manifest.count(b'[lib]') == 1
            and b'crate-type = ["cdylib"]' in manifest
            and b"[dependencies]" not in manifest
            and lock.count(b"[[package]]") == 1
            and b'name = "rebar-rust-continuation"' in manifest
            and b'name = "rebar-rust-continuation"' in lock,
            "freeze exactly one first-party Cargo package and zero external dependencies")
    return {
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_shape_ordering_mismatch_count": 1024,
        "latest_v25_shape_trailing_probe_mismatch_count": 56,
        "latest_v25_shape_malformed_expansion_mismatch_count": 32,
        "latest_v25_exact_disjoint_mismatch_partition": {
            "substitution_v2": 240,
            "shape_v2_ordering": 1024,
            "shape_v2_trailing_probe": 56,
            "shape_v2_malformed_expansion": 32,
        },
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_actual_candidate_worker_count": 13,
        "latest_v25_infrastructure_failure_count": 0,
        "latest_v25_failure_receipt_sha256": OWNER_BY_ROLE["v25_full_failure"][2],
        "latest_original_v26_candidate_status": "PASS",
        "latest_original_v26_semantic_mismatch_count": 0,
        "latest_original_v26_verified_passing_case_count": 31237,
        "latest_original_v26_completed_suite_count": 13,
        "latest_original_v26_actual_candidate_worker_count": 13,
        "latest_original_v26_failure_receipt_sha256":
            OWNER_BY_ROLE["v26_original_pass"][2],
        "latest_public_v33_candidate_status": "PASS",
        "latest_public_v33_case_count": 10434,
        "latest_public_v33_verified_passing_case_count": 10434,
        "latest_public_v33_mismatch_count": 0,
        "latest_public_v33_receipt_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
        "latest_public_v33_source_sha256": OWNER_BY_ROLE["v33_build_source"][2],
        "latest_public_v33_publication_sha256":
            OWNER_BY_ROLE["v33_build_publication"][2],
        "latest_public_v33_root_sha256": OWNER_BY_ROLE["v33_build_root"][2],
        "exact_literal_candidate_correctness": NOT_MEASURED,
        "strict_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
        "strict_audit_finding_count": 1,
        "strict_audit_finding_code": "CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE",
        "strict_audit_failure_receipt_sha256": OWNER_BY_ROLE["strict_audit_failure"][2],
        "corrected_bridge_private_getter_removed": True,
        "corrected_bridge_fresh_strict_audit": "NOT RUN; NOT ESTABLISHED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "public_case_count": 416,
        "public_paired_observation_count": 1664,
        "public_rust_faster_paired_count": 723,
        "public_rust_slower_paired_count": 937,
        "public_tied_paired_count": 4,
        "previous_successful_native_builds": previous,
        "immutable_v32_preexecution_failure": {
            "source_sha256": OWNER_BY_ROLE["v32_build_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["v32_build_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["v32_build_contract"][2],
            "failure_receipt_sha256": OWNER_BY_ROLE["v32_build_failure"][2],
            "frozen_commit": v32_failure["frozen_commit"],
            "failure_phase": v32_failure["failure_phase"],
            "native_build_started": False,
            "compiler_processes_started": 0,
            "inherited_corrected_adapter_sha256": BASE_ADAPTER_SHA,
            "inherited_corrected_adapter_bytes": BASE_ADAPTER_BYTES,
            "required_corrected_adapter_sha256": ADAPTER_SHA,
            "required_corrected_adapter_bytes": ADAPTER_BYTES,
            "v35_inherited_adapter_constants_rebound_before_actual_kernel": True,
        },
        "actual_public_10434_case_gates": public_gates,
        "latest_public_10434_mismatch_count": 0,
        "historical_v28_public_10434_mismatch_count": 1145,
        "latest_public_v28_disjoint_mismatch_partition": {
            "scanner": 470, "substitution": 376,
            "comment": 297, "scoped_unicode": 2,
        },
        "latest_public_v28_comment_overlap_partition": {
            "scanner_comment_overlap": 15,
            "substitution_comment_overlap": 12,
            "gross_comment_target_count": 324,
        },
        "complete_semantic_correction": complete_correction,
        "full_public_semantic_correction": full_public_correction,
        "final_proposal_files_read": 0,
        "final_proposal_metadata_probes": 0,
        "external_cargo_dependency_count": 0,
        "first_party_package_count": 1,
        "qualified_independent_candidate_count": 0,
        "final_holdout": FINAL_HOLDOUT_STATUS,
    }


def owner_document(row: tuple[object, ...]) -> dict[str, object]:
    return {"role": row[0], "path": row[1], "sha256": row[2],
            "bytes": row[3], "device": DEVICE, "inode": row[4],
            "mode": "0600", "nlink": 1}


def full_public_provenance() -> dict[str, object]:
    return {
        "latest_original_v33_candidate_status": "PASS",
        "latest_original_v33_semantic_mismatch_count": 0,
        "latest_original_v33_verified_passing_case_count": 31237,
        "latest_original_v33_case_execution_denominator": 31237,
        "latest_original_v33_completed_suite_count": 13,
        "latest_original_v33_pass_receipt_sha256":
            OWNER_BY_ROLE["exact_v33_original_pass"][2],
        "latest_public_v33_candidate_status": "PASS",
        "latest_public_v33_case_count": 10434,
        "latest_public_v33_verified_passing_case_count": 10434,
        "latest_public_v33_mismatch_count": 0,
        "latest_public_v33_receipt_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
        "latest_public_v33_source_sha256": OWNER_BY_ROLE["v33_build_source"][2],
        "latest_public_v33_protocol_sha256": OWNER_BY_ROLE["v33_build_protocol"][2],
        "latest_public_v33_contract_sha256": OWNER_BY_ROLE["v33_build_contract"][2],
        "latest_public_v33_build_publication_sha256":
            OWNER_BY_ROLE["v33_build_publication"][2],
        "latest_public_v33_build_root_sha256": OWNER_BY_ROLE["v33_build_root"][2],
        "latest_public_v33_performance_receipt_sha256":
            OWNER_BY_ROLE["exact_v33_public_performance_receipt"][2],
        "latest_public_v33_performance_summary_sha256":
            OWNER_BY_ROLE["exact_v33_public_performance_summary"][2],
        "latest_public_v33_faster_case_count": 252,
        "latest_public_v33_slower_case_count": 164,
        "latest_public_v33_regression_over_20_percent_count": 14,
        "latest_public_v33_paired_observation_count": 1664,
        "latest_public_v33_geomean_decimal": "1.2424347186648022",
        "latest_public_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "latest_public_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_correctness": NOT_MEASURED,
        "proposed_v35_performance": NOT_MEASURED,
        "proposed_v35_undefined_behavior": NOT_MEASURED,
        "latest_public_v28_candidate_status": "FAIL",
        "latest_public_v28_case_count": 10434,
        "latest_public_v28_mismatch_count": 1145,
        "latest_public_v28_receipt_sha256": OWNER_BY_ROLE["v28_public_gate"][2],
        "latest_public_v28_exact_disjoint_mismatch_partition": {
            "scanner": 470,
            "substitution": 376,
            "comment": 297,
            "scoped_unicode": 2,
        },
        "latest_public_v28_scanner_comment_overlap_count": 15,
        "latest_public_v28_substitution_comment_overlap_count": 12,
        "latest_public_v28_gross_comment_target_count": 324,
        "complete_scanner_bridge_source_sha256": OWNER_BY_ROLE["scanner_bridge_source"][2],
        "complete_scanner_bridge_protocol_sha256":
            OWNER_BY_ROLE["scanner_bridge_protocol"][2],
        "complete_scanner_bridge_contract_sha256":
            OWNER_BY_ROLE["scanner_bridge_contract"][2],
        "complete_scanner_bridge_application_sha256":
            OWNER_BY_ROLE["scanner_bridge_application"][2],
        "historical_complete_scanner_bridge_sha256": BRIDGE_SHA,
        "historical_complete_scanner_bridge_bytes": BRIDGE_BYTES,
        "combined_scoped_unicode_engine_source_sha256":
            OWNER_BY_ROLE["scoped_engine_source"][2],
        "combined_scoped_unicode_engine_protocol_sha256":
            OWNER_BY_ROLE["scoped_engine_protocol"][2],
        "combined_scoped_unicode_engine_contract_sha256":
            OWNER_BY_ROLE["scoped_engine_contract"][2],
        "combined_scoped_unicode_engine_application_sha256":
            OWNER_BY_ROLE["scoped_engine_application"][2],
        "corrected_comment_adapter_v2_source_sha256":
            OWNER_BY_ROLE["comment_adapter_v2_source"][2],
        "corrected_comment_adapter_v2_protocol_sha256":
            OWNER_BY_ROLE["comment_adapter_v2_protocol"][2],
        "corrected_comment_adapter_v2_contract_sha256":
            OWNER_BY_ROLE["comment_adapter_v2_contract"][2],
        "corrected_comment_adapter_v2_application_sha256":
            OWNER_BY_ROLE["comment_adapter_v2_application"][2],
        "corrected_comment_adapter_v1_failure_preserved_sha256":
            OWNER_BY_ROLE["comment_adapter_v1_failure"][2],
        "actual_v30_native_publication_receipt_sha256":
            OWNER_BY_ROLE["v30_build_publication"][2],
        "actual_v30_native_root_provenance_receipt_sha256":
            OWNER_BY_ROLE["v30_build_root"][2],
        "immutable_v32_source_sha256": OWNER_BY_ROLE["v32_build_source"][2],
        "immutable_v32_protocol_sha256": OWNER_BY_ROLE["v32_build_protocol"][2],
        "immutable_v32_contract_sha256": OWNER_BY_ROLE["v32_build_contract"][2],
        "immutable_v32_preexecution_failure_sha256":
            OWNER_BY_ROLE["v32_build_failure"][2],
        "inherited_v16_adapter_constants_rebound_before_run_build": True,
        "current_public_v3_proposal_status": CURRENT_PUBLIC_V3_STATUS,
        "current_public_v3_seed_created": False,
        "current_public_v3_proposal_contents_opened": 0,
        "proposal_files_opened": 0,
        "proposal_metadata_probes": 0,
    }


def build_contract(source: dict[str, object], protocol: dict[str, object],
                   history: dict[str, object], proposal: dict[str, object],
                   composition: dict[str, object], anchor_model: dict[str, object],
                   compiler_model: dict[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": "SOURCE FROZEN; NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED",
        "phase": "PHASE 2: FIRST-PARTY RUST CANDIDATE CORRECTNESS",
        "family": FAMILY,
        "source": source,
        "protocol": protocol,
        "authenticated_first_party_owner_count": len(STATIC_OWNERS),
        "authenticated_first_party_owners": [owner_document(row) for row in STATIC_OWNERS],
        "original_correctness": history,
        "retired_expanded_holdout_metadata_only": proposal,
        "final_holdout": FINAL_HOLDOUT_STATUS,
        "current_public_v3_proposal_status": CURRENT_PUBLIC_V3_STATUS,
        "current_public_v3_seed_created": False,
        "current_public_v3_proposal_content_opens": 0,
        "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
        "proposed_v35_correctness": NOT_MEASURED,
        "proposed_v35_performance": NOT_MEASURED,
        "proposed_v35_undefined_behavior": NOT_MEASURED,
        "candidate_sources": {
            "combined_engine": owner_document(OWNER_BY_ROLE["literal_engine"]),
            "exact_literal_engine": owner_document(OWNER_BY_ROLE["literal_engine"]),
            "exact_literal_scoped_parent":
                owner_document(OWNER_BY_ROLE["scoped_engine"]),
            "combined_search": owner_document(OWNER_BY_ROLE["combined_v2_search"]),
            "historical_complete_scanner_bridge":
                owner_document(OWNER_BY_ROLE["scanner_bridge"]),
            "historical_literal_acceleration_bridge":
                owner_document(OWNER_BY_ROLE["literal_bridge"]),
            "complete_semantic_correction_bridge":
                owner_document(OWNER_BY_ROLE["optimized_safe_bridge"]),
            "complete_scanner_bridge":
                owner_document(OWNER_BY_ROLE["optimized_safe_bridge"]),
            "no_external_introspection_bridge":
                owner_document(OWNER_BY_ROLE["optimized_safe_bridge"]),
            "optimized_native_handle_lease_bridge":
                owner_document(OWNER_BY_ROLE["optimized_safe_bridge"]),
            "corrected_comment_adapter": owner_document(OWNER_BY_ROLE["comment_adapter"]),
            "corrected_adapter": {
                "derivation": "FOUR PRIVATE INTERFACE REPAIRS PLUS THREE COMMENT REPAIRS",
                "source_path": OWNER_BY_ROLE["original_adapter"][1],
                "source_sha256": OWNER_BY_ROLE["original_adapter"][2],
                "repair_source_path": OWNER_BY_ROLE["adapter_repair_source"][1],
                "repair_source_sha256": OWNER_BY_ROLE["adapter_repair_source"][2],
                "comment_source_path": OWNER_BY_ROLE["comment_adapter_v2_source"][1],
                "comment_source_sha256": OWNER_BY_ROLE["comment_adapter_v2_source"][2],
                "materialized_path": OWNER_BY_ROLE["comment_adapter"][1],
                "materialized_device": DEVICE,
                "materialized_inode": OWNER_BY_ROLE["comment_adapter"][4],
                "derived_sha256": ADAPTER_SHA,
                "derived_bytes": ADAPTER_BYTES,
                "candidate_adapter_executed": False,
            },
        },
        "authentic_combined_v2": {
            "source_sha256": OWNER_BY_ROLE["combined_v2_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["combined_v2_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["combined_v2_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["combined_v2_application"][2],
            "replacement_count": 7,
            "combined_differential_case_count": 111552,
            "composition": composition,
            "anchor_synthetic_model": anchor_model,
            "compiler_synthetic_model": compiler_model,
        },
        "authentic_no_external_introspection_v1": {
            "source_sha256": OWNER_BY_ROLE["no_introspection_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["no_introspection_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["no_introspection_contract"][2],
            "application_receipt_sha256": OWNER_BY_ROLE["no_introspection_application"][2],
            "target_sha256": OWNER_BY_ROLE["no_introspection_bridge"][2],
            "target_bytes": OWNER_BY_ROLE["no_introspection_bridge"][3],
            "private_signature_getter_removed": True,
            "capture_clamp_preserved": True,
            "public_native_descriptors_preserved": True,
            "strict_audit": "NOT RERUN; HISTORICAL FAIL-1 PRESERVED",
        },
        "authentic_complete_semantic_correction_v2":
            history["complete_semantic_correction"],
        "authentic_full_public_semantic_correction":
            history["full_public_semantic_correction"],
        "authentic_exact_literal_first_party_architecture":
            history["exact_literal_architecture"],
        "authentic_optimized_safe_native_bridge":
            history["optimized_safe_bridge"],
        "preserved_immutable_v32_preexecution_failure":
            history["immutable_v32_preexecution_failure"],
        "preserved_original_31237_case_pass": {
            "receipt_sha256": OWNER_BY_ROLE["exact_v33_original_pass"][2],
            "candidate_status": "PASS",
            "semantic_mismatch_count": 0,
            "verified_passing_case_count": 31237,
            "completed_suite_count": 13,
        },
        "preserved_public_v28_1145_disjoint_partition": {
            "receipt_sha256": OWNER_BY_ROLE["v28_public_gate"][2],
            "candidate_status": "FAIL",
            "case_count": 10434,
            "mismatch_count": 1145,
            "partition": history["latest_public_v28_disjoint_mismatch_partition"],
            "scanner_comment_overlap_count": 15,
            "substitution_comment_overlap_count": 12,
        },
        "preserved_public_v33_10434_complete_pass": {
            "receipt_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
            "candidate_status": "PASS",
            "case_count": 10434,
            "verified_passing_case_count": 10434,
            "mismatch_count": 0,
            "source_sha256": OWNER_BY_ROLE["v33_build_source"][2],
            "protocol_sha256": OWNER_BY_ROLE["v33_build_protocol"][2],
            "contract_sha256": OWNER_BY_ROLE["v33_build_contract"][2],
            "native_publication_sha256": OWNER_BY_ROLE["v33_build_publication"][2],
            "native_root_sha256": OWNER_BY_ROLE["v33_build_root"][2],
            "exact_literal_candidate_correctness": NOT_MEASURED,
        },
        "preserved_actual_public_10434_case_gates":
            history["actual_public_10434_case_gates"],
        "proposal_reads": 0,
        "proposal_metadata_probes": 0,
        "frozen_offline_dual_phase_build": {
            "status": "NOT RUN",
            "label": LABEL,
            "actual_authorization": "ROOT ONLY AFTER ALL THREE OWNERS COMMITTED AND PUSHED",
            "required_commit_equals_pushed_commit": True,
            "phase_names": list(PHASES),
            "independent_phase_count": 2,
            "canonical_source_owners_per_phase": 9,
            "original_runtime_targets_restored_after_actual_build": 5,
            "unchanged_canonical_source_owners_per_phase": 5,
            "exclusive_authenticated_source_overlays_per_phase": 4,
            "combined_engine_overlay_sha256": ENGINE_SHA,
            "combined_engine_overlay_bytes": ENGINE_BYTES,
            "exact_literal_engine_source_sha256":
                OWNER_BY_ROLE["literal_source"][2],
            "exact_literal_engine_protocol_sha256":
                OWNER_BY_ROLE["literal_protocol"][2],
            "exact_literal_engine_contract_sha256":
                OWNER_BY_ROLE["literal_contract"][2],
            "exact_literal_engine_application_sha256":
                OWNER_BY_ROLE["literal_application"][2],
            "exact_literal_scoped_parent_sha256": SCOPED_ENGINE_SHA,
            "exact_literal_scoped_parent_bytes": SCOPED_ENGINE_BYTES,
            "combined_search_overlay_sha256": SEARCH_SHA,
            "combined_search_overlay_bytes": SEARCH_BYTES,
            "historical_complete_scanner_bridge_sha256": BRIDGE_SHA,
            "historical_complete_scanner_bridge_bytes": BRIDGE_BYTES,
            "literal_acceleration_bridge_source_sha256":
                OWNER_BY_ROLE["literal_bridge_source"][2],
            "literal_acceleration_bridge_protocol_sha256":
                OWNER_BY_ROLE["literal_bridge_protocol"][2],
            "literal_acceleration_bridge_contract_sha256":
                OWNER_BY_ROLE["literal_bridge_contract"][2],
            "literal_acceleration_bridge_application_sha256":
                OWNER_BY_ROLE["literal_bridge_application"][2],
            "native_handle_lease_source_sha256":
                OWNER_BY_ROLE["handle_lease_source"][2],
            "native_handle_lease_protocol_sha256":
                OWNER_BY_ROLE["handle_lease_protocol"][2],
            "native_handle_lease_contract_sha256":
                OWNER_BY_ROLE["handle_lease_contract"][2],
            "native_handle_lease_application_sha256":
                OWNER_BY_ROLE["handle_lease_application"][2],
            "safe_no_external_introspection_bridge_overlay_sha256": SAFE_BRIDGE_SHA,
            "safe_no_external_introspection_bridge_overlay_bytes": SAFE_BRIDGE_BYTES,
            "complete_semantic_correction_bridge_overlay_sha256": SAFE_BRIDGE_SHA,
            "complete_semantic_correction_bridge_overlay_bytes": SAFE_BRIDGE_BYTES,
            "optimized_native_handle_lease_bridge_overlay_sha256": SAFE_BRIDGE_SHA,
            "optimized_native_handle_lease_bridge_overlay_bytes": SAFE_BRIDGE_BYTES,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "corrected_adapter_overlay_sha256": ADAPTER_SHA,
            "corrected_adapter_overlay_bytes": ADAPTER_BYTES,
            "compiler_process_roles_per_phase": list(PROCESS_NAMES),
            "required_actual_compiler_process_count": 28,
            "external_cargo_dependency_count": 0,
            "cargo_flags": ["build", "--release", "--locked", "--offline", "--frozen"],
            "complete_engine_elf_byte_equality_required": True,
            "complete_bridge_elf_byte_equality_required": True,
            "native_symbol_and_dynamic_link_audits_required": True,
            "external_regular_expression_engine": "FORBIDDEN",
            "private_root_mode": "0700",
            "private_source_mode": "0600",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
        },
        "physical_source_wall": {
            "policy": "IRREVERSIBLE DENY DEFAULT; EXACT DESCRIPTOR-PINNED OWNERS ONLY",
            "installed_before_first_owner_read": True,
            "retired_v2_proposal_allowed_metadata_probes": 0,
            "retired_v2_proposal_content_opens_by_this_controller": 0,
            "all_final_proposal_reads_allowed": False,
            "all_final_proposal_metadata_probes_allowed": False,
            "global_v2_unopened_claim": False,
            "candidate_imports_allowed": False,
            "candidate_execution_allowed": False,
            "native_binary_opens_allowed": False,
            "native_library_loads_allowed": False,
            "compiler_processes_allowed": False,
            "clock_access_allowed": False,
            "entropy_or_hidden_case_generation_allowed": False,
            "archive_reads_allowed": False,
            "private_root_access_allowed": False,
            "workspace_mutations_allowed": False,
            "network_access_allowed": False,
            "exact_pinned_dynamic_source_transformer_count": 4,
            "four_required_source_gates": [
                "normal --self-test", "normal --verify-frozen-context",
                "sterile --self-test", "sterile --verify-frozen-context",
            ],
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_executions": 0,
            "candidate_workers_started": 0,
            "compiler_processes_started": 0,
            "native_binary_files_opened": 0,
            "native_libraries_loaded": 0,
            "compressed_archives_opened": 0,
            "hidden_cases_opened": 0,
            "hidden_cases_generated": 0,
            "retired_holdout_content_open_count_by_this_controller": 0,
            "retired_holdout_metadata_probe_count": 0,
            "clock_samples": 0,
            "network_requests": 0,
            "workspace_mutations": 0,
            "private_roots_created": 0,
            "private_roots_opened": 0,
            "candidate_correctness": NOT_MEASURED,
            "candidate_matching": "NOT RUN",
            "candidate_performance": NOT_MEASURED,
            "candidate_memory": NOT_MEASURED,
            "current_exact_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "current_exact_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "undefined_behavior": NOT_MEASURED,
            "candidate_qualified": False,
            "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT_STATUS,
        },
    }


def load_source_context(mode: str, source_pin: str, protocol_pin: str,
                        contract_pin: str | None) -> dict[str, object]:
    clean_imports()
    wall = SourceWall()
    wall.install()
    source_raw, source_info = live_owner(wall, "source", SOURCE, source_pin)
    protocol_raw, protocol_info = live_owner(wall, "protocol", PROTOCOL, protocol_pin)
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and b"SOURCE-ONLY WALL" in protocol_raw
            and FINAL_HOLDOUT_STATUS.encode("ascii") in protocol_raw,
            "authenticate the complete V35 controller and invalidated-final protocol")

    originals: dict[str, bytes] = {}
    for row in STATIC_OWNERS:
        payload, _identity = read_owner(wall, row)
        originals[row[0]] = payload
    anchor = frozen_module(wall, "anchor_transformer", originals["anchor_transformer"])
    compiler = frozen_module(wall, "compiler_transformer", originals["compiler_transformer"])
    combined = frozen_module(wall, "combined_v2_source", originals["combined_v2_source"])
    literal = frozen_module(wall, "literal_source", originals["literal_source"])
    require(anchor.SCHEMA == "rebar-owned-rust-mandatory-anchor-search-v1"
            and compiler.SCHEMA == "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
            and combined.SCHEMA == "rebar-first-party-rust-combined-search-compiler-fastpath-v2"
            and callable(anchor.StrictJSON) and callable(anchor.canonical)
            and callable(compiler.derive_source) and callable(compiler.synthetic_semantics)
            and callable(combined.derive_sources) and callable(combined.check_composition)
            and callable(literal.derive_engine),
            "load only four exact independently frozen first-party source transformers")

    history = verify_history(anchor, originals)
    history["exact_literal_architecture"] = validate_exact_literal_sources(
        anchor, literal, originals)
    history["optimized_safe_bridge"] = validate_optimized_safe_bridge(
        anchor, originals)
    exact_owners = {
        "anchor_lib": originals["anchor_variant_engine"],
        "canonical_lib": originals["original_engine"],
        "canonical_search": originals["original_search"],
        "compiler_variant": originals["compiler_variant_engine"],
        "anchor_search": originals["combined_v2_search"],
    }
    engine, search, composition = combined.derive_sources(
        exact_owners, compiler.__dict__, anchor.__dict__,
    )
    require(engine == originals["combined_v2_engine"]
            and search == originals["combined_v2_search"]
            and digest(engine) == BASE_ENGINE_SHA and len(engine) == BASE_ENGINE_BYTES
            and digest(search) == SEARCH_SHA and len(search) == SEARCH_BYTES
            and composition.get("replacement_count") == 7
            and composition.get("transformations_commute") is True
            and composition.get("transformation_is_exactly_reversible") is True,
            "independently rederive both exact commuting combined Rust source owners")
    anchor_model = anchor.check_model()
    compiler_model = compiler.synthetic_semantics()
    interaction = combined.check_composition(compiler.__dict__, anchor.__dict__)
    require(anchor_model.get("differential_checks") == 11328
            and anchor_model.get("semantic_pattern_count") == 18
            and compiler_model.get("synthetic_case_count") == 960
            and compiler_model.get("synthetic_source_lifetime_control_count") == 40
            and compiler_model.get("synthetic_distinct_scanner_runtime_flag_case_count") == 42
            and interaction.get("combined_differential_case_count") == 111552,
            "rerun every independent 11328/960/111552 combined source-only semantic proof")
    private_adapter = derive_adapter(originals["original_adapter"],
                                     originals["adapter_repair_source"])
    require(digest(private_adapter) == BASE_ADAPTER_SHA
            and len(private_adapter) == BASE_ADAPTER_BYTES,
            "independently rederive all four exact preexisting private adapter repairs")
    adapter = originals["comment_adapter"]
    proposal = retired_metadata(wall)
    frozen = build_contract(source_info, protocol_info, history, proposal,
                            composition, anchor_model, compiler_model)
    if mode != "--render-contract":
        require(type(contract_pin) is str,
                "independently pin the complete frozen V35 machine contract")
        contract_raw, _contract_info = live_owner(wall, "contract", CONTRACT, contract_pin)
        expected = (anchor.canonical(frozen) + "\n").encode("utf-8")
        require(contract_raw == expected
                and public_document(anchor, contract_raw, "complete frozen V35 contract")
                == frozen,
                "reject any altered, incomplete, or noncanonical V35 frozen contract")
    require(not wall.live and wall.proposal_metadata_probes == 0
            and wall.proposal_content_opens == 0,
            "close all source descriptors without opening or statting any final proposal")
    clean_imports()
    return {"wall": wall, "contract": frozen, "canonical": anchor.canonical,
            "originals": originals, "adapter": adapter}


def bind_actual_private_adapter_authority(module: types.ModuleType) -> None:
    require(type(module) is types.ModuleType
            and getattr(module, "CORRECTED_ADAPTER_SHA256", None) == BASE_ADAPTER_SHA
            and getattr(module, "CORRECTED_ADAPTER_BYTES", None) == BASE_ADAPTER_BYTES,
            "authenticate the unchanged historical V16 private-adapter kernel contract")
    module.CORRECTED_ADAPTER_SHA256 = ADAPTER_SHA
    module.CORRECTED_ADAPTER_BYTES = ADAPTER_BYTES
    require(module.CORRECTED_ADAPTER_SHA256 == ADAPTER_SHA
            and module.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES,
            "rebind both inherited V16 adapter constants before any native kernel call")


def require_actual_private_overlay_authority(module: types.ModuleType,
                                             bridge_sha: object, bridge_bytes: object,
                                             adapter_sha: object,
                                             adapter_bytes: object) -> None:
    bridge = getattr(module, "COMBINED_VARIANT", None)
    require(getattr(bridge, "sha256", None) == SAFE_BRIDGE_SHA
            and getattr(bridge, "size", None) == SAFE_BRIDGE_BYTES
            and bridge_sha == module.COMBINED_VARIANT.sha256
            and bridge_bytes == module.COMBINED_VARIANT.size
            and module.CORRECTED_ADAPTER_SHA256 == ADAPTER_SHA
            and module.CORRECTED_ADAPTER_BYTES == ADAPTER_BYTES
            and adapter_sha == module.CORRECTED_ADAPTER_SHA256
            and adapter_bytes == module.CORRECTED_ADAPTER_BYTES,
            "independently caller-pin both rebound complete first-party private overlays")


def rejected_actual_overlay_owner_after_rebind() -> None:
    preview = types.ModuleType("_rebar_v35_synthetic_authenticated_actual_kernel")
    preview.COMBINED_VARIANT = types.SimpleNamespace(sha256=SAFE_BRIDGE_SHA,
                                                       size=SAFE_BRIDGE_BYTES)
    preview.CORRECTED_ADAPTER_SHA256 = BASE_ADAPTER_SHA
    preview.CORRECTED_ADAPTER_BYTES = BASE_ADAPTER_BYTES
    bind_actual_private_adapter_authority(preview)
    require_actual_private_overlay_authority(preview, SAFE_BRIDGE_SHA, SAFE_BRIDGE_BYTES,
                                             BASE_ADAPTER_SHA, BASE_ADAPTER_BYTES)


def rejected_actual_historical_bridge_after_rebind() -> None:
    preview = types.ModuleType("_rebar_v35_synthetic_rejected_historical_bridge")
    preview.COMBINED_VARIANT = types.SimpleNamespace(sha256=BRIDGE_SHA,
                                                       size=BRIDGE_BYTES)
    preview.CORRECTED_ADAPTER_SHA256 = BASE_ADAPTER_SHA
    preview.CORRECTED_ADAPTER_BYTES = BASE_ADAPTER_BYTES
    bind_actual_private_adapter_authority(preview)
    require_actual_private_overlay_authority(preview, BRIDGE_SHA, BRIDGE_BYTES,
                                             ADAPTER_SHA, ADAPTER_BYTES)


def hostile_controls(context: dict[str, object]) -> dict[str, object]:
    wall = context["wall"]
    assert isinstance(wall, SourceWall)
    controls: tuple[tuple[str, object], ...] = (
        ("candidate-import", lambda: __import__("candidates.rust_candidate")),
        ("native-installed-engine", lambda: os.open(
            ROOT + "/candidates/_rust_engine.so", os.O_RDONLY | os.O_NOFOLLOW)),
        ("private-root", lambda: os.open(
            "/tmp/rebar-phase2-native-build-v9-rust-v35", os.O_RDONLY | os.O_NOFOLLOW)),
        ("retired-final-content", lambda: os.open(
            ROOT + "/" + RETIRED_PROPOSAL, os.O_RDONLY | os.O_NOFOLLOW)),
        ("retired-final-second-metadata", lambda: os.lstat(ROOT + "/" + RETIRED_PROPOSAL)),
        ("public-final-v3-proposal", lambda: os.open(
            ROOT + "/oracle/phase3/expanded-sealed-holdout-v3.json",
            os.O_RDONLY | os.O_NOFOLLOW)),
        ("hidden-case", lambda: os.open(
            ROOT + "/oracle/phase3/hidden-case-v35.json", os.O_RDONLY | os.O_NOFOLLOW)),
        ("native-loader", lambda: sys.audit("ctypes.dlopen", "forbidden-v35.so")),
        ("compiler-process", lambda: sys.audit("subprocess.Popen", "cargo", [], None, None)),
        ("candidate-process", lambda: sys.audit("os.posix_spawn", "candidate", [], {})),
        ("network", lambda: sys.audit("socket.connect", object(), object())),
        ("clock", lambda: time.perf_counter_ns()),
        ("entropy", lambda: os.urandom(8)),
        ("inherited-descriptor", lambda: os.read(0, 1)),
        ("direct-metadata", lambda: os.stat(ROOT)),
        ("workspace-write", lambda: os.open(
            ROOT + "/" + SOURCE, os.O_WRONLY | os.O_NOFOLLOW)),
        ("directory-enumeration", lambda: os.listdir(ROOT)),
        ("foreign-code", lambda: compile("1", "forbidden-v35-code", "exec")),
        ("actual-overlay-bad-owner-after-rebind",
         rejected_actual_overlay_owner_after_rebind),
        ("actual-old-unsafe-bridge-after-rebind",
         rejected_actual_historical_bridge_after_rebind),
        ("optimized-safe-bridge-replaced-by-historical-scanner-bridge", lambda: require(
            context["contract"]["candidate_sources"]
                ["optimized_native_handle_lease_bridge"]["sha256"] == BRIDGE_SHA,
            "reject replacing the final owning capsule bridge with its historical parent")),
        ("exact-v33-original-pass-replaced-with-historical-v26", lambda: require(
            context["contract"]["preserved_original_31237_case_pass"]
                ["receipt_sha256"] == OWNER_BY_ROLE["v26_original_pass"][2],
            "reject presenting the historical V26 pass as the exact V33 compatibility proof")),
        ("v30-static-audit-misattributed-to-exact-v33-or-v35", lambda: require(
            context["contract"]["authentic_optimized_safe_native_bridge"]
                ["historical_v30_audit_covers_exact_v33_or_proposed_v35"] is True,
            "reject a different-build V30 static audit as exact V33 or new V35 evidence")),
        ("exact-literal-altered-private-engine", lambda: require(
            digest(context["originals"]["literal_engine"][:-1]) == ENGINE_SHA,
            "reject truncated first-party exact-literal engine bytes")),
        ("v33-public-pass-reported-as-failure", lambda: require(
            context["contract"]["preserved_public_v33_10434_complete_pass"]
                ["mismatch_count"] != 0,
            "reject downgrading the genuine 10434-case V33 public PASS")),
        ("exact-literal-unmeasured-reported-qualified", lambda: require(
            context["contract"]["authentic_exact_literal_first_party_architecture"]
                ["candidate_correctness"] == "PASS",
            "reject reporting unmeasured exact-literal correctness as qualified")),
    )
    rejected: list[str] = []
    for label, operation in controls:
        try:
            assert callable(operation)
            operation()
        except BuildFreezeError:
            rejected.append(label)
        else:
            raise BuildFreezeError("an actual hostile source-only control escaped: " + label)
    require(len(rejected) == len(controls) and not wall.live,
            "physically reject every candidate, native, clock, process, and final-case attack")
    # The rejected hostile open is counted separately and does not mean content was read.
    require(wall.proposal_metadata_probes == 0,
            "all final proposal metadata and content operations must remain rejected")
    return {"schema": SCHEMA + "-source-only-self-test", "version": VERSION,
            "status": "PASS", "hostile_controls_rejected": rejected,
            "hostile_control_count": len(rejected), "blocked_effects": dict(wall.blocked),
            "retired_proposal_content_bytes_read": 0,
            "candidate_imports": 0, "candidate_executions": 0,
            "compiler_processes_started": 0, "native_libraries_loaded": 0,
            "clock_samples": 0, "hidden_cases_generated": 0,
            "workspace_mutations": 0, "final_holdout": FINAL_HOLDOUT_STATUS,
            "actual_private_adapter_constants_rebound": True,
            "actual_bad_owner_rejected_after_rebind": True,
            "actual_historical_unsafe_bridge_rejected_after_rebind": True,
            "frozen_contract": context["contract"]}


def checked_label(value: object) -> str:
    require(type(value) is str and value == LABEL
            and all(character.isascii()
                    and (character.isalnum() or character in "-_") for character in value),
            "caller-pin the one exact genuine V35 actual build label")
    return value


def parse_source(arguments: list[str]) -> tuple[str, str, str, str | None]:
    require(type(arguments) is list and bool(arguments) and arguments[0] in SOURCE_MODES,
            "select one physically isolated V35 source-only gate")
    mode = arguments[0]
    pins: dict[str, str] = {}
    for position in range(1, len(arguments), 2):
        require(position + 1 < len(arguments), "each V35 source-only pin needs a value")
        name, value = arguments[position], arguments[position + 1]
        require(name in ("--source-sha256", "--protocol-sha256", "--contract-sha256")
                and name not in pins, "reject repeated or unknown source-only authority")
        pins[name] = hash_pin(value, name)
    expected = {"--source-sha256", "--protocol-sha256"}
    if mode != "--render-contract":
        expected.add("--contract-sha256")
    require(set(pins) == expected, "independently pin every complete V35 source gate")
    return mode, pins["--source-sha256"], pins["--protocol-sha256"], \
        pins.get("--contract-sha256")


def parse_actual(arguments: list[str]) -> dict[str, object]:
    require(type(arguments) is list and arguments and arguments[0] in ACTUAL_MODES,
            "select one genuine, separately authorized, committed V35 dual build")
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--frozen-commit": "frozen_commit",
        "--pushed-commit": "pushed_commit",
        "--label": "label",
        "--combined-engine-sha256": "combined_engine_sha256",
        "--combined-engine-bytes": "combined_engine_bytes",
        "--combined-search-sha256": "combined_search_sha256",
        "--combined-search-bytes": "combined_search_bytes",
        "--safe-bridge-sha256": "safe_bridge_sha256",
        "--safe-bridge-bytes": "safe_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--combined-v2-contract-sha256": "combined_v2_contract_sha256",
        "--combined-v2-application-sha256": "combined_v2_application_sha256",
        "--no-introspection-contract-sha256": "no_introspection_contract_sha256",
        "--no-introspection-application-sha256": "no_introspection_application_sha256",
        "--complete-correction-source-sha256": "complete_correction_source_sha256",
        "--complete-correction-protocol-sha256": "complete_correction_protocol_sha256",
        "--complete-correction-contract-sha256": "complete_correction_contract_sha256",
        "--complete-correction-application-sha256": "complete_correction_application_sha256",
        "--scanner-source-sha256": "scanner_source_sha256",
        "--scanner-protocol-sha256": "scanner_protocol_sha256",
        "--scanner-contract-sha256": "scanner_contract_sha256",
        "--scanner-application-sha256": "scanner_application_sha256",
        "--scoped-source-sha256": "scoped_source_sha256",
        "--scoped-protocol-sha256": "scoped_protocol_sha256",
        "--scoped-contract-sha256": "scoped_contract_sha256",
        "--scoped-application-sha256": "scoped_application_sha256",
        "--exact-literal-source-sha256": "exact_literal_source_sha256",
        "--exact-literal-protocol-sha256": "exact_literal_protocol_sha256",
        "--exact-literal-contract-sha256": "exact_literal_contract_sha256",
        "--exact-literal-application-sha256": "exact_literal_application_sha256",
        "--literal-bridge-source-sha256": "literal_bridge_source_sha256",
        "--literal-bridge-protocol-sha256": "literal_bridge_protocol_sha256",
        "--literal-bridge-contract-sha256": "literal_bridge_contract_sha256",
        "--literal-bridge-application-sha256": "literal_bridge_application_sha256",
        "--native-handle-lease-source-sha256": "native_handle_lease_source_sha256",
        "--native-handle-lease-protocol-sha256": "native_handle_lease_protocol_sha256",
        "--native-handle-lease-contract-sha256": "native_handle_lease_contract_sha256",
        "--native-handle-lease-application-sha256": "native_handle_lease_application_sha256",
        "--exact-v33-original-pass-sha256": "exact_v33_original_pass_sha256",
        "--exact-v33-performance-receipt-sha256": "exact_v33_performance_receipt_sha256",
        "--exact-v33-performance-summary-sha256": "exact_v33_performance_summary_sha256",
        "--historical-v30-static-audit-sha256": "historical_v30_static_audit_sha256",
        "--comment-source-sha256": "comment_source_sha256",
        "--comment-protocol-sha256": "comment_protocol_sha256",
        "--comment-contract-sha256": "comment_contract_sha256",
        "--comment-application-sha256": "comment_application_sha256",
        "--comment-v1-failure-sha256": "comment_v1_failure_sha256",
        "--v28-publication-sha256": "v28_publication_sha256",
        "--v28-root-sha256": "v28_root_sha256",
        "--v30-publication-sha256": "v30_publication_sha256",
        "--v30-root-sha256": "v30_root_sha256",
        "--v32-source-sha256": "v32_source_sha256",
        "--v32-protocol-sha256": "v32_protocol_sha256",
        "--v32-contract-sha256": "v32_contract_sha256",
        "--v32-failure-sha256": "v32_failure_sha256",
        "--v33-source-sha256": "v33_source_sha256",
        "--v33-protocol-sha256": "v33_protocol_sha256",
        "--v33-contract-sha256": "v33_contract_sha256",
        "--v33-publication-sha256": "v33_publication_sha256",
        "--v33-root-sha256": "v33_root_sha256",
        "--v33-public-pass-sha256": "v33_public_pass_sha256",
        "--v26-original-pass-sha256": "v26_original_pass_sha256",
        "--v26-public-gate-sha256": "v26_public_gate_sha256",
        "--v27-public-gate-sha256": "v27_public_gate_sha256",
        "--v28-public-gate-sha256": "v28_public_gate_sha256",
        "--v26-publication-sha256": "v26_publication_sha256",
        "--v26-root-sha256": "v26_root_sha256",
        "--v27-publication-sha256": "v27_publication_sha256",
        "--v27-root-sha256": "v27_root_sha256",
        "--v25-failure-sha256": "v25_failure_sha256",
        "--strict-audit-failure-sha256": "strict_audit_failure_sha256",
    }
    result: dict[str, object] = {"mode": arguments[0], "owned_source_sha256": [],
                                 "root_authorized": False,
                                 "frozen_committed_pushed": False}
    position = 1
    while position < len(arguments):
        flag = arguments[position]
        if flag in ("--root-authorized", "--frozen-committed-pushed"):
            name = flag[2:].replace("-", "_")
            require(result[name] is False, "reject duplicate root-only build authorization")
            result[name] = True
            position += 1
            continue
        require(position + 1 < len(arguments), "each exact V35 actual pin requires a value")
        value = arguments[position + 1]
        if flag == "--owned-source-sha256":
            require(type(value) is str, "caller-pin one complete immutable canonical owner")
            assert isinstance(result["owned_source_sha256"], list)
            result["owned_source_sha256"].append(value)
            position += 2
            continue
        require(flag in mapping and mapping[flag] not in result,
                "reject unknown, duplicate, or missing V35 root-build authority")
        name = mapping[flag]
        if name.endswith("_bytes"):
            require(type(value) is str and value.isascii() and value.isdecimal(),
                    "caller-pin each exact private-overlay byte count")
            result[name] = int(value)
        elif name in ("frozen_commit", "pushed_commit"):
            result[name] = commit_pin(value, name)
        elif name == "label":
            result[name] = checked_label(value)
        else:
            result[name] = hash_pin(value, name)
        position += 2
    require(set(result) == set(mapping.values())
            | {"mode", "owned_source_sha256", "root_authorized", "frozen_committed_pushed"},
            "root must caller-pin every independent V35 input before any compiler starts")
    require(result["root_authorized"] is True
            and result["frozen_committed_pushed"] is True
            and result["frozen_commit"] == result["pushed_commit"],
            "root may build only the exact fully committed and pushed V35 freeze")
    expected = {
        "combined_engine_sha256": ENGINE_SHA, "combined_engine_bytes": ENGINE_BYTES,
        "combined_search_sha256": SEARCH_SHA, "combined_search_bytes": SEARCH_BYTES,
        "safe_bridge_sha256": SAFE_BRIDGE_SHA, "safe_bridge_bytes": SAFE_BRIDGE_BYTES,
        "corrected_adapter_sha256": ADAPTER_SHA, "corrected_adapter_bytes": ADAPTER_BYTES,
        "combined_v2_contract_sha256": OWNER_BY_ROLE["combined_v2_contract"][2],
        "combined_v2_application_sha256": OWNER_BY_ROLE["combined_v2_application"][2],
        "no_introspection_contract_sha256": OWNER_BY_ROLE["no_introspection_contract"][2],
        "no_introspection_application_sha256": OWNER_BY_ROLE["no_introspection_application"][2],
        "complete_correction_source_sha256": OWNER_BY_ROLE["complete_semantic_source"][2],
        "complete_correction_protocol_sha256": OWNER_BY_ROLE["complete_semantic_protocol"][2],
        "complete_correction_contract_sha256": OWNER_BY_ROLE["complete_semantic_contract"][2],
        "complete_correction_application_sha256": OWNER_BY_ROLE["complete_semantic_application"][2],
        "scanner_source_sha256": OWNER_BY_ROLE["scanner_bridge_source"][2],
        "scanner_protocol_sha256": OWNER_BY_ROLE["scanner_bridge_protocol"][2],
        "scanner_contract_sha256": OWNER_BY_ROLE["scanner_bridge_contract"][2],
        "scanner_application_sha256": OWNER_BY_ROLE["scanner_bridge_application"][2],
        "scoped_source_sha256": OWNER_BY_ROLE["scoped_engine_source"][2],
        "scoped_protocol_sha256": OWNER_BY_ROLE["scoped_engine_protocol"][2],
        "scoped_contract_sha256": OWNER_BY_ROLE["scoped_engine_contract"][2],
        "scoped_application_sha256": OWNER_BY_ROLE["scoped_engine_application"][2],
        "exact_literal_source_sha256": OWNER_BY_ROLE["literal_source"][2],
        "exact_literal_protocol_sha256": OWNER_BY_ROLE["literal_protocol"][2],
        "exact_literal_contract_sha256": OWNER_BY_ROLE["literal_contract"][2],
        "exact_literal_application_sha256": OWNER_BY_ROLE["literal_application"][2],
        "literal_bridge_source_sha256": OWNER_BY_ROLE["literal_bridge_source"][2],
        "literal_bridge_protocol_sha256": OWNER_BY_ROLE["literal_bridge_protocol"][2],
        "literal_bridge_contract_sha256": OWNER_BY_ROLE["literal_bridge_contract"][2],
        "literal_bridge_application_sha256": OWNER_BY_ROLE["literal_bridge_application"][2],
        "native_handle_lease_source_sha256": OWNER_BY_ROLE["handle_lease_source"][2],
        "native_handle_lease_protocol_sha256": OWNER_BY_ROLE["handle_lease_protocol"][2],
        "native_handle_lease_contract_sha256": OWNER_BY_ROLE["handle_lease_contract"][2],
        "native_handle_lease_application_sha256": OWNER_BY_ROLE["handle_lease_application"][2],
        "exact_v33_original_pass_sha256": OWNER_BY_ROLE["exact_v33_original_pass"][2],
        "exact_v33_performance_receipt_sha256":
            OWNER_BY_ROLE["exact_v33_public_performance_receipt"][2],
        "exact_v33_performance_summary_sha256":
            OWNER_BY_ROLE["exact_v33_public_performance_summary"][2],
        "historical_v30_static_audit_sha256": OWNER_BY_ROLE["historical_v30_static_audit"][2],
        "comment_source_sha256": OWNER_BY_ROLE["comment_adapter_v2_source"][2],
        "comment_protocol_sha256": OWNER_BY_ROLE["comment_adapter_v2_protocol"][2],
        "comment_contract_sha256": OWNER_BY_ROLE["comment_adapter_v2_contract"][2],
        "comment_application_sha256": OWNER_BY_ROLE["comment_adapter_v2_application"][2],
        "comment_v1_failure_sha256": OWNER_BY_ROLE["comment_adapter_v1_failure"][2],
        "v26_publication_sha256": OWNER_BY_ROLE["v26_build_publication"][2],
        "v26_root_sha256": OWNER_BY_ROLE["v26_build_root"][2],
        "v27_publication_sha256": OWNER_BY_ROLE["v27_build_publication"][2],
        "v27_root_sha256": OWNER_BY_ROLE["v27_build_root"][2],
        "v28_publication_sha256": OWNER_BY_ROLE["v28_build_publication"][2],
        "v28_root_sha256": OWNER_BY_ROLE["v28_build_root"][2],
        "v30_publication_sha256": OWNER_BY_ROLE["v30_build_publication"][2],
        "v30_root_sha256": OWNER_BY_ROLE["v30_build_root"][2],
        "v32_source_sha256": OWNER_BY_ROLE["v32_build_source"][2],
        "v32_protocol_sha256": OWNER_BY_ROLE["v32_build_protocol"][2],
        "v32_contract_sha256": OWNER_BY_ROLE["v32_build_contract"][2],
        "v32_failure_sha256": OWNER_BY_ROLE["v32_build_failure"][2],
        "v33_source_sha256": OWNER_BY_ROLE["v33_build_source"][2],
        "v33_protocol_sha256": OWNER_BY_ROLE["v33_build_protocol"][2],
        "v33_contract_sha256": OWNER_BY_ROLE["v33_build_contract"][2],
        "v33_publication_sha256": OWNER_BY_ROLE["v33_build_publication"][2],
        "v33_root_sha256": OWNER_BY_ROLE["v33_build_root"][2],
        "v33_public_pass_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
        "v26_original_pass_sha256": OWNER_BY_ROLE["v26_original_pass"][2],
        "v26_public_gate_sha256": OWNER_BY_ROLE["v26_public_gate"][2],
        "v27_public_gate_sha256": OWNER_BY_ROLE["v27_public_gate"][2],
        "v28_public_gate_sha256": OWNER_BY_ROLE["v28_public_gate"][2],
        "v25_failure_sha256": OWNER_BY_ROLE["v25_full_failure"][2],
        "strict_audit_failure_sha256": OWNER_BY_ROLE["strict_audit_failure"][2],
        "label": LABEL,
    }
    for name, value in expected.items():
        require(result.get(name) == value, "reject substituted V35 actual authority: " + name)
    provided = result["owned_source_sha256"]
    genuine = {row[1] + "=" + row[2] for row in CANONICAL_OWNERS}
    require(type(provided) is list and len(provided) == 9
            and len(set(provided)) == 9 and set(provided) == genuine,
            "independently caller-pin all nine complete canonical Rust source owners")
    return result


def read_actual_owner(row: tuple[object, ...]) -> tuple[bytes, dict[str, object]]:
    role, relative, expected, count, inode = row
    descriptor = os.open(ROOT + "/" + str(relative),
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode)
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_dev == DEVICE and before.st_ino == inode
                and before.st_size == count and before.st_uid == os.geteuid()
                and before.st_nlink == 1,
                "reject a substituted exact actual-build owner: " + str(role))
        chunks: list[bytes] = []
        remaining = int(count)
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            require(bool(chunk), "reject a truncated authenticated actual source owner")
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"", "reject an expanded actual source owner")
        after = os.fstat(descriptor)
        require(all(getattr(before, key) == getattr(after, key)
                    for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                "st_mtime_ns", "st_ctime_ns")),
                "reject an actual source owner changed during descriptor authentication")
        payload = b"".join(chunks)
        require(digest(payload) == expected, "reject changed complete actual source bytes")
        return payload, {"role": role, "path": relative, "sha256": expected,
                         "bytes": count, "device": before.st_dev,
                         "inode": before.st_ino, "mode": "0600", "nlink": 1,
                         "uid": before.st_uid}
    finally:
        os.close(descriptor)


def actual_self(relative: str, pin: str) -> tuple[bytes, dict[str, object]]:
    descriptor = os.open(ROOT + "/" + relative,
                         os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        identity = os.fstat(descriptor)
        require(stat.S_ISREG(identity.st_mode)
                and stat.S_IMODE(identity.st_mode) == 0o600
                and identity.st_dev == DEVICE and identity.st_uid == os.geteuid()
                and identity.st_nlink == 1 and 0 < identity.st_size <= MAX_OWNER_BYTES,
                "reject a substituted actual V35 frozen owner")
        raw = b""
        while len(raw) < identity.st_size:
            part = os.read(descriptor, min(65536, identity.st_size - len(raw)))
            require(bool(part), "a caller-pinned actual V35 owner ended early")
            raw += part
        require(os.read(descriptor, 1) == b"" and digest(raw) == pin,
                "reject an incomplete or substituted root-authorized V35 owner")
        return raw, {"path": relative, "sha256": pin, "bytes": identity.st_size,
                     "device": identity.st_dev, "inode": identity.st_ino,
                     "mode": "0600", "uid": identity.st_uid, "nlink": identity.st_nlink}
    finally:
        os.close(descriptor)


def snapshot_actual_runtime_targets() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for role, relative, expected, size, inode, mode in ACTUAL_RUNTIME_TARGETS:
        descriptor = os.open(ROOT + "/" + relative,
                             os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode)
                    and stat.S_IMODE(before.st_mode) == mode
                    and before.st_dev == DEVICE and before.st_ino == inode
                    and before.st_size == size and before.st_uid == os.geteuid()
                    and before.st_nlink == 1,
                    "reject a substituted original runtime target: " + role)
            hashed = hashlib.sha256()
            remaining = size
            while remaining:
                part = os.read(descriptor, min(remaining, 65536))
                require(bool(part), "an original runtime target ended early: " + role)
                hashed.update(part)
                remaining -= len(part)
            require(os.read(descriptor, 1) == b"" and hashed.hexdigest() == expected,
                    "authenticate every complete unchanged original runtime target")
            after = os.fstat(descriptor)
            require(all(getattr(before, key) == getattr(after, key)
                        for key in ("st_dev", "st_ino", "st_size", "st_nlink",
                                    "st_mtime_ns", "st_ctime_ns")),
                    "an original runtime target changed during actual authentication")
            result[role] = {"path": relative, "sha256": expected, "bytes": size,
                            "device": before.st_dev, "inode": before.st_ino,
                            "mode": "0755" if mode == 0o755 else "0600",
                            "uid": before.st_uid, "nlink": before.st_nlink,
                            "mtime_ns": before.st_mtime_ns,
                            "ctime_ns": before.st_ctime_ns}
        finally:
            os.close(descriptor)
    require(len(result) == 5,
            "preserve the original engine, bridge, adapter, and both installed native files")
    return result


def actual_evidence_names(label: str, failed: bool) -> tuple[str, str]:
    stem = "native-source-build-v35-rust-" + checked_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def actual_root_receipt_name(label: str) -> str:
    return "native-source-build-v35-rust-" + checked_label(label) \
        + "-root-provenance-receipt.json"


def actual_module(role: str, payload: bytes, name: str) -> types.ModuleType:
    owner = OWNER_BY_ROLE[role]
    require(digest(payload) == owner[2] and len(payload) == owner[3]
            and name not in sys.modules,
            "execute only complete independently authenticated actual build kernels")
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + owner[1]
    sys.modules[name] = module
    try:
        exec(compile(payload, module.__file__, "exec", dont_inherit=True), module.__dict__)
        return module
    except BaseException:
        sys.modules.pop(name, None)
        raise


def capture_actual_root(workdir: str,
                        phases: list[dict[str, object]]) -> dict[str, object]:
    """Capture both genuine native inodes without enumerating or loading a root."""
    flags = (os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW)
    root_descriptor = os.open(workdir, flags)
    try:
        root = os.fstat(root_descriptor)
        named = os.stat(workdir, follow_symlinks=False)
        require(stat.S_ISDIR(root.st_mode) and stat.S_IMODE(root.st_mode) == 0o700
                and root.st_uid == os.geteuid()
                and (root.st_dev, root.st_ino) == (named.st_dev, named.st_ino)
                and type(phases) is list and len(phases) == 2,
                "capture one genuine owner-only actual V35 dual-build root")
        rows: list[dict[str, object]] = []
        distinct: set[tuple[int, int]] = set()
        for index, phase in enumerate(phases):
            require(type(phase) is dict and phase.get("name") == PHASES[index],
                    "authenticate both ordered independently completed V35 phases")
            phase_descriptor = os.open(PHASES[index], flags, dir_fd=root_descriptor)
            try:
                phase_identity = os.fstat(phase_descriptor)
                require(stat.S_ISDIR(phase_identity.st_mode)
                        and stat.S_IMODE(phase_identity.st_mode) == 0o700
                        and phase_identity.st_uid == os.geteuid(),
                        "reject a substituted or publicly accessible private build phase")
                native_descriptor = os.open("native", flags, dir_fd=phase_descriptor)
                try:
                    native_identity = os.fstat(native_descriptor)
                    outputs = phase.get("native_outputs")
                    require(stat.S_ISDIR(native_identity.st_mode)
                            and stat.S_IMODE(native_identity.st_mode) == 0o700
                            and native_identity.st_uid == os.geteuid()
                            and type(outputs) is dict
                            and set(outputs) == {"engine", "bridge"},
                            "capture precisely two genuine private native ELF outputs")
                    artifacts: list[dict[str, object]] = []
                    for role, filename in (
                        ("engine", "_rust_engine.so"),
                        ("bridge", "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
                    ):
                        output = outputs[role]
                        require(type(output) is dict
                                and output.get("file_name") == filename
                                and type(output.get("sha256")) is str
                                and type(output.get("size_bytes")) is int,
                                "reject a substituted actual private native output: " + role)
                        artifact_descriptor = os.open(
                            filename, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                            dir_fd=native_descriptor,
                        )
                        try:
                            artifact = os.fstat(artifact_descriptor)
                            identity = (artifact.st_dev, artifact.st_ino)
                            require(stat.S_ISREG(artifact.st_mode)
                                    and artifact.st_uid == os.geteuid()
                                    and artifact.st_nlink == 1
                                    and identity not in distinct
                                    and (artifact.st_dev, artifact.st_ino,
                                         artifact.st_size)
                                    == (output.get("device"), output.get("inode"),
                                        output.get("size_bytes")),
                                    "reject swapped or cross-phase native artifact: " + role)
                            distinct.add(identity)
                            artifacts.append({
                                "role": role, "file_name": filename,
                                "absolute_path": workdir + "/" + PHASES[index]
                                    + "/native/" + filename,
                                "sha256": output["sha256"], "bytes": artifact.st_size,
                                "device": artifact.st_dev, "inode": artifact.st_ino,
                                "mode": format(stat.S_IMODE(artifact.st_mode), "04o"),
                                "uid": artifact.st_uid, "nlink": artifact.st_nlink,
                                "native_loaded": False,
                                "hash_provenance":
                                    "COMPLETE INDEPENDENT FIRST-PARTY ELF AUDIT",
                            })
                        finally:
                            os.close(artifact_descriptor)
                finally:
                    os.close(native_descriptor)
                rows.append({"name": PHASES[index],
                             "absolute_path": workdir + "/" + PHASES[index],
                             "device": phase_identity.st_dev,
                             "inode": phase_identity.st_ino,
                             "uid": phase_identity.st_uid,
                             "mode": format(stat.S_IMODE(phase_identity.st_mode), "04o"),
                             "native_outputs": artifacts})
            finally:
                os.close(phase_descriptor)
        require(len(distinct) == 4,
                "capture all four genuinely distinct independently built ELF identities")
        return {"path": workdir,
                "prefix": "/tmp/rebar-phase2-native-build-v9-rust-",
                "device": root.st_dev, "inode": root.st_ino,
                "uid": root.st_uid, "mode": "0700", "phase_count": 2,
                "nofollow_directory_descriptor": True,
                "descriptor_opened_during_live_verification": True,
                "directory_scanned": False, "phases": rows}
    finally:
        os.close(root_descriptor)


def copy_four_overlays(module: types.ModuleType, workdir: str, family: str,
                       phase: str, originals: dict[str, bytes]) -> dict[str, object]:
    require(module._ACTIVE is not None,
            "require the genuine root-authorized V35 28-process native build kernel")
    state = module._ACTIVE
    kernel = state["kernel"]
    low_level = state["v9"]
    expected_paths = {owner.path for owner in module.RUST_OWNERS}
    require(family == FAMILY and phase in PHASES and set(originals) == expected_paths
            and (workdir, phase) not in module._APPLIED_PHASES,
            "require exactly nine immutable first-party owners in a fresh V35 phase")
    paths = low_level.phase_paths(workdir, family, phase)
    overlays = {
        "candidates/rust/src/lib.rs": (state["combined_engine"], ENGINE_SHA,
                                         ENGINE_BYTES, "combined-search-and-parser-engine"),
        "candidates/rust/src/search.rs": (state["combined_search"], SEARCH_SHA,
                                            SEARCH_BYTES, "combined-mandatory-anchor-search"),
        module.BRIDGE_PATH: (state["combined_bridge"], SAFE_BRIDGE_SHA,
                             SAFE_BRIDGE_BYTES, "optimized-literal-native-handle-lease-bridge"),
        module.PUBLIC_PATH: (state["corrected_adapter"], ADAPTER_SHA,
                             ADAPTER_BYTES, "corrected-first-party-public-adapter"),
    }
    rows: dict[str, object] = {}
    for original in sorted(module.RUST_OWNERS, key=lambda row: row.path):
        raw = originals[original.path]
        require(type(raw) is bytes and digest(raw) == original.sha256
                and len(raw) == original.size,
                "preserve every exact original immutable first-party Rust owner")
        if original.path in overlays:
            continue
        target = paths["source"] / original.path
        kernel.mkdir_private(target.parent)
        item = kernel.write_fresh(target, raw, synchronize=False)
        item["path"] = low_level.sanitized(item["path"], workdir, family)
        rows[original.path] = item
    require(len(rows) == 5,
            "preserve five unchanged canonical owners in each private source phase")
    for path, (payload, expected_sha, expected_bytes, role) in overlays.items():
        require(type(payload) is bytes and digest(payload) == expected_sha
                and len(payload) == expected_bytes,
                "authenticate one exact complete first-party private V35 overlay")
        if path in ("candidates/rust/src/lib.rs", "candidates/rust/src/search.rs"):
            audit = kernel.audit_native_source(payload, family=FAMILY, location=path)
            require(type(audit) is dict and audit.get("external_regex_dependency_count") == 0
                    and audit.get("cross_family_dependency_count") == 0,
                    "reject a delegated, borrowed, or external Rust matching engine")
        if path == module.BRIDGE_PATH:
            require(b"rust_bound_get_signature" not in payload
                    and b'PyImport_ImportModule("inspect")' not in payload
                    and payload.count(b"rust_literal_next_contiguous(") == 3
                    and payload.count(b"static void rust_native_handle_destructor(") == 1
                    and payload.count(b"rust_native_handle_owner(handle)") == 2
                    and payload.count(b"iterator->handle_owner = Py_NewRef(handle_owner);") == 1
                    and payload.count(b"Py_CLEAR(iterator->handle_owner);") == 1
                    and b"PyLong_AsVoidPtr(" not in payload
                    and b"PyLong_FromVoidPtr(" not in payload,
                    "copy only the accelerated, capsule-owned, no-inspection native bridge")
        target = paths["source"] / path
        kernel.mkdir_private(target.parent)
        saved = kernel.write_fresh(target, payload, synchronize=True)
        verified, reread = kernel.authenticate_file(
            target, expected=expected_sha, maximum=MAX_OWNER_BYTES,
            exact_size=expected_bytes, capture=True,
        )
        require(type(reread) is bytes and reread == payload
                and saved.get("sha256") == expected_sha
                and saved.get("bytes") == expected_bytes
                and saved.get("device") == verified.get("device")
                and saved.get("inode") == verified.get("inode")
                and saved.get("exclusive_creation") is True
                and saved.get("file_fsync_completed") is True
                and stat.S_IMODE(os.lstat(target).st_mode) == 0o600,
                "exclusively create, synchronize, and reread one genuine private overlay")
        rows[path] = {
            "path": low_level.sanitized(verified["path"], workdir, family),
            "sha256": verified["sha256"], "bytes": verified["size_bytes"],
            "device": verified["device"], "inode": verified["inode"],
            "exclusive_creation": True, "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "source_overlay": {"status": "PASS", "phase": phase, "role": role,
                               "source_apply_count": 1, "derived_sha256": expected_sha,
                               "derived_source_sha256": expected_sha,
                               "derived_bytes": expected_bytes,
                               "derived_source_bytes": expected_bytes,
                               "candidate_original_modified": False,
                               "canonical_candidate_modified": False},
        }
    require(set(rows) == expected_paths,
            "close one independent five-original, four-overlay Rust source phase")
    for row in CANONICAL_OWNERS:
        read_actual_owner(row)
    module._APPLIED_PHASES.add((workdir, phase))
    return rows


def run_actual(options: dict[str, object]) -> dict[str, object]:
    require(options.get("root_authorized") is True
            and options.get("frozen_committed_pushed") is True
            and options.get("frozen_commit") == options.get("pushed_commit")
            and options.get("label") == LABEL,
            "only root may run the separately committed and pushed complete V35 build")
    runtime_before = snapshot_actual_runtime_targets()
    source_raw, source_info = actual_self(SOURCE, str(options["source_sha256"]))
    protocol_raw, protocol_info = actual_self(PROTOCOL, str(options["protocol_sha256"]))
    contract_raw, contract_info = actual_self(CONTRACT, str(options["contract_sha256"]))
    require(source_raw.startswith(b"#!/usr/bin/env python3\n")
            and FINAL_HOLDOUT_STATUS.encode("ascii") in protocol_raw
            and FINAL_HOLDOUT_STATUS.encode("ascii") in contract_raw,
            "require the exact complete invalidated-final V35 source freeze")
    raw: dict[str, bytes] = {}
    identities: dict[str, dict[str, object]] = {}
    for row in STATIC_OWNERS:
        payload, identity = read_actual_owner(row)
        raw[row[0]] = payload
        identities[row[0]] = identity
    canonical_before = {row[1]: identities[row[0]] for row in CANONICAL_OWNERS}
    require(len(canonical_before) == 9, "authenticate all nine immutable original owners")
    private_adapter = derive_adapter(raw["original_adapter"], raw["adapter_repair_source"])
    require(digest(private_adapter) == BASE_ADAPTER_SHA
            and len(private_adapter) == BASE_ADAPTER_BYTES,
            "reauthenticate the four exact historical private adapter repairs")
    adapter = raw["comment_adapter"]
    require(digest(adapter) == ADAPTER_SHA and len(adapter) == ADAPTER_BYTES,
            "authenticate the exclusive seven-repair corrected public comment adapter")

    # Actual mode deliberately loads only the already pinned operational kernel.
    # Its authenticated V9/V7/V4 descendants perform the complete native ELF audit.
    kernel_name = "_rebar_v35_authenticated_actual_v16_native_kernel"
    module = actual_module("actual_v16_kernel", raw["actual_v16_kernel"], kernel_name)
    require(module.SCHEMA == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
            and module.VERSION == 16 and module.FAMILY == FAMILY
            and module.PHASES == PHASES and module.PROCESS_NAMES == PROCESS_NAMES
            and callable(module.run_build) and callable(module.verify_reproduced_phases),
            "reject a dummy, delegated, or substituted first-party 28-process build kernel")
    frozen = module.json.loads(contract_raw)
    require(type(frozen) is dict and frozen.get("schema") == SCHEMA + "-source-freeze"
            and frozen.get("final_holdout") == FINAL_HOLDOUT_STATUS
            and frozen.get("source", {}).get("sha256") == options["source_sha256"]
            and frozen.get("protocol", {}).get("sha256") == options["protocol_sha256"]
            and frozen.get("candidate_sources", {}).get("combined_engine", {})
                .get("sha256") == ENGINE_SHA
            and frozen.get("candidate_sources", {}).get("combined_search", {})
                .get("sha256") == SEARCH_SHA
            and frozen.get("candidate_sources", {}).get("no_external_introspection_bridge", {})
                .get("sha256") == SAFE_BRIDGE_SHA
            and frozen.get("candidate_sources", {})
                .get("optimized_native_handle_lease_bridge", {}).get("sha256")
                    == SAFE_BRIDGE_SHA
            and frozen.get("candidate_sources", {}).get("corrected_comment_adapter", {})
                .get("sha256") == ADAPTER_SHA
            and frozen.get("preserved_original_31237_case_pass", {})
                .get("verified_passing_case_count") == 31237
            and frozen.get("preserved_public_v28_1145_disjoint_partition", {})
                .get("mismatch_count") == 1145
            and frozen.get("preserved_public_v33_10434_complete_pass", {})
                .get("verified_passing_case_count") == 10434
            and frozen.get("preserved_public_v33_10434_complete_pass", {})
                .get("mismatch_count") == 0
            and frozen.get("authentic_exact_literal_first_party_architecture", {})
                .get("engine_sha256") == ENGINE_SHA
            and frozen.get("authentic_optimized_safe_native_bridge", {})
                .get("optimized_safe_bridge_sha256") == SAFE_BRIDGE_SHA
            and frozen.get("authentic_optimized_safe_native_bridge", {})
                .get("handle_lease_application_sha256")
                    == OWNER_BY_ROLE["handle_lease_application"][2],
            "authenticate the exact canonical V35 source contract before actual compilation")

    module.SCHEMA = SCHEMA
    module.VERSION = VERSION
    module.SOURCE_PATH = SOURCE
    module.PROTOCOL_PATH = PROTOCOL
    module.CONTRACT_PATH = CONTRACT
    module.COMBINED_VARIANT = module.Owner(
        OWNER_BY_ROLE["optimized_safe_bridge"][1], SAFE_BRIDGE_SHA, SAFE_BRIDGE_BYTES,
    )
    module.BUFFER_VARIANT = module.COMBINED_VARIANT
    bind_actual_private_adapter_authority(module)
    module.checked_label = checked_label
    module.evidence_names = actual_evidence_names
    captures: dict[str, object] = {}

    def context(source_pin: str, protocol_pin: str,
                contract_pin: str) -> tuple[dict[str, object], dict[str, object]]:
        require((source_pin, protocol_pin, contract_pin)
                == (options["source_sha256"], options["protocol_sha256"],
                    options["contract_sha256"]),
                "reject substituted or incomplete actual V35 triple authority")
        return {"schema": SCHEMA + "-verified-actual-context", "status": "PASS",
                "family": FAMILY, "source": source_info, "protocol": protocol_info,
                "contract": contract_info, "final_holdout": FINAL_HOLDOUT_STATUS}, {
                    "originals": {row[1]: raw[row[0]] for row in CANONICAL_OWNERS},
                    "combined_bridge": raw["optimized_safe_bridge"],
                    "corrected_adapter": adapter,
                    "low_level_v9_source": raw["actual_v9_kernel"],
                    "combined_engine": raw["literal_engine"],
                    "combined_search": raw["combined_v2_search"],
                }

    original_expected = module.expected_source_owner

    def expected(path: str) -> tuple[str, int]:
        if path == "candidates/rust/src/lib.rs":
            return ENGINE_SHA, ENGINE_BYTES
        if path == "candidates/rust/src/search.rs":
            return SEARCH_SHA, SEARCH_BYTES
        return original_expected(path)

    previous_verify = module.verify_reproduced_phases

    def verify(low_level: types.ModuleType, native: types.ModuleType, workdir: str,
               phases: list[dict[str, object]],
               operations: list[dict[str, object]]) -> dict[str, object]:
        require(type(operations) is list and len(operations) == 28
                and not captures, "require 28 distinct real successful V35 process roles")
        proof = previous_verify(low_level, native, workdir, phases, operations)
        require(proof.get("status") == "PASS"
                and proof.get("independent_fresh_phase_count") == 2
                and proof.get("source_owners_per_phase") == 9
                and proof.get("unique_process_count") == 28
                and proof.get("combined_bridge_overlay_count") == 2
                and proof.get("corrected_public_adapter_overlay_count") == 2
                and proof.get("combined_bridge_sha256") == SAFE_BRIDGE_SHA
                and proof.get("combined_bridge_bytes") == SAFE_BRIDGE_BYTES
                and proof.get("corrected_public_adapter_sha256") == ADAPTER_SHA
                and proof.get("byte_identical") is True
                and proof.get("native_libraries_loaded") == 0
                and type(proof.get("native_outputs")) is dict
                and set(proof["native_outputs"]) == {"engine", "bridge"},
                "require two actual independent byte-identical engine and safe bridge ELFs")
        phase_owners: list[dict[str, object]] = []
        all_inodes: set[tuple[int, int]] = set()
        pids: set[int] = set()
        for index, operation in enumerate(operations):
            require(operation.get("name") == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                    and type(operation.get("pid")) is int
                    and operation["pid"] not in pids
                    and operation.get("exit_status") == 0,
                    "require every compiler and native-symbol inspection role exactly once")
            pids.add(operation["pid"])
        for index, phase in enumerate(phases):
            require(phase.get("name") == PHASES[index],
                    "preserve both ordered independently owned private source phases")
            owners = phase.get("fresh_source_owners")
            require(type(owners) is dict and len(owners) == 9,
                    "require nine independent source owners in each actual V35 phase")
            for path, owner in owners.items():
                require(type(owner) is dict and type(owner.get("device")) is int
                        and type(owner.get("inode")) is int
                        and (owner["device"], owner["inode"]) not in all_inodes,
                        "no private source may be borrowed or hard-linked across phases")
                all_inodes.add((owner["device"], owner["inode"]))
            for path, expected_sha, expected_bytes in (
                ("candidates/rust/src/lib.rs", ENGINE_SHA, ENGINE_BYTES),
                ("candidates/rust/src/search.rs", SEARCH_SHA, SEARCH_BYTES),
                (module.BRIDGE_PATH, SAFE_BRIDGE_SHA, SAFE_BRIDGE_BYTES),
                (module.PUBLIC_PATH, ADAPTER_SHA, ADAPTER_BYTES),
            ):
                item = owners.get(path)
                overlay = item.get("source_overlay") if type(item) is dict else None
                require(type(overlay) is dict and overlay.get("status") == "PASS"
                        and overlay.get("phase") == PHASES[index]
                        and overlay.get("source_apply_count") == 1
                        and overlay.get("derived_sha256") == expected_sha
                        and overlay.get("derived_bytes") == expected_bytes,
                        "prove every authentic independently applied private source overlay")
            phase_owners.append({"phase": PHASES[index], "owners": dict(owners)})
        require(len(all_inodes) == 18 and len(pids) == 28,
                "require 18 genuine private source identities and 28 real process identities")
        root = capture_actual_root(workdir, phases)
        require(root.get("path") == workdir and root.get("phase_count") == 2
                and root.get("directory_scanned") is False
                and workdir.startswith("/tmp/rebar-phase2-native-build-v9-rust-"),
                "preserve all four actual native ELF identities in the fresh private root")
        proof.update({"unchanged_source_owners_per_phase": 5,
                      "combined_engine_overlay_count": 2,
                      "combined_search_overlay_count": 2,
                      "safe_no_external_introspection_bridge_overlay_count": 2,
                      "corrected_public_adapter_overlay_count": 2,
                      "total_private_source_overlay_apply_count": 8,
                      "distinct_private_source_identity_count": 18,
                      "final_holdout": FINAL_HOLDOUT_STATUS})
        captures.update({"root": root,
                         "process_ids": sorted(pids), "private_source_owners": phase_owners,
                         "native_outputs": proof["native_outputs"]})
        return proof

    def publish(kernel: types.ModuleType,
                report: dict[str, object]) -> dict[str, object]:
        require(report.get("status") in ("PASS", "FAIL")
                and report.get("family") == FAMILY and report.get("label") == LABEL,
                "publish only one complete genuine root-authorized V35 build outcome")
        complete = dict(report)
        complete.update({
            "schema": SCHEMA + "-actual-combined-dual-source-build",
            "version": VERSION,
            "frozen_commit": options["frozen_commit"],
            "pushed_commit": options["pushed_commit"],
            "combined_engine_sha256": ENGINE_SHA,
            "combined_engine_bytes": ENGINE_BYTES,
            "combined_search_sha256": SEARCH_SHA,
            "combined_search_bytes": SEARCH_BYTES,
            "historical_complete_scanner_bridge_sha256": BRIDGE_SHA,
            "historical_complete_scanner_bridge_bytes": BRIDGE_BYTES,
            "safe_no_external_introspection_bridge_sha256": SAFE_BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": SAFE_BRIDGE_BYTES,
            "materialized_complete_bridge_sha256": SAFE_BRIDGE_SHA,
            "materialized_complete_bridge_bytes": SAFE_BRIDGE_BYTES,
            "optimized_native_handle_lease_bridge_sha256": SAFE_BRIDGE_SHA,
            "optimized_native_handle_lease_bridge_bytes": SAFE_BRIDGE_BYTES,
            "literal_bridge_application_sha256":
                OWNER_BY_ROLE["literal_bridge_application"][2],
            "native_handle_lease_application_sha256":
                OWNER_BY_ROLE["handle_lease_application"][2],
            "exact_v33_original_pass_sha256":
                OWNER_BY_ROLE["exact_v33_original_pass"][2],
            "exact_v33_public_pass_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
            "exact_v33_public_performance_receipt_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_receipt"][2],
            "exact_v33_public_performance_summary_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_summary"][2],
            "complete_semantic_correction_contract_sha256":
                OWNER_BY_ROLE["complete_semantic_contract"][2],
            "complete_semantic_correction_application_sha256":
                OWNER_BY_ROLE["complete_semantic_application"][2],
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_exact_disjoint_mismatch_partition": {
                "substitution_v2": 240, "shape_v2_ordering": 1024,
                "shape_v2_trailing_probe": 56,
                "shape_v2_malformed_expansion": 32,
            },
            "latest_public_10434_mismatch_count": 0,
            "historical_v28_public_10434_mismatch_count": 1145,
            "latest_v25_verified_passing_case_count": 15877,
            "latest_v25_original_case_execution_denominator": 31237,
            "latest_v25_completed_suite_count": 13,
            "historical_strict_v4_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "historical_strict_v4_audit_finding_count": 1,
            "historical_v30_static_audit_sha256":
                OWNER_BY_ROLE["historical_v30_static_audit"][2],
            "historical_v30_static_audit_covers_exact_v33_or_v35": False,
            "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_undefined_behavior": NOT_MEASURED,
            "historical_v26_publication_receipt_sha256":
                OWNER_BY_ROLE["v26_build_publication"][2],
            "historical_v26_root_receipt_sha256": OWNER_BY_ROLE["v26_build_root"][2],
            "historical_v27_publication_receipt_sha256":
                OWNER_BY_ROLE["v27_build_publication"][2],
            "historical_v27_root_receipt_sha256": OWNER_BY_ROLE["v27_build_root"][2],
            "hidden_cases_read": 0,
            "hidden_cases_generated": 0,
            "retired_v2_holdout_content_opened_by_this_controller": False,
            "retired_v2_holdout_global_unopened_claim": False,
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "final_holdout": FINAL_HOLDOUT_STATUS,
            "holdout": FINAL_HOLDOUT_STATUS,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "winner_selected": False,
        })
        complete.update(full_public_provenance())
        archive_name, receipt_name = actual_evidence_names(
            LABEL, complete["status"] == "FAIL",
        )
        directory = module.ROOT / module.EVIDENCE_PATH
        plain = module.canonical(complete)
        compressed = module.gzip.compress(plain, compresslevel=9, mtime=0)
        archived = kernel.write_fresh(directory / archive_name, compressed,
                                      synchronize=True)
        archive_sync = kernel.fsync_directory(directory)
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "version": VERSION, "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "build_status": complete["status"], "family": FAMILY, "label": LABEL,
            "source_sha256": options["source_sha256"],
            "protocol_sha256": options["protocol_sha256"],
            "contract_sha256": options["contract_sha256"],
            "frozen_commit": options["frozen_commit"],
            "pushed_commit": options["pushed_commit"],
            "archive_relative": module.EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": archived["sha256"], "archive_bytes": archived["bytes"],
            "archive_inode": archived["inode"], "archive_device": archived["device"],
            "archive_publication": archived,
            "archive_directory_fsync": archive_sync,
            "uncompressed_sha256": digest(plain), "uncompressed_bytes": len(plain),
            "actual_compiler_process_count": complete.get("actual_compiler_process_count", 0),
            "actual_completed_phase_count": complete.get("phase_count", 0),
            "external_cargo_dependency_count": 0,
            "combined_engine_source_sha256": ENGINE_SHA,
            "combined_engine_source_bytes": ENGINE_BYTES,
            "combined_search_source_sha256": SEARCH_SHA,
            "combined_search_source_bytes": SEARCH_BYTES,
            "historical_complete_scanner_bridge_sha256": BRIDGE_SHA,
            "historical_complete_scanner_bridge_bytes": BRIDGE_BYTES,
            "safe_no_external_introspection_bridge_sha256": SAFE_BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": SAFE_BRIDGE_BYTES,
            "materialized_complete_bridge_sha256": SAFE_BRIDGE_SHA,
            "materialized_complete_bridge_bytes": SAFE_BRIDGE_BYTES,
            "optimized_native_handle_lease_bridge_sha256": SAFE_BRIDGE_SHA,
            "optimized_native_handle_lease_bridge_bytes": SAFE_BRIDGE_BYTES,
            "literal_bridge_application_sha256":
                OWNER_BY_ROLE["literal_bridge_application"][2],
            "native_handle_lease_application_sha256":
                OWNER_BY_ROLE["handle_lease_application"][2],
            "exact_v33_original_pass_sha256":
                OWNER_BY_ROLE["exact_v33_original_pass"][2],
            "exact_v33_public_pass_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
            "exact_v33_public_performance_receipt_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_receipt"][2],
            "exact_v33_public_performance_summary_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_summary"][2],
            "complete_semantic_correction_contract_sha256":
                OWNER_BY_ROLE["complete_semantic_contract"][2],
            "complete_semantic_correction_application_sha256":
                OWNER_BY_ROLE["complete_semantic_application"][2],
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_exact_disjoint_mismatch_partition": {
                "substitution_v2": 240, "shape_v2_ordering": 1024,
                "shape_v2_trailing_probe": 56,
                "shape_v2_malformed_expansion": 32,
            },
            "latest_public_10434_mismatch_count": 0,
            "historical_v28_public_10434_mismatch_count": 1145,
            "latest_v25_original_case_execution_denominator": 31237,
            "historical_strict_v4_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "historical_strict_v4_audit_finding_count": 1,
            "historical_v30_static_audit_sha256":
                OWNER_BY_ROLE["historical_v30_static_audit"][2],
            "historical_v30_static_audit_covers_exact_v33_or_v35": False,
            "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_undefined_behavior": NOT_MEASURED,
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "retired_v2_holdout_global_unopened_claim": False,
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False,
            "hidden_cases_generated": 0,
            "final_holdout": FINAL_HOLDOUT_STATUS, "holdout": FINAL_HOLDOUT_STATUS,
        }
        receipt.update(full_public_provenance())
        receipt_raw = module.canonical(receipt)
        saved = kernel.write_fresh(directory / receipt_name, receipt_raw,
                                   synchronize=True)
        kernel.fsync_directory(directory)
        result: dict[str, object] = {
            "schema": SCHEMA + "-published-actual-build",
            "status": complete["status"], "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "family": FAMILY, "label": LABEL,
            "archive_relative": module.EVIDENCE_PATH + "/" + archive_name,
            "archive_sha256": archived["sha256"],
            "archive_bytes": archived["bytes"],
            "archive_inode": archived["inode"],
            "receipt_relative": module.EVIDENCE_PATH + "/" + receipt_name,
            "receipt_sha256": saved["sha256"],
            "failure_preserved": complete["status"] == "FAIL",
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
            "final_holdout": FINAL_HOLDOUT_STATUS, "winner_selected": False,
        }
        if complete["status"] != "PASS":
            return result
        require(captures and len(captures["process_ids"]) == 28,
                "publish private-root provenance only after both real native phases pass")
        canonical_after = {row[1]: read_actual_owner(row)[1] for row in CANONICAL_OWNERS}
        runtime_after = snapshot_actual_runtime_targets()
        require(canonical_before == canonical_after,
                "preserve all nine exact canonical Rust owner identities")
        require(runtime_before == runtime_after,
                "preserve every original source, adapter, and installed native identity")
        root_receipt = {
            "schema": SCHEMA + "-durable-root-provenance-receipt",
            "version": VERSION, "status": "PASS", "family": FAMILY, "label": LABEL,
            "source_sha256": options["source_sha256"],
            "protocol_sha256": options["protocol_sha256"],
            "contract_sha256": options["contract_sha256"],
            "canonical_build_status": "PASS",
            "canonical_build_receipt_relative": result["receipt_relative"],
            "canonical_build_receipt_sha256": result["receipt_sha256"],
            "canonical_build_receipt_bytes": saved["bytes"],
            "canonical_build_receipt_device": saved["device"],
            "canonical_build_receipt_inode": saved["inode"],
            "canonical_build_archive_relative": receipt["archive_relative"],
            "canonical_build_archive_sha256": receipt["archive_sha256"],
            "canonical_build_archive_bytes": receipt["archive_bytes"],
            "canonical_build_archive_inode": archived["inode"],
            "canonical_build_archive_device": archived["device"],
            "canonical_build_archive_opened": False,
            "archive_publication": archived,
            "archive_inode": archived["inode"],
            "archive_sha256": archived["sha256"],
            "archive_bytes": archived["bytes"],
            "uncompressed_sha256": receipt["uncompressed_sha256"],
            "uncompressed_bytes": receipt["uncompressed_bytes"],
            "root": captures["root"],
            "phase_native_outputs": captures["root"]["phases"],
            "phase_native_inodes": [
                [owner["inode"] for owner in phase["native_outputs"]]
                for phase in captures["root"]["phases"]
            ],
            "actual_compiler_process_count": 28,
            "actual_compiler_process_ids": captures["process_ids"],
            "actual_source_phase_count": 2,
            "actual_private_source_owners": captures["private_source_owners"],
            "actual_reproduced_native_outputs": captures["native_outputs"],
            "cross_phase_complete_engine_elf_byte_identical": True,
            "cross_phase_complete_bridge_elf_byte_identical": True,
            "distinct_private_source_identity_count": 18,
            "unchanged_canonical_source_owners_per_phase": 5,
            "combined_engine_overlay_apply_count": 2,
            "combined_search_overlay_apply_count": 2,
            "safe_no_external_introspection_bridge_overlay_apply_count": 2,
            "corrected_adapter_overlay_apply_count": 2,
            "total_private_source_overlay_apply_count": 8,
            "combined_engine_source_sha256": ENGINE_SHA,
            "combined_engine_source_bytes": ENGINE_BYTES,
            "combined_search_source_sha256": SEARCH_SHA,
            "combined_search_source_bytes": SEARCH_BYTES,
            "historical_complete_scanner_bridge_sha256": BRIDGE_SHA,
            "historical_complete_scanner_bridge_bytes": BRIDGE_BYTES,
            "safe_no_external_introspection_bridge_sha256": SAFE_BRIDGE_SHA,
            "safe_no_external_introspection_bridge_bytes": SAFE_BRIDGE_BYTES,
            "materialized_complete_bridge_sha256": SAFE_BRIDGE_SHA,
            "materialized_complete_bridge_bytes": SAFE_BRIDGE_BYTES,
            "optimized_native_handle_lease_bridge_sha256": SAFE_BRIDGE_SHA,
            "optimized_native_handle_lease_bridge_bytes": SAFE_BRIDGE_BYTES,
            "literal_bridge_application_sha256":
                OWNER_BY_ROLE["literal_bridge_application"][2],
            "native_handle_lease_application_sha256":
                OWNER_BY_ROLE["handle_lease_application"][2],
            "exact_v33_original_pass_sha256":
                OWNER_BY_ROLE["exact_v33_original_pass"][2],
            "exact_v33_public_pass_sha256": OWNER_BY_ROLE["v33_public_pass"][2],
            "exact_v33_public_performance_receipt_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_receipt"][2],
            "exact_v33_public_performance_summary_sha256":
                OWNER_BY_ROLE["exact_v33_public_performance_summary"][2],
            "complete_semantic_correction_contract_sha256":
                OWNER_BY_ROLE["complete_semantic_contract"][2],
            "complete_semantic_correction_application_sha256":
                OWNER_BY_ROLE["complete_semantic_application"][2],
            "corrected_public_adapter_sha256": ADAPTER_SHA,
            "corrected_public_adapter_bytes": ADAPTER_BYTES,
            "all_original_source_identities_restored": True,
            "all_original_runtime_target_identities_restored": True,
            "actual_original_runtime_target_count": 5,
            "actual_original_runtime_targets_before": runtime_before,
            "actual_original_runtime_targets_after": runtime_after,
            "actual_original_source_identities_before": canonical_before,
            "actual_original_source_identities_after": canonical_after,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_exact_disjoint_mismatch_partition": {
                "substitution_v2": 240, "shape_v2_ordering": 1024,
                "shape_v2_trailing_probe": 56,
                "shape_v2_malformed_expansion": 32,
            },
            "latest_public_10434_mismatch_count": 0,
            "historical_v28_public_10434_mismatch_count": 1145,
            "latest_v25_original_case_execution_denominator": 31237,
            "historical_strict_v4_audit_status": "FAIL; HISTORICAL PRIVATE GETTER PRESENT",
            "historical_strict_v4_audit_finding_count": 1,
            "historical_v30_static_audit_sha256":
                OWNER_BY_ROLE["historical_v30_static_audit"][2],
            "historical_v30_static_audit_covers_exact_v33_or_v35": False,
            "exact_previous_v33_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "exact_previous_v33_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_static_source_and_elf_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_live_runtime_non_delegation": "NOT ESTABLISHED",
            "proposed_v35_undefined_behavior": NOT_MEASURED,
            "historical_retired_v2_proposal_case_count": RETIRED_PROPOSAL_CASE_COUNT,
            "retired_v2_holdout_global_unopened_claim": False,
            "hidden_cases_generated": 0,
            "candidate_matching": "NOT RUN", "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False, "winner_selected": False,
            "final_holdout": FINAL_HOLDOUT_STATUS, "holdout": FINAL_HOLDOUT_STATUS,
        }
        root_receipt.update(full_public_provenance())
        root_name = actual_root_receipt_name(LABEL)
        root_raw = module.canonical(root_receipt)
        published_root = kernel.write_fresh(directory / root_name, root_raw,
                                             synchronize=True)
        kernel.fsync_directory(directory)
        result.update({"root_provenance_status": "PASS",
                       "root_receipt_relative": module.EVIDENCE_PATH + "/" + root_name,
                       "root_receipt_sha256": published_root["sha256"],
                       "actual_compiler_process_count": 28,
                       "actual_source_phase_count": 2,
                       "cross_phase_complete_engine_elf_byte_identical": True,
                       "cross_phase_complete_bridge_elf_byte_identical": True,
                       "latest_original_v33_candidate_status": "PASS",
                       "latest_original_v33_verified_passing_case_count": 31237,
                       "latest_original_v33_pass_receipt_sha256":
                           OWNER_BY_ROLE["exact_v33_original_pass"][2],
                       "latest_public_v28_mismatch_count": 1145,
                       "scanner_comment_overlap_count": 15,
                       "substitution_comment_overlap_count": 12})
        return result

    module.verify_frozen_context = context
    module.expected_source_owner = expected
    module.copy_combined_snapshot = lambda workdir, family, phase, originals: (
        copy_four_overlays(module, workdir, family, phase, originals)
    )
    module.verify_reproduced_phases = verify
    module.publish_build_report = publish

    class ActualOptions:
        pass

    forwarded = ActualOptions()
    for name in ("source_sha256", "protocol_sha256", "contract_sha256", "label",
                 "owned_source_sha256", "corrected_adapter_sha256",
                 "corrected_adapter_bytes"):
        setattr(forwarded, name, options[name])
    forwarded.combined_bridge_sha256 = SAFE_BRIDGE_SHA
    forwarded.combined_bridge_bytes = SAFE_BRIDGE_BYTES
    require_actual_private_overlay_authority(
        module, forwarded.combined_bridge_sha256, forwarded.combined_bridge_bytes,
        forwarded.corrected_adapter_sha256, forwarded.corrected_adapter_bytes,
    )
    result = module.run_build(forwarded)
    require(type(result) is dict and result.get("family") == FAMILY,
            "publish exactly one genuine V35 first-party native build outcome")
    canonical_after = {row[1]: read_actual_owner(row)[1] for row in CANONICAL_OWNERS}
    require(canonical_before == canonical_after
            and runtime_before == snapshot_actual_runtime_targets(),
            "restore all nine canonical sources and all five original runtime targets")
    # Keep the authenticated operational module until main emits canonical
    # bytes.  Re-executing a source-only transformer after subprocess/json
    # imports would correctly trip its clean-matcher precondition.
    return result


def main(arguments: list[str]) -> int:
    try:
        require(sys.executable == PYTHON and sys.version_info[:3] == (3, 14, 6)
                and sys.flags.isolated == 1 and sys.flags.no_site == 1
                and sys.flags.dont_write_bytecode == 1,
                "use only the pinned CPython 3.14.6 with -I -B -S")
        require(type(arguments) is list and bool(arguments),
                "select one source-only V35 gate or one actual root-authorized build")
        if arguments[0] in ACTUAL_MODES:
            result = run_actual(parse_actual(arguments))
            # The actual authenticated operational kernel owns canonical JSON.
            module = sys.modules.get("_rebar_v35_authenticated_actual_v16_native_kernel")
            if type(module) is types.ModuleType and callable(module.canonical):
                output = module.canonical(result)
                sys.stdout.buffer.write(output)
                sys.stdout.flush()
                return 0
            # run_actual removes its temporary module; encode with a pinned prior transformer.
            source, _ = read_actual_owner(OWNER_BY_ROLE["anchor_transformer"])
            encoder = actual_module("anchor_transformer", source,
                                    "_rebar_v35_actual_canonical_encoder")
            sys.stdout.write(encoder.canonical(result) + "\n")
            sys.stdout.flush()
            return 0
        mode, source_pin, protocol_pin, contract_pin = parse_source(arguments)
        context = load_source_context(mode, source_pin, protocol_pin, contract_pin)
        canonical = context["canonical"]
        assert callable(canonical)
        if mode == "--render-contract":
            value = context["contract"]
        elif mode == "--self-test":
            value = hostile_controls(context)
        else:
            value = {"schema": SCHEMA + "-verified-source-only-context",
                     "version": VERSION, "status": "PASS",
                     "source_sha256": source_pin, "protocol_sha256": protocol_pin,
                     "contract_sha256": contract_pin,
                     "candidate_executions": 0, "candidate_imports": 0,
                     "compiler_processes_started": 0, "native_libraries_loaded": 0,
                     "clock_samples": 0, "hidden_cases_generated": 0,
                     "retired_holdout_content_bytes_read": 0,
                     "workspace_mutations": 0,
                     "final_holdout": FINAL_HOLDOUT_STATUS,
                     "frozen_contract": context["contract"]}
        sys.stdout.write(canonical(value) + "\n")
        sys.stdout.flush()
        return 0
    except BaseException as error:
        try:
            sys.stderr.write("V35 combined first-party source build FAILED: "
                             + type(error).__name__ + ": " + str(error)[:8192] + "\n")
            sys.stderr.flush()
        except BaseException:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
