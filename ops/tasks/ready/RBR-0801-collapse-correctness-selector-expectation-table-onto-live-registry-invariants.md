# RBR-0801: Collapse the correctness selector expectation table onto live registry invariants

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the mirrored selector-filename table from `tests/python/test_fixture_parity_support_contract.py`; `SELECTOR_EXPECTATION_TABLE` and `SELECTOR_EXPECTATIONS` currently restate the same nondefault selector filenames that `python/rebar_harness/correctness.py` already owns in `_CORRECTNESS_FIXTURE_FILENAMES_BY_SELECTOR`.
- Keep the selector contract coverage focused on durable invariants: declared selector constants, membership in the published full-suite inventory, published-order preservation, and real fixture-path validation, instead of maintaining a second handwritten filename registry in the test file.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` no longer defines or references:
  - `SELECTOR_EXPECTATION_TABLE`; or
  - `SELECTOR_EXPECTATIONS`.
- The selector contract coverage in `tests/python/test_fixture_parity_support_contract.py` still proves the shared correctness selectors behave as expected, but without a second mirrored filename registry:
  - every declared nondefault `*_FIXTURE_SELECTOR` exported by `python/rebar_harness/correctness.py` is still exercised exactly once;
  - `select_correctness_fixture_paths(selector)` still resolves to a non-empty, duplicate-free, published-order-preserving subset of `select_correctness_fixture_paths(PUBLISHED_FULL_SUITE_FIXTURE_SELECTOR)` for each exercised nondefault selector;
  - every resolved path still stays under `CORRECTNESS_FIXTURES_ROOT`, points at a real `.py` fixture module, and remains part of the published full-suite selector inventory; and
  - the existing unknown-selector and declared-selector-registry assertions stay intact.
- Preserve the current higher-signal full-suite inventory coverage in the same file:
  - keep `test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory()` and `test_published_full_suite_fixture_selector_preserves_explicit_manifest_order()` asserting against `DEFAULT_FIXTURE_PATHS`;
  - do not change `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, benchmark files, reports, README copy, or tracked project-state prose; and
  - do not broaden into benchmark selector cleanup in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` during this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector or published_full_suite_fixture_selector'`
  - `bash -lc "! rg -n '^(SELECTOR_EXPECTATION_TABLE|SELECTOR_EXPECTATIONS) =' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_fixture_parity_support_contract.py`.
- Prefer deleting the mirrored selector table over adding another shared selector helper, another duplicated filename registry, or another import-only wrapper.

## Notes
- `RBR-0801` is free in the current checkout:
  - `rg -n "RBR-0801|RBR-0802|RBR-0803" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returned no reserved or queued `RBR-0801`-series matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0801|^RBR-0802|^RBR-0803'` returned no conflicting live task files.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector or published_full_suite_fixture_selector'` currently passes (`17 passed, 238 deselected in 0.09s`);
  - `rg -n '^(SELECTOR_EXPECTATION_TABLE|SELECTOR_EXPECTATIONS) =' tests/python/test_fixture_parity_support_contract.py` currently reports only this file (`82:SELECTOR_EXPECTATION_TABLE = (` and `233:SELECTOR_EXPECTATIONS = tuple(`); and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_fixture_parity_support_contract as mod
for selector, expected_filenames, _ in mod.SELECTOR_EXPECTATION_TABLE:
    resolved = tuple(path.name for path in mod.select_correctness_fixture_paths(selector))
    assert resolved == expected_filenames, (selector, resolved, expected_filenames)
print("ok")
PY` currently passes (`ok`), showing the handwritten table is a direct mirror of live selector resolution rather than an independent contract source.
- This follows the same post-JSON simplification direction as the recent parity-harness sidecar removals, but keeps scope tighter than the remaining benchmark-selector duplication by deleting the largest live filename mirror first.
