#!/usr/bin/env python3
"""Freeze and genuinely reproduce the first-party Rust V27 compiler fast path.

Source-only modes first install an irreversible, deny-default physical wall;
they never start a build, import a candidate, or inspect a native artifact.
After the complete freeze is pushed, an independently pinned root-authorized
actual mode uses only the genuine V16/V9 compiler kernel to reproduce the
complete a127 capture-clamp bridge and independently materialized 64228
first-party compiler source in two fresh offline phases while preserving the
fully observed V24 candidate FAIL-1352 and successful genuine V25 lineage.
"""

from __future__ import annotations

import sys

if any(name in sys.modules for name in ("re", "_sre", "regex")):
    raise SystemExit("a first-party Rust source freeze must not load a matcher")

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
PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
DEVICE = 2064
SOURCE = "tools/reproduce_owned_rust_compiler_fastpath_source_build_v27.py"
PROTOCOL = "oracle/phase2/RUST-COMPILER-FASTPATH-SOURCE-BUILD-V27.md"
CONTRACT = "oracle/phase2/rust-compiler-fastpath-source-build-v27.json"
SCHEMA = "rebar-phase2-owned-rust-compiler-fastpath-source-build-v27"
VERSION = 27
FAMILY = "rust"
NOT_MEASURED = "NOT MEASURED"
MAX_OWNER_BYTES = 1_048_576
GOAL_SHA = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
BUILD_LABEL = "phase2-v27-rust-compiler-fast-v1-root-provenance"
A0_SHA = "a0b9e7fbfc92da4c3b97608cf156fb0ca2f94fb5358901b7b6baa0a819fffc8a"
F9_SHA = "f9bd2d3c8406e4b2c703ce96f42964ee15941611e22447b12acc9b54fac98055"
INPUT_VARIANT_SHA = "1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0"
VARIANT_SHA = "a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54"
INPUT_VARIANT_BYTES = 178860
VARIANT_BYTES = 178805
EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT = 141_557_760
EXPANDED_HOLDOUT_PROPOSAL_SHA = (
    "5d9fa3920c1dcabc92a3521d742cd10ec399cff1a979b71ac079daba6f92cba0"
)
PREVIOUS_BUILD_RECEIPT_SHA = (
    "da4edc2ff3352aab2a7b0c992286534b38dce422fd258f1fe1531464a277d6e4"
)
PREVIOUS_ROOT_RECEIPT_SHA = (
    "f2117effdca435e10fbc453bac28fd32b3517e60a9611209a96eca0f6b5d172e"
)
PREVIOUS_FAILURE_RECEIPT_SHA = (
    "5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09"
)
PREVIOUS_ENGINE_SHA = (
    "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
)
PREVIOUS_BRIDGE_SHA = (
    "e0c26cb83fe35eb18297e7a9cd58b63be891d847479237d2ba972e4ba1b3b3bf"
)
MATCHER_SHA = "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d"
ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
ADAPTER_BYTES = 31934
COMPILER_VARIANT_SHA = (
    "64228afb698f5326e6a30fd93c2ea27bd81653ecdd4a4a8e2b0dda5983e895b6"
)
COMPILER_VARIANT_BYTES = 178021
V25_BUILD_RECEIPT_SHA = (
    "55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc"
)
V25_ROOT_RECEIPT_SHA = (
    "e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2"
)
V25_FAILURE_RECEIPT_SHA = (
    "d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59"
)
V25_FAILURE_ARCHIVE_SHA = (
    "dee05f06d473af52db5447b485265d886e66e5420cb3e814b5b972d8798a04a7"
)
RUST_TOOLCHAIN = "/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu"
RUSTC = RUST_TOOLCHAIN + "/bin/rustc"
CARGO = RUST_TOOLCHAIN + "/bin/cargo"
GCC = "/usr/bin/x86_64-linux-gnu-gcc-13"
READELF = "/usr/bin/x86_64-linux-gnu-readelf"
PYTHON_INCLUDE = (
    "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14"
)
PHASES = ("reference-a", "reference-b")
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols", "engine_sections",
    "engine_notes", "bridge_sections", "bridge_notes",
)
GCC_FLAGS = (
    "-pthread", "-std=c11", "-shared", "-fPIC", "-O3", "-Wall",
    "-Wextra", "-Werror", "-Wl,-z,noexecstack",
    "-Wl,--exclude-libs,ALL", "-Wl,--build-id=sha1",
)
EVIDENCE_PATH = "oracle/phase2/evidence"
ROOT_CAPTURE: dict[str, object] | None = None
PHASE_ONE_V4_PINS = {
    "phase1_v4_source_sha256":
        "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d",
    "phase1_v4_protocol_sha256":
        "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2",
    "phase1_v4_contract_sha256":
        "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
}

CAPTURE_V2_OWNERS = (
    ("capture_v2_source", "tools/apply_owned_rust_capture_shape_semantics_v2.py",
     "e285d0c39950f7ffc5929f0c5f5a0708b8c3e8878b655255cb29e1b0725233c2",
     83214, 431144),
    ("capture_v2_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2.md",
     "999e8cdf9f7a7b0fbaca67759d8c0a13f49c7ca10c753539010d11681a1aaa8d",
     5289, 525411),
    ("capture_v2_contract",
     "oracle/phase2/rust-capture-shape-semantics-v2.json",
     "cafb121e38ed738c51d30978a22ddf788eafd729b2a145a8f3564ea97412e673",
     14661, 525421),
)

PUBLIC_OWNERS = (
    ("goal", "GOAL.md", GOAL_SHA, 3756, 31364044),
    ("original_oracle", "oracle/phase1/p0-completeness-v4.json",
     "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1",
     34875, 524713),
    ("supplemental_oracle",
     "oracle/phase1/p0-differential-fuzz-reference-v3.json",
     "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff",
     5288, 525082),
    ("substitution_oracle",
     "tools/independent_substitution_buffer_semantics_v2.py",
     "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573",
     317541, 432058),
    ("shape_oracle", "tools/independent_shape_changing_buffer_semantics_v2.py",
     "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c",
     137527, 432070),
    ("semantic_v1_source", "tools/apply_owned_rust_capture_shape_semantics_v1.py",
     "d3213d43bd09b1216f618a3a14472ff0fe290b13852c403a0d1c0ecd8a0408b2",
     53555, 431487),
    ("semantic_v1_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V1.md",
     "edbeb811483b39f094dbead1237e912e20af07609474c7256db75fce45887f54",
     4883, 525377),
    ("semantic_v1_contract",
     "oracle/phase2/rust-capture-shape-semantics-v1.json",
     "5e262226341a7554943a7ae21fad616009555231e855ea23b7eb715c94317b63",
     6524, 525378),
    ("native_v22_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_source_build_v22.py",
     "0ce73b2168c5143e2f95256d454ffe131bdc2c5736d91176509cc651819f58d4",
     65949, 430180),
    ("native_v22_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-SOURCE-BUILD-V22.md",
     "31467e166ecc83ef49c43ca51bb97b7699a696068a4267dcd013c64078b3050a",
     5372, 524832),
    ("native_v22_contract",
     "oracle/phase2/rust-capture-shape-semantics-source-build-v22.json",
     "b43f1a1f5f7c5c72990f4d8c3c9e321e53d7970b3ceaa4b0afdb82a08fa4b308",
     10067, 524833),
    ("native_v22_publication",
     "oracle/phase2/evidence/native-source-build-v22-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-publication-receipt.json",
     "851c7c6fd8546ee59f8107ea3687d0150d0ada0bf6764b040019b083776701b2",
     3500, 524926),
    ("native_v22_root_receipt",
     "oracle/phase2/evidence/native-source-build-v22-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-root-provenance-receipt.json",
     "93cb91b186faaf32522a11caeb564829cd4504751bc88aebf955c36d19e572a3",
     5607, 524930),
    ("campaign_v22_source", "tools/run_owned_repaired_rust_original_campaign_v22.py",
     "e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61",
     61761, 430995),
    ("campaign_v22_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V22.md",
     "c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396",
     6038, 525307),
    ("campaign_v22_contract",
     "oracle/phase2/repaired-rust-original-campaign-v22.json",
     "f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a",
     42352, 525314),
    ("prior_actual_v20",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v21-rust-captured-findall-root-provenance-"
     "original-p0-v20-failures-publication-receipt.json",
     "ad9e04aa3595a4e44a5bbc12b6413fde08b926c9e73b23aa6b3eedacd35e4a36",
     45973, 524829),
    ("actual_v22",
     "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
     "phase2-v22-rust-capture-shape-root-provenance-"
     "original-p0-v22-failures-publication-receipt.json",
     "7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7",
     47336, 525371),
)

GUARD_OWNERS = (
    ("guard_v3_source", "tools/verify_owned_candidate_runtime_independence_v3.py",
     "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
     59765, 430856),
    ("guard_v3_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
     "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
     5297, 525096),
    ("guard_v3_contract", "oracle/phase2/candidate-runtime-independence-v3.json",
     "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
     9157, 525114),
    ("guard_v2_source", "tools/verify_owned_candidate_runtime_independence_v2.py",
     "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
     67097, 431371),
    ("guard_v2_protocol", "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
     "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
     4437, 524886),
    ("guard_v2_contract", "oracle/phase2/candidate-runtime-independence-v2.json",
     "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
     7671, 524887),
    ("producer_v5_source", "tools/run_owned_six_family_original_p0_producer_v5.py",
     "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538",
     102286, 431370),
    ("producer_v5_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md",
     "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4",
     5270, 524884),
    ("producer_v5_contract", "oracle/phase2/six-family-p0-producer-v5.json",
     "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53",
     21036, 524885),
)

CAMPAIGN_V23_OWNERS = (
    ("campaign_v23_source", "tools/run_owned_repaired_rust_original_campaign_v23.py",
     "dfa8b2a4d2a8ecbadbe36097a7dc55ce92abfeda56bf6cd0a8f02ae72b544b29",
     66129, 431185),
    ("campaign_v23_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V23.md",
     "289fb9f2ddd20d3f29749f0328894be2f540eaec8485ad0d7ba4d5e932eaf68e",
     7194, 525487),
    ("campaign_v23_contract",
     "oracle/phase2/repaired-rust-original-campaign-v23.json",
     "08cb3111855de792b2708db0c281c6d110735f79f3e85a3ef6c5de9944be5aa6",
     181093, 525488),
)

BUILD_V24_OWNERS = (
    ("native_v24_build_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v24.py",
     "5bf779c3f9df24814565c2342dd2972254c2703d6f08d771c4096b5152683ac2",
     136322, 431516),
    ("native_v24_build_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2-SOURCE-BUILD-V24.md",
     "273ba50f4629961ed61e666593d9af49f9b49fbc73c83564d2453c3bf017b101",
     7361, 525609),
    ("native_v24_build_contract",
     "oracle/phase2/rust-capture-shape-semantics-v2-source-build-v24.json",
     "cd1a77792bbb9822bfe3e05f0005bb0629c05ecd16daa68a3e11337130a54876",
     578498, 525612),
)

CAMPAIGN_V24_OWNERS = (
    ("actual_v24_campaign_source",
     "tools/run_owned_repaired_rust_original_campaign_v24.py",
     "f855f73e320f4ec33063dac1f22c11b1977ba04a02e1f97dfddca1d0670f705d",
     83262, 429270),
    ("actual_v24_campaign_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V24.md",
     "d482cf8d06f9f328c08fda43a63db79db408e2421bad24e6e047ad507ef70431",
     6617, 525887),
    ("actual_v24_campaign_contract",
     "oracle/phase2/repaired-rust-original-campaign-v24.json",
     "605737aa5060b78eb3802c8b3e58954a680bdf08b6f62a402de453552a0cd8f4",
     14607, 525907),
)

RUNTIME_GUARD_V4_OWNERS = (
    ("runtime_guard_v4_source",
     "tools/verify_owned_candidate_runtime_independence_v4.py",
     "5b498643fa730dc09090bdc9e189e2d395cbe41a2b14019937eb251fd38240f3",
     48687, 429243),
    ("runtime_guard_v4_protocol",
     "oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V4.md",
     "835473a98f62c9b2cb0dee61736b6cbbab4460f14d8371597e80933c64721a16",
     4492, 525890),
    ("runtime_guard_v4_contract",
     "oracle/phase2/candidate-runtime-independence-v4.json",
     "30f5c52d5aadfd6e8a7be7c6f355d9628510384d7fd922bcfb609dfe854acea2",
     9352, 525891),
)

CAPTURE_CLAMP_OWNERS = (
    ("capture_clamp_v1_transformer_source",
     "tools/apply_owned_rust_capture_clamp_semantics_v1.py",
     "ff4b45f370bb6df1a3693cb1046031df93f3dffb336f4cca695768a1adb34fb7",
     71522, 429579),
    ("capture_clamp_v1_transformer_protocol",
     "oracle/phase2/RUST-CAPTURE-CLAMP-SEMANTICS-V1.md",
     "15bd3b25b3f86638ddcb45cbc11d962341a905903a4cd52a632f6c3f1a078ff9",
     4645, 526033),
    ("capture_clamp_v1_transformer_contract",
     "oracle/phase2/rust-capture-clamp-semantics-v1.json",
     "46344723f24c65c123c4550c9652b3547866a2ae1a8419444d3359eb048294c6",
     11342, 526034),
)

V24_BUILD_RECEIPT_OWNER = (
    "actual_v24_native_build_receipt",
    "oracle/phase2/evidence/native-source-build-v24-rust-"
    "phase2-v24-rust-capture-shape-v2-root-provenance-publication-receipt.json",
    PREVIOUS_BUILD_RECEIPT_SHA, 4229, 525876,
)
V24_ROOT_RECEIPT_OWNER = (
    "actual_v24_native_root_receipt",
    "oracle/phase2/evidence/native-source-build-v24-rust-"
    "phase2-v24-rust-capture-shape-v2-root-provenance-"
    "root-provenance-receipt.json",
    PREVIOUS_ROOT_RECEIPT_SHA, 60276, 525877,
)
V24_FAILURE_RECEIPT_OWNER = (
    "actual_v24_complete_original_failure_receipt",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v24-rust-capture-shape-v2-root-provenance-"
    "original-p0-v24-failures-publication-receipt.json",
    PREVIOUS_FAILURE_RECEIPT_SHA, 11832, 525952,
)

BUILD_V23_OWNERS = (
    ("materialized_v23_build_source",
     "tools/reproduce_owned_rust_capture_shape_semantics_v2_source_build_v23.py",
     "d4d27b33423fea02cc74529ea279fe02776447f40c5a8d83022004d2af3f771b",
     80196, 431415),
    ("materialized_v23_build_protocol",
     "oracle/phase2/RUST-CAPTURE-SHAPE-SEMANTICS-V2-SOURCE-BUILD-V23.md",
     "3fb90120ff21a6cafe1f6ce24c7e4d1d08e1327b98b980e69c0eb0295ae48520",
     7708, 525569),
    ("materialized_v23_build_contract",
     "oracle/phase2/rust-capture-shape-semantics-v2-source-build-v23.json",
     "e4138ea585eefc0a22c254b21f761a2d9795fef4ff914b2368178e7c8e392028",
     288435, 525570),
)

NATIVE_SOURCE_OWNERS = (
    ("native_v9_source", "tools/reproduce_owned_native_source_build_v9.py",
     "c4a4b85b92ef0d600528732c9e0acb8f8303b7b2fbfc320e84c9b9e2d384219f",
     81124, 429976),
    ("native_v9_protocol", "oracle/phase2/NATIVE-SOURCE-BUILD-V9.md",
     "18494d4b778a3c958b07903996e8a1b13f4466e08b2c9e72cd5d711957dbcecc",
     4960, 524423),
    ("native_v9_contract", "oracle/phase2/native-source-build-v9.json",
     "6a4aee7f0c639b2b338d1497c35a69d35939841cf55b0dbe38abe404cea404da",
     9134, 524424),
    ("native_v16_source", "tools/reproduce_owned_rust_buffer_shape_source_build_v16.py",
     "bcea8f23fc5e52af1e8062145d75ef1a6ed835cea3ac113a155cc8ebf3116a8a",
     134640, 431980),
    ("native_v16_protocol", "oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V16.md",
     "315f0a24e64b50804565f86c6ca4187024c4a1db5a23ab2f57c8805ed37f51f5",
     6497, 524984),
    ("native_v16_contract", "oracle/phase2/rust-buffer-shape-source-build-v16.json",
     "4f82f88da3329c6bacac2092af19d915d379f90101dcd9840366274355cc92b7",
     18260, 524985),
)

ADAPTER_REPAIR_OWNERS = (
    ("adapter_v3_source", "tools/apply_owned_rust_public_contract_source_repair_v3.py",
     "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859",
     92060, 431033),
    ("adapter_v3_protocol",
     "oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
     "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34",
     6405, 524675),
    ("adapter_v3_contract",
     "oracle/phase2/rust-public-contract-source-repair-v3.json",
     "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1",
     14817, 524678),
)

CANONICAL_RUST_OWNERS = (
    ("canonical_cargo_lock", "candidates/rust/Cargo.lock",
     "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63",
     167, 428098),
    ("canonical_cargo_manifest", "candidates/rust/Cargo.toml",
     "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966",
     225, 428094),
    ("canonical_original_bridge", "candidates/rust/py_bridge.c",
     "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
     175676, 419054),
    ("canonical_matching_engine", "candidates/rust/src/lib.rs", MATCHER_SHA,
     177967, 428096),
    ("canonical_newline", "candidates/rust/src/newline.rs",
     "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b",
     14416, 427958),
    ("canonical_search", "candidates/rust/src/search.rs",
     "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe",
     14773, 429682),
    ("canonical_stack", "candidates/rust/src/stack.rs",
     "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e",
     7269, 428151),
    ("canonical_unicode_tables", "candidates/rust/src/unicode_tables.rs",
     "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af",
     471989, 428152),
    ("canonical_original_adapter", "candidates/rust_candidate.py",
     "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
     31151, 428100),
)

A0_OWNER = (
    "captured_findall_a0_base",
    "candidates/rust/variants/buffer_shape_pickle_findall_captures_v1/py_bridge.c",
    A0_SHA, 179520, 524770,
)
VARIANT_OWNER = (
    "materialized_capture_clamp_semantics_v1_bridge",
    "candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c",
    VARIANT_SHA, VARIANT_BYTES, 526064,
)
INPUT_VARIANT_OWNER = (
    "immutable_actual_v24_capture_shape_semantics_v2_bridge",
    "candidates/rust/variants/"
    "buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c",
    INPUT_VARIANT_SHA, INPUT_VARIANT_BYTES, 525539,
)

BUILD_V25_OWNERS = (
    ("successful_v25_native_build_source",
     "tools/reproduce_owned_rust_capture_clamp_source_build_v25.py",
     "f0a5d0b0af76b83e4f7091050afc187458c8c4380a37418f5df0de41d882b408",
     186263, 429530),
    ("successful_v25_native_build_protocol",
     "oracle/phase2/RUST-CAPTURE-CLAMP-SOURCE-BUILD-V25.md",
     "ddc7c1fcf385ec979c73a304123025a6e5974a8eb37dd61cf189ccba20687f85",
     7140, 525993),
    ("successful_v25_native_build_contract",
     "oracle/phase2/rust-capture-clamp-source-build-v25.json",
     "528d2bcccb2cceed5f607f7ec8428b18df10f30b9b6b6f7313083a288061127a",
     229419, 526066),
)
CAMPAIGN_V25_OWNERS = (
    ("actual_v25_original_campaign_source",
     "tools/run_owned_repaired_rust_original_campaign_v25.py",
     "09074713ee068a01dc91c07db68a7efcd4500f9b92990699f5e849fa77410edc",
     100824, 430716),
    ("actual_v25_original_campaign_protocol",
     "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V25.md",
     "9a2d0a3a71e998750cc6213a7ad4c42c6a8bf8a022347af55723d2407aa345e1",
     5638, 526197),
    ("actual_v25_original_campaign_contract",
     "oracle/phase2/repaired-rust-original-campaign-v25.json",
     "230e4c98914b0ca2b1d4bc55eb9d7cf38474eed835626c2639916bd4ed581c1a",
     57478, 526253),
)
COMPILER_FASTPATH_OWNERS = (
    ("compiler_fastpath_source",
     "tools/apply_owned_rust_compiler_allocation_fastpath_v1.py",
     "13ad7948ba05a057f1c93f404998d72217ad42a8a93da8d71f9a3f7b5a41d1bf",
     75362, 429789),
    ("compiler_fastpath_protocol",
     "oracle/phase2/RUST-COMPILER-ALLOCATION-FASTPATH-V1.md",
     "dd1516d037aa9f56458d0bbcb61ee36a283463c7fc38bb9372ac55c35112382c",
     5306, 526090),
    ("compiler_fastpath_contract",
     "oracle/phase2/rust-compiler-allocation-fastpath-v1.json",
     "915170849be177d17c26b135b6fb8792981ffef35d6876bc4c073237d0f58f55",
     9667, 526100),
)
COMPILER_APPLICATION_OWNER = (
    "compiler_fastpath_exclusive_application",
    "oracle/phase2/evidence/rust-compiler-allocation-fastpath-v1-application.json",
    "37f9a96e511095461af237e3fcf7d9e674995c274e7fe5c69368d59afeddccc6",
    2143, 526158,
)
COMPILER_VARIANT_OWNER = (
    "materialized_compiler_allocation_fastpath_source",
    "candidates/rust/variants/compiler_allocation_fastpath_v1/lib.rs",
    COMPILER_VARIANT_SHA, COMPILER_VARIANT_BYTES, 526157,
)
V25_BUILD_RECEIPT_OWNER = (
    "successful_v25_native_publication_receipt",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-publication-receipt.json",
    V25_BUILD_RECEIPT_SHA, 5231, 526084,
)
V25_ROOT_RECEIPT_OWNER = (
    "successful_v25_native_root_receipt",
    "oracle/phase2/evidence/native-source-build-v25-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-"
    "root-provenance-receipt.json",
    V25_ROOT_RECEIPT_SHA, 61798, 526085,
)
V25_FAILURE_RECEIPT_OWNER = (
    "actual_v25_complete_original_failure_receipt",
    "oracle/phase2/evidence/repaired-rust-original-campaign-v16-rust-"
    "phase2-v25-rust-capture-clamp-v1-root-provenance-"
    "original-p0-v25-failures-publication-receipt.json",
    V25_FAILURE_RECEIPT_SHA, 11832, 524846,
)
PUBLIC_PRACTICE_OWNERS = (
    ("preserved_public_stdlib_correctness",
     "experiments/rust_public_profile_v1/public-run-001/"
     "stdlib.correctness.raw.json",
     "efe0a3cc37194290b9577d5bd4f502a5c482016bc2b8ae90acec6254545b5381",
     445036, 526005),
    ("preserved_public_rust_correctness",
     "experiments/rust_public_profile_v1/public-run-001/"
     "rust.correctness.raw.json",
     "8774ad035e17126252803e75494a80d376386a85e13c46cb3e0380b82dae89b0",
     445394, 526006),
    ("preserved_public_paired_practice",
     "experiments/rust_public_profile_v1/public-run-001/"
     "paired-timing.raw.json",
     "3da06bdb04ace9897d359aaa962ca412f3e9260a5c1a337703e0aa35567b6b85",
     504907, 526015),
)
V27_ADDITIONAL_OWNERS = (
    BUILD_V25_OWNERS + CAMPAIGN_V25_OWNERS + COMPILER_FASTPATH_OWNERS
    + PUBLIC_PRACTICE_OWNERS
    + (COMPILER_APPLICATION_OWNER, COMPILER_VARIANT_OWNER,
       V25_BUILD_RECEIPT_OWNER, V25_ROOT_RECEIPT_OWNER,
       V25_FAILURE_RECEIPT_OWNER)
)

PARENT_STATIC_OWNERS = CAPTURE_V2_OWNERS + PUBLIC_OWNERS + GUARD_OWNERS
STATIC_OWNERS = (
    PARENT_STATIC_OWNERS + CAMPAIGN_V23_OWNERS + BUILD_V23_OWNERS
    + NATIVE_SOURCE_OWNERS
    + ADAPTER_REPAIR_OWNERS + CANONICAL_RUST_OWNERS
    + BUILD_V24_OWNERS + CAMPAIGN_V24_OWNERS + RUNTIME_GUARD_V4_OWNERS
    + CAPTURE_CLAMP_OWNERS
    + (A0_OWNER, INPUT_VARIANT_OWNER, VARIANT_OWNER,
       V24_BUILD_RECEIPT_OWNER, V24_ROOT_RECEIPT_OWNER,
       V24_FAILURE_RECEIPT_OWNER)
    + V27_ADDITIONAL_OWNERS
)

TOOLCHAIN_OWNERS = (
    {
        "path": RUSTC,
        "sha256": "bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6",
        "bytes": 644784, "device": DEVICE, "inode": 31359570,
        "mode": 493, "uid": 1000, "nlink": 1,
    },
    {
        "path": CARGO,
        "sha256": "841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66",
        "bytes": 42185192, "device": DEVICE, "inode": 31359488,
        "mode": 493, "uid": 1000, "nlink": 1,
    },
    {
        "path": GCC,
        "sha256": "1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26",
        "bytes": 1023032, "device": 1048708, "inode": 10445975,
        "mode": 493, "uid": 65534, "nlink": 1,
    },
    {
        "path": READELF,
        "sha256": "64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0",
        "bytes": 789280, "device": 1048708, "inode": 10446013,
        "mode": 493, "uid": 65534, "nlink": 1,
    },
)
SOURCE_MODES = ("--render-contract", "--verify-frozen-context", "--self-test")
ACTUAL_MODES = ("--run", "--build")


class BuildFreezeError(Exception):
    """Reject altered Rust owners or a build without real root authority."""


def require(value: object, label: str) -> None:
    if value is not True:
        raise BuildFreezeError(label)


def digest(raw: bytes) -> str:
    require(type(raw) is bytes, "hash only complete genuine source bytes")
    return hashlib.sha256(raw).hexdigest()


def hash_pin(value: object, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "independently pin the complete source owner: " + label)
    assert isinstance(value, str)
    return value


def no_matching_imports() -> None:
    forbidden = (
        "re", "_sre", "regex", "re2", "pcre", "pcre2", "oniguruma",
        "ctypes", "candidates", "rebar", "subprocess", "socket",
        "concurrent.interpreters",
    )
    require(not any(
        module == root or module.startswith(root + ".")
        for module in sys.modules for root in forbidden
    ), "reject candidate imports, matching engines, native loads, and network")


