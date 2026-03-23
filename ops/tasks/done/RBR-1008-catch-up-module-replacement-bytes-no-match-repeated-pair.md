# RBR-1008: Catch up the raw `re.sub()` / `re.subn()` bytes no-match/repeated pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw-module bytes `re.sub()` / `re.subn()` literal no-match/repeated pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zzz")`
- `re.subn(b"abc", b"x", b"abcabc")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module bytes literal-replacement workloads:
  - add `module-sub-bytes-no-match-purged-bytes`; and
  - add `module-subn-bytes-repeated-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `module-sub-bytes-no-match-purged-bytes` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zzz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-bytes-repeated-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `module-sub-bytes-no-match` and `module-subn-bytes-repeated`;
  - keep the raw-module literal replacement slice adjacent on the existing collection/replacement manifest path, with the new `module.sub()` row ordered before the new `module.subn()` row; and
  - do not widen into str module-helper follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - add a focused raw-module literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids above are required to publish as measured on the shared manifest without widening into template, keyword, wrong-text-model, compiled-pattern-first-argument, or direct-`Pattern` replacement selectors;
  - add raw-module literal-replacement anchor coverage, or extend an equivalent existing standard benchmark anchor contract, so `module-sub-bytes-no-match-purged-bytes` anchors to `module-sub-bytes-no-match` and `module-subn-bytes-repeated-purged-bytes` anchors to `module-subn-bytes-repeated` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached module-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `949` total / `949` measured / `0` known gaps across `30` manifests to `951` / `951` / `0` across the same `30` manifests;
  - `module_workloads` moves from `941` to `943`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 400, "warm": 445}` to `{"cold": 104, "purged": 402, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `110` selected / `110` measured / `110` workload-count rows to `112` / `112` / `112`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `110` workload-count rows to `112`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1008-module-replacement-bytes-no-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw-module bytes `re.sub()` / `re.subn()` no-match/repeated pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two raw-module bytes replacement rows above. Leave str module-helper follow-ons, compiled-pattern-first-argument follow-ons, grouped-template rows, callable replacement rows, and deeper raw-module replacement expansion for later tasks.

## Notes
- `RBR-1008` is the next available feature task id in the current checkout:
  - `RBR-1006` is the latest done feature task on the drained raw-module bytes replacement publication frontier;
  - `RBR-1007` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained raw-module bytes `re.sub()` / `re.subn()` correctness publication because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent bytes no-match/repeated pair rather than str module-helper follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-repeated-match)'` currently passes (`2 passed`), so the exact raw-module bytes replacement correctness/parity slice is already green in this checkout;
  - `rg -n 'module-sub-bytes-no-match-purged-bytes|module-subn-bytes-repeated-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact Python-path benchmark rows are still absent from the tracked owner-path surfaces;
  - `reports/benchmarks/latest.py` currently reports `949` total / `949` measured / `0` known gaps overall, with `module_workloads == 941`, `workloads_by_cache_mode == {"cold": 104, "purged": 400, "warm": 445}`, and `collection-replacement-boundary` at `110` selected / `110` measured / `110` workload-count rows; and
  - the landed `RBR-1006` completion note already records synthetic benchmark probes for both hypothetical workload ids returning `status == "measured"` for both adapters, so this follow-on can stay on the existing Python-path benchmark owner route instead of needing another implementation prerequisite first.

## Completion Note
- Landed the two raw-module bytes literal-replacement benchmark rows on `benchmarks/workloads/collection_replacement_boundary.py` as `module-sub-bytes-no-match-purged-bytes` and `module-subn-bytes-repeated-purged-bytes`, with the `module.sub()` row ordered before the adjacent `module.subn()` row on the shared collection/replacement manifest.
- Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with a focused measured-row assertion plus a standard benchmark anchor contract that pins the new workload ids to `module-sub-bytes-no-match` and `module-subn-bytes-repeated` and keeps callback-result parity enabled on the existing owner route.
- Regenerated the tracked source-tree-shim benchmark publication at `reports/benchmarks/latest.py`; the tracked report now reads `951` total / `951` measured / `0` known gaps, `module_workloads == 943`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 402, "warm": 445}`, and `collection-replacement-boundary == 112` selected / `112` measured / `112` workload-count rows with both new workload ids publishing `status == "measured"`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-repeated-match)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1008-module-replacement-bytes-no-match-repeated-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
