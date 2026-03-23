# RBR-1046: Publish the direct `module.sub()` str count-one singleton

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct raw-module `str` `sub()` count-bounded singleton that the live source-package runtime already matches against CPython, publishing that exact owner-path row before the matching Python-path benchmark catch-up, bytes single-match follow-ons, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", 1)`
- `rebar.sub("abc", "x", "abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `module_call` row:
  - add `module-sub-str-count-one`;
  - keep the row pinned to the exact raw-module workflow above with `helper == "sub"`, `args == ["abc", "x", "abcabc", 1]`, and categories `["workflow", "sub", "literal", "str", "count-one"]`;
  - insert `module-sub-str-count-one` immediately after `module-sub-str-repeated`;
  - keep `module-sub-str-negative-count` immediately after `module-sub-str-count-one`; and
  - do not widen into benchmark rows, bytes single-match follow-ons, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves exactly thirteen rows in this order:
    - `module-sub-str-no-match`
    - `module-sub-str-single-match`
    - `module-sub-str-repeated`
    - `module-sub-str-count-one`
    - `module-sub-str-negative-count`
    - `module-subn-str-count`
    - `module-subn-str-repeated`
    - `module-subn-str-negative-count`
    - `module-sub-bytes-no-match`
    - `module-sub-bytes-repeated`
    - `module-sub-bytes-count-one`
    - `module-subn-bytes-count`
    - `module-subn-bytes-repeated`
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-sub-str-count-one == ("abc", "x", "abcabc", 1)` on the same file;
  - keep the shared direct source-package `module.sub()` helper parity coverage on the same file and ensure the already-present `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` `str-count-one` case remains selected by the shared coverage path rather than introducing another replacement-only test module; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1587` total / `1587` passed / `0` failed / `0` unimplemented across `114` manifests to `1588` / `1588` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `50` total / `50` passed to `51` / `51`;
  - `collection.replacement.workflow.str` moves from `31` total / `31` passed to `32` / `32`;
  - `collection.replacement.workflow.bytes` stays `19` total / `19` passed;
  - `collection.replacement.workflow.module_call` moves from `22` total / `22` passed to `23` / `23`;
  - `collection.replacement.workflow.pattern_call` stays `28` total / `28` passed; and
  - the new `module-sub-str-count-one` row is visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-count-one'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1046-module-sub-str-count-one-singleton.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the one direct raw-module `str` `sub()` count-bounded row above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, bytes single-match follow-ons, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1046` is the next available feature task id in the current checkout:
  - `RBR-1045` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1044` because the newest done frontier closed the adjacent raw-module `bytes` repeated/count-bounded benchmark catch-up, and the next concrete unpublished same-family owner-path gap is the deferred `module-sub-str-count-one` correctness singleton rather than another benchmark-only slice, bytes single-match follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `DIRECT_LITERAL_MODULE_REPLACEMENT_CASES` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already contains the direct source-package `str-count-one` case, so the runtime parity slice is already exercised on the shared owner path;
  - a direct runtime probe in this run confirmed `rebar.sub("abc", "x", "abcabc", 1) == re.sub("abc", "x", "abcabc", 1)` on the live branch;
  - `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS` currently jumps from `module-sub-str-repeated` to `module-sub-str-negative-count`, confirming the exact adjacent raw-module `str` publication gap on the shared correctness path;
  - `rg -n 'module-sub-str-count-one' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` returned no matches in this run, confirming the exact correctness publication id is still absent from the tracked owner-path surfaces; and
  - the matching benchmark-side workload id `module-sub-str-count-one-purged-str` is also still absent from `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so Python-path benchmark catch-up should stay sequenced behind this correctness publication instead of replacing it.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a tracked state refresh in the same run.
