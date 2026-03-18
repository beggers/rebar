# RBR-0622: Fold the detached nested-and-alternation conditional suite into the core conditional suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Expand `tests/python/test_conditional_group_exists_parity_suite.py` to absorb `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`, so the conditional group-exists parity surface has one fixture-backed owner instead of a second detached suite that repeats the same bundle-contract plus compile/module/pattern parity ladders.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` covers exactly the current twenty-two manifests carried by the two suites, and no more:
  - current base and quantified manifests:
    - `optional-group-conditional-workflows`
    - `conditional-group-exists-workflows`
    - `conditional-group-exists-no-else-workflows`
    - `conditional-group-exists-empty-else-workflows`
    - `conditional-group-exists-empty-yes-else-workflows`
    - `conditional-group-exists-fully-empty-workflows`
    - `conditional-group-exists-quantified-workflows`
    - `conditional-group-exists-quantified-alternation-workflows`
    - `conditional-group-exists-no-else-quantified-workflows`
    - `conditional-group-exists-empty-else-quantified-workflows`
    - `conditional-group-exists-empty-yes-else-quantified-workflows`
    - `conditional-group-exists-fully-empty-quantified-workflows`
  - absorbed nested and alternation manifests:
    - `conditional-group-exists-nested-workflows`
    - `conditional-group-exists-no-else-nested-workflows`
    - `conditional-group-exists-empty-else-nested-workflows`
    - `conditional-group-exists-empty-yes-else-nested-workflows`
    - `conditional-group-exists-fully-empty-nested-workflows`
    - `conditional-group-exists-alternation-workflows`
    - `conditional-group-exists-no-else-alternation-workflows`
    - `conditional-group-exists-empty-else-alternation-workflows`
    - `conditional-group-exists-empty-yes-else-alternation-workflows`
    - `conditional-group-exists-fully-empty-alternation-workflows`
- One local definition surface in `tests/python/test_conditional_group_exists_parity_suite.py` owns the per-family metadata now split across the two files:
  - the ordered `FixtureBundleSpec(...)` declarations for all twenty-two manifests;
  - the current base bounded-window and optional-group branch-selection case tables from the core suite;
  - the current generated quantified-conditional spec/candidate tables plus match-api and supplemental fullmatch/miss tables from the core suite; and
  - the current nested/alternation helper-count constants plus simple compile/module/pattern partitions from the detached suite.
