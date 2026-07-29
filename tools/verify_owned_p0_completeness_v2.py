#!/usr/bin/env python3
"""Verify the additive, fail-closed Python ``re`` correctness crosswalk."""

from __future__ import annotations

import sys


_BOOT_MODULES = frozenset(sys.modules)
if "re" in _BOOT_MODULES or "_sre" in _BOOT_MODULES:
    raise SystemExit("the source-only P0 crosswalk must start without re or _sre")

import builtins
import hashlib
import os
import stat


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
SOURCE = "tools/verify_owned_p0_completeness_v2.py"
PROTOCOL = "oracle/phase1/P0-COMPLETENESS-V2.md"
CONTRACT = "oracle/phase1/p0-completeness-v2.json"
SCHEMA = "rebar-cpython-re-p0-completeness-v2"
GOAL_SHA256 = "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
ORIGINAL_CASES = 31_237
SUITE_COUNT = 13
PRIVATE_WAIVER_COUNT = 13
FUZZ_CASES = 8_244
FUZZ_BYTES = 7_602_476
FUZZ_SHA256 = "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2"
CORRECTED_PUBLIC_SHA256 = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
CORRECTED_CACHE_SHA256 = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
HISTORICAL_PUBLIC_SHA256 = "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
PUBLIC_MATRIX_SHA256 = "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
PUBLIC_CACHE_IDS_SHA256 = "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
PUBLIC_CACHE_MATRIX_SHA256 = "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
SIGNATURE_MATRIX_SHA256 = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
IMPORT_MATRIX_SHA256 = "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
LARGE_MATRIX_SHA256 = "a105aea287d093ff977819dda8971f592c3ed396eabd3133e5c52838ce8e2f65"
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_OWNER_BYTES = 8 * 1024 * 1024
MAX_JSON_DEPTH = 64
READ_CHUNK = 65_536
MAX_RECORD_BYTES = 256 * 1024

