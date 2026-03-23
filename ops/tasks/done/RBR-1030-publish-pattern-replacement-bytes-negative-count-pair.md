# RBR-1030: Publish the direct `Pattern.sub()` / `Pattern.subn()` bytes negative-count pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct compiled-pattern bytes negative-count pair that the current runtime already matches on the live branch, publishing the exact CPython-visible `Pattern.sub()` / `Pattern.subn()` `count=-1` bytes outcomes before any later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc", -1)`
- `re.compile(b"abc").subn(b"x", b"abcabc", -1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `pattern-sub-bytes-negative-count`; and
  - add `pattern-subn-bytes-negative-count`.
- Keep those two rows pinned to the exact compiled-pattern workflows above rather than widening the collection frontier:
  - `pattern-sub-bytes-negative-count` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "sub"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}, -1]`, and categories `["workflow", "sub", "literal", "bytes", "negative-count"]`;
  - `pattern-subn-bytes-negative-count` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "subn"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}, -1]`, and categories `["workflow", "subn", "literal", "bytes", "negative-count"]`;
  - insert `pattern-sub-bytes-negative-count` immediately after `pattern-sub-bytes-single-match`;
  - insert `pattern-subn-bytes-negative-count` immediately after `pattern-subn-bytes-repeated`; and
  - keep the direct compiled-pattern literal replacement block ordered as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-sub-str-negative-count`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-subn-str-negative-count`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-sub-bytes-negative-count`, `pattern-subn-bytes-count`, `pattern-subn-bytes-repeated`, and `pattern-subn-bytes-negative-count`, without widening into raw-module bytes negative-count follow-ons, benchmark updates, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached bytes-negative-count publication table:
  - extend `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES`, or a strictly equivalent existing direct source-package parity matrix, so the shared direct `Pattern.sub()` / `Pattern.subn()` replacement coverage now includes `pytest.param(b"abc", b"x", b"abcabc", -1, id="bytes-negative-count")`;
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the twelve published direct literal pattern replacement rows in the exact order listed above;
  - tighten the existing published direct-pattern literal-replacement assertion path so the selected rows above are checked for order, helper, args, and text-model alignment on the same file; and
  - keep the direct source-package compiled-pattern bytes negative-count parity coverage on the same file rather than introducing another replacement-only test module.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1579` total / `1579` passed / `0` failed / `0` unimplemented across `114` manifests to `1581` / `1581` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `42` total / `42` passed to `44` / `44`;
  - `collection.replacement.workflow.bytes` moves from `13` total / `13` passed to `15` / `15`;
  - `collection.replacement.workflow.str` stays `29` total / `29` passed;
  - `collection.replacement.workflow.pattern_call` moves from `22` total / `22` passed to `24` / `24`; and
  - `collection.replacement.workflow.module_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1030-pattern-replacement-bytes-negative-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-pattern replacement publication file.
- Keep the scope pinned to the two direct compiled-pattern bytes negative-count rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, raw-module bytes negative-count follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1030` is the next available feature task id in the current checkout:
  - `RBR-1028` was retired from `ops/tasks/ready/` as a stale ready task in this run after its benchmark target was verified as already landed;
  - `RBR-1029` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the retired `RBR-1028` slice because the next concrete unpublished same-family owner-path gap is the adjacent direct compiled-pattern bytes negative-count correctness pair rather than raw-module bytes negative-count follow-ons, another benchmark-only slice, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe confirms `rebar.compile(b"abc").sub(b"x", b"abcabc", -1) == re.compile(b"abc").sub(b"x", b"abcabc", -1)` and `rebar.compile(b"abc").subn(b"x", b"abcabc", -1) == re.compile(b"abc").subn(b"x", b"abcabc", -1)` on the live branch;
  - `rg -n 'pattern-sub-bytes-negative-count|pattern-subn-bytes-negative-count' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently returns no matches, confirming the exact correctness publication ids are still absent from the tracked owner-path surfaces; and
  - `RBR-1028` already landed the adjacent benchmark-side `str` negative-count catch-up on the same owner route, so this follow-on can stay correctness-only instead of queuing another implementation or benchmark prerequisite first.

## Completion
- Added the two missing shared-manifest direct compiled-pattern bytes negative-count rows in `tests/conformance/fixtures/collection_replacement_workflows.py`: `pattern-sub-bytes-negative-count` immediately after `pattern-sub-bytes-single-match`, and `pattern-subn-bytes-negative-count` immediately after `pattern-subn-bytes-repeated`.
- Extended the existing shared direct `Pattern.sub()` / `Pattern.subn()` parity/publication route in `tests/python/test_fixture_backed_replacement_parity_suite.py` with the `bytes-negative-count` source-package case, the twelve published direct pattern replacement ids in the required order, and aligned helper/args/text-model publication assertions.
- Refreshed `tests/conformance/test_combined_correctness_scorecards.py` so the shared collection-replacement manifest expectation now samples both new published ids.
- Regenerated `reports/correctness/latest.py`; the tracked combined summary is now `1581` total / `1581` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `44` / `44`, `.bytes` at `15` / `15`, `.str` unchanged at `29` / `29`, `.pattern_call` at `24` / `24`, and `.module_call` unchanged at `20` / `20`.
- Verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-negative-count'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1030-pattern-replacement-bytes-negative-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
