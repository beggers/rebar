# RBR-1057: Publish the direct `Pattern.subn()` bytes single-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct compiled-pattern `bytes` `subn()` single-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.compile(b"abc").subn(b"x", b"zabczz")`
- `rebar.compile(b"abc").subn(b"x", b"zabczz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `pattern_call` row:
  - add `pattern-subn-bytes-single-match`;
  - keep the row pinned to the exact compiled-pattern workflow above with `pattern == "abc"`, `helper == "subn"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zabczz"}]`, and categories `["workflow", "subn", "literal", "bytes", "single-match"]`;
  - insert `pattern-subn-bytes-single-match` immediately after `pattern-subn-bytes-count`;
  - keep `pattern-subn-bytes-repeated` immediately after `pattern-subn-bytes-single-match`; and
  - do not widen into benchmark rows, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached compiled-pattern publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves exactly seventeen rows in this order:
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
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-subn-bytes-single-match == (b"x", b"zabczz")` on the same file; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached compiled-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1590` total / `1590` passed / `0` failed / `0` unimplemented across `114` manifests to `1591` / `1591` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `53` total / `53` passed to `54` / `54`;
  - `collection.replacement.workflow.bytes` moves from `21` total / `21` passed to `22` / `22`;
  - `collection.replacement.workflow.str` stays `32` total / `32` passed;
  - `collection.replacement.workflow.module_call` stays `25` total / `25` passed; and
  - `collection.replacement.workflow.pattern_call` moves from `28` total / `28` passed to `29` / `29`, with the new `pattern-subn-bytes-single-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1057-pattern-subn-bytes-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern replacement publication file.
- Keep the scope pinned to the one compiled-pattern `bytes` `subn()` single-match row above. Leave the matching Python-path benchmark catch-up, direct raw-module `subn()` no-match publication, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1057` is the next available feature task id in the current checkout:
  - `RBR-1055` is already occupied by the live feature task in `ops/tasks/ready/RBR-1055-catch-up-module-subn-bytes-single-match.md`;
  - `RBR-1056` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty apart from the queue placeholder in this checkout.
- Queue this directly after `RBR-1055` because once the active ready direct raw-module `bytes` `module.subn()` benchmark catch-up drains, the next concrete missing same-family owner-path slice is the direct compiled-pattern `bytes` `Pattern.subn()` single-match correctness row rather than direct raw-module `subn()` no-match publication, another benchmark-only slice, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile(b"abc").subn(b"x", b"zabczz") == re.compile(b"abc").subn(b"x", b"zabczz")` on the live branch;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `bytes-single-match` direct compiled-pattern replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `tests/conformance/fixtures/collection_replacement_workflows.py` currently jumps from `pattern-subn-bytes-count` to `pattern-subn-bytes-repeated`, confirming the exact adjacent compiled-pattern publication gap on the shared correctness path;
  - `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS` in `tests/python/test_fixture_backed_replacement_parity_suite.py` currently jumps from `pattern-subn-bytes-count` to `pattern-subn-bytes-repeated`, confirming the same owner-path publication gap on the shared parity selector; and
  - `rg -n 'pattern-subn-bytes-single-match|pattern-subn-bytes-single-match-purged-bytes' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` returned no matches in this run, so the matching Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