# Every row is an already published, private, plaintext file.  No archive,
# candidate, installed module, temporary path, compiler, or holdout is a row.
OWNERS = (
    ("goal", "GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 2064, 31364044),
    ("v1_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md", "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798", 10392, 2064, 524381),
    ("v1_inventory", "oracle/phase1/p0-completeness-v1.json", "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f", 45632, 2064, 524385),
    ("v1_verifier", "tools/verify_p0_completeness_v1.py", "0bb256c3d1140688f0f466d90cae020345aafcb5d3e8130b38b09e9de3930a0c", 118040, 2064, 432204),
    ("upstream_protocol", "oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md", "21e77143bbec1f54faa6fc8a74a842808e32bd36815802a0df3ddfef11c597e1", 9201, 2064, 432207),
    ("upstream_manifest", "oracle/cpython-3.14.6/manifest-v5.json", "41b598475a6f756bf63dcd71141d602da05ebb7a810525c45b6c07635b78c0d7", 75694, 2064, 432193),
    ("upstream_test_re", "oracle/cpython-3.14.6/test_re.py", "879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2", 150895, 2064, 428437),
    ("upstream_re_tests", "oracle/cpython-3.14.6/re_tests.py", "ec04a2b2a77338d20b37d931693c7e588a2896d3c73c7b4b47973e24c13b5aab", 26552, 2064, 428438),
    ("original_bounded_v5_source", "tools/independent_original_cpython_suite_v5.py", "8e499c03d076cec59da44a2d7dac15bdec6eb49bfec562cbd3dd4893cf3bdfce", 123750, 2064, 431594),
    ("public_v3_source", "tools/rust_public_practice_benchmark_v1.py", "d74932c13bdda64e1340c958cbea48d65db36531b849e202dfc16170de150b37", 80268, 2064, 430397),
    ("scanner_v3_source", "tools/rust_scanner_differential_v1.py", "fcc82a76e7bcaaa25d92a8482d4dc611b643d887d7fd983db0906c7340b91fd7", 39826, 2064, 430580),
    ("buffer_v3_source", "tools/rust_memoryview_expand_differential_v1.py", "226f129f0e90b060c977e599e6e8369f5a5285890089c69108b718cfcb2980e6", 47223, 2064, 431004),
    ("managed_v1_source", "tools/independent_managed_buffer_lifetime_v1.py", "cedbab1227ea58a97d407cb339d2959a9f9be58a2085ce3106b65bb3385de489", 123890, 2064, 430528),
    ("scanner_verbose_v1_source", "tools/independent_scanner_verbose_comments_v1.py", "5508910eae3f5e59d2013bc9fa4f1a8948a823e27de09bf416de2fffc8e91c9d", 88737, 2064, 431462),
    ("public_types_v1_source", "tools/independent_public_type_identity_serialization_v1.py", "7ce0606da0d830ef8e9cf9b8e9b952a9836bf705254a23a65551832bf1d92e20", 150015, 2064, 432032),
    ("substitution_v2_source", "tools/independent_substitution_buffer_semantics_v2.py", "e7cc951b4fbb90b2826c3730bbb3b3e81b50e8a5eac8a3d758962358d9414573", 317541, 2064, 432058),
    ("shape_v2_source", "tools/independent_shape_changing_buffer_semantics_v2.py", "0262807f793a818307f2c8c6ecfd84bf970264a6ef5d656acf30c9d3606f0e2c", 137527, 2064, 432070),
    ("public_surface_v19_source", "tools/python_re_public_surface_oracle_stage19.py", "fda386f3c00be660a41e92d8005fc287706d9dc050967cf2b708cb6f8aba113e", 199366, 2064, 430521),
    ("subinterpreter_v2_source", "tools/python_re_subinterpreter_oracle_v2.py", "54735efb77a099feb2dd076723d3a93d81415226b9b9213307c32cc0f38c52c8", 151395, 2064, 432166),
    ("pep688_v4_source", "tools/python_re_buffer_exporter_oracle_v4.py", "8da0b8e5c5519e7335cd1b53ceb7042f1da1f902c486ad8ac35ddf53d8a04490", 162181, 2064, 432192),
    ("threaded_pattern_v1_source", "tools/python_re_threaded_pattern_oracle_v1.py", "05226e59736d8721a975eda8afa10247213999690c2766a7b3235c567b9f8276", 146417, 2064, 432206),
    ("public_context_protocol", "oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md", "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018", 10691, 2064, 524740),
    ("public_context_contract", "oracle/phase1/p0-public-type-reference-context-v1.json", "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b", 13965, 2064, 524741),
    ("public_context_source", "tools/verify_owned_public_type_reference_context_v1.py", "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc", 102474, 2064, 431631),
    ("public_falsification", "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json", "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670", 3892, 2064, 524739),
    ("public_reference_receipt", "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json", "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509, 2064, 524769),
    ("signature_protocol", "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md", "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8", 8952, 2064, 524649),
    ("signature_contract", "oracle/phase1/p0-callable-introspection-v1.json", "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749, 2064, 524650),
    ("signature_worker", "tools/verify_python_re_callable_introspection_v1.py", "5a64fb4546bdccd13b6d8d9ba32a7472b01cb86dd0d9f2c643678e6bbf919653", 75608, 2064, 428944),
    ("signature_reference_protocol", "oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md", "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f", 7487, 2064, 524684),
    ("signature_reference_contract", "oracle/phase1/callable-introspection-reference-v2.json", "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42", 7253, 2064, 524694),
    ("signature_reference_source", "tools/run_owned_callable_introspection_reference_v2.py", "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4", 86258, 2064, 431230),
    ("signature_reference_receipt", "oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json", "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533, 2064, 524690),
    ("import_protocol", "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md", "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0", 7991, 2064, 524880),
    ("import_contract", "oracle/phase1/p0-public-entrypoint-import-v1.json", "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47", 9823, 2064, 524881),
    ("import_source", "tools/verify_public_entrypoint_import_v1.py", "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4", 83957, 2064, 431858),
    ("large_protocol", "oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md", "0a640ee044c52394fa897d0221d51dfc3d85e9abb95608367698f11fba8ca879", 5345, 2064, 524897),
    ("large_contract", "oracle/phase1/p0-large-input-indexing-v1.json", "23601fe4947c70979081d8248ee9891287e3fa618b554b97a8ee56024823bacf", 17322, 2064, 524819),
    ("large_source", "tools/verify_large_input_indexing_v1.py", "57a9e0d0e456b854cb46dfadb2b23db244597f01904fcf93587b1f5d8a5e4544", 99829, 2064, 431873),
    ("producer_v4_source", "tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782, 2064, 431710),
    ("producer_v4_protocol", "oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981, 2064, 524782),
    ("producer_v4_contract", "oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867, 2064, 524783),
    ("candidate_v10_source", "tools/run_frozen_p0_candidate_v10.py", "c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a", 91132, 2064, 431751),
    ("candidate_v10_protocol", "oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md", "2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae", 6792, 2064, 524827),
    ("candidate_v10_contract", "oracle/phase2/p0-candidate-protocol-v10.json", "8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737", 21238, 2064, 524828),
    ("fuzz_v1_protocol", "oracle/v1/P0.md", "30dc3dd121c8e2d7a080884923109164b4bbdf37103f56c2bac84727acbd4424", 4619, 2064, 427902),
    ("fuzz_v1_suite", "oracle/v1/suite.py", "097d51609c1f8d677a7ddb98bcb1a5c245764fff6246ee6239d642a264fb5fc9", 19888, 2064, 427903),
    ("fuzz_v1_runner", "tools/oracle.py", "fda0ca974afaea3e37106fce59169eaead387cf8f63e7b6f93bdee5992eab541", 19573, 2064, 427905),
    ("fuzz_v1_manifest", "oracle/v1/manifest.json", "4c3e5ebd70ceb2352dfd6f0708ad8172d53b53dc3c9e42f2eeafb9e4736200ba", 1039, 2064, 427911),
    ("fuzz_v1_seeds", "oracle/v1/seeds.json", "75d159b2bfb9e3343c9bb3787b398db3de8a44f39b973ea74cd921257469feea", 156, 2064, 427943),
    ("fuzz_v1_expected", "oracle/v1/expected.jsonl", "983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed", 1203505, 2064, 427910),
    ("fuzz_v1_self", "oracle/v1/evidence/correctness-self.json", "517e948197ead373e74139aa86692efff861da4700bb7f4524a3e1b6b239bf54", 270, 2064, 427913),
    ("fuzz_v2_protocol", "oracle/v2/P0.md", "50fe34edd81ae22f3a2b8fb836a615fe625dc2b7c32ce0f045275554bf3b9e44", 2531, 2064, 428247),
    ("fuzz_v2_suite", "oracle/v2/suite.py", "a05912d8f3ef01e3f8ccd5e421647afd55a72963fefbfd431140ac5977b333a1", 12393, 2064, 428239),
    ("fuzz_v2_runner", "tools/oracle_v2.py", "f038145dc0527f802203e18556f03b4bba636bb219105dc38c675c52a23e0fbb", 14248, 2064, 428240),
    ("fuzz_v2_manifest", "oracle/v2/manifest.json", "91ce7da8cd0ebcdf2861fbb82cd531855631e52815aa8c1684f6a798da6563f6", 1359, 2064, 428246),
    ("fuzz_v2_seeds", "oracle/v2/seeds.json", "761d074856c36880db60965583207c78a46b8fced204e0f3b4e03e744fed74c7", 210, 2064, 428245),
    ("fuzz_v2_expected", "oracle/v2/expected.jsonl", "ae6a095bc0cd2b3ba1512a04f0d4fbe57916cf2d5b583fd4ecdda5c2c70a5bb2", 7602476, 2064, 428243),
    ("fuzz_v2_self", "oracle/v2/evidence/correctness-self.json", "98e91a0b0ca63ec6718e32d682219df65d12bf0d947fe54934caf4b42412b8ce", 270, 2064, 428249),
    ("overview_v60_renderer", "tools/render_candidate_current_overview_v60.py", "66975e14fed35b40e63fb332364d54a5f40aa714b40757580db57018fbd15534", 84809, 2064, 431602),
    ("overview_v60_inputs", "docs/evidence/candidate-current-overview-v60.inputs.json", "b63da6a1b3f135a2e303b2ffb807a04aa25405d3f37c3233857a70a5e0e5cc3d", 921967, 2064, 432171),
    ("overview_v60_summary", "docs/evidence/candidate-current-overview-v60.json", "f766cdd9bee4d8a2eec8c4bd70148a4c58021156d36cb1d00858bce1d0d4e025", 2516206, 2064, 432172),
    ("overview_v60_svg", "docs/evidence/candidate-current-overview-v60.svg", "5870676d9ccac46c04538b9ac77bd27d7b07bec5973d521635deef4a64be7fec", 14821, 2064, 432173),
)
OWNER_BY_ROLE = {item[0]: item for item in OWNERS}

SUITES = (
    ("original_bounded_v5", 151, None, "93f0fe07cf6cc0fbe0332b748ca61768f3b966bd5c0fdd81d024520a7deff240", "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"),
    ("public_v3", 864, "5928217332825411633", "367d30517874745b11d6facf43685a906784dc94c0246dc6a6381c17afcc776e", "0ae84d65f16976e046a267704585306c3968703194d26bbc3c5223b746304f7c"),
    ("scanner_v3", 1024, "5999710933164053041", "83a8ad125b36846c1790ca01564305b2ab9714185f972efa838740b7bbf4b55c", "37de08e1991adf28990e35b72c2130ebafa78c72b04750d28550cce08555666d"),
    ("buffer_v3", 768, "5567953616029762609", "b40fb92f42c7019a73eec72800077f262f1a6be516886a6ddda372e24807eb60", "8312263785cd49f7283ab8c6fac13443befe9c5a3d739b2e068aebdcf3f59b75"),
    ("managed_v1", 1024, "5567095966978627121", "28ef84b6989542ba8865c98e5296639c780c786078e2a99c7c0a95bfcb4b0976", "80293f5332300220f38c3f017d38611a5514b1b686918e692a53491945b196df"),
    ("scanner_verbose_v1", 2854, "5999725261024810545", "01bca287cd481a5e4ae134b910911e2e2f8f1501eebb7ffd2947092ab170d17b", "d7e2d499eb4dbe6ae0f8743d8b152e4835898656daa8b3167598636ef7be6012"),
    ("public_types_v1", 6912, "6077977430793212465", "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123", "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"),
    ("substitution_v2", 5120, "6004778603531028017", "26f46fe7f1abc5135d1265a7882ccd4a2e2b45cdec80ba293520fda510235b54", "2bc65461b9ac60fd19a3c66856bd33ee48db038ab6a5de62193837800840f61b"),
    ("shape_v2", 10240, "6001118316486346290", "10fe3e3fd4b4650bff1da6a745b5b883f01033ed14df3f9795aa2f7a30c6d8d8", "58bbc78828ba2d4cde6b99cbebea815ce9381cda24d0acec03f6cc095b8b643c"),
    ("public_surface_v19", 1376, "2026072483", "7885a9ac0b2e22db88db7dc4ab9c33c4ba229ddb6d15fcdd4bfe9b0d6f10e8aa", "c002fc9e82bb73e592ffa3b5ba73731070004eb892cf85cfcf288fe7693b0aef"),
    ("subinterpreter_v2", 128, "2026072501", "edda77658c5eef9746c6d4769734c69e40db4c9d986171fa63799093f4cb62d3", "450fccc859099ca78aec725911b6195695cd932ad281af931ca7945cec8c51e8"),
    ("pep688_v4", 264, None, "2d9eb4e637387bc89020d2f883f59ff03dd98cbebd2f2aaa2a30dc55d0836891", "7827586e0c7d4f43ac1fbd288f6b28f6a44b810b46274830d3803505c76692a8"),
    ("threaded_pattern_v1", 512, "2026072701", "a7d467e3e529204946fe00ddb819e734421e7087ea909af9ec24b757e42afa0b", "928ea100d6fdaecc7c1dcf01e32c24fd98a146964c0955989a8149c1216ffe81"),
)
PRIVATE_WAIVERS = (
    "DebugTests.test_debug_flag", "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one", "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable", "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness", "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules", "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc", "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
INHERITED_OBLIGATIONS = (
    "API-EXPORTS", "API-FLAGS", "API-COMPILE", "API-SEARCH", "API-MATCH",
    "API-FULLMATCH", "API-FINDALL", "API-FINDITER", "API-SPLIT", "API-SUB",
    "API-SUBN", "API-ESCAPE", "API-PATTERN", "API-MATCH-OBJECT", "API-SCANNER",
    "S-LITERAL", "S-DOT-CLASS", "S-ANCHOR", "S-QUANTIFIER", "S-POSSESSIVE",
    "S-ALTERNATION", "S-GROUP", "S-BACKREF", "S-CONDITIONAL", "S-LOOKAROUND",
    "S-ATOMIC", "S-INLINE", "S-VERBOSE", "S-UNICODE", "S-ASCII", "S-LOCALE",
    "S-EMPTY", "S-WINDOW", "E-PATTERN", "E-TYPE", "E-TEMPLATE", "E-WARNING",
    "E-DEBUG", "API-GENERIC", "API-BYTESLIKE", "API-REPRESENTATION",
    "API-MATCH-COPY", "E-DEPRECATION", "S-LOOKBEHIND-REF", "S-DEEP-FUZZ",
)
ADDITIONAL_OBLIGATIONS = (
    "API-UPSTREAM-ALL-165", "API-UPSTREAM-403-CORPUS",
    "API-UPSTREAM-11-EXTERNAL-ASSERTIONS", "API-MODULE-SCANNER",
    "API-SCANNER-CALLBACK-ORDER", "API-SCANNER-LEXICON-IDENTITY",
    "API-VERBOSE-ESCAPED-COMMENTS", "API-PUBLIC-TYPE-IDENTITY",
    "API-GENERIC-ALIASES", "API-WEAKREF-COPY-ATOMICITY",
    "API-PICKLE-PROTOCOLS-0-5", "API-PUBLIC-CACHE-PURGE",
    "API-PEP688-DIRECT-EXPORTER", "API-PEP688-NESTED-EXPORTER",
    "API-BUFFER-ACQUIRE-RELEASE-ORDER", "API-SCANNER-GC-RETAINED-CYCLE",
    "API-SHAPE-CHANGING-EXPORTER", "API-CALLBACK-EXCEPTION-IDENTITY",
    "API-LOCALE-CROSS-TRANSITION", "API-SUBINTERPRETER-ISOLATION",
    "API-SUBINTERPRETER-TEARDOWN", "S-UNICODE-ESCAPED-LONE-SURROGATES",
    "E-EXACT-PATTERN-ATTRIBUTES", "E-WARNING-CATEGORY-MESSAGE-LOCATION",
    "E-64BIT-INDEX-OVERFLOW", "E-FIXTURE-VERSUS-USER-EXCEPTION",
    "API-THREAD-SHARED-PATTERN-REENTRANCY", "API-MODULE-VERSION-METADATA",
)
SEEDS = {
    "deep_bytes": 1979121302, "deep_str": 1979121301,
    "invalid_patterns": 1511506921, "invalid_templates": 1511506922,
    "properties": 1511506920, "valid_bytes": 1511506919,
    "valid_str": 1511506918,
}
FUZZ_KINDS = {
    "byteslike": 11, "byteslike-escape": 2, "cache": 1, "call": 7359,
    "compile": 2, "debug": 1, "error": 456, "escape": 2, "exports": 1,
    "flags": 1, "generic": 4, "match-copy": 3, "pattern-equality": 1,
    "positional-warning": 3, "property": 384, "representation": 5,
    "roundtrip": 1, "scanner": 2, "warning": 5,
}
BLOCKERS = (
    "SUPPLEMENTAL_8244_TWO_INDEPENDENT_REFERENCE_PROCESSES_NOT_RUN",
    "SUPPLEMENTAL_8244_CANDIDATE_GATE_NOT_RUN",
    "PUBLIC_IMPORT_FAIL",
    "PUBLIC_CALLABLE_SIGNATURE_CANDIDATE_GATE_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SEARCH_NOT_RUN",
    "FULL_SIZE_2GIB_CANDIDATE_SUBSTITUTION_NOT_RUN",
    "RUNTIME_NO_DELEGATION_NOT_ESTABLISHED",
)


class FreezeError(Exception):
    """A frozen compatibility owner or real phase boundary changed."""


_WALL_ENABLED = False
_BLOCKED_EVENTS: dict[str, int] = {}
_ALLOWED_SOURCE_PATHS = frozenset(
    [ROOT + "/" + SOURCE, ROOT + "/" + PROTOCOL, ROOT + "/" + CONTRACT]
    + [ROOT + "/" + row[1] for row in OWNERS]
)


def require(condition: object, message: str) -> None:
    if not condition:
        raise FreezeError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def checked_hash(value: object, name: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value),
            "an exact lowercase SHA-256 is required: " + name)
    return value


def no_forbidden_modules() -> None:
    require("re" not in sys.modules and "_sre" not in sys.modules,
            "the source-only verifier imported a Python regular-expression engine")
    require(not any(name == "rebar" or name.startswith("rebar.")
                    or name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "the source-only verifier imported a replacement or candidate")


def deny(event: str, reason: str) -> None:
    _BLOCKED_EVENTS[event] = _BLOCKED_EVENTS.get(event, 0) + 1
    raise FreezeError("physical source-only wall blocked " + event + ": " + reason)


def audit_wall(event: str, arguments: tuple[object, ...]) -> None:
    if event == "open":
        path = arguments[0] if arguments else None
        flags = arguments[2] if len(arguments) > 2 else None
        if type(path) is not str or path not in _ALLOWED_SOURCE_PATHS:
            deny(event, "unlisted, temporary, archive, holdout, or candidate path")
        if type(flags) is not int:
            deny(event, "a checked read-only file descriptor is mandatory")
        forbidden = (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC
                     | os.O_APPEND | getattr(os, "O_TMPFILE", 0))
        if flags & forbidden:
            deny(event, "source-only verification cannot create or change a file")
        if getattr(os, "O_NOFOLLOW", 0) and not flags & os.O_NOFOLLOW:
            deny(event, "a frozen owner cannot be followed through a symlink")
        return
    if event == "import":
        deny(event, "no modules may be imported after the source wall is active")
    if (event == "exec" or event == "compile" or event.startswith("ctypes.")
            or event.startswith("subprocess.") or event.startswith("socket.")
            or event.startswith("multiprocessing.")
            or event.startswith("threading.") or event.startswith("_thread.")
            or event.startswith("time.")
            or event in {
                "os.system", "os.fork", "os.forkpty", "os.posix_spawn",
                "os.spawn", "os.exec", "os.chdir", "os.putenv", "os.unsetenv",
                "os.remove", "os.rename", "os.replace", "os.mkdir", "os.rmdir",
                "os.symlink", "os.link", "os.chmod", "os.chown", "os.truncate",
                "os.utime", "code.__new__", "function.__new__", "marshal.loads",
            }):
        deny(event, "execution, compilation, native loading, processes, clocks, network, or mutation is forbidden")


def install_wall() -> None:
    global _WALL_ENABLED
    require(not _WALL_ENABLED, "the physical source-only wall cannot be installed twice")
    no_forbidden_modules()
    sys.addaudithook(audit_wall)
    _WALL_ENABLED = True
    no_forbidden_modules()


def quote(value: str) -> str:
    require(type(value) is str, "canonical JSON requires real string keys")
    output = ['"']
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f",
               "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for char in value:
        code = ord(char)
        if char in escapes:
            output.append(escapes[char])
        elif code < 0x20 or 0x7f <= code <= 0xffff:
            output.append("\\u" + format(code, "04x"))
        elif code > 0xffff:
            code -= 0x10000
            output.extend(("\\u" + format(0xd800 + (code >> 10), "04x"),
                           "\\u" + format(0xdc00 + (code & 0x3ff), "04x")))
        else:
            output.append(char)
    output.append('"')
    return "".join(output)


def canonical(value: object, depth: int = 0) -> str:
    require(depth <= MAX_JSON_DEPTH, "canonical JSON exceeds its strict depth limit")
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is str:
        return quote(value)
    if type(value) is int:
        return str(value)
    if type(value) is float:
        require(value == value and abs(value) != float("inf"),
                "non-finite JSON numbers cannot be frozen")
        return repr(value)
    if type(value) in (list, tuple):
        return "[" + ",".join(canonical(item, depth + 1) for item in value) + "]"
    if type(value) is dict:
        require(all(type(key) is str for key in value),
                "canonical JSON object keys must all be strings")
        return "{" + ",".join(quote(key) + ":" + canonical(value[key], depth + 1)
                              for key in sorted(value)) + "}"
    raise FreezeError("unsupported canonical JSON value: " + type(value).__name__)


class StrictJSON:
    """Decode bounded JSON without importing ``json`` and therefore ``re``."""

    def __init__(self, raw: bytes):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_JSON_BYTES,
                "JSON owner is empty or exceeds its frozen byte limit")
        try:
            self.text = raw.decode("utf-8", "strict")
        except UnicodeError as error:
            raise FreezeError("a frozen JSON owner is not strict UTF-8") from error
        self.index = 0

    def whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index] in " \t\r\n":
            self.index += 1

    def string(self) -> str:
        require(self.text[self.index:self.index + 1] == '"',
                "a quoted JSON object name or string is mandatory")
        self.index += 1
        output: list[str] = []
        ordinary = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                    "n": "\n", "r": "\r", "t": "\t"}
        while self.index < len(self.text):
            char = self.text[self.index]
            self.index += 1
            if char == '"':
                return "".join(output)
            if char != "\\":
                require(ord(char) >= 0x20, "a JSON string contains an unescaped control")
                output.append(char)
                continue
            require(self.index < len(self.text), "an incomplete JSON string escape")
            escaped = self.text[self.index]
            self.index += 1
            if escaped != "u":
                require(escaped in ordinary, "an invalid JSON string escape")
                output.append(ordinary[escaped])
                continue
            digits = self.text[self.index:self.index + 4]
            require(len(digits) == 4
                    and all(char in "0123456789abcdefABCDEF" for char in digits),
                    "a JSON Unicode escape must contain exactly four hex digits")
            self.index += 4
            code = int(digits, 16)
            if 0xd800 <= code <= 0xdbff:
                require(self.text[self.index:self.index + 2] == "\\u",
                        "an unpaired high JSON surrogate was rejected")
                low = self.text[self.index + 2:self.index + 6]
                require(len(low) == 4
                        and all(char in "0123456789abcdefABCDEF" for char in low),
                        "a low JSON surrogate must contain four hex digits")
                low_code = int(low, 16)
                require(0xdc00 <= low_code <= 0xdfff,
                        "an unpaired high JSON surrogate was rejected")
                self.index += 6
                output.append(chr(0x10000 + ((code - 0xd800) << 10)
                                  + low_code - 0xdc00))
            else:
                require(not 0xdc00 <= code <= 0xdfff,
                        "an unpaired low JSON surrogate was rejected")
                output.append(chr(code))
        raise FreezeError("an unterminated JSON string was rejected")

    def number(self) -> int | float:
        start = self.index
        if self.text[self.index:self.index + 1] == "-":
            self.index += 1
        require(self.index < len(self.text), "an incomplete JSON number was rejected")
        if self.text[self.index] == "0":
            self.index += 1
            require(self.index == len(self.text)
                    or self.text[self.index] not in "0123456789",
                    "a leading-zero JSON number was rejected")
        else:
            require(self.text[self.index] in "123456789",
                    "an invalid JSON number was rejected")
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
        fractional = False
        if self.text[self.index:self.index + 1] == ".":
            fractional = True
            self.index += 1
            beginning = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > beginning, "an incomplete JSON fraction was rejected")
        if self.text[self.index:self.index + 1] in ("e", "E"):
            fractional = True
            self.index += 1
            if self.text[self.index:self.index + 1] in ("+", "-"):
                self.index += 1
            beginning = self.index
            while self.index < len(self.text) and self.text[self.index] in "0123456789":
                self.index += 1
            require(self.index > beginning, "an incomplete JSON exponent was rejected")
        word = self.text[start:self.index]
        require(0 < len(word) <= 128, "a JSON number exceeds its strict digit bound")
        if not fractional:
            return int(word)
        value = float(word)
        require(value == value and abs(value) != float("inf"),
                "a non-finite JSON number was rejected")
        return value

    def value(self, depth: int = 0) -> object:
        require(depth <= MAX_JSON_DEPTH, "JSON exceeds the strict nesting bound")
        self.whitespace()
        require(self.index < len(self.text), "a JSON value is missing")
        char = self.text[self.index]
        if char == '"':
            return self.string()
        if char == "{":
            self.index += 1
            result: dict[str, object] = {}
            self.whitespace()
            if self.text[self.index:self.index + 1] == "}":
                self.index += 1
                return result
            while True:
                self.whitespace()
                key = self.string()
                require(key not in result, "a duplicate JSON object key was rejected: " + key)
                self.whitespace()
                require(self.text[self.index:self.index + 1] == ":",
                        "a JSON object colon is missing")
                self.index += 1
                result[key] = self.value(depth + 1)
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "}":
                    return result
                require(separator == ",", "an invalid JSON object separator was rejected")
        if char == "[":
            self.index += 1
            result_list: list[object] = []
            self.whitespace()
            if self.text[self.index:self.index + 1] == "]":
                self.index += 1
                return result_list
            while True:
                result_list.append(self.value(depth + 1))
                self.whitespace()
                separator = self.text[self.index:self.index + 1]
                self.index += 1
                if separator == "]":
                    return result_list
                require(separator == ",", "an invalid JSON array separator was rejected")
        if char == "-" or char in "0123456789":
            return self.number()
        for word, value in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(word, self.index):
                self.index += len(word)
                return value
        raise FreezeError("an invalid JSON value was rejected")

    def decode(self) -> object:
        result = self.value()
        self.whitespace()
        require(self.index == len(self.text), "trailing or multiple JSON documents were rejected")
        return result


def canonical_digest(value: object) -> str:
    return digest(canonical(value).encode("ascii"))


def owner_document(role: str) -> dict[str, object]:
    row = OWNER_BY_ROLE[role]
    return {"path": row[1], "sha256": row[2], "bytes": row[3],
            "device": row[4], "inode": row[5], "mode": "0600"}


def consume_fuzz_record(raw: bytes, state: dict[str, object]) -> None:
    require(type(raw) is bytes and 0 < len(raw) <= MAX_RECORD_BYTES,
            "a supplemental record exceeds the strict 256 KiB per-line bound")
    document = StrictJSON(raw).decode()
    require(type(document) is dict
            and set(document) == {"id", "kind", "obligations", "result"},
            "a supplemental record has missing, duplicate, or invented fields")
    identifier, kind = document.get("id"), document.get("kind")
    mapped = document.get("obligations")
    ids, obligations = state.get("case_ids"), state.get("mapped_ids")
    counts = state.get("kind_counts")
    require(type(ids) is set and type(obligations) is set and type(counts) is dict,
            "the supplemental corpus lost its bounded streaming state")
    require(type(identifier) is str and bool(identifier) and identifier not in ids,
            "a supplemental case identity is missing or duplicated")
    require(type(kind) is str and kind in FUZZ_KINDS,
            "a supplemental record has an unknown case kind")
    require(type(mapped) is list and len(mapped) > 0
            and all(type(item) is str and item in INHERITED_OBLIGATIONS
                    for item in mapped)
            and len(mapped) == len(set(mapped)),
            "a supplemental record has unknown or duplicate obligation IDs")
    ids.add(identifier)
    obligations.update(mapped)
    counts[kind] = counts.get(kind, 0) + 1
    if state["first_case_id"] is None:
        state["first_case_id"] = identifier
    state["last_case_id"] = identifier
    state["maximum_record_bytes"] = max(state["maximum_record_bytes"], len(raw))


def finish_fuzz_records(state: dict[str, object]) -> None:
    require(not state.get("tail"),
            "the supplemental corpus ends with a partial or non-newline record")
    require(type(state.get("case_ids")) is set
            and len(state["case_ids"]) == FUZZ_CASES
            and state.get("first_case_id") == "api.exports"
            and state.get("last_case_id") == "v2.deep.bytes.2047"
            and state.get("kind_counts") == FUZZ_KINDS
            and state.get("mapped_ids") == set(INHERITED_OBLIGATIONS)
            and state.get("maximum_record_bytes") == 83_667,
            "the 8,244 unique cases, 19 exact kinds, 45 mappings, or largest record changed")


def exact_reader(path: str, expected_hash: str, expected_size: int,
                 expected_device: int | None = None,
                 expected_inode: int | None = None, *, capture: bool = True,
                 expected_lines: int | None = None,
                 validate_records: bool = False) -> dict[str, object]:
    require(_WALL_ENABLED, "owner authentication requires the installed physical audit wall")
    checked_hash(expected_hash, path)
    require(type(path) is str and not path.startswith("/") and ".." not in path.split("/")
            and not path.endswith(".gz") and not path.endswith(".so"),
            "only an exact in-project plaintext owner may be authenticated")
    require(type(expected_size) is int and 0 < expected_size <= MAX_OWNER_BYTES,
            "a bounded exact owner size is required")
    absolute = ROOT + "/" + path
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(absolute, flags)
    except OSError as error:
        raise FreezeError("cannot open the exact private source owner: " + path) from error
    hasher = hashlib.sha256()
    parts: list[bytes] = []
    read_bytes = 0
    line_count = 0
    last_byte = b""
    state: dict[str, object] = {
        "tail": bytearray(), "case_ids": set(), "mapped_ids": set(),
        "kind_counts": {}, "first_case_id": None, "last_case_id": None,
        "maximum_record_bytes": 0,
    }
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode) == 0o600
                and before.st_nlink == 1 and before.st_size == expected_size,
                "owner is not an exact private, singly linked, regular file: " + path)
        if expected_device is not None:
            require(before.st_dev == expected_device,
                    "the immutable owner's device changed: " + path)
        if expected_inode is not None:
            require(before.st_ino == expected_inode,
                    "the immutable owner's inode changed: " + path)
        while read_bytes < expected_size:
            chunk = os.read(descriptor, min(READ_CHUNK, expected_size - read_bytes))
            require(type(chunk) is bytes and len(chunk) > 0,
                    "a frozen plaintext owner was truncated: " + path)
            hasher.update(chunk)
            read_bytes += len(chunk)
            line_count += chunk.count(b"\n")
            last_byte = chunk[-1:]
            if validate_records:
                tail = state["tail"]
                require(type(tail) is bytearray,
                        "the supplemental record lost its bounded line buffer")
                tail.extend(chunk)
                while True:
                    boundary = tail.find(b"\n")
                    if boundary < 0:
                        require(len(tail) <= MAX_RECORD_BYTES,
                                "an incomplete fuzz record exceeds 256 KiB")
                        break
                    require(boundary <= MAX_RECORD_BYTES,
                            "a complete fuzz record exceeds 256 KiB")
                    raw_line = bytes(tail[:boundary])
                    del tail[:boundary + 1]
                    consume_fuzz_record(raw_line, state)
            if capture:
                require(read_bytes <= MAX_JSON_BYTES,
                        "a captured source owner exceeded the bounded memory allowance")
                parts.append(chunk)
        require(os.read(descriptor, 1) == b"",
                "a frozen source owner grew during streaming: " + path)
        after = os.fstat(descriptor)
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                 before.st_ctime_ns, before.st_nlink)
                == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                    after.st_ctime_ns, after.st_nlink),
                "a source owner changed beneath its authenticated descriptor: " + path)
    finally:
        os.close(descriptor)
    require(read_bytes == expected_size and hasher.hexdigest() == expected_hash,
            "a complete plaintext owner does not match its published fingerprint: " + path)
    if expected_lines is not None:
        require(line_count == expected_lines and last_byte == b"\n",
                "the complete streamed corpus lost, added, or truncated a frozen case")
    if validate_records:
        finish_fuzz_records(state)
    result: dict[str, object] = {
        "path": path, "sha256": expected_hash, "bytes": expected_size,
        "device": before.st_dev, "inode": before.st_ino,
        "mode": "0600", "line_count": line_count,
    }
    if capture:
        result["raw"] = b"".join(parts)
    if validate_records:
        result.update({
            "record_case_id_count": len(state["case_ids"]),
            "record_first_case_id": state["first_case_id"],
            "record_last_case_id": state["last_case_id"],
            "record_kind_counts": state["kind_counts"],
            "record_mapped_obligation_ids": [
                name for name in INHERITED_OBLIGATIONS
                if name in state["mapped_ids"]
            ],
            "maximum_record_bytes": state["maximum_record_bytes"],
            "per_record_limit_bytes": MAX_RECORD_BYTES,
        })
    return result


