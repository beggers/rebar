# RBR-0829: Collapse helper-backed correctness selector ordering onto published subsets

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the remaining local ordering drift from the helper-backed correctness selectors in `python/rebar_harness/correctness.py`.
- Keep those selectors derived from the canonical `published-full-suite` fixture order instead of quietly carrying a second suite-local ordering contract that the current support test does not catch.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`
- Update only the affected parity suites below if the selector-order normalization requires local expectation refreshes:
  - `tests/python/test_quantified_alternation_parity_suite.py`
  - `tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `tests/python/test_branch_local_backreference_parity_suite.py`
  - `tests/python/test_callable_replacement_parity_suite.py`
  - `tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` no longer alphabetizes helper-backed selector subsets away from the canonical published order:
  - replace the current `_sorted_published_fixture_subset(...)` behavior with a helper whose returned tuple preserves the exact `PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR` order for the selected filenames; and
  - keep the helper bounded to filename validation plus ordered-subset derivation from the published selector instead of introducing another registry, another expectation table, or filesystem discovery.
- The following helper-backed selectors resolve in exact published-full-suite order after the cleanup:
  - `QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR`
  - `CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR`
  - `GROUPED_REPLACEMENT_FIXTURE_SELECTOR`
  - `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR`
  - `BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR`
  - `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`
  - `OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR`
  - `OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR`
- `tests/python/test_fixture_parity_support_contract.py` gains a targeted selector-order contract for that helper-backed set:
  - keep the existing broad registry/path coverage green for all declared nondefault correctness selectors;
  - add or tighten a focused assertion that, for the helper-backed selector set above, `select_correctness_fixture_paths(selector)` is exactly the ordered subset of `select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)` filtered to the selector's resolved paths; and
  - do not broaden this task into the still-manual selector rows (`PARSER_PARITY_FIXTURE_SELECTOR`, `CONDITIONAL_GROUP_EXISTS_FIXTURE_SELECTOR`, `MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR`, `PUBLIC_SURFACE_FIXTURE_SELECTOR`, `GROUPED_CAPTURE_FIXTURE_SELECTOR`) beyond any minimal refactor needed to keep the support contract legible.
- If any of the affected parity suites rely on the old helper-backed local ordering, refresh only the order-sensitive expectations needed to keep them aligned with the canonical published subset order; do not change fixture contents, manifest ids, selected case ids, or frontier scope.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    GROUPED_REPLACEMENT_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR,
    WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR,
)

selectors = (
    QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR,
    CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
    GROUPED_REPLACEMENT_FIXTURE_SELECTOR,
    WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
    BRANCH_LOCAL_BACKREFERENCE_FIXTURE_SELECTOR,
    CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_REPLACEMENT_TEMPLATE_FIXTURE_SELECTOR,
    OPEN_ENDED_QUANTIFIED_GROUP_FIXTURE_SELECTOR,
)
published = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
]
for selector in selectors:
    actual = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector]
    expected = tuple(name for name in published if name in set(actual))
    assert actual == expected, f"{selector}: {actual!r} != {expected!r}"
print("ok")
PY`

## Constraints
- Keep this cleanup structural. Do not edit fixture manifests under `tests/conformance/fixtures/`, reports, README copy, benchmark files, or tracked project-state prose.
- Prefer deleting misleading ordering logic over layering another helper or selector expectation table on top of it.
- Keep the task bounded to the helper-backed selector family listed above; leave the remaining manual selector-order normalization for a separate follow-up if it is still needed.

## Notes
- `RBR-0829` is free in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only `RBR-0828` on the active frontier in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0829|^RBR-0830|^RBR-0831'` returned no conflicting task files in this run.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed architecture, architecture-implementation, feature work, cleanup, and reporting cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is live in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or declared_correctness_fixture_selectors_match_registry_keys or published_full_suite_fixture_selector'` currently passes (`23 passed, 265 deselected in 0.10s`), which shows the support contract is not catching selector-order drift today;
  - the helper-backed selector probe from Acceptance currently fails exactly on ordering drift, starting with `quantified-alternation`;
  - a live probe over `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR` reports `11` nondefault selector mismatches against canonical published order, of which the eight selectors scoped in this task are all helper-backed; and
  - the suite verification slice named above is already green in the current checkout:
    - `tests/python/test_quantified_alternation_parity_suite.py` (`778 passed`)
    - `tests/python/test_open_ended_quantified_group_parity_suite.py` (`3902 passed`)
    - `tests/python/test_branch_local_backreference_parity_suite.py` (`561 passed`)
    - `tests/python/test_callable_replacement_parity_suite.py` (`2747 passed`)
    - `tests/python/test_fixture_backed_replacement_parity_suite.py` (`1166 passed`)
    - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`1341 passed`)
- This task is the direct bounded follow-up to the note left in `ops/tasks/done/RBR-0827-collapse-reintroduced-correctness-selector-filename-mirror.md`: the correctness-side support contract now runs on live registry invariants, but the helper-backed selector rows themselves still encode a different local order than the canonical published subset.
