# RBR-1111: Collapse single-manifest selector bundle loads onto shared parity support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining owner-local selector-to-first-path bundle-loading boilerplate in parity suites by routing single-manifest correctness selectors through one shared helper on `tests/python/fixture_parity_support.py` instead of repeating `select_correctness_fixture_paths(...)[0]` or `*_FIXTURE_PATHS[0]`.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing support path, that:
  - resolves a correctness fixture selector through `select_correctness_fixture_paths(...)`;
  - requires that selector to resolve to exactly one published fixture path; and
  - returns the corresponding `FixtureBundle` through the existing `build_selected_fixture_bundle(...)` path without adding a new registry or wrapper layer elsewhere.
- Extend `tests/python/test_fixture_parity_support_contract.py` so the helper is covered for:
  - returning the expected manifest path and manifest id when a selector resolves to exactly one published fixture; and
  - rejecting selectors that resolve to more than one published fixture path with a clear error.
- `tests/python/test_literal_flag_parity_suite.py` stops open-coding `build_selected_fixture_bundle(select_correctness_fixture_paths(LITERAL_FLAG_FIXTURE_SELECTOR)[0])` and uses the shared helper instead.
- `tests/python/test_module_workflow_parity_suite.py` stops carrying the owner-local collection-replacement first-path plumbing:
  - remove the top-level `COLLECTION_REPLACEMENT_FIXTURE_PATHS = select_correctness_fixture_paths(...)` setup; and
  - build `COLLECTION_REPLACEMENT_BUNDLE` through the shared single-manifest helper instead of indexing `[0]`.
- `tests/python/test_callable_replacement_parity_suite.py` stops carrying the same owner-local collection-replacement first-path plumbing:
  - remove the top-level `COLLECTION_REPLACEMENT_FIXTURE_PATHS = select_correctness_fixture_paths(...)` setup; and
  - build `COLLECTION_REPLACEMENT_OWNER_BUNDLE` through the shared single-manifest helper instead of indexing `[0]`.
- Preserve current owner behavior after the cleanup:
  - the same manifest ids still back `LITERAL_FLAG_FIXTURE_BUNDLE`, `COLLECTION_REPLACEMENT_BUNDLE`, and `COLLECTION_REPLACEMENT_OWNER_BUNDLE`;
  - current expected fixture-path assertions still pass; and
  - no direct parity expectations, selected case slices, or manifest-specific assertions change.
- Keep the cleanup structural and limited to the five files above. Do not widen it into harness implementation code, reports, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
- `bash -lc "! rg -n 'select_correctness_fixture_paths\\(LITERAL_FLAG_FIXTURE_SELECTOR\\)\\[0\\]|^COLLECTION_REPLACEMENT_FIXTURE_PATHS = select_correctness_fixture_paths\\(|COLLECTION_REPLACEMENT_FIXTURE_PATHS\\[0\\]' tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"`

## Constraints
- Prefer extending `tests/python/fixture_parity_support.py` over adding a new support module, registry, or detached abstraction tier.
- Reuse `build_selected_fixture_bundle(...)` and `select_correctness_fixture_paths(...)` as they exist today; this task is about deleting repeated owner wiring, not inventing a new loading stack.
- Do not widen the task into the multi-manifest `load_published_fixture_bundles(...)` owners or the deeper selective-bundle reshaping in `tests/python/test_fixture_backed_replacement_parity_suite.py`.

## Notes
- `RBR-1111` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1110`; and
  - `rg -n 'RBR-1111|RBR-1112|RBR-1113|RBR-1114|RBR-1115' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_literal_flag_parity_suite.py:187-188` still open-codes a selector-to-first-path bundle load;
  - `tests/python/test_module_workflow_parity_suite.py:1132-1136` still open-codes the collection-replacement selector tuple plus `[0]` bundle load; and
  - `tests/python/test_callable_replacement_parity_suite.py:1093-1094` plus `tests/python/test_callable_replacement_parity_suite.py:1160-1161` still carry the same collection-replacement first-path plumbing.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` returned `5232 passed, 1 skipped` in this run.
- The negative `rg` verification currently fails exactly on the targeted owner-local boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.

## Completion
- Added `load_single_published_fixture_bundle()` on `tests/python/fixture_parity_support.py` so single-manifest correctness selectors resolve through one shared exact-one-path helper that still delegates to `build_selected_fixture_bundle(...)`.
- Extended `tests/python/test_fixture_parity_support_contract.py` with contract coverage for the new helper's exact-one-path success case and its multi-path rejection error.
- Replaced the remaining owner-local single-manifest selector-to-`[0]` bundle loads in `tests/python/test_literal_flag_parity_suite.py`, `tests/python/test_module_workflow_parity_suite.py`, and `tests/python/test_callable_replacement_parity_suite.py` without changing the backing manifest ids, selected case slices, or fixture-path assertions.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
- `bash -lc "! rg -n 'select_correctness_fixture_paths\\(LITERAL_FLAG_FIXTURE_SELECTOR\\)\\[0\\]|^COLLECTION_REPLACEMENT_FIXTURE_PATHS = select_correctness_fixture_paths\\(|COLLECTION_REPLACEMENT_FIXTURE_PATHS\\[0\\]' tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_callable_replacement_parity_suite.py"`
