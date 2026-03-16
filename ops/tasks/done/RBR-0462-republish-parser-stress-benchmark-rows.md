# RBR-0462: Republish the parser-stress benchmark rows as measured source-tree timings

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark expectations and published benchmark report now that the parser-stress compile proxy is live behind `rebar.compile()`, flipping the existing `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` rows from explicit known gaps to measured timings without widening the manifest frontier.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` updates only the existing shared scorecard/combined-manifest expectations that still classify the now-live parser-stress rows as gaps:
  - `compile-matrix` no longer treats `compile-parser-stress-cold` as a representative known gap and no longer expects the old "outside the current rebar compile surface" note for that row;
  - `regression-pack-smoke` keeps the current workload order `("regression-import-cold", "regression-parser-atomic-lookbehind-cold")` but treats `regression-parser-atomic-lookbehind-cold` as measured rather than as a representative known gap; and
  - `regression-pack-full` plus the shared `regression-matrix` combined-manifest expectation leave `regression-parser-bytes-backreference-purged` as the only remaining explicit `regression-matrix` gap.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` change only as needed so the full verification path passes against the updated measured/gap distribution; do not add a new benchmark expectation table, a manifest-local wrapper, or another benchmark test module.
- `reports/benchmarks/latest.py` is regenerated honestly and moves from `588` published workloads with `570` real `rebar` timings and `18` known-gap workloads to `588` published workloads with `572` real `rebar` timings and `16` known-gap workloads:
  - `compile-matrix` now reports all `6` workloads as measured with `0` known gaps;
  - `regression-matrix` now reports `4` measured workloads with `1` known gap; and
  - `regression-parser-bytes-backreference-purged` remains the only explicit `regression-matrix` known gap.
- Keep the task bounded to the existing `compile-matrix` and `regression-matrix` surfaces. Do not add benchmark workload rows, create another manifest, change `python/rebar_harness/benchmarks.py`, touch correctness fixtures/reports, or widen compile support in Rust or `python/rebar/__init__.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/compile_matrix.py --report .rebar/tmp/rbr-0462-compile-matrix.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0462-regression-matrix.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-publication only. The parser-stress compile behavior is already live; do not spend this run widening parser support or adding a second correctness publication step for the same `str` pattern.
- Preserve the existing workload ids, workload order, shared benchmark surfaces, and source-tree-shim publication path. This task should only bring the expectations and tracked report back in sync with the live runner output.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/compile_matrix.py --report .rebar/tmp/feature-planning-compile-matrix-probe.py` reports `6` total workloads with `6` measured and `0` known gaps in the current checkout, confirming `compile-parser-stress-cold` is already live as a measured timing.
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/feature-planning-regression-matrix-probe.py` reports `5` total workloads with `4` measured and `1` known gap, confirming `regression-parser-atomic-lookbehind-cold` is already measured and `regression-parser-bytes-backreference-purged` is now the lone remaining `regression-matrix` gap.
- `ops/tasks/blocked/RBR-0463-collapse-quantified-nested-group-benchmark-representatives-onto-slice-expectations.md` is blocked only because the full benchmark expectation tests still describe those two parser-stress rows as gaps.
- The concrete surviving follow-on after this benchmark refresh is `RBR-0464`, which should publish the exact bytes parser compile proxy `b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}"` on the shared `parser-matrix` correctness surface before Rust-backed parity or later regression benchmark catch-up reopen that bytes backreference slice.

## Completion
- 2026-03-16: Updated the shared source-tree benchmark expectations so `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` are treated as measured rows, while `regression-parser-bytes-backreference-purged` remains the lone `regression-matrix` known gap.
- 2026-03-16: Refreshed the adjacent `compile-matrix` workload note so the tracked publication no longer labels `compile-parser-stress-cold` as an explicit known gap after the measured timing landed.
- 2026-03-16: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/compile_matrix.py --report .rebar/tmp/rbr-0462-compile-matrix.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0462-regression-matrix.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- 2026-03-16: Republished the tracked benchmark scorecard at `reports/benchmarks/latest.py` with `588` total workloads, `572` measured `rebar` timings, and `16` known gaps; the tracked `compile-matrix` section now reports `6` measured workloads with `0` known gaps, and the tracked `regression-matrix` section now reports `4` measured workloads with `1` known gap (`regression-parser-bytes-backreference-purged`).
