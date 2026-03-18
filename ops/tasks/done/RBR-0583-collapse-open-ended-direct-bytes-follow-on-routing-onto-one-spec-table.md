# RBR-0583: Collapse open-ended direct-bytes follow-on routing onto one spec table

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Remove the remaining one-off direct-bytes follow-on routing boilerplate from `tests/python/test_open_ended_quantified_group_parity_suite.py` so that suite uses one shared spec table for its direct-follow-on bundle registry and one parametrized routing test, matching the representation already used by the adjacent quantified-alternation and wider-ranged-repeat parity suites.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` introduces one module-level tuple named `DIRECT_BYTES_FOLLOW_ON_SPECS` and one module-level tuple named `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`.
- The new spec table keeps the current direct-follow-on bundle surface exact and explicit:
  - preserve the same four bundle anchors currently routed through the supplemental bytes path:
    - `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE`
    - `OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`
    - `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE`
    - `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`
  - derive `DIRECT_BYTES_FOLLOW_ON_BUNDLES` from `DIRECT_BYTES_FOLLOW_ON_SPECS` instead of maintaining a separate handwritten bundle tuple; and
  - keep the resulting `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` contents unchanged.
- Replace these four one-off routing tests with one parametrized test named `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(...)`:
  - `test_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor`
  - `test_broader_range_open_ended_alternation_bytes_fixture_rows_route_through_direct_follow_on_anchor`
  - `test_broader_range_open_ended_conditional_bytes_fixture_rows_route_through_direct_follow_on_anchor`
  - `test_broader_range_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor`
- The replacement parametrized test must:
  - iterate `DIRECT_BYTES_FOLLOW_ON_SPECS` with `ids=DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`;
  - call `assert_direct_bytes_follow_on_bundle_routing(...)` with the same `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` objects used today; and
  - keep the routing assertion depth unchanged, without adding bundle-specific logic back into the loop body.
- Preserve current suite behavior exactly:
  - keep all existing explicit bytes-case tests and their bundle-specific assertions unchanged;
  - do not change any bytes supplemental case tables, fixture bundle specs, case ids, patterns, or match/miss expectations;
  - do not change `tests/python/fixture_parity_support.py`, any other parity suite, correctness fixtures, Rust code, benchmark files, or published reports.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    path = Path('tests/python/test_open_ended_quantified_group_parity_suite.py')
    module = ast.parse(path.read_text())
    function_names = {
        node.name
        for node in module.body
        if isinstance(node, ast.FunctionDef)
    }
    module_assignments = {
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    failures = []
    for symbol in ('DIRECT_BYTES_FOLLOW_ON_SPECS', 'DIRECT_BYTES_FOLLOW_ON_SPEC_IDS'):
        if symbol not in module_assignments:
            failures.append(f'module:missing:{symbol}')

    required_function = (
        'test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets'
    )
    if required_function not in function_names:
        failures.append(f'function:missing:{required_function}')

    old_names = (
        'test_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor',
        'test_broader_range_open_ended_alternation_bytes_fixture_rows_route_through_direct_follow_on_anchor',
        'test_broader_range_open_ended_conditional_bytes_fixture_rows_route_through_direct_follow_on_anchor',
        'test_broader_range_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor',
    )
    for old_name in old_names:
        if old_name in function_names:
            failures.append(f'function:still-present:{old_name}')

    if failures:
        raise SystemExit('\n'.join(failures))

    print('ok')
    PY
    ```

## Constraints
- Keep this cleanup structural only. Do not alter parity coverage, backend behavior, bytes follow-on bundle membership, or the direct-follow-on routing policy itself.
- Prefer one small local spec table plus parametrized test over another helper module, another dataclass layer, or a second registry that restates the same bundle list.
- Keep the new spec surface aligned with the existing quantified-alternation and wider-ranged-repeat suite shape instead of inventing a third representation just for the open-ended suite.

## Notes
- `RBR-0582` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active feature-owned quantified-alternation nested-branch bytes benchmark catch-up task, and it edits `tests/benchmarks/benchmark_expectations.py` plus the source-tree benchmark test modules. This architecture cleanup stays off those files to avoid unnecessary shared-queue file contention, so `RBR-0583` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `c6c59b80ab9c9892655336ae3d607223f229145a` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicated routing surface is concrete in the current checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` currently defines `DIRECT_BYTES_FOLLOW_ON_BUNDLES` without a matching `DIRECT_BYTES_FOLLOW_ON_SPECS` or `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS` registry;
  - the same file still carries four one-off `*_route_through_direct_follow_on_anchor` tests that only differ by bundle constant; and
  - the adjacent `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` already use a `DIRECT_BYTES_FOLLOW_ON_SPECS` plus `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS` parametrization pattern for the same routing assertion shape.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passes (`3891 passed in 2.59s`);
  - the AST probe above currently fails exactly on this cleanup with:
    - `module:missing:DIRECT_BYTES_FOLLOW_ON_SPECS`
    - `module:missing:DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`
    - `function:missing:test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets`
    - `function:still-present:test_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor`
    - `function:still-present:test_broader_range_open_ended_alternation_bytes_fixture_rows_route_through_direct_follow_on_anchor`
    - `function:still-present:test_broader_range_open_ended_conditional_bytes_fixture_rows_route_through_direct_follow_on_anchor`
    - `function:still-present:test_broader_range_open_ended_backtracking_heavy_bytes_fixture_rows_route_through_direct_follow_on_anchor`

## Completion Notes
- 2026-03-18 architecture-implementation: Replaced the handwritten `DIRECT_BYTES_FOLLOW_ON_BUNDLES` tuple in `tests/python/test_open_ended_quantified_group_parity_suite.py` with one shared `DIRECT_BYTES_FOLLOW_ON_SPECS` table plus `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, deriving the direct-follow-on bundle tuple from that registry while keeping the same four open-ended bytes follow-on anchors and the same `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` partitioning.
- Replaced the four one-off `*_route_through_direct_follow_on_anchor` tests with the parametrized `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(...)`, mirroring the adjacent quantified-alternation and wider-ranged-repeat parity-suite shape without changing any explicit bytes supplemental cases or bundle-specific assertions.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` (`3891 passed in 2.72s`) and the task acceptance AST probe (`ok`).
