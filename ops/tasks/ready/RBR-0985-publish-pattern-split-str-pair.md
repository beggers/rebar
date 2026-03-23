## RBR-0985: Publish the direct Pattern `split()` str pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent direct `Pattern.split()` str pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible no-match and repeated-match workflows before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Pair
- `re.compile("abc").split("zzz")`
- `re.compile("abc").split("abcabc")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new direct-`Pattern` `pattern_call` rows:
  - add `pattern-split-str-no-match`; and
  - add `pattern-split-str-repeated`.
- Keep those two rows pinned to the exact direct helper workflows above rather than widening the collection frontier:
  - `pattern-split-str-no-match` uses `pattern == "abc"`, `helper == "split"`, `args == ["zzz"]`, `text_model == "str"`, and categories `["workflow", "split", "literal", "str", "no-match"]`;
  - `pattern-split-str-repeated` uses `pattern == "abc"`, `helper == "split"`, `args == ["abcabc"]`, `text_model == "str"`, and categories `["workflow", "split", "literal", "str", "repeated"]`;
  - insert the new pair immediately before `pattern-split-bytes-maxsplit`, preserving the exact order `pattern-split-str-no-match`, `pattern-split-str-repeated`, then `pattern-split-bytes-maxsplit`; and
  - do not widen into `Pattern.split()` maxsplit follow-ons, `Pattern.findall()` or `Pattern.finditer()` siblings, module-level collection helpers, replacement workflows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, parity suite, or detached `split()` selector table:
  - `_published_pattern_collection_cases_for_helper("split")` or an equivalent existing owner-path assertion resolves, in order, to `pattern-split-str-no-match`, `pattern-split-str-repeated`, and `pattern-split-bytes-maxsplit`;
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier()` or an equivalent existing collection-frontier assertion keeps the `pattern-split` bucket aligned to that three-row published slice on the shared owner path; and
  - keep the published collection frontier on the existing `collection-replacement-workflows` bundle rather than forking a second pattern-collection correctness file.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1561` total / `1561` passed / `0` failed / `0` unimplemented across `114` manifests to `1563` / `1563` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `24` total / `24` passed to `26` / `26`;
  - `collection.replacement.workflow.str` moves from `17` total / `17` passed to `19` / `19`;
  - `collection.replacement.workflow.bytes` stays `7` total / `7` passed;
  - `collection.replacement.workflow.pattern_call` moves from `12` total / `12` passed to `14` / `14`; and
  - `collection.replacement.workflow.module_call` stays `12` total / `12` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-no-match or pattern-split-str-repeated or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0985-pattern-split-str-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached `Pattern.split()` publication file.
- Keep the scope pinned to the two direct `Pattern.split()` str rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0985` is the next available feature task id in the current checkout:
  - `RBR-0983` is the latest done feature task on the drained direct-`Pattern` collection/replacement benchmark frontier;
  - `RBR-0984` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained bounded direct `Pattern.finditer()` benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane sits on the adjacent direct `Pattern.split()` str surface rather than another benchmark-only sibling or a new harness lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-no-match or pattern-split-str-repeated or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`5 passed`), so the exact direct parity slice is already green in this checkout;
  - `rg -n 'pattern-split-str-no-match|pattern-split-str-repeated|workflow-pattern-split-str-no-match|workflow-pattern-split-str-repeated' tests/conformance/fixtures/collection_replacement_workflows.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently returns no matches, so the exact pair is still absent from the published correctness surface; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... synthetic Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) for pattern-split-no-match-warm-str and pattern-split-repeated-warm-str ... PY` returns `status == "measured"` for both adapters on both synthetic workloads through the current benchmark harness, confirming a later Python-path benchmark catch-up remains concrete on the existing `collection_replacement_boundary.py` owner route.
