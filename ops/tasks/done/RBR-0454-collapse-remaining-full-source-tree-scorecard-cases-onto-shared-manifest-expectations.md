# RBR-0454: Collapse the remaining full source-tree scorecard cases onto shared manifest expectations

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining duplicated full-scorecard bookkeeping in `tests/benchmarks/benchmark_expectations.py` so all full source-tree scorecard cases derive their shared summary and per-manifest known-gap metadata from the live manifest documents plus `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` instead of keeping a second hand-maintained copy inside `SOURCE_TREE_SCORECARD_EXPECTATIONS`.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one small helper or declarative case-definition shape for full source-tree scorecard cases that is built on the existing benchmark expectation surface rather than a new registry, support module, or generated file.
- The helper is used for the current full source-tree scorecard cases only:
  - `compile-matrix`
  - `post-parser-workflows`
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
  - `branch-local-backreference-boundary`
  - `conditional-group-exists-boundary`
  - `regression-pack-full`
- For those seven cases, `SOURCE_TREE_SCORECARD_EXPECTATIONS` no longer open-codes the shared full-scorecard structure that the file already knows how to derive:
  - `selection_mode` fixed at `"full"`
  - `expected_summary`
  - `manifest_expectations` blocks whose only payload is per-manifest `known_gap_count`
- The derived values come from the live manifest documents plus `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, and `source_tree_scorecard_case(...)` still returns the same public case shape consumed by `tests/benchmarks/test_source_tree_benchmark_scorecards.py`.
- Keep the case-local frontier explicit where it is still intentionally narrower than the derived shared metadata:
  - `compile-matrix` still keeps its current `expected_first_deferred`, `representative_measured_workload_ids`, `representative_known_gap_workload_ids`, and `workload_note_substrings` local to the case definition.
  - `post-parser-workflows` still keeps its current representative measured-workload and known-gap id tuples local to the case definition.
  - `nested-group-replacement-boundary` and `nested-group-callable-replacement-boundary` still keep their current shorter representative measured-workload subsets local instead of silently inheriting the larger combined-manifest representative sets.
  - `regression-pack-full` still keeps its current representative measured-workload and known-gap id tuples local to the case definition.
- Keep the refactor bounded to full scorecard cases. Do not broaden this run into:
  - smoke-only cases such as `compile-smoke` or `regression-pack-smoke`
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
  - `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - benchmark workloads, workload ids, manifest order, or known-gap counts
- The cleanup stays structural only:
  - no benchmark workload rows, manifest selections, representative workload ids, deferred metadata, workload-note substring assertions, or public `source_tree_scorecard_case(...)` fields broaden or shrink
  - no changes are made to `benchmarks/workloads/*.py`, `python/rebar_harness/benchmarks.py`, Rust code, published reports, README text, or tracked state files beyond this task file
- If `tests/benchmarks/test_source_tree_benchmark_scorecards.py` needs edits, keep them limited to consuming the same returned case shape more directly; do not add a second helper registry in the test file.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Prefer extending the existing `SOURCE_TREE_SCORECARD_EXPECTATIONS` resolver path over adding another expectation table. This cleanup should make one file more legible, not create a new place to look.
- Preserve the current explicit manifest order for `post-parser-workflows` and `regression-pack-full`. The value of this task is deleting duplicate structure, not hiding case sequencing.
- Keep smoke-only scorecard cases manual for now. This run should delete the remaining full-case duplication without widening into a broader benchmark-expectation rewrite.

## Notes
- `RBR-0453` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned verbose `module.compile()` correctness slice, so this architecture cleanup starts at `RBR-0454`.
- The runtime dashboard is current and clean (`Generated: 2026-03-16T06:57:37+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0452` already collapsed the five single-manifest full scorecard cases onto the shared manifest-expectation surface and explicitly left the multi-manifest full cases out of scope.
- In the current checkout, `tests/benchmarks/benchmark_expectations.py` is still `1761` lines long, and the two remaining manual full-case definitions are concentrated at:
  - `post-parser-workflows`
  - `regression-pack-full`
  Those two cases still restate `selection_mode`, summary totals, and per-manifest `known_gap_count` bookkeeping that can be derived from the same live manifest documents and shared expectation map already used by the combined-boundary path and the single-manifest helper.

## Completion
- 2026-03-16: Replaced the single-manifest-only scorecard case shape with `_full_source_tree_scorecard_case_definition(...)`, and updated all seven scoped full source-tree scorecard cases to derive `manifest_ids`, `selection_mode`, `expected_summary`, and per-manifest `known_gap_count` blocks from the live manifest documents plus `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`.
- 2026-03-16: Kept the intentionally narrower case-local frontier explicit by leaving the local deferred metadata, representative workload ids, and workload-note assertions in place for `compile-matrix`, `post-parser-workflows`, `nested-group-replacement-boundary`, `nested-group-callable-replacement-boundary`, and `regression-pack-full`.
- 2026-03-16: Verified `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed (`4 passed, 394 subtests passed in 19.17s`).