class FirstPartySourceWall:
    """Permit only complete pinned first-party sources and public evidence."""

    def __init__(self) -> None:
        relatives = (SOURCE, PROTOCOL, CONTRACT) + tuple(
            row[1] for row in STATIC_OWNERS
        )
        require(len(relatives) == len(frozenset(relatives)),
                "reject duplicate or aliased first-party source owners")
        self.allowed = frozenset(ROOT + "/" + name for name in relatives)
        self.blocked: dict[str, int] = {}
        self.live: set[int] = set()
        self.installed = False
        self.error_type: type[Exception] = BuildFreezeError
        self.native_open = os.open
        self.native_read = os.read
        self.native_fstat = os.fstat
        self.native_close = os.close

    def deny(self, category: str) -> None:
        self.blocked[category] = self.blocked.get(category, 0) + 1
        raise self.error_type(
            "V23 first-party physical source wall rejected " + category,
        )

    def approved(self, path: object) -> bool:
        return (
            type(path) is str
            and path.startswith(ROOT + "/")
            and path == os.path.normpath(path)
            and not any(part in (".", "..") for part in path.split("/"))
            and path in self.allowed
            and not path.endswith((".so", ".gz"))
            and not path.startswith(ROOT + "/oracle/phase3/")
            and "holdout" not in path.lower()
            and "benchmark" not in path.lower()
        )

    def audit(self, event: str, arguments: tuple) -> None:
        if event == "open":
            path = arguments[0] if arguments else None
            mode = arguments[1] if len(arguments) > 1 else None
            flags = arguments[2] if len(arguments) > 2 else None
            destructive = (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                | os.O_APPEND | getattr(os, "O_TMPFILE", 0)
            )
            if (
                not self.approved(path)
                or type(flags) is not int
                or flags & destructive
                or not flags & getattr(os, "O_NOFOLLOW", 0)
                or type(mode) is str and any(char in mode for char in "wax+")
            ):
                self.deny("unowned-direct-file-open")
            return
        if event in ("exec", "compile"):
            value = arguments[0] if arguments else None
            filename = (
                getattr(value, "co_filename", None)
                if event == "exec"
                else arguments[1] if len(arguments) > 1 else None
            )
            if not self.approved(filename):
                self.deny("unowned-dynamic-execution")
            return
        if (
            event in (
                "import", "marshal.loads", "os.system", "os.fork",
                "os.posix_spawn", "os.posix_spawnp", "os.rename",
                "os.replace", "os.remove", "os.unlink", "os.mkdir",
                "os.rmdir", "os.chmod", "os.chown", "os.urandom",
                "os.getrandom", "_interpreters.create", "_interpreters.exec",
                "cpython.PyInterpreterState_New",
            )
            or event.startswith((
                "subprocess.", "socket.", "ctypes.", "threading.",
                "multiprocessing.", "tempfile.", "time.", "os.exec",
                "os.spawn", "random.",
            ))
        ):
            self.deny("import-compiler-native-network-clock-or-mutation")

    def _forbidden(self, category: str):
        def denied(*_args: object, **_kwargs: object) -> object:
            self.deny(category)
        return denied

    def guarded_open(
        self, path: object, flags: object, mode: int = 0o777,
        *, dir_fd: object = None,
    ) -> int:
        destructive = (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            | getattr(os, "O_TMPFILE", 0) | getattr(os, "O_DIRECTORY", 0)
        )
        if (
            not self.approved(path)
            or type(flags) is not int
            or flags & destructive
            or not flags & getattr(os, "O_NOFOLLOW", 0)
            or dir_fd is not None
        ):
            self.deny("unowned-os-open-or-directory-descriptor")
        assert isinstance(path, str)
        descriptor = self.native_open(path, flags, mode)
        require(type(descriptor) is int and descriptor >= 0,
                "open only one real pinned first-party source descriptor")
        require(descriptor not in self.live,
                "reject an already live first-party source descriptor")
        self.live.add(descriptor)
        return descriptor

    def guarded_read(self, descriptor: object, count: object) -> bytes:
        if (
            type(descriptor) is not int or descriptor not in self.live
            or type(count) is not int or not 0 <= count <= MAX_OWNER_BYTES
        ):
            self.deny("unowned-or-unbounded-direct-descriptor-read")
        assert isinstance(descriptor, int) and isinstance(count, int)
        return self.native_read(descriptor, count)

    def guarded_fstat(self, descriptor: object) -> os.stat_result:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("unowned-direct-descriptor-stat")
        assert isinstance(descriptor, int)
        return self.native_fstat(descriptor)

    def guarded_close(self, descriptor: object) -> None:
        if type(descriptor) is not int or descriptor not in self.live:
            self.deny("unowned-direct-descriptor-close")
        assert isinstance(descriptor, int)
        self.live.remove(descriptor)
        self.native_close(descriptor)

    def install(self) -> None:
        require(not self.installed,
                "install exactly one fresh first-party source wall")
        sys.addaudithook(self.audit)
        builtins.open = self._forbidden("builtins-open")
        _io.open = self._forbidden("direct-_io-open")
        _io.FileIO = self._forbidden("direct-_io-fileio")
        io.open = self._forbidden("direct-io-open")
        io.FileIO = self._forbidden("direct-io-fileio")
        if hasattr(_io, "open_code"):
            _io.open_code = self._forbidden("direct-_io-open-code")
        if hasattr(io, "open_code"):
            io.open_code = self._forbidden("direct-io-open-code")
        os.open = self.guarded_open
        os.read = self.guarded_read
        os.fstat = self.guarded_fstat
        os.close = self.guarded_close
        for name in (
            "fdopen", "dup", "dup2", "stat", "lstat", "readlink", "listdir",
            "scandir", "walk", "fwalk", "access", "fork", "posix_spawn",
            "posix_spawnp", "system", "mkdir", "makedirs", "remove",
            "unlink", "rename", "replace", "rmdir", "chmod", "chown",
            "urandom", "getrandom",
        ):
            if hasattr(os, name):
                setattr(os, name, self._forbidden("direct-os-" + name))
        for name in (
            "time", "time_ns", "monotonic", "monotonic_ns", "perf_counter",
            "perf_counter_ns", "process_time", "process_time_ns",
            "thread_time", "thread_time_ns", "clock_gettime",
            "clock_gettime_ns", "sleep",
        ):
            if hasattr(time, name):
                setattr(time, name, self._forbidden("clock-" + name))
        self.installed = True


def secure_owner(wall: FirstPartySourceWall, row: tuple) -> bytes:
    require(type(row) is tuple and len(row) == 5,
            "require one entire independently pinned first-party owner")
    role, relative, expected, count, inode = row
    require(
        type(role) is str and type(relative) is str
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and type(count) is int and 0 < count <= MAX_OWNER_BYTES
        and type(inode) is int and inode > 0,
        "reject an unbounded or noncanonical first-party source owner",
    )
    hash_pin(expected, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "install the source wall before the first predecessor byte")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_IMODE(before.st_mode) == 0o600
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == count
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1,
            "reject a substituted complete first-party source: " + role,
        )
        remaining = count
        blocks: list[bytes] = []
        while remaining:
            block = os.read(descriptor, min(remaining, 65536))
            require(type(block) is bytes and bool(block),
                    "reject truncated complete first-party bytes: " + role)
            blocks.append(block)
            remaining -= len(block)
        require(os.read(descriptor, 1) == b"",
                "reject expanded complete first-party bytes: " + role)
        after = os.fstat(descriptor)
        require(all(
            getattr(before, field) == getattr(after, field)
            for field in (
                "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns",
                "st_nlink",
            )
        ), "reject concurrent mutation of the first-party owner: " + role)
        raw = b"".join(blocks)
        require(digest(raw) == expected,
                "reject changed complete first-party source bytes: " + role)
        return raw
    finally:
        os.close(descriptor)


def dynamic_owner(
    wall: FirstPartySourceWall, role: str, relative: str, pin: str,
) -> tuple:
    require(relative in (SOURCE, PROTOCOL, CONTRACT),
            "reject unrelated dynamic V23 build-source ownership")
    hash_pin(pin, relative)
    absolute = ROOT + "/" + relative
    require(wall.installed and wall.approved(absolute),
            "authenticate a source owner only after the new physical wall")
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute, flags)
    try:
        value = os.fstat(descriptor)
        require(
            stat.S_ISREG(value.st_mode)
            and stat.S_IMODE(value.st_mode) == 0o600
            and value.st_dev == DEVICE
            and value.st_uid == os.geteuid()
            and value.st_nlink == 1
            and 0 < value.st_size <= MAX_OWNER_BYTES,
            "reject an exchanged exact V23 source-build owner",
        )
        return role, relative, pin, value.st_size, value.st_ino
    finally:
        os.close(descriptor)


def owner_document(row: tuple, *, uid: bool = True) -> dict:
    result = {
        "role": row[0], "path": row[1], "sha256": row[2], "bytes": row[3],
        "device": DEVICE, "inode": row[4], "mode": "0600", "nlink": 1,
    }
    if uid:
        result["uid"] = os.geteuid()
    return result


def simple_owner(row: tuple) -> dict:
    return {"path": row[1], "sha256": row[2], "bytes": row[3]}


def decode_public(
    capture: types.ModuleType, semantic: types.ModuleType,
    raw: bytes, label: str,
) -> dict:
    value = semantic.StrictJSON(raw).decode()
    require(type(value) is dict,
            "decode one complete strict public JSON object: " + label)
    require(raw == capture.canonical_document(semantic, value),
            "reject a noncanonical or truncated public document: " + label)
    return value


def bootstrap_parent(wall: FirstPartySourceWall) -> types.ModuleType:
    row = CAMPAIGN_V23_OWNERS[0]
    raw = secure_owner(wall, row)
    module = types.ModuleType("_rebar_build_v23_exact_frozen_campaign_v23")
    module.__file__ = ROOT + "/" + row[1]
    exec(compile(raw, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(
        module.SOURCE == CAMPAIGN_V23_OWNERS[0][1]
        and module.PROTOCOL == CAMPAIGN_V23_OWNERS[1][1]
        and module.CONTRACT == CAMPAIGN_V23_OWNERS[2][1]
        and module.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v23"
        and module.VERSION == 23
        and module.CAPTURE_V2_OWNERS == CAPTURE_V2_OWNERS
        and module.PUBLIC_OWNERS == PUBLIC_OWNERS
        and module.GUARD_OWNERS == GUARD_OWNERS
        and module.STATIC_OWNERS == PARENT_STATIC_OWNERS
        and callable(module.load_context)
        and callable(module.validate_exact_campaign)
        and callable(module.validate_exact_actual)
        and callable(module.validate_guard_v3),
        "reject a substituted factually corrected complete V23 source freeze",
    )
    no_matching_imports()
    return module


def verify_native_documents(v9: object, v16: object, adapter: object) -> None:
    require(
        type(v9) is dict
        and v9.get("schema")
        == "rebar-phase2-owned-native-source-build-v9-source-freeze"
        and v9.get("version") == 9
        and v9.get("family") == FAMILY,
        "authenticate the immutable first-party V9 offline compiler kernel",
    )
    package = v9.get("rust_package")
    policy = v9.get("future_build_policy")
    baseline = v9.get("source_baseline")
    require(
        type(package) is dict
        and package.get("name") == "rebar-rust-continuation"
        and package.get("version") == "0.1.0"
        and package.get("edition") == "2024"
        and package.get("rust_version") == "1.85"
        and package.get("crate_type") == ["cdylib"]
        and package.get("package_count") == 1
        and package.get("external_dependency_count") == 0
        and package.get("lock_format_version") == 4
        and package.get("publish") is False
        and package.get("release_opt_level") == 3
        and package.get("release_lto") is True
        and package.get("release_codegen_units") == 1
        and package.get("release_panic") == "abort"
        and package.get("network") == "FORBIDDEN",
        "reject an external Rust package, regex crate, or modified Cargo lock",
    )
    require(
        type(baseline) is dict
        and baseline.get("candidate_source_mutation") == "FORBIDDEN"
        and baseline.get("rust_source_owner_count") == 9
        and baseline.get("rust_sources")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS],
        "preserve all nine original canonical Rust source owners exactly",
    )
    require(
        type(policy) is dict
        and policy.get("rustc") == RUSTC
        and policy.get("cargo") == CARGO
        and policy.get("compiler") == GCC
        and policy.get("elf_inspector") == READELF
        and policy.get("phase_names") == list(PHASES)
        and policy.get("process_names_per_phase") == list(PROCESS_NAMES)
        and policy.get("processes_per_phase") == 14
        and policy.get("total_future_processes") == 28
        and policy.get("cargo_net_offline") is True
        and policy.get("cargo_flags") == [
            "build", "--manifest-path", "--release", "--locked",
            "--offline", "--frozen", "--target-dir",
        ]
        and policy.get("gcc_flags") == list(GCC_FLAGS)
        and policy.get("external_cargo_dependencies") == "FORBIDDEN"
        and policy.get("external_engine") == "FORBIDDEN"
        and policy.get("fallback") == "FORBIDDEN"
        and policy.get("network") == "FORBIDDEN"
        and policy.get("engine_name") == "_rust_engine.so"
        and policy.get("bridge_name")
        == "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
        and policy.get("bridge_runpath") == "$ORIGIN"
        and policy.get("python_include") == PYTHON_INCLUDE
        and policy.get("candidate_imports") == 0
        and policy.get("candidate_processes_started") == 0,
        "reject unpinned Rust 1.95 or a weakened reproducible offline build",
    )

    require(
        type(v16) is dict
        and v16.get("schema")
        == "rebar-phase2-owned-rust-buffer-shape-source-build-v16-source-freeze"
        and v16.get("version") == 16
        and v16.get("family") == FAMILY
        and v16.get("source", {}).get("sha256")
        == NATIVE_SOURCE_OWNERS[3][2]
        and v16.get("protocol", {}).get("sha256")
        == NATIVE_SOURCE_OWNERS[4][2],
        "authenticate the complete immutable first-party V16 build policy",
    )
    native = v16.get("future_offline_native_build")
    family = v16.get("first_party_source_family")
    history = v16.get("historical_first_party_source_derivation")
    require(
        type(native) is dict
        and native.get("toolchain") == list(TOOLCHAIN_OWNERS)
        and native.get("phase_count") == 2
        and native.get("processes_per_phase") == 14
        and native.get("total_successful_process_count") == 28
        and native.get("unique_successful_process_ids_required") is True
        and native.get("ordered_process_names_per_phase") == list(PROCESS_NAMES)
        and native.get("cargo_net_offline") is True
        and native.get("offline_cargo_flags") == [
            "--release", "--locked", "--offline", "--frozen", "--target-dir",
        ]
        and native.get("complete_raw_elf_comparison_required") is True
        and native.get("candidate_execution") == "FORBIDDEN"
        and native.get("native_library_loading") == "FORBIDDEN"
        and native.get("network_requests_allowed") == 0,
        "reject a substitute toolchain, candidate execution, or fabricated ELF",
    )
    require(
        type(family) is dict
        and family.get("canonical_rust_source_owner_count") == 9
        and family.get("canonical_rust_source_owners")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS]
        and family.get("external_cargo_dependency_count") == 0
        and family.get("rust_cargo_package_count") == 1
        and family.get("stdlib_regular_expression_engine") == "FORBIDDEN"
        and family.get("cpython_sre_engine") == "FORBIDDEN"
        and family.get("external_regular_expression_engine") == "FORBIDDEN"
        and family.get("another_candidate_engine") == "FORBIDDEN"
        and family.get("production_matching_fallback") == "FORBIDDEN"
        and family.get("original_sources_modified") is False,
        "reject stdlib, external, cross-candidate, or fallback delegation",
    )
    require(
        type(history) is dict
        and history.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and history.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and history.get("canonical_original_modified") is False
        and history.get("adapter_repair_owners")
        == [simple_owner(row) for row in ADAPTER_REPAIR_OWNERS],
        "retain the independently reproducible first-party private adapter",
    )

    require(
        type(adapter) is dict
        and adapter.get("schema")
        == "rebar-phase2-owned-rust-public-contract-source-repair-v3-"
        "source-freeze"
        and adapter.get("version") == 3
        and adapter.get("source", {}).get("sha256")
        == ADAPTER_REPAIR_OWNERS[0][2]
        and adapter.get("protocol", {}).get("sha256")
        == ADAPTER_REPAIR_OWNERS[1][2],
        "authenticate the complete immutable first-party adapter repair",
    )
    repair = adapter.get("repair")
    source = adapter.get("rust_source")
    boundary = adapter.get("phase_boundary")
    require(
        type(repair) is dict
        and repair.get("original") == {
            "path": CANONICAL_RUST_OWNERS[8][1],
            "sha256": CANONICAL_RUST_OWNERS[8][2],
            "bytes": CANONICAL_RUST_OWNERS[8][3], "modified": False,
        }
        and repair.get("derived", {}).get("sha256") == ADAPTER_SHA
        and repair.get("derived", {}).get("bytes") == ADAPTER_BYTES
        and repair.get("derived", {}).get("materialized") is False
        and repair.get("cross_family_delegation_added") is False
        and repair.get("external_regex_engine_added") is False
        and repair.get("stdlib_regex_delegation_added") is False
        and type(source) is dict
        and source.get("cargo_lock_package_count") == 1
        and source.get("cross_family_dependency_count") == 0
        and source.get("external_regex_dependency_count") == 0
        and source.get("owners")
        == [simple_owner(row) for row in CANONICAL_RUST_OWNERS]
        and type(boundary) is dict
        and boundary.get("candidate_imports") == 0
        and boundary.get("candidate_workers_started") == 0
        and boundary.get("compiler_processes_started") == 0
        and boundary.get("holdout") == "NOT OPENED",
        "never import the adapter repair, its stdlib oracle, or a candidate",
    )


def verify_variant(
    semantic: types.ModuleType, baseline: bytes, materialized: bytes,
    matcher: bytes,
) -> dict:
    require(digest(baseline) == A0_SHA and len(baseline) == 179520,
            "authenticate the complete actual captured-findall a0 source")
    require(digest(materialized) == VARIANT_SHA
            and len(materialized) == VARIANT_BYTES,
            "authenticate the complete materialized a127 capture-clamp bridge")
    require(digest(matcher) == MATCHER_SHA and len(matcher) == 177967,
            "preserve the actual complete original first-party Rust matcher")

    outer = semantic.OUTER_LENGTH_REWRITE
    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    failed = semantic.FAILED_REPLACEMENT_CORRECTED
    capture = semantic.CAPTURE_INSERTION
    require(
        type(outer) is bytes and len(outer) == 660
        and type(original) is bytes and len(original) == 97
        and type(failed) is bytes and len(failed) == 384
        and type(capture) is bytes
        and len(capture.splitlines()) == 17,
        "authenticate only complete frozen original first-party anchors",
    )
    helper_start = b"static int rust_restore_original_template_error("
    helper_follow = b"\nstatic int rust_replacement_cache("
    before, helper, after = semantic.split_function(
        baseline, helper_start, helper_follow,
        "one real captured-base error-position helper",
    )
    require(helper.count(outer) == 1 and baseline.count(outer) == 1,
            "remove exactly one frozen 660-byte original outer-length block")
    corrected_helper = helper.replace(outer, b"", 1)
    require(b"PyObject_Length(replacement)" not in corrected_helper,
            "reject reintroduced error-position exporter probing")
    predecessor = before + corrected_helper + after
    require(
        digest(predecessor) == INPUT_VARIANT_SHA
        and len(predecessor) == INPUT_VARIANT_BYTES,
        "rederive every byte of the immutable actual V24 1adb bridge",
    )
    old_capture = (
        b"    if (end > capture.length) {\n"
        b"        rust_subject_release(&capture);\n"
        b"        PyErr_SetString(\n"
        b"            PyExc_BufferError,\n"
        b'            "Rust captured buffer changed size during replacement"\n'
        b"        );\n"
        b"        return -1;\n"
        b"    }\n"
        b"    int result = rust_output_subject(writer, &capture, begin, end);\n"
    )
    new_capture = (
        b"    size_t first = begin > capture.length ? capture.length : begin;\n"
        b"    size_t finish = end > capture.length ? capture.length : end;\n"
        b"    if (finish < first) finish = first;\n"
        b"    int result = rust_output_subject(writer, &capture, first, finish);\n"
    )
    function_start = b"static int rust_output_capture("
    function_follow = b"\nstatic int rust_output_template("
    prefix, previous_function, suffix = semantic.split_function(
        predecessor, function_start, function_follow,
        "the one complete original V24 mutable-buffer capture function",
    )
    require(
        len(old_capture) == 299 and len(new_capture) == 244
        and previous_function.count(old_capture) == 1
        and predecessor.count(old_capture) == 1
        and previous_function.count(new_capture) == 0,
        "replace exactly one complete unsafe V24 capture bound guard",
    )
    corrected_function = previous_function.replace(old_capture, new_capture, 1)
    derived = prefix + corrected_function + suffix
    require(
        derived == materialized and digest(derived) == VARIANT_SHA
        and len(derived) == VARIANT_BYTES,
        "prove all 178805 complete capture-clamp bytes from immutable V24",
    )
    require(
        corrected_function.count(b"rust_subject_open(&capture,") == 1
        and corrected_function.count(b"rust_subject_release(&capture);") == 1
        and corrected_function.count(
            b"if (writer->text || PyBytes_CheckExact(subject->object))",
        ) == 1
        and corrected_function.count(
            b"size_t first = begin > capture.length ? capture.length : begin;",
        ) == 1
        and corrected_function.count(
            b"size_t finish = end > capture.length ? capture.length : end;",
        ) == 1
        and corrected_function.count(b"if (finish < first) finish = first;")
        == 1
        and corrected_function.count(
            b"rust_output_subject(writer, &capture, first, finish)",
        ) == 1
        and b"PyExc_BufferError" not in corrected_function,
        "preserve fast-path/acquire/release and clamp both capture bounds",
    )

    cache_start = b"static int rust_replacement_cache("
    cache_follow = b"\nstatic PyObject *rust_normalize_expand_buffer("
    _left, original_cache, _right = semantic.split_function(
        baseline, cache_start, cache_follow,
        "the genuine 97-byte original replacement branch",
    )
    _left2, repaired_cache, _right2 = semantic.split_function(
        materialized, cache_start, cache_follow,
        "the byte-identical 97-byte repaired replacement branch",
    )
    require(
        original_cache == repaired_cache
        and original_cache.count(original) == 1
        and original_cache.count(failed) == 0
        and repaired_cache.count(failed) == 0,
        "reject the known-failing f9 early guard or any replacement-cache edit",
    )
    capture_start = b"static int rust_append_batched_findall("
    capture_follow = b"\nstatic PyObject *rust_batched_findall("
    _cl, original_capture, _cr = semantic.split_function(
        baseline, capture_start, capture_follow,
        "original captured first-party findall fast path",
    )
    _vl, final_capture, _vr = semantic.split_function(
        materialized, capture_start, capture_follow,
        "materialized captured first-party findall fast path",
    )
    require(
        original_capture == final_capture
        and original_capture.count(capture) == 1
        and final_capture.count(capture) == 1,
        "preserve all 17 genuine first-party two-capture fast-path lines",
    )
    forbidden_c = (
        b'PyImport_ImportModule("re")',
        b'PyImport_ImportModule("_sre")',
        b'PyImport_ImportModule("regex")',
        b"#include <regex.h>", b"#include <pcre", b"dlopen(",
        b"PyRun_",
    )
    forbidden_rust = (
        b"extern crate regex", b"extern crate regex_automata",
        b"extern crate pcre", b"extern crate onig",
        b"use regex::", b"use regex_automata::", b"use pcre2::",
        b"use onig::", b"use fancy_regex::",
    )
    require(not any(marker in materialized for marker in forbidden_c)
            and not any(marker in matcher for marker in forbidden_rust),
            "reject delegated stdlib, external-crate, or native matching")
    return {
        "base_sha256": A0_SHA,
        "base_bytes": 179520,
        "immutable_actual_v24_bridge_sha256": INPUT_VARIANT_SHA,
        "immutable_actual_v24_bridge_bytes": INPUT_VARIANT_BYTES,
        "materialized_variant_sha256": VARIANT_SHA,
        "materialized_variant_bytes": VARIANT_BYTES,
        "capture_clamp_function_count": 1,
        "capture_clamp_old_guard_bytes": len(old_capture),
        "capture_clamp_corrected_guard_bytes": len(new_capture),
        "capture_clamp_removed_bytes": len(old_capture) - len(new_capture),
        "capture_lower_bound_clamped": True,
        "capture_upper_bound_clamped": True,
        "capture_finish_at_least_first": True,
        "capture_acquire_release_preserved": True,
        "capture_fast_path_preserved": True,
        "capture_buffer_error_guard_removed": True,
        "outer_length_block_removed_count": 1,
        "outer_length_block_removed_bytes": 660,
        "original_replacement_anchor_bytes": 97,
        "known_failing_f9_replacement_anchor_bytes": 384,
        "known_failing_f9_guard_added": False,
        "replacement_cache_byte_identical": True,
        "captured_findall_fast_path_lines": 17,
        "captured_findall_byte_identical": True,
        "matching_engine_sha256": MATCHER_SHA,
        "matching_engine_bytes": 177967,
        "matching_engine_changed": False,
        "complete_variant_source_materialized": True,
        "complete_variant_source_authenticated": True,
        "canonical_original_bridge_modified": False,
        "canonical_original_adapter_modified": False,
        "native_engine_built": False,
        "native_bridge_built": False,
        "candidate_imported": False,
        "candidate_correctness": NOT_MEASURED,
    }


def native_build_plan() -> dict:
    require(len(BUILD_LABEL) == 48 and len(PHASES) == 2
            and len(PROCESS_NAMES) == 14,
            "reject an unsafe build label or incomplete dual-phase plan")
    return {
        "status": "NOT RUN",
        "label": BUILD_LABEL,
        "root_parent": "/tmp",
        "private_root": "NOT CREATED; NOT OPENED",
        "root_prefix": "rebar-phase2-native-build-v9-rust-",
        "phase_names": list(PHASES),
        "phase_count": 2,
        "process_names_per_phase": list(PROCESS_NAMES),
        "processes_per_phase": 14,
        "required_actual_distinct_compiler_process_count": 28,
        "actual_compiler_process_count": 0,
        "actual_process_ids": [],
        "toolchain": list(TOOLCHAIN_OWNERS),
        "cargo": CARGO,
        "rustc": RUSTC,
        "compiler": GCC,
        "elf_inspector": READELF,
        "cpython": PYTHON,
        "cpython_sha256": PYTHON_SHA256,
        "cpython_include": PYTHON_INCLUDE,
        "cargo_flags": [
            "build", "--manifest-path", "--release", "--locked",
            "--offline", "--frozen", "--target-dir",
        ],
        "gcc_flags": list(GCC_FLAGS),
        "phase_prefix_map_target": "/rebar-phase2-v6-owned-source",
        "rust_soname": "_rust_engine.so",
        "bridge_runpath": "$ORIGIN",
        "phase_environment": {
            "PATH": RUST_TOOLCHAIN + "/bin:/usr/bin:/bin",
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
            "SOURCE_DATE_EPOCH": "1",
            "TMPDIR": "<FRESH_PRIVATE_PHASE>/temporary",
            "CARGO_HOME": "<FRESH_PRIVATE_PHASE>/cargo-home",
            "CARGO_NET_OFFLINE": "true",
            "CARGO_INCREMENTAL": "0",
            "CARGO_BUILD_JOBS": "1",
            "RUSTC": RUSTC,
            "RUSTFLAGS": (
                "--remap-path-prefix=<REFERENCE_A_SOURCE>="
                "/rebar-phase2-v6-owned-source "
                "--remap-path-prefix=<REFERENCE_B_SOURCE>="
                "/rebar-phase2-v6-owned-source "
                "-Clink-arg=-Wl,-soname,_rust_engine.so"
            ),
        },
        "canonical_source_owner_count": 9,
        "original_source_owners_per_phase": 6,
        "private_variant_overlay_count_per_phase": 1,
        "private_compiler_source_overlay_count_per_phase": 1,
        "private_compiler_source_sha256": COMPILER_VARIANT_SHA,
        "private_compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "canonical_matching_source_sha256": MATCHER_SHA,
        "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
        "private_corrected_adapter_overlay_count_per_phase": 1,
        "private_variant_sha256": VARIANT_SHA,
        "private_variant_bytes": VARIANT_BYTES,
        "private_corrected_adapter_sha256": ADAPTER_SHA,
        "private_corrected_adapter_bytes": ADAPTER_BYTES,
        "cross_phase_complete_engine_elf_equality_required": True,
        "cross_phase_complete_bridge_elf_equality_required": True,
        "immutable_previous_v24_engine_sha256": PREVIOUS_ENGINE_SHA,
        "immutable_successful_v25_engine_sha256": PREVIOUS_ENGINE_SHA,
        "new_engine_sha256": NOT_MEASURED,
        "new_engine_may_differ_from_successful_v25": True,
        "immutable_successful_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
        "immutable_successful_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
        "immutable_previous_v24_bridge_sha256": PREVIOUS_BRIDGE_SHA,
        "engine_sha256": NOT_MEASURED,
        "bridge_sha256": NOT_MEASURED,
        "engine_bytes": NOT_MEASURED,
        "bridge_bytes": NOT_MEASURED,
        "public_build_receipt_sha256": NOT_MEASURED,
        "public_root_receipt_sha256": NOT_MEASURED,
        "archives_opened": 0,
        "private_roots_opened": 0,
        "native_libraries_loaded": 0,
        "compiler_processes_started": 0,
        "network_requests": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "stdlib_re_engine": "FORBIDDEN",
        "stdlib_sre_engine": "FORBIDDEN",
        "external_regex_engine": "FORBIDDEN",
        "external_cargo_dependency_count": 0,
        "cross_candidate_engine": "FORBIDDEN",
        "matching_fallback": "FORBIDDEN",
        "run_authorization": (
            "IMPLEMENTED; ROOT AUTHORIZATION REQUIRED AFTER PUSH; NOT RUN"
        ),
        "actual_modes_implemented": ["--run", "--build"],
        "required_actual_authority_flags": [
            "--source-sha256", "--protocol-sha256", "--contract-sha256",
            "--label", "--variant-sha256", "--variant-bytes",
            "--corrected-adapter-sha256", "--corrected-adapter-bytes",
            "--previous-v23-source-sha256",
            "--previous-v23-protocol-sha256",
            "--previous-v23-contract-sha256",
            "--previous-v24-build-source-sha256",
            "--previous-v24-build-protocol-sha256",
            "--previous-v24-build-contract-sha256",
            "--previous-v24-build-receipt-sha256",
            "--previous-v24-root-receipt-sha256",
            "--previous-v24-failure-receipt-sha256",
            "--runtime-guard-v4-source-sha256",
            "--runtime-guard-v4-protocol-sha256",
            "--runtime-guard-v4-contract-sha256",
            "--capture-clamp-source-sha256",
            "--capture-clamp-protocol-sha256",
            "--capture-clamp-contract-sha256",
            "--phase1-v4-source-sha256",
            "--phase1-v4-protocol-sha256",
            "--phase1-v4-contract-sha256",
            "--compiler-source-sha256", "--compiler-source-bytes",
            "--compiler-freeze-source-sha256",
            "--compiler-freeze-protocol-sha256",
            "--compiler-freeze-contract-sha256",
            "--compiler-application-sha256",
            "--previous-v25-source-sha256",
            "--previous-v25-protocol-sha256",
            "--previous-v25-contract-sha256",
            "--previous-v25-publication-sha256",
            "--previous-v25-root-sha256",
            "--previous-v25-campaign-source-sha256",
            "--previous-v25-campaign-protocol-sha256",
            "--previous-v25-campaign-contract-sha256",
            "--previous-v25-failure-receipt-sha256",
            "--owned-source-sha256 (exactly nine)",
        ],
        "candidate_correctness": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
    }