def read_pinned(role: str, *, capture: bool = False,
                expected_lines: int | None = None,
                validate_records: bool = False) -> dict[str, object]:
    row = OWNER_BY_ROLE[role]
    return exact_reader(row[1], row[2], row[3], row[4], row[5],
                        capture=capture, expected_lines=expected_lines,
                        validate_records=validate_records)


def decoded(value: dict[str, object], role: str) -> dict[str, object]:
    raw = value.get("raw")
    require(type(raw) is bytes, "a captured bounded JSON owner is required: " + role)
    result = StrictJSON(raw).decode()
    require(type(result) is dict, "a frozen JSON owner must contain exactly one object: " + role)
    return result


def clone(value: object) -> object:
    if type(value) is dict:
        return {key: clone(item) for key, item in value.items()}
    if type(value) is list:
        return [clone(item) for item in value]
    if type(value) is tuple:
        return tuple(clone(item) for item in value)
    return value


def validate_original(inventory: dict[str, object]) -> None:
    require(inventory.get("schema") == "rebar-cpython-re-p0-completeness-v1"
            and inventory.get("version") == 1,
            "the immutable phase-one correctness inventory was substituted")
    goal = inventory.get("goal")
    require(type(goal) is dict and goal.get("path") == "GOAL.md"
            and goal.get("sha256") == GOAL_SHA256,
            "the immutable goal changed")
    denominator = inventory.get("denominator")
    require(type(denominator) is dict
            and denominator.get("available_frozen_vector_case_executions") == ORIGINAL_CASES
            and denominator.get("frozen_planned_case_execution_denominator") == ORIGINAL_CASES
            and denominator.get("final_required_case_execution_denominator") == ORIGINAL_CASES
            and denominator.get("private_upstream_methods_outside_public_denominator")
            == PRIVATE_WAIVER_COUNT
            and denominator.get("public_original_skip_cases_outside_runnable_denominator") == 1
            and denominator.get("counted_suite_ids") == [row[0] for row in SUITES]
            and denominator.get("not_semantically_deduplicated") is True,
            "the exact original 31,237 / 13 / 13 denominator was changed")
    suites = inventory.get("suites")
    require(type(suites) is list and len(suites) == SUITE_COUNT,
            "an original suite was dropped, duplicated, or renamed")
    require(canonical_digest([item.get("id") for item in suites if type(item) is dict])
            == "0bc6bb35f7584fd41331f180ac7764e3edcee8bd7920a33690099376b1bd1a07",
            "the exact source-ordered suite identity vector changed")
    case_sum = 0
    for item, expected in zip(suites, SUITES, strict=True):
        require(type(item) is dict, "every original frozen suite must be an object")
        name, count, seed, matrix, historical = expected
        source = item.get("source")
        pinned = OWNER_BY_ROLE[name + "_source"]
        baseline = item.get("baseline")
        require(item.get("id") == name and item.get("case_execution_count") == count
                and item.get("published_seed_decimal") == seed
                and item.get("matrix_sha256") == matrix
                and item.get("baseline_records_sha256") == historical
                and type(source) is dict and source.get("path") == pinned[1]
                and source.get("sha256") == pinned[2]
                and type(baseline) is dict and baseline.get("status") == "PASS",
                "an original case, seed, matrix, baseline, or source changed: " + name)
        case_sum += count
    require(case_sum == ORIGINAL_CASES, "original suite totals no longer equal exactly 31,237")
    upstream = inventory.get("original_upstream")
    require(type(upstream) is dict and upstream.get("source_method_count") == 165
            and upstream.get("public_method_count") == 152
            and upstream.get("runnable_public_method_count") == 151
            and upstream.get("private_waiver_count") == PRIVATE_WAIVER_COUNT,
            "the original 165/152/151 public-method accounting changed")
    waiver_rows = upstream.get("private_waivers")
    require(type(waiver_rows) is list and len(waiver_rows) == PRIVATE_WAIVER_COUNT
            and all(type(item) is dict for item in waiver_rows)
            and [item.get("method") for item in waiver_rows] == list(PRIVATE_WAIVERS)
            and canonical_digest(waiver_rows)
            == "ca3f6deb77518c7112790001ab1deb4a74f0282fc1d7326f79a09dc6ca60f61e"
            and canonical_digest([item["method"] for item in waiver_rows])
            == "9f8932d7c832b8c6ecf30f7408ac3228ea46980d4d196e2b0854a372236d79b9",
            "a named upstream private waiver was lost, duplicated, weakened, or added")
    skip = upstream.get("public_debug_skip")
    require(type(skip) is dict and skip.get("method") == "ReTests.test_memory_leaks"
            and skip.get("private_waiver") is False
            and skip.get("counted_as_runnable_case") is False
            and skip.get("reason") == "requires an actual CPython debug build",
            "the real release-debug public skip was converted to a pass or waiver")
    corpus = upstream.get("external_corpus")
    require(type(corpus) is dict and corpus.get("case_count") == 403
            and corpus.get("external_pattern_fixture_count") == 11,
            "the actual 403-case upstream corpus or its 11 fixtures changed")
    obligations = inventory.get("obligations")
    require(type(obligations) is dict, "the complete obligation crosswalk is missing")
    inherited = obligations.get("inherited")
    additional = obligations.get("additional")
    crosswalk = obligations.get("crosswalk")
    require(type(inherited) is list and type(additional) is list
            and type(crosswalk) is list
            and obligations.get("inherited_count") == len(INHERITED_OBLIGATIONS) == 45
            and obligations.get("additional_named_count")
            == len(ADDITIONAL_OBLIGATIONS) == 28
            and obligations.get("crosswalk_count") == len(crosswalk) == 34
            and all(type(item) is dict for item in inherited + additional + crosswalk)
            and [item.get("id") for item in inherited] == list(INHERITED_OBLIGATIONS)
            and [item.get("id") for item in additional] == list(ADDITIONAL_OBLIGATIONS)
            and [item.get("id") for item in crosswalk]
            == ["P0-" + format(index, "02d") for index in range(1, 35)],
            "the exact 45 + 28 obligations or 34 original mappings changed")
    require(canonical_digest(inherited + additional)
            == "599105639814150f3076563f597114db9a2d746ed9ad4ae8554b604dea44b728"
            and canonical_digest([item["id"] for item in inherited + additional])
            == "0eee54994b1d740b2b7660329f5aca2b06ae415ae064f9263fd962daea9eae99"
            and canonical_digest(crosswalk)
            == "349c524e070ad701608aaeed30b14717dd262dbe9956e535a4234a25ba13366f"
            and canonical_digest([item["id"] for item in crosswalk])
            == "0a293c79d4bd541ddad84e8c0745e51b61eec3b8ca1745f9d6f6c90156938551",
            "an obligation mapping was omitted, altered, duplicated, or fabricated")
    allowed = {row[0] for row in SUITES} | {"original_full_v5", "original_full_v6"}
    for row in inherited + additional + crosswalk:
        covered = row.get("covered_by")
        require(type(covered) is list and len(covered) > 0
                and len(covered) == len(set(covered))
                and all(type(name) is str and name in allowed for name in covered),
                "a complete obligation contains an invented or missing case owner")


