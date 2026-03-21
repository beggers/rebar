# RBR-0879: Collapse duplicated selector-introspection helpers onto scorecard_io

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the last duplicated "discover declared selector constants from a module" helper bodies from the benchmark and correctness selector-contract owners, so both suites read those declarations through one shared utility instead of each carrying the same `vars(module)` plus suffix filter logic locally.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/scorecard_io.py` becomes the single shared owner of selector-introspection for these contract tests:
  - add one small helper that takes a module object plus a name suffix and returns the declared string-valued constants whose names end with that suffix;
  - keep the current contract shape that both tests rely on:
    - include only attributes whose values are `str`;
    - preserve the module declaration order exposed by `vars(module)` instead of sorting; and
    - keep the helper generic at the "declared string constants by suffix" level instead of introducing another selector registry, filesystem scan, or harness-specific wrapper family.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops defining `_declared_benchmark_manifest_selectors()`:
  - drive the existing nondefault-selector parametrization and `test_declared_benchmark_manifest_selectors_match_registry_keys()` through the shared helper;
  - keep the built-native smoke selector covered on the current owner path;
  - keep the existing published-subset ordering, membership, and registry-key invariants unchanged in substance; and
  - do not broaden into anchor cleanup, manifest inventory rewrites, or scorecard-summary refactors in this run.
- `tests/python/test_fixture_parity_support_contract.py` stops defining `_declared_correctness_fixture_selectors()`:
  - drive `test_declared_correctness_fixture_selectors_match_registry_keys()` through the shared helper;
  - keep `_declared_nondefault_correctness_fixture_selectors()` only if it remains a thin derivation from that shared helper for the existing parametrization, or inline that derivation directly if it becomes clearer;
  - keep the current nondefault-selector parametrization, published-path subset checks, and registry-key invariants unchanged in substance; and
  - do not broaden into fixture-bundle helper cleanup, parity-suite rewrites, or correctness-manifest inventory refactors in this run.
- Keep this cleanup structural only:
  - do not change selector names, selector memberships, workload or fixture contents, harness reports, README copy, or tracked project-state prose; and
  - do not add a new test-only support module when `python/rebar_harness/scorecard_io.py` already owns the adjacent shared selector/report utilities.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or canonical_benchmark_manifest_subset_selectors_keep_membership_contract or declared_benchmark_manifest_selectors_match_registry_keys'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'`
  - `bash -lc "! rg -n '^def _declared_(benchmark_manifest|correctness_fixture)_selectors\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Prefer deleting the duplicated local helper bodies over adding another selector abstraction layer or another mirrored expectation table.
- Keep the change limited to selector-introspection plumbing for these two contract owners. Do not widen into selector-registry redesign, benchmark/correctness harness behavior changes, or another shared helper sweep.

## Notes
- `RBR-0879` is the next available architecture task id in the current checkout:
  - `RBR-0878` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queues do not reserve `RBR-0879`; and
  - `ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or canonical_benchmark_manifest_subset_selectors_keep_membership_contract or declared_benchmark_manifest_selectors_match_registry_keys'` currently passes (`3 passed, 473 deselected in 0.12s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'` currently passes (`2 passed, 296 deselected in 0.07s`);
  - `bash -lc "rg -n '^def _declared_(benchmark_manifest|correctness_fixture)_selectors\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py"` currently reports exactly the two remaining duplicated helper definitions; and
  - `python/rebar_harness/scorecard_io.py` already owns the adjacent shared selector/report utilities used by both harnesses, so consolidating this last reflection helper there reduces duplication without creating another owner module.

## Completion Note
- 2026-03-21: Added `declared_string_constants_by_suffix(...)` to `python/rebar_harness/scorecard_io.py` as the shared owner for suffix-based module constant discovery while preserving `vars(module)` declaration order and filtering to string-valued attributes only.
- Rewired `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/python/test_fixture_parity_support_contract.py` to use that shared helper, deleted both duplicated local selector-introspection helpers, and kept the existing nondefault-selector parametrization plus registry-key invariants unchanged.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or canonical_benchmark_manifest_subset_selectors_keep_membership_contract or declared_benchmark_manifest_selectors_match_registry_keys'` (`3 passed, 473 deselected`)
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or correctness_selector_subset_helper_keeps_fixture_specific_missing_filename_error or declared_correctness_fixture_selectors_match_registry_keys or declared_nondefault_correctness_fixture_selectors_are_parametrized_once'` (`22 passed, 276 deselected`)
  - `bash -lc "! rg -n '^def _declared_(benchmark_manifest|correctness_fixture)_selectors\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_fixture_parity_support_contract.py"` (passed with no matches)
