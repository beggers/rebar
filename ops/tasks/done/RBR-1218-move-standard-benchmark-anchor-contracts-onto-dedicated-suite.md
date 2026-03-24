# RBR-1218: Move standard benchmark anchor contracts onto dedicated suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining live standard-benchmark anchor contract block that still lives inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that owner surface onto the existing `tests/benchmarks/standard_benchmark_anchor_support.py` and `tests/benchmarks/test_standard_benchmark_anchor_support.py` pair, so the giant combined benchmark suite stops owning another generic anchor-contract layer.

## Deliverables
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/standard_benchmark_anchor_support.py` and `tests/benchmarks/test_standard_benchmark_anchor_support.py` so they become the owner for the current live standard-benchmark anchor contract surface now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move the current definition and parametrization plumbing that exists only to support that block, including the live `STANDARD_BENCHMARK_DEFINITIONS` contract set and the minimal helper selectors/builders that feed its anchor-only assertions, onto the dedicated standard-benchmark anchor owner instead of leaving them in the combined boundary suite.
- Move these existing tests into `tests/benchmarks/test_standard_benchmark_anchor_support.py` without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_keeps_expected_workloads_in_scope`
  - `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases`
  - `test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids`
  - `test_standard_benchmark_special_unanchored_workloads_stay_explicit`
  - `test_standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases`
  - `test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids`
  - `test_standard_benchmark_workload_callbacks_match_anchor_case_results`
  - `test_standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch`
- Keep the extracted contract surface pinned to current live behavior exactly:
  - preserve the current manifest paths, workload ids, case ids, direct-parity supplemental case coverage, callback-anchor subsets, legacy-anchor subsets, special-unanchored workload handling, and manual CPython dispatch expectations;
  - preserve the current pytest parametrization ids and test names apart from relocating them; and
  - keep using the existing published-manifest/load-manifest/anchor-support helpers instead of inventing another test-only representation.
- Reuse the existing dedicated suite instead of adding another architectural layer:
  - keep `tests/benchmarks/standard_benchmark_anchor_support.py` plus `tests/benchmarks/test_standard_benchmark_anchor_support.py` as the owner for this benchmark anchor-contract surface;
  - do not add a new `*_support.py` module or another sibling contract suite for this extraction; and
  - do not widen this cleanup into descriptor-materialization tests, duplicate-id loader validation, pattern-split signature normalization, bytes-template replacement contracts, benchmark harness implementation code, or workload-manifest edits.
- Delete the moved definitions/tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the three files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_keeps_expected_workloads_in_scope or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'`
- `bash -lc "! rg -n 'def test_(standard_benchmark_manifest_keeps_expected_workloads_in_scope|standard_benchmark_workloads_stay_anchored_to_published_correctness_cases|standard_benchmark_workloads_stay_pinned_to_exact_case_ids|standard_benchmark_special_unanchored_workloads_stay_explicit|standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases|standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids|standard_benchmark_workload_callbacks_match_anchor_case_results|standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1218` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run before this task was added; and
  - `rg -n 'RBR-1218|RBR-1219|RBR-1220' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this range was not reserved by planning-owned frontier notes.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed `RBR-1216` and `RBR-1217` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `rg -n 'def test_(standard_benchmark_manifest_keeps_expected_workloads_in_scope|standard_benchmark_workloads_stay_anchored_to_published_correctness_cases|standard_benchmark_workloads_stay_pinned_to_exact_case_ids|standard_benchmark_special_unanchored_workloads_stay_explicit|standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases|standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids|standard_benchmark_workload_callbacks_match_anchor_case_results|standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_standard_benchmark_anchor_support.py` currently matches only the combined-suite block at lines `12204`, `12230`, `12242`, `12254`, `12274`, `12314`, `12330`, and `12345`;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` already exists as the dedicated owner for this support layer; and
  - this task removes one misplaced anchor-contract block instead of creating another sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_keeps_expected_workloads_in_scope or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'` returned `195 passed, 159 deselected in 0.35s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those eight tests still live in the combined suite.

## Completion
- Moved the eight standard benchmark anchor-contract tests into `tests/benchmarks/test_standard_benchmark_anchor_support.py`, added lazy owner-side parametrization/helpers in `tests/benchmarks/standard_benchmark_anchor_support.py`, and removed the relocated tests plus the public parametrization surface from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification on 2026-03-24:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_keeps_expected_workloads_in_scope or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'` returned `195 passed, 159 deselected in 0.36s`.
  - `bash -lc \"! rg -n 'def test_(standard_benchmark_manifest_keeps_expected_workloads_in_scope|standard_benchmark_workloads_stay_anchored_to_published_correctness_cases|standard_benchmark_workloads_stay_pinned_to_exact_case_ids|standard_benchmark_special_unanchored_workloads_stay_explicit|standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases|standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids|standard_benchmark_workload_callbacks_match_anchor_case_results|standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py\"` succeeded.
