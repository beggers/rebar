# RBR-1052: Catch up the direct `module.sub()` bytes single-match

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct raw-module `bytes` `module.sub()` single-match workflow that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zabczz")`
- `rebar.sub(b"abc", b"x", b"zabczz")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly one direct raw-module `bytes` literal-replacement workload:
  - add `module-sub-bytes-single-match-purged-bytes`.
- Keep that workload pinned to the already-published correctness anchor above rather than widening the collection/replacement frontier:
  - `module-sub-bytes-single-match-purged-bytes` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the workload to `module-sub-bytes-single-match`;
  - keep the direct raw-module literal replacement measured workload ids ordered as `module-sub-str-no-match-purged-str`, `module-sub-str-single-match-purged-str`, `module-sub-str-repeated-purged-str`, `module-sub-str-count-one-purged-str`, `module-sub-str-negative-count-purged-str`, `module-subn-str-count-purged-str`, `module-subn-str-repeated-purged-str`, `module-subn-str-negative-count-purged-str`, `module-sub-bytes-no-match-purged-bytes`, `module-sub-bytes-single-match-purged-bytes`, `module-sub-bytes-repeated-purged-bytes`, `module-sub-bytes-count-one-purged-bytes`, `module-subn-bytes-count-purged-bytes`, and `module-subn-bytes-repeated-purged-bytes`; and
  - do not widen into direct raw-module `subn()` bytes single-match follow-ons, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same fourteen-row order listed above;
  - extend the direct-module literal-replacement anchor coverage in the shared benchmark owner path so the new workload id anchors to `module-sub-bytes-single-match` with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `970` total / `970` measured / `0` known gaps across `30` manifests to `971` / `971` / `0` across the same `30` manifests;
  - `module_workloads` moves from `962` to `963`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 417, "warm": 449}` to `{"cold": 104, "purged": 418, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 131`, `measured_workloads == 131`, `known_gap_count == 0`, and `workload_count == 131` to `132`, `132`, `0`, and `132`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 131` to `132`, with the new workload id publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1052-module-sub-bytes-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct raw-module `bytes` row above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the one exact raw-module `bytes` `module.sub()` row above. Leave any direct raw-module `subn()` bytes single-match follow-on, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1052` is the next available feature task id in the current checkout:
  - `RBR-1051` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1050` because the newest done frontier closed the adjacent direct raw-module `bytes` single-match correctness publication, and the next concrete missing same-family owner-path slice is the matching Python-path benchmark row rather than a direct raw-module `subn()` follow-on, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `module-sub-bytes-single-match` is already published in `tests/conformance/fixtures/collection_replacement_workflows.py` and selected on the shared owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py`;
  - a direct runtime probe in this run confirmed `rebar.sub(b"abc", b"x", b"zabczz") == re.sub(b"abc", b"x", b"zabczz")` on the live branch;
  - `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently jumps from `module-sub-bytes-no-match-purged-bytes` to `module-sub-bytes-repeated-purged-bytes`, confirming the exact benchmark publication gap on the shared owner path;
  - `rg -n 'module-sub-bytes-single-match-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, confirming the exact benchmark workload id is still absent from the tracked owner-path surfaces; and
  - `reports/benchmarks/latest.py` currently reports `970` total / `970` measured / `0` known gaps overall, with `module_workloads == 962`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 417, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 131`, `measured_workloads == 131`, `known_gap_count == 0`, and `workload_count == 131`.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a tracked state refresh in the same run.
- 2026-03-23T11:27:45+00:00: harness requeued after failed or incomplete run after run `20260323T112643Z-feature-implementation-RBR-1052-catch-up-module-sub-bytes-single-match` (exit=1, timed_out=false).
- 2026-03-23T11:48:24+00:00: completed by refreshing the stale published full-suite summary assertion in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and republishing `reports/benchmarks/latest.py` after confirming the scoped workload row and owner-path anchor coverage were already present in this checkout. Verified with the bounded replacement parity slice, the shared benchmark owner-route checks, a narrow `collection_replacement_boundary.py` benchmark run (`132/132` measured), and a full published benchmark refresh (`971` total / `971` measured / `0` known gaps; `collection-replacement-boundary` at `132` workloads with `module-sub-bytes-single-match-purged-bytes` published as `measured`).
