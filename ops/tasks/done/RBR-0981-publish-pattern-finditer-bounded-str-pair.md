## RBR-0981: Publish the direct Pattern `finditer()` bounded str pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent bounded direct `Pattern.finditer()` str pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible bounded-success and bounded-no-match workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Pair
- `re.compile("abc").finditer("zabcabcx", 1, 7)`
- `re.compile("abc").finditer("zabz", 1, 4)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new bounded direct-`Pattern` `finditer()` `pattern_call` rows:
  - add `pattern-finditer-str-bounded`; and
  - add `pattern-finditer-str-bounded-no-match`.
- Keep those two rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-finditer-str-bounded` uses `pattern == "abc"`, `helper == "finditer"`, `args == ["zabcabcx", 1, 7]`, `text_model == "str"`, and categories `["workflow", "finditer", "literal", "str", "bounded", "iterator-exhaustion"]`;
  - `pattern-finditer-str-bounded-no-match` uses `pattern == "abc"`, `helper == "finditer"`, `args == ["zabz", 1, 4]`, `text_model == "str"`, and categories `["workflow", "finditer", "literal", "str", "bounded", "no-match", "iterator-exhaustion"]`;
  - insert the new pair immediately after `module-finditer-str-repeated` and immediately before `pattern-finditer-bytes-bounded`, preserving the exact order listed above so the published `Pattern.finditer()` slice reads str-bounded, str-bounded-no-match, then the existing bytes-bounded row; and
  - do not widen into raw-module `finditer()` follow-ons, direct-`Pattern` `findall()` or replacement siblings, wrong-text-model publication, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, parity suite, or detached `finditer()` selector table:
  - `_published_pattern_collection_cases_for_helper("finditer")` or an equivalent existing owner-path assertion resolves, in order, to `pattern-finditer-str-bounded`, `pattern-finditer-str-bounded-no-match`, and `pattern-finditer-bytes-bounded`;
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier()` or an equivalent existing collection-frontier assertion keeps the `pattern-finditer` bucket aligned to that three-row published slice on the shared owner path; and
  - keep the published collection frontier on the existing `collection-replacement-workflows` bundle rather than forking a second pattern-collection correctness file.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1559` total / `1559` passed / `0` failed / `0` unimplemented across `114` manifests to `1561` / `1561` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `22` total / `22` passed to `24` / `24`;
  - `collection.replacement.workflow.str` moves from `15` total / `15` passed to `17` / `17`;
  - `collection.replacement.workflow.bytes` stays `7` total / `7` passed;
  - `collection.replacement.workflow.pattern_call` moves from `10` total / `10` passed to `12` / `12`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0981-pattern-finditer-bounded-str-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached `Pattern.finditer()` publication file.
- Keep the scope pinned to the two bounded direct `Pattern.finditer()` str rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0981` is the next available feature task id in the current checkout:
  - `RBR-0979` is the latest done feature task on the drained direct-`Pattern` collection/replacement benchmark frontier;
  - `RBR-0980` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after the drained bounded direct `Pattern.findall()` benchmark catch-up because the current bounded Python-path benchmark debt is now closed, while the next concrete unpublished owner-path gap sits on the adjacent direct `Pattern.finditer()` collection surface rather than another benchmark-only sibling or a new harness lane.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`11 passed`), so the exact bounded direct parity slice is already green in this checkout;
  - `rg -n 'pattern-finditer-str-bounded|pattern-finditer-str-bounded-no-match|workflow-pattern-finditer-str-bounded|workflow-pattern-finditer-str-bounded-no-match' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently returns only the neighboring bounded-wildcard owner-path publication on `module-workflow-surface`, confirming the exact bounded collection-pair ids are still absent from the published collection/replacement correctness surface; and
  - `rg -n 'pattern-finditer-bounded-warm-str|pattern-finditer-bounded-no-match-warm-str|pattern-finditer-bounded-purged-bytes|workflow-pattern-finditer-str-bounded|workflow-pattern-finditer-str-bounded-no-match|workflow-pattern-finditer-bytes-bounded' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns only the neighboring bounded-wildcard benchmark anchors on another owner path, while `benchmarks/workloads/collection_replacement_boundary.py` still carries only the existing `pattern-finditer-literal-warm-str` and `pattern-finditer-literal-purged-bytes` rows for direct `Pattern.finditer()`, confirming a later catch-up remains concrete on the existing `collection_replacement_boundary.py` path instead of requiring a new benchmark family.

## Completion Notes
- 2026-03-22: Published `pattern-finditer-str-bounded` and `pattern-finditer-str-bounded-no-match` on the existing `collection-replacement-workflows` manifest immediately before `pattern-finditer-bytes-bounded`, added an explicit owner-path ordering assertion for the shared `pattern-finditer` frontier, refreshed the combined scorecard expectation sample for this manifest, and republished `reports/correctness/latest.py`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or literal_collection_direct_test_buckets_cover_selected_frontier'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0981-pattern-finditer-bounded-str-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Published tracked totals in `reports/correctness/latest.py`: overall `1561` total / `1561` passed / `0` failed / `0` unimplemented across `114` manifests; `collection.replacement.workflow` `24`/`24`; `collection.replacement.workflow.str` `17`/`17`; `collection.replacement.workflow.bytes` stayed `7`/`7`; `collection.replacement.workflow.pattern_call` `12`/`12`; `collection.replacement.workflow.module_call` stayed `12`/`12`.
