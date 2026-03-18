# RBR-0612: Collapse the fixture-backed replacement parity modules onto one suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` and `tests/python/test_conditional_group_exists_replacement_parity_suite.py` with one backend-parameterized pytest suite so the published replacement surface stops duplicating the same fixture loading, compile/search helper flow, replacement-result parity, match-expand parity, and no-match/repeated-path scaffolding across two near-parallel modules.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- Delete `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` covers exactly the current thirteen fixture-backed replacement manifests carried by the two superseded modules, and no more:
  - open-ended branch-local-backreference replacement manifests:
    - `nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows`
  - conditional replacement manifests:
    - `conditional-group-exists-replacement-workflows`
    - `conditional-group-exists-replacement-template-workflows`
    - `conditional-group-exists-no-else-replacement-workflows`
    - `conditional-group-exists-empty-else-replacement-workflows`
    - `conditional-group-exists-empty-yes-else-replacement-workflows`
    - `conditional-group-exists-fully-empty-replacement-workflows`
    - `conditional-group-exists-alternation-replacement-workflows`
    - `conditional-group-exists-nested-replacement-workflows`
    - `conditional-group-exists-quantified-replacement-workflows`
    - `conditional-group-exists-quantified-alternation-replacement-workflows`
- One local definition table in `tests/python/test_fixture_backed_replacement_parity_suite.py` owns the per-surface metadata currently duplicated across the two superseded files:
  - the ordered `FixtureBundleSpec` declarations for each absorbed surface;
  - the compile-pattern source for any surface that still checks compile metadata separately;
  - the case partitions that drive replacement-result parity, template-expand parity, and the surface-specific no-match or repeated-replacement follow-ons; and
  - whether that surface also runs a selector-backed published-fixture coverage assertion.
- The consolidation preserves the current open-ended replacement coverage exactly:
  - keep the same three manifest ids, exact case-id membership, exact compile-pattern set, and `(operation, helper)` counts now declared in `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`;
  - preserve compile metadata parity, module replacement parity, pattern replacement parity, match capture/expand parity, the exact sixteen supplemental no-match rows, and the exact eight repeated-replacement rows; and
  - keep those no-match rows asserting the current `sub -> string` and `subn -> (string, 0)` outcomes instead of adding selector logic, helper extraction, or new fixture rows.
- The consolidation preserves the current conditional replacement coverage exactly:
  - keep the same ten manifest ids, exact case-id membership, exact pattern sets, and shared `(operation, helper)` counts now declared in `tests/python/test_conditional_group_exists_replacement_parity_suite.py`;
  - preserve the selector-backed published-fixture frontier check through `CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR` and keep `KNOWN_UNCOVERED_PUBLISHED_FIXTURE_FILENAMES == ()`;
  - preserve replacement-result parity, match snapshot parity, template-expand parity, shared no-match-text discovery, and the exact four repeated-template replacement rows; and
  - do not invent a second published-fixture selector for the open-ended slice.
- Keep this consolidation local and ordinary:
  - prefer one local dataclass/tuple surface plus parametrized pytest over another support module, registry layer, or thin compatibility wrapper;
  - keep `compile_with_cpython_parity(...)`, `assert_fixture_bundle_contract(...)`, `assert_match_parity(...)`, and `assert_match_convenience_api_parity(...)` on the current fixture-backed path instead of rewriting replacement execution through a new helper package; and
  - keep `tests/python/test_grouped_literal_replacement_template.py`, `tests/python/test_callable_replacement_parity_suite.py`, `tests/python/fixture_parity_support.py`, correctness fixtures, benchmarks, reports, Rust code, and `python/rebar/` out of scope.
- After the consolidation lands:
  - `bash -lc "! rg --files tests/python | rg 'test_(conditional_group_exists_replacement_parity_suite|open_ended_quantified_group_replacement_template_parity_suite)\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg --files tests/python | rg 'test_(conditional_group_exists_replacement_parity_suite|open_ended_quantified_group_replacement_template_parity_suite)\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not widen replacement semantics, selector scope, manifest coverage, or backend behavior.
- Preserve the current fixture case ids, compile-pattern sets, `(operation, helper)` counts, selector membership, no-match payloads, and repeated-replacement payloads exactly; the point is to delete duplicate harness code, not reinterpret replacement behavior.
- Do not replace the deleted modules with import-only wrappers or another support layer; the end state should be one real suite.

## Notes
- `RBR-0612` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve `RBR-0611` only;
  - `ops/tasks/ready/` currently stops at `RBR-0611`; and
  - `ops/tasks/in_progress/` and `ops/tasks/blocked/` are empty aside from `.gitkeep`.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: 5ec3b50f22776c02cbb2eabc7b45faf09316577f`, which matches the live clean checkout for this run; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` and `tests/python/test_conditional_group_exists_replacement_parity_suite.py` currently total `1059` lines;
  - the two files define separate `_search_match_for_case(...)` helpers and near-parallel compile/replacement/match/no-match/repeated-path test ladders over the same fixture-backed replacement harness surface; and
  - the two files currently carry `13` raw `FixtureBundleSpec(...)` blocks whose only structural differences are manifest metadata, selector coverage on the conditional side, and the explicit supplemental replacement rows.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_conditional_group_exists_replacement_parity_suite.py` passes (`674 passed in 0.51s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/python/test_fixture_backed_replacement_parity_suite.py`; and
  - `bash -lc "! rg --files tests/python | rg 'test_(conditional_group_exists_replacement_parity_suite|open_ended_quantified_group_replacement_template_parity_suite)\\.py$'"` currently fails exactly on this cleanup because both superseded files still exist.
- 2026-03-18 completion:
  - Replaced the two superseded replacement parity modules with `tests/python/test_fixture_backed_replacement_parity_suite.py`, driven by one local `ReplacementSurfaceSpec` table that keeps the existing thirteen `FixtureBundleSpec(...)` declarations, open-ended compile-pattern coverage, conditional selector-backed fixture-frontier check, template-expand partitions, shared no-match discovery, and explicit supplemental no-match/repeated rows on one fixture-backed path.
  - Deleted `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` and `tests/python/test_conditional_group_exists_replacement_parity_suite.py`, and verified the final git diff reports both paths as `D`.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` (`674 passed in 0.50s`) and `bash -lc "! rg --files tests/python | rg 'test_(conditional_group_exists_replacement_parity_suite|open_ended_quantified_group_replacement_template_parity_suite)\\.py$'"` (no matches).
