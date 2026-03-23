# RBR-0996: Collapse collection call wrapper pair

Status: done
Owner: cleanup
Created: 2026-03-23

## Goal
- Remove the remaining duplicate collection-call wrapper pair from `tests/python/test_module_workflow_parity_suite.py` so module and pattern collection parity tests dispatch through one smaller file-local helper instead of keeping two near-identical wrappers over `getattr(..., case.helper)`.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines both duplicate collection-call wrappers:
  - `_call_module_collection_helper(...)`
  - `_call_pattern_collection_helper(...)`
- Replace that pair with one explicit shared helper, or a strictly smaller equivalent, that preserves the current call shapes:
  - module collection cases still call `helper(pattern, string, *extra_args)`;
  - pattern collection cases still call `helper(string, *extra_args)` on the already-compiled pattern object.
- Repoint the eight local collection parity call sites through the shared helper without changing the selected test buckets or parity assertions:
  - `test_module_split_collection_helpers_match_cpython()`
  - `test_pattern_split_collection_helpers_match_cpython()`
  - `test_module_findall_collection_helpers_match_cpython()`
  - `test_pattern_findall_collection_helpers_match_cpython()`
  - `test_module_finditer_collection_helpers_match_cpython()`
  - `test_module_finditer_collection_helpers_preserve_match_identity_like_cpython()`
  - `test_pattern_finditer_collection_helpers_match_cpython()`
  - `test_pattern_finditer_collection_helpers_preserve_match_identity_like_cpython()`
- Keep the cleanup structural and file-local:
  - do not widen this run into collection-case selectors, positional-indexlike helpers, owner-path publication helpers, manifests, harness modules, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_split_collection_helpers_match_cpython or pattern_split_collection_helpers_match_cpython or module_findall_collection_helpers_match_cpython or pattern_findall_collection_helpers_match_cpython or module_finditer_collection_helpers_match_cpython or module_finditer_collection_helpers_preserve_match_identity_like_cpython or pattern_finditer_collection_helpers_match_cpython or pattern_finditer_collection_helpers_preserve_match_identity_like_cpython'`
- `bash -lc "! rg -n '^def _call_module_collection_helper\\(|^def _call_pattern_collection_helper\\(' tests/python/test_module_workflow_parity_suite.py"`

## Notes
- `RBR-0996` was unreserved in the tracked queue/state files when this cleanup started:
  - `rg -n 'RBR-0996' ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no live reservation in this run.
- The target file was clean before editing:
  - `git status --short -- tests/python/test_module_workflow_parity_suite.py` returned no output.
- This cleanup stays adjacent to the earlier collection-helper selector cleanup and only removes the duplicate call wrapper layer that remained in the same parity suite.

## Completion
- Replaced `_call_module_collection_helper(...)` and `_call_pattern_collection_helper(...)` in `tests/python/test_module_workflow_parity_suite.py` with one shared `_call_collection_helper(...)`.
- Repointed the eight collection parity call sites through the shared helper without changing the surrounding parity assertions.
- Verified with the focused collection-helper pytest slice and the structural `rg` no-match check.
