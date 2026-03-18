# RBR-0608: Collapse the open-ended quantified-group bytes routing and parity ladders onto one table

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the duplicated open-ended quantified-group bytes routing checks and per-family bytes compile/module/pattern parity ladders in `tests/python/test_open_ended_quantified_group_parity_suite.py` with one local spec-driven surface plus shared parametrized assertions, so the suite stops restating the same logic for the seven open-ended grouped bytes families.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the imported bytes case tuples (`OPEN_ENDED_ALTERNATION_BYTES_CASES`, `OPEN_ENDED_CONDITIONAL_BYTES_CASES`, `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`, `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES`, `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES`, `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES`, and `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`) plus `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, `DIRECT_BYTES_FOLLOW_ON_BUNDLE_SPECS`, `DIRECT_BYTES_FOLLOW_ON_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES`, but replaces the current family-specific bytes routing/parity ladders with one local spec-driven surface. The shared table should own only the metadata that currently differs across the seven bytes families:
  - which bundle and bytes case tuple are under test;
  - whether the family keeps bytes rows in the generic compile/module/pattern buckets or in the explicit direct-follow-on bundles;
  - the exact bytes-side `Counter((operation, helper), ...)` for the published rows in that bundle;
  - the exact published module-search texts by pattern; and
  - the exact published pattern-fullmatch texts by pattern.
- Consolidate the current nine family-specific bytes routing/anchor tests into shared parametrized assertions without changing behavior:
  - preserve the current open-ended alternation mixed-manifest coverage assertions, the two generic-bucket routing checks, and the six direct-follow-on anchor checks;
  - keep the exact case ids, byte patterns, bundle row counts, and published bytes text maps unchanged; and
  - keep the current routing split unchanged, where `open-ended-quantified-group-alternation-workflows`, `open-ended-quantified-group-alternation-conditional-workflows`, and `nested-open-ended-quantified-group-alternation-workflows` still expose bytes rows through the generic compile/module/pattern buckets while the four `DIRECT_BYTES_FOLLOW_ON_SPECS` families continue to exclude those bytes rows from the generic buckets and keep them explicit through the direct-follow-on bundles.
- Consolidate the current forty-nine family-specific bytes compile/module/pattern parity tests into shared parametrized tests over the combined bytes case surface without changing behavior:
  - preserve compile parity, module-search result parity, module-search convenience parity, module-search group-access parity, pattern-fullmatch result parity, pattern-fullmatch convenience parity, and pattern-fullmatch group-access parity;
  - keep `check_regs=True` wherever the current bytes ladders use it;
  - keep the current `search_matches`, `search_misses`, `fullmatch_matches`, and `fullmatch_misses` payloads on every imported `SupplementalCase` tuple untouched, including the families that assert no search misses and the families that continue to assert exact miss rows; and
  - do not add new `rebar` skip gating or unsupported annotations.
- Keep this cleanup local to the open-ended parity suite:
  - do not change `tests/python/fixture_parity_support.py`, correctness fixtures, benchmark workloads/tests, reports, Rust code, or `python/rebar/`;
  - do not rename the imported bytes case tuples, `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, `DIRECT_BYTES_FOLLOW_ON_BUNDLE_SPECS`, `DIRECT_BYTES_FOLLOW_ON_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, or `PATTERN_CASES`; and
  - leave the distinct trace and bounded-window coverage in the file intact instead of trying to abstract `OpenEndedTraceCase`, the bytes branch-order trace builders/tests, or `PATTERN_BOUNDS_*` into the same shared table.
- After the consolidation lands, no family-specific bytes routing or parity-ladder test functions remain in the file. This cleanup should remove the current duplicate prefixes rather than move them behind another named wrapper layer:
  - `bash -lc "! rg -n '^def test_(open_ended_(alternation|conditional|backtracking_heavy)|nested_open_ended_alternation|broader_range_open_ended_(alternation|conditional|backtracking_heavy))_bytes_(cases_stay_explicit_with_(mixed_manifest_coverage|one_direct_follow_on_anchor)|fixture_rows_run_through_generic_case_buckets)\\($' tests/python/test_open_ended_quantified_group_parity_suite.py"`
  - `bash -lc "! rg -n '^def test_(open_ended_(alternation|conditional|backtracking_heavy)|nested_open_ended_alternation|broader_range_open_ended_(alternation|conditional|backtracking_heavy))_bytes_(compile_metadata_matches_cpython|module_search_matches_cpython|module_search_convenience_api_matches_cpython|module_search_match_group_access_matches_cpython|pattern_fullmatch_matches_cpython|pattern_fullmatch_convenience_api_matches_cpython|pattern_fullmatch_match_group_access_matches_cpython)\\($' tests/python/test_open_ended_quantified_group_parity_suite.py"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_open_ended_quantified_group_parity_suite as mod

