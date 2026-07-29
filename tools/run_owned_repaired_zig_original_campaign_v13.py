#!/usr/bin/env python3
"""Freeze a V3-guarded first-party Zig lifetime original campaign."""

from __future__ import annotations

import ast
import builtins
import collections
import hashlib
import importlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SELF = "tools/run_owned_repaired_zig_original_campaign_v13.py"
PROTOCOL = "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V13.md"
CONTRACT = "oracle/phase2/repaired-zig-original-campaign-v13.json"
SCHEMA = "rebar-owned-repaired-zig-original-campaign-v13"
FAMILY = "zig"
LABEL = "phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13"
BUILD_LABEL = "phase2-v13-zig-scanner-phrase-v4"
DEVICE = 2064
PRIVATE_DEVICE = 2049
MAX_BYTES = 8 * 1024 * 1024
MAX_ACTUAL_WORKER_JSON_BYTES = 64 * 1024 * 1024
IMMUTABLE_PRODUCER_JSON_BYTES = 4 * 1024 * 1024
WORKER_UNICODE_TAG = "\x00rebar-zig-v12-surrogate-string"
WORKER_MAPPING_TAG = "\x00rebar-zig-v12-escaped-mapping"
WORKER_RESERVED_TAGS = frozenset({
    WORKER_UNICODE_TAG,
    WORKER_MAPPING_TAG,
})
PREDECESSOR_V10 = (
    (
        "tools/run_owned_repaired_zig_original_campaign_v10.py",
        "514c00a001c78bded833e6752f995986d3f7f1ac1535cddfb641fe0c5ec9ddd2",
        219644,
        431416,
    ),
    (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V10.md",
        "411c9c7cb62c4851ddcf58da8568f994420abcd2095cb1ec582203839c6f1e15",
        5943,
        525352,
    ),
    (
        "oracle/phase2/repaired-zig-original-campaign-v10.json",
        "5635b3e87a4b3158b107219c037fc13448dd92cc2296143024be825cfe1b4ffd",
        39991,
        525354,
    ),
    (
        "oracle/phase2/evidence/repaired-zig-original-campaign-v10-"
        "phase2-v13-zig-guard-clean-v1-original-p0-v10-"
        "failures-publication-receipt.json",
        "a13fad7e8e55af47235ddabd8f12d607a2c352b4d5b5d22f9422627381a10da7",
        89102,
        525391,
    ),
)
V10_SURROGATE_WORKER_OUTPUTS = (
    ("managed_v1", 5387422),
    ("substitution_v2", 14400358),
    ("public_surface_v19", 2859729),
)
V10_GENUINE_SEMANTIC_MISMATCHES = (
    ("scanner_verbose_v1", 620),
    ("public_types_v1", 248),
    ("shape_v2", 672),
)
DIRECT_GATE_SOURCE = (
    "tools/run_frozen_p0_candidate_v1.py",
    "c8378cd59a3b4dfaf75609c5b06f5a5ec20114d428e8e06ccc0f12ceec2076b8",
    104772,
    432295,
)
DIRECT_CORE_SOURCE = (
    "tools/independent_public_contract_v3.py",
    "9a831571c81e542d7d43ae56aea271f8e6c69550173d97ae1c9f8213eef40bf3",
    91039,
    430402,
)
PUBLIC_SURFACE_SOURCE = (
    "tools/python_re_public_surface_oracle_stage19.py",
    "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e",
    199366,
    430521,
)
PUBLIC_SURFACE_MODULE = "tools.python_re_public_surface_oracle_stage19"
PUBLIC_SURFACE_SCHEMA = "rebar-python-re-cycle-safe-guarded-public-surface-v19"
PREDECESSOR_V9 = (
    (
        "tools/run_owned_repaired_zig_original_campaign_v9.py",
        "5c894208a3bab5358cc84dcbf4ebeb2c17c47a381b00698618e8e23a2e39d38d",
        177226,
        431275,
    ),
    (
        "oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V9.md",
        "61fc1547a9b36dbb0aac90315a5bdaec544e8d599cb73dd51436153e995440dc",
        4889,
        525196,
    ),
    (
        "oracle/phase2/repaired-zig-original-campaign-v9.json",
        "f1b651f3ca7a55ae16543301b4a31ef8e4ff8701318d06b25a94bf70cccf0fee",
        32064,
        525197,
    ),
    (
        "oracle/phase2/evidence/repaired-zig-original-campaign-v9-"
        "phase2-v13-zig-guard-clean-v1-original-p0-v9-"
        "failures-publication-receipt.json",
        "9df60f301c11e16231483b5444b246196f906ea7eb6072a2c227feeb0b6e8dc8",
        88186,
        525312,
    ),
)
V9_OVERSIZED_WORKER_OUTPUTS = (
    ("managed_v1", 5387357),
    ("scanner_verbose_v1", 4574867),
    ("public_types_v1", 15964980),
    ("substitution_v2", 14400293),
    ("shape_v2", 33063343),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768),
    ("managed_v1", 1024), ("scanner_verbose_v1", 2854),
    ("public_types_v1", 6912), ("substitution_v2", 5120),
    ("shape_v2", 10240), ("public_surface_v19", 1376),
    ("subinterpreter_v2", 128), ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
PROCESS_ROLES = (
    "readelf_version", "gcc_version", "zig_version", "build_zig_engine",
    "build_zig_bridge", "engine_dynamic", "engine_symbols",
    "engine_sections", "engine_notes", "bridge_dynamic", "bridge_symbols",
    "bridge_sections", "bridge_notes",
)
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044)
P0 = (
    ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
    ("oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 524385),
    ("oracle/phase1/P0-DIFFERENTIAL-FUZZ-REFERENCE-V3.md", "8d67e3f4162945a454d8945abac3880a9c42620a04c2332ac2adc52f013305b6", 3929, 525081),
    ("oracle/phase1/p0-differential-fuzz-reference-v3.json", "2bd17e82cedb55467aad59e360a61665c0f534a23e33c3d0cad440a6114182ff", 5288, 525082),
    ("oracle/phase1/evidence/differential-fuzz-reference-v3-cpython-3146-two-worker-8244-v3/two-independent-reference-result.json", "8377e9c526a487c2e8838d7b8ba74e595b42d069f572bf7ed29f926f82d5b096", 3658, 524707),
)
GRAPH = (
    ("tools/render_candidate_current_overview_v86.py", "49c529c7f8b695c501dd03f9d35056c2853c73fcd36425718d8bfceb599b1a7d", 75354, 431699),
    ("docs/evidence/candidate-current-overview-v86.inputs.json", "42c534652a350eada8704581ebf8aa52c77687b6904e9fb486f03c2f117cbe6c", 1345744, 430944),
    ("docs/evidence/candidate-current-overview-v86.json", "ed728687e919410e6e9dae22ad3c976aa900d7a857f85231aaa93d0fc674f7cc", 4128155, 431704),
    ("docs/evidence/candidate-current-overview-v86.svg", "4bbf196a48997dbee3ea6b966d9a4eefce860962861675ad202506f685a80e55", 6214, 431705),
)
EXPANDED_HOLDOUT_PROPOSAL = (
    ("tools/verify_expanded_sealed_holdout_v1.py", "3dd9abcbd7a87486186ee8da804de595e65d79020a3fe33413d0157dde4f3309", 27311, 428806),
    ("oracle/phase3/EXPANDED-SEALED-HOLDOUT-V1.md", "818f1636d87ae721912f04a3fc8294ac04a59dff4a272319aa29a393f52a4fd4", 13237, 524760),
    ("oracle/phase3/expanded-sealed-holdout-v1.json", "676aac4f48c9404f5253c89b692efde5c425170f8d9f152b4f85b3e2a5225a76", 6628, 524761),
)
HISTORICAL_HOLDOUT_PROPOSAL = (
    "docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md",
    "f7509c60065860d30aad7939dda76f53e1c9f6ebb9db5e1298d0881f63a016eb",
    9481,
    431040,
)
PRODUCER = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py", "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538", 102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md", "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4", 5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json", "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53", 21036, 524885),
)
GUARD_V1 = (
    ("tools/verify_owned_candidate_runtime_independence_v1.py",
     "c511d72053957aaebeafe23d57c7d5438c72c00307bcbfed167a776666d0baa9",
     35270, 431283),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V1.md",
     "7d0cd123f7306eb1468d65bf10ff224151752bc16d6e587576bb6a3ccb7a8795",
     3464, 524839),
    ("oracle/phase2/candidate-runtime-independence-v1.json",
     "a784f0bc315a4cb946c09d160ed00387becd7fec9585a1e488d48a6c0f63f2fe",
     3987, 524840),
)
GUARD_V2 = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py",
     "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a",
     67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md",
     "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c",
     4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json",
     "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473",
     7671, 524887),
)
GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v3.py",
     "03f051e428ee31bb671d8ced82f02d7a9fe3520f24191aba78d2e8a0697202c2",
     59765, 430856),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V3.md",
     "d3437b642d322ccccf12851981555cb596ff7f9c5a12e0a6a389d6b80b5a068a",
     5297, 525096),
    ("oracle/phase2/candidate-runtime-independence-v3.json",
     "31e9a5d2754b5b4b273d4fc30d6a27967e495b57684fdd1e9306bbac3b2caaa7",
     9157, 525114),
)
SCANNER = (
    ("tools/apply_owned_zig_scanner_phrase_source_repair_v4.py", "31dafa08a8f394a8803fa352dd31c806fdac7aa6ee9160e67f2d5f60b2736a63", 65425, 428967),
    ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V4.md", "e17a46e13652e2950171d84096a0bf812020c88168589c17e50e1bab187339cf", 6919, 524729),
    ("oracle/phase2/zig-scanner-phrase-source-repair-v4.json", "5c8f9a220bf93fc56e9d8054002ea4358323c23a9a951d3ce28201b59947b19c", 11500, 524730),
)
V13 = (
    ("tools/reproduce_owned_zig_scanner_phrase_source_build_v13.py", "673cb1a5a1b2b70d36e77032e01312fda2887828a8898900f1c91378fde8687e", 123672, 431366),
    ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-BUILD-V13.md", "b8c3622d64041386c6202f0d980632c9e03a8c90c08455d1c38a50260ae68a40", 8765, 524873),
    ("oracle/phase2/zig-scanner-phrase-source-build-v13.json", "6b0b918da55d55144c1384d915027f9ba360048c910a4225568abce6fd3efd15", 21331, 524874),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-phase2-v13-zig-scanner-phrase-v4-build-receipt.json", "8d86fd25025caf440937679a7893aa2d72308f86eccd577073dbe502a341725d", 170856, 525149),
    ("oracle/phase2/evidence/zig-scanner-phrase-source-build-v13-phase2-v13-zig-scanner-phrase-v4-private-root-receipt.json", "03f661f87c9a061cb1fd1af49041b1dc5e616449ed91feb0575a1f013fafb3c2", 74891, 525148),
)
HISTORY = ("oracle/phase2/evidence/repaired-zig-original-campaign-v3-zig-phase2-v12-zig-scanner-v2-original-p0-failures-publication-receipt.json", "40be94851ae23d8c4a9d2ac759d28231605247a499b0703e727c757d25b2fb96", 4111, 524696)
PARENT_ADAPTER = ("candidates/zig/variants/scanner_phrase_v4/zig_candidate.py", "0ab9f56b469df7939af8a221a4deac9351de2162960085ca7fa2d69179480e2b", 68530, 428966)
CLEAN_ADAPTER = ("candidates/zig/variants/scanner_phrase_guard_clean_v1/zig_candidate.py", "e8a023a388d94369d3eab38260390e853cd8c38394713aef49856875cfd4ac11", 67262, 429081)

LIFETIME_ADAPTER = (
    "candidates/zig/variants/scanner_phrase_guard_clean_lifetime_v1/"
    "zig_candidate.py",
    "e9e052fdd50bcec54145b828b1353cf082c6bc13869176486bcfa41d1624ab50",
    67294, 525010,
)
LIFETIME_FREEZE = (
    ("tools/apply_owned_zig_deallocator_lifetime_source_repair_v1.py",
     "2d2be05fb04d43c453b7e4cd47dc8f55542eeb06b18058c996751b7e8a476e4e",
     85494, 430556),
    ("oracle/phase2/ZIG-DEALLOCATOR-LIFETIME-SOURCE-REPAIR-V1.md",
     "88dbdad010617a1930bb7e701b8dca02078ab8b6310257bf7f404fc540f3a1bb",
     7910, 525011),
    ("oracle/phase2/zig-deallocator-lifetime-source-repair-v1.json",
     "2021cca12e9c04ab421dca4fd7cc81e23ffe3b649317eb184dba21e47c6aad4e",
     17782, 525014),
)
PREDECESSOR_V12 = (
    ("tools/run_owned_repaired_zig_original_campaign_v12.py",
     "329c8ac8c50b3f61fc176e07267f9771a3878167e9ab5eb9246e06cafac31cf8",
     251811, 430069),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V12.md",
     "10bf90c29b0f23759acb3ea30ae9b364f90a9937d9b41388095b839e5ff5f551",
     5361, 524830),
    ("oracle/phase2/repaired-zig-original-campaign-v12.json",
     "97a04675f4f8afc4a44061979a0a856bff2f5bb8cb9ed1381e6ee52168156b07",
     46081, 524831),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v12-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v12-"
     "failures-publication-receipt.json",
     "ce7605be25bbb71e1b06b65b9aa3f79cfd09b39f0ce5f076ed9d986f15ee8de9",
     77604, 524975),
)
PINNED_PYTHON_SHA256 = (
    "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
)
ACTUAL_PASSING_SUITES = (
    ("original_bounded_v5", 151),
    ("public_v3", 864),
    ("scanner_v3", 1024),
    ("buffer_v3", 768),
    ("managed_v1", 1024),
    ("pep688_v4", 264),
    ("threaded_pattern_v1", 512),
)
ACTUAL_SEMANTIC_FAILURES = (
    ("scanner_verbose_v1", 620),
    ("public_types_v1", 248),
    ("substitution_v2", 64),
    ("shape_v2", 672),
    ("public_surface_v19", 96),
)
ORIGINAL_DEALLOCATOR = (
    "    def __del__(self):\n"
    "        handle = getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            _zig_bridge.free(handle)\n"
    "            self._handle = None\n"
)
REPAIRED_DEALLOCATOR = (
    "    def __del__(self, _free=_zig_bridge.free, _getattr=getattr):\n"
    "        handle = _getattr(self, \"_handle\", None)\n"
    "        if handle:\n"
    "            self._handle = None\n"
    "            _free(handle)\n"
)
EXPECTED_PATTERN_SLOTS = (
    "pattern", "flags", "groups", "_groupindex", "_handle",
    "_literal", "_templates", "__weakref__",
)
REQUIRED_NATIVE_OWNER_FIELDS = frozenset((
    "absolute_path", "bytes", "device", "family", "file_name",
    "inode", "mode", "native_loaded", "nlink", "relative", "role",
    "sha256", "size_bytes", "uid",
))

ENGINE_SOURCE = ("candidates/zig/mini_regex.zig", "a917e7b1a06008be400e4c4a74b6caee5a552624dc46a7d67c932758f594ef28", 186915, 429377)
BRIDGE_SOURCE = ("candidates/zig/py_bridge.c", "67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b", 173026, 429075)
ORIGINAL_ADAPTER = ("candidates/zig_candidate.py", "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862", 68422, 429360)
NATIVE = {
    "engine": ("caeb5ee7f5f9035f85e3ea2eb1d11396a1ca27f3c15ba585d7bbad40d9a87071", 108888),
    "bridge": ("3dfd80e26773d83acfc83cba7f0df1b85a796ed0059aaa6d855ec0a3b5a93121", 133656),
}
ORIGINALS = {
    "engine": {"relative": "candidates/_zig_probe.so", "sha256": "b76eb6c7ecd60c1d221f6ddb822573a5f962641cf4e6f16da75d21561b104652", "bytes": 478432, "device": DEVICE, "inode": 431260, "mode": 0o700, "uid": 1000, "nlink": 1},
    "bridge": {"relative": "candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so", "sha256": "d8ac0da492d960716cbc74c25d7cb5027aea3fcfe2bf0a6fb2ec8e432345fb3b", "bytes": 134112, "device": DEVICE, "inode": 431274, "mode": 0o700, "uid": 1000, "nlink": 1},
    "adapter": {"relative": ORIGINAL_ADAPTER[0], "sha256": ORIGINAL_ADAPTER[1], "bytes": ORIGINAL_ADAPTER[2], "device": DEVICE, "inode": ORIGINAL_ADAPTER[3], "mode": 0o600, "uid": 1000, "nlink": 1},
}
ROLES = ("engine", "bridge", "adapter")
RESTORE = ("adapter", "bridge", "engine")
RECOVERY = "/tmp/rebar-phase2-repaired-zig-original-campaign-v13-phase2-v13-zig-guard-clean-lifetime-v1-original-p0-v13"
PREDECESSOR_V8 = (
    ("tools/run_owned_repaired_zig_original_campaign_v8.py",
     "33786ae8da0e7627dbcb19d3e3e2e1141f8d9dba73be1a24c11c2a950320db79",
     147869, 431137),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V8.md",
     "da85fd3ee6cc3abad5c147a236944d32a3ccd6b6d12d3da1357e91f23ed6895e",
     5024, 525185),
    ("oracle/phase2/repaired-zig-original-campaign-v8.json",
     "d557473051f1ab7d55915f85a74cf16575f14e47532a7e8bdc8fd7474e4f1cdd",
     28024, 525189),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v8-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v8-"
     "failures-publication-receipt.json",
     "2a5d0a13f5141edf56cdd9af5537ba615326b03d8187fda863ae2f5740499652",
     97667, 525215),
)
LEGACY_V4_SOURCE = (
    "tools/run_owned_six_family_original_p0_producer_v4.py",
    "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8",
    230782,
    431710,
)
ORIGINAL_HARNESS_SOURCE = (
    "tools/rust_original_cpython_suite_v1.py",
    "cf0267e3766fb849891d182e5b57ced569a0634831dd494d8135e703844b6c95",
    67175,
    430765,
)
FORBIDDEN_LEGACY_CTYPES_PROXY = (
    "class _RebarZigV9ForbiddenCtypes:\n"
    "    __slots__ = ()\n"
    "    def __getattribute__(self, name):\n"
    "        raise RuntimeError("
    "'V9 strictly forbids historical ctypes: ' + str(name))\n"
    "ctypes = _RebarZigV9ForbiddenCtypes()\n"
)

PREDECESSOR_V7 = (
    ("tools/run_owned_repaired_zig_original_campaign_v7.py",
     "068af44d35bc9ce49219cf6637b903d1cb1c7d1eb2cc04bd5eec35899efa540e",
     128515, 431115),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V7.md",
     "5344997fd7cc3cb02b118acc163d9694d3e47953ca5ee878bc47940c9a0ee70f",
     5550, 525145),
    ("oracle/phase2/repaired-zig-original-campaign-v7.json",
     "eda54fe33314ca44d96817e54f3847e2435656d9b7543a34cb2f380eee4d2550",
     24243, 525146),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v7-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v7-"
     "failures-publication-receipt.json",
     "b7e9091f24bde56dd67ecceacc3195e931916dffd7f7fd15c09e2bb301a365ab",
     47922, 525166),
)
REPOSITORY_ROOT_INODE = 31364017
REPOSITORY_ROOT_MODE = 0o775
CANDIDATE_NAMESPACE_INODE = 427975
CANDIDATE_NAMESPACE_MODE = 0o700

PREDECESSOR_V6 = (
    ("tools/run_owned_repaired_zig_original_campaign_v6.py",
     "200024fba683d8027b4ad59f0b3ebab63304104493c165f0c4549d4dba2bfb2e",
     101571, 430939),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V6.md",
     "013fac08c19c3721882196fe2550958871b738ba2a7f75c7268c8ea006bc250c",
     5276, 525002),
    ("oracle/phase2/repaired-zig-original-campaign-v6.json",
     "103a22716f101198f070c6c8b3c0a182b77d57eb160f2768998f078208333df4",
     21517, 525003),
    ("oracle/phase2/evidence/repaired-zig-original-campaign-v6-"
     "phase2-v13-zig-guard-clean-v1-original-p0-v6-"
     "failures-publication-receipt.json",
     "c04bab24727a44ee56f6fd0e38129c0504b48ece8ad3a1fa73639f5d89cc2d52",
     11417, 525106),
)
MAX_FAILURE_MESSAGE_BYTES = 4096
MAX_FAILURE_TRACEBACK_BYTES = 16384
MAX_FAILURE_TRACEBACK_FRAMES = 24
MAX_PUBLIC_STDERR_BYTES = 4096

PREDECESSOR_V5 = (
    ("tools/run_owned_repaired_zig_original_campaign_v5.py",
     "cc01b6743cde15bbcf4d2c8a5bf54f3d6a6cd1307de6e2295038d8edfb457b0e",
     89272, 430182),
    ("oracle/phase2/REPAIRED-ZIG-ORIGINAL-CAMPAIGN-V5.md",
     "eefba93b3d37659a5de32c6be7bf308ebef507e4ab6abe83fd4a6d4f7fa23c3f",
     8044, 524787),
    ("oracle/phase2/repaired-zig-original-campaign-v5.json",
     "c574ed19f870c5ae57505c980dbc8512971833dfab9f7cd3251f1a223ec1ad70",
     19190, 524788),
)
EXTERNAL_LOCPATH = "/tmp/rebar-official-locale-proof-0EdjeBJ1lS"
SUITE_TIMEOUT_SECONDS = 120
MAX_SERIAL_SUITE_TIMEOUT_SECONDS = 13 * SUITE_TIMEOUT_SECONDS

ZERO_KEYS = (
    "actual_candidate_imports", "actual_candidate_workers",
    "actual_reference_workers", "native_libraries_loaded",
    "native_activations", "private_roots_opened", "private_snapshots_opened",
    "matching_archives_opened", "matching_archives_inflated",
    "benchmark_files_opened", "holdout_files_opened", "clock_samples",
    "timing_trials_run", "compiler_processes_started",
    "candidate_processes_started", "network_requests", "files_written",
    "recovery_roots_created", "recovery_journals_created",
    "canonical_targets_modified", "subinterpreters_created",
    "subinterpreter_case_executions", "subinterpreter_guards_installed",
    "threads_started", "native_owner_preloads",
)


class CampaignError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise CampaignError(message)


def pin(value, label):
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value),
            "reject incomplete " + label + " SHA-256")
    return value


def digest(data):
    require(type(data) is bytes, "hash only actual complete bytes")
    return hashlib.sha256(data).hexdigest()


def owners(*, active=False):
    require(type(active) is bool, "reject invented owner activation")
    result = (
        GOAL,
        *P0,
        *EXPANDED_HOLDOUT_PROPOSAL,
        HISTORICAL_HOLDOUT_PROPOSAL,
        *PREDECESSOR_V12,
        *LIFETIME_FREEZE,
        DIRECT_GATE_SOURCE,
        DIRECT_CORE_SOURCE,
        PUBLIC_SURFACE_SOURCE,
        LEGACY_V4_SOURCE,
        ORIGINAL_HARNESS_SOURCE,
        *PRODUCER,
        *GUARD_V1,
        *GUARD_V2,
        *GUARD,
        *SCANNER,
        *V13,
        PARENT_ADAPTER,
        CLEAN_ADAPTER,
        LIFETIME_ADAPTER,
        ENGINE_SOURCE,
        BRIDGE_SOURCE,
    )
    # Canonical candidate roles belong exclusively to real activation/recovery.
    # No source-only context may open the current candidate or native targets.
    return result


def record(item):
    return {"path": item[0], "sha256": item[1], "bytes": item[2],
            "device": DEVICE, "inode": item[3], "mode": "0600",
            "nlink": 1}


REAL_OPEN = os.open
ACTIVE_WALL = None


def relative(path):
    require(type(path) is str and bool(path) and not path.startswith("/")
            and "\\" not in path and "\x00" not in path
            and all(p not in ("", ".", "..") for p in path.split("/")),
            "reject a noncanonical first-party source path")
    return path


def read_owner(item):
    require(type(item) is tuple and len(item) == 4
            and relative(item[0]) == item[0]
            and pin(item[1], item[0])
            and type(item[2]) is int and 0 < item[2] <= MAX_BYTES
            and type(item[3]) is int and item[3] > 0,
            "reject an incomplete independently frozen source owner")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(ROOT + "/" + item[0], flags)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode)
                and before.st_dev == DEVICE and before.st_ino == item[3]
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_size == item[2],
                "reject a substituted first-party owner: " + item[0])
        parts, left = [], before.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject a truncated owner: " + item[0])
            parts.append(data)
            left -= len(data)
        require(not os.read(fd, 1), "reject an extended owner: " + item[0])
        data = b"".join(parts)
        after = os.fstat(fd)
        require(digest(data) == item[1]
                and (before.st_dev, before.st_ino, before.st_size,
                     before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size,
                    after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
                "reject bytes changed during first-party verification")
        return data
    finally:
        os.close(fd)


def read_suite(path, expected):
    relative(path)
    pin(expected, path)
    if ACTIVE_WALL is not None:
        ACTIVE_WALL.allowed.add(ROOT + "/" + path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(ROOT + "/" + path, flags)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_dev == DEVICE
                and before.st_uid == os.geteuid() and before.st_nlink == 1
                and stat.S_IMODE(before.st_mode) == 0o600
                and 0 < before.st_size <= MAX_BYTES,
                "reject an unfrozen original-suite source")
        parts, left = [], before.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject a truncated original-suite source")
            parts.append(data)
            left -= len(data)
        require(not os.read(fd, 1) and digest(b"".join(parts)) == expected,
                "reject an altered immutable original-suite source: " + path)
    finally:
        os.close(fd)


def load(item, name):
    module = types.ModuleType(name)
    module.__file__ = ROOT + "/" + item[0]
    exec(compile(read_owner(item), module.__file__, "exec",
                 dont_inherit=True), module.__dict__)
    require(module.__name__ == name, "reject a replaced first-party module")
    return module


def clean():
    require(sys.executable == PYTHON
            and tuple(sys.version_info[:3]) == (3, 14, 6)
            and sys.flags.isolated == 1 and sys.dont_write_bytecode
            and "re" not in sys.modules and "_sre" not in sys.modules
            and not any(n == "candidates" or n.startswith("candidates.")
                        for n in sys.modules),
            "require clean, isolated pinned Python before candidate import")


def normalize(raw):
    require(len(raw) == PARENT_ADAPTER[2]
            and digest(raw) == PARENT_ADAPTER[1],
            "reject a changed actual V13 scanner adapter")
    text = raw.decode("utf-8")
    tree = ast.parse(text, filename=ROOT + "/" + PARENT_ADAPTER[0])
    imports = [n for n in tree.body
               if isinstance(n, ast.Import) and len(n.names) == 1
               and n.names[0].name == "ctypes"
               and n.names[0].asname is None]
    classes = [n for n in tree.body
               if isinstance(n, ast.ClassDef) and n.name == "_Native"]
    require(len(imports) == len(classes) == 1,
            "require the unique unused first-party loader")
    methods = [n for n in classes[0].body
               if isinstance(n, ast.FunctionDef) and n.name == "__init__"]
    compile_methods = [n for n in classes[0].body
                       if isinstance(n, ast.FunctionDef) and n.name == "compile"]
    require(len(methods) == len(compile_methods) == 1
            and len(methods[0].body) == 20,
            "reject a changed or incomplete first-party loader")
    all_ctypes = [n for n in ast.walk(tree)
                  if isinstance(n, ast.Name) and n.id == "ctypes"]
    local_ctypes = [n for n in ast.walk(methods[0])
                    if isinstance(n, ast.Name) and n.id == "ctypes"]
    require(bool(local_ctypes) and len(all_ctypes) == len(local_ctypes),
            "reject ctypes used in any actual compiler or matcher")
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line.encode("utf-8")))
    edits = ((offsets[imports[0].lineno - 1],
              offsets[imports[0].end_lineno], b""),
             (offsets[methods[0].body[0].lineno - 1],
              offsets[methods[0].body[-1].end_lineno], b"        pass\n"))
    normalized = raw
    for start, end, replacement in sorted(edits, reverse=True):
        require(0 <= start < end <= len(normalized),
                "reject a changed exact AST source span")
        normalized = normalized[:start] + replacement + normalized[end:]
    actual = ast.parse(normalized.decode("utf-8"))
    tree.body.remove(imports[0])
    methods[0].body = [ast.Pass()]
    bridge_calls = [n for n in ast.walk(actual)
                    if isinstance(n, ast.Attribute)
                    and isinstance(n.value, ast.Name)
                    and n.value.id == "_zig_bridge" and n.attr == "compile"]
    scanners = [n for n in actual.body
                if isinstance(n, ast.ClassDef) and n.name == "Scanner"]
    require(len(normalized) == CLEAN_ADAPTER[2]
            and digest(normalized) == CLEAN_ADAPTER[1]
            and ast.dump(tree, include_attributes=False)
            == ast.dump(actual, include_attributes=False)
            and not any(isinstance(n, ast.Name) and n.id == "ctypes"
                        for n in ast.walk(actual))
            and bool(bridge_calls) and len(scanners) == 1,
            "reject any changed Zig parser, compiler, matcher, or scanner")
    return normalized


