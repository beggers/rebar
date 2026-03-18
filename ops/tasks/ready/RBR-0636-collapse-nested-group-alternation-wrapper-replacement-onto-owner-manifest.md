# RBR-0636: Collapse the nested grouped-alternation wrapper-template pair onto the owner replacement manifest

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete the one-off `nested_group_alternation_wrapper_replacement_workflows.py` correctness manifest by folding its two wrapper-template cases into `nested_group_alternation_replacement_workflows.py`, so this bounded replacement slice stays on one ordinary owner manifest instead of a companion wrapper-only path.

## Deliverables
- `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py`
- Delete `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py`
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py` becomes the sole correctness manifest for the bounded nested grouped-alternation template slice:
  - keep the existing `manifest_id` `nested-group-alternation-replacement-workflows` and `suite_id` `collection.replacement.nested_group_alternation`;
  - preserve the current `\\1x` / `\\g<outer>x` pair unchanged; and
  - absorb the existing wrapper-template pair with the same case ids, families, categories, notes, and public patterns/haystacks (`<\\1>` on `abdacd` and `<\\g<outer>>` on `abdacd` with `count=1`) instead of renaming or widening the slice.
- `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py` is deleted outright:
  - do not leave a second manifest id, an import-only wrapper, or a helper-generated sidecar behind; and
  - do not replace it with another `wrapper`-named correctness path.
- `python/rebar_harness/correctness.py` removes `nested_group_alternation_wrapper_replacement_workflows.py` from the published fixture selector path:
  - do not add another selector alias, manifest indirection, or merge-time special case to compensate for the deleted file.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` collapses ownership onto the existing grouped replacement surface:
  - remove the dedicated `FixtureBundleSpec` and manifest-id references for `nested-group-alternation-wrapper-replacement-workflows`;
  - keep wrapper-template behavior derived from case categories inside the existing grouped replacement assertions instead of introducing a new owner surface or helper module; and
  - keep the grouped replacement ownership/frontier checks asserting the merged wrapper-template cases through `nested-group-alternation-replacement-workflows`.
- `tests/conformance/correctness_expectations.py` no longer declares a separate `nested-group-alternation-wrapper-replacement-workflows` expectation:
  - expand `nested-group-alternation-replacement-workflows` representative cases so the merged manifest still proves both the original `\\1x` / `\\g<outer>x` pair and the absorbed wrapper-template pair are published; and
  - the tracked correctness registry/report expectations no longer reference `collection.replacement.nested_group_alternation.wrapper` or its manifest id.
- `reports/correctness/latest.py` is regenerated honestly:
  - `nested-group-alternation-replacement-workflows` publishes `4` total / `4` passed / `0` unimplemented cases for the merged slice;
  - `nested-group-alternation-wrapper-replacement-workflows` and the `collection.replacement.nested_group_alternation.wrapper*` suites disappear from the tracked report; and
  - the combined report keeps the same total case count while dropping one published manifest relative to the pre-task checkout.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py::test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit tests/python/test_fixture_backed_replacement_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture[nested-group-alternation-replacement-workflows] tests/python/test_fixture_backed_replacement_parity_suite.py::test_replacement_suite_tracks_published_case_frontier[nested-group-alternation-replacement-workflows]`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_scorecard_cases_preserve_fixture_prefix_and_representative_case_order`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path
from rebar_harness.correctness import load_fixture_manifest, published_fixture_manifests

fixture = load_fixture_manifest(
    Path("tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py")
)
case_ids = tuple(case.case_id for case in fixture.cases)
assert case_ids == (
    "module-sub-template-nested-group-alternation-numbered-outer-str",
    "pattern-subn-template-nested-group-alternation-named-outer-first-match-only-str",
    "module-sub-template-nested-group-alternation-numbered-wrapper-str",
    "pattern-subn-template-nested-group-alternation-named-wrapper-first-match-only-str",
), case_ids
assert fixture.suite_id == "collection.replacement.nested_group_alternation"
published_manifest_ids = {manifest.manifest_id for manifest in published_fixture_manifests()}
assert "nested-group-alternation-wrapper-replacement-workflows" not in published_manifest_ids
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this cleanup structural. Do not change Rust code, `python/rebar/` behavior, benchmark workloads or expectations, callable-replacement slices, or broader nested grouped replacement coverage.
- Prefer deleting the extra manifest and suite over adding another ownership abstraction or selector alias.
- Keep the public case ids and replacement semantics unchanged; only the owning manifest/suite shape should shrink.

## Notes
- `RBR-0636` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-063[6-9]|RBR-064[0-9]" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returns no reserved or active task in that range outside a stale note inside `RBR-0634`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` still shows an inherited-dirty skip at `aa53269be651a84ea9323d028656de4d7057c6ab`, but the live checkout is clean at `c30848c600f54854592712ab7c334b6402dc0a48` (`git status --porcelain=v1` returns nothing), so the queue bottleneck was checkpointed rather than still active; and
  - `ops/tasks/ready/` contains only `RBR-0635`, which is owned by `feature-implementation`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication is concrete in the current checkout:
  - a direct manifest probe shows `nested_group_alternation_replacement_workflows.py` and `nested_group_alternation_wrapper_replacement_workflows.py` publish the same two patterns (`a((b|c))d` and `a(?P<outer>(b|c))d`) with the same `('module_call', 'sub')` plus `('pattern_call', 'subn')` helper mix; the wrapper manifest differs only by carrying the `wrapper-template` category on its two cases;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py --report .rebar/tmp/architecture-nested-group-alternation-replacement-pair.py` currently passes and reports `4` total / `4` passed / `0` unimplemented;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py::test_grouped_replacement_surface_keeps_selected_bundle_ownership_explicit tests/python/test_fixture_backed_replacement_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture[nested-group-alternation-replacement-workflows] tests/python/test_fixture_backed_replacement_parity_suite.py::test_replacement_suite_tracks_published_case_frontier[nested-group-alternation-replacement-workflows]` currently passes (`3 passed in 0.07s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py::CorrectnessScorecardRegistryContractTest::test_scorecard_cases_preserve_fixture_prefix_and_representative_case_order` currently passes (`1 passed, 124 subtests passed in 0.52s`); and
  - the merged-state probe in Acceptance currently fails exactly because `nested_group_alternation_replacement_workflows.py` still contains only the two `\\1x` / `\\g<outer>x` cases and the published selector still exposes the separate wrapper manifest.