direct_manifest_ids = tuple(
    bundle.expected_manifest_id for bundle in mod.DIRECT_BYTES_FOLLOW_ON_BUNDLES
)
assert direct_manifest_ids == (
    "broader-range-open-ended-quantified-group-alternation-workflows",
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
)

generic_manifest_ids = tuple(
    bundle.manifest.manifest_id
    for bundle in mod.FIXTURE_BUNDLES
    if any(
        case.manifest_id == bundle.manifest.manifest_id and case.text_model == "bytes"
        for case in mod.COMPILE_CASES + mod.MODULE_CASES + mod.PATTERN_CASES
    )
)
assert generic_manifest_ids == (
    "open-ended-quantified-group-alternation-workflows",
    "open-ended-quantified-group-alternation-conditional-workflows",
    "nested-open-ended-quantified-group-alternation-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg -n '^def test_(open_ended_(alternation|conditional|backtracking_heavy)|nested_open_ended_alternation|broader_range_open_ended_(alternation|conditional|backtracking_heavy))_bytes_(cases_stay_explicit_with_(mixed_manifest_coverage|one_direct_follow_on_anchor)|fixture_rows_run_through_generic_case_buckets)\\($' tests/python/test_open_ended_quantified_group_parity_suite.py"`
  - `bash -lc "! rg -n '^def test_(open_ended_(alternation|conditional|backtracking_heavy)|nested_open_ended_alternation|broader_range_open_ended_(alternation|conditional|backtracking_heavy))_bytes_(compile_metadata_matches_cpython|module_search_matches_cpython|module_search_convenience_api_matches_cpython|module_search_match_group_access_matches_cpython|pattern_fullmatch_matches_cpython|pattern_fullmatch_convenience_api_matches_cpython|pattern_fullmatch_match_group_access_matches_cpython)\\($' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep the task structural only. Do not change the published correctness frontier, the bytes observations, or any backend behavior.
- Preserve the current bytes-case payloads exactly; the point is to delete duplicate harness code, not to reinterpret the open-ended grouped bytes surface.
- Prefer one ordinary local spec table plus shared parametrized pytest over another support module, registry layer, or bytes-only suite.

## Notes
- `RBR-0608` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` name no reserved `RBR-0608`;
  - `ops/tasks/ready/` currently stops at `RBR-0607`; and
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: f74a0d67e66be2a86a18a05d26c858a6ab1555b9`, which matches `git rev-parse HEAD`; and
  - the latest runtime cycle finished both task workers at `done`, with no inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` is currently `3151` lines long;
  - the file still carries `9` family-specific bytes routing/anchor test definitions matching the first `rg` pattern above;
  - the file still carries `49` family-specific bytes compile/module/pattern parity test definitions matching the second `rg` pattern above; and
  - the duplicated bytes routing/parity surface is confined to this one suite, while the separate bytes trace and bounded-window tests stay out of scope for this task.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passes (`3891 passed in 2.57s`)
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above passes (`ok`)
  - the first `bash -lc "! rg -n ..."` command above currently fails exactly on this cleanup because the `9` family-specific bytes routing/anchor test definitions are still present
  - the second `bash -lc "! rg -n ..."` command above currently fails exactly on this cleanup because the `49` family-specific bytes compile/module/pattern parity test definitions are still present