def validate_native_build_plan(value: object) -> None:
    require(type(value) is dict and value == native_build_plan(),
            "reject omitted or weakened first-party dual-build requirements")


def verify_previous_actual_v24(
    build: object, campaign: object, guard: object,
    build_receipt: object, root_receipt: object, failure: object,
    input_variant: bytes,
) -> None:
    require(
        type(build) is dict
        and build.get("schema")
        == "rebar-phase2-owned-rust-capture-shape-semantics-v2-"
           "source-build-v24-source-freeze"
        and build.get("version") == 24
        and build.get("family") == FAMILY
        and build.get("source", {}).get("sha256") == BUILD_V24_OWNERS[0][2]
        and build.get("protocol", {}).get("sha256") == BUILD_V24_OWNERS[1][2]
        and build.get("materialized_first_party_variant", {}).get(
            "complete_source_sha256",
        ) == INPUT_VARIANT_SHA
        and build.get("materialized_first_party_variant", {}).get(
            "complete_source_bytes",
        ) == INPUT_VARIANT_BYTES
        and build.get("frozen_offline_dual_phase_build", {}).get("phase_count")
        == 2
        and build.get("frozen_offline_dual_phase_build", {}).get(
            "required_actual_distinct_compiler_process_count",
        ) == 28
        and build.get("frozen_offline_dual_phase_build", {}).get(
            "external_cargo_dependency_count",
        ) == 0
        and digest(input_variant) == INPUT_VARIANT_SHA
        and len(input_variant) == INPUT_VARIANT_BYTES,
        "authenticate the exact full prior V24 source freeze and bridge",
    )
    require(
        type(campaign) is dict
        and campaign.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v24-"
           "recoverable-source-freeze"
        and campaign.get("version") == 24
        and campaign.get("source", {}).get("sha256")
        == CAMPAIGN_V24_OWNERS[0][2]
        and campaign.get("protocol", {}).get("sha256")
        == CAMPAIGN_V24_OWNERS[1][2]
        and campaign.get("original_correctness_boundary", {}).get(
            "case_execution_denominator",
        ) == 31237
        and campaign.get("original_correctness_boundary", {}).get("suite_count")
        == 13
        and campaign.get("original_correctness_boundary", {}).get(
            "named_private_waiver_count",
        ) == 13
        and campaign.get("actual_v24_native_build", {}).get("build_status")
        == "PASS"
        and campaign.get("actual_v24_native_build", {}).get(
            "publication_receipt", {},
        ).get("sha256") == PREVIOUS_BUILD_RECEIPT_SHA
        and campaign.get("actual_v24_native_build", {}).get(
            "root_provenance_receipt", {},
        ).get("sha256") == PREVIOUS_ROOT_RECEIPT_SHA
        and campaign.get("operational_runtime_guard_v4", {}).get("version")
        == 4
        and campaign.get("operational_runtime_guard_v4", {}).get(
            "complete_contract_sha256",
        ) == RUNTIME_GUARD_V4_OWNERS[2][2],
        "preserve the complete independently pinned strict V24 campaign",
    )
    require(
        type(guard) is dict
        and guard.get("schema")
        == "rebar-owned-candidate-runtime-independence-v4-source-freeze"
        and guard.get("version") == 4
        and guard.get("source", {}).get("sha256")
        == RUNTIME_GUARD_V4_OWNERS[0][2]
        and guard.get("protocol", {}).get("sha256")
        == RUNTIME_GUARD_V4_OWNERS[1][2]
        and guard.get("source_only_effects", {}).get("candidate_imports") == 0
        and guard.get("source_only_effects", {}).get(
            "compiler_processes_started",
        ) == 0
        and guard.get("holdout") == "NOT OPENED",
        "preserve the complete immutable strict runtime guard V4",
    )
    require(
        type(build_receipt) is dict
        and build_receipt.get("status") == "PASS"
        and build_receipt.get("build_status") == "PASS"
        and build_receipt.get("source_sha256") == BUILD_V24_OWNERS[0][2]
        and build_receipt.get("protocol_sha256") == BUILD_V24_OWNERS[1][2]
        and build_receipt.get("contract_sha256") == BUILD_V24_OWNERS[2][2]
        and build_receipt.get("combined_bridge_sha256") == INPUT_VARIANT_SHA
        and build_receipt.get("combined_bridge_bytes") == INPUT_VARIANT_BYTES
        and build_receipt.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and build_receipt.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and build_receipt.get("actual_compiler_process_count") == 28
        and build_receipt.get("actual_completed_phase_count") == 2
        and build_receipt.get("candidate_workers_started") == 0
        and build_receipt.get("holdout") == "NOT OPENED",
        "preserve the genuine da4 actual V24 first-party build success",
    )
    require(
        type(root_receipt) is dict
        and root_receipt.get("status") == "PASS"
        and root_receipt.get("version") == 24
        and root_receipt.get("canonical_build_status") == "PASS"
        and root_receipt.get("canonical_build_receipt_sha256")
        == PREVIOUS_BUILD_RECEIPT_SHA
        and root_receipt.get("materialized_complete_bridge_sha256")
        == INPUT_VARIANT_SHA
        and root_receipt.get("materialized_complete_bridge_bytes")
        == INPUT_VARIANT_BYTES
        and root_receipt.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and root_receipt.get("actual_compiler_process_count") == 28
        and root_receipt.get("actual_source_phase_count") == 2
        and root_receipt.get("bridge_overlay_apply_count") == 2
        and root_receipt.get("adapter_overlay_apply_count") == 2
        and root_receipt.get("cross_phase_complete_engine_elf_byte_identical")
        is True
        and root_receipt.get("cross_phase_complete_bridge_elf_byte_identical")
        is True
        and type(root_receipt.get("actual_reproduced_native_outputs")) is dict
        and root_receipt["actual_reproduced_native_outputs"].get(
            "engine", {},
        ).get("sha256") == PREVIOUS_ENGINE_SHA
        and root_receipt["actual_reproduced_native_outputs"].get(
            "bridge", {},
        ).get("sha256") == PREVIOUS_BRIDGE_SHA
        and root_receipt.get("actual_original_runtime_target_count") == 4
        and root_receipt.get("all_original_runtime_target_identities_restored")
        is True
        and root_receipt.get("actual_original_runtime_targets_before")
        == root_receipt.get("actual_original_runtime_targets_after")
        and type(root_receipt.get("actual_original_runtime_targets_after"))
        is dict
        and set(root_receipt["actual_original_runtime_targets_after"])
        == {
            "original_bridge_source", "original_public_adapter",
            "original_installed_engine", "original_installed_bridge",
        }
        and root_receipt["actual_original_runtime_targets_after"][
            "original_bridge_source"
        ].get("sha256") == CANONICAL_RUST_OWNERS[2][2]
        and root_receipt["actual_original_runtime_targets_after"][
            "original_public_adapter"
        ].get("sha256") == CANONICAL_RUST_OWNERS[8][2]
        and root_receipt["actual_original_runtime_targets_after"][
            "original_installed_engine"
        ].get("sha256")
        == "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"
        and root_receipt["actual_original_runtime_targets_after"][
            "original_installed_bridge"
        ].get("sha256")
        == "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15"
        and type(root_receipt.get("root")) is dict
        and root_receipt["root"].get("mode") == "0700"
        and type(root_receipt.get("actual_compiler_process_ids")) is list
        and len(root_receipt["actual_compiler_process_ids"]) == 28
        and len(frozenset(root_receipt["actual_compiler_process_ids"])) == 28
        and root_receipt.get("holdout") == "NOT OPENED",
        "preserve the complete genuine f211 V24 private-root provenance",
    )
    require(
        type(failure) is dict
        and failure.get("status") == "PASS"
        and failure.get("publication_status") == "PASS"
        and failure.get("candidate_status") == "FAIL"
        and failure.get("semantic_mismatch_count") == 1352
        and failure.get("verified_passing_case_count") == 15877
        and failure.get("case_execution_denominator") == 31237
        and failure.get("suite_count") == 13
        and failure.get("completed_suite_count") == 13
        and failure.get("actual_candidate_workers") == 13
        and failure.get("distinct_worker_process_id_count") == 13
        and type(failure.get("actual_worker_process_ids")) is list
        and len(failure["actual_worker_process_ids"]) == 13
        and len(frozenset(failure["actual_worker_process_ids"])) == 13
        and failure.get("named_private_waiver_count") == 13
        and failure.get("combined_bridge_source_sha256") == INPUT_VARIANT_SHA
        and failure.get("combined_bridge_source_bytes") == INPUT_VARIANT_BYTES
        and failure.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and failure.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and failure.get("actual_v24_build_receipt_sha256")
        == PREVIOUS_BUILD_RECEIPT_SHA
        and failure.get("actual_v24_compiler_process_count") == 28
        and failure.get("worker_failure_capture_complete") is True
        and failure.get("all_worker_failure_capture_count") == 0
        and failure.get("holdout") == "NOT OPENED",
        "preserve every independently observed genuine V24 FAIL-1352 fact",
    )
    suites = failure.get("suite_integrity")
    require(
        type(suites) is list and len(suites) == 13
        and all(type(row) is dict and row.get("fully_observed") is True
                for row in suites)
        and sum(row.get("mismatch_count", -1) for row in suites) == 1352
        and {
            row["suite"]: row["mismatch_count"]
            for row in suites if row.get("mismatch_count", 0)
        } == {"substitution_v2": 240, "shape_v2": 1112}
        and sum(row.get("verified_passing_case_count", -1) for row in suites)
        == 15877,
        "preserve all 13 actual rows and exact 240 + 1112 mismatch accounting",
    )


