# RBR-1020: Catch up the raw module literal replacement str/bytes benchmark pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the two remaining raw-module literal replacement rows that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub("abc", "x", "abcabc")`
- `re.subn(b"abc", b"x", b"abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module literal-replacement workloads:
  - add `module-sub-str-repeated-purged-str`; and
  - add `module-subn-bytes-count-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-sub-str-repeated-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-bytes-count-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-sub-str-repeated` and `module-subn-bytes-count`;
  - keep the raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into raw-module `str`/`bytes` replacement follow-ons beyond those two rows, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused raw-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in order as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`;
  - extend the raw-module literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `module-sub-str-repeated` and `module-subn-bytes-count` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `955` total / `955` measured / `0` known gaps across `30` manifests to `957` / `957` / `0` across the same `30` manifests;
  - `module_workloads` moves from `947` to `949`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 406, "warm": 445}` to `{"cold": 104, "purged": 408, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 116`, `measured_workloads == 116`, `known_gap_count == 0`, and `workload_count == 116` to `118`, `118`, `0`, and `118`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 116` to `118`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1020-module-replacement-str-repeated-bytes-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw-module literal replacement rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact raw-module rows above. Leave broader raw-module bytes/str follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1020` is the next available feature task id in the current checkout:
  - `RBR-1016` is the latest done feature task on the drained raw-module literal replacement benchmark frontier;
  - `RBR-1017` through `RBR-1019` are already occupied by architecture tasks in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1016` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the remaining raw-module literal replacement anchors `module-sub-str-repeated` and `module-subn-bytes-count`, rather than another correctness-publication slice, a new manifest lane, compiled-pattern-first-argument rows, grouped-template rows, or callable replacement work.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or bytes-count-one)'` currently passes (`2 passed, 1299 deselected`), so the exact raw-module `str` repeated `sub()` and bytes count-limited `subn()` parity slice is already green in this checkout;
  - `rg -n 'module-sub-str-repeated-purged-str|module-subn-bytes-count-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact Python-path benchmark rows are still absent from the tracked owner-path surfaces;
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on both hypothetical workloads `module-sub-str-repeated-purged-str` and `module-subn-bytes-count-purged-bytes`, so the benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first; and
  - `reports/benchmarks/latest.py` currently reports `955` total / `955` measured / `0` known gaps overall, with `module_workloads == 947`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 406, "warm": 445}`, and `collection-replacement-boundary` at `selected_workload_count == 116`, `measured_workloads == 116`, `known_gap_count == 0`, and `workload_count == 116`.

## Completion
- Added `module-sub-str-repeated-purged-str` and `module-subn-bytes-count-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py`, keeping the raw-module literal replacement slice on the existing owner-path manifest and ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`.
- Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared collection/replacement benchmark owner route now selects those eight module literal replacement workload ids in order, anchors the new rows to `module-sub-str-repeated` and `module-subn-bytes-count`, and expects the published full-suite summary to move to `957` total / `957` measured with `949` module workloads.
- Republished `reports/benchmarks/latest.py` on the tracked source-tree-shim path. The tracked report now shows `957` total / `957` measured / `0` known gaps across `30` manifests, `module_workloads == 949`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 408, "warm": 445}`, and `collection-replacement-boundary` at `selected_workload_count == 118`, `measured_workloads == 118`, `known_gap_count == 0`, and `workload_count == 118`, with both new workload ids published as `status == "measured"`.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or bytes-count-one)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1020-module-replacement-str-repeated-bytes-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
