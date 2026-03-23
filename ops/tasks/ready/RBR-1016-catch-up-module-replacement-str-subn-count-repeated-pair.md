# RBR-1016: Catch up the raw `re.subn()` str count/repeated pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw-module `str` literal `re.subn()` count/repeated pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.subn("abc", "x", "abcabc", 1)`
- `re.subn("abc", "x", "abcabc")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module `str` literal-replacement workloads:
  - add `module-subn-str-count-purged-str`; and
  - add `module-subn-str-repeated-purged-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-subn-str-count-purged-str` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-str-repeated-purged-str` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-subn-str-count` and `module-subn-str-repeated`;
  - keep the raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-sub-bytes-no-match-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into raw-module `str` `sub()` repeated follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused raw-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in order as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-sub-bytes-no-match-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`;
  - extend the raw-module literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `module-subn-str-count` and `module-subn-str-repeated` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `953` total / `953` measured / `0` known gaps across `30` manifests to `955` / `955` / `0` across the same `30` manifests;
  - `module_workloads` moves from `945` to `947`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 404, "warm": 445}` to `{"cold": 104, "purged": 406, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 114`, `measured_workloads == 114`, `known_gap_count == 0`, and `workload_count == 114` to `116`, `116`, `0`, and `116`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 114` to `116`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1016-module-replacement-str-subn-count-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw-module `str` `re.subn()` count/repeated pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two raw-module `str` replacement rows above. Leave raw-module `str` `sub()` repeated follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, and deeper raw-module replacement expansion for later tasks.

## Notes
- `RBR-1016` is the next available feature task id in the current checkout:
  - `RBR-1014` is the latest done feature task on the drained raw-module `str` replacement correctness frontier;
  - `RBR-1015` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained raw-module `str` correctness publication because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent count/repeated `re.subn()` pair rather than raw-module `str` `sub()` repeated follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'` currently passes (`2 passed`), so the exact raw-module `str` `subn()` count/repeated parity slice is already green in this checkout;
  - `rg -n 'module-subn-str-count-purged-str|module-subn-str-repeated-purged-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact Python-path benchmark rows are still absent from the tracked owner-path surfaces;
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on both hypothetical workloads `module-subn-str-count-purged-str` and `module-subn-str-repeated-purged-str`, so the later benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first; and
  - `reports/benchmarks/latest.py` currently reports `953` total / `953` measured / `0` known gaps overall, with `module_workloads == 945`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 404, "warm": 445}`, and `collection-replacement-boundary` at `selected_workload_count == 114`, `measured_workloads == 114`, `known_gap_count == 0`, and `workload_count == 114`.
