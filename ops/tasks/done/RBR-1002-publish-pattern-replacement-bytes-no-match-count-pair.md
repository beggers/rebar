# RBR-1002: Publish the direct `Pattern.sub()` / `Pattern.subn()` bytes no-match/count pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct bytes `Pattern.sub()` / `Pattern.subn()` literal no-match/count pair that the current runtime already matches in direct probes, publishing the exact CPython-visible compiled-bytes unchanged-string and bounded single-replacement workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"zzz")`
- `re.compile(b"abc").subn(b"x", b"abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new direct-`Pattern` `pattern_call` rows:
  - add `pattern-sub-bytes-no-match`; and
  - add `pattern-subn-bytes-count`.
- Keep those two rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-sub-bytes-no-match` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "sub"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zzz"}]`, and categories `["workflow", "sub", "literal", "bytes", "no-match"]`;
  - `pattern-subn-bytes-count` uses `pattern == "abc"`, `text_model == "bytes"`, `helper == "subn"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}, 1]`, and categories `["workflow", "subn", "literal", "bytes", "count"]`;
  - insert `pattern-sub-bytes-no-match` immediately before `pattern-sub-bytes-single-match`;
  - insert `pattern-subn-bytes-count` immediately before `pattern-subn-bytes-repeated`; and
  - preserve the exact direct compiled-pattern literal replacement order as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-subn-bytes-count`, `pattern-subn-bytes-repeated`, then `module-sub-template-str`, without widening into module-helper follow-ons, grouped-template rows, callable replacement rows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached bytes-only publication table:
  - extend `DIRECT_LITERAL_PATTERN_REPLACEMENT_CASES` so the existing direct compiled-pattern literal replacement parity parametrization now includes the exact bytes cases `bytes-no-match` and `bytes-count-one` on the same owner route;
  - extend `PUBLISHED_DIRECT_LITERAL_PATTERN_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published direct literal pattern replacement rows in order as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated`, `pattern-sub-bytes-no-match`, `pattern-sub-bytes-single-match`, `pattern-subn-bytes-count`, and `pattern-subn-bytes-repeated`;
  - keep the focused published direct-`Pattern` literal-replacement assertion path on the same file, tightening its order/arg/helper/text-model checks to cover the new bytes no-match/count rows without forking a second replacement publication test module; and
  - keep the direct source-package bytes literal replacement parity coverage on the same file rather than introducing another bytes-only parity suite.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1567` total / `1567` passed / `0` failed / `0` unimplemented across `114` manifests to `1569` / `1569` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `30` total / `30` passed to `32` / `32`;
  - `collection.replacement.workflow.bytes` moves from `9` total / `9` passed to `11` / `11`;
  - `collection.replacement.workflow.str` stays `21` total / `21` passed;
  - `collection.replacement.workflow.pattern_call` moves from `18` total / `18` passed to `20` / `20`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-count-one)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1002-pattern-replacement-bytes-no-match-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-`Pattern` replacement publication file.
- Keep the scope pinned to the two direct bytes replacement rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, module-helper follow-ons, grouped-template rows, and callable replacement rows for later tasks.

## Notes
- `RBR-1002` is the next available feature task id in the current checkout:
  - `RBR-1000` is the latest done feature task on the drained direct-`Pattern` replacement benchmark frontier;
  - `RBR-1001` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct bytes `Pattern.sub()` / `Pattern.subn()` benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent bytes no-match/count correctness pair rather than module-helper follow-ons, grouped-template rows, callable replacement rows, or another benchmark-only expansion.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(b"abc").sub(b"x", b"zzz") ... rebar.compile(b"abc").subn(b"x", b"abcabc", 1) ... PY` currently matches CPython for the exact direct compiled-bytes outputs `b"zzz"` / `(b"zzz", 0)` and `b"xabc"` / `(b"xabc", 1)`;
  - `rg -n 'pattern-sub-bytes-no-match|pattern-subn-bytes-count|pattern-sub-bytes-no-match-purged-bytes|pattern-subn-bytes-count-purged-bytes' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark ids are still absent from the tracked owner-path surfaces; and
  - the existing shared direct parity route already covers the surrounding bytes literal replacement family on `tests/python/test_fixture_backed_replacement_parity_suite.py`, so this run can stay publication-only instead of queuing another implementation prerequisite first.

## Completion
- Added `pattern-sub-bytes-no-match` and `pattern-subn-bytes-count` to `tests/conformance/fixtures/collection_replacement_workflows.py` in the required published direct-`Pattern` replacement order, and extended the shared owner-route assertions in `tests/python/test_fixture_backed_replacement_parity_suite.py` plus the collection manifest representative ids in `tests/conformance/test_combined_correctness_scorecards.py`.
- Verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-count-one)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1002-pattern-replacement-bytes-no-match-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Published tracked correctness report now reads `1569` total / `1569` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `32` / `32`, `collection.replacement.workflow.bytes` at `11` / `11`, `collection.replacement.workflow.str` unchanged at `21` / `21`, `collection.replacement.workflow.pattern_call` at `20` / `20`, and `collection.replacement.workflow.module_call` unchanged at `12` / `12`.
