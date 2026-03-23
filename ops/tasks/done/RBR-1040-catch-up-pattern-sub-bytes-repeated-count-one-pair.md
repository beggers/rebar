# RBR-1040: Catch up the direct `Pattern.sub()` bytes repeated/count-one pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct compiled-pattern `bytes` `Pattern.sub()` repeated/count-bounded pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc")`
- `re.compile(b"abc").sub(b"x", b"abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct compiled-pattern `bytes` literal-replacement workloads:
  - add `pattern-sub-bytes-repeated-purged-bytes`; and
  - add `pattern-sub-bytes-count-one-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-bytes-repeated-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-sub-bytes-count-one-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-bytes-repeated` and `pattern-sub-bytes-count-one`;
  - keep the direct-pattern literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-repeated-warm-str`, `pattern-sub-count-one-warm-str`, `pattern-sub-negative-count-warm-str`, `pattern-sub-bytes-no-match-purged-bytes`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-sub-bytes-repeated-purged-bytes`, `pattern-sub-bytes-count-one-purged-bytes`, `pattern-sub-bytes-negative-count-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`, `pattern-subn-negative-count-warm-str`, `pattern-subn-bytes-count-purged-bytes`, `pattern-subn-bytes-repeated-purged-bytes`, and `pattern-subn-bytes-negative-count-purged-bytes`; and
  - do not widen into raw-module rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused direct-pattern literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same sixteen-row order listed above;
  - extend the direct-pattern literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `pattern-sub-bytes-repeated` and `pattern-sub-bytes-count-one` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached pattern-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `965` total / `965` measured / `0` known gaps across `30` manifests to `967` / `967` / `0` across the same `30` manifests;
  - `module_workloads` moves from `957` to `959`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 412, "warm": 449}` to `{"cold": 104, "purged": 414, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 126`, `measured_workloads == 126`, `known_gap_count == 0`, and `workload_count == 126` to `128`, `128`, `0`, and `128`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 126` to `128`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-repeated-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1040-pattern-sub-bytes-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct compiled-pattern `bytes` repeated/count-bounded rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact direct-pattern `bytes` `Pattern.sub()` rows above. Leave raw-module follow-ons, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1040` is the next available feature task id in the current checkout:
  - `RBR-1039` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1038` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the adjacent direct compiled-pattern `bytes` repeated/count-bounded workloads rather than another correctness publication slice, raw-module follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `RBR-1038` already published the adjacent correctness ids `pattern-sub-bytes-repeated` and `pattern-sub-bytes-count-one` on `tests/conformance/fixtures/collection_replacement_workflows.py`;
  - the shared source-package parity route in `tests/python/test_fixture_backed_replacement_parity_suite.py` already carries the `bytes-repeated-match` and `bytes-count-one` direct compiled-pattern cases, and a direct runtime probe confirms `rebar.compile(b"abc").sub(b"x", b"abcabc") == re.compile(b"abc").sub(b"x", b"abcabc")` plus `rebar.compile(b"abc").sub(b"x", b"abcabc", 1) == re.compile(b"abc").sub(b"x", b"abcabc", 1)` on the live branch;
  - `rg -n 'pattern-sub-bytes-repeated-purged-bytes|pattern-sub-bytes-count-one-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact benchmark workload ids are still absent from the tracked owner-path surfaces; and
  - `reports/benchmarks/latest.py` currently reports `965` total / `965` measured / `0` known gaps overall, with `module_workloads == 957`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 412, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 126`, `measured_workloads == 126`, `known_gap_count == 0`, and `workload_count == 126`.

## Completion
- 2026-03-23: Added `pattern-sub-bytes-repeated-purged-bytes` and `pattern-sub-bytes-count-one-purged-bytes` to the existing `collection-replacement-boundary` manifest, kept the shared direct-pattern literal replacement assertion/anchor route at the required sixteen-row order, and republished `reports/benchmarks/latest.py` on the tracked source-tree-shim path. The tracked report now shows `967` total / `967` measured / `0` known gaps across `30` manifests, `module_workloads == 959`, `workloads_by_cache_mode == {"cold": 104, "purged": 414, "warm": 449}`, and `collection-replacement-boundary` at `128` selected/measured/workload rows with both new workload ids published as `measured`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1040-pattern-sub-bytes-repeated-count-one-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`. The task-file parity `-k` selector deselected all cases on this branch, so the equivalent direct test function was used as the narrow public-surface gate instead.
