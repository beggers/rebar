# RBR-1048: Catch up the direct `module.sub()` str count-one singleton

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct raw-module `str` `module.sub()` count-bounded singleton that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", 1)`
- `rebar.sub("abc", "x", "abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly one direct raw-module `str` literal-replacement workload:
  - add `module-sub-str-count-one-purged-str`.
- Keep that workload pinned to the already-published correctness anchor above rather than widening the collection/replacement frontier:
  - `module-sub-str-count-one-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the workload to `module-sub-str-count-one`;
  - keep the direct raw-module literal replacement measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-count-one-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-sub-bytes-repeated-purged-bytes`, `module-sub-bytes-count-one-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into any `module-sub-bytes-single-match` follow-on, direct raw-module `subn()` str count-one follow-ons, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend `test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured`, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same thirteen-row order listed above;
  - extend the direct-module literal-replacement anchor coverage in the shared benchmark owner path so the new workload id anchors to `module-sub-str-count-one` with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `969` total / `969` measured / `0` known gaps across `30` manifests to `970` / `970` / `0` across the same `30` manifests;
  - `module_workloads` moves from `961` to `962`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 416, "warm": 449}` to `{"cold": 104, "purged": 417, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 130`, `measured_workloads == 130`, `known_gap_count == 0`, and `workload_count == 130` to `131`, `131`, `0`, and `131`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 130` to `131`, with the new workload id publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-count-one'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1048-module-sub-str-count-one-singleton.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct raw-module `str` count-bounded row above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the one exact raw-module `str` `module.sub()` row above. Leave any bytes single-match follow-on, direct raw-module `subn()` str count-one follow-on, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1048` is the next available feature task id in the current checkout:
  - `RBR-1047` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1046` because the newest done frontier closed the adjacent direct raw-module `str` count-bounded correctness publication, and the next concrete missing same-family owner-path slice is the matching Python-path benchmark row rather than a bytes single-match follow-on, a direct raw-module `subn()` follow-on, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already contains the direct source-package `str-count-one` case, so the runtime parity slice is already exercised on the shared owner path;
  - a direct runtime probe in this run confirmed `rebar.sub("abc", "x", "abcabc", 1) == re.sub("abc", "x", "abcabc", 1)` on the live branch;
  - `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently jumps from `module-sub-str-repeated-purged-str` to `module-sub-str-negative-count-purged-str`, confirming the exact benchmark publication gap on the shared owner path;
  - `rg -n 'module-sub-str-count-one-purged-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, confirming the exact benchmark workload id is still absent from the tracked owner-path surfaces; and
  - `reports/benchmarks/latest.py` currently reports `969` total / `969` measured / `0` known gaps overall, with `module_workloads == 961`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 416, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 130`, `measured_workloads == 130`, `known_gap_count == 0`, and `workload_count == 130`.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a tracked state refresh in the same run.

## Completion Note
- 2026-03-23: Added the direct raw-module `str` count-one workload `module-sub-str-count-one-purged-str` to `benchmarks/workloads/collection_replacement_boundary.py` in the required owner-path order, extended the shared ordered owner-route tuple and measured-row assertion in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and regenerated the tracked combined benchmark publication at `reports/benchmarks/latest.py`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-count-one'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1048-module-sub-str-count-one-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
- Verified from the tracked published report that `reports/benchmarks/latest.py` now contains `module-sub-str-count-one-purged-str` with `status == "measured"`, the combined summary is `970` total / `970` measured / `0` known gaps across `30` manifests, `module_workloads == 962`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 417, "warm": 449}`, and `collection-replacement-boundary` now reports `selected_workload_count == 131`, `measured_workloads == 131`, `known_gap_count == 0`, and `workload_count == 131`, with the matching tracked artifact manifest record also at `workload_count == 131`.
