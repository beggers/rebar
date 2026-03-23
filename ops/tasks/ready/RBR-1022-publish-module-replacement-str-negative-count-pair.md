# RBR-1022: Publish the raw `re.sub()` / `re.subn()` str negative-count pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent raw-module `str` literal negative-count pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible module-helper `count=-1` outcomes before any later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", -1)`
- `re.subn("abc", "x", "abcabc", -1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new raw-module `module_call` rows:
  - add `module-sub-str-negative-count`; and
  - add `module-subn-str-negative-count`.
- Keep those two rows pinned to the exact module-helper workflows above rather than widening the collection frontier:
  - `module-sub-str-negative-count` uses `helper == "sub"`, `text_model == "str"`, `args == ["abc", "x", "abcabc", -1]`, and categories `["workflow", "sub", "literal", "str", "negative-count"]`;
  - `module-subn-str-negative-count` uses `helper == "subn"`, `text_model == "str"`, `args == ["abc", "x", "abcabc", -1]`, and categories `["workflow", "subn", "literal", "str", "negative-count"]`;
  - insert `module-sub-str-negative-count` immediately after `module-sub-str-repeated`;
  - insert `module-subn-str-negative-count` immediately after `module-subn-str-repeated`; and
  - keep the raw-module literal replacement block ordered as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-sub-str-negative-count`, `module-subn-str-count`, `module-subn-str-repeated`, `module-subn-str-negative-count`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated` immediately before the direct compiled-pattern replacement block, without widening into direct-`Pattern` negative-count publication, benchmark updates, bytes follow-ons, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module replacement publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published raw-module literal replacement rows in order as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-sub-str-negative-count`, `module-subn-str-count`, `module-subn-str-repeated`, `module-subn-str-negative-count`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated`;
  - tighten the existing published raw-module literal-replacement assertion path so the selected rows above are checked for order, helper, args, and text-model alignment on the same file;
  - keep the direct source-package module literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep the direct compiled-pattern replacement publication path, grouped-template rows, callable rows, and mixed-text-model replacement ownership checks honest while widening only this raw-module `str` negative-count pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1575` total / `1575` passed / `0` failed / `0` unimplemented across `114` manifests to `1577` / `1577` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `38` total / `38` passed to `40` / `40`;
  - `collection.replacement.workflow.str` moves from `25` total / `25` passed to `27` / `27`;
  - `collection.replacement.workflow.bytes` stays `13` total / `13` passed;
  - `collection.replacement.workflow.module_call` moves from `18` total / `18` passed to `20` / `20`; and
  - `collection.replacement.workflow.pattern_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1022-module-replacement-str-negative-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the two raw-module `str` negative-count rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, direct-`Pattern` negative-count publication, bytes follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1022` is the next available feature task id in the current checkout:
  - `python3` inspection over `ops/state/current_status.md`, `ops/state/backlog.md`, and all task queues reported `RBR-1022` as the first unused `RBR-` number in this run; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1020` because the raw-module literal replacement benchmark surface is now drained on the shared collection/replacement owner route, and the next concrete unpublished owner-path gap is the adjacent raw-module `str` negative-count correctness pair rather than direct-`Pattern` negative-count publication, another benchmark-only expansion, compiled-pattern-first-argument rows, grouped-template rows, or callable replacement work.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-negative-count'` currently passes (`1 passed, 1300 deselected`), so the exact raw-module negative-count parity slice is already green in this checkout;
  - a direct runtime probe confirms `rebar.sub("abc", "x", "abcabc", -1) == re.sub("abc", "x", "abcabc", -1)` and `rebar.subn("abc", "x", "abcabc", -1) == re.subn("abc", "x", "abcabc", -1)` on the live branch; and
  - a file-local scan across `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` reports `module-sub-str-negative-count` and `module-subn-str-negative-count` as absent, confirming the exact correctness publication ids are still missing from the tracked owner-path surfaces.
