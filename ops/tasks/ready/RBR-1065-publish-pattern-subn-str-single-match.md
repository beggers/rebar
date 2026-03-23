# RBR-1065: Publish the direct `Pattern.subn()` str single-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct compiled-pattern `str` `subn()` single-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.compile("abc").subn("x", "zabczz")`
- `rebar.compile("abc").subn("x", "zabczz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `pattern_call` row:
  - add `pattern-subn-str-single-match`;
  - keep the row pinned to the exact compiled-pattern workflow above with `pattern == "abc"`, `helper == "subn"`, `text_model == "str"`, `args == ["x", "zabczz"]`, and categories `["workflow", "subn", "literal", "str", "single-match"]`;
  - insert `pattern-subn-str-single-match` immediately after `pattern-subn-str-count`;
  - keep `pattern-subn-str-repeated` immediately after `pattern-subn-str-single-match`; and
  - do not widen into benchmark rows, direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached compiled-pattern publication table:
  - extend `_direct_literal_replacement_publication_case_ids(surface="pattern")`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves exactly nineteen rows in this order:
    - `pattern-sub-str-no-match`
    - `pattern-sub-str-single-match`
    - `pattern-sub-str-repeated`
    - `pattern-sub-str-count-one`
    - `pattern-sub-str-negative-count`
    - `pattern-subn-str-count`
    - `pattern-subn-str-single-match`
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
    - `pattern-subn-bytes-no-match`
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-subn-str-single-match == ("x", "zabczz")` on the same file; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached compiled-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1592` total / `1592` passed / `0` failed / `0` unimplemented across `114` manifests to `1593` / `1593` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `55` total / `55` passed to `56` / `56`;
  - `collection.replacement.workflow.bytes` stays `23` total / `23` passed;
  - `collection.replacement.workflow.str` moves from `32` total / `32` passed to `33` / `33`; and
  - `collection.replacement.workflow.pattern_call` moves from `30` total / `30` passed to `31` / `31`, with the new `pattern-subn-str-single-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and str-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1065-pattern-subn-str-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern replacement publication file.
- Keep the scope pinned to the one compiled-pattern `str` `subn()` single-match row above. Leave the matching Python-path benchmark catch-up, direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1065` is the next available feature task id in the current checkout:
  - `RBR-1063` is the live ready feature task in `ops/tasks/ready/RBR-1063-catch-up-pattern-subn-bytes-no-match.md`;
  - `RBR-1064` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1063` because once the active ready direct compiled-pattern `bytes` `Pattern.subn()` no-match benchmark catch-up drains, the next concrete missing same-family owner-path slice is the direct compiled-pattern `str` `Pattern.subn()` single-match correctness row rather than the matching benchmark catch-up, direct compiled-pattern `str` `subn()` no-match publication, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile("abc").subn("x", "zabczz") == re.compile("abc").subn("x", "zabczz")` on the live branch;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `str-single-match` direct compiled-pattern replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` currently returns `("pattern-subn-str-single-match", "pattern-subn-str-no-match")`, confirming the exact adjacent unpublished direct-pattern follow-on on the shared owner route once `RBR-1063` lands;
  - `rg -n 'pattern-subn-str-single-match|pattern-subn-str-single-match-warm-str' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` returned matches only in the shared parity-suite unpublished-gap assertion in this run, confirming the exact correctness row and matching benchmark workload are still absent from the tracked owner-path publication surfaces; and
  - because no tracked correctness row exists yet for this direct compiled-pattern `str` single-match `subn()` workflow, the matching Python-path benchmark catch-up should remain sequenced behind this publication task instead of replacing it.
