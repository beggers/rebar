# RBR-1067: Catch up the direct `Pattern.subn()` str single-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct compiled-pattern `str` `Pattern.subn()` single-match workflow that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc").subn("x", "zabczz")`
- `rebar.compile("abc").subn("x", "zabczz")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly one direct compiled-pattern `str` literal-replacement workload:
  - add `pattern-subn-single-match-warm-str`.
- Keep that workload pinned to the already-published correctness anchor above rather than widening the collection/replacement frontier:
  - `pattern-subn-single-match-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the workload to `pattern-subn-str-single-match`;
  - keep the direct-pattern literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-repeated-warm-str`, `pattern-sub-count-one-warm-str`, `pattern-sub-negative-count-warm-str`, `pattern-sub-bytes-no-match-purged-bytes`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-sub-bytes-repeated-purged-bytes`, `pattern-sub-bytes-count-one-purged-bytes`, `pattern-sub-bytes-negative-count-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-single-match-warm-str`, `pattern-subn-repeated-warm-str`, `pattern-subn-negative-count-warm-str`, `pattern-subn-bytes-count-purged-bytes`, `pattern-subn-bytes-single-match-purged-bytes`, `pattern-subn-bytes-repeated-purged-bytes`, `pattern-subn-bytes-negative-count-purged-bytes`, and `pattern-subn-bytes-no-match-purged-bytes`; and
  - do not widen into direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["pattern"]`, or a strictly equivalent existing owner-path route, so the shared direct-pattern literal-replacement benchmark path now resolves exactly nineteen workload/case pairs in the order listed above;
  - tighten `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured`, or a strictly equivalent existing owner-path assertion, so the selected workload ids now publish in the same nineteen-row order listed above;
  - keep `test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit`, or a strictly equivalent existing benchmark-gap assertion, green by removing `pattern-subn-str-single-match` from the remaining direct-pattern unbenchmarked set on the shared owner path;
  - extend the standard benchmark anchor contract coverage, or tighten an equivalent existing contract on the same file, so the new workload id anchors to `pattern-subn-str-single-match` with callback-result parity still enabled; and
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path instead of widening into native-only publication.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `974` total / `974` measured / `0` known gaps across `30` manifests to `975` / `975` / `0` across the same `30` manifests;
  - `module_workloads` moves from `966` to `967`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 421, "warm": 449}` to `{"cold": 104, "purged": 421, "warm": 450}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 135`, `measured_workloads == 135`, `known_gap_count == 0`, and `workload_count == 135` to `136`, `136`, `0`, and `136`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 135` to `136`, with the new workload id publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and str-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit or standard_benchmark_anchor_contract'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1067-pattern-subn-str-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct compiled-pattern `str` `Pattern.subn()` row above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the one exact direct compiled-pattern `str` `Pattern.subn()` row above. Leave direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1067` is the next available feature task id in the current checkout:
  - `RBR-1065` was just retired as stale because its published correctness end state already exists in the live checkout;
  - `RBR-1066` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the stale-task retirement because once the already-landed direct compiled-pattern `str` `Pattern.subn()` single-match correctness row is normalized out of `ready/`, the next concrete missing same-family owner-path slice is the matching Python-path benchmark row rather than direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile("abc").subn("x", "zabczz") == re.compile("abc").subn("x", "zabczz")` on the live branch;
  - `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `reports/correctness/latest.py` already publish `pattern-subn-str-single-match` on the shared correctness owner path;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit or test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured'` failed only on `pattern-subn-str-single-match` in this run, confirming the exact adjacent benchmark publication gap on the shared owner path;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` currently returns only `("pattern-subn-str-no-match",)`, confirming the matching correctness follow-on stays sequenced behind this benchmark catch-up instead of replacing it; and
  - `reports/benchmarks/latest.py` currently reports `974` total / `974` measured / `0` known gaps overall, with `module_workloads == 966`, `parser_workloads == 8`, `regression_workloads == 8`, `workloads_by_cache_mode == {"cold": 104, "purged": 421, "warm": 449}`, and `collection-replacement-boundary` at `selected_workload_count == 135`, `measured_workloads == 135`, `known_gap_count == 0`, and `workload_count == 135`.
