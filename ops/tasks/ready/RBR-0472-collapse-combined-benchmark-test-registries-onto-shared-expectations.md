# RBR-0472: Collapse combined benchmark test registries onto shared expectations

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining test-local registry copies in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined source-tree benchmark suite derives its gapped-manifest coverage and slice-derived representative coverage from the shared expectation surface instead of restating benchmark ids in a second place.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Keep the cleanup on the existing source-tree benchmark expectation path in `tests/benchmarks/benchmark_expectations.py`; do not add a new registry, support module, generated file, or manifest-local benchmark wrapper.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these top-level test-local registries:
  - `SLICE_DERIVED_MANIFEST_IDS`
  - `KNOWN_GAP_WORKLOAD_IDS_BY_MANIFEST`
- The gap-normalization regression in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` now derives its manifest scope and expected workload-id inventories from the canonical raw expectation table in `tests/benchmarks/benchmark_expectations.py`:
  - it still covers every manifest whose raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]` entry exposes `known_gap_workload_ids`;
  - it still asserts that `source_tree_combined_case(manifest_id)["manifest_expectation"]["known_gap_count"]` equals the length of that raw inventory for each such manifest; and
  - it does not re-copy those workload ids into a second dict inside the test module.
- The slice-backed representative regression in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` now derives its manifest scope from shared expectation data rather than a hard-coded tuple:
  - it still exercises the manifests whose representative measured ids are fully slice-derived rather than shape-derived or manifest-local;
  - it still asserts that `source_tree_combined_manifest_representative_measured_workload_ids(manifest_id)` equals the concatenated `expected_workload_ids` from `source_tree_combined_slice_expectations(manifest_id)` for each scoped manifest; and
  - it does not replace the deleted tuple with another manual manifest-id list under a different name.
- If `tests/benchmarks/benchmark_expectations.py` needs a helper to keep the test readable, keep it tiny and derive from the data already stored in:
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `source_tree_combined_slice_manifest_ids()`
  - `source_tree_combined_slice_expectations(...)`
  - `source_tree_combined_manifest_representative_measured_workload_ids(...)`
- Keep the existing public benchmark-expectation behavior intact:
  - zero-gap manifests such as `pattern-boundary` still expose `known_gap_count == 0` and empty representative gap tuples through `source_tree_combined_case(...)`;
  - shape-backed manifests stay on the existing `shape_expectation` path and are not folded into the slice-derived manifest scope; and
  - the current representative workload ordering remains unchanged.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change benchmark harness runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change workload ids, manifest selectors, published reports, README text, or tracked state files beyond this task file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py`
  - `rg -n '^KNOWN_GAP_WORKLOAD_IDS_BY_MANIFEST =|^SLICE_DERIVED_MANIFEST_IDS = \\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.

## Constraints
- Prefer deleting the duplicate registries over moving them into another helper constant. The intended end state is one canonical source of truth in `tests/benchmarks/benchmark_expectations.py`, not a renamed copy.
- Keep the scope to combined source-tree benchmark regression plumbing. Do not broaden this into another scorecard-case refactor, manifest-shape cleanup, benchmark publication refresh, or feature-owned benchmark work.
- Preserve the current subtest intent and ordering. This task should change where the manifest scopes come from, not what the suite verifies.

## Notes
- `RBR-0471` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the feature-owned `IGNORECASE|ASCII` parity follow-on, so this architecture cleanup starts at `RBR-0472`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T13:26:40+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, the remaining duplicate registries are concentrated at:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:32`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:40`
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `500` lines
  - `tests/benchmarks/benchmark_expectations.py`: `1802` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py` passes in the current checkout (`14 passed, 464 subtests passed in 19.56s`).
  - `rg -n '^KNOWN_GAP_WORKLOAD_IDS_BY_MANIFEST =|^SLICE_DERIVED_MANIFEST_IDS = \\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns two matches (`32:SLICE_DERIVED_MANIFEST_IDS = (` and `40:KNOWN_GAP_WORKLOAD_IDS_BY_MANIFEST = {`), which is the exact cleanup this task is meant to remove.
