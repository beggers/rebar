# RBR-0452: Collapse single-manifest source-tree scorecard cases onto shared manifest expectations

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove duplicated benchmark scorecard plumbing in `tests/benchmarks/benchmark_expectations.py` so single-manifest full source-tree scorecard cases derive their shared summary and known-gap metadata from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` instead of restating the same per-manifest structure in a second registry.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one small helper or data shape for single-manifest full source-tree scorecard cases that is built on the existing benchmark expectation surface rather than a new registry, support module, or generated file.
- The helper is used for the current single-manifest full scorecard cases only:
  - `compile-matrix`
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
  - `branch-local-backreference-boundary`
  - `conditional-group-exists-boundary`
- For those five cases, `SOURCE_TREE_SCORECARD_EXPECTATIONS` no longer open-codes the one-manifest bookkeeping that is already shared elsewhere:
  - `manifest_ids` with exactly one manifest id;
  - `selection_mode` fixed at `"full"`;
  - `expected_summary`; and
  - one-entry `manifest_expectations` blocks whose only payload is `known_gap_count`.
- The derived values come from the live manifest document plus `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, and `source_tree_scorecard_case(...)` still returns the same public case shape consumed by `tests/benchmarks/test_source_tree_benchmark_scorecards.py`.
- Keep the suite-local frontier explicit where it is still meaningfully narrower than the combined benchmark surface:
  - `compile-matrix` still keeps its current `expected_first_deferred`, `representative_measured_workload_ids`, `representative_known_gap_workload_ids`, and `workload_note_substrings` local to the scorecard case definition.
  - `nested-group-replacement-boundary` and `nested-group-callable-replacement-boundary` keep their current shorter representative measured-workload subsets local instead of silently inheriting the larger combined-manifest representative sets.
  - `branch-local-backreference-boundary` and `conditional-group-exists-boundary` may reuse the shared representative workload tuples from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` only if the resulting ids stay exactly the same as today's scorecard-case expectations.
- Keep the refactor bounded to single-manifest full cases. Do not broaden this run into:
  - multi-manifest full cases such as `post-parser-workflows` or `regression-pack-full`; or
  - the smoke-only `regression-pack-smoke` case.
- The cleanup stays structural only:
  - no benchmark workloads, workload ids, selected manifest order, known-gap counts, representative workload ids, deferred metadata, or workload-note substring assertions broaden or shrink; and
  - no changes are made to `benchmarks/workloads/*.py`, `python/rebar_harness/benchmarks.py`, Rust code, published reports, README text, or tracked state files beyond this task file.
- If `tests/benchmarks/test_source_tree_benchmark_scorecards.py` needs edits, keep them limited to consuming the same returned case shape more directly; do not add a second helper registry in the test file.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Prefer extending `tests/benchmarks/benchmark_expectations.py` over adding another support layer. This cleanup should make one existing expectation registry more legible, not introduce a third place to look.
- Treat `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` as the source of truth for per-manifest `known_gap_count` on published full-suite manifests once this cleanup lands.
- Preserve the current scorecard-case API. The value of this task is deleting duplicate structure, not forcing downstream test rewrites.

## Notes
- `RBR-0450` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned module-boundary compile benchmark catch-up task, and `RBR-0451` is already filed and done, so this architecture cleanup starts at `RBR-0452`.
- The runtime dashboard is current and clean (`Generated: 2026-03-16T06:21:20+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `tests/benchmarks/benchmark_expectations.py` is now a large benchmark-plumbing file (`1804` lines in the current checkout), and the single-manifest full scorecard cases still duplicate per-manifest summary bookkeeping that the same file already owns in `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`.
- Direct overlap confirmed in the current checkout:
  - `branch-local-backreference-boundary` and `conditional-group-exists-boundary` currently duplicate their representative measured-workload ids exactly across both registries;
  - `compile-matrix`, `nested-group-replacement-boundary`, and `nested-group-callable-replacement-boundary` still duplicate the one-manifest `known_gap_count` and summary structure even where their scorecard-case representative workload subsets intentionally differ from the broader combined-manifest coverage.

## Completion
- 2026-03-16: Added `_single_manifest_source_tree_scorecard_case_definition(...)` plus a small resolver in `tests/benchmarks/benchmark_expectations.py`, so the five scoped full single-manifest scorecard cases now derive `manifest_ids`, `selection_mode`, `expected_summary`, and single-entry `manifest_expectations` from the live manifest document and `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`.
- 2026-03-16: Kept the suite-local frontier explicit where required by leaving `compile-matrix` deferred metadata, representative ids, and workload-note substring assertions local, and by keeping the shorter local representative measured-workload subsets for `nested-group-replacement-boundary` and `nested-group-callable-replacement-boundary`.
- 2026-03-16: Reused the shared representative workload tuples for `branch-local-backreference-boundary` and `conditional-group-exists-boundary` through the combined-manifest expectation surface, without changing the public `source_tree_scorecard_case(...)` payload consumed by `tests/benchmarks/test_source_tree_benchmark_scorecards.py`.
- 2026-03-16: Verified `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`4 passed, 394 subtests passed in 19.12s`).
