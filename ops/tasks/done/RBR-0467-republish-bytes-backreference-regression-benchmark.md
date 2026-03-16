# RBR-0467: Republish the bytes named-backreference regression row as a measured source-tree benchmark

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication now that `rebar.compile()` supports the exact bytes named-backreference parser slice, so `regression-parser-bytes-backreference-purged` stops publishing as an explicit gap and instead becomes a measured `regression-matrix` row without widening the benchmark frontier.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload id `regression-parser-bytes-backreference-purged` in `benchmarks/workloads/regression_matrix.py`; do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- The source-tree benchmark expectations stop treating `regression-parser-bytes-backreference-purged` as a known gap on the shared regression surface:
  - `regression-pack-full` no longer lists that workload under representative known gaps.
  - the `regression-matrix` combined-manifest expectation reports `known_gap_count == 0` and `measured_workloads == 5`.
  - if `RBR-0466` lands first, preserve its explicit `known_gap_workload_ids` derivation instead of restoring manual count bookkeeping; if it has not landed yet, adjust the current expectation shape minimally and consistently.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `573` measured workloads, and `15` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes `regression-parser-bytes-backreference-purged` with `status == "measured"` on `regression-matrix`, while the tracked `regression-matrix` manifest reports `5` measured workloads / `0` known gaps and the overall summary reports `573` measured workloads / `15` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0467-regression.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the already-published regression row. Do not broaden into the remaining literal-flag or grouped helper known gaps in this run.

## Notes
- `RBR-0465` already landed the exact bytes compile slice behind `rebar.compile()` for `b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}"`, so this task should only republish the adjacent benchmark row on the existing regression surface.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact still reports `588` total workloads, `572` measured workloads, `16` known gaps, and `regression-matrix` at `4` measured workloads / `1` known gap.
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/feature-planning-rbr-0467-regression.py` now reports `5` measured workloads / `0` known gaps, and a full rerun to `.rebar/tmp/feature-planning-rbr-0467-full.py` reports `588` total workloads, `573` measured workloads, and `15` known gaps.
- The intended post-benchmark follow-on is `RBR-0468`, which should publish the exact `IGNORECASE|ASCII` literal helper pair already exposed as `literal-flag-boundary` gap rows on the shared `literal-flag-workflows` correctness surface before Rust-backed parity or benchmark catch-up revisit that flag-combination slice.

## Completion
- 2026-03-16: Updated `tests/benchmarks/benchmark_expectations.py` so the shared regression source-tree expectations stop classifying `regression-parser-bytes-backreference-purged` as a known gap, keep the `RBR-0466` inventory-derived gap-count flow intact, and instead treat that row as a representative measured regression workload.
- 2026-03-16: Added focused expectation coverage in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the regression pack no longer advertises the bytes backreference row as a representative gap and the direct regression-manifest rerun now asserts `5` measured workloads / `0` known gaps with that workload published as `measured`.
- 2026-03-16: Republished the tracked source-tree benchmark scorecard in `reports/benchmarks/latest.py`; the tracked artifact now reports `588` total workloads, `573` measured workloads, `15` known gaps overall, `regression-matrix` at `5` measured workloads / `0` known gaps, and `regression-parser-bytes-backreference-purged` with `implementation_timing.status == "measured"`.
- 2026-03-16: Verification completed with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0467-regression.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
