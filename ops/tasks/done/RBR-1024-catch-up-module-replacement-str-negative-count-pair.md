# RBR-1024: Catch up the raw `re.sub()` / `re.subn()` str negative-count pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw-module `str` literal negative-count pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", -1)`
- `re.subn("abc", "x", "abcabc", -1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module `str` literal-replacement workloads:
  - add `module-sub-str-negative-count-purged-str`; and
  - add `module-subn-str-negative-count-purged-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-sub-str-negative-count-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == -1`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-str-negative-count-purged-str` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == -1`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-sub-str-negative-count` and `module-subn-str-negative-count`;
  - keep the raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into direct-`Pattern` negative-count rows, bytes negative-count follow-ons, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused raw-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same ten-row order listed above;
  - extend the raw-module literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `module-sub-str-negative-count` and `module-subn-str-negative-count` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `957` total / `957` measured / `0` known gaps across `30` manifests to `959` / `959` / `0` across the same `30` manifests;
  - `module_workloads` moves from `949` to `951`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 408, "warm": 445}` to `{"cold": 104, "purged": 410, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 118`, `measured_workloads == 118`, `known_gap_count == 0`, and `workload_count == 118` to `120`, `120`, `0`, and `120`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 118` to `120`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1024-module-replacement-str-negative-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw-module `str` negative-count rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact raw-module `str` negative-count rows above. Leave direct-`Pattern` negative-count publication, bytes negative-count follow-ons, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1024` is the next available feature task id in the current checkout:
  - `RBR-1022` is the latest done feature task on the drained raw-module `str` negative-count correctness frontier;
  - `RBR-1023` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1022` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the adjacent raw-module `str` negative-count workloads rather than direct-`Pattern` negative-count publication, bytes negative-count follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-negative-count'` currently passes (`1 passed, 1300 deselected`), so the exact raw-module negative-count parity slice is already green in this checkout;
  - `rg -n 'module-sub-str-negative-count-purged-str|module-subn-str-negative-count-purged-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact Python-path benchmark rows are still absent from the tracked owner-path surfaces;
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on both hypothetical workloads `module-sub-str-negative-count-purged-str` and `module-subn-str-negative-count-purged-str`, so the benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first; and
  - `reports/benchmarks/latest.py` currently reports `957` total / `957` measured / `0` known gaps overall, with `module_workloads == 949`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 408, "warm": 445}`, and `collection-replacement-boundary` at `selected_workload_count == 118`, `measured_workloads == 118`, `known_gap_count == 0`, and `workload_count == 118`.

## Completion
- Added `module-sub-str-negative-count-purged-str` and `module-subn-str-negative-count-purged-str` to `benchmarks/workloads/collection_replacement_boundary.py`, keeping the raw-module literal replacement block on the existing collection/replacement owner-path manifest and ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`.
- Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared collection/replacement owner route now selects those ten module literal replacement workload ids in order, accepts `count == -1` on the existing filter, and anchors the two new workloads to `module-sub-str-negative-count` and `module-subn-str-negative-count` with callback-result parity still enabled.
- Republished `reports/benchmarks/latest.py` on the tracked source-tree-shim path. The tracked report now shows `959` total / `959` measured / `0` known gaps across `30` manifests, with `module_workloads == 951`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 410, "warm": 445}`, and `collection-replacement-boundary` at `selected_workload_count == 120`, `measured_workloads == 120`, `known_gap_count == 0`, and `workload_count == 120`; the matching artifact manifest entry now reports `workload_count == 120`, and both new workload ids publish `status == "measured"`.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-negative-count'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1024-module-replacement-str-negative-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
