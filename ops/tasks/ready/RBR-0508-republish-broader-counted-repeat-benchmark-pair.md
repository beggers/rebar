# RBR-0508: Republish the broader counted-repeat benchmark pair as measured source-tree timings

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Refresh the tracked source-tree benchmark publication so the remaining broader `{1,4}` counted-repeat anchors on the exact-repeat and ranged-repeat manifests stop publishing as explicit known gaps now that the current checkout already measures the bounded slice through the Python-facing `rebar` path.

## Deliverables
- `benchmarks/workloads/exact_repeat_quantified_group_boundary.py`
- `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark targets pinned to the existing workload ids on the current Python-path source-tree manifests:
  - `module-search-numbered-broader-ranged-repeat-group-cold-gap` in `benchmarks/workloads/exact_repeat_quantified_group_boundary.py`
  - `module-search-numbered-ranged-repeat-group-wider-range-cold-gap` in `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py`
  Do not add workload ids, rename anchors, or fork another benchmark manifest for this slice.
- `benchmarks/workloads/exact_repeat_quantified_group_boundary.py` and `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py` become honest for the now-measured broader `{1,4}` module `search()` slice while preserving the legacy ids:
  - the manifest-level notes no longer describe these rows as queued known-gap carry-forward anchors;
  - the exact rows no longer carry stale `unsupported` categories; and
  - the row notes describe the bounded upper-bound `module.search()` path on `"zzabcbcbcbcdzz"` instead of an unimplemented gap.
- `tests/benchmarks/benchmark_expectations.py` stops classifying the exact-repeat and ranged-repeat manifests as source-tree known-gap manifests for these rows:
  - `known_gap_workload_ids` no longer lists either workload id;
  - `representative_known_gap_workload_ids` becomes empty for both manifests; and
  - `representative_measured_workload_ids` promotes both legacy ids so the refreshed publication asserts the republished slice directly.
- `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py` keeps the refreshed rows pinned to published correctness coverage instead of leaving them as benchmark-only debt:
  - `module-search-numbered-broader-ranged-repeat-group-cold-gap` still anchors directly to `broader-range-wider-ranged-repeat-numbered-group-module-search-upper-bound-str`;
  - `module-search-numbered-ranged-repeat-group-wider-range-cold-gap` stays anchored to the published broader `{1,4}` counted-repeat correctness slice instead of remaining a benchmark-only gap row; and
  - the CPython `search()` result observed for both benchmark rows still matches the anchored correctness-case result.
- Focused manifest reruns report the counted-repeat manifests as fully measured:
  - `benchmarks/workloads/exact_repeat_quantified_group_boundary.py` reports `13` measured workloads and `0` known gaps; and
  - `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py` reports `8` measured workloads and `0` known gaps.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` pass against the refreshed source-tree publication with `588` total workloads, `588` measured workloads, and `0` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `exact-repeat-quantified-group-boundary` at `13` measured workloads / `0` known gaps;
  - `ranged-repeat-quantified-group-boundary` at `8` measured workloads / `0` known gaps; and
  - the combined source-tree summary at `588` total workloads / `588` measured workloads / `0` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/exact_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0508-exact-repeat-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0508-ranged-repeat-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark publication and expectation catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the already-measured broader `{1,4}` counted-repeat module-search anchors. Do not broaden into grouped alternation, grouped conditionals, open-ended repeats, bytes benchmark coverage, or unrelated benchmark cleanup in this run.

## Notes
- Build on `RBR-0507`.
- The matching correctness and parity slice already exists on `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_workflows.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`; this task only catches the tracked benchmark publication up to that already-landed behavior.
- 2026-03-17 feature-planning probes in the current checkout already show the live source-tree benchmark surface is ahead of the tracked publication:
  - direct public-API checks show `rebar.search(...)` matches CPython for both `a(bc){1,4}d` and `a(?P<word>bc){1,4}d` on `"zzabcbcbcbcdzz"`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/exact_repeat_quantified_group_boundary.py --report .rebar/tmp/feature-planning-exact-repeat-boundary.py` reports `13` measured workloads / `0` known gaps;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/feature-planning-ranged-repeat-boundary.py` reports `8` measured workloads / `0` known gaps; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-full-benchmarks.py` reports `588` total workloads / `588` measured workloads / `0` known gaps, while the tracked `reports/benchmarks/latest.py` artifact still sits at `588` total workloads / `586` measured workloads / `2` known gaps because `tests/benchmarks/benchmark_expectations.py` still classifies the legacy ids as known gaps and the tracked publication has not been regenerated since `RBR-0507` landed.
