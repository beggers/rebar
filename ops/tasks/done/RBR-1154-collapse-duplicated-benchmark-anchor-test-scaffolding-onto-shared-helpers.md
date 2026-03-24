## RBR-1154: Collapse duplicated benchmark anchor test scaffolding onto shared helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the duplicated synthetic benchmark-anchor test scaffolding that now lives in both `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_standard_benchmark_anchor_support.py` by moving the shared cache-reset and synthetic object builders onto one test-only helper module, so the benchmark support-contract layer keeps one ordinary helper surface instead of two near-identical local copies.

## Deliverables
- `tests/benchmarks/benchmark_anchor_support_test_helpers.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Add one bounded test-only helper module at `tests/benchmarks/benchmark_anchor_support_test_helpers.py` for the duplicated benchmark-anchor support scaffolding used by both support suites:
  - move the shared cache-reset fixture helper plus the shared synthetic object builders there, covering the current local surface around `anchor_support_cache_guard(...)`, `_synthetic_case(...)`, `_synthetic_workload(...)`, `_synthetic_manifest_loader(...)`, `_synthetic_workload_signature(...)`, `_synthetic_workload_is_included(...)`, and any tiny adjacent helpers those functions require to preserve the current tests verbatim;
  - keep that helper module test-only and ordinary Python; do not turn it into another runtime support layer, registry, or abstraction over the benchmark harness itself; and
  - preserve the current synthetic object shapes and cache-clearing behavior exactly, including the current `source_tree_benchmark_anchor_support` cache reset path.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to consume the shared test helper surface instead of owning the duplicated scaffolding inline:
  - keep the source-tree-specific contract assertions and file-local expectations in place;
  - remove the moved duplicated helper definitions once the shared helper fully covers them; and
  - leave source-tree support implementation coverage focused on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, not the new helper file.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` to consume the same shared test helper surface instead of owning a second copy of that scaffolding:
  - keep `_SyntheticStandardBenchmarkDefinition` and the standard-benchmark-specific assertions local to this file;
  - remove the moved duplicated helper definitions once the shared helper fully covers them; and
  - preserve the current delegated use of `tests/benchmarks/source_tree_benchmark_anchor_support.py` and `tests/benchmarks/standard_benchmark_anchor_support.py` exactly.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the duplicated local test scaffolding over adding another wrapper layer that simply re-exports the same names back into each test file.
- Keep owner-specific contract assertions in their current files; only the duplicated synthetic/cache scaffolding should move.

## Notes
- `RBR-1154` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1154|RBR-1155|RBR-1156|RBR-1157' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation at `RBR-1154`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and cross-file in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py` returned `16 passed` in this run, so the current support-contract slice is already isolated and green;
  - `rg -n '^def (anchor_support_cache_guard|_synthetic_case|_synthetic_workload|_synthetic_manifest_loader|_synthetic_workload_signature|_synthetic_case_signature|_synthetic_workload_is_included)\(' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py` currently shows the same cache-reset and synthetic-helper family defined in both files; and
  - `wc -l tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py` reports `452` and `221` lines respectively in this run, so the duplicated scaffolding is still large enough to justify one bounded extraction.

## Completion
- Added `tests/benchmarks/benchmark_anchor_support_test_helpers.py` as the shared test-only home for the duplicated cache-reset fixture and synthetic benchmark-anchor builders used by both support suites.
- Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_standard_benchmark_anchor_support.py` to import the shared helper surface while keeping source-tree-specific and standard-definition assertions local to their existing files.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py`, which returned `16 passed` in this run.
