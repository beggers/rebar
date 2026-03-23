# RBR-1034: Publish the direct `Pattern.sub()` str repeated/count-one pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct compiled-pattern `str` `Pattern.sub()` repeated/count-bounded pair that the live runtime already matches against CPython, publishing the exact module-boundary outcomes before any same-owner benchmark catch-up widens `collection_replacement_boundary.py`.

## Pattern Pair
- `re.compile("abc").sub("x", "abcabc")`
- `re.compile("abc").sub("x", "abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `pattern-sub-str-repeated`; and
  - add `pattern-sub-str-count-one`.
- Keep those two rows pinned to the exact compiled-pattern workflows above rather than widening the collection frontier:
  - `pattern-sub-str-repeated` uses `pattern == "abc"`, `helper == "sub"`, `args == ["x", "abcabc"]`, and categories `["workflow", "sub", "literal", "str", "repeated"]`;
  - `pattern-sub-str-count-one` uses `pattern == "abc"`, `helper == "sub"`, `args == ["x", "abcabc", 1]`, and categories `["workflow", "sub", "literal", "str", "count-one"]`;
  - insert `pattern-sub-str-repeated` immediately after `pattern-sub-str-single-match`;
  - insert `pattern-sub-str-count-one` immediately after `pattern-sub-str-repeated`;
  - keep `pattern-sub-str-negative-count` immediately after `pattern-sub-str-count-one`; and
  - keep the direct compiled-pattern literal replacement block ordered as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-sub-str-repeated`, `pattern-sub-str-count-one`, `pattern-sub-str-negative-count`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-subn-str-negative-count`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-sub-bytes-negative-count`, `pattern-subn-bytes-count`, `pattern-subn-bytes-repeated`, and `pattern-subn-bytes-negative-count`, without widening into bytes repeated/count-one follow-ons, raw-module follow-ons, grouped-template rows, callable replacement rows, benchmark manifests, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached `Pattern.sub()` publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves the fourteen rows in the exact order listed above;
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-sub-str-repeated == ("x", "abcabc")` and `pattern-sub-str-count-one == ("x", "abcabc", 1)` on the same file;
  - keep the existing direct source-package `Pattern.sub()` helper parity coverage on the same file and ensure the already-present `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` `str-repeated-match` and `str-count-one` cases remain selected by the shared coverage path rather than introducing another replacement-only test module; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached direct-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1581` total / `1581` passed / `0` failed / `0` unimplemented across `114` manifests to `1583` / `1583` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `44` total / `44` passed to `46` / `46`;
  - `collection.replacement.workflow.str` moves from `29` total / `29` passed to `31` / `31`;
  - `collection.replacement.workflow.pattern_call` moves from `24` total / `24` passed to `26` / `26`;
  - `collection.replacement.workflow.bytes` stays `15` total / `15` passed; and
  - `collection.replacement.workflow.module_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-repeated-match or str-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1034-pattern-sub-str-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-pattern replacement publication file.
- Keep the scope pinned to the two direct compiled-pattern `str` `Pattern.sub()` rows above. Leave bytes repeated/count-one follow-ons, the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1034` is the next available feature task id in the current checkout:
  - `RBR-1033` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1032` because the next concrete unpublished same-family owner-path gap is the adjacent direct compiled-pattern `Pattern.sub()` `str` repeated/count-bounded correctness pair rather than bytes follow-ons, another benchmark-only slice, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - direct runtime probes confirm `rebar.compile("abc").sub("x", "abcabc") == re.compile("abc").sub("x", "abcabc")` and `rebar.compile("abc").sub("x", "abcabc", 1) == re.compile("abc").sub("x", "abcabc", 1)` on the live branch;
  - `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already contains the source-package `str-repeated-match` and `str-count-one` cases, so the runtime parity slice is already exercised on the shared owner path;
  - `rg -n 'pattern-sub-str-repeated|pattern-sub-str-count-one' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py benchmarks/workloads/collection_replacement_boundary.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark publication ids are still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload ids `pattern-sub-repeated-warm-str` and `pattern-sub-count-one-warm-str` are also absent from `benchmarks/workloads/collection_replacement_boundary.py`, so benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
