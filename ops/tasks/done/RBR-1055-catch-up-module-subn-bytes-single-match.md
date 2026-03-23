# RBR-1055: Catch up the direct `module.subn()` bytes single-match

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct raw-module `bytes` `module.subn()` single-match workflow that the current runtime already matches against CPython and that `RBR-1053` publishes on the shared correctness owner path, keeping this run on the existing collection/replacement benchmark route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.subn(b"abc", b"x", b"zabczz")`
- `rebar.subn(b"abc", b"x", b"zabczz")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly one direct raw-module `bytes` literal-replacement workload:
  - add `module-subn-bytes-single-match-purged-bytes`.
- Keep that workload pinned to the already-published correctness anchor above rather than widening the collection/replacement frontier:
  - `module-subn-bytes-single-match-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the workload to `module-subn-bytes-single-match`;
  - keep the direct raw-module literal replacement measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-count-one-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-sub-bytes-single-match-purged-bytes`, `module-sub-bytes-repeated-purged-bytes`, `module-sub-bytes-count-one-purged-bytes`, `module-subn-bytes-count-purged-bytes`, `module-subn-bytes-single-match-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` bytes single-match, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same fifteen-row order listed above;
  - extend the direct-module literal-replacement anchor coverage in the shared benchmark owner path so the new workload id anchors to `module-subn-bytes-single-match` with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `971` total / `971` measured / `0` known gaps across `30` manifests to `972` / `972` / `0` across the same `30` manifests;
  - `module_workloads` moves from `963` to `964`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 418, "warm": 449}` to `{"cold": 104, "purged": 419, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 132`, `measured_workloads == 132`, `known_gap_count == 0`, and `workload_count == 132` to `133`, `133`, `0`, and `133`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 132` to `133`, with the new workload id publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1055-module-subn-bytes-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct raw-module `bytes` row above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the one exact raw-module `bytes` `module.subn()` row above. Leave direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` bytes single-match, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1055` is the next available feature task id in the current checkout:
  - `RBR-1054` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1053` because once the current ready direct raw-module `bytes` `module.subn()` single-match correctness publication drains, the next concrete missing same-family owner-path slice is the matching Python-path benchmark row rather than direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` bytes single-match, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.subn(b"abc", b"x", b"zabczz") == re.subn(b"abc", b"x", b"zabczz")` on the live branch;
  - `test_source_package_module_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `bytes-single-match` direct module replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently jumps from `module-subn-bytes-count-purged-bytes` to `module-subn-bytes-repeated-purged-bytes`, confirming the exact benchmark publication gap on the shared owner path;
  - `rg -n 'module-subn-bytes-single-match-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, confirming the exact benchmark workload id is still absent from the tracked owner-path surfaces; and
  - `reports/benchmarks/latest.py` currently reports `971` total / `971` measured / `0` known gaps overall, with `module_workloads == 963`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 418, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 132`, `measured_workloads == 132`, `known_gap_count == 0`, and `workload_count == 132`.

## Completion Note
- Completed 2026-03-23. Added `module-subn-bytes-single-match-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py`, extended the shared owner-path benchmark assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and republished `reports/benchmarks/latest.py`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-single-match'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1055-module-subn-bytes-single-match.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
- Published report now shows `972` total / `972` measured / `0` known gaps across `30` manifests, `module_workloads == 964`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 419, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 133`, `measured_workloads == 133`, `known_gap_count == 0`, and `workload_count == 133`, with the new workload publishing as `status == "measured"`.