def validate_correction(inventory: dict[str, object], receipt: dict[str, object],
                        falsification: dict[str, object],
                        producer: dict[str, object], controller: dict[str, object]) -> None:
    public = next(row for row in inventory["suites"] if row["id"] == "public_types_v1")
    require(public["baseline_records_sha256"] == HISTORICAL_PUBLIC_SHA256
            and public["matrix_sha256"] == PUBLIC_MATRIX_SHA256,
            "the immutable falsified historical public-type baseline was rewritten")
    require(receipt.get("schema")
            == "rebar-phase1-owned-public-type-reference-context-v1-durable-publication-receipt"
            and receipt.get("version") == 1
            and receipt.get("label") == "cpython-3-14-6-candidate-context-p0"
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("public_case_count_per_reference") == 6912
            and receipt.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and receipt.get("full_reference_records_sha256") == CORRECTED_PUBLIC_SHA256
            and receipt.get("cache_records_sha256") == CORRECTED_CACHE_SHA256
            and receipt.get("original_case_execution_denominator") == ORIGINAL_CASES
            and receipt.get("actual_distinct_reference_process_ids") == [81, 82]
            and receipt.get("actual_reference_worker_count") == 2
            and receipt.get("actual_started_reference_worker_count") == 2
            and receipt.get("attempted_reference_worker_count") == 2
            and receipt.get("completed_reference_worker_count") == 2
            and receipt.get("validated_reference_worker_count") == 2
            and receipt.get("source_sha256") == OWNER_BY_ROLE["public_context_source"][2]
            and receipt.get("protocol_sha256") == OWNER_BY_ROLE["public_context_protocol"][2]
            and receipt.get("contract_sha256") == OWNER_BY_ROLE["public_context_contract"][2]
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_workers_started") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED",
            "the corrected complete two-worker reference is missing, mixed, or not passing")
    require(falsification.get("schema") == "rebar-public-type-candidate-context-falsification-v1"
            and falsification.get("version") == 1
            and falsification.get("status") == "FALSIFIED"
            and falsification.get("candidate_facing_self_oracle_status") == "FAIL",
            "the 96-case historical context falsification was hidden or weakened")
    original = falsification.get("original_oracle")
    cases = falsification.get("falsifying_cases")
    interpretation = falsification.get("interpretation")
    require(type(original) is dict and type(cases) is dict
            and type(interpretation) is dict
            and original.get("case_execution_denominator") == ORIGINAL_CASES
            and original.get("suite_count") == SUITE_COUNT
            and original.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and original.get("affected_suite") == "public_types_v1"
            and original.get("affected_suite_case_count") == 6912
            and original.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and original.get("original_cases_removed") == 0
            and original.get("additional_private_waivers") == 0
            and original.get("case_denominator_changed") is False
            and cases.get("cohort") == "cache-pattern-type-separation"
            and cases.get("case_count") == 96
            and cases.get("text_subclass_case_count") == 48
            and cases.get("bytes_subclass_case_count") == 48
            and cases.get("case_ids_sha256") == PUBLIC_CACHE_IDS_SHA256
            and cases.get("exact_case_matrix_sha256") == PUBLIC_CACHE_MATRIX_SHA256
            and cases.get("actual_named_context_stdlib_records_sha256")
            == CORRECTED_CACHE_SHA256
            and cases.get("published_script_context_module") == "__main__"
            and cases.get("actual_candidate_facing_module")
            == "tools.independent_public_type_identity_serialization_v1"
            and cases.get("sole_normalized_difference_path")
            == "outcome.value.items[2].module"
            and interpretation.get("historical_rust_records_recomputed_or_deleted") is False
            and interpretation.get("c_pattern_equality_failure_waived") is False,
            "the real 96-case context proof or a real candidate failure was erased")
    require(producer.get("schema") == "rebar-owned-six-family-original-p0-producer-v4-source-freeze",
            "the exact corrected V4 case producer was substituted")
    phase = producer.get("phase_one")
    fixed = producer.get("corrected_candidate_context_public_type_reference")
    historical = producer.get("frozen_public_type_reference")
    require(type(phase) is dict and type(fixed) is dict and type(historical) is dict
            and phase.get("case_execution_denominator") == ORIGINAL_CASES
            and phase.get("suite_count") == SUITE_COUNT
            and phase.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and phase.get("inventory_sha256") == OWNER_BY_ROLE["v1_inventory"][2]
            and fixed.get("reference_status") == "PASS"
            and fixed.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and fixed.get("candidate_facing_reference") is True
            and fixed.get("records_sha256") == CORRECTED_PUBLIC_SHA256
            and fixed.get("historical_reference_records_sha256") == HISTORICAL_PUBLIC_SHA256
            and fixed.get("matrix_sha256") == PUBLIC_MATRIX_SHA256
            and fixed.get("case_count") == 6912
            and fixed.get("reference_pids") == [81, 82]
            and fixed.get("actual_reference_worker_count") == 2
            and fixed.get("attempted_reference_worker_count") == 2
            and fixed.get("completed_reference_worker_count") == 2
            and fixed.get("validated_reference_worker_count") == 2
            and fixed.get("cache_case_count") == 96
            and fixed.get("cache_case_ids_sha256") == PUBLIC_CACHE_IDS_SHA256
            and fixed.get("cache_records_sha256") == CORRECTED_CACHE_SHA256
            and fixed.get("candidate_run_uses_both_complete_reference_vectors") is True
            and fixed.get("candidate_run_starts_reference_processes") is False
            and fixed.get("c_pattern_equality_failure_waived") is False
            and historical.get("records_sha256") == HISTORICAL_PUBLIC_SHA256
            and historical.get("candidate_facing_reference") is False
            and historical.get("historical_script_context_only") is True,
            "the actual V4 producer mixed corrected and falsified reference contexts")
    corrected_owners = fixed.get("owners")
    require(type(corrected_owners) is dict, "the corrected producer source owners were omitted")
    for key, role in (("source", "public_context_source"),
                      ("protocol", "public_context_protocol"),
                      ("contract", "public_context_contract"),
                      ("receipt", "public_reference_receipt"),
                      ("falsification", "public_falsification")):
        owner = corrected_owners.get(key)
        frozen = OWNER_BY_ROLE[role]
        require(type(owner) is dict and owner.get("relative") == frozen[1]
                and owner.get("sha256") == frozen[2]
                and owner.get("size_bytes") == frozen[3],
                "a real corrected V4 public-context owner changed: " + key)
    require(controller.get("schema") == "rebar-frozen-python-re-p0-candidate-protocol-v10"
            and controller.get("version") == 10
            and controller.get("case_execution_denominator") == ORIGINAL_CASES
            and controller.get("suite_count") == SUITE_COUNT
            and controller.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT,
            "the independently frozen V10 case controller was substituted")
    controlled = controller.get("corrected_candidate_context_reference")
    require(type(controlled) is dict
            and controlled.get("actual_independent_reference_pids") == [81, 82]
            and controlled.get("records_sha256") == CORRECTED_PUBLIC_SHA256
            and controlled.get("historical_script_context_records_sha256")
            == HISTORICAL_PUBLIC_SHA256
            and controlled.get("cache_cohort_records_sha256") == CORRECTED_CACHE_SHA256
            and controlled.get("cache_cohort_case_count") == 96
            and controlled.get("cache_cohort_case_ids_sha256") == PUBLIC_CACHE_IDS_SHA256
            and controlled.get("c_pattern_equality_failure_waived") is False,
            "the actual V10 controller no longer uses the corrected named context")
    actual_suites = controller.get("original_suites")
    require(type(actual_suites) is list and len(actual_suites) == SUITE_COUNT,
            "the V10 controller lost an original worker category")
    for actual, expected in zip(actual_suites, SUITES, strict=True):
        name, count, seed, matrix, historical_sha = expected
        pinned = OWNER_BY_ROLE[name + "_source"]
        desired = CORRECTED_PUBLIC_SHA256 if name == "public_types_v1" else historical_sha
        require(type(actual) is dict and actual.get("id") == name
                and actual.get("case_execution_count") == count
                and actual.get("published_seed_decimal") == seed
                and actual.get("matrix_sha256") == matrix
                and actual.get("reference_records_sha256") == desired
                and actual.get("source_relative") == pinned[1]
                and actual.get("source_sha256") == pinned[2],
                "the V10 candidate-facing complete original vector changed: " + name)


