# RBR-0995: Catch up the direct `Pattern.sub()` / `Pattern.subn()` single-match/repeated pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` single-match/repeated pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc").sub("x", "zabczz")`
- `re.compile("abc").subn("x", "abcabc")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` literal-replacement workloads:
  - add `pattern-sub-single-match-warm-str`; and
  - add `pattern-subn-repeated-warm-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-single-match-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-repeated-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-str-single-match` and `pattern-subn-str-repeated`;
  - insert `pattern-sub-single-match-warm-str` immediately after `pattern-sub-no-match-warm-str`;
  - insert `pattern-subn-repeated-warm-str` immediately after `pattern-subn-count-warm-str`; and
  - do not widen into bytes follow-ons, grouped-template rows, callable replacement rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured(...)`, or an equivalent existing assertion, moves from `104` measured workloads to `106`, preserving the current collection/replacement subsets while adding this new direct replacement pair in the exact order `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`;
  - extend `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_IDS` and `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path definition, so the direct literal replacement anchor contract now maps the four workload ids above to `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, and `pattern-subn-str-repeated`;
  - keep the standard benchmark anchor contract on the existing `collection-replacement-boundary` owner route, with callback-result parity still enabled; and
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `943` total / `943` measured / `0` known gaps across `30` manifests to `945` / `945` / `0` across the same `30` manifests;
  - `module_workloads` moves from `935` to `937`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `104` selected / `104` measured / `104` workload-count rows to `106` / `106` / `106`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `104` workload-count rows to `106`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0995-pattern-replacement-single-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct `Pattern.sub()` / `Pattern.subn()` single-match/repeated pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two direct replacement rows above. Leave bytes follow-ons, grouped-template/callable replacement benchmark slices, and deeper direct-`Pattern` replacement expansion for later tasks.

## Notes
- `RBR-0995` is the next available feature task id in the current checkout:
  - `RBR-0992` is the latest done feature task on the drained direct-`Pattern` collection/replacement frontier;
  - `RBR-0993` and `RBR-0994` are already occupied by architecture tasks in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct `Pattern.sub()` / `Pattern.subn()` correctness publication because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent single-match/repeated pair rather than bytes follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'` currently passes (`2 passed`), so the exact direct replacement correctness/parity slice is already green in this checkout;
  - `rg -n 'pattern-sub-single-match-warm-str|pattern-subn-repeated-warm-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `rg -n 'pattern-sub-str-single-match|pattern-subn-str-repeated' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py reports/correctness/latest.py` finds both published correctness anchors, confirming the benchmark ids are still absent from the tracked Python-path benchmark surface;
  - a direct synthetic workload probe through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` returns `status == "measured"` for both adapters on both hypothetical workloads `pattern-sub-single-match-warm-str` and `pattern-subn-repeated-warm-str`; and
  - `reports/benchmarks/latest.py` currently reports `943` total / `943` measured / `0` known gaps overall, with `collection-replacement-boundary` at `104` selected / `104` measured / `104` workload-count rows.

## Completion
- 2026-03-23: Added `pattern-sub-single-match-warm-str` and `pattern-subn-repeated-warm-str` to `benchmarks/workloads/collection_replacement_boundary.py` in the required owner-route order immediately after `pattern-sub-no-match-warm-str` and `pattern-subn-count-warm-str`.
- Extended the shared owner-path assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the direct literal replacement contract now maps the ordered workload ids `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-subn-count-warm-str`, and `pattern-subn-repeated-warm-str` to the published correctness anchors `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, and `pattern-subn-str-repeated`, while updating the manifest-size and full-suite summary expectations to `106` manifest rows and `945` total measured workloads.
- Regenerated the tracked `reports/benchmarks/latest.py` publication on the source-tree-shim path; the tracked scorecard now reports `945` total / `945` measured / `0` known gaps overall, with `module_workloads == 937`, `parser_workloads == 8`, `regression_workloads == 8`, and `collection-replacement-boundary` at `106` selected / `106` measured / `106` workload-count rows. The tracked artifact also publishes both `pattern-sub-single-match-warm-str` and `pattern-subn-repeated-warm-str` with `status == "measured"`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0995-pattern-replacement-single-match-repeated-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
