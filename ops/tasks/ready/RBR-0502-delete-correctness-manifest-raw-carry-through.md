# RBR-0502: Delete correctness manifest raw carry-through

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the last raw-manifest carry-through from the correctness loader so `FixtureManifest` stops storing the entire original manifest dict just to support descriptor-shape assertions in parity tests. The intended end state is one typed correctness surface where the only pre-materialized fixture data that survives loading lives on each `FixtureCase`.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_python_fixture_manifest_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` deletes the manifest-wide raw carry-through:
  - `FixtureManifest` no longer has a `raw` field.
  - `load_fixture_manifest(...)` no longer stores the whole `raw_manifest` on the returned manifest once loader validation is complete.
  - `load_fixture_manifests(...)` continues to return `list[FixtureManifest]` with manifest ordering and duplicate-id validation unchanged.
- The remaining source-level fixture data needed by parity-support assertions becomes case-owned and explicit:
  - `FixtureCase` gains `source_args` and `source_kwargs` fields that preserve the pre-materialized manifest payload after defaults are applied.
  - `FixtureCase.args` and `FixtureCase.kwargs` remain the materialized runtime values used by harness execution.
  - `serialized_args()` and `serialized_kwargs()` keep their current scorecard contract unchanged; this task does not redesign scorecard serialization for callable descriptors.
- Source-payload access in the Python parity helpers stops recovering raw rows from `manifest.raw["cases"]`:
  - `tests/python/fixture_parity_support.py` deletes `_manifest_raw_cases(...)` and `raw_fixture_cases_by_id(...)`.
  - Any lookup of selected callable/template replacement descriptors is driven from `bundle.cases` / `FixtureCase` rather than dicts reconstructed from `manifest.raw`.
- The two raw-descriptor assertion surfaces switch to the new case-owned payloads without changing their current coverage:
  - `tests/python/test_fixture_parity_support_contract.py` still proves the published `collection_replacement_workflows.py` bundle exposes the callable-constant descriptor and grouping-template row from the selected cases, but it asserts through `FixtureCase.source_args` instead of `raw_cases[...]`.
  - `tests/python/test_callable_replacement_parity_suite.py` still validates callable replacement descriptor references against the published fixtures, but `_raw_callable_replacement(...)` and the adjacent literal-callable alignment checks are removed or rewritten to use the case-owned source payloads.
- Loader contract coverage pins the new source-payload surface without loosening the existing materialization checks:
  - `tests/conformance/test_python_fixture_manifest_contract.py` keeps the current `serialized_args()` / `serialized_kwargs()` expectations;
  - adds or updates assertions that `source_args` / `source_kwargs` preserve the original descriptor dicts and strings after default expansion; and
  - confirms those source payload collections do not alias across cases that inherit shared manifest defaults.
- Preserve current correctness behavior exactly:
  - keep published fixture ids, case ids, case ordering, manifest ordering, materialized callable behavior, and `rebar_harness.correctness` scorecard output unchanged for the same fixture selection.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_python_fixture_manifest_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0502-correctness-raw-descriptor-cleanup.py`
  - `rg -n 'raw: dict\\[str, Any\\]|manifest\\.raw|def _manifest_raw_cases\\(|raw_fixture_cases_by_id\\(' python/rebar_harness/correctness.py tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_python_fixture_manifest_contract.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from pathlib import Path
    from rebar_harness.correctness import load_fixture_manifest

    manifest = load_fixture_manifest(Path("tests/conformance/fixtures/collection_replacement_workflows.py"))
    case = next(case for case in manifest.cases if case.case_id == "module-sub-callable-str")
    assert not hasattr(manifest, "raw"), "manifest.raw should be removed"
    assert case.source_args[1] == {"type": "callable_constant", "value": "x"}
    assert case.source_kwargs == {}
    print("ok")
    PY
    ```

## Constraints
- Keep the cleanup structural only. Do not change fixture modules under `tests/conformance/fixtures/`, do not change published reports, README text, or tracked state files, and do not broaden into the queued feature follow-on `RBR-0501`.
- Prefer one explicit case-owned source payload surface over another manifest raw-lookup helper or a fixture reparse pass inside tests.
- Do not broaden this task into benchmark-harness cleanup, correctness scorecard payload changes, or a general descriptor-serialization redesign.

## Notes
- `RBR-0492` intentionally stopped after collapsing the correctness loader onto typed `FixtureManifest` / `FixtureCase` records and left one raw-descriptor seam local to `raw_fixture_cases_by_id(...)`; this is the direct follow-on to finish that cleanup.
- `RBR-0501` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, and `RBR-0502` is unused in tracked state and task queues.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The runtime dashboard queue count is stale relative to the filesystem: `.rebar/runtime/dashboard.md` still reports `ready: 1`, but `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are all empty in the current checkout, so rule 10 does not apply.
- Remaining raw-manifest coupling is concentrated in five files:
  - `python/rebar_harness/correctness.py` still stores `FixtureManifest.raw`.
  - `tests/python/fixture_parity_support.py` still walks `manifest.raw["cases"]` and exports `raw_fixture_cases_by_id(...)`.
  - `tests/python/test_fixture_parity_support_contract.py` still indexes selected rows through `raw_cases[...]`.
  - `tests/python/test_callable_replacement_parity_suite.py` still indexes raw case payloads through `raw_fixture_cases_by_id(...)`.
  - `tests/conformance/test_python_fixture_manifest_contract.py` does not yet pin a case-owned source payload surface.
- 2026-03-17 architecture probe:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_python_fixture_manifest_contract.py` passes in the current checkout (`6 passed, 10 subtests passed in 0.03s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_callable_replacement_parity_suite.py` passes in the current checkout (`1064 passed in 0.84s`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-0502-correctness-raw-descriptor-cleanup.py` currently succeeds and reports `{"executed_cases": 15, "failed_cases": 0, "passed_cases": 15, "skipped_cases": 0, "total_cases": 15, "unimplemented_cases": 0}`.
  - The `rg -n ...` command above currently returns the live `FixtureManifest.raw`, `_manifest_raw_cases(...)`, and `raw_fixture_cases_by_id(...)` matches listed in the notes, which is the exact coupling this task should delete.
  - The typed-source probe above currently fails with `AssertionError: manifest.raw should be removed`, which is the exact cleanup this task is meant to complete.
