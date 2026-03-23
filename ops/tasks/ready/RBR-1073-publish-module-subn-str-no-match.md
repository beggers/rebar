# RBR-1073: Publish the direct module `subn()` str no-match

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the still-unpublished direct raw-module `str` `subn()` no-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before the adjacent bytes no-match publication, matching Python-path benchmark catch-up, grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.subn("abc", "x", "zzz")`
- `rebar.subn("abc", "x", "zzz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `module_call` row:
  - add `module-subn-str-no-match`;
  - keep the row pinned to the exact raw-module workflow above with `pattern == "abc"`, `helper == "subn"`, `text_model == "str"`, `args == ["abc", "x", "zzz"]`, and categories `["workflow", "subn", "literal", "str", "no-match"]`;
  - insert `module-subn-str-no-match` immediately after `module-subn-str-negative-count`; and
  - do not widen into bytes no-match publication, benchmark rows, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `_direct_literal_replacement_publication_case_ids(surface="module")`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves exactly seventeen rows in this order:
    - `module-sub-str-no-match`
    - `module-sub-str-single-match`
    - `module-sub-str-repeated`
    - `module-sub-str-count-one`
    - `module-sub-str-negative-count`
    - `module-subn-str-count`
    - `module-subn-str-single-match`
    - `module-subn-str-repeated`
    - `module-subn-str-negative-count`
    - `module-subn-str-no-match`
    - `module-sub-bytes-no-match`
    - `module-sub-bytes-single-match`
    - `module-sub-bytes-repeated`
    - `module-sub-bytes-count-one`
    - `module-subn-bytes-count`
    - `module-subn-bytes-single-match`
    - `module-subn-bytes-repeated`
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-subn-str-no-match == ("abc", "x", "zzz")` on the same file;
  - keep `test_literal_replacement_publication_gaps_stay_explicit`, or a strictly equivalent existing publication-gap assertion, green by removing `module-subn-str-no-match` from the remaining direct-module unpublished set on the shared owner path so only `module-subn-bytes-no-match` remains unpublished; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1595` total / `1595` passed / `0` failed / `0` unimplemented across `114` manifests to `1596` / `1596` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `58` total / `58` passed to `59` / `59`;
  - `collection.replacement.workflow.str` moves from `35` total / `35` passed to `36` / `36`;
  - `collection.replacement.workflow.bytes` stays `23` total / `23` passed; and
  - `collection.replacement.workflow.module_call` moves from `26` total / `26` passed to `27` / `27`, with the new `module-subn-str-no-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and str-no-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or test_literal_replacement_publication_gaps_stay_explicit'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1073-module-subn-str-no-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the one raw-module `str` `subn()` no-match row above. Leave bytes no-match publication, matching Python-path benchmark catch-up, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1073` is the next available feature task id in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1073|RBR-1074|RBR-1075' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only historical notes inside done-task files, not a live reservation or task file for those ids.
- Queue this directly after `RBR-1071` because once the direct raw-module `str` `subn()` single-match correctness publication drained, the next concrete missing same-family owner-path slice is the adjacent direct raw-module `str` `subn()` no-match correctness row rather than bytes no-match publication, benchmark catch-up, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `_direct_literal_replacement_publication_case_ids(surface="module", selection="unpublished")` currently returns `("module-subn-str-no-match", "module-subn-bytes-no-match")`, confirming the adjacent same-family unpublished direct-module slice on the shared owner route;
  - a direct runtime probe in this run confirmed `rebar.subn("abc", "x", "zzz") == re.subn("abc", "x", "zzz")` on the live branch;
  - `test_source_package_module_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the direct raw-module `str` no-match replacement parity path and asserts `subn()` equality on the shared owner route; and
  - `rg -n "module-subn-str-no-match|module-subn-no-match-warm-str" tests/conformance/fixtures/collection_replacement_workflows.py benchmarks/workloads/collection_replacement_boundary.py reports/correctness/latest.py reports/benchmarks/latest.py` returned only the still-explicit unpublished reference in `tests/python/test_fixture_backed_replacement_parity_suite.py` in this run, confirming the exact correctness row and matching benchmark workload are still absent from the tracked owner-path publication surfaces.
