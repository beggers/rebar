# RBR-1069: Publish the direct `Pattern.subn()` str no-match

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Completion
- Added the single published `pattern-subn-str-no-match` `pattern_call` row to `tests/conformance/fixtures/collection_replacement_workflows.py` immediately after `pattern-subn-str-negative-count`, keeping `pattern-sub-bytes-no-match` immediately after it.
- Updated the shared direct-pattern literal replacement publication selector in `tests/python/test_fixture_backed_replacement_parity_suite.py` so the published owner-path order now includes `pattern-subn-str-no-match`, the direct-pattern unpublished gap set is empty, and the in-order fixture assertion now checks `("x", "zzz")` for that row.
- Regenerated `reports/correctness/latest.py`; the tracked combined summary is now `1594` total / `1594` passed / `0` failed / `0` unimplemented across `114` manifests, `collection.replacement.workflow` is `57/57`, `collection.replacement.workflow.bytes` remains `23/23`, `collection.replacement.workflow.str` is `34/34`, and `collection.replacement.workflow.pattern_call` is `32/32` with `pattern-subn-str-no-match` present in the tracked case list.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and str-no-match'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order or test_literal_replacement_publication_gaps_stay_explicit'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1069-pattern-subn-str-no-match.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct compiled-pattern `str` `subn()` no-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the matching Python-path benchmark catch-up, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.compile("abc").subn("x", "zzz")`
- `rebar.compile("abc").subn("x", "zzz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `pattern_call` row:
  - add `pattern-subn-str-no-match`;
  - keep the row pinned to the exact compiled-pattern workflow above with `pattern == "abc"`, `helper == "subn"`, `text_model == "str"`, `args == ["x", "zzz"]`, and categories `["workflow", "subn", "literal", "str", "no-match"]`;
  - insert `pattern-subn-str-no-match` immediately after `pattern-subn-str-negative-count`;
  - keep `pattern-sub-bytes-no-match` immediately after `pattern-subn-str-no-match`; and
  - do not widen into benchmark rows, direct raw-module `subn()` publication, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached compiled-pattern publication table:
  - extend `_direct_literal_replacement_publication_case_ids(surface="pattern")`, or a strictly equivalent existing owner-path selector, so the shared direct compiled-pattern literal replacement publication route now resolves exactly twenty rows in this order:
    - `pattern-sub-str-no-match`
    - `pattern-sub-str-single-match`
    - `pattern-sub-str-repeated`
    - `pattern-sub-str-count-one`
    - `pattern-sub-str-negative-count`
    - `pattern-subn-str-count`
    - `pattern-subn-str-single-match`
    - `pattern-subn-str-repeated`
    - `pattern-subn-str-negative-count`
    - `pattern-subn-str-no-match`
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
  - tighten `test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `pattern-subn-str-no-match == ("x", "zzz")` on the same file;
  - keep `test_literal_replacement_publication_gaps_stay_explicit`, or a strictly equivalent existing publication-gap assertion, green by removing `pattern-subn-str-no-match` from the remaining direct-pattern unpublished set on the shared owner path; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached compiled-pattern helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1593` total / `1593` passed / `0` failed / `0` unimplemented across `114` manifests to `1594` / `1594` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `56` total / `56` passed to `57` / `57`;
  - `collection.replacement.workflow.bytes` stays `23` total / `23` passed;
  - `collection.replacement.workflow.str` moves from `33` total / `33` passed to `34` / `34`; and
  - `collection.replacement.workflow.pattern_call` moves from `31` total / `31` passed to `32` / `32`, with the new `pattern-subn-str-no-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and str-no-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order or test_literal_replacement_publication_gaps_stay_explicit'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1069-pattern-subn-str-no-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern replacement publication file.
- Keep the scope pinned to the one compiled-pattern `str` `subn()` no-match row above. Leave the matching Python-path benchmark catch-up, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1069` is the next available feature task id in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task;
  - `RBR-1068` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - `rg -n 'RBR-1069|RBR-1070|RBR-1071' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only a historical note inside `ops/tasks/done/RBR-1068-retire-pattern-wrong-text-model-anchor-singleton.md`, not a live reservation or task file for those ids.
- Queue this directly after `RBR-1067` because once the active direct compiled-pattern `str` `Pattern.subn()` single-match benchmark catch-up drained, the next concrete missing same-family owner-path slice is the direct compiled-pattern `str` `Pattern.subn()` no-match correctness row rather than the matching benchmark catch-up, direct raw-module `subn()` follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - a direct runtime probe in this run confirmed `rebar.compile("abc").subn("x", "zzz") == re.compile("abc").subn("x", "zzz")` on the live branch;
  - `test_source_package_pattern_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the `str-no-match` direct compiled-pattern replacement parity path and asserts both `sub()` and `subn()` equality on the shared owner route;
  - `_direct_literal_replacement_publication_case_ids(surface="pattern", selection="unpublished")` currently returns only `("pattern-subn-str-no-match",)`, confirming the exact adjacent unpublished direct-pattern follow-on on the shared owner route;
  - `rg -n 'pattern-subn-str-no-match|pattern-subn-str-no-match-warm-str' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns matches only from the parity-suite unpublished-gap assertion, confirming the exact correctness row and matching benchmark workload are still absent from the tracked owner-path publication surfaces; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_pattern_literal_replacement_rows_in_order or test_source_package_pattern_literal_replacement_helpers_match_cpython'` passed in this run, confirming the bounded owner-path parity route is already stable before publication.
