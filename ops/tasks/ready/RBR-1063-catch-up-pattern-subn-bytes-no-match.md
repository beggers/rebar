# RBR-1063: Catch up the direct `Pattern.subn()` bytes no-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct compiled-pattern `bytes` `Pattern.subn()` no-match workflow that the current runtime already exposes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile(b"abc").subn(b"x", b"zzz")`
- `rebar.compile(b"abc").subn(b"x", b"zzz")`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly one direct compiled-pattern `bytes` literal-replacement workload:
  - add `pattern-subn-bytes-no-match-purged-bytes`.
- Keep that workload pinned to the already-sequenced correctness anchor above rather than widening the collection/replacement frontier:
  - `pattern-subn-bytes-no-match-purged-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zzz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the workload to `pattern-subn-bytes-no-match`;
  - keep the direct-pattern literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-repeated-warm-str`, `pattern-sub-count-one-warm-str`, `pattern-sub-negative-count-warm-str`, `pattern-sub-bytes-no-match-purged-bytes`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-sub-bytes-repeated-purged-bytes`, `pattern-sub-bytes-count-one-purged-bytes`, `pattern-sub-bytes-negative-count-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`, `pattern-subn-negative-count-warm-str`, `pattern-subn-bytes-count-purged-bytes`, `pattern-subn-bytes-single-match-purged-bytes`, `pattern-subn-bytes-repeated-purged-bytes`, `pattern-subn-bytes-negative-count-purged-bytes`, and `pattern-subn-bytes-no-match-purged-bytes`; and
  - do not widen into raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend the focused direct-pattern literal-replacement measured-row assertion, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same eighteen-row order listed above;
  - extend the direct-pattern literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload id anchors to `pattern-subn-bytes-no-match` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached pattern-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `973` total / `973` measured / `0` known gaps across `30` manifests to `974` / `974` / `0` across the same `30` manifests;
  - `module_workloads` moves from `965` to `966`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 420, "warm": 449}` to `{"cold": 104, "purged": 421, "warm": 449}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 134`, `measured_workloads == 134`, `known_gap_count == 0`, and `workload_count == 134` to `135`, `135`, `0`, and `135`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 134` to `135`, with the new workload id publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-no-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1063-pattern-subn-bytes-no-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct compiled-pattern `bytes` `Pattern.subn()` no-match row above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the one exact direct compiled-pattern `bytes` `Pattern.subn()` row above. Leave raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1063` is the next available feature task id in the current checkout:
  - `RBR-1061` is the live ready feature task in `ops/tasks/ready/RBR-1061-publish-pattern-subn-bytes-no-match.md`;
  - `RBR-1062` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1061` because once the active ready direct compiled-pattern `bytes` `Pattern.subn()` no-match correctness publication drains, the next concrete missing same-family owner-path slice is the matching Python-path benchmark row rather than direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile(b"abc").subn(b"x", b"zzz") == re.compile(b"abc").subn(b"x", b"zzz")` on the live branch;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `bytes-no-match` direct compiled-pattern replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` currently returns `("pattern-subn-str-single-match", "pattern-subn-str-no-match", "pattern-subn-bytes-no-match")`, confirming the exact adjacent correctness anchor on the shared owner route once `RBR-1061` lands;
  - `rg -n 'pattern-subn-bytes-no-match-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, confirming the exact benchmark workload id is still absent from the tracked owner-path surfaces; and
  - `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["pattern"].workload_case_pairs` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently jumps from `pattern-subn-bytes-negative-count-purged-bytes` back to the next owner family, confirming the exact adjacent benchmark publication gap on the shared owner path.
