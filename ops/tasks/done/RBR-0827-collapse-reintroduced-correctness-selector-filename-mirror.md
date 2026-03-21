# RBR-0827: Collapse the reintroduced correctness selector filename mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the reintroduced `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` mirror from `tests/python/test_fixture_parity_support_contract.py`.
- Keep the correctness selector contract focused on live registry invariants, matching the lighter benchmark-selector pattern already used in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of maintaining another handwritten filename table.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` no longer defines or references:
  - `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS`;
  - `expected_filenames = _SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS[selector]`; or
  - `test_selector_filename_expectations_cover_all_nondefault_correctness_selectors()`.
- `test_shared_correctness_fixture_selectors_resolve_published_paths()` is rewritten to use live published-selector invariants instead of a duplicated filename table:
  - keep parametrization over every declared nondefault `*_FIXTURE_SELECTOR`;
  - keep `selected_paths` non-empty and duplicate-free;
  - keep every selected path under `CORRECTNESS_FIXTURES_ROOT`, on a real `.py` file, and inside the published full-suite selector inventory; and
  - assert the resolved selector order matches the published full-suite order for the selected subset, following the same `expected_ordered_subset` pattern already used by the benchmark selector contract.
- Preserve the remaining selector coverage in the same file:
  - keep `test_unknown_correctness_fixture_selector_raises_clear_error()`;
  - keep `test_declared_correctness_fixture_selectors_match_registry_keys()`;
  - keep `test_declared_nondefault_correctness_fixture_selectors_are_parametrized_once()`;
  - keep `test_published_full_suite_fixture_selector_matches_tracked_fixture_inventory()`; and
  - keep `test_published_full_suite_fixture_selector_preserves_explicit_manifest_order()`.
- Do not change `python/rebar_harness/correctness.py`, fixture modules under `tests/conformance/fixtures/`, benchmark files, reports, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector or published_full_suite_fixture_selector'`
  - `bash -lc "! rg -n '^_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS =|expected_filenames = _SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\[selector\\]|tuple\\(sorted\\(_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\)\\)' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_fixture_parity_support_contract.py`.
- Prefer deleting the reintroduced filename mirror over adding another helper, another selector table, or another import-only wrapper.

## Notes
- `RBR-0827` is free in the current checkout:
  - `rg -n 'RBR-0827|RBR-0828|RBR-0829|RBR-0830' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0827|^RBR-0828|^RBR-0829|^RBR-0830'` returned no conflicting task files in this run.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle completed architecture, feature work, cleanup, and reporting cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector or published_full_suite_fixture_selector'` currently passes (`26 passed, 263 deselected in 0.10s`);
  - `rg -n '^_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS =|expected_filenames = _SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\[selector\\]|tuple\\(sorted\\(_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\)\\)' tests/python/test_fixture_parity_support_contract.py` currently reports the active mirror at lines `89`, `818`, and `861`; and
  - the benchmark-side contract in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already proves the lighter ordered-subset invariant is sufficient for selector-path coverage, so this cleanup converges the correctness side onto the same architecture instead of inventing another pattern.
- This is a bounded follow-up to the earlier selector-table cleanup lineage, not a new feature:
  - `ops/tasks/done/RBR-0801-collapse-correctness-selector-expectation-table-onto-live-registry-invariants.md`
  - `ops/tasks/done/RBR-0803-collapse-benchmark-selector-expectation-table-onto-live-registry-invariants.md`

## Completion
- 2026-03-21: Removed `_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS` and the mirror-coverage test from `tests/python/test_fixture_parity_support_contract.py`, keeping the selector contract on live `rebar_harness.correctness` registry data instead of a second handwritten filename table.
- 2026-03-21: Rewrote `test_shared_correctness_fixture_selectors_resolve_published_paths()` to assert that each declared nondefault selector still resolves once through the live registry, remains non-empty and duplicate-free, stays within the published full-suite inventory, points at real `.py` fixture modules under `CORRECTNESS_FIXTURES_ROOT`, and still produces the expected published-order-normalized subset without maintaining a second filename mirror in the test file.
- 2026-03-21: Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'selector or published_full_suite_fixture_selector'`
  - `bash -lc "! rg -n '^_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS =|expected_filenames = _SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\[selector\\]|tuple\\(sorted\\(_SHARED_CORRECTNESS_SELECTOR_FILENAME_EXPECTATIONS\\)\\)' tests/python/test_fixture_parity_support_contract.py"`
- Follow-up noted: several selector rows in `python/rebar_harness/correctness.py` still encode their own explicit path order rather than the published full-suite order, so a future architecture cleanup can normalize those live selector rows if the harness wants the correctness-side contract to match the benchmark-side direct ordered-subset invariant exactly.