- The consolidation preserves the current twelve-manifest core conditional coverage exactly:
  - keep the same manifest ids, exact `expected_case_ids`, exact pattern sets, and exact `expected_operation_helper_counts`;
  - preserve `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, and `OPTIONAL_GROUP_CONDITIONAL_BRANCH_CASES` exactly, including ids, helper selection, strings, and bounds; and
  - preserve `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS`, `MATCH_API_CASES`, `SUPPLEMENTAL_MODULE_FULLMATCH_CASES`, `SUPPLEMENTAL_PATTERN_FULLMATCH_CASES`, and `SUPPLEMENTAL_MISS_CASES` exactly, including failure prefixes, candidate counts, branch choices, ids, patterns, helpers, targets, texts, and bounds.
- The consolidation preserves the current ten-manifest nested/alternation coverage exactly:
  - keep the same manifest ids, exact `expected_case_ids`, exact pattern sets, and exact `expected_operation_helper_counts`;
  - preserve the detached suite's explicit `SYSTEMATIC_EMPTY_ELSE_OPERATION_HELPER_COUNTS` override for `conditional-group-exists-empty-else-nested-workflows`;
  - preserve the detached suite's explicit `FULLY_EMPTY_ALTERNATION_OPERATION_HELPER_COUNTS` split for `conditional-group-exists-fully-empty-alternation-workflows`; and
  - keep the absorbed nested/alternation rows str-only instead of widening them into bytes follow-ons, selector-backed frontier checks, or new generated matrices.
- The combined suite keeps the current conditional parity ladders only:
  - fixture-bundle contract coverage through `assert_fixture_bundle_contract(...)`;
  - compile parity through `compile_with_cpython_parity(...)`;
  - published module and pattern workflow parity through `assert_match_result_parity(...)` and the existing core-suite `assert_match_parity(...)` path; and
  - match convenience plus valid/invalid group-access parity only for the current match-producing rows that already exercise it today.
- Keep this consolidation local and ordinary:
  - prefer one local ordered bundle/spec table plus file-local dataclasses/helpers over another support module, registry layer, or import-only wrapper;
  - keep `tests/python/fixture_parity_support.py`, correctness fixtures, benchmarks, reports, Rust code, and `python/rebar/` out of scope; and
  - do not broaden into conditional replacement/callable-replacement suites, bytes follow-ons, or another multi-suite module-surface merge.
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
    "conditional-group-exists-nested-workflows",
    "conditional-group-exists-no-else-nested-workflows",
    "conditional-group-exists-empty-else-nested-workflows",
    "conditional-group-exists-empty-yes-else-nested-workflows",
    "conditional-group-exists-fully-empty-nested-workflows",
    "conditional-group-exists-alternation-workflows",
    "conditional-group-exists-no-else-alternation-workflows",
    "conditional-group-exists-empty-else-alternation-workflows",
    "conditional-group-exists-empty-yes-else-alternation-workflows",
    "conditional-group-exists-fully-empty-alternation-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_nested_alternation_parity_suite\\.py$'"`
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
    "conditional-group-exists-nested-workflows",
    "conditional-group-exists-no-else-nested-workflows",
    "conditional-group-exists-empty-else-nested-workflows",
    "conditional-group-exists-empty-yes-else-nested-workflows",
    "conditional-group-exists-fully-empty-nested-workflows",
    "conditional-group-exists-alternation-workflows",
    "conditional-group-exists-no-else-alternation-workflows",
    "conditional-group-exists-empty-else-alternation-workflows",
    "conditional-group-exists-empty-yes-else-alternation-workflows",
    "conditional-group-exists-fully-empty-alternation-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_nested_alternation_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, manifest ids, case ids, pattern sets, generated candidate matrices, helper routing, failure messages, or bounded supplemental texts/bounds.
- Keep the absorbed nested/alternation slice str-only; do not widen it into bytes parity during this cleanup.
- Do not replace the deleted suite with an import-only wrapper or another support layer; the end state should be one real conditional owner suite.

## Notes
- `RBR-0622` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve `RBR-0621` only; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` do not already contain `RBR-0622`.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: c94744a817c4643b4d43102341151e9dad615222`, which matches the live clean checkout for this run; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_conditional_group_exists_parity_suite.py` is `1286` lines and `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` is `363` lines;
  - `RBR-0614` and `RBR-0616` explicitly stopped after collapsing the smaller sibling splits inside this family, leaving the remaining detached nested/alternation owner as the next local simplification target; and
  - both files still define the same fixture-bundle contract, compile-through-`compile_with_cpython_parity(...)`, module-call result parity, and compiled-pattern `fullmatch()` parity shape, while only their manifest tables and file-local supplemental case partitions differ.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` passes (`530 passed in 0.47s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` manifest-order probe above currently fails exactly on this cleanup with `AssertionError` because `tests/python/test_conditional_group_exists_parity_suite.py` still exposes only the twelve base and quantified manifests; and
  - `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_nested_alternation_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists.
- 2026-03-18 completion:
  - Expanded `tests/python/test_conditional_group_exists_parity_suite.py` to carry all twenty-two conditional bundle specs in the required order, keeping the existing core bounded-window/generated-quantified tables intact while folding in the detached nested/alternation helper-count constants and compile/module/pattern partitions locally.
  - Deleted `tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py`; `git diff --name-status -- tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_nested_alternation_parity_suite.py` now reports `D` for the detached suite and `M` for the combined owner.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` (`530 passed in 0.48s`), the inline manifest-order probe (`ok`), and `bash -lc "! rg --files tests/python | rg 'test_conditional_group_exists_nested_alternation_parity_suite\\.py$'"` (no matches).
