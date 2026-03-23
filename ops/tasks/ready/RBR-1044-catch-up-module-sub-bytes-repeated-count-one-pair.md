# RBR-1044: Catch up the direct `module.sub()` bytes repeated/count-one pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct raw-module `bytes` `module.sub()` repeated/count-bounded pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zabcabc")`
- `re.sub(b"abc", b"x", b"abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct raw-module `bytes` literal-replacement workloads:
  - add `module-sub-bytes-repeated-purged-bytes`; and
  - add `module-sub-bytes-count-one-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-sub-bytes-repeated-purged-bytes` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabcabc"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-sub-bytes-count-one-purged-bytes` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-sub-bytes-repeated` and `module-sub-bytes-count-one`;
  - keep the direct raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-sub-bytes-repeated-purged-bytes`, `module-sub-bytes-count-one-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into the separate `module-sub-str-count-one` singleton gap, any `module-sub-bytes-single-match` follow-on, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused direct-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same twelve-row order listed above;
  - extend the direct-module literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `module-sub-bytes-repeated` and `module-sub-bytes-count-one` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `967` total / `967` measured / `0` known gaps across `30` manifests to `969` / `969` / `0` across the same `30` manifests;
  - `module_workloads` moves from `959` to `961`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 414, "warm": 449}` to `{"cold": 104, "purged": 416, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 128`, `measured_workloads == 128`, `known_gap_count == 0`, and `workload_count == 128` to `130`, `130`, `0`, and `130`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 128` to `130`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-repeated-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1044-module-sub-bytes-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct raw-module `bytes` repeated/count-bounded rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact raw-module `bytes` `module.sub()` rows above. Leave the separate `module-sub-str-count-one` correctness/publication gap, bytes single-match follow-ons, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1044` is the next available feature task id in the current checkout:
  - `RBR-1043` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1042` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the adjacent direct raw-module `bytes` repeated/count-bounded workloads rather than another correctness publication slice, the separate `module-sub-str-count-one` singleton gap, bytes single-match follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `RBR-1042` already published the adjacent correctness ids `module-sub-bytes-repeated` and `module-sub-bytes-count-one` on `tests/conformance/fixtures/collection_replacement_workflows.py`;
  - the shared source-package parity route in `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the `bytes-repeated-match` and `bytes-count-one` direct raw-module cases, confirming the runtime behavior exists on the live branch;
  - `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently jumps from `module-sub-bytes-no-match-purged-bytes` directly to `module-subn-bytes-count-purged-bytes`, confirming the exact benchmark publication gap on the shared owner path;
  - `rg -n 'module-sub-bytes-(repeated|count-one)-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact benchmark workload ids are still absent from the tracked owner-path surfaces; and
  - `reports/benchmarks/latest.py` currently reports `967` total / `967` measured / `0` known gaps overall, with `module_workloads == 959`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 414, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 128`, `measured_workloads == 128`, `known_gap_count == 0`, and `workload_count == 128`.
