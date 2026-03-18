# RBR-0614: Collapse the conditional nested and alternation parity suites onto one suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Replace `tests/python/test_conditional_group_exists_nested_parity_suite.py` and `tests/python/test_conditional_group_exists_alternation_parity_suite.py` with one fixture-backed pytest suite so this conditional parity surface stops carrying the same bundle-contract, compile-parity, module-workflow, and pattern-fullmatch ladders in two near-identical files.

## Deliverables
- `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_nested_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` covers exactly the current ten manifest bundles carried by the two superseded modules, and no more:
  - nested conditional bundles:
    - `conditional-group-exists-nested-workflows`
    - `conditional-group-exists-no-else-nested-workflows`
    - `conditional-group-exists-empty-else-nested-workflows`
    - `conditional-group-exists-empty-yes-else-nested-workflows`
    - `conditional-group-exists-fully-empty-nested-workflows`
  - alternation conditional bundles:
    - `conditional-group-exists-alternation-workflows`
    - `conditional-group-exists-no-else-alternation-workflows`
    - `conditional-group-exists-empty-else-alternation-workflows`
    - `conditional-group-exists-empty-yes-else-alternation-workflows`
    - `conditional-group-exists-fully-empty-alternation-workflows`
- The consolidation preserves the exact published bundle expectations that live in the two superseded files today:
  - keep the same manifest ids, exact `expected_case_ids`, exact pattern sets, and exact `expected_operation_helper_counts` per manifest;
  - preserve the nested suite's explicit `SYSTEMATIC_EMPTY_ELSE_OPERATION_HELPER_COUNTS` override for `conditional-group-exists-empty-else-nested-workflows`;
  - preserve the alternation suite's explicit `module_call/fullmatch` split for `conditional-group-exists-fully-empty-alternation-workflows`; and
  - keep the suite str-only instead of widening into bytes follow-ons or selector-backed frontier checks.
- The combined suite keeps the current four parity ladders only:
  - bundle-contract coverage through `assert_fixture_bundle_contract(...)`;
  - compile parity through `compile_with_cpython_parity(...)`;
  - module workflow result parity through `assert_match_result_parity(...)`; and
  - pattern `fullmatch()` result parity through `assert_match_result_parity(...)`.
- Keep this consolidation local and ordinary:
  - prefer one local `FIXTURE_BUNDLE_SPECS` declaration or one small local grouping table in the new file over another helper module, registry, or import-only wrapper;
  - keep `tests/python/fixture_parity_support.py`, `python/rebar_harness/`, correctness fixtures, benchmarks, reports, Rust code, and `python/rebar/` out of scope; and
  - do not broaden into `tests/python/test_conditional_group_exists_parity_suite.py` or `tests/python/test_conditional_group_exists_quantified_parity_suite.py` in the same run.
- After the consolidation lands:
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_(nested|alternation)_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_(nested|alternation)_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, manifest ids, pattern sets, case-id sets, or operation/helper counts.
- Do not replace the deleted modules with import-only wrappers or another support layer; the end state should be one real suite.
- Preserve readable pytest ids so the manifest ids and case ids that currently surface in the two files remain visible in the combined suite output.

## Notes
- `RBR-0614` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve `RBR-0613` only; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` do not already contain `RBR-0614`.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: bdbade9a024104825e1bfffeb482af7a27dfb106`, which matches the live clean checkout for this run; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_conditional_group_exists_nested_parity_suite.py` and `tests/python/test_conditional_group_exists_alternation_parity_suite.py` currently total `453` lines;
  - both files declare the same four test ladders over `FIXTURE_BUNDLE_SPECS`, `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES`; and
  - the only meaningful differences between the files are the ten manifest-specific `FixtureBundleSpec(...)` declarations and the nested suite's explicit empty-else counter override.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py` passes (`190 passed in 0.18s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`; and
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_(nested|alternation)_parity_suite\\.py$'"` currently fails exactly on this cleanup because both superseded files still exist.
- 2026-03-18 completion:
  - Replaced the two superseded modules with `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`, keeping one local ordered `FIXTURE_BUNDLE_SPECS` table for the same ten nested and alternation manifests, the nested empty-else systematic helper-count override, the alternation fully-empty `module_call`/`fullmatch` split, and the existing four parity ladders.
  - Deleted `tests/python/test_conditional_group_exists_nested_parity_suite.py` and `tests/python/test_conditional_group_exists_alternation_parity_suite.py`, with `git diff --name-status -- ...` reporting both legacy paths as `D`.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` (`190 passed in 0.16s`) and `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_(nested|alternation)_parity_suite\\.py$'"` (no matches).
