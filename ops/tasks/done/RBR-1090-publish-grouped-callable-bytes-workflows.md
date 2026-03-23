# RBR-1090: Publish grouped callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the collection/replacement owner path with the first concrete follow-on explicitly left behind by `RBR-1088`, adding the exact bounded bytes grouped callable replacement workflows to the published correctness surface before bytes benchmark catch-up or broader grouped callable replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")`
- `rebar.compile(rb"(?P<word>abc)").subn(lambda m: b"<" + m.group("word") + b">", b"abcabc", 1)`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/conformance/fixtures/named_group_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Publish the exact bounded bytes grouped callable replacement slice on the existing collection/replacement correctness owner path without widening into benchmarks or broader grouped replacement families:
  - `collection-replacement-workflows` gains the numbered module grouped callable bytes rows for `rb"(abc)"` through `sub()` and `subn(count=1)`;
  - `named-group-replacement-workflows` gains the named compiled-pattern grouped callable bytes rows for `rb"(?P<word>abc)"` through `sub()` and `subn(count=1)`; and
  - the new published representative case ids are explicit in the tracked correctness surface:
    - `module-sub-callable-grouped-bytes`
    - `module-subn-callable-grouped-bytes`
    - `pattern-sub-callable-named-grouped-bytes`
    - `pattern-subn-callable-named-grouped-bytes`
- Keep the work on the existing fixture-backed correctness owner path rather than creating a new manifest family, detached direct-test file, or benchmark workload:
  - `tests/conformance/test_combined_correctness_scorecards.py` recognizes the new grouped callable bytes rows under the existing `collection-replacement-workflows` and `named-group-replacement-workflows` expectations; and
  - `reports/correctness/latest.py` is regenerated so the published case list and manifest summary include the new grouped callable bytes rows.
- Preserve the already-landed runtime and nearby publication surfaces while staying bounded:
  - `tests/python/test_callable_replacement_parity_suite.py` still passes for `test_grouped_callable_replacement_module_matches_cpython` and `test_grouped_callable_replacement_pattern_matches_cpython`, including the bytes parametrizations already present there;
  - the existing str grouped callable publication rows stay green on the same owner path; and
  - `reports/correctness/latest.py` moves from `1601` total / `1601` passed / `0` failed / `0` unimplemented across `114` manifests to `1605` / `1605` / `0` / `0` across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'collection-replacement-workflows or named-group-replacement-workflows'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the publication bounded to the exact bytes grouped callable slice already proven by direct parity coverage. Leave bytes grouped callable benchmark rows and broader grouped callable replacement expansion for later tasks.
- Reuse the existing `collection-replacement-workflows` and `named-group-replacement-workflows` manifests instead of inventing a new grouped-callable manifest for this tiny adjacent slice.
- Do not widen this task into Rust/Python runtime changes, benchmark manifests, benchmark scorecards, README text, or tracked state prose.

## Notes
- `RBR-1090` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1090|RBR-1091|RBR-1092' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1088` explicitly left bytes publication and broader grouped callable replacement expansion for later work on this same owner family, so this is the first concrete deferred same-family follow-on rather than a new synthesized frontier.
- Narrow owner-path checks in this run confirm the publication slice is still missing while the runtime prerequisite is already present:
  - `tests/python/test_callable_replacement_parity_suite.py` already parameterizes `test_grouped_callable_replacement_module_matches_cpython` and `test_grouped_callable_replacement_pattern_matches_cpython` over the exact bytes workflows above, confirming the runtime owner path is live and this task can stay publication-only;
  - `tests/conformance/fixtures/collection_replacement_workflows.py` currently publishes `module-sub-callable-grouped-str` and `module-subn-callable-grouped-str` but no bytes variants;
  - `tests/conformance/fixtures/named_group_replacement_workflows.py` currently publishes `pattern-sub-callable-named-grouped-str` and `pattern-subn-callable-named-grouped-str` but no bytes variants; and
  - `reports/correctness/latest.py` currently contains those four str grouped callable ids and none of the adjacent bytes ids, confirming the exact gap is on the published correctness surface rather than in the runtime or benchmark path.

## Completion
- Added the four bounded bytes grouped callable publication rows on the existing owner path:
  - `module-sub-callable-grouped-bytes`
  - `module-subn-callable-grouped-bytes`
  - `pattern-sub-callable-named-grouped-bytes`
  - `pattern-subn-callable-named-grouped-bytes`
- Updated `tests/conformance/test_combined_correctness_scorecards.py` so both owner manifests require those bytes representative ids alongside the already-published str rows.
- Republished `reports/correctness/latest.py`; the tracked scorecard now shows `1605` total / `1605` passed / `0` failed / `0` unimplemented across the same `114` manifests.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
