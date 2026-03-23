# RBR-1086: Publish grouped callable replacement workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the collection/replacement owner path with the first deferred publication follow-on from `RBR-1084`, adding the exact bounded str grouped callable replacement workflows to the published correctness surface before simple grouped callable benchmark catch-up, bytes publication, or broader grouped replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")`
- `rebar.compile("(?P<word>abc)").subn(lambda m: f"<{m.group('word')}>", "abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/conformance/fixtures/named_group_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Publish the exact bounded str grouped callable replacement slice on the existing collection/replacement correctness owner path without widening into bytes publication or benchmarks:
  - `collection-replacement-workflows` gains the numbered module grouped callable rows for `"(abc)"` through `sub()` and `subn(count=1)`;
  - `named-group-replacement-workflows` gains the named compiled-pattern grouped callable rows for `(?P<word>abc)` through `sub()` and `subn(count=1)`; and
  - the new published representative case ids are explicit in the tracked correctness surface:
    - `module-sub-callable-grouped-str`
    - `module-subn-callable-grouped-str`
    - `pattern-sub-callable-named-grouped-str`
    - `pattern-subn-callable-named-grouped-str`
- Keep the work on the existing fixture-backed correctness owner path rather than creating a new manifest family, detached direct-test file, or benchmark workload:
  - `tests/conformance/test_combined_correctness_scorecards.py` recognizes the new grouped callable rows under the existing `collection-replacement-workflows` and `named-group-replacement-workflows` expectations; and
  - `reports/correctness/latest.py` is regenerated so the published case list and manifest summary include the new grouped callable rows.
- Preserve the already-landed runtime and nearby publication surfaces while staying bounded:
  - `tests/python/test_callable_replacement_parity_suite.py` still passes for `test_grouped_callable_replacement_module_matches_cpython` and `test_grouped_callable_replacement_pattern_matches_cpython`;
  - the existing literal callable and grouped template publication rows stay green on the same owner path; and
  - do not widen this task into bytes callable correctness publication, benchmark manifests, benchmark scorecards, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'collection-replacement-workflows or named-group-replacement-workflows'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the publication bounded to the exact str grouped callable slice already proven by direct parity coverage. Leave bytes publication, simple grouped callable benchmark rows, and broader grouped callable replacement families for later tasks.
- Reuse the existing `collection-replacement-workflows` and `named-group-replacement-workflows` manifests instead of inventing a new grouped-callable manifest for this tiny adjacent slice.
- Do not treat benchmark catch-up as part of this run; the paired benchmark owner path still lacks the exact simple grouped callable workload rows, so correctness publication should land first.

## Notes
- `RBR-1086` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1086|RBR-1087|RBR-1088' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1084` explicitly left grouped callable publication ahead of simple grouped callable benchmarks, bytes publication, and broader grouped replacement expansion on this same owner family.
- Narrow owner-path checks in this run confirm the publication slice is still missing while the runtime prerequisite is already present:
  - `tests/conformance/fixtures/collection_replacement_workflows.py` already publishes `module-sub-callable-str` and `module-sub-grouping-template`, but it still has no grouped callable publication row for `"(abc)"`;
  - `tests/conformance/fixtures/named_group_replacement_workflows.py` still publishes only grouped template rows for `(?P<word>abc)`;
  - `reports/correctness/latest.py` already includes deeper same-family callable rows such as `module-sub-callable-grouped-alternation-str` and `module-sub-callable-nested-group-numbered-str`, but it does not yet include `module-sub-callable-grouped-str` or `pattern-sub-callable-named-grouped-str`; and
  - `reports/benchmarks/latest.py` does not yet include the paired simple grouped callable workload ids on the collection/replacement benchmark path, so benchmark catch-up remains a later same-family follow-on instead of this task.
