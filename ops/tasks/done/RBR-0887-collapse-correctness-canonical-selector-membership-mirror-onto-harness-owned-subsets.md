# RBR-0887: Collapse correctness canonical selector membership mirror onto harness-owned subsets

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Delete the remaining handwritten canonical selector-membership mirror in `tests/python/test_fixture_parity_support_contract.py` by expressing the parser-parity and public-surface membership checks directly against the harness-owned nondefault selector table, so the correctness-side selector contract stops carrying a second filename registry after the adjacent benchmark-side cleanup in `RBR-0885`.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` stops maintaining `CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS` as a second selector-membership table:
  - remove `CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS`;
  - keep the existing parser-parity and public-surface selector membership contract covered on this owner path without introducing another mirrored tuple/list/map block;
  - drive that contract through `correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES` or an equally direct harness-owned selector-registry assertion path, while still proving the selected fixture paths preserve published-full-suite order; and
  - preserve the existing unknown-selector, published-full-suite inventory, declared-selector, and nondefault-selector parametrization invariants in substance.
- Keep this cleanup structural only:
  - do not change fixture contents, selector names, selector membership, `python/rebar_harness/correctness.py`, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirrored expectation table over adding another helper family or another test-only abstraction layer.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or canonical_published_subset_selectors_keep_explicit_membership_contract or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness import correctness

assert (
    correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
        correctness.PARSER_PARITY_FIXTURE_SELECTOR
    ]
    == correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES[
        correctness.PARSER_PARITY_FIXTURE_SELECTOR
    ]
)
assert (
    correctness._CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR[
        correctness.PUBLIC_SURFACE_FIXTURE_SELECTOR
    ]
    == correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES[
        correctness.PUBLIC_SURFACE_FIXTURE_SELECTOR
    ]
)
print("ok")
PY`
  - `bash -lc "! rg -n '^CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS =' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep the change limited to the correctness selector-contract owner test. Do not widen into a broader fixture-bundle rewrite, correctness-harness refactor, or benchmark-side cleanup in this run.
- Preserve the current published-full-suite order and the current parser-parity/public-surface selector memberships exactly; the point is to remove the duplicated contract table, not reinterpret either selector.

## Notes
- `RBR-0887` is the next available architecture task id in the current checkout:
  - `RBR-0886` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0886-catch-up-compiled-pattern-module-compile-ignorecase-rejection-named-group-boundary-pair.md`;
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues do not reserve `RBR-0887`; and
  - `/home/ubuntu/rebar/ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen, refine, or normalize first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup landed in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or canonical_published_subset_selectors_keep_explicit_membership_contract or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'` passes (`23 passed, 287 deselected`);
  - `bash -lc "! rg -n '^CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS =' tests/python/test_fixture_parity_support_contract.py"` now succeeds because the mirrored table is gone; and
  - the adjacent benchmark-side mirror removal already landed in `RBR-0885`, so this run closes the matching correctness-side follow-on rather than opening a new cleanup lane.

## Completion
- Removed `CANONICAL_PUBLISHED_SUBSET_SELECTOR_EXPECTATIONS` from `tests/python/test_fixture_parity_support_contract.py` and kept the parser-parity and public-surface membership contract asserted directly through `correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES`.
- Preserved the published-full-suite ordering check by asserting the selected canonical subset still resolves in published inventory order before matching the live selector registry and resolved fixture paths.
- Verified with the task-required focused pytest command, the direct Python registry assertions for the parser/public selectors, and the grep absence check for the deleted mirrored table.
