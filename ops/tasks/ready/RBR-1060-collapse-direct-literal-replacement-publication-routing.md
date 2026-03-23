# RBR-1060: Collapse direct literal replacement publication routing

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining hand-maintained direct literal replacement publication routing in `tests/python/test_fixture_backed_replacement_parity_suite.py` so the module and pattern publication checks derive their selected case ids through one canonical same-file route instead of parallel published/unpublished tuples plus a module-only ordering helper.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer defines any of these one-off direct literal publication intermediates:
  - `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`
  - `UNPUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`
  - `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`
  - `_DIRECT_MODULE_LITERAL_REPLACEMENT_SUFFIX_ORDER`
  - `_ordered_direct_module_literal_replacement_case_ids(...)`
- Replace that split with one explicit same-file publication-routing surface, or a strictly smaller equivalent, reused by all of these consumers:
  - `test_module_literal_replacement_publication_gaps_stay_explicit`;
  - `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`; and
  - `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`.
- Keep the current direct module publication contract intact after the cleanup:
  - the published module case ids still stay exactly, in order:
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
  - the unpublished module follow-ons still stay exactly, in order:
    - `module-subn-str-single-match`
    - `module-subn-str-no-match`
    - `module-subn-bytes-no-match`
  - `test_module_literal_replacement_publication_gaps_stay_explicit` still proves those two sets are disjoint and partition the full direct module literal replacement case-id sequence.
- Keep the current direct pattern publication contract intact after the cleanup:
  - the published pattern case ids still stay exactly, in order:
    - `pattern-sub-str-no-match`
    - `pattern-sub-str-single-match`
    - `pattern-sub-str-repeated`
    - `pattern-sub-str-count-one`
    - `pattern-sub-str-negative-count`
    - `pattern-subn-str-count`
    - `pattern-subn-str-repeated`
    - `pattern-subn-str-negative-count`
    - `pattern-sub-bytes-no-match`
    - `pattern-sub-bytes-single-match`
    - `pattern-sub-bytes-repeated`
    - `pattern-sub-bytes-count-one`
    - `pattern-sub-bytes-negative-count`
    - `pattern-subn-bytes-count`
    - `pattern-subn-bytes-single-match`
    - `pattern-subn-bytes-repeated`
    - `pattern-subn-bytes-negative-count`
  - the manifest-order assertion still keeps the same helper ordering, text-model ordering, and expected-args payloads already encoded in `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`.
- Keep the direct literal parity parametrization intact after the cleanup:
  - `test_source_package_module_literal_replacement_helpers_match_cpython` still runs against the existing direct module literal replacement cases;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` still runs against the existing direct pattern literal replacement cases; and
  - do not widen into grouped replacement surfaces, callable replacement cases, benchmark manifests, harness code, implementation code, or tracked project-state prose in this run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'module_literal_replacement_publication_gaps_stay_explicit or collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `bash -lc "! rg -n '^(PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS|UNPUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS|PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS|_DIRECT_MODULE_LITERAL_REPLACEMENT_SUFFIX_ORDER)\\b|^def _ordered_direct_module_literal_replacement_case_ids\\(' tests/python/test_fixture_backed_replacement_parity_suite.py"`

## Constraints
- Keep the cleanup file-local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Prefer deleting the hand-maintained publication-routing split over introducing another support module, registry file, generated artifact, or detached helper layer.
- Do not change the selected case ids, helper order, text-model order, payload order, or publication-gap boundary for these direct literal replacement checks.

## Notes
- `RBR-1060` is the next available unreserved task id in the current checkout:
  - `RBR-1059` is the current ready feature task in `ops/tasks/ready/RBR-1059-catch-up-pattern-subn-bytes-single-match.md`; and
  - `rg -n 'RBR-1059|RBR-1060|RBR-1061|RBR-1062|RBR-1063' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only for `RBR-1059` in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the newest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path; and
  - the checkout is currently clean.
- The duplication target is concrete in the live checkout:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` and `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` still sit at lines `147` and `158`;
  - the three hand-maintained published/unpublished case-id tuples still sit at lines `170`, `187`, and `192`; and
  - the remaining module-only ordering helper still sits at lines `245` through `280`.
- The focused verification slice already passes in the live checkout: `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'module_literal_replacement_publication_gaps_stay_explicit or collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'` returned `3 passed, 1302 deselected`.
