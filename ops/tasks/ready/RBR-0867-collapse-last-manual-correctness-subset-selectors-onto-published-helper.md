# RBR-0867: Collapse the last manual correctness subset selectors onto the published helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the last two nondefault correctness selector rows in `python/rebar_harness/correctness.py` that still hand-maintain raw filename tuples even though they already resolve to the canonical `published-full-suite` order.
- Leave the correctness harness with one rule for every nondefault selector: published-subset selectors derive from `_published_fixture_subset(...)` instead of mixing helper-backed rows with two manual exceptions.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` stops spelling these selector rows as raw tuple literals:
  - `PARSER_PARITY_FIXTURE_SELECTOR`
  - `PUBLIC_SURFACE_FIXTURE_SELECTOR`
- Replace those two rows with `_published_fixture_subset(...)` and keep their resolved membership and order unchanged:
  - `select_correctness_fixture_paths(PARSER_PARITY_FIXTURE_SELECTOR)` still resolves to `parser_matrix.py` followed by `conditional_group_exists_assertion_diagnostics.py`;
  - `select_correctness_fixture_paths(PUBLIC_SURFACE_FIXTURE_SELECTOR)` still resolves to `public_api_surface.py`, `exported_symbol_surface.py`, and `pattern_object_surface.py` in that order.
- Keep scope bounded to this cleanup:
  - do not change `PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR`;
  - do not add another selector helper, another selector registry, or filesystem-discovery logic; and
  - do not change fixture contents, selected case ids, benchmark manifests, reports, README copy, or tracked project-state prose.
- Any adjacent test edits stay limited to the files in Deliverables and only refresh expectations that were coupled to the old raw-tuple spelling.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py::test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_parser_matrix_parity_suite.py::test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_public_surface_parity_suite_stays_aligned_with_published_fixtures tests/python/test_module_workflow_parity_suite.py::test_public_surface_parity_suite_tracks_published_case_frontier`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    PARSER_PARITY_FIXTURE_SELECTOR,
    PUBLIC_SURFACE_FIXTURE_SELECTOR,
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR,
    _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR,
)

published = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
    PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR
]
for selector in (PARSER_PARITY_FIXTURE_SELECTOR, PUBLIC_SURFACE_FIXTURE_SELECTOR):
    actual = _CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[selector]
    expected = tuple(name for name in published if name in set(actual))
    assert actual == expected, f"{selector}: {actual!r} != {expected!r}"
print("ok")
PY`
  - `bash -lc "! rg -n '^\\s*(PARSER_PARITY_FIXTURE_SELECTOR|PUBLIC_SURFACE_FIXTURE_SELECTOR): \\(' python/rebar_harness/correctness.py"`

## Constraints
- Keep this cleanup structural. The point is to delete the last manual nondefault correctness selector exceptions, not to widen parser parity, public-surface coverage, or selector semantics.
- Prefer deleting the exceptional raw tuples over layering another special-case expectation on top of them.

## Notes
- `RBR-0867` is the next available architecture task id in the current checkout:
  - `RBR-0866` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0867`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This is the direct post-`RBR-0831` correctness-harness follow-on still left in the checkout:
  - `RBR-0829` normalized the helper-backed selector rows onto canonical published order;
  - `RBR-0831` normalized the remaining order-sensitive manual selector families but explicitly left `PARSER_PARITY_FIXTURE_SELECTOR` and `PUBLIC_SURFACE_FIXTURE_SELECTOR` as the two remaining manual nondefault rows; and
  - both selectors already satisfy the live published-order invariant in the current checkout, so the remaining work is purely deleting the manual tuple spelling rather than changing behavior.
- Current probes confirm the task is concrete and isolated:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector'` currently passes (`24 passed, 273 deselected in 0.10s`);
  - the parser/public-surface parity checks named in Acceptance currently pass (`2 passed` and `4 passed`);
  - the published-order probe in Acceptance currently prints `ok`; and
  - `bash -lc "! rg -n '^\\s*(PARSER_PARITY_FIXTURE_SELECTOR|PUBLIC_SURFACE_FIXTURE_SELECTOR): \\(' python/rebar_harness/correctness.py"` currently fails exactly on this cleanup because those two raw tuple rows still exist.