def verify_capture_clamp_freeze(
    wall: FirstPartySourceWall | None, source: bytes, contract: object,
    actual_v24_failure: dict, predecessor: bytes, materialized: bytes,
) -> types.ModuleType:
    require(
        type(source) is bytes and digest(source) == CAPTURE_CLAMP_OWNERS[0][2]
        and len(source) == CAPTURE_CLAMP_OWNERS[0][3]
        and type(contract) is dict
        and contract.get("schema")
        == "rebar-owned-rust-capture-clamp-semantics-v1-source-freeze"
        and contract.get("version") == 1
        and contract.get("source", {}).get("sha256")
        == CAPTURE_CLAMP_OWNERS[0][2]
        and contract.get("protocol", {}).get("sha256")
        == CAPTURE_CLAMP_OWNERS[1][2],
        "authenticate the full independently frozen capture-clamp controller",
    )
    assert isinstance(contract, dict)
    derivation = contract.get("derived_first_party_capture_clamp")
    failure = contract.get("actual_complete_v24_candidate_failure")
    semantics = contract.get("public_explicit_synthetic_semantics")
    proposal = contract.get("expanded_sealed_holdout_v2_proposal_metadata_only")
    require(
        type(derivation) is dict
        and derivation.get("source_base_path") == INPUT_VARIANT_OWNER[1]
        and derivation.get("source_base_sha256") == INPUT_VARIANT_SHA
        and derivation.get("source_base_bytes") == INPUT_VARIANT_BYTES
        and derivation.get("target_path") == VARIANT_OWNER[1]
        and derivation.get("sha256") == VARIANT_SHA
        and derivation.get("bytes") == VARIANT_BYTES
        and derivation.get("changed_function_count") == 1
        and derivation.get("changed_functions") == ["rust_output_capture"]
        and derivation.get("replacement_site_count") == 1
        and derivation.get("source_delta_bytes") == -55
        and derivation.get("acquisition_and_release_preserved") is True
        and derivation.get("fresh_export_begin_clamped") is True
        and derivation.get("fresh_export_end_clamped") is True
        and derivation.get("reversed_clamped_interval_normalized") is True
        and derivation.get("changed_size_buffer_error_removed") is True
        and derivation.get("out_of_bounds_capture_precluded") is True
        and derivation.get("bytes_or_text_fast_path_preserved") is True
        and derivation.get("matcher_engine_changed") is False
        and derivation.get("external_regex_dependency_added") is False
        and derivation.get("stdlib_matching_delegation_added") is False
        and derivation.get("cross_candidate_engine_added") is False
        and derivation.get("candidate_built") is False
        and derivation.get("candidate_imported") is False
        and derivation.get("candidate_matching") == "NOT RUN",
        "preserve every independently frozen safe capture-clamp obligation",
    )
    require(
        type(failure) is dict
        and failure.get("publication_receipt_sha256")
        == PREVIOUS_FAILURE_RECEIPT_SHA
        and failure.get("candidate_status") == "FAIL"
        and failure.get("semantic_mismatch_count") == 1352
        and failure.get("verified_passing_case_count") == 15877
        and failure.get("fully_observed_suite_mismatch_counts")
        == {"substitution_v2": 240, "shape_v2": 1112}
        and failure.get("actual_worker_process_ids")
        == actual_v24_failure["actual_worker_process_ids"],
        "bind the independently frozen clamp to the complete V24 failure",
    )
    require(
        type(semantics) is dict
        and semantics.get("synthetic_exhaustive_bounds_case_count") == 4800
        and semantics.get("synthetic_alias_case_count") == 50
        and semantics.get("public_cpython_expected_bytes") == "X "
        and semantics.get("public_witness_clamped_spans")
        == [[0, 1], [1, 1]]
        and semantics.get("public_witness_executed_candidate") is False
        and semantics.get("possible_out_of_bounds_capture_read") is False
        and semantics.get("begin_and_end_both_clamped") is True
        and semantics.get("reversed_interval_normalized_to_empty") is True,
        "preserve the 4800-case source-only CPython capture-bound witness",
    )
    require(
        type(proposal) is dict
        and proposal.get("path")
        == "oracle/phase3/expanded-sealed-holdout-v2.json"
        and proposal.get("case_count")
        == EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT
        and proposal.get("sha256_independently_pinned_not_read")
        == EXPANDED_HOLDOUT_PROPOSAL_SHA
        and proposal.get("proposal_file_open_count") == 0
        and proposal.get("proposal_content_read") is False
        and proposal.get("final_protocol_status") == "NOT FROZEN"
        and proposal.get("case_status") == "NOT GENERATED; NOT OPENED",
        "preserve 141557760 sealed proposal metadata without opening it",
    )
    require(
        wall is None or isinstance(wall, FirstPartySourceWall)
        and wall.installed,
        "install the source-only wall before executing frozen transformer code",
    )
    module = types.ModuleType("_rebar_v25_frozen_capture_clamp_transformer")
    module.__file__ = ROOT + "/" + CAPTURE_CLAMP_OWNERS[0][1]
    exec(compile(source, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(
        module.SCHEMA
        == "rebar-owned-rust-capture-clamp-semantics-v1-source-freeze"
        and module.SOURCE == CAPTURE_CLAMP_OWNERS[0][1]
        and module.PROTOCOL == CAPTURE_CLAMP_OWNERS[1][1]
        and module.CONTRACT == CAPTURE_CLAMP_OWNERS[2][1]
        and module.VARIANT == VARIANT_OWNER[1]
        and module.V24_BRIDGE_SHA256 == INPUT_VARIANT_SHA
        and module.V24_BRIDGE_BYTES == INPUT_VARIANT_BYTES
        and module.DERIVED_BRIDGE_SHA256 == VARIANT_SHA
        and module.DERIVED_BRIDGE_BYTES == VARIANT_BYTES
        and callable(module.derive_bridge)
        and module.derive_bridge(predecessor) == materialized,
        "reexecute only the frozen pure one-function first-party derivation",
    )
    no_matching_imports()
    return module



def verify_previous_actual_v25(
    contract: object, publication: object, root: object,
) -> None:
    require(
        type(contract) is dict
        and contract.get("schema")
        == "rebar-phase2-owned-rust-capture-clamp-source-build-v25-source-freeze"
        and contract.get("version") == 25
        and contract.get("source", {}).get("sha256") == BUILD_V25_OWNERS[0][2]
        and contract.get("protocol", {}).get("sha256") == BUILD_V25_OWNERS[1][2]
        and contract.get("frozen_offline_dual_phase_build", {}).get("phase_count") == 2
        and contract.get("frozen_offline_dual_phase_build", {}).get(
            "required_actual_distinct_compiler_process_count",
        ) == 28
        and contract.get("frozen_offline_dual_phase_build", {}).get(
            "external_cargo_dependency_count",
        ) == 0
        and contract.get("materialized_first_party_variant", {}).get(
            "complete_source_sha256",
        ) == VARIANT_SHA,
        "authenticate the complete successful frozen V25 native-build lineage",
    )
    require(
        type(publication) is dict
        and publication.get("schema")
        == "rebar-phase2-owned-rust-capture-clamp-source-build-v25-"
           "durable-publication-receipt"
        and publication.get("status") == "PASS"
        and publication.get("build_status") == "PASS"
        and publication.get("source_sha256") == BUILD_V25_OWNERS[0][2]
        and publication.get("protocol_sha256") == BUILD_V25_OWNERS[1][2]
        and publication.get("contract_sha256") == BUILD_V25_OWNERS[2][2]
        and publication.get("actual_compiler_process_count") == 28
        and publication.get("actual_completed_phase_count") == 2
        and publication.get("combined_bridge_sha256") == VARIANT_SHA
        and publication.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and publication.get("holdout") == "NOT OPENED"
        and publication.get("latest_v24_candidate_status") == "FAIL"
        and publication.get("latest_v24_semantic_mismatch_count") == 1352,
        "preserve the exact complete genuinely successful V25 publication",
    )
    require(
        type(root) is dict
        and root.get("schema")
        == "rebar-phase2-owned-rust-capture-clamp-source-build-v25-"
           "durable-root-provenance-receipt"
        and root.get("version") == 25 and root.get("status") == "PASS"
        and root.get("source_sha256") == BUILD_V25_OWNERS[0][2]
        and root.get("protocol_sha256") == BUILD_V25_OWNERS[1][2]
        and root.get("contract_sha256") == BUILD_V25_OWNERS[2][2]
        and root.get("canonical_build_receipt_sha256") == V25_BUILD_RECEIPT_SHA
        and root.get("actual_compiler_process_count") == 28
        and root.get("actual_source_phase_count") == 2
        and root.get("all_original_runtime_target_identities_restored") is True
        and root.get("all_original_source_identities_restored") is True
        and root.get("actual_original_runtime_target_count") == 4
        and root.get("actual_reproduced_native_outputs", {}).get(
            "engine", {},
        ).get("sha256") == PREVIOUS_ENGINE_SHA
        and root.get("actual_reproduced_native_outputs", {}).get(
            "bridge", {},
        ).get("sha256")
        == "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4"
        and type(root.get("actual_compiler_process_ids")) is list
        and len(root["actual_compiler_process_ids"]) == 28
        and len(set(root["actual_compiler_process_ids"])) == 28
        and root.get("holdout") == "NOT OPENED",
        "preserve the complete successful V25 root and 28 genuine compiler IDs",
    )


def verify_compiler_allocation_freeze(
    wall: FirstPartySourceWall | None,
    source: bytes, contract: object, application: object,
    canonical_source: bytes, materialized: bytes,
) -> types.ModuleType:
    require(
        type(source) is bytes
        and digest(source) == COMPILER_FASTPATH_OWNERS[0][2]
        and len(source) == COMPILER_FASTPATH_OWNERS[0][3]
        and type(contract) is dict
        and contract.get("schema")
        == "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
        and contract.get("version") == 1
        and contract.get("source", {}).get("sha256")
        == COMPILER_FASTPATH_OWNERS[0][2]
        and contract.get("protocol", {}).get("sha256")
        == COMPILER_FASTPATH_OWNERS[1][2],
        "authenticate the complete independently frozen compiler source owner",
    )
    assert isinstance(contract, dict)
    derived = contract.get("derived_first_party_compiler_source")
    semantics = contract.get("synthetic_differential_compiler_semantics")
    public = contract.get("independent_existing_public_practice")
    failure = contract.get("actual_complete_v24_candidate_failure")
    require(
        type(derived) is dict
        and derived.get("source_base_path") == CANONICAL_RUST_OWNERS[3][1]
        and derived.get("source_base_sha256") == MATCHER_SHA
        and derived.get("source_base_bytes") == CANONICAL_RUST_OWNERS[3][3]
        and derived.get("target_path") == COMPILER_VARIANT_OWNER[1]
        and derived.get("sha256") == COMPILER_VARIANT_SHA
        and derived.get("bytes") == COMPILER_VARIANT_BYTES
        and derived.get("exact_reversible_replacement_count") == 7
        and derived.get("semantic_optimization_count") == 2
        and derived.get("normal_pattern_u32_heap_clone_removed") is True
        and derived.get("scanner_phrase_u32_heap_clone_removed") is True
        and derived.get("alternation_free_parser_heap_allocation_removed") is True
        and derived.get("parser_borrow_retained_by_engine") is False
        and derived.get("external_dependencies_added") == 0
        and derived.get("materialized") is False
        and derived.get("built") is False and derived.get("executed") is False,
        "preserve the entire independently frozen compiler fast-path contract",
    )
    require(
        type(semantics) is dict
        and semantics.get("synthetic_case_count") == 960
        and semantics.get("synthetic_actual_alternation_case_count") == 680
        and semantics.get("synthetic_no_alternation_improved_case_count") == 456
        and semantics.get("synthetic_error_case_count") == 224
        and semantics.get("synthetic_distinct_scanner_runtime_flag_case_count") == 42
        and semantics.get("synthetic_source_lifetime_control_count") == 40
        and semantics.get("old_and_new_ast_match") is True
        and semantics.get("dangling_source_borrow_rejected") is True
        and semantics.get("candidate_executed") is False,
        "retain all 960 synthetic parser, scanner, and source-lifetime witnesses",
    )
    require(
        type(public) is dict
        and public.get("case_count") == 416
        and public.get("paired_row_count") == 1664
        and public.get("matrix_sha256")
        == "b13ff74122041ea792774fd5ee2d1f6d38033e94a1a6703c6e48522e461552a7"
        and public.get("baseline_total_ns") == 96434251
        and public.get("rust_total_ns") == 161853767
        and public.get("optimized_variant_measured") is False
        and public.get("optimized_variant_speed") == NOT_MEASURED
        and type(failure) is dict and failure.get("candidate_status") == "FAIL"
        and failure.get("semantic_mismatch_count") == 1352
        and failure.get("verified_passing_case_count") == 15877,
        "preserve authentic existing public practice and every real Rust loss",
    )
    require(
        type(application) is dict and application.get("status") == "PASS"
        and application.get("mode") == "apply"
        and application.get("source_sha256") == COMPILER_FASTPATH_OWNERS[0][2]
        and application.get("protocol_sha256") == COMPILER_FASTPATH_OWNERS[1][2]
        and application.get("contract_sha256") == COMPILER_FASTPATH_OWNERS[2][2]
        and application.get("variant_materialized") is True
        and application.get("derived_rust_source_sha256") == COMPILER_VARIANT_SHA
        and application.get("derived_rust_source_bytes") == COMPILER_VARIANT_BYTES
        and application.get("canonical_rust_source_sha256") == MATCHER_SHA
        and application.get("exact_reversible_replacement_count") == 7
        and application.get("synthetic_differential_case_count") == 960
        and application.get("synthetic_source_lifetime_control_count") == 40
        and application.get("preserved_public_paired_raw_sha256")
        == PUBLIC_PRACTICE_OWNERS[2][2]
        and application.get("materialized_variant", {}).get("inode")
        == COMPILER_VARIANT_OWNER[4]
        and application.get("materialized_variant", {}).get("exclusive_no_follow")
        is True
        and application.get("compiler_processes_started") == 0
        and application.get("candidate_imports") == 0
        and application.get("holdout") == "NOT OPENED",
        "authenticate the separate exact-once pushed compiler application",
    )
    require(
        type(canonical_source) is bytes and digest(canonical_source) == MATCHER_SHA
        and len(canonical_source) == CANONICAL_RUST_OWNERS[3][3]
        and type(materialized) is bytes and digest(materialized) == COMPILER_VARIANT_SHA
        and len(materialized) == COMPILER_VARIANT_BYTES
        and (wall is None or wall.installed),
        "require distinct complete canonical and reviewed materialized Rust sources",
    )
    module = types.ModuleType("_rebar_v27_frozen_compiler_fastpath_transformer")
    module.__file__ = ROOT + "/" + COMPILER_FASTPATH_OWNERS[0][1]
    exec(compile(source, module.__file__, "exec", dont_inherit=True),
         module.__dict__)
    require(
        module.SCHEMA
        == "rebar-owned-rust-compiler-allocation-fastpath-v1-source-freeze"
        and module.SOURCE == COMPILER_FASTPATH_OWNERS[0][1]
        and module.PROTOCOL == COMPILER_FASTPATH_OWNERS[1][1]
        and module.CONTRACT == COMPILER_FASTPATH_OWNERS[2][1]
        and module.VARIANT == COMPILER_VARIANT_OWNER[1]
        and module.ORIGINAL_SHA256 == MATCHER_SHA
        and module.DERIVED_SHA256 == COMPILER_VARIANT_SHA
        and len(module.REPLACEMENTS) == 7
        and callable(module.derive_source)
        and module.derive_source(canonical_source) == materialized
        and callable(module.synthetic_semantics)
        and module.synthetic_semantics() == semantics,
        "reexecute only the pinned pure first-party parser optimization",
    )
    no_matching_imports()
    return module


def verify_frozen_v25_original_campaign(campaign: object) -> None:
    require(
        type(campaign) is dict
        and campaign.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v25-"
           "recoverable-source-freeze"
        and campaign.get("version") == 25
        and campaign.get("family") == FAMILY
        and campaign.get("source", {}).get("sha256")
        == CAMPAIGN_V25_OWNERS[0][2]
        and campaign.get("protocol", {}).get("sha256")
        == CAMPAIGN_V25_OWNERS[1][2]
        and campaign.get("original_correctness_boundary", {}).get(
            "case_execution_denominator",
        ) == 31237
        and campaign.get("original_correctness_boundary", {}).get(
            "suite_count",
        ) == 13
        and campaign.get("original_correctness_boundary", {}).get(
            "named_private_waiver_count",
        ) == 13
        and campaign.get("actual_v25_native_build", {}).get(
            "publication_receipt", {},
        ).get("sha256") == V25_BUILD_RECEIPT_SHA
        and campaign.get("actual_v25_native_build", {}).get(
            "root_provenance_receipt", {},
        ).get("sha256") == V25_ROOT_RECEIPT_SHA
        and campaign.get("actual_v25_native_build", {}).get(
            "actual_compiler_process_count",
        ) == 28
        and campaign.get("immutable_actual_v24_candidate_failure", {}).get(
            "receipt_sha256",
        ) == PREVIOUS_FAILURE_RECEIPT_SHA
        and campaign.get("immutable_actual_v24_candidate_failure", {}).get(
            "semantic_mismatch_count",
        ) == 1352
        and campaign.get("independent_runtime_non_delegation_v4_audit", {}).get(
            "status",
        ) == "FAIL"
        and campaign.get("independent_runtime_non_delegation_v4_audit", {}).get(
            "finding_count",
        ) == 1,
        "preserve the exact frozen V25 original campaign, denominator, and audit",
    )


def verify_actual_v25_original_failure(campaign: object, failure: object) -> None:
    verify_frozen_v25_original_campaign(campaign)
    require(
        type(failure) is dict and len(failure) == 96
        and failure.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v25-"
           "durable-publication-receipt"
        and failure.get("status") == "PASS"
        and failure.get("publication_status") == "PASS"
        and failure.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
        and failure.get("candidate_status") == "FAIL"
        and failure.get("semantic_mismatch_count") == 1352
        and failure.get("verified_passing_case_count") == 15877
        and failure.get("case_execution_denominator") == 31237
        and failure.get("suite_count") == 13
        and failure.get("completed_suite_count") == 13
        and failure.get("actual_candidate_workers") == 13
        and failure.get("distinct_worker_process_id_count") == 13
        and failure.get("infrastructure_failure_count") == 0
        and failure.get("named_private_waiver_count") == 13
        and failure.get("campaign_source_sha256") == CAMPAIGN_V25_OWNERS[0][2]
        and failure.get("campaign_protocol_sha256") == CAMPAIGN_V25_OWNERS[1][2]
        and failure.get("campaign_contract_sha256") == CAMPAIGN_V25_OWNERS[2][2]
        and failure.get("actual_v25_build_source_sha256") == BUILD_V25_OWNERS[0][2]
        and failure.get("actual_v25_build_protocol_sha256") == BUILD_V25_OWNERS[1][2]
        and failure.get("actual_v25_build_contract_sha256") == BUILD_V25_OWNERS[2][2]
        and failure.get("actual_v25_build_receipt_sha256") == V25_BUILD_RECEIPT_SHA
        and failure.get("actual_v25_compiler_process_count") == 28
        and failure.get("native_engine_sha256") == PREVIOUS_ENGINE_SHA
        and failure.get("combined_bridge_source_sha256") == VARIANT_SHA
        and failure.get("combined_bridge_source_bytes") == VARIANT_BYTES
        and failure.get("corrected_public_adapter_sha256") == ADAPTER_SHA
        and failure.get("corrected_public_adapter_bytes") == ADAPTER_BYTES
        and failure.get("all_four_original_targets_restored") is True
        and failure.get("all_original_observation_vectors_complete") is True
        and failure.get("all_original_suite_rows_validated_before_publication")
        is True
        and failure.get("worker_failure_capture_complete") is True
        and failure.get("all_worker_failure_capture_count") == 0
        and failure.get("candidate_qualified") is False
        and failure.get("holdout") == "NOT OPENED",
        "preserve the complete actual V25 FAIL-1352 and all real 13 workers",
    )
    assert isinstance(failure, dict)
    archive = failure.get("archive")
    workers = failure.get("actual_worker_process_ids")
    suites = failure.get("suite_integrity")
    require(
        type(archive) is dict
        and archive.get("sha256") == V25_FAILURE_ARCHIVE_SHA
        and archive.get("size_bytes") == 3771743
        and archive.get("inode") == 524845
        and archive.get("exclusive_creation") is True
        and type(workers) is list and len(workers) == 13
        and len(set(workers)) == 13
        and type(suites) is list and len(suites) == 13
        and all(type(row) is dict and row.get("fully_observed") is True
                for row in suites)
        and sum(row.get("case_execution_denominator", -1) for row in suites)
        == 31237
        and sum(row.get("mismatch_count", -1) for row in suites) == 1352
        and sum(row.get("verified_passing_case_count", -1) for row in suites)
        == 15877
        and {row["suite"]: row["mismatch_count"]
             for row in suites if row.get("mismatch_count", 0)}
        == {"substitution_v2": 240, "shape_v2": 1112},
        "preserve all V25 suite rows and archive metadata without opening it",
    )


def reject_source_only_activation(choice: object) -> None:
    require(type(choice) is dict and choice.get("mode") in ACTUAL_MODES,
            "reject unrelated native-build activation")
    raise BuildFreezeError(
        "an installed, irreversible source-only wall cannot start a build",
    )


def load_context(
    wall: FirstPartySourceWall, pins: dict, rendering: bool,
) -> tuple[dict, dict]:
    source_row = dynamic_owner(wall, "source", SOURCE, pins["--source-sha256"])
    protocol_row = dynamic_owner(
        wall, "protocol", PROTOCOL, pins["--protocol-sha256"],
    )
    secure_owner(wall, source_row)
    secure_owner(wall, protocol_row)
    contract_row = None
    if not rendering:
        contract_row = dynamic_owner(
            wall, "contract", CONTRACT, pins["--contract-sha256"],
        )

    parent = bootstrap_parent(wall)
    parent_pins = {
        "--source-sha256": CAMPAIGN_V23_OWNERS[0][2],
        "--protocol-sha256": CAMPAIGN_V23_OWNERS[1][2],
        "--contract-sha256": CAMPAIGN_V23_OWNERS[2][2],
    }
    parent_frozen, parent_state = parent.load_context(wall, parent_pins, False)
    capture = parent_state["capture"]
    semantic = parent_state["semantic"]
    wall.error_type = type(
        "V23FirstPartySourceWallError",
        (BuildFreezeError, parent.FreezeError, capture.FreezeError),
        {},
    )
    require(
        parent_frozen.get("schema") == parent.SCHEMA
        and parent_frozen.get("version") == 23
        and parent_frozen.get("immutable_previous_v22_campaign", {}).get(
            "complete_current_contract_field_count",
        ) == 435
        and parent_frozen.get("immutable_previous_v22_campaign", {}).get(
            "complete_inherited_v21_contract_field_count",
        ) == 402
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "complete_receipt_field_count",
        ) == 96
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "candidate_status",
        ) == "FAIL"
        and parent_frozen.get("immutable_actual_v22_failure", {}).get(
            "actual_failing_worker_transient_native_child_creation",
        ) == NOT_MEASURED,
        "preserve the full factually correct V23 frozen failure boundary",
    )

    previous_build_raw = {
        row[0]: secure_owner(wall, row) for row in BUILD_V23_OWNERS
    }
    previous_build = decode_public(
        capture, semantic, previous_build_raw["materialized_v23_build_contract"],
        "complete materialized and pushed V23 native source-build freeze",
    )
    previous_plan = previous_build.get("frozen_offline_dual_phase_build")
    previous_materialized = previous_build.get("materialized_first_party_variant")
    previous_campaign = previous_build.get(
        "immutable_complete_v23_correctness_campaign",
    )
    previous_failure = previous_build.get("immutable_genuine_v22_failure")
    require(
        previous_build.get("schema")
        == "rebar-phase2-owned-rust-capture-shape-semantics-v2-"
           "source-build-v23-source-freeze"
        and previous_build.get("version") == 23
        and previous_build.get("family") == FAMILY
        and type(previous_plan) is dict
        and previous_plan.get("status") == "NOT RUN"
        and previous_plan.get("required_actual_distinct_compiler_process_count")
        == 28
        and previous_plan.get("private_variant_sha256") == INPUT_VARIANT_SHA
        and previous_plan.get("private_variant_bytes") == INPUT_VARIANT_BYTES
        and previous_plan.get("private_corrected_adapter_sha256") == ADAPTER_SHA
        and previous_plan.get("private_corrected_adapter_bytes") == ADAPTER_BYTES
        and type(previous_materialized) is dict
        and previous_materialized.get("complete_source_sha256")
        == INPUT_VARIANT_SHA
        and previous_materialized.get("complete_source_bytes")
        == INPUT_VARIANT_BYTES
        and type(previous_campaign) is dict
        and previous_campaign.get("complete_frozen_source_contract")
        == parent_frozen
        and type(previous_failure) is dict
        and previous_failure.get("complete_receipt")
        == parent_state["actual"]
        and previous_failure.get("complete_receipt_field_count") == 96
        and previous_failure.get("verified_passing_case_count") == 14725
        and previous_failure.get("fully_observed_mismatch_lower_bound") == 2018
        and previous_failure.get("global_semantic_mismatch_count")
        == NOT_MEASURED
        and previous_failure.get("transient_physical_native_child_creation")
        == NOT_MEASURED
        and previous_build.get("source", {}).get("sha256")
        == BUILD_V23_OWNERS[0][2]
        and previous_build.get("protocol", {}).get("sha256")
        == BUILD_V23_OWNERS[1][2],
        "preserve the entire pushed V23 source, plan, campaign and real failure",
    )

    additional: dict[str, bytes] = {}
    for row in (
        NATIVE_SOURCE_OWNERS + ADAPTER_REPAIR_OWNERS
        + CANONICAL_RUST_OWNERS + BUILD_V24_OWNERS + CAMPAIGN_V24_OWNERS
        + RUNTIME_GUARD_V4_OWNERS + CAPTURE_CLAMP_OWNERS
        + (A0_OWNER, INPUT_VARIANT_OWNER, VARIANT_OWNER,
           V24_BUILD_RECEIPT_OWNER, V24_ROOT_RECEIPT_OWNER,
           V24_FAILURE_RECEIPT_OWNER)
        + V27_ADDITIONAL_OWNERS
    ):
        additional[row[0]] = secure_owner(wall, row)
    native_v9 = decode_public(
        capture, semantic, additional["native_v9_contract"],
        "complete first-party V9 reproducibility kernel",
    )
    native_v16 = decode_public(
        capture, semantic, additional["native_v16_contract"],
        "complete first-party V16 toolchain and adapter policy",
    )
    adapter = decode_public(
        capture, semantic, additional["adapter_v3_contract"],
        "complete first-party public adapter repair",
    )
    actual_v24_build = decode_public(
        capture, semantic, additional[BUILD_V24_OWNERS[2][0]],
        "complete independently pinned actual V24 source-build freeze",
    )
    actual_v24_campaign = decode_public(
        capture, semantic, additional[CAMPAIGN_V24_OWNERS[2][0]],
        "complete independently pinned actual V24 original campaign freeze",
    )
    actual_v24_guard = decode_public(
        capture, semantic, additional[RUNTIME_GUARD_V4_OWNERS[2][0]],
        "complete independently pinned strict runtime guard V4",
    )
    actual_v24_build_receipt = decode_public(
        capture, semantic, additional[V24_BUILD_RECEIPT_OWNER[0]],
        "complete genuinely successful actual V24 build publication",
    )
    actual_v24_root_receipt = decode_public(
        capture, semantic, additional[V24_ROOT_RECEIPT_OWNER[0]],
        "complete genuinely successful actual V24 private-root provenance",
    )
    actual_v24_failure = decode_public(
        capture, semantic, additional[V24_FAILURE_RECEIPT_OWNER[0]],
        "complete independently observed actual V24 original candidate failure",
    )
    clamp_contract = decode_public(
        capture, semantic, additional[CAPTURE_CLAMP_OWNERS[2][0]],
        "complete independently frozen pure first-party capture clamp",
    )
    v25_contract = decode_public(
        capture, semantic, additional[BUILD_V25_OWNERS[2][0]],
        "complete independently successful V25 frozen build",
    )
    v25_campaign = decode_public(
        capture, semantic, additional[CAMPAIGN_V25_OWNERS[2][0]],
        "complete independently frozen V25 original correctness campaign",
    )
    v25_publication = decode_public(
        capture, semantic, additional[V25_BUILD_RECEIPT_OWNER[0]],
        "complete genuinely successful V25 native publication",
    )
    v25_failure = decode_public(
        capture, semantic, additional[V25_FAILURE_RECEIPT_OWNER[0]],
        "complete latest independently observed V25 original FAIL-1352",
    )
    v25_root = decode_public(
        capture, semantic, additional[V25_ROOT_RECEIPT_OWNER[0]],
        "complete genuinely successful V25 root provenance",
    )
    compiler_contract = decode_public(
        capture, semantic, additional[COMPILER_FASTPATH_OWNERS[2][0]],
        "complete independently frozen first-party compiler fast path",
    )
    compiler_application = decode_public(
        capture, semantic, additional[COMPILER_APPLICATION_OWNER[0]],
        "complete exclusive materialized compiler fast-path application",
    )
    verify_previous_actual_v25(v25_contract, v25_publication, v25_root)
    verify_actual_v25_original_failure(v25_campaign, v25_failure)
    compiler_transformer = verify_compiler_allocation_freeze(
        wall, additional[COMPILER_FASTPATH_OWNERS[0][0]],
        compiler_contract, compiler_application,
        additional[CANONICAL_RUST_OWNERS[3][0]],
        additional[COMPILER_VARIANT_OWNER[0]],
    )
    verify_previous_actual_v24(
        actual_v24_build, actual_v24_campaign, actual_v24_guard,
        actual_v24_build_receipt, actual_v24_root_receipt,
        actual_v24_failure, additional[INPUT_VARIANT_OWNER[0]],
    )
    clamp_transformer = verify_capture_clamp_freeze(
        wall, additional[CAPTURE_CLAMP_OWNERS[0][0]], clamp_contract,
        actual_v24_failure, additional[INPUT_VARIANT_OWNER[0]],
        additional[VARIANT_OWNER[0]],
    )
    verify_native_documents(native_v9, native_v16, adapter)
    proof = verify_variant(
        semantic,
        additional[A0_OWNER[0]],
        additional[VARIANT_OWNER[0]],
        additional["canonical_matching_engine"],
    )
    plan = native_build_plan()
    validate_native_build_plan(plan)
    capture.validate_originals(parent_state["actual"]["restored_original_targets"])
    require(not wall.live,
            "close all tracked canonical and first-party source descriptors")
    no_matching_imports()

    frozen = build_contract(
        source_row, protocol_row, parent_frozen, parent_state,
        native_v9, native_v16, adapter, proof, plan, previous_build,
        actual_v24_build, actual_v24_campaign, actual_v24_guard,
        actual_v24_build_receipt, actual_v24_root_receipt,
        actual_v24_failure, clamp_contract,
    )
    frozen.update({
        "immutable_complete_v25_actual_source_build": {
            "owners": [owner_document(row) for row in BUILD_V25_OWNERS],
            "complete_frozen_source_contract": v25_contract,
            "complete_contract_sha256": BUILD_V25_OWNERS[2][2],
            "actual_publication_owner": owner_document(V25_BUILD_RECEIPT_OWNER),
            "complete_actual_publication": v25_publication,
            "actual_root_owner": owner_document(V25_ROOT_RECEIPT_OWNER),
            "complete_actual_root": v25_root,
            "actual_compiler_process_count": 28,
            "actual_source_phase_count": 2,
            "actual_original_runtime_target_count": 4,
            "actual_engine_sha256": PREVIOUS_ENGINE_SHA,
            "actual_bridge_sha256":
                "adcb000c036e075a52f43926750648a4610e853e628d5433b1fbcc17e99a89e4",
            "archive_opened": False,
            "private_root_opened": False,
        },
        "immutable_complete_v25_original_correctness_campaign": {
            "owners": [owner_document(row) for row in CAMPAIGN_V25_OWNERS],
            "complete_frozen_source_contract": v25_campaign,
            "complete_contract_sha256": CAMPAIGN_V25_OWNERS[2][2],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_counted_in_original_denominator": False,
            "historical_v24_candidate_status": "FAIL",
            "historical_v24_semantic_mismatch_count": 1352,
            "v4_runtime_non_delegation_audit_status": "FAIL",
            "actual_failure_owner": owner_document(V25_FAILURE_RECEIPT_OWNER),
            "complete_actual_failure_receipt": v25_failure,
            "actual_failure_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
            "complete_actual_failure_field_count": 96,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "actual_candidate_worker_count": 13,
            "completed_suite_count": 13,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240, "shape_v2": 1112,
            },
            "infrastructure_failure_count": 0,
            "complete_failure_archive_sha256_metadata_only":
                V25_FAILURE_ARCHIVE_SHA,
            "complete_failure_archive_bytes_metadata_only": 3771743,
            "complete_failure_archive_opened": False,
        },
        "immutable_first_party_compiler_allocation_transformer": {
            "owners": [owner_document(row) for row in COMPILER_FASTPATH_OWNERS],
            "complete_frozen_source_contract": compiler_contract,
            "complete_contract_sha256": COMPILER_FASTPATH_OWNERS[2][2],
            "application_owner": owner_document(COMPILER_APPLICATION_OWNER),
            "complete_exclusive_application": compiler_application,
            "synthetic_semantic_case_count": 960,
            "synthetic_scanner_flag_case_count": 42,
            "synthetic_source_lifetime_control_count": 40,
            "exact_reversible_replacement_count": 7,
            "semantic_optimization_count": 2,
            "transformer_apply_invoked": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
        },
        "materialized_first_party_compiler_source": {
            "owner": owner_document(COMPILER_VARIANT_OWNER),
            "canonical_owner": owner_document(CANONICAL_RUST_OWNERS[3]),
            "canonical_source_sha256": MATCHER_SHA,
            "canonical_source_bytes": CANONICAL_RUST_OWNERS[3][3],
            "materialized_source_sha256": COMPILER_VARIANT_SHA,
            "materialized_source_bytes": COMPILER_VARIANT_BYTES,
            "source_delta_bytes": 54,
            "normal_and_scanner_heap_clone_removed": True,
            "alternation_allocation_lazy": True,
            "canonical_search_owner": owner_document(CANONICAL_RUST_OWNERS[5]),
            "anchor_search_variant_used": False,
            "bridge_owner": owner_document(VARIANT_OWNER),
            "bridge_source_changed_by_compiler_variant": False,
            "actual_build": "NOT RUN",
            "native_engine_sha256": NOT_MEASURED,
            "candidate_correctness": NOT_MEASURED,
            "performance": NOT_MEASURED,
        },
        "preserved_complete_public_practice_raw": {
            "owners": [owner_document(row) for row in PUBLIC_PRACTICE_OWNERS],
            "public_case_count": 416,
            "paired_row_count": 1664,
            "stdlib_total_ns": 96434251,
            "original_rust_total_ns": 161853767,
            "new_compiler_variant_executed": False,
            "new_compiler_variant_speed": NOT_MEASURED,
            "final_holdout": False,
        },
    })
    frozen["source_wall"]["materialized_new_variant_owner_count"] = 2
    frozen["source_wall"]["immutable_compiler_fastpath_owner_count"] = (
        len(COMPILER_FASTPATH_OWNERS)
    )
    frozen["source_wall"]["immutable_successful_v25_owner_count"] = (
        len(BUILD_V25_OWNERS) + 2
    )
    state = {
        "parent": parent, "parent_frozen": parent_frozen,
        "parent_state": parent_state, "capture": capture,
        "semantic": semantic, "additional": additional,
        "native_v9": native_v9, "native_v16": native_v16,
        "adapter": adapter, "variant_proof": proof, "native_plan": plan,
        "previous_build": previous_build,
        "previous_build_raw": previous_build_raw,
        "actual_v24_build": actual_v24_build,
        "actual_v24_campaign": actual_v24_campaign,
        "actual_v24_guard": actual_v24_guard,
        "actual_v24_build_receipt": actual_v24_build_receipt,
        "actual_v24_root_receipt": actual_v24_root_receipt,
        "actual_v24_failure": actual_v24_failure,
        "clamp_contract": clamp_contract,
        "clamp_transformer": clamp_transformer,
        "compiler_transformer": compiler_transformer,
        "compiler_contract": compiler_contract,
        "compiler_application": compiler_application,
        "v25_contract": v25_contract,
        "v25_campaign": v25_campaign,
        "v25_failure": v25_failure,
        "v25_publication": v25_publication,
        "v25_root": v25_root,
        "source_row": source_row, "protocol_row": protocol_row,
        "contract": frozen,
    }
    if not rendering:
        assert isinstance(contract_row, tuple)
        raw = secure_owner(wall, contract_row)
        require(raw == capture.canonical_document(semantic, frozen)
                and semantic.StrictJSON(raw).decode() == frozen,
                "reject any removed or changed complete V23 build obligation")
        state["contract_row"] = contract_row
    require(not wall.live, "close every tracked first-party source descriptor")
    no_matching_imports()
    return frozen, state


