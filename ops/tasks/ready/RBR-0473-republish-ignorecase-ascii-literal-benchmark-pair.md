# RBR-0473: Republish the IGNORECASE|ASCII literal benchmark pair as measured source-tree timings

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication once `RBR-0471` lands so the exact `IGNORECASE|ASCII` literal helper pair already anchored on `literal-flag-boundary` stops publishing as explicit gaps and instead becomes measured `rebar` timing coverage without widening the benchmark frontier.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/literal_flag_boundary.py`:
  - `module-search-ignorecase-ascii-cold-gap`
  - `pattern-search-ignorecase-ascii-warm-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact ASCII pair as source-tree known gaps on both the shared post-parser pack and the literal-flag combined-manifest expectation:
  - `post-parser-workflows` no longer lists either workload under `representative_known_gap_workload_ids`;
  - the same scorecard case promotes those exact workload ids onto the measured representative surface so the refreshed publication asserts them directly instead of dropping them from representative coverage; and
  - if `RBR-0466` has already landed, preserve its explicit `known_gap_workload_ids` derivation path instead of restoring manual `known_gap_count` bookkeeping.
- The `literal-flag-boundary` source-tree publication reports the bounded flag-combination slice as fully measured:
  - the direct manifest rerun reports `10` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `literal-flag-boundary` reports `known_gap_count == 0` and no representative known-gap ids; and
  - the refreshed workload records for `module-search-ignorecase-ascii-cold-gap` and `pattern-search-ignorecase-ascii-warm-gap` both publish `status == "measured"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `575` measured workloads, and `13` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `literal-flag-boundary` at `10` measured workloads / `0` known gaps; and
  - the overall summary at `588` total workloads / `575` measured workloads / `13` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/literal_flag_boundary.py --report .rebar/tmp/rbr-0473-literal-flag-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact `str`-valued `IGNORECASE|ASCII` `search()` pair already published on `literal-flag-boundary`. Do not broaden into bytes `ASCII`, `match()` or `fullmatch()`, inline-flag combinations, or unrelated benchmark gaps.

## Notes
- `RBR-0471` should land immediately ahead of this task and convert the matching correctness pair `flag-module-search-ignorecase-ascii-str-hit` / `flag-pattern-search-ignorecase-ascii-str-hit` to real Rust-backed parity on `literal-flag-workflows`.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact still reports `588` total workloads, `573` measured workloads, `15` known gaps overall, and `literal-flag-boundary` at `8` measured workloads / `2` known gaps with both exact ASCII rows still publishing as `status == "unimplemented"`.
- 2026-03-16 planning probe: `benchmarks/workloads/literal_flag_boundary.py` already carries the exact target rows pinned to pattern `"abc"`, haystack `"ABC"`, flags `258` (`IGNORECASE | ASCII`), and the ordinary module/pattern helper timing scopes, so this follow-on should stay on that existing path rather than inventing another manifest.
