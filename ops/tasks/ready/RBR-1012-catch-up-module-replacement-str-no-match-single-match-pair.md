# RBR-1012: Catch up the raw `re.sub()` str no-match/single-match pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw-module `str` literal `re.sub()` no-match/single-match pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub("abc", "x", "zzz")`
- `re.sub("abc", "x", "zabczz")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module `str` literal-replacement workloads:
  - add `module-sub-str-no-match-purged-str`; and
  - add `module-sub-str-single-match-purged-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-sub-str-no-match-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zzz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-sub-str-single-match-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-sub-str-no-match` and `module-sub-str-single-match`;
  - keep the raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with `module-sub-str-no-match-purged-str` ordered immediately before `module-sub-str-single-match-purged-str`, and both ordered before the existing bytes-side raw-module literal replacement workloads; and
  - do not widen into raw-module `str` repeated or `subn()` follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused raw-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in order as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-bytes-no-match-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`;
  - extend the raw-module literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `module-sub-str-no-match` and `module-sub-str-single-match` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `951` total / `951` measured / `0` known gaps across `30` manifests to `953` / `953` / `0` across the same `30` manifests;
  - `module_workloads` moves from `943` to `945`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 402, "warm": 445}` to `{"cold": 104, "purged": 404, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `112` selected / `112` measured / `112` workload-count rows to `114` / `114` / `114`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `112` workload-count rows to `114`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-no-match or str-single-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1012-module-replacement-str-no-match-single-match-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw-module `str` `re.sub()` no-match/single-match pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two raw-module `str` replacement rows above. Leave raw-module `str` repeated or `subn()` follow-ons, compiled-pattern-first-argument follow-ons, grouped-template rows, callable replacement rows, and deeper raw-module replacement expansion for later tasks.

## Notes
- `RBR-1012` is the next available feature task id in the current checkout:
  - `RBR-1010` is the latest done feature task on the drained raw-module `str` replacement correctness frontier;
  - `RBR-1011` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained raw-module `str` correctness publication because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent no-match/single-match `re.sub()` pair rather than raw-module `str` repeated or `subn()` follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-no-match or str-single-match)'` currently passes (`2 passed`), so the exact raw-module `str` replacement correctness/parity slice is already green in this checkout;
  - `rg -n 'module-sub-str-no-match-purged-str|module-sub-str-single-match-purged-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact Python-path benchmark rows are still absent from the tracked owner-path surfaces;
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on both hypothetical workloads `module-sub-str-no-match-purged-str` and `module-sub-str-single-match-purged-str`, so the later benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first; and
  - `reports/benchmarks/latest.py` currently reports `951` total / `951` measured / `0` known gaps overall, with `module_workloads == 943`, `workloads_by_cache_mode == {"cold": 104, "purged": 402, "warm": 445}`, and `collection-replacement-boundary` at `112` selected / `112` measured / `112` workload-count rows.
