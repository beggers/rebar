# RBR-0626: Collapse the counted-repeat quantified-group parity suite onto the wider-ranged-repeat owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_counted_repeat_quantified_group_parity_suite.py` by moving its exact-repeat and ranged-repeat quantified-group coverage onto `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, so this counted-repeat lane has one owner suite instead of a detached 144-line module that repeats the same compile/module/pattern parity ladder already present on the wider-ranged-repeat surface.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- Delete `tests/python/test_counted_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` covers exactly the current twelve manifests carried by the two suites, and no more:
  - absorbed counted-repeat manifests:
    - `exact-repeat-quantified-group-workflows`
    - `ranged-repeat-quantified-group-workflows`
  - existing wider-ranged-repeat owner manifests:
    - `wider-ranged-repeat-quantified-group-workflows`
    - `broader-range-wider-ranged-repeat-quantified-group-workflows`
    - `wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
    - `wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
    - `broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`
    - `broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
    - `broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
    - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`
    - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
    - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
- One local bundle-spec ownership surface in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` carries the absorbed manifests instead of leaving a sibling suite behind:
  - the exact-repeat manifest keeps the current exact case-id set, pattern set `{r"a(bc){2}d", r"a(?P<word>bc){2}d"}`, and helper counts `{("compile", None): 2, ("module_call", "search"): 2, ("pattern_call", "fullmatch"): 2}`;
  - the ranged-repeat manifest keeps the current exact case-id set, pattern set `{r"a(bc){1,2}d", r"a(?P<word>bc){1,2}d"}`, and helper counts `{("compile", None): 2, ("module_call", "search"): 2, ("pattern_call", "fullmatch"): 2}`; and
  - both absorbed manifests stay `str`-only and do not grow bytes follow-ons, new bounded-window cases, new backtracking-trace tables, or another counted-repeat-only helper layer.
- The absorbed exact/ranged rows stay on the existing wider-suite parity path instead of reintroducing duplicate scaffolding:
  - compile metadata still runs through `compile_with_cpython_parity(...)`;
  - module-search parity still uses the same shared module-result assertions already present on the wider owner; and
  - pattern-fullmatch parity still uses the same shared compiled-pattern assertions already present on the wider owner.
- The current wider-ranged-repeat owner behavior stays intact outside the absorbed counted-repeat rows:
  - preserve the existing ten wider/broader/nested manifest ids, current bytes direct-follow-on anchors, bounded-pattern cases, direct-test bucket accounting, and backtracking-trace coverage;
  - keep `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, and the wider/nested broader-range supplemental bytes expectations explicit in the owner suite instead of moving them into a new helper module; and
  - do not broaden this cleanup into `tests/python/test_open_ended_quantified_group_parity_suite.py`, benchmark workload files, correctness fixtures, or report regeneration.
- Keep the cleanup local and ordinary:
  - prefer one real owner suite with file-local tables over another support module, registry layer, or import-only compatibility wrapper; and
  - do not leave `tests/python/test_counted_repeat_quantified_group_parity_suite.py` behind as a forwarding shell.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_wider_ranged_repeat_quantified_group_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES) == (
    "exact-repeat-quantified-group-workflows",
    "ranged-repeat-quantified-group-workflows",
    "wider-ranged-repeat-quantified-group-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-workflows",
    "wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_counted_repeat_quantified_group_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_wider_ranged_repeat_quantified_group_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES) == (
    "exact-repeat-quantified-group-workflows",
    "ranged-repeat-quantified-group-workflows",
    "wider-ranged-repeat-quantified-group-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-workflows",
    "wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_counted_repeat_quantified_group_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, correctness fixtures under `tests/conformance/fixtures/`, benchmark workloads, reports, Rust code, or `python/rebar/`.
- Keep the absorbed exact/ranged manifests `str`-only and fixture-backed. Do not turn this into a bytes-expansion task or a counted-repeat feature pass.
- Do not add a new shared helper module or a second quantified-group owner suite just to move the duplicate scaffolding somewhere else.

## Notes
- `RBR-0626` is the next available task id:
  - `rg -n "RBR-0626|RBR-0627|RBR-0628" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0626'` returned no matches before this file was added.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest dashboard cycle shows both task workers finishing at `done`, so the shared queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This task intentionally stays off the replacement-parity lane because the ready feature task `RBR-0625` already targets `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_counted_repeat_quantified_group_parity_suite.py` is `144` lines and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` is `1376` lines;
  - the detached counted-repeat suite currently carries only the two manifests `exact-repeat-quantified-group-workflows` and `ranged-repeat-quantified-group-workflows`; and
  - the wider owner already carries ten adjacent counted-repeat/alternation/conditional/backtracking manifests plus the shared compile/module/pattern parity ladders, direct-case bucket accounting, and bytes follow-on routing that the detached counted-repeat suite does not need to duplicate.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` passes (`1308 passed in 0.94s`);
  - the inline manifest-order probe above currently fails exactly on this cleanup with `AssertionError` because `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still starts at `wider-ranged-repeat-quantified-group-workflows` and does not yet absorb the exact/ranged manifests; and
  - `bash -lc "! rg --files tests/python | rg 'test_counted_repeat_quantified_group_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists.