class SourceWall:
    def __init__(self):
        self.allowed = {ROOT + "/" + item[0] for item in owners()}
        self.allowed |= {ROOT + "/" + SELF, ROOT + "/" + PROTOCOL,
                         ROOT + "/" + CONTRACT}
        self.saved = {}
        self.active = False
        self.denials = 0

    def deny(self, why):
        self.denials += 1
        raise CampaignError("source-only wall rejected " + why)

    def imported(self, name, globals=None, locals=None, fromlist=(), level=0):
        blocked = {"re", "_sre", "regex", "re2", "ctypes", "subprocess",
                   "socket", "threading", "multiprocessing", "gzip",
                   "json", "pathlib", "tempfile", "time", "unittest",
                   "concurrent", "_interpreters"}
        if type(name) is not str or name.split(".", 1)[0] in blocked \
                or name == "candidates" or name.startswith("candidates."):
            self.deny("matching, native-loader, process, or timing import")
        return self.saved["import"](name, globals, locals, fromlist, level)

    def opened(self, path, flags, mode=0o777, *, dir_fd=None):
        if dir_fd is not None or type(path) is not str \
                or path not in self.allowed \
                or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            self.deny("private, native, archive, holdout, or write open")
        return self.saved["open"](path, flags, mode)

    def blocked(self, *args, **kwargs):
        self.deny("mutation, process, native load, or network")

    def audit(self, event, args):
        if not self.active:
            return
        if event == "open":
            path = args[0] if args else None
            if type(path) is str and path not in self.allowed:
                self.deny("unlisted physical file: " + path)
        elif event.startswith(("ctypes.", "subprocess.", "socket.",
                               "os.exec", "os.spawn")) \
                or event in {"os.system", "os.fork", "os.posix_spawn",
                             "cpython.PyInterpreterState_New",
                             "_interpreters.create", "_interpreters.exec"}:
            self.deny("physical dynamic loader, subprocess, or network")

    def __enter__(self):
        global ACTIVE_WALL
        require(ACTIVE_WALL is None, "reject a reused source-only wall")
        self.saved["import"] = builtins.__import__
        self.saved["builtin_open"] = builtins.open
        self.saved["open"] = os.open
        builtins.__import__ = self.imported
        builtins.open = self.blocked
        os.open = self.opened
        for name in ("system", "popen", "fork", "mkdir", "makedirs",
                     "rename", "replace", "unlink", "remove", "rmdir",
                     "link", "symlink", "chdir", "putenv", "unsetenv",
                     "posix_spawn", "posix_spawnp"):
            if hasattr(os, name):
                self.saved["os." + name] = getattr(os, name)
                setattr(os, name, self.blocked)
        ACTIVE_WALL = self
        self.active = True
        sys.addaudithook(self.audit)
        return self

    def __exit__(self, kind, value, trace):
        global ACTIVE_WALL
        self.active = False
        ACTIVE_WALL = None
        builtins.__import__ = self.saved["import"]
        builtins.open = self.saved["builtin_open"]
        os.open = self.saved["open"]
        for key, previous in self.saved.items():
            if key.startswith("os."):
                setattr(os, key[3:], previous)
        return False


def validate_build(producer):
    receipt = producer.JsonReader(read_owner(V13[3])).parse()
    root = producer.JsonReader(read_owner(V13[4])).parse()
    require(type(receipt) is dict
            and receipt.get("schema")
            == "rebar-owned-zig-scanner-phrase-source-build-v13-plaintext-build-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("label") == BUILD_LABEL
            and receipt.get("family") == FAMILY
            and receipt.get("source_sha256") == V13[0][1]
            and receipt.get("protocol_sha256") == V13[1][1]
            and receipt.get("contract_sha256") == V13[2][1]
            and receipt.get("candidate_correctness") == "NOT MEASURED",
            "reject a fabricated V13 first-party source build")
    linked = receipt.get("private_root_receipt", {})
    require(type(linked) is dict and linked.get("path") == V13[4][0]
            and linked.get("sha256") == V13[4][1]
            and linked.get("bytes") == V13[4][2]
            and linked.get("device") == DEVICE
            and linked.get("inode") == V13[4][3]
            and linked.get("mode") == "0600"
            and root.get("schema")
            == "rebar-owned-zig-scanner-phrase-source-build-v13-private-root-receipt"
            and root.get("status") == "PASS"
            and root.get("label") == BUILD_LABEL
            and root.get("actual_process_count") == 26
            and root.get("phase_names") == ["reference-a", "reference-b"]
            and root.get("candidate_correctness") == "NOT MEASURED",
            "reject a substituted durable private-root receipt")
    actual = receipt.get("complete_actual_build", {})
    require(type(actual) is dict and actual.get("status") == "PASS"
            and actual.get("actual_process_count") == 26
            and actual.get("actual_source_snapshot_count") == 6
            and actual.get("corrected_adapter_sha256") == PARENT_ADAPTER[1]
            and actual.get("first_party_engine_source_sha256") == ENGINE_SOURCE[1]
            and actual.get("first_party_bridge_source_sha256") == BRIDGE_SOURCE[1]
            and actual.get("original_case_execution_denominator") == 31237
            and actual.get("original_suite_count") == 13
            and actual.get("original_named_private_waiver_count") == 13
            and actual.get("supplemental_reference_case_count") == 8244
            and actual.get("cross_family_engine_count") == 0
            and actual.get("external_regex_dependency_count") == 0
            and actual.get("stdlib_regex_engine_count") == 0
            and actual.get("candidate_matching") == "NOT RUN"
            and actual.get("candidate_qualified") is False
            and actual.get("candidate_workers_started") == 0
            and actual.get("holdout_files_opened") == 0
            and actual.get("benchmark_files_opened") == 0
            and actual.get("native_activations") == 0,
            "reject V13 matching claims, hidden access, or external engines")
    processes = actual.get("processes")
    require(type(processes) is list and len(processes) == 26
            and all(type(row.get("pid")) is int and row["pid"] > 0
                    and row.get("returncode") == 0 for row in processes)
            and len({row["pid"] for row in processes}) == 26
            and tuple((row.get("phase"), row.get("role")) for row in processes)
            == tuple((phase, role)
                     for phase in ("reference-a", "reference-b")
                     for role in PROCESS_ROLES),
            "require all 26 genuine distinct first-party build processes")
    phases, roots = actual.get("build_phases"), root.get("phases")
    require(type(phases) is list and type(roots) is list
            and len(phases) == len(roots) == 2
            and [x.get("name") for x in phases]
            == [x.get("name") for x in roots]
            == ["reference-a", "reference-b"],
            "reject missing independent V13 native build phases")
    source_ids, native_ids = set(), {"engine": set(), "bridge": set()}
    expected_sources = {
        "candidates/zig/mini_regex.zig": ENGINE_SOURCE,
        "candidates/zig/py_bridge.c": BRIDGE_SOURCE,
        "candidates/zig_candidate.py": PARENT_ADAPTER,
    }
    for phase, rooted in zip(phases, roots, strict=True):
        sources, root_sources = phase.get("source_snapshots"), rooted.get("source_snapshots")
        require(type(sources) is dict and type(root_sources) is dict
                and set(sources) == set(root_sources) == set(expected_sources),
                "reject an omitted genuine V13 source snapshot")
        for path, expected in expected_sources.items():
            owner = sources[path]
            require(owner == root_sources[path]
                    and owner.get("sha256") == expected[1]
                    and owner.get("bytes") == expected[2]
                    and owner.get("device") == PRIVATE_DEVICE
                    and owner.get("mode") == "0600"
                    and owner.get("uid") == os.geteuid()
                    and owner.get("nlink") == 1,
                    "reject crossed or fabricated V13 first-party source bytes")
            identity = (owner["device"], owner["inode"])
            require(identity not in source_ids, "reject shared V13 source inodes")
            source_ids.add(identity)
        for role, (expected_hash, expected_size) in NATIVE.items():
            output = phase.get("native_outputs", {}).get(role, {})
            rooted_output = rooted.get("native_outputs", {}).get(role, {})
            owner, audit = output.get("owner"), output.get("independence_audit")
            require(type(owner) is dict and owner == rooted_output.get("owner")
                    and owner.get("sha256") == expected_hash
                    and owner.get("bytes") == expected_size
                    and owner.get("device") == PRIVATE_DEVICE
                    and owner.get("mode") == "0700"
                    and owner.get("uid") == os.geteuid()
                    and owner.get("nlink") == 1
                    and type(audit) is dict and audit.get("role") == role
                    and audit.get("cross_family_engine_count") == 0
                    and audit.get("external_regex_dependency_count") == 0
                    and audit.get("stdlib_regex_engine_count") == 0
                    and audit.get("native_loader_dependency_count") == 0,
                    "reject a wrapped, borrowed, or substituted V13 native engine")
            ident = (owner["device"], owner["inode"])
            require(ident not in native_ids[role],
                    "reject a reused independent V13 native phase")
            native_ids[role].add(ident)
            if role == "bridge":
                require(audit.get("needed") == ["_zig_probe.so", "libc.so.6"]
                        and audit.get("runpath") == "$ORIGIN",
                        "reject a bridge not linked to its own adjacent engine")
    repro = actual.get("reproducibility", {})
    require(len(source_ids) == 6 and repro.get("status") == "PASS"
            and repro.get("independent_phase_count") == 2
            and repro.get("compiler_process_count") == 26
            and repro.get("unique_compiler_process_count") == 26
            and repro.get("source_snapshot_count") == 6
            and all(repro.get("native_roles", {}).get(role, {}).get("byte_identical")
                    is True and repro["native_roles"][role].get("sha256") == spec[0]
                    and repro["native_roles"][role].get("bytes") == spec[1]
                    and repro["native_roles"][role].get("distinct_phase_owner_count") == 2
                    for role, spec in NATIVE.items()),
            "require two fully reproducible, complete first-party Zig phases")
    return receipt, root

class SyntheticReleaseError(Exception):
    """A genuine synthetic release error that must never be suppressed."""

def pattern_node(tree, label):
    scanners = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Scanner"
    ]
    require(
        len(scanners) == 1,
        "require the exact complete " + label + " first-party scanner",
    )
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Pattern"
    ]
    require(len(classes) == 1, "require one complete " + label + " Pattern")
    methods = [
        node for node in classes[0].body
        if isinstance(node, ast.FunctionDef) and node.name == "__del__"
    ]
    every = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "__del__"
    ]
    require(
        len(methods) == len(every) == 1 and every[0] is methods[0],
        "reject a missing, extra, nested, or foreign " + label + " destructor",
    )
    slot_rows = [
        node for node in classes[0].body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "__slots__"
    ]
    require(
        len(slot_rows) == 1
        and ast.literal_eval(slot_rows[0].value) == EXPECTED_PATTERN_SLOTS,
        "reject changed Pattern instance storage",
    )
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            require(len(node.names) == 1, "reject combined candidate imports")
            imports.append(("import", node.names[0].name, node.names[0].asname))
        elif isinstance(node, ast.ImportFrom):
            require(
                len(node.names) == 1,
                "reject widened first-party bridge imports",
            )
            imports.append((
                "from", node.module, node.level,
                node.names[0].name, node.names[0].asname,
            ))
    require(
        tuple(imports) == (
            ("import", "enum", None),
            ("import", "os", None),
            ("import", "types", None),
            ("import", "unicodedata", None),
            ("import", "warnings", None),
            ("from", "candidates", 0, "_zig_bridge", None),
        ),
        "reject an external, standard-library, or cross-candidate matcher",
    )
    return classes[0], methods[0]

def deallocator_shape(raw, *, repaired):
    require(type(raw) is bytes, "require complete source bytes")
    source = raw.decode("utf-8", "strict")
    tree = ast.parse(source, filename=(
        LIFETIME_ADAPTER[0] if repaired else CLEAN_ADAPTER[0]
    ))
    pattern, method = pattern_node(
        tree, "repaired" if repaired else "original",
    )
    exact = REPAIRED_DEALLOCATOR if repaired else ORIGINAL_DEALLOCATOR
    require(source.count(exact) == 1, "reject an inexact unique destructor")
    snippet = ast.parse("class Pattern:\n" + exact).body[0].body[0]
    require(
        ast.dump(method, include_attributes=False)
        == ast.dump(snippet, include_attributes=False),
        "reject changed defaults, release ordering, or suppressed cleanup",
    )
    if repaired:
        args = method.args
        require(
            [node.arg for node in args.args] == [
                "self", "_free", "_getattr",
            ]
            and not args.posonlyargs and not args.kwonlyargs
            and args.vararg is None and args.kwarg is None
            and len(args.defaults) == 2
            and isinstance(args.defaults[0], ast.Attribute)
            and isinstance(args.defaults[0].value, ast.Name)
            and args.defaults[0].value.id == "_zig_bridge"
            and args.defaults[0].attr == "free"
            and isinstance(args.defaults[1], ast.Name)
            and args.defaults[1].id == "getattr"
            and not any(
                isinstance(node, (ast.Try, ast.TryStar, ast.ExceptHandler))
                for node in ast.walk(method)
            ),
            "reject an uncached first-party release or swallowed failure",
        )
    return tree, pattern, method

def prove_lifetime_adapter(clean_raw, repaired_raw):
    require(
        len(clean_raw) == CLEAN_ADAPTER[2]
        and digest(clean_raw) == CLEAN_ADAPTER[1],
        "reject the authentic complete clean scanner adapter",
    )
    require(
        len(repaired_raw) == LIFETIME_ADAPTER[2]
        and digest(repaired_raw) == LIFETIME_ADAPTER[1],
        "reject the authentic complete lifetime scanner adapter",
    )
    old = ORIGINAL_DEALLOCATOR.encode("utf-8")
    new = REPAIRED_DEALLOCATOR.encode("utf-8")
    require(
        clean_raw.count(old) == 1
        and clean_raw.count(b"    def __del__(") == 1
        and repaired_raw.count(new) == 1
        and repaired_raw.count(b"    def __del__(") == 1
        and clean_raw.replace(old, new, 1) == repaired_raw,
        "reject anything beyond the one exact finalizer source edit",
    )
    old_tree, old_pattern, old_method = deallocator_shape(
        clean_raw, repaired=False,
    )
    repaired_tree, _, repaired_method = deallocator_shape(
        repaired_raw, repaired=True,
    )
    index = next(
        i for i, node in enumerate(old_pattern.body)
        if node is old_method
    )
    old_pattern.body[index] = repaired_method
    require(
        ast.dump(old_tree, include_attributes=False)
        == ast.dump(repaired_tree, include_attributes=False),
        "reject any changed matcher, parser, engine, scanner, or imports",
    )
    return {
        "original_destructor_count": 1,
        "repaired_destructor_count": 1,
        "repaired_class": "Pattern",
        "complete_other_ast_unchanged": True,
        "changed_ast_node_count": 1,
        "changed_source_block_count": 1,
        "instance_slots_changed": False,
        "matcher_parser_compiler_scanner_changed": False,
        "bridge_or_native_source_changed": False,
        "release_default": "_zig_bridge.free",
        "attribute_lookup_default": "getattr",
        "release_handle_cleared_before_call": True,
        "release_error_suppressed": False,
        "half_initialized_instance_supported": True,
    }

def validate_publication(predecessor, receipt):
    require(
        type(predecessor) is dict and type(receipt) is dict
        and predecessor.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v12-"
           "guard-clean-source-freeze"
        and predecessor.get("version") == 12
        and predecessor.get("status")
        == "SOURCE FROZEN; CORRECTED ZIG MATCHING NOT RUN"
        and predecessor.get("family") == FAMILY
        and predecessor.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and predecessor.get("source") == record(PREDECESSOR_V12[0])
        and predecessor.get("protocol") == record(PREDECESSOR_V12[1])
        and predecessor.get("corrected_original_matching") == "NOT RUN"
        and predecessor.get("corrected_supplemental_matching") == "NOT RUN"
        and predecessor.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and predecessor.get("qualified_candidate_count") == 0
        and predecessor.get("current_qualified_candidates") == 0
        and predecessor.get("minimum_qualified_candidates") == 3
        and predecessor.get("holdout_case_count") == 14155776,
        "reject the complete pushed V12 first-party source freeze",
    )
    original = predecessor.get("original_oracle", {})
    first_party = predecessor.get("first_party_zig", {})
    require(
        original.get("case_execution_denominator") == 31237
        and original.get("suite_count") == 13
        and original.get("obligation_count") == 73
        and original.get("crosswalk_count") == 34
        and original.get("named_private_waiver_count") == 13
        and original.get("supplemental_case_count") == 8244
        and original.get("supplemental_candidate_matching") == "NOT RUN"
        and original.get("supplemental_cases_added_to_original_denominator")
        is False
        and tuple(
            (row.get("id"), row.get("case_execution_count"))
            for row in original.get("suites", [])
        ) == SUITES
        and first_party.get("guard_clean_scanner_adapter")
        == record(CLEAN_ADAPTER)
        and first_party.get("engine_source") == record(ENGINE_SOURCE)
        and first_party.get("bridge_source") == record(BRIDGE_SOURCE)
        and first_party.get("complete_matching_ast_unchanged") is True
        and first_party.get("v13_build_attests_guard_clean_adapter")
        is False,
        "reject inherited P0, first-party Zig, or prior build claims",
    )
    require(
        receipt.get("schema")
        == "rebar-owned-repaired-zig-original-campaign-v12-"
           "durable-publication-receipt"
        and receipt.get("status") == "PASS"
        and receipt.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and receipt.get("source_sha256") == PREDECESSOR_V12[0][1]
        and receipt.get("protocol_sha256") == PREDECESSOR_V12[1][1]
        and receipt.get("contract_sha256") == PREDECESSOR_V12[2][1]
        and receipt.get("family") == FAMILY
        and receipt.get("label")
        == "phase2-v13-zig-guard-clean-v1-original-p0-v12"
        and receipt.get("all_original_suites_attempted") is True
        and receipt.get("case_execution_denominator") == 31237
        and receipt.get("suite_count") == 13
        and receipt.get("actual_candidate_workers") == 13
        and receipt.get("unique_candidate_worker_count") == 13
        and receipt.get("completed_suite_count") == 12
        and receipt.get("verified_passing_case_count") == 4607
        and receipt.get("observed_semantic_mismatch_lower_bound") == 1700
        and receipt.get("semantic_mismatch_count") == "NOT MEASURED"
        and receipt.get("infrastructure_failure_count") == 1
        and receipt.get("infrastructure_failure_suites")
        == ["subinterpreter_v2"]
        and receipt.get("failed_suites")
        == [name for name, _ in ACTUAL_SEMANTIC_FAILURES]
           + ["subinterpreter_v2"]
        and receipt.get("candidate_status") == "FAIL"
        and receipt.get("candidate_qualified") is False
        and receipt.get("original_campaign_passed") is False
        and receipt.get("all_three_original_targets_restored") is True
        and receipt.get("per_suite_timeout_seconds") == 120
        and receipt.get("maximum_serial_worker_timeout_seconds") == 1560
        and receipt.get("timeout_count") == 0
        and receipt.get("timed_out_suites") == []
        and receipt.get("supplemental_candidate_matching") == "NOT RUN"
        and receipt.get("hidden_cases_read") == 0
        and receipt.get("benchmark_files_read") == 0
        and receipt.get("timing_trials_run") == 0
        and receipt.get("holdout") == "NOT OPENED"
        and receipt.get("performance") == "NOT MEASURED"
        and receipt.get("memory") == "NOT MEASURED"
        and receipt.get("undefined_behavior") == "NOT MEASURED"
        and receipt.get("winner_selected") is False,
        "reject or exaggerate the actual fully guarded V12 publication",
    )
    archive = receipt.get("archive", {})
    require(
        type(archive) is dict
        and archive.get("name")
        == "repaired-zig-original-campaign-v12-phase2-v13-zig-"
           "guard-clean-v1-original-p0-v12-failures.json.gz"
        and archive.get("sha256")
        == "ab8aa0f69cce19d62ffb75f8c56ca57fc22d2441cb3b14b8718f5cc7280de5e4"
        and archive.get("bytes") == 5618052
        and archive.get("device") == DEVICE
        and archive.get("inode") == 524970
        and archive.get("uid") == os.geteuid()
        and archive.get("mode") == 0o600
        and archive.get("nlink") == 1,
        "reject actual archive metadata or claim the archive was opened",
    )
    rows = receipt.get("original_suite_diagnostics")
    require(
        type(rows) is list and len(rows) == 13
        and tuple((row.get("suite"), row.get("case_execution_denominator"))
                  for row in rows) == SUITES
        and all(type(row.get("pid")) is int and row["pid"] > 0
                for row in rows)
        and len({row["pid"] for row in rows}) == 13
        and all(row.get("guard_installed_before_candidate_import") is True
                and row.get("candidate_imported") is True for row in rows),
        "require 13 genuine distinct guard-proven original V12 workers",
    )
    passing = tuple(
        (row["suite"], row["case_execution_denominator"])
        for row in rows
        if row.get("status") == "PASS"
        and row.get("infrastructure_failure") is False
        and row.get("observed_semantic_mismatch_count") == 0
    )
    measured = tuple(
        (row["suite"], row["observed_semantic_mismatch_count"])
        for row in rows
        if row.get("status") == "FAIL"
        and row.get("infrastructure_failure") is False
        and type(row.get("observed_semantic_mismatch_count")) is int
    )
    require(
        passing == ACTUAL_PASSING_SUITES
        and sum(count for _, count in passing) == 4607
        and measured == ACTUAL_SEMANTIC_FAILURES
        and sum(count for _, count in measured) == 1700,
        "preserve all seven genuine passes and all five measured losses",
    )
    warnings = []
    for row in rows:
        excerpt = row.get("stderr_literal_excerpt")
        require(
            type(excerpt) is dict
            and excerpt.get("status") == "CAPTURED"
            and type(excerpt.get("text")) is str
            and "Exception ignored while calling deallocator"
            in excerpt["text"]
            and "line 1086" in excerpt["text"]
            and "'NoneType' object has no attribute 'free'"
            in excerpt["text"],
            "preserve the exact actual V12 warning in every worker",
        )
        warnings.append(row["suite"])
    nested_rows = [
        row for row in rows if row.get("suite") == "subinterpreter_v2"
    ]
    require(
        len(nested_rows) == 1,
        "require the genuine separately preserved original child failure",
    )
    row = nested_rows[0]
    nested = row.get("complete_actual_suite_failure_details")
    original_failure = (
        nested.get("complete_original_failure_details")
        if type(nested) is dict else None
    )
    require(
        row.get("status") == "FAIL"
        and row.get("infrastructure_failure") is True
        and row.get("activation_stage")
        == "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
        and row.get("error_type") == "ActualSuiteFailure"
        and row.get("error_message")
        == "preserve the actual guarded original child lifecycle failure"
        and row.get("observed_semantic_mismatch_count") == "NOT MEASURED"
        and type(nested) is dict
        and nested.get("schema")
        == "rebar-owned-six-family-original-p0-producer-v5-"
           "genuine-nested-failure"
        and nested.get("error_type") == "ActualSuiteFailure"
        and nested.get("error_message")
        == "retain every genuine failed private-interpreter call and cleanup"
        and nested.get("actual_child_guards_installed") == 1
        and nested.get("actual_candidate_subprocesses") == 0
        and nested.get("actual_guard_cleanup_interpreter_exec_calls") == 0
        and nested.get("expected_case_interpreter_exec_calls") == 394
        and nested.get("expected_interpreters_created") == 11
        and type(original_failure) is dict
        and original_failure.get("status") == "FAIL"
        and original_failure.get("active_phase")
        == "install-original-private-guard-A"
        and original_failure.get("actual_prepared_interpreter_ids") == []
        and original_failure.get("actual_case_interpreter_exec_calls") == 0
        and original_failure.get("actual_guard_cleanup_interpreter_exec_calls")
        == 0
        and original_failure.get("actual_initialization_interpreter_exec_calls")
        == 1
        and original_failure.get("actual_interpreters_created") == 2
        and original_failure.get("actual_interpreters_destroyed") == 2
        and original_failure.get("completed_a_records") == []
        and original_failure.get("completed_b_records") == []
        and original_failure.get("error_type") == "GuardError"
        and original_failure.get("error_message")
        == "runtime guard blocked unattested-child-bootstrap",
        "never count a generated child-guard field as installed or matching",
    )
    return {
        "passing_suites": passing,
        "semantic_failures": measured,
        "warning_suites": tuple(warnings),
        "subinterpreter": original_failure,
    }

ACTUAL_CALLER_PINS = (
    ("--build-receipt-sha256", V13[3][1]),
    ("--root-receipt-sha256", V13[4][1]),
    ("--producer-source-sha256", PRODUCER[0][1]),
    ("--producer-protocol-sha256", PRODUCER[1][1]),
    ("--producer-contract-sha256", PRODUCER[2][1]),
    ("--guard-source-sha256", GUARD[0][1]),
    ("--guard-protocol-sha256", GUARD[1][1]),
    ("--guard-contract-sha256", GUARD[2][1]),
    ("--v2-guard-source-sha256", GUARD_V2[0][1]),
    ("--v2-guard-protocol-sha256", GUARD_V2[1][1]),
    ("--v2-guard-contract-sha256", GUARD_V2[2][1]),
    ("--lifetime-source-sha256", LIFETIME_FREEZE[0][1]),
    ("--lifetime-protocol-sha256", LIFETIME_FREEZE[1][1]),
    ("--lifetime-contract-sha256", LIFETIME_FREEZE[2][1]),
    ("--adapter-sha256", LIFETIME_ADAPTER[1]),
)


