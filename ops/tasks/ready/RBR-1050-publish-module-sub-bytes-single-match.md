# RBR-1050: Publish the direct `module.sub()` bytes single-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct raw-module `bytes` `sub()` single-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zabczz")`
- `rebar.sub(b"abc", b"x", b"zabczz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `module_call` row:
  - add `module-sub-bytes-single-match`;
  - keep the row pinned to the exact raw-module workflow above with `helper == "sub"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zabczz"}]`, and categories `["workflow", "sub", "literal", "bytes", "single-match"]`;
  - insert `module-sub-bytes-single-match` immediately after `module-sub-bytes-no-match`;
  - keep `module-sub-bytes-repeated` immediately after `module-sub-bytes-single-match`; and
  - do not widen into benchmark rows, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES`, or a strictly equivalent existing owner-path selector, so the shared direct source-package `module.sub()` parity route now includes the `bytes-single-match` case on the same file;
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves exactly fourteen rows in this order:
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
    - `module-subn-bytes-repeated`
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-sub-bytes-single-match == (b"abc", b"x", b"zabczz")` on the same file; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1588` total / `1588` passed / `0` failed / `0` unimplemented across `114` manifests to `1589` / `1589` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `51` total / `51` passed to `52` / `52`;
  - `collection.replacement.workflow.bytes` moves from `19` total / `19` passed to `20` / `20`;
  - `collection.replacement.workflow.str` stays `32` total / `32` passed;
  - `collection.replacement.workflow.module_call` moves from `23` total / `23` passed to `24` / `24`;
  - `collection.replacement.workflow.pattern_call` stays `28` total / `28` passed; and
  - the new `module-sub-bytes-single-match` row is visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-single-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1050-module-sub-bytes-single-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the one direct raw-module `bytes` `sub()` single-match row above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1050` is the next available feature task id in the current checkout:
  - `RBR-1049` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1048` because the newest done frontier closed the adjacent direct raw-module `str` count-one benchmark catch-up, and the next concrete unpublished same-family owner-path gap is the deferred `module-sub-bytes-single-match` correctness row rather than another benchmark-only slice, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.sub(b"abc", b"x", b"zabczz") == re.sub(b"abc", b"x", b"zabczz")` on the live branch;
  - `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS` in `tests/python/test_fixture_backed_replacement_parity_suite.py` currently jumps from `module-sub-bytes-no-match` to `module-sub-bytes-repeated`, confirming the exact adjacent raw-module `bytes` publication gap on the shared correctness path;
  - `rg -n 'module-sub-bytes-single-match' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` returned no matches in this run, confirming the exact correctness publication id is still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload id `module-sub-bytes-single-match-purged-bytes` is also absent from `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a tracked state refresh in the same run.
