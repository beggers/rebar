#!/usr/bin/env python3
"""Show the real failed public import without inventing candidate results."""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import types


ROOT = Path("/home/dev-user/src/rebar")
SELF = "tools/render_candidate_current_overview_v45.py"
OUTPUT = "docs/evidence/candidate-current-overview-v45"
SCHEMA = "rebar-candidate-current-overview-v45"
V44 = {
    "source": (
        "tools/render_candidate_current_overview_v44.py",
        "10b64e05336485445b5199acdf4626854812c16df6c8248371860a764450324d",
        85131,
    ),
    "inputs": (
        "docs/evidence/candidate-current-overview-v44.inputs.json",
        "7b51e6fa89d7b1d3ccc043e0268f405fe072999d22bd6067aaf2f20ab43e0d94",
        334269,
    ),
    "summary": (
        "docs/evidence/candidate-current-overview-v44.json",
        "5fa65d50eb041b0e12384846c5a7de548581cbc5f9183b1f72bc5f3d703a41c9",
        973979,
    ),
    "svg": (
        "docs/evidence/candidate-current-overview-v44.svg",
        "b23c43fab061df0cf192b9c5c869aee8854ad794397dc3c9512aa6f946150ab8",
        14375,
    ),
}
PUBLIC_ORACLE = {
    "source": (
        "tools/verify_public_entrypoint_import_v1.py",
        "c0a61c4cf520e82bf0c327a17c06daf64f57a1dcfd20b37c6e9f7b84177108b4",
        83957,
    ),
    "protocol": (
        "oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md",
        "01ace52c6285142733bdcb2b4556feb43226e01c8b181b84019b8fa8c42697c0",
        7991,
    ),
    "contract": (
        "oracle/phase1/p0-public-entrypoint-import-v1.json",
        "b80ba35a6af481f0dd1c5b9141e2995f7b0ffd12f8ffa7060bab50344ddbda47",
        9823,
    ),
}
MATRIX_SHA256 = (
    "f67f8d4d62f9939c94250ad2e4df55b14df013df7212aa66930ecc3a772d2a58"
)
GOAL_SHA256 = (
    "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62"
)
PUBLIC_STATUS = "UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER"
CASE_ROWS = (
    ("entrypoint.source.exact-bytes", "PASS"),
    ("entrypoint.source.ast-only-observation", "PASS"),
    ("entrypoint.source.no-import-during-freeze", "PASS"),
    ("entrypoint.surface.ordered-wildcard-exports", "PASS"),
    ("entrypoint.surface.pattern-error-alias", "PASS"),
    ("entrypoint.surface.direct-debug-attribute", "PASS"),
    ("entrypoint.surface.direct-scanner-attribute", "PASS"),
    ("entrypoint.surface.module-version", "FAIL"),
    ("entrypoint.selection.qualified-winner", "FAIL"),
    ("entrypoint.selection.historical-zig-qualification", "FAIL"),
    ("entrypoint.selection.no-premature-family", "FAIL"),
    ("entrypoint.native.no-eager-bridge-import", "FAIL"),
    ("entrypoint.native.no-eager-engine-load", "FAIL"),
    ("entrypoint.native.actual-freeze-load-count", "PASS"),
    ("entrypoint.packaging.uv-package-enabled", "FAIL"),
    ("entrypoint.packaging.installed-artifact", "NOT MEASURED"),
    ("entrypoint.provenance.owned-zig-source", "PASS"),
    ("entrypoint.provenance.runtime-no-delegation", "NOT ESTABLISHED"),
    ("entrypoint.p0.original-case-denominator", "PASS"),
    ("entrypoint.p0.original-suite-denominator", "PASS"),
    ("entrypoint.p0.named-private-waivers", "PASS"),
    ("entrypoint.p0.separate-signature-denominator", "PASS"),
    ("entrypoint.p0.two-reference-signature-baseline", "PASS"),
    ("entrypoint.p0.candidate-signature-observations", "NOT MEASURED"),
    ("entrypoint.p0.public-entrypoint-matching", "NOT MEASURED"),
    ("entrypoint.safety.native-undefined-behavior", "NOT MEASURED"),
    ("entrypoint.safety.native-memory", "NOT MEASURED"),
    ("entrypoint.performance.end-to-end", "NOT MEASURED"),
    ("entrypoint.performance.final-holdout", "NOT OPENED"),
    ("entrypoint.history.actual-rust-failure-preserved", "PASS"),
    ("entrypoint.history.actual-zig-failure-preserved", "PASS"),
    ("entrypoint.history.zero-qualified-families", "PASS"),
)
CASE_COUNTS = {
    "PASS": 17,
    "FAIL": 7,
    "NOT MEASURED": 6,
    "NOT ESTABLISHED": 1,
    "NOT OPENED": 1,
}
PUBLIC_OWNER_ROWS = (
    (
        "goal", "GOAL.md",
        "e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62",
        3756,
    ),
    (
        "public_entrypoint", "rebar.py",
        "289769bd637ea525ae7e71d263377e15c0f394ba20619c11b98e266f57fcc34f",
        212,
    ),
    (
        "project_configuration", "pyproject.toml",
        "7d50e8c6c2bc76a0e3ddcac6b5f157b013bcfd76944fdeb2c1c81e0181ae7825",
        224,
    ),
    (
        "historical_zig_adapter", "candidates/zig_candidate.py",
        "2d7ec411bc035091fea3f20857a4793b21092d3f490d20a9a0efaa418cda0862",
        68422,
    ),
    (
        "original_p0_inventory", "oracle/phase1/p0-completeness-v1.json",
        "cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f",
        45632,
    ),
    (
        "original_p0_protocol", "oracle/phase1/P0-COMPLETENESS-V1.md",
        "1457b15ce0ac80eb0247ec3bc5ad7fad4675478881e5fe7160070225f7e43798",
        10392,
    ),
    (
        "additional_signature_inventory",
        "oracle/phase1/p0-callable-introspection-v1.json",
        "e7415894dcc3920d49cf5e14206b4cfd59c4aa4380cb9d960430f688e97f7349",
        14749,
    ),
    (
        "additional_signature_protocol",
        "oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md",
        "1c3082048fc13338e86a055a577128ba678f1a18abde3465a08552d1295b90e8",
        8952,
    ),
    (
        "actual_signature_reference_receipt",
        "oracle/phase1/evidence/"
        "callable-introspection-reference-v2-cpython-3.14.6-"
        "publication-receipt.json",
        "29b4a389e1b99cce15f07069ee1a0895f193e13400f944a037a4f42832619334",
        3533,
    ),
    (
        "first_party_source_inventory",
        "oracle/phase2/candidate-independence-v2.json",
        "89662570a643d94ae1581393ed48015c6fa78d5dbe5ad0419e9a2032e4609659",
        8798,
    ),
    (
        "first_party_source_protocol",
        "oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md",
        "80a1de729c067da36648dcfb9751f7bd3833ff561956df9ad82fc6106a19a16b",
        6194,
    ),
    ("current_overview_renderer", *V44["source"]),
    ("current_overview_inputs", *V44["inputs"]),
    ("current_overview_summary", *V44["summary"]),
    ("current_overview_svg", *V44["svg"]),
    (
        "repaired_rust_v7_source",
        "tools/run_owned_repaired_rust_original_campaign_v7.py",
        "eb6738e6f1c2315aa044c8a4a7978e6df750a9ef359e9ff0551df5f92ab23104",
        505616,
    ),
    (
        "repaired_rust_v7_protocol",
        "oracle/phase2/REPAIRED-RUST-ORIGINAL-CAMPAIGN-V7.md",
        "0b5182a7eee74e586839abc3a0e8bdd122bac248e9cb3b76c603c5add9281840",
        8433,
    ),
    (
        "repaired_rust_v7_contract",
        "oracle/phase2/repaired-rust-original-campaign-v7.json",
        "9c8e85dcc5dcf0a00953b36dd02c29c2ab7b1ed0b4281eb27f6693c058d155e5",
        46385,
    ),
    (
        "pinned_python_executable",
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14",
        "255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016",
        32387816,
    ),
    (
        "pinned_stdlib_re_source",
        "/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/"
        "lib/python3.14/re/__init__.py",
        "741a9de729ed8207bfa19db990f8826f1bf3661f33d0970a80c08cd1338ebc35",
        17876,
    ),
)
PUBLIC_BOUNDARIES = {
    "source_freeze_status": "PASS",
    "observed_public_entrypoint_status": "FAIL",
    "observed_public_entrypoint_classification": "UNQUALIFIED_ZIG_PROTOTYPE",
    "public_entrypoint_qualified": False,
    "qualified_candidate_count": 0,
    "winner_selected": False,
    "stdlib_fallback_allowed": False,
    "external_engine_allowed": False,
    "cross_candidate_delegation_allowed": False,
    "runtime_no_delegation": "NOT ESTABLISHED",
    "installed_public_artifact": "NOT MEASURED",
    "native_undefined_behavior": "NOT MEASURED",
    "native_memory": "NOT MEASURED",
    "performance": "NOT MEASURED",
    "final_holdout_status": "NOT OPENED",
    "final_holdout_planned_case_count": 4194304,
    "final_holdout_generated": False,
    "final_holdout_opened": False,
    "actual_reference_workers_started": 0,
    "actual_candidate_workers_started": 0,
    "actual_candidate_imports": 0,
    "actual_public_entrypoint_imports": 0,
    "actual_stdlib_regex_imports": 0,
    "actual_native_libraries_loaded": 0,
    "actual_archives_opened": 0,
    "actual_archives_decompressed": 0,
    "actual_subprocesses_started": 0,
    "actual_network_requests": 0,
    "actual_clock_samples": 0,
    "actual_holdout_cases_read": 0,
    "actual_hidden_cases_read": 0,
    "workspace_files_written": 0,
    "physical_audit_hook_required": True,
    "physical_audit_denies_unlisted_reads": True,
    "physical_audit_denies_module_imports": True,
    "physical_audit_denies_native_loading": True,
    "physical_audit_denies_execution_and_processes": True,
    "physical_audit_denies_network_and_writes": True,
}
FUTURE_WINNER_POLICY = {
    "allows_candidate_import_in_source_freeze": False,
    "allows_entrypoint_import_in_source_freeze": False,
    "allows_stdlib_regex_fallback": False,
    "allows_cross_family_fallback": False,
    "allows_external_regex_engine": False,
    "allows_premature_winner": False,
    "requires_three_distinct_correctness_qualified_families": True,
    "requires_original_case_count": 31237,
    "requires_original_suite_count": 13,
    "requires_original_private_waiver_count": 13,
    "requires_separate_signature_case_count": 50,
    "requires_separate_signature_pass": True,
    "requires_actual_packaged_public_import": True,
    "requires_exact_public_module_version": "2.2.1",
    "requires_exact_python_wildcard_exports": True,
    "requires_direct_debug_and_scanner_attributes": True,
    "requires_independent_runtime_no_delegation": True,
    "requires_safety_gates": True,
    "requires_frozen_fair_performance_oracle": True,
    "requires_statistically_qualified_winner": True,
    "requires_verified_winner_native_provenance": True,
    "fixes_public_entrypoint_in_this_chunk": False,
}


