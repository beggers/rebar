# RBR-1117: Collapse published manifest-id lookups onto shared test support

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining owner-local published-manifest id-map boilerplate from the large correctness and benchmark scorecard tests by routing those lookups through one shared helper on `tests/conftest.py` instead of rebuilding `{manifest.manifest_id: manifest}` maps in multiple places.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/conftest.py`, or a strictly smaller equivalent on that existing support path, that:
  - accepts an iterable of published manifest-like records;
  - builds a manifest-id keyed lookup using the existing `manifest_id` attribute contract;
  - preserves access to the original manifest objects without reshaping them; and
  - rejects duplicate manifest ids instead of silently overwriting them.
- Extend `tests/python/test_shared_test_support_contract.py` so the new helper is covered with focused synthetic inputs, including:
  - a success case that returns the expected manifest-id keyed mapping for unique manifest ids; and
  - a duplicate-id rejection case that proves repeated manifest ids fail loudly.
- `tests/conformance/test_combined_correctness_scorecards.py` stops rebuilding published manifest-id maps inline inside:
  - `CorrectnessScorecardRegistryContractTest._assert_mixed_text_manifests_cover_both_representative_text_models`; and
  - `CorrectnessScorecardRegistryContractTest._assert_mixed_text_manifests_mirror_representative_bytes_rows`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops carrying the owner-local `_source_tree_manifest_records()` dict-comprehension wrapper and uses the shared helper surface instead for the same published benchmark manifest-id lookup contract.
- Preserve current behavior after the cleanup:
  - correctness and benchmark owners still read the same published manifest objects;
  - duplicate manifest ids still fail loudly instead of being overwritten; and
  - no scorecard expectation, manifest ordering, workload selection, or report assertion changes.
- Keep the cleanup structural and limited to the four files above. Do not widen it into harness implementation code, reports, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'manifests_by_id = \\{|def _source_tree_manifest_records\\(' tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Reuse `tests/conftest.py` as the shared-support home; do not add a new helper module, registry, or abstraction tier.
- Keep the helper generic enough for both correctness and benchmark manifest records without encoding suite-specific selector names or report semantics.
- Keep the task focused on deleting repeated manifest-id lookup plumbing, not on changing scorecard contents, manifest inventories, or benchmark/correctness harness behavior.

## Notes
- `RBR-1117` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1116`; and
  - `rg -n 'RBR-1117|RBR-1118|RBR-1119|RBR-1120|RBR-1121' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/conformance/test_combined_correctness_scorecards.py:4657` and `tests/conformance/test_combined_correctness_scorecards.py:4703` still rebuild the same `manifests_by_id` mapping from `correctness.published_fixture_manifests()` inside two registry-contract helpers; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:2817` still carries `_source_tree_manifest_records()` as an owner-local published benchmark manifest-id map wrapper.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned `804 passed, 3 skipped, 4022 subtests passed` in this run.
- The negative `rg` verification currently fails exactly on the targeted lookup boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.
