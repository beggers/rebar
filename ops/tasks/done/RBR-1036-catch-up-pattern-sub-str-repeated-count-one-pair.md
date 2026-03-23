# RBR-1036: Catch up the direct `Pattern.sub()` str repeated/count-one pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct compiled-pattern `str` `Pattern.sub()` repeated/count-bounded pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc").sub("x", "abcabc")`
- `re.compile("abc").sub("x", "abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct compiled-pattern `str` literal-replacement workloads:
  - add `pattern-sub-repeated-warm-str`; and
  - add `pattern-sub-count-one-warm-str`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-repeated-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-sub-count-one-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-str-repeated` and `pattern-sub-str-count-one`;
  - keep the direct-pattern literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-repeated-warm-str`, `pattern-sub-count-one-warm-str`, `pattern-sub-negative-count-warm-str`, `pattern-sub-bytes-no-match-purged-bytes`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-sub-bytes-negative-count-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`, `pattern-subn-negative-count-warm-str`, `pattern-subn-bytes-count-purged-bytes`, `pattern-subn-bytes-repeated-purged-bytes`, and `pattern-subn-bytes-negative-count-purged-bytes`; and
  - do not widen into bytes repeated/count-one follow-ons, raw-module rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused direct-pattern literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same fourteen-row order listed above;
  - extend the direct-pattern literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `pattern-sub-str-repeated` and `pattern-sub-str-count-one` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached pattern-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `963` total / `963` measured / `0` known gaps across `30` manifests to `965` / `965` / `0` across the same `30` manifests;
  - `module_workloads` moves from `955` to `957`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 412, "warm": 447}` to `{"cold": 104, "purged": 412, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 124`, `measured_workloads == 124`, `known_gap_count == 0`, and `workload_count == 124` to `126`, `126`, `0`, and `126`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 124` to `126`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1036-pattern-sub-str-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct compiled-pattern `str` repeated/count-bounded rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact direct-pattern `str` `Pattern.sub()` rows above. Leave bytes repeated/count-one follow-ons, raw-module rows, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1036` is the next available feature task id in the current checkout:
  - `RBR-1035` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1034` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the adjacent direct compiled-pattern `str` repeated/count-bounded workloads rather than bytes follow-ons, raw-module rows, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `RBR-1034` already published the adjacent correctness ids `pattern-sub-str-repeated` and `pattern-sub-str-count-one` on `tests/conformance/fixtures/collection_replacement_workflows.py`;
  - the shared source-package parity route in `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the `str-repeated-match` and `str-count-one` direct compiled-pattern cases, confirming the runtime behavior exists on the live branch;
  - `rg -n 'pattern-sub-repeated-warm-str|pattern-sub-count-one-warm-str' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact benchmark workload ids are still absent from the tracked owner-path surfaces; and
  - the current benchmark owner-route pair list still exposes only the twelve-row direct-pattern literal replacement slice rooted at `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`, so this benchmark catch-up remains the next bounded same-family follow-on instead of widening into bytes repeated/count-one rows or another owner path.

## Completion Note
- 2026-03-23: Added `pattern-sub-repeated-warm-str` and `pattern-sub-count-one-warm-str` to `benchmarks/workloads/collection_replacement_boundary.py` on the existing direct compiled-pattern replacement block, updated the shared owner-route assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and republished `reports/benchmarks/latest.py` on the tracked source-tree-shim path.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1036-pattern-sub-str-repeated-count-one-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
- Published benchmark report now records `965` total / `965` measured / `0` known gaps across `30` manifests, with `module_workloads == 957`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 412, "warm": 449}`, and `collection-replacement-boundary` at `126` selected/measured workloads with both new workload ids published as `measured`.