def require_actual_authority(args, *, worker=False):
    require(
        type(args) is dict
        and args.get("--family") == FAMILY
        and args.get("--label") == LABEL
        and all(
            args.get(name) == expected
            for name, expected in ACTUAL_CALLER_PINS
        )
        and (not worker or args.get("--suite") in dict(SUITES)),
        "require complete independent V3, V2, V5, lifetime, and native caller pins",
    )

def context(source_sha, protocol_sha, *, active=False):
    clean()
    for path, expected in (
        (SELF, pin(source_sha, "source")),
        (PROTOCOL, pin(protocol_sha, "protocol")),
    ):
        info = os.stat(ROOT + "/" + path, follow_symlinks=False)
        read_owner((path, expected, info.st_size, info.st_ino))
    for item in owners(active=active):
        read_owner(item)
    producer = load(
        PRODUCER[0], "_rebar_zig_v13_exact_immutable_v5_json",
    )
    require(
        producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v5"
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and producer.CASE_DENOMINATOR == 31237
        and producer.SUITE_COUNT == 13
        and producer.PRIVATE_WAIVER_COUNT == 13
        and producer.ORIGINAL_OBLIGATION_COUNT == 73
        and producer.ORIGINAL_CROSSWALK_COUNT == 34
        and producer.SUPPLEMENTAL_CASE_COUNT == 8244
        and tuple(
            (row.name, row.case_count) for row in producer.SUITES
        ) == SUITES
        and sum(count for _, count in SUITES) == 31237,
        "reject an altered immutable V5 original correctness producer",
    )
    phase = producer.JsonReader(read_owner(P0[1])).parse()
    gate = phase.get("phase_gate", {})
    oracle = phase.get("original_oracle", {})
    require(
        phase.get("schema") == "rebar-cpython-re-p0-completeness-v4"
        and phase.get("version") == 4
        and phase.get("status") == "PASS"
        and phase.get("original_case_execution_denominator") == 31237
        and phase.get("original_suite_count") == 13
        and phase.get("original_named_private_waiver_count") == 13
        and phase.get("original_obligation_count") == 73
        and phase.get("original_crosswalk_count") == 34
        and gate.get("status") == "PASS"
        and gate.get("candidate_evaluation_authorized") is True
        and gate.get("final_holdout_authorized") is False
        and gate.get("performance_oracle_authorized") is False
        and tuple(
            (row.get("id"), row.get("case_execution_count"))
            for row in oracle.get("suites", [])
        ) == SUITES,
        "reject a weakened or renumbered complete frozen P0 matrix",
    )
    for suite in producer.SUITES:
        read_suite(suite.source_relative, suite.source_sha256)
    manifest = producer.JsonReader(read_owner(P0[2])).parse()
    require(
        type(manifest.get("suites")) is list
        and len(manifest["suites"]) == 13,
        "reject an incomplete original CPython baseline manifest",
    )
    fuzz = producer.JsonReader(read_owner(P0[5])).parse()
    workers = fuzz.get("workers", [])
    require(
        fuzz.get("status") == "PASS"
        and fuzz.get("actual_reference_worker_count") == 2
        and fuzz.get("supplemental_case_count") == 8244
        and len(workers) == 2
        and {row.get("pid") for row in workers} == {81, 82}
        and all(row.get("case_count") == 8244 for row in workers)
        and fuzz.get("holdout") == "NOT OPENED",
        "reject the separate frozen two-worker differential reference",
    )
    proposal = producer.JsonReader(
        read_owner(EXPANDED_HOLDOUT_PROPOSAL[2])
    ).parse()
    required = proposal.get("required_public_owners", [])
    historical = [
        row for row in required
        if type(row) is dict
        and row.get("path") == HISTORICAL_HOLDOUT_PROPOSAL[0]
    ]
    require(
        proposal.get("schema")
        == "rebar-expanded-sealed-holdout-pre-phase3-proposal-v1"
        and proposal.get("proposal_status") == "PRE-PHASE-3 PROPOSAL"
        and proposal.get("final_protocol_status") == "NOT FROZEN"
        and proposal.get("generator_status") == "NOT FROZEN"
        and proposal.get("secret_status") == "NOT GENERATED"
        and proposal.get("case_status") == "NOT GENERATED; NOT OPENED"
        and proposal.get("timing_status") == "NOT RUN; NOT MEASURED"
        and proposal.get("memory_status") == "NOT RUN; NOT MEASURED"
        and proposal.get("runtime_independence_status") == "NOT ESTABLISHED"
        and proposal.get("winner_status") == "NOT SELECTED"
        and proposal.get("qualified_independent_family_count") == 0
        and proposal.get("minimum_qualified_independent_family_count") == 3
        and proposal.get("original_p0_case_count") == 31237
        and proposal.get("original_p0_suite_count") == 13
        and proposal.get("named_private_waiver_count") == 13
        and proposal.get("separate_differential_case_count") == 8244
        and proposal.get("pinned_python_version") == "3.14.6"
        and proposal.get("pinned_python_path") == PYTHON
        and proposal.get("pinned_python_sha256") == PINNED_PYTHON_SHA256
        and proposal.get("preserved_previous_proposal_case_count") == 4194304
        and proposal.get("case_count") == 14155776
        and proposal.get("timed_case_count") == 14155776
        and proposal.get("operation_count") == 36
        and proposal.get("pattern_family_count") == 24
        and proposal.get("subject_type_count") == 4
        and proposal.get("lifecycle_count") == 4
        and proposal.get("cases_per_stratum") == 1024
        and proposal.get("stratum_count") == 13824
        and 36 * 24 * 4 * 4 * 1024 == 14155776
        and proposal.get("candidate_participant_count") == 3
        and proposal.get("baseline_participant_count") == 1
        and proposal.get("participant_count") == 4
        and len(proposal.get("operations", [])) == 36
        and len(proposal.get("primary_pattern_families", [])) == 24
        and len(proposal.get("subject_types", [])) == 4
        and len(proposal.get("lifecycle_slots", [])) == 4
        and len(historical) == 1
        and historical[0].get("sha256")
        == HISTORICAL_HOLDOUT_PROPOSAL[1],
        "reject opening, weakening, or inventing the expanded holdout",
    )
    producer_contract = producer.JsonReader(
        read_owner(PRODUCER[2])
    ).parse()
    zig = [
        row for row in producer_contract.get("families", [])
        if row.get("name") == FAMILY
    ]
    require(
        producer_contract.get("version") == 5
        and producer_contract.get("original_obligation_count") == 73
        and producer_contract.get("original_crosswalk_count") == 34
        and producer_contract.get("supplemental_case_count") == 8244
        and len(zig) == 1
        and zig[0].get("owned_ctypes") is True,
        "reject a changed first-party six-family P0 contract",
    )
    guard_v2 = producer.JsonReader(read_owner(GUARD_V2[2])).parse()
    require(
        guard_v2.get("schema")
        == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
        and guard_v2.get("version") == 2
        and guard_v2.get("source") == record(GUARD_V2[0])
        and guard_v2.get("protocol") == record(GUARD_V2[1])
        and guard_v2.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and guard_v2.get("qualified_candidate_count") == 0,
        "reject the unchanged immutable V5-attested original V2 guard",
    )
    guard = producer.JsonReader(read_owner(GUARD[2])).parse()
    v2_lineage = guard.get("immutable_predecessor_v2", {})
    v5_lineage = guard.get("immutable_producer_v5", {})
    child = guard.get("subinterpreter_bootstrap", {})
    native_policy = guard.get("native_owner_policy", {})
    require(
        guard.get("schema")
        == "rebar-owned-candidate-runtime-independence-v3-source-freeze"
        and guard.get("version") == 3
        and guard.get("status")
        == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
        and guard.get("source") == record(GUARD[0])
        and guard.get("protocol") == record(GUARD[1])
        and guard.get("goal_sha256") == GOAL[1]
        and guard.get("runtime_non_delegation") == "NOT ESTABLISHED"
        and guard.get("qualified_candidate_count") == 0
        and guard.get("holdout") == "NOT OPENED"
        and guard.get("candidate_matching") == "NOT RUN"
        and v2_lineage.get("version") == 2
        and v2_lineage.get("owners") == {
            "source": record(GUARD_V2[0]),
            "protocol": record(GUARD_V2[1]),
            "contract": record(GUARD_V2[2]),
        }
        and v2_lineage.get("policy")
        == "EXACT AUTHENTICATED V2 RUNTIME POLICY SUBCLASS"
        and v2_lineage.get("prepare_family")
        == "INHERITED EXACT V2 FUNCTION AND GLOBALS"
        and v2_lineage.get("child_bootstrap")
        == "UNCHANGED AUTHENTICATED V2 CHILD SOURCE"
        and v5_lineage.get("version") == 5
        and v5_lineage.get("owners") == {
            "source": record(PRODUCER[0]),
            "protocol": record(PRODUCER[1]),
            "contract": record(PRODUCER[2]),
        }
        and v5_lineage.get("source_mutated") is False
        and child.get("suite") == "subinterpreter_v2"
        and child.get("original_case_count") == 128
        and child.get("expected_interpreters_created") == 11
        and child.get("expected_interpreters_destroyed") == 11
        and child.get("expected_case_interpreter_exec_calls") == 394
        and child.get("expected_bootstrap_interpreter_exec_calls") == 11
        and child.get("expected_cleanup_interpreter_exec_calls") == 11
        and child.get("expected_total_real_interpreter_exec_calls") == 416
        and child.get("creation_audit_event") == "cpython.PyInterpreterState_New"
        and child.get("creation_audit_arguments") == "NOT MEASURED"
        and child.get("actual_interpreters_created") == 0
        and child.get("actual_interpreters_destroyed") == 0
        and child.get("actual_case_interpreter_exec_calls") == 0
        and child.get("actual_bootstrap_interpreter_exec_calls") == 0
        and child.get("actual_cleanup_interpreter_exec_calls") == 0
        and child.get("actual_child_guards_installed") == 0
        and child.get("candidate_status") == "NOT RUN"
        and native_policy.get("required_field_count") == 14
        and native_policy.get("required_fields")
        == sorted(REQUIRED_NATIVE_OWNER_FIELDS)
        and native_policy.get("extra_or_missing_fields") == "FORBIDDEN"
        and native_policy.get("native_loaded") is False,
        "reject, weaken, execute, or falsely attest the exact V3 live-child guard",
    )
    previous = producer.JsonReader(
        read_owner(PREDECESSOR_V12[2])
    ).parse()
    publication = producer.JsonReader(
        read_owner(PREDECESSOR_V12[3])
    ).parse()
    actual = validate_publication(previous, publication)
    build, build_root = validate_build(producer)
    clean_adapter = read_owner(CLEAN_ADAPTER)
    require(
        normalize(read_owner(PARENT_ADAPTER)) == clean_adapter,
        "reject the complete source-authenticated V13 clean scanner lineage",
    )
    repaired = read_owner(LIFETIME_ADAPTER)
    proof = prove_lifetime_adapter(clean_adapter, repaired)
    lifetime = producer.JsonReader(read_owner(LIFETIME_FREEZE[2])).parse()
    frozen_repair = lifetime.get("first_party_lifetime_repair", {})
    historical = lifetime.get("pushed_v12_predecessor", {})
    require(
        lifetime.get("schema")
        == "rebar-owned-zig-deallocator-lifetime-source-repair-v1-source-freeze"
        and lifetime.get("version") == 1
        and lifetime.get("status")
        == "SOURCE FROZEN; FIRST-PARTY LIFETIME VARIANT NOT BUILT OR RUN"
        and lifetime.get("source") == record(LIFETIME_FREEZE[0])
        and lifetime.get("protocol") == record(LIFETIME_FREEZE[1])
        and frozen_repair.get("clean_input") == record(CLEAN_ADAPTER)
        and frozen_repair.get("additive_lifetime_variant")
        == record(LIFETIME_ADAPTER)
        and frozen_repair.get("complete_byte_replacement_proven") is True
        and frozen_repair.get("complete_other_ast_unchanged") is True
        and frozen_repair.get("changed_ast_node_count") == 1
        and frozen_repair.get("changed_source_block_count") == 1
        and frozen_repair.get("instance_slots_changed") is False
        and frozen_repair.get("matcher_parser_compiler_scanner_changed")
        is False
        and frozen_repair.get("bridge_or_native_source_changed") is False
        and frozen_repair.get("release_default") == "_zig_bridge.free"
        and frozen_repair.get("attribute_lookup_default") == "getattr"
        and frozen_repair.get("release_handle_cleared_before_call") is True
        and frozen_repair.get("release_error_suppressed") is False
        and frozen_repair.get("adapter_imported") is False
        and frozen_repair.get("candidate_built") is False
        and frozen_repair.get("candidate_matching") == "NOT RUN"
        and frozen_repair.get("candidate_qualified") is False
        and historical.get("owners") == [
            record(item) for item in PREDECESSOR_V12
        ],
        "reject expanded, delegated, run, or falsely qualified lifetime repair",
    )
    warnings = publication.get("original_suite_diagnostics", [])
    stderr_bytes = sum(
        row.get("stderr", {}).get("bytes", -1)
        for row in warnings
    )
    require(
        len(warnings) == 13 and stderr_bytes == 311416,
        "reject complete actual prior worker stderr byte identities",
    )
    implementation = load(
        GUARD[0], "_rebar_zig_v13_source_authenticated_guard_v3",
    )
    require(
        implementation.SELF == GUARD[0][0]
        and implementation.PROTOCOL == GUARD[1][0]
        and implementation.CONTRACT == GUARD[2][0]
        and implementation.NATIVE_OWNER_KEYS == REQUIRED_NATIVE_OWNER_FIELDS
        and implementation.RuntimePolicy.prepare_family
        is implementation.BASE.RuntimePolicy.prepare_family
        and implementation.RuntimePolicy.prepare_family.__globals__
        is implementation.BASE.__dict__
        and implementation.RuntimePolicy.prepare_family.__globals__["SELF"]
        == GUARD_V2[0][0]
        and implementation.RuntimePolicy.prepare_family.__globals__["PROTOCOL"]
        == GUARD_V2[1][0]
        and implementation.RuntimePolicy.prepare_family.__globals__["CONTRACT"]
        == GUARD_V2[2][0]
        and implementation.RuntimePolicy.prepare_family.__code__.co_filename
        == ROOT + "/" + GUARD_V2[0][0]
        and implementation.child_bootstrap_source
        is implementation.BASE.child_bootstrap_source
        and implementation.CREATE_EVENT == "cpython.PyInterpreterState_New"
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "concurrent.interpreters" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "reject exact inherited V2 code/global identity or source-only V3 isolation",
    )
    clean()
    return {
        "producer": producer,
        "phase": phase,
        "manifest": manifest,
        "fuzz": fuzz,
        "proposal": proposal,
        "producer_contract": producer_contract,
        "guard": guard,
        "guard_v2": guard_v2,
        "guard_implementation": implementation,
        "lifetime": lifetime,
        "predecessor": previous,
        "publication": publication,
        "actual": actual,
        "historical_stderr_bytes": stderr_bytes,
        "build": build,
        "build_root": build_root,
        "clean_adapter": clean_adapter,
        "repaired_adapter": repaired,
        "proof": proof,
    }