def load_v44() -> tuple[
    types.ModuleType, types.ModuleType, types.ModuleType,
    types.ModuleType, types.ModuleType, types.ModuleType,
]:
    path, fingerprint, size = V44["source"]
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
            or before.st_size != size
        ):
            raise ValueError("reject a nonprivate or substituted pushed V44 source")
        pieces: list[bytes] = []
        remaining = size
        while remaining:
            piece = os.read(descriptor, min(262144, remaining))
            if not piece:
                raise ValueError("reject a truncated pushed V44 source")
            pieces.append(piece)
            remaining -= len(piece)
        if os.read(descriptor, 1):
            raise ValueError("reject appended bytes after pushed V44 source")
        raw = b"".join(pieces)
        after = os.fstat(descriptor)
        if (
            hashlib.sha256(raw).hexdigest() != fingerprint
            or (
                before.st_dev, before.st_ino, before.st_size,
                before.st_nlink, before.st_mtime_ns,
            ) != (
                after.st_dev, after.st_ino, after.st_size,
                after.st_nlink, after.st_mtime_ns,
            )
        ):
            raise ValueError("reject replacement during pushed V44 authentication")
    finally:
        os.close(descriptor)
    previous = types.ModuleType("_rebar_pushed_public_import_v44_for_v45")
    previous.__file__ = str(ROOT / path)
    previous.__package__ = ""
    exec(
        compile(raw, previous.__file__, "exec", dont_inherit=True),
        previous.__dict__,
    )
    v43, v42, v41, v40, base = previous.load_v43()
    base.runtime()
    base.need(
        previous.SCHEMA == "rebar-candidate-current-overview-v44"
        and previous.SELF == path
        and previous.PUBLIC_STATUS == PUBLIC_STATUS,
        "load only the exactly pushed, failed-public-import V44 renderer",
    )
    return previous, v43, v42, v41, v40, base


def public_rows() -> list[dict[str, str]]:
    return [
        {"id": name, "observed_status": observed}
        for name, observed in CASE_ROWS
    ]


def public_owner_mapping() -> dict[str, dict]:
    return {
        role: {"path": path, "sha256": fingerprint, "bytes": size}
        for role, path, fingerprint, size in PUBLIC_OWNER_ROWS
    }


def validate_public_contract(base: types.ModuleType, document: object) -> None:
    base.need(type(document) is dict,
              "reject an incomplete public-entrypoint source-freeze contract")
    assert isinstance(document, dict)
    rows = public_rows()
    counts = {
        status: sum(row["observed_status"] == status for row in rows)
        for status in CASE_COUNTS
    }
    base.need(
        document.get("schema")
        == "rebar-python-re-public-entrypoint-import-v1-source-freeze"
        and document.get("version") == 1
        and document.get("goal_sha256") == GOAL_SHA256
        and document.get("current_overview_version") == 44
        and document.get("pinned_python") == base.PYTHON
        and document.get("original_correctness") == {
            "case_count": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "additional_signature_case_count": 50,
            "additional_signature_cases_in_original_denominator": False,
        }
        and document.get("case_matrix") == rows
        and len(rows) == 32
        and len({row["id"] for row in rows}) == 32
        and counts == CASE_COUNTS
        and document.get("case_matrix_sha256") == MATRIX_SHA256
        and base.digest(base.canonical(rows)[:-1]) == MATRIX_SHA256
        and document.get("owners") == public_owner_mapping()
        and len(document["owners"]) == 20
        and document.get("boundaries") == PUBLIC_BOUNDARIES
        and document.get("future_public_winner_policy")
        == FUTURE_WINNER_POLICY,
        "require the complete pushed-V44-bound, 20-owner PEP578 public "
        "contract and the separately counted 32 = 17/7/6/1/1 observations",
    )


