# RBR-1075: Publish the direct module `subn()` bytes no-match

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the last still-unpublished direct raw-module `bytes` `subn()` no-match row that the live source-package runtime already matches against CPython, publishing that exact owner-path outcome before grouped-template rows, callable replacement rows, or another owner family reopens the queue.

## Pattern Pair
- `re.subn(b"abc", b"x", b"zzz")`
- `rebar.subn(b"abc", b"x", b"zzz")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly one new `module_call` row:
  - add `module-subn-bytes-no-match`;
  - keep the row pinned to the exact raw-module workflow above with `pattern == b"abc"`, `helper == "subn"`, `text_model == "bytes"`, `args == [b"abc", b"x", b"zzz"]`, and categories `["workflow", "subn", "literal", "bytes", "no-match"]`;
  - insert `module-subn-bytes-no-match` immediately after `module-subn-bytes-repeated`; and
  - do not widen into benchmark rows, grouped-template rows, callable replacement rows, or another correctness manifest in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module publication table:
  - extend `_direct_literal_replacement_publication_case_ids(surface="module")`, or a strictly equivalent existing owner-path selector, so the shared direct raw-module literal replacement publication route now resolves exactly eighteen rows in this order:
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
    - `module-subn-bytes-no-match`
  - tighten `test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order`, or a strictly equivalent existing owner-path assertion, so the selected published rows now check `module-subn-bytes-no-match == (b"abc", b"x", b"zzz")` on the same file;
  - keep `test_literal_replacement_publication_gaps_stay_explicit`, or a strictly equivalent existing publication-gap assertion, green by removing `module-subn-bytes-no-match` from the remaining direct-module unpublished set so the shared direct-module literal replacement route has no unpublished rows left; and
  - keep the helper/text-model/order assertions on the shared collection/replacement owner route instead of inventing a detached raw-module helper family.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1596` total / `1596` passed / `0` failed / `0` unimplemented across `114` manifests to `1597` / `1597` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `59` total / `59` passed to `60` / `60`;
  - `collection.replacement.workflow.str` stays `36` total / `36` passed;
  - `collection.replacement.workflow.bytes` moves from `23` total / `23` passed to `24` / `24`; and
  - `collection.replacement.workflow.module_call` moves from `27` total / `27` passed to `28` / `28`, with the new `module-subn-bytes-no-match` row visible in the tracked scorecard as a representative `collection-replacement-workflows` case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-no-match'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or test_literal_replacement_publication_gaps_stay_explicit'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1075-module-subn-bytes-no-match.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the one raw-module `bytes` `subn()` no-match row above. Leave grouped-template rows, callable replacement rows, benchmark catch-up, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1075` is the next available feature task id in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - the next unreserved `RBR-` id after the current done queue is `1075` in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1073` because once the direct raw-module `str` `subn()` no-match correctness publication drained, the next concrete missing same-family owner-path slice is the adjacent direct raw-module `bytes` `subn()` no-match correctness row rather than grouped-template rows, callable replacement rows, benchmark catch-up, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `_direct_literal_replacement_publication_case_ids(surface="module", selection="unpublished")` currently returns `("module-subn-bytes-no-match",)`, confirming the last adjacent unpublished direct-module slice on the shared owner route;
  - a direct runtime probe in this run confirmed `rebar.subn(b"abc", b"x", b"zzz") == re.subn(b"abc", b"x", b"zzz")` on the live branch;
  - `test_source_package_module_literal_replacement_helpers_match_cpython` in `tests/python/test_fixture_backed_replacement_parity_suite.py` already exercises the direct raw-module `bytes` no-match replacement parity path and asserts `subn()` equality on the shared owner route; and
  - `rg -n "module-subn-bytes-no-match" tests/conformance/fixtures/collection_replacement_workflows.py reports/correctness/latest.py` returned no matches in this run, confirming the exact correctness row is still absent from the tracked owner-path publication surfaces.

## Completion
- Landed the single `module-subn-bytes-no-match` `module_call` row in `tests/conformance/fixtures/collection_replacement_workflows.py` immediately after `module-subn-bytes-repeated`, kept the shared collection/replacement publication selector on the existing owner path, and removed the final direct-module unpublished literal replacement gap.
- Regenerated `reports/correctness/latest.py`; the tracked published scorecard now reads `1597` total / `1597` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow == 60/60`, `collection.replacement.workflow.bytes == 24/24`, and `collection.replacement.workflow.module_call == 28/28`, and the tracked report includes `module-subn-bytes-no-match` as a representative `collection-replacement-workflows` case.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and bytes-no-match'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_collection_replacement_manifest_publishes_direct_module_literal_replacement_rows_in_order or test_literal_replacement_publication_gaps_stay_explicit'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1075-module-subn-bytes-no-match.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