def contract_value(source_sha, protocol_sha, state=None):
    if state is None:
        state = context(source_sha, protocol_sha)
    source_stat = os.stat(ROOT + "/" + SELF, follow_symlinks=False)
    protocol_stat = os.stat(ROOT + "/" + PROTOCOL, follow_symlinks=False)
    publication = state["publication"]
    actual = state["actual"]
    previous_rows = publication["original_suite_diagnostics"]
    guard = state["guard"]
    guard_child = guard["subinterpreter_bootstrap"]
    lifetime = state["lifetime"]["first_party_lifetime_repair"]
    return {
        "schema": SCHEMA + "-guarded-lifetime-source-freeze",
        "version": 13,
        "status": (
            "SOURCE FROZEN; V3-GUARDED LIFETIME ZIG MATCHING NOT RUN"
        ),
        "family": FAMILY,
        "label": LABEL,
        "source": record((
            SELF, source_sha, source_stat.st_size, source_stat.st_ino,
        )),
        "protocol": record((
            PROTOCOL, protocol_sha,
            protocol_stat.st_size, protocol_stat.st_ino,
        )),
        "goal": record(GOAL),
        "pinned_cpython": {
            "path": PYTHON,
            "version": "3.14.6",
            "sha256": PINNED_PYTHON_SHA256,
            "isolated_flags": ["-I", "-B", "-S"],
            "bytecode_written": False,
        },
        "original_oracle": {
            "phase_one_owners": [record(item) for item in P0],
            "matrix_version": 4,
            "case_execution_denominator": 31237,
            "suite_count": 13,
            "suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "suite_source_owners_authenticated": 13,
            "obligation_count": 73,
            "crosswalk_count": 34,
            "named_private_waiver_count": 13,
            "named_private_waivers": list(
                state["producer"].PRIVATE_WAIVER_NAMES
            ),
            "supplemental_reference_case_count": 8244,
            "supplemental_reference_worker_count": 2,
            "supplemental_candidate_matching": "NOT RUN",
            "supplemental_cases_added_to_original_denominator": False,
            "performance_oracle_authorized": False,
            "final_holdout_authorized": False,
        },
        "immutable_v5_original_producer": {
            "owners": [record(item) for item in PRODUCER],
            "version": 5,
            "source_modified": False,
            "original_suites_modified": False,
            "maximum_json_bytes": IMMUTABLE_PRODUCER_JSON_BYTES,
            "actual_worker_json_maximum_bytes": MAX_ACTUAL_WORKER_JSON_BYTES,
            "original_13_worker_processes_started_by_source_gate": 0,
        },
        "pushed_v12_actual_predecessor": {
            "owners": [record(item) for item in PREDECESSOR_V12],
            "source_freeze_schema": state["predecessor"]["schema"],
            "source_freeze_version": 12,
            "durable_plaintext_publication": {
                "owner": record(PREDECESSOR_V12[3]),
                "publication_status": "PASS",
                "publication_pass_means": "DURABLE PUBLICATION ONLY",
                "candidate_status": "FAIL",
                "candidate_qualified": False,
                "all_original_suites_attempted": True,
                "case_execution_denominator": 31237,
                "suite_count": 13,
                "actual_candidate_workers": 13,
                "unique_candidate_worker_count": 13,
                "all_parent_worker_guard_markers_established": True,
                "completed_suite_count": 12,
                "verified_passing_suite_count": 7,
                "verified_passing_case_count": 4607,
                "verified_passing_suites": [
                    {"suite": name, "cases": count}
                    for name, count in actual["passing_suites"]
                ],
                "completed_semantic_failure_count": 5,
                "genuine_completed_semantic_failures": [
                    {
                        "suite": name,
                        "observed_semantic_mismatch_count": count,
                        "infrastructure_failure": False,
                    }
                    for name, count in actual["semantic_failures"]
                ],
                "observed_semantic_mismatch_lower_bound": 1700,
                "semantic_mismatch_count": "NOT MEASURED",
                "all_complete_actual_public_suite_diagnostics": previous_rows,
                "public_suite_diagnostic_count": 13,
                "private_case_details_claimed": False,
                "failed_suite_classification": [
                    {
                        "suite": row["suite"],
                        "recorded_status": row["status"],
                        "recorded_infrastructure_failure": (
                            row["infrastructure_failure"]
                        ),
                        "observed_semantic_mismatch_count": (
                            row["observed_semantic_mismatch_count"]
                        ),
                    }
                    for row in previous_rows
                    if row["status"] != "PASS"
                ],
                "actual_subinterpreter_failure": {
                    "suite": "subinterpreter_v2",
                    "activation_stage": (
                        "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
                    ),
                    "recorded_outer_error_type": "ActualSuiteFailure",
                    "recorded_nested_error_type": "ActualSuiteFailure",
                    "recorded_original_error_type": "GuardError",
                    "recorded_original_error_message": (
                        "runtime guard blocked unattested-child-bootstrap"
                    ),
                    "recorded_original_active_phase": (
                        "install-original-private-guard-A"
                    ),
                    "reported_wrapper_child_guard_count": 1,
                    "reported_count_proves_actual_installation": False,
                    "actual_prepared_interpreter_ids": [],
                    "actual_case_interpreter_exec_calls": 0,
                    "actual_guard_cleanup_interpreter_exec_calls": 0,
                    "actual_initialization_interpreter_exec_calls": 1,
                    "actual_interpreters_created": 2,
                    "actual_interpreters_destroyed": 2,
                    "expected_interpreters_created": 11,
                    "expected_case_interpreter_exec_calls": 394,
                    "semantic_mismatch_count": "NOT MEASURED",
                    "lifetime_variant_corrects_failure": "NOT ESTABLISHED",
                    "v3_guard_corrects_failure": "NOT ESTABLISHED",
                    "complete_actual_original_failure_details": (
                        actual["subinterpreter"]
                    ),
                },
                "complete_stderr_metadata_bytes": (
                    state["historical_stderr_bytes"]
                ),
                "deallocator_warning": {
                    "observed_suite_count": 13,
                    "observed_in_all_seven_passing_suites": True,
                    "observed_suite_names": list(actual["warning_suites"]),
                    "complete_worker_stderr_bytes": 311416,
                    "literal_warning": (
                        "Exception ignored while calling deallocator"
                    ),
                    "source_line": 1086,
                    "literal_error": (
                        "'NoneType' object has no attribute 'free'"
                    ),
                    "repaired_real_run_warning": "NOT MEASURED",
                    "worker_stderr_suppressed": False,
                },
                "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
                "maximum_serial_worker_timeout_seconds": (
                    MAX_SERIAL_SUITE_TIMEOUT_SECONDS
                ),
                "all_three_original_targets_restored": True,
                "archive_metadata": publication["archive"],
                "compressed_archive_opened": False,
            },
        },
        "first_party_lifetime_adapter": {
            "source_repair_owners": [
                record(item) for item in LIFETIME_FREEZE
            ],
            "original_clean_adapter": record(CLEAN_ADAPTER),
            "additive_lifetime_adapter": record(LIFETIME_ADAPTER),
            "original_v13_build_scanner_adapter": record(PARENT_ADAPTER),
            "first_party_native_engine_source": record(ENGINE_SOURCE),
            "first_party_native_bridge_source": record(BRIDGE_SOURCE),
            "original_destructor": ORIGINAL_DEALLOCATOR,
            "repaired_destructor": REPAIRED_DEALLOCATOR,
            **state["proof"],
            "definition_time_callable_retains_bridge_module": True,
            "reentrant_release_is_at_most_once": True,
            "release_error_propagates": True,
            "ordinary_scanner_cleanup_changed": False,
            "source_repair_declares_candidate_imported": (
                lifetime["adapter_imported"]
            ),
            "source_repair_declares_candidate_built": (
                lifetime["candidate_built"]
            ),
            "source_repair_declares_candidate_matching": (
                lifetime["candidate_matching"]
            ),
            "external_regex_engine_added": False,
            "cross_candidate_engine_added": False,
            "stdlib_regex_fallback_added": False,
            "lifetime_adapter_matched_in_source_gate": False,
        },
        "immutable_v2_runtime_guard": {
            "owners": [record(item) for item in GUARD_V2],
            "version": 2,
            "v1_source_owners": [
                record(item) for item in GUARD_V1
            ],
            "source_or_policy_modified": False,
            "producer_child_pin_identity": (
                "EXACT V2 FUNCTION, CODE, GLOBALS AND CHILD BOOTSTRAP"
            ),
        },
        "pushed_v3_real_interpreter_guard": {
            "owners": [record(item) for item in GUARD],
            "version": 3,
            "status": "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE",
            "v2_policy_exactly_inherited": True,
            "prepare_family_exact_v2_function": True,
            "prepare_family_exact_v2_globals": True,
            "prepare_family_exact_v2_code_filename": True,
            "immutable_v5_guarded_create_closure_required": True,
            "pinned_public_provider_source": (
                guard["pinned_cpython"]["public_interpreter_source"]
            ),
            "actual_live_provider_frame_required": True,
            "recompiled_equal_frame_accepted": False,
            "native_public_live_set_delta_required": True,
            "genuine_creation_audit_event": (
                guard_child["creation_audit_event"]
            ),
            "actual_creation_audit_arguments": "NOT MEASURED",
            "legacy_creation_events_accepted": False,
            "strict_native_owner": {
                "required_field_count": 14,
                "required_fields": sorted(REQUIRED_NATIVE_OWNER_FIELDS),
                "missing_or_extra_fields_accepted": False,
                "loaded_native_owner_accepted": False,
                "cross_family_owner_accepted": False,
            },
            "subinterpreter_suite": "subinterpreter_v2",
            "original_case_count": 128,
            "expected_interpreters_created": 11,
            "expected_interpreters_destroyed": 11,
            "expected_case_interpreter_exec_calls": 394,
            "expected_bootstrap_interpreter_exec_calls": 11,
            "expected_cleanup_interpreter_exec_calls": 11,
            "expected_total_real_interpreter_exec_calls": 416,
            "actual_interpreters_created_in_source_gate": 0,
            "actual_interpreters_destroyed_in_source_gate": 0,
            "actual_child_guards_installed_in_source_gate": 0,
            "actual_case_interpreter_exec_calls_in_source_gate": 0,
            "actual_bootstrap_interpreter_exec_calls_in_source_gate": 0,
            "actual_cleanup_interpreter_exec_calls_in_source_gate": 0,
            "runtime_non_delegation": "NOT ESTABLISHED",
        },
        "historical_first_party_v13_native_build": {
            "owners": [record(item) for item in V13],
            "status": "PASS",
            "label": BUILD_LABEL,
            "actual_prior_process_count": 26,
            "actual_prior_unique_process_count": 26,
            "independent_phase_count": 2,
            "source_snapshot_count": 6,
            "native_engine": {
                "sha256": NATIVE["engine"][0],
                "bytes": NATIVE["engine"][1],
            },
            "native_bridge": {
                "sha256": NATIVE["bridge"][0],
                "bytes": NATIVE["bridge"][1],
            },
            "source_reproducible": True,
            "cross_family_engine_count": 0,
            "external_regex_dependency_count": 0,
            "stdlib_regex_engine_count": 0,
            "prior_build_attests_lifetime_adapter": False,
            "private_native_root_opened_by_source_gate": False,
            "matching_archive_opened_by_source_gate": False,
            "compiler_processes_started_by_source_gate": 0,
            "candidate_correctness": "NOT MEASURED",
        },
        "source_only_worker_transport": {
            "immutable_json_maximum_bytes": (
                IMMUTABLE_PRODUCER_JSON_BYTES
            ),
            "actual_worker_json_maximum_bytes": (
                MAX_ACTUAL_WORKER_JSON_BYTES
            ),
            "injective_unicode_transport_required": True,
            "surrogate_and_reserved_key_collisions_rejected": True,
            "preserve_complete_worker_stdout_and_stderr": True,
            "publish_all_13_public_worker_diagnostics": True,
            "complete_nested_failures_preserved": True,
            "actual_worker_started_in_source_gate": False,
        },
        "future_actual_run": {
            "authorization": "SEPARATE EXPLICIT FULLY PINNED --run",
            "root_exclusive_canonical_target_window_required": True,
            "caller_pins": [
                {"option": key, "sha256": value}
                for key, value in ACTUAL_CALLER_PINS
            ],
            "candidate_family": FAMILY,
            "candidate_label": LABEL,
            "original_suite_worker_count": 13,
            "unique_original_worker_pid_count_required": 13,
            "case_execution_denominator": 31237,
            "native_build_authorized": False,
            "compiler_processes_authorized": False,
            "only_pushed_lifetime_adapter": record(LIFETIME_ADAPTER),
            "guard_installed_before_candidate_import": True,
            "guard_version": 3,
            "runtime_guard_owners": [
                record(item) for item in GUARD
            ],
            "inherited_v2_owners": [
                record(item) for item in GUARD_V2
            ],
            "producer_owners": [
                record(item) for item in PRODUCER
            ],
            "exact_native_owner_field_count": 14,
            "recovery_root": RECOVERY,
            "durable_three_role_journal_before_replacement": True,
            "exclusive_recovery_lock": "campaign-v13.lock",
            "role_order": list(ROLES),
            "restoration_order": list(RESTORE),
            "canonical_original_targets": ORIGINALS,
            "exact_original_inode_backup_required": True,
            "all_three_original_targets_restored_before_publication": True,
            "separate_pinned_recovery_action": "--recover",
            "per_complete_original_suite_timeout_seconds": (
                SUITE_TIMEOUT_SECONDS
            ),
            "maximum_serial_worker_timeout_seconds": (
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS
            ),
            "continue_after_every_recorded_failure": True,
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "success_publication_receipt": (
                "oracle/phase2/evidence/"
                + publication_stem("success")
                + "-publication-receipt.json"
            ),
            "failure_publication_receipt": (
                "oracle/phase2/evidence/"
                + publication_stem("failures")
                + "-publication-receipt.json"
            ),
            "success_result_archive": (
                "oracle/phase2/evidence/"
                + publication_stem("success")
                + ".json.gz"
            ),
            "failure_result_archive": (
                "oracle/phase2/evidence/"
                + publication_stem("failures")
                + ".json.gz"
            ),
            "supplemental_candidate_matching": "NOT RUN",
            "benchmark_files_opened": 0,
            "holdout_files_opened": 0,
        },
        "expanded_sealed_holdout_proposal": {
            "owners": [
                record(item) for item in EXPANDED_HOLDOUT_PROPOSAL
            ],
            "historical_public_proposal": (
                record(HISTORICAL_HOLDOUT_PROPOSAL)
            ),
            "proposal_status": "PRE-PHASE-3 PROPOSAL",
            "final_protocol_status": "NOT FROZEN",
            "case_count": 14155776,
            "historical_case_count": 4194304,
            "operation_count": 36,
            "pattern_family_count": 24,
            "subject_type_count": 4,
            "lifecycle_count": 4,
            "stratum_count": 13824,
            "cases_per_stratum": 1024,
            "candidate_participant_count": 3,
            "baseline_participant_count": 1,
            "qualified_independent_family_count": 0,
            "minimum_qualified_independent_family_count": 3,
            "secret_status": "NOT GENERATED",
            "case_status": "NOT GENERATED; NOT OPENED",
            "holdout_files_opened": 0,
            "benchmark_files_opened": 0,
            "timing_trials_run": 0,
            "proposal_verifier_executed": False,
        },
        "source_only_effects": {name: 0 for name in ZERO_KEYS},
        "corrected_original_matching": "NOT RUN",
        "corrected_supplemental_matching": "NOT RUN",
        "repaired_warning": "NOT MEASURED",
        "repaired_subinterpreter": "NOT MEASURED",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "qualified_candidate_count": 0,
        "current_qualified_candidates": 0,
        "minimum_qualified_candidates": 3,
        "holdout_case_count": 14155776,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def verify(source_sha, protocol_sha, contract_sha, *, active=False):
    state = context(source_sha, protocol_sha, active=active)
    info = os.stat(ROOT + "/" + CONTRACT, follow_symlinks=False)
    owner = (
        CONTRACT, pin(contract_sha, "contract"),
        info.st_size, info.st_ino,
    )
    raw = read_owner(owner)
    document = state["producer"].JsonReader(raw).parse()
    require(
        document == contract_value(source_sha, protocol_sha, state)
        and state["producer"].canonical(document) == raw,
        "reject a noncanonical or falsely measured complete V13 source freeze",
    )
    return state


def reject(operation, label):
    try:
        operation()
    except (
        CampaignError, OSError, ImportError, SyntaxError, ValueError,
        TypeError,
    ):
        return 1
    raise CampaignError("accepted a hostile V13 source-only control: " + label)

class SyntheticRelease:
    __slots__ = ("calls", "owner", "reenter", "failure")

    def __init__(self, *, reenter=False, failure=False):
        self.calls = []
        self.owner = None
        self.reenter = reenter
        self.failure = failure

    def __call__(self, handle):
        self.calls.append(handle)
        if self.reenter:
            self.reenter = False
            require(self.owner is not None, "missing synthetic owner")
            self.owner.__del__()
        if self.failure:
            raise SyntheticReleaseError("genuine synthetic release failure")

def synthetic_pattern(*, reenter=False, failure=False):
    release = SyntheticRelease(reenter=reenter, failure=failure)
    bridge = types.SimpleNamespace(free=release)
    namespace = {
        "__name__": "_rebar_zig_lifetime_v1_synthetic",
        "__builtins__": builtins.__dict__,
        "_zig_bridge": bridge,
        "getattr": builtins.getattr,
    }
    source = (
        "class SyntheticPattern:\n"
        "    __slots__ = ('_handle',)\n"
        + REPAIRED_DEALLOCATOR
    )
    synthetic_tree = ast.parse(source)
    synthetic_method = [
        node for node in synthetic_tree.body[0].body
        if isinstance(node, ast.FunctionDef)
        and node.name == "__del__"
    ]
    require(
        len(synthetic_method) == 1
        and ast.dump(
            synthetic_method[0], include_attributes=False,
        ) == ast.dump(
            ast.parse("class Pattern:\n" + REPAIRED_DEALLOCATOR)
            .body[0].body[0],
            include_attributes=False,
        ),
        "reject execution of an unauthenticated synthetic finalizer",
    )
    exec(
        compile(source, "<first-party-synthetic-lifetime-v1>", "exec",
                dont_inherit=True),
        namespace,
    )
    pattern = namespace["SyntheticPattern"]
    require(
        pattern.__del__.__defaults__ == (release, builtins.getattr)
        and pattern.__del__.__defaults__[0] is bridge.free
        and pattern.__del__.__defaults__[1] is builtins.getattr,
        "reject substituted definition-time lifetime defaults",
    )
    return pattern, release, namespace

def synthetic_lifetime_controls():
    checks = 0
    pattern, release, namespace = synthetic_pattern()
    target = pattern.__new__(pattern)
    target._handle = 71
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    target.__del__()
    require(
        release.calls == [71] and target._handle is None
        and pattern.__del__.__defaults__[0] is release
        and pattern.__del__.__defaults__[1] is builtins.getattr,
        "reject a first-party finalizer after module globals are destroyed",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [71] and target._handle is None,
        "reject double release after a successful finalizer",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    half = pattern.__new__(pattern)
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    half.__del__()
    half.__del__()
    require(
        release.calls == [] and not hasattr(half, "_handle"),
        "reject cleanup of a genuinely half-initialized pattern",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    for value in (None, 0, False):
        target = pattern.__new__(pattern)
        target._handle = value
        target.__del__()
    require(
        release.calls == [],
        "reject native cleanup for an absent or falsy handle",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern(reenter=True)
    target = pattern.__new__(pattern)
    target._handle = 103
    release.owner = target
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    target.__del__()
    release.owner = None
    require(
        release.calls == [103] and target._handle is None,
        "reject a reentrant double release",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern(failure=True)
    target = pattern.__new__(pattern)
    target._handle = 149
    namespace["_zig_bridge"] = None
    namespace["getattr"] = None
    try:
        target.__del__()
    except SyntheticReleaseError as error:
        require(
            str(error) == "genuine synthetic release failure",
            "reject a changed genuine cleanup error",
        )
    else:
        raise CampaignError("suppressed a genuine native-release failure")
    require(
        release.calls == [149] and target._handle is None,
        "reject uncleared ownership when genuine release fails",
    )
    checks += 1
    target.__del__()
    require(
        release.calls == [149],
        "reject retry or double release after a genuine failure",
    )
    checks += 1

    pattern, release, namespace = synthetic_pattern()
    original_callable = pattern.__del__.__defaults__[0]
    namespace["_zig_bridge"] = types.SimpleNamespace(
        free=lambda handle: (_ for _ in ()).throw(
            SyntheticReleaseError("poisoned module bridge"),
        ),
    )
    namespace["getattr"] = lambda *args: (_ for _ in ()).throw(
        SyntheticReleaseError("poisoned module getattr"),
    )
    target = pattern.__new__(pattern)
    target._handle = 211
    target.__del__()
    require(
        release.calls == [211]
        and pattern.__del__.__defaults__[0] is original_callable
        and target._handle is None,
        "reject a late rebound or poisoned finalizer module global",
    )
    checks += 1
    return checks

def altered_publication(receipt, *, field=None, value=None,
                        warning=False, child=False):
    changed = dict(receipt)
    if field is not None:
        changed[field] = value
    if warning or child:
        rows = list(receipt["original_suite_diagnostics"])
        index = 0 if warning else next(
            index for index, row in enumerate(rows)
            if row.get("suite") == "subinterpreter_v2"
        )
        row = dict(rows[index])
        if warning:
            excerpt = dict(row["stderr_literal_excerpt"])
            excerpt["text"] = "warning intentionally removed"
            row["stderr_literal_excerpt"] = excerpt
        else:
            nested = dict(row["complete_actual_suite_failure_details"])
            original = dict(nested["complete_original_failure_details"])
            original["actual_case_interpreter_exec_calls"] = 1
            nested["complete_original_failure_details"] = original
            row["complete_actual_suite_failure_details"] = nested
        rows[index] = row
        changed["original_suite_diagnostics"] = rows
    return changed

class CriticalSignals:
    """Block termination while the exact durable recovery state changes."""

    def __init__(self):
        self.signal = None
        self.previous = None

    def __enter__(self):
        self.signal = __import__("signal")
        require(callable(getattr(self.signal, "pthread_sigmask", None)),
                "require real POSIX recovery signal masking")
        mask = {
            getattr(self.signal, name)
            for name in ("SIGINT", "SIGTERM", "SIGHUP")
            if hasattr(self.signal, name)
        }
        require(bool(mask), "require independently real controller signals")
        self.previous = self.signal.pthread_sigmask(
            self.signal.SIG_BLOCK, mask)
        return self

    def __exit__(self, kind, value, trace):
        require(self.signal is not None and self.previous is not None,
                "reject a fabricated recovery signal state")
        self.signal.pthread_sigmask(
            self.signal.SIG_SETMASK, self.previous)
        return False


def private_owner(owner, role):
    expected = (PARENT_ADAPTER[1:3] if role == "adapter" else NATIVE[role])
    require(type(owner) is dict and type(owner.get("path")) is str
            and owner["path"].startswith(
                "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-")
            and "/reference-a/" in owner["path"]
            and owner.get("device") == PRIVATE_DEVICE
            and owner.get("uid") == os.geteuid()
            and owner.get("nlink") == 1
            and owner.get("sha256") == expected[0]
            and owner.get("bytes") == expected[1]
            and owner.get("mode") in ("0600", "0700"),
            "reject a crossed V13 actual private snapshot: " + role)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(owner["path"], flags)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == owner["device"]
                and info.st_ino == owner["inode"]
                and info.st_uid == owner["uid"] and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == int(owner["mode"], 8)
                and info.st_size == expected[1],
                "reject changed actual private V13 inode")
        parts, left = [], info.st_size
        while left:
            part = os.read(fd, min(left, 262144))
            require(bool(part), "reject truncated private V13 output")
            parts.append(part)
            left -= len(part)
        raw = b"".join(parts)
        require(not os.read(fd, 1) and digest(raw) == expected[0],
                "reject modified genuine private V13 native bytes")
        return raw
    finally:
        os.close(fd)


def target_identity(role, expected):
    path = ROOT + "/" + ORIGINALS[role]["relative"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = REAL_OPEN(path, flags)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == expected["device"]
                and info.st_ino == expected["inode"]
                and info.st_uid == expected["uid"]
                and info.st_nlink == expected["nlink"]
                and stat.S_IMODE(info.st_mode) == expected["mode"]
                and info.st_size == expected["bytes"],
                "reject a changed exact canonical Zig " + role)
        state, left = hashlib.sha256(), info.st_size
        while left:
            data = os.read(fd, min(left, 262144))
            require(bool(data), "reject truncated canonical role")
            state.update(data)
            left -= len(data)
        require(not os.read(fd, 1) and state.hexdigest() == expected["sha256"],
                "reject changed complete canonical role bytes")
        return dict(expected)
    finally:
        os.close(fd)


def exclusive(directory, name, data):
    require(type(name) is str and "/" not in name and name not in ("", ".", ".."),
            "reject a nonlocal exclusive owner")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
    fd = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        pending = memoryview(data)
        while pending:
            wrote = os.write(fd, pending)
            require(type(wrote) is int and wrote > 0,
                    "reject incomplete durable stage")
            pending = pending[wrote:]
        os.fsync(fd)
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode)
                and info.st_uid == os.geteuid() and info.st_nlink == 1
                and stat.S_IMODE(info.st_mode) == 0o600
                and info.st_size == len(data),
                "reject an unsafe staged owner")
        result = {"name": name, "sha256": digest(data),
                  "bytes": info.st_size, "device": info.st_dev,
                  "inode": info.st_ino, "mode": 0o600,
                  "uid": info.st_uid, "nlink": info.st_nlink}
    finally:
        os.close(fd)
    os.fsync(directory)
    return result


def recovery_directory(create):
    require(os.path.dirname(RECOVERY) == "/tmp"
            and RECOVERY.startswith("/tmp/rebar-phase2-repaired-zig-"),
            "reject an unsafe recovery-root target")
    if create:
        try:
            os.mkdir(RECOVERY, 0o700)
        except FileExistsError:
            pass
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(RECOVERY, flags)
    try:
        info = os.fstat(directory)
        require(stat.S_ISDIR(info.st_mode)
                and stat.S_IMODE(info.st_mode) == 0o700
                and info.st_uid == os.geteuid(),
                "reject a shared or substituted recovery root")
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT
        lock = os.open("campaign-v13.lock", flags, 0o600, dir_fd=directory)
        try:
            owner = os.fstat(lock)
            require(stat.S_ISREG(owner.st_mode)
                    and stat.S_IMODE(owner.st_mode) == 0o600
                    and owner.st_uid == os.geteuid()
                    and owner.st_nlink == 1,
                    "reject a foreign recovery lock")
            fcntl = __import__("fcntl")
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(lock)
            raise
        return directory, lock
    except BaseException:
        os.close(directory)
        raise


def names(role):
    require(role in ROLES, "reject a crossed activation role")
    stem = ".rebar-zig-guard-clean-lifetime-v13-" + role
    return stem + ".stage", stem + ".original"


def candidate_directory():
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    fd = os.open(ROOT + "/candidates", flags)
    info = os.fstat(fd)
    require(stat.S_ISDIR(info.st_mode) and info.st_dev == DEVICE
            and info.st_uid == os.geteuid(),
            "reject a substituted candidates directory")
    return fd


def prepare(state):
    for role in ROLES:
        target_identity(role, ORIGINALS[role])
    phase = state["build"]["complete_actual_build"]["build_phases"][0]
    data = {}
    for role in ROLES:
        if role == "adapter":
            data[role] = read_owner(LIFETIME_ADAPTER)
            require(
                state["proof"].get("complete_other_ast_unchanged") is True
                and state["proof"].get("changed_ast_node_count") == 1
                and digest(data[role]) == LIFETIME_ADAPTER[1],
                "reject altered independently source-owned lifetime adapter",
            )
        else:
            data[role] = private_owner(
                phase["native_outputs"][role]["owner"], role)
    recovery_fd, lock_fd = recovery_directory(True)
    candidate_fd = candidate_directory()
    journal = None
    stages = {}
    try:
        for role in ROLES:
            stage, _ = names(role)
            stages[role] = exclusive(candidate_fd, stage, data[role])
            expected = LIFETIME_ADAPTER[1] if role == "adapter" else NATIVE[role][0]
            require(stages[role]["device"] == DEVICE
                    and stages[role]["sha256"] == expected,
                    "require exact mode-0600 repository-device native stages")
        producer = state["producer"]
        journal = {
            "schema": SCHEMA + "-three-role-journal", "status": "PREPARED",
            "family": FAMILY, "label": LABEL, "build_label": BUILD_LABEL,
            "build_receipt_sha256": V13[3][1],
            "root_receipt_sha256": V13[4][1],
            "recovery_root": RECOVERY, "role_order": list(ROLES),
            "restoration_order": list(RESTORE), "atomic_group": False,
            "lifetime_adapter_sha256": LIFETIME_ADAPTER[1],
            "roles": {
                role: {"original": ORIGINALS[role],
                       "stage": stages[role], "backup_name": names(role)[1],
                       "stage_name": names(role)[0]}
                for role in ROLES
            },
        }
        with CriticalSignals():
            journal_owner = exclusive(
                recovery_fd, "recovery-journal.json",
                producer.canonical(journal))
            journal["published_journal"] = journal_owner
            for role in ROLES:
                target = ORIGINALS[role]["relative"].rsplit("/", 1)[1]
                stage, backup = names(role)
                os.link(target, backup, src_dir_fd=candidate_fd,
                        dst_dir_fd=candidate_fd, follow_symlinks=False)
                os.fsync(candidate_fd)
                os.replace(stage, target, src_dir_fd=candidate_fd,
                           dst_dir_fd=candidate_fd)
                os.fsync(candidate_fd)
                exclusive(recovery_fd, "activation-" + role + ".json",
                          producer.canonical({
                              "schema": SCHEMA + "-activation-step",
                              "status": "PASS", "role": role,
                              "journal_sha256": journal_owner["sha256"],
                          }))
        return recovery_fd, lock_fd, candidate_fd, journal
    except BaseException as primary:
        recovery_failure = None
        try:
            if journal is not None:
                with CriticalSignals():
                    restore(candidate_fd, journal)
            for role, stage in stages.items():
                stage_name, _backup = names(role)
                try:
                    info = os.stat(stage_name, dir_fd=candidate_fd,
                                   follow_symlinks=False)
                except FileNotFoundError:
                    continue
                require(info.st_dev == stage["device"]
                        and info.st_ino == stage["inode"]
                        and stat.S_IMODE(info.st_mode) == 0o600
                        and info.st_uid == os.geteuid()
                        and info.st_nlink == 1,
                        "refuse cleanup of an unrelated user-owned stage")
                os.unlink(stage_name, dir_fd=candidate_fd)
                os.fsync(candidate_fd)
        except BaseException as error:
            recovery_failure = error
        finally:
            os.close(candidate_fd)
            os.close(lock_fd)
            os.close(recovery_fd)
        if recovery_failure is not None:
            raise CampaignError(
                "actual activation failed and exact three-role recovery "
                "requires the published recovery journal: "
                + type(recovery_failure).__qualname__ + ": "
                + str(recovery_failure)
            ) from primary
        raise


def restore(candidate_fd, journal):
    require(journal.get("schema") == SCHEMA + "-three-role-journal"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("role_order") == list(ROLES)
            and journal.get("restoration_order") == list(RESTORE)
            and set(journal.get("roles", {})) == set(ROLES),
            "reject unauthenticated three-role recovery")
    result = []
    for role in RESTORE:
        entry = journal["roles"][role]
        _, backup = names(role)
        require(entry["original"] == ORIGINALS[role]
                and entry["backup_name"] == backup,
                "reject crossed original backup identity")
        try:
            info = os.stat(backup, dir_fd=candidate_fd, follow_symlinks=False)
        except FileNotFoundError:
            result.append(target_identity(role, ORIGINALS[role]))
            continue
        original = ORIGINALS[role]
        require(stat.S_ISREG(info.st_mode)
                and info.st_dev == original["device"]
                and info.st_ino == original["inode"]
                and info.st_uid == original["uid"]
                and stat.S_IMODE(info.st_mode) == original["mode"],
                "reject a substituted exact original-inode hardlink")
        os.replace(backup, original["relative"].rsplit("/", 1)[1],
                   src_dir_fd=candidate_fd, dst_dir_fd=candidate_fd)
        os.fsync(candidate_fd)
        result.append(target_identity(role, original))
    require(len(result) == 3,
            "require exact restoration of all three original source/native owners")
    for role in ROLES:
        stage_name, _backup = names(role)
        try:
            actual = os.stat(stage_name, dir_fd=candidate_fd,
                             follow_symlinks=False)
        except FileNotFoundError:
            continue
        stage = journal["roles"][role]["stage"]
        require(stat.S_ISREG(actual.st_mode)
                and actual.st_dev == stage["device"]
                and actual.st_ino == stage["inode"]
                and actual.st_uid == stage["uid"]
                and actual.st_nlink == 1
                and stat.S_IMODE(actual.st_mode) == 0o600
                and actual.st_size == stage["bytes"],
                "refuse to remove an unrelated user-owned recovery stage")
        os.unlink(stage_name, dir_fd=candidate_fd)
        os.fsync(candidate_fd)
    return result



def active_owner(role, staged):
    require(
        role in ROLES and type(staged) is dict,
        "reject an unselected exact canonical lifetime/native role",
    )
    expected_hash, expected_size = (
        (LIFETIME_ADAPTER[1], LIFETIME_ADAPTER[2])
        if role == "adapter" else NATIVE[role]
    )
    expected = {
        "relative": ORIGINALS[role]["relative"],
        "sha256": expected_hash,
        "bytes": expected_size,
        "device": DEVICE,
        "inode": staged["inode"],
        "mode": 0o600,
        "uid": os.geteuid(),
        "nlink": 1,
    }
    target_identity(role, expected)
    owner = {
        "family": FAMILY,
        "role": role,
        "absolute_path": ROOT + "/" + expected["relative"],
        **expected,
        "file_name": expected["relative"].rsplit("/", 1)[-1],
        "size_bytes": expected_size,
        "native_loaded": False,
    }
    require(
        set(owner) == REQUIRED_NATIVE_OWNER_FIELDS
        and owner["bytes"] == owner["size_bytes"]
        and owner["absolute_path"] == ROOT + "/" + owner["relative"]
        and owner["native_loaded"] is False,
        "reject missing, extra, crossed, or preloaded V3 native owner fields",
    )
    return owner

def read_live_journal(producer, expected_sha):
    expected_sha = pin(expected_sha, "recovery journal")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_DIRECTORY", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(RECOVERY, flags)
    try:
        root = os.fstat(directory)
        require(stat.S_ISDIR(root.st_mode)
                and stat.S_IMODE(root.st_mode) == 0o700
                and root.st_uid == os.geteuid(),
                "reject a substituted read-only actual recovery root")
        file_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                      | getattr(os, "O_NOFOLLOW", 0))
        fd = os.open("recovery-journal.json", file_flags, dir_fd=directory)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode)
                    and stat.S_IMODE(info.st_mode) == 0o600
                    and info.st_uid == os.geteuid()
                    and info.st_nlink == 1
                    and 0 < info.st_size < MAX_BYTES,
                    "reject an unsafe original three-role journal")
            pieces, left = [], info.st_size
            while left:
                chunk = os.read(fd, min(left, 262144))
                require(bool(chunk), "reject a truncated live journal")
                pieces.append(chunk)
                left -= len(chunk)
            raw = b"".join(pieces)
            require(not os.read(fd, 1) and digest(raw) == expected_sha,
                    "reject an unannounced actual three-role journal")
        finally:
            os.close(fd)
    finally:
        os.close(directory)
    journal = producer.JsonReader(raw).parse()
    require(journal.get("schema") == SCHEMA + "-three-role-journal"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("build_receipt_sha256") == V13[3][1]
            and journal.get("root_receipt_sha256") == V13[4][1]
            and journal.get("lifetime_adapter_sha256") == LIFETIME_ADAPTER[1]
            and journal.get("role_order") == list(ROLES)
            and journal.get("restoration_order") == list(RESTORE)
            and set(journal.get("roles", {})) == set(ROLES),
            "reject fabricated or crossed actual activation")
    return journal


def reject_dynamic_historical_ctypes(tree):
    require(isinstance(tree, ast.AST),
            "require a complete authenticated historical source tree")
    for item in ast.walk(tree):
        if isinstance(item, ast.ImportFrom):
            require(
                not (
                    isinstance(item.module, str)
                    and (
                        item.module == "ctypes"
                        or item.module.startswith("ctypes.")
                    )
                ),
                "reject any historical from-ctypes delegation",
            )
        elif isinstance(item, ast.Import):
            for alias in item.names:
                if alias.name == "ctypes" or alias.name.startswith("ctypes."):
                    require(
                        item in getattr(tree, "body", ())
                        and len(item.names) == 1
                        and alias.name == "ctypes"
                        and alias.asname is None,
                        "reject aliased, nested, or additional ctypes imports",
                    )
        elif isinstance(item, ast.Call) and item.args:
            first = item.args[0]
            if (
                isinstance(first, ast.Constant)
                and isinstance(first.value, str)
                and (
                    first.value == "ctypes"
                    or first.value.startswith("ctypes.")
                )
            ):
                direct = (
                    isinstance(item.func, ast.Name)
                    and item.func.id == "__import__"
                )
                indirect = (
                    isinstance(item.func, ast.Attribute)
                    and item.func.attr == "import_module"
                )
                require(
                    not (direct or indirect),
                    "reject a dynamic historical ctypes import",
                )


def clean_historical_zig_v4(raw):
    require(
        type(raw) is bytes
        and len(raw) == LEGACY_V4_SOURCE[2]
        and digest(raw) == LEGACY_V4_SOURCE[1],
        "authenticate exact immutable historical V4 producer source",
    )
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=LEGACY_V4_SOURCE[0])
    reject_dynamic_historical_ctypes(tree)
    imports = [
        node for node in tree.body
        if isinstance(node, ast.Import)
        and any(alias.name == "ctypes" for alias in node.names)
    ]
    require(
        len(imports) == 1
        and imports[0].lineno == 21
        and imports[0].end_lineno == 21
        and imports[0].col_offset == 0
        and len(imports[0].names) == 1
        and imports[0].names[0].name == "ctypes"
        and imports[0].names[0].asname is None,
        "reject any additional or relocated historical ctypes import",
    )
    lines = text.splitlines(keepends=True)
    require(
        len(lines) >= 21
        and lines[20] in ("import ctypes\n", "import ctypes\r\n"),
        "require the independently pinned historical ctypes source line",
    )
    fixed = (
        "".join(lines[:20])
        + FORBIDDEN_LEGACY_CTYPES_PROXY
        + "".join(lines[21:])
    ).encode("utf-8")
    cleaned = ast.parse(
        fixed.decode("utf-8"), filename=LEGACY_V4_SOURCE[0]
    )
    reject_dynamic_historical_ctypes(cleaned)
    require(
        not any(
            isinstance(node, (ast.Import, ast.ImportFrom))
            and (
                (
                    isinstance(node, ast.Import)
                    and any(
                        entry.name == "ctypes"
                        or entry.name.startswith("ctypes.")
                        for entry in node.names
                    )
                )
                or (
                    isinstance(node, ast.ImportFrom)
                    and isinstance(node.module, str)
                    and (
                        node.module == "ctypes"
                        or node.module.startswith("ctypes.")
                    )
                )
            )
            for node in ast.walk(cleaned)
        ),
        "reject residual historical ctypes package imports",
    )
    return fixed


