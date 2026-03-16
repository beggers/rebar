# RBR-0493: Republish the nested grouped-alternation replacement benchmark pair as measured source-tree timings

Status: blocked
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the shared source-tree benchmark publication once `RBR-0491` lands so the exact nested grouped-alternation replacement-template helper pair already anchored on `grouped-alternation-replacement-boundary` stops publishing as explicit known gaps and instead becomes measured `rebar` timings without widening the benchmark frontier.

## Deliverables
- `benchmarks/workloads/grouped_alternation_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/grouped_alternation_replacement_boundary.py`:
  - `module-sub-template-nested-grouped-alternation-cold-gap`
  - `pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `benchmarks/workloads/grouped_alternation_replacement_boundary.py` becomes honest for the now-supported slice while preserving the legacy ids for scorecard continuity:
  - the two exact nested grouped-alternation rows no longer carry the stale `gap` category; and
  - the manifest and row notes stop describing `a((b|c))d` plus `\\1x` and `a(?P<outer>(b|c))d` plus `\\g<outer>x` as still queued once `RBR-0491` has landed.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact nested grouped-alternation replacement pair as source-tree known gaps on the `grouped-alternation-replacement-boundary` combined-manifest expectation:
  - `known_gap_workload_ids` no longer lists either workload for `grouped-alternation-replacement-boundary`;
  - `representative_known_gap_workload_ids` becomes empty for that manifest; and
  - the same manifest expectation promotes both exact workload ids onto the measured representative surface so the refreshed publication asserts them directly instead of dropping them from representative coverage.
- `tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py` keeps the refreshed benchmark rows pinned to published correctness cases instead of leaving the nested pair on the known-gap path:
  - all measured grouped-alternation replacement workloads stay anchored to published correctness cases; and
  - the former known-gap nested pair now anchors directly to `module-sub-template-nested-group-alternation-numbered-outer-str` and `pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str`.
- The `grouped-alternation-replacement-boundary` source-tree publication reports the bounded nested replacement slice as fully measured:
  - the direct manifest rerun reports `10` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `grouped-alternation-replacement-boundary` reports `known_gap_count == 0`; and
  - the refreshed workload records for `module-sub-template-nested-grouped-alternation-cold-gap` and `pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap` both publish `status == "measured"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `583` measured workloads, and `5` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `grouped-alternation-replacement-boundary` at `10` measured workloads / `0` known gaps; and
  - the overall summary at `588` total workloads / `583` measured workloads / `5` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/grouped_alternation_replacement_boundary.py --report .rebar/tmp/rbr-0493-grouped-alternation-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact numbered `str` module `sub()` path for `a((b|c))d` plus `\\1x` on `"abdacd"` and the named compiled-`Pattern` `subn()` first-match-only path for `a(?P<outer>(b|c))d` plus `\\g<outer>x` on `"acdabd"` with `count=1`. Do not broaden into the adjacent wrapper-template pair on `grouped_alternation_boundary.py`, inner-capture template references, callable replacements, quantified nested alternation, or another manifest.

## Notes
- `RBR-0491` should land immediately ahead of this task and convert the matching correctness pair to real Rust-backed parity on the shared grouped replacement pytest path.
- 2026-03-16 planning probe: `benchmarks/workloads/grouped_alternation_replacement_boundary.py` already carries the exact target rows pinned to patterns `a((b|c))d` and `a(?P<outer>(b|c))d`, haystacks `abdacd` and `acdabd`, replacement templates `\\1x` and `\\g<outer>x`, flags `0`, and the ordinary module/pattern helper timing scopes, so this follow-on should stay on that existing benchmark path rather than inventing another manifest.
- 2026-03-16 planning probe: the tracked `reports/benchmarks/latest.py` artifact currently reports `588` total workloads, `581` measured workloads, `7` known gaps overall, and `grouped-alternation-replacement-boundary` at `8` measured workloads / `2` known gaps, with both exact nested replacement rows still publishing `status == "unimplemented"`.

## Blocker Note
- 2026-03-16 feature-implementation: Updated `benchmarks/workloads/grouped_alternation_replacement_boundary.py`, `tests/benchmarks/benchmark_expectations.py`, and `tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py` so the exact nested `\\1x` / `\\g<outer>x` legacy ids are modeled as measured and anchored directly to the published nested grouped-alternation correctness cases. Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py` (`5 passed, 10 subtests passed`) and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py` (`9 passed, 146 subtests passed`). Verified the narrow manifest rerun at `.rebar/tmp/rbr-0493-grouped-alternation-replacement-boundary.py`, which now reports `10` measured workloads / `0` known gaps for `grouped-alternation-replacement-boundary`.
- Blocking issue: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still fails because the adjacent wrapper-template pair on `benchmarks/workloads/grouped_alternation_boundary.py` is already timing as measured too. The narrow rerun at `.rebar/tmp/rbr-0493-grouped-alternation-boundary-adjacent.py` reports `grouped-alternation-boundary` at `8` measured workloads / `0` known gaps, while the shared combined-suite expectations and queued follow-on `RBR-0495` still treat that manifest as `6` measured / `2` known gaps. Republishing `reports/benchmarks/latest.py` from this checkout would therefore publish an out-of-scope extra benchmark slice and shift the combined totals past this task's claimed `583` measured / `5` known-gap target.