def assigned_literal(tree: ast.Module, name: str,
                     *, pinned_python: str | None = None) -> object:
    matches: list[ast.expr] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == name
                for target in node.targets
            ):
                matches.append(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
            and node.value is not None
        ):
            matches.append(node.value)
    if len(matches) != 1:
        raise ValueError("require one exact bounded source AST owner: " + name)
    expression: ast.expr = matches[0]
    if pinned_python is not None:
        class PinnedPythonLiteral(ast.NodeTransformer):
            def visit_Name(self, node: ast.Name) -> ast.AST:
                if node.id != "PYTHON" or not isinstance(node.ctx, ast.Load):
                    raise ValueError(
                        "reject executable public source owner: " + node.id,
                    )
                return ast.copy_location(ast.Constant(pinned_python), node)

        expression = PinnedPythonLiteral().visit(copy.deepcopy(expression))
        assert isinstance(expression, ast.expr)
        ast.fix_missing_locations(expression)
    return ast.literal_eval(expression)


def validate_public_source_ast(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject fabricated public-source physical-wall evidence")
    assert isinstance(proof, dict)
    expected = {
        "source_ast_parsed_without_execution": True,
        "exact_source_owner_count": 20,
        "exact_source_matrix_case_count": 32,
        "source_matrix_sha256": MATRIX_SHA256,
        "pep578_audit_hook_defined": True,
        "pep578_audit_hook_installer_defined": True,
        "pep578_addaudithook_call_present": True,
        "pep578_real_sys_audit_probes_present": True,
        "source_self_test_defined": True,
        "source_context_defined": True,
        "source_only_control_count": 191,
        "source_only_physically_blocked_effect_attempt_count": 33,
        "actual_public_imports_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "actual_archive_reads_by_graph": 0,
        "actual_archive_inflations_by_graph": 0,
        "actual_candidate_workers_by_graph": 0,
        "actual_reference_workers_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_holdout_reads_by_graph": 0,
    }
    base.need(
        all(proof.get(key) == value for key, value in expected.items()),
        "never run the PEP578 public oracle, import an entrypoint, open an "
        "archive or confuse blocked hostile attempts with actual effects",
    )


def authenticate_public_source_ast(base: types.ModuleType,
                                   raw: bytes) -> dict:
    try:
        tree = ast.parse(raw, filename=str(ROOT / PUBLIC_ORACLE["source"][0]))
        owners = assigned_literal(tree, "OWNERS", pinned_python=base.PYTHON)
        rows = assigned_literal(tree, "CASE_ROWS")
        matrix = assigned_literal(tree, "MATRIX_SHA256")
        overview = assigned_literal(tree, "OVERVIEW_VERSION")
        source = assigned_literal(tree, "SOURCE")
        protocol = assigned_literal(tree, "PROTOCOL")
        contract = assigned_literal(tree, "CONTRACT")
        functions = {
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        calls = [
            node for node in ast.walk(tree) if isinstance(node, ast.Call)
        ]
        add_hook = any(
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "addaudithook"
            for node in calls
        )
        audit = any(
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "audit"
            for node in calls
        )
    except (SyntaxError, UnicodeError, ValueError, TypeError) as error:
        raise base.GraphError(
            "reject an incomplete or executable source-only public AST",
        ) from error
    base.need(
        type(owners) is tuple
        and owners == PUBLIC_OWNER_ROWS
        and type(rows) is tuple and rows == CASE_ROWS
        and matrix == MATRIX_SHA256
        and overview == 44
        and source == PUBLIC_ORACLE["source"][0]
        and protocol == PUBLIC_ORACLE["protocol"][0]
        and contract == PUBLIC_ORACLE["contract"][0]
        and {
            "source_only_audit_hook", "install_source_only_audit_wall",
            "run_self_test", "verify_context", "validate_contract",
            "no_matcher_imports", "main",
        }.issubset(functions)
        and add_hook and audit,
        "prove the exact PEP578-isolated public verifier, all 20 source "
        "owners, full ordered 32 observations and actual blocked probes "
        "from complete AST only; never import or execute that verifier",
    )
    proof = {
        "source_ast_parsed_without_execution": True,
        "exact_source_owner_count": 20,
        "exact_source_matrix_case_count": 32,
        "source_matrix_sha256": MATRIX_SHA256,
        "pep578_audit_hook_defined": True,
        "pep578_audit_hook_installer_defined": True,
        "pep578_addaudithook_call_present": True,
        "pep578_real_sys_audit_probes_present": True,
        "source_self_test_defined": True,
        "source_context_defined": True,
        "source_only_control_count": 191,
        "source_only_physically_blocked_effect_attempt_count": 33,
        "actual_public_imports_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "actual_archive_reads_by_graph": 0,
        "actual_archive_inflations_by_graph": 0,
        "actual_candidate_workers_by_graph": 0,
        "actual_reference_workers_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_holdout_reads_by_graph": 0,
    }
    validate_public_source_ast(base, proof)
    return proof


def validate_public_proof(base: types.ModuleType, proof: object) -> None:
    base.need(type(proof) is dict,
              "reject a fabricated actual public import or winner")
    assert isinstance(proof, dict)
    expected = {
        "schema": SCHEMA + "-authenticated-public-entrypoint-source-oracle",
        "version": 1,
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification":
            "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_entrypoint_status": PUBLIC_STATUS,
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": MATRIX_SHA256,
        "public_case_status_counts": CASE_COUNTS,
        "public_case_pass_count": 17,
        "public_case_fail_count": 7,
        "public_case_not_measured_count": 6,
        "public_case_not_established_count": 1,
        "public_case_not_opened_count": 1,
        "public_oracle_owner_count": 20,
        "public_source_only_control_count": 191,
        "public_physically_blocked_effect_attempt_count": 33,
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "actual_public_entrypoint_imports_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_archives_opened_by_graph": 0,
        "actual_archives_decompressed_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    base.need(
        all(proof.get(key) == value for key, value in expected.items())
        and proof.get("public_case_rows") == public_rows(),
        "preserve all real separate public failures and zero actual effects",
    )
    for role, pin in PUBLIC_ORACLE.items():
        owner = proof.get(role)
        base.need(
            type(owner) is dict
            and owner.get("path") == pin[0]
            and owner.get("sha256") == pin[1]
            and owner.get("bytes") == pin[2]
            and owner.get("uid") == os.geteuid()
            and owner.get("mode") == "0600"
            and owner.get("nlink") == 1
            and type(owner.get("device")) is int and owner["device"] > 0
            and type(owner.get("inode")) is int and owner["inode"] > 0,
            "authenticate the actual released public oracle " + role,
        )
    contract = proof.get("complete_frozen_contract")
    validate_public_contract(base, contract)
    source_ast = proof.get("source_ast")
    validate_public_source_ast(base, source_ast)
    binding = base.digest(base.canonical({
        "source": proof["source"],
        "protocol": proof["protocol"],
        "contract": proof["contract"],
        "complete_frozen_contract": contract,
        "source_ast": source_ast,
        **expected,
        "public_case_rows": public_rows(),
    }))
    base.need(
        proof.get("complete_public_source_binding_sha256") == binding,
        "bind all exact public-source owners, PEP578 AST and 32 public rows",
    )


def make_public_proof(base: types.ModuleType, owners: dict[str, dict],
                      contract: dict, source_ast: dict) -> dict:
    validate_public_contract(base, contract)
    validate_public_source_ast(base, source_ast)
    proof = {
        "schema": SCHEMA + "-authenticated-public-entrypoint-source-oracle",
        "version": 1,
        **owners,
        "complete_frozen_contract": contract,
        "source_ast": source_ast,
        "source_freeze_status": "PASS",
        "observed_public_entrypoint_status": "FAIL",
        "observed_public_entrypoint_classification":
            "UNQUALIFIED_ZIG_PROTOTYPE",
        "public_entrypoint_status": PUBLIC_STATUS,
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_case_matrix_count": 32,
        "public_case_matrix_sha256": MATRIX_SHA256,
        "public_case_rows": public_rows(),
        "public_case_status_counts": copy.deepcopy(CASE_COUNTS),
        "public_case_pass_count": 17,
        "public_case_fail_count": 7,
        "public_case_not_measured_count": 6,
        "public_case_not_established_count": 1,
        "public_case_not_opened_count": 1,
        "public_oracle_owner_count": 20,
        "public_source_only_control_count": 191,
        "public_physically_blocked_effect_attempt_count": 33,
        "original_case_count": 31237,
        "original_suite_count": 13,
        "original_private_waiver_count": 13,
        "additional_signature_case_count": 50,
        "additional_cases_included_in_original_denominator": False,
        "actual_public_entrypoint_imports_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "actual_archives_opened_by_graph": 0,
        "actual_archives_decompressed_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_hidden_cases_read_by_graph": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "holdout": "NOT OPENED",
        "qualified_candidate_count": 0,
        "winner_selected": False,
    }
    proof["complete_public_source_binding_sha256"] = base.digest(
        base.canonical({
            "source": owners["source"],
            "protocol": owners["protocol"],
            "contract": owners["contract"],
            "complete_frozen_contract": contract,
            "source_ast": source_ast,
            **{
                name: value for name, value in proof.items()
                if name not in (
                    "source", "protocol", "contract",
                    "complete_frozen_contract", "source_ast",
                )
            },
        }),
    )
    validate_public_proof(base, proof)
    return proof


def authenticate_public_oracle(base: types.ModuleType,
                               source_pin: str, protocol_pin: str,
                               contract_pin: str, matrix_pin: str) -> dict:
    for role, supplied in (
        ("source", source_pin),
        ("protocol", protocol_pin),
        ("contract", contract_pin),
    ):
        base.need(
            base.checked(supplied, "exact public source oracle " + role)
            == PUBLIC_ORACLE[role][1],
            "reject an unreviewed public entrypoint " + role,
        )
    base.need(
        base.checked(matrix_pin, "exact separately frozen 32-case matrix")
        == MATRIX_SHA256,
        "reject guessed, combined or substituted public entrypoint cases",
    )
    owners: dict[str, dict] = {}
    source_raw = b""
    contract_raw = b""
    for role, pin in PUBLIC_ORACLE.items():
        raw, owner = base.read_owner(*pin, private=True)
        owners[role] = owner
        if role == "source":
            source_raw = raw
        elif role == "contract":
            contract_raw = raw
    contract = base.document(
        contract_raw, "complete exact public P0 contract", exact=False,
    )
    source_ast = authenticate_public_source_ast(base, source_raw)
    return make_public_proof(base, owners, contract, source_ast)


def public_fields(proof: dict) -> dict:
    return {
        "public_entrypoint_source_oracle": copy.deepcopy(proof),
        "public_entrypoint_oracle_source_sha256": PUBLIC_ORACLE["source"][1],
        "public_entrypoint_oracle_protocol_sha256":
            PUBLIC_ORACLE["protocol"][1],
        "public_entrypoint_oracle_contract_sha256":
            PUBLIC_ORACLE["contract"][1],
        "public_entrypoint_oracle_source_freeze_status": "PASS",
        "public_entrypoint_actual_observed_status": "FAIL",
        "public_entrypoint_status": PUBLIC_STATUS,
        "public_entrypoint_module_version_status": "FAIL/MISSING",
        "public_entrypoint_qualified": False,
        "public_entrypoint_package_mode": False,
        "public_entrypoint_packaged_artifact": "NOT MEASURED",
        "public_entrypoint_installation_status": "NOT MEASURED",
        "public_entrypoint_actual_imports_by_graph": 0,
        "public_entrypoint_actual_native_loads_by_graph": 0,
        "public_entrypoint_runtime_no_delegation": "NOT ESTABLISHED",
        "public_entrypoint_case_matrix_count": 32,
        "public_entrypoint_case_matrix_sha256": MATRIX_SHA256,
        "public_entrypoint_case_rows": public_rows(),
        "public_entrypoint_case_status_counts": copy.deepcopy(CASE_COUNTS),
        "public_entrypoint_pass_count": 17,
        "public_entrypoint_fail_count": 7,
        "public_entrypoint_not_measured_count": 6,
        "public_entrypoint_not_established_count": 1,
        "public_entrypoint_not_opened_count": 1,
        "public_entrypoint_frozen_owner_count": 20,
        "public_entrypoint_source_only_control_count": 191,
        "public_entrypoint_physically_blocked_effect_attempt_count": 33,
        "public_entrypoint_cases_in_original_denominator": False,
        "public_entrypoint_cases_in_signature_denominator": False,
        "supplementary_signature_check_count": 50,
        "supplementary_signature_candidate_status": "NOT MEASURED",
        "candidate_signature_checks_executed": 0,
        "corrected_rust_v7_source_self_test_control_count": 517,
        "actual_candidate_imports_by_graph": 0,
        "actual_candidate_workers_started_by_graph": 0,
        "actual_reference_workers_started_by_graph": 0,
        "actual_native_libraries_loaded_by_graph": 0,
        "candidate_matching_archives_opened_by_graph": 0,
        "reference_archive_gzip_inflation_count": 0,
        "matching_archive_gzip_inflation_count": 0,
        "source_build_archive_gzip_inflation_count_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "clock_samples": 0,
        "hidden_cases_read": 0,
        "timing_trials_run": 0,
        "runtime_no_delegation": "NOT ESTABLISHED",
        "performance": "NOT MEASURED",
        "memory": "NOT MEASURED",
        "confidence_intervals": "NOT MEASURED",
        "undefined_behavior": "NOT MEASURED",
        "final_comparison_planned_case_count": 4194304,
        "final_comparison_cases_generated": False,
        "final_holdout_opened": False,
        "winner_selected": False,
    }


def authenticate_v44(previous: types.ModuleType, v43: types.ModuleType,
                     v42: types.ModuleType, v41: types.ModuleType,
                     v40: types.ModuleType, base: types.ModuleType,
                     supplied: dict[str, str]) -> tuple[dict, dict, bytes]:
    for role, pin in V44.items():
        base.need(
            base.checked(supplied.get(role), "exact pushed V44 " + role)
            == pin[1],
            "require independently supplied pushed V44 " + role,
        )
    raw: dict[str, bytes] = {}
    for role, pin in V44.items():
        raw[role], _ = base.read_owner(*pin, private=True)
    old = base.document(raw["summary"], "complete pushed V44 summary")
    old_inputs = base.document(raw["inputs"], "complete pushed V44 inputs")
    snapshot = old.get("snapshot")
    previous.validate_snapshot(v43, v42, v41, v40, base, snapshot)
    base.need(
        old.get("schema") == "rebar-candidate-current-overview-v44-summary"
        and old.get("version") == 44
        and old.get("status") == "PASS"
        and old.get("source") == base.pin(*V44["source"])
        and old.get("inputs") == base.pin(*V44["inputs"])
        and old.get("svg") == base.pin(*V44["svg"])
        and old_inputs.get("schema")
        == "rebar-candidate-current-overview-v44-inputs"
        and old_inputs.get("version") == 44
        and old_inputs.get("renderer") == base.pin(*V44["source"])
        and raw["svg"] == previous.make_svg(
            v43, v42, v41, v40, base, snapshot,
            V44["source"][1], V44["inputs"][1],
        )
        and old.get("public_entrypoint_status") == PUBLIC_STATUS
        and old.get("public_entrypoint_module_version_status") == "FAIL/MISSING"
        and old.get("qualified_candidate_count") == 0,
        "authenticate all four pushed V44 owners, the actual failed public "
        "shim, unchanged historical failures and complete reproducible SVG",
    )
    previous.authenticate_v43(v43, v42, v41, v40, base)
    actual_rust = previous.authenticate_v7(
        base,
        previous.RUST_V7["source"][1],
        previous.RUST_V7["protocol"][1],
        previous.RUST_V7["contract"][1],
    )
    actual_public = previous.authenticate_public_entrypoint(
        base,
        previous.PUBLIC_OWNERS["module"][1],
        previous.PUBLIC_OWNERS["module"][2],
        previous.PUBLIC_OWNERS["project"][1],
        previous.PUBLIC_OWNERS["project"][2],
    )
    base.need(
        snapshot.get("corrected_rust_v7_source_freeze") == actual_rust
        and snapshot.get("public_entrypoint_static_audit") == actual_public,
        "re-authenticate the true independently pushed Rust V7 and exact "
        "tracked public shim without importing or activating either",
    )
    return old, old_inputs, raw["svg"]


def validate_snapshot(previous: types.ModuleType, v43: types.ModuleType,
                      v42: types.ModuleType, v41: types.ModuleType,
                      v40: types.ModuleType, base: types.ModuleType,
                      snapshot: object) -> None:
    base.need(type(snapshot) is dict,
              "reject a missing complete real-public-failure overview")
    assert isinstance(snapshot, dict)
    previous.validate_snapshot(v43, v42, v41, v40, base, snapshot)
    proof = snapshot.get("public_entrypoint_source_oracle")
    validate_public_proof(base, proof)
    assert isinstance(proof, dict)
    for key, expected in public_fields(proof).items():
        base.need(
            snapshot.get(key) == expected,
            "reject a changed separate public result or actual effect: " + key,
        )
    base.need(
        snapshot.get("full_case_denominator") == 31237
        and snapshot.get("suite_count") == 13
        and snapshot.get("private_waiver_count") == 13
        and snapshot.get("supplementary_signature_check_count") == 50
        and snapshot.get("actual_rust_controller_status") == "FAIL"
        and snapshot.get("actual_rust_source_build_archive_read_count") == 1
        and snapshot.get(
            "actual_rust_controller_ledger_omits_source_build_archive_effect",
        ) is True
        and snapshot.get("authenticated_evidence_owner_lower_bound") == 166
        and snapshot.get("authenticated_history_reference_lower_bound") == 171
        and snapshot.get("first_party_source_inventory_family_count") == 6
        and snapshot.get("frozen_corrected_runner_source_family_count") == 2
        and snapshot.get("actually_runnable_candidate_family_count") == 0
        and snapshot.get("qualified_candidate_count") == 0
        and snapshot.get("corrected_rust_v7_actual_candidate_workers") == 0
        and snapshot.get("corrected_rust_v7_candidate_matching_status")
        == "NOT RUN"
        and snapshot.get("performance") == "NOT MEASURED"
        and snapshot.get("memory") == "NOT MEASURED"
        and snapshot.get("final_holdout_opened") is False,
        "preserve the original denominator, signatures, failed Rust archive, "
        "six first-party source designs and unopened final holdout",
    )


def make_svg(previous: types.ModuleType, v43: types.ModuleType,
             v42: types.ModuleType, v41: types.ModuleType,
             v40: types.ModuleType, base: types.ModuleType,
             snapshot: dict, old_svg: bytes,
             source_sha: str, inputs_sha: str) -> bytes:
    validate_snapshot(previous, v43, v42, v41, v40, base, snapshot)
    source_sha = base.checked(source_sha, "actual current V45 renderer footer")
    inputs_sha = base.checked(inputs_sha, "actual current V45 inputs footer")
    visible = old_svg.decode("utf-8")
    visible = visible.replace("v44-title", "v45-title")
    visible = visible.replace("v44-description", "v45-description")
    replacements = (
        (
            "baseline passes; public Zig import is unqualified; "
            "Rust fix is source-tested only</title>",
            "public import fails 7 checks; no replacement is yet "
            "compatible or measured</title>",
            "honest plain-language public-import headline",
        ),
        (
            "Python now agrees with itself. Six first-party source designs; "
            "two frozen runner sources; public Zig prototype unqualified; "
            "zero runnable replacements.",
            "31,237 original checks; 50 separate signature checks; "
            "32 separate public-import observations; zero qualified "
            "replacements.",
            "keep all three denominators visibly distinct",
        ),
        (
            "The actual public Zig prototype is unqualified, has no "
            "__version__, and has packaging disabled.",
            "A separate 32-observation public audit finds 17 source "
            "observations passing, 7 failing, 6 not measured, 1 not "
            "established and 1 not opened. The actual public Zig prototype "
            "is unqualified, has no __version__, and has packaging disabled.",
            "describe the exact separate public failures without claiming "
            "candidate passes",
        ),
    )
    for before, after, label in replacements:
        visible = v43.replace_once(base, visible, before, after, label)
    visible = v43.replace_once(
        base, visible,
        "Graph inputs SHA-256: " + V44["inputs"][1],
        "Graph inputs SHA-256: " + inputs_sha,
        "label only the actual current V45 graph inputs digest",
    )
    visible = v43.replace_once(
        base, visible,
        "Graph renderer SHA-256: " + V44["source"][1],
        "Graph renderer SHA-256: " + source_sha,
        "label only the actual current V45 graph renderer digest",
    )
    visible = v43.replace_once(
        base, visible,
        'height="2590" viewBox="0 0 1440 2590"',
        'height="2825" viewBox="0 0 1440 2825"',
        "make room for the independently frozen public-import mini-bar",
    )
    lines = [v42.move_y(line, 190) for line in visible.splitlines()]
    insertion = next(
        index + 1 for index, line in enumerate(lines)
        if "source-tested only; C has not run." in line
    )
    lines[insertion:insertion] = [
        '<rect x="44" y="302" width="1352" height="171" rx="14" '
        'fill="#fff1ed" stroke="#e6b3a6"/>',
        '<text x="65" y="335" class="warning">PUBLIC IMPORT FAILS: '
        'UNQUALIFIED ZIG PROTOTYPE; NOT A WINNER</text>',
        '<text x="67" y="358" class="body">Missing __version__; '
        'premature Zig selection; package mode false. The 32 source-only '
        'observations are not candidate test passes.</text>',
        '<rect x="68" y="375" width="646" height="22" rx="5" '
        'fill="#268256"/>',
        '<rect x="714" y="375" width="266" height="22" '
        'fill="#bf5a43"/>',
        '<rect x="980" y="375" width="228" height="22" '
        'fill="#7c8da5"/>',
        '<rect x="1208" y="375" width="38" height="22" '
        'fill="#bf9439"/>',
        '<rect x="1246" y="375" width="38" height="22" rx="5" '
        'fill="#7463a4"/>',
        '<text x="68" y="421" class="small">17 source observations '
        'pass</text>',
        '<text x="294" y="421" class="small">7 actual public checks '
        'fail</text>',
        '<text x="529" y="421" class="small">6 not measured</text>',
        '<text x="747" y="421" class="small">1 not established</text>',
        '<text x="975" y="421" class="small">1 not opened</text>',
        '<text x="67" y="452" class="body">Separate from 31,237 '
        'original cases and 50 signature checks; no public module, '
        'candidate or native engine was imported.</text>',
    ]
    historical_footer = next(
        index for index, line in enumerate(lines)
        if line.startswith("<!-- Zig source correction is frozen only;")
    )
    lines[historical_footer:historical_footer] = [
        '<text x="47" y="2760" class="foot">Historical V44 graph '
        'inputs SHA-256: ' + V44["inputs"][1] + '</text>',
        '<text x="47" y="2782" class="foot">Historical V44 graph '
        'renderer SHA-256: ' + V44["source"][1] + '</text>',
    ]
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    current_input_footer = (
        "Graph inputs SHA-256: " + inputs_sha
    ).encode("ascii")
    current_source_footer = (
        "Graph renderer SHA-256: " + source_sha
    ).encode("ascii")
    historical_input_footer = (
        "Historical V44 graph inputs SHA-256: " + V44["inputs"][1]
    ).encode("ascii")
    historical_source_footer = (
        "Historical V44 graph renderer SHA-256: " + V44["source"][1]
    ).encode("ascii")
    base.need(
        raw.count(current_input_footer) == 1
        and raw.count(current_source_footer) == 1
        and raw.count(historical_input_footer) == 1
        and raw.count(historical_source_footer) == 1
        and (
            "Graph inputs SHA-256: " + V44["inputs"][1]
        ).encode("ascii") not in raw
        and (
            "Graph renderer SHA-256: " + V44["source"][1]
        ).encode("ascii") not in raw,
        "require distinct visible exact current V45 input and renderer "
        "footers and explicitly historical V44 predecessor footers",
    )
    for phrase in (
        b"public import fails", b"unqualified zig prototype; not a winner",
        b"missing __version__", b"premature zig selection",
        b"package mode false", b"32 source-only observations",
        b"not candidate test passes", b"17 source observations pass",
        b"7 actual public checks fail", b"6 not measured",
        b"1 not established", b"1 not opened",
        b"separate from 31,237", b"50 signature checks",
        b"no public module", b"actual rust v6 preflight failed",
        b"108,985", b"760,477", b"1,036", b"1,230", b"1,764",
        b"166 / 171", b"zero runnable", b"4,194,304", b"not opened",
    ):
        base.need(
            phrase.lower() in raw.lower(),
            "reject omitted separate public failure or prior evidence: "
            + repr(phrase),
        )
    for lie in (
        b"32 candidate passes", b"17 candidates pass",
        b"public import passes", b"public entrypoint qualified",
        b"public module imported", b"winner selected",
        b"32,000 original cases", b"31,269 original cases",
    ):
        base.need(
            lie not in raw.lower(),
            "reject invented public-import success or changed denominator",
        )
    base.need(raw.endswith(b"\n") and not raw.endswith(b"\n\n"),
              "render exactly one terminal SVG linefeed")
    return raw


def build(previous: types.ModuleType, v43: types.ModuleType,
          v42: types.ModuleType, v41: types.ModuleType,
          v40: types.ModuleType, base: types.ModuleType,
          options: argparse.Namespace) -> tuple[
              dict, tuple[tuple[str, bytes], ...],
          ]:
    source_pin = base.checked(options.source_sha256, "exact V45 graph source")
    base.need(
        type(options.source_bytes) is int
        and 0 < options.source_bytes <= base.OWNER_LIMIT,
        "require the exact independently supplied V45 source byte count",
    )
    own_raw, _ = base.read_owner(
        SELF, source_pin, options.source_bytes, private=True,
    )
    old, old_inputs, old_svg = authenticate_v44(
        previous, v43, v42, v41, v40, base,
        {
            "source": options.previous_source_sha256,
            "inputs": options.previous_inputs_sha256,
            "summary": options.previous_summary_sha256,
            "svg": options.previous_svg_sha256,
        },
    )
    base.need(
        base.checked(options.rust_source_sha256, "exact pushed Rust V7 source")
        == previous.RUST_V7["source"][1]
        and base.checked(
            options.rust_protocol_sha256, "exact pushed Rust V7 protocol",
        ) == previous.RUST_V7["protocol"][1]
        and base.checked(
            options.rust_contract_sha256, "exact pushed Rust V7 contract",
        ) == previous.RUST_V7["contract"][1]
        and base.checked(
            options.failure_sha256, "actual historical Rust V6 failure",
        ) == v43.FAILURE[1]
        and base.checked(
            options.observation_sha256, "actual omitted Rust V6 archive effect",
        ) == v43.OBSERVATION[1]
        and base.checked(
            options.public_module_sha256,
            "exact actual unqualified public module",
        ) == previous.PUBLIC_OWNERS["module"][1]
        and options.public_module_bytes == previous.PUBLIC_OWNERS["module"][2]
        and base.checked(
            options.public_project_sha256,
            "exact actual package-disabled public project",
        ) == previous.PUBLIC_OWNERS["project"][1]
        and options.public_project_bytes
        == previous.PUBLIC_OWNERS["project"][2],
        "bind the independently supplied real Rust, failure and tracked "
        "public-module owners before graph publication",
    )
    proof = authenticate_public_oracle(
        base, options.public_oracle_source_sha256,
        options.public_oracle_protocol_sha256,
        options.public_oracle_contract_sha256,
        options.public_case_matrix_sha256,
    )
    snapshot = copy.deepcopy(old["snapshot"])
    snapshot.update(public_fields(proof))
    validate_snapshot(previous, v43, v42, v41, v40, base, snapshot)
    predecessors = {
        role: base.pin(*owner) for role, owner in V44.items()
    }
    inputs = copy.deepcopy(old_inputs)
    inputs.update({
        "schema": SCHEMA + "-inputs",
        "version": 45,
        "python": "3.14.6",
        "renderer": base.pin(SELF, source_pin, len(own_raw)),
        "previous_overview": predecessors,
        **public_fields(proof),
    })
    input_raw = base.canonical(inputs)
    svg = make_svg(
        previous, v43, v42, v41, v40, base, snapshot, old_svg,
        source_pin, base.digest(input_raw),
    )
    families = copy.deepcopy(old["families"])
    for row in families:
        if row.get("family") == "python":
            continue
        row.update({
            "public_entrypoint_status": PUBLIC_STATUS,
            "public_entrypoint_actual_observed_status": "FAIL",
            "public_entrypoint_module_version_status": "FAIL/MISSING",
            "public_entrypoint_case_matrix_count": 32,
            "public_entrypoint_case_status_counts": copy.deepcopy(CASE_COUNTS),
            "public_entrypoint_cases_in_original_denominator": False,
            "supplementary_signature_check_count": 50,
            "supplementary_signature_candidate_status": "NOT MEASURED",
            "actual_candidate_workers": 0,
            "actual_native_activations": 0,
            "qualified": False,
            "performance": "NOT MEASURED",
        })
    summary = copy.deepcopy(old)
    summary.update({
        "schema": SCHEMA + "-summary",
        "version": 45,
        "status": "PASS",
        "python": "3.14.6",
        "source": base.pin(SELF, source_pin, len(own_raw)),
        "inputs": base.pin(
            OUTPUT + ".inputs.json", base.digest(input_raw), len(input_raw),
        ),
        "svg": base.pin(OUTPUT + ".svg", base.digest(svg), len(svg)),
        "previous_overview": predecessors,
        "snapshot": snapshot,
        "families": families,
        **public_fields(proof),
    })
    return snapshot, (
        (OUTPUT + ".inputs.json", input_raw),
        (OUTPUT + ".json", base.canonical(summary)),
        (OUTPUT + ".svg", svg),
    )


def synthetic_contract(base: types.ModuleType) -> dict:
    contract = {
        "schema": "rebar-python-re-public-entrypoint-import-v1-source-freeze",
        "version": 1,
        "goal_sha256": GOAL_SHA256,
        "current_overview_version": 44,
        "pinned_python": base.PYTHON,
        "original_correctness": {
            "case_count": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "additional_signature_case_count": 50,
            "additional_signature_cases_in_original_denominator": False,
        },
        "case_matrix": public_rows(),
        "case_matrix_sha256": MATRIX_SHA256,
        "owners": public_owner_mapping(),
        "boundaries": copy.deepcopy(PUBLIC_BOUNDARIES),
        "future_public_winner_policy": copy.deepcopy(FUTURE_WINNER_POLICY),
    }
    validate_public_contract(base, contract)
    return contract


def synthetic_source_ast(base: types.ModuleType) -> dict:
    proof = {
        "source_ast_parsed_without_execution": True,
        "exact_source_owner_count": 20,
        "exact_source_matrix_case_count": 32,
        "source_matrix_sha256": MATRIX_SHA256,
        "pep578_audit_hook_defined": True,
        "pep578_audit_hook_installer_defined": True,
        "pep578_addaudithook_call_present": True,
        "pep578_real_sys_audit_probes_present": True,
        "source_self_test_defined": True,
        "source_context_defined": True,
        "source_only_control_count": 191,
        "source_only_physically_blocked_effect_attempt_count": 33,
        "actual_public_imports_by_graph": 0,
        "actual_candidate_imports_by_graph": 0,
        "actual_native_loads_by_graph": 0,
        "actual_archive_reads_by_graph": 0,
        "actual_archive_inflations_by_graph": 0,
        "actual_candidate_workers_by_graph": 0,
        "actual_reference_workers_by_graph": 0,
        "actual_clock_samples_by_graph": 0,
        "actual_holdout_reads_by_graph": 0,
    }
    validate_public_source_ast(base, proof)
    return proof


def synthetic_proof(base: types.ModuleType) -> dict:
    owners = {
        role: base.synthetic_owner(pin, 945000 + index)
        for index, (role, pin) in enumerate(PUBLIC_ORACLE.items())
    }
    return make_public_proof(
        base, owners, synthetic_contract(base), synthetic_source_ast(base),
    )


def self_test(previous: types.ModuleType, v43: types.ModuleType,
              v42: types.ModuleType, v41: types.ModuleType,
              v40: types.ModuleType, base: types.ModuleType) -> dict:
    history = previous.self_test(v43, v42, v41, v40, base)
    base.need(
        history.get("status") == "PASS"
        and history.get("rejected_hostile_control_count") == 1132
        and history.get("reference_archive_gzip_inflation_count") == 0
        and history.get("matching_archive_gzip_inflation_count") == 0
        and history.get("source_build_archive_gzip_inflation_count_by_graph")
        == 0
        and history.get("public_entrypoint_status") == PUBLIC_STATUS,
        "first preserve all 1,132 exact pushed V44 source-only hostile gates",
    )
    rejected = 0
    with base.SourceOnlyWall() as wall:
        proof = synthetic_proof(base)
        for field, value in proof.items():
            hostile = copy.deepcopy(proof)
            hostile[field] = v43.forged_value(base, value)
            try:
                validate_public_proof(base, hostile)
            except (
                base.GraphError, TypeError, ValueError,
                KeyError, AttributeError, RecursionError,
            ):
                rejected += 1
            else:
                raise base.GraphError(
                    "accepted invented public-oracle result: " + field,
                )
        for role in ("source", "protocol", "contract"):
            for field, value in proof[role].items():
                hostile = copy.deepcopy(proof)
                hostile[role][field] = v43.forged_value(base, value)
                try:
                    validate_public_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted a substituted public oracle " + role,
                    )
        for group in ("source_ast",):
            for field, value in proof[group].items():
                hostile = copy.deepcopy(proof)
                hostile[group][field] = v43.forged_value(base, value)
                try:
                    validate_public_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted fabricated physical isolation: " + field,
                    )
        for group in (
            "original_correctness", "boundaries",
            "future_public_winner_policy", "owners",
        ):
            for field, value in proof["complete_frozen_contract"][group].items():
                hostile = copy.deepcopy(proof)
                hostile["complete_frozen_contract"][group][field] = (
                    v43.forged_value(base, value)
                )
                try:
                    validate_public_proof(base, hostile)
                except (
                    base.GraphError, TypeError, ValueError,
                    KeyError, AttributeError, RecursionError,
                ):
                    rejected += 1
                else:
                    raise base.GraphError(
                        "accepted forged public contract " + group + ":" + field,
                    )
        for index, row in enumerate(public_rows()):
            hostile = copy.deepcopy(proof)
            hostile["public_case_rows"][index]["observed_status"] = (
                "PASS" if row["observed_status"] != "PASS" else "FAIL"
            )
            try:
                validate_public_proof(base, hostile)
            except (base.GraphError, TypeError, ValueError, KeyError):
                rejected += 1
            else:
                raise base.GraphError("accepted invented public check: " + row["id"])
        probes = (
            ("filesystem", lambda: builtins.open("forbidden-v45")),
            ("filesystem", lambda: os.open("forbidden-v45", os.O_RDONLY)),
            ("filesystem", lambda: os.stat("forbidden-v45")),
            ("write", lambda: os.mkdir("forbidden-v45")),
            ("process", lambda: subprocess.run(("forbidden-v45",))),
            ("process", lambda: subprocess.Popen(("forbidden-v45",))),
            ("process", lambda: os.execv("/forbidden-v45", [])),
        )
        for kind, action in probes:
            before = wall.blocked[kind]
            try:
                action()
            except base.GraphError:
                base.need(
                    wall.blocked[kind] == before + 1,
                    "physically block the actual V45 source-only " + kind,
                )
            else:
                raise base.GraphError("a genuine V45 physical effect escaped")
        base.need(rejected >= 100,
                  "reject every public matrix, owner and isolation forgery")
        return {
            "schema": SCHEMA + "-source-only-self-test",
            "version": 45,
            "status": "PASS",
            "synthetic_only": True,
            "previous_v44_hostile_controls":
                history["rejected_hostile_control_count"],
            "new_v45_hostile_controls": rejected,
            "rejected_hostile_control_count":
                history["rejected_hostile_control_count"] + rejected,
            "blocked_effects_by_kind": dict(wall.blocked),
            "actual_public_oracle_read_by_self_test": 0,
            "actual_public_imports_by_graph": 0,
            "actual_candidate_imports_by_graph": 0,
            "actual_native_libraries_loaded_by_graph": 0,
            "reference_archive_gzip_inflation_count": 0,
            "matching_archive_gzip_inflation_count": 0,
            "source_build_archive_gzip_inflation_count_by_graph": 0,
            "actual_candidate_workers_started_by_graph": 0,
            "actual_reference_workers_started_by_graph": 0,
            "actual_clock_samples_by_graph": 0,
            "actual_hidden_cases_read_by_graph": 0,
            "full_case_denominator": 31237,
            "suite_count": 13,
            "private_waiver_count": 13,
            "authenticated_evidence_owner_lower_bound": 166,
            "authenticated_history_reference_lower_bound": 171,
            "first_party_source_inventory_family_count": 6,
            "frozen_corrected_runner_source_family_count": 2,
            "actually_runnable_candidate_family_count": 0,
            "qualified_candidate_count": 0,
            **public_fields(proof),
        }


