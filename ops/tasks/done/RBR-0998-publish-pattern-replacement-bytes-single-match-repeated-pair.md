# RBR-0998: Publish the direct `Pattern.sub()` / `Pattern.subn()` bytes single-match/repeated pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct bytes `Pattern.sub()` / `Pattern.subn()` literal-success pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible compiled-bytes single-match and repeated-match workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"zabczz")`
- `re.compile(b"abc").subn(b"x", b"abcabc")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new direct-`Pattern` `pattern_call` rows:
  - add `pattern-sub-bytes-single-match`; and
  - add `pattern-subn-bytes-repeated`.
- Keep those two rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-sub-bytes-single-match` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "sub"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zabczz"}]`, and categories `["workflow", "sub", "literal", "bytes", "single-match"]`;
  - `pattern-subn-bytes-repeated` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "subn"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}]`, and categories `["workflow", "subn", "literal", "bytes", "repeated"]`;
  - insert the new pair immediately after `pattern-subn-str-repeated`, preserving the exact direct compiled-pattern literal replacement order `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-sub-bytes-single-match`, `pattern-subn-bytes-repeated`, then `module-sub-template-str`; and
  - do not widen into bytes module-helper follow-ons, grouped-template rows, callable replacement rows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached bytes-only publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published direct literal pattern replacement rows in order as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-sub-bytes-single-match`, and `pattern-subn-bytes-repeated`;
  - keep the focused published direct-`Pattern` literal-replacement assertion path on the same file, tightening its order/arg/helper/text-model checks to cover the two bytes rows without forking a second replacement publication test module; and
  - keep the direct source-package bytes literal replacement parity coverage on the same file rather than introducing another bytes-only parity suite.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1565` total / `1565` passed / `0` failed / `0` unimplemented across `114` manifests to `1567` / `1567` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `28` total / `28` passed to `30` / `30`;
  - `collection.replacement.workflow.bytes` moves from `7` total / `7` passed to `9` / `9`;
  - `collection.replacement.workflow.str` stays `21` total / `21` passed;
  - `collection.replacement.workflow.pattern_call` moves from `16` total / `16` passed to `18` / `18`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-single-match or bytes-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0998-pattern-replacement-bytes-single-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-`Pattern` replacement publication file.
- Keep the scope pinned to the two direct bytes replacement rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, bytes module-helper follow-ons, grouped-template rows, and callable replacement rows for later tasks.

## Notes
- `RBR-0998` is the next available feature task id in the current checkout:
  - `RBR-0995` is the latest done feature task on the drained direct-`Pattern` collection/replacement frontier;
  - `RBR-0996` and `RBR-0997` are already occupied by architecture cleanup tasks in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct `Pattern.sub()` / `Pattern.subn()` str benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent bytes single-match/repeated correctness pair rather than grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-single-match or bytes-repeated-match)'` currently passes (`2 passed`), so the exact direct bytes parity slice is already green in this checkout;
  - `rg -n 'pattern-sub-bytes-single-match|pattern-subn-bytes-repeated|workflow-pattern-sub-bytes-single-match|workflow-pattern-subn-bytes-repeated' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py tests/python/test_fixture_backed_replacement_parity_suite.py` currently returns no matches, confirming the exact bytes publication rows are still absent from the tracked correctness surface; and
  - the shared direct parity coverage already carries the bounded bytes single-match and repeated-match inputs on the existing owner route, so this run can stay publication-only instead of queuing another implementation prerequisite first.

## Completion
- 2026-03-23: Added `pattern-sub-bytes-single-match` and `pattern-subn-bytes-repeated` to `tests/conformance/fixtures/collection_replacement_workflows.py` immediately after `pattern-subn-str-repeated`, preserving the required direct compiled-pattern literal replacement order ahead of `module-sub-template-str`.
- Extended `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS` and the shared publication-order assertions in `tests/python/test_fixture_backed_replacement_parity_suite.py` so the owner-path selector now publishes the ordered direct literal `Pattern.sub()` / `Pattern.subn()` rows `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-sub-bytes-single-match`, and `pattern-subn-bytes-repeated`, with explicit bytes args/helper/text-model checks for the new pair.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` so the combined scorecard manifest expectation for `collection-replacement-workflows` includes the new bytes representative rows and keeps the mixed-text publication sample honest.
- Regenerated the tracked `reports/correctness/latest.py` publication. The tracked artifact now reports `1567` total / `1567` passed / `0` failed / `0` unimplemented cases overall, and `collection-replacement-workflows` now publishes `30` cases including both `pattern-sub-bytes-single-match` and `pattern-subn-bytes-repeated`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-single-match or bytes-repeated-match)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'tracked_report_keeps_sample_manifests_fresh or suite_registry_manifest_expectations_keep_nonempty_unique_representative_case_ids or tracked_report_freshness_helpers_follow_registry_and_fixture_order'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'runner_regenerates_correctness_scorecards or mixed_text'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0998-pattern-replacement-bytes-single-match-repeated-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
