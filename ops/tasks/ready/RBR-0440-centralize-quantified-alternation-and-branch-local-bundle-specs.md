# RBR-0440: Centralize quantified-alternation and branch-local bundle specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining repeated whole-manifest `load_fixture_bundle(...)` declarations and bundle-to-case fanout in the two largest fixture-backed parity suites with the existing declarative spec helpers in `tests/python/fixture_parity_support.py`, so the post-JSON pytest surface stops hand-maintaining 19 near-identical bundle loads after the earlier suite-consolidation passes.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- Both targeted suites switch from inline `FIXTURE_BUNDLES = (load_fixture_bundle(...), ...)` declarations to explicit `FIXTURE_BUNDLE_SPECS = (...)` tuples of `WholeManifestBundleSpec(...)`, followed by `FIXTURE_BUNDLES = load_whole_manifest_fixture_bundles(FIXTURE_BUNDLE_SPECS)`.
- Both suites route shared case fanout through the existing helper surface instead of open-coded bundle comprehensions:
  - `tests/python/test_quantified_alternation_parity_suite.py` uses `fixture_cases_from_bundles(...)` for `PUBLISHED_CASES` and `fixture_cases_for_operation(...)` for `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES`.
  - `tests/python/test_branch_local_backreference_parity_suite.py` uses `fixture_cases_from_bundles(...)` for `PUBLISHED_CASES` and `fixture_cases_for_operation(...)` for `COMPILE_CASES`; if `WORKFLOW_CASES` still needs an `operation != "compile"` filter, keep it derived from that shared `PUBLISHED_CASES` value rather than another bundle fanout.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps its current explicit frontier local to the suite instead of hiding it in support code:
  - keep the exact manifest ids, exact case-id sets, pattern sets, and `(operation, helper)` counters explicit in the suite for all nine currently covered manifests:
    - `literal-alternation-workflows`
    - `exact-repeat-quantified-group-alternation-workflows`
    - `quantified-alternation-workflows`
    - `quantified-nested-group-alternation-workflows`
    - `quantified-alternation-backtracking-heavy-workflows`
    - `quantified-alternation-broader-range-workflows`
    - `quantified-alternation-conditional-workflows`
    - `quantified-alternation-open-ended-workflows`
    - `quantified-alternation-nested-branch-workflows`
  - keep `REGS_PARITY_CASE_IDS`, `BACKTRACKING_BRANCH_TEXT`, `ZERO_REPETITION_NO_MATCH_TEXT`, `OVERLAP_TAIL_NO_MATCH_TEXT`, `BacktrackingTraceCase`, `SupplementalNoMatchCase`, `_compile_case_prefix(...)`, `_build_backtracking_trace_cases(...)`, `_build_supplemental_no_match_cases(...)`, `BACKTRACKING_TRACE_CASES`, and `SUPPLEMENTAL_NO_MATCH_CASES` explicit in the suite; and
  - replace the local `next(bundle for bundle in FIXTURE_BUNDLES ...)` lookup for the backtracking-heavy manifest with the existing shared manifest-id lookup helper from `tests/python/fixture_parity_support.py`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps its current explicit frontier local to the suite instead of hiding it in support code:
  - keep the exact manifest ids, exact case-id sets, pattern sets, and `(operation, helper)` counters explicit in the suite for all ten currently covered manifests:
    - `branch-local-backreference-workflows`
    - `quantified-branch-local-backreference-workflows`
    - `optional-group-alternation-branch-local-backreference-workflows`
    - `conditional-group-exists-branch-local-backreference-workflows`
    - `nested-group-alternation-branch-local-backreference-workflows`
    - `quantified-alternation-branch-local-backreference-workflows`
    - `quantified-nested-group-alternation-branch-local-backreference-workflows`
    - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows`
    - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows`
  - keep `MATCH_CONVENIENCE_MANIFEST_IDS`, `MATCH_CONVENIENCE_CASE_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, `MATCH_GROUP_ACCESS_CASES`, `SupplementalMissCase`, `BoundedPatternCase`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, `SUPPLEMENTAL_MISS_CASES`, and `_bounded_pattern(...)` explicit in the suite; and
  - keep `CASES_BY_ID` file-local if that remains the clearest shape, but build it from the shared `PUBLISHED_CASES` fanout rather than from another manifest-loading loop.
- The cleanup remains structural only:
  - do not change correctness fixtures, Rust code, `python/rebar/`, `python/rebar_harness/`, benchmark workloads, published reports, README text, or tracked state files beyond this task file; and
  - do not broaden into `tests/python/test_open_ended_quantified_group_parity_suite.py` or `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` in the same run.
- No fixture membership, case ordering, supplemental parity coverage, or assertion semantics broaden or shrink as part of the refactor.
- If the current helper surface is sufficient, do not grow another support layer. If one tiny helper adjustment is genuinely necessary, keep it in `tests/python/fixture_parity_support.py`, keep it generic to whole-manifest bundle reuse, and add focused coverage in `tests/python/test_fixture_parity_support_contract.py`.
- After the cleanup:
  - `rg -n 'load_fixture_bundle\\(' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` returns no matches.
  - `rg -n 'case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` returns no matches.
  - `rg -n 'next\\(\\s*bundle\\s+for\\s+bundle\\s+in\\s+FIXTURE_BUNDLES' tests/python/test_quantified_alternation_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py`.

## Constraints
- Prefer the existing `WholeManifestBundleSpec`, `load_whole_manifest_fixture_bundles(...)`, `fixture_cases_from_bundles(...)`, `fixture_cases_for_operation(...)`, and shared manifest-id lookup helper in `tests/python/fixture_parity_support.py` over another support module, registry, or generated table.
- Keep the task bounded to these two suites. `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` should remain follow-on cleanup candidates rather than being pulled into the same run.

## Notes
- `RBR-0439` is already reserved in `README.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` for the next feature-owned quantified alternation-heavy conditional-replacement follow-on, so this architecture cleanup starts at `RBR-0440`.
- The runtime dashboard is current and clean (`Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one cleanup task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `rg -o "load_fixture_bundle\\(" tests/python/*.py | cut -d: -f1 | sort | uniq -c | sort -nr` shows these two targeted suites as the densest remaining whole-manifest bundle-load owners after the earlier conditional and grouped-capture cleanup passes:
  - `10 tests/python/test_branch_local_backreference_parity_suite.py`
  - `9 tests/python/test_quantified_alternation_parity_suite.py`
