## RBR-0977: Publish the direct Pattern `findall()` bounded trio

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent bound `Pattern.findall()` bounded trio that the current runtime already matches in direct parity tests, publishing the exact CPython-visible bounded-success and bounded-no-match workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").findall("zabcabcz", 1, 7)`
- `re.compile("abc").findall("zabz", 1, 4)`
- `re.compile(b"abc").findall(b"zabcabcz", 1, 7)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly three new bound-pattern `pattern_call` rows:
  - add `pattern-findall-str-bounded`;
  - add `pattern-findall-str-bounded-no-match`; and
  - add `pattern-findall-bytes-bounded`.
- Keep those three rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-findall-str-bounded` uses `pattern == "abc"`, `helper == "findall"`, `args == ["zabcabcz", 1, 7]`, `text_model == "str"`, and categories `["workflow", "findall", "literal", "str", "bounded"]`;
  - `pattern-findall-str-bounded-no-match` uses `pattern == "abc"`, `helper == "findall"`, `args == ["zabz", 1, 4]`, `text_model == "str"`, and categories `["workflow", "findall", "literal", "str", "bounded", "no-match"]`;
  - `pattern-findall-bytes-bounded` uses `pattern == "abc"`, `helper == "findall"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "zabcabcz"}, 1, 7]`, `text_model == "bytes"`, and categories `["workflow", "findall", "literal", "bytes", "bounded"]`;
  - insert the new trio immediately after `pattern-findall-str-no-match` and immediately before `pattern-findall-bytes-pattern-on-str-string`, preserving the exact order listed above; and
  - do not widen into `Pattern.split()` follow-ons, `Pattern.finditer()` str follow-ons, module-level collection helpers, replacement workflows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, parity suite, or detached `findall()` selector table:
  - `_published_pattern_collection_cases_for_helper("findall")` or an equivalent existing owner-path assertion resolves, in order, to `pattern-findall-str-no-match`, `pattern-findall-str-bounded`, `pattern-findall-str-bounded-no-match`, and `pattern-findall-bytes-bounded`;
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier()` or an equivalent existing collection-frontier assertion keeps the `pattern-findall` bucket aligned to that four-row published slice on the shared owner path; and
  - keep the published collection frontier on the existing `collection-replacement-workflows` bundle rather than forking a second pattern-collection correctness file.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1556` total / `1556` passed / `0` failed / `0` unimplemented across `114` manifests to `1559` / `1559` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `19` total / `19` passed to `22` / `22`;
  - `collection.replacement.workflow.str` moves from `13` total / `13` passed to `15` / `15`;
  - `collection.replacement.workflow.bytes` moves from `6` total / `6` passed to `7` / `7`;
  - `collection.replacement.workflow.pattern_call` moves from `7` total / `7` passed to `10` / `10`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0977-pattern-findall-bounded-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached pattern-collection publication file.
- Keep the scope pinned to the three bound `Pattern.findall()` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0977` is the next available feature task id in the current checkout:
  - `RBR-0975` is the latest done feature task on the drained direct-`Pattern` benchmark frontier;
  - `RBR-0976` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after the drained direct-`Pattern` benchmark catch-up because the current bounded Python-path benchmark debt is now closed, while the next concrete unpublished owner-path gap sits on the adjacent `Pattern.findall()` collection surface rather than another benchmark-only sibling or a new harness lane.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`9 passed`), so the exact bounded direct parity slice is already green in this checkout;
  - `rg -n 'pattern-findall-str-bounded|pattern-findall-str-bounded-no-match|pattern-findall-bytes-bounded|workflow-pattern-findall-str-bounded|workflow-pattern-findall-bytes-bounded' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently returns no matches, so the exact trio is still absent from the published correctness surface; and
  - `rg -n 'pattern-findall' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently shows only the existing bounded-wildcard and keyword-window `Pattern.findall()` benchmark anchors, confirming a later catch-up remains concrete on the existing `collection_replacement_boundary.py` path instead of requiring a new benchmark family.

## Completion
- Added the three bounded `Pattern.findall()` publication rows to `tests/conformance/fixtures/collection_replacement_workflows.py` in the required slot, added an explicit ordered `findall` frontier assertion to `tests/python/test_module_workflow_parity_suite.py`, and extended the combined scorecard manifest sample in `tests/conformance/test_combined_correctness_scorecards.py`.
- Republished `reports/correctness/latest.py`; the tracked report now shows `1559` total / `1559` passed / `0` failed / `0` unimplemented across `114` manifests, with `collection.replacement.workflow` at `22/22`, `.str` at `15/15`, `.bytes` at `7/7`, `.pattern_call` at `10/10`, and `.module_call` unchanged at `12/12`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0977-pattern-findall-bounded-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
