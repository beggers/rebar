# RBR-0841: Collapse replacement pytest-param sidecars onto live surfaces

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the detached pytest-param tuple sidecars from `tests/python/test_fixture_backed_replacement_parity_suite.py` so `REPLACEMENT_SURFACES` remains the sole canonical owner for replacement-surface ordering, bundle routing, and case/compile parametrization inside this parity owner.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` stops defining or reading these detached pytest-param tuple sidecars:
  - `SELECTOR_SURFACE_PARAMS`
  - `BUNDLE_PARAMS`
  - `COMPILE_PATTERN_PARAMS`
  - `MODULE_CASE_PARAMS`
  - `PATTERN_CASE_PARAMS`
  - `MATCH_SNAPSHOT_CASE_PARAMS`
  - `MATCH_GROUP_ACCESS_CASE_PARAMS`
  - `TEMPLATE_EXPAND_CASE_PARAMS`
  - `DISCOVERED_NO_MATCH_CASE_PARAMS`
- The affected parametrized tests derive directly from `REPLACEMENT_SURFACES` or from tiny file-local helpers that flatten only the live surface fields they already own:
  - `test_replacement_parity_suite_tracks_published_fixture_coverage_frontier`
  - `test_parity_suite_stays_aligned_with_published_correctness_fixture`
  - `test_replacement_suite_tracks_published_case_frontier`
  - `test_replacement_direct_test_buckets_cover_selected_frontier`
  - `test_compile_metadata_matches_cpython`
  - `test_module_replacement_matches_cpython`
  - `test_pattern_replacement_matches_cpython`
  - `test_replacement_match_snapshot_matches_cpython`
  - `test_replacement_match_group_accessors_match_cpython`
  - `test_replacement_invalid_group_access_errors_match_cpython`
  - `test_replacement_template_match_expand_matches_cpython`
  - `test_discovered_no_match_paths_leave_input_unchanged`
- Preserve the current effective parametrization order exactly by deriving it from the existing surface-owned tuples instead of from another mirrored top-level block:
  - selector params stay in `REPLACEMENT_SURFACES` order, filtered to surfaces whose `spec.fixture_selector` is not `None`;
  - bundle params stay in nested `REPLACEMENT_SURFACES` then `surface.bundles` order;
  - compile-pattern params stay in nested `REPLACEMENT_SURFACES` then `surface.spec.compile_patterns` order;
  - module, pattern, match-snapshot, match-group-access, template-expand, and discovered-no-match params stay in nested `REPLACEMENT_SURFACES` then the corresponding `surface.*cases` order.
- Keep canonical replacement ownership otherwise unchanged:
  - do not change `REPLACEMENT_SURFACES`, `REPLACEMENT_SURFACE_SPECS`, grouped/open-ended/conditional surface membership, bundle ordering, compile pattern payloads, case payloads, mixed-text routing, or pending-bytes follow-on behavior; and
  - if tiny helpers are useful, keep them file-local and surface-derived instead of introducing another registry, helper module, or parallel param table.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^(SELECTOR_SURFACE_PARAMS|BUNDLE_PARAMS|COMPILE_PATTERN_PARAMS|MODULE_CASE_PARAMS|PATTERN_CASE_PARAMS|MATCH_SNAPSHOT_CASE_PARAMS|MATCH_GROUP_ACCESS_CASE_PARAMS|TEMPLATE_EXPAND_CASE_PARAMS|DISCOVERED_NO_MATCH_CASE_PARAMS) =' tests/python/test_fixture_backed_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_fixture_backed_replacement_parity_suite as mod

assert tuple(
    surface.spec.id
    for surface in mod.REPLACEMENT_SURFACES
    if surface.spec.fixture_selector is not None
) == (
    "grouped-replacement-template",
    "open-ended-quantified-group-replacement",
    "conditional-group-exists-replacement",
)
assert tuple(
    bundle.expected_manifest_id
    for surface in mod.REPLACEMENT_SURFACES
    for bundle in surface.bundles
) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-replacement-workflows",
    "nested-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-replacement-workflows",
    "conditional-group-exists-replacement-workflows",
    "conditional-group-exists-replacement-template-workflows",
    "conditional-group-exists-alternation-replacement-workflows",
    "conditional-group-exists-nested-replacement-workflows",
    "conditional-group-exists-quantified-replacement-workflows",
    "conditional-group-exists-quantified-alternation-replacement-workflows",
    "conditional-group-exists-no-else-replacement-workflows",
    "conditional-group-exists-empty-else-replacement-workflows",
    "conditional-group-exists-empty-yes-else-replacement-workflows",
    "conditional-group-exists-fully-empty-replacement-workflows",
)
assert tuple(
    mod._pattern_param_id(pattern)
    for surface in mod.REPLACEMENT_SURFACES
    for pattern in surface.spec.compile_patterns
) == (
    "(?P<word>abc)",
    "(abc)",
    "a((b))d",
    "a((bc)+)d",
    "a((b|c))d",
    "a((b|c){1,4})\\2d",
    "a(?P<outer>(?P<inner>b))d",
    "a(?P<outer>(?P<inner>bc)+)d",
    "a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d",
    "a(?P<outer>(b|c))d",
    "a(?P<word>b|c)d",
    "a(b|c)d",
    "abc",
    "b'a((b|c){1,4})\\\\2d'",
    "b'a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d'",
    "a((b|c){1,})\\2d",
    "a((b|c){2,})\\2(?(2)d|e)",
    "a((b|c){2,})\\2d",
    "a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d",
    "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)",
    "a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d",
    "b'a((b|c){2,})\\\\2(?(2)d|e)'",
    "b'a((b|c){2,})\\\\2d'",
    "b'a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)'",
    "b'a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d'",
)
module_case_ids = tuple(
    case.case_id for surface in mod.REPLACEMENT_SURFACES for case in surface.module_cases
)
pattern_case_ids = tuple(
    case.case_id for surface in mod.REPLACEMENT_SURFACES for case in surface.pattern_cases
)
assert module_case_ids[:8] == (
    "module-sub-callable-str",
    "module-sub-grouping-template",
    "module-sub-template-named-group-str",
    "module-subn-template-named-group-str",
    "module-sub-template-grouped-alternation-str",
    "module-subn-template-grouped-alternation-str",
    "module-sub-template-named-grouped-alternation-str",
    "module-subn-template-named-grouped-alternation-str",
)
assert pattern_case_ids[:8] == (
    "pattern-sub-template-named-group-str",
    "pattern-subn-template-named-group-str",
    "pattern-sub-template-grouped-alternation-str",
    "pattern-subn-template-grouped-alternation-str",
    "pattern-sub-template-named-grouped-alternation-str",
    "pattern-subn-template-named-grouped-alternation-str",
    "pattern-sub-template-nested-group-numbered-str",
    "pattern-subn-template-nested-group-numbered-str",
)
assert len(module_case_ids) == 86
assert len(pattern_case_ids) == 84
assert len(
    tuple(
        case.case_id
        for surface in mod.REPLACEMENT_SURFACES
        for case in surface.match_snapshot_cases
    )
) == 80
assert len(
    tuple(
        case.case_id
        for surface in mod.REPLACEMENT_SURFACES
        for case in surface.match_group_access_cases
    )
) == 20
assert len(
    tuple(
        case.case_id
        for surface in mod.REPLACEMENT_SURFACES
        for case in surface.template_expand_cases
    )
) == 89
assert len(
    tuple(
        case.case_id
        for surface in mod.REPLACEMENT_SURFACES
        for case in surface.discovered_no_match_cases
    )
) == 80
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the mirrored param-sidecar layer inside the replacement parity owner, not to reinterpret replacement semantics, adjust which cases stay published, or broaden the harness surface.
- Keep scope limited to `tests/python/test_fixture_backed_replacement_parity_suite.py`. Do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0841` is the next available task id in the current checkout:
  - `python3` queue/id inspection in this run returned `RBR-0841` with an empty reserved tail; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` only reserve the already-filed `RBR-0840`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py` currently passes (`1166 passed in 0.87s`);
  - `rg -n '^(SELECTOR_SURFACE_PARAMS|BUNDLE_PARAMS|COMPILE_PATTERN_PARAMS|MODULE_CASE_PARAMS|PATTERN_CASE_PARAMS|MATCH_SNAPSHOT_CASE_PARAMS|MATCH_GROUP_ACCESS_CASE_PARAMS|TEMPLATE_EXPAND_CASE_PARAMS|DISCOVERED_NO_MATCH_CASE_PARAMS) =' tests/python/test_fixture_backed_replacement_parity_suite.py` currently shows exactly the nine detached tuple declarations and no other owners;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those mirrored param tables still exist; and
  - the import probe in Acceptance already passes (`ok`), showing `REPLACEMENT_SURFACES` already carries the canonical ordering and payloads needed to delete the extra param layer without changing behavior.
- This stays on the same bounded replacement-harness simplification track as `RBR-0713`, `RBR-0785`, `RBR-0807`, and `RBR-0819`: those tasks already collapsed adjacent manifest-id, bundle-spec, and selector sidecars in this owner, and these remaining pytest-param tuples are now just another mirrored top-level view over live replacement surfaces.