def publish(base: types.ModuleType, path: str, raw: bytes) -> None:
    base.need(
        path in {
            OUTPUT + ".inputs.json", OUTPUT + ".json", OUTPUT + ".svg",
        }
        and type(raw) is bytes and 0 < len(raw) <= base.OWNER_LIMIT,
        "write only the three expressly authorized new V45 graph owners",
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(ROOT / path), flags, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            base.need(type(written) is int and written > 0,
                      "reject an incomplete source-only V45 output")
            remaining = remaining[written:]
        os.fsync(descriptor)
        owner = os.fstat(descriptor)
        base.need(
            owner.st_uid == os.geteuid()
            and owner.st_nlink == 1
            and owner.st_size == len(raw)
            and stat.S_IMODE(owner.st_mode) == 0o600,
            "publish one exact private, independently ownable V45 graph",
        )
    finally:
        os.close(descriptor)
    directory = os.open(
        str(ROOT / Path(path).parent),
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    observed, _ = base.read_owner(path, base.digest(raw), len(raw), private=True)
    base.need(observed == raw,
              "re-authenticate all complete published V45 output bytes")


def result(base: types.ModuleType, snapshot: dict,
           outputs: dict[str, bytes], source: str,
           *, written: bool, suffix: str) -> dict:
    return {
        "schema": SCHEMA + suffix,
        "version": 45,
        "status": "PASS",
        "source_sha256": source,
        "inputs_sha256": base.digest(outputs[OUTPUT + ".inputs.json"]),
        "summary_sha256": base.digest(outputs[OUTPUT + ".json"]),
        "svg_sha256": base.digest(outputs[OUTPUT + ".svg"]),
        "previous_overview_version": 44,
        **{
            "previous_overview_" + role + "_sha256": owner[1]
            for role, owner in V44.items()
        },
        "actual_failure_sha256":
            snapshot["actual_rust_failure_evidence_sha256"],
        "actual_observation_sha256":
            snapshot["actual_rust_observed_effects_sha256"],
        "rust_v7_source_sha256":
            snapshot["corrected_rust_v7_source_sha256"],
        "rust_v7_protocol_sha256":
            snapshot["corrected_rust_v7_protocol_sha256"],
        "rust_v7_contract_sha256":
            snapshot["corrected_rust_v7_contract_sha256"],
        "outputs_written": written,
        **public_fields(snapshot["public_entrypoint_source_oracle"]),
        **{
            key: copy.deepcopy(snapshot[key])
            for key in (
                "actual_rust_controller_status",
                "actual_rust_controller_process_count",
                "actual_rust_attempted_suite_count",
                "actual_rust_started_suite_count",
                "actual_rust_completed_suite_count",
                "actual_rust_candidate_workers",
                "actual_rust_native_activations",
                "actual_rust_source_build_archive_read_count",
                "actual_rust_source_build_archive_gzip_inflation_count",
                "actual_rust_source_build_archive_compressed_bytes",
                "actual_rust_source_build_archive_uncompressed_bytes",
                "actual_rust_controller_ledger_omits_source_build_archive_effect",
                "actual_rust_matching_archive_read_count",
                "actual_rust_reference_archive_read_count",
                "actual_rust_semantic_mismatch_count",
                "corrected_rust_v7_actual_candidate_workers",
                "corrected_rust_v7_candidate_matching_status",
                "corrected_rust_v7_all_worker_and_recovery_source_wall_tested",
                "corrected_rust_v7_current_evidence_owner_lower_bound",
                "corrected_rust_v7_current_history_reference_lower_bound",
                "corrected_rust_v7_future_evidence_owner_lower_bound",
                "corrected_rust_v7_future_history_reference_lower_bound",
                "corrected_rust_v7_future_publication_distinct_owner_count",
                "frozen_corrected_runner_source_family_count",
                "frozen_corrected_runner_source_families",
                "actually_runnable_candidate_family_count",
                "actually_runnable_candidate_families",
                "first_party_source_inventory_family_count",
                "other_corrected_candidate_family_count",
                "pending_corrected_candidate_families",
                "corrected_c_matching_status",
                "corrected_rust_matching_status",
                "qualified_candidate_count",
                "authenticated_evidence_owner_lower_bound",
                "authenticated_history_reference_lower_bound",
                "exact_whole_repository_evidence_owner_count",
                "exact_whole_repository_reference_count",
                "full_case_denominator",
                "suite_count",
                "private_waiver_count",
            )
        },
    }


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--render", action="store_true")
    modes.add_argument("--verify-frozen-context", action="store_true")
    parser.add_argument("--source-sha256")
    parser.add_argument("--source-bytes", type=int)
    parser.add_argument("--previous-source-sha256")
    parser.add_argument("--previous-inputs-sha256")
    parser.add_argument("--previous-summary-sha256")
    parser.add_argument("--previous-svg-sha256")
    parser.add_argument("--failure-sha256")
    parser.add_argument("--observation-sha256")
    parser.add_argument("--rust-source-sha256")
    parser.add_argument("--rust-protocol-sha256")
    parser.add_argument("--rust-contract-sha256")
    parser.add_argument("--public-module-sha256")
    parser.add_argument("--public-module-bytes", type=int)
    parser.add_argument("--public-project-sha256")
    parser.add_argument("--public-project-bytes", type=int)
    parser.add_argument("--public-oracle-source-sha256")
    parser.add_argument("--public-oracle-protocol-sha256")
    parser.add_argument("--public-oracle-contract-sha256")
    parser.add_argument("--public-case-matrix-sha256")
    parser.add_argument("--inputs-sha256")
    parser.add_argument("--summary-sha256")
    parser.add_argument("--svg-sha256")
    options = parser.parse_args(arguments)
    try:
        previous, v43, v42, v41, v40, base = load_v44()
        if options.self_test:
            base.need(
                all(
                    getattr(options, name) is None
                    for name in (
                        "source_sha256", "source_bytes",
                        "previous_source_sha256", "previous_inputs_sha256",
                        "previous_summary_sha256", "previous_svg_sha256",
                        "failure_sha256", "observation_sha256",
                        "rust_source_sha256", "rust_protocol_sha256",
                        "rust_contract_sha256", "public_module_sha256",
                        "public_module_bytes", "public_project_sha256",
                        "public_project_bytes", "public_oracle_source_sha256",
                        "public_oracle_protocol_sha256",
                        "public_oracle_contract_sha256",
                        "public_case_matrix_sha256", "inputs_sha256",
                        "summary_sha256", "svg_sha256",
                    )
                ),
                "synthetic-only V45 self-tests cannot read actual evidence "
                "owners or accept context pins",
            )
            sys.stdout.buffer.write(base.canonical(
                self_test(previous, v43, v42, v41, v40, base),
            ))
            return 0
        snapshot, pairs = build(
            previous, v43, v42, v41, v40, base, options,
        )
        outputs = dict(pairs)
        source = base.checked(options.source_sha256, "exact complete V45")
        if options.render:
            base.need(
                options.inputs_sha256 is None
                and options.summary_sha256 is None
                and options.svg_sha256 is None,
                "render exactly three new authorized V45 graph owners once",
            )
            for path, raw in pairs:
                publish(base, path, raw)
            sys.stdout.buffer.write(base.canonical(result(
                base, snapshot, outputs, source,
                written=True, suffix="-published",
            )))
            return 0
        expected = {
            OUTPUT + ".inputs.json": base.checked(
                options.inputs_sha256, "exact V45 public observation inputs",
            ),
            OUTPUT + ".json": base.checked(
                options.summary_sha256, "exact V45 public observation summary",
            ),
            OUTPUT + ".svg": base.checked(
                options.svg_sha256, "exact readable V45 public mini-bar",
            ),
        }
        for path, fingerprint in expected.items():
            actual, _ = base.read_owner(
                path, fingerprint, len(outputs[path]), private=True,
            )
            base.need(
                actual == outputs[path],
                "reproduce all V45 failed-public-observation graph bytes",
            )
        sys.stdout.buffer.write(base.canonical(result(
            base, snapshot, outputs, source,
            written=False, suffix="-read-only-frozen-context",
        )))
        return 0
    except (
        ValueError, OSError, TypeError, EOFError, KeyError,
        AttributeError, RecursionError,
    ) as error:
        sys.stderr.write("current V45 overview rejected: " + str(error) + "\n")
        return 2
    except Exception as error:
        if type(error).__name__ == "GraphError":
            sys.stderr.write("current V45 overview rejected: " + str(error) + "\n")
            return 2
        raise


if __name__ == "__main__":
    raise SystemExit(main())
