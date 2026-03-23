## RBR-1011: Collapse direct literal replacement publication contract

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated direct-literal replacement publication contract glue from `tests/python/test_fixture_backed_replacement_parity_suite.py` so the adjacent module and pattern publication tests assert through one smaller file-local helper surface instead of each rebuilding the selected bundle and open-coding the same order/helper/text-model checks.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` adds one explicit file-local helper surface for the shared direct-literal publication contract, or a strictly smaller equivalent, that centralizes the repeated bundle-loading and selected-case contract currently open-coded in:
  - `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order()`
  - `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order()`
- Repoint both tests through that shared helper surface instead of leaving each body to repeat:
  - `build_selected_fixture_bundle(...)` against `collection_replacement_workflows.py`;
  - `cases_by_id = {case.case_id: case for case in bundle.cases}`;
  - one ordered `bundle.cases` assertion plus one owner-operation assertion through `fixture_cases_for_operation(...)`; and
  - per-case `args`, `helper`, and `text_model` assertions for the published direct-literal rows.
- Preserve the current module direct-literal publication contract exactly while shrinking the glue:
  - the selected case ids still stay exactly:
    - `module-sub-str-no-match`
    - `module-sub-str-single-match`
    - `module-sub-str-repeated`
    - `module-sub-bytes-no-match`
    - `module-subn-bytes-count`
    - `module-subn-bytes-repeated`
  - the `module_call` owner slice selected through `fixture_cases_for_operation((bundle,), "module_call")` still stays in that same order;
  - the row arguments still stay exactly:
    - `module-sub-str-no-match` -> `("abc", "x", "zzz")`
    - `module-sub-str-single-match` -> `("abc", "x", "zabczz")`
    - `module-sub-str-repeated` -> `("abc", "x", "abcabc")`
    - `module-sub-bytes-no-match` -> `(b"abc", b"x", b"zzz")`
    - `module-subn-bytes-count` -> `(b"abc", b"x", b"abcabc", 1)`
    - `module-subn-bytes-repeated` -> `(b"abc", b"x", b"abcabc")`
  - the helper sequence still stays `("sub", "sub", "sub", "sub", "subn", "subn")`; and
  - the text-model sequence still stays `("str", "str", "str", "bytes", "bytes", "bytes")`.
- Preserve the current pattern direct-literal publication contract exactly while shrinking the glue:
  - the selected case ids still stay exactly:
    - `pattern-sub-str-no-match`
    - `pattern-sub-str-single-match`
    - `pattern-subn-str-count`
    - `pattern-subn-str-repeated`
    - `pattern-sub-bytes-no-match`
    - `pattern-sub-bytes-single-match`
    - `pattern-subn-bytes-count`
    - `pattern-subn-bytes-repeated`
  - the `pattern_call` owner slice selected through `fixture_cases_for_operation((bundle,), "pattern_call")` still stays in that same order;
  - the row arguments still stay exactly:
    - `pattern-sub-str-no-match` -> `("x", "zzz")`
    - `pattern-sub-str-single-match` -> `("x", "zabczz")`
    - `pattern-subn-str-count` -> `("x", "abcabc", 1)`
    - `pattern-subn-str-repeated` -> `("x", "abcabc")`
    - `pattern-sub-bytes-no-match` -> `(b"x", b"zzz")`
    - `pattern-sub-bytes-single-match` -> `(b"x", b"zabczz")`
    - `pattern-subn-bytes-count` -> `(b"x", b"abcabc", 1)`
    - `pattern-subn-bytes-repeated` -> `(b"x", b"abcabc")`
  - the helper sequence still stays `("sub", "sub", "subn", "subn", "sub", "sub", "subn", "subn")`; and
  - the text-model sequence still stays `("str", "str", "str", "str", "bytes", "bytes", "bytes", "bytes")`.
- Keep the cleanup structural and file-local:
  - do not widen this run into direct replacement parity parametrization, mixed-text surface loading, fixture manifests, correctness harness modules, benchmark files, reports, or tracked state prose;
  - do not add a shared helper module, registry, or checked-in data representation; and
  - prefer deleting repeated assertion glue over introducing another detached abstraction layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Preserve the exact published direct-literal module and pattern row contracts while shrinking the helper/test glue.
- Do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-replacement parity test files in this run.

## Notes
- `RBR-1011` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1011|RBR-1012|RBR-1013|RBR-1014' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in the current checkout.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`2 passed, 1299 deselected`);
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` still repeats the same bundle-loading and selected-case contract shape across the module block at lines `2466`-`2516` and the pattern block at lines `2521`-`2563`; and
  - the cleanup can stay structural and file-local because those two tests differ only in their selected case ids, owner operation, and expected case metadata.