def build_contract(
    source_row: tuple, protocol_row: tuple, parent: dict,
    parent_state: dict, native_v9: dict, native_v16: dict,
    adapter: dict, proof: dict, plan: dict, previous_build: dict,
    actual_v24_build: dict, actual_v24_campaign: dict,
    actual_v24_guard: dict, actual_v24_build_receipt: dict,
    actual_v24_root_receipt: dict, actual_v24_failure: dict,
    clamp_contract: dict,
) -> dict:
    actual = parent_state["actual"]
    previous = parent["immutable_actual_v22_failure"]
    return {
        "schema": SCHEMA + "-source-freeze",
        "version": VERSION,
        "status": (
            "COMPLETE FIRST-PARTY CAPTURE-CLAMP SOURCE MATERIALIZED; "
            "NATIVE BUILD NOT RUN; CORRECTNESS NOT MEASURED"
        ),
        "phase": "PHASE 2: FIRST-PARTY RUST CANDIDATE CORRECTNESS",
        "family": FAMILY,
        "goal_sha256": GOAL_SHA,
        "source": owner_document(source_row),
        "protocol": owner_document(protocol_row),
        "materialized_first_party_variant": {
            "owner": owner_document(VARIANT_OWNER),
            "source_materialized": True,
            "complete_source_sha256": VARIANT_SHA,
            "complete_source_bytes": VARIANT_BYTES,
            "base_owner": owner_document(A0_OWNER),
            "immutable_actual_v24_input_owner": owner_document(
                INPUT_VARIANT_OWNER,
            ),
            "derivation": proof,
            "native_build": "NOT RUN",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
            "candidate_imports": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "candidate_qualified": False,
        },
        "authenticated_first_party_source_owners": [
            owner_document(row) for row in CANONICAL_RUST_OWNERS
        ],
        "canonical_original_source_identity": {
            "owner_count": 9,
            "bridge_source": owner_document(CANONICAL_RUST_OWNERS[2]),
            "public_adapter": owner_document(CANONICAL_RUST_OWNERS[8]),
            "matching_engine": owner_document(CANONICAL_RUST_OWNERS[3]),
            "canonical_sources_modified": False,
            "installed_native_owners_opened": False,
            "installed_engine_sha256": (
                "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4"
            ),
            "installed_bridge_sha256": (
                "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15"
            ),
            "native_identity_scope": (
                "EXACT IMMUTABLE PUBLISHED V22 RECEIPT; "
                "NO NATIVE FILE OPEN OR METADATA PROBE"
            ),
        },
        "immutable_complete_v23_materialized_source_build": {
            "owners": [owner_document(row) for row in BUILD_V23_OWNERS],
            "complete_contract_sha256": BUILD_V23_OWNERS[2][2],
            "complete_contract_bytes": BUILD_V23_OWNERS[2][3],
            "complete_contract_authenticated": True,
            "complete_contract_field_count": len(previous_build),
            "source_build_invoked": False,
            "native_build": "NOT RUN",
            "all_source_only_effects_preserved": True,
        },
        "immutable_complete_v23_correctness_campaign": {
            "owners": [owner_document(row) for row in CAMPAIGN_V23_OWNERS],
            "complete_contract_sha256": CAMPAIGN_V23_OWNERS[2][2],
            "complete_contract_bytes": CAMPAIGN_V23_OWNERS[2][3],
            "complete_contract_authenticated": True,
            "complete_contract_field_count": len(parent),
            "corrected_candidate_run": "NOT RUN",
            "original_case_count": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_differential_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
        },
        "immutable_complete_v24_actual_source_build": {
            "owners": [owner_document(row) for row in BUILD_V24_OWNERS],
            "complete_contract_sha256": BUILD_V24_OWNERS[2][2],
            "complete_contract_bytes": BUILD_V24_OWNERS[2][3],
            "complete_contract_authenticated": True,
            "source_contract_status": actual_v24_build["status"],
            "actual_build_receipt_owner": owner_document(
                V24_BUILD_RECEIPT_OWNER,
            ),
            "complete_actual_build_receipt": actual_v24_build_receipt,
            "actual_root_receipt_owner": owner_document(
                V24_ROOT_RECEIPT_OWNER,
            ),
            "complete_actual_root_receipt": actual_v24_root_receipt,
            "actual_build_status": "PASS",
            "actual_compiler_process_count": 28,
            "actual_source_phase_count": 2,
            "actual_original_runtime_target_count": 4,
            "actual_original_runtime_targets_restored": True,
            "actual_v24_private_root_opened": False,
            "actual_v24_archive_opened": False,
        },
        "immutable_complete_v24_correctness_campaign": {
            "owners": [owner_document(row) for row in CAMPAIGN_V24_OWNERS],
            "complete_frozen_source_contract": actual_v24_campaign,
            "complete_contract_sha256": CAMPAIGN_V24_OWNERS[2][2],
            "original_case_count": 31237,
            "original_suite_count": 13,
            "named_private_waiver_count": 13,
            "supplemental_differential_case_count": 8244,
            "supplemental_counted_in_original_denominator": False,
            "corrected_reference_case_count": 6912,
            "corrected_reference_counted_in_original_denominator": False,
        },
        "immutable_complete_v24_actual_candidate_failure": {
            "owner": owner_document(V24_FAILURE_RECEIPT_OWNER),
            "complete_receipt": actual_v24_failure,
            "complete_receipt_field_count": len(actual_v24_failure),
            "receipt_sha256": PREVIOUS_FAILURE_RECEIPT_SHA,
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "semantic_mismatch_count": 1352,
            "verified_passing_case_count": 15877,
            "original_case_denominator": 31237,
            "actual_worker_count": 13,
            "completed_suite_count": 13,
            "fully_observed_suite_mismatch_counts": {
                "substitution_v2": 240,
                "shape_v2": 1112,
            },
            "previous_build_receipt_sha256": PREVIOUS_BUILD_RECEIPT_SHA,
            "previous_root_receipt_sha256": PREVIOUS_ROOT_RECEIPT_SHA,
            "measured_values_taken_from_complete_receipt": True,
        },
        "immutable_operational_runtime_guard_v4": {
            "owners": [owner_document(row) for row in RUNTIME_GUARD_V4_OWNERS],
            "complete_frozen_source_contract": actual_v24_guard,
            "complete_contract_sha256": RUNTIME_GUARD_V4_OWNERS[2][2],
            "version": 4,
            "candidate_execution": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "immutable_first_party_capture_clamp_transformer": {
            "owners": [owner_document(row) for row in CAPTURE_CLAMP_OWNERS],
            "complete_frozen_source_contract": clamp_contract,
            "complete_contract_sha256": CAPTURE_CLAMP_OWNERS[2][2],
            "complete_contract_bytes": CAPTURE_CLAMP_OWNERS[2][3],
            "complete_pure_derivation_reexecuted": True,
            "capture_function_changed_count": 1,
            "source_delta_bytes": -55,
            "synthetic_bounds_case_count": 4800,
            "synthetic_alias_case_count": 50,
            "sealed_proposal_sha256_metadata_only":
                EXPANDED_HOLDOUT_PROPOSAL_SHA,
            "sealed_proposal_case_count":
                EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT,
            "sealed_proposal_file_opened": False,
            "transformer_apply_invoked": False,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
        },
        "immutable_genuine_v22_failure": {
            "complete_receipt": actual,
            "complete_receipt_field_count": 96,
            "receipt_sha256": PUBLIC_OWNERS[17][2],
            "publication_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": "FAIL",
            "original_case_denominator": 31237,
            "actual_worker_count": 13,
            "completed_suite_count": 12,
            "verified_passing_case_count": 14725,
            "fully_observed_mismatch_lower_bound": 2018,
            "fully_observed_suite_mismatch_counts": {
                "managed_v1": 42,
                "substitution_v2": 352,
                "shape_v2": 1624,
            },
            "global_semantic_mismatch_count": NOT_MEASURED,
            "failing_worker_pid": 188,
            "failing_worker_candidate_imports": 1,
            "failing_worker_native_library_loads": 2,
            "recorded_successfully_returned_child_interpreters": 0,
            "recorded_installed_child_guards": 0,
            "recorded_case_interpreter_exec_calls": 0,
            "transient_physical_native_child_creation": NOT_MEASURED,
            "remaining_interpreter_warning_count": 1,
            "destructor_warning_count": 16,
            "warning_scope": "ONLY ACTUAL SUBINTERPRETER WORKER PID 188",
            "old_f9_bridge_sha256": F9_SHA,
            "old_f9_bridge_bytes": 179147,
            "old_failed_f9_is_new_variant": False,
            "measured_values_taken_from_complete_receipt": True,
            "failing_worker_counter_scope": previous[
                "actual_failing_worker_counter_scope"
            ],
        },
        "immutable_complete_native_v9_kernel": {
            "owners": [owner_document(row) for row in NATIVE_SOURCE_OWNERS[:3]],
            "complete_frozen_source_contract": native_v9,
            "kernel_executed": False,
        },
        "immutable_complete_native_v16_toolchain": {
            "owners": [owner_document(row) for row in NATIVE_SOURCE_OWNERS[3:]],
            "complete_frozen_source_contract": native_v16,
            "controller_executed": False,
            "toolchain_binaries_opened": False,
        },
        "immutable_first_party_private_adapter_repair": {
            "owners": [owner_document(row) for row in ADAPTER_REPAIR_OWNERS],
            "complete_frozen_source_contract": adapter,
            "corrected_private_adapter_sha256": ADAPTER_SHA,
            "corrected_private_adapter_bytes": ADAPTER_BYTES,
            "canonical_original_adapter_modified": False,
            "adapter_repair_controller_executed": False,
            "adapter_oracle_stdlib_re_imported": False,
        },
        "frozen_offline_dual_phase_build": plan,
        "source_wall": {
            "policy": (
                "DENY DEFAULT; EXACT PUBLIC EVIDENCE AND PINNED "
                "FIRST-PARTY SOURCE OWNERS ONLY"
            ),
            "installed_before_first_predecessor_byte": True,
            "static_source_owner_count": len(STATIC_OWNERS),
            "new_controller_owner_count": 3,
            "actual_canonical_rust_source_owner_count": 9,
            "materialized_new_variant_owner_count": 1,
            "immutable_capture_clamp_transformer_owner_count":
                len(CAPTURE_CLAMP_OWNERS),
            "authentic_a0_base_owner_count": 1,
            "any_other_candidate_paths_allowed": 0,
            "native_library_paths_allowed": 0,
            "private_root_paths_allowed": 0,
            "archive_paths_allowed": 0,
            "phase_three_proposal_paths_allowed": 0,
            "foreign_descriptor_reads_allowed": 0,
            "direct_io_allowed": False,
            "direct_metadata_allowed": False,
            "timing_allowed": False,
            "entropy_allowed": False,
        },
        "source_only_effects": {
            "candidate_imports": 0,
            "candidate_workers_started": 0,
            "reference_workers_started": 0,
            "compiler_processes_started": 0,
            "native_libraries_loaded": 0,
            "native_binary_files_read": 0,
            "native_binary_metadata_probes": 0,
            "private_roots_created": 0,
            "private_roots_opened": 0,
            "compressed_archives_opened": 0,
            "compressed_archives_inflated": 0,
            "hidden_cases_read": 0,
            "holdout_cases_opened": 0,
            "phase_three_files_read": 0,
            "benchmark_files_read": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "network_requests": 0,
            "subinterpreters_created": 0,
            "threads_started": 0,
            "canonical_source_mutations": 0,
            "adapter_repair_controllers_executed": 0,
            "native_build_controllers_executed": 0,
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "expanded_holdout_proposal_case_count":
                EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT,
            "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
            "holdout": "NOT OPENED",
            "native_engine_sha256": NOT_MEASURED,
            "native_bridge_sha256": NOT_MEASURED,
            "native_build_receipt_sha256": NOT_MEASURED,
            "native_root_receipt_sha256": NOT_MEASURED,
            "performance": NOT_MEASURED,
            "memory": NOT_MEASURED,
            "confidence_intervals": NOT_MEASURED,
            "undefined_behavior": NOT_MEASURED,
            "qualified_candidate_count": 0,
            "winner_selected": False,
        },
    }


def reject(action: object, label: str, *types_: type) -> str:
    require(callable(action), "require one executed bounded hostile control")
    try:
        action()
    except (
        BuildFreezeError, OSError, ValueError, TypeError, KeyError,
        IndexError, UnicodeError, OverflowError, *types_,
    ):
        return label
    raise BuildFreezeError("accepted hostile first-party source control: " + label)


def validate_exact_document(
    capture: types.ModuleType, semantic: types.ModuleType,
    proposed: object, authentic: dict, label: str,
) -> None:
    require(type(proposed) is dict and set(proposed) == set(authentic),
            "reject missing or added complete immutable evidence: " + label)
    assert isinstance(proposed, dict)
    require(
        capture.canonical_document(semantic, proposed)
        == capture.canonical_document(semantic, authentic),
        "reject a changed complete immutable evidence value: " + label,
    )


def self_test(wall: FirstPartySourceWall, frozen: dict, state: dict) -> list[str]:
    parent = state["parent"]
    capture = state["capture"]
    semantic = state["semantic"]
    actual = state["parent_state"]["actual"]
    campaign = state["parent_state"]["campaign"]
    additional = state["additional"]
    baseline = additional[A0_OWNER[0]]
    actual_v24_input = additional[INPUT_VARIANT_OWNER[0]]
    materialized = additional[VARIANT_OWNER[0]]
    matcher = additional["canonical_matching_engine"]
    kinds = (
        parent.FreezeError, capture.FreezeError, semantic.FreezeError,
        state["compiler_transformer"].FreezeError,
    )
    checks: list[str] = []

    for key in sorted(campaign):
        missing = dict(campaign)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: parent.validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-missing-complete-v22-obligation-" + key, *kinds,
        ))
        altered = dict(campaign)
        altered[key] = {"__v23_source_build_forged_obligation__": key}
        checks.append(reject(
            lambda item=altered: parent.validate_exact_campaign(
                capture, semantic, item, campaign,
            ), "reject-changed-complete-v22-obligation-" + key, *kinds,
        ))

    for key in sorted(actual):
        missing = dict(actual)
        missing.pop(key)
        checks.append(reject(
            lambda item=missing: parent.validate_exact_actual(
                capture, semantic, item, actual,
            ), "reject-missing-complete-v22-failure-receipt-" + key, *kinds,
        ))
        altered = dict(actual)
        altered[key] = {"__v23_source_build_forged_actual_receipt__": key}
        checks.append(reject(
            lambda item=altered: parent.validate_exact_actual(
                capture, semantic, item, actual,
            ), "reject-changed-complete-v22-failure-receipt-" + key, *kinds,
        ))

    for section, authentic in (
        ("complete-v23-campaign", state["parent_frozen"]),
        ("complete-v23-materialized-source-build", state["previous_build"]),
        ("complete-v24-actual-source-build", state["actual_v24_build"]),
        ("complete-v24-correctness-campaign", state["actual_v24_campaign"]),
        ("complete-v24-strict-runtime-guard", state["actual_v24_guard"]),
        ("complete-v24-successful-build-receipt",
         state["actual_v24_build_receipt"]),
        ("complete-v24-successful-root-receipt",
         state["actual_v24_root_receipt"]),
        ("complete-v24-failed-candidate-receipt",
         state["actual_v24_failure"]),
        ("complete-frozen-first-party-capture-clamp",
         state["clamp_contract"]),
        ("complete-successful-v25-build-freeze", state["v25_contract"]),
        ("complete-v25-original-campaign-freeze", state["v25_campaign"]),
        ("complete-v25-original-failure-receipt", state["v25_failure"]),
        ("complete-successful-v25-publication", state["v25_publication"]),
        ("complete-successful-v25-root-provenance", state["v25_root"]),
        ("complete-compiler-fastpath-freeze", state["compiler_contract"]),
        ("complete-compiler-fastpath-application", state["compiler_application"]),
        ("complete-v9-compiler-kernel", state["native_v9"]),
        ("complete-v16-native-build", state["native_v16"]),
        ("complete-v3-adapter-repair", state["adapter"]),
    ):
        for key in sorted(authentic):
            missing = dict(authentic)
            missing.pop(key)
            checks.append(reject(
                lambda item=missing, exact=authentic, title=section:
                    validate_exact_document(
                        capture, semantic, item, exact, title,
                    ),
                "reject-missing-" + section + "-" + key, *kinds,
            ))

    compiler_original = additional[CANONICAL_RUST_OWNERS[3][0]]
    compiler_materialized = additional[COMPILER_VARIANT_OWNER[0]]
    for counterfeit, label in (
        (compiler_original + b"\\n", "changed-canonical-compiler-source"),
        (compiler_materialized, "optimized-source-presented-as-canonical"),
    ):
        checks.append(reject(
            lambda forged=counterfeit:
            state["compiler_transformer"].derive_source(forged),
            "reject-" + label, *kinds,
        ))
    checks.append(reject(
        lambda: verify_previous_actual_v25(
            state["v25_contract"],
            {**state["v25_publication"], "actual_compiler_process_count": 27},
            state["v25_root"],
        ), "reject-weakened-genuine-v25-compiler-count", *kinds,
    ))
    checks.append(reject(
        lambda: verify_actual_v25_original_failure(
            state["v25_campaign"],
            {**state["v25_failure"], "candidate_status": "PASS"},
        ), "reject-failed-v25-candidate-reclassified-as-pass", *kinds,
    ))
    checks.append(reject(
        lambda: verify_actual_v25_original_failure(
            state["v25_campaign"],
            {**state["v25_failure"], "semantic_mismatch_count": 1351},
        ), "reject-undercounted-complete-v25-mismatches", *kinds,
    ))
    checks.append(reject(
        lambda: verify_compiler_allocation_freeze(
            wall, additional[COMPILER_FASTPATH_OWNERS[0][0]],
            state["compiler_contract"],
            {**state["compiler_application"],
             "derived_rust_source_sha256": MATCHER_SHA},
            compiler_original, compiler_materialized,
        ), "reject-substituted-compiler-application-source", *kinds,
    ))

    for key in sorted(state["actual_v24_failure"]):
        altered_failure = dict(state["actual_v24_failure"])
        altered_failure[key] = {
            "__v25_forged_complete_actual_v24_failure_field__": key,
        }
        checks.append(reject(
            lambda item=altered_failure: validate_exact_document(
                capture, semantic, item, state["actual_v24_failure"],
                "complete independently published actual V24 FAIL-1352 receipt",
            ),
            "reject-changed-complete-actual-v24-failure-receipt-" + key,
            *kinds,
        ))

    for field, forged, label in (
        ("candidate_status", "PASS", "failed-v24-candidate-as-pass"),
        ("semantic_mismatch_count", 1351, "undercounted-v24-mismatches"),
        ("semantic_mismatch_count", 1353, "inflated-v24-mismatches"),
        ("verified_passing_case_count", 15878,
         "invented-v24-passing-observation"),
        ("completed_suite_count", 12, "dropped-complete-v24-suite"),
        ("combined_bridge_source_sha256", F9_SHA,
         "substituted-failed-f9-v24-source"),
        ("actual_v24_build_receipt_sha256", "0" * 64,
         "substituted-v24-build-success-receipt"),
    ):
        altered_failure = dict(state["actual_v24_failure"])
        altered_failure[field] = forged
        checks.append(reject(
            lambda item=altered_failure: verify_previous_actual_v24(
                state["actual_v24_build"], state["actual_v24_campaign"],
                state["actual_v24_guard"], state["actual_v24_build_receipt"],
                state["actual_v24_root_receipt"], item,
                additional[INPUT_VARIANT_OWNER[0]],
            ),
            "reject-" + label,
            *kinds,
        ))

    outer = semantic.OUTER_LENGTH_REWRITE
    original = semantic.FAILED_REPLACEMENT_ORIGINAL
    failed = semantic.FAILED_REPLACEMENT_CORRECTED
    capture_anchor = semantic.CAPTURE_INSERTION
    _bl, cache, _br = semantic.split_function(
        actual_v24_input,
        b"static int rust_replacement_cache(",
        b"\nstatic PyObject *rust_normalize_expand_buffer(",
        "authentic materialized V2 replacement cache",
    )
    forged_f9_cache = cache.replace(original, failed, 1)
    left, _cache, right = semantic.split_function(
        actual_v24_input,
        b"static int rust_replacement_cache(",
        b"\nstatic PyObject *rust_normalize_expand_buffer(",
        "reject the actual failed V22 replacement guard",
    )
    forged_f9 = left + forged_f9_cache + right
    require(digest(forged_f9) == F9_SHA and len(forged_f9) == 179147,
            "derive the entire genuine failed f9 solely as a negative control")
    variants = (
        (baseline + b"\n", materialized, matcher, "changed-complete-a0-base"),
        (baseline, baseline, matcher, "uncorrected-a0-base-as-new-variant"),
        (baseline, actual_v24_input, matcher,
         "uncorrected-complete-actual-v24-capture-bounds"),
        (baseline, forged_f9, matcher, "known-failing-f9-early-return-guard"),
        (baseline, materialized + b"\n", matcher,
         "changed-materialized-1adb-complete-bytes"),
        (baseline, materialized.replace(capture_anchor, b"", 1), matcher,
         "deleted-seventeen-line-captured-findall-path"),
        (baseline, materialized.replace(original, failed, 1), matcher,
         "replacement-cache-early-return-regression"),
        (baseline, materialized.replace(outer, b"", 1) + b"x", matcher,
         "forged-outer-length-source-derivation"),
        (baseline, materialized, matcher + b"\n",
         "changed-first-party-rust-matching-engine"),
    )
    for fake_base, fake_variant, fake_matcher, label in variants:
        checks.append(reject(
            lambda first=fake_base, second=fake_variant, engine=fake_matcher:
                verify_variant(semantic, first, second, engine),
            "reject-materialized-first-party-" + label, *kinds,
        ))

    for key in sorted(native_build_plan()):
        bad = dict(state["native_plan"])
        bad.pop(key)
        checks.append(reject(
            lambda item=bad: validate_native_build_plan(item),
            "reject-missing-complete-offline-build-obligation-" + key, *kinds,
        ))
    for key, value in (
        ("status", "PASS"),
        ("label", "phase2-v22-rust-capture-shape-root-provenance"),
        ("rustc", "/home/dev-user/.cargo/bin/rustc"),
        ("cargo", "/home/dev-user/.cargo/bin/cargo"),
        ("phase_count", 1),
        ("processes_per_phase", 13),
        ("required_actual_distinct_compiler_process_count", 27),
        ("actual_compiler_process_count", 28),
        ("actual_process_ids", [1]),
        ("private_variant_sha256", F9_SHA),
        ("private_variant_bytes", 179147),
        ("private_corrected_adapter_sha256", "0" * 64),
        ("engine_sha256", "0" * 64),
        ("bridge_sha256", "0" * 64),
        ("public_build_receipt_sha256", "0" * 64),
        ("public_root_receipt_sha256", "0" * 64),
        ("external_cargo_dependency_count", 1),
        ("stdlib_re_engine", "ALLOWED"),
        ("stdlib_sre_engine", "ALLOWED"),
        ("external_regex_engine", "ALLOWED"),
        ("cross_candidate_engine", "ALLOWED"),
        ("matching_fallback", "ALLOWED"),
        ("compiler_processes_started", 1),
        ("candidate_imports", 1),
        ("private_roots_opened", 1),
        ("network_requests", 1),
        ("holdout", "OPENED"),
    ):
        bad = dict(state["native_plan"])
        bad[key] = value
        checks.append(reject(
            lambda item=bad: validate_native_build_plan(item),
            "reject-forged-offline-dual-build-" + key, *kinds,
        ))

    for section, key, value, label in (
        ("immutable_complete_v24_actual_candidate_failure", "candidate_status",
         "PASS", "historical-failed-v24-candidate-as-pass"),
        ("immutable_complete_v24_actual_candidate_failure",
         "semantic_mismatch_count", 1351,
         "historical-v24-complete-1352-mismatches-as-1351"),
        ("immutable_complete_v24_actual_candidate_failure",
         "verified_passing_case_count", 15878,
         "fabricated-v24-verified-passing-case"),
        ("immutable_complete_v24_actual_source_build", "actual_build_status",
         "FAIL", "historical-passing-v24-native-build-as-failure"),
        ("immutable_operational_runtime_guard_v4", "version", 3,
         "downgraded-strict-operational-v4-guard"),
        ("immutable_first_party_capture_clamp_transformer",
         "capture_function_changed_count", 2,
         "multiple-unowned-capture-functions-changed"),
        ("immutable_first_party_capture_clamp_transformer",
         "synthetic_bounds_case_count", 4799,
         "dropped-frozen-capture-bounds-hostile-case"),
        ("immutable_first_party_capture_clamp_transformer",
         "sealed_proposal_file_opened", True,
         "opened-frozen-phase-three-proposal"),
        ("immutable_genuine_v22_failure", "candidate_status", "PASS",
         "historical-failed-candidate-as-pass"),
        ("immutable_genuine_v22_failure", "global_semantic_mismatch_count",
         2018, "observed-lower-bound-as-complete-mismatch-count"),
        ("immutable_genuine_v22_failure",
         "transient_physical_native_child_creation", False,
         "false-absence-of-transient-native-child"),
        ("immutable_genuine_v22_failure",
         "transient_physical_native_child_creation", True,
         "false-confirmation-of-transient-native-child"),
        ("immutable_genuine_v22_failure",
         "recorded_successfully_returned_child_interpreters", 1,
         "fabricated-successful-historical-child"),
        ("immutable_genuine_v22_failure",
         "failing_worker_native_library_loads", 0,
         "erased-two-real-historical-worker-native-loads"),
        ("materialized_first_party_variant", "native_build", "PASS",
         "materialized-source-as-native-build"),
        ("materialized_first_party_variant", "candidate_correctness", "PASS",
         "source-only-candidate-correctness"),
        ("materialized_first_party_variant", "native_engine_sha256",
         "0" * 64, "fabricated-engine-binary"),
        ("source_only_effects", "candidate_imports", 1,
         "unauthorized-candidate-import"),
        ("source_only_effects", "compiler_processes_started", 1,
         "unauthorized-native-compilation"),
        ("source_only_effects", "holdout", "OPENED",
         "opened-sealed-holdout"),
        ("source_only_effects", "expanded_holdout_proposal_case_count",
         14155776, "downgraded-141557760-case-sealed-proposal"),
        ("source_only_effects", "performance", "1.5x",
         "invented-source-only-speed"),
        ("source_only_effects", "winner_selected", True,
         "invented-source-only-winner"),
    ):
        bad = capture.clone(semantic, frozen)
        assert isinstance(bad, dict)
        bad[section][key] = value
        checks.append(reject(
            lambda item=bad: validate_exact_document(
                capture, semantic, item, frozen, "complete V23 build freeze",
            ), "reject-v23-build-" + label, *kinds,
        ))

    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    forbidden_paths = (
        (ROOT + "/candidates/_rust_engine.so", "installed-native-engine"),
        (ROOT + "/candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
         "installed-native-bridge"),
        (ROOT + "/candidates/zig_candidate.py", "other-candidate-family"),
        (ROOT + "/candidates/cpp_candidate.py", "other-native-family"),
        (ROOT + "/candidates/rust/variants/unapproved/py_bridge.c",
         "unapproved-variant"),
        (ROOT + "/tools/../candidates/_rust_engine.so",
         "lexical-native-path-traversal"),
        (ROOT + "/tools/./../candidates/rust_candidate.py",
         "lexical-candidate-path-traversal"),
        (ROOT + "/oracle/phase2/../../candidates/_rust_engine.so",
         "oracle-native-path-traversal"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v1.json",
         "sealed-phase-three-holdout"),
        (ROOT + "/oracle/phase3/expanded-sealed-holdout-v2.json",
         "sealed-141557760-case-final-holdout"),
        (ROOT + "/candidates/rust/variants/mandatory_anchor_search_v1/lib.rs",
         "independent-anchor-architecture-matcher"),
        (ROOT + "/candidates/rust/variants/mandatory_anchor_search_v1/search.rs",
         "independent-anchor-architecture-search"),
        (ROOT + "/oracle/phase2/evidence/forbidden.json.gz",
         "compressed-historical-archive"),
        (ROOT + "/oracle/phase2/evidence/repaired-rust-original-campaign-v16-"
         "rust-phase2-v25-rust-capture-clamp-v1-root-provenance-"
         "original-p0-v25-failures.json.gz",
         "complete-3771743-byte-v25-failure-archive"),
        ("/tmp/rebar-phase2-native-build-v9-rust-forbidden",
         "private-native-build-root"),
        ("/tmp/rebar-hidden-holdout", "external-hidden-holdout"),
        ("/etc/hosts", "foreign-unowned-source"),
    )
    for path, label in forbidden_paths:
        checks.append(reject(
            lambda target=path: os.open(target, flags),
            "physical-source-wall-rejects-os-open-" + label, *kinds,
        ))
        checks.append(reject(
            lambda target=path: wall.native_open(target, flags),
            "physical-source-wall-rejects-native-open-" + label, *kinds,
        ))

    historical_native = ROOT + "/candidates/_rust_engine.so"
    for label, action in (
        ("builtins-open", lambda: builtins.open(historical_native, "rb")),
        ("direct-_io-open", lambda: _io.open(historical_native, "rb")),
        ("direct-_io-fileio", lambda: _io.FileIO(historical_native, "r")),
        ("direct-io-open", lambda: io.open(historical_native, "rb")),
        ("direct-io-fileio", lambda: io.FileIO(historical_native, "r")),
        ("unowned-descriptor-read", lambda: os.read(0, 1)),
        ("unowned-descriptor-stat", lambda: os.fstat(0)),
        ("unowned-descriptor-close", lambda: os.close(0)),
        ("unowned-descriptor-dup", lambda: os.dup(0)),
        ("unowned-descriptor-fdopen", lambda: os.fdopen(0)),
        ("candidate-stat", lambda: os.stat(historical_native)),
        ("candidate-lstat", lambda: os.lstat(historical_native)),
        ("candidate-readlink", lambda: os.readlink(historical_native)),
        ("candidate-access", lambda: os.access(historical_native, os.R_OK)),
        ("candidate-listdir", lambda: os.listdir(ROOT + "/candidates")),
        ("candidate-scandir", lambda: os.scandir(ROOT + "/candidates")),
        ("clock-time", lambda: time.time()),
        ("clock-monotonic", lambda: time.monotonic()),
        ("clock-perf-counter", lambda: time.perf_counter()),
        ("entropy-urandom", lambda: os.urandom(8)),
        ("source-write", lambda: builtins.open(ROOT + "/" + SOURCE, "w")),
        ("stdlib-matcher", lambda: sys.audit("import", "re", None)),
        ("stdlib-native-matcher", lambda: sys.audit("import", "_sre", None)),
        ("external-regex-engine", lambda: sys.audit("import", "regex", None)),
        ("native-dynamic-loader", lambda: sys.audit("ctypes.dlopen", "x")),
        ("rust-compiler-process",
         lambda: sys.audit("subprocess.Popen", "rustc")),
        ("native-child-creation",
         lambda: sys.audit("cpython.PyInterpreterState_New")),
        ("private-build-root",
         lambda: sys.audit("tempfile.mkdtemp", "x")),
        ("network", lambda: sys.audit("socket.connect", "x")),
        ("untrusted-dynamic-code", lambda: sys.audit("exec", "x")),
    ):
        checks.append(reject(
            action, "physical-source-wall-rejects-" + label, *kinds,
        ))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE, os.O_RDONLY),
        "physical-source-wall-rejects-approved-owner-without-no-follow",
        *kinds,
    ))
    checks.append(reject(
        lambda: os.open(ROOT + "/" + SOURCE, flags | os.O_WRONLY | os.O_TRUNC),
        "physical-source-wall-rejects-approved-source-destruction",
        *kinds,
    ))

    for mode in ACTUAL_MODES:
        live_before = len(wall.live)
        blocks_before = dict(wall.blocked)
        checks.append(reject(
            lambda selected=mode: reject_source_only_activation(
                {"mode": selected},
            ),
            "reject-unpushed-unexecuted-native-build-"
            + mode.removeprefix("--"), *kinds,
        ))
        require(len(wall.live) == live_before and wall.blocked == blocks_before,
                "reject a synthetic build mode without private or candidate I/O")

    actual_arguments = [
        "--run",
        "--source-sha256", state["source_row"][2],
        "--protocol-sha256", state["protocol_row"][2],
        "--contract-sha256", state["contract_row"][2],
        "--label", BUILD_LABEL,
        "--variant-sha256", VARIANT_SHA,
        "--variant-bytes", str(VARIANT_BYTES),
        "--corrected-adapter-sha256", ADAPTER_SHA,
        "--corrected-adapter-bytes", str(ADAPTER_BYTES),
        "--previous-v23-source-sha256", BUILD_V23_OWNERS[0][2],
        "--previous-v23-protocol-sha256", BUILD_V23_OWNERS[1][2],
        "--previous-v23-contract-sha256", BUILD_V23_OWNERS[2][2],
        "--phase1-v4-source-sha256",
        PHASE_ONE_V4_PINS["phase1_v4_source_sha256"],
        "--phase1-v4-protocol-sha256",
        PHASE_ONE_V4_PINS["phase1_v4_protocol_sha256"],
        "--phase1-v4-contract-sha256",
        PHASE_ONE_V4_PINS["phase1_v4_contract_sha256"],
        "--previous-v24-build-source-sha256", BUILD_V24_OWNERS[0][2],
        "--previous-v24-build-protocol-sha256", BUILD_V24_OWNERS[1][2],
        "--previous-v24-build-contract-sha256", BUILD_V24_OWNERS[2][2],
        "--previous-v24-build-receipt-sha256", PREVIOUS_BUILD_RECEIPT_SHA,
        "--previous-v24-root-receipt-sha256", PREVIOUS_ROOT_RECEIPT_SHA,
        "--previous-v24-failure-receipt-sha256", PREVIOUS_FAILURE_RECEIPT_SHA,
        "--runtime-guard-v4-source-sha256", RUNTIME_GUARD_V4_OWNERS[0][2],
        "--runtime-guard-v4-protocol-sha256", RUNTIME_GUARD_V4_OWNERS[1][2],
        "--runtime-guard-v4-contract-sha256", RUNTIME_GUARD_V4_OWNERS[2][2],
        "--capture-clamp-source-sha256", CAPTURE_CLAMP_OWNERS[0][2],
        "--capture-clamp-protocol-sha256", CAPTURE_CLAMP_OWNERS[1][2],
        "--capture-clamp-contract-sha256", CAPTURE_CLAMP_OWNERS[2][2],
        "--compiler-source-sha256", COMPILER_VARIANT_SHA,
        "--compiler-source-bytes", str(COMPILER_VARIANT_BYTES),
        "--compiler-freeze-source-sha256", COMPILER_FASTPATH_OWNERS[0][2],
        "--compiler-freeze-protocol-sha256", COMPILER_FASTPATH_OWNERS[1][2],
        "--compiler-freeze-contract-sha256", COMPILER_FASTPATH_OWNERS[2][2],
        "--compiler-application-sha256", COMPILER_APPLICATION_OWNER[2],
        "--previous-v25-source-sha256", BUILD_V25_OWNERS[0][2],
        "--previous-v25-protocol-sha256", BUILD_V25_OWNERS[1][2],
        "--previous-v25-contract-sha256", BUILD_V25_OWNERS[2][2],
        "--previous-v25-publication-sha256", V25_BUILD_RECEIPT_SHA,
        "--previous-v25-root-sha256", V25_ROOT_RECEIPT_SHA,
        "--previous-v25-campaign-source-sha256", CAMPAIGN_V25_OWNERS[0][2],
        "--previous-v25-campaign-protocol-sha256", CAMPAIGN_V25_OWNERS[1][2],
        "--previous-v25-campaign-contract-sha256", CAMPAIGN_V25_OWNERS[2][2],
        "--previous-v25-failure-receipt-sha256", V25_FAILURE_RECEIPT_SHA,
    ]
    for row in CANONICAL_RUST_OWNERS:
        actual_arguments.extend(
            ("--owned-source-sha256", row[1] + "=" + row[2]),
        )
    parsed = parse_actual_arguments(actual_arguments)
    require(
        parsed["combined_bridge_sha256"] == VARIANT_SHA
        and parsed["combined_bridge_bytes"] == VARIANT_BYTES
        and parsed["compiler_source_sha256"] == COMPILER_VARIANT_SHA
        and parsed["compiler_source_bytes"] == COMPILER_VARIANT_BYTES
        and parsed["previous_v25_root_sha256"] == V25_ROOT_RECEIPT_SHA
        and len(parsed["owned_source_sha256"]) == 9,
        "synthetically validate complete actual pins without starting a build",
    )
    checks.append("validate-complete-actual-authority-without-activation")
    for index in range(1, len(actual_arguments), 2):
        shortened = (
            actual_arguments[:index] + actual_arguments[index + 2:]
        )
        checks.append(reject(
            lambda item=shortened: parse_actual_arguments(item),
            "reject-missing-actual-authority-"
            + actual_arguments[index].removeprefix("--")
            + "-" + str(index),
            *kinds,
        ))
    for index, value, label in (
        (8, "phase2-v23-rust-capture-shape-v2-root-provenance",
         "previous-version-label"),
        (10, F9_SHA, "historical-failed-f9-bridge"),
        (12, "179147", "historical-failed-f9-byte-count"),
        (14, "0" * 64, "substituted-private-adapter"),
        (16, "31933", "truncated-private-adapter"),
        (18, "0" * 64, "substituted-previous-v23-source"),
        (20, "0" * 64, "substituted-previous-v23-protocol"),
        (22, "0" * 64, "substituted-previous-v23-contract"),
        (24, "0" * 64, "substituted-phase-one-source"),
        (26, "0" * 64, "substituted-phase-one-protocol"),
        (28, "0" * 64, "substituted-phase-one-contract"),
    ):
        forged = list(actual_arguments)
        forged[index] = value
        checks.append(reject(
            lambda item=forged: parse_actual_arguments(item),
            "reject-forged-actual-authority-" + label,
            *kinds,
        ))
    checks.append(reject(
        lambda: parse_actual_arguments(
            actual_arguments
            + ["--combined-bridge-sha256", VARIANT_SHA],
        ),
        "reject-aliased-duplicate-actual-bridge-authority",
        *kinds,
    ))
    require(
        len(wall.live) == 0,
        "actual-authority self-tests must not open native or private files",
    )

    extra = dict(frozen)
    extra["__fabricated_v23_native_build_evidence__"] = True
    checks.append(reject(
        lambda: validate_exact_document(
            capture, semantic, extra, frozen, "complete V23 build freeze",
        ), "reject-fabricated-v23-native-build-evidence", *kinds,
    ))
    no_matching_imports()
    require(wall.installed and not wall.live and bool(wall.blocked)
            and len(checks) >= 1200,
            "require complete physically isolated genuine-source controls")
    return checks



