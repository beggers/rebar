# RBR-0458: Collapse slice-covered benchmark representatives onto shared expectations

Status: blocked
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining manifest-level source-tree benchmark representative workload lists that only copy workload ids already owned by shared combined-suite slice expectations, so benchmark coverage is described in one place instead of two.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one small helper or extends the current representative-id resolution path so a manifest can derive `representative_measured_workload_ids` from existing shared expectation data already stored in:
  - `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - `shape_expectation` entries inside `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`
- Keep the scope to the exact manifests whose explicit measured representative ids are already fully restated elsewhere in the file:
  - `grouped-alternation-callable-replacement-boundary`
  - `branch-local-backreference-boundary`
  - `conditional-group-exists-boundary`
- After the refactor, those three entries in `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` no longer duplicate the current measured workload tuples under `representative_measured_workload_ids`; the shared slice expectations become the source of truth for those rows.
- `source_tree_scorecard_case(...)` still returns representative measured workload ids for the single-manifest scorecard cases that depend on those manifests today:
  - `branch-local-backreference-boundary`
  - `conditional-group-exists-boundary`
  Those ids must now be derived from the shared slice expectation surface rather than copied into either `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` or `SOURCE_TREE_SCORECARD_EXPECTATIONS`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` continues to validate the same measured rows for the three scoped manifests through the existing combined-suite path; do not move those copied tuples into a second helper table or open-code them inside the test file.
- Leave partially covered manifests alone in this run. In particular, do not broaden the cleanup into:
  - `module-boundary`
  - `pattern-boundary`
  - `nested-group-alternation-boundary`
  - `nested-group-replacement-boundary`
  - `nested-group-callable-replacement-boundary`
  - `wider-ranged-repeat-quantified-group-boundary`
  - `open-ended-quantified-group-boundary`
  - representative known-gap wiring such as `regression-matrix`
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Prefer extending the existing `representative_measured_workload_ids(...)`, `source_tree_scorecard_case(...)`, or nearby expectation helpers over adding another registry, support module, or generated file.
- Keep the task structural only. Do not change benchmark workload manifests, workload ids, known-gap counts, manifest selectors, benchmark harness runtime behavior, published reports, README text, or tracked state files.
- Preserve current assertion semantics and measured-row coverage; the value of this task is deleting duplicate expectation data, not broadening or shrinking the published benchmark surface.

## Notes
- `RBR-0457` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the feature-owned verbose `module.compile()` benchmark catch-up, so this architecture cleanup starts at `RBR-0458`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T08:12:09+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply.
- JSON counts are still fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, the duplicated representative-id copies are concentrated at:
  - `tests/benchmarks/benchmark_expectations.py:288-295` for `grouped-alternation-callable-replacement-boundary`, which restates the `former-gap-callable-replacement-rows` slice at `tests/benchmarks/benchmark_expectations.py:1174-1194`
  - `tests/benchmarks/benchmark_expectations.py:389-400` for `branch-local-backreference-boundary`, which restates the `broader-range-open-ended-conditional-branch-local-backreference` slice at `tests/benchmarks/benchmark_expectations.py:685-708`
  - `tests/benchmarks/benchmark_expectations.py:566-598` for `conditional-group-exists-boundary`, which restates the four slice blocks at `tests/benchmarks/benchmark_expectations.py:1217-1345`
- `tests/benchmarks/benchmark_expectations.py` is `1831` lines long in the current checkout, so keeping slice-covered representative ids single-sourced is still a worthwhile bounded simplification after `RBR-0454` and `RBR-0456`.

## Run Notes
- Landed the scoped refactor in `tests/benchmarks/benchmark_expectations.py`: the three duplicated manifest-level `representative_measured_workload_ids` tuples are now empty, and the new `source_tree_combined_manifest_representative_measured_workload_ids(...)` helper derives those rows from shared slice/shape expectations instead.
- Added focused regression coverage in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the branch-local and conditional single-manifest scorecards still expose slice-backed representative ids and the three scoped manifests stay single-sourced through the shared slice expectation surface.
- Scoped verification passed with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k slice_backed` (`2 passed`).
- The exact acceptance command reran after the refactor and now fails only on summary assertions (`28 failed, 6 passed, 365 subtests passed`). The blocker is unrelated pre-existing benchmark expectation drift outside this task's allowed scope: live source-tree runs already report `regression-module-compile-verbose-purged` as `measured`, while `tests/benchmarks/benchmark_expectations.py` and `reports/benchmarks/latest.py` still count that workload under the `regression-matrix` known-gap surface reserved for `RBR-0457`. That single known-gap mismatch keeps the two benchmark files red on expected summary counts even though the slice-backed representative-id refactor itself is behaving correctly.
