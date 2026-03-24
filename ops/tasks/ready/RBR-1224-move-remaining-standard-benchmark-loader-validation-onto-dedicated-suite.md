Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining standard-benchmark manifest loader/materialization validation block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated validation owner in `tests/benchmarks/test_benchmark_manifest_validation.py`, so the giant combined benchmark suite stops owning validation-only coverage that does not depend on its broader source-tree anchor wiring.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_manifest_validation.py` so it becomes the owner for the current loader/materialization validation-only block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated validation file without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_materializes_callable_replacement_descriptors`
  - `test_standard_benchmark_manifest_loader_rejects_duplicate_ids`
  - `test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads`
- Keep the extracted loader/materialization surface pinned to current live behavior exactly:
  - preserve the current `python-benchmark-loader-contract` manifest round-trip coverage for numbered callable replacements, named callable replacements, and bytes callable constants, including the same `workload_to_payload(...)` expectations and direct callable execution against `re.search(...)`;
  - preserve the current duplicate-id rejection surface exactly for both duplicate manifest ids and duplicate workload ids via `load_manifests(...)`; and
  - preserve the current bytes template replacement materialization coverage for the numbered and named nested-group conditional benchmark workloads, including the existing `pattern_payload()`, `haystack_payload()`, replacement payload, and `workload_to_payload(...)` expectations.
- Reuse the existing dedicated validation suite instead of adding another layer:
  - keep `tests/benchmarks/test_benchmark_manifest_validation.py` as the owner for this extracted block;
  - keep using the existing `_write_test_manifest(...)`, `load_manifest(...)`, `load_manifests(...)`, `workload_to_payload(...)`, and related validation helpers already in the benchmark test tree; and
  - do not add a new `*_support.py` module, a new sibling benchmark contract suite, or wrappers/aliases left behind in the combined suite.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_materializes_callable_replacement_descriptors or standard_benchmark_manifest_loader_rejects_duplicate_ids or standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads'`
- `bash -lc "! rg -n 'def test_(standard_benchmark_manifest_materializes_callable_replacement_descriptors|standard_benchmark_manifest_loader_rejects_duplicate_ids|standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1224` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/` currently contains only `RBR-1223`, and `ops/tasks/in_progress/` plus `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1224|RBR-1225|RBR-1226|RBR-1227" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical notes inside completed task files and did not reveal a live reservation or sibling task at `RBR-1224`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 0`; and
  - the latest anomaly is a requeued feature task (`RBR-1223`) rather than inherited-dirty checkpoint churn or a stalled post-task refresh/commit path.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is still `11337` lines in this run;
  - `rg -n 'def test_(standard_benchmark_manifest_materializes_callable_replacement_descriptors|standard_benchmark_manifest_loader_rejects_duplicate_ids|standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` currently matches only the combined-suite copies at lines `11030`, `11192`, and `11279`;
  - `tests/benchmarks/test_benchmark_manifest_validation.py` already owns adjacent benchmark manifest and payload validation coverage after `RBR-1194` and `RBR-1196`; and
  - this cleanup removes one more validation-only block from the combined suite instead of introducing another owner or helper layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_materializes_callable_replacement_descriptors or standard_benchmark_manifest_loader_rejects_duplicate_ids or standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads'` returned `3 passed, 162 deselected in 0.15s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those three tests still live in the combined suite.
