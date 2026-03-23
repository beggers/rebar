# RBR-0989: Catch up the direct `Pattern.sub()` / `Pattern.subn()` literal-success pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` literal-success pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc").sub("x", "zzz")`
- `re.compile("abc").subn("x", "abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` literal-success workloads:
  - add `pattern-sub-no-match-warm-str`; and
  - add `pattern-subn-count-warm-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-no-match-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zzz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-count-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-str-no-match` and `pattern-subn-str-count`;
  - insert `pattern-sub-no-match-warm-str` immediately after `pattern-split-on-bytes-string-warm-str` and immediately before `pattern-sub-count-indexlike-positional-purged-bytes`;
  - insert `pattern-subn-count-warm-str` immediately after `pattern-subn-on-str-string-purged-bytes` and immediately before `pattern-subn-grouped-template-warm-str`; and
  - do not widen into raw-module replacement rows, compiled-pattern-first-argument rows, keyword/error rows, grouped-template follow-ons, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - add `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured(...)` or an equivalent existing assertion so the manifest moves from `102` measured workloads to `104`, preserving the existing positional-indexlike, keyword, compiled-pattern, wrong-text-model, bounded-`findall()`, bounded-`finditer()`, and direct-`Pattern` `split()` subsets while adding this new direct replacement pair in the exact order above;
  - extend the standard benchmark anchor-contract definitions with exactly one new direct-`Pattern` collection/replacement literal-success owner-path definition, or a strictly equivalent widening of an existing direct-`Pattern` replacement definition, that maps the two workload ids above to their two published correctness case ids and verifies callback-result parity on the existing owner route;
  - keep the existing `collection-replacement-boundary` positional-indexlike, keyword, compiled-pattern, wrong-text-model, bounded-`findall()`, bounded-`finditer()`, and direct-`Pattern` `split()` ownership checks honest while moving the zero-gap manifest expectation from `102` selected / `102` measured to `104` / `104`; and
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `941` total / `941` measured / `0` known gaps across `30` manifests to `943` / `943` / `0` across the same `30` manifests;
  - `module_workloads` moves from `933` to `935`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `102` selected / `102` measured / `102` workload-count rows to `104` / `104` / `104`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `102` workload-count rows to `104`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_pattern_replacement_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0989-pattern-replacement-literal-success-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct `Pattern.sub()` / `Pattern.subn()` literal-success pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two direct replacement rows above. Leave module replacement follow-ons, grouped-template follow-ons, callable follow-ons, and deeper direct-`Pattern` replacement expansion for later tasks.

## Notes
- `RBR-0989` is the next available feature task id in the current checkout:
  - `RBR-0987` is the latest done feature task on the drained direct-`Pattern` collection/replacement benchmark frontier;
  - `RBR-0988` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct `Pattern.split()` benchmark catch-up because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent direct replacement success pair rather than another keyword/error slice, another grouped-template slice, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_pattern_replacement_matches_cpython'` currently passes (`168 passed`), so the exact direct replacement correctness/parity slice is already green in this checkout;
  - `rg -n 'pattern-sub-no-match-warm-str|pattern-subn-count-warm-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `rg -n 'pattern-sub-str-no-match|pattern-subn-str-count' tests/conformance/fixtures/collection_replacement_workflows.py reports/correctness/latest.py` finds both published correctness anchors, confirming the benchmark ids are still absent from the tracked Python-path benchmark surface;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... synthetic Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) for pattern-sub-no-match-warm-str and pattern-subn-count-warm-str ... PY` returns `status == "measured"` for both adapters on both synthetic workloads through the current benchmark harness in this checkout; and
  - current published benchmark totals in this checkout are `941` total / `941` measured / `0` known gaps overall, with `collection-replacement-boundary` at `102` selected / `102` measured / `0` known gaps and `102` workload-count rows in both the manifest summary and matching artifact record.
