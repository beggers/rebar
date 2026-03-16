# RBR-0457: Republish the verbose module.compile regression row as a measured source-tree timing

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared Python-path benchmark publication now that the exact verbose `module.compile()` regression row already measures in the live checkout, so the tracked `regression-matrix` report and shared expectations stop reporting that row as an explicit known gap.

## Deliverables
- `reports/benchmarks/latest.py`
- `tests/benchmarks/benchmark_expectations.py`

## Acceptance Criteria
- Keep the task scoped to the existing `regression-module-compile-verbose-purged` workload in `benchmarks/workloads/regression_matrix.py`; do not add workload rows, widen the regression manifest, or reopen the adjacent parser-stress benchmark gaps in this run.
- `reports/benchmarks/latest.py` is regenerated honestly and flips `regression-module-compile-verbose-purged` from `status == "unimplemented"` to `status == "measured"` while leaving `regression-parser-atomic-lookbehind-cold` and `regression-parser-bytes-backreference-purged` as the only explicit `regression-matrix` gaps.
- The refreshed publication moves the shared `regression-matrix` manifest summary from `5` workloads with `2` measured / `3` known gaps to `5` workloads with `3` measured / `2` known gaps, and the combined benchmark summary from `588` workloads with `569` real `rebar` timings / `19` known gaps to `588` workloads with `570` real `rebar` timings / `18` known gaps.
- `tests/benchmarks/benchmark_expectations.py` is updated only as needed to keep the shared source-tree scorecard expectations aligned with that refreshed publication. The `regression-matrix` known-gap surface must drop only `regression-module-compile-verbose-purged`; the two parser-stress rows remain explicit known gaps and representative known-gap coverage stays honest.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0457-regression-matrix.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task benchmark-publication only. Do not change Rust or Python implementation behavior, benchmark harness runtime semantics, manifest selectors, or the adjacent parser-matrix correctness surface to complete it.
- Keep the catch-up on the ordinary source-tree benchmark path so the published comparison remains at the same module boundary as stdlib `re`.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/feature-planning-rbr-0457-probe.py` already produced `5` regression workloads with `3` measured / `2` known gaps and showed `regression-module-compile-verbose-purged` as `status == "measured"`.
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-post-0457-full.py` already produced `588` total workloads with `570` measured / `18` known gaps, confirming this run should be a publication and expectation refresh rather than another implementation slice.
- `RBR-0458` is currently blocked only because the tracked benchmark expectation and publication layers still count this verbose regression row as a known gap; landing this task should remove that unrelated summary drift without widening the architecture cleanup.
- The intended post-catch-up follow-on is `RBR-0459`, which should publish the exact parser-stress compile proxy already anchored by `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` on the shared `parser-matrix` correctness path before parity or later benchmark refreshes reopen that heavier parser frontier.
