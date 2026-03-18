# RBR-0610: Collapse the callable replacement fixture and near-miss ladders onto shared specs

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the manifest-specific callable replacement fixture-shape checks and near-miss no-match ladders in `tests/python/test_callable_replacement_parity_suite.py` with one local spec-driven surface plus shared parametrized assertions, so the suite stops restating the same logic for the conditional, quantified nested-group, and nested broader-range callable families.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` keeps the current published callable replacement coverage, but replaces the duplicated manifest-specific fixture and near-miss ladders with shared local tables plus parametrized tests:
  - keep the literal callable case contract, the bundle-wide fixture shape contract, the published module/pattern callable parity assertions, the callback match-object and callback-exception parity checks, and the pattern wrong-return-type checks;
  - keep `EXPECTED_OPERATION_HELPER_COUNTS`, `PENDING_REBAR_MANIFEST_IDS`, `PENDING_REBAR_COMPILE_PATTERNS`, `PENDING_REBAR_NO_MATCH_PATTERNS`, `_skip_pending_rebar_callable_parity()`, `_invoke_callable_replacement()`, and the existing callable helper assertions intact in behavior; and
  - do not widen the suite into bytes work, new fixtures, new pending-manifest skips, or helper extraction outside this file.
- Replace the current per-manifest constant ladders and four duplicate fixture-shape tests with one shared manifest-spec surface that owns only the metadata that currently differs across the four published callable families:
  - manifest id;
  - exact expected case-id set;
  - exact expected compile-pattern set; and
  - whether that family also owns an explicit near-miss matrix in this file.
- Consolidate these four tests into one parametrized assertion without changing coverage or behavior:
  - `test_quantified_nested_group_alternation_callable_cases_stay_aligned_with_published_fixture`
  - `test_conditional_group_exists_callable_cases_stay_aligned_with_published_fixture`
  - `test_nested_broader_range_open_ended_callable_cases_stay_aligned_with_published_fixture`
  - `test_nested_broader_range_open_ended_conditional_callable_cases_stay_aligned_with_published_fixture`
- Replace the three family-specific near-miss case tuples and duplicate near-miss tests with one shared near-miss surface plus one parametrized assertion:
  - preserve the exact `pytest.param(...)` ids, `pattern`, `helper`, `text`, `count`, and `expected_result` payloads currently carried by `CONDITIONAL_GROUP_EXISTS_CALLABLE_NEAR_MISS_CASES`, `QUANTIFIED_NESTED_GROUP_ALTERNATION_NO_MATCH_CASES`, and `NESTED_BROADER_RANGE_OPEN_ENDED_CALLABLE_NEAR_MISS_CASES`;
  - preserve the existing rebar pending-pattern skip behavior on those cases; and
  - preserve the existing `callback_calls == []` assertion for every near-miss row.
- Keep this cleanup structural and local:
  - do not change `tests/python/fixture_parity_support.py`, correctness fixtures, reports, Rust code, benchmark files, or `python/rebar/`;
  - prefer ordinary local dataclasses/tuples plus parametrized pytest over another support module, registry layer, or cross-suite abstraction; and
  - delete duplicate local constants and tests rather than hiding them behind a second wrapper layer.
- After the cleanup lands, no manifest-specific fixture-shape or near-miss test functions remain in the file:
  - `bash -lc "! rg -n '^def test_(quantified_nested_group_alternation|conditional_group_exists|nested_broader_range_open_ended|nested_broader_range_open_ended_conditional)_callable_cases_stay_aligned_with_published_fixture|^def test_(conditional_group_exists|quantified_nested_group_alternation|nested_broader_range_open_ended)_callable_replacement_near_miss_paths_leave_input_unchanged' tests/python/test_callable_replacement_parity_suite.py"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^def test_(quantified_nested_group_alternation|conditional_group_exists|nested_broader_range_open_ended|nested_broader_range_open_ended_conditional)_callable_cases_stay_aligned_with_published_fixture|^def test_(conditional_group_exists|quantified_nested_group_alternation|nested_broader_range_open_ended)_callable_replacement_near_miss_paths_leave_input_unchanged' tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Keep the task structural only. Do not change the published callable replacement frontier, pending-manifest policy, or backend behavior.
- Preserve the current callable-fixture ids, compile-pattern sets, and near-miss payloads exactly; the point is to delete duplicate harness code, not reinterpret callable semantics.
- Keep this suite self-contained. Do not add a new shared helper module or move callable replacement metadata into `fixture_parity_support.py`.

## Notes
- `RBR-0610` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` name no reserved `RBR-0610`;
  - `ops/tasks/ready/` currently stops at `RBR-0609`; and
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: 04eae51c3ea54c64d29b8bead91d49913f48be21`, which matches the current clean checkout state for this run; and
  - the latest runtime cycle finished both task workers at `done`, with no inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_callable_replacement_parity_suite.py` is currently `1336` lines long;
  - the file still carries four manifest-specific fixture-shape tests and three manifest-specific near-miss tests matching the `rg` pattern above; and
  - those seven tests all restate the same bundle lookup / expected-case-id / expected-pattern / no-match callback assertions with different local constants.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` passes (`963 passed in 0.79s`)
  - the `bash -lc "! rg -n ..."` command above currently fails exactly on this cleanup because the seven duplicate manifest-specific test definitions are still present.
- 2026-03-18 completion:
  - Replaced the manifest-specific callable fixture-shape and near-miss ladders in `tests/python/test_callable_replacement_parity_suite.py` with local `CallableManifestSpec` and `CallableNearMissCase` tables plus shared parametrized assertions, while preserving the existing callable helper counts, pending-manifest behavior, fixture ids, compile-pattern sets, and near-miss payloads.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` (`963 passed in 0.82s`) and the required `bash -lc "! rg -n ..."` absence check (no matches).
