# RBR-1010: Publish the raw `re.sub()` str no-match/single-match pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent raw-module `str` literal `re.sub()` no-match/single-match pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible module-helper outcomes before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.sub("abc", "x", "zzz")`
- `re.sub("abc", "x", "zabczz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new raw-module `module_call` rows:
  - add `module-sub-str-no-match`; and
  - add `module-sub-str-single-match`.
- Keep those two rows pinned to the exact module-helper workflows above rather than widening the collection frontier:
  - `module-sub-str-no-match` uses `helper == "sub"`, `text_model == "str"`, `args == ["abc", "x", "zzz"]`, and categories `["workflow", "sub", "literal", "str", "no-match"]`;
  - `module-sub-str-single-match` uses `helper == "sub"`, `text_model == "str"`, `args == ["abc", "x", "zabczz"]`, and categories `["workflow", "sub", "literal", "str", "single-match"]`;
  - insert `module-sub-str-no-match` immediately before `module-sub-str-single-match`;
  - insert `module-sub-str-single-match` immediately before `module-sub-str-repeated`; and
  - keep the raw-module literal replacement block ordered as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated` immediately before the direct compiled-pattern replacement block, without widening into `subn()` str follow-ons, bytes follow-ons, grouped-template rows, callable replacement rows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module replacement publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published raw-module literal replacement rows in order as `module-sub-str-no-match`, `module-sub-str-single-match`, `module-sub-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated`;
  - tighten the existing published raw-module literal-replacement assertion path so the selected rows above are checked for order, helper, args, and text-model alignment on the same file;
  - keep the direct source-package module literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep the direct compiled-pattern replacement publication path, grouped-template rows, callable rows, and mixed-text-model replacement ownership checks honest while widening only this raw-module `str` pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1571` total / `1571` passed / `0` failed / `0` unimplemented across `114` manifests to `1573` / `1573` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `34` total / `34` passed to `36` / `36`;
  - `collection.replacement.workflow.str` moves from `21` total / `21` passed to `23` / `23`;
  - `collection.replacement.workflow.bytes` stays `13` total / `13` passed;
  - `collection.replacement.workflow.module_call` moves from `14` total / `14` passed to `16` / `16`; and
  - `collection.replacement.workflow.pattern_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-no-match or str-single-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1010-module-replacement-str-no-match-single-match-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the two raw-module `str` replacement rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, `subn()` str follow-ons, bytes follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1010` is the next available feature task id in the current checkout:
  - `RBR-1008` is the latest done feature task on the drained raw-module bytes replacement benchmark frontier;
  - `RBR-1009` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained raw-module bytes replacement benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent raw-module `str` no-match/single-match pair rather than `subn()` str follow-ons, bytes follow-ons, grouped-template rows, callable replacement rows, or another benchmark-only expansion.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-no-match or str-single-match)'` currently passes (`2 passed`), so the exact raw-module `str` parity slice is already green in this checkout; and
  - `rg -n 'module-sub-str-no-match|module-sub-str-single-match|module-sub-str-no-match-warm-str|module-sub-str-single-match-warm-str' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark ids are still absent from the tracked owner-path surfaces.

## Completion Note
- Added `module-sub-str-no-match` and `module-sub-str-single-match` to `tests/conformance/fixtures/collection_replacement_workflows.py` in the required raw-module order and kept the slice on the existing `collection-replacement-workflows` owner path.
- Extended the shared published raw-module selector/assertion coverage in `tests/python/test_fixture_backed_replacement_parity_suite.py` and refreshed the collection replacement representative-case coverage in `tests/conformance/test_combined_correctness_scorecards.py`.
- Regenerated `reports/correctness/latest.py`; the tracked published summary is now `1573` total / `1573` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `36/36`, `.str` at `23/23`, `.bytes` unchanged at `13/13`, `.module_call` at `16/16`, and `.pattern_call` unchanged at `20/20`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (str-no-match or str-single-match)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1010-module-replacement-str-no-match-single-match-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
