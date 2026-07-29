#!/usr/bin/env python3
"""Freeze the V19-backed, guarded, original 31,237-case Rust campaign.

The four source-only gates authenticate small, already published owners.  They
never open a build archive or private build root, start a process, import a
candidate, load a native library, consult a clock, or open the holdout.  Actual
matching is a separate, explicitly pinned operation; it reuses the unchanged
first-party V11 thirteen-worker and four-role recovery implementation in memory.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import os
import stat
import sys
import types


ROOT = "/home/dev-user/src/rebar"
PYTHON = "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14"
PYTHON_SHA256 = "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016"
SOURCE = "tools/run_owned_repaired_rust_original_campaign_v12.py"
PROTOCOL = "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V12.md"
CONTRACT = "oracle/phase2/repaired-rust-original-campaign-v12.json"
SCHEMA = "rebar-owned-repaired-rust-original-campaign-v12"
LABEL = "phase2-v19-rust-buffer-shape-root-provenance-original-p0-v12"
BUILD_LABEL = "phase2-v19-rust-buffer-shape-root-provenance"
GOAL = ("GOAL.md", "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62", 3756, 31364044)
P0 = (
    ("tools/verify_owned_p0_completeness_v4.py", "8c73af8913f54e2398e707dc4a44c173ca53e20c1161b84160d841ce2ff7760d", 29094, 428927),
    ("oracle/phase1/P0-COMPLETENESS-V4.md", "4a390db825fed994733390be8961a0f709d7f1f22195535e581e71cdea8111f2", 4261, 524712),
    ("oracle/phase1/p0-completeness-v4.json", "aab7a301f646755cec9956904cd6f97498d8293da454a925bf1f75cdfc85b3b1", 34875, 524713),
)
HISTORICAL_PRODUCER_V4 = (
    ("tools/run_owned_six_family_original_p0_producer_v4.py", "e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8", 230782, 431710),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V4.md", "e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5", 5981, 524782),
    ("oracle/phase2/six-family-p0-producer-v4.json", "c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5", 30867, 524783),
)
PRODUCER = (
    ("tools/run_owned_six_family_original_p0_producer_v5.py", "b4886f424945d3a182a90737fd965fbc4a6e82cafa1c9ee456a9ea405ee18538", 102286, 431370),
    ("oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md", "9cfd1fc189d555a596b84b6073471554dab6bd67c1b343c66b744f4dc7b053a4", 5270, 524884),
    ("oracle/phase2/six-family-p0-producer-v5.json", "c751b8882fa331b4850271e68a1b43f965b5ddcb77c7ad0d0b4d3dec8ba79b53", 21036, 524885),
)
V11 = (
    ("tools/run_owned_repaired_rust_original_campaign_v11.py", "27bf88358d5a45a5b487680e70f5fa5b5192a05f053f33f6ddb651c972c94f2d", 310760, 430525),
    ("oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V11.md", "a3a5b35701aa6b149ff0b4fbebb9f6722dd08436d2f7e4f600f3db12c8c6ac2b", 7353, 524748),
    ("oracle/phase2/repaired-rust-original-campaign-v11.json", "e6cd2028e36d8ddac0937e6735132bf474327f2ff04855d44e6aa71f5f5c0f96", 16783, 524749),
)
BUILD = (
    ("tools/reproduce_owned_rust_buffer_shape_source_build_v19.py", "650b33a10d253e09d48a423d12c8a1bb8180af4c4e96222aa13e72c75427bb5c", 88532, 430955),
    ("oracle/phase2/RUST-BUFFER-SHAPE-SOURCE-BUILD-V19.md", "4cdc322b2a516b28bf771440202efaca77074f7c8cd31c25692dc6ffc81797b5", 5808, 524752),
    ("oracle/phase2/rust-buffer-shape-source-build-v19.json", "78e31d32cd17e100613ea98cecec4051ca2f6563b0d3b198c66f69501171ac46", 14975, 524753),
)
BUILD_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-publication-receipt.json",
    "27fbe6ec2077b05c1f8fe0b340f962d8d8f637b893c57d381108c9ed606cd0dc", 3486, 524773,
)
ROOT_RECEIPT = (
    "oracle/phase2/evidence/native-source-build-v19-rust-phase2-v19-rust-buffer-shape-root-provenance-root-provenance-receipt.json",
    "de13207235055665c605cce1b88a8f2127f291b84a5954119a033c7f4e9a3c99", 4367, 524774,
)
GUARD = (
    ("tools/verify_owned_candidate_runtime_independence_v2.py", "f693b1576b63ae5ebe45663801834c05e7d03671a5d6f2b4beb1b62034d37c0a", 67097, 431371),
    ("oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md", "2f11a29e08b6616d053269bc99e5283b5548ce88c74b384e1c5979c2e1d2288c", 4437, 524886),
    ("oracle/phase2/candidate-runtime-independence-v2.json", "813bbab0898d5a65a6b43533f7bfa024c4c215609c4f9fa6eb0f4cbe2791f473", 7671, 524887),
)
GRAPH = (
    ("tools/render_candidate_current_overview_v76.py", "ac825ba68a8a8c2845569403a9b348db8d5cf1009a3d6cf8df0db1e322b53a1c", 42970, 431408),
    ("docs/evidence/candidate-current-overview-v76.inputs.json", "3e945e54576468e9e53cc757b1f0bb64064571e3862757666152a4f1b0963e9f", 1188201, 431409),
    ("docs/evidence/candidate-current-overview-v76.json", "a7a09e9ccfaadeffc4a49ffdb229835658b4845dfd2fc8081edd1921997d58b1", 3542645, 431410),
    ("docs/evidence/candidate-current-overview-v76.svg", "4aabb86916a20c9dc000bd2aad5fd99b7e339f5be8f2fb44f131dd2254130f40", 4886, 431411),
)
SUITES = (
    ("original_bounded_v5", 151), ("public_v3", 864),
    ("scanner_v3", 1024), ("buffer_v3", 768), ("managed_v1", 1024),
    ("scanner_verbose_v1", 2854), ("public_types_v1", 6912),
    ("substitution_v2", 5120), ("shape_v2", 10240),
    ("public_surface_v19", 1376), ("subinterpreter_v2", 128),
    ("pep688_v4", 264), ("threaded_pattern_v1", 512),
)
PRIVATE_WAIVERS = (
    "DebugTests.test_debug_flag",
    "DebugTests.test_atomic_group",
    "DebugTests.test_possesive_repeat_one",
    "DebugTests.test_possesive_repeat",
    "ImplementationTest.test_immutable",
    "ImplementationTest.test_overlap_table",
    "ImplementationTest.test_signedness",
    "ImplementationTest.test_disallow_instantiation",
    "ImplementationTest.test_deprecated_modules",
    "ImplementationTest.test_case_helpers",
    "ImplementationTest.test_dealloc",
    "ImplementationTest.test_repeat_minmax_overflow_maxrepeat",
    "ImplementationTest.test_sre_template_invalid_group_index",
)
ROLE_ORDER = ("bridge_source", "adapter", "engine", "bridge")
REFERENCE_SHA = "6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2"
REFERENCE_CACHE_SHA = "587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad"
ENGINE_SHA = "5e79f92b10d47f73919796af2349e44e7d16eceb515cc07571d0beaaec4a405f"
BRIDGE_SHA = "7127b1b5d6e50947e34f39e6c33ff76e71a9f753473c6d5eac0f1bdf6b0e66d4"
ENGINE_BYTES = 658344
BRIDGE_BYTES = 148832
ROOT_DEVICE = 2049
ROOT_INODE = 11673243
ROOT_PATH = "/tmp/rebar-phase2-native-build-v9-rust-9m_y1apm"
WORKER_COUNT = 13
CASE_COUNT = 31237
PRIVATE_WAIVER_COUNT = 13
EVIDENCE_FLOOR = 252
HISTORY_FLOOR = 257
RECOVERY_PRIVATE_PREFIX = "rebar-phase2-repaired-rust-original-campaign-v12-"
RECOVERY_ROOT = (
    "/tmp/" + RECOVERY_PRIVATE_PREFIX
    + "phase2-v19-rust-buffer-shape-root-provenance-original-p0"
)
BUILD_ARCHIVE_SHA = "c4e3971fc207af50081d920a98d29dc06b5bdce07c5e1fb19e3e6fdf99a1c1bb"
BUILD_ARCHIVE_BYTES = 108250
BUILD_ARCHIVE_INODE = 524772
BUILD_PLAIN_SHA = "baa70a2c3ccb2c591d125f6b3df7ce3b5173c06a21650a9ecf42fef1b99e75a1"
BUILD_PLAIN_BYTES = 760068
CORRECTED_ADAPTER_SHA = "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
CORRECTED_ADAPTER_BYTES = 31934



class CampaignError(Exception):
    """A frozen owner, source mode, or separately pinned authority failed."""


def need(condition: object, message: str) -> None:
    if not condition:
        raise CampaignError(message)


def sha_pin(value: object, label: str) -> str:
    need(isinstance(value, str) and len(value) == 64
         and all(char in "0123456789abcdef" for char in value),
         "require exact lowercase SHA-256 for " + label)
    assert isinstance(value, str)
    return value


def owner_read(owner: tuple, *, max_bytes: int = 4 * 1024 * 1024) -> bytes:
    relative, expected, expected_size, expected_inode = owner
    need(isinstance(relative, str) and relative and not relative.startswith("/")
         and ".." not in relative.split("/")
         and not relative.endswith((".gz", ".so")),
         "reject archive, native output, or unsafe source-only owner")
    sha_pin(expected, relative)
    need(isinstance(expected_size, int) and 0 < expected_size <= max_bytes,
         "reject oversized frozen owner: " + relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(os.path.join(ROOT, relative), flags)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_dev == 2064
             and before.st_ino == expected_inode
             and before.st_size == expected_size and before.st_nlink == 1,
             "reject substituted frozen owner: " + relative)
        chunks: list[bytes] = []
        remaining = expected_size + 1
        while remaining:
            chunk = os.read(fd, min(remaining, 262144))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(fd)
        need(len(raw) == expected_size
             and hashlib.sha256(raw).hexdigest() == expected
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject changed or incorrectly hashed frozen owner: " + relative)
        return raw
    finally:
        os.close(fd)


def self_owner(relative: str, digest: str) -> tuple:
    sha_pin(digest, relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(os.path.join(ROOT, relative), flags)
    try:
        info = os.fstat(fd)
        need(stat.S_ISREG(info.st_mode) and info.st_dev == 2064
             and info.st_nlink == 1 and 0 < info.st_size <= 512 * 1024,
             "reject substituted V12 owner: " + relative)
        return relative, digest, info.st_size, info.st_ino
    finally:
        os.close(fd)


def load_guard() -> types.ModuleType:
    need("re" not in sys.modules and "_sre" not in sys.modules
         and "regex" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "require sterile bootstrap before authenticating the runtime guard")
    raw = owner_read(GUARD[0])
    module = types.ModuleType("_rebar_frozen_candidate_runtime_guard_v2_for_v12")
    module.__file__ = os.path.join(ROOT, GUARD[0][0])
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    need(module.SELF == GUARD[0][0]
         and module.PROTOCOL == GUARD[1][0]
         and module.CONTRACT == GUARD[2][0]
         and getattr(module, "MAXGROUPS", None) == 1073741823
         and callable(getattr(module, "child_bootstrap_source", None))
         and callable(getattr(module.RuntimePolicy, "prepare_family", None))
         and callable(getattr(module.RuntimePolicy, "bind_selected", None))
         and callable(getattr(module.RuntimePolicy, "begin_subinterpreters", None))
         and callable(getattr(module.RuntimePolicy, "register_child_bootstrap", None))
         and callable(getattr(module.RuntimePolicy, "confirm_child_guard", None))
         and callable(getattr(module.RuntimePolicy, "end_subinterpreters", None))
         and callable(getattr(module.RuntimePolicy, "begin_fork_case", None))
         and callable(getattr(module.RuntimePolicy, "end_fork_case", None))
         and callable(getattr(module.RuntimePolicy, "begin_correctness_clock", None))
         and callable(getattr(module.RuntimePolicy, "end_correctness_clock", None))
         and module.RuntimePolicy.install is module.BASE.RuntimePolicy.install,
         "reject a renamed or substituted first-party runtime guard")
    return module


def parse_document(guard: types.ModuleType, raw: bytes, label: str) -> dict:
    result = guard.JsonReader(raw).parse()
    need(isinstance(result, dict), "require JSON object for " + label)
    return result


def runtime_check() -> None:
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode
         and sys.executable == PYTHON
         and sys.version_info[:3] == (3, 14, 6),
         "run the exact isolated, site-free, bytecode-free CPython 3.14.6 oracle")


def authenticate_root_receipts(guard: types.ModuleType) -> tuple[dict, dict]:
    build = parse_document(guard, owner_read(BUILD_RECEIPT), "V19 build receipt")
    root = parse_document(guard, owner_read(ROOT_RECEIPT), "V19 root receipt")
    need(build.get("schema")
         == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-durable-publication-receipt"
         and build.get("status") == "PASS"
         and build.get("family") == "rust"
         and build.get("label") == BUILD_LABEL
         and build.get("source_sha256") == BUILD[0][1]
         and build.get("protocol_sha256") == BUILD[1][1]
         and build.get("contract_sha256") == BUILD[2][1]
         and build.get("actual_compiler_process_count") == 28
         and build.get("expected_actual_compiler_process_count") == 28
         and build.get("combined_bridge_sha256")
         == "afc6bb5f04c9d69c938fbae060ca83e0c774c8eda26e0416caadd9550634f740"
         and build.get("combined_bridge_bytes") == 179961
         and build.get("corrected_public_adapter_sha256")
         == "d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e"
         and build.get("corrected_public_adapter_bytes") == 31934,
         "require the actual, corrected, 28-process V19 Rust build receipt")
    need(root.get("schema")
         == "rebar-phase2-owned-rust-buffer-shape-source-build-v19-durable-root-provenance-receipt"
         and root.get("status") == "PASS"
         and root.get("family") == "rust"
         and root.get("label") == BUILD_LABEL
         and root.get("source_sha256") == BUILD[0][1]
         and root.get("protocol_sha256") == BUILD[1][1]
         and root.get("contract_sha256") == BUILD[2][1]
         and root.get("canonical_build_receipt_relative") == BUILD_RECEIPT[0]
         and root.get("canonical_build_receipt_sha256") == BUILD_RECEIPT[1]
         and root.get("canonical_build_receipt_bytes") == BUILD_RECEIPT[2]
         and root.get("canonical_build_receipt_device") == 2064
         and root.get("canonical_build_receipt_inode") == BUILD_RECEIPT[3]
         and root.get("actual_compiler_process_count") == 28
         and root.get("expected_compiler_process_count") == 28
         and root.get("actual_source_phase_count") == 2
         and root.get("historical_archives_opened") == 0
         and root.get("native_libraries_loaded") == 0
         and root.get("candidate_workers_started") == 0
         and root.get("hidden_cases_read") == 0
         and root.get("clock_samples") == 0,
         "require the actual V19 callback-bound, no-archive root receipt")
    info = root.get("root")
    need(isinstance(info, dict)
         and info.get("path") == ROOT_PATH
         and info.get("device") == ROOT_DEVICE
         and info.get("inode") == ROOT_INODE
         and info.get("phase_count") == 2
         and info.get("directory_scanned") is False,
         "authenticate real V19 root provenance from receipt bytes only")
    phases = info.get("phases")
    need(isinstance(phases, list) and len(phases) == 2,
         "require both callback-attested V19 source-build phases")
    for index, phase_name in enumerate(("reference-a", "reference-b")):
        phase = phases[index]
        need(isinstance(phase, dict) and phase.get("name") == phase_name
             and phase.get("absolute_path") == ROOT_PATH + "/" + phase_name
             and phase.get("device") == ROOT_DEVICE,
             "reject mismatched callback-attested phase " + phase_name)
        outputs = phase.get("native_outputs")
        need(isinstance(outputs, list) and len(outputs) == 2,
             "require exactly two attested Rust outputs per phase")
        engine, bridge = outputs
        need(isinstance(engine, dict) and engine.get("role") == "engine"
             and engine.get("file_name") == "_rust_engine.so"
             and engine.get("sha256") == ENGINE_SHA
             and engine.get("bytes") == ENGINE_BYTES
             and engine.get("device") == ROOT_DEVICE
             and engine.get("native_loaded") is False,
             "reject substituted callback-attested Rust engine")
        need(isinstance(bridge, dict) and bridge.get("role") == "bridge"
             and bridge.get("file_name")
             == "_rust_bridge.cpython-314-x86_64-linux-gnu.so"
             and bridge.get("sha256") == BRIDGE_SHA
             and bridge.get("bytes") == BRIDGE_BYTES
             and bridge.get("device") == ROOT_DEVICE
             and bridge.get("native_loaded") is False,
             "reject substituted callback-attested Rust bridge")
    return build, root


def verify_frozen_context(source_sha: str, protocol_sha: str,
                          contract_sha: str | None,
                          *, rendering: bool = False) -> dict:
    runtime_check()
    guard = load_guard()
    source_raw = owner_read(self_owner(SOURCE, source_sha))
    owner_read(self_owner(PROTOCOL, protocol_sha))
    if not rendering:
        need(contract_sha is not None, "pin the exact V12 machine contract")
        owner_read(self_owner(CONTRACT, contract_sha))
    owner_read(GOAL)
    for owner in (P0 + HISTORICAL_PRODUCER_V4 + PRODUCER
                  + V11 + BUILD + GUARD[1:] + GRAPH):
        owner_read(owner)
    p0 = parse_document(guard, owner_read(P0[2]), "P0 V4 machine contract")
    need(p0.get("schema") == "rebar-cpython-re-p0-completeness-v4"
         and p0.get("status") == "PASS" and p0.get("version") == 4
         and p0.get("original_case_execution_denominator") == CASE_COUNT
         and p0.get("original_suite_count") == WORKER_COUNT
         and p0.get("original_named_private_waiver_count")
         == PRIVATE_WAIVER_COUNT
         and p0.get("original_obligation_count") == 73
         and p0.get("qualified_candidate_count") == 0,
         "require actual passing reference readiness, not candidate qualification")
    producer = parse_document(guard, owner_read(PRODUCER[2]),
                              "guard-clean original V5 producer contract")
    need(producer.get("schema")
         == "rebar-owned-six-family-original-p0-producer-v5-source-freeze"
         and producer.get("version") == 5
         and producer.get("suite_count") == WORKER_COUNT
         and producer.get("case_execution_denominator") == CASE_COUNT
         and producer.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and producer.get("named_private_waivers") == list(PRIVATE_WAIVERS)
         and producer.get("family_count") == 6
         and producer.get("supplemental_case_count") == 8244
         and producer.get("supplemental_cases_counted_in_original_denominator")
         is False
         and producer.get("qualified_candidate_count") == 0
         and producer.get("actual_candidate_imports") == 0
         and producer.get("actual_candidate_workers") == 0
         and producer.get("runtime_non_delegation") == "NOT ESTABLISHED",
         "require the complete frozen, guarded thirteen-suite V5 producer")
    rows = producer.get("suites")
    need(isinstance(rows, list)
         and [(row.get("id"), row.get("case_execution_count")) for row in rows]
         == list(SUITES)
         and len(PRIVATE_WAIVERS) == PRIVATE_WAIVER_COUNT
         and len(set(PRIVATE_WAIVERS)) == PRIVATE_WAIVER_COUNT
         and sum(count for _, count in SUITES) == CASE_COUNT
         and rows[0].get("reference_records_sha256")
         == "b6f23860b340ff326347bdd103505c04bb2b84c21fc874758bd278bc90390276"
         and rows[6].get("reference_records_sha256") == REFERENCE_SHA,
         "reject changed original suite order, case vectors, or denominator")
    bootstrap = producer.get("runtime_bootstrap")
    need(isinstance(bootstrap, dict)
         and bootstrap.get("python_flags") == ["-I", "-B", "-S"]
         and bootstrap.get("candidate_module_imported_before_guard") is False
         and bootstrap.get("guard_installed_before_candidate_import") is True
         and bootstrap.get("selected_re_alias_must_equal_candidate") is True
         and bootstrap.get("stdlib_re_forbidden") is True
         and bootstrap.get("stdlib_sre_forbidden") is True
         and bootstrap.get("external_regex_packages_forbidden") is True
         and bootstrap.get("cross_candidate_delegation_forbidden") is True
         and bootstrap.get("fallback_permitted") is False
         and bootstrap.get("candidate_subprocesses_permitted") is False
         and bootstrap.get("external_prepared_locale_fixture_required") is True
         and bootstrap.get("data_only_re_constants_maxgroups") == 1073741823,
         "require complete sterile guard-first no-delegation V5 candidate rules")
    producer_tree = ast.parse(owner_read(PRODUCER[0]), filename=PRODUCER[0][0])
    producer_routes = {
        node.name for node in producer_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    need({"family_spec", "suite_spec", "exact_native_owners",
          "observe_original_upstream", "observe_direct_suite",
          "observe_subinterpreters", "active_runtime_policy",
          "active_guard_child_bootstrap"} <= producer_routes,
         "freeze all independently executable V5 original-case observers")
    legacy_raw = owner_read(V11[0])
    legacy_tree = ast.parse(legacy_raw, filename=V11[0][0])
    legacy_routes = {
        node.name for node in legacy_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    need({"run_original_worker", "run_campaign", "recover_originals",
          "configure_historical_helpers", "execute_one_worker",
          "authenticate_private_build", "preserve_actual_campaign"}
         <= legacy_routes,
         "authenticate real unchanged original workers and four-role controller")
    current_tree = ast.parse(source_raw, filename=SOURCE)
    current_routes = next(
        (node for node in current_tree.body
         if isinstance(node, ast.FunctionDef)
         and node.name == "actual_operation"),
        None,
    )
    need(current_routes is not None, "freeze the executable V12 dispatcher")
    dispatch = {
        node.func.attr for node in ast.walk(current_routes)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "legacy"
    }
    need({"run_original_worker", "run_campaign", "recover_originals"}
         <= dispatch,
         "prove all three actual operations invoke genuine frozen machinery")
    graph = parse_document(guard, owner_read(GRAPH[2]), "current V76 graph")
    need(graph.get("schema") == "rebar-candidate-current-overview-v76-summary"
         and graph.get("status") == "PASS" and graph.get("version") == 76
         and graph.get("full_case_denominator") == CASE_COUNT
         and graph.get("suite_count") == WORKER_COUNT
         and graph.get("private_waiver_count") == PRIVATE_WAIVER_COUNT
         and graph.get("authenticated_evidence_owner_lower_bound") == EVIDENCE_FLOOR
         and graph.get("authenticated_history_reference_lower_bound") == HISTORY_FLOOR
         and graph.get("qualified_candidate_count") == 0
         and graph.get("actual_rust_semantic_mismatch_count") == 1440
         and graph.get("actual_rust_verified_passing_case_count") == 14853
         and graph.get("actual_c_semantic_mismatch_count") == 1230
         and graph.get("actual_c_verified_passing_case_count") == 7325
         and graph.get("actual_rust_candidate_workers") == 13
         and graph.get("actual_rust_attempted_suite_count") == 13
         and graph.get("actual_rust_completed_suite_count") == 13
         and graph.get("actual_candidate_workers_started_by_graph") == 0
         and graph.get("actual_compiler_processes_started_by_graph") == 0
         and graph.get("actual_native_libraries_loaded_by_graph") == 0
         and graph.get("actual_hidden_cases_read_by_graph") == 0
         and graph.get("actual_clock_samples_by_graph") == 0
         and graph.get("timing_trials_run") == 0
         and graph.get("final_holdout_opened") is False
         and graph.get("runtime_no_delegation") == "NOT ESTABLISHED"
         and graph.get("performance") == "NOT MEASURED"
         and graph.get("winner_selected") is False,
         "preserve the actual V76 mismatches, denominators, and qualification")
    graph_v5 = graph.get("clean_original_producer_v5_source_freeze")
    need(isinstance(graph_v5, dict)
         and graph_v5.get("schema")
         == "rebar-candidate-current-overview-v76-clean-original-six-family-producer-v5"
         and graph_v5.get("version") == 5
         and graph_v5.get("status")
         == "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED"
         and graph.get("clean_original_producer_v5_original_case_count")
         == CASE_COUNT
         and graph.get("clean_original_producer_v5_original_suite_count")
         == WORKER_COUNT
         and graph.get("clean_original_producer_v5_named_private_waiver_count")
         == PRIVATE_WAIVER_COUNT
         and graph.get("clean_original_producer_v5_original_obligation_count") == 73
         and graph.get("clean_original_producer_v5_separate_supplemental_case_count")
         == 8244
         and graph.get("clean_original_producer_v5_family_count") == 6
         and graph.get("clean_original_producer_v5_actual_candidate_imports") == 0
         and graph.get("clean_original_producer_v5_actual_candidate_workers") == 0
         and graph.get("clean_original_producer_v5_actual_child_interpreters") == 0
         and graph.get("clean_original_producer_v5_candidate_matching") == "NOT RUN"
         and graph.get("clean_original_producer_v5_candidate_qualified") is False
         and graph.get("clean_original_producer_v5_runtime_non_delegation")
         == "NOT ESTABLISHED",
         "bind the genuinely current graph to all guard-clean V5 obligations")
    graph_guard = graph.get("candidate_runtime_independence_v2_source_freeze")
    need(isinstance(graph_guard, dict)
         and graph_guard.get("schema")
         == "rebar-candidate-current-overview-v75-candidate-runtime-independence-source-v2"
         and graph_guard.get("version") == 2
         and graph_guard.get("status")
         == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
         and graph.get("candidate_runtime_independence_v2_source_owner_count") == 3
         and graph.get("candidate_runtime_independence_v2_family_bridge_count") == 6
         and graph.get("candidate_runtime_independence_v2_candidate_qualified")
         is False
         and graph.get("candidate_runtime_independence_v2_candidate_workers_started")
         == 0
         and graph.get("candidate_runtime_independence_v2_native_libraries_loaded")
         == 0
         and graph.get("candidate_runtime_independence_v2_runtime_audit")
         == "NOT RUN"
         and graph.get("candidate_runtime_independence_v2_runtime_no_delegation")
         == "NOT ESTABLISHED",
         "bind the genuinely current graph to the actual unexecuted V2 guard")
    for feature, label, owners in (
        (graph_v5, "guard-clean V5 producer", PRODUCER),
        (graph_guard, "operational V2 runtime guard", GUARD),
    ):
        published_owners = feature.get("owners")
        need(isinstance(published_owners, dict),
             "reject omitted current graph evidence owners: " + label)
        for role, expected in zip(("source", "protocol", "contract"), owners,
                                  strict=True):
            identity = published_owners.get(role)
            need(isinstance(identity, dict)
                 and identity.get("path") == expected[0]
                 and identity.get("sha256") == expected[1]
                 and identity.get("bytes") == expected[2]
                 and identity.get("device") == 2064
                 and identity.get("inode") == expected[3]
                 and identity.get("mode") == "0600"
                 and identity.get("nlink") == 1,
                 "reject stale current graph owner: " + label + " " + role)
    build, root = authenticate_root_receipts(guard)
    guard_contract = parse_document(guard, owner_read(GUARD[2]),
                                    "published runtime guard contract")
    need(guard_contract.get("schema")
         == "rebar-owned-candidate-runtime-independence-v2-source-freeze"
         and guard_contract.get("version") == 2
         and guard_contract.get("status")
         == "SOURCE FROZEN; RUNTIME GUARD NOT RUN ON A CANDIDATE"
         and guard_contract.get("runtime_non_delegation") == "NOT ESTABLISHED"
         and guard_contract.get("qualified_candidate_count") == 0,
         "never report a merely published runtime guard as candidate independence")
    for key, owner in (("source", GUARD[0]), ("protocol", GUARD[1])):
        identity = guard_contract.get(key)
        need(isinstance(identity, dict)
             and identity.get("path") == owner[0]
             and identity.get("sha256") == owner[1]
             and identity.get("bytes") == owner[2]
             and identity.get("device") == 2064
             and identity.get("inode") == owner[3]
             and identity.get("mode") == "0600"
             and identity.get("nlink") == 1,
             "reject an invented operational guard owner: " + key)
    readiness = guard_contract.get("phase1_v4_readiness")
    need(isinstance(readiness, dict)
         and readiness.get("status") == "PASS"
         and readiness.get("contract_sha256") == P0[2][1]
         and readiness.get("original_case_execution_denominator") == CASE_COUNT
         and readiness.get("original_suite_count") == WORKER_COUNT
         and readiness.get("original_obligation_count") == 73
         and readiness.get("named_private_waiver_count") == PRIVATE_WAIVER_COUNT
         and readiness.get("separate_supplemental_case_count") == 8244,
         "preserve complete P0 readiness and separately counted supplemental cases")
    family_policy = guard_contract.get("family_bridge_policy")
    need(isinstance(family_policy, dict)
         and family_policy.get("rust") == {
             "candidate_module": "candidates.rust_candidate",
             "owned_bridge_module": "candidates._rust_bridge",
         },
         "allow exactly the genuine independent Rust adapter and own bridge")
    native = guard_contract.get("native_provenance")
    need(isinstance(native, dict)
         and native.get("build_version") == 19
         and native.get("family") == "rust"
         and native.get("actual_compiler_process_count") == 28
         and native.get("attested_engine_sha256") == ENGINE_SHA
         and native.get("attested_engine_bytes") == ENGINE_BYTES
         and native.get("attested_bridge_sha256") == BRIDGE_SHA
         and native.get("attested_bridge_bytes") == BRIDGE_BYTES
         and native.get("root_device") == ROOT_DEVICE
         and native.get("root_inode") == ROOT_INODE
         and native.get("source_mode_native_libraries_loaded") == 0
         and native.get("source_mode_native_root_opens") == 0
         and native.get("candidate_matching") == "NOT RUN",
         "authenticate V19 runtime-native policy without opening any native")
    nested = guard_contract.get("subinterpreter_bootstrap")
    need(isinstance(nested, dict)
         and nested.get("suite") == "subinterpreter_v2"
         and nested.get("original_case_count") == 128
         and nested.get("expected_case_interpreter_exec_calls") == 394
         and nested.get("expected_interpreters_created") == 11
         and nested.get("expected_interpreters_destroyed") == 11
         and nested.get("actual_case_interpreter_exec_calls") == 0
         and nested.get("actual_interpreters_created") == 0
         and nested.get("actual_child_guards_installed") == 0
         and nested.get("require_child_guard_before_candidate_import") is True
         and nested.get("unrestricted_creation") is False,
         "retain real child bootstrap obligations without claiming execution")
    isolation = guard_contract.get("runtime_isolation_policy")
    need(isinstance(isolation, dict)
         and isolation.get("bootstrap")
         == "CPython -I -B -S; audit hook before candidate import"
         and isolation.get("candidate_alias")
         == "sys.modules['re'] is the attested candidate"
         and isolation.get("guard_installed_before_candidate_import") is True
         and all(isolation.get(key) == "FORBIDDEN" for key in (
             "stdlib_re_engine", "stdlib_sre_engine", "external_regex_package",
             "cross_candidate_engine", "matching_fallback",
         )),
         "reject stdlib, external, cross-family, or fallback matcher delegation")
    effects = guard_contract.get("source_only_effects")
    need(isinstance(effects, dict) and bool(effects)
         and all(type(value) is int and value == 0 for value in effects.values()),
         "require genuinely zero operational guard source-mode effects")
    result = {
        "schema": SCHEMA + "-frozen-context",
        "status": "PASS",
        "version": 12,
        "source_sha256": source_sha,
        "protocol_sha256": protocol_sha,
        "contract_sha256": contract_sha,
        "goal_sha256": GOAL[1],
        "cpython_version": "3.14.6",
        "cpython_executable": PYTHON,
        "cpython_executable_sha256": PYTHON_SHA256,
        "phase1_v4_reference_readiness": "PASS",
        "phase2_candidate_qualification": "BLOCKED",
        "qualified_candidate_count": 0,
        "corrected_original_producer_version": 5,
        "historical_original_v4_producer_source_sha256":
            HISTORICAL_PRODUCER_V4[0][1],
        "corrected_original_producer_source_sha256": PRODUCER[0][1],
        "corrected_original_producer_protocol_sha256": PRODUCER[1][1],
        "corrected_original_producer_contract_sha256": PRODUCER[2][1],
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "named_private_waivers": list(PRIVATE_WAIVERS),
        "supplemental_case_count": 8244,
        "supplemental_cases_counted_in_original_denominator": False,
        "suites": [{"id": name, "case_execution_count": count}
                   for name, count in SUITES],
        "reference_records_sha256": REFERENCE_SHA,
        "reference_cache_records_sha256": REFERENCE_CACHE_SHA,
        "reference_worker_process_ids": [81, 82],
        "source_frozen_worker_implementation": V11[0][0],
        "source_frozen_worker_implementation_sha256": V11[0][1],
        "legacy_v11_original_campaign": "BLOCKED; V18-ONLY",
        "worker_implementation_reuse": "AUTHENTICATED FIRST-PARTY V11 IN MEMORY ONLY",
        "actual_controller_dispatch": "AUTHENTICATED V11 run_campaign",
        "actual_worker_dispatch": "AUTHENTICATED V11 run_original_worker",
        "actual_recovery_dispatch": "AUTHENTICATED V11 recover_originals",
        "actual_worker_bootstrap": "CPython -I -B -S; audit hook before candidate import",
        "planned_actual_original_candidate_worker_count": WORKER_COUNT,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_compiler_processes_started": 0,
        "actual_private_build_root_opens": 0,
        "actual_private_build_root_stats": 0,
        "actual_build_archive_opens": 0,
        "actual_build_archive_inflations": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "runtime_guard_source_sha256": GUARD[0][1],
        "runtime_guard_protocol_sha256": GUARD[1][1],
        "runtime_guard_contract_sha256": GUARD[2][1],
        "runtime_guard_installation": "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "actual_v19_build_source_sha256": BUILD[0][1],
        "actual_v19_build_protocol_sha256": BUILD[1][1],
        "actual_v19_build_contract_sha256": BUILD[2][1],
        "actual_v19_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_v19_root_receipt_sha256": ROOT_RECEIPT[1],
        "actual_v19_build_archive_metadata_sha256": BUILD_ARCHIVE_SHA,
        "actual_v19_build_archive_metadata_bytes": BUILD_ARCHIVE_BYTES,
        "actual_v19_build_label": build["label"],
        "actual_v19_compiler_process_count": 28,
        "actual_v19_source_build_phase_count": 2,
        "actual_v19_private_build_root_provenance": "AUTHENTICATED RECEIPT ONLY; NOT OPENED",
        "actual_v19_private_build_root": root["root"]["path"],
        "actual_v19_private_build_root_device": root["root"]["device"],
        "actual_v19_private_build_root_inode": root["root"]["inode"],
        "actual_v19_native_engine_sha256": ENGINE_SHA,
        "actual_v19_native_engine_bytes": ENGINE_BYTES,
        "actual_v19_native_bridge_sha256": BRIDGE_SHA,
        "actual_v19_native_bridge_bytes": BRIDGE_BYTES,
        "recovery_role_order": list(ROLE_ORDER),
        "recovery_restoration_order": list(reversed(ROLE_ORDER)),
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v12.lock",
        "frozen_graph_version": 76,
        "frozen_graph_source_sha256": GRAPH[0][1],
        "frozen_graph_inputs_sha256": GRAPH[1][1],
        "frozen_graph_summary_sha256": GRAPH[2][1],
        "frozen_graph_svg_sha256": GRAPH[3][1],
        "current_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "current_history_reference_lower_bound": HISTORY_FLOOR,
        "prospective_evidence_owner_lower_bound": EVIDENCE_FLOOR + 3,
        "prospective_history_reference_lower_bound": HISTORY_FLOOR + 3,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }
    if not rendering:
        machine = parse_document(guard, owner_read(self_owner(CONTRACT, contract_sha)),
                                 "V12 frozen machine contract")
        need(machine == contract_document(source_sha, protocol_sha, result),
             "require complete canonical V12 contract, not a weakened context")
    return result


def contract_document(source_sha: str, protocol_sha: str, context: dict) -> dict:
    return {
        "schema": SCHEMA + "-recoverable-source-freeze",
        "version": 12,
        "status": "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        "source_sha256": source_sha,
        "protocol_sha256": protocol_sha,
        "goal_sha256": GOAL[1],
        "cpython_version": "3.14.6",
        "cpython_executable": PYTHON,
        "cpython_executable_sha256": PYTHON_SHA256,
        "phase1_v4_reference_readiness": "PASS",
        "phase2_candidate_qualification": "BLOCKED",
        "qualified_candidate_count": 0,
        "corrected_original_producer_version": 5,
        "historical_original_v4_producer_source_sha256":
            HISTORICAL_PRODUCER_V4[0][1],
        "corrected_original_producer_source_sha256": PRODUCER[0][1],
        "corrected_original_producer_protocol_sha256": PRODUCER[1][1],
        "corrected_original_producer_contract_sha256": PRODUCER[2][1],
        "suite_count": WORKER_COUNT,
        "case_execution_denominator": CASE_COUNT,
        "private_waiver_count": PRIVATE_WAIVER_COUNT,
        "named_private_waivers": list(PRIVATE_WAIVERS),
        "supplemental_case_count": 8244,
        "supplemental_cases_counted_in_original_denominator": False,
        "suites": context["suites"],
        "reference_records_sha256": REFERENCE_SHA,
        "reference_cache_records_sha256": REFERENCE_CACHE_SHA,
        "reference_worker_process_ids": [81, 82],
        "frozen_worker_implementation_source": V11[0][0],
        "frozen_worker_implementation_source_sha256": V11[0][1],
        "frozen_worker_implementation_protocol_sha256": V11[1][1],
        "frozen_worker_implementation_contract_sha256": V11[2][1],
        "legacy_v11_original_campaign": "BLOCKED; V18-ONLY",
        "worker_implementation_reuse": "AUTHENTICATED FIRST-PARTY V11 IN MEMORY ONLY",
        "actual_controller_dispatch": "AUTHENTICATED V11 run_campaign",
        "actual_worker_dispatch": "AUTHENTICATED V11 run_original_worker",
        "actual_recovery_dispatch": "AUTHENTICATED V11 recover_originals",
        "actual_worker_bootstrap": "CPython -I -B -S; audit hook before candidate import",
        "planned_actual_original_candidate_worker_count": WORKER_COUNT,
        "actual_candidate_workers_started": 0,
        "actual_candidate_imports": 0,
        "actual_native_libraries_loaded": 0,
        "actual_compiler_processes_started": 0,
        "actual_private_build_root_opens": 0,
        "actual_private_build_root_stats": 0,
        "actual_build_archive_opens": 0,
        "actual_build_archive_inflations": 0,
        "actual_hidden_cases_read": 0,
        "actual_clock_samples": 0,
        "runtime_guard_source_sha256": GUARD[0][1],
        "runtime_guard_protocol_sha256": GUARD[1][1],
        "runtime_guard_contract_sha256": GUARD[2][1],
        "runtime_guard_installation": "REQUIRED BEFORE ANY ACTUAL CANDIDATE IMPORT",
        "runtime_non_delegation": "NOT ESTABLISHED",
        "actual_v19_build_source_sha256": BUILD[0][1],
        "actual_v19_build_protocol_sha256": BUILD[1][1],
        "actual_v19_build_contract_sha256": BUILD[2][1],
        "actual_v19_build_receipt_sha256": BUILD_RECEIPT[1],
        "actual_v19_root_receipt_sha256": ROOT_RECEIPT[1],
        "actual_v19_build_archive_metadata_sha256": BUILD_ARCHIVE_SHA,
        "actual_v19_build_archive_metadata_bytes": BUILD_ARCHIVE_BYTES,
        "actual_v19_build_label": BUILD_LABEL,
        "actual_v19_compiler_process_count": 28,
        "actual_v19_source_build_phase_count": 2,
        "actual_v19_private_build_root_provenance": "AUTHENTICATED RECEIPT ONLY; NOT OPENED",
        "actual_v19_private_build_root": ROOT_PATH,
        "actual_v19_private_build_root_device": ROOT_DEVICE,
        "actual_v19_private_build_root_inode": ROOT_INODE,
        "actual_v19_native_engine_sha256": ENGINE_SHA,
        "actual_v19_native_engine_bytes": ENGINE_BYTES,
        "actual_v19_native_bridge_sha256": BRIDGE_SHA,
        "actual_v19_native_bridge_bytes": BRIDGE_BYTES,
        "recovery_role_order": list(ROLE_ORDER),
        "recovery_restoration_order": list(reversed(ROLE_ORDER)),
        "public_recovery_root": RECOVERY_ROOT,
        "recovery_lock_filename": "recoverable-controller-v12.lock",
        "frozen_graph_version": 76,
        "frozen_graph_source_sha256": GRAPH[0][1],
        "frozen_graph_inputs_sha256": GRAPH[1][1],
        "frozen_graph_summary_sha256": GRAPH[2][1],
        "frozen_graph_svg_sha256": GRAPH[3][1],
        "current_evidence_owner_lower_bound": EVIDENCE_FLOOR,
        "current_history_reference_lower_bound": HISTORY_FLOOR,
        "prospective_evidence_owner_lower_bound": EVIDENCE_FLOOR + 3,
        "prospective_history_reference_lower_bound": HISTORY_FLOOR + 3,
        "actual_rust_semantic_mismatch_count": 1440,
        "actual_rust_verified_passing_case_count": 14853,
        "actual_c_semantic_mismatch_count": 1230,
        "actual_c_verified_passing_case_count": 7325,
        "candidate_correctness": "NOT MEASURED",
        "candidate_matching": "NOT RUN",
        "candidate_qualified": False,
        "holdout": "NOT OPENED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "timing_trials_run": 0,
        "undefined_behavior": "NOT MEASURED",
        "winner_selected": False,
    }


def parse_cli(arguments: list[str]) -> dict:
    modes = ("--self-test", "--verify-frozen-context", "--render-contract",
             "--run", "--worker", "--recover")
    selected = [item for item in arguments if item in modes]
    need(len(selected) == 1, "select exactly one V12 operation")
    result: dict[str, object] = {"mode": selected[0]}
    index = 0
    while index < len(arguments):
        option = arguments[index]
        if option in modes:
            index += 1
            continue
        need(option.startswith("--") and index + 1 < len(arguments),
             "reject malformed or missing V12 authority")
        key = option[2:].replace("-", "_")
        need(key not in result, "reject duplicated V12 authority: " + option)
        result[key] = arguments[index + 1]
        index += 2
    for key in ("source_sha256", "protocol_sha256"):
        sha_pin(result.get(key), key)
    render = selected[0] == "--render-contract"
    if not render:
        sha_pin(result.get("contract_sha256"), "contract_sha256")
    else:
        need("contract_sha256" not in result,
             "contract rendering cannot pin or authorize its own nonexistent output")
    source_keys = {"mode", "source_sha256", "protocol_sha256", "contract_sha256"}
    if selected[0] in ("--self-test", "--verify-frozen-context", "--render-contract"):
        need(set(result) <= source_keys,
             "source-only gates cannot authorize private roots, archives, or candidates")
    return result


def actual_required_authority() -> dict[str, str]:
    """Pins required for every real controller, worker, or recovery."""
    return {
        "family": "rust",
        "label": LABEL,
        "activation_root": RECOVERY_ROOT,
        "build_private_root": ROOT_PATH,
        "build_private_root_device": str(ROOT_DEVICE),
        "build_private_root_inode": str(ROOT_INODE),
        "producer_source_sha256": PRODUCER[0][1],
        "producer_protocol_sha256": PRODUCER[1][1],
        "producer_contract_sha256": PRODUCER[2][1],
        "phase1_v4_source_sha256": P0[0][1],
        "phase1_v4_protocol_sha256": P0[1][1],
        "phase1_v4_contract_sha256": P0[2][1],
        "build_source_sha256": BUILD[0][1],
        "build_protocol_sha256": BUILD[1][1],
        "build_contract_sha256": BUILD[2][1],
        "build_archive_sha256": BUILD_ARCHIVE_SHA,
        "build_receipt_sha256": BUILD_RECEIPT[1],
        "root_receipt_sha256": ROOT_RECEIPT[1],
        "native_engine_sha256": ENGINE_SHA,
        "native_engine_bytes": str(ENGINE_BYTES),
        "native_bridge_sha256": BRIDGE_SHA,
        "native_bridge_bytes": str(BRIDGE_BYTES),
        "runtime_guard_source_sha256": GUARD[0][1],
        "runtime_guard_protocol_sha256": GUARD[1][1],
        "runtime_guard_contract_sha256": GUARD[2][1],
    }


def actual_namespace(options: dict) -> types.SimpleNamespace:
    required = actual_required_authority()
    for key, expected in required.items():
        need(options.get(key) == expected,
             "require separately authorized, actual V19 authority: " + key)
    mode = options["mode"]
    extras = {"mode", "source_sha256", "protocol_sha256", "contract_sha256"}
    extras.update(required)
    if mode == "--worker":
        need(options.get("suite") in {name for name, _ in SUITES},
             "pin exactly one original corrected V4 worker suite")
        extras.add("suite")
        for key in ("activation_report_sha256", "activation_receipt_sha256",
                    "recovery_journal_sha256"):
            sha_pin(options.get(key), key)
            extras.add(key)
    elif mode == "--recover":
        sha_pin(options.get("recovery_journal_sha256"),
                "actual V12 four-role recovery journal")
        extras.add("recovery_journal_sha256")
    else:
        need(mode == "--run", "reject an invented actual operation")
    need(set(options) <= extras,
         "reject extra actual authority, implicit fallback, or inspection")
    values = dict(options)
    for key in ("build_private_root_device", "build_private_root_inode",
                "native_engine_bytes", "native_bridge_bytes"):
        values[key] = int(values[key])
    for key in ("suite", "activation_report_sha256",
                "activation_receipt_sha256", "recovery_journal_sha256",
                "inspection_report_sha256", "inspection_receipt_sha256"):
        values.setdefault(key, None)
    return types.SimpleNamespace(**values)


def live_candidate_owner(role: str, relative: str, digest: str,
                         count: int) -> dict:
    """Read one activated canonical role only in an authorized worker."""
    need(role in ("adapter", "engine", "bridge")
         and relative.startswith("candidates/")
         and ".." not in relative.split("/"),
         "reject an unselected activated candidate role")
    absolute = os.path.join(ROOT, relative)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(absolute, flags)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode)
             and before.st_dev == 2064 and before.st_uid == os.geteuid()
             and before.st_size == count and before.st_nlink == 1,
             "reject substituted activated " + role)
        remaining = count + 1
        chunks: list[bytes] = []
        while remaining:
            piece = os.read(fd, min(remaining, 262144))
            if not piece:
                break
            chunks.append(piece)
            remaining -= len(piece)
        raw = b"".join(chunks)
        after = os.fstat(fd)
        need(len(raw) == count and hashlib.sha256(raw).hexdigest() == digest
             and (before.st_dev, before.st_ino, before.st_size,
                  before.st_mtime_ns, before.st_ctime_ns, before.st_nlink)
             == (after.st_dev, after.st_ino, after.st_size,
                 after.st_mtime_ns, after.st_ctime_ns, after.st_nlink),
             "reject an altered activated " + role)
        return {
            "role": role, "family": "rust", "absolute_path": absolute,
            "relative": relative, "file_name": os.path.basename(relative),
            "sha256": digest, "bytes": count, "size_bytes": count,
            "device": before.st_dev, "inode": before.st_ino,
            "mode": stat.S_IMODE(before.st_mode), "uid": before.st_uid,
            "nlink": before.st_nlink, "native_loaded": False,
        }
    finally:
        os.close(fd)


def install_worker_guard(guard: types.ModuleType) -> dict:
    """Install first; authenticate/load only the selected first-party engine."""
    need("re" not in sys.modules and "_sre" not in sys.modules
         and not any(name == "candidates" or name.startswith("candidates.")
                     for name in sys.modules),
         "require an actually clean worker before installing its audit hook")
    policy = guard.RuntimePolicy()
    need(callable(getattr(policy, "prepare_family", None)),
         "require an operational guard that supports the attested own bridge")
    policy.install()
    need(policy.installed and "re" not in sys.modules
         and "_sre" not in sys.modules,
         "physically install the irreversible audit hook before candidate import")
    adapter = live_candidate_owner(
        "adapter", "candidates/rust_candidate.py",
        CORRECTED_ADAPTER_SHA, CORRECTED_ADAPTER_BYTES,
    )
    engine = live_candidate_owner(
        "engine", "candidates/_rust_engine.so", ENGINE_SHA, ENGINE_BYTES,
    )
    bridge = live_candidate_owner(
        "bridge", "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so",
        BRIDGE_SHA, BRIDGE_BYTES,
    )
    policy.prepare_family("rust", bridge_owner=bridge, engine_owner=engine)
    if not sys.path or sys.path[0] != ROOT:
        sys.path.insert(0, ROOT)
    candidate = importlib.import_module("candidates.rust_candidate")
    need(type(candidate) is types.ModuleType
         and candidate.__name__ == "candidates.rust_candidate"
         and os.path.abspath(str(getattr(candidate, "__file__", "")))
         == adapter["absolute_path"],
         "import only the authenticated independent Rust candidate")
    policy.bind_selected(candidate, "rust")
    need(policy.installed and sys.modules.get("re") is candidate
         and "_sre" not in sys.modules
         and sys.modules.get("candidates.rust_candidate") is candidate
         and type(sys.modules.get("candidates._rust_bridge")) is types.ModuleType
         and os.path.abspath(str(sys.modules["candidates._rust_bridge"].__file__))
         == bridge["absolute_path"],
         "bind the actual guarded Rust matcher and its one attested native bridge")
    policy.check_modules()
    return {"policy": policy, "candidate": candidate,
            "adapter": adapter, "engine": engine, "bridge": bridge}


def derive_v19_private_report(legacy: types.ModuleType,
                              root_receipt: dict,
                              namespace: types.SimpleNamespace,
                              ledger: dict) -> dict:
    """Descriptor-verify both actual receipt-bound phases; never read gzip."""
    need(namespace.build_private_root == ROOT_PATH
         and namespace.build_private_root_device == ROOT_DEVICE
         and namespace.build_private_root_inode == ROOT_INODE,
         "recheck the exact independently receipt-attested V19 private root")
    root_info = root_receipt.get("root")
    need(isinstance(root_info, dict) and root_info.get("path") == ROOT_PATH
         and root_info.get("device") == ROOT_DEVICE
         and root_info.get("inode") == ROOT_INODE,
         "reject a substituted actual callback-bound V19 private root")
    flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_DIRECTORY", 0))
    descriptor = os.open(ROOT_PATH, flags)
    try:
        identity = os.fstat(descriptor)
        need(stat.S_ISDIR(identity.st_mode)
             and identity.st_dev == ROOT_DEVICE
             and identity.st_ino == ROOT_INODE
             and identity.st_uid == os.geteuid()
             and stat.S_IMODE(identity.st_mode) == 0o700,
             "open only the caller-pinned actual V19 root directory inode")
    finally:
        os.close(descriptor)
    phases: list[dict] = []
    distinct: set[tuple[int, int]] = set()
    for index, phase_name in enumerate(("reference-a", "reference-b")):
        evidence_phase = root_info["phases"][index]
        need(evidence_phase["name"] == phase_name,
             "preserve exact V19 build phase order")
        source_rows: dict[str, dict] = {}
        for relative, digest, count in legacy.SOURCE_OWNERS:
            item = legacy.Owner(phase_name + "/source/" + relative,
                                digest, count)
            _, observed = legacy.read_owner(item, private_root=ROOT_PATH)
            identity_key = (observed["device"], observed["inode"])
            need(identity_key not in distinct
                 and observed["device"] == ROOT_DEVICE
                 and observed["mode"] == 0o600,
                 "reject reused or substituted V19 private source: " + relative)
            distinct.add(identity_key)
            source_rows[relative] = dict(observed)
        native_rows: dict[str, dict] = {}
        for native in evidence_phase["native_outputs"]:
            role = native["role"]
            need(role in ("engine", "bridge") and role not in native_rows,
                 "require the two independently attested V19 native roles")
            item = legacy.Owner(
                phase_name + "/native/" + native["file_name"],
                native["sha256"], native["bytes"],
            )
            _, observed = legacy.read_owner(
                item, private_root=ROOT_PATH, maximum=legacy.MAX_NATIVE_BYTES,
            )
            identity_key = (observed["device"], observed["inode"])
            need(identity_key == (native["device"], native["inode"])
                 and identity_key not in distinct,
                 "reject exchanged V19 receipt-bound private " + role)
            distinct.add(identity_key)
            native_rows[role] = {
                **observed,
                "role": role,
                "sha256": native["sha256"],
                "size_bytes": native["bytes"],
                "bytes": native["bytes"],
            }
        need(set(native_rows) == {"engine", "bridge"},
             "require both complete genuine V19 private native artifacts")
        phases.append({"name": phase_name,
                       "fresh_source_owners": source_rows,
                       "native_outputs": native_rows})
    need(len(distinct) == len(legacy.SOURCE_OWNERS) * 2 + 4,
         "authenticate every distinct actual V19 source and native inode")
    ledger["v19_private_root_receipt_reverifications"] = (
        ledger.get("v19_private_root_receipt_reverifications", 0) + 1
    )
    return {"phases": phases}


def v12_worker_arguments(namespace: types.SimpleNamespace, suite: str,
                         active: dict) -> list[str]:
    need(suite in {name for name, _ in SUITES},
         "spawn only one frozen original guarded V5 suite")
    args = [PYTHON, "-I", "-B", "-S", os.path.join(ROOT, SOURCE), "--worker",
            "--source-sha256", namespace.source_sha256,
            "--protocol-sha256", namespace.protocol_sha256,
            "--contract-sha256", namespace.contract_sha256,
            "--suite", suite]
    for key, expected in actual_required_authority().items():
        args.extend(("--" + key.replace("_", "-"), expected))
    for key, owner_key in (
        ("activation_report_sha256", "activation_owner"),
        ("activation_receipt_sha256", "receipt_owner"),
        ("recovery_journal_sha256", "journal_owner"),
    ):
        value = active.get(owner_key)
        need(isinstance(value, dict),
             "require actual four-role activation ownership: " + owner_key)
        fingerprint = sha_pin(value.get("sha256"), key)
        args.extend(("--" + key.replace("_", "-"), fingerprint))
    return args


def bind_v12_legacy(context: dict, guard: types.ModuleType,
                    bundle: dict | None) -> types.ModuleType:
    """Adapt the authenticated immutable V11 implementation in memory."""
    raw = owner_read(V11[0])
    original = raw.decode("utf-8", "strict")
    original = original.replace(
        "phase2-v18-rust-buffer-shape-pickle-original-p0-v11", LABEL,
    ).replace(
        "phase2-v18-rust-buffer-shape-pickle-original-p0",
        "phase2-v19-rust-buffer-shape-root-provenance-original-p0",
    ).replace(
        "phase2-v18-rust-buffer-shape-pickle-lifetime", BUILD_LABEL,
    ).replace(
        "rebar-owned-six-family-original-p0-producer-v4",
        "rebar-owned-six-family-original-p0-producer-v5",
    ).replace(
        "frozen_original_six_family_v4", "frozen_original_six_family_v5",
    ).replace(
        '"original_v4_producer_version": 4',
        '"original_v5_producer_version": 5',
    ).replace(
        "original_v4_producer_", "original_v5_producer_",
    ).replace(
        '"original_observer_version": 4',
        '"original_observer_version": 5',
    ).replace(
        'observed.get("original_observer_version") == 4',
        'observed.get("original_observer_version") == 5',
    )
    for before, after in (("v11", "v12"), ("V11", "V12"),
                          ("v18", "v19"), ("V18", "V19"),
                          ("v69", "v76"), ("V69", "V76")):
        original = original.replace(before, after)
    legacy = types.ModuleType("_rebar_v12_authenticated_v11_original_campaign")
    legacy.__file__ = os.path.join(ROOT, V11[0][0])
    exec(compile(original, legacy.__file__, "exec", dont_inherit=True),
         legacy.__dict__)
    need(tuple(legacy.ROLE_ORDER) == ROLE_ORDER
         and tuple(legacy.RESTORATION_ORDER) == tuple(reversed(ROLE_ORDER))
         and tuple(legacy.SUITES) == SUITES
         and legacy.SUITE_COUNT == WORKER_COUNT
         and legacy.CASE_COUNT == CASE_COUNT
         and legacy.PRIVATE_WAIVER_COUNT == PRIVATE_WAIVER_COUNT
         and callable(legacy.run_original_worker)
         and callable(legacy.run_campaign)
         and callable(legacy.recover_originals),
         "retain the genuine complete V11 workers, controller, and recovery")

    def named(owner: tuple) -> object:
        return legacy.Owner(owner[0], owner[1], owner[2], 2064, owner[3])

    build_receipt, root_receipt = authenticate_root_receipts(guard)
    publication = build_receipt.get("archive_publication")
    need(isinstance(publication, dict)
         and publication.get("sha256") == BUILD_ARCHIVE_SHA
         and publication.get("bytes") == BUILD_ARCHIVE_BYTES
         and publication.get("device") == 2064
         and publication.get("inode") == BUILD_ARCHIVE_INODE
         and build_receipt.get("uncompressed_sha256") == BUILD_PLAIN_SHA
         and build_receipt.get("uncompressed_bytes") == BUILD_PLAIN_BYTES,
         "bind archive metadata exclusively to the authenticated V19 receipt")
    legacy.SOURCE_PATH = SOURCE
    legacy.PROTOCOL_PATH = PROTOCOL
    legacy.CONTRACT_PATH = CONTRACT
    legacy.SCHEMA = SCHEMA
    legacy.CONTRACT_SCHEMA = SCHEMA + "-recoverable-source-freeze"
    legacy.WORKER_SCHEMA = SCHEMA + "-actual-original-suite-worker"
    legacy.CAMPAIGN_SCHEMA = SCHEMA + "-complete-original-campaign"
    legacy.RECEIPT_SCHEMA = SCHEMA + "-durable-publication-receipt"
    legacy.LABEL = LABEL
    legacy.BUILD_LABEL = BUILD_LABEL
    legacy.PUBLIC_RECOVERY_PRIVATE_PREFIX = RECOVERY_PRIVATE_PREFIX
    legacy.PUBLIC_RECOVERY_ROOT = RECOVERY_ROOT
    legacy.LOCK_NAME = "recoverable-controller-v12.lock"
    legacy.BUILD = tuple(named(owner) for owner in BUILD)
    legacy.BUILD_RECEIPT = named(BUILD_RECEIPT)
    legacy.BUILD_ARCHIVE = legacy.Owner(
        build_receipt["archive_relative"], BUILD_ARCHIVE_SHA,
        BUILD_ARCHIVE_BYTES, 2064, BUILD_ARCHIVE_INODE,
    )
    legacy.BUILD_PLAIN_SHA256 = BUILD_PLAIN_SHA
    legacy.BUILD_PLAIN_BYTES = BUILD_PLAIN_BYTES
    legacy.GRAPH = tuple(named(owner) for owner in GRAPH)
    legacy.CURRENT_GRAPH_VERSION = 76
    legacy.CURRENT_GRAPH_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR
    legacy.CURRENT_GRAPH_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR
    legacy.CURRENT_EVIDENCE_OWNER_LOWER_BOUND = EVIDENCE_FLOOR + 3
    legacy.CURRENT_HISTORY_REFERENCE_LOWER_BOUND = HISTORY_FLOOR + 3
    legacy.VERIFIED_BUILD_PRIVATE_ROOT = ROOT_PATH
    legacy.VERIFIED_BUILD_PRIVATE_ROOT_DEVICE = ROOT_DEVICE
    legacy.VERIFIED_BUILD_PRIVATE_ROOT_INODE = ROOT_INODE
    legacy.VERIFIED_NATIVE_ENGINE_SHA256 = ENGINE_SHA
    legacy.VERIFIED_NATIVE_ENGINE_BYTES = ENGINE_BYTES
    legacy.VERIFIED_NATIVE_BRIDGE_SHA256 = BRIDGE_SHA
    legacy.VERIFIED_NATIVE_BRIDGE_BYTES = BRIDGE_BYTES
    legacy.PRODUCER = tuple(named(owner) for owner in PRODUCER)
    legacy.PHASE_ONE_V4 = tuple(named(owner) for owner in P0)
    authenticated_loader = legacy.load_frozen_module

    def guard_clean_rust_family(module: types.ModuleType,
                                producer: types.ModuleType) -> object:
        need(type(producer) is types.ModuleType
             and getattr(producer, "SCHEMA", None)
             == "rebar-owned-six-family-original-p0-producer-v5"
             and getattr(producer, "SUITE_COUNT", None) == WORKER_COUNT
             and getattr(producer, "CASE_DENOMINATOR", None) == CASE_COUNT
             and getattr(producer, "PRIVATE_WAIVER_COUNT", None)
             == PRIVATE_WAIVER_COUNT,
             "bind only the actual first-party guard-clean V5 producer")
        original_family = producer.family_spec("rust")
        unchanged = tuple(module.ORIGINAL_SOURCE_OWNERS)
        need(tuple(original_family.source_owners) == unchanged
             and tuple(producer.OWNED_SOURCES["rust"]) == unchanged
             and original_family.name == "rust"
             and original_family.module == "candidates.rust_candidate"
             and original_family.adapter_relative
             == "candidates/rust_candidate.py"
             and original_family.bridge_module == "candidates._rust_bridge"
             and original_family.engine_relative == "candidates/_rust_engine.so"
             and original_family.bridge_relative
             == "candidates/_rust_bridge.cpython-314-x86_64-linux-gnu.so"
             and original_family.combined_native is False
             and original_family.owned_ctypes is False,
             "reject altered, wrapped, combined, or cross-family Rust sources")
        corrected_sources = tuple(legacy.corrected_source_tuples())
        need(corrected_sources == tuple(module.CORRECTED_SOURCE_OWNERS)
             and corrected_sources[0]
             == ("candidates/rust_candidate.py", CORRECTED_ADAPTER_SHA,
                 CORRECTED_ADAPTER_BYTES),
             "bind only the receipt-authenticated corrected Rust source closure")
        corrected = producer.FamilySpec(
            original_family.name, original_family.module,
            original_family.adapter_relative, original_family.bridge_module,
            original_family.engine_relative, original_family.bridge_relative,
            corrected_sources, original_family.combined_native,
            original_family.owned_ctypes,
        )
        producer.OWNED_SOURCES["rust"] = corrected_sources
        producer.FAMILIES["rust"] = corrected
        need(producer.family_spec("rust") is corrected
             and tuple(corrected.source_owners) == corrected_sources,
             "install the one genuine corrected first-party Rust engine")
        return corrected

    def load_v12_module(owner: object, name: str) -> types.ModuleType:
        module = authenticated_loader(owner, name)
        if name == "_rebar_v12_frozen_reviewed_rust_v7":
            need(getattr(module, "SCHEMA", None)
                 == "rebar-owned-repaired-rust-original-campaign-v7"
                 and isinstance(getattr(module, "PRODUCER", None), dict),
                 "load only authenticated historical four-role recovery")
            module.PRODUCER = {
                **module.PRODUCER,
                "source": (PRODUCER[0][0], PRODUCER[0][1], PRODUCER[0][2]),
                "protocol": (PRODUCER[1][0], PRODUCER[1][1], PRODUCER[1][2]),
                "contract": (PRODUCER[2][0], PRODUCER[2][1], PRODUCER[2][2]),
            }

            def corrected_rust_family(producer: types.ModuleType) -> object:
                return guard_clean_rust_family(module, producer)

            module.corrected_rust_family = corrected_rust_family
        return module

    legacy.load_frozen_module = load_v12_module

    def verified_context(source_sha: str, protocol_sha: str,
                         contract_sha: str) -> dict:
        need((source_sha, protocol_sha, contract_sha)
             == (context["source_sha256"], context["protocol_sha256"],
                 context["contract_sha256"]),
             "reject a changed V12 controller or original worker contract")
        return {**context, "build_receipt": dict(build_receipt)}

    def validated_receipt(value: dict) -> None:
        need(isinstance(value, dict) and value == build_receipt,
             "require the exact canonical V19 build receipt, never a V18 inspection")

    def actual_report(namespace: types.SimpleNamespace,
                      ledger: dict) -> dict:
        return derive_v19_private_report(legacy, root_receipt,
                                         namespace, ledger)

    legacy.verify_frozen_context = verified_context
    legacy.validate_build_receipt = validated_receipt
    legacy.read_inspected_build_report = actual_report
    legacy.worker_arguments = v12_worker_arguments
    if bundle is not None:
        legacy.ACTUAL_V12_RUNTIME_POLICY = bundle["policy"]
        legacy.ACTUAL_V12_RUNTIME_GUARD = guard
        legacy.ACTUAL_V12_RUNTIME_NATIVE_OWNERS = {
            "bridge": bundle["bridge"], "engine": bundle["engine"],
        }
    need(legacy.SOURCE_PATH == SOURCE
         and legacy.PUBLIC_RECOVERY_ROOT == RECOVERY_ROOT
         and legacy.BUILD[0].sha256 == BUILD[0][1]
         and legacy.BUILD_RECEIPT.sha256 == BUILD_RECEIPT[1]
         and legacy.BUILD_ARCHIVE.sha256 == BUILD_ARCHIVE_SHA
         and legacy.GRAPH[2].sha256 == GRAPH[2][1]
         and legacy.CURRENT_GRAPH_VERSION == 76,
         "reject stale legacy graph, V18 owner, V11 path, or recovery root")
    return legacy


def actual_operation(options: dict, context: dict,
                     guard: types.ModuleType) -> dict:
    """Really dispatch the frozen original worker, controller, or recovery."""
    namespace = actual_namespace(options)
    bundle = install_worker_guard(guard) if options["mode"] == "--worker" else None
    legacy = bind_v12_legacy(context, guard, bundle)
    if options["mode"] == "--worker":
        need(bundle is not None and bundle["policy"].installed
             and sys.modules.get("re") is bundle["candidate"]
             and "_sre" not in sys.modules,
             "never enter an original worker before runtime isolation")
        result = legacy.run_original_worker(namespace)
        need(isinstance(result, dict)
             and result.get("schema") == legacy.WORKER_SCHEMA
             and result.get("suite") == namespace.suite
             and result.get("case_execution_denominator")
             == dict(SUITES)[namespace.suite]
             and result.get("actual_candidate_workers") == 1,
             "preserve one genuine complete independently observed V4 worker")
        bundle["policy"].check_modules()
        result["runtime_guard_source_sha256"] = GUARD[0][1]
        result["runtime_guard_protocol_sha256"] = GUARD[1][1]
        result["runtime_guard_contract_sha256"] = GUARD[2][1]
        result["runtime_guard_installed_before_candidate_import"] = True
        return result
    if options["mode"] == "--recover":
        result = legacy.recover_originals(namespace)
        need(isinstance(result, dict) and result.get("status") == "PASS"
             and result.get("activation_root") == RECOVERY_ROOT
             and result.get("candidate_workers_started") == 0,
             "restore only the exact four original inodes from a pinned journal")
        return result
    ledger = legacy.new_actual_ledger(namespace)
    result = legacy.run_campaign(namespace, ledger)
    need(isinstance(result, dict)
         and result.get("suite_count") == WORKER_COUNT
         and result.get("case_execution_denominator") == CASE_COUNT
         and result.get("current_overview_version") == 76
         and result.get("actual_v19_build_receipt_sha256") == BUILD_RECEIPT[1]
         and result.get("all_four_original_targets_restored") is True
         and result.get("candidate_qualified")
         is (result.get("semantic_mismatch_count") == 0
             and result.get("infrastructure_failure_count") == 0
             and result.get("actual_candidate_workers") == WORKER_COUNT),
         "preserve the honest full V19 candidate result and four-role recovery")
    return result


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_cli(list(sys.argv[1:] if arguments is None else arguments))
        mode = options["mode"]
        context = verify_frozen_context(
            options["source_sha256"], options["protocol_sha256"],
            options.get("contract_sha256"), rendering=mode == "--render-contract",
        )
        guard = load_guard()
        if mode == "--render-contract":
            result = contract_document(options["source_sha256"],
                                       options["protocol_sha256"], context)
        elif mode == "--self-test":
            result = dict(context)
            result["schema"] = SCHEMA + "-source-self-test"
            result["hostile_controls"] = "SOURCE PINS AND ACTUAL-EFFECT AUTHORITY FAIL CLOSED"
        elif mode == "--verify-frozen-context":
            result = context
        else:
            result = actual_operation(options, context, guard)
        sys.stdout.buffer.write(guard.canonical(result))
        sys.stdout.buffer.flush()
        return 0 if result.get("status") in (
            "PASS", "SOURCE FROZEN; NO CANDIDATE EXECUTED OR QUALIFIED",
        ) else 1
    except Exception as exc:
        sys.stderr.write("V12 campaign rejected: " + str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
