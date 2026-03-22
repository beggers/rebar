# RBR-0891: Collapse residual nondefault selector-enumeration mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the remaining owner-test selector enumeration mirrors where tests discover nondefault correctness or benchmark selectors by scanning module constants instead of iterating the harness-owned selector tables directly, so the selector contracts keep one live membership source after `RBR-0885`, `RBR-0887`, and `RBR-0889`.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` stops maintaining a second nondefault-selector inventory through `_declared_nondefault_correctness_fixture_selectors()`:
  - remove `_declared_nondefault_correctness_fixture_selectors()`;
  - drive `test_shared_correctness_fixture_selectors_resolve_published_paths` directly from `correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES` or another equally direct harness-owned selector-table path;
  - keep `test_declared_nondefault_correctness_fixture_selectors_are_parametrized_once` proving the declared `*_FIXTURE_SELECTOR` constants still match the nondefault selector inventory; and
  - preserve the current selector order, selector membership, published-order assertions, and path invariants in substance.
- `tests/conformance/test_combined_correctness_scorecards.py` stops deriving the nondefault correctness selector list through `declared_string_constants_by_suffix(...)` inside `test_shared_correctness_fixture_selectors_resolve_published_subset_invariants`:
  - iterate that shared-subset contract directly from the harness-owned nondefault selector table instead of rescanning module constants;
  - keep `test_declared_correctness_fixture_selectors_match_registry_keys` as the owner path that proves the declared constants still cover the registry; and
  - preserve the existing published-subset ordering and file/path invariants in substance.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops deriving the nondefault benchmark selector list through `declared_string_constants_by_suffix(...)` in the parametrization for `test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants`:
  - parametrize that test directly from `benchmarks._NONDEFAULT_BENCHMARK_MANIFEST_SELECTOR_REQUESTED_FILENAMES` or another equally direct harness-owned selector-table path;
  - keep `test_declared_benchmark_manifest_selectors_match_registry_keys` as the owner path that proves the declared constants still cover the registry; and
  - preserve the current selector order, selector membership, published-order subset assertions, and manifest-path invariants in substance.
- Keep this cleanup structural only:
  - do not change selector names, selector memberships, fixture/workload contents, scorecard payloads, reports, README copy, or tracked project-state prose; and
  - prefer deleting the mirrored selector-enumeration paths over adding another helper family or another test-only selector registry.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or declared_nondefault_correctness_fixture_selectors_are_parametrized_once or declared_correctness_fixture_selectors_match_registry_keys'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'shared_correctness_fixture_selectors_resolve_published_subset_invariants or declared_correctness_fixture_selectors_match_registry_keys or default_correctness_published_manifest_helper_is_cached_and_preserves_selector_order'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or declared_benchmark_manifest_selectors_match_registry_keys or default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order'`
  - `bash -lc "! rg -n '^def _declared_nondefault_correctness_fixture_selectors' tests/python/test_fixture_parity_support_contract.py"`
  - `bash -lc "! rg -n 'for selector in declared_string_constants_by_suffix\\(' tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the change limited to these residual selector-enumeration mirrors in owner tests. Do not widen into another selector-registry rewrite, a new shared test helper, or any harness behavior change in this run.
- Preserve the existing nondefault selector memberships exactly; the point is to remove mirrored selector discovery paths, not reinterpret which selectors exist.

## Notes
- `RBR-0891` is the next available architecture task id in the current checkout:
  - `RBR-0890` is already occupied by the ready feature task in `/home/ubuntu/rebar/ops/tasks/ready/RBR-0890-publish-module-workflow-compiled-pattern-compile-noflag-literal-pair.md`;
  - `rg -n 'RBR-0891|RBR-0892|RBR-0893' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned no matches, so the tracked state and task queues do not reserve `RBR-0891`; and
  - `/home/ubuntu/rebar/ops/tasks/blocked/` is empty, so there is no blocked architecture task to reopen, refine, or normalize first.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `/home/ubuntu/rebar/.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup is concrete in the live checkout:
  - `rg -n 'declared_string_constants_by_suffix\\(' tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the residual selector-enumeration scans at `tests/python/test_fixture_parity_support_contract.py:81`, `tests/conformance/test_combined_correctness_scorecards.py:4534`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:9476`, while the matching declared-selector contract checks remain separately anchored later in those files;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'shared_correctness_fixture_selectors_resolve_published_paths or declared_nondefault_correctness_fixture_selectors_are_parametrized_once or declared_correctness_fixture_selectors_match_registry_keys'` currently passes (`21 passed, 291 deselected`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'shared_correctness_fixture_selectors_resolve_published_subset_invariants or declared_correctness_fixture_selectors_match_registry_keys or default_correctness_published_manifest_helper_is_cached_and_preserves_selector_order'` currently passes (`3 passed, 41 deselected, 19 subtests passed`); and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'shared_benchmark_manifest_selectors_resolve_published_subset_invariants or declared_benchmark_manifest_selectors_match_registry_keys or default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order'` currently passes (`3 passed, 545 deselected`).
- This is the next small post-JSON selector cleanup after the recent architecture lane:
  - `RBR-0885` moved the benchmark selector registry and owner test onto one declarative nondefault table;
  - `RBR-0887` removed the matching correctness-side canonical membership mirror; and
  - `RBR-0889` removed the residual scorecard helper/report-path pass-throughs, leaving these selector-enumeration mirrors as the next bounded owner-test cleanup.

## Completion
- Removed `_declared_nondefault_correctness_fixture_selectors()` from `tests/python/test_fixture_parity_support_contract.py` and drove the shared-selector parametrization plus the declared-selector inventory check directly from `correctness._NONDEFAULT_CORRECTNESS_FIXTURE_SELECTOR_REQUESTED_FILENAMES`, keeping the existing alphabetized selector order for that owner test.
- Switched the shared subset contracts in `tests/conformance/test_combined_correctness_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to iterate directly from the harness-owned nondefault selector tables instead of rescanning declared string constants.
- Verified with the task's three focused pytest commands plus the two grep absence checks proving the helper and residual selector-enumeration scans are gone.
