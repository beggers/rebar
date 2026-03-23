# RBR-1038: Publish the direct `Pattern.sub()` bytes repeated/count-one pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct compiled-pattern `bytes` `Pattern.sub()` repeated/count-bounded pair that the live runtime already matches against CPython, publishing the exact module-boundary outcomes before any same-owner benchmark catch-up widens `collection_replacement_boundary.py`.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc")`
- `re.compile(b"abc").sub(b"x", b"abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `pattern-sub-bytes-repeated`; and
  - add `pattern-sub-bytes-count-one`.
- Keep those two rows pinned to the exact compiled-pattern workflows above rather than widening the collection frontier:
  - `pattern-sub-bytes-repeated` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "sub"`, `args == [b"x", b"abcabc"]`, and categories `["workflow", "sub", "literal", "bytes", "repeated"]`;
  - `pattern-sub-bytes-count-one` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "sub"`, `args == [b"x", b"abcabc", 1]`, and categories `["workflow", "sub", "literal", "bytes", "count-one"]`;
  - insert `pattern-sub-bytes-repeated` immediately after `pattern-sub-bytes-single-match`;
  - insert `pattern-sub-bytes-count-one` immediately after `pattern-sub-bytes-repeated`;
  - keep `pattern-sub-bytes-negative-count` immediately after `pattern-sub-bytes-count-one`; and
  - keep the direct compiled-pattern literal replacement block ordered as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-sub-str-repeated`, `pattern-sub-str-count-one`, `pattern-sub-str-negative-count`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-subn-str-negative-count`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-sub-bytes-repeated`, `pattern-sub-bytes-count-one`, `pattern-sub-bytes-negative-count`, `pattern-subn-bytes-count`, `pattern-subn-bytes-repeated`, and `pattern-subn-bytes-negative-count`, without widening into module rows, benchmark rows, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached `Pattern.sub()` publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves the sixteen rows in the exact order listed above;
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-sub-bytes-repeated == (b"x", b"abcabc")` and `pattern-sub-bytes-count-one == (b"x", b"abcabc", 1)` on the same file;
  - keep the existing direct source-package `Pattern.sub()` helper parity coverage on the same file and ensure the already-present `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` `bytes-repeated-match` and `bytes-count-one` cases remain selected by the shared coverage path rather than introducing another replacement-only test module; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached direct-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1583` total / `1583` passed / `0` failed / `0` unimplemented across `114` manifests to `1585` / `1585` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `46` total / `46` passed to `48` / `48`;
  - `collection.replacement.workflow.bytes` moves from `15` total / `15` passed to `17` / `17`;
  - `collection.replacement.workflow.pattern_call` moves from `26` total / `26` passed to `28` / `28`;
  - `collection.replacement.workflow.str` stays `31` total / `31` passed; and
  - `collection.replacement.workflow.module_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-repeated-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1038-pattern-sub-bytes-repeated-count-one-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-pattern replacement publication file.
- Keep the scope pinned to the two direct compiled-pattern `bytes` `Pattern.sub()` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, module follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1038` is the next available feature task id in the current checkout:
  - `RBR-1037` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1036` because the next concrete unpublished same-family owner-path gap is the adjacent direct compiled-pattern `Pattern.sub()` `bytes` repeated/count-bounded correctness pair rather than another benchmark-only slice, module follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already contains the source-package `bytes-repeated-match` and `bytes-count-one` cases, so the runtime parity slice is already exercised on the shared owner path;
  - `tests/conformance/fixtures/collection_replacement_workflows.py` currently jumps from `pattern-sub-bytes-single-match` directly to `pattern-sub-bytes-negative-count`, confirming the exact adjacent publication gap on the shared correctness path;
  - `rg -n 'pattern-sub-bytes-(repeated|count-one)' tests/conformance/fixtures/collection_replacement_workflows.py reports/correctness/latest.py` currently returns no matches, confirming the exact correctness publication ids are still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload ids are also still absent from `benchmarks/workloads/collection_replacement_boundary.py`, so Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.

## Completion Note
- 2026-03-23: Added `pattern-sub-bytes-repeated` and `pattern-sub-bytes-count-one` to the shared `collection-replacement-workflows` manifest, extended the existing direct-pattern literal replacement publication selector/assertions on the shared parity suite, refreshed the combined correctness representative ids, and republished `reports/correctness/latest.py`. Verified with the task's narrow parity/publication pytest commands, the full `tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` gate, a narrow fixture-only correctness refresh to `.rebar/tmp/rbr-1038-pattern-sub-bytes-repeated-count-one-pair.py` (`48` total / `48` passed), and the tracked combined refresh at `reports/correctness/latest.py` (`1585` total / `1585` passed / `0` failed / `0` unimplemented across `114` manifests; `collection.replacement.workflow` `48/48`, `.bytes` `17/17`, `.str` `31/31`, `.module_call` `20/20`, `.pattern_call` `28/28`).