def validate_fuzz(manifest: dict[str, object], seeds: dict[str, object],
                  historical: dict[str, object], parent: dict[str, object],
                  parent_seeds: dict[str, object], parent_historical: dict[str, object],
                  stream: dict[str, object], parent_stream: dict[str, object]) -> None:
    require(manifest.get("schema") == "rebar-correctness-v2"
            and manifest.get("cases") == FUZZ_CASES
            and manifest.get("expected_sha256") == FUZZ_SHA256
            and manifest.get("parent_expected_sha256")
            == OWNER_BY_ROLE["fuzz_v1_expected"][2]
            and manifest.get("suite_sha256") == OWNER_BY_ROLE["fuzz_v2_suite"][2]
            and manifest.get("runner_sha256") == OWNER_BY_ROLE["fuzz_v2_runner"][2]
            and manifest.get("goal_sha256") == GOAL_SHA256
            and manifest.get("implementation") == "CPython"
            and manifest.get("python") == "3.14.6"
            and manifest.get("unicode") == "16.0.0"
            and manifest.get("locale") == "C"
            and manifest.get("obligations") == 45
            and manifest.get("mapped_obligations") == 45
            and manifest.get("seeds") == SEEDS and seeds == SEEDS,
            "the independently frozen 8,244-case predecessor corpus or exact seeds changed")
    kinds = manifest.get("kinds")
    require(type(kinds) is dict and kinds == FUZZ_KINDS
            and sum(kinds.values()) == FUZZ_CASES,
            "the complete supplemental differential/property/fuzz case kinds changed")
    require(manifest.get("private_waivers")
            == ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"],
            "the historically recorded abstract fuzz metadata was silently rewritten")
    require(stream.get("path") == OWNER_BY_ROLE["fuzz_v2_expected"][1]
            and stream.get("sha256") == FUZZ_SHA256
            and stream.get("bytes") == FUZZ_BYTES
            and stream.get("line_count") == FUZZ_CASES
            and stream.get("record_case_id_count") == FUZZ_CASES
            and stream.get("record_first_case_id") == "api.exports"
            and stream.get("record_last_case_id") == "v2.deep.bytes.2047"
            and stream.get("record_kind_counts") == FUZZ_KINDS
            and stream.get("record_mapped_obligation_ids")
            == list(INHERITED_OBLIGATIONS)
            and stream.get("maximum_record_bytes") == 83_667
            and stream.get("per_record_limit_bytes") == MAX_RECORD_BYTES
            and "raw" not in stream,
            "the entire 8,244-case plaintext corpus was not incrementally authenticated")
    require(historical == {
        "cases": FUZZ_CASES, "expected_sha256": FUZZ_SHA256,
        "failed": 0, "failures": [], "mapped_obligations": 45,
        "module": "re", "obligations": 45, "passed": FUZZ_CASES,
        "schema": "rebar-correctness-result-v2",
    }, "the historical single-context fuzz result was changed or invented")
    require(not any(key in historical for key in (
        "reference_process_count", "reference_worker_count",
        "actual_distinct_reference_process_ids", "actual_reference_process_ids",
        "reference_pids", "reference_status", "candidate_results",
    )), "worker provenance was fabricated for the historical supplemental result")
    require(parent.get("schema") == "rebar-correctness-v1.1"
            and parent.get("cases") == 2048
            and parent.get("expected_sha256") == OWNER_BY_ROLE["fuzz_v1_expected"][2]
            and parent.get("suite_sha256") == OWNER_BY_ROLE["fuzz_v1_suite"][2]
            and parent.get("runner_sha256") == OWNER_BY_ROLE["fuzz_v1_runner"][2]
            and parent.get("goal_sha256") == GOAL_SHA256
            and parent.get("private_waivers")
            == ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"]
            and parent.get("seeds") == parent_seeds
            and all(SEEDS.get(key) == value for key, value in parent_seeds.items())
            and parent_stream.get("line_count") == 2048
            and parent_stream.get("sha256") == OWNER_BY_ROLE["fuzz_v1_expected"][2]
            and "raw" not in parent_stream,
            "the complete transitive v1 fuzz-parent source closure changed")
    require(parent_historical == {
        "cases": 2048,
        "expected_sha256": OWNER_BY_ROLE["fuzz_v1_expected"][2],
        "failed": 0, "failures": [], "mapped_obligations": 38,
        "module": "re", "obligations": 38, "passed": 2048,
        "schema": "rebar-correctness-result-v1",
    }, "the historical single-context v1 fuzz result was changed or invented")