def clean_original_zig_harness(raw):
    require(
        type(raw) is bytes
        and len(raw) == ORIGINAL_HARNESS_SOURCE[2]
        and digest(raw) == ORIGINAL_HARNESS_SOURCE[1],
        "authenticate exact immutable original upstream harness source",
    )
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=ORIGINAL_HARNESS_SOURCE[0])
    functions = [
        item for item in tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == "authenticate_original_sources"
    ]
    require(
        len(functions) == 1
        and len(functions[0].body) >= 1,
        "reject crossed original source authentication",
    )
    statement = functions[0].body[0]
    require(
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Call)
        and isinstance(statement.value.func, ast.Name)
        and statement.value.func.id == "verify_runtime"
        and not statement.value.args
        and not statement.value.keywords
        and statement.lineno == 211
        and statement.end_lineno == 211,
        "replace only the exact original Rust-only runtime classification",
    )
    lines = text.splitlines(keepends=True)
    require(
        lines[210] in (
            "    verify_runtime()\n",
            "    verify_runtime()\r\n",
        ),
        "reject a changed original source-authentication runtime call",
    )
    ending = "\r\n" if lines[210].endswith("\r\n") else "\n"
    lines[210] = "    verify_runtime(candidate=True)" + ending
    fixed = "".join(lines).encode("utf-8")
    parsed = ast.parse(
        fixed.decode("utf-8"),
        filename=ORIGINAL_HARNESS_SOURCE[0],
    )
    statement.value.keywords = [
        ast.keyword(arg="candidate", value=ast.Constant(value=True))
    ]
    require(
        ast.dump(tree, include_attributes=False)
        == ast.dump(parsed, include_attributes=False),
        "reject changes beyond the exact original family classification",
    )
    return fixed



def clean_original_zig_direct_core(raw):
    require(
        type(raw) is bytes
        and len(raw) == DIRECT_CORE_SOURCE[2]
        and digest(raw) == DIRECT_CORE_SOURCE[1],
        "authenticate exact immutable original public direct-core source",
    )
    text = raw.decode("utf-8", "strict")
    tree = ast.parse(text, filename=DIRECT_CORE_SOURCE[0])
    functions = [
        item for item in tree.body
        if isinstance(item, ast.FunctionDef)
        and item.name == "load_prerequisites"
    ]
    require(
        len(functions) == 1 and bool(functions[0].body),
        "reject a substituted original direct-core source function",
    )
    statement = functions[0].body[0]
    require(
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Call)
        and isinstance(statement.value.func, ast.Name)
        and statement.value.func.id == "verify_runtime"
        and not statement.value.args
        and not statement.value.keywords
        and statement.lineno == 483
        and statement.end_lineno == 483,
        "change only the exact original-only direct-core runtime call",
    )
    lines = text.splitlines(keepends=True)
    require(
        len(lines) >= 483
        and lines[482] in (
            "    verify_runtime()\n",
            "    verify_runtime()\r\n",
        ),
        "reject a changed immutable direct-core runtime source line",
    )
    ending = "\r\n" if lines[482].endswith("\r\n") else "\n"
    lines[482] = "    verify_runtime(candidate_loaded=True)" + ending
    fixed = "".join(lines).encode("utf-8")
    checked = ast.parse(fixed.decode("utf-8"), filename=DIRECT_CORE_SOURCE[0])
    statement.value.keywords = [
        ast.keyword(
            arg="candidate_loaded",
            value=ast.Constant(value=True),
        )
    ]
    require(
        ast.dump(tree, include_attributes=False)
        == ast.dump(checked, include_attributes=False),
        "reject any direct-core case, observer, guard, or vector change",
    )
    return fixed


def install_authenticated_zig_direct_core(
    gate,
    producer,
    selected,
    policy,
    counts,
):
    require(
        type(gate) is types.ModuleType
        and getattr(gate, "CORE_RELATIVE", None)
        == DIRECT_CORE_SOURCE[0]
        and getattr(gate, "CORE_SHA256", None)
        == DIRECT_CORE_SOURCE[1]
        and tuple(producer.DIRECT_GATE_OWNER) == DIRECT_GATE_SOURCE
        and producer.family_spec(FAMILY) is selected
        and producer.require_selected(selected) is policy.selected
        and policy.installed is True
        and policy.selected is sys.modules.get("re")
        and sys.modules.get("re")
        is sys.modules.get("candidates.zig_candidate")
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules,
        "bind the original direct gate only to authenticated guarded Zig",
    )
    original_resolver = gate.source_module_for_core

    def guarded_source_module_for_core(spec):
        require(
            getattr(spec, "name", None)
            in {"public_v3", "scanner_v3", "buffer_v3"}
            and producer.family_spec(FAMILY) is selected
            and producer.require_selected(selected) is policy.selected
            and policy.installed is True
            and policy.selected is sys.modules.get("re")
            and sys.modules.get("re")
            is sys.modules.get("candidates.zig_candidate")
            and "_sre" not in sys.modules
            and "ctypes" not in sys.modules,
            "reject a crossed or unguarded original direct-core overlay",
        )
        core, category = original_resolver(spec)
        require(
            type(core) is types.ModuleType
            and core.__name__ == "tools.independent_public_contract_v3"
            and core.__file__ == ROOT + "/" + DIRECT_CORE_SOURCE[0]
            and sys.modules.get(core.__name__) is core
            and getattr(core, "SOURCE_RELATIVE", None)
            == DIRECT_CORE_SOURCE[0]
            and getattr(category, "case_count", None)
            == getattr(spec, "case_count", None)
            and getattr(category, "matrix_sha256", None)
            == getattr(spec, "matrix_sha256", None)
            and callable(getattr(core, "load_prerequisites", None))
            and core.load_prerequisites.__globals__ is core.__dict__,
            "authenticate the exact original direct-core module and case",
        )
        fixed = clean_original_zig_direct_core(
            read_owner(DIRECT_CORE_SOURCE)
        )
        parsed = ast.parse(
            fixed.decode("utf-8"),
            filename=DIRECT_CORE_SOURCE[0],
        )
        definitions = [
            item for item in parsed.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "load_prerequisites"
        ]
        require(
            len(definitions) == 1,
            "reject a duplicated corrected original direct-core function",
        )
        fragment = ast.Module(body=definitions, type_ignores=[])
        namespace = {}
        exec(
            compile(
                fragment,
                ROOT + "/" + DIRECT_CORE_SOURCE[0],
                "exec",
                dont_inherit=True,
            ),
            core.__dict__,
            namespace,
        )
        corrected = namespace.get("load_prerequisites")
        require(
            type(corrected) is types.FunctionType
            and corrected.__module__ == core.__name__
            and corrected.__name__ == "load_prerequisites"
            and corrected.__globals__ is core.__dict__
            and producer.family_spec(FAMILY) is selected
            and producer.require_selected(selected) is policy.selected
            and "_sre" not in sys.modules
            and "ctypes" not in sys.modules,
            "reject a delegated or non-original direct-core function",
        )
        core.load_prerequisites = corrected
        counts["direct_core_family_overlays"] += 1
        return core, category

    gate.source_module_for_core = guarded_source_module_for_core
    counts["direct_gate_source_proxies"] += 1
    require(
        gate.source_module_for_core is guarded_source_module_for_core
        and producer.family_spec(FAMILY) is selected
        and producer.require_selected(selected) is policy.selected
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules,
        "reject an unguarded original direct-gate source proxy",
    )
    return gate


def install_authenticated_zig_observer_proxy(
    producer,
    selected,
    policy,
):
    require(
        type(producer) is types.ModuleType
        and producer.SCHEMA
        == "rebar-owned-six-family-original-p0-producer-v5"
        and producer.family_spec(FAMILY).module
        == "candidates.zig_candidate"
        and type(selected) is producer.FamilySpec
        and selected.name == FAMILY
        and selected.module == "candidates.zig_candidate"
        and selected.adapter_relative == ORIGINAL_ADAPTER[0]
        and selected.bridge_module == "candidates._zig_bridge"
        and selected.engine_relative == "candidates/_zig_probe.so"
        and selected.combined_native is False
        and selected.owned_ctypes is False
        and producer.require_selected(selected)
        is sys.modules.get("candidates.zig_candidate")
        and policy.installed is True
        and policy.selected is sys.modules.get("re")
        and sys.modules.get("re")
        is sys.modules.get("candidates.zig_candidate")
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules,
        "bind an in-memory observer proxy only to genuine guarded "
        "first-party Zig",
    )
    actual_owners = (
        (ORIGINAL_ADAPTER[0], LIFETIME_ADAPTER[1], LIFETIME_ADAPTER[2]),
        (ENGINE_SOURCE[0], ENGINE_SOURCE[1], ENGINE_SOURCE[2]),
        (BRIDGE_SOURCE[0], BRIDGE_SOURCE[1], BRIDGE_SOURCE[2]),
    )
    require(
        selected.source_owners == actual_owners
        and tuple(producer.V4_OWNERS[0]) == LEGACY_V4_SOURCE
        and tuple(producer.HARNESS_OWNER) == ORIGINAL_HARNESS_SOURCE
        and tuple(producer.DIRECT_GATE_OWNER) == DIRECT_GATE_SOURCE,
        "reject an unpinned historical producer or first-party adapter",
    )
    old_load = producer.load_module
    other_families = {
        name: producer.FAMILIES[name]
        for name in producer.FAMILIES
        if name != FAMILY
    }
    producer.OWNED_SOURCES[FAMILY] = actual_owners
    producer.FAMILIES[FAMILY] = selected
    require(
        producer.family_spec(FAMILY) is selected
        and all(
            producer.FAMILIES[name] is value
            for name, value in other_families.items()
        )
        and "ctypes" not in sys.modules,
        "modify only the selected authenticated V5 Zig family",
    )
    counts = {
        "historical_v4_source_transforms": 0,
        "original_harness_source_transforms": 0,
        "historical_zig_family_overlays": 0,
        "direct_gate_source_proxies": 0,
        "direct_core_family_overlays": 0,
    }

    def guarded_loader(item, name):
        if item not in (
            LEGACY_V4_SOURCE,
            ORIGINAL_HARNESS_SOURCE,
            DIRECT_GATE_SOURCE,
        ):
            return old_load(item, name)
        require(
            type(name) is str
            and (
                (
                    item == LEGACY_V4_SOURCE
                    and (
                        name.startswith(
                            "_rebar_v5_legacy_producer_zig_"
                        )
                        or name
                        == "_rebar_v5_guarded_nested_legacy_zig"
                    )
                )
                or (
                    item == ORIGINAL_HARNESS_SOURCE
                    and name == "_rebar_v5_original_harness_zig"
                )
                or (
                    item == DIRECT_GATE_SOURCE
                    and name.startswith("_rebar_v5_direct_gate_zig_")
                )
            )
            and producer.family_spec(FAMILY) is selected
            and producer.require_selected(selected)
            is policy.selected
            and "ctypes" not in sys.modules
            and "_sre" not in sys.modules,
            "reject a crossed, unguarded, or delegated observer loader",
        )
        previous_read = producer.read_owner

        def guarded_read(owner, *args, **kwargs):
            raw = previous_read(owner, *args, **kwargs)
            if owner == LEGACY_V4_SOURCE:
                counts["historical_v4_source_transforms"] += 1
                return clean_historical_zig_v4(raw)
            if owner == ORIGINAL_HARNESS_SOURCE:
                counts["original_harness_source_transforms"] += 1
                return clean_original_zig_harness(raw)
            return raw

        producer.read_owner = guarded_read
        try:
            loaded = old_load(item, name)
        finally:
            producer.read_owner = previous_read
        require(
            "ctypes" not in sys.modules
            and producer.require_selected(selected)
            is policy.selected,
            "reject a historical loader that weakens strict isolation",
        )
        if item == DIRECT_GATE_SOURCE:
            return install_authenticated_zig_direct_core(
                loaded,
                producer,
                selected,
                policy,
                counts,
            )
        if item == LEGACY_V4_SOURCE:
            previous_family = loaded.family_spec
            legacy = loaded.family_spec(FAMILY)
            require(
                legacy.name == FAMILY
                and legacy.module == selected.module
                and legacy.bridge_module == selected.bridge_module
                and legacy.adapter_relative == selected.adapter_relative
                and legacy.combined_native is False
                and legacy.owned_ctypes is True,
                "reject a changed historical Zig ownership contract",
            )
            corrected = loaded.FamilySpec(
                selected.name,
                selected.module,
                selected.adapter_relative,
                selected.bridge_module,
                selected.engine_relative,
                selected.bridge_relative,
                actual_owners,
                False,
                False,
            )
            loaded.OWNED_SOURCES[FAMILY] = actual_owners
            loaded.FAMILIES[FAMILY] = corrected

            def guarded_family(value):
                if value != FAMILY:
                    return previous_family(value)
                require(
                    loaded.FAMILIES[FAMILY] is corrected
                    and loaded.OWNED_SOURCES[FAMILY] == actual_owners
                    and producer.family_spec(FAMILY) is selected
                    and producer.require_selected(selected)
                    is policy.selected
                    and "_sre" not in sys.modules
                    and "ctypes" not in sys.modules,
                    "reject an unguarded historical Zig family overlay",
                )
                return corrected

            loaded.family_spec = guarded_family
            require(
                loaded.family_spec(FAMILY) is corrected
                and corrected.owned_ctypes is False
                and corrected.source_owners == actual_owners,
                "require exact first-party historical Zig provenance",
            )
            counts["historical_zig_family_overlays"] += 1
        return loaded

    producer.load_module = guarded_loader
    require(
        producer.load_module is guarded_loader
        and producer.read_owner is not guarded_loader
        and producer.family_spec(FAMILY) is selected
        and all(
            producer.FAMILIES[name] is value
            for name, value in other_families.items()
        )
        and "ctypes" not in sys.modules,
        "require an authenticated Zig-only fail-closed loader proxy",
    )
    return counts


def authenticated_first_party_namespace(path=ROOT):
    require(
        type(path) is str
        and path == ROOT
        and path == "/home/dev-user/src/rebar"
        and sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.flags.dont_write_bytecode == 1,
        "reject an unpinned, relative, environment-derived, or "
        "non-isolated first-party package root",
    )
    root = os.stat(path, follow_symlinks=False)
    namespace_path = path + "/candidates"
    namespace = os.stat(namespace_path, follow_symlinks=False)
    adapter_path = namespace_path + "/zig_candidate.py"
    adapter = os.stat(adapter_path, follow_symlinks=False)
    uid = os.geteuid()
    require(
        stat.S_ISDIR(root.st_mode)
        and root.st_dev == DEVICE
        and root.st_ino == REPOSITORY_ROOT_INODE
        and stat.S_IMODE(root.st_mode) == REPOSITORY_ROOT_MODE
        and root.st_uid == uid
        and stat.S_ISDIR(namespace.st_mode)
        and namespace.st_dev == DEVICE
        and namespace.st_ino == CANDIDATE_NAMESPACE_INODE
        and stat.S_IMODE(namespace.st_mode) == CANDIDATE_NAMESPACE_MODE
        and namespace.st_uid == uid
        and stat.S_ISREG(adapter.st_mode)
        and adapter.st_dev == DEVICE
        and stat.S_IMODE(adapter.st_mode) == 0o600
        and adapter.st_uid == uid
        and adapter.st_nlink == 1,
        "reject a substituted, symlinked, foreign, or unowned "
        "first-party namespace",
    )
    finder = importlib._bootstrap_external.PathFinder
    require(
        finder in sys.meta_path
        and finder.__module__ == "_frozen_importlib_external"
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject a replaced finder or preloaded matching package",
    )
    package = finder.find_spec("candidates", [path])
    require(
        package is not None
        and package.name == "candidates"
        and package.loader is None
        and package.origin is None
        and tuple(package.submodule_search_locations or ())
        == (namespace_path,),
        "reject a foreign or noncanonical PEP 420 namespace",
    )
    candidate = finder.find_spec(
        "candidates.zig_candidate", [namespace_path]
    )
    require(
        candidate is not None
        and candidate.name == "candidates.zig_candidate"
        and candidate.origin == adapter_path
        and type(candidate.loader).__module__
        == "_frozen_importlib_external"
        and type(candidate.loader).__name__ == "SourceFileLoader"
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules,
        "reject a crossed candidate source without importing it",
    )
    return {
        "root": path,
        "namespace": namespace_path,
        "adapter": adapter_path,
        "root_inode": root.st_ino,
        "namespace_inode": namespace.st_ino,
    }


def prepend_authenticated_first_party_namespace(owner):
    require(
        type(owner) is dict
        and owner.get("root") == ROOT
        and owner.get("namespace") == ROOT + "/candidates"
        and owner.get("adapter") == ROOT + "/candidates/zig_candidate.py"
        and owner.get("root_inode") == REPOSITORY_ROOT_INODE
        and owner.get("namespace_inode") == CANDIDATE_NAMESPACE_INODE
        and type(sys.path) is list
        and all(type(item) is str for item in sys.path)
        and ROOT not in sys.path
        and "" not in sys.path
        and "." not in sys.path
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject a duplicate, relative, preloaded, or foreign package path",
    )
    before = tuple(sys.path)
    sys.path.insert(0, ROOT)
    require(
        sys.path[0] == ROOT
        and tuple(sys.path[1:]) == before,
        "prepend only the exact authenticated repository root",
    )
    finder = importlib._bootstrap_external.PathFinder
    package = finder.find_spec("candidates", None)
    require(
        package is not None
        and package.name == "candidates"
        and package.loader is None
        and package.origin is None
        and tuple(package.submodule_search_locations or ())
        == (ROOT + "/candidates",)
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "reject first-party namespace resolution or a guard bypass",
    )
    return owner


def bounded_literal(value, maximum):
    require(type(maximum) is int and maximum > 0,
            "reject an unbounded diagnostic excerpt")
    if type(value) is str:
        raw = value.encode("utf-8", "backslashreplace")
    else:
        require(type(value) is bytes,
                "reject a fabricated nonliteral diagnostic excerpt")
        raw = value
    captured = raw[:maximum]
    return {
        "text": captured.decode("utf-8", "backslashreplace"),
        "total_bytes": len(raw),
        "captured_bytes": len(captured),
        "limit_bytes": maximum,
        "truncated": len(raw) > maximum,
        "sha256": digest(raw),
        "encoding": "UTF-8; INVALID BYTES BACKSLASH-ESCAPED",
    }


def literal_stderr(value, reason=None):
    if value is None:
        require(type(reason) is str and bool(reason),
                "require a genuine reason for unavailable worker stderr")
        return {
            "status": "NOT AVAILABLE",
            "reason": bounded_literal(reason, MAX_FAILURE_MESSAGE_BYTES),
            "text": None,
            "total_bytes": "NOT MEASURED",
            "captured_bytes": 0,
            "limit_bytes": MAX_PUBLIC_STDERR_BYTES,
            "truncated": "NOT MEASURED",
            "sha256": "NOT MEASURED",
            "encoding": "NOT MEASURED",
        }
    require(type(value) is bytes,
            "preserve only genuine complete captured worker stderr")
    return {
        "status": "CAPTURED",
        **bounded_literal(value, MAX_PUBLIC_STDERR_BYTES),
    }


def failure_details(error, stage):
    require(isinstance(error, BaseException)
            and type(stage) is str and bool(stage),
            "capture only genuine stage-attributed exceptions")
    kind = type(error)
    qualified = kind.__module__ + "." + kind.__qualname__
    try:
        message = str(error)
    except BaseException as secondary:
        other = type(secondary)
        message = (
            "<exception string failed: "
            + other.__module__ + "." + other.__qualname__ + ">"
        )
    bounded_message = bounded_literal(
        message, MAX_FAILURE_MESSAGE_BYTES
    )
    frames = []
    trace = error.__traceback__
    while trace is not None and len(frames) < MAX_FAILURE_TRACEBACK_FRAMES:
        frame = trace.tb_frame
        frames.append({
            "file": bounded_literal(
                frame.f_code.co_filename, MAX_FAILURE_MESSAGE_BYTES
            )["text"],
            "function": bounded_literal(
                frame.f_code.co_name, MAX_FAILURE_MESSAGE_BYTES
            )["text"],
            "line": trace.tb_lineno,
        })
        trace = trace.tb_next
    lines = ["Traceback (most recent call last):"]
    for frame in frames:
        lines.append(
            '  File "' + frame["file"] + '", line '
            + str(frame["line"]) + ", in " + frame["function"]
        )
    if trace is not None:
        lines.append("  ... additional traceback frames omitted")
    lines.append(qualified + ": " + bounded_message["text"])
    return {
        "activation_stage": stage,
        "error_type": kind.__qualname__,
        "error_class": qualified,
        "error_message": bounded_message["text"],
        "error_message_detail": bounded_message,
        "error_traceback": bounded_literal(
            "\n".join(lines), MAX_FAILURE_TRACEBACK_BYTES
        ),
        "traceback_frames": frames,
        "traceback_frames_truncated": trace is not None,
    }


def worker_quote(value):
    require(type(value) is str, "quote only canonical worker strings")
    output = ['"']
    escapes = {
        "\\": "\\\\", '"': '\\"', "\b": "\\b", "\f": "\\f",
        "\n": "\\n", "\r": "\\r", "\t": "\\t",
    }
    for character in value:
        if character in escapes:
            output.append(escapes[character])
        elif ord(character) < 32:
            output.append("\\u" + format(ord(character), "04x"))
        elif ord(character) > 127:
            point = ord(character)
            if point <= 0xffff:
                output.append("\\u" + format(point, "04x"))
            else:
                point -= 0x10000
                output.append(
                    "\\u" + format(0xd800 + (point >> 10), "04x")
                )
                output.append(
                    "\\u" + format(0xdc00 + (point & 0x3ff), "04x")
                )
        else:
            output.append(character)
    output.append('"')
    return "".join(output)




def worker_has_surrogate(value):
    require(
        type(value) is str,
        "inspect only an exact first-party worker Unicode value",
    )
    return any(
        0xD800 <= ord(character) <= 0xDFFF
        for character in value
    )


def worker_unicode_chunks(value):
    require(
        type(value) is str and worker_has_surrogate(value),
        "tag only actual worker strings containing surrogate code units",
    )
    chunks = []
    start = 0
    for index, character in enumerate(value):
        point = ord(character)
        if 0xD800 <= point <= 0xDFFF:
            if start < index:
                chunks.append(value[start:index])
            chunks.append(point)
            start = index + 1
    if start < len(value):
        chunks.append(value[start:])
    require(
        bool(chunks)
        and any(type(chunk) is int for chunk in chunks)
        and all(
            (
                type(chunk) is int and 0xD800 <= chunk <= 0xDFFF
            )
            or (
                type(chunk) is str
                and bool(chunk)
                and not worker_has_surrogate(chunk)
            )
            for chunk in chunks
        ),
        "reject a lossy or forged worker surrogate chunk",
    )
    return chunks


def escaped_worker_mapping_required(mapping):
    require(
        type(mapping) is dict
        or type(mapping).__name__ == "_NormalizedEnvelope",
        "classify only an exact authenticated source-worker mapping",
    )
    require(
        all(type(key) is str for key in mapping),
        "reject a non-string actual worker evidence mapping key",
    )
    return (
        any(worker_has_surrogate(key) for key in mapping)
        or (
            len(mapping) == 1
            and next(iter(mapping)) in WORKER_RESERVED_TAGS
        )
    )


def decode_worker_unicode_transport(item, depth=0):
    require(
        type(depth) is int and 0 <= depth <= 64,
        "reject excessive reversible original worker-wire depth",
    )
    if item is None or type(item) in (bool, int):
        return item
    if type(item) is str:
        require(
            not worker_has_surrogate(item),
            "reject a surrogate before strict immutable JSON validation",
        )
        return item
    if type(item) is list:
        return [
            decode_worker_unicode_transport(value, depth + 1)
            for value in item
        ]
    require(
        type(item) is dict,
        "reject an unauthenticated worker transport structure",
    )
    require(
        all(
            type(key) is str and not worker_has_surrogate(key)
            for key in item
        ),
        "reject a noncanonical strict worker-wire object key",
    )
    if len(item) == 1 and WORKER_UNICODE_TAG in item:
        chunks = item[WORKER_UNICODE_TAG]
        require(
            type(chunks) is list and bool(chunks),
            "reject an absent or forged first-party surrogate envelope",
        )
        restored = []
        previous_was_text = False
        surrogate_count = 0
        for fragment in chunks:
            if type(fragment) is str:
                require(
                    bool(fragment)
                    and not previous_was_text
                    and not worker_has_surrogate(fragment),
                    "reject an empty, adjacent, or nonscalar text chunk",
                )
                previous_was_text = True
                restored.append(fragment)
            else:
                require(
                    type(fragment) is int
                    and 0xD800 <= fragment <= 0xDFFF,
                    "reject a forged Unicode surrogate code unit",
                )
                previous_was_text = False
                surrogate_count += 1
                restored.append(chr(fragment))
        value = "".join(restored)
        require(
            surrogate_count > 0
            and worker_has_surrogate(value)
            and worker_unicode_chunks(value) == chunks,
            "reject a nonminimal or non-injective surrogate envelope",
        )
        return value
    if len(item) == 1 and WORKER_MAPPING_TAG in item:
        pairs = item[WORKER_MAPPING_TAG]
        require(
            type(pairs) is list and bool(pairs),
            "reject an absent or forged escaped worker mapping",
        )
        restored = {}
        previous = None
        for pair in pairs:
            require(
                type(pair) is list and len(pair) == 2,
                "reject a malformed or truncated original mapping pair",
            )
            key = decode_worker_unicode_transport(pair[0], depth + 2)
            value = decode_worker_unicode_transport(pair[1], depth + 2)
            require(
                type(key) is str
                and key not in restored
                and (
                    previous is None
                    or previous < key
                ),
                "reject crossed, duplicated, or unsorted original keys",
            )
            restored[key] = value
            previous = key
        require(
            escaped_worker_mapping_required(restored),
            "reject an unnecessary or forged original mapping envelope",
        )
        return restored
    return {
        key: decode_worker_unicode_transport(value, depth + 1)
        for key, value in item.items()
    }


