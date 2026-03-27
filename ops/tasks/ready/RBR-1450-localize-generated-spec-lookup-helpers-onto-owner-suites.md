## RBR-1450: Localize generated spec lookup helpers onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the shared generated-spec lookup layer from `tests/python/fixture_parity_support.py`.
- Keep generated-text matrix ownership with the three parity suites that actually define those generated spec tables instead of routing lookup through a cross-suite support module plus a central contract file.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- Rewrite `tests/python/test_quantified_alternation_parity_suite.py` so it no longer imports `generated_specs_by_manifest_id` or `generated_spec_by_manifest_id` from `tests.python.fixture_parity_support`, and instead owns the tiny manifest-id indexing and lookup helper it needs for `GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS`.
- Rewrite `tests/python/test_branch_local_backreference_parity_suite.py` so it no longer imports `generated_specs_by_manifest_id` or `generated_spec_by_manifest_id` from `tests.python.fixture_parity_support`, and instead owns the tiny manifest-id indexing and lookup helper it needs for `GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPECS`.
- Rewrite `tests/python/test_conditional_group_exists_parity_suite.py` so it no longer imports `generated_specs_by_manifest_id` or `generated_spec_by_manifest_id` from `tests.python.fixture_parity_support`, and instead owns the tiny manifest-id indexing and lookup helper it needs for its generated quantified conditional specs.
- Delete `generated_specs_by_manifest_id` and `generated_spec_by_manifest_id` from `tests/python/fixture_parity_support.py`, and retire the matching contract coverage from `tests/python/test_fixture_parity_support_contract.py` instead of moving that contract to another shared helper surface.
- Keep the run structural:
  - do not change `python/rebar_harness/`, `python/rebar/`, Rust sources, published reports, or tracked project-state prose
  - do not add a replacement shared support module under `tests/`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_fixture_parity_support_contract.py -k 'generated_spec or generated_text_matrix'`
- `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_fixture_parity_support_contract.py`
- `bash -lc \"! rg -n 'def generated_specs_by_manifest_id|def generated_spec_by_manifest_id' tests/python/fixture_parity_support.py\"`
- `bash -lc \"! rg -n 'generated_specs_by_manifest_id|generated_spec_by_manifest_id' tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py\"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this planning run:
  - `ops/tasks/blocked/` contained no architecture task to reopen or normalize first.
  - `rg -n \"RBR-145[0-9]|RBR-14[6-9][0-9]|RBR-15[0-9][0-9]\" ops/state/backlog.md ops/state/current_status.md || true` returned no reserved future IDs, so `RBR-1450` was available.
- Candidate selection in this planning run:
  - `tests/python/fixture_parity_support.py` still exports `generated_specs_by_manifest_id` and `generated_spec_by_manifest_id`, but only three parity owners consume them: `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `tests/python/test_conditional_group_exists_parity_suite.py`.
  - Those helpers are only a thin manifest-id index/lookup layer around owner-local spec tuples, so keeping them shared preserves a small but unnecessary cross-suite abstraction after the larger benchmark/publication dependency path was already removed.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_fixture_parity_support_contract.py -k 'generated_spec or generated_text_matrix'` passed (`7 passed, 2311 deselected`).
  - `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_fixture_parity_support_contract.py` passed.
  - The two negative `rg` verifications are intentionally red in the current checkout because the shared helper definitions and imports are the exact boundary this task removes.
