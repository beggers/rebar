# RBR-0485: Republish the numbered-backreference grouped-segment benchmark pair as measured source-tree timings

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication once `RBR-0483` lands so the exact numbered-backreference grouped-segment helper pair already anchored on `numbered-backreference-boundary` stops publishing as explicit known gaps and instead becomes measured `rebar` timings without widening the benchmark frontier.

## Deliverables
- `benchmarks/workloads/numbered_backreference_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/numbered_backreference_boundary.py`:
  - `module-search-numbered-backreference-segment-cold-gap`
  - `pattern-search-numbered-backreference-prefix-purged-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `benchmarks/workloads/numbered_backreference_boundary.py` becomes honest for the now-supported slice while preserving the legacy ids for scorecard continuity:
  - the two exact grouped-segment rows no longer carry the stale `unsupported` category; and
  - the manifest and row notes stop describing the `(ab)x\\1` / `x(ab)\\1` pair as still unsupported once `RBR-0483` has landed.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact numbered-backreference grouped-segment pair as source-tree known gaps on the `numbered-backreference-boundary` combined-manifest expectation:
  - `known_gap_workload_ids` no longer lists either workload for `numbered-backreference-boundary`;
  - `representative_known_gap_workload_ids` becomes empty for that manifest; and
  - the same manifest expectation promotes both exact workload ids onto the measured representative surface so the refreshed publication asserts them directly instead of dropping them from representative coverage.
- The `numbered-backreference-boundary` source-tree publication reports the bounded grouped-segment slice as fully measured:
  - the direct manifest rerun reports `5` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `numbered-backreference-boundary` reports `known_gap_count == 0`; and
  - the refreshed workload records for `module-search-numbered-backreference-segment-cold-gap` and `pattern-search-numbered-backreference-prefix-purged-gap` both publish `status == "measured"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `579` measured workloads, and `9` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `numbered-backreference-boundary` at `5` measured workloads / `0` known gaps; and
  - the overall summary at `588` total workloads / `579` measured workloads / `9` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/numbered_backreference_boundary.py --report .rebar/tmp/rbr-0485-numbered-backreference-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact numbered `str` `(ab)x\\1` / `x(ab)\\1` module/pattern `search()` pair already published on `numbered-backreference-boundary`. Do not broaden into named grouped-segment backreferences, `match()` / `fullmatch()`, replacements, branch-local backreferences, alternation, or grouped-reference work on another manifest.

## Notes
- `RBR-0483` should land immediately ahead of this task and convert the matching correctness pair `numbered-backreference-segment-module-search-str` / `numbered-backreference-prefix-pattern-search-str` to real Rust-backed parity on `numbered-backreference-workflows`.
- 2026-03-16 planning probe: `benchmarks/workloads/numbered_backreference_boundary.py` already carries the exact target rows pinned to patterns `"(ab)x\\1"` and `"x(ab)\\1"`, haystacks `"zzabxabzz"` and `"zzxababzz"`, flags `0`, and the ordinary module/pattern helper timing scopes, so this follow-on should stay on that existing benchmark path rather than inventing another manifest.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact currently reports `588` total workloads, `577` measured workloads, `11` known gaps overall, and `numbered-backreference-boundary` at `3` measured workloads / `2` known gaps, with both exact grouped-segment rows still publishing `status == "unimplemented"`.
