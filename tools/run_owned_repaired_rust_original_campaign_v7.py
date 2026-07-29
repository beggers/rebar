#!/usr/bin/env python3
"""Freeze a recoverable, genuinely original Rust V13 correctness campaign.

Source verification is read-only.  Matching, native replacement, recovery,
threads, subprocesses, and evidence publication are explicit, separate modes.
"""

from __future__ import annotations

import argparse
import ast
import base64
import builtins
import contextlib
import copy
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import importlib.machinery
import io
import json
import locale
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
import unicodedata
from typing import Any, Iterator, Mapping, Sequence
import zlib


ROOT = Path("/home/dev-user/src/rebar")
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE_RELATIVE = "tools/run_owned_repaired_rust_original_campaign_v7.py"
PROTOCOL_RELATIVE = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md"
CONTRACT_RELATIVE = "oracle/phase2/repaired-rust-original-campaign-v7.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v7"
CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
RECOVERY_SCHEMA = SCHEMA + "-public-exact-inode-recovery"
RESTORATION_SCHEMA = SCHEMA + "-exact-original-inode-restoration"
SIGNAL_SCHEMA = SCHEMA + "-graceful-controller-signal"
FAMILY = "rust"
LABEL = "phase2-v13-rust-pattern-repr-original-p0"
EVIDENCE_RELATIVE = "oracle/phase2/evidence"
PUBLIC_RECOVERY_ROOT = (
    "/tmp/rebar-phase2-repaired-rust-original-campaign-v2-"
    "safe-v7-phase2-v13-rust-pattern-repr-original-p0"
)
LOCK_NAME = "recoverable-controller-v7.lock"
PHASE_NAMES = ("reference-a", "reference-b")
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
RESTORATION_ORDER = tuple(reversed(ROLE_ORDER))
SIGNAL_NAMES = ("SIGINT", "SIGTERM", "SIGHUP")
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_BUILD_ARCHIVE_BYTES = 2 * 1024 * 1024
MAX_BUILD_PLAIN_BYTES = 2 * 1024 * 1024
MAX_RECEIPT_BYTES = 64 * 1024
MAX_GRAPH_BYTES = 2 * 1024 * 1024
MAX_NATIVE_BYTES = 2 * 1024 * 1024
MAX_WORKER_STDOUT_BYTES = 32 * 1024 * 1024
MAX_WORKER_STDERR_BYTES = 4 * 1024 * 1024
MAX_FAILURE_STREAM_CAPTURE_BYTES = 64 * 1024
MAX_SUITE_COMPRESSED_BYTES = 16 * 1024 * 1024
MAX_SUITE_PLAIN_BYTES = 512 * 1024 * 1024
MAX_PUBLIC_REPORT_BYTES = 32 * 1024 * 1024
WORKER_TIMEOUT_SECONDS = 8 * 3600
SUITE_COUNT = 13
CASE_COUNT = 31_237
PRIVATE_WAIVER_COUNT = 13
PREVIOUS_EVIDENCE_OWNER_COUNT = 159
PREVIOUS_AUTHENTICATED_REFERENCE_COUNT = 164
ACTUAL_EVIDENCE_OWNER_COUNT = 164
ACTUAL_AUTHENTICATED_REFERENCE_COUNT = 169
SUPPLEMENT_CASE_COUNT = 50
SUPPLEMENT_REFERENCE_PROCESS_COUNT = 2
SUPPLEMENT_MATRIX_SHA256 = "89ff9e5197ac0fee63a5b7f3880d9d66083f7e25255d0d062e14ff84ab5c884b"
ACTUAL_FIRST_MISMATCH = "pattern-and-match-representation/058"
ACTUAL_FIRST_MISMATCH_SHA256 = "1130da7818fe8b27a0d74f607bd4531c43f5f12ec9d6674419aa448786884d75"

# Every entry is an already published, immutable source or evidence owner.
PRODUCER = {
    "source": ("tools/run_owned_six_family_original_p0_producer_v4.py",
               "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md",
                 "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981),
    "contract": ("oracle/phase2/six-family-p0-producer-v4.json",
                 "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867),
}
V39 = {
    "source": ("tools/render_candidate_current_overview_v39.py",
               "8adb7202644da2d19a4d2f50fe191de8d84007ce9b654a427a61fb4ea883c6b5", 115526),
    "inputs": ("docs/evidence/candidate-current-overview-v39.inputs.json",
               "22e740d2f7a22e4bd485c5d6e83204bfd2c529f1b87dd041d4ed604849b69d6b", 198039),
    "summary": ("docs/evidence/candidate-current-overview-v39.json",
                "d25c486e36d82069c718f82a1f6281295d539606dcd72a0a6c2c295f5a4e4ca6", 561943),
    "svg": ("docs/evidence/candidate-current-overview-v39.svg",
            "eecc366a7e14e3bee67a801cbf4b07e848af3659a82cc0715a90525c05652a9a", 11485),
}
V40 = {
    "source": ("tools/render_candidate_current_overview_v40.py",
               "15dc12f2d6a3c329d326f8d5b53bd2b1db7e82d01bb7c55e1178bd4ec0587c14", 50218),
    "inputs": ("docs/evidence/candidate-current-overview-v40.inputs.json",
               "a05ee04da984b618781bc31fe0deba6d1daf7c44256d7804e539ddd1392a2ffd", 211598),
    "summary": ("docs/evidence/candidate-current-overview-v40.json",
                "5e9f2216fc2a0ab4742d36a1aa49c422880a8ae17e3e1534da9b362ca0eeda92", 602620),
    "svg": ("docs/evidence/candidate-current-overview-v40.svg",
            "7e9189fb06410903b9f5d851648893e7984b8ecd1ba7d42c73329c1f985857e3", 12009),
}
V41 = {
    "source": ("tools/render_candidate_current_overview_v41.py",
               "c0ab9b19acd895a122a171ca1d9df9010de0ec732b81b0f52f29b96cbc88f87a", 50242),
    "inputs": ("docs/evidence/candidate-current-overview-v41.inputs.json",
               "3abaa207a8d25f03c59bd9f7443dcd0bfb5fd6934c7f1fa388e2abf636893fc4", 235674),
    "summary": ("docs/evidence/candidate-current-overview-v41.json",
                "e2835917d55d654a6d4c167298737c51f5f3b299ab7e2bc2c2eba60f9bff4f9f", 675118),
    "svg": ("docs/evidence/candidate-current-overview-v41.svg",
            "882e8ddb4e233a1c569c0330bbbf618f65f54bcf3d0bb59dc1c99542677dd2b7", 12401),
}
V42 = {
    "source": ("tools/render_candidate_current_overview_v42.py",
               "8e4783f7c61340ce8f291f84e2dfa802189a66353edd7a89026934d9863d1ce2", 51652),
    "inputs": ("docs/evidence/candidate-current-overview-v42.inputs.json",
               "ca11b1d4d7e7cd483a8ebf81fe12f36037a22608cf8ab459ce9d97d16f86dda2", 271354),
    "summary": ("docs/evidence/candidate-current-overview-v42.json",
                "30b7ba546209796f950ea6720a19acb16972bf8d984841f74d45c00d4c639838", 787504),
    "svg": ("docs/evidence/candidate-current-overview-v42.svg",
            "3d1f05706861d662f3113dc7340ceb09731c66b137df99637819a3e8b4cbd781", 12837),
}
V43 = {
    "source": ("tools/render_candidate_current_overview_v43.py",
               "3b3647a2090fd98e89ea421b2d2a3018983e1014adecf9f0b30731b54ca51e8b", 67805),
    "inputs": ("docs/evidence/candidate-current-overview-v43.inputs.json",
               "394fb27e12b9a48fbd8bdd353930084891c09118e0cfa49fc90f596124e15017", 281096),
    "summary": ("docs/evidence/candidate-current-overview-v43.json",
                "1c5ea146e6d40f0e81f2fe274f2a1a50fe01efdd074ca7ea5b36cca420d16bf0", 817337),
    "svg": ("docs/evidence/candidate-current-overview-v43.svg",
            "bee43e78aa59a806927a50e1e807181c62a3f6497d75add1834de2c75fdc546b", 13359),
}
V6_PREDECESSOR = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v6.py",
               "c25cbdf3674fc3e054c388e53de3ed38d4b1dab0a820808c42848e1803909f5e", 374429),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md",
                 "ddc5c212d3e188bc1d1cdde992bf872a38962e64d3b07d6ec7c275ba4f55f13c", 8551),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v6.json",
                 "ce044f18be388ab0608d0bd3bb68751e6970973f8e6ef758971e75e6d6b584a5", 33386),
}
ACTUAL_V6_PREFLIGHT_FAILURE = {
    "failure": (
        "oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v6-rust-"
        "phase2-v13-rust-pattern-repr-original-p0-entry-failure.json",
        "88367fd41665bbeafb0645e3b03130ca97c1c54729863372d422e693169420d7",
        3175,
    ),
    "observation": (
        "oracle/phase2/evidence/"
        "repaired-rust-original-campaign-v6-rust-"
        "phase2-v13-rust-pattern-repr-original-p0-entry-failure-observation.json",
        "51846c742aafbfc2c42ddad75836310bba518b3a76d0f8fa1548a55128852ad6",
        3061,
    ),
}
CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND = 166
CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND = 171
CORRECTED_C_ONLY_V10 = {
    "runner": ("tools/run_frozen_p0_candidate_v10.py",
               "c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a", 91132),
    "worker": ("tools/run_frozen_p0_candidate_worker_v8.py",
               "78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1", 95361),
    "protocol": ("oracle/phase2/P0-CANDIDATE-PROTOCOL-V10.md",
                 "2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae", 6792),
    "contract": ("oracle/phase2/p0-candidate-protocol-v10.json",
                 "8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737", 21238),
}
# This independently reviewed V40 draft was superseded before any commit.
# Its same three paths now hold this V41 rebase: never authenticate these
# historic digests as live, committed, pushed, or candidate-run owners.
SUPERSEDED_REVIEWED_V40_RUST_V6 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v6.py",
               "e1dbad33e0e6ee323f6110559d797fb91eb1610b63b639e217b04485dc60fefd", 349224),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V6.md",
                 "6a8f086fa80c938c8f6c5e9521d5933c23de70e7f26c05893a30c472a40e5ef8", 6944),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v6.json",
                 "6ec627e4ffd380e8620642578327b95025dafb7e9ef553bd27bd2a072e2dc4ee", 26499),
}
ZIG_PHRASE_V3 = {
    "source": ("tools/apply_owned_zig_scanner_phrase_source_repair_v3.py",
               "9b5cf55b9d66729b84b91470f8ba5906208ccee09312b43c329acaab2ff34010", 84556),
    "protocol": ("oracle/phase2/ZIG-SCANNER-PHRASE-SOURCE-REPAIR-V3.md",
                 "78fccd7fffd33e5ecd9a9033d8225c294d82ee07f391eb46ccd621a08e0d38e1", 6205),
    "contract": ("oracle/phase2/zig-scanner-phrase-source-repair-v3.json",
                 "4eee672b4fe6f25f7481c34a34928f00d34a45a9e0675e024238a8ee5576fade", 11117),
}
CORRECTED_REFERENCE = {
    "source": ("tools/verify_owned_public_type_reference_context_v1.py",
               "bff95e5630e875e1b389eeb4555810a112728dbed5f2cc7c43e1ec83d0817ddc", 102474),
    "protocol": ("oracle/phase1/P0-PUBLIC-TYPE-REFERENCE-CONTEXT-V1.md",
                 "11ca046ccd5087b2212b8ad8496896fb1fd60e408a193e038bae4b19fb360018", 10691),
    "contract": ("oracle/phase1/p0-public-type-reference-context-v1.json",
                 "dd0ea680e9a73345f7c323e278ba7ccebd5a3bb26cb606a9bdbecf7c3fb8298b", 13965),
    "archive": (
        "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0.json.gz",
        "c4906928850329fa3576576221e713ce653adae17a02a4de4bac4cb006389e05", 1374913,
    ),
    "receipt": (
        "oracle/phase1/evidence/public-type-reference-context-v1-cpython-3-14-6-candidate-context-p0-publication-receipt.json",
        "ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966", 2509,
    ),
    "falsification": (
        "oracle/phase1/evidence/public-type-candidate-context-falsification-v1.json",
        "319f0f75aaaea16fd1f41d814785d67060c57060852893349366cc3b482c4670", 3892,
    ),
}
IMMUTABLE_GOAL = {
    "goal": ("GOAL.md",
             "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756),
}
CORRECTED_REFERENCE_RECORDS_SHA256 = (
    "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
)
CORRECTED_REFERENCE_CACHE_RECORDS_SHA256 = (
    "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
)
HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256 = (
    "df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a"
)
HISTORICAL_FULL_PUBLIC_RECORDS_SHA256 = (
    "0b78702279b7ae2eb8be493bbf04df75719f36c2943f26c9df3e950f32d68e21"
)
CORRECTED_REFERENCE_MATRIX_SHA256 = (
    "c315e37dfa2e79ab62519ea84c710d4e3ca41d63d34873894bf7415278b56123"
)
CORRECTED_REFERENCE_CACHE_MATRIX_SHA256 = (
    "09b5d7cb665af227b8d6c733c795d68f9a1e22c62956b9d64105a9234af6abca"
)
CORRECTED_REFERENCE_CACHE_CASE_IDS_SHA256 = (
    "df43bd52adb112c0fde2bfe24a45200ca2ac30a9c41dfdc5716e3e81cbe19ce0"
)
CORRECTED_REFERENCE_PIDS = (81, 82)
CORRECTED_REFERENCE_CASE_COUNT = 6912
CORRECTED_REFERENCE_CACHE_CASE_COUNT = 96
CORRECTED_REFERENCE_REPORT_SHA256 = (
    "bc6c0fc9b4e3ff57faecd7e6dda982c1099d170e09dd8ce5641c48872479bebd"
)
CORRECTED_REFERENCE_REPORT_BYTES = 73371145
PUBLICATION = {
    "source": ("tools/run_owned_six_family_original_p0_campaign_v2.py",
               "6b06931ff64c5fe5b6bbbc3e970e56c0a94a24c28dfa6d3aa6140fc4d8fb54a1", 101836),
    "protocol": ("oracle/phase2/SIX-FAMILY-P0-CAMPAIGN-V2.md",
                 "e47cce8a6f60971bd3c18a4bfe248039ed9abd5b4144ec4355a77825a1435d4e", 4995),
    "contract": ("oracle/phase2/six-family-p0-campaign-v2.json",
                 "e44960e46c590cb5ab482ef323f3ae8598900f144b53a2377f62b3bb827935d7", 21314),
}
V2 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v2.py",
               "a6ffce3eb9ff09f27f3e35f84b35b9d1aba6e29dae225c56c036de85e089b7b3", 143441),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V2.md",
                 "9b9a246a08c0e89667899a6317df41424320617f7c4ac6cb84ef210fabee1ca0", 9342),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v2.json",
                 "bc100f6a7a3d4ec2640e131211ecea202172846daa10c93d73cbf58ea74ed547", 15927),
}
V3 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v3.py",
               "23819da6e6bb1ce8b27144a5d974b4bb0ecac845c844cb6fadae2ba01b2ef3d2", 89825),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V3.md",
                 "c29edb7751045da17cce2052e028b92530d8eab5ba6b8adafc21135a746f7883", 5766),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v3.json",
                 "ab4b424570254201865394330e025850b4626dfe2eaacd4ec82f41d2e99b0980", 10992),
}
V4 = {
    "source": ("tools/run_owned_repaired_rust_original_campaign_v4.py",
               "7d63b397deddd5c23af075754fcb50f7b3bdfb44390269383aae7903d46b4dd0", 176358),
    "protocol": ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V4.md",
                 "5296b7ed7c3ba37ce4e299924e9e9edae849bebcd0e92e828977ae9ac6c9e26b", 7725),
    "contract": ("oracle/phase2/repaired-rust-original-campaign-v4.json",
                 "26e86429e1e437fc791401197fb8c6dd9cf399bb025bd027af5f9c2554d6f60b", 14361),
}
V35 = {
    "source": ("tools/render_candidate_current_overview_v35.py",
               "390373ef8d196c54301ba6917b15b847708359dd27724f7463d9497e706aa618", 86043),
    "inputs": ("docs/evidence/candidate-current-overview-v35.inputs.json",
               "e90ba3ac5bce1b4c73e1005e740d36c1d24d94a065f71d154ae50075895cf73a", 141446),
    "summary": ("docs/evidence/candidate-current-overview-v35.json",
                "5cf793bbd79a65720b4081809c53333b028f133f51143ee22acb3ce43b805367", 442601),
    "svg": ("docs/evidence/candidate-current-overview-v35.svg",
            "bc4ec953b521973d4f2ee69db36e75d4e9ec539b4025e1cef3ad90a7c18315a3", 9905),
}
BUILD = {
    "source": ("tools/reproduce_owned_rust_pattern_repr_source_build_v13.py",
               "2ec050c9902cbb3a239ed3a2dce3258344300b40546e37aea374cf18a9c8b797", 133023),
    "protocol": ("oracle/phase2/RUST-PATTERN-REPR-SOURCE-BUILD-V13.md",
                 "3c486fdb63041b4f6060a6147186dd93c8339cbdff5f8060f597ab156ff05701", 5894),
    "contract": ("oracle/phase2/rust-pattern-repr-source-build-v13.json",
                 "15023a0a484715f2d97ae5ea9649bb16fe3d30781d601635bda40c246c5906aa", 20519),
    "archive": (
        "oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0.json.gz",
        "c201c014f55a51454baab77d2148dc39d6024bae3273242d6eb1f1b43f419f6a", 108985,
    ),
    "receipt": (
        "oracle/phase2/evidence/native-source-build-v13-rust-phase2-v13-rust-pattern-repr-original-p0-publication-receipt.json",
        "4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805", 2437,
    ),
}
PUBLIC_REPAIR = {
    "source": ("tools/apply_owned_rust_public_contract_source_repair_v3.py",
               "5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859", 92060),
    "protocol": ("oracle/phase2/RUST-PUBLIC-CONTRACT-SOURCE-REPAIR-V3.md",
                 "2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34", 6405),
    "contract": ("oracle/phase2/rust-public-contract-source-repair-v3.json",
                 "82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1", 14817),
}
REFERENCE = {
    "source": ("tools/run_owned_callable_introspection_reference_v2.py",
               "00c543077bfbe38e5c48e9970f7881119d21cb32cf91e838d21587f8f820ada4", 86258),
    "protocol": ("oracle/phase1/CALLABLE-INTROSPECTION-REFERENCE-V2.md",
                 "1e316b848e5d7a44b83a8f44605f08370faacb33074c2b79c042c76d9390a59f", 7487),
    "contract": ("oracle/phase1/callable-introspection-reference-v2.json",
                 "0f87ef8926771cfe39e33d95b3b871f03c9f1c44fe932615f7067d391eb68f42", 7253),
    "receipt": ("oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6-publication-receipt.json",
                "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334", 3533),
    "supplement": ("oracle/phase1/p0-callable-introspection-v1.json",
                    "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349", 14749),
}
HISTORICAL_RUST_RECEIPT = (
    "oracle/phase2/evidence/repaired-rust-original-campaign-v4-rust-"
    "phase2-v12-rust-flag-original-p0-failures-publication-receipt.json",
    "201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3", 4674,
)
HISTORICAL_RUST_ARCHIVE_SHA256 = (
    "2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f"
)
HISTORICAL_RUST_JOURNAL = (
    "726e81e5d2ee255e1f46d3029290ae9486fbd23711c9a45a691d091d088f3278"
)
CORRECTED_PUBLIC_SHA256 = (
    "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
)
CORRECTED_PUBLIC_BYTES = 31934
HISTORICAL_DERIVED_PUBLIC_SHA256 = (
    "f8afb6c6e020faad3452b59ceb84abc957ee74d1397397008b3178856abe01a5"
)
HISTORICAL_V2_REPAIRED_PUBLIC_SHA256 = (
    "81089bab906c9bb511fe0779d8e1ddf735850fce62eaac06ca1e6c678856578c"
)
HISTORICAL_V2_REPAIRED_PUBLIC_BYTES = 31_464
BRIDGE_SOURCE_SHA256 = (
    "4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257"
)
BRIDGE_SOURCE_BYTES = 176118
ENGINE_SHA256 = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
ENGINE_BYTES = 658344
BRIDGE_SHA256 = "7f5dfb587fc7f53ce3a7b6cfa568a6e49c009a4d0015929b4dada28cb5425c54"
BRIDGE_BYTES = 148656
V13_PLAIN_SHA256 = "7bf86cbaec1df17548a0989d03db896036a86b0671d32e82f12ce4c3fae630db"
V13_PLAIN_BYTES = 760477
ACTUAL_V13_PRIVATE_ROOT = "/tmp/rebar-phase2-native-build-v9-rust-8esd2fj3"
ACTUAL_V13_NATIVE_IDENTITIES = {
    "reference-a": {"engine": (2049, 11672997),
                    "bridge": (2049, 11673003)},
    "reference-b": {"engine": (2049, 11673027),
                    "bridge": (2049, 11673033)},
}

ORIGINALS: dict[str, dict[str, Any]] = {
    "bridge_source": {
        "relative": "candidates/rust/py_bridge.c",
        "sha256": "f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b",
        "bytes": 175676, "device": 2064, "inode": 419054,
        "mode": 0o600, "uid": 1000, "nlink": 1,
    },
    "adapter": {
        "relative": "candidates/rust_candidate.py",
        "sha256": "6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b",
        "bytes": 31151, "device": 2064, "inode": 428100,
        "mode": 0o600, "uid": 1000, "nlink": 1,
    },
    "engine": {
        "relative": "candidates/_rust_engine.so",
        "sha256": "f8cd2e8ecac5ab6a12eb933e6d1d234700a71ab64fc1578800f46ce93d25b8b4",
        "bytes": 660440, "device": 2064, "inode": 430563,
        "mode": 0o755, "uid": 1000, "nlink": 1,
    },
    "bridge": {
        "relative": "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        "sha256": "6fdd114c812b63acce88ef56b8077da5a260c8719ffe2058d29e5be418a26f15",
        "bytes": 144992, "device": 2064, "inode": 430629,
        "mode": 0o755, "uid": 1000, "nlink": 1,
    },
}
CORRECTED_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", CORRECTED_PUBLIC_SHA256, CORRECTED_PUBLIC_BYTES),
    ("candidates/rust/py_bridge.c", BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
    ("candidates/rust/Cargo.toml", "2e57ff8ad346ffc850d50eab429a0f05c14825c4984fd8c9bc36eab03239a966", 225),
    ("candidates/rust/Cargo.lock", "267c3b21dc41432f7c5ee036b50b48d81f9228384780b4d13a6b41a8ad2cef63", 167),
    ("candidates/rust/src/lib.rs", "c4901e83e359191badc39fbf42ea65f0eb07a3db870172acf8cae65ffb1eaf2d", 177967),
    ("candidates/rust/src/newline.rs", "13216ffbea967af121c77d57abe14906030e7f3a6906c554399511154a3d6d8b", 14416),
    ("candidates/rust/src/search.rs", "4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe", 14773),
    ("candidates/rust/src/stack.rs", "5198a056e99bde5632169cfc5b07ad913910cdb1b30785dad4744ccb9a30809e", 7269),
    ("candidates/rust/src/unicode_tables.rs", "f33ac8b88ec2925ee096febb1815a8958b90cd2ca3c54217267d0c255f67a6af", 471989),
)
HISTORICAL_V2_REPAIRED_SOURCE_OWNERS: tuple[
    tuple[str, str, int], ...
] = (
    (
        "candidates/rust_candidate.py",
        HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
        HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
    ),
    *CORRECTED_SOURCE_OWNERS[1:],
)

ORIGINAL_SOURCE_OWNERS: tuple[tuple[str, str, int], ...] = (
    ("candidates/rust_candidate.py", ORIGINALS["adapter"]["sha256"], ORIGINALS["adapter"]["bytes"]),
    ("candidates/rust/py_bridge.c", ORIGINALS["bridge_source"]["sha256"], ORIGINALS["bridge_source"]["bytes"]),
    *CORRECTED_SOURCE_OWNERS[2:],
)
SUITES: tuple[tuple[str, int], ...] = (
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
PROCESS_NAMES = (
    "readelf_version", "gcc_version", "rustc_version", "cargo_version",
    "build_rust_engine", "build_rust_bridge", "engine_dynamic",
    "engine_symbols", "bridge_dynamic", "bridge_symbols",
    "engine_sections", "engine_notes", "bridge_sections", "bridge_notes",
)
RUST_EXPORTS = (
    "rebar_collect_ascii", "rebar_collect_wide", "rebar_compile",
    "rebar_compile_scanner", "rebar_error_copy", "rebar_error_include",
    "rebar_error_len", "rebar_error_pos", "rebar_flags", "rebar_free",
    "rebar_groups", "rebar_match", "rebar_match_ascii", "rebar_match_wide",
    "rebar_name_copy", "rebar_name_count", "rebar_name_group", "rebar_name_len",
)


class CampaignError(Exception):
    """A frozen original case, actual owner, or recovery proof was rejected."""


class SourceOnlyViolation(CampaignError):
    """A synthetic source check attempted an actual external operation."""


class GracefulControllerSignal(CampaignError):
    """An actually installed controller handler received a recoverable signal."""

    def __init__(self, signum: int) -> None:
        self.signum = signum
        self.signal_name = signal.Signals(signum).name
        super().__init__("restore all original Rust inodes after " + self.signal_name)


def require(valid: Any, reason: str) -> None:
    if valid is not True:
        raise CampaignError(reason)


def checked_digest(value: Any, label: str) -> str:
    require(type(value) is str and len(value) == 64
            and all(part in "0123456789abcdef" for part in value),
            "require an exact independent SHA-256 for " + label)
    return value


def digest(raw: Any) -> str:
    require(type(raw) is bytes, "hash only complete actual bytes")
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                           separators=(",", ":"), allow_nan=False)
                .encode("ascii") + b"\n")
    except (TypeError, ValueError, OverflowError, UnicodeError) as error:
        raise CampaignError("reject a noncanonical complete observation") from error


def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CampaignError("reject duplicated JSON owner: " + str(key))
        result[key] = value
    return result


def strict_document(raw: Any, label: str, *, exact: bool = True) -> dict[str, Any]:
    require(type(raw) is bytes and bool(raw),
            "require the complete immutable document " + label)
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                CampaignError("reject a non-finite JSON number: " + token)),
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CampaignError("reject malformed original document " + label) from error
    require(type(value) is dict, "require an exact object for " + label)
    if exact:
        require(canonical(value) == raw,
                "reject noncanonical or concealed owner bytes: " + label)
    return value


def checked_relative(value: Any) -> str:
    require(type(value) is str and bool(value) and not value.startswith("/")
            and "\\" not in value and "\x00" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "reject an absolute, escaped, empty, or ambiguous owner")
    return value


def verify_runtime() -> None:
    require(sys.implementation.name == "cpython"
            and sys.version_info[:3] == (3, 14, 6)
            and os.path.abspath(sys.executable) == PYTHON
            and sys.flags.isolated == 1 and sys.dont_write_bytecode is True,
            "require independently pinned isolated CPython 3.14.6 with -I -B")


def read_absolute(path: str, expected: str, *, maximum: int,
                  exact_size: int | None = None,
                  private: bool = False,
                  device: int | None = None,
                  inode: int | None = None) -> tuple[bytes, dict[str, Any]]:
    checked_digest(expected, "descriptor-bound exact owner")
    require(type(path) is str and os.path.isabs(path) and "\x00" not in path
            and type(maximum) is int and maximum > 0,
            "read only one exact bounded absolute owner")
    if exact_size is not None:
        require(type(exact_size) is int and 0 <= exact_size <= maximum,
                "reject an invalid exact owner byte count")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    handle = os.open(path, flags)
    try:
        first = os.fstat(handle)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1
                and 0 <= first.st_size <= maximum
                and (exact_size is None or first.st_size == exact_size)
                and (not private or (first.st_uid == os.geteuid()
                                     and stat.S_IMODE(first.st_mode) == 0o600))
                and (device is None or first.st_dev == device)
                and (inode is None or first.st_ino == inode),
                "reject a foreign, linked, substituted, oversized, or truncated owner")
        remaining = first.st_size
        pieces: list[bytes] = []
        while remaining:
            piece = os.read(handle, min(remaining, 1024 * 1024))
            require(type(piece) is bytes and bool(piece),
                    "reject a truncated bounded owner")
            pieces.append(piece)
            remaining -= len(piece)
        require(os.read(handle, 1) == b"", "reject concealed trailing owner bytes")
        raw = b"".join(pieces)
        last = os.fstat(handle)
        require((first.st_dev, first.st_ino, first.st_size,
                 first.st_mtime_ns, first.st_ctime_ns)
                == (last.st_dev, last.st_ino, last.st_size,
                    last.st_mtime_ns, last.st_ctime_ns)
                and digest(raw) == expected,
                "reject owner bytes or inode exchanged during authentication")
        return raw, {
            "path": path, "sha256": expected, "bytes": len(raw),
            "size_bytes": len(raw), "device": last.st_dev,
            "inode": last.st_ino, "mode": stat.S_IMODE(last.st_mode),
            "uid": last.st_uid, "nlink": last.st_nlink,
        }
    finally:
        os.close(handle)


def read_owned(item: tuple[str, str, int], *, maximum: int = MAX_SOURCE_BYTES,
               private: bool = False) -> tuple[bytes, dict[str, Any]]:
    relative, expected, count = item
    checked_relative(relative)
    raw, owner = read_absolute(str(ROOT / relative), expected,
                               maximum=maximum, exact_size=count,
                               private=private)
    owner["relative"] = relative
    return raw, owner


def owner_document(item: tuple[str, str, int]) -> dict[str, Any]:
    return {"path": item[0], "sha256": item[1], "bytes": item[2]}


def grouped_owners(items: Mapping[str, tuple[str, str, int]]) -> dict[str, Any]:
    return {name: owner_document(item)
            for name, item in sorted(items.items())}


def zero_effects() -> dict[str, Any]:
    return {
        "actual_candidate_workers": 0,
        "actual_candidate_imports": 0,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "actual_native_activations": 0,
        "actual_native_library_loads": 0,
        "canonical_target_reads": 0,
        "canonical_target_stats": 0,
        "canonical_target_replacements": 0,
        "recovery_roots_created": 0,
        "recovery_locks_acquired": 0,
        "recovery_journals_created": 0,
        "signal_handlers_installed": 0,
        "signal_masks_installed": 0,
        "threads_started": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "matching_archive_gzip_inflation_count": 0,
        "matching_archive_bytes_read": 0,
        "v13_source_build_archive_read_attempted": False,
        "v13_source_build_archive_read_count": 0,
        "v13_source_build_archive_compressed_bytes_read": 0,
        "v13_source_build_archive_gzip_inflation_attempted": False,
        "v13_source_build_archive_gzip_inflation_count": 0,
        "v13_source_build_archive_uncompressed_bytes_read": 0,
        "v13_source_build_archive_uncompressed_sha256": "NOT READ",
        "phase1_reference_archive_bytes_read": 0,
        "phase1_reference_archive_decompressed": False,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "workspace_mutations": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def protocol_document(source_pin: str, protocol_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "V7 campaign source")
    checked_digest(protocol_pin, "V7 campaign explanation")
    return {
        "schema": CONTRACT_SCHEMA,
        "status": "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN",
        "version": 7,
        "family": FAMILY,
        "campaign_label": LABEL,
        "source": {"path": SOURCE_RELATIVE, "sha256": source_pin},
        "protocol": {"path": PROTOCOL_RELATIVE, "sha256": protocol_pin},
        "pinned_cpython": {"path": PYTHON, "sha256": PYTHON_SHA256,
                            "version": "3.14.6", "isolated": True},
        "original_oracle": {
            "producer": grouped_owners(PRODUCER),
            "suite_count": SUITE_COUNT,
            "case_execution_denominator": CASE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "source_ordered_suites": [
                {"id": name, "case_execution_count": count}
                for name, count in SUITES
            ],
            "upstream_public_records": 152,
            "upstream_real_debug_skip_count": 1,
            "nested_case_count": 128,
            "nested_interpreter_events": 394,
            "nested_interpreters_created": 11,
            "nested_interpreters_destroyed": 11,
            "actual_locale_cases": 64,
            "actual_locale_transitions": 192,
            "actual_shared_pattern_thread_cases": 512,
            "actual_python_buffer_exporter_cases": 264,
            "canonical_public_module": "candidates.rust_candidate",
            "cross_family_matching_allowed": False,
            "external_regex_dependency_allowed": False,
            "stdlib_re_fallback_allowed": False,
            "candidate_wrapper_allowed": False,
            "reference_worker_started": False,
            "candidate_case_producer_version": 4,
            "corrected_reference_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "corrected_cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "candidate_run_uses_both_complete_reference_vectors": True,
        },
        "actual_corrected_candidate_context_reference": {
            "owners": grouped_owners(CORRECTED_REFERENCE),
            "actual_reference_status": "PASS",
            "actual_publication_status": "PASS",
            "source_contract_reference_status":
                "NOT RUN; FROZEN BEFORE REAL RUN",
            "actual_distinct_reference_process_count": 2,
            "actual_distinct_reference_process_ids":
                list(CORRECTED_REFERENCE_PIDS),
            "case_count_per_reference": CORRECTED_REFERENCE_CASE_COUNT,
            "total_observed_reference_case_count":
                2 * CORRECTED_REFERENCE_CASE_COUNT,
            "full_reference_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "cache_case_count_per_reference":
                CORRECTED_REFERENCE_CACHE_CASE_COUNT,
            "cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "cache_case_ids_sha256":
                CORRECTED_REFERENCE_CACHE_CASE_IDS_SHA256,
            "cache_matrix_sha256":
                CORRECTED_REFERENCE_CACHE_MATRIX_SHA256,
            "original_suite_matrix_sha256":
                CORRECTED_REFERENCE_MATRIX_SHA256,
            "historical_script_context_records_sha256":
                HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
            "historical_full_script_context_records_sha256":
                HISTORICAL_FULL_PUBLIC_RECORDS_SHA256,
            "corrected_reference_report_uncompressed_sha256":
                CORRECTED_REFERENCE_REPORT_SHA256,
            "corrected_reference_report_uncompressed_bytes":
                CORRECTED_REFERENCE_REPORT_BYTES,
            "source_context_opens_reference_archive": False,
            "source_context_inflates_reference_archive": False,
            "candidate_run_requires_both_complete_reference_vectors": True,
            "historical_96_case_falsification_removed": False,
            "original_public_cases_removed": 0,
            "additional_private_waivers": 0,
            "c_pattern_equality_failure_waived": False,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
        },
        "actual_corrected_v13_build": {
            "owners": grouped_owners(BUILD),
            "build_status": "PASS",
            "build_version": 13,
            "build_label": LABEL,
            "phase_count": 2,
            "compiler_process_count": 28,
            "process_names_per_phase": list(PROCESS_NAMES),
            "compressed_archive_byte_limit": MAX_BUILD_ARCHIVE_BYTES,
            "uncompressed_archive_byte_limit": MAX_BUILD_PLAIN_BYTES,
            "uncompressed_sha256": V13_PLAIN_SHA256,
            "uncompressed_bytes": V13_PLAIN_BYTES,
            "native_role_count": 2,
            "engine": {"sha256": ENGINE_SHA256, "bytes": ENGINE_BYTES},
            "bridge": {"sha256": BRIDGE_SHA256, "bytes": BRIDGE_BYTES},
            "corrected_public_adapter": {
                "relative": "candidates/rust_candidate.py",
                "sha256": CORRECTED_PUBLIC_SHA256,
                "bytes": CORRECTED_PUBLIC_BYTES,
                "independent_fresh_phase_count": 2,
            },
            "corrected_bridge_source": {
                "relative": "candidates/rust/py_bridge.c",
                "sha256": BRIDGE_SOURCE_SHA256,
                "bytes": BRIDGE_SOURCE_BYTES,
                "independent_fresh_phase_count": 2,
            },
            "corrected_public_overlay_apply_count": 2,
            "bridge_overlay_apply_count": 2,
            "source_owner_count_per_phase": 9,
            "unchanged_source_owner_count_per_phase": 7,
            "complete_corrected_source_owners": [
                {"relative": relative, "sha256": fingerprint,
                 "bytes": count}
                for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS
            ],
            "corrected_public_source_repair": grouped_owners(PUBLIC_REPAIR),
            "native_bytes_may_equal_an_earlier_reproducible_build": True,
            "actual_v13_build_provenance_cannot_be_replaced_with_v11": True,
            "actual_v13_build_provenance_cannot_be_replaced_with_v12": True,
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
        },
        "corrected_c_only_runner_v10": {
            "owners": grouped_owners(CORRECTED_C_ONLY_V10),
            "status": "C-ONLY RUNNER SOURCE FROZEN; CORRECTED C MATCHING NOT RUN",
            "family": "c",
            "runnable_candidate_families": ["c"],
            "runnable_candidate_family_count": 1,
            "first_party_source_inventory_family_count": 6,
            "six_family_inventory_is_source_only": True,
            "corrected_candidate_matching": "NOT RUN",
            "candidate_workers_started": 0,
            "candidate_qualified": False,
            "other_corrected_candidate_family_count": 5,
            "other_corrected_candidate_matching": "NOT RUN",
            "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
        "historical_v2_helper_authentication": {
            "owners": grouped_owners(V2),
            "historical_helper_schema":
                "rebar-owned-repaired-rust-original-campaign-v2",
            "historical_helper_contract_schema":
                "rebar-owned-repaired-rust-original-campaign-v2-source-freeze",
            "historical_repaired_source_owners": [
                {"path": relative, "sha256": fingerprint, "bytes": count}
                for relative, fingerprint, count
                in HISTORICAL_V2_REPAIRED_SOURCE_OWNERS
            ],
            "historical_repaired_source_owner_count": 9,
            "historical_public_adapter": {
                "path": "candidates/rust_candidate.py",
                "sha256": HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
                "bytes": HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
            },
            "distinct_historical_v12_public_adapter_sha256":
                HISTORICAL_DERIVED_PUBLIC_SHA256,
            "corrected_v13_public_adapter": {
                "path": "candidates/rust_candidate.py",
                "sha256": CORRECTED_PUBLIC_SHA256,
                "bytes": CORRECTED_PUBLIC_BYTES,
            },
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "source_verification_method":
                "BOUNDED COMPLETE SOURCE AST; NO IMPORT OR EXECUTION",
            "helper_source_verified_before_any_archive_read": True,
            "real_helper_predicates_verified_before_any_archive_read": True,
            "module_imported_by_source_gate": False,
            "module_executed_by_source_gate": False,
            "helper_invoked_by_source_gate": False,
            "source_build_archive_reads_by_source_gate": 0,
            "candidate_workers_started_by_source_gate": 0,
            "holdout": "NOT OPENED",
        },
        "preserved_actual_v6_preflight_failure": {
            "owners": grouped_owners(ACTUAL_V6_PREFLIGHT_FAILURE),
            "historical_v6_controller": grouped_owners(V6_PREDECESSOR),
            "status": "FAIL",
            "failure_class":
                "PRE-ACTIVATION HISTORICAL HELPER FINGERPRINT MISMATCH",
            "error_type": "CampaignError",
            "error_message":
                "authenticate immutable historical helpers without running V2",
            "actual_controller_process_count": 1,
            "attempted_suite_count": 0,
            "started_suite_count": 0,
            "completed_suite_count": 0,
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "actual_source_build_archive_read_count": 1,
            "actual_source_build_archive_gzip_inflation_count": 1,
            "actual_source_build_archive_sha256": BUILD["archive"][1],
            "actual_source_build_archive_compressed_bytes":
                BUILD["archive"][2],
            "actual_source_build_archive_uncompressed_bytes":
                V13_PLAIN_BYTES,
            "actual_source_build_archive_uncompressed_sha256":
                V13_PLAIN_SHA256,
            "historical_controller_ledger_omitted_archive_effect": True,
            "matching_archive_read_count": 0,
            "reference_archive_read_count": 0,
            "semantic_mismatch_count": "NOT MEASURED",
            "candidate_qualified": False,
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
        "published_current_v43_overview": {
            "owners": grouped_owners(V43),
            "graph_status": "PASS",
            "overview_version": 43,
            "previous_v42_overview": grouped_owners(V42),
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "candidate_case_producer": grouped_owners(PRODUCER),
            "candidate_case_producer_status":
                "V4 SOURCE FROZEN; RUST PREFLIGHT FAIL; "
                "ZERO RUNNABLE CANDIDATES",
            "same_context_reference_correction_status": "PASS",
            "corrected_reference_status": "PASS",
            "corrected_reference_publication_status": "PASS",
            "corrected_reference_full_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "corrected_reference_cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "first_party_source_inventory_family_count": 6,
            "actually_runnable_candidate_families": [],
            "actually_runnable_candidate_family_count": 0,
            "corrected_c_matching_status": "NOT RUN",
            "corrected_rust_matching_status": "NOT RUN",
            "rust_v6_runner_status":
                "SOURCE FROZEN; NOT RUNNABLE; PREFLIGHT FAILED",
            "actual_v6_controller_status": "FAIL",
            "actual_v6_failure_owners":
                grouped_owners(ACTUAL_V6_PREFLIGHT_FAILURE),
            "actual_v6_controller_process_count": 1,
            "actual_v6_candidate_workers": 0,
            "actual_v6_native_activations": 0,
            "actual_v6_source_build_archive_read_count": 1,
            "actual_v6_source_build_archive_gzip_inflation_count": 1,
            "actual_v6_source_build_archive_compressed_bytes":
                BUILD["archive"][2],
            "actual_v6_source_build_archive_uncompressed_bytes":
                V13_PLAIN_BYTES,
            "actual_v6_controller_ledger_omits_archive_effect": True,
            "all_candidate_matching_blocked": True,
            "authenticated_evidence_owner_lower_bound":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
            "authenticated_history_reference_lower_bound":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
            "qualified_candidate_count": 0,
            "candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
        "preserved_v42_overview": {
            "owners": grouped_owners(V42),
            "graph_status": "PASS",
            "overview_version": 42,
            "previous_v41_overview": grouped_owners(V41),
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "historical_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNER_COUNT,
            "historical_history_reference_lower_bound":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "corrected_c_matching_status": "NOT RUN",
            "corrected_rust_matching_status": "NOT RUN",
            "qualified_candidate_count": 0,
            "candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
        },
        "preserved_v41_overview": {
            "owners": grouped_owners(V41),
            "graph_status": "PASS",
            "overview_version": 41,
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "candidate_case_producer": grouped_owners(PRODUCER),
            "candidate_case_producer_status":
                "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN",
            "same_context_reference_correction_status": "PASS",
            "corrected_reference_status": "PASS",
            "corrected_reference_publication_status": "PASS",
            "corrected_reference_full_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "corrected_reference_cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "corrected_c_only_runner_owners":
                grouped_owners(CORRECTED_C_ONLY_V10),
            "corrected_c_only_runner_family": "c",
            "corrected_c_only_runnable_family_count": 1,
            "corrected_c_only_runner_status":
                "C-ONLY RUNNER SOURCE FROZEN; CORRECTED C MATCHING NOT RUN",
            "corrected_c_matching_status": "NOT RUN",
            "corrected_c_candidate_workers_started": 0,
            "corrected_c_candidate_qualified": False,
            "corrected_c_matching_mismatch_reduction": "NOT MEASURED",
            "corrected_c_matching_speedup": "NOT MEASURED",
            "first_party_source_inventory_family_count": 6,
            "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
            "all_candidate_matching_blocked": True,
            "required_corrected_candidate_runner_versions": ["RUST V6"],
            "stale_candidate_worker_versions": ["RUST V5"],
            "authenticated_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNER_COUNT,
            "authenticated_history_reference_lower_bound":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "previous_v40_overview": grouped_owners(V40),
            "zig_scanner_phrase_source_repair": {
                "owners": grouped_owners(ZIG_PHRASE_V3),
                "status":
                    "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN",
                "source_applied": False,
                "scanner_case_count": 1024,
                "preserved_nonoverflow_case_count": 960,
                "prospective_overflow_case_count": 64,
                "corrected_candidate_matching": "NOT RUN",
                "measured_mismatch_reduction": "NOT MEASURED",
                "measured_speedup": "NOT MEASURED",
                "candidate_workers_started": 0,
            },
            "later_append_only_evidence_allowed": True,
            "qualified_candidate_count": 0,
            "candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
        },
        "superseded_reviewed_v40_rust_v6_source_freeze": {
            "owners": grouped_owners(SUPERSEDED_REVIEWED_V40_RUST_V6),
            "review_status": "INDEPENDENTLY REVIEWED; SUPERSEDED BEFORE COMMIT",
            "historical_overview_version": 40,
            "historical_snapshot_only": True,
            "committed": False,
            "pushed": False,
            "live_owner_authentication":
                "NOT POSSIBLE; SAME THREE PATHS REBASED TO V41",
            "candidate_matching": "NOT RUN",
            "candidate_qualified": False,
        },
        "preserved_v40_overview": {
            "owners": grouped_owners(V40),
            "graph_status": "PASS",
            "overview_version": 40,
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "candidate_case_producer": grouped_owners(PRODUCER),
            "candidate_case_producer_status":
                "SOURCE FROZEN; CANDIDATES NOT RUN",
            "same_context_reference_correction_status": "PASS",
            "corrected_reference_status": "PASS",
            "corrected_reference_publication_status": "PASS",
            "corrected_reference_full_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "corrected_reference_cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "all_candidate_matching_blocked": True,
            "required_corrected_candidate_runner_versions":
                ["V8", "V10", "RUST V6"],
            "stale_candidate_worker_versions":
                ["V7", "V9", "RUST V5"],
            "authenticated_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNER_COUNT,
            "authenticated_history_reference_lower_bound":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "previous_v39_overview": grouped_owners(V39),
            "zig_scanner_phrase_source_repair": {
                "owners": grouped_owners(ZIG_PHRASE_V3),
                "status":
                    "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN",
                "source_applied": False,
                "scanner_case_count": 1024,
                "preserved_nonoverflow_case_count": 960,
                "prospective_overflow_case_count": 64,
                "corrected_candidate_matching": "NOT RUN",
                "measured_mismatch_reduction": "NOT MEASURED",
                "measured_speedup": "NOT MEASURED",
                "candidate_workers_started": 0,
            },
            "later_append_only_evidence_allowed": True,
            "qualified_candidate_count": 0,
            "candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
        },
        "preserved_v39_overview": {
            "owners": grouped_owners(V39),
            "graph_status": "PASS",
            "overview_version": 39,
            "case_execution_denominator": CASE_COUNT,
            "suite_count": SUITE_COUNT,
            "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            "candidate_case_producer": grouped_owners(PRODUCER),
            "candidate_case_producer_status":
                "SOURCE FROZEN; CANDIDATES NOT RUN",
            "same_context_reference_correction_status": "PASS",
            "corrected_reference_status": "PASS",
            "corrected_reference_publication_status": "PASS",
            "corrected_reference_full_records_sha256":
                CORRECTED_REFERENCE_RECORDS_SHA256,
            "corrected_reference_cache_records_sha256":
                CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
            "all_candidate_matching_blocked": True,
            "required_corrected_candidate_runner_versions":
                ["V8", "V10", "RUST V6"],
            "stale_candidate_worker_versions":
                ["V7", "V9", "RUST V5"],
            "authenticated_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNER_COUNT,
            "authenticated_history_reference_lower_bound":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "later_append_only_evidence_allowed": True,
            "qualified_candidate_count": 0,
            "candidate_matching": "NOT RUN",
            "holdout": "NOT OPENED",
        },
        "preserved_v35_history": {
            "owners": grouped_owners(V35),
            "repository_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
            "authenticated_reference_count": PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
            "actual_rust_status": "FAIL",
            "actual_rust_semantic_mismatch_count": 1036,
            "actual_rust_verified_passing_case_count": 8965,
            "actual_rust_first_failure_case": ACTUAL_FIRST_MISMATCH,
            "actual_rust_first_failure_record_sha256":
                ACTUAL_FIRST_MISMATCH_SHA256,
            "actual_rust_original_receipt": owner_document(HISTORICAL_RUST_RECEIPT),
            "actual_rust_original_archive_sha256": HISTORICAL_RUST_ARCHIVE_SHA256,
            "actual_rust_original_uncompressed_bytes": 5280314,
            "actual_rust_original_archive_decompressed": False,
            "actual_rust_original_journal_sha256": HISTORICAL_RUST_JOURNAL,
            "actual_c_status": "FAIL",
            "actual_c_semantic_mismatch_count": 1230,
            "actual_c_verified_passing_case_count": 7325,
            "actual_zig_status": "FAIL",
            "actual_zig_semantic_mismatch_count": 1764,
            "actual_zig_verified_passing_case_count": 3711,
            "qualified_candidate_count": 0,
        },
        "actual_supplementary_reference": {
            "owners": grouped_owners(REFERENCE),
            "case_count": SUPPLEMENT_CASE_COUNT,
            "reference_status": "PASS",
            "actual_reference_process_count":
                SUPPLEMENT_REFERENCE_PROCESS_COUNT,
            "reference_process_ids": [81, 82],
            "reference_failure_count": 0,
            "matrix_sha256": SUPPLEMENT_MATRIX_SHA256,
            "included_in_original_case_denominator": False,
            "candidate_status": "NOT RUN",
            "candidate_cases_executed": 0,
            "reference_archive_decompressed": False,
            "reference_workers_started_by_source_gate": 0,
        },
        "current_historical_accounting": {
            "historical_v35_evidence_owner_count":
                PREVIOUS_EVIDENCE_OWNER_COUNT,
            "historical_v35_authenticated_reference_count":
                PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
            "historical_pre_failure_evidence_owner_lower_bound":
                ACTUAL_EVIDENCE_OWNER_COUNT,
            "historical_pre_failure_reference_lower_bound":
                ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
            "actual_v6_failure_evidence_owners_created": 2,
            "actual_evidence_owner_count_before_new_campaign":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
            "actual_authenticated_reference_count_before_new_campaign":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
            "evidence_owner_lower_bound_before_new_campaign":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
            "authenticated_reference_lower_bound_before_new_campaign":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
            "future_campaign_evidence_owners_created": 0,
            "later_append_only_evidence_allowed": True,
            "qualified_candidate_count": 0,
        },
        "historical_frozen_campaigns": {
            "rust_v2_worker_only": grouped_owners(V2),
            "rust_v3_recoverable_controller": grouped_owners(V3),
            "rust_v4_recoverable_controller": grouped_owners(V4),
            "streaming_publication_v2": grouped_owners(PUBLICATION),
            "v2_unsafe_controller_allowed": False,
            "v2_unsafe_activation_allowed": False,
            "c_only_v9_runner_allowed": False,
            "zig_only_v7_activation_allowed": False,
        },
        "four_original_target_owners": [
            {"role": role, "original": copy.deepcopy(ORIGINALS[role])}
            for role in ROLE_ORDER
        ],
        "public_recovery": {
            "root": PUBLIC_RECOVERY_ROOT,
            "root_owner_mode": "0700",
            "lock_filename": LOCK_NAME,
            "lock_owner_mode": "0600",
            "exclusive_nonblocking_controller_lock": True,
            "fixed_public_journal_filename": "recovery-journal.json",
            "journal_fsync_before_first_target_mutation": True,
            "journal_location_announced_before_first_target_mutation": True,
            "individual_intention_fsync_before_hardlink_or_replace": True,
            "original_inode_backup": "ADJACENT SAME-DIRECTORY NO-FOLLOW HARDLINK",
            "role_order": list(ROLE_ORDER),
            "restoration_order": list(RESTORATION_ORDER),
            "restore_device_inode_mode_uid_nlink_and_hash": True,
            "registered_graceful_signals": list(SIGNAL_NAMES),
            "block_graceful_signals_during_individual_mutations": True,
            "keyboard_interrupt_and_system_exit_swallowed": False,
            "sigkill_automatically_recovered": False,
            "power_failure_automatically_recovered": False,
            "sigkill_or_power_failure_requires_public_recover": True,
            "recovery_command_mode": "--recover",
            "caller_pins_exact_journal_sha256": True,
            "caller_pins_exact_root": True,
            "unknown_or_foreign_owner_is_overwritten": False,
            "recovery_idempotent": True,
            "group_atomic": False,
        },
        "future_lossless_publication": {
            "historical_helper_source_verified_before_archive": True,
            "historical_helper_module_verified_before_archive": True,
            "current_evidence_owner_lower_bound_before_publication":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
            "current_history_reference_lower_bound_before_publication":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
            "new_distinct_durable_publication_owner_count": 2,
            "resulting_evidence_owner_lower_bound_after_both_owners":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND + 2,
            "resulting_history_reference_lower_bound_after_both_owners":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND + 2,
            "resulting_counts_require_two_distinct_durable_owners": True,
            "publication_failure_never_claims_resulting_counts": True,
            "complete_publication_exercised_inside_source_wall": True,
            "streaming_archive_owner_relative_is_evidence_basename": True,
            "v2_receipt_owner_relative_is_repository_evidence_path": True,
            "both_owner_absolute_paths_are_independently_authenticated":
                True,
            "receipt_owner_digest_size_uid_and_single_link_verified": True,
            "only_controller_retains_v13_source_build_archive": True,
            "controller_v13_source_build_archive_read_count": 1,
            "controller_v13_source_build_archive_effect_ledger_required":
                True,
            "unledgered_retained_build_context_rejected_before_any_read":
                True,
            "original_suite_workers_retain_v13_source_build_archive": False,
            "original_suite_worker_v13_source_build_archive_reads": 0,
            "public_recovery_retain_v13_source_build_archive": False,
            "public_recovery_v13_source_build_archive_reads": 0,
            "public_recovery_succeeds_without_source_build_archive": True,
            "actual_worker_and_recovery_callables_source_wall_tested": True,
            "corrected_original_reference_inputs_unchanged": True,
            "source_build_archive_read_attempt_recorded_before_read": True,
            "source_build_archive_actual_read_count_retained": True,
            "source_build_archive_compressed_bytes_retained": True,
            "source_build_archive_inflation_attempt_recorded_before_inflation":
                True,
            "source_build_archive_actual_inflation_count_retained": True,
            "source_build_archive_uncompressed_bytes_and_sha256_retained":
                True,
            "source_build_archive_effects_survive_entry_failure": True,
            "publication_only_after_all_four_original_inodes_restored": True,
            "actual_original_suite_worker_count": SUITE_COUNT,
            "worker_launch_attempt_recorded_before_spawn": True,
            "started_worker_pid_retained_before_communication": True,
            "worker_attempts_starts_and_complete_observations_are_distinct": True,
            "distinct_positive_worker_process_ids_required": True,
            "maximum_complete_worker_stdout_bytes": MAX_WORKER_STDOUT_BYTES,
            "maximum_complete_worker_stderr_bytes": MAX_WORKER_STDERR_BYTES,
            "maximum_failure_stream_prefix_bytes":
            MAX_FAILURE_STREAM_CAPTURE_BYTES,
            "oversized_worker_stream_retains_full_size_and_sha256": True,
            "truncated_worker_stream_never_counts_as_complete": True,
            "maximum_worker_compressed_observation_bytes":
            MAX_SUITE_COMPRESSED_BYTES,
            "maximum_streamed_public_report_bytes": MAX_PUBLIC_REPORT_BYTES,
            "numeric_total_mismatches_require_all_thirteen_observations": True,
            "partial_total_mismatches": "NOT MEASURED",
            "authorized_run_entry_failure_retains_actual_effect_ledger": True,
            "publication_failure_never_reports_source_only_zero_effects": True,
            "deterministic_single_member_zero_time_gzip": True,
            "archive_and_receipt_distinct_fresh_owner_inodes": True,
            "archive_owner_mode": "0600",
            "receipt_owner_mode": "0600",
            "publication_pass_means": "DURABLE PUBLICATION ONLY",
            "all_original_case_records_preserved": True,
            "all_actual_mismatches_preserved": True,
            "reference_oracle_rerun_allowed": False,
        },
        "immutable_goal": owner_document(IMMUTABLE_GOAL["goal"]),
        "source_only_effects": zero_effects(),
    }


def validate_contract(value: Any, source_pin: str,
                      protocol_pin: str) -> dict[str, Any]:
    require(type(value) is dict
            and canonical(value) == canonical(protocol_document(
                checked_digest(source_pin, "V4 source"),
                checked_digest(protocol_pin, "V4 protocol"))),
            "reject a substituted Rust V13 build, original suite, owner, or recovery policy")
    return value


def bounded_build_gzip(raw: bytes, *, expected_sha256: str,
                       expected_size: int) -> bytes:
    require(type(raw) is bytes and 18 <= len(raw) <= MAX_BUILD_ARCHIVE_BYTES
            and raw[:3] == b"\x1f\x8b\x08"
            and raw[4:8] == b"\x00\x00\x00\x00",
            "require exactly one deterministic, bounded V13 gzip member")
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        plain = decoder.decompress(raw, MAX_BUILD_PLAIN_BYTES + 1)
        require(len(plain) <= MAX_BUILD_PLAIN_BYTES
                and not decoder.unconsumed_tail
                and decoder.eof and not decoder.unused_data,
                "reject an oversized, truncated, trailing, or multiple-member V13 archive")
        remainder = decoder.flush()
        require(len(plain) + len(remainder) <= MAX_BUILD_PLAIN_BYTES,
                "reject concealed V13 decompression bytes")
        plain += remainder
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject an invalid original V13 gzip archive") from error
    require(len(plain) == expected_size and digest(plain) == expected_sha256,
            "authenticate every real V13 build document byte")
    return plain


def decode_process_stream(record: Mapping[str, Any], channel: str) -> bytes:
    encoded = record.get(channel + "_base64")
    expected_size = record.get(channel + "_bytes")
    expected_hash = record.get(channel + "_sha256")
    require(type(encoded) is str and type(expected_size) is int
            and 0 <= expected_size <= MAX_BUILD_PLAIN_BYTES,
            "preserve each complete real V13 compiler " + channel)
    checked_digest(expected_hash, "actual V13 compiler " + channel)
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject forged V13 compiler " + channel) from error
    require(len(raw) == expected_size and digest(raw) == expected_hash,
            "reject substituted V13 compiler " + channel)
    return raw


def require_actual_native_audit(output: Mapping[str, Any], role: str) -> None:
    require(type(output) is dict and output.get("family") == FAMILY
            and output.get("role") == role
            and output.get("candidate_imported") is False
            and output.get("prebuilt_artifact_read") is False,
            "reject a borrowed, imported, or prebuilt Rust native " + role)
    expected_hash, expected_size = (
        (ENGINE_SHA256, ENGINE_BYTES) if role == "engine"
        else (BRIDGE_SHA256, BRIDGE_BYTES)
    )
    expected_name = (
        "_rust_engine.so" if role == "engine"
        else "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
    )
    require(output.get("sha256") == expected_hash
            and output.get("size_bytes") == expected_size
            and output.get("file_name") == expected_name
            and type(output.get("device")) is int
            and type(output.get("inode")) is int
            and output["device"] >= 0 and output["inode"] > 0,
            "reject unproven complete V13 Rust native output " + role)
    audit = output.get("audit")
    require(type(audit) is dict and audit.get("role") == role
            and audit.get("cross_family_dependency_count") == 0
            and audit.get("external_regex_dependency_count") == 0,
            "reject sibling or external regex delegation in " + role)
    if role == "engine":
        require(tuple(audit.get("required_exports", ())) == RUST_EXPORTS
                and tuple(audit.get("exports", ())) == RUST_EXPORTS
                and tuple(audit.get("needed", ()))
                == ("ld-linux-x86-64.so.2", "libc.so.6", "libgcc_s.so.1")
                and audit.get("runpath") == [],
                "verify all eighteen genuine independently owned Rust exports")
    else:
        require(audit.get("exports") == ["PyInit__rust_bridge"]
                and audit.get("required_exports") == ["PyInit__rust_bridge"]
                and audit.get("needed") == ["_rust_engine.so", "libc.so.6"]
                and audit.get("runpath") == ["$ORIGIN"],
                "require the exact own-engine-only $ORIGIN CPython bridge")


def validate_phase(phase: Any, index: int, *, inspect_private: bool
                   ) -> dict[str, Any]:
    require(type(phase) is dict and 0 <= index < len(PHASE_NAMES)
            and phase.get("name") == PHASE_NAMES[index]
            and phase.get("candidate_imports") == 0
            and phase.get("candidate_processes_started") == 0
            and phase.get("hidden_cases_read") == 0
            and phase.get("timing_trials_run") == 0
            and phase.get("native_libraries_loaded") == 0,
            "require the exact fresh no-matching V13 build phase")
    sources = phase.get("fresh_source_owners")
    outputs = phase.get("native_outputs")
    forensics = phase.get("native_forensics")
    require(type(sources) is dict and type(outputs) is dict
            and type(forensics) is dict
            and set(sources) == {entry[0] for entry in CORRECTED_SOURCE_OWNERS}
            and set(outputs) == {"engine", "bridge"}
            and set(forensics) == {"engine", "bridge"},
            "require all nine original Rust owners and both native roles")
    actual_inodes: set[tuple[int, int]] = set()
    snapshot_root: str | None = None
    live: dict[str, dict[str, Any]] = {}
    for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS:
        row = sources[relative]
        require(type(row) is dict and row.get("sha256") == fingerprint
                and row.get("bytes") == count
                and type(row.get("device")) is int
                and type(row.get("inode")) is int and row["inode"] > 0
                and row.get("exclusive_creation") is True
                and row.get("same_inode_readback_verified") is True
                and row.get("path")
                == "<FRESH_PRIVATE_TMP>/" + PHASE_NAMES[index]
                + "/source/" + relative,
                "reject an omitted, crossed, stale, or renamed V13 source: "
                + relative)
        identity = (row["device"], row["inode"])
        require(identity not in actual_inodes,
                "require nine genuinely distinct private V13 source inodes")
        actual_inodes.add(identity)
        if relative in {"candidates/rust_candidate.py",
                        "candidates/rust/py_bridge.c"}:
            overlay = row.get("source_overlay")
            require(type(overlay) is dict and overlay.get("status") == "PASS"
                    and overlay.get("phase") == PHASE_NAMES[index]
                    and overlay.get("source_apply_count") == 1
                    and overlay.get("candidate_imports", 0) == 0,
                    "require one real phase-owned first-party source overlay")
            root = overlay.get("snapshot_root")
            require(type(root) is str
                    and root.startswith("/tmp/rebar-phase2-native-build-v9-rust-")
                    and root.endswith("/" + PHASE_NAMES[index] + "/source")
                    and ".." not in Path(root).parts,
                    "reject a substituted actual V13 private phase root")
            if inspect_private:
                require(root == ACTUAL_V13_PRIVATE_ROOT + "/"
                        + PHASE_NAMES[index] + "/source",
                        "reject every stale equal-byte V13 private build root")
            if snapshot_root is None:
                snapshot_root = root
            require(snapshot_root == root,
                    "bind both corrected overlays to the same real phase root")
            if relative == "candidates/rust_candidate.py":
                require(overlay.get("schema")
                        == "rebar-phase2-owned-rust-public-contract-source-repair-v3-private-source-application"
                        and overlay.get("source_sha256") == PUBLIC_REPAIR["source"][1]
                        and overlay.get("protocol_sha256") == PUBLIC_REPAIR["protocol"][1]
                        and overlay.get("contract_sha256") == PUBLIC_REPAIR["contract"][1]
                        and overlay.get("derived_source_sha256")
                        == CORRECTED_PUBLIC_SHA256
                        and overlay.get("derived_source_bytes")
                        == CORRECTED_PUBLIC_BYTES
                        and overlay.get("canonical_candidate_modified") is False,
                        "reject the old f8afb V12 public adapter or a wrapper")
            else:
                require(overlay.get("derived_sha256") == BRIDGE_SOURCE_SHA256
                        and overlay.get("derived_bytes") == BRIDGE_SOURCE_BYTES
                        and overlay.get("candidate_original_modified") is False,
                        "authenticate the genuinely corrected private Rust bridge")
    require(type(snapshot_root) is str,
            "retain the authentic complete V13 source snapshot root")
    for role in ("engine", "bridge"):
        output = outputs[role]
        require_actual_native_audit(output, role)
        if inspect_private:
            require((output.get("device"), output.get("inode"))
                    == ACTUAL_V13_NATIVE_IDENTITIES[PHASE_NAMES[index]][role],
                    "reject a stale equal-byte or substituted actual V13 "
                    + PHASE_NAMES[index] + " native inode: " + role)
        expected_name = ("_rust_engine.so" if role == "engine"
                         else "_rust_bridge.cpython-314-x86_64-linux-gnu.so")
        require(output.get("path")
                == "<FRESH_PRIVATE_TMP>/" + PHASE_NAMES[index]
                + "/native/" + expected_name,
                "reject a redirected native build phase")
        forensic = forensics[role]
        require(type(forensic) is dict
                and set(forensic) == {"sections", "notes", "raw_elf64"}
                and all(type(forensic[name]) is dict
                        for name in ("sections", "notes", "raw_elf64")),
                "preserve complete actual independently owned ELF forensics")
    if inspect_private:
        for relative, fingerprint, count in CORRECTED_SOURCE_OWNERS:
            row = sources[relative]
            _, actual = read_absolute(
                snapshot_root + "/" + relative, fingerprint,
                maximum=MAX_NATIVE_BYTES, exact_size=count,
                device=row["device"], inode=row["inode"],
            )
            live[relative] = actual
        native_root = snapshot_root.removesuffix("/source") + "/native"
        for role in ("engine", "bridge"):
            row = outputs[role]
            name = row["file_name"]
            _, actual = read_absolute(
                native_root + "/" + name, row["sha256"],
                maximum=MAX_NATIVE_BYTES,
                exact_size=row["size_bytes"],
                device=row["device"], inode=row["inode"],
            )
            live[role] = actual
    return {"phase": phase, "snapshot_root": snapshot_root,
            "live_owners": live, "source_owner_count": len(sources)}


def validate_v13_report(report: Any, receipt: Any,
                        archive_owner: Mapping[str, Any],
                        *, inspect_private: bool) -> dict[str, Any]:
    require(type(report) is dict and type(receipt) is dict
            and type(archive_owner) is dict,
            "require three independent actual V13 build owners")
    require(report.get("schema")
            == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-actual-corrected-dual-overlay-build"
            and report.get("status") == "PASS"
            and report.get("version") == 13
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("source_sha256") == BUILD["source"][1]
            and report.get("protocol_sha256") == BUILD["protocol"][1]
            and report.get("contract_sha256") == BUILD["contract"][1]
            and report.get("phase_count") == 2
            and report.get("expected_actual_compiler_process_count") == 28
            and report.get("actual_compiler_process_count") == 28
            and report.get("public_derived_sha256") == CORRECTED_PUBLIC_SHA256
            and report.get("historical_public_derived_sha256")
            == HISTORICAL_DERIVED_PUBLIC_SHA256
            and report.get("corrected_public_overlay_apply_count") == 2
            and report.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA256
            and report.get("bridge_overlay_apply_count") == 2
            and report.get("candidate_correctness") == "NOT MEASURED"
            and report.get("candidate_qualified") is False
            and report.get("candidate_processes_started") == 0
            and report.get("candidate_imports") == 0
            and report.get("native_libraries_loaded") == 0
            and report.get("hidden_cases_read") == 0
            and report.get("clock_samples") == 0
            and report.get("timing_trials_run") == 0
            and report.get("performance") == "NOT MEASURED"
            and report.get("memory") == "NOT MEASURED"
            and report.get("holdout") == "NOT OPENED"
            and report.get("winner_selected") is False,
            "reject a V11, nonreproducible, unowned, or candidate-running V13 build")
    require(receipt.get("schema")
            == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == LABEL
            and receipt.get("source_sha256") == BUILD["source"][1]
            and receipt.get("protocol_sha256") == BUILD["protocol"][1]
            and receipt.get("contract_sha256") == BUILD["contract"][1]
            and receipt.get("archive_relative") == BUILD["archive"][0]
            and receipt.get("archive_sha256") == BUILD["archive"][1]
            and receipt.get("archive_bytes") == BUILD["archive"][2]
            and receipt.get("uncompressed_sha256") == V13_PLAIN_SHA256
            and receipt.get("uncompressed_bytes") == V13_PLAIN_BYTES
            and receipt.get("public_derived_sha256") == CORRECTED_PUBLIC_SHA256
            and receipt.get("corrected_public_overlay_apply_count") == 2
            and receipt.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA256
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_imports") == 0
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("holdout") == "NOT OPENED",
            "never confuse V13 publication, source build, or matching status")
    publication = receipt.get("archive_publication")
    require(type(publication) is dict
            and publication.get("path") == str(ROOT / BUILD["archive"][0])
            and publication.get("sha256") == archive_owner.get("sha256")
            and publication.get("bytes") == archive_owner.get("bytes")
            and publication.get("device") == archive_owner.get("device")
            and publication.get("inode") == archive_owner.get("inode")
            and publication.get("exclusive_creation") is True
            and publication.get("same_inode_readback_verified") is True
            and publication.get("file_fsync_completed") is True
            and type(publication.get("write_calls")) is int
            and publication["write_calls"] > 0
            and type(receipt.get("archive_directory_fsync")) is dict
            and receipt["archive_directory_fsync"].get("completed") is True,
            "bind the V13 receipt to the exact durable archive inode")
    old = report.get("frozen_context")
    require(type(old) is dict and old.get("status") == "PASS"
            and old.get("version") == 13 and old.get("family") == FAMILY
            and old.get("repository_evidence_owner_lower_bound")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and old.get("authenticated_reference_lower_bound")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and old.get("case_execution_denominator") == CASE_COUNT
            and old.get("suite_count") == SUITE_COUNT
            and old.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and old.get("actual_rust_semantic_mismatch_count") == 1036
            and old.get("actual_rust_verified_passing_case_count") == 8965
            and old.get("actual_first_failure_case") == ACTUAL_FIRST_MISMATCH
            and old.get("actual_first_failure_record_sha256")
            == ACTUAL_FIRST_MISMATCH_SHA256
            and old.get("actual_c_semantic_mismatch_count") == 1230
            and old.get("actual_c_verified_passing_case_count") == 7325
            and old.get("actual_zig_v3_matching_status") == "FAIL"
            and old.get("actual_zig_v3_semantic_mismatch_count") == 1764
            and old.get("actual_zig_v3_verified_passing_case_count") == 3711
            and old.get("supplementary_signature_reference_status") == "PASS"
            and old.get("supplementary_signature_reference_cases_executed")
            == SUPPLEMENT_CASE_COUNT
            and old.get("supplementary_signature_reference_process_count")
            == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and old.get("supplementary_signature_candidate_status")
            == "NOT RUN"
            and old.get("qualified_candidate_count") == 0
            and old.get("corrected_public_derived_source_sha256")
            == CORRECTED_PUBLIC_SHA256
            and old.get("corrected_public_derived_source_bytes")
            == CORRECTED_PUBLIC_BYTES
            and old.get("bridge_derived_source_sha256") == BRIDGE_SOURCE_SHA256
            and old.get("bridge_derived_source_bytes") == BRIDGE_SOURCE_BYTES
            and old.get("candidate_imports") == 0
            and old.get("canonical_native_target_reads") == 0
            and old.get("canonical_native_target_stats") == 0
            and old.get("native_activations") == 0
            and old.get("hidden_cases_read") == 0
            and old.get("benchmark_files_read") == 0
            and old.get("holdout") == "NOT OPENED",
            "preserve all 159/164 historical owners, real Zig, and the "
            "completed independent 50-case CPython reference")
    processes = report.get("compiler_processes")
    require(type(processes) is list and len(processes) == 28
            and [item.get("name") for item in processes]
            == [*PROCESS_NAMES, *PROCESS_NAMES],
            "require both complete genuine fourteen-process source-build phases")
    pids: set[int] = set()
    for process in processes:
        require(type(process) is dict
                and type(process.get("pid")) is int and process["pid"] > 0
                and process["pid"] not in pids
                and process.get("exit_status") == 0
                and process.get("shell") is False
                and type(process.get("argv")) is list
                and bool(process["argv"])
                and all(type(item) is str for item in process["argv"]),
                "reject invented, failed, repeated, shell, or missing real compiler processes")
        pids.add(process["pid"])
        decode_process_stream(process, "stdout")
        decode_process_stream(process, "stderr")
    phases = report.get("phases")
    require(type(phases) is list and len(phases) == 2,
            "require both exact independent Rust V13 build phases")
    inspected = [validate_phase(phase, index, inspect_private=inspect_private)
                 for index, phase in enumerate(phases)]
    for relative, _, _ in CORRECTED_SOURCE_OWNERS:
        first = phases[0]["fresh_source_owners"][relative]
        second = phases[1]["fresh_source_owners"][relative]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"]),
                "reject reused cross-phase source inode: " + relative)
    for role in ("engine", "bridge"):
        first = phases[0]["native_outputs"][role]
        second = phases[1]["native_outputs"][role]
        require((first["device"], first["inode"])
                != (second["device"], second["inode"])
                and first["sha256"] == second["sha256"]
                and first["size_bytes"] == second["size_bytes"],
                "prove both genuinely independently reproduced native " + role)
    reproduction = report.get("reproducibility")
    require(type(reproduction) is dict
            and reproduction.get("status") == "PASS"
            and reproduction.get("byte_identical") is True
            and reproduction.get("independent_fresh_phase_count") == 2
            and reproduction.get("unique_process_count") == 28
            and reproduction.get("native_role_count") == 2
            and reproduction.get("source_owners_per_phase") == 9
            and reproduction.get("unchanged_source_owners_per_phase") == 7
            and reproduction.get("corrected_public_overlay_count") == 2
            and reproduction.get("bridge_overlay_count") == 2
            and reproduction.get("public_derived_sha256")
            == CORRECTED_PUBLIC_SHA256
            and reproduction.get("bridge_derived_sha256")
            == BRIDGE_SOURCE_SHA256
            and reproduction.get("native_libraries_loaded") == 0
            and reproduction.get("original_sources_modified") is False
            and reproduction.get("prebuilt_artifact_count") == 0,
            "reject a falsely reproducible, applied, or source-modifying V13 build")
    native = reproduction.get("native_outputs")
    require(type(native) is dict and set(native) == {"engine", "bridge"},
            "retain exactly both V13 reproduced native outputs")
    for role, expected_hash, expected_size in (
        ("engine", ENGINE_SHA256, ENGINE_BYTES),
        ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
    ):
        row = native[role]
        require(type(row) is dict and row.get("sha256") == expected_hash
                and row.get("size_bytes") == expected_size
                and row.get("fresh_independent_inode_count") == 2,
                "authenticate exact reproducible V13 native " + role)
    comparisons = reproduction.get("raw_elf_comparisons")
    require(type(comparisons) is dict
            and set(comparisons) == {"engine", "bridge"},
            "require the two complete actual native ELF comparisons")
    actual_pairs: set[tuple[str, int]] = set()
    for role, expected_hash, expected_size in (
        ("engine", ENGINE_SHA256, ENGINE_BYTES),
        ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
    ):
        row = comparisons[role]
        require(type(row) is dict
                and row.get("schema")
                == "rebar-phase2-owned-native-source-build-v7-complete-raw-elf-difference"
                and row.get("byte_identical") is True
                and row.get("phase_a_sha256") == expected_hash
                and row.get("phase_a_bytes") == expected_size
                and row.get("phase_a_sha256") == row.get("phase_b_sha256")
                and row.get("phase_a_bytes") == row.get("phase_b_bytes")
                and row.get("changed_section_count") == 0
                and row.get("changed_sections") == []
                and row.get("total_difference_span_count") == 0
                and row.get("total_differing_byte_count") == 0
                and row.get("difference_spans") == []
                and row.get("reported_span_count") == 0
                and row.get("omitted_span_count") == 0
                and row.get("report_truncated") is False,
                "reject incomplete actual Rust raw-byte reproducibility")
        actual_pairs.add((row["phase_a_sha256"], row["phase_a_bytes"]))
    require(actual_pairs == {(ENGINE_SHA256, ENGINE_BYTES),
                             (BRIDGE_SHA256, BRIDGE_BYTES)},
            "bind the raw-byte comparison to both real native V13 roles")
    return {"report": report, "receipt": receipt,
            "archive_owner": dict(archive_owner), "phases": inspected,
            "actual_process_count": len(pids), "native_roles": native}


def authenticate_v35(summary: Any, inputs: Any,
                     rust_receipt: Any) -> dict[str, Any]:
    require(type(summary) is dict and type(inputs) is dict
            and type(rust_receipt) is dict,
            "require three independently frozen previous matching documents")
    require(summary.get("schema") == "rebar-candidate-current-overview-v35-summary"
            and summary.get("status") == "PASS"
            and summary.get("full_case_denominator") == CASE_COUNT
            and summary.get("suite_count") == SUITE_COUNT
            and summary.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and summary.get("repository_evidence_owner_count")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and summary.get("authenticated_digest_addressed_history_paths")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and summary.get("qualified_candidate_count") == 0
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_receipt_status") == "PASS"
            and summary.get("rust_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and summary.get("rust_original_campaign_case_execution_denominator")
            == CASE_COUNT
            and summary.get("rust_original_campaign_candidate_worker_count") == 13
            and summary.get("rust_original_campaign_completed_suite_count") == 13
            and summary.get("rust_original_campaign_semantic_mismatch_count") == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count") == 8965
            and summary.get("rust_original_campaign_infrastructure_failure_count") == 0
            and summary.get("rust_original_campaign_recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and summary.get("rust_original_campaign_all_four_original_targets_restored")
            is True
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count") == 1230
            and summary.get("c_original_campaign_verified_passing_case_count") == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count") == 1764
            and summary.get("zig_original_campaign_verified_passing_case_count") == 3711
            and summary.get("additional_signature_frozen_case_count")
            == SUPPLEMENT_CASE_COUNT
            and summary.get("additional_signature_reference_status") == "PASS"
            and summary.get("additional_signature_reference_cases_executed")
            == SUPPLEMENT_CASE_COUNT
            and summary.get("additional_signature_candidate_status")
            == "NOT RUN"
            and summary.get("additional_signature_candidate_cases_executed")
            == 0
            and summary.get("uncompressed_rust_archive_opened_by_graph") is False
            and summary.get("uncompressed_rust_archive_bytes_read_by_graph") == 0
            and summary.get("hidden_cases_read") == 0
            and summary.get("clock_samples") == 0
            and summary.get("timing_trials_run") == 0
            and summary.get("performance") == "NOT MEASURED"
            and summary.get("final_holdout_opened") is False
            and summary.get("winner_selected") is False,
            "preserve real historical V35 159/164 owners, all three losses, "
            "and the actually passing separate 50-case reference")
    require(inputs.get("schema") == "rebar-candidate-current-overview-v35-inputs"
            and inputs.get("version") == 35
            and inputs.get("full_case_denominator") == CASE_COUNT
            and inputs.get("suite_count") == SUITE_COUNT
            and inputs.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and inputs.get("repository_evidence_owner_count")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and inputs.get("all_digest_addressed_history_path_count")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and inputs.get("candidate_qualified_count") == 0
            and inputs.get("actual_rust_candidate_workers") == 13
            and inputs.get("actual_rust_semantic_mismatch_count") == 1036
            and inputs.get("actual_rust_verified_passing_case_count") == 8965
            and inputs.get("actual_rust_infrastructure_failure_count") == 0
            and inputs.get("additional_signature_frozen_case_count")
            == SUPPLEMENT_CASE_COUNT
            and inputs.get("additional_signature_reference_status") == "PASS"
            and inputs.get("additional_signature_reference_cases_executed")
            == SUPPLEMENT_CASE_COUNT
            and inputs.get("additional_signature_candidate_status")
            == "NOT RUN"
            and inputs.get("additional_signature_candidate_cases_executed")
            == 0
            and inputs.get("uncompressed_rust_archive_opened_by_graph") is False
            and inputs.get("uncompressed_rust_archive_bytes_read_by_graph") == 0,
            "bind the original full Rust failure to independently frozen V35 inputs")
    require(rust_receipt.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v4-durable-publication-receipt"
            and rust_receipt.get("status") == "PASS"
            and rust_receipt.get("publication_status") == "PASS"
            and rust_receipt.get("publication_pass_means")
            == "DURABLE PUBLICATION ONLY"
            and rust_receipt.get("candidate_status") == "FAIL"
            and rust_receipt.get("family") == FAMILY
            and rust_receipt.get("label")
            == "phase2-v12-rust-flag-original-p0"
            and rust_receipt.get("suite_count") == SUITE_COUNT
            and rust_receipt.get("completed_suite_count") == SUITE_COUNT
            and rust_receipt.get("case_execution_denominator") == CASE_COUNT
            and rust_receipt.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and rust_receipt.get("actual_candidate_workers") == SUITE_COUNT
            and rust_receipt.get("verified_passing_case_count") == 8965
            and rust_receipt.get("semantic_mismatch_count") == 1036
            and rust_receipt.get("infrastructure_failure_count") == 0
            and rust_receipt.get("candidate_qualified") is False
            and rust_receipt.get("recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and rust_receipt.get("all_four_original_targets_restored") is True
            and rust_receipt.get("restoration_verified_before_publication") is True
            and rust_receipt.get("uncompressed_bytes") == 5280314
            and rust_receipt.get("group_atomic") is False
            and rust_receipt.get("hidden_cases_read") == 0
            and rust_receipt.get("benchmark_files_read") == 0
            and rust_receipt.get("holdout") == "NOT OPENED"
            and rust_receipt.get("performance") == "NOT MEASURED",
            "never mistake durable prior Rust failure publication for compatibility")
    archive = rust_receipt.get("archive")
    require(type(archive) is dict
            and archive.get("sha256") == HISTORICAL_RUST_ARCHIVE_SHA256
            and archive.get("size_bytes") == 3663299
            and archive.get("device") == 2064
            and archive.get("inode") == 524655
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True,
            "authenticate historical archive from its tiny receipt without opening it")
    restored = rust_receipt.get("restored_original_targets")
    require(type(restored) is dict and set(restored) == set(ROLE_ORDER),
            "preserve all four independently proved genuine original Rust targets")
    for role in ROLE_ORDER:
        expected = ORIGINALS[role]
        item = restored[role]
        require(type(item) is dict
                and item.get("relative") == expected["relative"]
                and item.get("sha256") == expected["sha256"]
                and item.get("size_bytes") == expected["bytes"]
                and item.get("device") == expected["device"]
                and item.get("inode") == expected["inode"]
                and item.get("mode") == expected["mode"]
                and item.get("uid") == expected["uid"]
                and item.get("nlink") == expected["nlink"],
                "reject a stale copied original Rust owner: " + role)
    included = inputs.get("actual_complete_rust_v4_campaign")
    require(type(included) is dict and included.get("status") == "FAIL"
            and included.get("semantic_mismatch_count") == 1036
            and included.get("verified_passing_case_count") == 8965
            and included.get("publication_receipt") == rust_receipt,
            "authenticate the exact prior independent Rust receipt twice")
    return {
        "historical_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "historical_authenticated_reference_count":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "rust_semantic_mismatch_count": 1036,
        "rust_verified_passing_case_count": 8965,
        "c_semantic_mismatch_count": 1230,
        "c_verified_passing_case_count": 7325,
        "zig_semantic_mismatch_count": 1764,
        "zig_verified_passing_case_count": 3711,
        "supplementary_reference_status": "PASS",
        "supplementary_reference_cases_executed": SUPPLEMENT_CASE_COUNT,
        "supplementary_candidate_status": "NOT RUN",
        "historical_rust_matching_archive_opened": False,
        "historical_rust_matching_archive_bytes_read": 0,
        "qualified_candidate_count": 0,
    }


def authenticate_supplementary_reference(
        receipt: Any, source_contract: Any) -> dict[str, Any]:
    require(type(receipt) is dict and type(source_contract) is dict,
            "require the independently pinned actual 50-case reference")
    frozen = source_contract.get("frozen_additional_oracle")
    core = source_contract.get("original_core")
    wall = source_contract.get("phase_boundary")
    require(source_contract.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-source-freeze"
            and source_contract.get("version") == 2
            and source_contract.get("source", {}).get("sha256")
            == REFERENCE["source"][1]
            and source_contract.get("protocol", {}).get("sha256")
            == REFERENCE["protocol"][1]
            and type(core) is dict
            and core.get("case_execution_denominator") == CASE_COUNT
            and core.get("suite_count") == SUITE_COUNT
            and core.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and core.get("denominator_modified") is False
            and type(frozen) is dict
            and frozen.get("separately_counted_case_count")
            == SUPPLEMENT_CASE_COUNT
            and frozen.get("included_in_original_core_denominator") is False
            and frozen.get("matrix_sha256") == SUPPLEMENT_MATRIX_SHA256
            and frozen.get("contract")
            == owner_document(REFERENCE["supplement"])
            and frozen.get("reference_status") == "NOT RUN"
            and type(wall) is dict
            and wall.get("actual_reference_processes_started") == 0
            and wall.get("actual_candidate_processes_started") == 0
            and wall.get("holdout") == "NOT OPENED",
            "preserve the actual historical independent V2 reference freeze")
    appended = receipt.get("appended_corrected_zig_matching")
    pids = receipt.get("actual_distinct_process_ids")
    archive = receipt.get("archive")
    require(receipt.get("schema")
            == "rebar-owned-callable-introspection-reference-v2-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("version") == 2
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means")
            == "EVIDENCE PUBLICATION ONLY"
            and receipt.get("source_sha256") == REFERENCE["source"][1]
            and receipt.get("protocol_sha256") == REFERENCE["protocol"][1]
            and receipt.get("contract_sha256") == REFERENCE["contract"][1]
            and receipt.get("frozen_v1_contract_sha256")
            == REFERENCE["supplement"][1]
            and receipt.get("matrix_sha256") == SUPPLEMENT_MATRIX_SHA256
            and receipt.get("original_case_denominator") == CASE_COUNT
            and receipt.get("original_suite_count") == SUITE_COUNT
            and receipt.get("original_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and receipt.get("additional_case_count") == SUPPLEMENT_CASE_COUNT
            and receipt.get("additional_cases_included_in_original_denominator")
            is False
            and receipt.get("reference_status") == "PASS"
            and receipt.get("reference_failure_count") == 0
            and receipt.get("actual_reference_processes_started")
            == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and type(pids) is list and pids == [81, 82]
            and len(set(pids)) == SUPPLEMENT_REFERENCE_PROCESS_COUNT
            and receipt.get("candidate_introspection") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("minimum_evidence_owner_count_after_publication")
            == PREVIOUS_EVIDENCE_OWNER_COUNT
            and receipt.get("minimum_history_reference_count_after_publication")
            == PREVIOUS_AUTHENTICATED_REFERENCE_COUNT
            and type(appended) is dict
            and appended.get("candidate_status") == "FAIL"
            and appended.get("semantic_mismatch_count") == 1764
            and appended.get("verified_passing_case_count") == 3711
            and appended.get("matching_archive_opened") is False
            and appended.get("matching_archive_decompressed") is False
            and type(archive) is dict
            and archive.get("path")
            == "oracle/phase1/evidence/callable-introspection-reference-v2-cpython-3.14.6.json.gz"
            and archive.get("sha256")
            == "7875f249a6cec7910e31800566ef5ccb1ee7398a29a403f307c5de88e647736c"
            and archive.get("bytes") == 8538
            and archive.get("mode") == "0600"
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True
            and receipt.get("source_build_archives_decompressed") == 0
            and receipt.get("matching_archives_opened") == 0
            and receipt.get("final_cases_read") == 0
            and receipt.get("holdout_cases_read") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("winner_selected") is False,
            "authenticate both actual passing 50-case reference processes "
            "from the small real receipt without opening any archive")
    return {"reference_status": "PASS",
            "case_count": SUPPLEMENT_CASE_COUNT,
            "reference_failure_count": 0,
            "actual_reference_process_count":
                SUPPLEMENT_REFERENCE_PROCESS_COUNT,
            "actual_reference_process_ids": list(pids),
            "candidate_status": "NOT RUN",
            "candidate_cases_executed": 0,
            "included_in_original_case_denominator": False,
            "receipt_sha256": REFERENCE["receipt"][1],
            "matching_archive_opened": False,
            "reference_archive_opened": False}



def same_published_owner(value: Any,
                         expected: tuple[str, str, int]) -> bool:
    """Compare only separately authenticated, digest-addressed owner facts."""
    if type(value) is not dict:
        return False
    path = value.get("path", value.get("relative"))
    count = value.get("bytes", value.get("size_bytes"))
    return (path == expected[0] and value.get("sha256") == expected[1]
            and count == expected[2])


def authenticate_corrected_candidate_reference(
        receipt: Any, reference_contract: Any,
        falsification: Any, producer_contract: Any) -> dict[str, Any]:
    """Authenticate actual PASS evidence without opening the reference archive."""
    require(type(receipt) is dict and type(reference_contract) is dict
            and type(falsification) is dict
            and type(producer_contract) is dict,
            "require the exact corrected two-reference and V4 producer owners")
    original = reference_contract.get("original_p0")
    public = reference_contract.get("original_public_suite")
    planned = reference_contract.get("prospective_correction")
    source_boundary = reference_contract.get("source_only_boundaries")
    require(reference_contract.get("schema")
            == "rebar-phase1-owned-public-type-reference-context-v1-frozen-contract"
            and reference_contract.get("version") == 1
            and reference_contract.get("status")
            == "SOURCE FROZEN; CORRECTED TWO-REFERENCE BASELINE NOT RUN"
            and same_published_owner(reference_contract.get("goal"),
                                     IMMUTABLE_GOAL["goal"])
            and reference_contract.get("source", {}).get("path")
            == CORRECTED_REFERENCE["source"][0]
            and reference_contract.get("source", {}).get("sha256")
            == CORRECTED_REFERENCE["source"][1]
            and reference_contract.get("protocol", {}).get("path")
            == CORRECTED_REFERENCE["protocol"][0]
            and reference_contract.get("protocol", {}).get("sha256")
            == CORRECTED_REFERENCE["protocol"][1]
            and type(original) is dict
            and original.get("case_execution_denominator") == CASE_COUNT
            and original.get("suite_count") == SUITE_COUNT
            and original.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and original.get("cases_removed") == 0
            and original.get("new_private_waivers") == 0
            and original.get("denominator_changed") is False
            and type(public) is dict
            and public.get("suite") == "public_types_v1"
            and public.get("case_count") == CORRECTED_REFERENCE_CASE_COUNT
            and public.get("matrix_sha256") == CORRECTED_REFERENCE_MATRIX_SHA256
            and public.get("published_seed_decimal") == "6077977430793212465"
            and type(public.get("historical_baseline")) is dict
            and public["historical_baseline"].get("full_vector_sha256")
            == HISTORICAL_FULL_PUBLIC_RECORDS_SHA256
            and public["historical_baseline"].get("status")
            == "FALSIFIED FOR CANDIDATE-FACING EXECUTION CONTEXT"
            and type(planned) is dict and planned.get("status") == "NOT RUN"
            and planned.get("required_actual_distinct_reference_process_count")
            == 2
            and planned.get("preserve_all_96_original_case_ids") is True
            and planned.get("preserve_full_original_matrix") is True
            and planned.get("reference_records_must_agree") is True
            and planned.get("load_any_candidate") is False
            and type(source_boundary) is dict
            and source_boundary.get("archive_decompressions") == 0
            and source_boundary.get("candidate_imports") == 0
            and source_boundary.get("candidate_processes_started") == 0
            and source_boundary.get("corrected_reference_workers_started") == 0
            and source_boundary.get("holdout") == "NOT OPENED",
            "separate the earlier NOT RUN source freeze from the real PASS receipt")
    archive = receipt.get("archive")
    pids = receipt.get("actual_distinct_reference_process_ids")
    require(receipt.get("schema")
            == "rebar-phase1-owned-public-type-reference-context-v1"
               "-durable-publication-receipt"
            and receipt.get("version") == 1
            and receipt.get("status") == "PASS"
            and receipt.get("reference_status") == "PASS"
            and receipt.get("publication_status") == "PASS"
            and receipt.get("publication_pass_means") == "DURABLE PUBLICATION ONLY"
            and receipt.get("source_sha256") == CORRECTED_REFERENCE["source"][1]
            and receipt.get("protocol_sha256")
            == CORRECTED_REFERENCE["protocol"][1]
            and receipt.get("contract_sha256")
            == CORRECTED_REFERENCE["contract"][1]
            and receipt.get("matrix_sha256")
            == CORRECTED_REFERENCE_MATRIX_SHA256
            and receipt.get("original_case_execution_denominator") == CASE_COUNT
            and receipt.get("public_case_count_per_reference")
            == CORRECTED_REFERENCE_CASE_COUNT
            and receipt.get("attempted_reference_worker_count") == 2
            and receipt.get("actual_reference_worker_count") == 2
            and receipt.get("actual_started_reference_worker_count") == 2
            and receipt.get("completed_reference_worker_count") == 2
            and receipt.get("validated_reference_worker_count") == 2
            and type(pids) is list and pids == list(CORRECTED_REFERENCE_PIDS)
            and len(set(pids)) == 2
            and receipt.get("full_reference_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and receipt.get("cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and receipt.get("uncompressed_sha256")
            == CORRECTED_REFERENCE_REPORT_SHA256
            and receipt.get("uncompressed_bytes")
            == CORRECTED_REFERENCE_REPORT_BYTES
            and receipt.get("gzip_mtime") == 0
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_workers_started") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and same_published_owner(archive, CORRECTED_REFERENCE["archive"])
            and archive.get("device") == 2064
            and archive.get("inode") == 524768
            and archive.get("mode") == 0o600
            and archive.get("nlink") == 1
            and archive.get("exclusive_creation") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and archive.get("same_inode_readback_verified") is True,
            "authenticate both actual corrected Python references from their "
            "small PASS receipt without opening the archive")
    replay = falsification.get("actual_replay")
    failing = falsification.get("falsifying_cases")
    affected = falsification.get("original_oracle")
    interpretation = falsification.get("interpretation")
    require(falsification.get("schema")
            == "rebar-public-type-candidate-context-falsification-v1"
            and falsification.get("version") == 1
            and falsification.get("status") == "FALSIFIED"
            and falsification.get("candidate_facing_self_oracle_status") == "FAIL"
            and type(failing) is dict
            and failing.get("cohort") == "cache-pattern-type-separation"
            and failing.get("case_count") == CORRECTED_REFERENCE_CACHE_CASE_COUNT
            and failing.get("text_subclass_case_count") == 48
            and failing.get("bytes_subclass_case_count") == 48
            and failing.get("case_ids_sha256")
            == CORRECTED_REFERENCE_CACHE_CASE_IDS_SHA256
            and failing.get("exact_case_matrix_sha256")
            == CORRECTED_REFERENCE_CACHE_MATRIX_SHA256
            and failing.get("published_script_context_records_sha256")
            == HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256
            and failing.get("actual_named_context_stdlib_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and failing.get("published_script_context_module") == "__main__"
            and failing.get("actual_candidate_facing_module")
            == "tools.independent_public_type_identity_serialization_v1"
            and type(affected) is dict
            and affected.get("case_execution_denominator") == CASE_COUNT
            and affected.get("suite_count") == SUITE_COUNT
            and affected.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and affected.get("affected_suite") == "public_types_v1"
            and affected.get("affected_suite_case_count")
            == CORRECTED_REFERENCE_CASE_COUNT
            and affected.get("original_cases_removed") == 0
            and affected.get("additional_private_waivers") == 0
            and affected.get("case_denominator_changed") is False
            and type(replay) is dict
            and replay.get("candidate_import_count") == 0
            and replay.get("candidate_workers_started") == 0
            and replay.get("matching_archives_opened") == 0
            and replay.get("holdout_opened") is False
            and type(interpretation) is dict
            and interpretation.get("candidate_facing_python_against_python_agrees")
            is False
            and interpretation.get("historical_rust_records_recomputed_or_deleted")
            is False
            and interpretation.get("c_pattern_equality_failure_waived") is False
            and interpretation.get("zig_pattern_equality_failure_waived") is False
            and interpretation.get("same_context_reference_correction_status")
            == "NOT RUN",
            "preserve the real 96-case historic falsification without "
            "mistaking its old status for the corrected reference")
    phase_one = producer_contract.get("phase_one")
    producer_reference = producer_contract.get(
        "corrected_candidate_context_public_type_reference")
    suites = producer_contract.get("suites")
    families = producer_contract.get("families")
    require(producer_contract.get("schema")
            == "rebar-owned-six-family-original-p0-producer-v4-source-freeze"
            and producer_contract.get("version") == 4
            and producer_contract.get("status")
            == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
            and producer_contract.get("family_count") == 6
            and producer_contract.get("suite_count") == SUITE_COUNT
            and producer_contract.get("case_execution_denominator") == CASE_COUNT
            and type(phase_one) is dict
            and phase_one.get("suite_count") == SUITE_COUNT
            and phase_one.get("case_execution_denominator") == CASE_COUNT
            and phase_one.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and phase_one.get("supplemental_cases_added") is False
            and type(suites) is list and len(suites) == SUITE_COUNT
            and [(item.get("id"), item.get("case_execution_count"))
                 for item in suites if type(item) is dict] == list(SUITES)
            and type(families) is list and len(families) == 6
            and [item.get("family") for item in families if type(item) is dict]
            == ["rust", "c", "zig", "cpp", "go", "fortran"]
            and type(producer_reference) is dict
            and producer_reference.get("status") == "PASS"
            and producer_reference.get("reference_status") == "PASS"
            and producer_reference.get("publication_status") == "PASS"
            and producer_reference.get("publication_pass_means")
            == "DURABLE PUBLICATION ONLY"
            and producer_reference.get("candidate_facing_reference") is True
            and producer_reference.get("case_count")
            == CORRECTED_REFERENCE_CASE_COUNT
            and producer_reference.get("matrix_sha256")
            == CORRECTED_REFERENCE_MATRIX_SHA256
            and producer_reference.get("records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and producer_reference.get("historical_reference_records_sha256")
            == HISTORICAL_FULL_PUBLIC_RECORDS_SHA256
            and producer_reference.get("reference_pids")
            == list(CORRECTED_REFERENCE_PIDS)
            and producer_reference.get("actual_reference_worker_count") == 2
            and producer_reference.get("attempted_reference_worker_count") == 2
            and producer_reference.get("completed_reference_worker_count") == 2
            and producer_reference.get("validated_reference_worker_count") == 2
            and producer_reference.get("cache_case_count")
            == CORRECTED_REFERENCE_CACHE_CASE_COUNT
            and producer_reference.get("cache_case_ids_sha256")
            == CORRECTED_REFERENCE_CACHE_CASE_IDS_SHA256
            and producer_reference.get("cache_matrix_sha256")
            == CORRECTED_REFERENCE_CACHE_MATRIX_SHA256
            and producer_reference.get("cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and producer_reference.get("candidate_run_starts_reference_processes")
            is False
            and producer_reference.get("candidate_run_uses_both_complete_reference_vectors")
            is True
            and producer_reference.get("c_pattern_equality_failure_waived")
            is False,
            "bind every Rust worker to the genuine corrected V4 six-family producer")
    owners = producer_reference.get("owners")
    require(type(owners) is dict,
            "retain all original independently corrected reference owners")
    for name, item in CORRECTED_REFERENCE.items():
        observed = owners.get(name)
        require(type(observed) is dict
                and observed.get("relative") == item[0]
                and observed.get("sha256") == item[1]
                and observed.get("size_bytes") == item[2],
                "reject a substituted corrected-reference owner: " + name)
    corrected_suite = suites[6]
    require(corrected_suite.get("id") == "public_types_v1"
            and corrected_suite.get("case_execution_count")
            == CORRECTED_REFERENCE_CASE_COUNT
            and corrected_suite.get("matrix_sha256")
            == CORRECTED_REFERENCE_MATRIX_SHA256
            and corrected_suite.get("reference_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256,
            "require all 6,912 original candidate-context records")
    actual_rust = families[0]
    original_rust_sources = actual_rust.get("sources")
    require(actual_rust.get("family") == FAMILY
            and actual_rust.get("module") == "candidates.rust_candidate"
            and actual_rust.get("adapter_relative")
            == "candidates/rust_candidate.py"
            and actual_rust.get("bridge_module") == "candidates._rust_bridge"
            and actual_rust.get("combined_native_engine_and_bridge") is False
            and actual_rust.get("owned_ctypes_allowed") is False
            and actual_rust.get("owned_source_count")
            == len(ORIGINAL_SOURCE_OWNERS)
            and type(original_rust_sources) is list
            and [(row.get("relative"), row.get("sha256"),
                  row.get("size_bytes"))
                 for row in original_rust_sources if type(row) is dict]
            == list(ORIGINAL_SOURCE_OWNERS),
            "reject an external package, borrowed engine, altered Rust family, "
            "or public wrapper in the corrected V4 case producer")
    return {
        "status": "PASS",
        "reference_status": "PASS",
        "publication_status": "PASS",
        "source_contract_reference_status":
            "NOT RUN; FROZEN BEFORE REAL RUN",
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_archive_sha256":
            CORRECTED_REFERENCE["archive"][1],
        "corrected_reference_archive_opened": False,
        "corrected_reference_archive_decompressed": False,
        "corrected_reference_archive_bytes_read": 0,
        "actual_reference_worker_count": 2,
        "actual_distinct_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "case_count_per_reference": CORRECTED_REFERENCE_CASE_COUNT,
        "total_observed_reference_case_count":
            2 * CORRECTED_REFERENCE_CASE_COUNT,
        "full_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "cache_case_count_per_reference":
            CORRECTED_REFERENCE_CACHE_CASE_COUNT,
        "cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "historical_script_context_records_sha256":
            HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
        "historical_full_script_context_records_sha256":
            HISTORICAL_FULL_PUBLIC_RECORDS_SHA256,
        "historical_falsification_status": "FALSIFIED",
        "historical_falsification_evidence_sha256":
            CORRECTED_REFERENCE["falsification"][1],
        "historical_falsification_deleted": False,
        "original_cases_removed": 0,
        "additional_private_waivers": 0,
        "c_pattern_equality_failure_waived": False,
        "corrected_original_producer_source_sha256": PRODUCER["source"][1],
        "corrected_original_producer_protocol_sha256":
            PRODUCER["protocol"][1],
        "corrected_original_producer_contract_sha256":
            PRODUCER["contract"][1],
        "candidate_run_uses_both_complete_reference_vectors": True,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
    }



def authenticate_published_v13_build_receipt(
        receipt: Any) -> dict[str, Any]:
    """Bind the genuine first-party build without opening its archive."""
    require(type(receipt) is dict,
            "require the independent small published Rust V13 build receipt")
    publication = receipt.get("archive_publication")
    fsync = receipt.get("archive_directory_fsync")
    require(receipt.get("schema")
            == "rebar-phase2-owned-rust-pattern-repr-source-build-v13"
               "-durable-publication-receipt"
            and receipt.get("status") == "PASS"
            and receipt.get("build_status") == "PASS"
            and receipt.get("family") == FAMILY
            and receipt.get("label") == LABEL
            and receipt.get("source_sha256") == BUILD["source"][1]
            and receipt.get("protocol_sha256") == BUILD["protocol"][1]
            and receipt.get("contract_sha256") == BUILD["contract"][1]
            and receipt.get("archive_relative") == BUILD["archive"][0]
            and receipt.get("archive_sha256") == BUILD["archive"][1]
            and receipt.get("archive_bytes") == BUILD["archive"][2]
            and receipt.get("uncompressed_bytes") == V13_PLAIN_BYTES
            and receipt.get("uncompressed_sha256") == V13_PLAIN_SHA256
            and receipt.get("expected_actual_compiler_process_count") == 28
            and receipt.get("actual_compiler_process_count") == 28
            and receipt.get("bridge_derived_sha256") == BRIDGE_SOURCE_SHA256
            and receipt.get("public_derived_sha256") == CORRECTED_PUBLIC_SHA256
            and receipt.get("bridge_overlay_apply_count") == 2
            and receipt.get("corrected_public_overlay_apply_count") == 2
            and receipt.get("candidate_correctness") == "NOT MEASURED"
            and receipt.get("candidate_imports") == 0
            and receipt.get("candidate_processes_started") == 0
            and receipt.get("candidate_qualified") is False
            and receipt.get("native_libraries_loaded") == 0
            and receipt.get("hidden_cases_read") == 0
            and receipt.get("clock_samples") == 0
            and receipt.get("timing_trials_run") == 0
            and receipt.get("holdout") == "NOT OPENED"
            and receipt.get("performance") == "NOT MEASURED"
            and receipt.get("memory") == "NOT MEASURED"
            and receipt.get("winner_selected") is False
            and type(publication) is dict
            and publication.get("path") == str(ROOT / BUILD["archive"][0])
            and publication.get("sha256") == BUILD["archive"][1]
            and publication.get("bytes") == BUILD["archive"][2]
            and publication.get("device") == 2064
            and publication.get("inode") == 524714
            and publication.get("exclusive_creation") is True
            and publication.get("file_fsync_completed") is True
            and publication.get("same_inode_readback_verified") is True
            and type(fsync) is dict and fsync.get("completed") is True,
            "reject a substituted, partial, imported, external, unbuilt, "
            "or falsely qualification-labelled Rust V13 receipt")
    return {
        "status": "PASS",
        "build_status": "PASS",
        "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "archive_sha256": BUILD["archive"][1],
        "receipt_sha256": BUILD["receipt"][1],
        "actual_process_count": 28,
        "corrected_public_overlay_apply_count": 2,
        "bridge_overlay_apply_count": 2,
        "candidate_matching": "NOT RUN",
        "candidate_correctness": "NOT MEASURED",
        "candidate_qualified": False,
        "archive_bytes_read": 0,
        "archive_gzip_inflation_count": 0,
    }


def authenticate_preserved_v39(
        summary: Any, inputs: Any, producer_contract: Any,
        reference_receipt: Any, falsification: Any,
        build_receipt: Any) -> dict[str, Any]:
    """Fail closed against the final pushed graph and every corrected owner."""
    require(type(summary) is dict and type(inputs) is dict,
            "require both final independently pinned V39 graph documents")
    for value, expected_schema, qualified_field in (
        (summary, "rebar-candidate-current-overview-v39-summary",
         "qualified_candidate_count"),
        (inputs, "rebar-candidate-current-overview-v39-inputs",
         "candidate_qualified_count"),
    ):
        require(value.get("schema") == expected_schema
                and value.get("version") == 39
                and value.get("full_case_denominator") == CASE_COUNT
                and value.get("suite_count") == SUITE_COUNT
                and value.get("private_waiver_count")
                == PRIVATE_WAIVER_COUNT
                and value.get(qualified_field) == 0
                and value.get("candidate_case_producer_source_sha256")
                == PRODUCER["source"][1]
                and value.get("candidate_case_producer_protocol_sha256")
                == PRODUCER["protocol"][1]
                and value.get("candidate_case_producer_contract_sha256")
                == PRODUCER["contract"][1]
                and value.get("candidate_case_producer_status")
                == "FROZEN; CANDIDATE WORKERS STILL STALE"
                and value.get("candidate_case_producer_corrected_v4_status")
                == "SOURCE FROZEN; CANDIDATES NOT RUN"
                and value.get("candidate_facing_self_oracle_status") == "PASS"
                and value.get("phase_one_reference_gate_status") == "PASS"
                and value.get("same_context_reference_correction_status")
                == "PASS"
                and value.get("corrected_reference_status") == "PASS"
                and value.get("corrected_reference_publication_status") == "PASS"
                and value.get("corrected_reference_full_records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and value.get("corrected_reference_cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and value.get("corrected_reference_actual_worker_count") == 2
                and value.get("corrected_reference_case_count_per_worker")
                == CORRECTED_REFERENCE_CASE_COUNT
                and value.get("corrected_reference_cache_cases_per_worker")
                == CORRECTED_REFERENCE_CACHE_CASE_COUNT
                and value.get("corrected_reference_process_ids")
                == list(CORRECTED_REFERENCE_PIDS)
                and value.get("actual_candidate_facing_reference_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and value.get("additional_private_waivers") == 0
                and value.get("authenticated_evidence_owner_lower_bound")
                == ACTUAL_EVIDENCE_OWNER_COUNT
                and value.get("authenticated_history_reference_lower_bound")
                == ACTUAL_AUTHENTICATED_REFERENCE_COUNT
                and value.get("all_candidate_matching_blocked") is True
                and value.get("required_corrected_candidate_runner_versions")
                == ["V8", "V10", "RUST V6"]
                and value.get("stale_candidate_worker_versions")
                == ["V7", "V9", "RUST V5"]
                and value.get("additional_signature_frozen_case_count")
                == SUPPLEMENT_CASE_COUNT
                and value.get("additional_signature_reference_status") == "PASS"
                and value.get("additional_signature_reference_cases_executed")
                == SUPPLEMENT_CASE_COUNT
                and value.get("additional_signature_candidate_status")
                == "NOT RUN"
                and value.get("additional_signature_candidate_cases_executed")
                == 0
                and value.get("matching_archive_gzip_inflation_count") == 0
                and value.get("candidate_matching_archives_opened_by_graph") == 0
                and value.get("hidden_cases_read") == 0
                and value.get("clock_samples") == 0
                and value.get("timing_trials_run") == 0
                and value.get("performance") == "NOT MEASURED"
                and value.get("final_holdout_opened") is False
                and value.get("winner_selected") is False,
                "reject a stale, incomplete, misleading, or uncorrected "
                + expected_schema)
    require(summary.get("status") == "PASS"
            and same_published_owner(summary.get("source"), V39["source"])
            and same_published_owner(summary.get("inputs"), V39["inputs"])
            and same_published_owner(summary.get("svg"), V39["svg"])
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_receipt_status") == "PASS"
            and summary.get("rust_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and summary.get("rust_original_campaign_case_execution_denominator")
            == CASE_COUNT
            and summary.get("rust_original_campaign_candidate_worker_count")
            == SUITE_COUNT
            and summary.get("rust_original_campaign_completed_suite_count")
            == SUITE_COUNT
            and summary.get("rust_original_campaign_semantic_mismatch_count")
            == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count")
            == 8965
            and summary.get("rust_original_campaign_infrastructure_failure_count")
            == 0
            and summary.get("rust_original_campaign_recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and summary.get("rust_original_campaign_all_four_original_targets_restored")
            is True
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count")
            == 1230
            and summary.get("c_original_campaign_verified_passing_case_count")
            == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count")
            == 1764
            and summary.get("zig_original_campaign_verified_passing_case_count")
            == 3711
            and summary.get("actual_candidate_workers_started_by_graph") == 0
            and summary.get("actual_reference_workers_started_by_graph") == 0
            and summary.get("actual_candidate_imports") == 0
            and summary.get("actual_native_activations") == 0
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED",
            "preserve the exact pushed V39 headline and all genuine Rust, C, "
            "and Zig losses without inventing a qualified candidate")
    proof = summary.get("corrected_candidate_producer_v4")
    require(type(proof) is dict
            and proof.get("schema")
            == "rebar-candidate-current-overview-v39"
               "-authenticated-frozen-v4-producer"
            and proof.get("status") == "SOURCE FROZEN; CANDIDATES NOT RUN"
            and same_published_owner(proof.get("source"), PRODUCER["source"])
            and same_published_owner(proof.get("protocol"),
                                     PRODUCER["protocol"])
            and same_published_owner(proof.get("contract"),
                                     PRODUCER["contract"])
            and canonical(proof.get("complete_frozen_contract"))
            == canonical(producer_contract)
            and proof.get("candidate_workers_started") == 0
            and proof.get("reference_workers_started") == 0
            and proof.get("source_builds_started") == 0
            and proof.get("qualified_candidate_count") == 0
            and proof.get("holdout") == "NOT OPENED"
            and canonical(inputs.get("corrected_candidate_producer_v4"))
            == canonical(proof),
            "bind both current graph documents to the complete corrected "
            "V4 producer and no stale V3 worker")
    actual = summary.get("actual_corrected_two_reference")
    require(type(actual) is dict
            and actual.get("schema")
            == "rebar-candidate-current-overview-v39"
               "-authenticated-actual-two-reference"
            and actual.get("status") == "PASS"
            and actual.get("reference_status") == "PASS"
            and actual.get("publication_status") == "PASS"
            and actual.get("publication_pass_means")
            == "DURABLE PUBLICATION ONLY"
            and actual.get("source_sha256")
            == CORRECTED_REFERENCE["source"][1]
            and actual.get("protocol_sha256")
            == CORRECTED_REFERENCE["protocol"][1]
            and actual.get("contract_sha256")
            == CORRECTED_REFERENCE["contract"][1]
            and same_published_owner(actual.get("archive"),
                                     CORRECTED_REFERENCE["archive"])
            and same_published_owner(actual.get("receipt"),
                                     CORRECTED_REFERENCE["receipt"])
            and canonical(actual.get("complete_publication_receipt"))
            == canonical(reference_receipt)
            and actual.get("actual_distinct_reference_process_ids")
            == list(CORRECTED_REFERENCE_PIDS)
            and actual.get("attempted_reference_worker_count") == 2
            and actual.get("completed_reference_worker_count") == 2
            and actual.get("validated_reference_worker_count") == 2
            and actual.get("reference_case_count_per_worker")
            == CORRECTED_REFERENCE_CASE_COUNT
            and actual.get("total_observed_reference_case_count")
            == 2 * CORRECTED_REFERENCE_CASE_COUNT
            and actual.get("matrix_sha256")
            == CORRECTED_REFERENCE_MATRIX_SHA256
            and actual.get("full_reference_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and actual.get("cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and actual.get("historical_falsified_script_context_sha256")
            == HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256
            and actual.get("candidate_imports") == 0
            and actual.get("candidate_workers_started") == 0
            and actual.get("candidate_matching_archives_opened") == 0
            and actual.get("reference_workers_started_by_graph") == 0
            and actual.get("holdout") == "NOT OPENED"
            and canonical(inputs.get("actual_corrected_two_reference"))
            == canonical(actual),
            "authenticate both actual named-context reference roles and "
            "full receipt from the current graph")
    workers = actual.get("complete_worker_observations")
    require(type(workers) is list and len(workers) == 2,
            "retain summaries of both complete independent reference processes")
    for index, role in enumerate(("reference-a", "reference-b")):
        worker = workers[index]
        require(type(worker) is dict and worker.get("role") == role
                and worker.get("pid") == CORRECTED_REFERENCE_PIDS[index]
                and worker.get("status") == "PASS"
                and worker.get("case_count") == CORRECTED_REFERENCE_CASE_COUNT
                and worker.get("records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and worker.get("cache_case_count")
                == CORRECTED_REFERENCE_CACHE_CASE_COUNT
                and worker.get("cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and worker.get("candidate_import_count") == 0
                and worker.get("candidate_workers_started") == 0
                and worker.get("holdout") == "NOT OPENED"
                and type(worker.get("stdout_bytes")) is int
                and worker["stdout_bytes"] > 0
                and type(worker.get("stderr_bytes")) is int
                and worker["stderr_bytes"] == 0,
                "reject missing, reused, partial, or candidate-tainted "
                + role + " reference summary")
        checked_digest(worker.get("stdout_sha256"),
                       role + " full observed stdout")
        checked_digest(worker.get("stderr_sha256"),
                       role + " full observed stderr")
    history = summary.get("actual_reference_context_falsification")
    require(type(history) is dict
            and history.get("schema")
            == "rebar-candidate-current-overview-v37"
               "-authenticated-reference-context-falsification"
            and history.get("status") == "FALSIFIED"
            and history.get("candidate_facing_self_oracle_status") == "FAIL"
            and history.get("falsifying_case_count")
            == CORRECTED_REFERENCE_CACHE_CASE_COUNT
            and history.get("published_script_context_records_sha256")
            == HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256
            and history.get("actual_candidate_facing_reference_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and same_published_owner(history.get("evidence"),
                                     CORRECTED_REFERENCE["falsification"])
            and canonical(history.get("complete_falsification_record"))
            == canonical(falsification)
            and history.get("original_cases_removed") == 0
            and history.get("additional_private_waivers") == 0
            and history.get("full_original_case_execution_denominator")
            == CASE_COUNT
            and history.get("original_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and canonical(inputs.get("actual_reference_context_falsification"))
            == canonical(history),
            "preserve and authenticate the original failed 96-case self-oracle")
    built = summary.get("actual_rust_v13_corrected_source_build")
    require(type(built) is dict
            and built.get("schema")
            == "rebar-candidate-current-overview-v36"
               "-authenticated-corrected-rust-v13-source-build"
            and built.get("status") == "PASS"
            and built.get("build_status") == "PASS"
            and same_published_owner(built.get("source"), BUILD["source"])
            and same_published_owner(built.get("protocol"), BUILD["protocol"])
            and same_published_owner(built.get("contract"), BUILD["contract"])
            and same_published_owner(built.get("archive"), BUILD["archive"])
            and same_published_owner(built.get("receipt"), BUILD["receipt"])
            and canonical(built.get("publication_receipt"))
            == canonical(build_receipt)
            and built.get("actual_compiler_process_count") == 28
            and built.get("actual_unique_compiler_process_count") == 28
            and built.get("actual_independent_phase_count") == 2
            and built.get("actual_source_owner_count_per_phase") == 9
            and built.get("actual_native_role_count") == 2
            and built.get("corrected_public_overlay_apply_count") == 2
            and built.get("bridge_overlay_apply_count") == 2
            and built.get("external_regex_native_dependency_count") == 0
            and built.get("cross_family_native_dependency_count") == 0
            and built.get("actual_candidate_imports") == 0
            and built.get("actual_candidate_processes_started") == 0
            and built.get("native_libraries_loaded") == 0
            and built.get("new_rust_candidate_worker_count") == 0
            and built.get("new_rust_matching_test_status") == "NOT RUN"
            and built.get("candidate_correctness") == "NOT MEASURED"
            and built.get("candidate_qualified") is False
            and built.get("build_report_gzip_inflation_count") == 1
            and built.get("build_report_uncompressed_bytes_read")
            == V13_PLAIN_BYTES
            and built.get("build_report_uncompressed_sha256")
            == V13_PLAIN_SHA256
            and built.get("matching_archive_gzip_inflation_count") == 0
            and built.get("matching_archives_opened_by_graph") == 0
            and built.get("hidden_cases_read") == 0
            and built.get("clock_samples") == 0
            and built.get("holdout") == "NOT OPENED"
            and built.get("performance") == "NOT MEASURED"
            and built.get("undefined_behavior") == "NOT MEASURED"
            and canonical(inputs.get("actual_rust_v13_corrected_source_build"))
            == canonical(built),
            "require the genuine first-party 28-process Rust build without "
            "calling it candidate correctness")
    return {
        "status": "PASS",
        "overview_version": 39,
        "owners": grouped_owners(V39),
        "corrected_producer_source_sha256": PRODUCER["source"][1],
        "corrected_producer_protocol_sha256": PRODUCER["protocol"][1],
        "corrected_producer_contract_sha256": PRODUCER["contract"][1],
        "same_context_reference_correction_status": "PASS",
        "actual_reference_status": "PASS",
        "actual_reference_publication_status": "PASS",
        "actual_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "actual_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "actual_reference_process_ids": list(CORRECTED_REFERENCE_PIDS),
        "historical_falsification_status": "FALSIFIED",
        "actual_build_status": "PASS",
        "actual_v13_compiler_process_count": 28,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 1764,
        "authenticated_evidence_owner_lower_bound":
            ACTUAL_EVIDENCE_OWNER_COUNT,
        "authenticated_history_reference_lower_bound":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "all_candidate_matching_blocked": True,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
    }


def authenticate_current_v40(
        summary: Any, inputs: Any, producer_contract: Any,
        reference_receipt: Any, falsification: Any,
        build_receipt: Any, zig_contract: Any) -> dict[str, Any]:
    """Fail closed against the final pushed graph and every corrected owner."""
    require(type(summary) is dict and type(inputs) is dict,
            "require both final independently pinned V39 graph documents")
    for value, expected_schema, qualified_field in (
        (summary, "rebar-candidate-current-overview-v40-summary",
         "qualified_candidate_count"),
        (inputs, "rebar-candidate-current-overview-v40-inputs",
         "candidate_qualified_count"),
    ):
        require(value.get("schema") == expected_schema
                and value.get("version") == 40
                and value.get("full_case_denominator") == CASE_COUNT
                and value.get("suite_count") == SUITE_COUNT
                and value.get("private_waiver_count")
                == PRIVATE_WAIVER_COUNT
                and value.get(qualified_field) == 0
                and value.get("candidate_case_producer_source_sha256")
                == PRODUCER["source"][1]
                and value.get("candidate_case_producer_protocol_sha256")
                == PRODUCER["protocol"][1]
                and value.get("candidate_case_producer_contract_sha256")
                == PRODUCER["contract"][1]
                and value.get("candidate_case_producer_status")
                == "FROZEN; CANDIDATE WORKERS STILL STALE"
                and value.get("candidate_case_producer_corrected_v4_status")
                == "SOURCE FROZEN; CANDIDATES NOT RUN"
                and value.get("candidate_facing_self_oracle_status") == "PASS"
                and value.get("phase_one_reference_gate_status") == "PASS"
                and value.get("same_context_reference_correction_status")
                == "PASS"
                and value.get("corrected_reference_status") == "PASS"
                and value.get("corrected_reference_publication_status") == "PASS"
                and value.get("corrected_reference_full_records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and value.get("corrected_reference_cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and value.get("corrected_reference_actual_worker_count") == 2
                and value.get("corrected_reference_case_count_per_worker")
                == CORRECTED_REFERENCE_CASE_COUNT
                and value.get("corrected_reference_cache_cases_per_worker")
                == CORRECTED_REFERENCE_CACHE_CASE_COUNT
                and value.get("corrected_reference_process_ids")
                == list(CORRECTED_REFERENCE_PIDS)
                and value.get("actual_candidate_facing_reference_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and value.get("additional_private_waivers") == 0
                and value.get("authenticated_evidence_owner_lower_bound")
                == ACTUAL_EVIDENCE_OWNER_COUNT
                and value.get("authenticated_history_reference_lower_bound")
                == ACTUAL_AUTHENTICATED_REFERENCE_COUNT
                and value.get("all_candidate_matching_blocked") is True
                and value.get("required_corrected_candidate_runner_versions")
                == ["V8", "V10", "RUST V6"]
                and value.get("stale_candidate_worker_versions")
                == ["V7", "V9", "RUST V5"]
                and value.get("additional_signature_frozen_case_count")
                == SUPPLEMENT_CASE_COUNT
                and value.get("additional_signature_reference_status") == "PASS"
                and value.get("additional_signature_reference_cases_executed")
                == SUPPLEMENT_CASE_COUNT
                and value.get("additional_signature_candidate_status")
                == "NOT RUN"
                and value.get("additional_signature_candidate_cases_executed")
                == 0
                and value.get("matching_archive_gzip_inflation_count") == 0
                and value.get("candidate_matching_archives_opened_by_graph") == 0
                and value.get("hidden_cases_read") == 0
                and value.get("clock_samples") == 0
                and value.get("timing_trials_run") == 0
                and value.get("performance") == "NOT MEASURED"
                and value.get("final_holdout_opened") is False
                and value.get("winner_selected") is False,
                "reject a stale, incomplete, misleading, or uncorrected "
                + expected_schema)
    require(summary.get("status") == "PASS"
            and same_published_owner(summary.get("source"), V40["source"])
            and same_published_owner(summary.get("inputs"), V40["inputs"])
            and same_published_owner(summary.get("svg"), V40["svg"])
            and summary.get("rust_original_campaign_status") == "FAIL"
            and summary.get("rust_original_campaign_receipt_status") == "PASS"
            and summary.get("rust_original_campaign_receipt_pass_means")
            == "DURABLE FAILURE PUBLICATION ONLY"
            and summary.get("rust_original_campaign_case_execution_denominator")
            == CASE_COUNT
            and summary.get("rust_original_campaign_candidate_worker_count")
            == SUITE_COUNT
            and summary.get("rust_original_campaign_completed_suite_count")
            == SUITE_COUNT
            and summary.get("rust_original_campaign_semantic_mismatch_count")
            == 1036
            and summary.get("rust_original_campaign_verified_passing_case_count")
            == 8965
            and summary.get("rust_original_campaign_infrastructure_failure_count")
            == 0
            and summary.get("rust_original_campaign_recovery_journal_sha256")
            == HISTORICAL_RUST_JOURNAL
            and summary.get("rust_original_campaign_all_four_original_targets_restored")
            is True
            and summary.get("c_original_campaign_status") == "FAIL"
            and summary.get("c_original_campaign_semantic_mismatch_count")
            == 1230
            and summary.get("c_original_campaign_verified_passing_case_count")
            == 7325
            and summary.get("zig_original_campaign_status") == "FAIL"
            and summary.get("zig_original_campaign_semantic_mismatch_count")
            == 1764
            and summary.get("zig_original_campaign_verified_passing_case_count")
            == 3711
            and summary.get("actual_candidate_workers_started_by_graph") == 0
            and summary.get("actual_reference_workers_started_by_graph") == 0
            and summary.get("actual_candidate_imports") == 0
            and summary.get("actual_native_activations") == 0
            and summary.get("memory") == "NOT MEASURED"
            and summary.get("undefined_behavior") == "NOT MEASURED",
            "preserve the exact pushed V40 headline and all genuine Rust, C, "
            "and Zig losses without inventing a qualified candidate")
    previous = summary.get("previous_overview")
    require(type(previous) is dict
            and canonical(previous) == canonical(grouped_owners(V39))
            and canonical(inputs.get("previous_overview"))
            == canonical(previous),
            "authenticate the exact immutable V39 graph as V40 history")
    proof = summary.get("corrected_candidate_producer_v4")
    require(type(proof) is dict
            and proof.get("schema")
            == "rebar-candidate-current-overview-v39"
               "-authenticated-frozen-v4-producer"
            and proof.get("status") == "SOURCE FROZEN; CANDIDATES NOT RUN"
            and same_published_owner(proof.get("source"), PRODUCER["source"])
            and same_published_owner(proof.get("protocol"),
                                     PRODUCER["protocol"])
            and same_published_owner(proof.get("contract"),
                                     PRODUCER["contract"])
            and canonical(proof.get("complete_frozen_contract"))
            == canonical(producer_contract)
            and proof.get("candidate_workers_started") == 0
            and proof.get("reference_workers_started") == 0
            and proof.get("source_builds_started") == 0
            and proof.get("qualified_candidate_count") == 0
            and proof.get("holdout") == "NOT OPENED"
            and canonical(inputs.get("corrected_candidate_producer_v4"))
            == canonical(proof),
            "bind both current graph documents to the complete corrected "
            "V4 producer and no stale V3 worker")
    actual = summary.get("actual_corrected_two_reference")
    require(type(actual) is dict
            and actual.get("schema")
            == "rebar-candidate-current-overview-v39"
               "-authenticated-actual-two-reference"
            and actual.get("status") == "PASS"
            and actual.get("reference_status") == "PASS"
            and actual.get("publication_status") == "PASS"
            and actual.get("publication_pass_means")
            == "DURABLE PUBLICATION ONLY"
            and actual.get("source_sha256")
            == CORRECTED_REFERENCE["source"][1]
            and actual.get("protocol_sha256")
            == CORRECTED_REFERENCE["protocol"][1]
            and actual.get("contract_sha256")
            == CORRECTED_REFERENCE["contract"][1]
            and same_published_owner(actual.get("archive"),
                                     CORRECTED_REFERENCE["archive"])
            and same_published_owner(actual.get("receipt"),
                                     CORRECTED_REFERENCE["receipt"])
            and canonical(actual.get("complete_publication_receipt"))
            == canonical(reference_receipt)
            and actual.get("actual_distinct_reference_process_ids")
            == list(CORRECTED_REFERENCE_PIDS)
            and actual.get("attempted_reference_worker_count") == 2
            and actual.get("completed_reference_worker_count") == 2
            and actual.get("validated_reference_worker_count") == 2
            and actual.get("reference_case_count_per_worker")
            == CORRECTED_REFERENCE_CASE_COUNT
            and actual.get("total_observed_reference_case_count")
            == 2 * CORRECTED_REFERENCE_CASE_COUNT
            and actual.get("matrix_sha256")
            == CORRECTED_REFERENCE_MATRIX_SHA256
            and actual.get("full_reference_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and actual.get("cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and actual.get("historical_falsified_script_context_sha256")
            == HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256
            and actual.get("candidate_imports") == 0
            and actual.get("candidate_workers_started") == 0
            and actual.get("candidate_matching_archives_opened") == 0
            and actual.get("reference_workers_started_by_graph") == 0
            and actual.get("holdout") == "NOT OPENED"
            and canonical(inputs.get("actual_corrected_two_reference"))
            == canonical(actual),
            "authenticate both actual named-context reference roles and "
            "full receipt from the current graph")
    workers = actual.get("complete_worker_observations")
    require(type(workers) is list and len(workers) == 2,
            "retain summaries of both complete independent reference processes")
    for index, role in enumerate(("reference-a", "reference-b")):
        worker = workers[index]
        require(type(worker) is dict and worker.get("role") == role
                and worker.get("pid") == CORRECTED_REFERENCE_PIDS[index]
                and worker.get("status") == "PASS"
                and worker.get("case_count") == CORRECTED_REFERENCE_CASE_COUNT
                and worker.get("records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and worker.get("cache_case_count")
                == CORRECTED_REFERENCE_CACHE_CASE_COUNT
                and worker.get("cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and worker.get("candidate_import_count") == 0
                and worker.get("candidate_workers_started") == 0
                and worker.get("holdout") == "NOT OPENED"
                and type(worker.get("stdout_bytes")) is int
                and worker["stdout_bytes"] > 0
                and type(worker.get("stderr_bytes")) is int
                and worker["stderr_bytes"] == 0,
                "reject missing, reused, partial, or candidate-tainted "
                + role + " reference summary")
        checked_digest(worker.get("stdout_sha256"),
                       role + " full observed stdout")
        checked_digest(worker.get("stderr_sha256"),
                       role + " full observed stderr")
    history = summary.get("actual_reference_context_falsification")
    require(type(history) is dict
            and history.get("schema")
            == "rebar-candidate-current-overview-v37"
               "-authenticated-reference-context-falsification"
            and history.get("status") == "FALSIFIED"
            and history.get("candidate_facing_self_oracle_status") == "FAIL"
            and history.get("falsifying_case_count")
            == CORRECTED_REFERENCE_CACHE_CASE_COUNT
            and history.get("published_script_context_records_sha256")
            == HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256
            and history.get("actual_candidate_facing_reference_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and same_published_owner(history.get("evidence"),
                                     CORRECTED_REFERENCE["falsification"])
            and canonical(history.get("complete_falsification_record"))
            == canonical(falsification)
            and history.get("original_cases_removed") == 0
            and history.get("additional_private_waivers") == 0
            and history.get("full_original_case_execution_denominator")
            == CASE_COUNT
            and history.get("original_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and canonical(inputs.get("actual_reference_context_falsification"))
            == canonical(history),
            "preserve and authenticate the original failed 96-case self-oracle")
    built = summary.get("actual_rust_v13_corrected_source_build")
    require(type(built) is dict
            and built.get("schema")
            == "rebar-candidate-current-overview-v36"
               "-authenticated-corrected-rust-v13-source-build"
            and built.get("status") == "PASS"
            and built.get("build_status") == "PASS"
            and same_published_owner(built.get("source"), BUILD["source"])
            and same_published_owner(built.get("protocol"), BUILD["protocol"])
            and same_published_owner(built.get("contract"), BUILD["contract"])
            and same_published_owner(built.get("archive"), BUILD["archive"])
            and same_published_owner(built.get("receipt"), BUILD["receipt"])
            and canonical(built.get("publication_receipt"))
            == canonical(build_receipt)
            and built.get("actual_compiler_process_count") == 28
            and built.get("actual_unique_compiler_process_count") == 28
            and built.get("actual_independent_phase_count") == 2
            and built.get("actual_source_owner_count_per_phase") == 9
            and built.get("actual_native_role_count") == 2
            and built.get("corrected_public_overlay_apply_count") == 2
            and built.get("bridge_overlay_apply_count") == 2
            and built.get("external_regex_native_dependency_count") == 0
            and built.get("cross_family_native_dependency_count") == 0
            and built.get("actual_candidate_imports") == 0
            and built.get("actual_candidate_processes_started") == 0
            and built.get("native_libraries_loaded") == 0
            and built.get("new_rust_candidate_worker_count") == 0
            and built.get("new_rust_matching_test_status") == "NOT RUN"
            and built.get("candidate_correctness") == "NOT MEASURED"
            and built.get("candidate_qualified") is False
            and built.get("build_report_gzip_inflation_count") == 1
            and built.get("build_report_uncompressed_bytes_read")
            == V13_PLAIN_BYTES
            and built.get("build_report_uncompressed_sha256")
            == V13_PLAIN_SHA256
            and built.get("matching_archive_gzip_inflation_count") == 0
            and built.get("matching_archives_opened_by_graph") == 0
            and built.get("hidden_cases_read") == 0
            and built.get("clock_samples") == 0
            and built.get("holdout") == "NOT OPENED"
            and built.get("performance") == "NOT MEASURED"
            and built.get("undefined_behavior") == "NOT MEASURED"
            and canonical(inputs.get("actual_rust_v13_corrected_source_build"))
            == canonical(built),
            "require the genuine first-party 28-process Rust build without "
            "calling it candidate correctness")
    policy = zig_contract.get("from_scratch_policy")
    original = zig_contract.get("original_oracle")
    require(type(zig_contract) is dict
            and zig_contract.get("schema")
            == "rebar-owned-zig-scanner-phrase-source-repair-v3"
            and zig_contract.get("version") == 3
            and zig_contract.get("status")
            == "SOURCE FROZEN; CORRECTED CANDIDATE NOT RUN"
            and zig_contract.get("source", {}).get("path")
            == ZIG_PHRASE_V3["source"][0]
            and zig_contract.get("source", {}).get("sha256")
            == ZIG_PHRASE_V3["source"][1]
            and zig_contract.get("protocol", {}).get("path")
            == ZIG_PHRASE_V3["protocol"][0]
            and zig_contract.get("protocol", {}).get("sha256")
            == ZIG_PHRASE_V3["protocol"][1]
            and type(original) is dict
            and original.get("case_execution_denominator") == CASE_COUNT
            and original.get("suite_count") == SUITE_COUNT
            and original.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and type(policy) is dict
            and policy.get("another_candidate_engine") == "FORBIDDEN"
            and policy.get("external_regex_package") == "FORBIDDEN"
            and policy.get("matching_fallback") == "FORBIDDEN"
            and policy.get("stdlib_matching_engine") == "FORBIDDEN"
            and policy.get("runtime_non_delegation") == "NOT ESTABLISHED"
            and zig_contract.get("holdout") == "NOT OPENED"
            and zig_contract.get("performance") == "NOT MEASURED"
            and zig_contract.get("memory") == "NOT MEASURED"
            and zig_contract.get("undefined_behavior") == "NOT MEASURED"
            and zig_contract.get("winner_selected") is False,
            "authenticate the separately frozen from-scratch Zig repair "
            "without applying or running it")
    zig = summary.get("zig_scanner_phrase_source_repair_v3")
    require(type(zig) is dict
            and zig.get("schema")
            == "rebar-candidate-current-overview-v40"
               "-authenticated-zig-scanner-phrase-source-v3"
            and zig.get("status")
            == "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN"
            and same_published_owner(zig.get("source"),
                                     ZIG_PHRASE_V3["source"])
            and same_published_owner(zig.get("protocol"),
                                     ZIG_PHRASE_V3["protocol"])
            and same_published_owner(zig.get("contract"),
                                     ZIG_PHRASE_V3["contract"])
            and canonical(zig.get("complete_frozen_contract"))
            == canonical(zig_contract)
            and zig.get("source_applied") is False
            and zig.get("scanner_case_count") == 1024
            and zig.get("preserved_nonoverflow_case_count") == 960
            and zig.get("prospective_overflow_case_count") == 64
            and zig.get("candidate_matching_status") == "NOT RUN"
            and zig.get("candidate_workers_started") == 0
            and zig.get("reference_workers_started") == 0
            and zig.get("native_builds_started") == 0
            and zig.get("measured_compatibility_improvement")
            == "NOT MEASURED"
            and zig.get("measured_performance_improvement")
            == "NOT MEASURED"
            and zig.get("historical_semantic_mismatch_count") == 1764
            and zig.get("historical_verified_passing_case_count") == 3711
            and zig.get("holdout") == "NOT OPENED"
            and canonical(inputs.get("zig_scanner_phrase_source_repair_v3"))
            == canonical(zig)
            and summary.get("zig_scanner_phrase_source_repair_status")
            == "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN"
            and summary.get("zig_scanner_phrase_corrected_matching_status")
            == "NOT RUN"
            and summary.get("zig_scanner_phrase_correction_applied") is False
            and summary.get("zig_scanner_phrase_matrix_case_count") == 1024
            and summary.get("zig_scanner_phrase_preserved_nonoverflow_case_count")
            == 960
            and summary.get("zig_scanner_phrase_prospective_case_count") == 64
            and summary.get("zig_scanner_phrase_measured_mismatch_reduction")
            == "NOT MEASURED"
            and summary.get("zig_scanner_phrase_measured_speedup")
            == "NOT MEASURED"
            and inputs.get("zig_scanner_phrase_source_repair_status")
            == summary.get("zig_scanner_phrase_source_repair_status")
            and inputs.get("zig_scanner_phrase_corrected_matching_status")
            == "NOT RUN"
            and inputs.get("zig_scanner_phrase_correction_applied") is False
            and inputs.get("zig_scanner_phrase_matrix_case_count") == 1024
            and inputs.get("zig_scanner_phrase_preserved_nonoverflow_case_count")
            == 960
            and inputs.get("zig_scanner_phrase_prospective_case_count") == 64
            and inputs.get("zig_scanner_phrase_measured_mismatch_reduction")
            == "NOT MEASURED"
            and inputs.get("zig_scanner_phrase_measured_speedup")
            == "NOT MEASURED",
            "preserve all original Zig scanner cases and historical failures "
            "without claiming an unapplied repair has improved matching")
    return {
        "status": "PASS",
        "overview_version": 40,
        "owners": grouped_owners(V40),
        "preserved_v39_overview": grouped_owners(V39),
        "zig_phrase_source_freeze": {
            "owners": grouped_owners(ZIG_PHRASE_V3),
            "status":
                "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN",
            "scanner_case_count": 1024,
            "preserved_nonoverflow_case_count": 960,
            "prospective_overflow_case_count": 64,
            "candidate_matching": "NOT RUN",
            "source_applied": False,
            "candidate_workers_started": 0,
            "measured_mismatch_reduction": "NOT MEASURED",
            "measured_speedup": "NOT MEASURED",
        },
        "corrected_producer_source_sha256": PRODUCER["source"][1],
        "corrected_producer_protocol_sha256": PRODUCER["protocol"][1],
        "corrected_producer_contract_sha256": PRODUCER["contract"][1],
        "same_context_reference_correction_status": "PASS",
        "actual_reference_status": "PASS",
        "actual_reference_publication_status": "PASS",
        "actual_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "actual_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "actual_reference_process_ids": list(CORRECTED_REFERENCE_PIDS),
        "historical_falsification_status": "FALSIFIED",
        "actual_build_status": "PASS",
        "actual_v13_compiler_process_count": 28,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_zig_semantic_mismatch_count": 1764,
        "authenticated_evidence_owner_lower_bound":
            ACTUAL_EVIDENCE_OWNER_COUNT,
        "authenticated_history_reference_lower_bound":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "all_candidate_matching_blocked": True,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
    }


def extract_historical_v2_helper_owners(raw: bytes) -> tuple[
        tuple[str, str, int], ...]:
    """Inspect only literal owner declarations; never import or execute V2."""
    require(type(raw) is bytes and 0 < len(raw) <= MAX_SOURCE_BYTES,
            "require a bounded independently frozen historical V2 source")
    try:
        tree = ast.parse(
            raw.decode("utf-8"), filename=V2["source"][0], mode="exec",
        )
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise CampaignError(
            "reject a malformed or nonliteral historical V2 helper"
        ) from error
    declarations: list[ast.AnnAssign] = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            if (isinstance(node.target, ast.Name)
                    and node.target.id == "REPAIRED_SOURCE_OWNERS"):
                declarations.append(node)
        elif isinstance(node, ast.Assign):
            require(
                not any(
                    isinstance(target, ast.Name)
                    and target.id == "REPAIRED_SOURCE_OWNERS"
                    for target in node.targets
                ),
                "reject reassigned historical V2 repaired source owners",
            )
        elif isinstance(node, ast.AugAssign):
            require(
                not (isinstance(node.target, ast.Name)
                     and node.target.id == "REPAIRED_SOURCE_OWNERS"),
                "reject augmented historical V2 repaired source owners",
            )
        elif isinstance(node, ast.Delete):
            require(
                not any(
                    isinstance(target, ast.Name)
                    and target.id == "REPAIRED_SOURCE_OWNERS"
                    for target in node.targets
                ),
                "reject deleted historical V2 repaired source owners",
            )
    require(len(declarations) == 1
            and isinstance(declarations[0].value, ast.Tuple),
            "require exactly one complete literal historical V2 owner tuple")
    try:
        owners = ast.literal_eval(declarations[0].value)
    except (ValueError, TypeError, RecursionError) as error:
        raise CampaignError(
            "reject a dynamic historical V2 owner expression"
        ) from error
    require(
        type(owners) is tuple
        and len(owners) == len(HISTORICAL_V2_REPAIRED_SOURCE_OWNERS)
        and all(
            type(row) is tuple and len(row) == 3
            and type(row[0]) is str and type(row[1]) is str
            and type(row[2]) is int
            for row in owners
        )
        and owners == HISTORICAL_V2_REPAIRED_SOURCE_OWNERS,
        "bind all nine ordered original immutable V2 repaired source owners",
    )
    return owners


def authenticate_historical_v2_helper_source(
        source_raw: bytes, frozen_contract: Any) -> dict[str, Any]:
    """Prove the complete historic helper with no import, call, or archive."""
    require(
        type(source_raw) is bytes
        and len(source_raw) == V2["source"][2]
        and digest(source_raw) == V2["source"][1],
        "require every byte of the actual immutable historical V2 helper",
    )
    owners = extract_historical_v2_helper_owners(source_raw)
    try:
        tree = ast.parse(
            source_raw.decode("utf-8"),
            filename=V2["source"][0], mode="exec",
        )
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as error:
        raise CampaignError(
            "reject the complete historical V2 helper syntax"
        ) from error
    function_names = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required_helpers = {
        "_read_owned", "current_original", "ensure_absent",
        "exact_originals", "open_target_parent", "private_directory",
        "read_private", "read_recorded_phase", "role_target_names",
        "same_original", "sync_directory", "write_evidence_receipt",
        "write_private", "write_stage",
    }
    require(required_helpers.issubset(function_names),
            "require every immutable no-delegation V2 recovery helper")
    expected_owners = [
        {"path": relative, "sha256": fingerprint, "bytes": count}
        for relative, fingerprint, count in owners
    ]
    historical_repairs = {
        "bridge_source": (BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
        "adapter": (
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        ),
        "engine": (ENGINE_SHA256, ENGINE_BYTES),
        "bridge": (BRIDGE_SHA256, BRIDGE_BYTES),
    }
    expected_roles = []
    for role in ROLE_ORDER:
        original = dict(ORIGINALS[role])
        original["mode"] = format(original["mode"], "04o")
        fingerprint, size = historical_repairs[role]
        expected_roles.append({
            "role": role,
            "original": original,
            "repaired_sha256": fingerprint,
            "repaired_bytes": size,
        })
    build = (
        frozen_contract.get("actual_rust_v11_source_build")
        if type(frozen_contract) is dict else None
    )
    oracle = (
        frozen_contract.get("original_oracle")
        if type(frozen_contract) is dict else None
    )
    recovery = (
        frozen_contract.get("recovery_policy")
        if type(frozen_contract) is dict else None
    )
    workers = (
        frozen_contract.get("worker_policy")
        if type(frozen_contract) is dict else None
    )
    require(
        type(frozen_contract) is dict
        and frozen_contract.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v2-source-freeze"
        and frozen_contract.get("version") == 2
        and frozen_contract.get("status")
        == "SOURCE FROZEN; RUST CANDIDATE NOT RUN"
        and frozen_contract.get("family") == FAMILY
        and frozen_contract.get("campaign_label")
        == "phase2-v11-rust-dual-overlay-original-p0"
        and frozen_contract.get("source")
        == {"path": V2["source"][0], "sha256": V2["source"][1]}
        and frozen_contract.get("protocol")
        == {"path": V2["protocol"][0], "sha256": V2["protocol"][1]}
        and type(build) is dict
        and build.get("actual_compiler_process_count") == 28
        and build.get("independent_phase_count") == 2
        and build.get("label") == "phase2-v11-rust-dual-overlay"
        and canonical(build.get("repaired_source_owners"))
        == canonical(expected_owners)
        and canonical(build.get("native_roles"))
        == canonical([
            {
                "role": "engine",
                "sha256": ENGINE_SHA256,
                "bytes": ENGINE_BYTES,
            },
            {
                "role": "bridge",
                "sha256": BRIDGE_SHA256,
                "bytes": BRIDGE_BYTES,
            },
        ])
        and canonical(frozen_contract.get("four_original_target_owners"))
        == canonical(expected_roles)
        and type(oracle) is dict
        and oracle.get("suite_count") == SUITE_COUNT
        and oracle.get("case_execution_denominator") == CASE_COUNT
        and oracle.get("named_private_waiver_count")
        == PRIVATE_WAIVER_COUNT
        and canonical(oracle.get("source_ordered_suites"))
        == canonical([
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ])
        and type(recovery) is dict
        and recovery.get("role_order") == list(ROLE_ORDER)
        and recovery.get("restoration_order") == list(RESTORATION_ORDER)
        and recovery.get("target_count") == len(ROLE_ORDER)
        and recovery.get("group_atomic") is False
        and recovery.get("touch_other_family") is False
        and recovery.get("journal_fsync_before_any_mutation") is True
        and recovery.get("restore_all_four_originals_before_publication")
        is True
        and type(workers) is dict
        and workers.get("actual_worker_count") == SUITE_COUNT
        and workers.get("actual_distinct_worker_processes") == SUITE_COUNT
        and workers.get("candidate_matching_delegated") is False
        and workers.get("cross_family_matching") == "FORBIDDEN"
        and workers.get("external_regex_engine") == "FORBIDDEN"
        and workers.get("stdlib_regex_engine") == "FORBIDDEN",
        "bind every historical V2 helper role, source, mode and policy "
        "without confusing its adapter with V4, V12, or V13",
    )
    return {
        "schema": SCHEMA + "-authenticated-historical-v2-helper-source",
        "status": "PASS",
        "owners": grouped_owners(V2),
        "historical_helper_schema":
            "rebar-owned-repaired-rust-original-campaign-v2",
        "historical_contract_schema": frozen_contract["schema"],
        "historical_repaired_source_owners": expected_owners,
        "historical_repaired_source_owner_count": len(expected_owners),
        "historical_public_adapter": {
            "path": "candidates/rust_candidate.py",
            "sha256": HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
            "bytes": HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        },
        "historical_v12_public_adapter_sha256":
            HISTORICAL_DERIVED_PUBLIC_SHA256,
        "corrected_v13_public_adapter": {
            "path": "candidates/rust_candidate.py",
            "sha256": CORRECTED_PUBLIC_SHA256,
            "bytes": CORRECTED_PUBLIC_BYTES,
        },
        "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "required_helper_function_count": len(required_helpers),
        "source_verification_method":
            "BOUNDED COMPLETE SOURCE AST; NO IMPORT OR EXECUTION",
        "module_imported_by_source_gate": False,
        "module_executed_by_source_gate": False,
        "helper_invoked_by_source_gate": False,
        "candidate_workers_started_by_source_gate": 0,
        "source_build_archive_reads": 0,
        "source_build_archive_gzip_inflations": 0,
        "holdout": "NOT OPENED",
    }


def authenticate_actual_v6_entry_failure(
        failure: Any, observation: Any) -> dict[str, Any]:
    """Preserve the one real V6 failure and its independently proven effect."""
    require(type(failure) is dict and type(observation) is dict,
            "preserve both independently owned V6 failure records")
    invoke = observation.get("actual_invocation")
    cause = observation.get("root_cause")
    effects = observation.get("actual_candidate_effects")
    archived = observation.get("source_build_archive_effect")
    require(
        failure.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6-entry-failure"
        and failure.get("status") == "FAIL"
        and failure.get("family") == FAMILY
        and failure.get("suite_count") == SUITE_COUNT
        and failure.get("case_execution_denominator") == CASE_COUNT
        and failure.get("campaign_source_sha256")
        == V6_PREDECESSOR["source"][1]
        and failure.get("campaign_protocol_sha256")
        == V6_PREDECESSOR["protocol"][1]
        and failure.get("campaign_contract_sha256")
        == V6_PREDECESSOR["contract"][1]
        and failure.get("error_type") == "CampaignError"
        and failure.get("error_message")
        == "authenticate immutable historical helpers without running V2"
        and failure.get("attempted_suite_count") == 0
        and failure.get("started_suite_count") == 0
        and failure.get("fully_observed_suite_count") == 0
        and failure.get("actual_candidate_workers") == 0
        and failure.get("actual_reference_workers") == 0
        and failure.get("actual_native_activations") == 0
        and failure.get("recovery_roots_created") == 0
        and failure.get("recovery_journals_created") == 0
        and failure.get("publication_attempted") is False
        and failure.get("publication_status") == "NOT ATTEMPTED"
        and failure.get("semantic_mismatch_count") == "NOT MEASURED"
        and failure.get("candidate_qualified") is False
        and failure.get("holdout") == "NOT OPENED"
        and observation.get("schema")
        == "rebar-owned-repaired-rust-original-campaign-v6"
        "-entry-failure-independent-observation-v1"
        and observation.get("observation_status")
        == "PASS; FAILURE AND OMITTED SOURCE-BUILD EFFECT PRESERVED"
        and type(invoke) is dict
        and invoke.get("count") == 1
        and invoke.get("mode") == "AUTHORIZED RUN"
        and invoke.get("family") == FAMILY
        and invoke.get("exit_code") == 1
        and invoke.get("source_sha256") == V6_PREDECESSOR["source"][1]
        and invoke.get("protocol_sha256") == V6_PREDECESSOR["protocol"][1]
        and invoke.get("contract_sha256") == V6_PREDECESSOR["contract"][1]
        and same_published_owner(
            invoke.get("stdout"), ACTUAL_V6_PREFLIGHT_FAILURE["failure"]
        )
        and invoke.get("error_type") == "CampaignError"
        and invoke.get("error_message") == failure["error_message"]
        and type(cause) is dict
        and cause.get("kind")
        == "IMMUTABLE HISTORICAL HELPER ADAPTER FINGERPRINT MISMATCH"
        and same_published_owner(cause.get("helper_source"), V2["source"])
        and type(cause.get("actual_v2_repaired_adapter")) is dict
        and cause["actual_v2_repaired_adapter"].get("path")
        == "candidates/rust_candidate.py"
        and cause["actual_v2_repaired_adapter"].get("sha256")
        == HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
        and cause["actual_v2_repaired_adapter"].get("bytes")
        == HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
        and cause.get("incorrect_v6_expected_historical_adapter_sha256")
        == HISTORICAL_DERIVED_PUBLIC_SHA256
        and type(effects) is dict
        and effects.get("candidate_workers") == 0
        and effects.get("reference_workers") == 0
        and effects.get("native_activations") == 0
        and effects.get("recovery_roots_created") == 0
        and effects.get("recovery_journals_created") == 0
        and effects.get("semantic_mismatch_count") == "NOT MEASURED"
        and effects.get("candidate_qualified") is False
        and effects.get("holdout") == "NOT OPENED"
        and type(archived) is dict
        and archived.get("controller_failure_ledger_records_effect") is False
        and archived.get("archive_read_count") == 1
        and archived.get("gzip_inflation_count") == 1
        and type(archived.get("archive")) is dict
        and archived["archive"].get("path") == BUILD["archive"][0]
        and archived["archive"].get("sha256") == BUILD["archive"][1]
        and archived["archive"].get("compressed_bytes")
        == BUILD["archive"][2]
        and archived["archive"].get("uncompressed_bytes") == V13_PLAIN_BYTES
        and archived["archive"].get("uncompressed_sha256") == V13_PLAIN_SHA256
        and archived.get("matching_archive_read_count") == 0
        and archived.get("reference_archive_read_count") == 0
        and archived.get("nested_matching_archive_read_count") == 0,
        "preserve the exact one real historical V6 preactivation failure "
        "and its previously omitted V13 source-build archive effect",
    )
    return {
        "schema": SCHEMA + "-preserved-actual-v6-preflight-failure",
        "status": "FAIL",
        "owners": grouped_owners(ACTUAL_V6_PREFLIGHT_FAILURE),
        "historical_v6_controller": grouped_owners(V6_PREDECESSOR),
        "failure_class":
            "PRE-ACTIVATION HISTORICAL HELPER FINGERPRINT MISMATCH",
        "error_type": "CampaignError",
        "error_message": failure["error_message"],
        "actual_controller_process_count": 1,
        "actual_candidate_workers": 0,
        "actual_native_activations": 0,
        "actual_source_build_archive_read_count": 1,
        "actual_source_build_archive_gzip_inflation_count": 1,
        "actual_source_build_archive_compressed_bytes": BUILD["archive"][2],
        "actual_source_build_archive_uncompressed_bytes": V13_PLAIN_BYTES,
        "actual_source_build_archive_uncompressed_sha256": V13_PLAIN_SHA256,
        "historical_controller_ledger_omitted_archive_effect": True,
        "actual_matching_archive_read_count": 0,
        "actual_reference_archive_read_count": 0,
        "semantic_mismatch_count": "NOT MEASURED",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
    }


def authenticate_current_v41(
        summary: Any, inputs: Any, producer_contract: Any,
        reference_receipt: Any, falsification: Any,
        build_receipt: Any, zig_contract: Any,
        c_contract: Any) -> dict[str, Any]:
    """Bind the actual V41 graph and its strictly C-only frozen runner."""
    require(type(summary) is dict and type(inputs) is dict,
            "require both exact committed and pushed V41 graph documents")
    for value, expected_schema, qualified_field in (
            (summary, "rebar-candidate-current-overview-v41-summary",
             "qualified_candidate_count"),
            (inputs, "rebar-candidate-current-overview-v41-inputs",
             "candidate_qualified_count")):
        require(
            value.get("schema") == expected_schema
            and value.get("version") == 41
            and value.get("full_case_denominator") == CASE_COUNT
            and value.get("suite_count") == SUITE_COUNT
            and value.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and value.get(qualified_field) == 0
            and value.get("candidate_case_producer_status")
            == "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN"
            and value.get("required_corrected_candidate_runner_versions")
            == ["RUST V6"]
            and value.get("stale_candidate_worker_versions") == ["RUST V5"]
            and value.get("all_candidate_matching_blocked") is True
            and value.get("first_party_source_inventory_family_count") == 6
            and value.get("corrected_c_only_runner_family") == "c"
            and value.get("corrected_c_only_runnable_family_count") == 1
            and value.get("corrected_c_only_runner_source_sha256")
            == CORRECTED_C_ONLY_V10["runner"][1]
            and value.get("corrected_c_only_runner_status")
            == "C-ONLY RUNNER SOURCE FROZEN; CORRECTED C MATCHING NOT RUN"
            and value.get("corrected_c_matching_status") == "NOT RUN"
            and value.get("corrected_c_candidate_workers_started") == 0
            and value.get("corrected_c_candidate_qualified") is False
            and value.get("corrected_c_matching_mismatch_reduction")
            == "NOT MEASURED"
            and value.get("corrected_c_matching_speedup") == "NOT MEASURED"
            and value.get("rust_v6_runner_status") == "UNCOMMITTED",
            "reject a stale graph, a six-family runner claim, "
            "or unobserved C or Rust matching in " + expected_schema)
    require(
        summary.get("status") == "PASS"
        and same_published_owner(summary.get("source"), V41["source"])
        and same_published_owner(summary.get("inputs"), V41["inputs"])
        and same_published_owner(summary.get("svg"), V41["svg"])
        and canonical(summary.get("previous_overview"))
        == canonical(grouped_owners(V40))
        and canonical(inputs.get("previous_overview"))
        == canonical(grouped_owners(V40)),
        "require the exact pushed V41 owners and V40 as immediate history")
    family = c_contract.get("candidate_family") if type(c_contract) is dict else None
    phase = c_contract.get("phase_boundary") if type(c_contract) is dict else None
    inventories = (
        c_contract.get("source_inventory_families")
        if type(c_contract) is dict else None
    )
    require(
        type(c_contract) is dict
        and c_contract.get("schema")
        == "rebar-frozen-python-re-p0-candidate-protocol-v10"
        and c_contract.get("version") == 10
        and c_contract.get("suite_count") == SUITE_COUNT
        and c_contract.get("case_execution_denominator") == CASE_COUNT
        and c_contract.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
        and c_contract.get("source_family_count") == 6
        and c_contract.get("source_owner_count") == 25
        and c_contract.get("source_inventory_family_count") == 6
        and c_contract.get("source_inventory_owner_count") == 25
        and c_contract.get("six_family_inventory_is_source_only") is True
        and c_contract.get("candidate_execution_scope")
        == "C-ONLY; VERIFIED C15 NATIVE REQUIRED"
        and c_contract.get("runnable_candidate_families") == ["c"]
        and c_contract.get("runnable_candidate_family_count") == 1
        and type(inventories) is list
        and [item.get("family") for item in inventories
             if type(item) is dict]
        == ["rust", "c", "zig", "cpp", "go", "fortran"]
        and type(family) is dict
        and family.get("name") == "c"
        and family.get("external_regex_engine_allowed") is False
        and family.get("shared_candidate_engine_allowed") is False
        and family.get("stdlib_engine_delegation_allowed") is False
        and family.get("original_family_spec_unchanged") is True
        and type(phase) is dict
        and phase.get("actual_candidate_workers") == 0
        and phase.get("actual_native_activations") == 0
        and phase.get("actual_reference_workers") == 0
        and phase.get("actual_source_builds") == 0
        and phase.get("benchmark_files_read") == 0
        and phase.get("hidden_cases_read") == 0
        and phase.get("clock_samples") == 0
        and phase.get("timing_trials_run") == 0
        and phase.get("candidate_qualified_count") == 0
        and phase.get("candidate_correctness") == "NOT MEASURED"
        and phase.get("holdout") == "NOT OPENED"
        and phase.get("memory") == "NOT MEASURED"
        and phase.get("performance") == "NOT MEASURED"
        and phase.get("winner_selected") is False
        and c_contract.get("runner", {}).get("path")
        == CORRECTED_C_ONLY_V10["runner"][0]
        and c_contract.get("runner", {}).get("sha256")
        == CORRECTED_C_ONLY_V10["runner"][1]
        and c_contract.get("worker", {}).get("path")
        == CORRECTED_C_ONLY_V10["worker"][0]
        and c_contract.get("worker", {}).get("sha256")
        == CORRECTED_C_ONLY_V10["worker"][1]
        and c_contract.get("protocol", {}).get("path")
        == CORRECTED_C_ONLY_V10["protocol"][0]
        and c_contract.get("protocol", {}).get("sha256")
        == CORRECTED_C_ONLY_V10["protocol"][1]
        and c_contract.get("caller_pinned_original_producer", {})
        .get("source_sha256") == PRODUCER["source"][1]
        and c_contract.get("caller_pinned_original_producer", {})
        .get("protocol_sha256") == PRODUCER["protocol"][1]
        and c_contract.get("caller_pinned_original_producer", {})
        .get("document_sha256") == PRODUCER["contract"][1],
        "authenticate all six first-party source designs as inventory "
        "but the single frozen runnable candidate as C only")
    proof = summary.get("corrected_c_only_runner_v10")
    require(
        type(proof) is dict
        and proof.get("schema")
        == "rebar-candidate-current-overview-v41-authenticated-c-only-runner-v10"
        and proof.get("status")
        == "C-ONLY RUNNER SOURCE FROZEN; CORRECTED C MATCHING NOT RUN"
        and all(same_published_owner(proof.get(role), owner)
                for role, owner in CORRECTED_C_ONLY_V10.items())
        and canonical(proof.get("complete_frozen_contract"))
        == canonical(c_contract)
        and proof.get("complete_runner_binding_sha256")
        == "9bffc5dab2acdaec5ad1bd03ad251b2c7bf626257dba2ecb25905a4a2df3a7f4"
        and proof.get("candidate_family") == "c"
        and proof.get("runnable_candidate_family_count") == 1
        and proof.get("first_party_source_inventory_family_count") == 6
        and proof.get("other_corrected_candidate_family_count") == 5
        and proof.get("other_corrected_candidate_matching_status")
        == "NOT RUN"
        and proof.get("actual_candidate_workers_started") == 0
        and proof.get("actual_compiler_processes_started") == 0
        and proof.get("actual_reference_workers_started") == 0
        and proof.get("qualified_candidate_count") == 0
        and proof.get("corrected_c_matching_status") == "NOT RUN"
        and proof.get("rust_v6_runner_status") == "UNCOMMITTED"
        and proof.get("holdout") == "NOT OPENED"
        and proof.get("memory") == "NOT MEASURED"
        and proof.get("performance") == "NOT MEASURED"
        and canonical(inputs.get("corrected_c_only_runner_v10"))
        == canonical(proof),
        "bind both actual V41 graph documents to all four exact "
        "committed C-only owners without starting matching")
    normalized_summary = copy.deepcopy(summary)
    normalized_inputs = copy.deepcopy(inputs)
    for value, expected_schema in (
            (normalized_summary,
             "rebar-candidate-current-overview-v40-summary"),
            (normalized_inputs,
             "rebar-candidate-current-overview-v40-inputs")):
        value["schema"] = expected_schema
        value["version"] = 40
        value["candidate_case_producer_status"] = (
            "FROZEN; CANDIDATE WORKERS STILL STALE"
        )
        value["required_corrected_candidate_runner_versions"] = (
            ["V8", "V10", "RUST V6"]
        )
        value["stale_candidate_worker_versions"] = (
            ["V7", "V9", "RUST V5"]
        )
        value["previous_overview"] = grouped_owners(V39)
    for role in ("source", "inputs", "svg"):
        normalized_summary[role] = grouped_owners(V40)[role]
    previous = authenticate_current_v40(
        normalized_summary, normalized_inputs, producer_contract,
        reference_receipt, falsification, build_receipt, zig_contract,
    )
    return {
        **previous,
        "overview_version": 41,
        "owners": grouped_owners(V41),
        "preserved_v40_overview": grouped_owners(V40),
        "corrected_c_only_runner_v10": {
            "owners": grouped_owners(CORRECTED_C_ONLY_V10),
            "status": proof["status"],
            "candidate_family": "c",
            "runnable_candidate_family_count": 1,
            "first_party_source_inventory_family_count": 6,
            "other_corrected_candidate_family_count": 5,
            "corrected_c_matching_status": "NOT RUN",
            "actual_candidate_workers_started": 0,
            "candidate_qualified": False,
            "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
            "holdout": "NOT OPENED",
            "performance": "NOT MEASURED",
        },
        "required_corrected_candidate_runner_versions": ["RUST V6"],
        "stale_candidate_worker_versions": ["RUST V5"],
        "candidate_case_producer_status":
            "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; C MATCHING NOT RUN",
        "first_party_source_inventory_family_count": 6,
        "corrected_c_only_runnable_family_count": 1,
        "corrected_c_matching_status": "NOT RUN",
        "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
    }


def authenticate_preserved_v42(
        summary: Any, inputs: Any, predecessor_contract: Any,
        c_contract: Any) -> dict[str, Any]:
    """Preserve the independently frozen predecessor before its real run."""
    require(type(summary) is dict and type(inputs) is dict,
            "require both exact independently frozen V42 graph owners")
    for value, schema, qualified in (
            (summary, "rebar-candidate-current-overview-v42-summary",
             "qualified_candidate_count"),
            (inputs, "rebar-candidate-current-overview-v42-inputs",
             "candidate_qualified_count")):
        require(
            value.get("schema") == schema
            and value.get("version") == 42
            and value.get("full_case_denominator") == CASE_COUNT
            and value.get("suite_count") == SUITE_COUNT
            and value.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and value.get(qualified) == 0
            and value.get("authenticated_evidence_owner_lower_bound")
            == ACTUAL_EVIDENCE_OWNER_COUNT
            and value.get("authenticated_history_reference_lower_bound")
            == ACTUAL_AUTHENTICATED_REFERENCE_COUNT
            and value.get("candidate_case_producer_status")
            == "V4 SOURCE FROZEN; SEPARATE C-ONLY V8/V10 "
               "AND RUST-ONLY V6 RUNNERS FROZEN; BOTH MATCHING NOT RUN"
            and value.get("corrected_reference_full_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and value.get("corrected_reference_cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and value.get("corrected_reference_process_ids")
            == list(CORRECTED_REFERENCE_PIDS)
            and value.get("corrected_c_matching_status") == "NOT RUN"
            and value.get("corrected_rust_matching_status") == "NOT RUN"
            and value.get("matching_archive_gzip_inflation_count") == 0
            and value.get("candidate_matching_archives_opened_by_graph") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("performance") == "NOT MEASURED"
            and value.get("final_holdout_opened") is False
            and value.get("winner_selected") is False,
            "preserve the genuine pre-failure V42 graph without a stale runner",
        )
    require(
        summary.get("status") == "PASS"
        and same_published_owner(summary.get("source"), V42["source"])
        and same_published_owner(summary.get("inputs"), V42["inputs"])
        and same_published_owner(summary.get("svg"), V42["svg"])
        and canonical(summary.get("previous_overview"))
        == canonical(grouped_owners(V41))
        and canonical(inputs.get("previous_overview"))
        == canonical(grouped_owners(V41)),
        "authenticate all four historical V42 owners and V41 ancestry",
    )
    rust = summary.get("corrected_rust_only_runner_v6")
    require(
        type(rust) is dict
        and rust.get("schema")
        == "rebar-candidate-current-overview-v42"
           "-authenticated-rust-only-original-runner-v6"
        and rust.get("status")
        == "RUST-ONLY RUNNER SOURCE FROZEN; CORRECTED RUST MATCHING NOT RUN"
        and rust.get("candidate_family") == FAMILY
        and all(same_published_owner(rust.get(role), owner)
                for role, owner in V6_PREDECESSOR.items())
        and canonical(rust.get("complete_frozen_contract"))
        == canonical(predecessor_contract)
        and rust.get("actual_candidate_workers_started") == 0
        and rust.get("actual_reference_workers_started") == 0
        and rust.get("actual_compiler_processes_started") == 0
        and rust.get("candidate_qualified") is False
        and rust.get("holdout") == "NOT OPENED"
        and rust.get("performance") == "NOT MEASURED"
        and canonical(inputs.get("corrected_rust_only_runner_v6"))
        == canonical(rust),
        "preserve the actual immutable V6 source freeze without "
        "relabeling it as matching",
    )
    c_proof = summary.get("corrected_c_only_runner_v10")
    require(
        type(c_proof) is dict
        and all(same_published_owner(c_proof.get(role), owner)
                for role, owner in CORRECTED_C_ONLY_V10.items())
        and canonical(c_proof.get("complete_frozen_contract"))
        == canonical(c_contract)
        and c_proof.get("candidate_family") == "c"
        and c_proof.get("actual_candidate_workers_started") == 0
        and c_proof.get("qualified_candidate_count") == 0
        and canonical(inputs.get("corrected_c_only_runner_v10"))
        == canonical(c_proof),
        "preserve independently frozen C without running its matcher",
    )
    return {
        "status": "PASS",
        "overview_version": 42,
        "owners": grouped_owners(V42),
        "previous_v41_overview": grouped_owners(V41),
        "historical_evidence_owner_lower_bound":
            ACTUAL_EVIDENCE_OWNER_COUNT,
        "historical_history_reference_lower_bound":
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT,
        "historical_v6_source_matching": "NOT RUN",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
    }


def authenticate_current_v43(
        summary: Any, inputs: Any, producer_contract: Any,
        reference_receipt: Any, falsification: Any,
        build_receipt: Any, zig_contract: Any, c_contract: Any,
        predecessor_contract: Any, failure: Any,
        observation: Any) -> dict[str, Any]:
    """Authenticate current failure evidence without repeating any run."""
    require(type(summary) is dict and type(inputs) is dict,
            "require both independently pinned actual V43 graph documents")
    for value, expected_schema, qualified_field in (
            (summary, "rebar-candidate-current-overview-v43-summary",
             "qualified_candidate_count"),
            (inputs, "rebar-candidate-current-overview-v43-inputs",
             "candidate_qualified_count")):
        require(
            value.get("schema") == expected_schema
            and value.get("version") == 43
            and value.get("full_case_denominator") == CASE_COUNT
            and value.get("suite_count") == SUITE_COUNT
            and value.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
            and value.get(qualified_field) == 0
            and value.get("candidate_case_producer_status")
            == "V4 SOURCE FROZEN; RUST PREFLIGHT FAIL; "
               "ZERO RUNNABLE CANDIDATES"
            and value.get("all_candidate_matching_blocked") is True
            and value.get("actually_runnable_candidate_families") == []
            and value.get("actually_runnable_candidate_family_count") == 0
            and value.get("first_party_source_inventory_family_count") == 6
            and value.get("corrected_c_only_runner_family") == "c"
            and value.get("corrected_c_only_runnable_family_count") == 1
            and value.get("corrected_c_only_runner_source_sha256")
            == CORRECTED_C_ONLY_V10["runner"][1]
            and value.get("corrected_c_matching_status") == "NOT RUN"
            and value.get("corrected_c_candidate_workers_started") == 0
            and value.get("corrected_c_candidate_qualified") is False
            and value.get("rust_v6_runner_status")
            == "SOURCE FROZEN; NOT RUNNABLE; PREFLIGHT FAILED"
            and value.get("corrected_rust_matching_status") == "NOT RUN"
            and value.get("corrected_rust_candidate_workers_started") == 0
            and value.get("corrected_rust_candidate_qualified") is False
            and value.get("actual_rust_controller_status") == "FAIL"
            and value.get("actual_rust_failure_class")
            == "PRE-ACTIVATION HISTORICAL HELPER FINGERPRINT MISMATCH"
            and value.get("actual_rust_error_type") == "CampaignError"
            and value.get("actual_rust_error_message")
            == "authenticate immutable historical helpers without running V2"
            and value.get("actual_rust_failure_evidence_sha256")
            == ACTUAL_V6_PREFLIGHT_FAILURE["failure"][1]
            and value.get("actual_rust_observed_effects_sha256")
            == ACTUAL_V6_PREFLIGHT_FAILURE["observation"][1]
            and value.get("actual_rust_controller_ledger_omits_source_build_archive_effect")
            is True
            and value.get("actual_rust_source_build_archive_sha256")
            == BUILD["archive"][1]
            and value.get("actual_rust_source_build_archive_read_count") == 1
            and value.get("actual_rust_source_build_archive_gzip_inflation_count")
            == 1
            and value.get("actual_rust_source_build_archive_compressed_bytes")
            == BUILD["archive"][2]
            and value.get("actual_rust_source_build_archive_uncompressed_bytes")
            == V13_PLAIN_BYTES
            and value.get("actual_rust_controller_process_count") == 1
            and value.get("actual_rust_attempted_suite_count") == 0
            and value.get("actual_rust_started_suite_count") == 0
            and value.get("actual_rust_completed_suite_count") == 0
            and value.get("actual_rust_candidate_workers") == 0
            and value.get("actual_rust_native_activations") == 0
            and value.get("actual_rust_semantic_mismatch_count")
            == "NOT MEASURED"
            and value.get("actual_rust_matching_archive_read_count") == 0
            and value.get("actual_rust_reference_archive_read_count") == 0
            and value.get("authenticated_evidence_owner_lower_bound")
            == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
            and value.get("authenticated_history_reference_lower_bound")
            == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
            and value.get("matching_archive_gzip_inflation_count") == 0
            and value.get("candidate_matching_archives_opened_by_graph") == 0
            and value.get("hidden_cases_read") == 0
            and value.get("clock_samples") == 0
            and value.get("timing_trials_run") == 0
            and value.get("performance") == "NOT MEASURED"
            and value.get("final_holdout_opened") is False
            and value.get("winner_selected") is False,
            "reject a stale graph, concealed actual V6 failure, "
            "invented candidate, archive, baseline, or performance "
            + expected_schema,
        )
    require(
        summary.get("status") == "PASS"
        and same_published_owner(summary.get("source"), V43["source"])
        and same_published_owner(summary.get("inputs"), V43["inputs"])
        and same_published_owner(summary.get("svg"), V43["svg"])
        and canonical(summary.get("previous_overview"))
        == canonical(grouped_owners(V42))
        and canonical(inputs.get("previous_overview"))
        == canonical(grouped_owners(V42)),
        "bind every actual pushed V43 owner to immediate V42 history",
    )
    preserved_failure = authenticate_actual_v6_entry_failure(
        failure, observation,
    )
    proof = summary.get("actual_rust_preflight_failure")
    require(
        type(proof) is dict
        and proof.get("schema")
        == "rebar-candidate-current-overview-v43"
           "-authenticated-real-rust-preflight-failure"
        and proof.get("status") == "FAIL"
        and same_published_owner(
            proof.get("failure"), ACTUAL_V6_PREFLIGHT_FAILURE["failure"]
        )
        and same_published_owner(
            proof.get("observation"),
            ACTUAL_V6_PREFLIGHT_FAILURE["observation"],
        )
        and canonical(proof.get("complete_actual_failure"))
        == canonical(failure)
        and canonical(proof.get("complete_independent_observation"))
        == canonical(observation)
        and proof.get("complete_actual_failure_binding_sha256")
        == "f5c4fc4fd48f51afb88554363e607a93cb3adf9e2f0f5e54bda04c03b1946e44"
        and proof.get("actual_controller_process_count") == 1
        and proof.get("actual_rust_candidate_workers") == 0
        and proof.get("actual_rust_native_activations") == 0
        and proof.get("actual_rust_semantic_mismatch_count")
        == "NOT MEASURED"
        and proof.get("actual_source_build_archive_read_count") == 1
        and proof.get("actual_source_build_archive_gzip_inflation_count")
        == 1
        and proof.get("actual_matching_archive_read_count") == 0
        and proof.get("actual_reference_archive_read_count") == 0
        and proof.get("actually_runnable_candidate_family_count") == 0
        and proof.get("candidate_qualified") is False
        and proof.get("controller_failure_ledger_omits_build_archive_effect")
        is True
        and proof.get("holdout") == "NOT OPENED"
        and proof.get("performance") == "NOT MEASURED"
        and canonical(inputs.get("actual_rust_preflight_failure"))
        == canonical(proof),
        "bind both current graphs to the exact genuine failure and "
        "independently observed missing source-build archive effect",
    )
    rust = summary.get("corrected_rust_only_runner_v6")
    require(
        type(rust) is dict
        and rust.get("schema")
        == "rebar-candidate-current-overview-v42"
           "-authenticated-rust-only-original-runner-v6"
        and rust.get("candidate_family") == FAMILY
        and all(same_published_owner(rust.get(role), owner)
                for role, owner in V6_PREDECESSOR.items())
        and canonical(rust.get("complete_frozen_contract"))
        == canonical(predecessor_contract)
        and rust.get("candidate_qualified") is False
        and canonical(inputs.get("corrected_rust_only_runner_v6"))
        == canonical(rust),
        "preserve the exact V6 source, contract, and historical loss",
    )
    normalized_summary = copy.deepcopy(summary)
    normalized_inputs = copy.deepcopy(inputs)
    for value, expected_schema in (
            (normalized_summary,
             "rebar-candidate-current-overview-v41-summary"),
            (normalized_inputs,
             "rebar-candidate-current-overview-v41-inputs")):
        value["schema"] = expected_schema
        value["version"] = 41
        value["candidate_case_producer_status"] = (
            "V4 SOURCE FROZEN; C-ONLY V8/V10 RUNNER FROZEN; "
            "C MATCHING NOT RUN"
        )
        value["required_corrected_candidate_runner_versions"] = ["RUST V6"]
        value["stale_candidate_worker_versions"] = ["RUST V5"]
        value["authenticated_evidence_owner_lower_bound"] = (
            ACTUAL_EVIDENCE_OWNER_COUNT
        )
        value["authenticated_history_reference_lower_bound"] = (
            ACTUAL_AUTHENTICATED_REFERENCE_COUNT
        )
        value["rust_v6_runner_status"] = "UNCOMMITTED"
        value["previous_overview"] = grouped_owners(V40)
    for role in ("source", "inputs", "svg"):
        normalized_summary[role] = grouped_owners(V41)[role]
    original = authenticate_current_v41(
        normalized_summary, normalized_inputs, producer_contract,
        reference_receipt, falsification, build_receipt,
        zig_contract, c_contract,
    )
    return {
        **original,
        "status": "PASS",
        "overview_version": 43,
        "owners": grouped_owners(V43),
        "preserved_v42_overview": grouped_owners(V42),
        "actual_rust_v6_preflight_failure": preserved_failure,
        "first_party_source_inventory_family_count": 6,
        "actually_runnable_candidate_families": [],
        "actually_runnable_candidate_family_count": 0,
        "actual_rust_controller_process_count": 1,
        "actual_rust_source_build_archive_read_count": 1,
        "actual_rust_source_build_archive_gzip_inflation_count": 1,
        "controller_failure_ledger_omits_build_archive_effect": True,
        "authenticated_evidence_owner_lower_bound":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_history_reference_lower_bound":
            CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
    }


def verify_context(source_pin: str, protocol_pin: str,
                   contract_pin: str | None = None,
                   *, retain: bool = False,
                   ledger: dict[str, Any] | None = None
                   ) -> tuple[dict[str, Any], dict[str, Any]]:
    require(ledger is None or type(ledger) is dict,
            "bind retained source-build effects only to a mutable actual ledger")
    require(type(retain) is bool and (not retain or type(ledger) is dict),
            "reject a retained source-build archive before any read "
            "without the mutable actual controller effect ledger")
    verify_runtime()
    source_raw, source_owner = read_owned(
        (SOURCE_RELATIVE, checked_digest(source_pin, "V4 campaign source"),
         _exact_source_size(source_pin)), maximum=MAX_SOURCE_BYTES)
    del source_raw
    protocol_raw, protocol_owner = read_owned(
        (PROTOCOL_RELATIVE, checked_digest(protocol_pin, "V4 campaign protocol"),
         _exact_protocol_size(protocol_pin)), maximum=MAX_SOURCE_BYTES)
    del protocol_raw
    frozen_owner: dict[str, Any] | None = None
    if contract_pin is not None:
        raw, frozen_owner = read_owned(
            (CONTRACT_RELATIVE, checked_digest(contract_pin, "V4 campaign contract"),
             _exact_contract_size(contract_pin)), maximum=MAX_SOURCE_BYTES)
        validate_contract(strict_document(raw, "frozen Rust V4 machine contract"),
                          source_pin, protocol_pin)
    authenticated: dict[str, dict[str, Any]] = {}
    content: dict[str, bytes] = {}
    for group in (PRODUCER, PUBLICATION, V2, V3, V4, V35, V39, V40,
                  V41, V42, V43, V6_PREDECESSOR,
                  ACTUAL_V6_PREFLIGHT_FAILURE, CORRECTED_C_ONLY_V10,
                  BUILD, PUBLIC_REPAIR, REFERENCE, CORRECTED_REFERENCE,
                  ZIG_PHRASE_V3, IMMUTABLE_GOAL):
        for item in group.values():
            if (item[0] in authenticated
                    or item[0] == BUILD["archive"][0]
                    or item[0] == CORRECTED_REFERENCE["archive"][0]):
                continue
            maximum = (
                MAX_RECEIPT_BYTES
                if item in (BUILD["receipt"], REFERENCE["receipt"],
                            CORRECTED_REFERENCE["receipt"])
                else MAX_GRAPH_BYTES
                if (item in V35.values() or item in V39.values()
                    or item in V40.values() or item in V41.values()
                    or item in V42.values() or item in V43.values())
                else MAX_SOURCE_BYTES
            )
            private = item in (
                BUILD["receipt"], REFERENCE["receipt"],
                CORRECTED_REFERENCE["receipt"],
            )
            raw, owner = read_owned(item, maximum=maximum, private=private)
            authenticated[item[0]] = owner
            content[item[0]] = raw
    # This genuine whole-source AST and frozen contract must pass before
    # retain=True can open, read, or inflate the historical build archive.
    historical_v2_contract = strict_document(
        content[V2["contract"][0]],
        "exact separately frozen immutable historical V2 helper contract",
    )
    historical_v2_helper = authenticate_historical_v2_helper_source(
        content[V2["source"][0]], historical_v2_contract,
    )
    actual_v6_failure = strict_document(
        content[ACTUAL_V6_PREFLIGHT_FAILURE["failure"][0]],
        "complete one-time actual V6 controller preactivation failure",
    )
    actual_v6_observation = strict_document(
        content[ACTUAL_V6_PREFLIGHT_FAILURE["observation"][0]],
        "complete independently observed V6 source-build archive effect",
        exact=False,
    )
    observed_v6_failure = authenticate_actual_v6_entry_failure(
        actual_v6_failure, actual_v6_observation,
    )
    previous_raw, previous_owner = read_owned(
        HISTORICAL_RUST_RECEIPT, maximum=MAX_RECEIPT_BYTES, private=True)
    authenticated[HISTORICAL_RUST_RECEIPT[0]] = previous_owner
    previous = strict_document(previous_raw, "exact historical Rust V4 failure receipt")
    summary = strict_document(content[V35["summary"][0]], "actual V35 summary")
    graph_inputs = strict_document(content[V35["inputs"][0]], "actual V35 inputs")
    history = authenticate_v35(summary, graph_inputs, previous)
    supplementary = authenticate_supplementary_reference(
        strict_document(content[REFERENCE["receipt"][0]],
                        "actual successful two-worker CPython reference"),
        strict_document(content[REFERENCE["contract"][0]],
                        "historical frozen V2 two-worker reference policy"))
    build_receipt = strict_document(
        content[BUILD["receipt"][0]], "actual durable V13 build receipt")
    published_build = authenticate_published_v13_build_receipt(build_receipt)
    if retain:
        if ledger is not None:
            ledger["v13_source_build_archive_read_attempted"] = True
            ledger["v13_source_build_archive_read_status"] = (
                "ATTEMPTED; OUTCOME UNKNOWN"
            )
        compressed, archive_owner = read_owned(
            BUILD["archive"], maximum=MAX_BUILD_ARCHIVE_BYTES, private=True,
        )
        if ledger is not None:
            ledger["v13_source_build_archive_read_count"] += 1
            ledger["v13_source_build_archive_compressed_bytes_read"] += (
                len(compressed)
            )
            ledger["v13_source_build_archive_read_status"] = "PASS"
        require(
            (archive_owner["device"], archive_owner["inode"])
            != (authenticated[BUILD["receipt"][0]]["device"],
                authenticated[BUILD["receipt"][0]]["inode"]),
            "require independently durable V13 build archive and receipt",
        )
        if ledger is not None:
            ledger["v13_source_build_archive_gzip_inflation_attempted"] = True
            ledger["v13_source_build_archive_gzip_inflation_status"] = (
                "ATTEMPTED; OUTCOME UNKNOWN"
            )
        plain = bounded_build_gzip(
            compressed,
            expected_sha256=V13_PLAIN_SHA256,
            expected_size=V13_PLAIN_BYTES,
        )
        if ledger is not None:
            ledger["v13_source_build_archive_gzip_inflation_count"] += 1
            ledger["v13_source_build_archive_uncompressed_bytes_read"] += (
                len(plain)
            )
            ledger["v13_source_build_archive_uncompressed_sha256"] = (
                digest(plain)
            )
            ledger["v13_source_build_archive_gzip_inflation_status"] = (
                "PASS"
            )
        report = strict_document(
            plain, "complete bounded actual first-party V13 build",
        )
        build = validate_v13_report(
            report, build_receipt, archive_owner, inspect_private=True,
        )
    else:
        build = published_build
    build_contract = strict_document(content[BUILD["contract"][0]],
                                     "exact committed V13 source-build contract")
    require(build_contract.get("schema")
            == "rebar-phase2-owned-rust-pattern-repr-source-build-v13-source-freeze"
            and build_contract.get("version") == 13
            and build_contract.get("source", {}).get("sha256")
            == BUILD["source"][1]
            and build_contract.get("protocol", {}).get("sha256")
            == BUILD["protocol"][1]
            and build_contract.get("oracle", {})
            .get("case_execution_denominator") == CASE_COUNT
            and build_contract.get("oracle", {})
            .get("supplementary_signature_reference_status") == "PASS"
            and build_contract.get("oracle", {})
            .get("supplementary_signature_reference_cases_executed")
            == SUPPLEMENT_CASE_COUNT
            and build_contract.get("oracle", {})
            .get("supplementary_signature_candidate_status") == "NOT RUN"
            and build_contract.get("corrected_first_party_public_overlay", {})
            .get("derived", {}).get("sha256") == CORRECTED_PUBLIC_SHA256
            and build_contract.get("corrected_first_party_public_overlay", {})
            .get("derived", {}).get("bytes") == CORRECTED_PUBLIC_BYTES
            and build_contract.get("future_native_build", {})
            .get("total_actual_processes_required") == 28,
            "bind matching only to the actually committed V13 build source")
    old_contract = strict_document(content[V3["contract"][0]],
                                   "unchanged historical Rust V3 source freeze")
    require(old_contract.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v3-recoverable-source-freeze"
            and old_contract.get("version") == 3
            and old_contract.get("family") == FAMILY
            and old_contract.get("source", {}).get("sha256") == V3["source"][1]
            and old_contract.get("protocol", {}).get("sha256")
            == V3["protocol"][1]
            and old_contract.get("original_oracle", {}).get("suite_count")
            == SUITE_COUNT
            and old_contract["original_oracle"].get("case_execution_denominator")
            == CASE_COUNT
            and old_contract["original_oracle"].get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and old_contract["original_oracle"].get("nested_interpreter_events")
            == 394,
            "preserve the actual committed original Rust recovery freeze")
    mature = strict_document(content[V4["contract"][0]],
                             "committed mature four-role Rust V4 recovery")
    require(mature.get("schema")
            == "rebar-owned-repaired-rust-original-campaign-v4-recoverable-source-freeze"
            and mature.get("version") == 4
            and mature.get("family") == FAMILY
            and mature.get("source", {}).get("sha256") == V4["source"][1]
            and mature.get("protocol", {}).get("sha256")
            == V4["protocol"][1]
            and mature.get("original_oracle", {}).get("suite_count")
            == SUITE_COUNT
            and mature.get("original_oracle", {})
            .get("case_execution_denominator") == CASE_COUNT
            and mature.get("original_oracle", {})
            .get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
            and mature.get("public_recovery", {}).get("role_order")
            == list(ROLE_ORDER)
            and mature.get("public_recovery", {}).get("restoration_order")
            == list(RESTORATION_ORDER)
            and mature.get("public_recovery", {}).get("group_atomic")
            is False,
            "preserve the entire separately committed mature V4 recovery")
    producer_contract = strict_document(
        content[PRODUCER["contract"][0]],
        "immutable corrected six-family original V4 P0 producer",
    )
    corrected_reference_receipt = strict_document(
        content[CORRECTED_REFERENCE["receipt"][0]],
        "actual two-worker corrected candidate-context reference receipt",
    )
    corrected_reference_contract = strict_document(
        content[CORRECTED_REFERENCE["contract"][0]],
        "historical frozen corrected-reference source contract",
    )
    reference_falsification = strict_document(
        content[CORRECTED_REFERENCE["falsification"][0]],
        "preserved real 96-case candidate-context reference falsification",
        exact=False,
    )
    corrected_reference = authenticate_corrected_candidate_reference(
        corrected_reference_receipt, corrected_reference_contract,
        reference_falsification, producer_contract,
    )
    historical_v39_summary = strict_document(
        content[V39["summary"][0]],
        "exact preserved corrected-whitespace V39 summary",
    )
    historical_v39_inputs = strict_document(
        content[V39["inputs"][0]],
        "exact preserved corrected-whitespace V39 inputs",
    )
    preserved_v39_graph = authenticate_preserved_v39(
        historical_v39_summary, historical_v39_inputs, producer_contract,
        corrected_reference_receipt, reference_falsification,
        build_receipt,
    )
    historical_v40_summary = strict_document(
        content[V40["summary"][0]],
        "exact preserved committed and pushed V40 summary",
    )
    historical_v40_inputs = strict_document(
        content[V40["inputs"][0]],
        "exact preserved committed and pushed V40 inputs",
    )
    zig_source_contract = strict_document(
        content[ZIG_PHRASE_V3["contract"][0]],
        "exact frozen but unapplied first-party Zig scanner phrase source",
    )
    preserved_v40_graph = authenticate_current_v40(
        historical_v40_summary, historical_v40_inputs, producer_contract,
        corrected_reference_receipt, reference_falsification,
        build_receipt, zig_source_contract,
    )
    historical_v41_summary = strict_document(
        content[V41["summary"][0]],
        "exact preserved committed and pushed V41 summary",
    )
    historical_v41_inputs = strict_document(
        content[V41["inputs"][0]],
        "exact preserved committed and pushed V41 inputs",
    )
    c_only_contract = strict_document(
        content[CORRECTED_C_ONLY_V10["contract"][0]],
        "complete committed and pushed C-only V8/V10 runner contract",
    )
    preserved_v41_graph = authenticate_current_v41(
        historical_v41_summary, historical_v41_inputs, producer_contract,
        corrected_reference_receipt, reference_falsification,
        build_receipt, zig_source_contract, c_only_contract,
    )
    predecessor_contract = strict_document(
        content[V6_PREDECESSOR["contract"][0]],
        "complete immutable actually failed V6 source contract",
    )
    historical_v42_summary = strict_document(
        content[V42["summary"][0]],
        "exact preserved committed and pushed V42 summary",
    )
    historical_v42_inputs = strict_document(
        content[V42["inputs"][0]],
        "exact preserved committed and pushed V42 inputs",
    )
    preserved_v42_graph = authenticate_preserved_v42(
        historical_v42_summary, historical_v42_inputs,
        predecessor_contract, c_only_contract,
    )
    current_summary = strict_document(
        content[V43["summary"][0]],
        "exact current committed and pushed V43 summary",
    )
    current_inputs = strict_document(
        content[V43["inputs"][0]],
        "exact current committed and pushed V43 inputs",
    )
    current_graph = authenticate_current_v43(
        current_summary, current_inputs, producer_contract,
        corrected_reference_receipt, reference_falsification,
        build_receipt, zig_source_contract, c_only_contract,
        predecessor_contract, actual_v6_failure, actual_v6_observation,
    )
    repair_contract = strict_document(content[PUBLIC_REPAIR["contract"][0]],
                                      "exact corrected private public repair")
    require(repair_contract.get("schema")
            == "rebar-phase2-owned-rust-public-contract-source-repair-v3-source-freeze"
            and type(repair_contract.get("repair")) is dict
            and type(repair_contract["repair"].get("derived")) is dict
            and repair_contract["repair"]["derived"].get("sha256")
            == CORRECTED_PUBLIC_SHA256
            and repair_contract["repair"]["derived"].get("bytes")
            == CORRECTED_PUBLIC_BYTES
            and repair_contract["repair"]["derived"].get("materialized")
            is False
            and repair_contract["repair"]["derived"].get("path")
            == "candidates/rust_candidate.py",
            "bind actual matching only to the actual corrected V3 d47a adapter")
    require(not any(name == "candidates" or name.startswith("candidates.")
                    for name in sys.modules),
            "read-only verification may never import a candidate")
    result = {
        "schema": SCHEMA + "-read-only-frozen-context",
        "status": "PASS", "version": 7, "family": FAMILY,
        "mode": "READ-ONLY CORRECTED V13 ORIGINAL RUST SOURCE FREEZE",
        "source": source_owner, "protocol": protocol_owner,
        "contract": frozen_owner,
        "authenticated_support_owner_count": len(authenticated) + 1,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "source_ordered_suites": [
            {"id": name, "case_execution_count": count}
            for name, count in SUITES
        ],
        "original_producer_source_sha256": PRODUCER["source"][1],
        "original_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_producer_contract_sha256": PRODUCER["contract"][1],
        "original_producer_version": 4,
        "published_current_v43_overview": current_graph,
        "preserved_v42_overview": preserved_v42_graph,
        "preserved_v41_overview": preserved_v41_graph,
        "historical_v2_helper_source": historical_v2_helper,
        "preserved_actual_v6_preflight_failure": observed_v6_failure,
        "preserved_v40_overview": preserved_v40_graph,
        "preserved_v39_overview": preserved_v39_graph,
        "corrected_candidate_context_reference": corrected_reference,
        "immutable_goal": authenticated[IMMUTABLE_GOAL["goal"][0]],
        "corrected_reference_source_sha256":
            CORRECTED_REFERENCE["source"][1],
        "corrected_reference_protocol_sha256":
            CORRECTED_REFERENCE["protocol"][1],
        "corrected_reference_contract_sha256":
            CORRECTED_REFERENCE["contract"][1],
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_receipt_bytes_read":
            CORRECTED_REFERENCE["receipt"][2],
        "corrected_reference_archive_sha256":
            CORRECTED_REFERENCE["archive"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_case_count_per_worker":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "historical_reference_falsification_sha256":
            CORRECTED_REFERENCE["falsification"][1],
        "historical_falsified_script_context_records_sha256":
            HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v13_build_archive_bytes": BUILD["archive"][2],
        "actual_v13_build_uncompressed_bytes": V13_PLAIN_BYTES,
        "actual_v13_build_uncompressed_sha256": V13_PLAIN_SHA256,
        "actual_v13_build_phase_count": 2,
        "actual_v13_compiler_process_count": build["actual_process_count"],
        "actual_v13_corrected_public_overlay_count": 2,
        "actual_v13_bridge_overlay_count": 2,
        "actual_v13_source_owner_count_per_phase": 9,
        "actual_v13_independent_native_roles": 2,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_engine_bytes": ENGINE_BYTES,
        "native_bridge_bytes": BRIDGE_BYTES,
        "actual_evidence_owner_count_before_new_campaign":
        CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_authenticated_reference_count_before_new_campaign":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "repository_evidence_owner_lower_bound":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_reference_lower_bound":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "later_append_only_evidence_allowed": True,
        "new_v13_build_evidence_owner_count": 2,
        "new_campaign_evidence_owner_count": 0,
        "published_v35_evidence_owner_count": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "published_v35_authenticated_reference_count":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "preserved_history": history,
        "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
        SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
        SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_reference_process_ids": [81, 82],
        "supplementary_signature_reference_failure_count": 0,
        "supplementary_signature_candidate_status": "NOT RUN",
        "supplementary_signature_candidate_cases_executed": 0,
        "supplementary_signature_reference_receipt_sha256":
        REFERENCE["receipt"][1],
        "supplementary_signature_reference_archive_opened": False,
        "supplementary_signature_reference_archive_decompressed": False,
        "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
        "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
        "actual_v13_private_build_root": ACTUAL_V13_PRIVATE_ROOT,
        "actual_v13_native_identities": {
            name: {role: {"device": identity[0], "inode": identity[1]}
                   for role, identity in roles.items()}
            for name, roles in ACTUAL_V13_NATIVE_IDENTITIES.items()
        },
        "historical_rust_failure_receipt_sha256":
        HISTORICAL_RUST_RECEIPT[1],
        "historical_rust_failure_archive_sha256":
        HISTORICAL_RUST_ARCHIVE_SHA256,
        "historical_rust_failure_archive_decompressed": False,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "original_target_count": len(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "nested_case_count": 128,
        "nested_interpreter_event_count": 394,
        "nested_interpreters_created": 11,
        "group_atomic": False,
        **zero_effects(),
        "v13_source_build_archive_gzip_inflation_count":
            1 if retain else 0,
        "v13_source_build_archive_compressed_bytes_read":
            BUILD["archive"][2] if retain else 0,
        "v13_source_build_archive_uncompressed_bytes_read":
            V13_PLAIN_BYTES if retain else 0,
        "v13_source_build_archive_uncompressed_sha256":
            V13_PLAIN_SHA256 if retain else "NOT READ",
        "v13_source_build_receipt_bytes_read": BUILD["receipt"][2],
        "source_context_opens_any_archive": retain,
        "phase1_reference_archive_bytes_read": 0,
        "phase1_reference_archive_decompressed": False,
        "corrected_reference_archive_bytes_read": 0,
        "corrected_reference_archive_decompressed": False,
        "matching_archive_gzip_inflation_count": 0,
        "matching_archive_bytes_read": 0,
        "all_candidate_matching_blocked": True,
    }
    kept = {
        "build": build,
        "summary": current_summary,
        "previous_summary": historical_v42_summary,
        "historical_v41_summary": historical_v41_summary,
        "historical_v40_summary": historical_v40_summary,
        "historical_v39_summary": historical_v39_summary,
        "historical_v35_summary": summary,
        "published_current_v43_overview": current_graph,
        "preserved_v42_overview": preserved_v42_graph,
        "preserved_v41_overview": preserved_v41_graph,
        "historical_v2_helper_source": historical_v2_helper,
        "preserved_actual_v6_preflight_failure": observed_v6_failure,
        "preserved_v40_overview": preserved_v40_graph,
        "preserved_v39_overview": preserved_v39_graph,
        "corrected_reference": corrected_reference,
        "corrected_reference_receipt": corrected_reference_receipt,
        "corrected_producer_contract": producer_contract,
        "supplementary_reference": supplementary,
        "historical_receipt": previous,
        "owners": authenticated,
    } if retain else {}
    return result, kept


def _exact_source_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / SOURCE_RELATIVE))


def _exact_protocol_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / PROTOCOL_RELATIVE))


def _exact_contract_size(fingerprint: str) -> int:
    del fingerprint
    return os.path.getsize(str(ROOT / CONTRACT_RELATIVE))


class SourceWall:
    """Deny all real I/O, imports, native loaders, processes and clocks."""

    def __init__(self) -> None:
        self.blocked: dict[str, int] = {}
        self.originals: list[tuple[Any, str, Any]] = []

    def install(self, owner: Any, name: str, counter: str) -> None:
        if not hasattr(owner, name):
            return
        previous = getattr(owner, name)

        def blocked(*args: Any, **kwargs: Any) -> Any:
            del args, kwargs
            self.blocked[counter] = self.blocked.get(counter, 0) + 1
            raise SourceOnlyViolation(
                "source-only V7 blocks actual " + counter + ": " + name
            )

        self.originals.append((owner, name, previous))
        setattr(owner, name, blocked)

    def __enter__(self) -> SourceWall:
        actions: list[tuple[Any, tuple[str, ...], str]] = [
            (builtins, ("open",), "filesystem_reads"),
            (builtins, ("__import__",), "candidate_imports"),
            (io, ("open",), "filesystem_reads"),
            (os, ("open", "read", "stat", "lstat", "scandir",
                  "listdir"), "filesystem_reads"),
            (Path, ("open", "read_bytes", "read_text", "stat",
                    "lstat", "resolve"), "filesystem_reads"),
            (os, ("write", "unlink", "remove", "rename", "replace",
                  "link", "symlink", "mkdir", "makedirs", "rmdir",
                  "fsync", "fchmod", "urandom"),
             "filesystem_mutations"),
            (Path, ("write_bytes", "write_text", "mkdir", "unlink",
                    "rename", "replace", "touch"),
             "filesystem_mutations"),
            (subprocess, ("run", "Popen", "call", "check_call",
                          "check_output", "_fork_exec"),
             "processes"),
            (os, ("fork", "system", "posix_spawn", "posix_spawnp",
                  "execv", "execve", "execl", "execle", "execlp",
                  "execlpe", "execvp", "execvpe", "spawnv", "spawnve",
                  "spawnvp", "spawnvpe"), "processes"),
            (importlib, ("import_module",), "candidate_imports"),
            (importlib.machinery.SourceFileLoader,
             ("create_module", "exec_module", "load_module"),
             "candidate_imports"),
            (importlib.machinery.SourcelessFileLoader,
             ("create_module", "exec_module", "load_module"),
             "candidate_imports"),
            (importlib.machinery.ExtensionFileLoader,
             ("create_module", "exec_module", "load_module"),
             "native_library_loads"),
            (importlib.machinery.BuiltinImporter,
             ("create_module", "exec_module", "load_module"),
             "native_library_loads"),
            (importlib.machinery.FrozenImporter,
             ("create_module", "exec_module", "load_module"),
             "candidate_imports"),
            (ctypes, ("CDLL", "PyDLL", "_dlopen"),
             "native_library_loads"),
            (tempfile, ("mkdtemp", "mkstemp", "TemporaryFile",
                        "NamedTemporaryFile"), "recovery_roots"),
            (socket, ("socket", "create_connection", "getaddrinfo"),
             "network_requests"),
            (threading, ("_start_joinable_thread", "_start_new_thread"),
             "threads"),
            (threading.Thread, ("start",), "threads"),
            (locale, ("setlocale",), "locale_transitions"),
            (signal, ("signal", "raise_signal"), "signal_handlers"),
            (signal, ("pthread_sigmask",), "signal_masks"),
            (fcntl, ("flock", "lockf"), "recovery_locks"),
            (gzip, ("open", "decompress"),
             "actual_archive_operations"),
            (time, ("time", "time_ns", "monotonic", "monotonic_ns",
                    "perf_counter", "perf_counter_ns", "process_time",
                    "process_time_ns", "thread_time", "thread_time_ns",
                    "sleep"), "clocks"),
        ]
        for module_name, names, counter in (
            ("_io", ("open",), "filesystem_reads"),
            ("posix", ("open", "read", "stat", "lstat", "scandir",
                       "listdir"), "filesystem_reads"),
            ("posix", ("write", "unlink", "remove", "rename", "replace",
                       "link", "symlink", "mkdir", "rmdir", "fsync"),
             "filesystem_mutations"),
            ("posix", ("fork", "posix_spawn", "posix_spawnp",
                       "execv", "execve", "spawnv", "spawnve"),
             "processes"),
            ("_posixsubprocess", ("fork_exec",), "processes"),
            ("_ctypes", ("dlopen",), "native_library_loads"),
            ("_imp", ("create_dynamic", "exec_dynamic", "create_builtin",
                      "exec_builtin", "init_frozen"),
             "native_library_loads"),
            ("_socket", ("socket", "getaddrinfo"), "network_requests"),
            ("_thread", ("start_new_thread", "start_joinable_thread"),
             "threads"),
        ):
            module = sys.modules.get(module_name)
            if module is not None:
                actions.append((module, names, counter))
        for owner, names, counter in actions:
            for name in names:
                self.install(owner, name, counter)
        original_gzip_file = gzip.GzipFile

        def memory_only_gzip_file(*args: Any, **kwargs: Any) -> Any:
            filename = kwargs.get("filename", args[0] if args else None)
            file_object = kwargs.get("fileobj")
            if filename is None and type(file_object) is io.BytesIO:
                return original_gzip_file(*args, **kwargs)
            counter = "actual_archive_operations"
            self.blocked[counter] = self.blocked.get(counter, 0) + 1
            raise SourceOnlyViolation(
                "source-only V7 blocks actual archive-backed GzipFile"
            )

        self.originals.append((gzip, "GzipFile", original_gzip_file))
        gzip.GzipFile = memory_only_gzip_file
        return self

    def __exit__(self, kind: Any, value: Any, detail: Any) -> bool:
        del kind, value, detail
        for owner, name, original in reversed(self.originals):
            setattr(owner, name, original)
        return False


def _expect_rejected(name: str, operation: Any,
                     rejected: list[str]) -> None:
    try:
        operation()
    except (CampaignError, ValueError, TypeError, OverflowError,
            UnicodeError, RecursionError):
        rejected.append(name)
        return
    raise CampaignError("accepted hostile source-only case: " + name)


def _synthetic_stream(name: str, channel: str) -> dict[str, Any]:
    raw = ("synthetic-v13-" + name + "-" + channel).encode("ascii")
    return {channel + "_base64": base64.b64encode(raw).decode("ascii"),
            channel + "_bytes": len(raw),
            channel + "_sha256": digest(raw)}


def synthetic_v13_fixture() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    phases = []
    process_records = []
    root = "/tmp/rebar-phase2-native-build-v9-rust-synthetic-v5"
    for phase_index, phase_name in enumerate(PHASE_NAMES):
        sources: dict[str, Any] = {}
        for index, (relative, fingerprint, count) in enumerate(
                CORRECTED_SOURCE_OWNERS):
            row: dict[str, Any] = {
                "path": "<FRESH_PRIVATE_TMP>/" + phase_name
                + "/source/" + relative,
                "sha256": fingerprint, "bytes": count,
                "device": 2049, "inode": 100000 + phase_index * 100 + index,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": relative in {
                    "candidates/rust_candidate.py", "candidates/rust/py_bridge.c"},
            }
            if relative == "candidates/rust_candidate.py":
                row["source_overlay"] = {
                    "schema": "rebar-phase2-owned-rust-public-contract-source-repair-v3-private-source-application",
                    "status": "PASS", "phase": phase_name,
                    "source_apply_count": 1,
                    "snapshot_root": root + "/" + phase_name + "/source",
                    "source_sha256": PUBLIC_REPAIR["source"][1],
                    "protocol_sha256": PUBLIC_REPAIR["protocol"][1],
                    "contract_sha256": PUBLIC_REPAIR["contract"][1],
                    "derived_source_sha256": CORRECTED_PUBLIC_SHA256,
                    "derived_source_bytes": CORRECTED_PUBLIC_BYTES,
                    "candidate_imports": 0,
                    "canonical_candidate_modified": False,
                }
            elif relative == "candidates/rust/py_bridge.c":
                row["source_overlay"] = {
                    "status": "PASS", "phase": phase_name,
                    "source_apply_count": 1,
                    "snapshot_root": root + "/" + phase_name + "/source",
                    "derived_sha256": BRIDGE_SOURCE_SHA256,
                    "derived_bytes": BRIDGE_SOURCE_BYTES,
                    "candidate_imports": 0,
                    "candidate_original_modified": False,
                }
            sources[relative] = row
        outputs: dict[str, Any] = {}
        for offset, (role, fingerprint, count, filename) in enumerate((
            ("engine", ENGINE_SHA256, ENGINE_BYTES, "_rust_engine.so"),
            ("bridge", BRIDGE_SHA256, BRIDGE_BYTES,
             "_rust_bridge.cpython-314-x86_64-linux-gnu.so"),
        )):
            audit = {
                "role": role,
                "cross_family_dependency_count": 0,
                "external_regex_dependency_count": 0,
                "exports": (list(RUST_EXPORTS) if role == "engine"
                            else ["PyInit__rust_bridge"]),
                "required_exports": (list(RUST_EXPORTS) if role == "engine"
                                     else ["PyInit__rust_bridge"]),
                "needed": (["ld-linux-x86-64.so.2", "libc.so.6",
                            "libgcc_s.so.1"] if role == "engine"
                           else ["_rust_engine.so", "libc.so.6"]),
                "runpath": ([] if role == "engine" else ["$ORIGIN"]),
            }
            outputs[role] = {
                "family": FAMILY, "role": role, "sha256": fingerprint,
                "size_bytes": count, "device": 2049,
                "inode": 200000 + phase_index * 100 + offset,
                "file_name": filename,
                "path": "<FRESH_PRIVATE_TMP>/" + phase_name
                + "/native/" + filename,
                "candidate_imported": False,
                "prebuilt_artifact_read": False,
                "audit": audit,
            }
        phases.append({
            "name": phase_name,
            "fresh_source_owners": sources,
            "native_outputs": outputs,
            "native_forensics": {
                role: {"sections": {}, "notes": {}, "raw_elf64": {}}
                for role in ("engine", "bridge")
            },
            "candidate_imports": 0, "candidate_processes_started": 0,
            "hidden_cases_read": 0, "timing_trials_run": 0,
            "native_libraries_loaded": 0,
        })
        for offset, name in enumerate(PROCESS_NAMES):
            record = {
                "name": name, "pid": 300000 + phase_index * 100 + offset,
                "exit_status": 0, "shell": False,
                "argv": ["/independently-pinned-synthetic/" + name],
                **_synthetic_stream(name, "stdout"),
                **_synthetic_stream(name, "stderr"),
            }
            process_records.append(record)
    previous = {
        "status": "PASS", "version": 13, "family": FAMILY,
        "repository_evidence_owner_lower_bound": PREVIOUS_EVIDENCE_OWNER_COUNT,
        "authenticated_reference_lower_bound":
        PREVIOUS_AUTHENTICATED_REFERENCE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "suite_count": SUITE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "actual_rust_semantic_mismatch_count": 1036,
        "actual_rust_verified_passing_case_count": 8965,
        "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
        "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "actual_zig_v3_matching_status": "FAIL",
        "actual_zig_v3_semantic_mismatch_count": 1764,
        "actual_zig_v3_verified_passing_case_count": 3711,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
        SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
        SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_candidate_status": "NOT RUN",
        "qualified_candidate_count": 0,
        "corrected_public_derived_source_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_public_derived_source_bytes": CORRECTED_PUBLIC_BYTES,
        "bridge_derived_source_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_derived_source_bytes": BRIDGE_SOURCE_BYTES,
        "candidate_imports": 0,
        "canonical_native_target_reads": 0,
        "canonical_native_target_stats": 0,
        "native_activations": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "holdout": "NOT OPENED",
    }
    reproduction = {
        "status": "PASS", "byte_identical": True,
        "independent_fresh_phase_count": 2,
        "unique_process_count": 28,
        "native_role_count": 2,
        "source_owners_per_phase": 9,
        "unchanged_source_owners_per_phase": 7,
        "corrected_public_overlay_count": 2,
        "bridge_overlay_count": 2,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "native_libraries_loaded": 0,
        "original_sources_modified": False,
        "prebuilt_artifact_count": 0,
        "native_outputs": {
            "engine": {"sha256": ENGINE_SHA256, "size_bytes": ENGINE_BYTES,
                       "fresh_independent_inode_count": 2},
            "bridge": {"sha256": BRIDGE_SHA256, "size_bytes": BRIDGE_BYTES,
                       "fresh_independent_inode_count": 2},
        },
        "raw_elf_comparisons": {
            role: {
             "schema": "rebar-phase2-owned-native-source-build-v7-complete-raw-elf-difference",
             "byte_identical": True,
             "phase_a_sha256": fingerprint, "phase_b_sha256": fingerprint,
             "phase_a_bytes": size, "phase_b_bytes": size,
             "changed_section_count": 0, "changed_sections": [],
             "total_difference_span_count": 0,
             "total_differing_byte_count": 0, "difference_spans": [],
             "reported_span_count": 0, "omitted_span_count": 0,
             "report_truncated": False}
            for role, fingerprint, size in (
                ("bridge", BRIDGE_SHA256, BRIDGE_BYTES),
                ("engine", ENGINE_SHA256, ENGINE_BYTES),
            )
        },
    }
    archive_owner = {
        "path": str(ROOT / BUILD["archive"][0]),
        "relative": BUILD["archive"][0],
        "sha256": BUILD["archive"][1], "bytes": BUILD["archive"][2],
        "size_bytes": BUILD["archive"][2], "device": 2064,
        "inode": 524714, "mode": 0o600, "uid": 1000, "nlink": 1,
    }
    report = {
        "schema": "rebar-phase2-owned-rust-pattern-repr-source-build-v13-actual-corrected-dual-overlay-build",
        "status": "PASS", "version": 13, "family": FAMILY,
        "label": LABEL, "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "phase_count": 2,
        "expected_actual_compiler_process_count": 28,
        "actual_compiler_process_count": 28,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "historical_public_derived_sha256": HISTORICAL_DERIVED_PUBLIC_SHA256,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_overlay_apply_count": 2,
        "frozen_context": previous,
        "compiler_processes": process_records,
        "phases": phases, "reproducibility": reproduction,
        "candidate_correctness": "NOT MEASURED", "candidate_qualified": False,
        "candidate_processes_started": 0, "candidate_imports": 0,
        "native_libraries_loaded": 0, "hidden_cases_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    receipt = {
        "schema": "rebar-phase2-owned-rust-pattern-repr-source-build-v13-durable-publication-receipt",
        "status": "PASS", "build_status": "PASS", "family": FAMILY,
        "label": LABEL, "source_sha256": BUILD["source"][1],
        "protocol_sha256": BUILD["protocol"][1],
        "contract_sha256": BUILD["contract"][1],
        "archive_relative": BUILD["archive"][0],
        "archive_sha256": BUILD["archive"][1],
        "archive_bytes": BUILD["archive"][2],
        "archive_publication": {
            "path": archive_owner["path"],
            "sha256": archive_owner["sha256"],
            "bytes": archive_owner["bytes"],
            "device": archive_owner["device"],
            "inode": archive_owner["inode"],
            "exclusive_creation": True,
            "same_inode_readback_verified": True,
            "file_fsync_completed": True,
            "write_calls": 1,
        },
        "archive_directory_fsync": {"completed": True},
        "uncompressed_sha256": V13_PLAIN_SHA256,
        "uncompressed_bytes": V13_PLAIN_BYTES,
        "public_derived_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_public_overlay_apply_count": 2,
        "bridge_derived_sha256": BRIDGE_SOURCE_SHA256,
        "bridge_overlay_apply_count": 2,
        "actual_compiler_process_count": 28,
        "expected_actual_compiler_process_count": 28,
        "candidate_correctness": "NOT MEASURED",
        "candidate_processes_started": 0,
        "candidate_imports": 0, "native_libraries_loaded": 0,
        "hidden_cases_read": 0, "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
    }
    return report, receipt, archive_owner


def synthetic_original_worker_document(name: str, count: int,
                                       *, mismatches: int = 0
                                       ) -> dict[str, Any]:
    status = "PASS" if mismatches == 0 else "FAIL"
    original = {
        "schema": "rebar-owned-six-family-original-p0-producer-v4"
        + "-actual-original-suite",
        "status": status,
        "suite": name,
        "candidate_family": FAMILY,
        "case_execution_denominator": count,
        "actual_candidate_case_count": count,
        "mismatch_count": mismatches,
        "all_mismatches": [
            {"case": "synthetic-hostile-control/" + str(index)}
            for index in range(mismatches)
        ],
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "holdout": "NOT OPENED",
    }
    return {
        "schema": WORKER_SCHEMA,
        "status": status,
        "candidate_family": FAMILY,
        "label": LABEL,
        "suite": name,
        "case_execution_denominator": count,
        "actual_candidate_case_count": count,
        "mismatch_count": mismatches,
        "failure_class": "PASS" if mismatches == 0 else "SEMANTIC MISMATCH",
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_version": 4,
        "original_observer_unchanged": True,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "repaired_source_owner_count": 9,
        "corrected_public_source_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "complete_original_observation": stream_observation(original),
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "clock_samples": 0,
        "holdout": "NOT OPENED",
    }


class SyntheticOriginalWorker:
    """An in-memory fake; it has no OS child, descriptor, clock, or target."""

    def __init__(self, *, mode: str, pid: int | None,
                 stdout: bytes, stderr: bytes,
                 returncode: int) -> None:
        self.mode = mode
        self.pid = pid
        self.stdout_bytes = stdout
        self.stderr_bytes = stderr
        self.final_returncode = returncode
        self.returncode: int | None = None
        self.communication_count = 0

    def communicate(self, timeout: int | None = None
                    ) -> tuple[bytes, bytes]:
        self.communication_count += 1
        if self.mode == "post-spawn-exception" and self.communication_count == 1:
            raise OSError("synthetic exception after successful Popen")
        if self.mode == "timeout" and self.communication_count == 1:
            raise subprocess.TimeoutExpired(
                "synthetic-owned-original-worker",
                timeout if timeout is not None else WORKER_TIMEOUT_SECONDS,
                output=b"synthetic partial original stdout",
                stderr=b"synthetic partial original stderr",
            )
        if self.returncode is None:
            self.returncode = self.final_returncode
        return self.stdout_bytes, self.stderr_bytes

    def poll(self) -> int | None:
        return self.returncode

    def kill(self) -> None:
        self.returncode = -9


@contextlib.contextmanager
def synthetic_original_worker_launch(*, mode: str, name: str,
                                     count: int, pid: int | None,
                                     mismatches: int = 0
                                     ) -> Iterator[None]:
    previous = subprocess.Popen
    document = synthetic_original_worker_document(
        name, count, mismatches=mismatches)
    stdout = canonical(document)
    stderr = b""
    returncode = 0 if mismatches == 0 else 1
    if mode == "malformed-json":
        stdout = b'{"duplicate":1,"duplicate":2}\n'
    elif mode == "malformed-gzip":
        broken = copy.deepcopy(document)
        compressed = b"synthetic malformed original gzip"
        observation = broken["complete_original_observation"]
        observation["compressed_base64"] = (
            base64.b64encode(compressed).decode("ascii")
        )
        observation["compressed_bytes"] = len(compressed)
        observation["compressed_sha256"] = digest(compressed)
        stdout = canonical(broken)
    elif mode == "oversized-stdout":
        stdout = b"x" * (MAX_WORKER_STDOUT_BYTES + 1)
    elif mode == "oversized-stderr":
        stderr = b"x" * (MAX_WORKER_STDERR_BYTES + 1)
    elif mode == "crash":
        returncode = -11

    def factory(argv: Any, *args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        require(type(argv) is list and bool(argv) and argv[0] == PYTHON,
                "exercise only an in-memory independently pinned fake Popen")
        if mode == "launch-failure":
            raise OSError("synthetic Popen failed before an OS child existed")
        return SyntheticOriginalWorker(
            mode=mode, pid=pid, stdout=stdout, stderr=stderr,
            returncode=returncode,
        )

    subprocess.Popen = factory
    try:
        yield
    finally:
        subprocess.Popen = previous


def synthetic_complete_publication_controls(
        options: argparse.Namespace,
        complete_rows: Sequence[dict[str, Any]],
        complete_shape: Mapping[str, Any],
        observe: Any,
        accepted: list[str],
        rejected: list[str],
        ) -> dict[str, Any]:
    """Run real publication logic with only distinct in-memory owners."""
    require(
        CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND == 166
        and CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND == 171
        and ACTUAL_EVIDENCE_OWNER_COUNT == 164
        and ACTUAL_AUTHENTICATED_REFERENCE_COUNT == 169
        and len(complete_rows) == SUITE_COUNT
        and complete_shape.get("candidate_qualified") is True,
        "distinguish immutable historical owners from the current V43 graph",
    )
    originals = {
        role: {
            "relative": original["relative"],
            "sha256": original["sha256"],
            "size_bytes": original["bytes"],
            "device": original["device"],
            "inode": original["inode"],
            "mode": original["mode"],
            "uid": original["uid"],
            "nlink": original["nlink"],
        }
        for role, original in ORIGINALS.items()
    }
    base_report: dict[str, Any] = {
        **copy.deepcopy(dict(complete_shape)),
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS",
        "family": FAMILY,
        "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "historical_evidence_owner_count_before_publication":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
            CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "all_four_original_targets_restored": True,
        "restored_original_targets": originals,
        "restoration_verified_before_publication": True,
        "recovery_journal_sha256": "c" * 64,
        "holdout": "NOT OPENED",
    }

    def make_trial(document: dict[str, Any], mode: str = "valid"
                   ) -> tuple[Any, dict[str, Any], dict[str, Any]]:
        state: dict[str, Any] = {
            "directory_open_count": 0,
            "directory_closures": [],
            "archive_documents": [],
            "receipt_documents": [],
        }
        effect = new_campaign_effect_ledger(options)
        effect.update({
            "attempted_suite_count": SUITE_COUNT,
            "started_suite_count": SUITE_COUNT,
            "fully_observed_suite_count": SUITE_COUNT,
            "actual_candidate_workers": SUITE_COUNT,
            "actual_worker_process_ids": list(
                document.get("actual_worker_process_ids", [])
            ),
            "retained_suite_results": copy.deepcopy(
                document.get("suite_results", [])
            ),
            "actual_native_activations": 1,
            "activated_target_roles": list(ROLE_ORDER),
            "canonical_target_replacements": len(ROLE_ORDER),
            "recovery_root_creation_attempted": True,
            "recovery_roots_created": 1,
            "recovery_lock_attempted": True,
            "recovery_locks_acquired": 1,
            "recovery_journal_creation_attempted": True,
            "recovery_journals_created": 1,
            "recovery_journal_sha256": "c" * 64,
            "recovery_journal_announced": True,
            "restoration_attempted": True,
            "restored_target_roles": list(RESTORATION_ORDER),
            "all_four_original_targets_restored": True,
            "restoration_verified": True,
        })

        def open_directory() -> int:
            state["directory_open_count"] += 1
            return 917_001

        def close_directory(descriptor: int) -> None:
            require(descriptor == 917_001,
                    "close only the in-memory synthetic evidence directory")
            state["directory_closures"].append(descriptor)

        def write_archive(value: dict[str, Any], name: str,
                          directory: int
                          ) -> tuple[dict[str, Any], dict[str, Any]]:
            require(value is document and directory == 917_001,
                    "stream only the real in-memory thirteen-suite report")
            if mode == "archive-failure":
                raise CampaignError("synthetic in-memory archive failure")
            raw = canonical(value)
            memory = io.BytesIO()
            with gzip.GzipFile(fileobj=memory, mode="wb", mtime=0) as zipped:
                zipped.write(raw)
            compressed = memory.getvalue()
            archive = {
                "relative": name,
                "path": str(ROOT / EVIDENCE_RELATIVE / name),
                "sha256": digest(compressed),
                "size_bytes": len(compressed),
                "device": 2064,
                "inode": 990_001,
                "mode": 0o600,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "streaming_readback_verified": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True,
                "write_calls": 1,
            }
            if mode == "incomplete-archive-owner":
                archive["directory_fsync_completed"] = False
            if mode == "prefixed-archive-relative":
                archive["relative"] = EVIDENCE_RELATIVE + "/" + name
            if mode == "forged-archive-path":
                archive["path"] = str(ROOT / EVIDENCE_RELATIVE / "forged")
            if mode == "forged-archive-sha256":
                archive["sha256"] = "0" * 64
            if mode == "forged-archive-size":
                archive["size_bytes"] += 1
            if mode == "forged-archive-write-calls":
                archive["write_calls"] = 0
            stream = {
                "gzip_mtime": 0,
                "gzip_single_member": True,
                "uncompressed_bytes": len(raw),
                "uncompressed_sha256": digest(raw),
                "uncompressed_chunk_count": 1,
                "archive_sha256": digest(compressed),
                "archive_bytes": len(compressed),
                "archive_write_calls": 1,
                "canonical_terminal_newline_count": 1,
            }
            state["archive_documents"].append(copy.deepcopy(archive))
            return archive, stream

        def write_receipt(name: str,
                          receipt: dict[str, Any]) -> dict[str, Any]:
            require(name == evidence_names(document["status"] == "FAIL")[1],
                    "publish only the matching synthetic result receipt")
            if mode == "receipt-failure":
                raise CampaignError("synthetic in-memory receipt failure")
            if mode == "fabricated-resulting-evidence-count":
                receipt["resulting_repository_evidence_owner_count"] = (
                    CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
                )
            if mode == "fabricated-resulting-reference-count":
                receipt["resulting_authenticated_reference_count"] = (
                    CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
                )
            state["receipt_documents"].append(copy.deepcopy(receipt))
            raw = canonical(receipt)
            owner = {
                "relative": EVIDENCE_RELATIVE + "/" + name,
                "path": str(ROOT / EVIDENCE_RELATIVE / name),
                "sha256": digest(raw),
                "bytes": len(raw),
                "size_bytes": len(raw),
                "device": 2064,
                "inode": 990_001 if mode == "single-evidence-owner"
                    else 990_002,
                "mode": 0o600,
                "uid": ORIGINALS["adapter"]["uid"],
                "nlink": 1,
                "exclusive_creation": True,
                "same_inode_readback_verified": True,
                "file_fsync_completed": True,
                "directory_fsync_completed": True,
            }
            if mode == "basename-receipt-relative":
                owner["relative"] = name
            if mode == "forged-receipt-path":
                owner["path"] = str(ROOT / EVIDENCE_RELATIVE / "forged")
            if mode == "forged-receipt-sha256":
                owner["sha256"] = "0" * 64
            if mode == "forged-receipt-size":
                owner["size_bytes"] += 1
            if mode == "forged-receipt-uid":
                owner["uid"] += 1
            if mode == "linked-receipt-owner":
                owner["nlink"] = 2
            if mode == "undurable-receipt-owner":
                owner["directory_fsync_completed"] = False
            return owner

        publication = types.SimpleNamespace(
            open_evidence_directory=open_directory,
            write_streamed_archive=write_archive,
        )
        helper = types.SimpleNamespace(
            exact_originals=lambda: copy.deepcopy(originals),
            write_evidence_receipt=write_receipt,
        )

        def run_trial() -> dict[str, Any]:
            return preserve_campaign(
                document,
                {"publication": publication},
                helper,
                effect,
                directory_closer=close_directory,
            )

        return run_trial, state, effect

    success, success_state, success_ledger = make_trial(
        copy.deepcopy(base_report),
    )
    passed = success()
    require(
        passed.get("status") == "PASS"
        and passed.get("publication_status") == "PASS"
        and passed.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and passed.get("suite_count") == SUITE_COUNT
        and passed.get("case_execution_denominator") == CASE_COUNT
        and passed.get("attempted_suite_count") == SUITE_COUNT
        and passed.get("started_suite_count") == SUITE_COUNT
        and passed.get("completed_suite_count") == SUITE_COUNT
        and passed.get("actual_candidate_workers") == SUITE_COUNT
        and passed.get("distinct_worker_process_id_count") == SUITE_COUNT
        and passed.get("all_original_observation_vectors_complete") is True
        and passed.get("candidate_qualified") is True
        and passed.get("historical_evidence_owner_count_before_publication")
        == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
        and passed.get(
            "historical_authenticated_reference_count_before_publication"
        ) == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
        and passed.get("new_repository_evidence_owner_count") == 2
        and passed.get("resulting_repository_evidence_owner_count") == 168
        and passed.get("resulting_authenticated_reference_count") == 173
        and passed.get("all_four_original_targets_restored") is True
        and passed.get("restored_original_targets") == originals
        and success_state["directory_open_count"] == 1
        and success_state["directory_closures"] == [917_001]
        and len(success_state["archive_documents"]) == 1
        and len(success_state["receipt_documents"]) == 1
        and success_state["receipt_documents"][0].get(
            "historical_evidence_owner_count_before_publication"
        ) == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
        and success_state["receipt_documents"][0].get(
            "historical_authenticated_reference_count_before_publication"
        ) == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
        and success_state["receipt_documents"][0].get(
            "new_repository_evidence_owner_count"
        ) == 2
        and success_state["receipt_documents"][0].get(
            "resulting_repository_evidence_owner_count"
        ) == 168
        and success_state["receipt_documents"][0].get(
            "resulting_authenticated_reference_count"
        ) == 173
        and success_ledger.get("archive_publication_status") == "PASS"
        and success_ledger.get("receipt_publication_status") == "PASS"
        and success_ledger.get("publication_status") == "PASS"
        and passed["archive"].get("relative") == evidence_names(False)[0]
        and passed["archive"].get("path")
        == str(ROOT / EVIDENCE_RELATIVE / evidence_names(False)[0])
        and passed["receipt"].get("relative")
        == EVIDENCE_RELATIVE + "/" + evidence_names(False)[1]
        and passed["receipt"].get("path")
        == str(ROOT / EVIDENCE_RELATIVE / evidence_names(False)[1])
        and passed["receipt"].get("sha256")
        == digest(canonical(success_state["receipt_documents"][0]))
        and passed["receipt"].get("bytes")
        == len(canonical(success_state["receipt_documents"][0]))
        and passed["receipt"].get("size_bytes")
        == passed["receipt"].get("bytes")
        and passed["receipt"].get("uid") == ORIGINALS["adapter"]["uid"]
        and passed["receipt"].get("nlink") == 1
        and (passed["archive"]["device"], passed["archive"]["inode"])
        != (passed["receipt"]["device"], passed["receipt"]["inode"]),
        "exercise genuine complete thirteen-worker publication with "
        "166/171 current owners and 168/173 only after two durable owners",
    )
    accepted.append(
        "accept-real-preserve-thirteen-workers-four-inodes-166-171-to-168-173"
    )
    accepted.append(
        "accept-two-distinct-synthetic-durable-publication-owner-inodes"
    )
    accepted.append(
        "accept-exact-real-archive-basename-and-v2-repository-receipt-path"
    )

    failure_row = observe("valid", 0, pid=930_002, mismatches=3)
    failure_shape = aggregate_worker_rows(
        [failure_row, *complete_rows[1:]],
    )
    require(
        failure_shape.get("completed_suite_count") == SUITE_COUNT
        and failure_shape.get("distinct_worker_process_id_count")
        == SUITE_COUNT
        and failure_shape.get("semantic_mismatch_count") == 3
        and failure_shape.get("candidate_qualified") is False,
        "preserve all thirteen complete synthetic semantic-loss vectors",
    )
    failed_report = {
        **copy.deepcopy(base_report),
        **copy.deepcopy(failure_shape),
        "status": "FAIL",
    }
    failure, failure_state, failure_ledger = make_trial(failed_report)
    failed = failure()
    require(
        failed.get("status") == "FAIL"
        and failed.get("publication_status") == "PASS"
        and failed.get("publication_pass_means")
        == "DURABLE PUBLICATION ONLY"
        and failed.get("candidate_qualified") is False
        and failed.get("semantic_mismatch_count") == 3
        and failed.get("completed_suite_count") == SUITE_COUNT
        and failed.get("resulting_repository_evidence_owner_count") == 168
        and failed.get("resulting_authenticated_reference_count") == 173
        and failed.get("archive", {}).get("relative")
        == evidence_names(True)[0]
        and failed.get("receipt", {}).get("relative")
        == EVIDENCE_RELATIVE + "/" + evidence_names(True)[1]
        and failure_state["directory_closures"] == [917_001]
        and failure_ledger.get("publication_status") == "PASS",
        "durably preserve an actual full-denominator semantic loss without "
        "confusing publication with passing candidate correctness",
    )
    accepted.append("accept-real-preserve-complete-semantic-loss-publication")

    prepublication_controls = (
        ("stale-historical-evidence-164",
         "historical_evidence_owner_count_before_publication",
         ACTUAL_EVIDENCE_OWNER_COUNT),
        ("stale-historical-reference-169",
         "historical_authenticated_reference_count_before_publication",
         ACTUAL_AUTHENTICATED_REFERENCE_COUNT),
        ("fabricated-current-evidence-165",
         "historical_evidence_owner_count_before_publication",
         CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND - 1),
        ("fabricated-current-evidence-167",
         "historical_evidence_owner_count_before_publication",
         CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND + 1),
        ("fabricated-current-reference-170",
         "historical_authenticated_reference_count_before_publication",
         CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND - 1),
        ("fabricated-current-reference-172",
         "historical_authenticated_reference_count_before_publication",
         CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND + 1),
        ("unrestored-original-targets",
         "all_four_original_targets_restored", False),
        ("unverified-original-restoration",
         "restoration_verified_before_publication", False),
    )
    for tag, field, forged in prepublication_controls:
        hostile = copy.deepcopy(base_report)
        hostile[field] = forged
        operation, state, effect = make_trial(hostile)
        _expect_rejected(
            "reject-prepublication-" + tag,
            operation,
            rejected,
        )
        require(
            state["directory_open_count"] == 0
            and state["directory_closures"] == []
            and state["archive_documents"] == []
            and state["receipt_documents"] == []
            and effect.get("archive_publication_attempted") is False
            and effect.get("receipt_publication_attempted") is False,
            "reject forged current owners or restoration before publication: "
            + tag,
        )

    publication_hostile_modes = (
        "archive-failure",
        "incomplete-archive-owner",
        "prefixed-archive-relative",
        "forged-archive-path",
        "forged-archive-sha256",
        "forged-archive-size",
        "forged-archive-write-calls",
        "receipt-failure",
        "basename-receipt-relative",
        "forged-receipt-path",
        "forged-receipt-sha256",
        "forged-receipt-size",
        "forged-receipt-uid",
        "linked-receipt-owner",
        "undurable-receipt-owner",
        "single-evidence-owner",
        "fabricated-resulting-evidence-count",
        "fabricated-resulting-reference-count",
    )
    for mode in publication_hostile_modes:
        operation, state, effect = make_trial(
            copy.deepcopy(base_report),
            mode,
        )
        _expect_rejected(
            "reject-complete-publication-" + mode,
            operation,
            rejected,
        )
        require(
            state["directory_open_count"] == 1
            and state["directory_closures"] == [917_001]
            and effect.get("publication_attempted") is True,
            "retain the genuine synthetic publication attempt: " + mode,
        )
        failure_evidence = campaign_entry_failure_result(
            CampaignError("synthetic complete publication " + mode),
            effect,
        )
        require(
            failure_evidence.get("status") == "FAIL"
            and failure_evidence.get(
                "actual_evidence_owner_count_before_new_campaign"
            ) == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
            and failure_evidence.get(
                "actual_authenticated_reference_count_before_new_campaign"
            ) == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
            and failure_evidence.get("publication_status") == "FAIL"
            and failure_evidence.get("actual_candidate_workers")
            == SUITE_COUNT
            and failure_evidence.get("all_four_original_targets_restored")
            is True
            and "resulting_repository_evidence_owner_count"
            not in failure_evidence
            and "resulting_authenticated_reference_count"
            not in failure_evidence
            and failure_evidence.get("source_only_zero_effects_claimed")
            is False,
            "never announce two resulting owners after a failed "
            "full-denominator publication: " + mode,
        )

    return {
        "status": "PASS",
        "complete_synthetic_publication_modes": 2,
        "complete_synthetic_publication_hostile_modes": len(
            publication_hostile_modes
        ),
        "prepublication_hostile_count": len(prepublication_controls),
        "current_evidence_owner_lower_bound":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "current_history_reference_lower_bound":
            CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "resulting_evidence_owner_lower_bound":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND + 2,
        "resulting_history_reference_lower_bound":
            CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND + 2,
        "actual_files_opened": 0,
        "actual_archive_reads": 0,
        "actual_archive_gzip_inflations": 0,
        "actual_os_processes_started": 0,
        "actual_native_activations": 0,
        "holdout": "NOT OPENED",
    }


@contextlib.contextmanager
def synthetic_actual_route_overrides(
        overrides: Mapping[str, Any],
        ) -> Iterator[None]:
    """Scope in-memory doubles to this module; never alter platform I/O."""
    permitted = {
        "patched_v2_helpers", "verify_context", "active_worker_approval",
        "load_frozen_module", "corrected_rust_family", "read_owned",
        "bounded_build_gzip", "blocked_controller_signals",
        "open_recovery_lock", "restore_corrected_four_roles",
    }
    require(type(overrides) is dict and set(overrides) <= permitted
            and all(callable(value) for value in overrides.values()),
            "scope only explicit in-memory real worker and recovery doubles")
    namespace = globals()
    previous = {name: namespace[name] for name in overrides}
    try:
        namespace.update(overrides)
        yield
    finally:
        namespace.update(previous)


def walk_actual_archive_route_ast(node: ast.AST) -> Iterator[ast.AST]:
    """Traverse a bounded AST without ast.walk's lazy stdlib import."""
    require(isinstance(node, ast.AST),
            "traverse only one complete actual source AST")
    pending = [node]
    visited = 0
    while pending:
        current = pending.pop()
        visited += 1
        require(visited <= 200_000,
                "bound every import-free actual source-route AST")
        yield current
        pending.extend(reversed(list(ast.iter_child_nodes(current))))


def authenticate_actual_archive_route_ast(
        tree: ast.AST,
        ) -> dict[str, Any]:
    require(isinstance(tree, ast.Module),
            "authenticate complete controller, worker and recovery source")
    expected = {
        "run_worker": (False, False),
        "recover_originals": (False, False),
        "run_campaign": (True, True),
    }
    found: dict[str, tuple[bool, bool]] = {}
    for name, (retained, ledgered) in expected.items():
        functions = [node for node in tree.body
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and node.name == name]
        require(len(functions) == 1,
                "authenticate exactly one actual route: " + name)
        calls = [node for node in walk_actual_archive_route_ast(functions[0])
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "verify_context"]
        require(len(calls) == 1,
                "authenticate exactly one actual context proof: " + name)
        keywords = {keyword.arg: keyword.value
                    for keyword in calls[0].keywords
                    if keyword.arg is not None}
        require(len(keywords) == len(calls[0].keywords)
                and isinstance(keywords.get("retain"), ast.Constant)
                and type(keywords["retain"].value) is bool
                and keywords["retain"].value is retained
                and ((ledgered
                      and isinstance(keywords.get("ledger"), ast.Name)
                      and keywords["ledger"].id == "ledger")
                     or (not ledgered and "ledger" not in keywords)),
                "reject an unledgered or archive-dependent actual route: "
                + name)
        found[name] = (retained, ledgered)
    require(len(found) == 3,
            "preserve the single ledgered controller and two archive-free routes")
    return {
        "status": "PASS",
        "controller_retains_build_archive": found["run_campaign"][0],
        "controller_uses_actual_effect_ledger": found["run_campaign"][1],
        "worker_retains_build_archive": found["run_worker"][0],
        "recovery_retains_build_archive": found["recover_originals"][0],
    }


def synthetic_actual_worker_recovery_controls(
        source_raw: bytes,
        source_pin: str,
        protocol_pin: str,
        contract_pin: str,
        wall: SourceWall,
        accepted: list[str],
        rejected: list[str],
        ) -> dict[str, Any]:
    """Invoke genuine worker/recovery functions without archives or I/O."""
    try:
        parsed = ast.parse(source_raw, filename="<actual-v7-source-routes>")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise CampaignError("reject changed actual V7 archive route source") from error
    policy = authenticate_actual_archive_route_ast(parsed)
    accepted.append("accept-one-controller-ledger-and-archive-free-worker-recovery")
    route_names = ("run_worker", "recover_originals", "run_campaign")
    selected = ast.Module(
        body=[copy.deepcopy(node) for node in parsed.body
              if isinstance(node, ast.FunctionDef)
              and node.name in route_names],
        type_ignores=[],
    )
    for name, forged in (
            ("run_worker", True),
            ("recover_originals", True),
            ("run_campaign", False)):
        hostile = copy.deepcopy(selected)
        target = next(node for node in hostile.body if node.name == name)
        call = next(node for node in walk_actual_archive_route_ast(target)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "verify_context")
        retain = next(item for item in call.keywords if item.arg == "retain")
        retain.value = ast.Constant(value=forged)
        _expect_rejected(
            "reject-actual-" + name + "-forged-build-retain-policy",
            lambda item=hostile: authenticate_actual_archive_route_ast(item),
            rejected,
        )
    hostile_ledger = copy.deepcopy(selected)
    controller = next(node for node in hostile_ledger.body
                      if node.name == "run_campaign")
    controller_call = next(
        node for node in walk_actual_archive_route_ast(controller)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "verify_context"
    )
    controller_call.keywords = [
        item for item in controller_call.keywords if item.arg != "ledger"
    ]
    _expect_rejected(
        "reject-actual-controller-retained-build-without-effect-ledger",
        lambda: authenticate_actual_archive_route_ast(hostile_ledger),
        rejected,
    )

    blocked_before = dict(wall.blocked)
    _expect_rejected(
        "reject-real-verify-context-retain-true-without-ledger-before-io",
        lambda: verify_context(
            source_pin, protocol_pin, contract_pin,
            retain=True, ledger=None,
        ),
        rejected,
    )
    require(wall.blocked == blocked_before,
            "reject an unledgered real retained context before any I/O")

    state: dict[str, Any] = {
        "current_route": "worker",
        "worker_context_count": 0,
        "recovery_context_count": 0,
        "helper_calls": 0,
        "native_owner_audits": 0,
        "activation_approvals": 0,
        "producer_loads": 0,
        "phase_one_manifest_reads": 0,
        "observer_routes": [],
        "build_archive_reads": 0,
        "build_archive_inflations": 0,
        "hostile_build_archive_probe_count": 0,
        "hostile_retained_context_count": 0,
        "journal_reads": 0,
        "recovery_locks": 0,
        "signal_masks": 0,
        "closed_descriptors": [],
        "restorations": 0,
        "mismatches": 0,
        "archive_available": False,
        "forged_journal_schema": False,
    }
    suite_specs = tuple(
        types.SimpleNamespace(
            name=name,
            case_count=count,
            reference_sha256=(
                CORRECTED_REFERENCE_RECORDS_SHA256
                if name == "public_types_v1"
                else digest(("synthetic-actual-reference/" + name)
                            .encode("ascii"))
            ),
            matrix_sha256=(
                CORRECTED_REFERENCE_MATRIX_SHA256
                if name == "public_types_v1"
                else digest(("synthetic-actual-matrix/" + name)
                            .encode("ascii"))
            ),
        )
        for name, count in SUITES
    )
    suites = {item.name: item for item in suite_specs}
    corrected_roles = {
        "bridge_source": (BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
        "adapter": (CORRECTED_PUBLIC_SHA256, CORRECTED_PUBLIC_BYTES),
        "engine": (ENGINE_SHA256, ENGINE_BYTES),
        "bridge": (BRIDGE_SHA256, BRIDGE_BYTES),
    }
    original_target_owners = {
        role: {
            **copy.deepcopy(original),
            "path": str(ROOT / original["relative"]),
            "size_bytes": original["bytes"],
        }
        for role, original in ORIGINALS.items()
    }
    journal_digest = "c" * 64
    journal_roles = {
        role: {
            "role": role,
            "relative": ORIGINALS[role]["relative"],
            "original": copy.deepcopy(ORIGINALS[role]),
            "repaired_sha256": corrected_roles[role][0],
            "repaired_bytes": corrected_roles[role][1],
            "backup_filename": ".synthetic-v7-original-" + role,
        }
        for role in ROLE_ORDER
    }
    journal = {
        "schema": "rebar-owned-repaired-rust-original-campaign-v2"
            + "-four-owner-recovery-journal",
        "status": "PREPARED",
        "family": FAMILY,
        "label": LABEL,
        "activation_root": PUBLIC_RECOVERY_ROOT,
        "source_sha256": V2["source"][1],
        "protocol_sha256": V2["protocol"][1],
        "contract_sha256": V2["contract"][1],
        "build_archive_sha256": BUILD["archive"][1],
        "build_receipt_sha256": BUILD["receipt"][1],
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "recoverable_v4_public_root": PUBLIC_RECOVERY_ROOT,
        "recoverable_v4_public_lock_filename": LOCK_NAME,
        "recoverable_v7_controller_source_sha256": source_pin,
        "recoverable_v7_controller_protocol_sha256": protocol_pin,
        "recoverable_v7_controller_contract_sha256": contract_pin,
        "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "roles": journal_roles,
        "group_atomic": False,
    }

    def fake_read_private(root: str, name: str,
                          fingerprint: str | None = None
                          ) -> tuple[dict[str, Any], dict[str, Any]]:
        require(root == PUBLIC_RECOVERY_ROOT
                and name == "recovery-journal.json"
                and fingerprint == journal_digest,
                "authenticate the exact in-memory caller-pinned recovery journal")
        state["journal_reads"] += 1
        recorded = copy.deepcopy(journal)
        if state["forged_journal_schema"]:
            recorded["schema"] = (
                "rebar-owned-repaired-rust-original-campaign-v2-journal"
            )
        return recorded, {
            "sha256": journal_digest,
            "device": 2064,
            "inode": 991_003,
            "size_bytes": len(canonical(journal)),
        }

    helper = types.SimpleNamespace(
        JOURNAL_SCHEMA=journal["schema"],
        ROLES={
            role: {
                "relative": ORIGINALS[role]["relative"],
                "original": copy.deepcopy(ORIGINALS[role]),
                "sha256": corrected_roles[role][0],
                "bytes": corrected_roles[role][1],
            }
            for role in ROLE_ORDER
        },
        read_private=fake_read_private,
        exact_originals=lambda: copy.deepcopy(original_target_owners),
        same_original=lambda actual, original:
            type(actual) is dict
            and all(actual.get(field) == value
                    for field, value in original.items()),
    )

    def fake_helpers(*args: Any, **kwargs: Any) -> Any:
        require(not args and not kwargs,
                "authenticate only the actual worker or recovery helper route")
        state["helper_calls"] += 1
        return helper

    def fake_context(source: str, protocol: str,
                     contract: str | None = None, *,
                     retain: bool = False,
                     ledger: dict[str, Any] | None = None
                     ) -> tuple[dict[str, Any], dict[str, Any]]:
        require(source == source_pin and protocol == protocol_pin
                and contract == contract_pin,
                "authenticate every real source/protocol/contract route pin")
        if retain is not False or ledger is not None:
            state["hostile_retained_context_count"] += 1
            raise CampaignError(
                "synthetic missing V13 build archive forbids retained context"
            )
        route = state["current_route"]
        require(route in ("worker", "recovery"),
                "attribute one actual non-retained source context")
        state[route + "_context_count"] += 1
        return {
            "status": "PASS",
            "historical_v2_public_adapter_sha256":
                HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
            "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
            "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
            "actual_evidence_owner_count_before_new_campaign":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
            "actual_authenticated_reference_count_before_new_campaign":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
            "v13_source_build_archive_read_count": 0,
            "v13_source_build_archive_gzip_inflation_count": 0,
            "holdout": "NOT OPENED",
        }, {}

    def fake_active(value: Any, options: argparse.Namespace) -> dict[str, Any]:
        require(value is helper
                and options.activation_root == PUBLIC_RECOVERY_ROOT
                and options.activation_report_sha256 == "a" * 64
                and options.activation_receipt_sha256 == "b" * 64
                and options.recovery_journal_sha256 == journal_digest,
                "authenticate all three genuine corrected active worker owners")
        state["activation_approvals"] += 1
        return {
            "root": PUBLIC_RECOVERY_ROOT,
            "report_owner": {"sha256": "a" * 64},
            "receipt_owner": {"sha256": "b" * 64},
            "journal_owner": {"sha256": journal_digest},
        }

    def fake_observation(suite: Any, route: str) -> dict[str, Any]:
        require(suite.name in suites and suite is suites[suite.name],
                "observe only one complete original frozen suite")
        state["observer_routes"].append((route, suite.name))
        mismatches = state["mismatches"]
        observation: dict[str, Any] = {
            "schema": "rebar-owned-six-family-original-p0-producer-v4"
                + "-actual-original-suite",
            "status": "FAIL" if mismatches else "PASS",
            "suite": suite.name,
            "candidate_family": FAMILY,
            "case_execution_denominator": suite.case_count,
            "actual_candidate_case_count": suite.case_count,
            "reference_records_sha256": suite.reference_sha256,
            "mismatch_count": mismatches,
            "all_mismatches": [
                {"case": "synthetic-real-worker/" + str(index)}
                for index in range(mismatches)
            ],
            "actual_candidate_workers": 1,
            "clock_samples": 0,
            "holdout": "NOT OPENED",
        }
        if suite.name == "public_types_v1":
            observation["baseline_evidence"] = {
                "status": "PASS",
                "reference_status": "PASS",
                "actual_independent_reference_count": 2,
                "reference_decoder_sha256": CORRECTED_REFERENCE["source"][1],
                "reference_roles_separately_authenticated": True,
                "reference_records_sha256":
                    CORRECTED_REFERENCE_RECORDS_SHA256,
                "historical_reference_records_sha256":
                    HISTORICAL_FULL_PUBLIC_RECORDS_SHA256,
                "baseline_reference_pids": list(CORRECTED_REFERENCE_PIDS),
                "cache_case_count": CORRECTED_REFERENCE_CACHE_CASE_COUNT,
                "cache_records_sha256":
                    CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
                "new_reference_workers_started": 0,
                "candidate_imports_by_reference_decoder": 0,
                "c_pattern_equality_failure_waived": False,
            }
        if suite.name == "original_bounded_v5":
            observation.update({
                "actual_public_record_count": 152,
                "actual_debug_skip_count": 1,
                "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
            })
        if suite.name == "subinterpreter_v2" and mismatches == 0:
            observation.update({
                "actual_case_interpreter_exec_calls": 394,
                "actual_interpreters_created": 11,
                "actual_interpreters_destroyed": 11,
                "all_real_pipes_read_to_eof": True,
                "all_real_pipe_descriptors_closed": True,
                "interpreter_live_set_restored": True,
            })
        return observation

    def fake_observe_direct(suite: Any, spec: Any, pins: Any,
                            source_pins: Any,
                            phase_one: Mapping[str, Any]
                            ) -> dict[str, Any]:
        require(type(phase_one) is dict
                and phase_one.get("schema")
                == "synthetic-source-only-original-phase-one",
                "preserve the unchanged direct-suite phase-one input route")
        del spec, pins, source_pins
        return fake_observation(suite, "direct")

    def fake_observe_original(suite: Any, spec: Any,
                              pins: Any, source_pins: Any
                              ) -> dict[str, Any]:
        del spec, pins, source_pins
        return fake_observation(suite, "original-bounded")

    def fake_observe_subinterpreters(suite: Any, spec: Any,
                                      pins: Any, source_pins: Any,
                                      *, producer_sha256: str
                                      ) -> dict[str, Any]:
        del spec, pins, source_pins
        require(producer_sha256 == PRODUCER["source"][1],
                "bind actual nested interpreter observation to V4 source")
        return fake_observation(suite, "subinterpreter")

    def fake_native(spec: Any, pins: Mapping[str, str],
                    source_pins: Mapping[str, str]
                    ) -> dict[str, dict[str, Any]]:
        require(spec.get("family") == FAMILY
                and spec.get("source_owners") == CORRECTED_SOURCE_OWNERS
                and pins == {
                    "source": CORRECTED_PUBLIC_SHA256,
                    "native_engine": ENGINE_SHA256,
                    "native_bridge": BRIDGE_SHA256,
                }
                and dict(source_pins)
                == {path: fingerprint
                    for path, fingerprint, _ in CORRECTED_SOURCE_OWNERS},
                "authenticate all nine corrected native first-party owners")
        state["native_owner_audits"] += 1
        return {
            "source": {"sha256": CORRECTED_PUBLIC_SHA256},
            "native_engine": {"sha256": ENGINE_SHA256},
            "native_bridge": {"sha256": BRIDGE_SHA256},
        }

    producer = types.SimpleNamespace(
        SCHEMA="rebar-owned-six-family-original-p0-producer-v4",
        SUITE_COUNT=SUITE_COUNT,
        CASE_DENOMINATOR=CASE_COUNT,
        PRIVATE_WAIVER_COUNT=PRIVATE_WAIVER_COUNT,
        CORRECTED_PUBLIC_RECORDS_SHA256=CORRECTED_REFERENCE_RECORDS_SHA256,
        CORRECTED_PUBLIC_COHORT_RECORDS_SHA256=
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        CORRECTED_PUBLIC_REFERENCE_PIDS=CORRECTED_REFERENCE_PIDS,
        CORRECTED_PUBLIC_COHORT_CASE_COUNT=
            CORRECTED_REFERENCE_CACHE_CASE_COUNT,
        SUITES=suite_specs,
        OWNED_SOURCES={FAMILY: ORIGINAL_SOURCE_OWNERS},
        suite_spec=lambda name: suites[name],
        exact_native_owners=fake_native,
        observe_direct_suite=fake_observe_direct,
        observe_original_upstream=fake_observe_original,
        observe_subinterpreters=fake_observe_subinterpreters,
    )

    def fake_producer(item: tuple[str, str, int],
                      name: str) -> Any:
        require(item == PRODUCER["source"]
                and name == "_rebar_exact_original_six_family_v4_for_v13_rust",
                "load only the exact pinned original V4 producer owner")
        state["producer_loads"] += 1
        return producer

    def fake_corrected_family(value: Any) -> dict[str, Any]:
        require(value is producer
                and tuple(value.OWNED_SOURCES[FAMILY])
                == ORIGINAL_SOURCE_OWNERS,
                "retain only the exact unchanged original V4 Rust family")
        return {"family": FAMILY, "source_owners": CORRECTED_SOURCE_OWNERS}

    def fake_read_owned(item: Any, *args: Any,
                        **kwargs: Any) -> tuple[bytes, dict[str, Any]]:
        del args, kwargs
        if type(item) is tuple and item and item[0] == BUILD["archive"][0]:
            state["hostile_build_archive_probe_count"] += 1
            raise CampaignError("synthetic V13 source-build archive is missing")
        expected = (
            "oracle/phase1/p0-completeness-v1.json",
            "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
            45632,
        )
        require(item == expected,
                "read only the unchanged synthetic direct-suite P0 manifest")
        state["phase_one_manifest_reads"] += 1
        raw = canonical({"schema": "synthetic-source-only-original-phase-one"})
        return raw, {"sha256": expected[1], "bytes": len(raw)}

    def reject_build_inflation(*args: Any, **kwargs: Any) -> bytes:
        del args, kwargs
        state["hostile_build_archive_probe_count"] += 1
        raise CampaignError("never inflate a missing V13 source-build archive")

    @contextlib.contextmanager
    def fake_signal_mask() -> Iterator[None]:
        state["signal_masks"] += 1
        yield

    def fake_recovery_lock(value: Any, root: str, *,
                           create: bool,
                           ledger: dict[str, Any] | None = None
                           ) -> tuple[int, int]:
        require(value is helper and root == PUBLIC_RECOVERY_ROOT
                and create is False and ledger is None,
                "open only the exact existing synthetic pinned recovery lock")
        state["recovery_locks"] += 1
        return 992_001, 992_002

    def fake_restore(value: Any, root: str,
                     recorded: dict[str, Any], fingerprint: str,
                     ledger: dict[str, Any] | None = None
                     ) -> dict[str, Any]:
        require(value is helper and root == PUBLIC_RECOVERY_ROOT
                and fingerprint == journal_digest and ledger is None
                and recorded.get("schema") == helper.JOURNAL_SCHEMA
                and recorded.get("schema")
                == "rebar-owned-repaired-rust-original-campaign-v2"
                    + "-four-owner-recovery-journal"
                and canonical(recorded) == canonical(journal)
                and set(recorded.get("roles", {})) == set(ROLE_ORDER)
                and all(recorded["roles"][role]["original"]
                        == ORIGINALS[role]
                        and recorded["roles"][role]["repaired_sha256"]
                        == corrected_roles[role][0]
                        and recorded["roles"][role]["repaired_bytes"]
                        == corrected_roles[role][1]
                        for role in ROLE_ORDER),
                "recover all four exact original identities from the "
                "caller-pinned journal without reading the build archive")
        state["restorations"] += 1
        return {
            "status": "PASS",
            "report": {"status": "PASS", "original_inodes_preserved": True},
            "restoration_order": list(RESTORATION_ORDER),
        }

    def close_synthetic_descriptor(descriptor: int) -> None:
        require(descriptor in (992_001, 992_002),
                "close only the exact in-memory recovery lock descriptors")
        state["closed_descriptors"].append(descriptor)

    overrides = {
        "patched_v2_helpers": fake_helpers,
        "verify_context": fake_context,
        "active_worker_approval": fake_active,
        "load_frozen_module": fake_producer,
        "corrected_rust_family": fake_corrected_family,
        "read_owned": fake_read_owned,
        "bounded_build_gzip": reject_build_inflation,
        "blocked_controller_signals": fake_signal_mask,
        "open_recovery_lock": fake_recovery_lock,
        "restore_corrected_four_roles": fake_restore,
    }
    with synthetic_actual_route_overrides(overrides):
        results = []
        for suite in suite_specs:
            state["current_route"] = "worker"
            state["mismatches"] = 0
            options = argparse.Namespace(
                source_sha256=source_pin,
                protocol_sha256=protocol_pin,
                contract_sha256=contract_pin,
                suite=suite.name,
                activation_root=PUBLIC_RECOVERY_ROOT,
                activation_report_sha256="a" * 64,
                activation_receipt_sha256="b" * 64,
                recovery_journal_sha256=journal_digest,
            )
            observed = run_worker(options)
            require(
                observed.get("schema") == WORKER_SCHEMA
                and observed.get("status") == "PASS"
                and observed.get("suite") == suite.name
                and observed.get("case_execution_denominator")
                == suite.case_count
                and observed.get("actual_candidate_case_count")
                == suite.case_count
                and observed.get("mismatch_count") == 0
                and observed.get("repaired_source_owner_count") == 9
                and observed.get("corrected_public_source_sha256")
                == CORRECTED_PUBLIC_SHA256
                and observed.get("native_engine_sha256") == ENGINE_SHA256
                and observed.get("native_bridge_sha256") == BRIDGE_SHA256
                and observed.get("activation_report_sha256") == "a" * 64
                and observed.get("activation_receipt_sha256") == "b" * 64
                and observed.get("recovery_journal_sha256") == journal_digest
                and observed.get("corrected_reference_records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and observed.get("corrected_reference_cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and observed.get("corrected_reference_process_ids")
                == list(CORRECTED_REFERENCE_PIDS)
                and observed.get("holdout") == "NOT OPENED",
                "execute real archive-free original worker: " + suite.name,
            )
            validate_streamed_observation(
                observed["complete_original_observation"]
            )
            results.append(observed)
        require(
            len(results) == SUITE_COUNT
            and [(item["suite"], item["case_execution_denominator"])
                 for item in results] == list(SUITES)
            and sum(item["case_execution_denominator"] for item in results)
            == CASE_COUNT
            and state["worker_context_count"] == SUITE_COUNT
            and state["native_owner_audits"] == SUITE_COUNT
            and state["activation_approvals"] == SUITE_COUNT
            and state["producer_loads"] == SUITE_COUNT
            and state["phase_one_manifest_reads"] == SUITE_COUNT - 2
            and state["observer_routes"]
            == [(
                "original-bounded" if name == "original_bounded_v5"
                else "subinterpreter" if name == "subinterpreter_v2"
                else "direct", name,
            ) for name, _ in SUITES]
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "execute all thirteen actual worker functions and all 31,237 "
            "unchanged original cases without the V13 source-build archive",
        )
        accepted.append(
            "accept-thirteen-actual-run-worker-calls-without-build-archive"
        )
        accepted.append(
            "accept-actual-public-type-two-references-cache-and-subinterpreters"
        )

        state["mismatches"] = 3
        semantic_options = argparse.Namespace(
            source_sha256=source_pin,
            protocol_sha256=protocol_pin,
            contract_sha256=contract_pin,
            suite="scanner_v3",
            activation_root=PUBLIC_RECOVERY_ROOT,
            activation_report_sha256="a" * 64,
            activation_receipt_sha256="b" * 64,
            recovery_journal_sha256=journal_digest,
        )
        semantic_failure = run_worker(semantic_options)
        require(
            semantic_failure.get("status") == "FAIL"
            and semantic_failure.get("failure_class") == "SEMANTIC MISMATCH"
            and semantic_failure.get("suite") == "scanner_v3"
            and semantic_failure.get("mismatch_count") == 3
            and semantic_failure.get("actual_candidate_workers") == 1
            and semantic_failure.get("holdout") == "NOT OPENED"
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "preserve actual semantic worker failures without reopening "
            "the historical source-build archive",
        )
        accepted.append("accept-actual-run-worker-true-semantic-failure")
        state["mismatches"] = 0

        state["current_route"] = "recovery"
        recovery_options = argparse.Namespace(
            source_sha256=source_pin,
            protocol_sha256=protocol_pin,
            contract_sha256=contract_pin,
            activation_root=PUBLIC_RECOVERY_ROOT,
            recovery_journal_sha256=journal_digest,
        )
        recovered = recover_originals(
            recovery_options,
            descriptor_closer=close_synthetic_descriptor,
        )
        require(
            recovered.get("schema") == RECOVERY_SCHEMA
            and recovered.get("status") == "PASS"
            and recovered.get("version") == 7
            and recovered.get("family") == FAMILY
            and recovered.get("activation_root") == PUBLIC_RECOVERY_ROOT
            and recovered.get("recovery_journal_sha256") == journal_digest
            and recovered.get("restoration_order") == list(RESTORATION_ORDER)
            and recovered.get("restored_original_targets")
            == original_target_owners
            and recovered.get("all_four_original_targets_restored") is True
            and recovered.get("actual_candidate_workers") == 0
            and recovered.get("holdout") == "NOT OPENED"
            and state["archive_available"] is False
            and state["recovery_context_count"] == 1
            and state["journal_reads"] == 1
            and state["recovery_locks"] == 1
            and state["signal_masks"] == 1
            and state["restorations"] == 1
            and state["closed_descriptors"] == [992_002, 992_001]
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "execute the genuine recovery callable against an independently "
            "pinned four-role journal when the V13 archive is missing",
        )
        accepted.append(
            "accept-actual-four-inode-recovery-with-missing-build-archive"
        )

        for route in ("worker", "recovery"):
            state["current_route"] = route
            _expect_rejected(
                "reject-actual-" + route
                + "-retained-context-with-missing-build-archive",
                lambda: fake_context(
                    source_pin, protocol_pin, contract_pin,
                    retain=True, ledger=None,
                ),
                rejected,
            )
        _expect_rejected(
            "reject-actual-missing-source-build-archive-read",
            lambda: fake_read_owned(BUILD["archive"]),
            rejected,
        )
        _expect_rejected(
            "reject-actual-missing-source-build-archive-inflation",
            lambda: reject_build_inflation(b"synthetic-missing"),
            rejected,
        )
        require(
            state["hostile_retained_context_count"] == 2
            and state["hostile_build_archive_probe_count"] == 2
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "distinguish deliberate missing-build hostile probes from "
            "all genuine archive-free worker and recovery paths",
        )

        state["current_route"] = "recovery"
        wrong_journal = argparse.Namespace(**vars(recovery_options))
        wrong_journal.recovery_journal_sha256 = "d" * 64
        _expect_rejected(
            "reject-actual-recovery-substituted-caller-pinned-journal",
            lambda: recover_originals(
                wrong_journal,
                descriptor_closer=close_synthetic_descriptor,
            ),
            rejected,
        )
        require(
            state["restorations"] == 1
            and state["closed_descriptors"]
            == [992_002, 992_001, 992_002, 992_001]
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "reject a forged recovery journal without any missing archive "
            "access or leaked synthetic recovery descriptor",
        )
        state["forged_journal_schema"] = True
        try:
            _expect_rejected(
                "reject-actual-recovery-fabricated-real-v2-journal-schema",
                lambda: recover_originals(
                    recovery_options,
                    descriptor_closer=close_synthetic_descriptor,
                ),
                rejected,
            )
        finally:
            state["forged_journal_schema"] = False
        require(
            state["restorations"] == 1
            and state["closed_descriptors"]
            == [992_002, 992_001, 992_002, 992_001,
                992_002, 992_001]
            and state["build_archive_reads"] == 0
            and state["build_archive_inflations"] == 0,
            "reject the exact genuine V2 journal-schema substitution "
            "without archive access or descriptor loss",
        )

    return {
        "status": "PASS",
        "actual_worker_callable_success_count": SUITE_COUNT,
        "actual_worker_callable_semantic_failure_count": 1,
        "actual_worker_callable_case_denominator": CASE_COUNT,
        "actual_worker_direct_suite_count": SUITE_COUNT - 2,
        "actual_worker_bounded_suite_count": 1,
        "actual_worker_subinterpreter_suite_count": 1,
        "actual_worker_context_retain": False,
        "actual_recovery_callable_success_count": 1,
        "actual_recovery_context_retain": False,
        "actual_recovery_archive_available": False,
        "actual_recovery_four_original_identities_restored": True,
        "actual_recovery_hostile_journal_rejected": True,
        "actual_recovery_hostile_journal_schema_rejected": True,
        "actual_worker_source_build_archive_reads": 0,
        "actual_worker_source_build_archive_inflations": 0,
        "actual_recovery_source_build_archive_reads": 0,
        "actual_recovery_source_build_archive_inflations": 0,
        "controller_build_archive_retain": policy[
            "controller_retains_build_archive"
        ],
        "controller_build_archive_effect_ledger_required": policy[
            "controller_uses_actual_effect_ledger"
        ],
        "hostile_retained_context_rejections":
            state["hostile_retained_context_count"],
        "hostile_missing_build_archive_rejections":
            state["hostile_build_archive_probe_count"],
        "all_source_route_overrides_restored": True,
        "actual_files_opened": 0,
        "actual_archive_reads": 0,
        "actual_archive_gzip_inflations": 0,
        "actual_native_activations": 0,
        "actual_os_processes_started": 0,
        "genuine_corrected_reference_inputs_preserved": True,
        "holdout": "NOT OPENED",
    }


def synthetic_worker_hostile_controls(source_pin: str, protocol_pin: str,
                                     contract_pin: str,
                                     accepted: list[str],
                                     rejected: list[str]) -> dict[str, Any]:
    options = argparse.Namespace(
        source_sha256=source_pin,
        protocol_sha256=protocol_pin,
        contract_sha256=contract_pin,
    )
    active = {
        "root": PUBLIC_RECOVERY_ROOT,
        "activation_owner": {"sha256": "a" * 64},
        "receipt_owner": {"sha256": "b" * 64},
        "journal_owner": {"sha256": "c" * 64},
    }

    def observe(mode: str, index: int, *, pid: int | None = None,
                mismatches: int = 0,
                ledger: dict[str, Any] | None = None
                ) -> dict[str, Any]:
        name, count = SUITES[index]
        identity = 910_000 + index if pid is None and mode != "missing-pid" else pid
        with synthetic_original_worker_launch(
                mode=mode, name=name, count=count, pid=identity,
                mismatches=mismatches):
            attempt = new_worker_attempt(name, count, ledger)
            row = execute_one_worker(options, name, count, active, attempt)
        require(row.get("worker_attempted") is True,
                "preserve the actual synthetic original launch attempt")
        return row

    launch = observe("launch-failure", 0)
    require(launch.get("failure_class") == "INFRASTRUCTURE FAILURE"
            and launch.get("actual_worker_started") is False
            and launch.get("actual_worker_processes") == 0
            and launch.get("fully_observed") is False
            and launch.get("process") is None,
            "report no-start only when synthetic Popen actually fails")
    rejected.append("reject-actual-original-worker-popen-launch-failure")

    for mode in (
        "post-spawn-exception", "oversized-stdout", "oversized-stderr",
        "timeout", "crash", "malformed-json", "malformed-gzip",
    ):
        row = observe(mode, 0, pid=920_001)
        process = row.get("process")
        require(row.get("failure_class") == "INFRASTRUCTURE FAILURE"
                and row.get("actual_worker_started") is True
                and row.get("actual_worker_processes") == 1
                and row.get("fully_observed") is False
                and type(process) is dict
                and process.get("pid") == 920_001,
                "retain the real started PID after synthetic " + mode)
        if mode in ("oversized-stdout", "oversized-stderr"):
            channel = "stdout" if mode == "oversized-stdout" else "stderr"
            value = process[channel]
            limit = (MAX_WORKER_STDOUT_BYTES if channel == "stdout"
                     else MAX_WORKER_STDERR_BYTES)
            require(value.get("size_bytes") == limit + 1
                    and value.get("sha256") == digest(b"x" * (limit + 1))
                    and value.get("captured_prefix_bytes")
                    == min(limit, MAX_FAILURE_STREAM_CAPTURE_BYTES)
                    and value.get("truncated") is True
                    and value.get("complete") is False
                    and value.get("limit_exceeded") is True,
                    "retain full observed size/hash and a bounded "
                    + channel + " prefix without pretending completion")
        if mode == "timeout":
            require(process.get("timed_out") is True
                    and process.get("kill_attempted") is True,
                    "retain and reap an actually timed-out synthetic PID")
        rejected.append("reject-actual-original-worker-" + mode)

    missing = observe("missing-pid", 0)
    require(missing.get("actual_worker_started") is True
            and missing.get("fully_observed") is False
            and type(missing.get("process")) is dict
            and missing["process"].get("pid") is None,
            "retain a started worker without fabricating its missing PID")
    rejected.append("reject-started-original-worker-missing-pid")

    ledger = new_campaign_effect_ledger(options)
    complete_rows = [
        observe("valid", index, ledger=ledger)
        for index in range(SUITE_COUNT)
    ]
    genuine_shape = aggregate_worker_rows(complete_rows)
    require(genuine_shape.get("attempted_suite_count") == SUITE_COUNT
            and genuine_shape.get("started_suite_count") == SUITE_COUNT
            and genuine_shape.get("completed_suite_count") == SUITE_COUNT
            and genuine_shape.get("distinct_worker_process_id_count")
            == SUITE_COUNT
            and genuine_shape.get("semantic_mismatch_count") == 0
            and genuine_shape.get("candidate_qualified") is True
            and ledger.get("attempted_suite_count") == SUITE_COUNT
            and ledger.get("started_suite_count") == SUITE_COUNT
            and ledger.get("fully_observed_suite_count") == SUITE_COUNT,
            "accept only thirteen synthetic complete distinct observations")
    accepted.append("accept-thirteen-synthetic-distinct-complete-worker-vectors")
    complete_publication_controls = synthetic_complete_publication_controls(
        options,
        complete_rows,
        genuine_shape,
        observe,
        accepted,
        rejected,
    )

    first_mismatch = observe("valid", 0, pid=930_001, mismatches=3)
    partial_rows = [first_mismatch] + [
        failed_worker(name, count,
                      CampaignError("synthetic original worker not attempted"))
        for name, count in SUITES[1:]
    ]
    partial = aggregate_worker_rows(partial_rows)
    require(partial.get("attempted_suite_count") == 1
            and partial.get("started_suite_count") == 1
            and partial.get("completed_suite_count") == 1
            and partial.get("actual_candidate_workers") == 1
            and partial.get("observed_partial_semantic_mismatch_count") == 3
            and partial.get("semantic_mismatch_count") == "NOT MEASURED"
            and partial.get("candidate_qualified") is False,
            "never extrapolate three observed losses from one of thirteen suites")
    rejected.append("reject-one-of-thirteen-partial-numeric-mismatch-total")

    duplicated_rows = list(complete_rows)
    duplicated = copy.deepcopy(complete_rows[1])
    duplicated["process"]["pid"] = complete_rows[0]["process"]["pid"]
    duplicated_rows[1] = duplicated
    duplicate_summary = aggregate_worker_rows(duplicated_rows)
    require(duplicate_summary.get("started_suite_count") == SUITE_COUNT
            and duplicate_summary.get("completed_suite_count") == SUITE_COUNT - 1
            and duplicate_summary.get("duplicate_worker_process_id_count") == 1
            and duplicate_summary.get("distinct_worker_process_id_count")
            == SUITE_COUNT - 1
            and duplicate_summary.get("semantic_mismatch_count")
            == "NOT MEASURED"
            and duplicate_summary.get("candidate_qualified") is False,
            "reject a duplicated actual original PID without losing its record")
    rejected.append("reject-duplicate-original-worker-process-pid")

    missing_rows = list(complete_rows)
    missing_rows[0] = missing
    missing_summary = aggregate_worker_rows(missing_rows)
    require(missing_summary.get("started_suite_count") == SUITE_COUNT
            and missing_summary.get("completed_suite_count") == SUITE_COUNT - 1
            and missing_summary.get("missing_worker_process_id_count") == 1
            and missing_summary.get("semantic_mismatch_count")
            == "NOT MEASURED"
            and missing_summary.get("candidate_qualified") is False,
            "reject a started missing-PID observation without inventing identity")
    rejected.append("reject-missing-original-worker-pid-in-aggregate")

    for stage in ("bounded-report", "archive-stream", "archive-owner",
                  "receipt-publication"):
        state = new_campaign_effect_ledger(options)
        state.update({
            "attempted_suite_count": SUITE_COUNT,
            "started_suite_count": SUITE_COUNT,
            "fully_observed_suite_count": SUITE_COUNT,
            "actual_candidate_workers": SUITE_COUNT,
            "actual_worker_process_ids": [
                row["process"]["pid"] for row in complete_rows
            ],
            "actual_native_activations": 1,
            "activated_target_roles": list(ROLE_ORDER),
            "canonical_target_replacements": len(ROLE_ORDER),
            "recovery_root_creation_attempted": True,
            "recovery_roots_created": 1,
            "recovery_lock_attempted": True,
            "recovery_locks_acquired": 1,
            "recovery_journal_creation_attempted": True,
            "recovery_journals_created": 1,
            "recovery_journal_sha256": "c" * 64,
            "recovery_journal_announced": True,
            "restoration_attempted": True,
            "restored_target_roles": list(RESTORATION_ORDER),
            "all_four_original_targets_restored": True,
            "restoration_verified": True,
            "publication_attempted": True,
            "bounded_report_attempted": True,
        })
        if stage != "bounded-report":
            state["archive_publication_attempted"] = True
        if stage in ("archive-owner", "receipt-publication"):
            state["archive_publication_status"] = "PASS"
            state["archive_owner"] = {
                "sha256": "d" * 64, "bytes": 1024,
                "device": 2049, "inode": 940_001,
            }
        if stage == "receipt-publication":
            state["receipt_publication_attempted"] = True
        result = campaign_entry_failure_result(
            CampaignError("synthetic " + stage + " publication failure"),
            state,
        )
        require(result.get("status") == "FAIL"
                and result.get("campaign_mode") == "AUTHORIZED RUN"
                and result.get("actual_candidate_workers") == SUITE_COUNT
                and result.get("actual_native_activations") == 1
                and result.get("canonical_target_replacements")
                == len(ROLE_ORDER)
                and result.get("recovery_journal_sha256") == "c" * 64
                and result.get("all_four_original_targets_restored") is True
                and result.get("publication_attempted") is True
                and result.get("publication_status") == "FAIL"
                and result.get("semantic_mismatch_count") == "NOT MEASURED"
                and len(result.get("actual_worker_process_ids", []))
                == SUITE_COUNT
                and result.get("source_only_zero_effects_claimed") is False,
                "retain every activated worker and recovery effect after "
                + stage + " failure")
        rejected.append("reject-zero-effect-claim-after-" + stage + "-failure")

    for stage, updates in (
            ("archive-read-attempt", {
                "historical_v2_helper_preflight_attempted": True,
                "historical_v2_helper_source_preflight_status": "PASS",
                "historical_v2_helper_module_preflight_status": "PASS",
                "v13_source_build_archive_read_attempted": True,
                "v13_source_build_archive_read_status":
                    "ATTEMPTED; OUTCOME UNKNOWN",
            }),
            ("archive-read-complete", {
                "historical_v2_helper_preflight_attempted": True,
                "historical_v2_helper_source_preflight_status": "PASS",
                "historical_v2_helper_module_preflight_status": "PASS",
                "v13_source_build_archive_read_attempted": True,
                "v13_source_build_archive_read_status": "PASS",
                "v13_source_build_archive_read_count": 1,
                "v13_source_build_archive_compressed_bytes_read":
                    BUILD["archive"][2],
            }),
            ("archive-gzip-attempt", {
                "historical_v2_helper_preflight_attempted": True,
                "historical_v2_helper_source_preflight_status": "PASS",
                "historical_v2_helper_module_preflight_status": "PASS",
                "v13_source_build_archive_read_attempted": True,
                "v13_source_build_archive_read_status": "PASS",
                "v13_source_build_archive_read_count": 1,
                "v13_source_build_archive_compressed_bytes_read":
                    BUILD["archive"][2],
                "v13_source_build_archive_gzip_inflation_attempted": True,
                "v13_source_build_archive_gzip_inflation_status":
                    "ATTEMPTED; OUTCOME UNKNOWN",
            }),
            ("archive-gzip-complete", {
                "historical_v2_helper_preflight_attempted": True,
                "historical_v2_helper_source_preflight_status": "PASS",
                "historical_v2_helper_module_preflight_status": "PASS",
                "v13_source_build_archive_read_attempted": True,
                "v13_source_build_archive_read_status": "PASS",
                "v13_source_build_archive_read_count": 1,
                "v13_source_build_archive_compressed_bytes_read":
                    BUILD["archive"][2],
                "v13_source_build_archive_gzip_inflation_attempted": True,
                "v13_source_build_archive_gzip_inflation_status": "PASS",
                "v13_source_build_archive_gzip_inflation_count": 1,
                "v13_source_build_archive_uncompressed_bytes_read":
                    V13_PLAIN_BYTES,
                "v13_source_build_archive_uncompressed_sha256":
                    V13_PLAIN_SHA256,
            })):
        state = new_campaign_effect_ledger(options)
        state.update(updates)
        result = campaign_entry_failure_result(
            CampaignError("synthetic post-" + stage + " failure"),
            state,
        )
        require(
            result.get("status") == "FAIL"
            and result.get("actual_candidate_workers") == 0
            and result.get("actual_native_activations") == 0
            and result.get("source_only_zero_effects_claimed") is False
            and all(result.get(key) == value
                    for key, value in updates.items())
            and result.get("semantic_mismatch_count") == "NOT MEASURED",
            "preserve each genuine source-build effect in an entry failure: "
            + stage,
        )
        rejected.append("reject-concealed-source-build-effect-" + stage)

    return {
        "actual_os_processes_started": 0,
        "actual_files_opened": 0,
        "actual_targets_modified": 0,
        "complete_synthetic_worker_count": SUITE_COUNT,
        "post_spawn_failure_modes": 7,
        "publication_failure_modes": 4,
        "complete_publication_controls": complete_publication_controls,
        "partial_total_mismatches": "NOT MEASURED",
    }


def synthetic_historical_v2_helper_controls(
        source_raw: bytes, frozen_contract: Mapping[str, Any],
        accepted: list[str], rejected: list[str]) -> dict[str, Any]:
    """Exercise the real historical guard in memory behind SourceWall."""
    proof = authenticate_historical_v2_helper_source(
        source_raw, frozen_contract,
    )
    require(
        proof.get("status") == "PASS"
        and proof.get("historical_repaired_source_owner_count") == 9
        and proof.get("historical_public_adapter", {}).get("sha256")
        == HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
        and proof.get("historical_public_adapter", {}).get("bytes")
        == HISTORICAL_V2_REPAIRED_PUBLIC_BYTES
        and proof.get("corrected_v13_public_adapter", {}).get("sha256")
        == CORRECTED_PUBLIC_SHA256
        and proof.get("module_imported_by_source_gate") is False
        and proof.get("module_executed_by_source_gate") is False
        and proof.get("helper_invoked_by_source_gate") is False,
        "exercise the complete actual immutable V2 AST inside SourceWall",
    )
    accepted.append("accept-real-historical-v2-81089-ast-before-archive")
    accepted.append("accept-nine-exact-v2-owners-without-module-execution")
    accepted.append("accept-four-v2-original-roles-and-normalized-modes")
    accepted.append("distinguish-historical-v2-v12-and-corrected-v13-adapters")
    baseline = (
        b"REPAIRED_SOURCE_OWNERS: tuple = "
        + repr(HISTORICAL_V2_REPAIRED_SOURCE_OWNERS).encode("ascii")
        + b"\n"
    )
    require(
        extract_historical_v2_helper_owners(baseline)
        == HISTORICAL_V2_REPAIRED_SOURCE_OWNERS,
        "accept one genuinely exact literal historical owner tuple",
    )
    accepted.append("accept-exact-literal-only-v2-owner-ast")
    historical = HISTORICAL_V2_REPAIRED_SOURCE_OWNERS
    variants: list[tuple[str, bytes]] = [
        (
            "reject-v2-missing-owner-assignment",
            b"UNRELATED_OWNERS: tuple = ()\n",
        ),
        (
            "reject-v2-duplicate-annotated-owner-assignment",
            baseline + baseline,
        ),
        (
            "reject-v2-duplicate-plain-owner-assignment",
            baseline + b"REPAIRED_SOURCE_OWNERS = ()\n",
        ),
        (
            "reject-v2-augmented-owner-assignment",
            baseline + b"REPAIRED_SOURCE_OWNERS += ()\n",
        ),
        (
            "reject-v2-deleted-owner-assignment",
            baseline + b"del REPAIRED_SOURCE_OWNERS\n",
        ),
        (
            "reject-v2-dynamic-owner-call",
            b"REPAIRED_SOURCE_OWNERS: tuple = tuple()\n",
        ),
        (
            "reject-v2-malformed-owner-source",
            b"REPAIRED_SOURCE_OWNERS: tuple = (\n",
        ),
    ]
    for index, (relative, fingerprint, count) in enumerate(historical):
        for field, replacement in (
                ("path", ("../" + relative, fingerprint, count)),
                ("sha256", (relative, "0" * 64, count)),
                ("bytes", (relative, fingerprint, count + 1))):
            rows = list(historical)
            rows[index] = replacement
            variants.append((
                "reject-v2-owner-" + str(index) + "-" + field,
                b"REPAIRED_SOURCE_OWNERS: tuple = "
                + repr(tuple(rows)).encode("ascii") + b"\n",
            ))
    for fingerprint, tag in (
            (HISTORICAL_DERIVED_PUBLIC_SHA256, "historical-v12-f8afb"),
            (CORRECTED_PUBLIC_SHA256, "corrected-v13-d47a"),
            (ORIGINALS["adapter"]["sha256"], "original-target-6fb6")):
        rows = list(historical)
        relative, _, count = rows[0]
        rows[0] = (relative, fingerprint, count)
        variants.append((
            "reject-v2-adapter-substitution-" + tag,
            b"REPAIRED_SOURCE_OWNERS: tuple = "
            + repr(tuple(rows)).encode("ascii") + b"\n",
        ))
    for rows, tag in (
            (historical[1:], "missing-owner"),
            (historical + (historical[0],), "duplicate-owner"),
            ((historical[1], historical[0], *historical[2:]),
             "reordered-owner")):
        variants.append((
            "reject-v2-" + tag,
            b"REPAIRED_SOURCE_OWNERS: tuple = "
            + repr(tuple(rows)).encode("ascii") + b"\n",
        ))
    for tag, raw in variants:
        _expect_rejected(
            tag,
            lambda value=raw: extract_historical_v2_helper_owners(value),
            rejected,
        )
    for field, value, tag in (
            ("schema", "foreign-historical-helper",
             "reject-v2-contract-foreign-schema"),
            ("version", 3, "reject-v2-contract-stale-version"),
            ("family", "c", "reject-v2-contract-cross-family"),
            ("status", "PASS", "reject-v2-contract-fake-pass"),
            ("campaign_label", LABEL,
             "reject-v2-contract-confused-v13-label")):
        hostile = copy.deepcopy(frozen_contract)
        hostile[field] = value
        _expect_rejected(
            tag,
            lambda value=hostile:
                authenticate_historical_v2_helper_source(source_raw, value),
            rejected,
        )
    for index, role in enumerate(ROLE_ORDER):
        for field, value in (
                ("role", "foreign-" + role),
                ("repaired_sha256", "0" * 64),
                ("repaired_bytes", 1)):
            hostile = copy.deepcopy(frozen_contract)
            hostile["four_original_target_owners"][index][field] = value
            _expect_rejected(
                "reject-v2-role-" + role + "-" + field,
                lambda value=hostile:
                    authenticate_historical_v2_helper_source(
                        source_raw, value,
                    ),
                rejected,
            )
        hostile = copy.deepcopy(frozen_contract)
        hostile["four_original_target_owners"][index]["original"]["mode"] = (
            "0777"
        )
        _expect_rejected(
            "reject-v2-role-" + role + "-original-mode",
            lambda value=hostile:
                authenticate_historical_v2_helper_source(source_raw, value),
            rejected,
        )
    return {
        "status": "PASS",
        "historical_v2_public_adapter_sha256":
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
        "historical_v2_public_adapter_bytes":
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        "historical_source_owner_count": len(historical),
        "real_source_ast_evaluated": True,
        "actual_module_imported": False,
        "actual_module_executed": False,
        "actual_helper_invoked": False,
        "hostile_owner_variants_tested": len(variants),
        "holdout": "NOT OPENED",
    }


def source_self_test(source_pin: str, protocol_pin: str,
                     contract_pin: str) -> dict[str, Any]:
    checked_digest(source_pin, "synthetic V7 source")
    checked_digest(protocol_pin, "synthetic V7 protocol")
    checked_digest(contract_pin, "synthetic V7 machine contract")
    # Read only this exact source, the immutable helper source and tiny
    # historical contract; never import, execute or invoke V2.
    actual_source_raw, _ = read_owned(
        (SOURCE_RELATIVE, source_pin, _exact_source_size(source_pin)),
        maximum=MAX_SOURCE_BYTES,
    )
    helper_raw, _ = read_owned(
        V2["source"], maximum=MAX_SOURCE_BYTES,
    )
    helper_contract_raw, _ = read_owned(
        V2["contract"], maximum=MAX_SOURCE_BYTES,
    )
    helper_contract = strict_document(
        helper_contract_raw, "actual immutable historical V2 source contract",
    )
    accepted: list[str] = []
    rejected: list[str] = []
    with SourceWall() as wall:
        contract = protocol_document(source_pin, protocol_pin)
        require(validate_contract(copy.deepcopy(contract), source_pin,
                                  protocol_pin) == contract,
                "accept the one exact pure corrected Rust V7 source freeze")
        accepted.append("accept-exact-corrected-rust-v7-v13-source-freeze")
        require(sys.modules.get("unicodedata") is unicodedata,
                "preload the trusted CPython Unicode-name database "
                "before physically blocking imports")
        accepted.append("accept-preloaded-trusted-cpython-unicodedata")
        historical_helper_controls = (
            synthetic_historical_v2_helper_controls(
                helper_raw, helper_contract, accepted, rejected,
            )
        )
        require(contract["original_oracle"]["candidate_case_producer_version"] == 4
                and contract["original_oracle"]
                ["corrected_reference_records_sha256"]
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and contract["actual_corrected_candidate_context_reference"]
                ["actual_reference_status"] == "PASS"
                and contract["actual_corrected_candidate_context_reference"]
                ["actual_publication_status"] == "PASS"
                and contract["actual_corrected_candidate_context_reference"]
                ["actual_distinct_reference_process_ids"]
                == list(CORRECTED_REFERENCE_PIDS)
                and contract["preserved_v39_overview"]
                ["overview_version"] == 39
                and contract["preserved_v39_overview"]
                ["same_context_reference_correction_status"] == "PASS"
                and contract["preserved_v39_overview"]
                ["all_candidate_matching_blocked"] is True
                and contract["preserved_v40_overview"]
                ["overview_version"] == 40
                and contract["preserved_v40_overview"]
                ["same_context_reference_correction_status"] == "PASS"
                and contract["preserved_v40_overview"]
                ["all_candidate_matching_blocked"] is True
                and contract["preserved_v40_overview"]
                ["zig_scanner_phrase_source_repair"]
                ["status"]
                == "SOURCE FROZEN; NOT APPLIED; CORRECTED CANDIDATE NOT RUN"
                and contract["preserved_v40_overview"]
                ["zig_scanner_phrase_source_repair"]
                ["candidate_workers_started"] == 0
                and contract["preserved_v41_overview"]
                ["overview_version"] == 41
                and contract["preserved_v41_overview"]
                ["owners"] == grouped_owners(V41)
                and contract["preserved_v41_overview"]
                ["previous_v40_overview"] == grouped_owners(V40)
                and contract["preserved_v41_overview"]
                ["corrected_c_only_runner_family"] == "c"
                and contract["preserved_v41_overview"]
                ["corrected_c_only_runnable_family_count"] == 1
                and contract["preserved_v41_overview"]
                ["corrected_c_matching_status"] == "NOT RUN"
                and contract["preserved_v41_overview"]
                ["rust_v6_runner_status_at_v41_publication"] == "UNCOMMITTED"
                and contract["corrected_c_only_runner_v10"]
                ["owners"] == grouped_owners(CORRECTED_C_ONLY_V10)
                and contract["corrected_c_only_runner_v10"]
                ["runnable_candidate_families"] == ["c"]
                and contract["corrected_c_only_runner_v10"]
                ["candidate_workers_started"] == 0
                and contract["superseded_reviewed_v40_rust_v6_source_freeze"]
                ["historical_snapshot_only"] is True
                and contract["superseded_reviewed_v40_rust_v6_source_freeze"]
                ["committed"] is False
                and contract["published_current_v43_overview"]
                ["overview_version"] == 43
                and contract["published_current_v43_overview"]
                ["owners"] == grouped_owners(V43)
                and contract["published_current_v43_overview"]
                ["previous_v42_overview"] == grouped_owners(V42)
                and contract["published_current_v43_overview"]
                ["actually_runnable_candidate_family_count"] == 0
                and contract["published_current_v43_overview"]
                ["authenticated_evidence_owner_lower_bound"] == 166
                and contract["published_current_v43_overview"]
                ["authenticated_history_reference_lower_bound"] == 171
                and contract["published_current_v43_overview"]
                ["actual_v6_controller_status"] == "FAIL"
                and contract["published_current_v43_overview"]
                ["actual_v6_source_build_archive_read_count"] == 1
                and contract["preserved_v42_overview"]
                ["historical_evidence_owner_lower_bound"] == 164
                and contract["preserved_v42_overview"]
                ["historical_history_reference_lower_bound"] == 169
                and contract["historical_v2_helper_authentication"]
                ["historical_public_adapter"]["sha256"]
                == HISTORICAL_V2_REPAIRED_PUBLIC_SHA256
                and contract["historical_v2_helper_authentication"]
                ["historical_repaired_source_owner_count"] == 9
                and contract["preserved_actual_v6_preflight_failure"]
                ["owners"] == grouped_owners(ACTUAL_V6_PREFLIGHT_FAILURE),
                "accept the exact current pushed V43 genuine failure, "
                "V42 history, real 81089 V2 helper and complete P0")
        accepted.append("accept-pushed-corrected-six-family-v4-producer")
        accepted.append("accept-real-complete-6912-case-two-reference-baseline")
        accepted.append("accept-all-original-96-named-context-cache-cases")
        accepted.append("accept-preserved-falsified-script-context-history")
        accepted.append("accept-exact-preserved-whitespace-clean-v39-history")
        accepted.append("accept-exact-preserved-pushed-v40-overview")
        accepted.append("accept-exact-preserved-pushed-v41-overview")
        accepted.append("accept-exact-current-pushed-v43-overview")
        accepted.append("accept-preserved-one-real-v6-controller-failure")
        accepted.append("accept-historical-v42-164-169-current-v43-166-171")
        accepted.append("accept-exact-committed-c-only-v8-v10-runner")
        accepted.append("accept-uncommitted-superseded-v40-rust-v6-audit")
        accepted.append("accept-frozen-unapplied-zig-scanner-without-matching")
        require(sum(count for _, count in SUITES) == CASE_COUNT
                and len(SUITES) == SUITE_COUNT,
                "retain all thirteen unchanged original suite denominators")
        accepted.append("accept-all-thirteen-original-suites-and-31237-cases")
        report, receipt, archive = synthetic_v13_fixture()
        observed = validate_v13_report(report, receipt, archive,
                                       inspect_private=False)
        require(observed["actual_process_count"] == 28
                and len(observed["phases"]) == 2,
                "accept both complete synthetic independent source-build phases")
        accepted.append("accept-two-exact-corrected-nine-owner-build-phases")
        accepted.append("accept-twenty-eight-distinct-source-build-processes")
        accepted.append("accept-reproduced-v11-identical-native-bytes-only-with-v13-proof")
        accepted.append("accept-corrected-private-v3-d47a-public-adapter")
        accepted.append("accept-both-real-own-engine-elf-export-profiles")
        accepted.append("accept-pushed-v39-at-least-164-real-evidence-owners")
        accepted.append("accept-pushed-v39-at-least-169-authenticated-history-references")
        accepted.append("accept-four-exact-original-inode-identities")
        accepted.append("accept-authentic-394-call-original-interpreter-policy")
        accepted.append("accept-publication-pass-only-as-durable-publication")
        worker_controls = synthetic_worker_hostile_controls(
            source_pin, protocol_pin, contract_pin, accepted, rejected)
        actual_worker_recovery_controls = (
            synthetic_actual_worker_recovery_controls(
                actual_source_raw,
                source_pin,
                protocol_pin,
                contract_pin,
                wall,
                accepted,
                rejected,
            )
        )
        bad_contract_fields: tuple[tuple[str, Any], ...] = (
            ("schema", SCHEMA),
            ("status", "PASS"), ("version", 3), ("family", "c"),
            ("campaign_label", "phase2-v11-rust-dual-overlay-original-p0"),
        )
        for field, value in bad_contract_fields:
            hostile = copy.deepcopy(contract)
            hostile[field] = value
            _expect_rejected("reject-contract-" + field,
                             lambda item=hostile: validate_contract(
                                 item, source_pin, protocol_pin), rejected)
        for section, owner_key, expected in (
            ("original_oracle", "producer", PRODUCER),
            ("published_current_v43_overview", "owners", V43),
            ("preserved_v42_overview", "owners", V42),
            ("preserved_v41_overview", "owners", V41),
            ("historical_v2_helper_authentication", "owners", V2),
            ("preserved_actual_v6_preflight_failure", "owners",
             ACTUAL_V6_PREFLIGHT_FAILURE),
            ("preserved_actual_v6_preflight_failure",
             "historical_v6_controller", V6_PREDECESSOR),
            ("preserved_v40_overview", "owners", V40),
            ("preserved_v39_overview", "owners", V39),
            ("corrected_c_only_runner_v10", "owners", CORRECTED_C_ONLY_V10),
            ("superseded_reviewed_v40_rust_v6_source_freeze", "owners",
             SUPERSEDED_REVIEWED_V40_RUST_V6),
            ("actual_corrected_candidate_context_reference",
             "owners", CORRECTED_REFERENCE),
            ("actual_corrected_v13_build", "owners", BUILD),
        ):
            for role in expected:
                for field, replacement in (
                    ("sha256", "0" * 64),
                    ("path", "foreign/substituted-owner"),
                    ("bytes", 1),
                ):
                    hostile = copy.deepcopy(contract)
                    hostile[section][owner_key][role][field] = replacement
                    _expect_rejected(
                        "reject-" + section + "-" + role + "-" + field,
                        lambda item=hostile: validate_contract(
                            item, source_pin, protocol_pin),
                        rejected,
                    )
        for index, (name, count) in enumerate(SUITES):
            for changed_name, changed_count, label in (
                (name + "-forged", count, "identity"),
                (name, count + 1, "denominator"),
            ):
                hostile = copy.deepcopy(contract)
                hostile["original_oracle"]["source_ordered_suites"][index] = {
                    "id": changed_name, "case_execution_count": changed_count}
                _expect_rejected(
                    "reject-original-" + name + "-" + label,
                    lambda item=hostile: validate_contract(
                        item, source_pin, protocol_pin), rejected)
        for section, field, value, name in (
            ("original_oracle", "case_execution_denominator", 31236,
             "omit-original-case"),
            ("original_oracle", "candidate_case_producer_version", 3,
             "reuse-stale-v3-case-producer"),
            ("original_oracle", "corrected_reference_records_sha256",
             HISTORICAL_FULL_PUBLIC_RECORDS_SHA256,
             "reuse-falsified-full-script-context-reference"),
            ("original_oracle", "corrected_cache_records_sha256",
             HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
             "reuse-falsified-96-case-script-context-reference"),
            ("original_oracle",
             "candidate_run_uses_both_complete_reference_vectors", False,
             "drop-independent-second-corrected-reference-vector"),
            ("actual_corrected_candidate_context_reference",
             "actual_reference_status", "NOT RUN",
             "mistake-earlier-source-freeze-for-real-passing-reference"),
            ("actual_corrected_candidate_context_reference",
             "actual_publication_status", "FAIL",
             "accept-undurable-corrected-reference-publication"),
            ("actual_corrected_candidate_context_reference",
             "actual_distinct_reference_process_count", 1,
             "accept-one-corrected-reference-process"),
            ("actual_corrected_candidate_context_reference",
             "actual_distinct_reference_process_ids", [81, 81],
             "reuse-corrected-reference-process-id"),
            ("actual_corrected_candidate_context_reference",
             "case_count_per_reference", 96,
             "substitute-cache-subset-for-complete-corrected-reference"),
            ("actual_corrected_candidate_context_reference",
             "full_reference_records_sha256",
             HISTORICAL_FULL_PUBLIC_RECORDS_SHA256,
             "substitute-falsified-historical-full-reference-vector"),
            ("actual_corrected_candidate_context_reference",
             "cache_records_sha256",
             HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
             "substitute-falsified-historical-cache-vector"),
            ("actual_corrected_candidate_context_reference",
             "historical_96_case_falsification_removed", True,
             "delete-real-falsified-96-case-history"),
            ("actual_corrected_candidate_context_reference",
             "original_public_cases_removed", 96,
             "remove-original-falsifying-cache-cases"),
            ("actual_corrected_candidate_context_reference",
             "additional_private_waivers", 1,
             "waive-real-candidate-context-cache-failure"),
            ("actual_corrected_candidate_context_reference",
             "c_pattern_equality_failure_waived", True,
             "silently-waive-real-c-pattern-subclass-equality"),
            ("published_current_v43_overview", "overview_version", 42,
             "mislabel-v42-history-as-current-v43"),
            ("published_current_v43_overview",
             "authenticated_evidence_owner_lower_bound", 164,
             "erase-two-real-v6-failure-evidence-owners"),
            ("published_current_v43_overview",
             "authenticated_history_reference_lower_bound", 169,
             "erase-two-real-v6-failure-history-references"),
            ("published_current_v43_overview",
             "actually_runnable_candidate_family_count", 1,
             "invent-a-runnable-candidate-after-real-v6-failure"),
            ("published_current_v43_overview",
             "actual_v6_controller_status", "PASS",
             "hide-real-v6-controller-failure"),
            ("published_current_v43_overview",
             "actual_v6_source_build_archive_read_count", 0,
             "hide-real-historical-v13-source-build-archive-read"),
            ("published_current_v43_overview",
             "actual_v6_controller_ledger_omits_archive_effect", False,
             "rewrite-the-genuine-v6-effect-ledger-omission"),
            ("historical_v2_helper_authentication",
             "historical_repaired_source_owner_count", 8,
             "omit-an-actual-v2-historical-source-owner"),
            ("historical_v2_helper_authentication",
             "module_imported_by_source_gate", True,
             "import-historical-helper-in-source-only-mode"),
            ("historical_v2_helper_authentication",
             "module_executed_by_source_gate", True,
             "execute-historical-helper-in-source-only-mode"),
            ("preserved_actual_v6_preflight_failure",
             "actual_source_build_archive_read_count", 0,
             "suppress-independently-observed-v6-build-archive-effect"),
            ("preserved_actual_v6_preflight_failure",
             "candidate_qualified", True,
             "qualify-a-v6-candidate-that-never-started"),
            ("preserved_v41_overview", "overview_version", 40,
             "mislabel-historical-v40-as-current-after-v41-push"),
            ("preserved_v41_overview",
             "same_context_reference_correction_status", "NOT RUN",
             "erase-passing-reference-from-current-v41"),
            ("preserved_v41_overview",
             "authenticated_evidence_owner_lower_bound", 161,
             "regress-current-v41-evidence-lower-bound"),
            ("preserved_v41_overview",
             "authenticated_history_reference_lower_bound", 166,
             "regress-current-v41-history-lower-bound"),
            ("preserved_v41_overview",
             "corrected_c_only_runner_family", "rust",
             "mislabel-c-only-runner-as-rust"),
            ("preserved_v41_overview",
             "corrected_c_only_runnable_family_count", 6,
             "claim-all-six-source-designs-are-runnable"),
            ("preserved_v41_overview",
             "corrected_c_matching_status", "PASS",
             "claim-unobserved-c-matching-passed"),
            ("preserved_v41_overview",
             "corrected_c_candidate_workers_started", 1,
             "invent-a-corrected-c-candidate-worker"),
            ("preserved_v41_overview",
             "corrected_c_candidate_qualified", True,
             "qualify-c-without-complete-original-matching"),
            ("preserved_v41_overview",
             "rust_v6_runner_status_at_v41_publication", "FROZEN",
             "backdate-dedicated-rust-runner-into-v41-publication"),
            ("corrected_c_only_runner_v10",
             "runnable_candidate_family_count", 6,
             "mistake-source-inventory-for-six-runnable-families"),
            ("corrected_c_only_runner_v10", "family", "rust",
             "run-rust-through-c-only-runner"),
            ("corrected_c_only_runner_v10",
             "candidate_workers_started", 1,
             "claim-c-worker-started-in-source-freeze"),
            ("corrected_c_only_runner_v10", "candidate_qualified", True,
             "qualify-c-in-source-only-runner-freeze"),
            ("superseded_reviewed_v40_rust_v6_source_freeze",
             "committed", True,
             "claim-superseded-v40-rust-draft-was-committed"),
            ("superseded_reviewed_v40_rust_v6_source_freeze",
             "pushed", True,
             "claim-superseded-v40-rust-draft-was-pushed"),
            ("superseded_reviewed_v40_rust_v6_source_freeze",
             "historical_snapshot_only", False,
             "present-superseded-v40-rust-pins-as-live-owners"),
            ("preserved_v40_overview", "overview_version", 39,
             "mislabel-historical-v39-as-current-after-v40-push"),
            ("preserved_v40_overview",
             "same_context_reference_correction_status", "NOT RUN",
             "erase-passing-reference-from-current-v40"),
            ("preserved_v40_overview",
             "authenticated_evidence_owner_lower_bound", 161,
             "regress-current-v40-evidence-lower-bound"),
            ("preserved_v40_overview",
             "authenticated_history_reference_lower_bound", 166,
             "regress-current-v40-history-lower-bound"),
            ("preserved_v40_overview",
             "all_candidate_matching_blocked", False,
             "start-candidate-before-all-current-v40-runner-freezes"),
            ("preserved_v40_overview",
             "qualified_candidate_count", 1,
             "claim-current-v40-candidate-qualified-without-matching"),
            ("preserved_v39_overview", "overview_version", 38,
             "reuse-stale-published-v38-overview"),
            ("preserved_v39_overview",
             "same_context_reference_correction_status", "NOT RUN",
             "claim-corrected-reference-before-real-publication"),
            ("preserved_v39_overview",
             "authenticated_evidence_owner_lower_bound", 161,
             "regress-evidence-lower-bound-to-stale-v35"),
            ("preserved_v39_overview",
             "authenticated_history_reference_lower_bound", 166,
             "regress-history-lower-bound-to-stale-v35"),
            ("preserved_v39_overview",
             "all_candidate_matching_blocked", False,
             "authorize-candidate-before-all-runner-freezes-are-pushed"),
            ("preserved_v39_overview",
             "qualified_candidate_count", 1,
             "claim-a-correctness-qualified-candidate-without-a-run"),
            ("original_oracle", "suite_count", 12, "omit-original-suite"),
            ("original_oracle", "named_private_waiver_count", 12,
             "add-private-waiver"),
            ("original_oracle", "nested_interpreter_events", 385,
             "accept-old-failed-nested-lifecycle"),
            ("original_oracle", "canonical_public_module",
             "candidates.repaired_rust_candidate", "accept-wrapper-module"),
            ("original_oracle", "stdlib_re_fallback_allowed", True,
             "accept-standard-library-fallback"),
            ("original_oracle", "external_regex_dependency_allowed", True,
             "accept-external-regex-engine"),
            ("original_oracle", "cross_family_matching_allowed", True,
             "accept-borrowed-candidate-engine"),
            ("current_historical_accounting",
             "actual_evidence_owner_count_before_new_campaign", 150,
             "miscount-actual-owner"),
            ("current_historical_accounting",
             "actual_authenticated_reference_count_before_new_campaign", 155,
             "miscount-actual-reference"),
            ("preserved_v35_history", "actual_rust_semantic_mismatch_count",
             1086, "hide-original-rust-loss"),
            ("preserved_v35_history", "actual_c_semantic_mismatch_count", 0,
             "hide-original-c-loss"),
            ("preserved_v35_history", "actual_zig_semantic_mismatch_count", 0,
             "hide-original-zig-loss"),
            ("public_recovery", "group_atomic", True,
             "falsely-claim-group-atomic-replacement"),
            ("public_recovery", "sigkill_automatically_recovered", True,
             "claim-automatic-sigkill-recovery"),
            ("public_recovery", "power_failure_automatically_recovered", True,
             "claim-automatic-power-loss-recovery"),
            ("future_lossless_publication", "publication_pass_means",
             "CANDIDATE PASSED", "equate-publication-and-correctness"),
            ("future_lossless_publication",
             "worker_launch_attempt_recorded_before_spawn", False,
             "discard-original-worker-launch-attempt"),
            ("future_lossless_publication",
             "started_worker_pid_retained_before_communication", False,
             "discard-started-original-worker-pid"),
            ("future_lossless_publication",
             "worker_attempts_starts_and_complete_observations_are_distinct",
             False, "equate-started-and-fully-observed-original-worker"),
            ("future_lossless_publication",
             "distinct_positive_worker_process_ids_required", False,
             "accept-duplicate-or-missing-original-worker-pid"),
            ("future_lossless_publication",
             "oversized_worker_stream_retains_full_size_and_sha256", False,
             "discard-oversized-worker-stream-size-or-sha256"),
            ("future_lossless_publication",
             "truncated_worker_stream_never_counts_as_complete", False,
             "count-truncated-worker-stream-as-complete"),
            ("future_lossless_publication",
             "numeric_total_mismatches_require_all_thirteen_observations",
             False, "publish-one-of-thirteen-numeric-mismatch-total"),
            ("future_lossless_publication", "partial_total_mismatches", 0,
             "invent-unmeasured-original-mismatch-total"),
            ("future_lossless_publication",
             "authorized_run_entry_failure_retains_actual_effect_ledger",
             False, "discard-activated-run-effect-ledger"),
            ("future_lossless_publication",
             "publication_failure_never_reports_source_only_zero_effects",
             False, "claim-zero-effects-after-worker-or-publication"),
        ):
            hostile = copy.deepcopy(contract)
            hostile[section][field] = value
            _expect_rejected("reject-" + name,
                             lambda item=hostile: validate_contract(
                                 item, source_pin, protocol_pin), rejected)
        for role in ROLE_ORDER:
            for field, value in (("inode", 999999), ("device", 999999),
                                 ("mode", 0o777), ("nlink", 2),
                                 ("sha256", "0" * 64)):
                hostile = copy.deepcopy(contract)
                record = next(item for item in
                              hostile["four_original_target_owners"]
                              if item["role"] == role)
                record["original"][field] = value
                _expect_rejected("reject-" + role + "-original-" + field,
                                 lambda item=hostile: validate_contract(
                                     item, source_pin, protocol_pin), rejected)
        for field, value, tag in (
            ("schema", "rebar-phase2-owned-native-source-build-v11", "v11-schema"),
            ("status", "FAIL", "failed-build"),
            ("family", "c", "foreign-family"),
            ("label", "phase2-v11-rust-dual-overlay", "stale-build-label"),
            ("source_sha256", V3["source"][1], "stale-source"),
            ("phase_count", 1, "missing-phase"),
            ("actual_compiler_process_count", 27, "missing-real-process"),
            ("public_derived_sha256", HISTORICAL_DERIVED_PUBLIC_SHA256,
             "old-f8afb-public-adapter"),
            ("corrected_public_overlay_apply_count", 1,
             "missing-corrected-private-apply"),
            ("bridge_overlay_apply_count", 1, "missing-bridge-apply"),
            ("candidate_qualified", True, "build-as-qualified-candidate"),
            ("candidate_imports", 1, "source-build-imported-candidate"),
            ("hidden_cases_read", 1, "source-build-opened-holdout"),
            ("clock_samples", 1, "source-build-timed-matching"),
        ):
            hostile = copy.deepcopy(report)
            hostile[field] = value
            _expect_rejected("reject-real-v13-" + tag,
                             lambda item=hostile: validate_v13_report(
                                 item, receipt, archive,
                                 inspect_private=False), rejected)
        for phase_index, phase_name in enumerate(PHASE_NAMES):
            for relative, _, _ in CORRECTED_SOURCE_OWNERS:
                hostile = copy.deepcopy(report)
                hostile["phases"][phase_index]["fresh_source_owners"][relative]["sha256"] = "0" * 64
                _expect_rejected(
                    "reject-" + phase_name + "-source-"
                    + relative.replace("/", "-"),
                    lambda item=hostile: validate_v13_report(
                        item, receipt, archive,
                        inspect_private=False), rejected)
            for role in ("engine", "bridge"):
                for field, value in (("sha256", "0" * 64),
                                     ("size_bytes", 1),
                                     ("inode", 0),
                                     ("candidate_imported", True),
                                     ("prebuilt_artifact_read", True)):
                    hostile = copy.deepcopy(report)
                    hostile["phases"][phase_index]["native_outputs"][role][field] = value
                    _expect_rejected(
                        "reject-" + phase_name + "-" + role + "-" + field,
                        lambda item=hostile: validate_v13_report(
                            item, receipt, archive,
                            inspect_private=False), rejected)
                for field, value in (("cross_family_dependency_count", 1),
                                     ("external_regex_dependency_count", 1)):
                    hostile = copy.deepcopy(report)
                    hostile["phases"][phase_index]["native_outputs"][role]["audit"][field] = value
                    _expect_rejected(
                        "reject-" + phase_name + "-" + role + "-" + field,
                        lambda item=hostile: validate_v13_report(
                            item, receipt, archive,
                            inspect_private=False), rejected)
        for field, value in (("status", "FAIL"), ("build_status", "FAIL"),
                             ("family", "zig"),
                             ("archive_sha256", "0" * 64),
                             ("uncompressed_bytes", V13_PLAIN_BYTES - 1),
                             ("public_derived_sha256",
                              HISTORICAL_DERIVED_PUBLIC_SHA256),
                             ("candidate_processes_started", 1),
                             ("hidden_cases_read", 1)):
            hostile = copy.deepcopy(receipt)
            hostile[field] = value
            _expect_rejected("reject-v13-build-receipt-" + field,
                             lambda item=hostile: validate_v13_report(
                                 report, item, archive,
                                 inspect_private=False), rejected)
        for index in (0, 1, 13, 14, 27):
            hostile = copy.deepcopy(report)
            hostile["compiler_processes"][index]["exit_status"] = 1
            _expect_rejected("reject-failed-real-v13-process-" + str(index),
                             lambda item=hostile: validate_v13_report(
                                 item, receipt, archive,
                                 inspect_private=False), rejected)
        duplicate = copy.deepcopy(report)
        duplicate["compiler_processes"][1]["pid"] = (
            duplicate["compiler_processes"][0]["pid"])
        _expect_rejected("reject-duplicate-real-v13-process-identity",
                         lambda: validate_v13_report(
                             duplicate, receipt, archive,
                             inspect_private=False), rejected)
        for raw, tag in ((b'{"same":1,"same":2}\n', "duplicate-json"),
                         (b'{"number":NaN}\n', "json-nan"),
                         (b'{"number":Infinity}\n', "json-infinity"),
                         (b'{ "same": 1 }\n', "noncanonical-json")):
            _expect_rejected("reject-" + tag,
                             lambda value=raw: strict_document(
                                 value, "synthetic hostile"), rejected)
        hostile_raw = gzip.compress(b"synthetic\n", mtime=0)
        for raw, tag in ((hostile_raw + hostile_raw, "two-gzip-members"),
                         (hostile_raw[:-3], "truncated-gzip"),
                         (hostile_raw + b"trailing", "trailing-gzip")):
            _expect_rejected("reject-" + tag,
                             lambda value=raw: bounded_build_gzip(
                                 value, expected_sha256=digest(b"synthetic\n"),
                                 expected_size=len(b"synthetic\n")), rejected)
        actions = (
            ("file-open", lambda: builtins.open("forbidden-v6")),
            ("io-open", lambda: io.open("forbidden-v6")),
            ("path-open", lambda: Path("forbidden-v6").open()),
            ("os-open", lambda: os.open("forbidden-v6", os.O_RDONLY)),
            ("candidate-import", lambda: importlib.import_module(
                "candidates.rust_candidate")),
            ("direct-candidate-import", lambda: builtins.__import__(
                "candidates.rust_candidate")),
            ("source-loader-create", lambda:
                importlib.machinery.SourceFileLoader.create_module(None, None)),
            ("source-loader-exec", lambda:
                importlib.machinery.SourceFileLoader.exec_module(None, None)),
            ("sourceless-loader-create", lambda:
                importlib.machinery.SourcelessFileLoader.create_module(
                    None, None)),
            ("sourceless-loader-exec", lambda:
                importlib.machinery.SourcelessFileLoader.exec_module(
                    None, None)),
            ("extension-loader-create", lambda:
                importlib.machinery.ExtensionFileLoader.create_module(
                    None, None)),
            ("extension-loader-exec", lambda:
                importlib.machinery.ExtensionFileLoader.exec_module(
                    None, None)),
            ("native-load", lambda: ctypes.CDLL("forbidden-v6.so")),
            ("python-native-load", lambda: ctypes.PyDLL("forbidden-v6.so")),
            ("process", lambda: subprocess.run(("forbidden-v6",))),
            ("worker", lambda: subprocess.Popen(("forbidden-v6",))),
            ("direct-posix-process", lambda: os.posix_spawn(
                "forbidden-v6", ["forbidden-v6"], {})),
            ("gzip-archive-open", lambda: gzip.open("forbidden-v6.json.gz")),
            ("gzip-archive-file", lambda: gzip.GzipFile(
                "forbidden-v6.json.gz")),
            ("recovery-root", lambda: tempfile.mkdtemp()),
            ("network", lambda: socket.socket()),
            ("thread", lambda: threading.Thread(target=lambda: None).start()),
            ("locale", lambda: locale.setlocale(locale.LC_CTYPE)),
            ("signal", lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)),
            ("signal-mask", lambda: signal.pthread_sigmask(
                signal.SIG_BLOCK, {signal.SIGINT})),
            ("lock", lambda: fcntl.flock(0, fcntl.LOCK_EX)),
            ("replace", lambda: os.replace("forbidden-a", "forbidden-b")),
            ("hardlink", lambda: os.link("forbidden-a", "forbidden-b")),
            ("journal-fsync", lambda: os.fsync(0)),
            ("random-root", lambda: os.urandom(16)),
            ("clock", lambda: time.perf_counter()),
        )
        for tag, action in actions:
            _expect_rejected("block-actual-" + tag, action, rejected)
        for module_name, method, counter in (
            ("_imp", "create_dynamic", "native_library_loads"),
            ("_imp", "exec_dynamic", "native_library_loads"),
            ("_ctypes", "dlopen", "native_library_loads"),
            ("_posixsubprocess", "fork_exec", "processes"),
            ("posix", "posix_spawn", "processes"),
            ("_thread", "start_new_thread", "threads"),
        ):
            module = sys.modules.get(module_name)
            if module is not None and hasattr(module, method):
                method_before = wall.blocked.get(counter, 0)
                _expect_rejected(
                    "block-direct-" + module_name + "-" + method,
                    lambda owner=module, name=method: getattr(owner, name)(
                        None
                    ),
                    rejected,
                )
                require(wall.blocked.get(counter, 0) == method_before + 1,
                        "physically reject direct source-only effect: "
                        + module_name + "." + method)
        require(wall.blocked.get("candidate_imports", 0) >= 6
                and wall.blocked.get("native_library_loads", 0) >= 4
                and wall.blocked.get("processes", 0) >= 3
                and wall.blocked.get("filesystem_reads", 0) >= 4
                and wall.blocked.get("actual_archive_operations", 0) >= 1,
                "exercise the actual direct builtins/import/native/process/"
                "archive barriers")
        require(len(rejected) >= 180,
                "run substantial hostile V13, owner, original-case and effect controls")
        blocked = dict(wall.blocked)
    return {
        "schema": SCHEMA + "-source-only-self-test",
        "status": "PASS", "version": 7, "synthetic": True,
        "source_sha256": source_pin,
        "protocol_sha256": protocol_pin,
        "contract_sha256": contract_pin,
        "accepted_control_count": len(accepted),
        "accepted_controls": accepted,
        "rejected_hostile_control_count": len(rejected),
        "rejected_hostile_controls": rejected,
        "blocked_source_only_effects": blocked,
        "synthetic_original_worker_controls": worker_controls,
        "actual_worker_recovery_source_controls":
            actual_worker_recovery_controls,
        "historical_v2_helper_source_controls":
            historical_helper_controls,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "original_producer_version": 4,
        "original_producer_source_sha256": PRODUCER["source"][1],
        "original_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_producer_contract_sha256": PRODUCER["contract"][1],
        "published_current_v43_source_sha256": V43["source"][1],
        "published_current_v43_inputs_sha256": V43["inputs"][1],
        "published_current_v43_summary_sha256": V43["summary"][1],
        "published_current_v43_svg_sha256": V43["svg"][1],
        "current_overview_version": 43,
        "preserved_v42_source_sha256": V42["source"][1],
        "preserved_v42_inputs_sha256": V42["inputs"][1],
        "preserved_v42_summary_sha256": V42["summary"][1],
        "preserved_v42_svg_sha256": V42["svg"][1],
        "preserved_v41_source_sha256": V41["source"][1],
        "preserved_v41_inputs_sha256": V41["inputs"][1],
        "preserved_v41_summary_sha256": V41["summary"][1],
        "preserved_v41_svg_sha256": V41["svg"][1],
        "historical_v2_public_adapter_sha256":
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
        "historical_v2_public_adapter_bytes":
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        "actual_v6_preflight_failure_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["failure"][1],
        "actual_v6_preflight_observation_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["observation"][1],
        "preserved_v40_source_sha256": V40["source"][1],
        "preserved_v40_inputs_sha256": V40["inputs"][1],
        "preserved_v40_summary_sha256": V40["summary"][1],
        "preserved_v40_svg_sha256": V40["svg"][1],
        "corrected_c_only_runner_v10_source_sha256":
            CORRECTED_C_ONLY_V10["runner"][1],
        "corrected_c_only_worker_v8_source_sha256":
            CORRECTED_C_ONLY_V10["worker"][1],
        "corrected_c_only_protocol_v10_sha256":
            CORRECTED_C_ONLY_V10["protocol"][1],
        "corrected_c_only_contract_v10_sha256":
            CORRECTED_C_ONLY_V10["contract"][1],
        "first_party_source_inventory_family_count": 6,
        "corrected_c_only_runnable_family_count": 1,
        "corrected_c_matching_status": "NOT RUN",
        "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
        "preserved_v39_source_sha256": V39["source"][1],
        "preserved_v39_inputs_sha256": V39["inputs"][1],
        "preserved_v39_summary_sha256": V39["summary"][1],
        "preserved_v39_svg_sha256": V39["svg"][1],
        "corrected_reference_status": "PASS",
        "corrected_reference_publication_status": "PASS",
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count_per_worker":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_actual_worker_count": 2,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "historical_falsified_script_context_records_sha256":
            HISTORICAL_FALSIFIED_REFERENCE_RECORDS_SHA256,
        "all_candidate_matching_blocked": True,
        "actual_v13_source_build_process_count": 28,
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "actual_evidence_owner_count_before_new_campaign":
        CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_authenticated_reference_count_before_new_campaign":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "repository_evidence_owner_lower_bound":
            CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "authenticated_reference_lower_bound":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "later_append_only_evidence_allowed": True,
        "historical_rust_semantic_mismatch_count": 1036,
        "historical_rust_verified_passing_case_count": 8965,
        "historical_c_semantic_mismatch_count": 1230,
        "historical_c_verified_passing_case_count": 7325,
        "historical_zig_semantic_mismatch_count": 1764,
        "historical_zig_verified_passing_case_count": 3711,
        "actual_first_failure_case": ACTUAL_FIRST_MISMATCH,
        "actual_first_failure_record_sha256": ACTUAL_FIRST_MISMATCH_SHA256,
        "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
        SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
        SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_reference_receipt_sha256":
        REFERENCE["receipt"][1],
        "supplementary_signature_candidate_status": "NOT RUN",
        "supplementary_signature_candidate_cases_executed": 0,
        "supplementary_signature_reference_archive_opened": False,
        "supplementary_signature_reference_archive_decompressed": False,
        "group_atomic": False,
        **zero_effects(),
    }


def load_frozen_module(item: tuple[str, str, int], name: str) -> types.ModuleType:
    raw, _ = read_owned(item)
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / item[0])
    module.__package__ = ""
    sys.modules[name] = module
    try:
        exec(compile(raw, module.__file__, "exec", dont_inherit=True),
             module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def patched_v2_helpers(
        ledger: dict[str, Any] | None = None,
        ) -> types.ModuleType:
    require(ledger is None or type(ledger) is dict,
            "bind actual V7 helper verification to its genuine effect ledger")
    if ledger is not None:
        ledger["historical_v2_helper_preflight_attempted"] = True
        ledger["historical_v2_helper_source_preflight_status"] = (
            "ATTEMPTED; OUTCOME UNKNOWN"
        )
    source_raw, _ = read_owned(
        V2["source"], maximum=MAX_SOURCE_BYTES,
    )
    contract_raw, _ = read_owned(
        V2["contract"], maximum=MAX_SOURCE_BYTES,
    )
    frozen_contract = strict_document(
        contract_raw,
        "exact immutable V2 contract before native or archive effects",
    )
    authenticate_historical_v2_helper_source(source_raw, frozen_contract)
    if ledger is not None:
        ledger["historical_v2_helper_source_preflight_status"] = "PASS"
        ledger["historical_v2_helper_module_preflight_status"] = (
            "ATTEMPTED; OUTCOME UNKNOWN"
        )
    v2 = load_frozen_module(
        V2["source"], "_rebar_frozen_rust_v2_helpers_for_actual_v7",
    )
    historical_roles = {
        "bridge_source": (BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
        "adapter": (
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        ),
        "engine": (ENGINE_SHA256, ENGINE_BYTES),
        "bridge": (BRIDGE_SHA256, BRIDGE_BYTES),
    }
    require(
        v2.SCHEMA == "rebar-owned-repaired-rust-original-campaign-v2"
        and tuple(v2.ROLE_ORDER) == ROLE_ORDER
        and tuple(v2.RESTORATION_ORDER) == RESTORATION_ORDER
        and tuple(v2.ORIGINAL_RUST_SOURCE_OWNERS)
        == ORIGINAL_SOURCE_OWNERS
        and tuple(v2.REPAIRED_SOURCE_OWNERS)
        == HISTORICAL_V2_REPAIRED_SOURCE_OWNERS
        and type(v2.ROLES) is dict
        and set(v2.ROLES) == set(ROLE_ORDER)
        and all(
            type(v2.ROLES[role]) is dict
            and v2.ROLES[role].get("relative")
            == ORIGINALS[role]["relative"]
            and v2.ROLES[role].get("original") == ORIGINALS[role]
            and v2.ROLES[role].get("sha256")
            == historical_roles[role][0]
            and v2.ROLES[role].get("bytes")
            == historical_roles[role][1]
            for role in ROLE_ORDER
        ),
        "authenticate every actual immutable V2 helper owner, historical "
        "81089 adapter and recovery role before any V13 archive",
    )
    if ledger is not None:
        ledger["historical_v2_helper_module_preflight_status"] = "PASS"
    roles = copy.deepcopy(v2.ROLES)
    corrected = {
        "bridge_source": (BRIDGE_SOURCE_SHA256, BRIDGE_SOURCE_BYTES),
        "adapter": (CORRECTED_PUBLIC_SHA256, CORRECTED_PUBLIC_BYTES),
        "engine": (ENGINE_SHA256, ENGINE_BYTES),
        "bridge": (BRIDGE_SHA256, BRIDGE_BYTES),
    }
    for role, (fingerprint, count) in corrected.items():
        roles[role]["sha256"] = fingerprint
        roles[role]["bytes"] = count
    v2.ROLES = roles
    v2.REPAIRED_SOURCE_OWNERS = CORRECTED_SOURCE_OWNERS
    v2.LABEL = LABEL
    return v2


def corrected_rust_family(producer: types.ModuleType) -> Any:
    original = producer.family_spec(FAMILY)
    require(tuple(original.source_owners) == ORIGINAL_SOURCE_OWNERS
            and tuple(producer.OWNED_SOURCES[FAMILY])
            == ORIGINAL_SOURCE_OWNERS
            and original.module == "candidates.rust_candidate"
            and original.adapter_relative == "candidates/rust_candidate.py"
            and original.bridge_module == "candidates._rust_bridge"
            and original.combined_native is False
            and original.owned_ctypes is False,
            "authenticate the exact original Rust module, no wrapper, and own bridge")
    corrected = producer.FamilySpec(
        original.name, original.module, original.adapter_relative,
        original.bridge_module, original.engine_relative,
        original.bridge_relative, CORRECTED_SOURCE_OWNERS,
        original.combined_native, original.owned_ctypes,
    )
    producer.OWNED_SOURCES[FAMILY] = CORRECTED_SOURCE_OWNERS
    producer.FAMILIES[FAMILY] = corrected
    require(producer.family_spec(FAMILY) is corrected,
            "rebind only genuine corrected same-family original source owners")
    original_bootstrap = producer.interpreter_bootstrap_source

    def corrected_bootstrap(spec: Any, pins: Any, source_pins: Any,
                            *, owner: str, producer_sha256: str) -> str:
        program = original_bootstrap(spec, pins, source_pins,
                                    owner=owner,
                                    producer_sha256=producer_sha256)
        marker = "_six_producer.install_owned_interpreter_guard("
        require(program.count(marker) == 1,
                "preserve the unique frozen upstream interpreter guard")
        prefix = (
            "_six_original = _six_producer.FAMILIES['rust']\n"
            "assert _six_original.name == 'rust'\n"
            "assert tuple(_six_producer.OWNED_SOURCES['rust']) == "
            + repr(ORIGINAL_SOURCE_OWNERS) + "\n"
            "_six_repaired_sources = " + repr(CORRECTED_SOURCE_OWNERS) + "\n"
            "_six_producer.OWNED_SOURCES['rust'] = _six_repaired_sources\n"
            "_six_producer.FAMILIES['rust'] = _six_producer.FamilySpec(\n"
            "    _six_original.name, _six_original.module,\n"
            "    _six_original.adapter_relative, _six_original.bridge_module,\n"
            "    _six_original.engine_relative, _six_original.bridge_relative,\n"
            "    _six_repaired_sources, _six_original.combined_native,\n"
            "    _six_original.owned_ctypes)\n"
            "assert _six_producer.family_spec('rust').source_owners "
            "== _six_repaired_sources\n"
        )
        final = program.replace(marker, prefix + marker, 1)
        try:
            ast.parse(final, filename="<genuine-v13-rust-original-interpreter>")
        except (SyntaxError, ValueError, RecursionError) as error:
            raise CampaignError("reject a changed original Rust interpreter bootstrap") from error
        return final

    producer.interpreter_bootstrap_source = corrected_bootstrap
    return corrected


@contextlib.contextmanager
def installed_signal_handlers() -> Iterator[None]:
    require(threading.current_thread() is threading.main_thread(),
            "install actual controller signal handlers only in the main thread")
    previous: list[tuple[int, Any]] = []

    def handler(signum: int, frame: Any) -> None:
        del frame
        raise GracefulControllerSignal(signum)

    try:
        for name in SIGNAL_NAMES:
            number = getattr(signal, name)
            previous.append((number, signal.getsignal(number)))
            signal.signal(number, handler)
        yield
    finally:
        for number, old in reversed(previous):
            signal.signal(number, old)


@contextlib.contextmanager
def blocked_controller_signals() -> Iterator[None]:
    require(callable(getattr(signal, "pthread_sigmask", None)),
            "require genuine signal masking for each durable target mutation")
    selected = {getattr(signal, name) for name in SIGNAL_NAMES}
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, selected)
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def checked_root(value: Any) -> str:
    require(type(value) is str and value == PUBLIC_RECOVERY_ROOT
            and value.startswith("/tmp/")
            and len(value.split("/")) == 3,
            "require the exact versioned caller-pinned V4 private recovery root")
    return value


def open_recovery_lock(v2: types.ModuleType, root: str,
                       *, create: bool,
                       ledger: dict[str, Any] | None = None
                       ) -> tuple[int, int]:
    checked_root(root)
    if create:
        if ledger is not None:
            ledger["recovery_root_creation_attempted"] = True
        os.mkdir(root, mode=0o700)
        if ledger is not None:
            ledger["recovery_roots_created"] += 1
        temporary = os.open(
            "/tmp", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(temporary)
        finally:
            os.close(temporary)
    directory = v2.private_directory(root)
    descriptor: int | None = None
    try:
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if create:
            flags |= os.O_CREAT | os.O_EXCL
            if ledger is not None:
                ledger["recovery_lock_attempted"] = True
        descriptor = os.open(LOCK_NAME, flags, 0o600, dir_fd=directory)
        actual = os.fstat(descriptor)
        visible = os.stat(LOCK_NAME, dir_fd=directory, follow_symlinks=False)
        require(stat.S_ISREG(actual.st_mode)
                and actual.st_uid == os.geteuid()
                and actual.st_nlink == 1
                and stat.S_IMODE(actual.st_mode) == 0o600
                and (actual.st_dev, actual.st_ino)
                == (visible.st_dev, visible.st_ino),
                "reject a substituted, shared, or foreign V4 recovery lock")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if ledger is not None:
            ledger["recovery_locks_acquired"] += 1
        os.fsync(descriptor)
        os.fsync(directory)
        return directory, descriptor
    except BaseException:
        if descriptor is not None:
            os.close(descriptor)
        os.close(directory)
        raise


def announce_recovery(root: str, journal_digest: str) -> None:
    record = {
        "schema": SCHEMA + "-preactivation-public-recovery-announcement",
        "status": "PASS", "family": FAMILY,
        "activation_root": checked_root(root),
        "journal_relative": "recovery-journal.json",
        "recovery_journal_sha256": checked_digest(
            journal_digest, "actual V4 pre-mutation recovery journal"),
        "canonical_target_replacements_so_far": 0,
        "group_atomic": False, "holdout": "NOT OPENED",
    }
    sys.stderr.buffer.write(canonical(record))
    sys.stderr.buffer.flush()


def restore_corrected_four_roles(
        v2: types.ModuleType, root: str, journal: dict[str, Any],
        journal_sha256: str,
        ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    if ledger is not None:
        ledger["restoration_attempted"] = True
    checked_root(root)
    checked_digest(journal_sha256, "actual V4 four-owner recovery journal")
    require(type(journal) is dict
            and journal.get("schema") == v2.JOURNAL_SCHEMA
            and journal.get("status") == "PREPARED"
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("activation_root") == root
            and journal.get("source_sha256") == V2["source"][1]
            and journal.get("protocol_sha256") == V2["protocol"][1]
            and journal.get("contract_sha256") == V2["contract"][1]
            and journal.get("build_archive_sha256") == BUILD["archive"][1]
            and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
            and journal.get("corrected_public_adapter_sha256")
            == CORRECTED_PUBLIC_SHA256
            and journal.get("recoverable_v4_public_root")
            == PUBLIC_RECOVERY_ROOT
            and journal.get("recoverable_v4_public_lock_filename")
            == LOCK_NAME
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False
            and type(journal.get("roles")) is dict
            and set(journal["roles"]) == set(ROLE_ORDER),
            "recover only the independently corrected exact V13 V4 journal")
    recorded, journal_owner = v2.read_private(
        root, "recovery-journal.json", journal_sha256)
    require(canonical(recorded) == canonical(journal)
            and journal_owner["sha256"] == journal_sha256,
            "reauthenticate every actual corrected V4 journal byte")
    restored: dict[str, dict[str, Any]] = {}
    for role in RESTORATION_ORDER:
        definition = v2.ROLES[role]
        entry = journal["roles"][role]
        expected = definition["original"]
        require(type(entry) is dict
                and entry.get("role") == role
                and entry.get("relative") == definition["relative"]
                and entry.get("original") == ORIGINALS[role]
                and expected == ORIGINALS[role]
                and entry.get("repaired_sha256") == definition["sha256"]
                and entry.get("repaired_bytes") == definition["bytes"],
                "refuse a stale V11 or substituted V13 recovery role: " + role)
        repository, directory, filename = v2.open_target_parent(
            definition["relative"])
        try:
            before = os.fstat(directory)
            try:
                current = os.stat(filename, dir_fd=directory,
                                  follow_symlinks=False)
            except FileNotFoundError as error:
                raise CampaignError(
                    "refuse a removed genuine original Rust target: " + role
                ) from error
            require(stat.S_ISREG(current.st_mode)
                    and current.st_uid == os.geteuid(),
                    "refuse a foreign or symlinked actual V4 recovery target")
            identity = (current.st_dev, current.st_ino)
            original_identity = (expected["device"], expected["inode"])
            if identity == original_identity and current.st_nlink == 1:
                try:
                    os.stat(entry["backup_filename"], dir_fd=directory,
                            follow_symlinks=False)
                except FileNotFoundError:
                    restored[role] = v2.current_original(role)
                    if ledger is not None:
                        ledger["restored_target_roles"].append(role)
                    continue
                raise CampaignError(
                    "refuse an unexplained actual V4 original backup")
            if identity == original_identity and current.st_nlink == 2:
                intent, _ = v2.read_private(
                    root, "link-intent-" + role + ".json")
                require(intent.get("schema") == v2.INTENTION_SCHEMA
                        and intent.get("operation") == "HARDLINK_BACKUP"
                        and intent.get("family") == FAMILY
                        and intent.get("journal_sha256") == journal_sha256
                        and intent.get("role") == role
                        and intent.get("backup_filename")
                        == entry["backup_filename"],
                        "refuse an unauthenticated V4 original hardlink")
                backup = os.stat(entry["backup_filename"],
                                 dir_fd=directory, follow_symlinks=False)
                require((backup.st_dev, backup.st_ino) == original_identity
                        and backup.st_nlink == 2
                        and backup.st_uid == expected["uid"],
                        "refuse a substituted V4 original hardlink")
                os.unlink(entry["backup_filename"], dir_fd=directory)
                v2.sync_directory(directory, before)
                restored[role] = v2.current_original(role)
                if ledger is not None:
                    ledger["restored_target_roles"].append(role)
                continue
            intent, _ = v2.read_private(
                root, "promotion-intent-" + role + ".json")
            require(intent.get("schema") == v2.INTENTION_SCHEMA
                    and intent.get("operation") == "PROMOTE"
                    and intent.get("family") == FAMILY
                    and intent.get("journal_sha256") == journal_sha256
                    and intent.get("role") == role
                    and intent.get("repaired_sha256")
                    == definition["sha256"]
                    and intent.get("repaired_bytes") == definition["bytes"]
                    and current.st_size == definition["bytes"]
                    and stat.S_IMODE(current.st_mode) == expected["mode"]
                    and current.st_nlink == 1,
                    "never overwrite changed or stale actual V13 Rust bytes")
            _, promoted = v2._read_owned(
                str(ROOT), definition["relative"], definition["sha256"],
                exact_size=definition["bytes"], maximum=v2.MAX_BINARY_BYTES,
                allow_canonical_target=True)
            require((promoted["device"], promoted["inode"]) == identity,
                    "never replace a substituted user-owned Rust inode")
            backup = os.stat(entry["backup_filename"], dir_fd=directory,
                             follow_symlinks=False)
            require(stat.S_ISREG(backup.st_mode)
                    and (backup.st_dev, backup.st_ino) == original_identity
                    and backup.st_nlink == 1
                    and backup.st_uid == expected["uid"]
                    and backup.st_size == expected["bytes"]
                    and stat.S_IMODE(backup.st_mode) == expected["mode"],
                    "restore only the exact retained genuine original inode")
            intention = {
                "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
                "operation": "RESTORE", "family": FAMILY, "role": role,
                "journal_sha256": journal_sha256,
                "target": definition["relative"],
                "backup_filename": entry["backup_filename"],
                "group_atomic": False,
            }
            try:
                v2.write_private(root, "restore-intent-" + role + ".json",
                                 intention)
            except FileExistsError:
                previous, _ = v2.read_private(
                    root, "restore-intent-" + role + ".json")
                require(canonical(previous) == canonical(intention),
                        "retry only the exact durable V4 restoration intent")
            os.replace(entry["backup_filename"], filename,
                       src_dir_fd=directory, dst_dir_fd=directory)
            if ledger is not None:
                ledger["canonical_target_replacements"] += 1
            v2.sync_directory(directory, before)
            restored[role] = v2.current_original(role)
            if ledger is not None:
                ledger["restored_target_roles"].append(role)
        finally:
            os.close(directory)
            os.close(repository)
    require(set(restored) == set(ROLE_ORDER)
            and all(v2.same_original(restored[role], ORIGINALS[role])
                    for role in ROLE_ORDER),
            "prove independent V4 recovery of every exact original inode")
    if ledger is not None:
        ledger["all_four_original_targets_restored"] = True
    record = {
        "schema": RESTORATION_SCHEMA, "status": "PASS", "version": 7,
        "family": FAMILY, "label": LABEL, "activation_root": root,
        "journal_sha256": journal_sha256,
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "restored_targets": restored,
        "restoration_order": list(RESTORATION_ORDER),
        "original_inodes_preserved": True,
        "unchanged_v2_restoration_invoked": False,
        "group_atomic": False, "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
    }
    try:
        owner = v2.write_private(root, "restoration-receipt.json", record)
    except FileExistsError:
        previous, owner = v2.read_private(root, "restoration-receipt.json")
        require(canonical(previous) == canonical(record),
                "refuse a substituted corrected V4 restoration record")
    if ledger is not None:
        ledger["restoration_verified"] = True
    return {"report": record, "owner": owner}


def activate_four_roles(v2: types.ModuleType,
                        retained: Mapping[str, Any],
                        options: argparse.Namespace,
                        ledger: dict[str, Any] | None = None
                        ) -> dict[str, Any]:
    root = checked_root(options.activation_root)
    originals = v2.exact_originals()
    if ledger is not None:
        ledger["canonical_target_read_lower_bound"] += len(ROLE_ORDER)
    require(all(v2.same_original(originals[role], ORIGINALS[role])
                for role in ROLE_ORDER),
            "authenticate all four genuine original inodes before activation")
    phase = retained["build"]["phases"][0]["phase"]
    payloads = {role: v2.read_recorded_phase(phase, role)
                for role in ROLE_ORDER}
    token = os.urandom(16).hex()
    entries: dict[str, dict[str, Any]] = {}
    for role in ROLE_ORDER:
        backup, stage = v2.role_target_names(token, role)
        expected = v2.ROLES[role]
        entries[role] = {
            "role": role, "relative": expected["relative"],
            "original": dict(expected["original"]),
            "backup_filename": backup, "stage_filename": stage,
            "repaired_sha256": expected["sha256"],
            "repaired_bytes": expected["bytes"],
        }
    journal = {
        "schema": v2.JOURNAL_SCHEMA, "status": "PREPARED", "version": 2,
        "family": FAMILY, "label": LABEL, "activation_root": root,
        "source_sha256": V2["source"][1],
        "protocol_sha256": V2["protocol"][1],
        "contract_sha256": V2["contract"][1],
        "build_archive_sha256": BUILD["archive"][1],
        "build_receipt_sha256": BUILD["receipt"][1],
        "roles": entries, "role_order": list(ROLE_ORDER),
        "restoration_order": list(RESTORATION_ORDER),
        "group_atomic": False,
        "exact_original_inode_backup": "ADJACENT SAME-DIRECTORY HARDLINK",
        "recoverable_v7_controller_source_sha256": options.source_sha256,
        "recoverable_v7_controller_protocol_sha256": options.protocol_sha256,
        "recoverable_v7_controller_contract_sha256": options.contract_sha256,
        "recoverable_v4_public_root": PUBLIC_RECOVERY_ROOT,
        "recoverable_v4_public_lock_filename": LOCK_NAME,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "holdout": "NOT OPENED", "performance": "NOT MEASURED",
    }
    with blocked_controller_signals():
        if ledger is not None:
            ledger["recovery_journal_creation_attempted"] = True
        journal_owner = v2.write_private(root, "recovery-journal.json", journal)
        if ledger is not None:
            ledger["recovery_journals_created"] += 1
            ledger["recovery_journal_sha256"] = journal_owner["sha256"]
        announce_recovery(root, journal_owner["sha256"])
        if ledger is not None:
            ledger["recovery_journal_announced"] = True
    try:
        for role in ROLE_ORDER:
            with blocked_controller_signals():
                entry = entries[role]
                owned = v2.ROLES[role]
                original = v2.current_original(role)
                require(v2.same_original(original, owned["original"]),
                        "refuse an original changed after journal publication")
                repository, directory, filename = v2.open_target_parent(
                    entry["relative"])
                try:
                    before = os.fstat(directory)
                    v2.ensure_absent(directory, entry["backup_filename"])
                    v2.ensure_absent(directory, entry["stage_filename"])
                    intention = {
                        "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
                        "operation": "HARDLINK_BACKUP", "family": FAMILY,
                        "role": role, "target": entry["relative"],
                        "activation_root": root,
                        "journal_sha256": journal_owner["sha256"],
                        "original": entry["original"],
                        "backup_filename": entry["backup_filename"],
                        "group_atomic": False,
                    }
                    v2.write_private(root, "link-intent-" + role + ".json",
                                     intention)
                    os.link(filename, entry["backup_filename"],
                            src_dir_fd=directory, dst_dir_fd=directory,
                            follow_symlinks=False)
                    current = os.stat(filename, dir_fd=directory,
                                      follow_symlinks=False)
                    backup = os.stat(entry["backup_filename"],
                                     dir_fd=directory,
                                     follow_symlinks=False)
                    expected = owned["original"]
                    require((current.st_dev, current.st_ino)
                            == (backup.st_dev, backup.st_ino)
                            == (expected["device"], expected["inode"])
                            and current.st_nlink == 2
                            and backup.st_nlink == 2
                            and current.st_uid == expected["uid"]
                            and stat.S_IMODE(current.st_mode)
                            == expected["mode"],
                            "preserve the real identical hardlinked original inode")
                    v2.sync_directory(directory, before)
                    promotion = {
                        "schema": v2.INTENTION_SCHEMA, "status": "PREPARED",
                        "operation": "PROMOTE", "family": FAMILY,
                        "role": role, "target": entry["relative"],
                        "activation_root": root,
                        "journal_sha256": journal_owner["sha256"],
                        "original": entry["original"],
                        "backup_filename": entry["backup_filename"],
                        "stage_filename": entry["stage_filename"],
                        "repaired_sha256": entry["repaired_sha256"],
                        "repaired_bytes": entry["repaired_bytes"],
                        "group_atomic": False,
                    }
                    v2.write_private(root,
                                     "promotion-intent-" + role + ".json",
                                     promotion)
                    staged = v2.write_stage(
                        directory, entry["stage_filename"],
                        payloads[role], expected["mode"])
                    require(staged.get("sha256") == owned["sha256"]
                            and staged.get("size_bytes") == owned["bytes"],
                            "never promote unverified V13 private source or native bytes")
                    v2.sync_directory(directory, before)
                    os.replace(entry["stage_filename"], filename,
                               src_dir_fd=directory, dst_dir_fd=directory)
                    if ledger is not None:
                        ledger["canonical_target_replacements"] += 1
                        ledger["actual_native_activations"] = 1
                        ledger["activated_target_roles"].append(role)
                    v2.sync_directory(directory, before)
                    _, promoted = v2._read_owned(
                        str(ROOT), entry["relative"], owned["sha256"],
                        exact_size=owned["bytes"],
                        maximum=v2.MAX_BINARY_BYTES,
                        allow_canonical_target=True)
                    require(promoted["device"] == staged["device"]
                            and promoted["inode"] == staged["inode"]
                            and promoted["mode"] == expected["mode"]
                            and promoted["nlink"] == 1,
                            "authenticate every one individually promoted source inode")
                finally:
                    os.close(directory)
                    os.close(repository)
        targets: dict[str, Any] = {}
        with blocked_controller_signals():
            for role in ROLE_ORDER:
                owned = v2.ROLES[role]
                _, targets[role] = v2._read_owned(
                    str(ROOT), owned["relative"], owned["sha256"],
                    exact_size=owned["bytes"], maximum=v2.MAX_BINARY_BYTES,
                    allow_canonical_target=True)
            report = {
                "schema": v2.ACTIVATION_SCHEMA, "status": "PASS",
                "version": 2, "family": FAMILY, "label": LABEL,
                "activation_root": root, "journal": journal_owner,
                "targets": targets, "role_order": list(ROLE_ORDER),
                "restoration_order": list(RESTORATION_ORDER),
                "build_archive_sha256": BUILD["archive"][1],
                "build_receipt_sha256": BUILD["receipt"][1],
                "all_four_original_inodes_retained": True,
                "recoverable_v7_controller_source_sha256": options.source_sha256,
                "group_atomic": False,
            }
            report_owner = v2.write_private(root, "activation-report.json", report)
            receipt = {
                "schema": v2.ACTIVATION_RECEIPT_SCHEMA,
                "status": "PASS", "activation_status": "PASS",
                "family": FAMILY, "activation_root": root,
                "activation": report_owner, "journal": journal_owner,
                "group_atomic": False,
            }
            receipt_owner = v2.write_private(
                root, "activation-receipt.json", receipt)
        return {
            "root": root, "journal": journal,
            "journal_owner": journal_owner,
            "activation": report, "activation_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "originals": originals,
        }
    except BaseException:
        with blocked_controller_signals():
            restore_corrected_four_roles(
                v2, root, journal, journal_owner["sha256"], ledger)
        raise


def stream_observation(value: Any) -> dict[str, Any]:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    plain_hash = hashlib.sha256()
    plain_size = 0
    destination = io.BytesIO()
    with gzip.GzipFile(fileobj=destination, mode="wb", compresslevel=9,
                       mtime=0) as stream:
        for piece in encoder.iterencode(value):
            raw = piece.encode("ascii")
            plain_size += len(raw)
            require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                    "bound the complete actual original suite observation")
            plain_hash.update(raw)
            stream.write(raw)
            require(destination.tell() <= MAX_SUITE_COMPRESSED_BYTES,
                    "bound complete compressed original suite output")
        plain_size += 1
        require(plain_size <= MAX_SUITE_PLAIN_BYTES,
                "bound the exact original observation newline")
        plain_hash.update(b"\n")
        stream.write(b"\n")
    compressed = destination.getvalue()
    require(0 < len(compressed) <= MAX_SUITE_COMPRESSED_BYTES,
            "retain one complete bounded original observation gzip")
    return {
        "encoding": "deterministic-single-member-gzip-base64",
        "gzip_mtime": 0,
        "compressed_sha256": digest(compressed),
        "compressed_bytes": len(compressed),
        "compressed_base64": base64.b64encode(compressed).decode("ascii"),
        "uncompressed_sha256": plain_hash.hexdigest(),
        "uncompressed_bytes": plain_size,
    }


def validate_streamed_observation(value: Any) -> dict[str, Any]:
    require(type(value) is dict
            and value.get("encoding")
            == "deterministic-single-member-gzip-base64"
            and value.get("gzip_mtime") == 0
            and type(value.get("compressed_bytes")) is int
            and 0 < value["compressed_bytes"] <= MAX_SUITE_COMPRESSED_BYTES
            and type(value.get("uncompressed_bytes")) is int
            and 0 < value["uncompressed_bytes"] <= MAX_SUITE_PLAIN_BYTES
            and type(value.get("compressed_base64")) is str,
            "preserve a complete bounded original worker gzip")
    checked_digest(value.get("compressed_sha256"), "complete original worker gzip")
    checked_digest(value.get("uncompressed_sha256"), "complete original records")
    try:
        compressed = base64.b64decode(value["compressed_base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject concealed actual original worker gzip") from error
    require(len(compressed) == value["compressed_bytes"]
            and digest(compressed) == value["compressed_sha256"]
            and compressed[:3] == b"\x1f\x8b\x08"
            and compressed[4:8] == b"\x00\x00\x00\x00",
            "authenticate all genuinely compressed original records")
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    actual_hash = hashlib.sha256()
    total = 0
    cursor = 0
    try:
        while cursor < len(compressed):
            part = compressed[cursor:cursor + 64 * 1024]
            cursor += len(part)
            pending = part
            while pending:
                block = decoder.decompress(pending, 1024 * 1024)
                total += len(block)
                require(total <= MAX_SUITE_PLAIN_BYTES,
                        "reject an oversized complete original observation")
                actual_hash.update(block)
                pending = decoder.unconsumed_tail
                if decoder.unused_data:
                    raise CampaignError("reject multiple original observation members")
        remainder = decoder.flush()
        total += len(remainder)
        require(total <= MAX_SUITE_PLAIN_BYTES and decoder.eof,
                "reject truncated actual candidate records")
        actual_hash.update(remainder)
    except (zlib.error, EOFError, OSError) as error:
        raise CampaignError("reject corrupt complete original case records") from error
    require(total == value["uncompressed_bytes"]
            and actual_hash.hexdigest() == value["uncompressed_sha256"],
            "reauthenticate every original mismatch without materializing the archive")
    return value


def same_owner(expected: Any, actual: Mapping[str, Any]) -> bool:
    return (type(expected) is dict
            and expected.get("sha256") == actual.get("sha256")
            and expected.get("device") == actual.get("device")
            and expected.get("inode") == actual.get("inode")
            and expected.get("size_bytes") == actual.get("size_bytes"))


def active_worker_approval(v2: types.ModuleType,
                           options: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(options.activation_root)
    report, report_owner = v2.read_private(
        root, "activation-report.json", options.activation_report_sha256)
    receipt, receipt_owner = v2.read_private(
        root, "activation-receipt.json", options.activation_receipt_sha256)
    journal, journal_owner = v2.read_private(
        root, "recovery-journal.json", options.recovery_journal_sha256)
    require(report.get("schema") == v2.ACTIVATION_SCHEMA
            and report.get("status") == "PASS"
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("activation_root") == root
            and report.get("build_archive_sha256") == BUILD["archive"][1]
            and report.get("build_receipt_sha256") == BUILD["receipt"][1]
            and report.get("group_atomic") is False
            and same_owner(report.get("journal"), journal_owner)
            and receipt.get("schema") == v2.ACTIVATION_RECEIPT_SCHEMA
            and receipt.get("status") == "PASS"
            and receipt.get("activation_status") == "PASS"
            and receipt.get("family") == FAMILY
            and same_owner(receipt.get("activation"), report_owner)
            and same_owner(receipt.get("journal"), journal_owner)
            and journal.get("schema") == v2.JOURNAL_SCHEMA
            and journal.get("family") == FAMILY
            and journal.get("label") == LABEL
            and journal.get("build_archive_sha256") == BUILD["archive"][1]
            and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
            and journal.get("corrected_public_adapter_sha256")
            == CORRECTED_PUBLIC_SHA256
            and journal.get("role_order") == list(ROLE_ORDER)
            and journal.get("restoration_order") == list(RESTORATION_ORDER)
            and journal.get("group_atomic") is False,
            "authenticate only the live corrected four-owner Rust V13 journal")
    for role in ROLE_ORDER:
        expected = v2.ROLES[role]
        row = journal.get("roles", {}).get(role)
        current = report.get("targets", {}).get(role)
        require(type(row) is dict and row.get("original") == expected["original"]
                and row.get("repaired_sha256") == expected["sha256"]
                and row.get("repaired_bytes") == expected["bytes"]
                and type(current) is dict
                and current.get("relative") == expected["relative"]
                and current.get("sha256") == expected["sha256"]
                and current.get("size_bytes") == expected["bytes"],
                "reject a changed actual corrected activation role: " + role)
    return {"root": root, "report": report, "report_owner": report_owner,
            "receipt": receipt, "receipt_owner": receipt_owner,
            "journal": journal, "journal_owner": journal_owner}


def run_worker(options: argparse.Namespace) -> dict[str, Any]:
    v2 = patched_v2_helpers()
    context, _ = verify_context(
        options.source_sha256,
        options.protocol_sha256,
        options.contract_sha256,
        retain=False,
    )
    require(
        context.get("status") == "PASS",
        "authenticate the complete V7 helper before one original worker",
    )
    active = active_worker_approval(v2, options)
    producer = load_frozen_module(
        PRODUCER["source"], "_rebar_exact_original_six_family_v4_for_v13_rust")
    require(producer.SCHEMA == "rebar-owned-six-family-original-p0-producer-v4"
            and producer.SUITE_COUNT == SUITE_COUNT
            and producer.CASE_DENOMINATOR == CASE_COUNT
            and producer.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
            and producer.CORRECTED_PUBLIC_RECORDS_SHA256
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and producer.CORRECTED_PUBLIC_COHORT_RECORDS_SHA256
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and tuple(producer.CORRECTED_PUBLIC_REFERENCE_PIDS)
            == CORRECTED_REFERENCE_PIDS
            and producer.CORRECTED_PUBLIC_COHORT_CASE_COUNT
            == CORRECTED_REFERENCE_CACHE_CASE_COUNT
            and [(item.name, item.case_count) for item in producer.SUITES]
            == list(SUITES),
            "run only the complete unchanged original CPython P0 producer")
    spec = corrected_rust_family(producer)
    suite = producer.suite_spec(options.suite)
    source_pins = {path: fingerprint
                   for path, fingerprint, _ in CORRECTED_SOURCE_OWNERS}
    pins = {"source": CORRECTED_PUBLIC_SHA256,
            "native_engine": ENGINE_SHA256,
            "native_bridge": BRIDGE_SHA256}
    actual = producer.exact_native_owners(spec, pins, source_pins)
    require(actual["source"]["sha256"] == CORRECTED_PUBLIC_SHA256
            and actual["native_engine"]["sha256"] == ENGINE_SHA256
            and actual["native_bridge"]["sha256"] == BRIDGE_SHA256,
            "match only through the corrected actual first-party Rust owner")
    if suite.name == "original_bounded_v5":
        observation = producer.observe_original_upstream(
            suite, spec, pins, source_pins)
    elif suite.name == "subinterpreter_v2":
        observation = producer.observe_subinterpreters(
            suite, spec, pins, source_pins,
            producer_sha256=PRODUCER["source"][1])
    else:
        manifest_item = (
            "oracle/phase1/p0-completeness-v1.json",
            "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
            45632,
        )
        raw, _ = read_owned(manifest_item, maximum=MAX_SOURCE_BYTES)
        phase_one = strict_document(raw, "unchanged original complete phase-one oracle")
        observation = producer.observe_direct_suite(
            suite, spec, pins, source_pins, phase_one)
    require(type(observation) is dict
            and observation.get("schema")
            == producer.SCHEMA + "-actual-original-suite"
            and observation.get("status") in ("PASS", "FAIL")
            and observation.get("suite") == suite.name
            and observation.get("candidate_family") == FAMILY
            and observation.get("case_execution_denominator") == suite.case_count
            and observation.get("actual_candidate_case_count") == suite.case_count
            and observation.get("reference_records_sha256")
            == suite.reference_sha256
            and type(observation.get("mismatch_count")) is int
            and observation["mismatch_count"] >= 0
            and type(observation.get("all_mismatches")) is list
            and len(observation["all_mismatches"])
            == observation["mismatch_count"]
            and observation.get("actual_candidate_workers") == 1
            and observation.get("clock_samples") == 0
            and observation.get("holdout") == "NOT OPENED",
            "retain every literal original upstream record and true mismatch")
    if suite.name == "public_types_v1":
        baseline = observation.get("baseline_evidence")
        require(suite.reference_sha256 == CORRECTED_REFERENCE_RECORDS_SHA256
                and suite.matrix_sha256 == CORRECTED_REFERENCE_MATRIX_SHA256
                and type(baseline) is dict
                and baseline.get("status") == "PASS"
                and baseline.get("reference_status") == "PASS"
                and baseline.get("actual_independent_reference_count") == 2
                and baseline.get("reference_decoder_sha256")
                == CORRECTED_REFERENCE["source"][1]
                and baseline.get("reference_roles_separately_authenticated")
                is True
                and baseline.get("reference_records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and baseline.get("historical_reference_records_sha256")
                == HISTORICAL_FULL_PUBLIC_RECORDS_SHA256
                and baseline.get("baseline_reference_pids")
                == list(CORRECTED_REFERENCE_PIDS)
                and baseline.get("cache_case_count")
                == CORRECTED_REFERENCE_CACHE_CASE_COUNT
                and baseline.get("cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and baseline.get("new_reference_workers_started") == 0
                and baseline.get("candidate_imports_by_reference_decoder") == 0
                and baseline.get("c_pattern_equality_failure_waived") is False,
                "compare all 6,912 Rust observations against both genuine "
                "complete corrected Python references")
    if suite.name == "original_bounded_v5":
        require(observation.get("actual_public_record_count") == 152
                and observation.get("actual_debug_skip_count") == 1
                and observation.get("named_private_waiver_count") == 13,
                "never suppress an upstream case or unnamed private failure")
    if suite.name == "subinterpreter_v2" and observation["status"] == "PASS":
        require(observation.get("actual_case_interpreter_exec_calls") == 394
                and observation.get("actual_interpreters_created") == 11
                and observation.get("actual_interpreters_destroyed") == 11
                and observation.get("all_real_pipes_read_to_eof") is True
                and observation.get("all_real_pipe_descriptors_closed") is True
                and observation.get("interpreter_live_set_restored") is True,
                "preserve all actual original 128/394/11 interpreter events")
    encoded = stream_observation(observation)
    return {
        "schema": WORKER_SCHEMA, "status": observation["status"],
        "candidate_family": FAMILY, "label": LABEL,
        "suite": suite.name,
        "case_execution_denominator": suite.case_count,
        "actual_candidate_case_count": suite.case_count,
        "mismatch_count": observation["mismatch_count"],
        "failure_class": ("PASS" if observation["status"] == "PASS"
                          else "SEMANTIC MISMATCH"),
        "original_observer_source_sha256": PRODUCER["source"][1],
        "original_observer_version": 4,
        "original_observer_unchanged": True,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "activation_report_sha256": active["report_owner"]["sha256"],
        "activation_receipt_sha256": active["receipt_owner"]["sha256"],
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "repaired_source_owner_count": 9,
        "corrected_public_source_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "complete_original_observation": encoded,
        "all_original_records_and_mismatches_preserved": True,
        "actual_candidate_workers": 1,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "candidate_qualified": False, "winner_selected": False,
    }


def worker_arguments(options: argparse.Namespace, name: str,
                     active: Mapping[str, Any]) -> list[str]:
    return [
        PYTHON, "-I", "-B", str(ROOT / SOURCE_RELATIVE), "--worker",
        "--source-sha256", options.source_sha256,
        "--protocol-sha256", options.protocol_sha256,
        "--contract-sha256", options.contract_sha256,
        "--family", FAMILY, "--label", LABEL,
        "--suite", name,
        "--activation-root", active["root"],
        "--activation-report-sha256", active["activation_owner"]["sha256"],
        "--activation-receipt-sha256", active["receipt_owner"]["sha256"],
        "--recovery-journal-sha256", active["journal_owner"]["sha256"],
        "--producer-source-sha256", PRODUCER["source"][1],
        "--producer-protocol-sha256", PRODUCER["protocol"][1],
        "--producer-contract-sha256", PRODUCER["contract"][1],
        "--build-source-sha256", BUILD["source"][1],
        "--build-protocol-sha256", BUILD["protocol"][1],
        "--build-contract-sha256", BUILD["contract"][1],
        "--build-archive-sha256", BUILD["archive"][1],
        "--build-receipt-sha256", BUILD["receipt"][1],
        "--native-engine-sha256", ENGINE_SHA256,
        "--native-bridge-sha256", BRIDGE_SHA256,
        "--native-engine-bytes", str(ENGINE_BYTES),
        "--native-bridge-bytes", str(BRIDGE_BYTES),
    ]


def encode_stream(raw: bytes, limit: int, label: str) -> dict[str, Any]:
    require(type(raw) is bytes and len(raw) <= limit,
            "preserve one complete bounded " + label)
    return {
        "base64": base64.b64encode(raw).decode("ascii"),
        "sha256": digest(raw),
        "size_bytes": len(raw),
        "captured_prefix_bytes": len(raw),
        "limit_bytes": limit,
        "complete": True,
        "truncated": False,
        "limit_exceeded": False,
    }


def new_campaign_effect_ledger(options: argparse.Namespace
                               ) -> dict[str, Any]:
    return {
        "schema": SCHEMA + "-authorized-run-actual-effect-ledger",
        "campaign_mode": "AUTHORIZED RUN",
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "historical_v2_helper_preflight_attempted": False,
        "historical_v2_helper_source_preflight_status": "NOT ATTEMPTED",
        "historical_v2_helper_module_preflight_status": "NOT ATTEMPTED",
        "v13_source_build_archive_read_attempted": False,
        "v13_source_build_archive_read_status": "NOT ATTEMPTED",
        "v13_source_build_archive_read_count": 0,
        "v13_source_build_archive_compressed_bytes_read": 0,
        "v13_source_build_archive_gzip_inflation_attempted": False,
        "v13_source_build_archive_gzip_inflation_status": "NOT ATTEMPTED",
        "v13_source_build_archive_gzip_inflation_count": 0,
        "v13_source_build_archive_uncompressed_bytes_read": 0,
        "v13_source_build_archive_uncompressed_sha256": "NOT READ",
        "attempted_suite_count": 0,
        "started_suite_count": 0,
        "fully_observed_suite_count": 0,
        "actual_candidate_workers": 0,
        "actual_worker_process_ids": [],
        "worker_attempts": [],
        "retained_suite_results": [],
        "actual_native_activations": 0,
        "activated_target_roles": [],
        "canonical_target_replacements": 0,
        "canonical_target_reads": "NOT MEASURED",
        "canonical_target_stats": "NOT MEASURED",
        "canonical_target_read_lower_bound": 0,
        "recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_root_creation_attempted": False,
        "recovery_roots_created": 0,
        "recovery_lock_attempted": False,
        "recovery_locks_acquired": 0,
        "recovery_journal_creation_attempted": False,
        "recovery_journals_created": 0,
        "recovery_journal_sha256": None,
        "recovery_journal_announced": False,
        "restoration_attempted": False,
        "restored_target_roles": [],
        "all_four_original_targets_restored": False,
        "restoration_verified": False,
        "publication_attempted": False,
        "bounded_report_attempted": False,
        "archive_publication_attempted": False,
        "archive_publication_status": "NOT ATTEMPTED",
        "archive_owner": None,
        "receipt_publication_attempted": False,
        "receipt_publication_status": "NOT ATTEMPTED",
        "receipt_owner": None,
        "publication_status": "NOT ATTEMPTED",
        "publication_failure": None,
        "actual_reference_workers": 0,
        "actual_source_builds": 0,
        "hidden_cases_read": 0,
        "benchmark_files_read": 0,
        "clock_samples": 0,
        "timing_trials_run": 0,
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "candidate_qualified": False,
        "winner_selected": False,
    }


def new_worker_attempt(name: str, count: int,
                       ledger: dict[str, Any] | None = None
                       ) -> dict[str, Any]:
    require(type(name) is str and type(count) is int and count > 0,
            "record an exact original suite launch before attempting it")
    attempt: dict[str, Any] = {
        "suite": name,
        "case_execution_denominator": count,
        "worker_attempted": True,
        "actual_worker_started": False,
        "fully_observed": False,
        "actual_worker_processes": 0,
        "process": None,
        "ledger": ledger,
    }
    if ledger is not None:
        ledger["attempted_suite_count"] += 1
        entry = {
            "suite": name,
            "case_execution_denominator": count,
            "worker_attempted": True,
            "actual_worker_started": False,
            "fully_observed": False,
            "pid": None,
        }
        ledger["worker_attempts"].append(entry)
        attempt["ledger_entry"] = entry
    return attempt


def retained_failure_stream(raw: Any, limit: int,
                            label: str) -> dict[str, Any]:
    require(type(limit) is int and limit > 0,
            "bound an actual retained worker " + label)
    if type(raw) is not bytes:
        return {
            "base64": "",
            "sha256": "NOT MEASURED",
            "size_bytes": "NOT MEASURED",
            "captured_prefix_bytes": 0,
            "limit_bytes": limit,
            "complete": False,
            "truncated": False,
            "limit_exceeded": "NOT MEASURED",
            "capture_status": "NOT CAPTURED",
            "observed_value_type": type(raw).__qualname__,
        }
    capture_limit = min(limit, MAX_FAILURE_STREAM_CAPTURE_BYTES)
    prefix = raw[:capture_limit]
    return {
        "base64": base64.b64encode(prefix).decode("ascii"),
        "sha256": digest(raw),
        "size_bytes": len(raw),
        "captured_prefix_bytes": len(prefix),
        "limit_bytes": limit,
        "complete": len(prefix) == len(raw),
        "truncated": len(prefix) != len(raw),
        "limit_exceeded": len(raw) > limit,
        "capture_status": (
            "COMPLETE" if len(prefix) == len(raw) else "TRUNCATED PREFIX"
        ),
        "observed_value_type": "bytes",
    }


def remember_worker_streams(process: dict[str, Any], stdout: Any,
                            stderr: Any) -> None:
    process["stdout"] = retained_failure_stream(
        stdout, MAX_WORKER_STDOUT_BYTES, "stdout")
    process["stderr"] = retained_failure_stream(
        stderr, MAX_WORKER_STDERR_BYTES, "stderr")


def reap_started_worker(child: Any, process: dict[str, Any]) -> None:
    cleanup = process.setdefault("cleanup_failures", [])
    try:
        running = child.poll() is None
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        raise
    except BaseException as error:
        cleanup.append(record_failure(error))
        running = True
    if not running:
        try:
            process["returncode"] = child.returncode
        except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
            raise
        except BaseException as error:
            cleanup.append(record_failure(error))
        return
    try:
        child.kill()
        process["kill_attempted"] = True
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        raise
    except BaseException as error:
        process["kill_attempted"] = True
        cleanup.append(record_failure(error))
    try:
        stdout, stderr = child.communicate()
        remember_worker_streams(process, stdout, stderr)
        process["returncode"] = child.returncode
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        raise
    except BaseException as error:
        cleanup.append(record_failure(error))


def execute_one_worker(options: argparse.Namespace, name: str,
                       count: int, active: Mapping[str, Any],
                       attempt: dict[str, Any] | None = None
                       ) -> dict[str, Any]:
    if attempt is None:
        attempt = new_worker_attempt(name, count)
    require(attempt.get("suite") == name
            and attempt.get("case_execution_denominator") == count
            and attempt.get("worker_attempted") is True
            and attempt.get("actual_worker_started") is False,
            "retain the caller-owned original worker launch attempt")
    try:
        argv = worker_arguments(options, name, active)
        attempt["argv"] = argv
        try:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
            raise
        except BaseException as error:
            return failed_worker(name, count, error, attempt=attempt)
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        raise
    except BaseException as error:
        return failed_worker(name, count, error, attempt=attempt)

    # Popen succeeded. Preserve this fact and the actual PID in caller-owned
    # state before communicate, validation, encoding, or cleanup can fail.
    process: dict[str, Any] = {
        "argv": argv,
        "pid": child.pid,
        "returncode": None,
        "timed_out": False,
        "stdout": None,
        "stderr": None,
        "actual_worker_processes": 1,
        "cleanup_failures": [],
        "kill_attempted": False,
    }
    attempt["actual_worker_started"] = True
    attempt["actual_worker_processes"] = 1
    attempt["process"] = process
    ledger = attempt.get("ledger")
    if type(ledger) is dict:
        ledger["started_suite_count"] += 1
        ledger["actual_candidate_workers"] += 1
        entry = attempt.get("ledger_entry")
        if type(entry) is dict:
            entry["actual_worker_started"] = True
            entry["pid"] = child.pid
        if type(child.pid) is int and child.pid > 0:
            ledger["actual_worker_process_ids"].append(child.pid)

    observed: dict[str, Any] | None = None
    try:
        process["stdout"] = retained_failure_stream(
            None, MAX_WORKER_STDOUT_BYTES, "stdout")
        process["stderr"] = retained_failure_stream(
            None, MAX_WORKER_STDERR_BYTES, "stderr")
        require(type(child.pid) is int and child.pid > 0,
                "retain a genuine positive started original worker PID")
        try:
            stdout, stderr = child.communicate(
                timeout=WORKER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as error:
            process["timed_out"] = True
            remember_worker_streams(process, error.output, error.stderr)
            reap_started_worker(child, process)
            return failed_worker(name, count, error, attempt=attempt)
        remember_worker_streams(process, stdout, stderr)
        process["returncode"] = child.returncode
        require(type(stdout) is bytes and type(stderr) is bytes
                and len(stdout) <= MAX_WORKER_STDOUT_BYTES
                and len(stderr) <= MAX_WORKER_STDERR_BYTES,
                "reject oversized or incomplete original worker streams "
                "without discarding the started PID or complete-byte hashes")
        process["stdout"] = encode_stream(
            stdout, MAX_WORKER_STDOUT_BYTES, "original suite stdout")
        process["stderr"] = encode_stream(
            stderr, MAX_WORKER_STDERR_BYTES, "original suite stderr")
        observed = strict_document(stdout, "actual corrected Rust V6 worker")
        require(observed.get("schema") == WORKER_SCHEMA
                and observed.get("candidate_family") == FAMILY
                and observed.get("label") == LABEL
                and observed.get("suite") == name
                and observed.get("case_execution_denominator") == count
                and observed.get("actual_candidate_case_count") == count
                and observed.get("original_observer_source_sha256")
                == PRODUCER["source"][1]
                and observed.get("original_observer_version") == 4
                and observed.get("corrected_reference_receipt_sha256")
                == CORRECTED_REFERENCE["receipt"][1]
                and observed.get("corrected_reference_records_sha256")
                == CORRECTED_REFERENCE_RECORDS_SHA256
                and observed.get("corrected_reference_cache_records_sha256")
                == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
                and observed.get("corrected_reference_case_count")
                == CORRECTED_REFERENCE_CASE_COUNT
                and observed.get("corrected_reference_process_ids")
                == list(CORRECTED_REFERENCE_PIDS)
                and observed.get("candidate_run_uses_both_complete_reference_vectors")
                is True
                and observed.get("actual_v13_build_archive_sha256")
                == BUILD["archive"][1]
                and observed.get("actual_v13_build_receipt_sha256")
                == BUILD["receipt"][1]
                and observed.get("corrected_public_source_sha256")
                == CORRECTED_PUBLIC_SHA256
                and observed.get("corrected_bridge_source_sha256")
                == BRIDGE_SOURCE_SHA256
                and observed.get("native_engine_sha256") == ENGINE_SHA256
                and observed.get("native_bridge_sha256") == BRIDGE_SHA256
                and observed.get("repaired_source_owner_count") == 9
                and observed.get("all_original_records_and_mismatches_preserved")
                is True
                and observed.get("actual_candidate_workers") == 1
                and observed.get("status") in ("PASS", "FAIL")
                and type(observed.get("mismatch_count")) is int
                and observed["mismatch_count"] >= 0
                and observed.get("failure_class")
                == ("PASS" if observed["status"] == "PASS"
                    else "SEMANTIC MISMATCH")
                and (observed["status"] != "PASS"
                     or observed["mismatch_count"] == 0)
                and not process["timed_out"]
                and child.returncode
                == (0 if observed["status"] == "PASS" else 1)
                and observed.get("clock_samples") == 0
                and observed.get("holdout") == "NOT OPENED",
                "reject a missing, stale, forged, timed-out, or C-family worker")
        validate_streamed_observation(observed.get("complete_original_observation"))
        attempt["fully_observed"] = True
        if type(ledger) is dict:
            ledger["fully_observed_suite_count"] += 1
            entry = attempt.get("ledger_entry")
            if type(entry) is dict:
                entry["fully_observed"] = True
        return {
            "suite": name, "status": observed["status"],
            "case_execution_denominator": count,
            "failure_class": observed["failure_class"],
            "mismatch_count": observed["mismatch_count"],
            "worker_attempted": True,
            "actual_worker_started": True,
            "fully_observed": True,
            "actual_worker_processes": 1,
            "all_original_records_and_mismatches_preserved": True,
            "original_observer": observed,
            "process": process,
        }
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        reap_started_worker(child, process)
        raise
    except BaseException as error:
        reap_started_worker(child, process)
        return failed_worker(name, count, error, attempt=attempt,
                             observed=observed)


def failed_worker(name: str, count: int, error: BaseException,
                  *, attempt: Mapping[str, Any] | None = None,
                  observed: Mapping[str, Any] | None = None
                  ) -> dict[str, Any]:
    started = (attempt is not None
               and attempt.get("actual_worker_started") is True)
    process = (attempt.get("process") if started and attempt is not None
               else None)
    failure = record_failure(error)
    return {
        "suite": name, "status": "FAIL",
        "case_execution_denominator": count,
        "failure_class": "INFRASTRUCTURE FAILURE",
        "mismatch_count": "NOT MEASURED",
        "worker_attempted": (attempt is not None
                              and attempt.get("worker_attempted") is True),
        "actual_worker_started": started,
        "fully_observed": False,
        "actual_worker_processes": 1 if started else 0,
        "all_original_records_and_mismatches_preserved": False,
        "error_type": failure["error_type"],
        "error_message": failure["error_message"],
        "traceback": failure["traceback"],
        "worker_decoding_failure": failure,
        "actual_worker_output": observed,
        "process": process,
    }


def validate_complete_worker_stream(value: Any, limit: int,
                                    label: str) -> None:
    require(type(value) is dict
            and value.get("complete") is True
            and value.get("truncated") is False
            and value.get("limit_exceeded") is False
            and value.get("limit_bytes") == limit
            and type(value.get("size_bytes")) is int
            and 0 <= value["size_bytes"] <= limit
            and value.get("captured_prefix_bytes") == value["size_bytes"]
            and type(value.get("base64")) is str,
            "never treat a missing or truncated " + label + " as complete")
    checked_digest(value.get("sha256"), "complete original " + label)
    try:
        raw = base64.b64decode(value["base64"], validate=True)
    except (ValueError, TypeError) as error:
        raise CampaignError("reject concealed complete worker " + label) from error
    require(len(raw) == value["size_bytes"]
            and digest(raw) == value["sha256"],
            "authenticate every complete original worker " + label + " byte")


def validate_complete_worker_row(row: Any, name: str, count: int) -> None:
    require(type(row) is dict
            and row.get("suite") == name
            and row.get("case_execution_denominator") == count
            and row.get("worker_attempted") is True
            and row.get("actual_worker_started") is True
            and row.get("fully_observed") is True
            and row.get("actual_worker_processes") == 1
            and row.get("all_original_records_and_mismatches_preserved") is True
            and row.get("status") in ("PASS", "FAIL")
            and row.get("failure_class")
            == ("PASS" if row.get("status") == "PASS"
                else "SEMANTIC MISMATCH")
            and type(row.get("mismatch_count")) is int
            and row["mismatch_count"] >= 0
            and (row["status"] != "PASS" or row["mismatch_count"] == 0),
            "require one fully validated actual original " + name + " result")
    process = row.get("process")
    require(type(process) is dict
            and type(process.get("pid")) is int and process["pid"] > 0
            and process.get("actual_worker_processes") == 1
            and process.get("timed_out") is False
            and process.get("returncode")
            == (0 if row["status"] == "PASS" else 1),
            "require one genuine distinct non-timed-out " + name + " process")
    validate_complete_worker_stream(
        process.get("stdout"), MAX_WORKER_STDOUT_BYTES, name + " stdout")
    validate_complete_worker_stream(
        process.get("stderr"), MAX_WORKER_STDERR_BYTES, name + " stderr")
    observed = row.get("original_observer")
    require(type(observed) is dict
            and observed.get("schema") == WORKER_SCHEMA
            and observed.get("suite") == name
            and observed.get("candidate_family") == FAMILY
            and observed.get("label") == LABEL
            and observed.get("case_execution_denominator") == count
            and observed.get("actual_candidate_case_count") == count
            and observed.get("status") == row["status"]
            and observed.get("failure_class") == row["failure_class"]
            and observed.get("mismatch_count") == row["mismatch_count"]
            and observed.get("original_observer_source_sha256")
            == PRODUCER["source"][1]
            and observed.get("original_observer_version") == 4
            and observed.get("corrected_reference_receipt_sha256")
            == CORRECTED_REFERENCE["receipt"][1]
            and observed.get("corrected_reference_records_sha256")
            == CORRECTED_REFERENCE_RECORDS_SHA256
            and observed.get("corrected_reference_cache_records_sha256")
            == CORRECTED_REFERENCE_CACHE_RECORDS_SHA256
            and observed.get("corrected_reference_case_count")
            == CORRECTED_REFERENCE_CASE_COUNT
            and observed.get("corrected_reference_process_ids")
            == list(CORRECTED_REFERENCE_PIDS)
            and observed.get("candidate_run_uses_both_complete_reference_vectors")
            is True
            and observed.get("actual_v13_build_archive_sha256")
            == BUILD["archive"][1]
            and observed.get("actual_v13_build_receipt_sha256")
            == BUILD["receipt"][1]
            and observed.get("corrected_public_source_sha256")
            == CORRECTED_PUBLIC_SHA256
            and observed.get("corrected_bridge_source_sha256")
            == BRIDGE_SOURCE_SHA256
            and observed.get("native_engine_sha256") == ENGINE_SHA256
            and observed.get("native_bridge_sha256") == BRIDGE_SHA256
            and observed.get("repaired_source_owner_count") == 9
            and observed.get("all_original_records_and_mismatches_preserved")
            is True
            and observed.get("actual_candidate_workers") == 1
            and observed.get("clock_samples") == 0
            and observed.get("holdout") == "NOT OPENED",
            "bind all complete original " + name + " records to real V13")
    validate_streamed_observation(observed.get("complete_original_observation"))


def aggregate_worker_rows(rows: Sequence[dict[str, Any]],
                          *, controller_failure: Mapping[str, Any] | None = None,
                          graceful: Mapping[str, Any] | None = None
                          ) -> dict[str, Any]:
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "retain all thirteen exact original groups before aggregation")
    normalized: list[dict[str, Any]] = []
    unique_pids: set[int] = set()
    pids: list[int] = []
    attempted = 0
    started = 0
    complete = 0
    duplicates = 0
    missing = 0
    passed = 0
    observed_mismatches = 0
    for (name, count), original in zip(SUITES, rows, strict=True):
        row = original
        attempted += int(row.get("worker_attempted") is True)
        actual_started = row.get("actual_worker_started") is True
        started += int(actual_started)
        process = row.get("process")
        pid = process.get("pid") if type(process) is dict else None
        identity_error: CampaignError | None = None
        if actual_started:
            if type(pid) is not int or pid <= 0:
                missing += 1
                identity_error = CampaignError(
                    "preserve the started original " + name
                    + " worker without inventing a missing PID")
            elif pid in unique_pids:
                duplicates += 1
                identity_error = CampaignError(
                    "reject duplicated started original worker PID "
                    + str(pid))
            else:
                unique_pids.add(pid)
                pids.append(pid)
        if identity_error is None and row.get("fully_observed") is True:
            try:
                validate_complete_worker_row(row, name, count)
            except (CampaignError, ValueError, TypeError, zlib.error) as error:
                identity_error = CampaignError(
                    "reject incomplete original " + name + ": " + str(error))
        elif identity_error is None and row.get("fully_observed") is False:
            require(row.get("failure_class") == "INFRASTRUCTURE FAILURE",
                    "classify every incomplete original " + name
                    + " observation as an infrastructure failure")
        elif identity_error is None:
            identity_error = CampaignError(
                "reject an unspecified original observation state: " + name)
        if identity_error is not None:
            retained_attempt = {
                "worker_attempted": row.get("worker_attempted") is True,
                "actual_worker_started": actual_started,
                "process": process,
            }
            row = failed_worker(name, count, identity_error,
                                attempt=retained_attempt,
                                observed=row.get("original_observer"))
            row["rejected_worker_observation"] = original
        elif row.get("fully_observed") is True:
            complete += 1
            observed_mismatches += row["mismatch_count"]
            if row["failure_class"] == "PASS":
                passed += count
        normalized.append(row)
    infrastructure = sum(
        row.get("failure_class") == "INFRASTRUCTURE FAILURE"
        for row in normalized
    ) + int(controller_failure is not None)
    all_vectors_complete = (
        complete == SUITE_COUNT
        and started == SUITE_COUNT
        and len(pids) == SUITE_COUNT
        and duplicates == 0 and missing == 0
    )
    mismatch_count: int | str = (
        observed_mismatches if all_vectors_complete else "NOT MEASURED"
    )
    qualified = (
        all_vectors_complete
        and passed == CASE_COUNT
        and mismatch_count == 0
        and infrastructure == 0
        and graceful is None
    )
    return {
        "suite_results": normalized,
        "attempted_suite_count": attempted,
        "started_suite_count": started,
        "completed_suite_count": complete,
        "actual_candidate_workers": started,
        "actual_worker_process_ids": pids,
        "distinct_worker_process_id_count": len(pids),
        "duplicate_worker_process_id_count": duplicates,
        "missing_worker_process_id_count": missing,
        "all_original_observation_vectors_complete": all_vectors_complete,
        "verified_passing_case_count": passed,
        "semantic_mismatch_count": mismatch_count,
        "observed_partial_semantic_mismatch_count": observed_mismatches,
        "infrastructure_failure_count": infrastructure,
        "candidate_qualified": qualified,
    }


def evidence_names(failure: bool) -> tuple[str, str]:
    require(type(failure) is bool, "choose one exact exclusive campaign outcome")
    stem = "repaired-rust-original-campaign-v7-rust-" + LABEL
    if failure:
        stem += "-failures"
    return stem + ".json.gz", stem + "-publication-receipt.json"


def ensure_fresh_evidence(publication: types.ModuleType) -> None:
    directory = publication.open_evidence_directory()
    try:
        for failure in (False, True):
            for name in evidence_names(failure):
                try:
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise CampaignError("never overwrite a previous original Rust result: "
                                    + name)
    finally:
        os.close(directory)


def bounded_public_report(report: Mapping[str, Any]) -> int:
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=True,
                               separators=(",", ":"), allow_nan=False)
    count = 1
    for piece in encoder.iterencode(report):
        count += len(piece.encode("ascii"))
        require(count <= MAX_PUBLIC_REPORT_BYTES,
                "bound complete streamed original V4 campaign report to 32 MiB")
    return count


def validated_publication_accounting(
        report: Mapping[str, Any],
        ) -> dict[str, int]:
    evidence = report.get(
        "historical_evidence_owner_count_before_publication",
    )
    references = report.get(
        "historical_authenticated_reference_count_before_publication",
    )
    require(
        type(evidence) is int
        and evidence == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
        and type(references) is int
        and references == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "bind publication to the genuine current V43 owner lower bounds",
    )
    return {
        "historical_evidence_owner_count_before_publication": evidence,
        "historical_authenticated_reference_count_before_publication":
            references,
        "new_repository_evidence_owner_count": 2,
        "resulting_repository_evidence_owner_count": evidence + 2,
        "resulting_authenticated_reference_count": references + 2,
    }


def preserve_campaign(
        report: dict[str, Any],
        retained: Mapping[str, Any],
        v2: Any,
        ledger: dict[str, Any] | None = None,
        *,
        directory_closer: Any | None = None,
        ) -> dict[str, Any]:
    if ledger is not None:
        ledger["publication_attempted"] = True
        ledger["publication_status"] = "ATTEMPTED; NOT COMPLETE"
    require(report.get("schema") == CAMPAIGN_SCHEMA
            and report.get("status") in ("PASS", "FAIL")
            and report.get("family") == FAMILY
            and report.get("label") == LABEL
            and report.get("suite_count") == SUITE_COUNT
            and report.get("case_execution_denominator") == CASE_COUNT
            and report.get("named_private_waiver_count")
            == PRIVATE_WAIVER_COUNT
            and type(report.get("suite_results")) is list
            and len(report["suite_results"]) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in report["suite_results"]] == list(SUITES)
            and report.get("all_four_original_targets_restored") is True
            and report.get("restoration_verified_before_publication") is True
            and report.get("historical_evidence_owner_count_before_publication")
            == CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND
            and report.get("historical_authenticated_reference_count_before_publication")
            == CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND
            and report.get("holdout") == "NOT OPENED",
            "never publish invented original cases or unrestored Rust target inodes")
    publication_counts = validated_publication_accounting(report)
    if ledger is not None:
        ledger["bounded_report_attempted"] = True
    size = bounded_public_report(report)
    if ledger is not None:
        ledger["bounded_report_status"] = "PASS"
    current = v2.exact_originals()
    require(report.get("restored_original_targets") == current,
            "prove all exact original target inodes immediately before publication")
    publication = retained["publication"]
    archive_name, receipt_name = evidence_names(report["status"] == "FAIL")
    if ledger is not None:
        ledger["archive_publication_attempted"] = True
        ledger["archive_publication_status"] = "ATTEMPTED; OUTCOME UNKNOWN"
    directory = publication.open_evidence_directory()
    try:
        archive, stream = publication.write_streamed_archive(
            report, archive_name, directory)
    finally:
        (os.close if directory_closer is None
         else directory_closer)(directory)
    if ledger is not None:
        ledger["archive_owner"] = copy.deepcopy(archive)
        ledger["archive_publication_status"] = "WRITTEN; NOT YET VERIFIED"
    require(type(archive) is dict
            and type(stream) is dict
            and archive.get("relative") == archive_name
            and archive.get("path")
            == str(ROOT / EVIDENCE_RELATIVE / archive_name)
            and archive.get("sha256") == stream.get("archive_sha256")
            and archive.get("size_bytes") == stream.get("archive_bytes")
            and type(archive.get("write_calls")) is int
            and archive["write_calls"] > 0
            and archive["write_calls"] == stream.get("archive_write_calls")
            and archive.get("mode") == 0o600
            and archive.get("exclusive_creation") is True
            and archive.get("same_inode_readback_verified") is True
            and archive.get("streaming_readback_verified") is True
            and archive.get("file_fsync_completed") is True
            and archive.get("directory_fsync_completed") is True
            and stream.get("gzip_mtime") == 0
            and stream.get("gzip_single_member") is True
            and stream.get("canonical_terminal_newline_count") == 1
            and stream.get("uncompressed_bytes") == size,
            "create one complete owner-only deterministic streamed V4 result")
    if ledger is not None:
        ledger["archive_publication_status"] = "PASS"
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": "PASS",
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "candidate_status": report["status"],
        "family": FAMILY, "label": LABEL, "archive": archive,
        "campaign_source_sha256": report["campaign_source_sha256"],
        "campaign_protocol_sha256": report["campaign_protocol_sha256"],
        "campaign_contract_sha256": report["campaign_contract_sha256"],
        "original_v4_producer_source_sha256": PRODUCER["source"][1],
        "original_v4_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v4_producer_contract_sha256": PRODUCER["contract"][1],
        "original_v4_producer_version": 4,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v43_source_sha256": V43["source"][1],
        "published_current_v43_inputs_sha256": V43["inputs"][1],
        "published_current_v43_summary_sha256": V43["summary"][1],
        "published_current_v43_svg_sha256": V43["svg"][1],
        "current_overview_version": 43,
        "preserved_v42_source_sha256": V42["source"][1],
        "preserved_v42_inputs_sha256": V42["inputs"][1],
        "preserved_v42_summary_sha256": V42["summary"][1],
        "preserved_v42_svg_sha256": V42["svg"][1],
        "preserved_v41_source_sha256": V41["source"][1],
        "preserved_v41_inputs_sha256": V41["inputs"][1],
        "preserved_v41_summary_sha256": V41["summary"][1],
        "preserved_v41_svg_sha256": V41["svg"][1],
        "historical_v2_public_adapter_sha256":
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
        "historical_v2_public_adapter_bytes":
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        "actual_v6_preflight_failure_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["failure"][1],
        "actual_v6_preflight_observation_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["observation"][1],
        "preserved_v40_source_sha256": V40["source"][1],
        "preserved_v40_inputs_sha256": V40["inputs"][1],
        "preserved_v40_summary_sha256": V40["summary"][1],
        "preserved_v40_svg_sha256": V40["svg"][1],
        "corrected_c_only_runner_v10_source_sha256":
            CORRECTED_C_ONLY_V10["runner"][1],
        "corrected_c_only_worker_v8_source_sha256":
            CORRECTED_C_ONLY_V10["worker"][1],
        "corrected_c_only_protocol_v10_sha256":
            CORRECTED_C_ONLY_V10["protocol"][1],
        "corrected_c_only_contract_v10_sha256":
            CORRECTED_C_ONLY_V10["contract"][1],
        "first_party_source_inventory_family_count": 6,
        "corrected_c_only_runnable_family_count": 1,
        "corrected_c_matching_status": "NOT RUN",
        "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
        "preserved_v39_source_sha256": V39["source"][1],
        "preserved_v39_inputs_sha256": V39["inputs"][1],
        "preserved_v39_summary_sha256": V39["summary"][1],
        "preserved_v39_svg_sha256": V39["svg"][1],
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "uncompressed_sha256": stream["uncompressed_sha256"],
        "uncompressed_bytes": stream["uncompressed_bytes"],
        "uncompressed_chunk_count": stream["uncompressed_chunk_count"],
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        "attempted_suite_count": report["attempted_suite_count"],
        "started_suite_count": report["started_suite_count"],
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_worker_process_ids": report["actual_worker_process_ids"],
        "distinct_worker_process_id_count":
        report["distinct_worker_process_id_count"],
        "duplicate_worker_process_id_count":
        report["duplicate_worker_process_id_count"],
        "missing_worker_process_id_count":
        report["missing_worker_process_id_count"],
        "all_original_observation_vectors_complete":
        report["all_original_observation_vectors_complete"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        **publication_counts,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "restoration_verified_before_publication": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }
    if ledger is not None:
        ledger["receipt_publication_attempted"] = True
        ledger["receipt_publication_status"] = "ATTEMPTED; OUTCOME UNKNOWN"
    receipt_owner = v2.write_evidence_receipt(receipt_name, receipt)
    if ledger is not None:
        ledger["receipt_owner"] = copy.deepcopy(receipt_owner)
        ledger["receipt_publication_status"] = "WRITTEN; NOT YET VERIFIED"
    complete_receipt = canonical(receipt)
    require(type(receipt_owner) is dict
            and receipt_owner.get("relative")
            == EVIDENCE_RELATIVE + "/" + receipt_name
            and receipt_owner.get("path")
            == str(ROOT / EVIDENCE_RELATIVE / receipt_name)
            and receipt_owner.get("sha256") == digest(complete_receipt)
            and receipt_owner.get("bytes") == len(complete_receipt)
            and receipt_owner.get("size_bytes") == len(complete_receipt)
            and receipt_owner.get("mode") == 0o600
            and receipt_owner.get("uid") == ORIGINALS["adapter"]["uid"]
            and receipt_owner.get("nlink") == 1
            and receipt_owner.get("exclusive_creation") is True
            and receipt_owner.get("same_inode_readback_verified") is True
            and receipt_owner.get("file_fsync_completed") is True
            and receipt_owner.get("directory_fsync_completed") is True
            and all(receipt.get(field) == value
                    for field, value in publication_counts.items())
            and (archive["device"], archive["inode"])
            != (receipt_owner["device"], receipt_owner["inode"])
            and v2.exact_originals() == current,
            "publish two distinct durable owners only after exact restoration")
    if ledger is not None:
        ledger["receipt_publication_status"] = "PASS"
        ledger["publication_status"] = "PASS"
    return {
        "schema": SCHEMA + "-published-complete-original-campaign",
        "status": report["status"],
        "publication_status": "PASS",
        "publication_pass_means": "DURABLE PUBLICATION ONLY",
        "family": FAMILY, "label": LABEL,
        "archive": archive, "receipt": receipt_owner,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "attempted_suite_count": report["attempted_suite_count"],
        "started_suite_count": report["started_suite_count"],
        "completed_suite_count": report["completed_suite_count"],
        "actual_candidate_workers": report["actual_candidate_workers"],
        "actual_worker_process_ids": report["actual_worker_process_ids"],
        "distinct_worker_process_id_count":
        report["distinct_worker_process_id_count"],
        "duplicate_worker_process_id_count":
        report["duplicate_worker_process_id_count"],
        "missing_worker_process_id_count":
        report["missing_worker_process_id_count"],
        "all_original_observation_vectors_complete":
        report["all_original_observation_vectors_complete"],
        "verified_passing_case_count": report["verified_passing_case_count"],
        "semantic_mismatch_count": report["semantic_mismatch_count"],
        "infrastructure_failure_count": report["infrastructure_failure_count"],
        "candidate_qualified": report["candidate_qualified"],
        **publication_counts,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": report["recovery_journal_sha256"],
        "all_four_original_targets_restored": True,
        "restored_original_targets": current,
        "group_atomic": False,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "holdout": "NOT OPENED", "winner_selected": False,
    }


def record_failure(error: BaseException) -> dict[str, Any]:
    frames: list[str] = ["Traceback (most recent call last):\n"]
    current = error.__traceback__
    count = 0
    while current is not None and count < 32:
        code = current.tb_frame.f_code
        frames.append(
            '  File "' + str(code.co_filename)[:1024]
            + '", line ' + str(current.tb_lineno)
            + ", in " + str(code.co_name)[:256] + "\n"
        )
        current = current.tb_next
        count += 1
    if current is not None:
        frames.append("  [remaining traceback frames explicitly omitted]\n")
    try:
        message = str(error)[:4096]
    except (KeyboardInterrupt, SystemExit, GracefulControllerSignal):
        raise
    except BaseException:
        message = "error message could not be safely represented"
    frames.append(type(error).__qualname__ + ": " + message + "\n")
    return {"error_type": type(error).__qualname__,
            "error_message": message, "traceback": frames}


def compact_worker_failure_record(row: Mapping[str, Any]) -> dict[str, Any]:
    compact = {
        key: row.get(key)
        for key in (
            "suite", "status", "case_execution_denominator",
            "failure_class", "mismatch_count", "worker_attempted",
            "actual_worker_started", "fully_observed",
            "actual_worker_processes",
            "all_original_records_and_mismatches_preserved",
            "error_type", "error_message",
        )
        if key in row
    }
    process = row.get("process")
    if type(process) is dict:
        retained = {
            key: process.get(key)
            for key in (
                "argv", "pid", "returncode", "timed_out",
                "actual_worker_processes", "cleanup_failures",
                "kill_attempted",
            )
            if key in process
        }
        for channel in ("stdout", "stderr"):
            value = process.get(channel)
            if type(value) is not dict:
                retained[channel] = value
                continue
            detail = dict(value)
            encoded = detail.get("base64")
            if type(encoded) is str:
                prefix_length = 4 * (
                    (MAX_FAILURE_STREAM_CAPTURE_BYTES + 2) // 3
                )
                if len(encoded) > prefix_length:
                    prefix = base64.b64decode(
                        encoded[:prefix_length], validate=True
                    )[:MAX_FAILURE_STREAM_CAPTURE_BYTES]
                    detail["base64"] = base64.b64encode(prefix).decode("ascii")
                    detail["captured_prefix_bytes"] = len(prefix)
                    detail["complete"] = False
                    detail["truncated"] = True
                    detail["capture_status"] = "TRUNCATED FAILURE-REPORT PREFIX"
            retained[channel] = detail
        compact["process"] = retained
    else:
        compact["process"] = process
    observed = row.get("original_observer")
    if type(observed) is dict:
        observation = observed.get("complete_original_observation")
        compact["retained_original_observation"] = {
            "schema": observed.get("schema"),
            "status": observed.get("status"),
            "suite": observed.get("suite"),
            "mismatch_count": observed.get("mismatch_count"),
            "compressed_observation": (
                {
                    key: observation.get(key)
                    for key in (
                        "encoding", "gzip_mtime", "compressed_sha256",
                        "compressed_bytes", "uncompressed_sha256",
                        "uncompressed_bytes",
                    )
                }
                if type(observation) is dict else None
            ),
            "complete_case_archive_durably_published": False,
        }
    if type(row.get("worker_decoding_failure")) is dict:
        compact["worker_decoding_failure"] = row["worker_decoding_failure"]
    return compact


def campaign_entry_failure_result(error: BaseException,
                                  ledger: Mapping[str, Any]
                                  ) -> dict[str, Any]:
    require(type(ledger) is dict
            and ledger.get("schema")
            == SCHEMA + "-authorized-run-actual-effect-ledger"
            and ledger.get("campaign_mode") == "AUTHORIZED RUN",
            "report an authorized campaign failure from its actual effect ledger")
    failure = record_failure(error)
    snapshot = {
        key: copy.deepcopy(value)
        for key, value in ledger.items()
        if key not in ("schema", "retained_suite_results")
    }
    snapshot["effect_ledger_schema"] = ledger["schema"]
    snapshot["retained_suite_results"] = [
        compact_worker_failure_record(row)
        for row in ledger.get("retained_suite_results", [])
    ]
    if snapshot.get("publication_attempted") is True:
        snapshot["publication_status"] = "FAIL"
        snapshot["publication_failure"] = failure
    return {
        **snapshot,
        "schema": SCHEMA + "-entry-failure",
        "status": "FAIL",
        "family": FAMILY,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "actual_evidence_owner_count_before_new_campaign":
        CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "actual_authenticated_reference_count_before_new_campaign":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "semantic_mismatch_count": "NOT MEASURED",
        "all_original_observation_vectors_complete": False,
        "original_case_archive_durably_published": False,
        "source_only_zero_effects_claimed": False,
        "candidate_qualified": False,
        "winner_selected": False,
        "group_atomic": False,
        "error_type": failure["error_type"],
        "error_message": failure["error_message"],
        "traceback": failure["traceback"],
    }


def run_campaign(options: argparse.Namespace,
                 ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    if ledger is None:
        ledger = new_campaign_effect_ledger(options)
    assert_actual_authorization(options)
    # Prove the complete historical helper before any retained build effect.
    v2 = patched_v2_helpers(ledger)
    context, retained = verify_context(
        options.source_sha256,
        options.protocol_sha256,
        options.contract_sha256,
        retain=True,
        ledger=ledger,
    )
    require(
        context.get("status") == "PASS",
        "authenticate current V43, the genuine V6 loss, and real V13 "
        "before any target mutation",
    )
    publication = load_frozen_module(
        PUBLICATION["source"], "_rebar_exact_v2_streaming_publication_for_rust_v4")
    require(publication.SCHEMA == "rebar-owned-six-family-original-p0-campaign-v2"
            and callable(publication.write_streamed_archive),
            "reuse only the exact original first-party streaming publisher")
    retained["publication"] = publication
    ensure_fresh_evidence(publication)
    baseline: dict[str, Any] | None = None
    active: dict[str, Any] | None = None
    restoration: dict[str, Any] | None = None
    controller_failure: dict[str, Any] | None = None
    graceful: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    directory: int | None = None
    lock: int | None = None
    with installed_signal_handlers():
        ledger["signal_handlers_installed"] = len(SIGNAL_NAMES)
        try:
            with blocked_controller_signals():
                directory, lock = open_recovery_lock(
                    v2, options.activation_root, create=True,
                    ledger=ledger)
            baseline = v2.exact_originals()
            ledger["canonical_target_read_lower_bound"] += len(ROLE_ORDER)
            active = activate_four_roles(v2, retained, options, ledger)
            for name, count in SUITES:
                attempt = new_worker_attempt(name, count, ledger)
                try:
                    row = execute_one_worker(
                        options, name, count, active, attempt)
                except GracefulControllerSignal as error:
                    row = failed_worker(name, count, error, attempt=attempt)
                    rows.append(row)
                    ledger["retained_suite_results"].append(row)
                    raise
                except Exception as error:
                    row = failed_worker(name, count, error, attempt=attempt)
                rows.append(row)
                ledger["retained_suite_results"].append(row)
        except GracefulControllerSignal as error:
            controller_failure = record_failure(error)
            graceful = {
                "schema": SIGNAL_SCHEMA, "status": "FAIL",
                "signal_name": error.signal_name,
                "signal_number": error.signum,
                "candidate_matching_result": "NOT MEASURED",
                "group_atomic": False,
            }
            seen = {row.get("suite") for row in rows}
            for name, count in SUITES:
                if name not in seen:
                    row = failed_worker(name, count, error)
                    rows.append(row)
                    ledger["retained_suite_results"].append(row)
        except Exception as error:
            controller_failure = record_failure(error)
            seen = {row.get("suite") for row in rows}
            for name, count in SUITES:
                if name not in seen:
                    row = failed_worker(name, count, error)
                    rows.append(row)
                    ledger["retained_suite_results"].append(row)
        finally:
            try:
                if active is not None:
                    with blocked_controller_signals():
                        restoration = restore_corrected_four_roles(
                            v2, active["root"], active["journal"],
                            active["journal_owner"]["sha256"], ledger)
                if baseline is not None:
                    with blocked_controller_signals():
                        require(v2.exact_originals() == baseline,
                                "restore every exact original Rust owner inode")
            finally:
                if lock is not None:
                    os.close(lock)
                if directory is not None:
                    os.close(directory)
    suite_positions = {name: position
                       for position, (name, _) in enumerate(SUITES)}
    rows.sort(key=lambda row: suite_positions[row["suite"]])
    require(len(rows) == SUITE_COUNT
            and [(row.get("suite"), row.get("case_execution_denominator"))
                 for row in rows] == list(SUITES),
            "preserve all original groups even when a genuine worker fails")
    require(baseline is not None and active is not None
            and restoration is not None,
            "never publish a campaign without actual exact original recovery")
    originals = v2.exact_originals()
    require(originals == baseline,
            "reauthenticate original inodes before any public evidence")
    aggregate = aggregate_worker_rows(
        rows, controller_failure=controller_failure, graceful=graceful)
    rows = aggregate["suite_results"]
    ledger["retained_suite_results"] = rows
    ledger["attempted_suite_count"] = aggregate["attempted_suite_count"]
    ledger["started_suite_count"] = aggregate["started_suite_count"]
    ledger["fully_observed_suite_count"] = aggregate["completed_suite_count"]
    ledger["actual_candidate_workers"] = aggregate["actual_candidate_workers"]
    ledger["actual_worker_process_ids"] = aggregate["actual_worker_process_ids"]
    qualified = aggregate["candidate_qualified"]
    report = {
        "schema": CAMPAIGN_SCHEMA,
        "status": "PASS" if qualified else "FAIL",
        "family": FAMILY, "label": LABEL,
        "campaign_source_sha256": options.source_sha256,
        "campaign_protocol_sha256": options.protocol_sha256,
        "campaign_contract_sha256": options.contract_sha256,
        "original_v4_producer_source_sha256": PRODUCER["source"][1],
        "original_v4_producer_protocol_sha256": PRODUCER["protocol"][1],
        "original_v4_producer_contract_sha256": PRODUCER["contract"][1],
        "original_v4_producer_version": 4,
        "corrected_reference_receipt_sha256":
            CORRECTED_REFERENCE["receipt"][1],
        "corrected_reference_records_sha256":
            CORRECTED_REFERENCE_RECORDS_SHA256,
        "corrected_reference_cache_records_sha256":
            CORRECTED_REFERENCE_CACHE_RECORDS_SHA256,
        "corrected_reference_case_count":
            CORRECTED_REFERENCE_CASE_COUNT,
        "corrected_reference_process_ids":
            list(CORRECTED_REFERENCE_PIDS),
        "candidate_run_uses_both_complete_reference_vectors": True,
        "published_current_v43_source_sha256": V43["source"][1],
        "published_current_v43_inputs_sha256": V43["inputs"][1],
        "published_current_v43_summary_sha256": V43["summary"][1],
        "published_current_v43_svg_sha256": V43["svg"][1],
        "current_overview_version": 43,
        "preserved_v42_source_sha256": V42["source"][1],
        "preserved_v42_inputs_sha256": V42["inputs"][1],
        "preserved_v42_summary_sha256": V42["summary"][1],
        "preserved_v42_svg_sha256": V42["svg"][1],
        "preserved_v41_source_sha256": V41["source"][1],
        "preserved_v41_inputs_sha256": V41["inputs"][1],
        "preserved_v41_summary_sha256": V41["summary"][1],
        "preserved_v41_svg_sha256": V41["svg"][1],
        "historical_v2_public_adapter_sha256":
            HISTORICAL_V2_REPAIRED_PUBLIC_SHA256,
        "historical_v2_public_adapter_bytes":
            HISTORICAL_V2_REPAIRED_PUBLIC_BYTES,
        "actual_v6_preflight_failure_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["failure"][1],
        "actual_v6_preflight_observation_sha256":
            ACTUAL_V6_PREFLIGHT_FAILURE["observation"][1],
        "preserved_v40_source_sha256": V40["source"][1],
        "preserved_v40_inputs_sha256": V40["inputs"][1],
        "preserved_v40_summary_sha256": V40["summary"][1],
        "preserved_v40_svg_sha256": V40["svg"][1],
        "corrected_c_only_runner_v10_source_sha256":
            CORRECTED_C_ONLY_V10["runner"][1],
        "corrected_c_only_worker_v8_source_sha256":
            CORRECTED_C_ONLY_V10["worker"][1],
        "corrected_c_only_protocol_v10_sha256":
            CORRECTED_C_ONLY_V10["protocol"][1],
        "corrected_c_only_contract_v10_sha256":
            CORRECTED_C_ONLY_V10["contract"][1],
        "first_party_source_inventory_family_count": 6,
        "corrected_c_only_runnable_family_count": 1,
        "corrected_c_matching_status": "NOT RUN",
        "rust_v6_runner_status_at_v41_publication": "UNCOMMITTED",
        "preserved_v39_source_sha256": V39["source"][1],
        "preserved_v39_inputs_sha256": V39["inputs"][1],
        "preserved_v39_summary_sha256": V39["summary"][1],
        "preserved_v39_svg_sha256": V39["svg"][1],
        "actual_v13_build_source_sha256": BUILD["source"][1],
        "actual_v13_build_protocol_sha256": BUILD["protocol"][1],
        "actual_v13_build_contract_sha256": BUILD["contract"][1],
        "actual_v13_build_archive_sha256": BUILD["archive"][1],
        "actual_v13_build_receipt_sha256": BUILD["receipt"][1],
        "actual_v13_compiler_process_count": 28,
        "actual_corrected_rust_source_owner_count": 9,
        "corrected_public_adapter_sha256": CORRECTED_PUBLIC_SHA256,
        "corrected_bridge_source_sha256": BRIDGE_SOURCE_SHA256,
        "native_engine_sha256": ENGINE_SHA256,
        "native_bridge_sha256": BRIDGE_SHA256,
        "native_engine_bytes": ENGINE_BYTES,
        "native_bridge_bytes": BRIDGE_BYTES,
        "suite_count": SUITE_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "named_private_waiver_count": PRIVATE_WAIVER_COUNT,
        **aggregate,
        "historical_evidence_owner_count_before_publication":
        CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
        "historical_authenticated_reference_count_before_publication":
        CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
        "preserved_previous_rust_semantic_mismatch_count": 1036,
        "preserved_previous_rust_verified_passing_case_count": 8965,
        "preserved_c_semantic_mismatch_count": 1230,
        "preserved_c_verified_passing_case_count": 7325,
        "preserved_zig_semantic_mismatch_count": 1764,
        "preserved_zig_verified_passing_case_count": 3711,
        "supplementary_signature_case_count": SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_status": "PASS",
        "supplementary_signature_reference_cases_executed":
        SUPPLEMENT_CASE_COUNT,
        "supplementary_signature_reference_process_count":
        SUPPLEMENT_REFERENCE_PROCESS_COUNT,
        "supplementary_signature_reference_receipt_sha256":
        REFERENCE["receipt"][1],
        "supplementary_signature_candidate_status": "NOT RUN",
        "supplementary_signature_candidate_cases_executed": 0,
        "public_recovery_root": PUBLIC_RECOVERY_ROOT,
        "recovery_journal_sha256": active["journal_owner"]["sha256"],
        "graceful_signal": graceful,
        "all_four_original_targets_restored": True,
        "restored_original_targets": originals,
        "restoration": restoration,
        "restoration_verified_before_publication": True,
        "v9_c_only_runner_invoked": False,
        "v7_zig_only_activation_invoked": False,
        "v2_unsafe_controller_invoked": False,
        "v2_unsafe_activation_invoked": False,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "controller_failure": controller_failure,
        "hidden_cases_read": 0, "benchmark_files_read": 0,
        "clock_samples": 0, "timing_trials_run": 0,
        "performance": "NOT MEASURED", "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }
    return preserve_campaign(report, retained, v2, ledger)


def recover_originals(
        options: argparse.Namespace,
        *,
        descriptor_closer: Any | None = None,
        ) -> dict[str, Any]:
    require(
        options.recovery_journal_sha256 is not None,
        "independently pin the actual V7 journal before public recovery",
    )
    v2 = patched_v2_helpers()
    context, _ = verify_context(
        options.source_sha256,
        options.protocol_sha256,
        options.contract_sha256,
        retain=False,
    )
    require(
        context.get("status") == "PASS",
        "authenticate the complete immutable V7 context before recovery",
    )
    root = checked_root(options.activation_root)
    directory: int | None = None
    lock: int | None = None
    restoration: dict[str, Any] | None = None
    try:
        with blocked_controller_signals():
            directory, lock = open_recovery_lock(v2, root, create=False)
            journal, owner = v2.read_private(
                root, "recovery-journal.json",
                options.recovery_journal_sha256)
            require(owner["sha256"] == options.recovery_journal_sha256
                    and journal.get("recoverable_v7_controller_source_sha256")
                    == options.source_sha256
                    and journal.get("recoverable_v7_controller_protocol_sha256")
                    == options.protocol_sha256
                    and journal.get("recoverable_v7_controller_contract_sha256")
                    == options.contract_sha256
                    and journal.get("corrected_public_adapter_sha256")
                    == CORRECTED_PUBLIC_SHA256
                    and journal.get("build_archive_sha256") == BUILD["archive"][1]
                    and journal.get("build_receipt_sha256") == BUILD["receipt"][1]
                    and journal.get("activation_root") == root
                    and journal.get("role_order") == list(ROLE_ORDER)
                    and journal.get("restoration_order")
                    == list(RESTORATION_ORDER)
                    and journal.get("group_atomic") is False,
                    "recover only the caller-pinned genuine exact V4 journal")
            restoration = restore_corrected_four_roles(
                v2, root, journal, options.recovery_journal_sha256)
            originals = v2.exact_originals()
            require(all(v2.same_original(originals[role], ORIGINALS[role])
                        for role in ROLE_ORDER)
                    and restoration.get("report", {}).get("status") == "PASS"
                    and restoration["report"].get("original_inodes_preserved")
                    is True,
                    "prove exact reverse recovery of all four original Rust inodes")
    finally:
        if lock is not None:
            (os.close if descriptor_closer is None
             else descriptor_closer)(lock)
        if directory is not None:
            (os.close if descriptor_closer is None
             else descriptor_closer)(directory)
    return {
        "schema": RECOVERY_SCHEMA, "status": "PASS", "version": 7,
        "family": FAMILY, "activation_root": root,
        "recovery_journal_sha256": options.recovery_journal_sha256,
        "restoration_order": list(RESTORATION_ORDER),
        "restoration": restoration,
        "restored_original_targets": originals,
        "all_four_original_targets_restored": True,
        "actual_candidate_workers": 0,
        "group_atomic": False,
        "sigkill_automatically_recovered": False,
        "power_failure_automatically_recovered": False,
        "performance": "NOT MEASURED", "holdout": "NOT OPENED",
        "winner_selected": False,
    }


def assert_actual_authorization(options: argparse.Namespace) -> None:
    require(options.family == FAMILY and options.label == LABEL
            and options.activation_root == PUBLIC_RECOVERY_ROOT
            and options.producer_source_sha256 == PRODUCER["source"][1]
            and options.producer_protocol_sha256 == PRODUCER["protocol"][1]
            and options.producer_contract_sha256 == PRODUCER["contract"][1]
            and options.build_source_sha256 == BUILD["source"][1]
            and options.build_protocol_sha256 == BUILD["protocol"][1]
            and options.build_contract_sha256 == BUILD["contract"][1]
            and options.build_archive_sha256 == BUILD["archive"][1]
            and options.build_receipt_sha256 == BUILD["receipt"][1]
            and options.native_engine_sha256 == ENGINE_SHA256
            and options.native_bridge_sha256 == BRIDGE_SHA256
            and options.native_engine_bytes == ENGINE_BYTES
            and options.native_bridge_bytes == BRIDGE_BYTES,
            "independently caller-pin the exact actual V13 and original producer")


def parse_arguments(arguments: Sequence[str] | None = None
                    ) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    modes.add_argument("--render-contract", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--worker", action="store_true")
    modes.add_argument("--recover", action="store_true")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--protocol-sha256", required=True)
    parser.add_argument("--contract-sha256")
    parser.add_argument("--family")
    parser.add_argument("--label")
    parser.add_argument("--suite", choices=tuple(name for name, _ in SUITES))
    parser.add_argument("--activation-root")
    parser.add_argument("--native-engine-bytes", type=int)
    parser.add_argument("--native-bridge-bytes", type=int)
    for name in (
        "producer-source", "producer-protocol", "producer-contract",
        "build-source", "build-protocol", "build-contract", "build-archive",
        "build-receipt", "native-engine", "native-bridge",
        "activation-report", "activation-receipt", "recovery-journal",
    ):
        parser.add_argument("--" + name + "-sha256")
    options = parser.parse_args(arguments)
    checked_digest(options.source_sha256, "V4 controller source")
    checked_digest(options.protocol_sha256, "V4 controller protocol")
    if options.contract_sha256 is not None:
        checked_digest(options.contract_sha256, "V4 controller contract")
    actual_names = (
        "family", "label", "suite", "activation_root",
        "native_engine_bytes", "native_bridge_bytes",
        "producer_source_sha256", "producer_protocol_sha256",
        "producer_contract_sha256", "build_source_sha256",
        "build_protocol_sha256", "build_contract_sha256",
        "build_archive_sha256", "build_receipt_sha256",
        "native_engine_sha256", "native_bridge_sha256",
        "activation_report_sha256", "activation_receipt_sha256",
        "recovery_journal_sha256",
    )
    if options.render_contract:
        require(options.contract_sha256 is None
                and all(getattr(options, name) is None for name in actual_names),
                "machine rendering may never select, activate, or run Rust")
        return options
    require(options.contract_sha256 is not None,
            "independently pin the immutable Rust V4 machine contract")
    if options.self_test or options.verify_frozen_context:
        require(all(getattr(options, name) is None for name in actual_names),
                "source-only V4 may never run or recover a candidate")
        return options
    if options.recover:
        require(options.family == FAMILY
                and options.activation_root == PUBLIC_RECOVERY_ROOT
                and options.recovery_journal_sha256 is not None
                and options.label is None and options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None,
                "authorize only exact caller-pinned public recovery")
        checked_digest(options.recovery_journal_sha256,
                       "actual durable V4 recovery journal")
        return options
    assert_actual_authorization(options)
    if options.worker:
        require(options.suite is not None
                and options.activation_report_sha256 is not None
                and options.activation_receipt_sha256 is not None
                and options.recovery_journal_sha256 is not None,
                "bind each original worker to all three real live activation owners")
        for name in ("activation_report_sha256", "activation_receipt_sha256",
                     "recovery_journal_sha256"):
            checked_digest(getattr(options, name), name)
    else:
        require(options.suite is None
                and options.activation_report_sha256 is None
                and options.activation_receipt_sha256 is None
                and options.recovery_journal_sha256 is None,
                "run all thirteen original suites only through fresh V4 activation")
    return options


def main(arguments: Sequence[str] | None = None) -> int:
    options: argparse.Namespace | None = None
    campaign_ledger: dict[str, Any] | None = None
    try:
        options = parse_arguments(arguments)
        if options.run:
            campaign_ledger = new_campaign_effect_ledger(options)
        verify_runtime()
        if options.self_test:
            result = source_self_test(options.source_sha256,
                                      options.protocol_sha256,
                                      options.contract_sha256)
        elif options.verify_frozen_context:
            result, _ = verify_context(options.source_sha256,
                                       options.protocol_sha256,
                                       options.contract_sha256)
        elif options.render_contract:
            result = protocol_document(options.source_sha256,
                                       options.protocol_sha256)
        elif options.worker:
            result = run_worker(options)
        elif options.recover:
            result = recover_originals(options)
        else:
            require(campaign_ledger is not None,
                    "install a truthful actual effect ledger before a real run")
            result = run_campaign(options, campaign_ledger)
        raw = canonical(result)
        require(len(raw) <= MAX_WORKER_STDOUT_BYTES,
                "never truncate the complete caller-visible V4 result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in ("PASS", "SOURCE FROZEN; CORRECTED RUST V13 CANDIDATE NOT RUN") else 1
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        if options is not None and options.run:
            if campaign_ledger is None:
                campaign_ledger = new_campaign_effect_ledger(options)
            result = campaign_entry_failure_result(error, campaign_ledger)
        else:
            failure = record_failure(error)
            result = {
                "schema": SCHEMA + "-entry-failure", "status": "FAIL",
                "error_type": failure["error_type"],
                "error_message": failure["error_message"],
                "traceback": failure["traceback"],
                "family": FAMILY, "suite_count": SUITE_COUNT,
                "case_execution_denominator": CASE_COUNT,
                "actual_evidence_owner_count_before_new_campaign":
                CURRENT_V43_EVIDENCE_OWNER_LOWER_BOUND,
                "actual_authenticated_reference_count_before_new_campaign":
                CURRENT_V43_HISTORY_REFERENCE_LOWER_BOUND,
                "group_atomic": False,
            }
            if options is not None and (options.worker or options.recover):
                result.update({
                    "actual_operation_mode":
                    "WORKER" if options.worker else "RECOVERY",
                    "actual_operation_effects": "NOT MEASURED",
                    "actual_candidate_workers": "NOT MEASURED",
                    "actual_native_activations": "NOT MEASURED",
                    "canonical_target_replacements": "NOT MEASURED",
                    "candidate_qualified": False,
                    "source_only_zero_effects_claimed": False,
                    "performance": "NOT MEASURED",
                    "holdout": "NOT OPENED",
                    "winner_selected": False,
                })
            else:
                result.update(zero_effects())
        raw = canonical(result)
        require(len(raw) <= MAX_WORKER_STDOUT_BYTES,
                "never truncate a truthful complete campaign failure result")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
