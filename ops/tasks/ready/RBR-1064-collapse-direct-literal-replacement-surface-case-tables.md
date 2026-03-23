# RBR-1064: Collapse direct literal replacement surface case tables

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining parallel direct-literal replacement case tables in `tests/python/test_fixture_backed_replacement_parity_suite.py` so the module and compiled-pattern replacement surfaces derive their direct parity params and publication routing from one smaller same-file source instead of two near-duplicate hand-maintained tables.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines either of these duplicate direct-literal case tables:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES`
  - `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES`
- Replace that split with one explicit same-file case owner, or a strictly smaller equivalent, reused by all of these existing consumers:
  - `test_source_package_module_literal_replacement_helpers_match_cpython`;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython`; and
  - `_direct_literal_replacement_publication_case_ids(...)`.
- Keep the current direct parity surface intact after the cleanup:
  - `test_source_package_module_literal_replacement_helpers_match_cpython` still runs exactly the current nine direct module rows, with the same param ids and the same omission of the bytes negative-count case;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` still runs exactly the current ten direct compiled-pattern rows, with the same param ids and the same inclusion of the bytes negative-count case; and
  - the direct parity assertions stay file-local to this suite rather than moving into another support helper or another test module.
- Keep the current publication routing contract intact after the cleanup:
  - `_direct_literal_replacement_publication_case_ids(surface="module", selection="unpublished")` still returns `("module-subn-str-single-match", "module-subn-str-no-match", "module-subn-bytes-no-match")`;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` still returns `("pattern-subn-str-single-match", "pattern-subn-str-no-match")`;
  - `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order` still proves the same 15 published module rows, helper ordering, text-model ordering, and argument payloads on `collection_replacement_workflows.py`; and
  - `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order` still proves the same 18 published pattern rows, helper ordering, text-model ordering, and argument payloads on that same owner manifest.
- Keep the cleanup file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`. Do not widen into fixture manifests, benchmark owners, implementation code, reports, tracked state docs, or a new helper module in this run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'source_package_module_literal_replacement_helpers_match_cpython or source_package_pattern_literal_replacement_helpers_match_cpython or literal_replacement_publication_gaps_stay_explicit or collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `bash -lc "! rg -n '^DIRECT_LITERAL_MODULE_REPLACEMENT_CASES =|^DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES =' tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Prefer deleting the parallel case tables over adding another shared support layer, registry, or generated artifact.
- Keep the existing param ids, published case ids, helper ordering, text-model ordering, and argument payloads intact.
- Do not broaden this into direct whole-match template cleanup, literal replacement matrix coverage, benchmark routing, or feature work in this run.

## Notes
- `RBR-1064` is the next available unreserved architecture task id in the current checkout:
  - `RBR-1063` is the live ready feature task in `ops/tasks/ready/`; and
  - `rg -n 'RBR-1064|RBR-1065|RBR-1066' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime stall rule does not apply in this run:
  - the dashboard reports a clean worktree, no blocked tasks, and no last-cycle anomalies; and
  - the last completed architecture task and the current ready feature task both drained through the normal done path.
- The duplication target is concrete in the live checkout:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` and `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` are still defined separately at lines 147 and 158 of `tests/python/test_fixture_backed_replacement_parity_suite.py`; and
  - the focused verification slice already passes in the current checkout: `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'source_package_module_literal_replacement_helpers_match_cpython or source_package_pattern_literal_replacement_helpers_match_cpython or literal_replacement_publication_gaps_stay_explicit or collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'` returned `23 passed, 1283 deselected` in this run.
