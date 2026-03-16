# RBR-0499: Republish the nested grouped-alternation wrapper-template benchmark pair as measured source-tree timings

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Refresh the grouped-alternation source-tree benchmark publication so the exact nested grouped-alternation wrapper-template helper pair already exposed on `grouped_alternation_boundary.py` stops publishing as explicit known gaps and the tracked benchmark report catches up to the already-measured grouped-alternation surfaces in the current checkout.

## Deliverables
- `benchmarks/workloads/grouped_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload ids in `benchmarks/workloads/grouped_alternation_boundary.py`:
  - `module-sub-template-nested-grouped-alternation-warm-gap`
  - `pattern-subn-template-named-nested-grouped-alternation-purged-gap`
  Do not add workload rows, rename workload ids, or introduce another benchmark manifest for this slice.
- `benchmarks/workloads/grouped_alternation_boundary.py` becomes honest for the now-supported slice while preserving the legacy ids for scorecard continuity:
  - the two exact nested wrapper-template rows no longer carry stale `gap` categories; and
  - the manifest and row notes stop describing `a((b|c))d` plus `<\\1>` and `a(?P<outer>(b|c))d` plus `<\\g<outer>>` as still queued known-gap rows once `RBR-0497` has landed.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact wrapper-template pair as source-tree known gaps on the `grouped-alternation-boundary` combined-manifest expectation:
  - `known_gap_workload_ids` no longer lists either workload for `grouped-alternation-boundary`;
  - `representative_known_gap_workload_ids` becomes empty for that manifest; and
  - `representative_measured_workload_ids` promotes both exact workload ids so the refreshed publication asserts them directly instead of leaving the manifest with no direct representative coverage for the republished slice.
- `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` keeps the refreshed wrapper-template rows pinned to published correctness cases instead of leaving them only on the benchmark path:
  - all measured grouped-alternation workloads stay anchored to published correctness cases;
  - the former known-gap wrapper pair now anchors directly to `module-sub-template-nested-group-alternation-numbered-wrapper-str` and `pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str`; and
  - CPython callback results for those two benchmark rows still match the anchored correctness-case results.
- The `grouped-alternation-boundary` source-tree publication reports the bounded wrapper-template slice as fully measured:
  - the direct manifest rerun reports `8` measured workloads and `0` known gaps;
  - the combined-manifest expectation for `grouped-alternation-boundary` reports `known_gap_count == 0`; and
  - the refreshed workload records for `module-sub-template-nested-grouped-alternation-warm-gap` and `pattern-subn-template-named-nested-grouped-alternation-purged-gap` both publish `status == "measured"`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` both pass against the refreshed source-tree publication with `588` total workloads, `585` measured workloads, and `3` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `grouped-alternation-boundary` at `8` measured workloads / `0` known gaps;
  - `grouped-alternation-replacement-boundary` at `10` measured workloads / `0` known gaps, because the current checkout already carries the sibling measured-row changes from blocked `RBR-0493`; and
  - the overall summary at `588` total workloads / `585` measured workloads / `3` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/grouped_alternation_boundary.py --report .rebar/tmp/rbr-0499-grouped-alternation-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark publication and expectation catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the exact numbered module `sub()` wrapper-template path for `a((b|c))d` plus `<\\1>` on `"abdacd"` and the named compiled-`Pattern` `subn()` first-match-only path for `a(?P<outer>(b|c))d` plus `<\\g<outer>>` on `"abdacd"` with `count=1`. Do not broaden into the adjacent `\\1x` / `\\g<outer>x` pair, inner-capture wrapper templates, callable replacements, or the three remaining non-grouped benchmark gaps.
- Do not edit blocked `RBR-0493` in this run; planning will retire or refresh that task separately once the combined publication is caught up.

## Notes
- `RBR-0497` already published the matching correctness pair as passing cases on `nested-group-alternation-wrapper-replacement-workflows`, so this benchmark follow-on should anchor directly to those published case ids instead of treating the rows as standalone benchmark-only debt.
- 2026-03-16 planning probe: direct public-API checks in the current checkout already report `rebar.sub("a((b|c))d", "<\\1>", "abdacd") == "<b><c>"` and `rebar.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1) == ("<b>acd", 1)`, matching CPython for the exact wrapper-template pair under test.
- 2026-03-16 planning probe: a fresh full-suite benchmark run to `.rebar/tmp/feature-planning-probe-benchmarks.py` already reports `588` total workloads / `585` measured workloads / `3` known gaps; the tracked `reports/benchmarks/latest.py` artifact is still stale at `581` / `7` because `grouped_alternation_boundary.py` expectations still classify the adjacent wrapper-template pair as known gaps.
