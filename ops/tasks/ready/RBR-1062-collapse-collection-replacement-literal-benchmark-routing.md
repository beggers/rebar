# RBR-1062: Collapse collection/replacement literal benchmark routing

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining hand-maintained direct literal replacement benchmark routing in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the module and pattern collection/replacement literal benchmark surfaces derive their ordered workload ids and correctness anchors through one canonical same-file route instead of two parallel workload/case pair tables.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these one-off direct literal replacement benchmark tables:
  - `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`
  - `_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`
- Replace that split with one explicit same-file routing surface, or a strictly smaller equivalent, reused by all of these existing benchmark consumers:
  - `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured`;
  - `test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured`;
  - `_pattern_collection_replacement_literal_replacement_correctness_case_signature(...)`;
  - `_module_collection_replacement_literal_replacement_correctness_case_signature(...)`;
  - `_is_collection_replacement_pattern_literal_replacement_workload(...)`;
  - `_is_collection_replacement_module_literal_replacement_workload(...)`;
  - the `collection-replacement-module-literal-replacement` standard benchmark anchor contract; and
  - the `collection-replacement-pattern-literal-replacement` standard benchmark anchor contract.
- Keep the current direct pattern literal benchmark contract intact after the cleanup:
  - the routed pattern workload ids still stay exactly, in order:
    - `pattern-sub-no-match-warm-str`
    - `pattern-sub-single-match-warm-str`
    - `pattern-sub-repeated-warm-str`
    - `pattern-sub-count-one-warm-str`
    - `pattern-sub-negative-count-warm-str`
    - `pattern-sub-bytes-no-match-purged-bytes`
    - `pattern-sub-bytes-single-match-purged-bytes`
    - `pattern-sub-bytes-repeated-purged-bytes`
    - `pattern-sub-bytes-count-one-purged-bytes`
    - `pattern-sub-bytes-negative-count-purged-bytes`
    - `pattern-subn-count-warm-str`
    - `pattern-subn-repeated-warm-str`
    - `pattern-subn-negative-count-warm-str`
    - `pattern-subn-bytes-count-purged-bytes`
    - `pattern-subn-bytes-single-match-purged-bytes`
    - `pattern-subn-bytes-repeated-purged-bytes`
    - `pattern-subn-bytes-negative-count-purged-bytes`
  - the routed pattern correctness anchor case ids still stay exactly, in order:
    - `pattern-sub-str-no-match`
    - `pattern-sub-str-single-match`
    - `pattern-sub-str-repeated`
    - `pattern-sub-str-count-one`
    - `pattern-sub-str-negative-count`
    - `pattern-sub-bytes-no-match`
    - `pattern-sub-bytes-single-match`
    - `pattern-sub-bytes-repeated`
    - `pattern-sub-bytes-count-one`
    - `pattern-sub-bytes-negative-count`
    - `pattern-subn-str-count`
    - `pattern-subn-str-repeated`
    - `pattern-subn-str-negative-count`
    - `pattern-subn-bytes-count`
    - `pattern-subn-bytes-single-match`
    - `pattern-subn-bytes-repeated`
    - `pattern-subn-bytes-negative-count`
  - `test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured` still proves the same 17 measured rows on the shared collection/replacement manifest.
- Keep the current direct module literal benchmark contract intact after the cleanup:
  - the routed module workload ids still stay exactly, in order:
    - `module-sub-str-no-match-purged-str`
    - `module-sub-str-single-match-purged-str`
    - `module-sub-str-repeated-purged-str`
    - `module-sub-str-count-one-purged-str`
    - `module-sub-str-negative-count-purged-str`
    - `module-subn-str-count-purged-str`
    - `module-subn-str-repeated-purged-str`
    - `module-subn-str-negative-count-purged-str`
    - `module-sub-bytes-no-match-purged-bytes`
    - `module-sub-bytes-single-match-purged-bytes`
    - `module-sub-bytes-repeated-purged-bytes`
    - `module-sub-bytes-count-one-purged-bytes`
    - `module-subn-bytes-count-purged-bytes`
    - `module-subn-bytes-single-match-purged-bytes`
    - `module-subn-bytes-repeated-purged-bytes`
  - the routed module correctness anchor case ids still stay exactly, in order:
    - `module-sub-str-no-match`
    - `module-sub-str-single-match`
    - `module-sub-str-repeated`
    - `module-sub-str-count-one`
    - `module-sub-str-negative-count`
    - `module-subn-str-count`
    - `module-subn-str-repeated`
    - `module-subn-str-negative-count`
    - `module-sub-bytes-no-match`
    - `module-sub-bytes-single-match`
    - `module-sub-bytes-repeated`
    - `module-sub-bytes-count-one`
    - `module-subn-bytes-count`
    - `module-subn-bytes-single-match`
    - `module-subn-bytes-repeated`
  - `test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured` still proves the same 15 measured rows on the shared collection/replacement manifest; and
  - `test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit` still keeps the benchmark gap set empty for the raw-module literal replacement slice.
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into new manifest files, new helper modules, correctness fixtures, implementation code, benchmark reports, or tracked state docs in this run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'`
- `bash -lc "! rg -n '^_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS\\b|^_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the parallel benchmark workload/case pair tables over introducing another support module, registry file, or generated artifact.
- Keep the existing workload ids, case ids, ordering, measured-row counts, and anchor coverage intact.
- Do not widen into the bounded findall/finditer/split pair tables, compiled-pattern module-helper contract surfaces, or feature work in this run.

## Notes
- `RBR-1062` is the next available unreserved task id in the current checkout:
  - `RBR-1061` is the live ready feature task in `ops/tasks/ready/RBR-1061-publish-pattern-subn-bytes-no-match.md`; and
  - `rg -n 'RBR-1060|RBR-1061|RBR-1062|RBR-1063|RBR-1064' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only for `RBR-1060` and `RBR-1061` in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - the dashboard also reports `Dirty worktree: false`; and
  - the newest runtime cycle shows no inherited-dirty checkpoint churn or stalled post-task refresh path, so the architecture no-op rule does not apply.
- The duplication target is concrete in the live checkout:
  - `rg -n '_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS|_MODULE_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns ten matches, including the two tuple definitions and their downstream consumers; and
  - the same direct literal replacement benchmark routing is currently threaded through measured-row checks, correctness-anchor signatures, workload selectors, and standard anchor-contract definitions in that one file.
- The focused benchmark verification slice already passes in the live checkout: `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or test_collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'` returned `10 passed, 712 deselected, 32 subtests passed`.
