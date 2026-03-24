# RBR-1144: Collapse module-workflow signature normalizers onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the duplicated module-workflow argument-signature normalization that still lives separately in the module-workflow parity owner and the source-tree benchmark owner by routing both through one shared helper surface on `tests/python/fixture_parity_support.py` instead of keeping parallel bool/int/indexlike/NOFLAG normalization logic in two files.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that file, for module-workflow signature normalization:
  - cover positional-argument signatures for `bool`, `int`, `str`, `bytes`, and `__index__` carriers;
  - cover keyword-argument signatures for the same carriers plus explicit `re.NOFLAG` preservation;
  - cover the benchmark-owner encoded indexlike payload shape (`{"type": "indexlike", "value": <int>}`) without forcing the benchmark suite to keep its own copy of the normalization logic; and
  - keep the helper path on the existing parity-support module instead of adding another helper file, protocol layer, or registry.
- `tests/python/test_module_workflow_parity_suite.py` stops owning local copies of the shared normalization logic:
  - remove `_workflow_keyword_kwargs_signature(...)`;
  - remove `_workflow_positional_args_signature(...)`;
  - route the existing owner-path selection, publication-contract, and direct-parity checks through the shared helper surface while preserving current tuple layouts, bool-vs-int distinctions, explicit `re.NOFLAG` handling, and indexlike normalization exactly; and
  - keep the existing module-workflow direct-case declarations, publication frontier assertions, and dedicated signature tests intact aside from the helper import path.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops owning its parallel copies of the same normalization logic:
  - remove `_module_workflow_keyword_kwargs_signature(...)`;
  - remove `_module_workflow_positional_args_signature(...)`;
  - route the existing source-tree benchmark workload and correctness signature comparisons through the same shared helper surface while preserving current tuple layouts, encoded-indexlike handling, workload filtering, and keyword-error matching behavior exactly; and
  - do not widen this cleanup into `freeze_signature_value(...)`, benchmark manifest definitions, or workload selection rules.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused shared-helper coverage instead of adding another owner-local contract block:
  - one check proves positional signatures still distinguish `bool`, `int`, and `__index__` carriers while normalizing equivalent indexlike values together;
  - one check proves keyword signatures still preserve explicit `re.NOFLAG` separately from plain integer zero and bool zero; and
  - one check proves the shared helper accepts the benchmark-owner encoded indexlike payload shape without changing the resulting signature tuple.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_preserves_explicit_noflag_carrier tests/python/test_module_workflow_parity_suite.py::test_workflow_positional_args_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_workflow_positional_args_signature_normalizes_indexlike_carriers_by_value tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points`
- `bash -lc "! rg -n '^def (_workflow_keyword_kwargs_signature|_workflow_positional_args_signature|_module_workflow_keyword_kwargs_signature|_module_workflow_positional_args_signature)\\(' tests/python/test_module_workflow_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, correctness fixtures, benchmark workload modules, README text, or tracked ops state prose.
- Prefer deleting the duplicated owner-local normalizers over adding a new abstraction layer that merely renames the same tuple-shaping logic.
- Preserve current signature tuple layouts, tuple ordering, bool/int/indexlike distinctions, explicit `re.NOFLAG` behavior, encoded-indexlike benchmark handling, and benchmark/parity frontier assertions exactly.

## Notes
- `RBR-1144` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in this run;
  - `ops/tasks/blocked/` is empty in this run; and
  - `rg -n "RBR-1144|RBR-1145|RBR-1146|RBR-1147|RBR-1148" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical notes inside completed task files and did not reveal a live reserved future task id at `RBR-1144`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and cross-file:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `_workflow_keyword_kwargs_signature(...)` and `_workflow_positional_args_signature(...)` for owner-path matching and publication checks;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `_module_workflow_keyword_kwargs_signature(...)` and `_module_workflow_positional_args_signature(...)` for source-tree workload/correctness signature matching; and
  - `tests/python/fixture_parity_support.py` already serves as the shared parity-support home for adjacent bundle, generated-spec, direct-bytes, compile-anchor, and native-boundary helpers, so this normalization logic belongs there rather than in another owner-local copy.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_preserves_explicit_noflag_carrier tests/python/test_module_workflow_parity_suite.py::test_workflow_positional_args_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_workflow_positional_args_signature_normalizes_indexlike_carriers_by_value tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_compiled_pattern_module_boundary_validation_matches_manifest_and_payload_entry_points tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points` returned `21 passed in 0.24s`.
  - `git status --short` returned a clean worktree before this task file was written.
