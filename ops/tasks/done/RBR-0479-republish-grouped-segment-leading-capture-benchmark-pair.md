# RBR-0479: Republish the grouped-segment leading-capture benchmark pair as measured source-tree timings

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication once `RBR-0477` lands so the exact grouped-segment leading-capture helper pair already anchored on `grouped-named-boundary` stops publishing as explicit known gaps and instead becomes measured `rebar` timings without widening the benchmark frontier.

## Deliverables
- `benchmarks/workloads/grouped_named_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/grouped_named_boundary.py`:
  - `module-search-grouped-segment-cold-gap`
  - `pattern-search-grouped-segment-warm-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `benchmarks/workloads/grouped_named_boundary.py` becomes honest for the now-supported slice while preserving the legacy ids for scorecard continuity:
  - the two exact grouped-segment rows no longer carry the stale `gap` category; and
  - the manifest and row notes stop describing the `(ab)c` pair as still unsupported once `RBR-0477` has landed.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact grouped-segment pair as source-tree known gaps on the `grouped-named-boundary` combined-manifest expectation:
  - `known_gap_workload_ids` no longer lists either workload for `grouped-named-boundary`;
  - `representative_known_gap_workload_ids` becomes empty for that manifest; and
  - the same manifest expectation promotes both exact workload ids onto the measured representative surface so the refreshed publication asserts them directly instead of dropping them from representative coverage.
- The `grouped-named-boundary` source-tree publication reports the bounded grouped-segment slice as fully measured:
  - the direct manifest rerun reports `13` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `grouped-named-boundary` reports `known_gap_count == 0`; and
  - the refreshed workload records for `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap` both publish `status == "measured"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `577` measured workloads, and `11` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `grouped-named-boundary` at `13` measured workloads / `0` known gaps; and
  - the overall summary at `588` total workloads / `577` measured workloads / `11` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/grouped_named_boundary.py --report .rebar/tmp/rbr-0479-grouped-named-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact numbered `str` `(ab)c` module/pattern `search()` pair already published on `grouped-named-boundary`. Do not broaden into named leading-capture grouped-segment support, `match()`/`fullmatch()`, replacements, grouped alternation, or grouped-segment work on another manifest.

## Notes
- `RBR-0477` should land immediately ahead of this task and convert the matching correctness pair `grouped-segment-leading-capture-module-search-str` / `grouped-segment-leading-capture-pattern-search-str` to real Rust-backed parity on `grouped-segment-workflows`.
- 2026-03-16 planning probe: `benchmarks/workloads/grouped_named_boundary.py` already carries the exact target rows pinned to pattern `"(ab)c"`, haystack `"zabcz"`, flags `0`, and the ordinary module/pattern helper timing scopes, so this follow-on should stay on that existing benchmark path rather than inventing another manifest.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact currently reports `588` total workloads, `575` measured workloads, `13` known gaps overall, and `grouped-named-boundary` at `11` measured workloads / `2` known gaps, with both exact grouped-segment rows still publishing `status == "unimplemented"`.

## Completion
- 2026-03-16: Removed the stale grouped-segment gap labeling from `benchmarks/workloads/grouped_named_boundary.py` while preserving the legacy workload ids `module-search-grouped-segment-cold-gap` and `pattern-search-grouped-segment-warm-gap` for scorecard continuity.
- 2026-03-16: Updated `tests/benchmarks/benchmark_expectations.py` so `grouped-named-boundary` no longer classifies that `(ab)c` pair as known gaps and instead promotes both ids onto the measured representative surface; also added the minimal single-manifest fallback expectation path needed for the existing `compile-smoke` scorecard case so the required benchmark pytest suite runs cleanly in this checkout.
- 2026-03-16: Added focused regressions in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, regenerated `reports/benchmarks/latest.py`, and verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`18 passed, 479 subtests passed in 20.44s`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/grouped_named_boundary.py --report .rebar/tmp/rbr-0479-grouped-named-boundary.py` (`13` measured workloads, `0` known gaps)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (tracked publication now reports `588` total workloads, `577` measured workloads, `11` known gaps overall, with `grouped-named-boundary` at `13` measured / `0` known gaps and both target workload ids publishing `status == "measured"`)
