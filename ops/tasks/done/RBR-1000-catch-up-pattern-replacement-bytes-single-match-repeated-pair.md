# RBR-1000: Catch up the direct `Pattern.sub()` / `Pattern.subn()` bytes single-match/repeated pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct bytes `Pattern.sub()` / `Pattern.subn()` literal-success pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"zabczz")`
- `re.compile(b"abc").subn(b"x", b"abcabc")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` bytes literal-replacement workloads:
  - add `pattern-sub-bytes-single-match-purged-bytes`; and
  - add `pattern-subn-bytes-repeated-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-bytes-single-match-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-bytes-repeated-purged-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-bytes-single-match` and `pattern-subn-bytes-repeated`;
  - insert `pattern-sub-bytes-single-match-purged-bytes` immediately after `pattern-sub-single-match-warm-str`;
  - insert `pattern-subn-bytes-repeated-purged-bytes` immediately after `pattern-subn-repeated-warm-str`; and
  - keep the smoke workload set unchanged at `module-split-literal-warm-str` and `pattern-subn-literal-purged-bytes` instead of widening smoke coverage in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured(...)`, or an equivalent existing assertion, moves from `106` measured workloads to `108`, preserving the current collection/replacement subsets while adding this bytes pair in the exact selected-workload order `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`, and `pattern-subn-bytes-repeated-purged-bytes`;
  - extend `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_IDS` and `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path definition, so the direct literal replacement contract now includes the six workload ids above and the six published correctness anchors `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-sub-bytes-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, and `pattern-subn-bytes-repeated`;
  - widen `_is_collection_replacement_pattern_literal_replacement_workload(...)`, or a strictly equivalent existing selector, so the shared owner-path contract accepts both `str` and `bytes` direct `Pattern.sub()` / `Pattern.subn()` literal-success workloads without widening into grouped-template rows, wrong-text-model rows, or keyword/count carrier rows;
  - keep the standard benchmark anchor contract on the existing `collection-replacement-boundary` owner route, with callback-result parity still enabled; and
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `945` total / `945` measured / `0` known gaps across `30` manifests to `947` / `947` / `0` across the same `30` manifests;
  - `module_workloads` moves from `937` to `939`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 396, "warm": 445}` to `{"cold": 104, "purged": 398, "warm": 445}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `106` selected / `106` measured / `106` workload-count rows to `108` / `108` / `108`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `106` workload-count rows to `108`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-single-match or bytes-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1000-pattern-replacement-bytes-single-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct bytes `Pattern.sub()` / `Pattern.subn()` single-match/repeated pair above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two direct bytes replacement rows above. Leave grouped-template/callable replacement benchmark slices, bytes module-helper follow-ons, and deeper direct-`Pattern` replacement expansion for later tasks.

## Notes
- `RBR-1000` is the next available feature task id in the current checkout:
  - `RBR-0998` is the latest done feature task on the drained direct-`Pattern` replacement publication frontier;
  - `RBR-0999` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct bytes `Pattern.sub()` / `Pattern.subn()` correctness publication because the next concrete missing Python-path benchmark rows on the same shared owner route are the adjacent bytes single-match/repeated pair rather than grouped-template rows, callable replacement rows, bytes module-helper follow-ons, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-single-match or bytes-repeated-match)'` currently passes (`2 passed`), so the exact direct bytes replacement correctness/parity slice is already green in this checkout;
  - `rg -n 'pattern-sub-bytes-single-match-purged-bytes|pattern-subn-bytes-repeated-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `rg -n 'pattern-sub-bytes-single-match|pattern-subn-bytes-repeated' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py reports/correctness/latest.py` finds both published correctness anchors, confirming the benchmark ids are still absent from the tracked Python-path benchmark surface;
  - a direct synthetic workload probe through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` returns `status == "measured"` for both adapters on both hypothetical workloads `pattern-sub-bytes-single-match-purged-bytes` and `pattern-subn-bytes-repeated-purged-bytes`; and
  - `reports/benchmarks/latest.py` currently reports `945` total / `945` measured / `0` known gaps overall, with `collection-replacement-boundary` at `106` selected / `106` measured / `106` workload-count rows and smoke workload ids `module-split-literal-warm-str` plus `pattern-subn-literal-purged-bytes`.
- 2026-03-23 completion:
  - added `pattern-sub-bytes-single-match-purged-bytes` and `pattern-subn-bytes-repeated-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py` in the required positions without changing the smoke workload set;
  - widened the shared owner-path benchmark assertions in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to the six direct literal replacement ids/anchors, kept callback-result parity enabled, and moved the manifest expectation from `106` to `108` rows;
  - verified the narrow parity subset (`2 passed`) and the targeted benchmark assertions (`2 passed, 6 subtests passed`);
  - regenerated the temporary manifest-local report at `.rebar/tmp/rbr-1000-pattern-replacement-bytes-single-match-repeated-pair.py` with `108` total / `108` measured; and
  - republished the tracked `reports/benchmarks/latest.py`, which now records `947` total / `947` measured / `0` known gaps overall, `939` module workloads, `398` purged workloads, and `collection-replacement-boundary` at `108` selected / `108` measured / `108` workload-count rows.
