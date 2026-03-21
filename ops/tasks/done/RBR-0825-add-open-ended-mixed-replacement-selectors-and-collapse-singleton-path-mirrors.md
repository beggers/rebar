## RBR-0825: Add open-ended mixed replacement selectors and collapse singleton path mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Delete the remaining singleton `selector_fixture_paths=(bundle.manifest.path,)` mirrors from `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Keep the two published mixed-text open-ended replacement owner manifests anchored to the shared correctness selector registry instead of restating their paths locally inside contract tests.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exports two dedicated selectors for the remaining singleton mixed-text replacement manifests:
  - add `NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR = "nested-broader-range-open-ended-replacement"`; and
  - add `NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR = "nested-broader-range-open-ended-conditional-replacement"`.
- Register those selectors in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` so `select_correctness_fixture_paths(...)` resolves exactly:
  - `NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR` -> `("nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",)`
  - `NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR` -> `("nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py",)`
- `tests/python/test_fixture_backed_replacement_parity_suite.py` no longer hard-codes singleton `selector_fixture_paths` tuples from bundle paths in the three mixed-text contract tests:
  - import and use the two new selectors plus `select_correctness_fixture_paths(...)`;
  - replace the direct tuple mirror at the broader-range pending-bytes contract;
  - replace the direct tuple mirror at the mixed conditional pending-bytes contract; and
  - replace the direct tuple mirror at the broader-range mixed-contract test.
- Preserve the current contract behavior after the path-mirror removal:
  - keep `MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE` anchored to manifest id `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows`;
  - keep `BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE` anchored to manifest id `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows`; and
  - keep all three contract tests selecting the same published case ids, uncovered bytes follow-on case ids, and helper-count expectations they assert today.
- `tests/python/test_fixture_parity_support_contract.py` treats both new selectors as first-class shared registry entries:
  - extend `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` with the exact singleton filename tuples for both selectors; and
  - keep the declared-selector coverage assertions green without adding a second selector registry or a suite-local expectation table.
- Do not broaden this cleanup into fixture manifests under `tests/conformance/fixtures/`, callable replacement suites, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n 'BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE\\.manifest\\.path|MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE\\.manifest\\.path' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR,
    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_fixture_backed_replacement_parity_suite as mod

replacement_paths = select_correctness_fixture_paths(
    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR
)
conditional_paths = select_correctness_fixture_paths(
    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR
)

assert tuple(path.name for path in replacement_paths) == (
    "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_replacement_workflows.py",
)
assert tuple(path.name for path in conditional_paths) == (
    "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_replacement_workflows.py",
)
assert (
    mod.BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE.manifest.path,
) == replacement_paths
assert (mod.MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE.manifest.path,) == conditional_paths
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `python/rebar_harness/correctness.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `tests/python/test_fixture_parity_support_contract.py`.
- Prefer deleting the remaining singleton bundle-path mirrors over adding another suite-local wrapper, another manifest-id table, or another helper module.

## Notes
- `RBR-0825` is free in the current checkout:
  - `rg -n 'RBR-0825|RBR-0826|RBR-0827|RBR-0828|RBR-0829' ops/state/backlog.md ops/state/current_status.md ops/tasks` returned only historical mentions inside completed task notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1166 passed in 0.88s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`287 passed in 0.36s`);
  - `rg -n 'BROADER_RANGE_OPEN_ENDED_MIXED_TEXT_REPLACEMENT_BUNDLE\\.manifest\\.path|MIXED_TEXT_MODEL_REPLACEMENT_BUNDLE\\.manifest\\.path' tests/python/test_fixture_backed_replacement_parity_suite.py` currently returns the three remaining singleton path mirrors at lines `1827`, `1891`, and `1954`; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
try:
    from rebar_harness.correctness import (
        NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
        NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR,
    )
except Exception as exc:
    print(type(exc).__name__, exc)
PY` currently fails with `ImportError`, which is the exact cleanup this task is meant to land.
- This cleanup follows the same selector-first simplification path as the recent parity-suite mirror removals:
  - `ops/tasks/done/RBR-0821-add-collection-replacement-selector-and-collapse-singleton-fixture-loads.md`
  - `ops/tasks/done/RBR-0823-add-surface-selectors-and-collapse-module-workflow-owner-paths.md`

## Completion
- Added `NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR` and `NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR` to `python/rebar_harness/correctness.py`, and registered both as first-class shared selector entries with their exact singleton published fixture filenames.
- Replaced the three remaining singleton `selector_fixture_paths=(bundle.manifest.path,)` mirrors in `tests/python/test_fixture_backed_replacement_parity_suite.py` with `select_correctness_fixture_paths(...)` calls against the new shared selectors, preserving the existing manifest ids, selected case ids, pending-bytes coverage, and helper-count assertions.
- Extended `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` in `tests/python/test_fixture_parity_support_contract.py` so the shared selector contract covers both new registry entries.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` (`1166 passed`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`289 passed`), the required `rg` absence check (no matches), and the selector-path probe from Acceptance (`ok`).
