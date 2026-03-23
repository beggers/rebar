# RBR-0992: Publish the direct `Pattern.sub()` / `Pattern.subn()` single-match/repeated pair

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct `Pattern.sub()` / `Pattern.subn()` literal-success pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible single-match and repeated-match workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc").sub("x", "zabczz")`
- `re.compile("abc").subn("x", "abcabc")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new direct-`Pattern` `pattern_call` rows:
  - add `pattern-sub-str-single-match`; and
  - add `pattern-subn-str-repeated`.
- Keep those two rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-sub-str-single-match` uses `pattern == "abc"`, `helper == "sub"`, `args == ["x", "zabczz"]`, `text_model == "str"`, and categories `["workflow", "sub", "literal", "str", "single-match"]`;
  - `pattern-subn-str-repeated` uses `pattern == "abc"`, `helper == "subn"`, `args == ["x", "abcabc"]`, `text_model == "str"`, and categories `["workflow", "subn", "literal", "str", "repeated"]`;
  - insert `pattern-sub-str-single-match` immediately after `pattern-sub-str-no-match`;
  - insert `pattern-subn-str-repeated` immediately after `pattern-subn-str-count`; and
  - keep the direct compiled-pattern literal replacement block ordered as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, `pattern-subn-str-repeated` immediately before `module-sub-template-str`, without widening into bytes follow-ons, grouped-template rows, callable replacement rows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached literal-replacement publication table:
  - add a focused published direct-`Pattern` literal-replacement assertion path, or tighten an equivalent existing owner-path assertion, so the shared `collection-replacement-workflows` route now resolves the published direct literal pattern replacement rows in order as `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, and `pattern-subn-str-repeated`;
  - keep the direct source-package literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep grouped-template, callable, and mixed-text-model replacement ownership checks honest while widening only this direct literal `Pattern` pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1563` total / `1563` passed / `0` failed / `0` unimplemented across `114` manifests to `1565` / `1565` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `26` total / `26` passed to `28` / `28`;
  - `collection.replacement.workflow.str` moves from `19` total / `19` passed to `21` / `21`;
  - `collection.replacement.workflow.bytes` stays `7` total / `7` passed;
  - `collection.replacement.workflow.pattern_call` moves from `14` total / `14` passed to `16` / `16`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0992-pattern-replacement-single-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached direct-`Pattern` replacement publication file.
- Keep the scope pinned to the two direct replacement rows above. Leave bytes follow-ons, grouped-template/callable replacement publication, and the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for later tasks.

## Notes
- `RBR-0992` is the next available feature task id in the current checkout:
  - `RBR-0989` is the latest done feature task on the drained direct-`Pattern` collection/replacement frontier;
  - `RBR-0990` and `RBR-0991` are already occupied by architecture cleanup tasks in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct `Pattern.sub()` / `Pattern.subn()` benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent direct single-match/repeated correctness pair rather than bytes follow-ons, grouped-template/callable slices, or another benchmark-only expansion.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'` currently passes (`2 passed`), so the exact direct parity slice is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile("abc").sub("x", "zabczz") ... rebar.compile("abc").subn("x", "abcabc") ... PY` currently matches CPython for the exact published outputs `zxzz` and `('xx', 2)` on the direct compiled-pattern path;
  - `rg -n 'pattern-sub-str-single-match|pattern-subn-str-repeated|workflow-pattern-sub-str-single-match|workflow-pattern-subn-str-repeated' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently returns no matches, confirming the exact publication rows are still absent from the tracked correctness surface; and
  - `reports/correctness/latest.py` currently reports `1563` total / `1563` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `26` / `26`, `.str` at `19` / `19`, `.bytes` at `7` / `7`, `.pattern_call` at `14` / `14`, and `.module_call` at `12` / `12`.

## Completion
- 2026-03-23: Added the two published direct `Pattern.sub()` / `Pattern.subn()` rows to `tests/conformance/fixtures/collection_replacement_workflows.py` in the required order, and kept the shared owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py` by adding a focused manifest-order assertion for `pattern-sub-str-no-match`, `pattern-sub-str-single-match`, `pattern-subn-str-count`, and `pattern-subn-str-repeated`.
- Regenerated `reports/correctness/latest.py`; the tracked published scorecard now reports `1565` total / `1565` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `28` / `28`, `.str` at `21` / `21`, `.bytes` still `7` / `7`, `.pattern_call` at `16` / `16`, and `.module_call` still `12` / `12`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and (str-single-match or str-repeated-match)'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0992-pattern-replacement-single-match-repeated-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