def bounded_actual_worker_json(producer, raw, *, synthetic_maximum=None):
    require(
        type(producer) is types.ModuleType
        and getattr(producer, "SCHEMA", None)
        == "rebar-owned-six-family-original-p0-producer-v5"
        and getattr(producer, "MAX_JSON_BYTES", None)
        == IMMUTABLE_PRODUCER_JSON_BYTES
        and type(getattr(producer, "JsonReader", None)) is type,
        "preserve the exact immutable V5 evidence reader and global cap",
    )
    maximum = MAX_ACTUAL_WORKER_JSON_BYTES
    if synthetic_maximum is not None:
        require(
            ACTIVE_WALL is not None
            and ACTIVE_WALL.active is True
            and type(synthetic_maximum) is int
            and 0 < synthetic_maximum < MAX_ACTUAL_WORKER_JSON_BYTES,
            "allow a reduced worker-transport cap only in a source control",
        )
        maximum = synthetic_maximum

    class BoundedActualWorkerJsonReader(producer.JsonReader):
        __slots__ = ()

        def __init__(self, actual):
            require(
                type(actual) is bytes
                and 0 < len(actual) <= maximum,
                "reject absent, truncated, or oversized actual worker JSON",
            )
            self.text = actual.decode("utf-8", "strict")
            self.index = 0

    wire = BoundedActualWorkerJsonReader(raw).parse()
    require(
        producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and producer.canonical(wire) == raw,
        "reject altered strict original JSON or noncanonical worker wire",
    )
    decoded = decode_worker_unicode_transport(wire)
    require(
        worker_canonical(decoded) == raw
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES,
        "reject forged, lossy, or nonminimal worker evidence transport",
    )
    return decoded


def authenticated_public_surface_mapping(item, *, source_module=None):
    if type(item) is dict:
        return item
    if source_module is None:
        module = sys.modules.get(PUBLIC_SURFACE_MODULE)
        require(
            type(module) is types.ModuleType
            and sys.modules.get(PUBLIC_SURFACE_MODULE) is module
            and getattr(module, "__name__", None) == PUBLIC_SURFACE_MODULE
            and getattr(module, "__file__", None)
            == ROOT + "/" + PUBLIC_SURFACE_SOURCE[0]
            and getattr(module, "SOURCE_RELATIVE", None)
            == PUBLIC_SURFACE_SOURCE[0]
            and getattr(module, "SCHEMA", None) == PUBLIC_SURFACE_SCHEMA
            and getattr(getattr(module, "__spec__", None), "name", None)
            == PUBLIC_SURFACE_MODULE
            and getattr(getattr(module, "__spec__", None), "origin", None)
            == ROOT + "/" + PUBLIC_SURFACE_SOURCE[0],
            "reject an unauthenticated original public-surface envelope owner",
        )
    else:
        require(
            ACTIVE_WALL is not None
            and ACTIVE_WALL.active is True
            and type(source_module) is types.ModuleType
            and source_module.__name__ == PUBLIC_SURFACE_MODULE
            and getattr(source_module, "__file__", None)
            == ROOT + "/" + PUBLIC_SURFACE_SOURCE[0]
            and getattr(source_module, "SOURCE_RELATIVE", None)
            == PUBLIC_SURFACE_SOURCE[0]
            and getattr(source_module, "SCHEMA", None)
            == PUBLIC_SURFACE_SCHEMA,
            "allow a synthetic surface owner only within the source wall",
        )
        module = source_module
    envelope = getattr(module, "_NormalizedEnvelope", None)
    registry = getattr(module, "_AUTHENTIC_NORMALIZED_ENVELOPES", None)
    require(
        type(envelope) is type
        and envelope.__name__ == "_NormalizedEnvelope"
        and envelope.__module__ == PUBLIC_SURFACE_MODULE
        and envelope.__bases__ == (dict,)
        and getattr(envelope, "__slots__", None) == ("__weakref__",)
        and type(item) is envelope
        and registry is not None
        and callable(getattr(registry, "get", None))
        and registry.get(id(item)) is item
        and (
            source_module is not None
            or (
                type(registry).__name__ == "WeakValueDictionary"
                and type(registry).__module__ == "weakref"
                and callable(
                    getattr(module, "_new_normalized_envelope", None)
                )
            )
        ),
        "reject a forged, unregistered, copied, or cross-owner "
        "public-surface normalized envelope",
    )
    return item


def worker_canonical(value, *, source_module=None):
    def encode(item, depth):
        require(depth <= 64, "reject excessive canonical worker nesting")
        if item is None:
            return "null"
        if item is True:
            return "true"
        if item is False:
            return "false"
        if type(item) is int:
            return str(item)
        if type(item) is str:
            if not worker_has_surrogate(item):
                return worker_quote(item)
            require(
                depth + 2 <= 64,
                "bound an exact surrogate worker transport envelope",
            )
            chunks = worker_unicode_chunks(item)
            return (
                "{" + worker_quote(WORKER_UNICODE_TAG) + ":["
                + ",".join(
                    worker_quote(chunk)
                    if type(chunk) is str
                    else str(chunk)
                    for chunk in chunks
                )
                + "]}"
            )
        if type(item) in (tuple, list):
            return "[" + ",".join(
                encode(child, depth + 1) for child in item
            ) + "]"
        if type(item) is dict or type(item).__name__ == "_NormalizedEnvelope":
            mapping = authenticated_public_surface_mapping(
                item,
                source_module=source_module,
            )
            require(all(type(key) is str for key in mapping),
                    "reject noncanonical actual worker keys")
            if escaped_worker_mapping_required(mapping):
                require(
                    depth + 3 <= 64,
                    "bound escaped surrogate or collision mapping keys",
                )
                pairs = (
                    "[" + encode(key, depth + 2) + ","
                    + encode(mapping[key], depth + 2) + "]"
                    for key in sorted(mapping)
                )
                return (
                    "{" + worker_quote(WORKER_MAPPING_TAG) + ":["
                    + ",".join(pairs) + "]}"
                )
            return "{" + ",".join(
                worker_quote(key) + ":" + encode(mapping[key], depth + 1)
                for key in sorted(mapping)
            ) + "}"
        raise CampaignError(
            "reject unsupported actual worker evidence: "
            + type(item).__name__
        )
    return (encode(value, 0) + "\n").encode("ascii")


def worker(args, *, bootstrap_hook=None):
    stage = "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
    suite_name = None
    suite_count = None
    installed = False
    imported = False
    observer_proxy = None
    synthetic = bootstrap_hook is not None
    try:
        require(type(args) is dict,
                "reject noncanonical worker bootstrap arguments")
        suite_name = args.get("--suite")
        suite_count = dict(SUITES).get(suite_name)
        if bootstrap_hook is not None:
            require(callable(bootstrap_hook),
                    "reject a noncallable source-only bootstrap control")
            bootstrap_hook()
        stage = "VERIFY_ACTIVE_FROZEN_CONTEXT"
        state = verify(args["--source-sha256"], args["--protocol-sha256"],
                       args["--contract-sha256"], active=True)
        producer = state["producer"]
        stage = "VALIDATE_PINNED_WORKER_AUTHORITY"
        require_actual_authority(args, worker=True)
        stage = "READ_AUTHENTICATED_ACTIVE_RECOVERY_JOURNAL"
        journal = read_live_journal(
            producer, args["--recovery-journal-sha256"]
        )
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_ENGINE"
        engine = active_owner(
            "engine", journal["roles"]["engine"]["stage"]
        )
        stage = "AUTHENTICATE_ACTIVE_FIRST_PARTY_BRIDGE"
        bridge = active_owner(
            "bridge", journal["roles"]["bridge"]["stage"]
        )
        stage = "AUTHENTICATE_ACTIVE_LIFETIME_ADAPTER"
        active_owner("adapter", journal["roles"]["adapter"]["stage"])
        stage = "VERIFY_CLEAN_PRE_GUARD_MODULE_STATE"
        clean()
        stage = "LOAD_IMMUTABLE_FIRST_PARTY_RUNTIME_GUARD"
        guard = load(GUARD[0], "_rebar_zig_v13_exact_runtime_guard_v3")
        stage = "CONSTRUCT_IMMUTABLE_RUNTIME_POLICY"
        policy = guard.RuntimePolicy()
        require(
            type(policy).prepare_family
            is guard.BASE.RuntimePolicy.prepare_family
            and type(policy).prepare_family.__globals__
            is guard.BASE.__dict__
            and type(policy).prepare_family.__globals__["SELF"]
            == GUARD_V2[0][0]
            and type(policy).prepare_family.__globals__["PROTOCOL"]
            == GUARD_V2[1][0]
            and type(policy).prepare_family.__globals__["CONTRACT"]
            == GUARD_V2[2][0]
            and type(policy).prepare_family.__code__.co_filename
            == ROOT + "/" + GUARD_V2[0][0]
            and guard.child_bootstrap_source
            is guard.BASE.child_bootstrap_source,
            "reject V3 guard without exact immutable V2 policy and child globals",
        )
        stage = "INSTALL_IMMUTABLE_RUNTIME_GUARD"
        policy.install()
        installed = True
        stage = "PREPARE_AUTHENTICATED_FIRST_PARTY_NATIVE_FAMILY"
        policy.prepare_family(
            FAMILY, bridge_owner=bridge, engine_owner=engine
        )
        stage = "AUTHENTICATE_GUARDED_FIRST_PARTY_NAMESPACE"
        namespace = authenticated_first_party_namespace()
        stage = "PREPEND_AUTHENTICATED_ISOLATED_FIRST_PARTY_ROOT"
        prepend_authenticated_first_party_namespace(namespace)
        stage = "VERIFY_RUNTIME_GUARD_BEFORE_CANDIDATE_IMPORT"
        require(
            installed
            and policy.installed
            and policy.prepared_family == FAMILY
            and sys.path[0] == ROOT
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "require genuine strict guard and authenticated namespace "
            "before the sole first-party candidate import",
        )
        stage = "IMPORT_GUARDED_FIRST_PARTY_ZIG_CANDIDATE"
        candidate = importlib.import_module("candidates.zig_candidate")
        imported = True
        stage = "BIND_SELECTED_FIRST_PARTY_CANDIDATE"
        policy.bind_selected(candidate, FAMILY)
        stage = "BUILD_IMMUTABLE_FIRST_PARTY_FAMILY_SPEC"
        base = producer.family_spec(FAMILY)
        source_owners = (
            (ORIGINAL_ADAPTER[0], LIFETIME_ADAPTER[1], LIFETIME_ADAPTER[2]),
            (ENGINE_SOURCE[0], ENGINE_SOURCE[1], ENGINE_SOURCE[2]),
            (BRIDGE_SOURCE[0], BRIDGE_SOURCE[1], BRIDGE_SOURCE[2]),
        )
        selected = producer.FamilySpec(
            base.name, base.module, base.adapter_relative,
            base.bridge_module, base.engine_relative,
            base.bridge_relative, source_owners, False, False,
        )
        stage = "VERIFY_GUARDED_FIRST_PARTY_FAMILY_IDENTITY"
        require(producer.family_spec(FAMILY) is base
                and base.owned_ctypes is True
                and selected.owned_ctypes is False
                and producer.require_selected(selected) is candidate
                and policy.selected is candidate
                and sys.modules.get("re") is candidate,
                "preserve the immutable producer and exact first-party alias")
        pins = {
            "source": LIFETIME_ADAPTER[1],
            "native_engine": NATIVE["engine"][0],
            "native_bridge": NATIVE["bridge"][0],
        }
        source_pins = {
            path: value for path, value, _ in source_owners
        }
        stage = "INSTALL_AUTHENTICATED_ZIG_OBSERVER_SOURCE_PROXY"
        observer_proxy = install_authenticated_zig_observer_proxy(
            producer, selected, policy
        )
        stage = "RESOLVE_IMMUTABLE_ORIGINAL_SUITE"
        suite = producer.suite_spec(args["--suite"])
        suite_name, suite_count = suite.name, suite.case_count
        if suite.name == "original_bounded_v5":
            stage = "OBSERVE_COMPLETE_UPSTREAM_ORIGINAL_SUITE"
            observation = producer.observe_original_upstream(
                suite, selected, pins, source_pins
            )
        elif suite.name == "subinterpreter_v2":
            stage = "OBSERVE_COMPLETE_ORIGINAL_SUBINTERPRETER_SUITE"
            observation = producer.observe_subinterpreters(
                suite, selected, pins, source_pins,
                producer_sha256=PRODUCER[0][1],
            )
        else:
            stage = "OBSERVE_COMPLETE_DIRECT_ORIGINAL_SUITE"
            observation = producer.observe_direct_suite(
                suite, selected, pins, source_pins, state["manifest"]
            )
        stage = "VALIDATE_COMPLETE_ORIGINAL_SUITE_OBSERVATION"
        require(type(observation) is dict
                and observation.get("suite") == suite.name
                and observation.get("candidate_family") == FAMILY
                and observation.get("case_execution_denominator")
                == suite.case_count
                and observation.get("actual_candidate_workers") == 1
                and observation.get("hidden_cases_read") == 0
                and observation.get("benchmark_files_read") == 0
                and observation.get("holdout") == "NOT OPENED",
                "reject omitted or fabricated genuine original records")
        return {
            "schema": SCHEMA + "-actual-suite-worker",
            "status": observation.get("status"),
            "family": FAMILY,
            "label": LABEL,
            "suite": suite.name,
            "case_execution_denominator": suite.case_count,
            "complete_actual_observation": observation,
            "activation_stage": "COMPLETE_ORIGINAL_OBSERVATION",
            "guard_installed_before_candidate_import": True,
            "candidate_imported": True,
            "actual_candidate_workers": 1,
            "synthetic_control": False,
            "observer_source_proxy": dict(observer_proxy),
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }
    except BaseException as error:
        details = getattr(error, "details", None)
        return {
            "schema": SCHEMA + "-actual-worker-failure",
            "status": "FAIL",
            "family": FAMILY,
            "label": LABEL,
            "suite": suite_name,
            "case_execution_denominator": suite_count,
            **failure_details(error, stage),
            "complete_actual_suite_failure_details": details,
            "guard_installed_before_candidate_import": installed,
            "candidate_imported": imported,
            "actual_candidate_workers": 0 if synthetic else 1,
            "synthetic_control": synthetic,
            "observer_source_proxy": (
                dict(observer_proxy)
                if type(observer_proxy) is dict
                else None
            ),
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }

def stream(raw, maximum):
    require(type(raw) is bytes and len(raw) <= maximum,
            "reject omitted or unbounded actual worker output")
    base64 = __import__("base64")
    return {"base64": base64.b64encode(raw).decode("ascii"),
            "bytes": len(raw), "sha256": digest(raw), "complete": True}



def command(args, suite, journal_sha):
    require_actual_authority(args)
    require(
        suite in dict(SUITES),
        "reject an omitted or substituted original suite worker",
    )
    argv = [PYTHON, "-I", "-B", "-S", ROOT + "/" + SELF, "--worker"]
    for key in ("--source-sha256", "--protocol-sha256", "--contract-sha256"):
        argv.extend((key, args[key]))
    for key, expected in ACTUAL_CALLER_PINS:
        require(
            args.get(key) == expected,
            "reject an omitted independently supplied actual worker pin",
        )
        argv.extend((key, args[key]))
    for key, value in (
        ("--family", FAMILY),
        ("--label", LABEL),
        ("--suite", suite),
        ("--recovery-journal-sha256", pin(journal_sha, "recovery journal")),
    ):
        argv.extend((key, value))
    return argv

def public_literal_stderr(row):
    require(type(row) is dict,
            "reject a fabricated worker literal-stderr row")
    excerpt = row.get("stderr_literal_excerpt")
    require(type(excerpt) is dict
            and excerpt.get("limit_bytes") == MAX_PUBLIC_STDERR_BYTES,
            "reject omitted or unbounded worker literal stderr")
    owner = row.get("stderr")
    if excerpt.get("status") == "NOT AVAILABLE":
        require(owner is None
                and excerpt.get("text") is None
                and excerpt.get("total_bytes") == "NOT MEASURED"
                and excerpt.get("captured_bytes") == 0
                and excerpt.get("sha256") == "NOT MEASURED"
                and type(excerpt.get("reason")) is dict,
                "reject invented unavailable actual worker stderr")
        return excerpt
    require(excerpt.get("status") == "CAPTURED"
            and type(owner) is dict
            and type(excerpt.get("text")) is str
            and type(excerpt.get("total_bytes")) is int
            and type(excerpt.get("captured_bytes")) is int
            and 0 <= excerpt["captured_bytes"]
            <= min(MAX_PUBLIC_STDERR_BYTES, excerpt["total_bytes"])
            and excerpt.get("truncated")
            is (excerpt["total_bytes"] > MAX_PUBLIC_STDERR_BYTES)
            and excerpt["total_bytes"] == owner.get("bytes")
            and excerpt.get("sha256") == owner.get("sha256")
            and owner.get("complete") is True,
            "reject omitted, altered, unbounded, or crossed literal stderr")
    return excerpt


def public_stream_owner(value):
    if value is None:
        return None
    require(type(value) is dict
            and type(value.get("bytes")) is int
            and value["bytes"] >= 0
            and value.get("complete") is True,
            "reject an incomplete public worker stream identity")
    return {
        "bytes": value["bytes"],
        "sha256": pin(value.get("sha256"), "complete worker stream"),
        "complete": True,
        "complete_payload_preserved_in_actual_archive": True,
    }


def public_campaign_diagnostics(report):
    rows = report.get("complete_original_suite_workers")
    require(type(rows) is list and len(rows) == len(SUITES)
            and all(type(row) is dict for row in rows)
            and tuple(
                (row.get("suite"), row.get("case_execution_denominator"))
                for row in rows
            ) == SUITES,
            "reject omitted, reordered, or miscounted public suite diagnostics")
    require(all(row.get("timed_out") is True
                or row.get("timed_out") is False for row in rows)
            and all(row.get("timeout_seconds") == SUITE_TIMEOUT_SECONDS
                    for row in rows)
            and all(
                row.get("timeout_classification")
                == ("INFRASTRUCTURE FAILURE"
                    if row["timed_out"] else "NOT TIMED OUT")
                for row in rows
            )
            and all(
                not row["timed_out"]
                or (row.get("status") == "FAIL"
                    and row.get("infrastructure_failure") is True)
                for row in rows
            ),
            "reject an omitted, weakened, or falsely passing suite timeout")
    timed_out = [
        row["suite"] for row in rows if row["timed_out"]
    ]
    infrastructure = [
        row["suite"] for row in rows
        if row.get("infrastructure_failure") is True
    ]
    failures = [
        row["suite"] for row in rows if row.get("status") != "PASS"
    ]
    require(report.get("case_execution_denominator") == 31237
            and report.get("suite_count") == 13
            and report.get("all_original_suites_attempted") is True
            and report.get("per_suite_timeout_seconds")
            == SUITE_TIMEOUT_SECONDS
            and report.get("maximum_serial_worker_timeout_seconds")
            == MAX_SERIAL_SUITE_TIMEOUT_SECONDS
            and report.get("timeout_classification")
            == "INFRASTRUCTURE FAILURE"
            and report.get("timeout_count") == len(timed_out)
            and report.get("timed_out_suites") == timed_out
            and report.get("infrastructure_failure_count")
            == len(infrastructure)
            and report.get("infrastructure_failure_suites")
            == infrastructure
            and report.get("failed_suites") == failures,
            "reject inconsistent public timeout, failure, or suite totals")
    diagnostics = []
    for row in rows:
        worker = row.get("complete_actual_worker")
        if type(worker) is not dict:
            worker = {}
        observation = worker.get("complete_actual_observation")
        if type(observation) is not dict:
            observation = {}
        mismatch_count = observation.get("mismatch_count")
        if type(mismatch_count) is not int:
            mismatch_count = "NOT MEASURED"
        diagnostics.append({
            "suite": row["suite"],
            "case_execution_denominator":
                row["case_execution_denominator"],
            "status": row.get("status"),
            "infrastructure_failure":
                row.get("infrastructure_failure") is True,
            "pid": row.get("pid"),
            "returncode": row.get("returncode"),
            "timed_out": row["timed_out"],
            "timeout_seconds": row["timeout_seconds"],
            "timeout_classification": row["timeout_classification"],
            "error_type": row.get("error_type", worker.get("error_type")),
            "error_message":
                row.get("error_message", worker.get("error_message")),
            "actual_worker_schema": worker.get("schema"),
            "complete_actual_suite_failure_details":
                worker.get("complete_actual_suite_failure_details"),
            "observed_semantic_mismatch_count": mismatch_count,
            "activation_stage":
                row.get("activation_stage", worker.get("activation_stage")),
            "error_class":
                row.get("error_class", worker.get("error_class")),
            "error_message_detail":
                row.get("error_message_detail",
                        worker.get("error_message_detail")),
            "error_traceback":
                row.get("error_traceback", worker.get("error_traceback")),
            "traceback_frames":
                row.get("traceback_frames", worker.get("traceback_frames")),
            "traceback_frames_truncated":
                row.get("traceback_frames_truncated",
                        worker.get("traceback_frames_truncated")),
            "guard_installed_before_candidate_import":
                worker.get("guard_installed_before_candidate_import"),
            "candidate_imported": worker.get("candidate_imported"),
            "stdout": public_stream_owner(row.get("stdout")),
            "stderr": public_stream_owner(row.get("stderr")),
            "stderr_literal_excerpt": public_literal_stderr(row),
            "observer_source_proxy":
                worker.get("observer_source_proxy"),
        })
    return {
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "actual_candidate_workers": report["actual_candidate_workers"],
        "unique_candidate_worker_count":
            report["unique_candidate_worker_count"],
        "completed_suite_count": report["completed_suite_count"],
        "verified_passing_case_count":
            report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "observed_semantic_mismatch_lower_bound":
            report["observed_semantic_mismatch_lower_bound"],
        "failed_suites": failures,
        "infrastructure_failure_count": len(infrastructure),
        "infrastructure_failure_suites": infrastructure,
        "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
        "maximum_serial_worker_timeout_seconds":
            MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
        "all_original_suites_attempted": True,
        "timeout_classification": "INFRASTRUCTURE FAILURE",
        "timeout_count": len(timed_out),
        "timed_out_suites": timed_out,
        "original_suite_diagnostics": diagnostics,
    }





def synthetic_zig_observer_proxy_controls():
    require(
        "ctypes" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules,
        "require clean source-only historical proxy controls",
    )
    historical = read_owner(LEGACY_V4_SOURCE)
    harness = read_owner(ORIGINAL_HARNESS_SOURCE)
    fixed_historical = clean_historical_zig_v4(historical)
    fixed_harness = clean_original_zig_harness(harness)
    require(
        type(fixed_historical) is bytes
        and type(fixed_harness) is bytes
        and fixed_historical != historical
        and fixed_harness != harness
        and b"import ctypes\n" not in fixed_historical
        and FORBIDDEN_LEGACY_CTYPES_PROXY.encode("utf-8")
        in fixed_historical
        and b"    verify_runtime(candidate=True)\n" in fixed_harness
        and "ctypes" not in sys.modules,
        "reject unchanged, broad, or delegating historical source proxies",
    )
    compile(
        fixed_historical,
        ROOT + "/" + LEGACY_V4_SOURCE[0],
        "exec",
        dont_inherit=True,
    )
    compile(
        fixed_harness,
        ROOT + "/" + ORIGINAL_HARNESS_SOURCE[0],
        "exec",
        dont_inherit=True,
    )
    scratch = {"__builtins__": builtins.__dict__}
    exec(
        compile(
            FORBIDDEN_LEGACY_CTYPES_PROXY,
            "<first-party-zig-v9-fail-closed-ctypes-proxy>",
            "exec",
            dont_inherit=True,
        ),
        scratch,
    )
    try:
        scratch["ctypes"].CDLL("forbidden-v9.so")
    except RuntimeError as error:
        require(
            "V9 strictly forbids historical ctypes" in str(error),
            "reject an incorrectly classified no-loader ctypes control",
        )
    else:
        raise CampaignError(
            "the historical ctypes proxy unexpectedly loaded native code"
        )
    checks = 1
    checks += reject(
        lambda: clean_historical_zig_v4(
            historical.replace(b"import ctypes\n", b"import ctypes as x\n", 1)
        ),
        "changed authenticated historical ctypes source",
    )
    checks += reject(
        lambda: clean_original_zig_harness(
            harness.replace(
                b"    verify_runtime()\n",
                b"    verify_runtime(candidate=False)\n",
                1,
            )
        ),
        "changed exact original Rust-only source line",
    )
    checks += reject(
        lambda: sys.audit("ctypes.dlopen", "forbidden-v9.so"),
        "historical observer proxy attempted native ctypes delegation",
    )
    def wrong_family():
        raise CampaignError(
            "a Rust candidate entered the original-only suite controller"
        )
    checks += reject(
        wrong_family,
        "synthetic authentic historical upstream misclassification",
    )
    require(
        "ctypes" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules,
        "reject imports during source-only observer-proxy controls",
    )
    return checks + 1

def synthetic_first_party_namespace_controls():
    before = tuple(sys.path)
    marker = object()
    cache = sys.path_importer_cache.get(ROOT, marker)
    checks = 0
    try:
        require(
            ROOT not in sys.path
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "require an untouched isolated source-only namespace",
        )
        owner = authenticated_first_party_namespace()
        prepend_authenticated_first_party_namespace(owner)
        finder = importlib._bootstrap_external.PathFinder
        package = finder.find_spec("candidates", None)
        candidate = finder.find_spec(
            "candidates.zig_candidate", [ROOT + "/candidates"]
        )
        require(
            sys.path[0] == ROOT
            and tuple(sys.path[1:]) == before
            and package is not None
            and tuple(package.submodule_search_locations or ())
            == (ROOT + "/candidates",)
            and candidate is not None
            and candidate.origin
            == ROOT + "/candidates/zig_candidate.py"
            and "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "reject an unimportable or imported first-party namespace",
        )
        checks += 1
        for name in (
            "re",
            "_sre",
            "ctypes",
            "candidates",
            "candidates.zig_candidate",
            "candidates.rust_candidate",
        ):
            checks += reject(
                lambda item=name: builtins.__import__(item),
                "namespace repair bypassed strict source guard: " + name,
            )
        checks += reject(
            lambda: authenticated_first_party_namespace(
                ROOT + "/candidates"
            ),
            "crossed canonical first-party repository root",
        )
        require(
            "candidates" not in sys.modules
            and "candidates.zig_candidate" not in sys.modules
            and "re" not in sys.modules
            and "_sre" not in sys.modules,
            "reject side effects from namespace hostile controls",
        )
    finally:
        sys.path[:] = before
        if cache is marker:
            sys.path_importer_cache.pop(ROOT, None)
        else:
            sys.path_importer_cache[ROOT] = cache
    require(
        tuple(sys.path) == before
        and "candidates" not in sys.modules
        and "candidates.zig_candidate" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules,
        "require complete source-only path and module restoration",
    )
    return checks + 1


