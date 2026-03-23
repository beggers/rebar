# RBR-1042: Publish the direct `module.sub()` bytes repeated/count-one pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent raw-module `bytes` `sub()` repeated/count-bounded pair that the live source-package runtime already matches against CPython, publishing the exact module-boundary outcomes before any same-owner benchmark catch-up widens `collection_replacement_boundary.py`.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zabcabc")`
- `re.sub(b"abc", b"x", b"abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new `module_call` rows:
  - add `module-sub-bytes-repeated`; and
  - add `module-sub-bytes-count-one`.
- Keep those two rows pinned to the exact raw-module workflows above rather than widening the collection frontier:
  - `module-sub-bytes-repeated` uses `helper == "sub"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zabcabc"}]`, and categories `["workflow", "sub", "literal", "bytes", "repeated"]`;
  - `module-sub-bytes-count-one` uses `helper == "sub"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}, 1]`, and categories `["workflow", "sub", "literal", "bytes", "count-one"]`;
  - insert `module-sub-bytes-repeated` immediately after `module-sub-bytes-no-match`;
  - insert `module-sub-bytes-count-one` immediately after `module-sub-bytes-repeated`;
  - keep `module-subn-bytes-count` immediately after `module-sub-bytes-count-one`; and
  - keep the direct raw-module literal replacement block ordered as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-sub-str-negative-count`, `module-subn-str-count`, `module-subn-str-repeated`, `module-subn-str-negative-count`, `module-sub-bytes-no-match`, `module-sub-bytes-repeated`, `module-sub-bytes-count-one`, `module-subn-bytes-count`, and `module-subn-bytes-repeated`, without widening into benchmark rows, the separate `module-sub-str-count-one` singleton gap, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves the twelve rows in the exact order listed above;
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-sub-bytes-repeated == (b"abc", b"x", b"zabcabc")` and `module-sub-bytes-count-one == (b"abc", b"x", b"abcabc", 1)` on the same file;
  - keep the existing direct source-package `module.sub()` helper parity coverage on the same file and ensure the already-present `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` `bytes-repeated-match` and `bytes-count-one` cases remain selected by the shared coverage path rather than introducing another replacement-only test module; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1585` total / `1585` passed / `0` failed / `0` unimplemented across `114` manifests to `1587` / `1587` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `48` total / `48` passed to `50` / `50`;
  - `collection.replacement.workflow.bytes` moves from `17` total / `17` passed to `19` / `19`;
  - `collection.replacement.workflow.str` stays `31` total / `31` passed;
  - `collection.replacement.workflow.pattern_call` stays `28` total / `28` passed; and
  - `collection.replacement.workflow.module_call` moves from `20` total / `20` passed to `22` / `22`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-repeated-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1042-module-sub-bytes-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the two direct raw-module `bytes` `sub()` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, the separate `module-sub-str-count-one` singleton gap, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1042` is the next available feature task id in the current checkout:
  - `RBR-1041` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1040` because the next concrete unpublished same-family owner-path gap is the adjacent direct raw-module `bytes` `sub()` repeated/count-bounded correctness pair rather than a benchmark-only slice, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already contains the source-package `bytes-repeated-match` and `bytes-count-one` cases, so the runtime parity slice is already exercised on the shared owner path;
  - `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS` currently jumps from `module-sub-bytes-no-match` to `module-subn-bytes-count`, confirming the exact adjacent raw-module bytes publication gap on the shared correctness path;
  - `rg -n 'module-sub-bytes-(repeated|count-one)' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py reports/correctness/latest.py benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark publication ids are still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload ids are also still absent from `benchmarks/workloads/collection_replacement_boundary.py`, so Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
- Keep the still-unpublished `module-sub-str-count-one` row out of this task: it is a separate singleton gap on the same owner path, while this run stays on one exact two-row `bytes` pair that can be queued without widening the task shape.
