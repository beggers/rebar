# RBR-1223: Publish conditional group-exists callable None-count workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported top-level two-arm conditional callable `count=None` slice on the shared conditional callable replacement correctness owner path by adding the exact bounded `sub()` and `subn()` workflows that the live direct parity suite already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", lambda m: m.group(1) + "x", "zzabcdzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(lambda m: m.group("word") + b"x", b"zzacezz", None)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the twenty-four adjacent top-level two-arm conditional callable `count=None` workflows already exercised on the shared direct parity owner path:
  - add the twelve `str` workflows for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` across numbered and named module/compiled-`Pattern` `sub()` and `subn()` entrypoints by mirroring the already-published present, absent, and negative-count top-level case tables while passing `count=None`;
  - add the matching twelve `bytes` workflows for `rb"a(b)?c(?(1)d|e)"` and `rb"a(?P<word>b)?c(?(word)d|e)"` on the same numbered/named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's `TypeError` remains explicit on the same owner path without inventing another callable helper shape; and
  - keep the slice bounded to the top-level two-arm conditional callable family only, leaving alternation-heavy, nested, quantified, and any broader callable argument-contract publication for later tasks.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, and mixed-text scorecard sync stay aligned with the widened `count=None` slice;
  - reuse the existing direct parity tables in `tests/python/test_callable_replacement_parity_suite.py` as the publication anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into benchmark publication, Rust implementation work, or non-conditional callable-owner expansion.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `conditional-group-exists-callable-replacement-workflows` manifest stays present on the shared owner path and gains the twenty-four top-level conditional callable `count=None` cases without introducing failures or `unimplemented` outcomes; and
  - the tracked combined correctness summary moves from `1797` total cases / `1797` passes / `0` failures / `0` unimplemented across `114` manifests to `1821` total cases / `1821` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists and not alternation and not nested and not quantified'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the scope pinned to the exact twenty-four top-level conditional callable `count=None` workflows above. Leave any later same-route callable count-contract publication beyond this top-level family for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached conditional callable contract file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1223` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1223|RBR-1224" ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1219`:
  - `tests/python/test_callable_replacement_parity_suite.py` already exercises the bounded top-level conditional callable `count=None` parity path through `test_module_callable_replacement_none_count_matches_cpython_typeerror`, `test_pattern_callable_replacement_none_count_matches_cpython_typeerror`, `test_module_bytes_callable_replacement_none_count_matches_cpython_typeerror`, and `test_pattern_bytes_callable_replacement_none_count_matches_cpython_typeerror` across the existing top-level conditional numbered and named case ids;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` currently publish the top-level present, absent, and negative-count conditional callable rows on this owner path, but no `count=None` contract rows;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists and not alternation and not nested and not quantified'` passed with `48 passed, 5732 deselected`, confirming the bounded runtime slice already exists on the current branch; and
  - no newer same-family done task or blocked note pins an exact post-drain feature follow-on after this publication slice lands, so the tracked backlog/current-status frontier remains honest without further state edits in this run.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `3 passed, 44 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-correctness-current.py` returned `1797 total / 1797 passed / 0 failed / 0 unimplemented`.
- 2026-03-24T19:04:43+00:00: harness requeued after failed or incomplete run after run `20260324T190328Z-feature-implementation-RBR-1223-publish-conditional-group-exists-callable-none-count-workflows` (exit=1, timed_out=false).
- Completed 2026-03-24: published the twenty-four top-level conditional callable `count=None` rows on the shared owner path, updated the shared callable parity/spec plumbing for explicit `None` counts, and republished `reports/correctness/latest.py` with `168/168` passing cases for `collection.replacement.conditional_group_exists.callable` and `1821/1821` passing cases across `114` manifests.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists and not alternation and not nested and not quantified'` -> `144 passed, 5828 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_cases_stay_aligned_with_published_fixture tests/python/test_callable_replacement_parity_suite.py::test_callable_replacement_callback_exception_case_pools_exclude_negative_count_none_count_and_no_match_rows` -> `11 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` -> `4 passed, 44 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1223-conditional-callable-none-count.py` -> `168 executed / 168 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` -> `1821 executed / 1821 passed`
