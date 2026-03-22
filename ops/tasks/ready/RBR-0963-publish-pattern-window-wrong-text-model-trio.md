# RBR-0963: Publish the direct Pattern window wrong-text-model trio

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the shared `module-workflow-surface` correctness frontier with the three adjacent direct-`Pattern` window-helper wrong-text-model spellings that the current runtime already matches, publishing the exact CPython-visible `TypeError` messages for `search()`, `match()`, and `fullmatch()` before a later Python-path benchmark catch-up widens the same `pattern_boundary.py` owner route.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").search(b"abc")`
- `re.compile(b"abc").match("abc")`
- `re.compile("abc").fullmatch(b"abc")`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly three new direct-`Pattern` `pattern_call` rows:
  - add `workflow-pattern-search-str-pattern-on-bytes-string`;
  - add `workflow-pattern-match-bytes-pattern-on-str-string`; and
  - add `workflow-pattern-fullmatch-str-pattern-on-bytes-string`.
  - keep `workflow-pattern-search-str-pattern-on-bytes-string` on the `str` path with `helper == "search"`, `pattern == "abc"`, and bytes payload encoding for `args == [b"abc"]`;
  - keep `workflow-pattern-match-bytes-pattern-on-str-string` on the `bytes` path with `helper == "match"`, `pattern == "abc"`, and `args == ["abc"]`;
  - keep `workflow-pattern-fullmatch-str-pattern-on-bytes-string` on the `str` path with `helper == "fullmatch"`, `pattern == "abc"`, and bytes payload encoding for `args == [b"abc"]`;
  - insert `workflow-pattern-search-str-pattern-on-bytes-string` immediately after `workflow-pattern-search-bytes-endpos-indexlike`;
  - insert `workflow-pattern-match-bytes-pattern-on-str-string` immediately after `workflow-pattern-match-bytes-window-indexlike`;
  - insert `workflow-pattern-fullmatch-str-pattern-on-bytes-string` immediately after `workflow-pattern-fullmatch-bytes-window-indexlike`;
  - categorize the three rows under the shared direct-`Pattern` wrong-text-model path with `["workflow", "<helper>", "literal", "<text-model>", "wrong-text-model"]`; and
  - keep the notes explicit that these are the adjacent direct-`Pattern` window wrong-text-model spellings on the shared owner path, not a broader pattern-helper error dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing direct-`Pattern` wrong-text-model owner path instead of creating another manifest, parity suite, or detached selector table:
  - extend `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases(...)` so the selected direct slice now includes:
    - `pattern-search-str-pattern-on-bytes-string`;
    - `pattern-match-bytes-pattern-on-str-string`;
    - `pattern-fullmatch-str-pattern-on-bytes-string`;
    - plus the already-published `split` / `sub` / `subn` wrong-text-model rows in stable order afterward;
  - move the published direct-`Pattern` wrong-text-model slice from `3` rows to `6`;
  - move the slice text-model split from `2` `str` / `1` `bytes` to `4` / `2`;
  - keep the slice helper breakdown honest at `search: 1`, `match: 1`, `fullmatch: 1`, `split: 1`, `sub: 1`, and `subn: 1`;
  - keep the selected direct-case ordering aligned with the published fixture ordering for the three new rows above; and
  - keep the broader pattern-call bundle honest by moving `PATTERN_CASES` from `70` rows to `73`, with helper totals moving from `search: 16` / `match: 6` / `fullmatch: 11` to `17` / `7` / `12` while leaving the other helper totals unchanged.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1553` total / `1553` passed / `0` unimplemented across `114` manifests to `1556` / `1556` / `0` across the same `114` manifests;
  - `module.workflow` moves from `179` / `179` / `0` to `182` / `182` / `0`;
  - `module.workflow.str` moves from `100` / `100` / `0` to `102` / `102` / `0`;
  - `module.workflow.bytes` moves from `79` / `79` / `0` to `80` / `80` / `0`;
  - `module.workflow.pattern_call` moves from `70` / `70` / `0` to `73` / `73` / `0`;
  - `module.workflow.module_call` stays `97` / `97` / `0`; and
  - at least one of the three new direct-`Pattern` wrong-text-model rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0963-pattern-window-wrong-text-model-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached wrong-text-model publication file.
- Keep the scope pinned to the three direct-`Pattern` wrong-text-model helper calls above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/pattern_boundary.py` for a later task.

## Notes
- `RBR-0963` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 8` currently ends at `RBR-0962-collapse-compiled-pattern-module-compile-case-surface-split.md`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after the drained direct-`Pattern` replacement keyword benchmark catch-up because the shared collection/replacement keyword lane is now fully published in the current bounded slice, while the next concrete unpublished owner-path gap sits back on the adjacent direct-`Pattern` window wrong-text-model correctness surface rather than another benchmark-only sibling.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string'` currently passes (`6 passed`), so the exact bounded owner-path parity is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile('abc').search(b'abc') ... rebar.compile('abc').search(b'abc') ... re.compile(b'abc').match('abc') ... rebar.compile(b'abc').match('abc') ... re.compile('abc').fullmatch(b'abc') ... rebar.compile('abc').fullmatch(b'abc') ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `('cannot use a string pattern on a bytes-like object',)` for the `search()` and `fullmatch()` spellings plus `('cannot use a bytes pattern on a string-like object',)` for the `match()` spelling;
  - `rg -n 'workflow-pattern-search-str-pattern-on-bytes-string|workflow-pattern-match-bytes-pattern-on-str-string|workflow-pattern-fullmatch-str-pattern-on-bytes-string' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py tests/conformance/test_combined_correctness_scorecards.py` currently returns no matches, so the exact publication ids are still absent in this checkout; and
  - `rg -n 'pattern-search-on-bytes-string|pattern-match-on-str-string|pattern-fullmatch-on-bytes-string' benchmarks/workloads/pattern_boundary.py reports/benchmarks/latest.py` currently returns no matches, so a later benchmark catch-up will still be concrete after this correctness publication lands.
