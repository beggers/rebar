# RBR-1091: Collapse parametrize id lambdas in source-tree benchmark suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `pytest.mark.parametrize(..., ids=lambda ...)` adapters from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the benchmark contract suite names its parametrized cases through named same-file helpers or a strictly smaller equivalent instead of four one-purpose anonymous wrappers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer contains any of these parametrize id lambdas:
  - `ids=lambda selector: selector`
  - `ids=lambda contract_case: contract_case.case_id`
  - `ids=lambda anchor_lane: anchor_lane.case_id`
  - `ids=lambda definition: definition.name`
- Replace that wrapper layer with named same-file helpers, or a strictly smaller equivalent, while preserving the current parametrized test ownership surface intact:
  - `test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation`
  - `test_compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases`
  - `test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids`
- Keep the existing case ids stable after the cleanup:
  - selector ids still render as the selector string;
  - compiled-pattern compile contract rows still render as `contract_case.case_id`;
  - compiled-pattern anchor lanes still render as `anchor_lane.case_id`; and
  - standard benchmark definition rows still render as `definition.name`.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'`
- `bash -lc "! rg -n 'ids=lambda selector: selector|ids=lambda contract_case: contract_case\\.case_id|ids=lambda anchor_lane: anchor_lane\\.case_id|ids=lambda definition: definition\\.name' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the anonymous id-wrapper layer over introducing another helper registry, support module, or detached abstraction tier.
- Keep the current parametrized test names, case ordering, manifest ownership, and expected ids intact.
- Do not broaden this into general lambda cleanup elsewhere in the file; keep the task bounded to the four `ids=` adapters above.

## Notes
- `RBR-1091` is the next available unreserved task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1090`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1091` task file; and
  - `rg -n 'RBR-1091|RBR-1092|RBR-1093|RBR-1094' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'ids=lambda selector: selector|ids=lambda contract_case: contract_case\\.case_id|ids=lambda anchor_lane: anchor_lane\\.case_id|ids=lambda definition: definition\\.name' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the four remaining trivial id adapters at lines `11051`, `17520`, `17587`, and `19971` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_contract_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'` returned `17 passed, 715 deselected` in this run.
