# RBR-1014: Publish the raw `re.subn()` str count/repeated pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent raw-module `str` literal `re.subn()` count/repeated pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible module-helper outcomes before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.subn("abc", "x", "abcabc", 1)`
- `re.subn("abc", "x", "abcabc")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new raw-module `module_call` rows:
  - add `module-subn-str-count`; and
  - add `module-subn-str-repeated`.
- Keep those two rows pinned to the exact module-helper workflows above rather than widening the collection frontier:
  - `module-subn-str-count` uses `helper == "subn"`, `text_model == "str"`, `args == ["abc", "x", "abcabc", 1]`, and categories `["workflow", "subn", "literal", "str", "count"]`;
  - `module-subn-str-repeated` uses `helper == "subn"`, `text_model == "str"`, `args == ["abc", "x", "abcabc"]`, and categories `["workflow", "subn", "literal", "str", "repeated"]`;
  - insert `module-subn-str-count` immediately after `module-sub-str-repeated`;
  - insert `module-subn-str-repeated` immediately after `module-subn-str-count`; and
  - keep the raw-module literal replacement block ordered as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-subn-str-count`, `module-subn-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated` immediately before the direct compiled-pattern replacement block, without widening into a benchmark update, `sub()` count follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module replacement publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published raw-module literal replacement rows in order as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-subn-str-count`, `module-subn-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated`;
  - tighten the existing published raw-module literal-replacement assertion path so the selected rows above are checked for order, helper, args, and text-model alignment on the same file;
  - keep the direct source-package module literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep the direct compiled-pattern replacement publication path, grouped-template rows, callable rows, and mixed-text-model replacement ownership checks honest while widening only this raw-module `str` `subn()` pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1573` total / `1573` passed / `0` failed / `0` unimplemented across `114` manifests to `1575` / `1575` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `36` total / `36` passed to `38` / `38`;
  - `collection.replacement.workflow.str` moves from `23` total / `23` passed to `25` / `25`;
  - `collection.replacement.workflow.bytes` stays `13` total / `13` passed;
  - `collection.replacement.workflow.module_call` moves from `16` total / `16` passed to `18` / `18`; and
  - `collection.replacement.workflow.pattern_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1014-module-replacement-str-subn-count-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the two raw-module `str` `re.subn()` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, `sub()` count follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1014` is the next available feature task id in the current checkout:
  - `RBR-1012` is the latest done feature task on the drained raw-module `str` replacement benchmark frontier;
  - `RBR-1013` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained raw-module `str` no-match/single-match benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent raw-module `str` `subn()` count/repeated pair rather than another benchmark-only expansion, `sub()` count follow-ons, bytes follow-ons, compiled-pattern-first-argument rows, grouped-template rows, or callable replacement rows.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'` currently passes (`2 passed`), so the exact raw-module `str` `subn()` count/repeated parity slice is already green in this checkout;
  - direct runtime probes confirm `rebar.subn("abc", "x", "abcabc", 1) == re.subn("abc", "x", "abcabc", 1)` and `rebar.subn("abc", "x", "abcabc") == re.subn("abc", "x", "abcabc")` on the live branch; and
  - `rg -n 'module-subn-str-count|module-subn-str-repeated|module-subn-str-count-purged-str|module-subn-str-repeated-purged-str' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark ids are still absent from the tracked owner-path surfaces.
