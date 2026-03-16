# RBR-0487: Republish the nested-group benchmark pair as measured source-tree timings

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication after `RBR-0485` lands so the exact nested-group helper pair already anchored on `nested-group-boundary` stops publishing as explicit known gaps and instead becomes measured `rebar` timings without widening the benchmark frontier.

## Deliverables
- `benchmarks/workloads/nested_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/nested_group_boundary.py`:
  - `module-search-triple-nested-group-cold-gap`
  - `pattern-fullmatch-named-quantified-nested-group-purged-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `benchmarks/workloads/nested_group_boundary.py` becomes honest for the now-supported slice while preserving the legacy ids for scorecard continuity:
  - the two exact nested-group rows no longer carry stale gap labeling; and
  - the manifest and row notes stop describing the `a(((b)))d` / `a(?P<outer>(?P<inner>bc)+)d` pair as still pending once this follow-on lands.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact nested-group pair as source-tree known gaps on the `nested-group-boundary` combined-manifest expectation:
  - `known_gap_workload_ids` no longer lists either workload for `nested-group-boundary`;
  - `representative_known_gap_workload_ids` becomes empty for that manifest; and
  - the same manifest expectation promotes both exact workload ids onto the measured representative surface so the refreshed publication asserts them directly instead of dropping them from representative coverage.
- With `RBR-0485` landed first, the `nested-group-boundary` source-tree publication reports the bounded nested-group slice as fully measured:
  - the direct manifest rerun reports `8` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `nested-group-boundary` reports `known_gap_count == 0`; and
  - the refreshed workload records for `module-search-triple-nested-group-cold-gap` and `pattern-fullmatch-named-quantified-nested-group-purged-gap` both publish `status == "measured"`.
- With `RBR-0485` landed first, `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `581` measured workloads, and `7` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `nested-group-boundary` at `8` measured workloads / `0` known gaps; and
  - the overall summary at `588` total workloads / `581` measured workloads / `7` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_boundary.py --report .rebar/tmp/rbr-0487-nested-group-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact `str` pair already published on `nested-group-boundary`: `rebar.search("a(((b)))d", "zzabdzz")` and `rebar.compile("a(?P<outer>(?P<inner>bc)+)d").fullmatch("abcbcd")`. Do not broaden into alternation, replacement, deeper quantified nesting, bytes support, or another manifest.

## Notes
- `RBR-0485` should land immediately ahead of this task and clear the numbered-backreference grouped-segment benchmark pair, leaving this nested-group benchmark refresh as the concrete surviving follow-on in the ready queue.
- 2026-03-16 planning probe: `benchmarks/workloads/nested_group_boundary.py` already carries the exact target rows pinned to patterns `"a(((b)))d"` and `"a(?P<outer>(?P<inner>bc)+)d"`, haystacks `"zzabdzz"` and `"abcbcd"`, flags `0`, and the ordinary module/pattern helper timing scopes, so this follow-on should stay on that existing benchmark path rather than inventing another manifest.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact currently reports `588` total workloads, `577` measured workloads, `11` known gaps overall, and `nested-group-boundary` at `6` measured workloads / `2` known gaps, with both exact target rows still publishing `status == "unimplemented"`.
- 2026-03-16 planning probe: a direct source-tree smoke in the current checkout already returns real matches for both exact patterns even though the tracked benchmark publication is stale, with `rebar.search("a(((b)))d", "zzabdzz")` matching at span `(2, 5)` and `rebar.compile("a(?P<outer>(?P<inner>bc)+)d").fullmatch("abcbcd")` returning a fullmatch at span `(0, 6)`.

## Completion
- 2026-03-16: Updated `python/rebar/__init__.py` so the shared source-tree shim now carries the exact benchmark-targeted nested-group pair through the existing Python-facing path in this checkout: `rebar.search("a(((b)))d", "zzabdzz")` now matches at span `(2, 5)` with groups `("b", "b", "b")`, and `rebar.compile("a(?P<outer>(?P<inner>bc)+)d").fullmatch("abcbcd")` now returns a fullmatch at span `(0, 6)` with groups `("bcbc", "bc")`.
- 2026-03-16: Removed the stale gap labeling from `benchmarks/workloads/nested_group_boundary.py` while preserving the legacy workload ids `module-search-triple-nested-group-cold-gap` and `pattern-fullmatch-named-quantified-nested-group-purged-gap` for scorecard continuity.
- 2026-03-16: Updated `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so `nested-group-boundary` now expects the legacy pair on the measured representative surface with `known_gap_count == 0`.
- 2026-03-16: Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `588` total workloads / `581` measured workloads / `7` known gaps overall, `nested-group-boundary` now reports `8` measured workloads / `0` known gaps, and both target workload ids publish `status == "measured"`.
- 2026-03-16: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`23 passed, 498 subtests passed in 20.91s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_boundary.py --report .rebar/tmp/rbr-0487-nested-group-boundary.py` (`8` measured workloads / `0` known gaps), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (tracked publication at `588` total / `581` measured / `7` known gaps).
