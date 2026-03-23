# RBR-1026: Publish the direct `Pattern.sub()` / `Pattern.subn()` str negative-count pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct compiled-pattern `str` literal negative-count pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible `Pattern.sub()` / `Pattern.subn()` `count=-1` outcomes before any later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc").sub("x", "abcabc", -1)`
- `re.compile("abc").subn("x", "abcabc", -1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `pattern-sub-str-negative-count`; and
  - add `pattern-subn-str-negative-count`.
- Keep those two rows pinned to the exact compiled-pattern workflows above rather than widening the collection frontier:
  - `pattern-sub-str-negative-count` uses `pattern == "abc"`, `helper == "sub"`, `args == ["x", "abcabc", -1]`, and categories `["workflow", "sub", "literal", "str", "negative-count"]`;
  - `pattern-subn-str-negative-count` uses `pattern == "abc"`, `helper == "subn"`, `args == ["x", "abcabc", -1]`, and categories `["workflow", "subn", "literal", "str", "negative-count"]`;
  - insert `pattern-sub-str-negative-count` immediately after `pattern-sub-str-single-match`;
  - insert `pattern-subn-str-negative-count` immediately after `pattern-subn-str-repeated`; and
  - keep the direct-pattern literal replacement block ordered as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-sub-str-negative-count`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-subn-str-negative-count`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-subn-bytes-count`, and `pattern-subn-bytes-repeated`, without widening into direct-pattern repeated/count-one publication, module-helper benchmark updates, bytes negative-count follow-ons, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached direct-pattern replacement publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the ten published direct-pattern literal replacement rows in the exact order listed above;
  - tighten the existing published direct-pattern literal-replacement assertion path so the selected rows above are checked for order, helper, args, and text-model alignment on the same file;
  - keep the direct source-package compiled-pattern literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep the direct module replacement publication path, grouped-template rows, callable rows, and mixed-text-model replacement ownership checks honest while widening only this direct-pattern `str` negative-count pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1577` total / `1577` passed / `0` failed / `0` unimplemented across `114` manifests to `1579` / `1579` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `40` total / `40` passed to `42` / `42`;
  - `collection.replacement.workflow.str` moves from `27` total / `27` passed to `29` / `29`;
  - `collection.replacement.workflow.bytes` stays `13` total / `13` passed;
  - `collection.replacement.workflow.module_call` stays `20` total / `20` passed; and
  - `collection.replacement.workflow.pattern_call` moves from `20` total / `20` passed to `22` / `22`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and str-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1026-pattern-replacement-str-negative-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-pattern replacement publication file.
- Keep the scope pinned to the two direct-pattern `str` negative-count rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, direct-pattern bytes negative-count follow-ons, direct-pattern repeated/count-one publication, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1026` is the next available feature task id in the current checkout:
  - `RBR-1024` is the latest done feature task on the drained raw-module `str` negative-count owner path;
  - `RBR-1025` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1024` because the next concrete unpublished same-family owner-path gap is the adjacent direct-pattern `str` negative-count correctness pair rather than another benchmark-only slice, bytes negative-count follow-ons, direct-pattern repeated/count-one publication, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'pattern and negative-count'` currently passes (`7 passed, 1294 deselected`), so the direct compiled-pattern negative-count parity slice is already green in this checkout;
  - a direct runtime probe confirms `rebar.compile("abc").sub("x", "abcabc", -1) == re.compile("abc").sub("x", "abcabc", -1)` and `rebar.compile("abc").subn("x", "abcabc", -1) == re.compile("abc").subn("x", "abcabc", -1)` on the live branch; and
  - a file-local scan across `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `reports/correctness/latest.py` reports `pattern-sub-str-negative-count` and `pattern-subn-str-negative-count` as absent, confirming the exact correctness publication ids are still missing from the tracked owner-path surfaces.