def validate_supplements(signature: dict[str, object], receipt: dict[str, object],
                         entrypoint: dict[str, object], large: dict[str, object]) -> None:
    require(signature.get("schema") == "rebar-python-re-callable-introspection-v1-source-freeze",
            "the separately frozen callable-introspection matrix was substituted")
    addition = signature.get("additional_obligation")
    require(type(addition) is dict and addition.get("case_count") == 50
            and addition.get("matrix_sha256") == SIGNATURE_MATRIX_SHA256
            and addition.get("included_in_original_31237_denominator") is False
            and type(addition.get("case_matrix")) is list
            and len(addition["case_matrix"]) == 50,
            "the 50 public signatures were removed or silently counted in 31,237")
    require(receipt.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt"
            and receipt.get("version") == 2
            and receipt.get("status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means") == "EVIDENCE PUBLICATION ONLY"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("reference_failure_count") == 0
            and receipt.get("additional_case_count") == 50
            and receipt.get("additional_cases_included_in_original_denominator") is False
            and receipt.get("actual_distinct_process_ids") == [81, 82]
            and receipt.get("actual_reference_processes_started") == 2
            and receipt.get("matrix_sha256") == SIGNATURE_MATRIX_SHA256
            and receipt.get("original_case_denominator") == ORIGINAL_CASES
            and receipt.get("original_suite_count") == SUITE_COUNT
            and receipt.get("original_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and receipt.get("candidate_introspection") == "NOT MEASURED"
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_qualified") is False,
            "the genuine separate signature reference or unrun candidate was misreported")
    require(entrypoint.get("schema") == "rebar-python-re-public-entrypoint-import-v1-source-freeze"
            and entrypoint.get("version") == 1
            and entrypoint.get("case_matrix_sha256") == IMPORT_MATRIX_SHA256
            and type(entrypoint.get("case_matrix")) is list
            and len(entrypoint["case_matrix"]) == 32,
            "the 32-observation actual public-import freeze was substituted")
    import_original = entrypoint.get("original_correctness")
    observed = entrypoint.get("boundaries")
    require(type(import_original) is dict and type(observed) is dict
            and import_original.get("case_count") == ORIGINAL_CASES
            and import_original.get("suite_count") == SUITE_COUNT
            and import_original.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and import_original.get("additional_signature_case_count") == 50
            and import_original.get("additional_signature_cases_in_original_denominator")
            is False
            and observed.get("source_freeze_status") == "PASS"
            and observed.get("observed_public_entrypoint_status") == "FAIL"
            and observed.get("observed_public_entrypoint_classification")
            == "UNQUALIFIED_ZIG_PROTOTYPE"
            and observed.get("public_entrypoint_qualified") is False
            and observed.get("qualified_candidate_count") == 0
            and observed.get("runtime_no_delegation") == "NOT ESTABLISHED"
            and observed.get("actual_candidate_imports") == 0
            and observed.get("actual_public_entrypoint_imports") == 0,
            "the genuine failed public import was misrepresented as a winner")
    require(large.get("schema") == "rebar-python-re-large-input-indexing-v1-source-freeze"
            and large.get("case_matrix_sha256") == LARGE_MATRIX_SHA256
            and type(large.get("case_matrix")) is list
            and len(large["case_matrix"]) == 32,
            "the independent 32-observation large-input source matrix changed")
    large_original = large.get("original_correctness")
    original = large.get("upstream_large_input")
    reference = large.get("historical_full_resource_reference")
    candidate = large.get("actual_candidate_large_input")
    require(type(large_original) is dict and type(original) is dict
            and type(reference) is dict and type(candidate) is dict
            and large_original.get("case_execution_denominator") == ORIGINAL_CASES
            and large_original.get("suite_count") == SUITE_COUNT
            and large_original.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and large_original.get("large_input_source_cases_in_original_denominator") is False
            and original.get("case_count") == 2
            and original.get("subject_size") == 2_147_483_648
            and reference.get("status") == "PASS; HISTORICAL PINNED MANIFEST EVIDENCE"
            and reference.get("reference_process_count") == 2
            and reference.get("real_max_memory_bytes") == 42_949_672_960
            and candidate.get("original_controller_bigmem_dry_run") is True
            and candidate.get("original_controller_maximum_subject_size") == 5147
            and candidate.get("full_resource_large_search") == "NOT RUN"
            and candidate.get("full_resource_large_subn") == "NOT RUN"
            and candidate.get("full_resource_candidate_qualification") == "NOT ESTABLISHED"
            and candidate.get("large_candidate_workers_started_by_this_source_oracle") == 0
            and candidate.get("candidate_qualified") is False,
            "a genuine 2 GiB candidate run was fabricated or its 5,147 cap was hidden")


def collect_context(source_hash: str, protocol_hash: str,
                    contract_hash: str | None, *, read_contract: bool) -> dict[str, object]:
    require(sys.implementation.name == "cpython"
            and sys.version_info[:3] == (3, 14, 6)
            and sys.executable == PYTHON,
            "run only the exact pinned CPython 3.14.6 source-only interpreter")
    require(os.path.abspath(__file__) == ROOT + "/" + SOURCE
            and os.path.realpath(__file__) == ROOT + "/" + SOURCE,
            "the owned Phase-1 verifier source path was substituted")
    install_wall()
    own_source = exact_reader(SOURCE, source_hash,
                              source_size(), capture=False)
    own_protocol = exact_reader(PROTOCOL, protocol_hash,
                                protocol_size(), capture=False)
    capture_roles = {
        "v1_inventory", "upstream_manifest", "public_falsification",
        "public_reference_receipt", "signature_contract", "signature_reference_receipt",
        "import_contract", "large_contract", "producer_v4_contract",
        "candidate_v10_contract", "fuzz_v1_manifest", "fuzz_v1_seeds",
        "fuzz_v1_self", "fuzz_v2_manifest", "fuzz_v2_seeds", "fuzz_v2_self",
    }
    evidence: dict[str, dict[str, object]] = {}
    for role, _path, _sha, _size, _device, _inode in OWNERS:
        lines = FUZZ_CASES if role == "fuzz_v2_expected" else (
            2048 if role == "fuzz_v1_expected" else None
        )
        evidence[role] = read_pinned(
            role, capture=role in capture_roles, expected_lines=lines,
            validate_records=role == "fuzz_v2_expected",
        )
    records = {role: decoded(evidence[role], role) for role in capture_roles}
    validate_original(records["v1_inventory"])
    validate_correction(records["v1_inventory"], records["public_reference_receipt"],
                        records["public_falsification"], records["producer_v4_contract"],
                        records["candidate_v10_contract"])
    validate_fuzz(records["fuzz_v2_manifest"], records["fuzz_v2_seeds"],
                  records["fuzz_v2_self"], records["fuzz_v1_manifest"],
                  records["fuzz_v1_seeds"], records["fuzz_v1_self"],
                  evidence["fuzz_v2_expected"], evidence["fuzz_v1_expected"])
    validate_supplements(records["signature_contract"],
                         records["signature_reference_receipt"],
                         records["import_contract"], records["large_contract"])
    result: dict[str, object] = {
        "source": own_source, "protocol": own_protocol,
        "owners": evidence, "records": records,
    }
    if read_contract:
        require(contract_hash is not None, "an independently caller-pinned contract is mandatory")
        own_contract = exact_reader(CONTRACT, contract_hash,
                                    contract_size(), capture=True)
        result["contract"] = own_contract
        result["document"] = decoded(own_contract, "phase1_v2_contract")
    no_forbidden_modules()
    return result


def source_size() -> int:
    # Reading metadata is avoided: the already running immutable source reveals
    # its complete bytes only through its physically guarded descriptor.
    descriptor = os.open(ROOT + "/" + SOURCE,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        result = os.fstat(descriptor)
        require(stat.S_ISREG(result.st_mode) and stat.S_IMODE(result.st_mode) == 0o600
                and result.st_nlink == 1 and 0 < result.st_size <= MAX_OWNER_BYTES,
                "the owned verifier is not a private immutable source")
        return result.st_size
    finally:
        os.close(descriptor)


def protocol_size() -> int:
    descriptor = os.open(ROOT + "/" + PROTOCOL,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        result = os.fstat(descriptor)
        require(stat.S_ISREG(result.st_mode) and stat.S_IMODE(result.st_mode) == 0o600
                and result.st_nlink == 1 and 0 < result.st_size <= MAX_OWNER_BYTES,
                "the owned explanation is not a private immutable source")
        return result.st_size
    finally:
        os.close(descriptor)


def contract_size() -> int:
    descriptor = os.open(ROOT + "/" + CONTRACT,
                         os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    try:
        result = os.fstat(descriptor)
        require(stat.S_ISREG(result.st_mode) and stat.S_IMODE(result.st_mode) == 0o600
                and result.st_nlink == 1 and 0 < result.st_size <= MAX_JSON_BYTES,
                "the owned contract is not a private immutable JSON document")
        return result.st_size
    finally:
        os.close(descriptor)


def own_document(result: dict[str, object]) -> dict[str, object]:
    return {"path": result["path"], "sha256": result["sha256"],
            "bytes": result["bytes"], "device": result["device"],
            "inode": result["inode"], "mode": result["mode"]}


def expected_contract(context: dict[str, object]) -> dict[str, object]:
    evidence = context["owners"]
    require(type(evidence) is dict, "the complete source owner closure is missing")
    fuzz = evidence["fuzz_v2_expected"]
    parent = evidence["fuzz_v1_expected"]
    require(type(fuzz) is dict and type(parent) is dict,
            "the incrementally streamed parent and expanded fuzz corpus are missing")
    return {
        "schema": SCHEMA,
        "version": 2,
        "phase": "CORRECTNESS ORACLE",
        "status": "BLOCKED",
        "source_crosswalk_status": "PASS",
        "phase1_canonical_candidate_context_crosswalk": "PASS",
        "goal": owner_document("goal"),
        "source": own_document(context["source"]),
        "protocol": own_document(context["protocol"]),
        "original_oracle": {
            "status": "CORRECTED ORIGINAL CROSSWALK PASS; UNIVERSAL GATE BLOCKED",
            "historical_inventory": owner_document("v1_inventory"),
            "historical_protocol": owner_document("v1_protocol"),
            "historical_verifier": owner_document("v1_verifier"),
            "case_execution_denominator": ORIGINAL_CASES,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_method_count": 165,
            "public_method_count": 152,
            "runnable_public_method_count": 151,
            "public_release_debug_skip": "ReTests.test_memory_leaks",
            "public_release_debug_skip_is_private_waiver": False,
            "upstream_corpus_case_count": 403,
            "upstream_external_fixture_count": 11,
            "inherited_obligation_count": 45,
            "additional_named_obligation_count": 28,
            "total_named_obligation_count": 73,
            "crosswalk_count": 34,
            "all_73_obligation_objects_sha256": "599105639814150f3076563f597114db9a2d746ed9ad4ae8554b604dea44b728",
            "all_73_obligation_ids_sha256": "0eee54994b1d740b2b7660329f5aca2b06ae415ae064f9263fd962daea9eae99",
            "all_34_crosswalk_objects_sha256": "349c524e070ad701608aaeed30b14717dd262dbe9956e535a4234a25ba13366f",
            "all_34_crosswalk_ids_sha256": "0a293c79d4bd541ddad84e8c0745e51b61eec3b8ca1745f9d6f6c90156938551",
            "all_13_named_waiver_objects_sha256": "ca3f6deb77518c7112790001ab1deb4a74f0282fc1d7326f79a09dc6ca60f61e",
            "all_13_named_waiver_ids_sha256": "9f8932d7c832b8c6ecf30f7408ac3228ea46980d4d196e2b0854a372236d79b9",
            "source_ordered_suite_ids_sha256": "0bc6bb35f7584fd41331f180ac7764e3edcee8bd7920a33690099376b1bd1a07",
            "named_private_waivers": list(PRIVATE_WAIVERS),
            "inherited_obligation_ids": list(INHERITED_OBLIGATIONS),
            "additional_obligation_ids": list(ADDITIONAL_OBLIGATIONS),
            "suites": [
                {"id": name, "case_execution_count": count,
                 "published_seed_decimal": seed, "matrix_sha256": matrix,
                 "historical_reference_records_sha256": historical,
                 "candidate_context_reference_records_sha256": (
                     CORRECTED_PUBLIC_SHA256 if name == "public_types_v1" else historical
                 ),
                 "source": owner_document(name + "_source")}
                for name, count, seed, matrix, historical in SUITES
            ],
            "full_resource_reference_history_double_counted": False,
            "supplemental_cases_silently_added": False,
            "legacy_abstract_fuzz_waivers_inherited": 0,
        },
        "historical_public_type_reference": {
            "candidate_context_status": "FALSIFIED",
            "records_sha256": HISTORICAL_PUBLIC_SHA256,
            "matrix_sha256": PUBLIC_MATRIX_SHA256,
            "case_count": 6912,
            "candidate_facing_reference": False,
            "historical_report_deleted_or_rewritten": False,
            "falsification": owner_document("public_falsification"),
            "falsifying_cohort": "cache-pattern-type-separation",
            "falsifying_case_count": 96,
            "text_subclass_case_count": 48,
            "bytes_subclass_case_count": 48,
            "cache_case_ids_sha256": PUBLIC_CACHE_IDS_SHA256,
            "cache_matrix_sha256": PUBLIC_CACHE_MATRIX_SHA256,
            "script_context_module": "__main__",
            "actual_candidate_context_module":
                "tools.independent_public_type_identity_serialization_v1",
            "sole_normalized_difference_path": "outcome.value.items[2].module",
            "real_c_pattern_equality_failure_waived": False,
        },
        "corrected_candidate_context_public_type_reference": {
            "status": "PASS",
            "reference_status": "PASS",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "candidate_facing_reference": True,
            "reference_pids": [81, 82],
            "actual_reference_worker_count": 2,
            "attempted_reference_worker_count": 2,
            "completed_reference_worker_count": 2,
            "validated_reference_worker_count": 2,
            "case_count": 6912,
            "matrix_sha256": PUBLIC_MATRIX_SHA256,
            "records_sha256": CORRECTED_PUBLIC_SHA256,
            "cache_records_sha256": CORRECTED_CACHE_SHA256,
            "cache_case_count": 96,
            "cache_case_ids_sha256": PUBLIC_CACHE_IDS_SHA256,
            "historical_reference_records_sha256": HISTORICAL_PUBLIC_SHA256,
            "source": owner_document("public_context_source"),
            "protocol": owner_document("public_context_protocol"),
            "contract": owner_document("public_context_contract"),
            "actual_reference_receipt": owner_document("public_reference_receipt"),
            "falsification": owner_document("public_falsification"),
            "producer_v4_source": owner_document("producer_v4_source"),
            "producer_v4_protocol": owner_document("producer_v4_protocol"),
            "producer_v4_contract": owner_document("producer_v4_contract"),
            "controller_v10_source": owner_document("candidate_v10_source"),
            "controller_v10_protocol": owner_document("candidate_v10_protocol"),
            "controller_v10_contract": owner_document("candidate_v10_contract"),
            "new_reference_workers_started_by_v2": 0,
            "new_candidate_workers_started_by_v2": 0,
            "matching_archive_opened_by_v2": False,
        },
        "supplemental_differential_property_fuzz": {
            "status": "BLOCKED",
            "case_count": FUZZ_CASES,
            "case_denominator_included_in_original_31237": False,
            "combined_separately_counted_case_count": ORIGINAL_CASES + FUZZ_CASES,
            "combined_count_is_new_original_denominator": False,
            "expected_records": owner_document("fuzz_v2_expected"),
            "expected_records_bytes": FUZZ_BYTES,
            "expected_records_sha256": FUZZ_SHA256,
            "complete_streamed_newline_count": fuzz["line_count"],
            "unique_record_case_count": fuzz["record_case_id_count"],
            "first_case_id": fuzz["record_first_case_id"],
            "last_case_id": fuzz["record_last_case_id"],
            "maximum_observed_record_bytes": fuzz["maximum_record_bytes"] + 1,
            "maximum_observed_record_payload_bytes": fuzz["maximum_record_bytes"],
            "per_record_limit_bytes": fuzz["per_record_limit_bytes"],
            "record_kind_counts": dict(FUZZ_KINDS),
            "record_mapped_obligation_ids": list(INHERITED_OBLIGATIONS),
            "plaintext_corpus_loaded_whole": False,
            "source": owner_document("fuzz_v2_suite"),
            "runner": owner_document("fuzz_v2_runner"),
            "protocol": owner_document("fuzz_v2_protocol"),
            "manifest": owner_document("fuzz_v2_manifest"),
            "seeds": owner_document("fuzz_v2_seeds"),
            "frozen_seed_values": dict(SEEDS),
            "historical_single_context_stdlib_evidence":
                owner_document("fuzz_v2_self"),
            "historical_single_context_stdlib_status": "PASS",
            "historical_single_context_stdlib_passing_case_count": FUZZ_CASES,
            "historical_independent_reference_process_ids": "NOT CAPTURED",
            "two_independent_reference_process_status": "NOT RUN",
            "independently_referenced_case_count": 0,
            "candidate_status": "NOT RUN",
            "candidate_case_count": 0,
            "candidate_qualified": False,
            "historical_abstract_private_waivers":
                ["PRIVATE-CACHE-LAYOUT", "PRIVATE-DEBUG-TEXT"],
            "historical_abstract_waivers_inherited_into_original": 0,
            "transitive_v1_parent": {
                "source": owner_document("fuzz_v1_suite"),
                "runner": owner_document("fuzz_v1_runner"),
                "protocol": owner_document("fuzz_v1_protocol"),
                "manifest": owner_document("fuzz_v1_manifest"),
                "seeds": owner_document("fuzz_v1_seeds"),
                "expected_records": owner_document("fuzz_v1_expected"),
                "complete_streamed_newline_count": parent["line_count"],
                "historical_single_context_stdlib_evidence":
                    owner_document("fuzz_v1_self"),
                "historical_single_context_stdlib_status": "PASS",
                "historical_reference_worker_provenance": "NOT ESTABLISHED",
                "historical_abstract_waivers_inherited_into_original": 0,
            },
        },
        "supplemental_public_contracts": {
            "all_supplemental_case_denominators_separate": True,
            "callable_introspection": {
                "case_count": 50,
                "matrix_sha256": SIGNATURE_MATRIX_SHA256,
                "included_in_original_case_denominator": False,
                "two_reference_status": "PASS",
                "actual_reference_process_ids": [81, 82],
                "candidate_status": "NOT RUN",
                "candidate_qualified": False,
                "contract": owner_document("signature_contract"),
                "protocol": owner_document("signature_protocol"),
                "worker": owner_document("signature_worker"),
                "reference_contract": owner_document("signature_reference_contract"),
                "reference_protocol": owner_document("signature_reference_protocol"),
                "reference_source": owner_document("signature_reference_source"),
                "actual_reference_receipt":
                    owner_document("signature_reference_receipt"),
            },
            "public_import": {
                "source_observation_count": 32,
                "matrix_sha256": IMPORT_MATRIX_SHA256,
                "included_in_original_case_denominator": False,
                "source_observation_status": "PASS",
                "actual_public_entrypoint_status": "FAIL",
                "classification": "UNQUALIFIED_ZIG_PROTOTYPE",
                "installed_public_artifact": "NOT MEASURED",
                "candidate_qualified": False,
                "protocol": owner_document("import_protocol"),
                "contract": owner_document("import_contract"),
                "source": owner_document("import_source"),
            },
            "genuine_large_input": {
                "source_observation_count": 32,
                "matrix_sha256": LARGE_MATRIX_SHA256,
                "included_in_original_case_denominator": False,
                "original_large_method_count": 2,
                "exact_subject_size": 2_147_483_648,
                "historical_two_reference_status": "PASS",
                "historical_reference_memory_allowance_bytes": 42_949_672_960,
                "actual_candidate_dry_run_maximum": 5147,
                "full_size_candidate_search": "NOT RUN",
                "full_size_candidate_substitution": "NOT RUN",
                "candidate_qualified": False,
                "protocol": owner_document("large_protocol"),
                "contract": owner_document("large_contract"),
                "source": owner_document("large_source"),
            },
            "module_version_observations_already_in_thread_suite": 32,
            "module_version_observations_counted_again": False,
        },
        "current_published_overview": {
            "version": 60,
            "renderer": owner_document("overview_v60_renderer"),
            "inputs": owner_document("overview_v60_inputs"),
            "summary": owner_document("overview_v60_summary"),
            "chart": owner_document("overview_v60_svg"),
            "matching_archives_opened": 0,
            "graphs_written": 0,
            "candidate_execution": "NOT RUN BY THIS SOURCE VERIFIER",
        },
        "phase_gate": {
            "status": "BLOCKED",
            "source_crosswalk_status": "PASS",
            "candidate_evaluation_authorized": False,
            "native_build_authorized": False,
            "performance_oracle_authorized": False,
            "final_holdout_authorized": False,
            "qualified_candidate_count": 0,
            "blockers": list(BLOCKERS),
        },
        "source_only_boundaries": {
            "physical_audit_wall_required": True,
            "exact_private_nofollow_owners_required": True,
            "duplicate_json_keys_rejected": True,
            "full_fuzz_corpus_incrementally_streamed": True,
            "archive_files_opened": 0,
            "holdout_files_opened": 0,
            "temporary_files_opened": 0,
            "source_files_written": 0,
            "candidate_imports": 0,
            "native_libraries_loaded": 0,
            "reference_processes_started": 0,
            "candidate_processes_started": 0,
            "compiler_processes_started": 0,
            "threads_started": 0,
            "network_requests": 0,
            "clock_samples": 0,
            "timing_trials_run": 0,
            "runtime_no_delegation": "NOT ESTABLISHED",
            "performance": "NOT MEASURED",
            "memory": "NOT MEASURED",
            "undefined_behavior": "NOT MEASURED",
            "holdout": "NOT OPENED",
            "winner_selected": False,
        },
    }


def validate_contract(document: dict[str, object], context: dict[str, object]) -> None:
    require(type(document) is dict and document == expected_contract(context),
            "the exact blocked, additive correctness contract differs from real frozen evidence")
    gate = document.get("phase_gate")
    fuzz = document.get("supplemental_differential_property_fuzz")
    corrected = document.get("corrected_candidate_context_public_type_reference")
    require(type(gate) is dict and type(fuzz) is dict and type(corrected) is dict
            and document.get("status") == "BLOCKED"
            and document.get("phase1_canonical_candidate_context_crosswalk") == "PASS"
            and gate.get("status") == "BLOCKED"
            and gate.get("candidate_evaluation_authorized") is False
            and gate.get("native_build_authorized") is False
            and gate.get("blockers") == list(BLOCKERS)
            and fuzz.get("two_independent_reference_process_status") == "NOT RUN"
            and fuzz.get("candidate_status") == "NOT RUN"
            and fuzz.get("candidate_qualified") is False
            and corrected.get("reference_pids") == [81, 82]
            and corrected.get("candidate_facing_reference") is True,
            "a source crosswalk PASS was misrepresented as complete universal qualification")


def rejected(name: str, action: object, controls: list[str]) -> None:
    require(callable(action), "a hostile control must be executable: " + name)
    try:
        action()
    except (FreezeError, OSError, ValueError, UnicodeError, RecursionError):
        controls.append(name)
        return
    raise FreezeError("a hostile or falsified control unexpectedly succeeded: " + name)


def hostile_controls(context: dict[str, object]) -> list[str]:
    controls: list[str] = []
    records = context["records"]
    document = context["document"]
    require(type(records) is dict and type(document) is dict,
            "hostile self-tests require the real authenticated frozen contract")

    def broken_original(change: object) -> None:
        candidate = clone(records["v1_inventory"])
        require(type(candidate) is dict and callable(change), "prepare the frozen original mutation")
        change(candidate)
        validate_original(candidate)

    def broken_contract(change: object) -> None:
        candidate = clone(document)
        require(type(candidate) is dict and callable(change), "prepare the frozen contract mutation")
        change(candidate)
        validate_contract(candidate, context)

    def broken_receipt(change: object) -> None:
        candidate = clone(records["public_reference_receipt"])
        require(type(candidate) is dict and callable(change), "prepare the public-reference mutation")
        change(candidate)
        validate_correction(records["v1_inventory"], candidate,
                            records["public_falsification"],
                            records["producer_v4_contract"],
                            records["candidate_v10_contract"])

    def broken_fuzz(change: object) -> None:
        candidate = clone(records["fuzz_v2_manifest"])
        require(type(candidate) is dict and callable(change), "prepare the supplemental fuzz mutation")
        change(candidate)
        owners = context["owners"]
        require(type(owners) is dict, "the real streamed corpus owners disappeared")
        validate_fuzz(candidate, records["fuzz_v2_seeds"], records["fuzz_v2_self"],
                      records["fuzz_v1_manifest"], records["fuzz_v1_seeds"],
                      records["fuzz_v1_self"], owners["fuzz_v2_expected"],
                      owners["fuzz_v1_expected"])

    rejected("reject-duplicate-json-keys",
             lambda: StrictJSON(b'{"status":"BLOCKED","status":"PASS"}').decode(), controls)
    rejected("reject-trailing-json-document",
             lambda: StrictJSON(b'{"status":"BLOCKED"} {"status":"PASS"}').decode(), controls)
    rejected("reject-unpaired-json-surrogate",
             lambda: StrictJSON(b'"\\ud800"').decode(), controls)
    rejected("reject-leading-zero-json-integer",
             lambda: StrictJSON(b'01').decode(), controls)
    rejected("reject-shortened-original-denominator",
             lambda: broken_original(lambda item: item["denominator"].__setitem__(
                 "final_required_case_execution_denominator", 31_236)), controls)
    rejected("reject-inflated-original-denominator",
             lambda: broken_original(lambda item: item["denominator"].__setitem__(
                 "final_required_case_execution_denominator", 39_481)), controls)
    rejected("reject-missing-original-suite",
             lambda: broken_original(lambda item: item["suites"].pop()), controls)
    rejected("reject-duplicated-original-suite",
             lambda: broken_original(lambda item: item["suites"].append(
                 clone(item["suites"][0]))), controls)
    rejected("reject-reordered-original-suite",
             lambda: broken_original(lambda item: item["suites"].reverse()), controls)
    rejected("reject-renamed-original-suite",
             lambda: broken_original(lambda item: item["suites"][0].__setitem__(
                 "id", "renamed-original")), controls)
    rejected("reject-suppressed-historical-public-reference",
             lambda: broken_original(lambda item: next(
                 row for row in item["suites"] if row["id"] == "public_types_v1"
             ).__setitem__("baseline_records_sha256", CORRECTED_PUBLIC_SHA256)), controls)
    rejected("reject-missing-named-private-waiver",
             lambda: broken_original(lambda item: item["original_upstream"]["private_waivers"].pop()),
             controls)
    rejected("reject-duplicated-named-private-waiver",
             lambda: broken_original(lambda item: item["original_upstream"]["private_waivers"].append(
                 clone(item["original_upstream"]["private_waivers"][0]))), controls)
    rejected("reject-historical-abstract-private-waiver",
             lambda: broken_original(lambda item: item["original_upstream"]["private_waivers"][0].__setitem__(
                 "method", "PRIVATE-CACHE-LAYOUT")), controls)
    rejected("reject-public-debug-skip-as-private-waiver",
             lambda: broken_original(lambda item: item["original_upstream"]["public_debug_skip"].__setitem__(
                 "private_waiver", True)), controls)
    rejected("reject-missing-inherited-obligation",
             lambda: broken_original(lambda item: item["obligations"]["inherited"].pop()), controls)
    rejected("reject-missing-additional-obligation",
             lambda: broken_original(lambda item: item["obligations"]["additional"].pop()), controls)
    rejected("reject-missing-crosswalk-mapping",
             lambda: broken_original(lambda item: item["obligations"]["crosswalk"].pop()), controls)
    rejected("reject-invented-crosswalk-owner",
             lambda: broken_original(lambda item: item["obligations"]["crosswalk"][0]["covered_by"].append(
                 "invented_candidate")), controls)
    rejected("reject-publication-pass-without-reference-pass",
             lambda: broken_receipt(lambda item: item.__setitem__("reference_status", "NOT RUN")),
             controls)
    rejected("reject-one-corrected-reference-worker",
             lambda: broken_receipt(lambda item: item.__setitem__("actual_reference_worker_count", 1)),
             controls)
    rejected("reject-duplicate-corrected-reference-pids",
             lambda: broken_receipt(lambda item: item.__setitem__(
                 "actual_distinct_reference_process_ids", [81, 81])), controls)
    rejected("reject-inferred-corrected-reference-pid",
             lambda: broken_receipt(lambda item: item.__setitem__(
                 "actual_distinct_reference_process_ids", [81, 83])), controls)
    rejected("reject-falsified-public-vector-as-corrected",
             lambda: broken_receipt(lambda item: item.__setitem__(
                 "full_reference_records_sha256", HISTORICAL_PUBLIC_SHA256)), controls)
    rejected("reject-mixed-public-cache-vector",
             lambda: broken_receipt(lambda item: item.__setitem__(
                 "cache_records_sha256", HISTORICAL_PUBLIC_SHA256)), controls)
    rejected("reject-fabricated-fuzz-case-count",
             lambda: broken_fuzz(lambda item: item.__setitem__("cases", 8243)), controls)
    rejected("reject-fabricated-fuzz-seed",
             lambda: broken_fuzz(lambda item: item["seeds"].__setitem__("deep_str", 1979121300)),
             controls)
    rejected("reject-wrong-transitive-fuzz-parent",
             lambda: broken_fuzz(lambda item: item.__setitem__(
                 "parent_expected_sha256", FUZZ_SHA256)), controls)
    rejected("reject-oversized-supplemental-corpus-record",
             lambda: consume_fuzz_record(b" " * (MAX_RECORD_BYTES + 1), {
                 "tail": bytearray(), "case_ids": set(), "mapped_ids": set(),
                 "kind_counts": {}, "first_case_id": None, "last_case_id": None,
                 "maximum_record_bytes": 0,
             }), controls)
    rejected("reject-partial-non-newline-supplemental-record",
             lambda: finish_fuzz_records({
                 "tail": bytearray(b"partial"), "case_ids": set(),
                 "mapped_ids": set(), "kind_counts": {},
                 "first_case_id": None, "last_case_id": None,
                 "maximum_record_bytes": 0,
             }), controls)

    def duplicate_fuzz_identity() -> None:
        state: dict[str, object] = {
            "tail": bytearray(), "case_ids": set(), "mapped_ids": set(),
            "kind_counts": {}, "first_case_id": None, "last_case_id": None,
            "maximum_record_bytes": 0,
        }
        raw = (b'{"id":"synthetic.case","kind":"exports",'
               b'"obligations":["API-EXPORTS"],"result":{}}')
        consume_fuzz_record(raw, state)
        consume_fuzz_record(raw, state)

    rejected("reject-duplicate-streamed-fuzz-case-identity",
             duplicate_fuzz_identity, controls)
    rejected("reject-top-level-premature-phase-one-pass",
             lambda: broken_contract(lambda item: item.__setitem__("status", "PASS")), controls)
    rejected("reject-premature-candidate-authorization",
             lambda: broken_contract(lambda item: item["phase_gate"].__setitem__(
                 "candidate_evaluation_authorized", True)), controls)
    rejected("reject-premature-native-build-authorization",
             lambda: broken_contract(lambda item: item["phase_gate"].__setitem__(
                 "native_build_authorized", True)), controls)
    rejected("reject-fabricated-fuzz-two-reference-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_differential_property_fuzz"
             ].__setitem__("two_independent_reference_process_status", "PASS")), controls)
    rejected("reject-fabricated-fuzz-candidate-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_differential_property_fuzz"
             ].__setitem__("candidate_status", "PASS")), controls)
    rejected("reject-silent-fuzz-denominator-change",
             lambda: broken_contract(lambda item: item[
                 "supplemental_differential_property_fuzz"
             ].__setitem__("case_denominator_included_in_original_31237", True)), controls)
    rejected("reject-fabricated-public-import-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_public_contracts"]["public_import"
             ].__setitem__("actual_public_entrypoint_status", "PASS")), controls)
    rejected("reject-fabricated-candidate-signature-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_public_contracts"]["callable_introspection"
             ].__setitem__("candidate_status", "PASS")), controls)
    rejected("reject-fabricated-two-gib-search-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_public_contracts"]["genuine_large_input"
             ].__setitem__("full_size_candidate_search", "PASS")), controls)
    rejected("reject-fabricated-two-gib-substitution-pass",
             lambda: broken_contract(lambda item: item[
                 "supplemental_public_contracts"]["genuine_large_input"
             ].__setitem__("full_size_candidate_substitution", "PASS")), controls)
    rejected("reject-missing-phase-one-blocker",
             lambda: broken_contract(lambda item: item["phase_gate"]["blockers"].pop()), controls)
    rejected("physically-block-standard-library-matcher-import",
             lambda: builtins.__import__("re"), controls)
    rejected("physically-block-candidate-import",
             lambda: builtins.__import__("candidates"), controls)
    rejected("physically-block-native-loader-import",
             lambda: builtins.__import__("ctypes"), controls)
    rejected("physically-block-network-import",
             lambda: builtins.__import__("socket"), controls)
    rejected("physically-block-process-execution",
             lambda: os.system("true"), controls)
    rejected("physically-block-source-owner-write",
             lambda: builtins.open(ROOT + "/" + SOURCE, "ab"), controls)
    rejected("physically-block-temporary-root-read",
             lambda: os.open("/tmp/rebar-p0-v2-forbidden", os.O_RDONLY
                             | getattr(os, "O_NOFOLLOW", 0)), controls)
    rejected("physically-block-reference-archive-read",
             lambda: os.open(ROOT + "/oracle/phase1/evidence/"
                             "public-type-reference-context-v1-cpython-3-14-6-"
                             "candidate-context-p0.json.gz",
                             os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)), controls)
    rejected("physically-block-hidden-holdout-read",
             lambda: os.open(ROOT + "/benchmarks/holdout-hidden.jsonl",
                             os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)), controls)
    rejected("physically-block-clock-audit-event",
             lambda: sys.audit("time.time"), controls)
    rejected("physically-block-thread-start-audit-event",
             lambda: sys.audit("_thread.start_new_thread"), controls)
    no_forbidden_modules()
    return controls


