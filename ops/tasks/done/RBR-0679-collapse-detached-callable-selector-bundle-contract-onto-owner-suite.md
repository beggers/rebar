# RBR-0679: Collapse the detached callable selector bundle contract onto the callable replacement owner suite

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Move the remaining callable-selector and published-bundle contract checks off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_callable_replacement_parity_suite.py`, so the callable replacement owner keeps selector membership, caller-selected bundle load order, and manifest-id lookup semantics beside `CALLABLE_FIXTURE_PATHS`, `FIXTURE_BUNDLES`, and `published_fixture_bundle_by_manifest_id(...)` instead of leaving that slice in a detached support-contract suite.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` becomes the sole owner for the callable-selector/published-bundle contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_callable_replacement_selector_tracks_published_callable_manifests(...)`;
  - absorb `test_published_fixture_bundle_loading_preserves_selector_path_order(...)`;
  - absorb `test_published_fixture_bundle_lookup_by_manifest_id_supports_success_and_clear_failures(...)`;
  - derive any new assertions from the existing callable owner data and helpers already on that file, including `CALLABLE_FIXTURE_PATHS`, `FIXTURE_BUNDLES`, `load_published_fixture_bundles(...)`, and `published_fixture_bundle_by_manifest_id(...)`, instead of adding another `*_support.py`, expanding `tests/python/conftest.py`, or moving this slice into a new shared helper layer; and
  - preserve the current callable-selector membership, reversed path-order behavior, missing-manifest-id error string, and duplicate-manifest-id error string exactly.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this callable-specific slice:
  - remove the three moved test functions above;
  - remove the `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` and `published_fixture_bundle_by_manifest_id` imports once they become unused; and
  - do not leave a renamed compatibility shell, second callable-selector contract block, or a detached manifest-id lookup probe beside the owner suite.
- The detached support file no longer mentions this callable-selector contract after the cleanup:
  - `tests/python/test_fixture_parity_support_contract.py` no longer contains `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`;
  - `tests/python/test_fixture_parity_support_contract.py` no longer contains `published_fixture_bundle_by_manifest_id`;
  - do not broaden into the generic selector inventory table, unknown-selector error coverage, mixed-text-model bundle loading, default fixture inventory coverage, or non-callable manifest-loader tests that still belong on the detached support-contract file.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, fixture manifests, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_callable_replacement_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_callable_replacement_selector_tracks_published_callable_manifests(",
    "def test_published_fixture_bundle_loading_preserves_selector_path_order(",
    "def test_published_fixture_bundle_lookup_by_manifest_id_supports_success_and_clear_failures(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'CALLABLE_REPLACEMENT_FIXTURE_SELECTOR|published_fixture_bundle_by_manifest_id|test_callable_replacement_selector_tracks_published_callable_manifests|test_published_fixture_bundle_loading_preserves_selector_path_order|test_published_fixture_bundle_lookup_by_manifest_id_supports_success_and_clear_failures' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached callable-selector contract seam, not to reinterpret callable replacement fixture selection, published bundle order, or manifest-id lookup semantics.
- Prefer the existing callable replacement owner and file-local assertions over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, manifest-loader, bundle-shape, parity-helper, and non-callable support coverage in place.

## Notes
- `RBR-0679` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0679|RBR-0680|RBR-0681|RBR-0682|RBR-0683|RBR-0684|RBR-0685" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0679*' -o -name 'RBR-0680*' -o -name 'RBR-0681*' -o -name 'RBR-0682*' -o -name 'RBR-0683*' -o -name 'RBR-0684*' -o -name 'RBR-0685*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in the live checkout aside from `.gitkeep`, `ops/tasks/blocked/` has no blocked task file, and the newest runtime task-worker runs both finished `done`;
  - `.rebar/runtime/dashboard.md` is lagging the live checkout because it still reports `Dirty worktree: true` while `git status --short` is empty, so queue and JSON state were cross-checked from the filesystem instead of trusting the stale dashboard alone; and
  - there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached callable-selector slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_callable_replacement_parity_suite.py` already imports `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`, `select_correctness_fixture_paths`, `load_published_fixture_bundles`, and `published_fixture_bundle_by_manifest_id`, defines `CALLABLE_FIXTURE_PATHS`, loads `FIXTURE_BUNDLES`, and uses manifest-id lookup on the callable owner path;
  - `tests/python/test_fixture_parity_support_contract.py` still carries the three callable-specific tests named in Acceptance plus the now-detached `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` and `published_fixture_bundle_by_manifest_id` imports;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2151 passed in 1.57s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`123 passed in 0.18s`);
  - the inline source probe in Acceptance currently reports `needs-move`, because the callable owner does not yet carry those three moved definitions; and
  - the final `rg` command in Acceptance currently fails exactly on this cleanup because the detached support file still contains the callable-selector import, manifest-id lookup helper import, and the three target test definitions.
- This simplification matches the current information flow:
  - the callable replacement owner already defines the selector-derived path list and published bundle load path that the detached tests exercise; and
  - the support-contract file is only keeping a second callable-selector contract seam alive beside that owner.

## Completion
- 2026-03-19: Moved the callable-selector membership, caller-selected bundle-order, and manifest-id lookup contract tests onto `tests/python/test_callable_replacement_parity_suite.py`, deriving the moved coverage from the owner suite's existing `CALLABLE_FIXTURE_PATHS`, `FIXTURE_BUNDLES`, `load_published_fixture_bundles(...)`, and `published_fixture_bundle_by_manifest_id(...)`.
- 2026-03-19: Removed the detached callable-specific coverage and the now-unused `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` / `published_fixture_bundle_by_manifest_id` imports from `tests/python/test_fixture_parity_support_contract.py`, leaving the remaining generic selector, bundle-shape, and manifest-loader coverage in place.

## Verification
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` (`2154 passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`120 passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` (`ok`)
- 2026-03-19: `bash -lc "! rg -n 'CALLABLE_REPLACEMENT_FIXTURE_SELECTOR|published_fixture_bundle_by_manifest_id|test_callable_replacement_selector_tracks_published_callable_manifests|test_published_fixture_bundle_loading_preserves_selector_path_order|test_published_fixture_bundle_lookup_by_manifest_id_supports_success_and_clear_failures' tests/python/test_fixture_parity_support_contract.py"` (no matches)
