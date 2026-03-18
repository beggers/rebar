# RBR-0616: Collapse the conditional core and quantified parity suites onto one suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Expand `tests/python/test_conditional_group_exists_parity_suite.py` to absorb `tests/python/test_conditional_group_exists_quantified_parity_suite.py` so the conditional parity surface stops splitting the same fixture-bundle contract plus compile/module/pattern parity ladders across two near-parallel suites.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_quantified_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` covers exactly the current twelve manifests carried by the two superseded suites, and no more:
  - base conditional manifests:
    - `optional-group-conditional-workflows`
    - `conditional-group-exists-workflows`
    - `conditional-group-exists-no-else-workflows`
    - `conditional-group-exists-empty-else-workflows`
    - `conditional-group-exists-empty-yes-else-workflows`
    - `conditional-group-exists-fully-empty-workflows`
  - quantified conditional manifests:
    - `conditional-group-exists-quantified-workflows`
    - `conditional-group-exists-quantified-alternation-workflows`
    - `conditional-group-exists-no-else-quantified-workflows`
    - `conditional-group-exists-empty-else-quantified-workflows`
    - `conditional-group-exists-empty-yes-else-quantified-workflows`
    - `conditional-group-exists-fully-empty-quantified-workflows`
- One local definition surface in `tests/python/test_conditional_group_exists_parity_suite.py` owns the per-family metadata now spread across the two files:
  - the ordered `FixtureBundleSpec(...)` declarations for all twelve manifests;
  - the current bounded-window and branch-selection case partitions from the base suite; and
  - the current quantified match-api, supplemental fullmatch, and supplemental miss partitions from the quantified suite.
- The consolidation preserves the current base conditional coverage exactly:
  - keep the same six base manifest ids, exact `expected_case_ids`, exact pattern sets, and exact `expected_operation_helper_counts`;
  - preserve `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, and `OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASES` exactly, including ids, helper selection, strings, and bounds; and
  - keep the optional-group conditional branch-selection checks on the existing direct bounded-window path instead of replacing them with a new helper module or selector layer.
- The consolidation preserves the current quantified conditional coverage exactly:
  - keep the same six quantified manifest ids, exact `expected_case_ids`, exact pattern sets, and exact `expected_operation_helper_counts`;
  - preserve `MATCH_API_CASE_IDS`, `SUPPLEMENTAL_MODULE_FULLMATCH_CASES`, `SUPPLEMENTAL_PATTERN_FULLMATCH_CASES`, and `SUPPLEMENTAL_MISS_CASES` exactly, including ids, patterns, texts, helpers, and target routing; and
  - keep the quantified alternation pattern constants and match-producing case selection explicit in the combined suite rather than moving them into another support module.
- The combined suite keeps the current conditional parity ladders only:
  - fixture-bundle contract coverage through `assert_fixture_bundle_contract(...)`;
  - compile parity through `compile_with_cpython_parity(...)`;
  - published module and pattern workflow parity through `assert_match_result_parity(...)` and `assert_match_parity(...)`; and
  - match convenience/group-access parity only for the current match-producing rows that already exercise it today.
- Keep this consolidation local and ordinary:
  - prefer one local ordered bundle/spec table plus file-local dataclasses/helpers over another support module, registry layer, or import-only wrapper;
  - keep `tests/python/fixture_parity_support.py`, correctness fixtures, benchmarks, reports, Rust code, and `python/rebar/` out of scope; and
  - do not broaden into `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`, replacement/callable conditional suites, or bytes follow-ons.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_conditional_group_exists_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES) == (
    "optional-group-conditional-workflows",
    "conditional-group-exists-workflows",
    "conditional-group-exists-no-else-workflows",
    "conditional-group-exists-empty-else-workflows",
    "conditional-group-exists-empty-yes-else-workflows",
    "conditional-group-exists-fully-empty-workflows",
    "conditional-group-exists-quantified-workflows",
    "conditional-group-exists-quantified-alternation-workflows",
    "conditional-group-exists-no-else-quantified-workflows",
    "conditional-group-exists-empty-else-quantified-workflows",
    "conditional-group-exists-empty-yes-else-quantified-workflows",
    "conditional-group-exists-fully-empty-quantified-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_quantified_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_conditional_group_exists_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES) == (
    "optional-group-conditional-workflows",
    "conditional-group-exists-workflows",
    "conditional-group-exists-no-else-workflows",
    "conditional-group-exists-empty-else-workflows",
    "conditional-group-exists-empty-yes-else-workflows",
    "conditional-group-exists-fully-empty-workflows",
    "conditional-group-exists-quantified-workflows",
    "conditional-group-exists-quantified-alternation-workflows",
    "conditional-group-exists-no-else-quantified-workflows",
    "conditional-group-exists-empty-else-quantified-workflows",
    "conditional-group-exists-empty-yes-else-quantified-workflows",
    "conditional-group-exists-fully-empty-quantified-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_quantified_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, manifest ids, case ids, pattern sets, texts, bounds, or helper routing.
- Keep the combined suite str-only; do not widen it into bytes parity or selector-backed publication checks.
- Do not replace the deleted quantified module with an import-only wrapper or a second support layer; the end state should be one real suite.

## Notes
- `RBR-0616` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve `RBR-0616` or a later concrete architecture follow-on;
  - `ops/tasks/ready/` currently stops at `RBR-0615`; and
  - `ops/tasks/in_progress/` and `ops/tasks/blocked/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: e9836163522072ba49a19eb8fbe00c460d9e268e`, which matches the live clean checkout for this run; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_conditional_group_exists_parity_suite.py` is `518` lines and `tests/python/test_conditional_group_exists_quantified_parity_suite.py` is `607` lines;
  - `RBR-0614` explicitly kept these two files out of scope while collapsing the nested and alternation conditional suites, leaving the core-plus-quantified split as the next conditional parity duplication target; and
  - both files still define the same fixture-bundle contract plus compile/module/pattern parity shape, while only their local supplemental case tables differ.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py` passes (`330 passed in 0.27s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` manifest probe above currently fails exactly on this cleanup with `AssertionError` because `tests/python/test_conditional_group_exists_parity_suite.py` still exposes only the six base manifests; and
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_quantified_parity_suite\\.py$'"` currently fails exactly on this cleanup because the redundant quantified-only suite still exists.