def synthetic_zig_direct_core_controls():
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules
        and "candidates" not in sys.modules,
        "require candidate-free original direct-core source controls",
    )
    original = read_owner(DIRECT_CORE_SOURCE)
    fixed = clean_original_zig_direct_core(original)
    require(
        fixed != original
        and b"    verify_runtime(candidate_loaded=True)\n" in fixed
        and b"    verify_runtime()\n" in original,
        "reject an unchanged or broad original direct-core repair",
    )
    compile(
        fixed,
        ROOT + "/" + DIRECT_CORE_SOURCE[0],
        "exec",
        dont_inherit=True,
    )
    checks = 1
    checks += reject(
        lambda: clean_original_zig_direct_core(
            original.replace(
                b"    verify_runtime()\n",
                b"    verify_runtime(candidate_loaded=False)\n",
                1,
            )
        ),
        "changed authenticated original direct-core runtime classification",
    )
    checks += reject(
        lambda: clean_original_zig_direct_core(
            original.replace(
                b"a candidate escaped into an original-only public controller",
                b"a candidate escaped into an original-only forged controller",
                1,
            )
        ),
        "changed original direct-core failure or frozen controller",
    )
    checks += reject(
        lambda: sys.audit("ctypes.dlopen", "forbidden-v10-direct-core.so"),
        "direct-core observer attempted forbidden native delegation",
    )
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and "ctypes" not in sys.modules
        and "candidates" not in sys.modules,
        "reject original direct-core control candidate or matcher imports",
    )
    return checks + 1


def synthetic_bounded_worker_json_controls(producer):
    require(
        producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and MAX_ACTUAL_WORKER_JSON_BYTES == 64 * 1024 * 1024
        and "json" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules,
        "require immutable candidate-free V5 worker-transport controls",
    )

    def reject_worker_transport(operation, label):
        try:
            operation()
        except (CampaignError, producer.ProducerError, ValueError):
            return 1
        raise CampaignError(
            "accepted invalid first-party worker transport: " + label
        )

    payload = {
        "evidence": "first-party actual worker transport",
        "padding": "z" * (IMMUTABLE_PRODUCER_JSON_BYTES + 64),
    }
    raw = producer.canonical(payload)
    require(
        IMMUTABLE_PRODUCER_JSON_BYTES
        < len(raw) <= MAX_ACTUAL_WORKER_JSON_BYTES,
        "require a genuine synthetic worker payload above the V5 global cap",
    )
    checks = 1
    checks += reject_worker_transport(
        lambda: producer.JsonReader(raw).parse(),
        "immutable V5 parser accepted oversized worker evidence",
    )
    decoded = bounded_actual_worker_json(producer, raw)
    require(
        decoded == payload
        and producer.canonical(decoded) == raw
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES,
        "reject truncated, changed, or noncanonical 4-MiB worker evidence",
    )
    checks += 1
    for invalid, description in (
        (b"", "absent actual worker output"),
        (b'{"duplicate":1,"duplicate":2}\n',
         "duplicate actual worker JSON key"),
        (b'{"truncated":', "truncated actual worker JSON"),
        (b'{"value":1} \n', "noncanonical actual worker JSON"),
        (b"\xff\n", "non-UTF-8 actual worker JSON"),
    ):
        checks += reject_worker_transport(
            lambda data=invalid: bounded_actual_worker_json(producer, data),
            description,
        )
    checks += reject_worker_transport(
        lambda: bounded_actual_worker_json(
            producer,
            b'{"actual":"too large"}\n',
            synthetic_maximum=8,
        ),
        "source-only reduced actual-worker transport limit",
    )
    require(
        producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and "json" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules,
        "reject modified global reader or imports in worker transport",
    )
    return checks + 1


def synthetic_authenticated_surface_envelope_controls(producer):
    require(
        ACTIVE_WALL is not None
        and ACTIVE_WALL.active is True
        and PUBLIC_SURFACE_MODULE not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules,
        "require a candidate-free, unimported public-surface control",
    )
    raw_source = read_owner(PUBLIC_SURFACE_SOURCE)
    tree = ast.parse(
        raw_source.decode("utf-8", "strict"),
        filename=PUBLIC_SURFACE_SOURCE[0],
    )
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "_NormalizedEnvelope"
    ]
    factories = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_new_normalized_envelope"
    ]
    require(
        len(classes) == 1
        and len(factories) == 1
        and len(classes[0].bases) == 1
        and isinstance(classes[0].bases[0], ast.Name)
        and classes[0].bases[0].id == "dict",
        "authenticate the immutable stage-19 envelope class and factory",
    )
    module = types.ModuleType(PUBLIC_SURFACE_MODULE)
    module.__file__ = ROOT + "/" + PUBLIC_SURFACE_SOURCE[0]
    module.SOURCE_RELATIVE = PUBLIC_SURFACE_SOURCE[0]
    module.SCHEMA = PUBLIC_SURFACE_SCHEMA
    envelope_class = type(
        "_NormalizedEnvelope",
        (dict,),
        {
            "__module__": PUBLIC_SURFACE_MODULE,
            "__slots__": ("__weakref__",),
        },
    )
    module._NormalizedEnvelope = envelope_class
    module._AUTHENTIC_NORMALIZED_ENVELOPES = {}
    authentic = envelope_class({
        "kind": "float",
        "hex": "0x1.0000000000000p+0",
    })
    module._AUTHENTIC_NORMALIZED_ENVELOPES[id(authentic)] = authentic
    value = {
        "ordinary": {"kind": "float", "hex": "ordinary user mapping"},
        "registered": authentic,
    }
    wire = worker_canonical(value, source_module=module)
    decoded = bounded_actual_worker_json(producer, wire)
    require(
        decoded == {
            "ordinary": {
                "kind": "float",
                "hex": "ordinary user mapping",
            },
            "registered": {
                "kind": "float",
                "hex": "0x1.0000000000000p+0",
            },
        }
        and producer.canonical(decoded) == wire
        and module._AUTHENTIC_NORMALIZED_ENVELOPES.get(id(authentic))
        is authentic
        and value["registered"] is authentic
        and PUBLIC_SURFACE_MODULE not in sys.modules,
        "reject rewritten authentic envelope or noncanonical transport",
    )
    checks = 1
    unregistered = envelope_class({
        "kind": "float",
        "hex": "0x1.0000000000000p+0",
    })
    checks += reject(
        lambda: worker_canonical(
            {"forged": unregistered},
            source_module=module,
        ),
        "unregistered exact public-surface envelope",
    )
    forged_class = type(
        "_ForgedEnvelope",
        (envelope_class,),
        {"__module__": PUBLIC_SURFACE_MODULE},
    )
    forged = forged_class({"kind": "float", "hex": "forged"})
    module._AUTHENTIC_NORMALIZED_ENVELOPES[id(forged)] = forged
    checks += reject(
        lambda: worker_canonical(
            {"forged": forged},
            source_module=module,
        ),
        "registered subclass of the authentic public-surface envelope",
    )
    copied = envelope_class(dict(authentic))
    checks += reject(
        lambda: worker_canonical(
            {"copied": copied},
            source_module=module,
        ),
        "copied lookalike public-surface envelope",
    )
    crossed = types.ModuleType("tools.forged_public_surface")
    crossed.__file__ = module.__file__
    crossed.SOURCE_RELATIVE = module.SOURCE_RELATIVE
    crossed.SCHEMA = module.SCHEMA
    crossed._NormalizedEnvelope = envelope_class
    crossed._AUTHENTIC_NORMALIZED_ENVELOPES = {
        id(authentic): authentic,
    }
    checks += reject(
        lambda: worker_canonical(
            {"crossed": authentic},
            source_module=crossed,
        ),
        "cross-owner forged public-surface registry",
    )
    checks += reject(
        lambda: worker_canonical({"registered": authentic}),
        "nonimported authentic public-surface module",
    )
    require(
        value["registered"] is authentic
        and module._AUTHENTIC_NORMALIZED_ENVELOPES.get(id(authentic))
        is authentic
        and PUBLIC_SURFACE_MODULE not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "candidates" not in sys.modules
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES,
        "reject modified surface records, candidate imports, or JSON caps",
    )
    return checks + 1



def synthetic_injective_worker_unicode_controls(producer):
    require(
        ACTIVE_WALL is not None
        and ACTIVE_WALL.active is True
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and MAX_ACTUAL_WORKER_JSON_BYTES == 64 * 1024 * 1024
        and WORKER_UNICODE_TAG != WORKER_MAPPING_TAG
        and WORKER_UNICODE_TAG.startswith("\x00")
        and WORKER_MAPPING_TAG.startswith("\x00")
        and "json" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "encodings.utf_16_be" not in sys.modules
        and "candidates" not in sys.modules,
        "require an exact candidate-free Unicode transport source control",
    )

    def reject_transport(operation, label):
        try:
            operation()
        except (CampaignError, producer.ProducerError, ValueError):
            return 1
        raise CampaignError(
            "accepted invalid genuine surrogate worker transport: " + label
        )

    checks = 0
    hostile = {
        "lone-high": "\ud800",
        "lone-low": "\udfff",
        "high-and-low-code-units": "\ud83d\ude00",
        "ordinary": "source-only ASCII worker evidence",
        "mixed": "before\ud800middle\udfffafter",
        "ordinary-unicode-tag-user-mapping": {
            WORKER_UNICODE_TAG: ["real", 55296],
        },
        "ordinary-mapping-tag-user-mapping": {
            WORKER_MAPPING_TAG: [["user", "real"]],
        },
        "surrogate-key-mapping": {
            "plain": "value",
            "\ud800-key": "high",
            "low-\udfff": "low",
        },
        "nested": [
            {"value": "\ud800"},
            {WORKER_UNICODE_TAG: ["not a private worker tag"]},
            {"\udfff": "\ud800"},
        ],
    }
    wire = worker_canonical(hostile)
    strict = producer.JsonReader(wire).parse()
    require(
        producer.canonical(strict) == wire
        and strict != hostile
        and bounded_actual_worker_json(producer, wire) == hostile
        and worker_canonical(
            bounded_actual_worker_json(producer, wire)
        ) == wire
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and "encodings.utf_16_be" not in sys.modules,
        "reject changed surrogate values, mapping collisions, or codecs",
    )
    checks += 1

    scalar = "\U0001f600"
    paired_units = "\ud83d\ude00"
    scalar_wire = worker_canonical({"value": scalar})
    paired_wire = worker_canonical({"value": paired_units})
    parsed_scalar = producer.JsonReader(scalar_wire).parse()
    parsed_pair = bounded_actual_worker_json(producer, paired_wire)
    require(
        scalar != paired_units
        and scalar_wire == b'{"value":"\\ud83d\\ude00"}\n'
        and parsed_scalar == {"value": scalar}
        and worker_canonical(parsed_scalar) == scalar_wire
        and parsed_pair == {"value": paired_units}
        and worker_canonical(parsed_pair) == paired_wire
        and scalar_wire != paired_wire
        and "encodings.utf_16_be" not in sys.modules,
        "reject astral scalar and paired code-unit confusion",
    )
    checks += 1

    bmp_wire = worker_canonical({"value": "\u00e9"})
    parsed_bmp = producer.JsonReader(bmp_wire).parse()
    require(
        bmp_wire == b'{"value":"\\u00e9"}\n'
        and parsed_bmp == {"value": "\u00e9"}
        and worker_canonical(parsed_bmp) == bmp_wire
        and "encodings.utf_16_be" not in sys.modules,
        "reject exact scalar Unicode or import a lazy UTF-16 codec",
    )
    checks += 1

    ordinary = {
        "ascii": "ordinary first-party data",
        "scalar": "first-party source-only ASCII",
        "mapping": {"unchanged": [None, True, 4]},
    }
    require(
        worker_canonical(ordinary) == producer.canonical(ordinary)
        and bounded_actual_worker_json(
            producer,
            producer.canonical(ordinary),
        ) == ordinary,
        "reject a changed authentic surrogate-free worker stream",
    )
    checks += 1

    for raw, name in (
        (b'{"value":"\\ud800"}\n',
         "unchanged strict high-surrogate rejection"),
        (b'{"value":"\\udfff"}\n',
         "unchanged strict low-surrogate rejection"),
        (b'{"value":"\\ud83d"}\n',
         "unchanged strict truncated-pair rejection"),
    ):
        checks += reject_transport(
            lambda data=raw: producer.JsonReader(data).parse(),
            name,
        )
        checks += reject_transport(
            lambda data=raw: bounded_actual_worker_json(producer, data),
            "worker " + name,
        )

    forged = (
        ({WORKER_UNICODE_TAG: []},
         "empty Unicode envelope"),
        ({WORKER_UNICODE_TAG: ["plain"]},
         "surrogate-free forged Unicode envelope"),
        ({WORKER_UNICODE_TAG: [55295]},
         "non-surrogate low scalar"),
        ({WORKER_UNICODE_TAG: [57344]},
         "non-surrogate high scalar"),
        ({WORKER_UNICODE_TAG: [True]},
         "boolean disguised as a Unicode code unit"),
        ({WORKER_UNICODE_TAG: ["", 55296]},
         "empty Unicode fragment"),
        ({WORKER_UNICODE_TAG: ["left", "right", 55296]},
         "adjacent nonminimal text fragments"),
        ({WORKER_UNICODE_TAG: [55296, "tail", "tail"]},
         "nonminimal adjacent trailing fragments"),
        ({WORKER_MAPPING_TAG: []},
         "empty forged escaped mapping"),
        ({WORKER_MAPPING_TAG: [["ordinary", "value"]]},
         "nonminimal ordinary escaped mapping"),
        ({WORKER_MAPPING_TAG: [["dup", 1], ["dup", 2]]},
         "duplicate escaped mapping keys"),
        ({WORKER_MAPPING_TAG: [["z", 1], ["a", 2]]},
         "unsorted escaped original mapping keys"),
        ({WORKER_MAPPING_TAG: [["only-key"]]},
         "truncated escaped mapping pair"),
        ({WORKER_MAPPING_TAG: [[False, "value"]]},
         "nonstrings as escaped original keys"),
        ({WORKER_MAPPING_TAG: [
            [{WORKER_UNICODE_TAG: []}, "value"],
        ]}, "forged escaped surrogate mapping key"),
    )
    for encoded, name in forged:
        canonical = producer.canonical(encoded)
        checks += reject_transport(
            lambda data=canonical: bounded_actual_worker_json(
                producer,
                data,
            ),
            name,
        )

    encoded_user_unicode = worker_canonical({
        WORKER_UNICODE_TAG: ["ordinary user data", 55296],
    })
    encoded_user_mapping = worker_canonical({
        WORKER_MAPPING_TAG: [["ordinary", "user"]],
    })
    encoded_surrogate_key = worker_canonical({
        "\ud800": "real object key",
    })
    for raw, expected in (
        (
            encoded_user_unicode,
            {WORKER_UNICODE_TAG: ["ordinary user data", 55296]},
        ),
        (
            encoded_user_mapping,
            {WORKER_MAPPING_TAG: [["ordinary", "user"]]},
        ),
        (
            encoded_surrogate_key,
            {"\ud800": "real object key"},
        ),
    ):
        parsed = producer.JsonReader(raw).parse()
        require(
            producer.canonical(parsed) == raw
            and bounded_actual_worker_json(producer, raw) == expected
            and worker_canonical(expected) == raw,
            "reject collision-safe original mapping identity",
        )
        checks += 1

    require(
        checks >= 28
        and producer.MAX_JSON_BYTES == IMMUTABLE_PRODUCER_JSON_BYTES
        and "json" not in sys.modules
        and "re" not in sys.modules
        and "_sre" not in sys.modules
        and "encodings.utf_16_be" not in sys.modules
        and "candidates" not in sys.modules,
        "reject incomplete or codec-loading Unicode hostile controls",
    )
    return checks


def synthetic_evidence_controls(producer):
    def before_active_context():
        raise CampaignError(
            "synthetic PRE-TRY first-party bootstrap exception"
        )

    result = worker(
        {"--suite": SUITES[0][0]},
        bootstrap_hook=before_active_context,
    )
    require(
        result.get("schema") == SCHEMA + "-actual-worker-failure"
        and result.get("status") == "FAIL"
        and result.get("suite") == SUITES[0][0]
        and result.get("case_execution_denominator") == SUITES[0][1]
        and result.get("activation_stage")
        == "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
        and result.get("error_type") == "CampaignError"
        and result.get("error_class") == __name__ + ".CampaignError"
        and "synthetic PRE-TRY" in result.get("error_message", "")
        and result.get("guard_installed_before_candidate_import") is False
        and result.get("candidate_imported") is False
        and result.get("actual_candidate_workers") == 0
        and result.get("synthetic_control") is True
        and type(result.get("error_traceback")) is dict
        and result["error_traceback"].get("limit_bytes")
        == MAX_FAILURE_TRACEBACK_BYTES
        and "before_active_context"
        in result["error_traceback"].get("text", "")
        and len(result.get("traceback_frames", []))
        <= MAX_FAILURE_TRACEBACK_FRAMES
        and worker_canonical(result) == producer.canonical(result),
        "reject uncaught, fabricated, native-running, or "
        "noncanonical pre-context bootstrap exception",
    )
    sample = {
        "ascii": "first-party canonical evidence",
        "control": "\n\t\b",
        "nested": [None, True, False, -1, {"z": "quoted \" value"}],
    }
    require(worker_canonical(sample) == producer.canonical(sample),
            "reject producer-independent canonical worker serialization")
    require(
        worker_canonical({
            "unicode": "first-party \u00e9 \U0001f9ea",
        })
        == (
            b'{"unicode":"first-party '
            b'\\u00e9 \\ud83e\\uddea"}\n'
        ),
        "reject first-party Unicode escaping without lazy codec imports",
    )
    raw = (
        b"FIRST-PARTY SYNTHETIC STDERR: "
        b"visible before archive inflation\n"
    )
    excerpt = literal_stderr(raw)
    stderr = {
        "bytes": len(raw),
        "sha256": digest(raw),
        "complete": True,
    }
    rows = []
    for suite_name, case_count in SUITES:
        synthetic_failure = dict(result)
        synthetic_failure["suite"] = suite_name
        synthetic_failure["case_execution_denominator"] = case_count
        rows.append({
            "suite": suite_name,
            "case_execution_denominator": case_count,
            "status": "FAIL",
            "infrastructure_failure": True,
            "pid": None,
            "returncode": None,
            "timed_out": False,
            "timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "timeout_classification": "NOT TIMED OUT",
            "stderr": dict(stderr),
            "stderr_literal_excerpt": dict(excerpt),
            "complete_actual_worker": synthetic_failure,
        })
    suite_names = [name for name, _ in SUITES]
    report = {
        "case_execution_denominator": 31237,
        "suite_count": 13,
        "all_original_suites_attempted": True,
        "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
        "maximum_serial_worker_timeout_seconds":
            MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
        "timeout_classification": "INFRASTRUCTURE FAILURE",
        "timeout_count": 0,
        "timed_out_suites": [],
        "infrastructure_failure_count": 13,
        "infrastructure_failure_suites": suite_names,
        "failed_suites": suite_names,
        "actual_candidate_workers": 0,
        "unique_candidate_worker_count": 0,
        "completed_suite_count": 0,
        "verified_passing_case_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "observed_semantic_mismatch_lower_bound": 0,
        "complete_original_suite_workers": rows,
    }
    visible = public_campaign_diagnostics(report)
    require(
        visible.get("semantic_mismatch_count") == "NOT MEASURED"
        and visible.get("actual_candidate_workers") == 0
        and visible.get("infrastructure_failure_count") == 13
        and len(visible.get("original_suite_diagnostics", [])) == 13
        and all(
            item.get("activation_stage")
            == "PRE_ACTIVE_CONTEXT_BOOTSTRAP"
            and item.get("stderr_literal_excerpt", {}).get("status")
            == "CAPTURED"
            and "FIRST-PARTY SYNTHETIC STDERR"
            in item["stderr_literal_excerpt"].get("text", "")
            and item["stderr_literal_excerpt"].get("sha256")
            == digest(raw)
            for item in visible["original_suite_diagnostics"]
        ),
        "reject missing literal stderr or bootstrap stage for any suite",
    )
    for suffix in ("durable-publication-receipt", "published-actual-result"):
        fixture = {
            "schema": SCHEMA + "-" + suffix,
            "synthetic_control": True,
            **visible,
        }
        encoded = producer.canonical(fixture)
        parsed = producer.JsonReader(encoded).parse()
        require(
            parsed == fixture
            and b"FIRST-PARTY SYNTHETIC STDERR" in encoded
            and b"PRE_ACTIVE_CONTEXT_BOOTSTRAP" in encoded
            and len(parsed.get("original_suite_diagnostics", [])) == 13,
            "reject invisible literal stderr in synthetic public evidence",
        )
    oversized = literal_stderr(
        b"x" * (MAX_PUBLIC_STDERR_BYTES + 17)
    )
    require(
        oversized.get("truncated") is True
        and oversized.get("captured_bytes") == MAX_PUBLIC_STDERR_BYTES
        and oversized.get("total_bytes") == MAX_PUBLIC_STDERR_BYTES + 17,
        "reject unbounded actual literal-stderr publication",
    )
    crossed = dict(rows[0])
    crossed["stderr_literal_excerpt"] = dict(excerpt)
    crossed["stderr_literal_excerpt"]["sha256"] = digest(b"crossed")
    checks = reject(
        lambda: public_literal_stderr(crossed),
        "crossed actual literal stderr",
    )
    return checks + 4

def publication_stem(suffix, *, observed=None):
    require(
        type(suffix) is str and suffix in ("success", "failures"),
        "reject an invented actual V13 publication outcome",
    )
    expected = (
        "repaired-zig-original-campaign-v13-" + LABEL + "-" + suffix
    )
    if observed is not None:
        require(
            type(observed) is str and observed == expected,
            "reject an inherited or substituted actual V13 publication stem",
        )
    return expected


