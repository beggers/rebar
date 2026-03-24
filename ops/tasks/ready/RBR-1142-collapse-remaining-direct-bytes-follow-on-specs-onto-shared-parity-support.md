# RBR-1142: Collapse remaining direct-bytes follow-on specs onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the last suite-local direct-bytes follow-on spec wrappers from the parity owners by routing both `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_branch_local_backreference_parity_suite.py` through one shared spec surface on `tests/python/fixture_parity_support.py` instead of keeping three near-duplicate local dataclasses alive beside the already-landed grouped-quantified helper path.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- Reuse `tests/python/fixture_parity_support.py` as the only shared home for the remaining direct-bytes follow-on spec shape:
  - either extend `GroupedQuantifiedBytesSurfaceSpec` or land a strictly smaller equivalent on that same file;
  - cover the fields both remaining suites still duplicate today: `bundle`, `cases`, optional `follow_on_id`, expected operation/helper counts, expected published `module search` texts by pattern, and expected published `pattern fullmatch` texts by pattern; and
  - if the branch-local suite still needs unsupported-backend expectations, keep that capability on the shared spec surface instead of another owner-local wrapper.
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining the suite-local `QuantifiedAlternationDirectBytesFollowOnSpec` dataclass and routes `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` through the shared parity-support spec surface instead.
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining both suite-local direct-bytes wrapper dataclasses:
  - remove `BranchLocalBackreferenceBytesFollowOnCase` in favor of the shared `SupplementalCase` payload already exported by `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent already on that file; and
  - remove `BranchLocalBytesFollowOnSpec` in favor of the same shared spec surface used by quantified alternation.
- Preserve the current owner-local frontier declarations and behavior exactly:
  - keep the existing bytes case tables, manifest pairings, follow-on ids, selected fixture frontiers, published search/fullmatch text expectations, and pytest ids unchanged;
  - preserve the branch-local unsupported-backend assertions exactly if they still apply; and
  - do not move the owner-local case tables, generated parity specs, or non-direct-bytes helpers into the support module.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused shared-surface coverage instead of adding another owner-specific contract block:
  - one check proves the shared spec preserves `follow_on_id` and bundle identity for a quantified-alternation-style direct-bytes surface;
  - one check proves the same shared spec preserves expected operation counts plus published bytes text maps for a branch-local-style direct-bytes surface; and
  - one check proves the shared case payload still carries optional unsupported-backend metadata through the direct-bytes path.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_bytes_follow_on'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py -k 'direct_bytes_follow_on'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'grouped_quantified_bytes_surface_spec'`

## Constraints
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting the redundant owner-local dataclasses over adding another helper layer that merely renames the same payload shape.
- Preserve current manifest ids, case ids, bytes follow-on routing, published text expectations, and unsupported-backend behavior exactly.

## Notes
- `RBR-1142` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in this run;
  - the highest live task id across `ops/tasks/done/` and `ops/tasks/blocked/` is `1141`; and
  - `rg -n "RBR-1142|RBR-1143|RBR-1144" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no live reserved future task id in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and cross-file:
  - `tests/python/fixture_parity_support.py` already exports `SupplementalCase` and `GroupedQuantifiedBytesSurfaceSpec` for the open-ended and wider-ranged grouped-quantified owners;
  - `tests/python/test_quantified_alternation_parity_suite.py` still defines `QuantifiedAlternationDirectBytesFollowOnSpec` only to hold `follow_on_id`, `bundle`, and `cases`; and
  - `tests/python/test_branch_local_backreference_parity_suite.py` still defines `BranchLocalBackreferenceBytesFollowOnCase` plus `BranchLocalBytesFollowOnSpec` even though their payload shape is already materially the same shared direct-bytes surface.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_bytes_follow_on'` returned `181 passed, 597 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py -k 'direct_bytes_follow_on'` returned `146 passed, 415 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'grouped_quantified_bytes_surface_spec'` returned `2 passed, 413 deselected`.
