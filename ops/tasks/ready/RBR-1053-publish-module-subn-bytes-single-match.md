# RBR-1053: Publish the direct `module.subn()` bytes single-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct raw-module `bytes` `subn()` single-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` follow-ons, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.subn(b"abc", b"x", b"zabczz")`
- `rebar.subn(b"abc", b"x", b"zabczz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `module_call` row:
  - add `module-subn-bytes-single-match`;
  - keep the row pinned to the exact raw-module workflow above with `helper == "subn"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zabczz"}]`, and categories `["workflow", "subn", "literal", "bytes", "single-match"]`;
  - insert `module-subn-bytes-single-match` immediately after `module-subn-bytes-count`;
  - keep `module-subn-bytes-repeated` immediately after `module-subn-bytes-single-match`; and
  - do not widen into benchmark rows, direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` bytes single-match, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves exactly fifteen rows in this order:
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
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-subn-bytes-single-match == (b"abc", b"x", b"zabczz")` on the same file; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1589` total / `1589` passed / `0` failed / `0` unimplemented across `114` manifests to `1590` / `1590` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `52` total / `52` passed to `53` / `53`;
  - `collection.replacement.workflow.bytes` moves from `20` total / `20` passed to `21` / `21`;
  - `collection.replacement.workflow.str` stays `32` total / `32` passed;
  - `collection.replacement.workflow.module_call` moves from `24` total / `24` passed to `25` / `25`;
  - `collection.replacement.workflow.pattern_call` stays `28` total / `28` passed; and
  - the new `module-subn-bytes-single-match` row is visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1053-module-subn-bytes-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the one direct raw-module `bytes` `subn()` single-match row above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` bytes single-match, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1053` is the next available feature task id in the current checkout:
  - `RBR-1052` is already occupied by the active collection/replacement benchmark catch-up task in `ops/tasks/ready/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1052` because once the active direct raw-module `bytes` `module.sub()` benchmark catch-up drains, the next concrete unpublished same-family owner-path gap is the deferred `module.subn()` `bytes` single-match correctness row rather than another benchmark-only slice, direct raw-module `bytes` negative-count or no-match follow-ons, pattern `subn()` follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.subn(b"abc", b"x", b"zabczz") == re.subn(b"abc", b"x", b"zabczz")` on the live branch;
  - `test_source_package_module_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `bytes-single-match` direct module replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS` in `tests/python/test_fixture_backed_replacement_parity_suite.py` currently jumps from `module-subn-bytes-count` to `module-subn-bytes-repeated`, confirming the exact adjacent raw-module `bytes` publication gap on the shared correctness path;
  - `rg -n 'module-subn-bytes-single-match' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` returned no matches in this run, confirming the exact correctness publication id is still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload id `module-subn-bytes-single-match-purged-bytes` is also absent from `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
