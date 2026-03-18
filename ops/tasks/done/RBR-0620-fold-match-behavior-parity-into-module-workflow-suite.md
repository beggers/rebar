# RBR-0620: Fold the detached match-behavior parity suite into the module workflow suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_match_behavior_parity_suite.py` by moving its basic module-call parity coverage onto `tests/python/test_module_workflow_parity_suite.py`, so the Python-facing module workflow surface has one owner suite instead of a second detached smoke module that repeats the same fixture-contract and match-result ladders.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- Delete `tests/python/test_match_behavior_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` absorbs the current `match-behavior-smoke` coverage while preserving its existing `module-workflow-surface` coverage exactly:
  - keep the current `module-workflow-surface` selected case ids, expected patterns, expected `(operation, helper)` counts, direct test buckets, verbose compile workflows, compiled-pattern helper workflows, cache/purge workflows, and escape workflows unchanged; and
  - add `match-behavior-smoke` to the same local owner-suite spec surface instead of creating another helper module, registry, or second owner file.
- The combined suite preserves the published `match-behavior-smoke` fixture contract exactly:
  - keep the six selected case ids now published by `tests/python/test_match_behavior_parity_suite.py`:
    - `search-str-success-literal`
    - `search-str-no-match`
    - `match-str-success-literal`
    - `match-str-no-match`
    - `fullmatch-str-success-literal`
    - `fullmatch-bytes-success-literal`
  - keep the expected pattern set `{"abc", "ab", "123", b"123"}`;
  - keep the expected `(operation, helper)` counts `{("module_call", "search"): 2, ("module_call", "match"): 2, ("module_call", "fullmatch"): 2}`; and
  - keep the expected text models `{"bytes", "str"}`.
- The combined suite preserves the current match-behavior supplemental bytes follow-ons exactly:
  - keep the same five `SUPPLEMENTAL_BYTES_CASES` rows and their current `(helper, matches)` matrix:
    - `("search", True)`
    - `("search", False)`
    - `("match", True)`
    - `("match", False)`
    - `("fullmatch", False)`
  - keep those rows bytes-only and local to `tests/python/test_module_workflow_parity_suite.py`; and
  - do not widen them into new fixture rows, bytes pattern helpers, or another support abstraction.
- The absorbed match-behavior assertions stay exactly on the current parity path:
  - keep module-call execution against both backends through `getattr(backend, case.helper)(...)` versus `getattr(re, case.helper)(...)`;
  - keep `assert_match_result_parity(..., check_regs=True)`;
  - keep `assert_match_convenience_api_parity(...)` only when CPython produces a match; and
  - keep the current matched-result follow-ons that assert the `group(0)` value type, `observed.re.pattern`, and `observed.string`.
- The combined suite keeps one ordinary local ownership surface:
  - prefer one ordered `SELECTED_CASE_BUNDLE_SPECS` table plus local `match-behavior` case tables inside `tests/python/test_module_workflow_parity_suite.py`;
  - do not leave an import-only wrapper or compatibility shell at `tests/python/test_match_behavior_parity_suite.py`; and
  - do not add another file-local indirection layer under `tests/python/fixture_parity_support.py`.
- Keep scope structural only:
  - do not change correctness fixtures, benchmark files, reports, Rust code, `python/rebar/`, or the current `module-workflow-surface` behavior; and
  - do not broaden this cleanup into `tests/python/test_public_surface_parity_suite.py`, `tests/python/test_literal_flag_parity_suite.py`, or another multi-suite module-surface merge.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(spec.expected_manifest_id for spec in mod.SELECTED_CASE_BUNDLE_SPECS) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_match_behavior_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(spec.expected_manifest_id for spec in mod.SELECTED_CASE_BUNDLE_SPECS) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_match_behavior_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, selected case ids, expected pattern sets, helper routing, or direct match-result semantics.
- Preserve the current `match-behavior-smoke` bytes supplemental payloads exactly; the point is to remove the detached owner file, not to reinterpret the bytes follow-on surface.
- Do not replace the deleted suite with an import-only wrapper or move this coverage into a new support module.

## Notes
- `RBR-0620` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve `RBR-0620` or a later concrete architecture follow-on;
  - `ops/tasks/ready/` currently stops at `RBR-0619`; and
  - `ops/tasks/in_progress/` and `ops/tasks/blocked/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_match_behavior_parity_suite.py` is `193` lines and `tests/python/test_module_workflow_parity_suite.py` is `887` lines;
  - both files already carry the same fixture-contract / frontier / direct-bucket scaffolding shape through `assert_fixture_bundle_contract(...)`, `assert_fixture_bundle_tracks_published_case_frontier(...)`, and `assert_direct_test_case_id_buckets_cover_selected_frontier(...)`; and
  - `tests/python/test_match_behavior_parity_suite.py` repeats the same module-call parity ladder already used elsewhere in the module workflow surface via `assert_match_result_parity(...)` plus `assert_match_convenience_api_parity(...)`, but on a detached six-case smoke bundle that belongs on the module workflow owner path.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_match_behavior_parity_suite.py tests/python/test_module_workflow_parity_suite.py` passes (`227 passed in 0.19s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` manifest-order probe above currently fails exactly on this cleanup with `AssertionError` because `tests/python/test_module_workflow_parity_suite.py` still declares only `module-workflow-surface`; and
  - `bash -lc "! rg --files tests/python | rg 'test_match_behavior_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists.

## Completion Note
- 2026-03-18: Folded the `match-behavior-smoke` bundle, its direct-bucket checks, and the five local supplemental bytes follow-ons into `tests/python/test_module_workflow_parity_suite.py`, then deleted `tests/python/test_match_behavior_parity_suite.py`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`227 passed in 0.21s`), the manifest-order probe, and the live `rg --files` deletion check.
