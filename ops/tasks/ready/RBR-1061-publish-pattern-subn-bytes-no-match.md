# RBR-1061: Publish the direct `Pattern.subn()` bytes no-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct compiled-pattern `bytes` `subn()` no-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.compile(b"abc").subn(b"x", b"zzz")`
- `rebar.compile(b"abc").subn(b"x", b"zzz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `pattern_call` row:
  - add `pattern-subn-bytes-no-match`;
  - keep the row pinned to the exact compiled-pattern workflow above with `pattern == "abc"`, `helper == "subn"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zzz"}]`, and categories `["workflow", "subn", "literal", "bytes", "no-match"]`;
  - insert `pattern-subn-bytes-no-match` immediately after `pattern-subn-bytes-negative-count`;
  - keep `module-sub-template-str` immediately after `pattern-subn-bytes-no-match`; and
  - do not widen into benchmark rows, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached compiled-pattern publication table:
  - extend `DIRECT_LITERAL_REPLACEMENT_PUBLICATION_ROUTE`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves exactly eighteen rows in this order:
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
    - `pattern-subn-bytes-no-match`
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-subn-bytes-no-match == (b"x", b"zzz")` on the same file; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached compiled-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1591` total / `1591` passed / `0` failed / `0` unimplemented across `114` manifests to `1592` / `1592` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `54` total / `54` passed to `55` / `55`;
  - `collection.replacement.workflow.bytes` moves from `22` total / `22` passed to `23` / `23`;
  - `collection.replacement.workflow.str` stays `32` total / `32` passed; and
  - `collection.replacement.workflow.pattern_call` moves from `29` total / `29` passed to `30` / `30`, with the new `pattern-subn-bytes-no-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-no-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1061-pattern-subn-bytes-no-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern replacement publication file.
- Keep the scope pinned to the one compiled-pattern `bytes` `subn()` no-match row above. Leave the matching Python-path benchmark catch-up, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1061` is the next available feature task id in the current checkout:
  - `RBR-1059` is the live ready feature task in `ops/tasks/ready/RBR-1059-catch-up-pattern-subn-bytes-single-match.md`;
  - `RBR-1060` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1059` because once the active ready direct compiled-pattern `bytes` `Pattern.subn()` single-match benchmark catch-up drains, the next concrete missing same-family owner-path slice is the direct compiled-pattern `bytes` `Pattern.subn()` no-match correctness row rather than the matching benchmark catch-up, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile(b"abc").subn(b"x", b"zzz") == re.compile(b"abc").subn(b"x", b"zzz")` on the live branch;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `bytes-no-match` direct compiled-pattern replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` currently returns `("pattern-subn-str-single-match", "pattern-subn-str-no-match", "pattern-subn-bytes-no-match")`, confirming the exact adjacent unpublished direct-pattern follow-on on the shared owner route;
  - `rg -n 'pattern-subn-bytes-no-match|pattern-subn-bytes-no-match-purged-bytes' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` returns no matches in this checkout, confirming the exact owner-path publication gap remains open; and
  - `reports/correctness/latest.py` currently reports `1591` total / `1591` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `54/54`, `collection.replacement.workflow.bytes` at `22/22`, and `collection.replacement.workflow.pattern_call` at `29/29`.