def publish_campaign(report, producer):
    require(type(report) is dict
            and report.get("schema")
            == SCHEMA + "-complete-actual-original-campaign"
            and report.get("all_three_original_targets_restored") is True
            and report.get("candidate_qualified") is False
            and report.get("supplemental_candidate_matching") == "NOT RUN"
            and report.get("holdout") == "NOT OPENED",
            "refuse to publish an incomplete or falsely qualified campaign")
    diagnostics = public_campaign_diagnostics(report)
    for role in ROLES:
        target_identity(role, ORIGINALS[role])
    plain = producer.canonical(report)
    require(0 < len(plain) <= 256 * 1024 * 1024,
            "bound every actual retained original case and worker record")
    zlib = __import__("zlib")
    compressor = zlib.compressobj(
        9, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
    compressed = compressor.compress(plain) + compressor.flush()
    require(compressed[:3] == b"\x1f\x8b\x08"
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "require one reproducible zero-time gzip evidence member")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    restored = decoder.decompress(compressed, len(plain) + 1)
    restored += decoder.flush()
    require(decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail and restored == plain,
            "reject truncated, concatenated, or altered actual results")
    directory_flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                       | getattr(os, "O_DIRECTORY", 0)
                       | getattr(os, "O_NOFOLLOW", 0))
    directory = os.open(ROOT + "/oracle/phase2/evidence", directory_flags)
    try:
        info = os.fstat(directory)
        require(stat.S_ISDIR(info.st_mode)
                and info.st_dev == DEVICE and info.st_uid == os.geteuid(),
                "reject a substituted actual evidence directory")
        suffix = "success" if report["original_campaign_passed"] else "failures"
        stem = publication_stem(suffix)
        archive = exclusive(directory, stem + ".json.gz", compressed)
        receipt = {
            "schema": SCHEMA + "-durable-publication-receipt",
            "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": report["status"],
            "original_campaign_passed": report["original_campaign_passed"],
            "candidate_qualified": False,
            "family": FAMILY,
            "label": LABEL,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            **diagnostics,
            "archive": archive,
            "uncompressed_bytes": len(plain),
            "uncompressed_sha256": digest(plain),
            "all_three_original_targets_restored": True,
            "supplemental_candidate_matching": "NOT RUN",
            "hidden_cases_read": 0,
            "benchmark_files_read": 0,
            "timing_trials_run": 0,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
        published = exclusive(
            directory, stem + "-publication-receipt.json",
            producer.canonical(receipt))
    finally:
        os.close(directory)
    return {"schema": SCHEMA + "-published-actual-result",
            "status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_status": report["status"],
            "original_campaign_passed": report["original_campaign_passed"],
            "candidate_qualified": False,
            "family": FAMILY, "label": LABEL,
            "source_sha256": report["source_sha256"],
            "protocol_sha256": report["protocol_sha256"],
            "contract_sha256": report["contract_sha256"],
            **diagnostics,
            "archive": archive, "publication_receipt": published,
            "all_three_original_targets_restored": True,
            "supplemental_candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "winner_selected": False}


def campaign(args):
    state = verify(args["--source-sha256"], args["--protocol-sha256"],
                   args["--contract-sha256"])
    require_actual_authority(args)
    require(os.environ.get("LOCPATH") == EXTERNAL_LOCPATH,
            "require the exact independently provisioned original locale "
            "before any native replacement")
    subprocess = __import__("subprocess")
    producer = state["producer"]
    recovery_fd = lock_fd = candidate_fd = None
    rows, restored, primary = [], None, None
    try:
        recovery_fd, lock_fd, candidate_fd, journal = prepare(state)
        journal_sha = journal["published_journal"]["sha256"]
        env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C",
               "LOCPATH": os.environ["LOCPATH"],
               "PYTHONDONTWRITEBYTECODE": "1"}
        for name, count in SUITES:
            try:
                child = subprocess.Popen(
                    command(args, name, journal_sha),
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, cwd=ROOT, env=env)
                timeout = False
                try:
                    stdout, stderr = child.communicate(timeout=SUITE_TIMEOUT_SECONDS)
                except subprocess.TimeoutExpired:
                    timeout = True
                    child.kill()
                    stdout, stderr = child.communicate()
                row = {"suite": name, "case_execution_denominator": count,
                       "pid": child.pid, "returncode": child.returncode,
                       "timed_out": timeout,
                       "timeout_seconds": SUITE_TIMEOUT_SECONDS,
                       "timeout_classification": (
                           "INFRASTRUCTURE FAILURE"
                           if timeout else "NOT TIMED OUT"),
                       "stdout": stream(stdout, 64 * 1024 * 1024),
                       "stderr": stream(stderr, 8 * 1024 * 1024),
                       "stderr_literal_excerpt": literal_stderr(stderr),
                       "status": "FAIL", "infrastructure_failure": True}
                if not timeout and child.returncode == 0 and stdout:
                    try:
                        observed = bounded_actual_worker_json(
                            producer,
                            stdout,
                        )
                        require(observed.get("schema") in {
                            SCHEMA + "-actual-suite-worker",
                            SCHEMA + "-actual-worker-failure"}
                            and observed.get("suite") == name
                            and observed.get("case_execution_denominator") == count
                            and observed.get("actual_candidate_workers") == 1
                            and observed.get("synthetic_control") is False
                            and observed.get("hidden_cases_read") == 0,
                            "reject crossed actual original worker output")
                        row["complete_actual_worker"] = observed
                        row["status"] = observed["status"]
                        row["infrastructure_failure"] = (
                            observed["schema"] == SCHEMA + "-actual-worker-failure")
                    except BaseException as error:
                        row.update(failure_details(
                            error, "VALIDATE_ACTUAL_WORKER_JSON"
                        ))
            except BaseException as error:
                row = {
                    "suite": name,
                    "case_execution_denominator": count,
                    "status": "FAIL",
                    "infrastructure_failure": True,
                    "timed_out": False,
                    "timeout_seconds": SUITE_TIMEOUT_SECONDS,
                    "timeout_classification": "NOT TIMED OUT",
                    "stderr_literal_excerpt": literal_stderr(
                        None,
                        "ACTUAL STDERR NOT AVAILABLE AFTER PROCESS "
                        "START OR CAPTURE FAILURE",
                    ),
                    **failure_details(
                        error, "CONTROLLER_PROCESS_START_OR_CAPTURE"
                    ),
                }
            rows.append(row)
    except BaseException as error:
        primary = error
    finally:
        if candidate_fd is not None:
            try:
                with CriticalSignals():
                    restored = restore(candidate_fd, journal)
            except BaseException as error:
                if primary is None:
                    primary = error
            finally:
                os.close(candidate_fd)
        if lock_fd is not None:
            os.close(lock_fd)
        if recovery_fd is not None:
            os.close(recovery_fd)
    if primary is not None:
        raise CampaignError("actual three-role campaign/recovery failed: "
                            + type(primary).__qualname__ + ": "
                            + str(primary)) from primary
    require(len(rows) == 13
            and tuple(row["suite"] for row in rows) == tuple(x for x, _ in SUITES)
            and sum(row["case_execution_denominator"] for row in rows) == 31237
            and restored is not None and len(restored) == 3,
            "require all actual original workers and three restored owners")
    pids = [row["pid"] for row in rows if type(row.get("pid")) is int]
    failure = [row for row in rows if row["status"] != "PASS"]
    infrastructure = [row for row in rows if row["infrastructure_failure"]]
    observed_mismatches = 0
    passes = 0
    complete_original_suites = 0
    for row in rows:
        observed = row.get("complete_actual_worker", {})
        observation = observed.get("complete_actual_observation", {})
        if type(observation.get("mismatch_count")) is int:
            observed_mismatches += observation["mismatch_count"]
        if (observed.get("schema") == SCHEMA + "-actual-suite-worker"
                and type(observation) is dict
                and observation.get("case_execution_denominator")
                == row["case_execution_denominator"]
                and observation.get("actual_candidate_case_count")
                == row["case_execution_denominator"]):
            complete_original_suites += 1
        if row["status"] == "PASS":
            passes += row["case_execution_denominator"]
    passed = (not failure and not infrastructure
              and len(set(pids)) == len(pids) == 13
              and complete_original_suites == 13 and passes == 31237)
    mismatch_count = (observed_mismatches
                      if complete_original_suites == 13
                      else "NOT MEASURED")
    report = {"schema": SCHEMA + "-complete-actual-original-campaign",
            "status": "PASS" if passed else "FAIL",
            "family": FAMILY, "label": LABEL,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "case_execution_denominator": 31237, "suite_count": 13,
            "actual_candidate_workers": len(pids),
            "unique_candidate_worker_count": len(set(pids)),
            "completed_suite_count": complete_original_suites,
            "verified_passing_case_count": passes,
            "semantic_mismatch_count": mismatch_count,
            "observed_semantic_mismatch_lower_bound": observed_mismatches,
            "infrastructure_failure_count": len(infrastructure),
            "infrastructure_failure_suites": [
                row["suite"] for row in infrastructure
            ],
            "failed_suites": [
                row["suite"] for row in failure
            ],
            "per_suite_timeout_seconds": SUITE_TIMEOUT_SECONDS,
            "maximum_serial_worker_timeout_seconds":
                MAX_SERIAL_SUITE_TIMEOUT_SECONDS,
            "all_original_suites_attempted": len(rows) == 13,
            "timeout_classification": "INFRASTRUCTURE FAILURE",
            "timeout_count": sum(
                row.get("timed_out") is True for row in rows),
            "timed_out_suites": [
                row["suite"] for row in rows
                if row.get("timed_out") is True
            ],
            "complete_original_suite_workers": rows,
            "all_three_original_targets_restored": True,
            "restored_original_roles": restored,
            "supplemental_candidate_matching": "NOT RUN",
            "supplemental_cases_counted_in_original_denominator": False,
            "original_campaign_passed": passed,
            "candidate_qualified": False,
            "runtime_non_delegation": "NOT ESTABLISHED",
            "hidden_cases_read": 0, "benchmark_files_read": 0,
            "timing_trials_run": 0, "holdout": "NOT OPENED",
            "performance": "NOT MEASURED", "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED", "winner_selected": False}
    return publish_campaign(report, producer)


def recover(args):
    state = verify(args["--source-sha256"], args["--protocol-sha256"],
                   args["--contract-sha256"], active=True)
    require_actual_authority(args)
    recovery_fd, lock_fd = recovery_directory(False)
    candidate_fd = None
    try:
        journal = read_live_journal(
            state["producer"], args["--recovery-journal-sha256"])
        candidate_fd = candidate_directory()
        with CriticalSignals():
            restored = restore(candidate_fd, journal)
    finally:
        if candidate_fd is not None:
            os.close(candidate_fd)
        os.close(lock_fd)
        os.close(recovery_fd)
    require(len(restored) == 3,
            "reject incomplete actual three-role original-inode recovery")
    return {
        "schema": SCHEMA + "-exact-three-role-recovery",
        "status": "PASS",
        "family": FAMILY,
        "label": LABEL,
        "restored_original_role_count": 3,
        "restored_original_roles": restored,
        "actual_candidate_workers": 0,
        "candidate_matching": "NOT RUN BY RECOVERY",
        "candidate_qualified": False,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "timing_trials_run": 0,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "winner_selected": False,
    }

def rejected_guard_control(guard, operation, label):
    try:
        operation()
    except (
        CampaignError,
        guard.GuardError,
        guard.BootstrapError,
        OSError,
        ImportError,
        TypeError,
        ValueError,
    ):
        return 1
    raise CampaignError(
        "accepted a hostile genuine V3 source-only guard control: " + label
    )


def synthetic_v3_guard_controls(state):
    guard = state["guard_implementation"]
    policy = guard.RuntimePolicy()
    require(
        type(policy).prepare_family
        is guard.BASE.RuntimePolicy.prepare_family
        and type(policy).prepare_family.__globals__
        is guard.BASE.__dict__
        and type(policy).prepare_family.__globals__["SELF"]
        == GUARD_V2[0][0]
        and type(policy).prepare_family.__globals__["PROTOCOL"]
        == GUARD_V2[1][0]
        and type(policy).prepare_family.__globals__["CONTRACT"]
        == GUARD_V2[2][0]
        and type(policy).prepare_family.__code__.co_filename
        == ROOT + "/" + GUARD_V2[0][0]
        and guard.child_bootstrap_source
        is guard.BASE.child_bootstrap_source
        and guard.NATIVE_OWNER_KEYS == REQUIRED_NATIVE_OWNER_FIELDS,
        "reject exact genuine V3-inherited immutable V2 guard identity",
    )
    checks = 1
    for role in ("bridge", "engine"):
        owner = guard.synthetic_owner(FAMILY, role)
        require(
            set(owner) == REQUIRED_NATIVE_OWNER_FIELDS
            and policy._strict_child_owner(owner, FAMILY, role) is owner,
            "reject exact source-only 14-field first-party V5 owner",
        )
        checks += 1
        for key in sorted(REQUIRED_NATIVE_OWNER_FIELDS):
            missing = dict(owner)
            missing.pop(key)
            checks += rejected_guard_control(
                guard,
                lambda item=missing, expected=role:
                    policy._strict_child_owner(item, FAMILY, expected),
                "missing genuine V3 owner field " + role + "/" + key,
            )
        extra = dict(owner)
        extra["invented"] = True
        checks += rejected_guard_control(
            guard,
            lambda item=extra, expected=role:
                policy._strict_child_owner(item, FAMILY, expected),
            "invented genuine V3 owner field " + role,
        )
        replacements = (
            ("absolute_path", ROOT + "/candidates/foreign.so"),
            ("bytes", owner["bytes"] + 1),
            ("device", PRIVATE_DEVICE),
            ("family", "rust"),
            ("file_name", "foreign.so"),
            ("inode", 0),
            ("mode", 0o644),
            ("native_loaded", True),
            ("nlink", 2),
            ("relative", "../foreign.so"),
            ("role", "engine" if role == "bridge" else "bridge"),
            ("sha256", "invalid"),
            ("size_bytes", owner["size_bytes"] + 1),
            ("uid", os.geteuid() + 1),
        )
        for key, value in replacements:
            forged = dict(owner)
            forged[key] = value
            checks += rejected_guard_control(
                guard,
                lambda item=forged, expected=role:
                    policy._strict_child_owner(item, FAMILY, expected),
                "substituted genuine V3 owner field " + role + "/" + key,
            )
    identity_source = (
        "def _rebar_v13_owned_actual_provider_frame():\n"
        "    return 1729\n"
    )
    identity_path = "<source-only-owned-zig-v13-provider-live-identity>"
    first = compile(
        identity_source, identity_path, "exec", dont_inherit=True,
    )
    second = compile(
        identity_source, identity_path, "exec", dont_inherit=True,
    )
    namespace = types.ModuleType("_rebar_zig_v13_synthetic_live_provider")
    exec(first, namespace.__dict__)
    function = namespace.__dict__[
        "_rebar_v13_owned_actual_provider_frame"
    ]
    independently_equal = guard.source_code(
        second, "_rebar_v13_owned_actual_provider_frame",
    )
    live = guard.actual_source_code(
        function,
        independently_equal,
        namespace.__dict__,
        "_rebar_v13_owned_actual_provider_frame",
    )
    require(
        live is function.__code__
        and live == independently_equal
        and live is not independently_equal,
        "accept only the actual live provider code, never recompiled identity",
    )
    checks += 1
    checks += rejected_guard_control(
        guard,
        lambda: guard.actual_source_code(
            function, independently_equal, {},
            "_rebar_v13_owned_actual_provider_frame",
        ),
        "forged source-equal live provider globals",
    )
    checks += rejected_guard_control(
        guard,
        lambda: guard.actual_source_code(
            function, independently_equal, namespace.__dict__,
            "_forged_zig_v13_provider",
        ),
        "forged source-equal live provider qualified name",
    )
    for event in (
        guard.CREATE_EVENT,
        "_interpreters.create",
        "_interpreters.exec",
    ):
        checks += rejected_guard_control(
            guard,
            lambda item=event: policy.audit(item, (1729, "fabricated")),
            "generated audit event is not actual interpreter execution: "
            + event,
        )
    for name in (
        "re", "_sre", "regex", "pcre", "candidates.rust_candidate",
    ):
        checks += rejected_guard_control(
            guard,
            lambda item=name: policy.check_import(item),
            "unprepared external or cross-family V3 matcher: " + name,
        )
    require(
        "re" not in sys.modules
        and "_sre" not in sys.modules
        and "concurrent.interpreters" not in sys.modules
        and not any(
            name == "candidates" or name.startswith("candidates.")
            for name in sys.modules
        ),
        "reject a real child, matcher, candidate, or provider in V3 controls",
    )
    return checks


def verify_source_worker_order(source_sha):
    own = os.stat(ROOT + "/" + SELF, follow_symlinks=False)
    raw = read_owner((
        SELF, pin(source_sha, "actual worker source"),
        own.st_size, own.st_ino,
    ))
    tree = ast.parse(raw.decode("utf-8", "strict"))
    workers = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "worker"
    ]
    require(len(workers) == 1, "reject substituted actual worker function")
    calls = sorted(
        (
            node.lineno,
            node.func.attr,
            node,
        )
        for node in ast.walk(workers[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and (
            node.func.value.id == "policy"
            and node.func.attr in ("install", "prepare_family")
            or node.func.value.id == "importlib"
            and node.func.attr == "import_module"
        )
    )
    install = [
        lineno for lineno, name, _ in calls if name == "install"
    ]
    prepare = [
        lineno for lineno, name, _ in calls if name == "prepare_family"
    ]
    candidate = [
        lineno
        for lineno, name, node in calls
        if name == "import_module"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "candidates.zig_candidate"
    ]
    require(
        len(install) == len(prepare) == len(candidate) == 1
        and install[0] < prepare[0] < candidate[0],
        "reject V3 installation/preparation before the only candidate import",
    )
    active = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "active_owner"
    ]
    require(
        len(active) == 1
        and any(
            isinstance(node, ast.Name)
            and node.id == "REQUIRED_NATIVE_OWNER_FIELDS"
            for node in ast.walk(active[0])
        )
        and any(
            isinstance(node, ast.Constant)
            and node.value == "native_loaded"
            for node in ast.walk(active[0])
        ),
        "reject incomplete actual V3 first-party 14-field native ownership",
    )
    return 2


def hostile_source_controls(state, wall, args):
    checks = 0
    for name in (
        "re", "_sre", "regex", "re2", "ctypes", "subprocess", "socket",
        "threading", "multiprocessing", "gzip", "json", "pathlib",
        "tempfile", "time", "unittest", "concurrent.interpreters",
        "_interpreters", "candidates", "candidates.zig_candidate",
        "candidates.rust_candidate", "candidates._zig_bridge",
    ):
        checks += reject(
            lambda value=name: builtins.__import__(value),
            "forbidden physically guarded source import " + name,
        )
    for path in (
        RECOVERY,
        EXTERNAL_LOCPATH,
        "/tmp/rebar-phase2-zig-scanner-phrase-source-build-v13-yhzrep3u",
        ROOT + "/candidates/_zig_probe.so",
        ROOT + "/candidates/_zig_bridge.cpython-314-x86_64-linux-gnu.so",
        ROOT + "/candidates/zig_candidate.py",
        ROOT + "/candidates/rust_candidate.py",
        ROOT + "/oracle/phase2/evidence/"
        "repaired-zig-original-campaign-v12-phase2-v13-zig-"
        "guard-clean-v1-original-p0-v12-failures.json.gz",
        ROOT + "/performance/final-holdout.json",
        ROOT + "/README.md",
    ):
        checks += reject(
            lambda value=path: os.open(value, os.O_RDONLY),
            "forbidden private/native/archive/holdout source path " + path,
        )
    for operation, label in (
        (
            lambda: os.open(ROOT + "/" + SELF, os.O_WRONLY),
            "V13 source mutation",
        ),
        (
            lambda: os.open(
                ROOT + "/" + LIFETIME_ADAPTER[0], os.O_RDWR,
            ),
            "lifetime candidate source mutation",
        ),
        (
            lambda: builtins.open(ROOT + "/" + CONTRACT, "w"),
            "canonical contract filesystem write",
        ),
        (
            lambda: os.mkdir("/tmp/rebar-zig-v13-source-forbidden"),
            "source-only private mutation",
        ),
        (
            lambda: sys.audit("ctypes.dlopen", "forbidden"),
            "source-only first-party native library load",
        ),
        (
            lambda: sys.audit(
                "ctypes.dlsym", None, "rebar_zig_compile",
            ),
            "source-only native regex-symbol access",
        ),
        (
            lambda: sys.audit(
                "subprocess.Popen", "zig", [], None, None,
            ),
            "source-only compiler/candidate worker process",
        ),
        (
            lambda: sys.audit("socket.connect", None, None),
            "source-only external network",
        ),
        (
            lambda: sys.audit(
                "cpython.PyInterpreterState_New", 1729, "forged",
            ),
            "forged or real source-only child creation",
        ),
        (
            lambda: pin("x" * 63, "truncated"),
            "incomplete independent caller pin",
        ),
        (
            lambda: relative("../holdout"),
            "escaped source-only physical owner",
        ),
    ):
        checks += reject(operation, label)
    raw = read_owner(PARENT_ADAPTER)
    checks += reject(
        lambda: normalize(
            raw.replace(b"class Scanner:", b"class ScanneR:", 1),
        ),
        "changed complete immutable scanner",
    )
    checks += reject(
        lambda: normalize(
            raw.replace(
                b"import ctypes\n", b"import ctypes as x\n", 1,
            ),
        ),
        "changed historical dead first-party loader",
    )
    checks += reject(
        lambda: public_campaign_diagnostics({}),
        "omitted actual public original-suite diagnostics",
    )
    checks += reject(
        lambda: public_stream_owner({
            "bytes": 0,
            "sha256": "invalid",
            "complete": True,
        }),
        "forged canonical actual worker stream",
    )
    for suffix in ("success", "failures"):
        expected = publication_stem(suffix)
        require(
            expected
            == "repaired-zig-original-campaign-v13-"
            + LABEL
            + "-"
            + suffix
            and not expected.startswith(
                "repaired-zig-original-campaign-v12-"
            ),
            "reject a misversioned actual V13 publication outcome",
        )
        checks += 1
        checks += reject(
            lambda outcome=suffix: publication_stem(
                outcome,
                observed=(
                    "repaired-zig-original-campaign-v12-"
                    + LABEL
                    + "-"
                    + outcome
                ),
            ),
            "inherited V12 publication prefix for V13 " + suffix,
        )
    checks += reject(
        lambda: publication_stem("invented"),
        "invented V13 success or failure publication",
    )
    for mode in (
        "--run", "--worker", "--recover", "--build", "--apply",
        "--benchmark", "--install",
    ):
        checks += reject(
            lambda value=mode: parse([value]),
            "actual campaign without complete independent authority " + mode,
        )
    predecessor = state["predecessor"]
    receipt = state["publication"]
    for field, value in (
        ("actual_candidate_workers", 12),
        ("unique_candidate_worker_count", 12),
        ("completed_suite_count", 13),
        ("verified_passing_case_count", 4608),
        ("observed_semantic_mismatch_lower_bound", 1699),
        ("semantic_mismatch_count", 0),
        ("candidate_qualified", True),
        ("infrastructure_failure_count", 0),
    ):
        checks += reject(
            lambda name=field, changed=value: validate_publication(
                predecessor,
                altered_publication(
                    receipt, field=name, value=changed,
                ),
            ),
            "invented actual V12 original evidence: " + field,
        )
    checks += reject(
        lambda: validate_publication(
            predecessor, altered_publication(receipt, warning=True),
        ),
        "removed genuine actual V12 deallocator warning",
    )
    checks += reject(
        lambda: validate_publication(
            predecessor, altered_publication(receipt, child=True),
        ),
        "fabricated V12 real child matching or guard installation",
    )
    original = state["clean_adapter"]
    repaired = state["repaired_adapter"]
    for needle, replacement, label in (
        (
            REPAIRED_DEALLOCATOR.encode("utf-8"),
            REPAIRED_DEALLOCATOR.replace(
                "_free=_zig_bridge.free", "_free=getattr", 1,
            ).encode("utf-8"),
            "uncached first-party lifetime release",
        ),
        (
            REPAIRED_DEALLOCATOR.encode("utf-8"),
            REPAIRED_DEALLOCATOR.replace(
                "_getattr=getattr", "_getattr=None", 1,
            ).encode("utf-8"),
            "uncached lifetime attribute lookup",
        ),
        (
            b"            self._handle = None\n"
            b"            _free(handle)\n",
            b"            _free(handle)\n"
            b"            self._handle = None\n",
            "release before ownership is cleared",
        ),
        (
            b"            _free(handle)\n",
            b"            try:\n"
            b"                _free(handle)\n"
            b"            except Exception:\n"
            b"                pass\n",
            "suppressed genuine lifetime release error",
        ),
        (
            b"class Scanner:",
            b"class ScanneR:",
            "changed lifetime scanner semantics",
        ),
        (
            b"from candidates import _zig_bridge\n",
            b"from candidates import _rust_bridge\n",
            "borrowed cross-family native bridge",
        ),
    ):
        require(
            repaired.count(needle) == 1,
            "missing exact hostile lifetime source control: " + label,
        )
        forged = repaired.replace(needle, replacement, 1)
        checks += reject(
            lambda item=forged: deallocator_shape(item, repaired=True),
            label,
        )
        checks += reject(
            lambda item=forged: prove_lifetime_adapter(original, item),
            "whole-source lifetime proof: " + label,
        )
    checks += synthetic_evidence_controls(state["producer"])
    checks += synthetic_first_party_namespace_controls()
    checks += synthetic_zig_observer_proxy_controls()
    checks += synthetic_zig_direct_core_controls()
    checks += synthetic_bounded_worker_json_controls(
        state["producer"],
    )
    checks += synthetic_authenticated_surface_envelope_controls(
        state["producer"],
    )
    checks += synthetic_injective_worker_unicode_controls(
        state["producer"],
    )
    checks += synthetic_lifetime_controls()
    checks += synthetic_v3_guard_controls(state)
    checks += verify_source_worker_order(
        args["--source-sha256"],
    )
    require(
        checks >= 160 and wall.denials >= 38,
        "reject incomplete V3/lifetime/Unicode/physical hostile controls",
    )
    clean()
    return checks


def source_mode(mode, args):
    with SourceWall() as wall:
        if mode == "--render-contract":
            state = context(
                args["--source-sha256"],
                args["--protocol-sha256"],
            )
            return state["producer"].canonical(contract_value(
                args["--source-sha256"],
                args["--protocol-sha256"],
                state,
            ))
        state = verify(
            args["--source-sha256"],
            args["--protocol-sha256"],
            args["--contract-sha256"],
        )
        checks = (
            hostile_source_controls(state, wall, args)
            if mode == "--self-test" else 0
        )
        clean()
        result = {
            "schema": SCHEMA + (
                "-source-self-test" if mode == "--self-test"
                else "-verified-frozen-context"
            ),
            "status": "PASS",
            "family": FAMILY,
            "source_sha256": args["--source-sha256"],
            "protocol_sha256": args["--protocol-sha256"],
            "contract_sha256": args["--contract-sha256"],
            "immutable_guard_version": 3,
            "immutable_guard_source_sha256": GUARD[0][1],
            "immutable_guard_protocol_sha256": GUARD[1][1],
            "immutable_guard_contract_sha256": GUARD[2][1],
            "guard_v2_source_sha256": GUARD_V2[0][1],
            "immutable_producer_source_sha256": PRODUCER[0][1],
            "lifetime_adapter_sha256": LIFETIME_ADAPTER[1],
            "original_case_execution_denominator": 31237,
            "original_suite_count": 13,
            "original_obligation_count": 73,
            "original_crosswalk_count": 34,
            "named_private_waiver_count": 13,
            "supplemental_reference_case_count": 8244,
            "supplemental_candidate_matching": "NOT RUN",
            "historical_v12_actual_candidate_workers": 13,
            "historical_v12_unique_candidate_workers": 13,
            "historical_v12_completed_suite_count": 12,
            "historical_v12_verified_passing_suite_count": 7,
            "historical_v12_verified_passing_case_count": 4607,
            "historical_v12_measured_semantic_failure_count": 5,
            "historical_v12_semantic_mismatch_lower_bound": 1700,
            "historical_v12_semantic_mismatch_count": "NOT MEASURED",
            "historical_v12_warning_observed_suite_count": 13,
            "historical_v12_complete_stderr_bytes": 311416,
            "historical_v12_actual_prepared_interpreter_count": 0,
            "historical_v12_actual_case_interpreter_exec_calls": 0,
            "historical_v12_reported_child_guard_count": 1,
            "historical_v12_reported_count_proves_installation": False,
            "historical_v12_original_child_error": (
                "runtime guard blocked unattested-child-bootstrap"
            ),
            "v3_native_owner_field_count": 14,
            "v3_exact_v2_prepare_function": True,
            "v3_exact_v2_prepare_globals": True,
            "v3_actual_provider_frame_required": True,
            "expected_real_child_interpreters": 11,
            "expected_original_case_child_exec_calls": 394,
            "expected_total_real_child_exec_calls": 416,
            "actual_child_interpreters_created": 0,
            "actual_child_case_exec_calls": 0,
            "actual_child_guards_installed": 0,
            "historical_native_build_process_count": 26,
            "historical_native_build_phase_count": 2,
            "source_only_hostile_controls": checks,
            "synthetic_v3_live_frame_and_owner_controls": (
                "PASS" if mode == "--self-test" else "NOT RUN"
            ),
            "synthetic_lifetime_controls": (
                "PASS" if mode == "--self-test" else "NOT RUN"
            ),
            "synthetic_unicode_and_full_worker_controls": (
                "PASS" if mode == "--self-test" else "NOT RUN"
            ),
            "source_only_effects": {key: 0 for key in ZERO_KEYS},
            "candidate_matching": "NOT RUN",
            "runtime_non_delegation": "NOT ESTABLISHED",
            "repaired_warning": "NOT MEASURED",
            "repaired_subinterpreter": "NOT MEASURED",
            "qualified_candidate_count": 0,
            "holdout_case_count": 14155776,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "winner_selected": False,
        }
        return state["producer"].canonical(result)


def parse(arguments):
    modes = {
        "--self-test",
        "--verify-frozen-context",
        "--render-contract",
        "--run",
        "--worker",
        "--recover",
    }
    selected = [item for item in arguments if item in modes]
    require(
        len(selected) == 1,
        "select exactly one independently pinned V13 campaign action",
    )
    mode = selected[0]
    source_options = {
        "--source-sha256",
        "--protocol-sha256",
    }
    actual_options = {name for name, _ in ACTUAL_CALLER_PINS}
    allowed = source_options | {
        "--contract-sha256",
        "--family",
        "--label",
        "--suite",
        "--recovery-journal-sha256",
    } | actual_options
    parsed = {}
    index = 0
    while index < len(arguments):
        key = arguments[index]
        if key in modes:
            require(
                key == mode,
                "reject conflicting actual V13 execution authorities",
            )
            index += 1
            continue
        require(
            key in allowed and key not in parsed
            and index + 1 < len(arguments),
            "reject omitted, repeated, unknown, or unpinned V13 authority",
        )
        parsed[key] = arguments[index + 1]
        index += 2
    if mode == "--render-contract":
        required = set(source_options)
    elif mode in ("--self-test", "--verify-frozen-context"):
        required = source_options | {"--contract-sha256"}
    else:
        required = source_options | {
            "--contract-sha256", "--family", "--label",
        } | actual_options
        if mode in ("--worker", "--recover"):
            required.add("--recovery-journal-sha256")
        if mode == "--worker":
            required.add("--suite")
    require(
        set(parsed) == required,
        "require every independent source/guard/native/lifetime campaign pin",
    )
    return mode, parsed


def main():
    mode, args = parse(list(sys.argv[1:]))
    if mode in (
        "--self-test", "--verify-frozen-context", "--render-contract",
    ):
        output = source_mode(mode, args)
    elif mode == "--worker":
        output = worker_canonical(worker(args))
    elif mode == "--recover":
        state = recover(args)
        producer = load(
            PRODUCER[0], "_rebar_zig_v13_exact_recovery_output",
        )
        output = producer.canonical(state)
    else:
        state = campaign(args)
        producer = load(
            PRODUCER[0], "_rebar_zig_v13_exact_campaign_output",
        )
        output = producer.canonical(state)
    require(
        type(output) is bytes and bool(output),
        "reject incomplete source-only or actual canonical worker evidence",
    )
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        if isinstance(error, SystemExit):
            raise
        sys.stderr.write(
            "first-party V3-guarded lifetime Zig original campaign rejected: "
            + type(error).__qualname__ + ": " + str(error) + "\n"
        )
        raise SystemExit(1) from error