def options() -> dict[str, str]:
    arguments = sys.argv[1:]
    require(len(arguments) in (5, 7),
            "usage: MODE --source-sha256 SHA --protocol-sha256 SHA [--contract-sha256 SHA]")
    mode = arguments[0]
    require(mode in ("--render-contract", "--self-test", "--verify-frozen-context"),
            "an explicit source-only mode is mandatory")
    result = {"mode": mode}
    for offset in range(1, len(arguments), 2):
        key = arguments[offset]
        require(key in ("--source-sha256", "--protocol-sha256", "--contract-sha256")
                and key not in result, "an unknown or duplicate source-only option was rejected")
        result[key] = checked_hash(arguments[offset + 1], key)
    require("--source-sha256" in result and "--protocol-sha256" in result,
            "the exact source and explanation must be independently caller-pinned")
    if mode == "--render-contract":
        require(len(arguments) == 5 and "--contract-sha256" not in result,
                "source-only contract rendering cannot assume an unpublished contract")
    else:
        require(len(arguments) == 7 and "--contract-sha256" in result,
                "verification requires an independently caller-pinned exact contract")
    return result


def main() -> int:
    try:
        parsed = options()
        mode = parsed["mode"]
        context = collect_context(
            parsed["--source-sha256"], parsed["--protocol-sha256"],
            parsed.get("--contract-sha256"), read_contract=mode != "--render-contract",
        )
        if mode == "--render-contract":
            sys.stdout.write(canonical(expected_contract(context)) + "\n")
            return 0
        document = context["document"]
        require(type(document) is dict, "the authenticated contract is missing")
        validate_contract(document, context)
        controls = hostile_controls(context) if mode == "--self-test" else []
        no_forbidden_modules()
        result = {
            "schema": SCHEMA + "-source-only-result",
            "version": 2,
            "mode": mode,
            "status": "PASS",
            "contract_status": "BLOCKED",
            "phase1_canonical_candidate_context_crosswalk": "PASS",
            "candidate_evaluation_authorized": False,
            "native_build_authorized": False,
            "original_case_execution_denominator": ORIGINAL_CASES,
            "original_suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "obligation_count": len(INHERITED_OBLIGATIONS) + len(ADDITIONAL_OBLIGATIONS),
            "crosswalk_count": 34,
            "corrected_reference_status": "PASS",
            "corrected_reference_process_ids": [81, 82],
            "supplemental_fuzz_case_count": FUZZ_CASES,
            "supplemental_fuzz_streamed_bytes": FUZZ_BYTES,
            "supplemental_fuzz_streamed_newlines": FUZZ_CASES,
            "supplemental_fuzz_unique_case_ids": FUZZ_CASES,
            "supplemental_fuzz_maximum_record_bytes": 83_668,
            "supplemental_fuzz_maximum_record_payload_bytes": 83_667,
            "supplemental_fuzz_record_limit_bytes": MAX_RECORD_BYTES,
            "supplemental_fuzz_independent_reference_status": "NOT RUN",
            "supplemental_fuzz_candidate_status": "NOT RUN",
            "authenticated_published_source_owner_count": len(OWNERS),
            "current_overview_version": 60,
            "physical_audit_wall": "ENFORCED",
            "rejected_hostile_control_count": len(controls),
            "rejected_hostile_controls": controls,
            "archive_files_opened": 0,
            "holdout_files_opened": 0,
            "source_files_written": 0,
            "reference_processes_started": 0,
            "candidate_processes_started": 0,
            "clock_samples": 0,
            "performance": "NOT MEASURED",
            "winner_selected": False,
        }
        sys.stdout.write(canonical(result) + "\n")
        return 0
    except (FreezeError, OSError, UnicodeError, ValueError, RecursionError) as error:
        sys.stderr.write("additive Phase-1 source-only gate failed closed: "
                         + str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