ACTUAL_ORIGINAL_TARGETS = (
    ("original_matching_engine_source", "candidates/rust/src/lib.rs",
     MATCHER_SHA, 177967, 428096, 0o600),
    ("original_bridge_source", "candidates/rust/py_bridge.c",
     "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
     175676, 419054, 0o600),
    ("original_public_adapter", "candidates/rust_candidate.py",
     "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
     31151, 428100, 0o600),
    ("original_installed_engine", "candidates/_rust_engine.so",
     "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
     660440, 430563, 0o755),
    ("original_installed_bridge",
     "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
     "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
     144992, 430629, 0o755),
)


def read_actual_owner(row: tuple, *, executable: bool = False) -> tuple:
    require(type(row) is tuple and len(row) in (5, 6),
            "require one independently owned complete actual build input")
    role, relative, expected, count, inode = row[:5]
    mode = row[5] if len(row) == 6 else 0o600
    require(
        type(role) is str and type(relative) is str
        and not relative.startswith("/")
        and ".." not in relative.split("/")
        and type(count) is int and 0 < count <= MAX_OWNER_BYTES
        and type(inode) is int and inode > 0
        and mode in (0o600, 0o755)
        and (mode == 0o755) == executable,
        "reject a substituted actual build source or original target",
    )
    hash_pin(expected, relative)
    flags = (
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(ROOT + "/" + relative, flags)
    try:
        before = os.fstat(descriptor)
        require(
            stat.S_ISREG(before.st_mode)
            and stat.S_IMODE(before.st_mode) == mode
            and before.st_dev == DEVICE
            and before.st_ino == inode
            and before.st_size == count
            and before.st_uid == os.geteuid()
            and before.st_nlink == 1,
            "reject a substituted complete actual owner: " + role,
        )
        chunks: list[bytes] = []
        remaining = count
        while remaining:
            chunk = os.read(descriptor, min(remaining, 65536))
            require(type(chunk) is bytes and bool(chunk),
                    "reject truncated actual owner: " + role)
            chunks.append(chunk)
            remaining -= len(chunk)
        require(os.read(descriptor, 1) == b"",
                "reject expanded actual owner: " + role)
        after = os.fstat(descriptor)
        require(all(
            getattr(before, field) == getattr(after, field)
            for field in (
                "st_dev", "st_ino", "st_size", "st_mtime_ns",
                "st_ctime_ns", "st_nlink",
            )
        ), "reject an actual owner changed while authenticated: " + role)
        raw = b"".join(chunks)
        require(digest(raw) == expected,
                "reject substituted complete actual owner bytes: " + role)
        identity = {
            "role": role, "path": relative, "sha256": expected,
            "bytes": count, "device": before.st_dev, "inode": before.st_ino,
            "mode": "0755" if executable else "0600",
            "uid": before.st_uid, "nlink": before.st_nlink,
            "mtime_ns": before.st_mtime_ns,
            "ctime_ns": before.st_ctime_ns,
        }
        return raw, identity
    finally:
        os.close(descriptor)


def snapshot_actual_original_targets() -> dict:
    identities: dict[str, dict] = {}
    for row in ACTUAL_ORIGINAL_TARGETS:
        _raw, identity = read_actual_owner(
            row, executable=row[5] == 0o755,
        )
        identities[row[0]] = identity
    require(
        len(identities) == 5,
        "authenticate the canonical matcher, bridge, adapter, and native targets",
    )
    return identities


def checked_actual_label(value: object) -> str:
    require(
        type(value) is str and value == BUILD_LABEL
        and len(value) == 48
        and all(
            character.isascii()
            and (character.isalnum() or character in "-_")
            for character in value
        ),
        "require the unique exact V24 evidence label",
    )
    return value


def actual_evidence_names(label: str, failed: bool) -> tuple[str, str]:
    require(type(failed) is bool,
            "preserve each genuine successful or failed build separately")
    stem = "native-source-build-v27-rust-" + checked_actual_label(label)
    if failed:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def actual_root_receipt_name(label: str) -> str:
    return (
        "native-source-build-v27-rust-" + checked_actual_label(label)
        + "-root-provenance-receipt.json"
    )


def actual_base_row(row: tuple) -> tuple:
    require(type(row) is tuple and len(row) == 5,
            "convert one complete no-follow first-party owner")
    return row[0], row[1], row[2], row[3], DEVICE, row[4]


def decode_actual_public(base: dict, raw: bytes, label: str) -> dict:
    value = base["StrictJSON"](raw).decode()
    require(type(value) is dict,
            "decode one complete actual frozen public object: " + label)
    require(
        (base["canonical"](value) + "\n").encode("ascii") == raw,
        "reject truncated, changed or noncanonical actual evidence: " + label,
    )
    return value


def parse_actual_arguments(arguments: list[str]) -> dict:
    require(
        type(arguments) is list and bool(arguments)
        and arguments[0] in ACTUAL_MODES,
        "select one explicitly root-authorized actual V24 build",
    )
    mapping = {
        "--source-sha256": "source_sha256",
        "--protocol-sha256": "protocol_sha256",
        "--contract-sha256": "contract_sha256",
        "--label": "label",
        "--variant-sha256": "combined_bridge_sha256",
        "--combined-bridge-sha256": "combined_bridge_sha256",
        "--variant-bytes": "combined_bridge_bytes",
        "--combined-bridge-bytes": "combined_bridge_bytes",
        "--corrected-adapter-sha256": "corrected_adapter_sha256",
        "--corrected-adapter-bytes": "corrected_adapter_bytes",
        "--previous-v23-source-sha256": "previous_v23_source_sha256",
        "--previous-v23-protocol-sha256": "previous_v23_protocol_sha256",
        "--previous-v23-contract-sha256": "previous_v23_contract_sha256",
        "--previous-v24-build-source-sha256":
            "previous_v24_build_source_sha256",
        "--previous-v24-build-protocol-sha256":
            "previous_v24_build_protocol_sha256",
        "--previous-v24-build-contract-sha256":
            "previous_v24_build_contract_sha256",
        "--previous-v24-build-receipt-sha256":
            "previous_v24_build_receipt_sha256",
        "--previous-v24-root-receipt-sha256":
            "previous_v24_root_receipt_sha256",
        "--previous-v24-failure-receipt-sha256":
            "previous_v24_failure_receipt_sha256",
        "--runtime-guard-v4-source-sha256": "runtime_guard_v4_source_sha256",
        "--runtime-guard-v4-protocol-sha256":
            "runtime_guard_v4_protocol_sha256",
        "--runtime-guard-v4-contract-sha256":
            "runtime_guard_v4_contract_sha256",
        "--capture-clamp-source-sha256": "capture_clamp_source_sha256",
        "--capture-clamp-protocol-sha256": "capture_clamp_protocol_sha256",
        "--capture-clamp-contract-sha256": "capture_clamp_contract_sha256",
        "--phase1-v4-source-sha256": "phase1_v4_source_sha256",
        "--phase1-v4-protocol-sha256": "phase1_v4_protocol_sha256",
        "--phase1-v4-contract-sha256": "phase1_v4_contract_sha256",
        "--compiler-source-sha256": "compiler_source_sha256",
        "--compiler-source-bytes": "compiler_source_bytes",
        "--compiler-freeze-source-sha256": "compiler_freeze_source_sha256",
        "--compiler-freeze-protocol-sha256": "compiler_freeze_protocol_sha256",
        "--compiler-freeze-contract-sha256": "compiler_freeze_contract_sha256",
        "--compiler-application-sha256": "compiler_application_sha256",
        "--previous-v25-source-sha256": "previous_v25_source_sha256",
        "--previous-v25-protocol-sha256": "previous_v25_protocol_sha256",
        "--previous-v25-contract-sha256": "previous_v25_contract_sha256",
        "--previous-v25-publication-sha256": "previous_v25_publication_sha256",
        "--previous-v25-root-sha256": "previous_v25_root_sha256",
        "--previous-v25-campaign-source-sha256":
            "previous_v25_campaign_source_sha256",
        "--previous-v25-campaign-protocol-sha256":
            "previous_v25_campaign_protocol_sha256",
        "--previous-v25-campaign-contract-sha256":
            "previous_v25_campaign_contract_sha256",
        "--previous-v25-failure-receipt-sha256":
            "previous_v25_failure_receipt_sha256",
    }
    result: dict[str, object] = {
        "mode": arguments[0], "owned_source_sha256": [],
    }
    index = 1
    while index < len(arguments):
        require(index + 1 < len(arguments),
                "reject a missing independent actual-build pin")
        flag, value = arguments[index], arguments[index + 1]
        require(type(flag) is str and type(value) is str,
                "reject non-string actual-build authority")
        if flag == "--owned-source-sha256":
            result["owned_source_sha256"].append(value)
            index += 2
            continue
        require(flag in mapping, "reject unknown actual-build authority")
        name = mapping[flag]
        require(name not in result,
                "reject duplicated or aliased actual-build authority")
        if name.endswith("_bytes"):
            require(value.isascii() and value.isdecimal(),
                    "require a decimal exact actual overlay byte count")
            result[name] = int(value)
        elif name == "label":
            result[name] = checked_actual_label(value)
        else:
            result[name] = hash_pin(value, flag)
        index += 2
    required = {
        "source_sha256", "protocol_sha256", "contract_sha256", "label",
        "combined_bridge_sha256", "combined_bridge_bytes",
        "corrected_adapter_sha256", "corrected_adapter_bytes",
        "previous_v23_source_sha256", "previous_v23_protocol_sha256",
        "previous_v23_contract_sha256",
        "previous_v24_build_source_sha256",
        "previous_v24_build_protocol_sha256",
        "previous_v24_build_contract_sha256",
        "previous_v24_build_receipt_sha256",
        "previous_v24_root_receipt_sha256",
        "previous_v24_failure_receipt_sha256",
        "runtime_guard_v4_source_sha256",
        "runtime_guard_v4_protocol_sha256",
        "runtime_guard_v4_contract_sha256",
        "capture_clamp_source_sha256",
        "capture_clamp_protocol_sha256",
        "capture_clamp_contract_sha256",
        "phase1_v4_source_sha256", "phase1_v4_protocol_sha256",
        "phase1_v4_contract_sha256",
        "compiler_source_sha256", "compiler_source_bytes",
        "compiler_freeze_source_sha256", "compiler_freeze_protocol_sha256",
        "compiler_freeze_contract_sha256", "compiler_application_sha256",
        "previous_v25_source_sha256", "previous_v25_protocol_sha256",
        "previous_v25_contract_sha256", "previous_v25_publication_sha256",
        "previous_v25_root_sha256",
        "previous_v25_campaign_source_sha256",
        "previous_v25_campaign_protocol_sha256",
        "previous_v25_campaign_contract_sha256",
        "previous_v25_failure_receipt_sha256",
    }
    require(
        set(result) == required | {"mode", "owned_source_sha256"},
        "caller-pin the complete root-authorized V24 build authority",
    )
    for key, expected in (
        ("label", BUILD_LABEL),
        ("combined_bridge_sha256", VARIANT_SHA),
        ("combined_bridge_bytes", VARIANT_BYTES),
        ("corrected_adapter_sha256", ADAPTER_SHA),
        ("corrected_adapter_bytes", ADAPTER_BYTES),
        ("previous_v23_source_sha256", BUILD_V23_OWNERS[0][2]),
        ("previous_v23_protocol_sha256", BUILD_V23_OWNERS[1][2]),
        ("previous_v23_contract_sha256", BUILD_V23_OWNERS[2][2]),
        ("previous_v24_build_source_sha256", BUILD_V24_OWNERS[0][2]),
        ("previous_v24_build_protocol_sha256", BUILD_V24_OWNERS[1][2]),
        ("previous_v24_build_contract_sha256", BUILD_V24_OWNERS[2][2]),
        ("previous_v24_build_receipt_sha256", PREVIOUS_BUILD_RECEIPT_SHA),
        ("previous_v24_root_receipt_sha256", PREVIOUS_ROOT_RECEIPT_SHA),
        ("previous_v24_failure_receipt_sha256", PREVIOUS_FAILURE_RECEIPT_SHA),
        ("runtime_guard_v4_source_sha256", RUNTIME_GUARD_V4_OWNERS[0][2]),
        ("runtime_guard_v4_protocol_sha256", RUNTIME_GUARD_V4_OWNERS[1][2]),
        ("runtime_guard_v4_contract_sha256", RUNTIME_GUARD_V4_OWNERS[2][2]),
        ("capture_clamp_source_sha256", CAPTURE_CLAMP_OWNERS[0][2]),
        ("capture_clamp_protocol_sha256", CAPTURE_CLAMP_OWNERS[1][2]),
        ("capture_clamp_contract_sha256", CAPTURE_CLAMP_OWNERS[2][2]),
        ("compiler_source_sha256", COMPILER_VARIANT_SHA),
        ("compiler_source_bytes", COMPILER_VARIANT_BYTES),
        ("compiler_freeze_source_sha256", COMPILER_FASTPATH_OWNERS[0][2]),
        ("compiler_freeze_protocol_sha256", COMPILER_FASTPATH_OWNERS[1][2]),
        ("compiler_freeze_contract_sha256", COMPILER_FASTPATH_OWNERS[2][2]),
        ("compiler_application_sha256", COMPILER_APPLICATION_OWNER[2]),
        ("previous_v25_source_sha256", BUILD_V25_OWNERS[0][2]),
        ("previous_v25_protocol_sha256", BUILD_V25_OWNERS[1][2]),
        ("previous_v25_contract_sha256", BUILD_V25_OWNERS[2][2]),
        ("previous_v25_publication_sha256", V25_BUILD_RECEIPT_SHA),
        ("previous_v25_root_sha256", V25_ROOT_RECEIPT_SHA),
        ("previous_v25_campaign_source_sha256", CAMPAIGN_V25_OWNERS[0][2]),
        ("previous_v25_campaign_protocol_sha256", CAMPAIGN_V25_OWNERS[1][2]),
        ("previous_v25_campaign_contract_sha256", CAMPAIGN_V25_OWNERS[2][2]),
        ("previous_v25_failure_receipt_sha256", V25_FAILURE_RECEIPT_SHA),
        *tuple(PHASE_ONE_V4_PINS.items()),
    ):
        require(result.get(key) == expected,
                "reject substituted actual V24 authority: " + key)
    expected_originals = {
        row[1] + "=" + row[2] for row in CANONICAL_RUST_OWNERS
    }
    provided = result["owned_source_sha256"]
    require(
        type(provided) is list and len(provided) == 9
        and len(set(provided)) == 9
        and set(provided) == expected_originals,
        "independently caller-pin all nine complete canonical Rust sources",
    )
    return result


def publish_actual_build_report(
    module: object, kernel: object, report: dict,
) -> dict:
    require(
        type(report) is dict and report.get("status") in ("PASS", "FAIL")
        and report.get("family") == FAMILY
        and report.get("label") == BUILD_LABEL,
        "publish only a genuine actual first-party V24 build outcome",
    )
    complete = dict(report)
    prior_mismatch = complete.pop("historical_rust_mismatch_count", None)
    prior_passing = complete.pop(
        "historical_rust_verified_passing_case_count", None,
    )
    require(
        prior_mismatch == 928 and prior_passing == 8965,
        "preserve but accurately identify the earlier V16 historical record",
    )
    reproduction = complete.get("reproducibility")
    compiler_overlay_count = (
        reproduction.get("compiler_source_overlay_count", 0)
        if type(reproduction) is dict else 0
    )
    require(
        complete.get("status") != "PASS" or compiler_overlay_count == 2,
        "require both private compiler overlays before successful publication",
    )
    complete.update({
        "compiler_source_sha256": COMPILER_VARIANT_SHA,
        "compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "compiler_source_overlay_apply_count": compiler_overlay_count,
        "compiler_freeze_source_sha256": COMPILER_FASTPATH_OWNERS[0][2],
        "compiler_freeze_protocol_sha256": COMPILER_FASTPATH_OWNERS[1][2],
        "compiler_freeze_contract_sha256": COMPILER_FASTPATH_OWNERS[2][2],
        "compiler_application_sha256": COMPILER_APPLICATION_OWNER[2],
        "previous_actual_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240, "shape_v2": 1112,
        },
        "canonical_matching_source_sha256": MATCHER_SHA,
        "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
        "anchor_search_variant_used": False,
        "earlier_v16_historical_rust_mismatch_count": prior_mismatch,
        "earlier_v16_historical_rust_verified_passing_case_count":
            prior_passing,
        "latest_v24_original_campaign_receipt_sha256":
            PREVIOUS_FAILURE_RECEIPT_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "latest_v24_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240,
            "shape_v2": 1112,
        },
        "previous_actual_v24_native_build_receipt_sha256":
            PREVIOUS_BUILD_RECEIPT_SHA,
        "previous_actual_v24_native_root_receipt_sha256":
            PREVIOUS_ROOT_RECEIPT_SHA,
        "strict_runtime_guard_v4_contract_sha256":
            RUNTIME_GUARD_V4_OWNERS[2][2],
        "capture_clamp_source_sha256": CAPTURE_CLAMP_OWNERS[0][2],
        "capture_clamp_protocol_sha256": CAPTURE_CLAMP_OWNERS[1][2],
        "capture_clamp_contract_sha256": CAPTURE_CLAMP_OWNERS[2][2],
        "latest_v22_original_campaign_receipt_sha256": PUBLIC_OWNERS[17][2],
        "latest_v22_candidate_status": "FAIL",
        "latest_v22_verified_passing_case_count": 14725,
        "latest_v22_observed_mismatch_lower_bound": 2018,
        "latest_v22_global_semantic_mismatch_count": NOT_MEASURED,
        "latest_v22_failing_worker_pid": 188,
        "latest_v22_failing_worker_candidate_imports": 1,
        "latest_v22_failing_worker_native_library_loads": 2,
        "latest_v22_failing_worker_transient_physical_native_child_creation":
            NOT_MEASURED,
        "latest_v22_remaining_interpreter_warnings": 1,
        "latest_v22_destructor_warnings": 16,
        "complete_previous_v23_source_build_contract_sha256":
            BUILD_V23_OWNERS[2][2],
    })
    label = checked_actual_label(complete["label"])
    archive_name, receipt_name = actual_evidence_names(
        label, complete["status"] == "FAIL",
    )
    directory = module.ROOT / EVIDENCE_PATH
    plain = module.canonical(complete)
    require(
        0 < len(plain) <= module.MAX_REPORT_BYTES,
        "bound the complete genuine V24 dual-source-build report",
    )
    archive = module.gzip.compress(plain, compresslevel=9, mtime=0)
    require(
        0 < len(archive) <= module.MAX_REPORT_BYTES,
        "bound the actual deterministic V24 native-build archive",
    )
    saved = kernel.write_fresh(
        directory / archive_name, archive, synchronize=True,
    )
    archive_sync = kernel.fsync_directory(directory)
    require(
        saved.get("sha256") == digest(archive)
        and saved.get("bytes") == len(archive)
        and saved.get("exclusive_creation") is True
        and saved.get("file_fsync_completed") is True
        and archive_sync.get("completed") is True,
        "exclusively create and synchronize the genuine actual V24 archive",
    )
    operations = complete.get("compiler_processes")
    require(type(operations) is list,
            "retain the complete genuinely observed compiler operations")
    receipt = {
        "schema": SCHEMA + "-durable-publication-receipt",
        "status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": complete["status"],
        "family": FAMILY,
        "label": label,
        "source_sha256": complete["source_sha256"],
        "protocol_sha256": complete["protocol_sha256"],
        "contract_sha256": complete["contract_sha256"],
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": saved["sha256"],
        "archive_bytes": saved["bytes"],
        "archive_publication": saved,
        "archive_directory_fsync": archive_sync,
        "uncompressed_sha256": digest(plain),
        "uncompressed_bytes": len(plain),
        "current_graph_version": module.FINAL_GRAPH_VERSION,
        "prepublication_evidence_owner_lower_bound":
            module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND,
        "prepublication_history_reference_lower_bound":
            module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND,
        "later_append_only_evidence_allowed": True,
        "new_actual_evidence_owner_count": 2,
        "evidence_owner_lower_bound_after_publication":
            module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND + 2,
        "history_reference_lower_bound_after_publication":
            module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND + 2,
        "global_evidence_owner_census": NOT_MEASURED,
        "global_history_reference_census": NOT_MEASURED,
        "earlier_v16_historical_rust_mismatch_count": prior_mismatch,
        "earlier_v16_historical_rust_verified_passing_case_count":
            prior_passing,
        "latest_v24_original_campaign_receipt_sha256":
            PREVIOUS_FAILURE_RECEIPT_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "latest_v24_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240,
            "shape_v2": 1112,
        },
        "previous_actual_v24_native_build_receipt_sha256":
            PREVIOUS_BUILD_RECEIPT_SHA,
        "previous_actual_v24_native_root_receipt_sha256":
            PREVIOUS_ROOT_RECEIPT_SHA,
        "strict_runtime_guard_v4_contract_sha256":
            RUNTIME_GUARD_V4_OWNERS[2][2],
        "capture_clamp_source_sha256": CAPTURE_CLAMP_OWNERS[0][2],
        "capture_clamp_protocol_sha256": CAPTURE_CLAMP_OWNERS[1][2],
        "capture_clamp_contract_sha256": CAPTURE_CLAMP_OWNERS[2][2],
        "expanded_holdout_proposal_case_count":
            EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT,
        "latest_v22_original_campaign_receipt_sha256": PUBLIC_OWNERS[17][2],
        "latest_v22_candidate_status": "FAIL",
        "latest_v22_verified_passing_case_count": 14725,
        "latest_v22_observed_mismatch_lower_bound": 2018,
        "latest_v22_global_semantic_mismatch_count": NOT_MEASURED,
        "latest_v22_failing_worker_pid": 188,
        "latest_v22_failing_worker_candidate_imports": 1,
        "latest_v22_failing_worker_native_library_loads": 2,
        "latest_v22_failing_worker_transient_physical_native_child_creation":
            NOT_MEASURED,
        "latest_v22_remaining_interpreter_warnings": 1,
        "latest_v22_destructor_warnings": 16,
        "complete_previous_v23_source_build_contract_sha256":
            BUILD_V23_OWNERS[2][2],
        "buffer_feature_source_sha256": module.BUFFER_FEATURE[0].sha256,
        "buffer_feature_protocol_sha256": module.BUFFER_FEATURE[1].sha256,
        "buffer_feature_contract_sha256": module.BUFFER_FEATURE[2].sha256,
        "buffer_variant_sha256": module.BUFFER_VARIANT.sha256,
        "pickle_feature_source_sha256": module.PICKLE_FEATURE[0].sha256,
        "pickle_feature_protocol_sha256": module.PICKLE_FEATURE[1].sha256,
        "pickle_feature_contract_sha256": module.PICKLE_FEATURE[2].sha256,
        "combined_bridge_sha256": VARIANT_SHA,
        "combined_bridge_bytes": VARIANT_BYTES,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "compiler_source_sha256": COMPILER_VARIANT_SHA,
        "compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "compiler_source_overlay_apply_count": compiler_overlay_count,
        "compiler_freeze_source_sha256": COMPILER_FASTPATH_OWNERS[0][2],
        "compiler_freeze_protocol_sha256": COMPILER_FASTPATH_OWNERS[1][2],
        "compiler_freeze_contract_sha256": COMPILER_FASTPATH_OWNERS[2][2],
        "compiler_application_sha256": COMPILER_APPLICATION_OWNER[2],
        "previous_actual_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240, "shape_v2": 1112,
        },
        "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
        "combined_bridge_overlay_apply_count":
            complete.get("combined_bridge_overlay_apply_count", 0),
        "corrected_public_adapter_overlay_apply_count":
            complete.get("corrected_public_adapter_overlay_apply_count", 0),
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": len(operations),
        "actual_completed_phase_count": complete.get("phase_count"),
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_processes_started": 0,
        "candidate_workers_started": 0,
        "candidate_imports": 0,
        "native_libraries_loaded": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    payload = module.canonical(receipt)
    require(
        0 < len(payload) <= module.MAX_SOURCE_BYTES,
        "bound the complete independently durable V24 actual receipt",
    )
    recorded = kernel.write_fresh(
        directory / receipt_name, payload, synchronize=True,
    )
    receipt_sync = kernel.fsync_directory(directory)
    require(
        recorded.get("sha256") == digest(payload)
        and recorded.get("bytes") == len(payload)
        and recorded.get("exclusive_creation") is True
        and recorded.get("file_fsync_completed") is True
        and receipt_sync.get("completed") is True,
        "exclusively create and synchronize the genuine actual V24 receipt",
    )
    return {
        "schema": SCHEMA + "-published-build",
        "status": complete["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "build_status": complete["status"],
        "family": FAMILY,
        "label": label,
        "archive_relative": EVIDENCE_PATH + "/" + archive_name,
        "archive_sha256": saved["sha256"],
        "receipt_relative": EVIDENCE_PATH + "/" + receipt_name,
        "receipt_sha256": recorded["sha256"],
        "receipt_directory_fsync": receipt_sync,
        "failure_preserved": complete["status"] == "FAIL",
        "actual_compiler_process_count": len(operations),
        "actual_completed_phase_count": complete.get("phase_count"),
        "combined_bridge_sha256": VARIANT_SHA,
        "combined_bridge_bytes": VARIANT_BYTES,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "compiler_source_sha256": COMPILER_VARIANT_SHA,
        "compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "compiler_source_overlay_apply_count": compiler_overlay_count,
        "previous_actual_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_verified_passing_case_count": 15877,
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "performance": NOT_MEASURED,
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def publish_actual_root_provenance(
    module: object, ancestor: dict, base: dict, state: dict,
    options: dict, result: dict, original_before: dict,
    original_after: dict,
) -> dict:
    require(
        result.get("status") == "PASS"
        and result.get("build_status") == "PASS"
        and result.get("family") == FAMILY
        and result.get("label") == BUILD_LABEL
        and type(ROOT_CAPTURE) is dict
        and original_before == original_after
        and len(original_after) == 5,
        "publish root provenance only after genuine success and five restorations",
    )
    capture = ROOT_CAPTURE
    assert isinstance(capture, dict)
    require(
        capture.get("unique_process_count") == 28
        and capture.get("phase_count") == 2
        and type(capture.get("compiler_process_ids")) is list
        and len(capture["compiler_process_ids"]) == 28,
        "require all genuine independently observed compiler process IDs",
    )
    runtime = state.get("runtime_state")
    require(
        type(runtime) is dict and runtime.get("kernel") is not None,
        "retain only the genuine first-party durable build kernel",
    )
    kernel = runtime["kernel"]
    relative = result.get("receipt_relative")
    expected_relative = (
        EVIDENCE_PATH + "/" + actual_evidence_names(BUILD_LABEL, False)[1]
    )
    require(relative == expected_relative,
            "bind the uniquely named actually published V24 success receipt")
    receipt_hash = hash_pin(result.get("receipt_sha256"), "actual V24 receipt")
    observed = os.stat(ROOT + "/" + relative, follow_symlinks=False)
    require(
        stat.S_ISREG(observed.st_mode)
        and stat.S_IMODE(observed.st_mode) == 0o600
        and observed.st_dev == DEVICE
        and observed.st_uid == os.geteuid()
        and observed.st_nlink == 1
        and 0 < observed.st_size <= MAX_OWNER_BYTES,
        "authenticate the genuine independently published V24 success receipt",
    )
    receipt_owner = (
        "fresh_actual_v24_native_receipt", relative, receipt_hash,
        observed.st_size, observed.st_dev, observed.st_ino,
    )
    base["_ALLOWLIST"] = frozenset(
        set(base["_ALLOWLIST"]) | {ROOT + "/" + relative},
    )
    receipt = decode_actual_public(
        base, base["read_exact"](receipt_owner),
        "exclusive successful actual V24 native build receipt",
    )
    for field, expected in (
        ("schema", SCHEMA + "-durable-publication-receipt"),
        ("status", "PASS"),
        ("build_status", "PASS"),
        ("family", FAMILY),
        ("label", BUILD_LABEL),
        ("source_sha256", options["source_sha256"]),
        ("protocol_sha256", options["protocol_sha256"]),
        ("contract_sha256", options["contract_sha256"]),
        ("expected_actual_compiler_process_count", 28),
        ("actual_compiler_process_count", 28),
        ("actual_completed_phase_count", 2),
        ("combined_bridge_sha256", VARIANT_SHA),
        ("combined_bridge_bytes", VARIANT_BYTES),
        ("combined_bridge_overlay_apply_count", 2),
        ("corrected_public_adapter_sha256", ADAPTER_SHA),
        ("corrected_public_adapter_bytes", ADAPTER_BYTES),
        ("corrected_public_adapter_overlay_apply_count", 2),
        ("compiler_source_sha256", COMPILER_VARIANT_SHA),
        ("compiler_source_bytes", COMPILER_VARIANT_BYTES),
        ("compiler_source_overlay_apply_count", 2),
        ("compiler_freeze_source_sha256", COMPILER_FASTPATH_OWNERS[0][2]),
        ("compiler_freeze_protocol_sha256", COMPILER_FASTPATH_OWNERS[1][2]),
        ("compiler_freeze_contract_sha256", COMPILER_FASTPATH_OWNERS[2][2]),
        ("compiler_application_sha256", COMPILER_APPLICATION_OWNER[2]),
        ("previous_actual_v25_build_receipt_sha256", V25_BUILD_RECEIPT_SHA),
        ("previous_actual_v25_root_receipt_sha256", V25_ROOT_RECEIPT_SHA),
        ("latest_v25_original_campaign_receipt_sha256",
         V25_FAILURE_RECEIPT_SHA),
        ("latest_v25_candidate_status", "FAIL"),
        ("latest_v25_semantic_mismatch_count", 1352),
        ("latest_v25_verified_passing_case_count", 15877),
        ("latest_v24_original_campaign_receipt_sha256",
         PREVIOUS_FAILURE_RECEIPT_SHA),
        ("latest_v24_candidate_status", "FAIL"),
        ("latest_v24_semantic_mismatch_count", 1352),
        ("latest_v24_verified_passing_case_count", 15877),
        ("previous_actual_v24_native_build_receipt_sha256",
         PREVIOUS_BUILD_RECEIPT_SHA),
        ("previous_actual_v24_native_root_receipt_sha256",
         PREVIOUS_ROOT_RECEIPT_SHA),
        ("strict_runtime_guard_v4_contract_sha256",
         RUNTIME_GUARD_V4_OWNERS[2][2]),
        ("capture_clamp_source_sha256", CAPTURE_CLAMP_OWNERS[0][2]),
        ("capture_clamp_protocol_sha256", CAPTURE_CLAMP_OWNERS[1][2]),
        ("capture_clamp_contract_sha256", CAPTURE_CLAMP_OWNERS[2][2]),
        ("expanded_holdout_proposal_case_count",
         EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT),
        ("latest_v22_original_campaign_receipt_sha256",
         PUBLIC_OWNERS[17][2]),
        ("latest_v22_candidate_status", "FAIL"),
        ("latest_v22_verified_passing_case_count", 14725),
        ("latest_v22_observed_mismatch_lower_bound", 2018),
        ("latest_v22_global_semantic_mismatch_count", NOT_MEASURED),
        ("latest_v22_failing_worker_pid", 188),
        ("latest_v22_failing_worker_transient_physical_native_child_creation",
         NOT_MEASURED),
        ("complete_previous_v23_source_build_contract_sha256",
         BUILD_V23_OWNERS[2][2]),
        ("candidate_matching", "NOT RUN"),
        ("candidate_qualified", False),
        ("holdout", "NOT OPENED"),
    ):
        require(receipt.get(field) == expected,
                "reject incomplete actual V24 success evidence: " + field)
    for name in base["RUST_SOURCE_NAMES"]:
        base["read_exact"](base["OWNER_BY_NAME"][name])
    record = {
        "schema": SCHEMA + "-durable-root-provenance-receipt",
        "version": VERSION,
        "status": "PASS",
        "publication_pass_means":
            "DURABLE FIRST-PARTY NATIVE SOURCE BUILD ONLY",
        "family": FAMILY,
        "label": BUILD_LABEL,
        "source_sha256": options["source_sha256"],
        "protocol_sha256": options["protocol_sha256"],
        "contract_sha256": options["contract_sha256"],
        "previous_materialized_v23_build_source_sha256":
            BUILD_V23_OWNERS[0][2],
        "previous_materialized_v23_build_protocol_sha256":
            BUILD_V23_OWNERS[1][2],
        "previous_materialized_v23_build_contract_sha256":
            BUILD_V23_OWNERS[2][2],
        "previous_actual_v24_native_build_source_sha256":
            BUILD_V24_OWNERS[0][2],
        "previous_actual_v24_native_build_protocol_sha256":
            BUILD_V24_OWNERS[1][2],
        "previous_actual_v24_native_build_contract_sha256":
            BUILD_V24_OWNERS[2][2],
        "previous_actual_v24_native_build_receipt_sha256":
            PREVIOUS_BUILD_RECEIPT_SHA,
        "previous_actual_v24_native_root_receipt_sha256":
            PREVIOUS_ROOT_RECEIPT_SHA,
        "latest_v24_original_campaign_receipt_sha256":
            PREVIOUS_FAILURE_RECEIPT_SHA,
        "latest_v24_candidate_status": "FAIL",
        "latest_v24_semantic_mismatch_count": 1352,
        "latest_v24_verified_passing_case_count": 15877,
        "latest_v24_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240,
            "shape_v2": 1112,
        },
        "strict_runtime_guard_v4_source_sha256":
            RUNTIME_GUARD_V4_OWNERS[0][2],
        "strict_runtime_guard_v4_protocol_sha256":
            RUNTIME_GUARD_V4_OWNERS[1][2],
        "strict_runtime_guard_v4_contract_sha256":
            RUNTIME_GUARD_V4_OWNERS[2][2],
        "capture_clamp_source_sha256": CAPTURE_CLAMP_OWNERS[0][2],
        "capture_clamp_protocol_sha256": CAPTURE_CLAMP_OWNERS[1][2],
        "capture_clamp_contract_sha256": CAPTURE_CLAMP_OWNERS[2][2],
        "latest_v22_original_campaign_receipt_sha256": PUBLIC_OWNERS[17][2],
        "latest_v22_candidate_status": "FAIL",
        "latest_v22_verified_passing_case_count": 14725,
        "latest_v22_observed_mismatch_lower_bound": 2018,
        "latest_v22_fully_observed_suite_mismatch_counts": {
            "managed_v1": 42, "substitution_v2": 352, "shape_v2": 1624,
        },
        "latest_v22_global_semantic_mismatch_count": NOT_MEASURED,
        "latest_v22_failing_worker_pid": 188,
        "latest_v22_failing_worker_candidate_imports": 1,
        "latest_v22_failing_worker_native_library_loads": 2,
        "latest_v22_recorded_successfully_returned_child_interpreters": 0,
        "latest_v22_recorded_installed_child_guards": 0,
        "latest_v22_recorded_case_interpreter_exec_calls": 0,
        "latest_v22_transient_physical_native_child_creation": NOT_MEASURED,
        "latest_v22_remaining_interpreter_warnings": 1,
        "latest_v22_destructor_warnings": 16,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "supplemental_differential_case_count": 8244,
        "supplemental_counted_in_original_denominator": False,
        "corrected_reference_case_count": 6912,
        "corrected_reference_counted_in_original_denominator": False,
        "materialized_complete_bridge_sha256": VARIANT_SHA,
        "materialized_complete_bridge_bytes": VARIANT_BYTES,
        "compiler_source_sha256": COMPILER_VARIANT_SHA,
        "compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "compiler_source_overlay_apply_count": 2,
        "compiler_freeze_source_sha256": COMPILER_FASTPATH_OWNERS[0][2],
        "compiler_freeze_protocol_sha256": COMPILER_FASTPATH_OWNERS[1][2],
        "compiler_freeze_contract_sha256": COMPILER_FASTPATH_OWNERS[2][2],
        "compiler_application_sha256": COMPILER_APPLICATION_OWNER[2],
        "previous_actual_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
        "previous_actual_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_fully_observed_suite_mismatch_counts": {
            "substitution_v2": 240, "shape_v2": 1112,
        },
        "latest_v25_original_failure_archive_sha256_metadata_only":
            V25_FAILURE_ARCHIVE_SHA,
        "latest_v25_original_failure_archive_bytes_metadata_only": 3771743,
        "latest_v25_original_failure_archive_opened": False,
        "canonical_matching_source_sha256": MATCHER_SHA,
        "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
        "anchor_search_variant_used": False,
        "corrected_public_adapter_sha256": ADAPTER_SHA,
        "corrected_public_adapter_bytes": ADAPTER_BYTES,
        "canonical_build_status": "PASS",
        "canonical_build_archive_relative": receipt["archive_relative"],
        "canonical_build_archive_sha256": receipt["archive_sha256"],
        "canonical_build_archive_bytes": receipt["archive_bytes"],
        "canonical_build_archive_opened": False,
        "canonical_build_receipt_relative": relative,
        "canonical_build_receipt_sha256": receipt_hash,
        "canonical_build_receipt_bytes": observed.st_size,
        "canonical_build_receipt_device": observed.st_dev,
        "canonical_build_receipt_inode": observed.st_ino,
        "root": capture["root"],
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "actual_source_phase_count": 2,
        "actual_compiler_process_ids": capture["compiler_process_ids"],
        "bridge_overlay_apply_count": 2,
        "adapter_overlay_apply_count": 2,
        "compiler_overlay_apply_count": 2,
        "unchanged_source_owners_per_phase": 6,
        "cross_phase_complete_engine_elf_byte_identical": True,
        "cross_phase_complete_bridge_elf_byte_identical": True,
        "actual_reproduced_native_outputs": capture["native_outputs"],
        "original_source_identity_count": 9,
        "actual_original_runtime_target_count": 5,
        "actual_original_runtime_targets_before": original_before,
        "actual_original_runtime_targets_after": original_after,
        "all_original_source_identities_restored": True,
        "all_original_runtime_target_identities_restored": True,
        "candidate_correctness": NOT_MEASURED,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "candidate_workers_started": 0,
        "native_libraries_loaded": 0,
        "canonical_sources_modified": False,
        "tmp_directory_scanned": False,
        "historical_archives_opened": 0,
        "hidden_cases_read": 0,
        "clock_samples": 0,
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "expanded_holdout_proposal_case_count":
            EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    payload = (base["canonical"](record) + "\n").encode("ascii")
    require(0 < len(payload) <= MAX_OWNER_BYTES,
            "bound complete genuine V24 private-root provenance")
    root_relative = actual_root_receipt_name(BUILD_LABEL)
    saved = kernel.write_fresh(
        module.ROOT / EVIDENCE_PATH / root_relative,
        payload, synchronize=True,
    )
    synced = kernel.fsync_directory(module.ROOT / EVIDENCE_PATH)
    require(
        saved.get("sha256") == digest(payload)
        and saved.get("bytes") == len(payload)
        and saved.get("exclusive_creation") is True
        and saved.get("file_fsync_completed") is True
        and synced.get("completed") is True,
        "exclusively create and synchronize the genuine V24 root receipt",
    )
    return {
        **result,
        "root_provenance_status": "PASS",
        "root_provenance_receipt_relative":
            EVIDENCE_PATH + "/" + root_relative,
        "root_provenance_receipt_sha256": saved["sha256"],
        "root_provenance_receipt_bytes": saved["bytes"],
        "root_provenance_directory_fsync": synced,
        "actual_compiler_process_count": 28,
        "actual_private_phase_count": 2,
        "actual_compiler_process_ids": capture["compiler_process_ids"],
        "materialized_complete_bridge_sha256": VARIANT_SHA,
        "materialized_complete_bridge_bytes": VARIANT_BYTES,
        "compiler_source_sha256": COMPILER_VARIANT_SHA,
        "compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "compiler_source_overlay_apply_count": 2,
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "all_original_source_identities_restored": True,
        "all_original_runtime_target_identities_restored": True,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": NOT_MEASURED,
        "candidate_qualified": False,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "holdout": "NOT OPENED",
    }


def run_actual_build(options: dict) -> dict:
    global ROOT_CAPTURE
    require(
        type(options) is dict and options.get("mode") in ACTUAL_MODES
        and options.get("label") == BUILD_LABEL and ROOT_CAPTURE is None,
        "require one explicitly authorized actual V24 native source build",
    )
    original_before = snapshot_actual_original_targets()
    v22_raw, _v22_identity = read_actual_owner(PUBLIC_OWNERS[8])
    v22_name = "_rebar_v24_verified_actual_v22_bootstrap"
    require(v22_name not in sys.modules,
            "reject reused first-party V24 source-build bootstrap")
    v22 = types.ModuleType(v22_name)
    v22.__file__ = ROOT + "/" + PUBLIC_OWNERS[8][1]
    sys.modules[v22_name] = v22
    kernel_name = "_rebar_v24_verified_first_party_actual_native_v16"
    try:
        exec(compile(v22_raw, v22.__file__, "exec", dont_inherit=True),
             v22.__dict__)
        require(
            v22.SCHEMA
            == "rebar-phase2-owned-rust-capture-shape-semantics-source-build-v22"
            and v22.VERSION == 22 and v22.FAMILY == FAMILY
            and v22.PHASES == PHASES
            and v22.PROCESS_NAMES == PROCESS_NAMES
            and callable(v22.bootstrap_controllers),
            "load only the complete pushed first-party V22 operational hook",
        )
        _old_semantic, previous, parent, ancestor, base = (
            v22.bootstrap_controllers()
        )
        require(
            type(previous) is dict and type(parent) is dict
            and type(ancestor) is dict and type(base) is dict
            and base.get("_WALL_ENABLED") is False
            and tuple(base.get("RUST_SOURCE_NAMES", ()))
            == (
                "cargo_lock", "cargo_manifest", "original_bridge",
                "rust_engine", "rust_newline", "rust_search",
                "rust_stack", "rust_unicode", "original_adapter",
            ),
            "reject an irreversible source gate or substituted build lineage",
        )
        additions = {ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL,
                     ROOT + "/" + CONTRACT}
        additions.update(ROOT + "/" + row[1] for row in STATIC_OWNERS)
        base["_ALLOWLIST"] = frozenset(
            set(base["_ALLOWLIST"]) | additions,
        )
        base["verify_future_phase_one_v4"](options)
        source_raw, source_info = base["read_self"](
            SOURCE, options["source_sha256"],
        )
        protocol_raw, protocol_info = base["read_self"](
            PROTOCOL, options["protocol_sha256"],
        )
        contract_raw, contract_info = base["read_self"](
            CONTRACT, options["contract_sha256"],
        )
        require(
            source_raw.endswith(b"\n")
            and not source_raw.endswith(b"\n\n")
            and protocol_raw.endswith(b"\n")
            and not protocol_raw.endswith(b"\n\n"),
            "authenticate each exact complete independently pinned V24 owner",
        )
        frozen = decode_actual_public(
            base, contract_raw, "complete caller-pinned V24 source contract",
        )
        originals = {
            row[0]: base["read_exact"](actual_base_row(row))
            for row in STATIC_OWNERS
        }
        previous_build = decode_actual_public(
            base, originals[BUILD_V23_OWNERS[2][0]],
            "complete previously committed V23 materialized build freeze",
        )
        actual_v24_build = decode_actual_public(
            base, originals[BUILD_V24_OWNERS[2][0]],
            "complete independently pinned preceding V24 source-build freeze",
        )
        actual_v24_campaign = decode_actual_public(
            base, originals[CAMPAIGN_V24_OWNERS[2][0]],
            "complete independently pinned preceding V24 candidate campaign",
        )
        actual_v24_guard = decode_actual_public(
            base, originals[RUNTIME_GUARD_V4_OWNERS[2][0]],
            "complete independently pinned strict operational V4 guard",
        )
        actual_v24_build_receipt = decode_actual_public(
            base, originals[V24_BUILD_RECEIPT_OWNER[0]],
            "complete independently pinned successful da4 V24 build receipt",
        )
        actual_v24_root_receipt = decode_actual_public(
            base, originals[V24_ROOT_RECEIPT_OWNER[0]],
            "complete independently pinned successful f211 V24 root receipt",
        )
        actual_v24_failure = decode_actual_public(
            base, originals[V24_FAILURE_RECEIPT_OWNER[0]],
            "complete independently pinned actual V24 FAIL-1352 receipt",
        )
        actual_clamp_contract = decode_actual_public(
            base, originals[CAPTURE_CLAMP_OWNERS[2][0]],
            "complete independently frozen and pushed capture-clamp contract",
        )
        actual_v25_contract = decode_actual_public(
            base, originals[BUILD_V25_OWNERS[2][0]],
            "complete independently successful V25 source-build freeze",
        )
        actual_v25_campaign = decode_actual_public(
            base, originals[CAMPAIGN_V25_OWNERS[2][0]],
            "complete independently frozen V25 original correctness campaign",
        )
        actual_v25_publication = decode_actual_public(
            base, originals[V25_BUILD_RECEIPT_OWNER[0]],
            "complete genuinely successful V25 publication",
        )
        actual_v25_failure = decode_actual_public(
            base, originals[V25_FAILURE_RECEIPT_OWNER[0]],
            "complete latest genuinely observed V25 original FAIL-1352",
        )
        actual_v25_root = decode_actual_public(
            base, originals[V25_ROOT_RECEIPT_OWNER[0]],
            "complete genuinely successful V25 root provenance",
        )
        actual_compiler_contract = decode_actual_public(
            base, originals[COMPILER_FASTPATH_OWNERS[2][0]],
            "complete independently frozen first-party compiler fast path",
        )
        actual_compiler_application = decode_actual_public(
            base, originals[COMPILER_APPLICATION_OWNER[0]],
            "complete exclusive applied compiler fast-path owner",
        )
        verify_previous_actual_v25(
            actual_v25_contract, actual_v25_publication, actual_v25_root,
        )
        verify_actual_v25_original_failure(
            actual_v25_campaign, actual_v25_failure,
        )
        verify_compiler_allocation_freeze(
            None, originals[COMPILER_FASTPATH_OWNERS[0][0]],
            actual_compiler_contract, actual_compiler_application,
            originals[CANONICAL_RUST_OWNERS[3][0]],
            originals[COMPILER_VARIANT_OWNER[0]],
        )
        verify_previous_actual_v24(
            actual_v24_build, actual_v24_campaign, actual_v24_guard,
            actual_v24_build_receipt, actual_v24_root_receipt,
            actual_v24_failure, originals[INPUT_VARIANT_OWNER[0]],
        )
        verify_capture_clamp_freeze(
            None, originals[CAPTURE_CLAMP_OWNERS[0][0]],
            actual_clamp_contract, actual_v24_failure,
            originals[INPUT_VARIANT_OWNER[0]], originals[VARIANT_OWNER[0]],
        )
        require(
            frozen.get("schema") == SCHEMA + "-source-freeze"
            and frozen.get("version") == VERSION
            and frozen.get("family") == FAMILY
            and frozen.get("source", {}).get("sha256")
            == options["source_sha256"]
            and frozen.get("protocol", {}).get("sha256")
            == options["protocol_sha256"]
            and frozen.get("immutable_complete_v23_materialized_source_build",
                           {}).get("complete_contract_sha256")
            == BUILD_V23_OWNERS[2][2]
            and frozen.get("immutable_complete_v23_materialized_source_build",
                           {}).get("complete_contract_authenticated") is True
            and frozen.get("immutable_complete_v23_materialized_source_build",
                           {}).get("complete_contract_field_count")
            == len(previous_build)
            and frozen.get("materialized_first_party_variant",
                           {}).get("complete_source_sha256") == VARIANT_SHA
            and frozen.get("materialized_first_party_variant",
                           {}).get("complete_source_bytes") == VARIANT_BYTES
            and frozen.get("materialized_first_party_variant", {}).get(
                "immutable_actual_v24_input_owner", {},
            ).get("sha256") == INPUT_VARIANT_SHA
            and frozen.get("immutable_complete_v24_actual_source_build", {}).get(
                "complete_contract_sha256",
            ) == BUILD_V24_OWNERS[2][2]
            and frozen.get("immutable_complete_v24_actual_source_build", {}).get(
                "complete_actual_build_receipt",
            ) == actual_v24_build_receipt
            and frozen.get("immutable_complete_v24_actual_source_build", {}).get(
                "complete_actual_root_receipt",
            ) == actual_v24_root_receipt
            and frozen.get("immutable_complete_v24_correctness_campaign", {}).get(
                "complete_frozen_source_contract",
            ) == actual_v24_campaign
            and frozen.get(
                "immutable_complete_v24_actual_candidate_failure", {},
            ).get("complete_receipt") == actual_v24_failure
            and frozen.get(
                "immutable_complete_v24_actual_candidate_failure", {},
            ).get("receipt_sha256") == PREVIOUS_FAILURE_RECEIPT_SHA
            and frozen.get(
                "immutable_complete_v24_actual_candidate_failure", {},
            ).get("candidate_status") == "FAIL"
            and frozen.get(
                "immutable_complete_v24_actual_candidate_failure", {},
            ).get("semantic_mismatch_count") == 1352
            and frozen.get("immutable_operational_runtime_guard_v4", {}).get(
                "complete_frozen_source_contract",
            ) == actual_v24_guard
            and frozen.get(
                "immutable_first_party_capture_clamp_transformer", {},
            ).get("complete_frozen_source_contract") == actual_clamp_contract
            and frozen.get(
                "immutable_first_party_capture_clamp_transformer", {},
            ).get("complete_contract_sha256") == CAPTURE_CLAMP_OWNERS[2][2]
            and frozen.get("source_only_effects", {}).get(
                "expanded_holdout_proposal_case_count",
            ) == EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT
            and frozen.get("immutable_genuine_v22_failure",
                           {}).get("receipt_sha256") == PUBLIC_OWNERS[17][2]
            and frozen.get("immutable_genuine_v22_failure",
                           {}).get("verified_passing_case_count") == 14725
            and frozen.get("immutable_genuine_v22_failure",
                           {}).get("fully_observed_mismatch_lower_bound")
            == 2018
            and frozen.get("immutable_genuine_v22_failure",
                           {}).get("global_semantic_mismatch_count")
            == NOT_MEASURED
            and frozen.get("immutable_genuine_v22_failure",
                           {}).get("transient_physical_native_child_creation")
            == NOT_MEASURED
            and frozen.get("immutable_complete_v25_actual_source_build", {}).get(
                "complete_frozen_source_contract",
            ) == actual_v25_contract
            and frozen.get("immutable_complete_v25_actual_source_build", {}).get(
                "complete_actual_publication",
            ) == actual_v25_publication
            and frozen.get("immutable_complete_v25_actual_source_build", {}).get(
                "complete_actual_root",
            ) == actual_v25_root
            and frozen.get(
                "immutable_complete_v25_original_correctness_campaign", {},
            ).get("complete_frozen_source_contract") == actual_v25_campaign
            and frozen.get(
                "immutable_complete_v25_original_correctness_campaign", {},
            ).get("complete_actual_failure_receipt") == actual_v25_failure
            and frozen.get(
                "immutable_complete_v25_original_correctness_campaign", {},
            ).get("actual_failure_receipt_sha256") == V25_FAILURE_RECEIPT_SHA
            and frozen.get(
                "immutable_complete_v25_original_correctness_campaign", {},
            ).get("candidate_status") == "FAIL"
            and frozen.get(
                "immutable_complete_v25_original_correctness_campaign", {},
            ).get("semantic_mismatch_count") == 1352
            and frozen.get("immutable_first_party_compiler_allocation_transformer",
                           {}).get("complete_frozen_source_contract")
            == actual_compiler_contract
            and frozen.get("immutable_first_party_compiler_allocation_transformer",
                           {}).get("complete_exclusive_application")
            == actual_compiler_application
            and frozen.get("materialized_first_party_compiler_source", {}).get(
                "materialized_source_sha256",
            ) == COMPILER_VARIANT_SHA
            and frozen.get("materialized_first_party_compiler_source", {}).get(
                "canonical_search_owner", {},
            ).get("sha256") == CANONICAL_RUST_OWNERS[5][2]
            and frozen.get("frozen_offline_dual_phase_build",
                           {}).get("label") == BUILD_LABEL
            and frozen.get("frozen_offline_dual_phase_build",
                           {}).get("required_actual_distinct_compiler_process_count")
            == 28
            and frozen.get("frozen_offline_dual_phase_build",
                           {}).get("external_cargo_dependency_count") == 0,
            "authenticate the entire pushed V24 context and all real V23 losses",
        )
        previous_failure = decode_actual_public(
            base, originals[PUBLIC_OWNERS[17][0]],
            "complete actual 96-field V22 failing-worker receipt",
        )
        require(
            len(previous_failure) == 96
            and frozen["immutable_genuine_v22_failure"]["complete_receipt"]
            == previous_failure,
            "preserve every field of the latest real original-campaign failure",
        )
        native_v9 = decode_actual_public(
            base, originals["native_v9_contract"],
            "complete actual first-party V9 offline kernel contract",
        )
        native_v16 = decode_actual_public(
            base, originals["native_v16_contract"],
            "complete actual first-party V16 native recorder contract",
        )
        adapter = decode_actual_public(
            base, originals["adapter_v3_contract"],
            "complete exact frozen first-party private adapter contract",
        )
        verify_native_documents(native_v9, native_v16, adapter)
        proof = verify_variant(
            types.SimpleNamespace(**_old_semantic),
            originals[A0_OWNER[0]],
            originals[VARIANT_OWNER[0]],
            originals["canonical_matching_engine"],
        )
        require(
            proof == frozen["materialized_first_party_variant"]["derivation"],
            "rederive the exact complete 1adb bridge before private compilation",
        )
        v21_context, v21_state = previous["collect_context"](
            parent, ancestor, base,
            v22.V21["source"][2],
            v22.V21["protocol"][2],
            v22.V21["contract"][2],
        )
        previous_state = v21_state.get("v18_state")
        require(
            v21_context.get("status") == "PASS"
            and type(previous_state) is dict
            and type(previous_state.get("originals")) is dict
            and len(previous_state["originals"]) == 9
            and type(previous_state.get("corrected_adapter")) is bytes
            and digest(previous_state["corrected_adapter"]) == ADAPTER_SHA
            and len(previous_state["corrected_adapter"]) == ADAPTER_BYTES
            and type(previous_state.get("low_level_v9_source")) is bytes,
            "retain genuine first-party original sources, adapter and V9 kernel",
        )
        raw = previous_state["owners"]["v16_builder"]
        owner = base["OWNER_BY_NAME"]["v16_builder"]
        require(
            type(raw) is bytes and digest(raw) == owner[2]
            and digest(raw) == NATIVE_SOURCE_OWNERS[3][2]
            and len(raw) == NATIVE_SOURCE_OWNERS[3][3]
            and kernel_name not in sys.modules,
            "execute only the genuinely pinned operational V16 compiler kernel",
        )
        module = types.ModuleType(kernel_name)
        module.__file__ = ROOT + "/" + owner[1]
        sys.modules[kernel_name] = module
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
        require(
            module.SCHEMA
            == "rebar-phase2-owned-rust-buffer-shape-source-build-v16"
            and module.VERSION == 16
            and module.FAMILY == FAMILY
            and module.PHASES == PHASES
            and module.PROCESS_NAMES == PROCESS_NAMES
            and module.ROOT_PREFIX == "rebar-phase2-native-build-v9-rust-"
            and callable(module.run_build)
            and callable(module.verify_reproduced_phases),
            "reject a dummy, external or substituted actual Rust build kernel",
        )
        module.SCHEMA = SCHEMA
        module.VERSION = VERSION
        module.SOURCE_PATH = SOURCE
        module.PROTOCOL_PATH = PROTOCOL
        module.CONTRACT_PATH = CONTRACT
        module.FINAL_GRAPH_VERSION = previous["GRAPH_VERSION"]
        module.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = previous["EVIDENCE_FLOOR"]
        module.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = previous["HISTORY_FLOOR"]
        module.COMBINED_VARIANT = module.Owner(
            VARIANT_OWNER[1], VARIANT_SHA, VARIANT_BYTES,
        )
        module.BUFFER_VARIANT = module.COMBINED_VARIANT
        module.BUFFER_FEATURE = tuple(
            module.Owner(
                base["OWNER_BY_NAME"][role][1],
                base["OWNER_BY_NAME"][role][2],
                base["OWNER_BY_NAME"][role][3],
            )
            for role in ("v2_repair", "v2_protocol", "v2_contract")
        )
        module.FINAL_GRAPH = tuple(
            module.Owner(row[1], row[2], row[3])
            for row in parent["GRAPH"].values()
        )
        state: dict[str, object] = {}
        context = {
            "schema": SCHEMA + "-verified-actual-build-context",
            "version": VERSION,
            "status": "PASS",
            "family": FAMILY,
            "source": source_info,
            "protocol": protocol_info,
            "contract": contract_info,
            "complete_frozen_v24_contract_sha256":
                options["contract_sha256"],
            "complete_previous_v23_build_contract_sha256":
                BUILD_V23_OWNERS[2][2],
            "previous_actual_v24_build_receipt_sha256":
                PREVIOUS_BUILD_RECEIPT_SHA,
            "previous_actual_v24_root_receipt_sha256":
                PREVIOUS_ROOT_RECEIPT_SHA,
            "latest_v24_original_failure_receipt_sha256":
                PREVIOUS_FAILURE_RECEIPT_SHA,
            "latest_v24_candidate_status": "FAIL",
            "latest_v24_semantic_mismatch_count": 1352,
            "latest_v24_verified_passing_case_count": 15877,
            "strict_runtime_guard_v4_contract_sha256":
                RUNTIME_GUARD_V4_OWNERS[2][2],
            "latest_v22_original_failure_receipt_sha256":
                PUBLIC_OWNERS[17][2],
            "latest_v22_verified_passing_case_count": 14725,
            "latest_v22_observed_mismatch_lower_bound": 2018,
            "latest_v22_global_semantic_mismatch_count": NOT_MEASURED,
            "first_party_canonical_rust_source_owner_count": 9,
            "external_cargo_dependency_count": 0,
            "compiler_source_sha256": COMPILER_VARIANT_SHA,
            "compiler_source_bytes": COMPILER_VARIANT_BYTES,
            "previous_actual_v25_build_receipt_sha256": V25_BUILD_RECEIPT_SHA,
            "previous_actual_v25_root_receipt_sha256": V25_ROOT_RECEIPT_SHA,
            "latest_v25_original_campaign_receipt_sha256":
                V25_FAILURE_RECEIPT_SHA,
            "latest_v25_candidate_status": "FAIL",
            "latest_v25_semantic_mismatch_count": 1352,
            "latest_v25_verified_passing_case_count": 15877,
            "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
            "candidate_matching": "NOT RUN",
            "candidate_correctness": NOT_MEASURED,
            "holdout": "NOT OPENED",
        }

        def verified_context(
            source_pin: str, protocol_pin: str, contract_pin: str,
        ) -> tuple:
            require(
                (source_pin, protocol_pin, contract_pin)
                == (
                    options["source_sha256"],
                    options["protocol_sha256"],
                    options["contract_sha256"],
                ),
                "reject substituted independently pinned V24 build authority",
            )
            runtime = {
                "originals": previous_state["originals"],
                "combined_bridge": originals[VARIANT_OWNER[0]],
                "corrected_adapter": previous_state["corrected_adapter"],
                "low_level_v9_source":
                    previous_state["low_level_v9_source"],
            }
            state["runtime_state"] = runtime
            return context, runtime


        canonical_expected_owner = module.expected_source_owner

        def compiler_expected_owner(path: str) -> tuple[str, int]:
            if path == CANONICAL_RUST_OWNERS[3][1]:
                return COMPILER_VARIANT_SHA, COMPILER_VARIANT_BYTES
            return canonical_expected_owner(path)

        module.expected_source_owner = compiler_expected_owner

        def compiler_private_snapshot(
            workdir: str, family: str, phase: str,
            canonical_originals: dict[str, bytes],
        ) -> dict[str, dict]:
            active = module._ACTIVE
            require(
                type(active) is dict and family == FAMILY and phase in PHASES
                and type(canonical_originals) is dict
                and set(canonical_originals)
                == {item.path for item in module.RUST_OWNERS}
                and (workdir, phase) not in module._APPLIED_PHASES,
                "require one uniquely authorized fresh compiler-overlay phase",
            )
            module.checked_workdir(workdir)
            kernel = active["kernel"]
            low_level = active["v9"]
            paths = low_level.phase_paths(workdir, family, phase)
            for peer in PHASES:
                sibling = low_level.phase_paths(workdir, family, peer)
                for folder in (
                    sibling["base"], sibling["source"],
                    sibling["source"] / "candidates",
                    sibling["source"] / "candidates/rust",
                ):
                    observed = os.lstat(folder)
                    require(
                        stat.S_ISDIR(observed.st_mode)
                        and stat.S_IMODE(observed.st_mode) == 0o700
                        and observed.st_uid == os.geteuid(),
                        "require independent, owner-only compiler-source phases",
                    )
            for item in module.RUST_OWNERS:
                value = canonical_originals.get(item.path)
                require(
                    type(value) is bytes and len(value) == item.size
                    and digest(value) == item.sha256,
                    "retain the exact canonical original owner: " + item.path,
                )
            overlay_paths = {
                module.BRIDGE_PATH,
                module.PUBLIC_PATH,
                CANONICAL_RUST_OWNERS[3][1],
            }
            rows: dict[str, dict] = {}
            for item in sorted(module.RUST_OWNERS, key=lambda owner: owner.path):
                if item.path in overlay_paths:
                    continue
                destination = paths["source"] / item.path
                kernel.mkdir_private(destination.parent)
                recorded = kernel.write_fresh(
                    destination, canonical_originals[item.path],
                    synchronize=False,
                )
                recorded["path"] = low_level.sanitized(
                    recorded["path"], workdir, family,
                )
                rows[item.path] = recorded
            require(
                len(rows) == 6,
                "preserve exactly six unchanged independent canonical sources",
            )
            for path, payload, expected_hash, expected_size, role in (
                (
                    module.BRIDGE_PATH, active["combined_bridge"],
                    VARIANT_SHA, VARIANT_BYTES, "safe-capture-clamp-bridge",
                ),
                (
                    module.PUBLIC_PATH, active["corrected_adapter"],
                    ADAPTER_SHA, ADAPTER_BYTES, "corrected-public-adapter",
                ),
                (
                    CANONICAL_RUST_OWNERS[3][1],
                    originals[COMPILER_VARIANT_OWNER[0]],
                    COMPILER_VARIANT_SHA, COMPILER_VARIANT_BYTES,
                    "first-party-compiler-allocation-fastpath",
                ),
            ):
                require(
                    type(payload) is bytes and digest(payload) == expected_hash
                    and len(payload) == expected_size,
                    "authenticate every complete exclusive private source overlay",
                )
                destination = paths["source"] / path
                kernel.mkdir_private(destination.parent)
                published = kernel.write_fresh(
                    destination, payload, synchronize=True,
                )
                observed, verified = kernel.authenticate_file(
                    destination, expected=expected_hash,
                    maximum=module.MAX_SOURCE_BYTES,
                    exact_size=expected_size, capture=True,
                )
                require(
                    type(verified) is bytes and verified == payload
                    and published.get("sha256") == expected_hash
                    and published.get("bytes") == expected_size
                    and published.get("device") == observed.get("device")
                    and published.get("inode") == observed.get("inode")
                    and stat.S_IMODE(os.lstat(destination).st_mode) == 0o600,
                    "prove exclusive no-follow synchronized compiler overlay",
                )
                rows[path] = {
                    "path": low_level.sanitized(
                        observed["path"], workdir, family,
                    ),
                    "sha256": observed["sha256"],
                    "bytes": observed["size_bytes"],
                    "device": observed["device"],
                    "inode": observed["inode"],
                    "exclusive_creation": True,
                    "same_inode_readback_verified": True,
                    "file_fsync_completed": True,
                    "source_overlay": {
                        "status": "PASS", "phase": phase, "role": role,
                        "source_apply_count": 1,
                        "derived_sha256": expected_hash,
                        "derived_source_sha256": expected_hash,
                        "derived_bytes": expected_size,
                        "derived_source_bytes": expected_size,
                        "candidate_original_modified": False,
                        "canonical_candidate_modified": False,
                    },
                }
            require(
                set(rows) == {item.path for item in module.RUST_OWNERS}
                and sum(
                    1 for value in rows.values() if "source_overlay" in value
                ) == 3,
                "close exactly six original owners and three exclusive overlays",
            )
            for item in module.RUST_OWNERS:
                module.read_owner(item)
            module._APPLIED_PHASES.add((workdir, phase))
            return rows

        module.copy_combined_snapshot = compiler_private_snapshot

        actual_verifier = module.verify_reproduced_phases

        def verify_actual_phases(
            low_level: object, kernel: object, workdir: str,
            phases: list, steps: list,
        ) -> dict:
            global ROOT_CAPTURE
            require(
                ROOT_CAPTURE is None and type(steps) is list
                and len(steps) == 28,
                "require exactly 28 real independently spawned V24 processes",
            )
            process_ids: set[int] = set()
            for index, operation in enumerate(steps):
                expected_phase = PHASES[index // len(PROCESS_NAMES)]
                require(
                    type(operation) is dict
                    and operation.get("name")
                    == PROCESS_NAMES[index % len(PROCESS_NAMES)]
                    and (
                        "phase" not in operation
                        or operation.get("phase") == expected_phase
                    )
                    and type(operation.get("pid")) is int
                    and operation["pid"] > 0
                    and operation["pid"] not in process_ids
                    and operation.get("exit_status") == 0
                    and operation.get("working_directory")
                    == "<FRESH_PRIVATE_TMP>/" + expected_phase,
                    "reject a missing, duplicated or failed real V24 build role",
                )
                process_ids.add(operation["pid"])
            descriptor, root = ancestor["capture_root_descriptor"](
                low_level, workdir, phases,
            )
            try:
                real_proof = actual_verifier(
                    low_level, kernel, workdir, phases, steps,
                )
                require(
                    type(real_proof) is dict
                    and real_proof.get("status") == "PASS"
                    and real_proof.get("independent_fresh_phase_count") == 2
                    and real_proof.get("unique_process_count") == 28
                    and real_proof.get("combined_bridge_overlay_count") == 2
                    and real_proof.get(
                        "corrected_public_adapter_overlay_count",
                    ) == 2
                    and real_proof.get("combined_bridge_sha256") == VARIANT_SHA
                    and real_proof.get("combined_bridge_bytes") == VARIANT_BYTES
                    and real_proof.get("corrected_public_adapter_sha256")
                    == ADAPTER_SHA
                    and real_proof.get("byte_identical") is True
                    and real_proof.get("native_libraries_loaded") == 0
                    and type(real_proof.get("native_outputs")) is dict
                    and set(real_proof["native_outputs"])
                    == {"engine", "bridge"}
                    and type(real_proof["native_outputs"].get("engine", {}).get(
                        "sha256",
                    )) is str
                    and real_proof["native_outputs"]["engine"]["sha256"]
                    != PREVIOUS_ENGINE_SHA,
                    "require two independently built byte-identical actual ELF files",
                )
                compiler_count = 0
                for index, phase in enumerate(phases):
                    rows = phase.get("fresh_source_owners")
                    require(type(rows) is dict and len(rows) == 9,
                            "retain all nine independent private source owners")
                    compiler = rows.get(CANONICAL_RUST_OWNERS[3][1])
                    require(type(compiler) is dict
                            and compiler.get("sha256") == COMPILER_VARIANT_SHA
                            and compiler.get("bytes") == COMPILER_VARIANT_BYTES,
                            "reject missing or changed private compiler source")
                    overlay = compiler.get("source_overlay")
                    require(type(overlay) is dict
                            and overlay.get("status") == "PASS"
                            and overlay.get("phase") == PHASES[index]
                            and overlay.get("source_apply_count") == 1
                            and overlay.get("derived_sha256")
                            == COMPILER_VARIANT_SHA
                            and overlay.get("derived_bytes")
                            == COMPILER_VARIANT_BYTES
                            and sum(1 for value in rows.values()
                                    if "source_overlay" in value) == 3,
                            "require exactly three genuine per-phase overlays")
                    compiler_count += 1
                require(compiler_count == 2,
                        "require two authentic optimized Rust parser overlays")
                real_proof["compiler_source_overlay_count"] = compiler_count
                real_proof["compiler_source_sha256"] = COMPILER_VARIANT_SHA
                real_proof["compiler_source_bytes"] = COMPILER_VARIANT_BYTES
                real_proof["unchanged_source_owners_per_phase"] = 6
                real_proof["private_source_overlays_per_phase"] = 3
                real_proof["canonical_search_source_sha256"] = (
                    CANONICAL_RUST_OWNERS[5][2]
                )
                after = os.fstat(descriptor)
                named = os.stat(workdir, follow_symlinks=False)
                require(
                    stat.S_ISDIR(after.st_mode)
                    and stat.S_IMODE(after.st_mode) == 0o700
                    and after.st_uid == os.geteuid()
                    and (after.st_dev, after.st_ino)
                    == (root["device"], root["inode"])
                    and (named.st_dev, named.st_ino)
                    == (root["device"], root["inode"]),
                    "reject an exchanged, borrowed or unsafe private build root",
                )
                ROOT_CAPTURE = {
                    "root": root,
                    "phase_count": 2,
                    "unique_process_count": 28,
                    "compiler_process_ids": sorted(process_ids),
                    "native_outputs": real_proof["native_outputs"],
                    "original_reproducibility": "PASS",
                }
                return real_proof
            finally:
                os.close(descriptor)

        module.verify_frozen_context = verified_context
        module.verify_reproduced_phases = verify_actual_phases
        module.evidence_names = actual_evidence_names
        module.publish_build_report = (
            lambda kernel, report: publish_actual_build_report(
                module, kernel, report,
            )
        )
        target = (
            ROOT + "/" + EVIDENCE_PATH + "/"
            + actual_root_receipt_name(BUILD_LABEL)
        )
        try:
            os.lstat(target)
        except FileNotFoundError:
            pass
        else:
            raise BuildFreezeError(
                "reject a pre-existing actual V24 root provenance receipt",
            )

        class ActualOptions:
            pass

        forwarded = ActualOptions()
        for field in (
            "source_sha256", "protocol_sha256", "contract_sha256",
            "owned_source_sha256", "combined_bridge_sha256",
            "combined_bridge_bytes", "corrected_adapter_sha256",
            "corrected_adapter_bytes", "label",
        ):
            setattr(forwarded, field, options[field])
        result = module.run_build(forwarded)
        require(
            type(result) is dict and result.get("family") == FAMILY,
            "publish only a genuine actual first-party V24 build result",
        )
        original_after = snapshot_actual_original_targets()
        require(
            original_before == original_after,
            "restore all five original source, adapter and native identities",
        )
        if result.get("status") != "PASS":
            require(
                result.get("build_status") == "FAIL"
                and result.get("failure_preserved") is True,
                "durably preserve a genuine failed build without root claims",
            )
            return {
                **result,
                "root_provenance_status": "NOT CREATED",
                "all_original_runtime_target_identities_restored": True,
            }
        return publish_actual_root_provenance(
            module, ancestor, base, state, options, result,
            original_before, original_after,
        )
    finally:
        sys.modules.pop(kernel_name, None)
        sys.modules.pop(v22_name, None)


def parse_arguments(arguments: list[str]) -> dict:
    require(bool(arguments), "select one exact first-party V24 source mode")
    mode = arguments[0]
    require(
        mode in SOURCE_MODES + ACTUAL_MODES,
        "reject unknown first-party source or actual native-build modes",
    )
    if mode in ACTUAL_MODES:
        return {
            "mode": mode,
            "options": parse_actual_arguments(arguments),
        }
    required = ["--source-sha256", "--protocol-sha256"]
    if mode != "--render-contract":
        required.append("--contract-sha256")
    require(
        len(arguments) == 1 + 2 * len(required),
        "independently caller-pin every exact V24 source owner",
    )
    pins: dict[str, str] = {}
    for index in range(1, len(arguments), 2):
        flag, value = arguments[index], arguments[index + 1]
        require(
            flag in required and flag not in pins,
            "reject repeated or unowned V24 source authority",
        )
        pins[flag] = hash_pin(value, flag)
    require(
        set(pins) == set(required),
        "reject missing independently pinned V24 source authority",
    )
    return {"mode": mode, "pins": pins}


def main(arguments: list[str] | None = None) -> int:
    require(
        sys.implementation.name == "cpython"
        and tuple(sys.version_info[:3]) == (3, 14, 6)
        and sys.executable == PYTHON
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode is True,
        "require exact independently pinned CPython 3.14.6 with -I -B -S",
    )
    no_matching_imports()
    choice = parse_arguments(
        list(sys.argv[1:] if arguments is None else arguments),
    )
    if choice["mode"] in ACTUAL_MODES:
        result = run_actual_build(choice["options"])
        import json
        sys.stdout.write(
            json.dumps(
                result, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            ) + "\n",
        )
        sys.stdout.flush()
        return 0

    wall = FirstPartySourceWall()
    wall.install()
    frozen, state = load_context(
        wall, choice["pins"], choice["mode"] == "--render-contract",
    )
    capture = state["capture"]
    semantic = state["semantic"]
    if choice["mode"] == "--render-contract":
        sys.stdout.buffer.write(capture.canonical_document(semantic, frozen))
        sys.stdout.buffer.flush()
        return 0

    checks = (
        self_test(wall, frozen, state)
        if choice["mode"] == "--self-test" else []
    )
    result = {
        "schema": SCHEMA + "-source-only-gate",
        "status": "PASS",
        "version": VERSION,
        "mode": choice["mode"].removeprefix("--"),
        "source_sha256": choice["pins"]["--source-sha256"],
        "protocol_sha256": choice["pins"]["--protocol-sha256"],
        "contract_sha256": choice["pins"]["--contract-sha256"],
        "public_source_wall_installed_before_predecessor": wall.installed,
        "public_source_wall_live_descriptors": len(wall.live),
        "authenticated_static_first_party_owner_count": len(STATIC_OWNERS),
        "authenticated_canonical_rust_source_owner_count": 9,
        "canonical_original_sources_modified": False,
        "canonical_native_binary_files_opened": 0,
        "canonical_native_metadata_probes": 0,
        "materialized_variant_path": VARIANT_OWNER[1],
        "materialized_variant_sha256": VARIANT_SHA,
        "materialized_variant_bytes": VARIANT_BYTES,
        "materialized_variant_device": DEVICE,
        "materialized_variant_inode": VARIANT_OWNER[4],
        "materialized_variant_mode": "0600",
        "materialized_variant_uid": os.geteuid(),
        "materialized_variant_nlink": 1,
        "immutable_actual_v24_input_bridge_sha256": INPUT_VARIANT_SHA,
        "immutable_actual_v24_input_bridge_bytes": INPUT_VARIANT_BYTES,
        "actual_v24_complete_failure_receipt_sha256":
            PREVIOUS_FAILURE_RECEIPT_SHA,
        "actual_v24_candidate_status": "FAIL",
        "actual_v24_semantic_mismatch_count": 1352,
        "actual_v24_verified_passing_case_count": 15877,
        "actual_v24_completed_suite_count": 13,
        "actual_v24_substitution_mismatch_count": 240,
        "actual_v24_shape_mismatch_count": 1112,
        "actual_v24_build_receipt_sha256": PREVIOUS_BUILD_RECEIPT_SHA,
        "actual_v24_root_receipt_sha256": PREVIOUS_ROOT_RECEIPT_SHA,
        "actual_v24_build_status": "PASS",
        "actual_v24_compiler_process_count": 28,
        "runtime_guard_v4_source_sha256": RUNTIME_GUARD_V4_OWNERS[0][2],
        "runtime_guard_v4_protocol_sha256": RUNTIME_GUARD_V4_OWNERS[1][2],
        "runtime_guard_v4_contract_sha256": RUNTIME_GUARD_V4_OWNERS[2][2],
        "capture_clamp_source_sha256": CAPTURE_CLAMP_OWNERS[0][2],
        "capture_clamp_protocol_sha256": CAPTURE_CLAMP_OWNERS[1][2],
        "capture_clamp_contract_sha256": CAPTURE_CLAMP_OWNERS[2][2],
        "capture_clamp_synthetic_bounds_case_count": 4800,
        "capture_clamp_synthetic_alias_case_count": 50,
        "expanded_holdout_proposal_sha256_metadata_only":
            EXPANDED_HOLDOUT_PROPOSAL_SHA,
        "actual_a0_base_sha256": A0_SHA,
        "actual_a0_base_bytes": 179520,
        "exact_outer_length_blocks_removed": 1,
        "exact_outer_length_bytes_removed": 660,
        "replacement_cache_byte_identical": True,
        "original_replacement_branch_bytes": 97,
        "known_failed_f9_guard_present": False,
        "captured_fast_path_lines": 17,
        "matching_engine_sha256": MATCHER_SHA,
        "matching_engine_changed": False,
        "materialized_compiler_source_path": COMPILER_VARIANT_OWNER[1],
        "materialized_compiler_source_sha256": COMPILER_VARIANT_SHA,
        "materialized_compiler_source_bytes": COMPILER_VARIANT_BYTES,
        "materialized_compiler_source_inode": COMPILER_VARIANT_OWNER[4],
        "compiler_fastpath_source_sha256": COMPILER_FASTPATH_OWNERS[0][2],
        "compiler_fastpath_protocol_sha256": COMPILER_FASTPATH_OWNERS[1][2],
        "compiler_fastpath_contract_sha256": COMPILER_FASTPATH_OWNERS[2][2],
        "compiler_fastpath_application_sha256": COMPILER_APPLICATION_OWNER[2],
        "compiler_synthetic_case_count": 960,
        "compiler_scanner_case_count": 42,
        "compiler_lifetime_control_count": 40,
        "canonical_search_source_sha256": CANONICAL_RUST_OWNERS[5][2],
        "anchor_search_variant_used": False,
        "successful_previous_v25_source_sha256": BUILD_V25_OWNERS[0][2],
        "successful_previous_v25_protocol_sha256": BUILD_V25_OWNERS[1][2],
        "successful_previous_v25_contract_sha256": BUILD_V25_OWNERS[2][2],
        "successful_previous_v25_publication_sha256": V25_BUILD_RECEIPT_SHA,
        "successful_previous_v25_root_sha256": V25_ROOT_RECEIPT_SHA,
        "latest_v25_original_campaign_source_sha256":
            CAMPAIGN_V25_OWNERS[0][2],
        "latest_v25_original_campaign_protocol_sha256":
            CAMPAIGN_V25_OWNERS[1][2],
        "latest_v25_original_campaign_contract_sha256":
            CAMPAIGN_V25_OWNERS[2][2],
        "latest_v25_original_campaign_receipt_sha256": V25_FAILURE_RECEIPT_SHA,
        "latest_v25_candidate_status": "FAIL",
        "latest_v25_semantic_mismatch_count": 1352,
        "latest_v25_verified_passing_case_count": 15877,
        "latest_v25_completed_suite_count": 13,
        "latest_v25_candidate_worker_count": 13,
        "latest_v25_substitution_mismatch_count": 240,
        "latest_v25_shape_mismatch_count": 1112,
        "latest_v25_infrastructure_failure_count": 0,
        "latest_v25_failure_archive_sha256_metadata_only":
            V25_FAILURE_ARCHIVE_SHA,
        "latest_v25_failure_archive_bytes_metadata_only": 3771743,
        "latest_v25_failure_archive_opened": False,
        "preserved_public_practice_case_count": 416,
        "preserved_public_practice_paired_row_count": 1664,
        "preserved_public_paired_raw_sha256": PUBLIC_PRACTICE_OWNERS[2][2],
        "operational_correctness_campaign_sha256": CAMPAIGN_V23_OWNERS[2][2],
        "complete_v22_original_contract_field_count": 435,
        "complete_v21_inherited_contract_field_count": 402,
        "complete_actual_v22_failure_receipt_field_count": 96,
        "actual_v22_failure_receipt_sha256": PUBLIC_OWNERS[17][2],
        "actual_v22_candidate_status": "FAIL",
        "actual_v22_verified_passing_case_count": 14725,
        "actual_v22_observed_mismatch_lower_bound": 2018,
        "actual_v22_global_semantic_mismatch_count": NOT_MEASURED,
        "actual_v22_failing_worker_pid": 188,
        "actual_v22_failing_worker_candidate_imports": 1,
        "actual_v22_failing_worker_native_library_loads": 2,
        "actual_v22_recorded_successfully_returned_child_interpreters": 0,
        "actual_v22_recorded_installed_child_guards": 0,
        "actual_v22_recorded_child_case_interpreter_exec_calls": 0,
        "actual_v22_transient_physical_native_child_creation": NOT_MEASURED,
        "actual_v22_remaining_interpreter_warnings": 1,
        "actual_v22_destructor_warnings": 16,
        "original_case_execution_denominator": 31237,
        "original_suite_count": 13,
        "named_private_waiver_count": 13,
        "separate_supplemental_differential_case_count": 8244,
        "separate_corrected_reference_case_count": 6912,
        "supplemental_counted_in_original_denominator": False,
        "reference_counted_in_original_denominator": False,
        "absolute_rustc": RUSTC,
        "absolute_cargo": CARGO,
        "pinned_rust_toolchain_version": "1.95.0",
        "external_cargo_dependency_count": 0,
        "future_phase_count": 2,
        "future_required_distinct_compiler_process_count": 28,
        "actual_compiler_process_count": 0,
        "candidate_imports": 0,
        "candidate_workers_started": 0,
        "reference_workers_started": 0,
        "compiler_processes_started": 0,
        "native_libraries_loaded": 0,
        "private_roots_created": 0,
        "private_roots_opened": 0,
        "archive_opens": 0,
        "hidden_cases_read": 0,
        "holdout_cases_opened": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "network_requests": 0,
        "hostile_control_count": len(checks),
        "hostile_controls": checks,
        "physically_blocked_effects": dict(wall.blocked),
        "native_engine_sha256": NOT_MEASURED,
        "native_bridge_sha256": NOT_MEASURED,
        "native_build_receipt_sha256": NOT_MEASURED,
        "native_root_receipt_sha256": NOT_MEASURED,
        "native_build": "NOT RUN",
        "actual_build_modes": {
            "run": "IMPLEMENTED; NOT RUN",
            "build": "IMPLEMENTED; NOT RUN",
        },
        "previous_materialized_v23_build_source_sha256":
            BUILD_V23_OWNERS[0][2],
        "previous_materialized_v23_build_protocol_sha256":
            BUILD_V23_OWNERS[1][2],
        "previous_materialized_v23_build_contract_sha256":
            BUILD_V23_OWNERS[2][2],
        "candidate_matching": "NOT RUN",
        "candidate_correctness": NOT_MEASURED,
        "runtime_non_delegation": "NOT ESTABLISHED",
        "expanded_holdout_proposal_case_count":
            EXPANDED_HOLDOUT_PROPOSAL_CASE_COUNT,
        "expanded_holdout_cases": "NOT FROZEN; NOT GENERATED; NOT OPENED",
        "holdout": "NOT OPENED",
        "performance": NOT_MEASURED,
        "memory": NOT_MEASURED,
        "confidence_intervals": NOT_MEASURED,
        "undefined_behavior": NOT_MEASURED,
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    sys.stdout.buffer.write(capture.canonical_document(semantic, result))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildFreezeError as error:
        sys.stderr.write("V27 native source-build rejected: " + str(error) + "\n")
        raise SystemExit(2)
