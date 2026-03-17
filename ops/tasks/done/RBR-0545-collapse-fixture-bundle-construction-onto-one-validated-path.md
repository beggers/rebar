# RBR-0545: Collapse fixture-bundle construction onto one validated path

Status: done
Owner: architecture-implementation
Created: 2026-03-17
Completed: 2026-03-17

## Goal
- Remove the last duplicated `FixtureBundle` construction path in `tests/python/fixture_parity_support.py` so whole-manifest and selected-case parity helpers materialize bundles through one shared builder instead of two hand-built constructors, and stop storing a second copy of each bundle's manifest id when the typed `FixtureManifest` already owns it.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` collapses the remaining duplicate bundle-build surface:
  - `load_fixture_bundles(...)` and `load_published_fixture_bundles(...)` both route through one shared private helper that owns `FixtureBundle` construction plus the existing derived defaults for `expected_case_ids` and `expected_text_models`;
  - `FixtureBundle` no longer stores `expected_manifest_id` as a dataclass field;
  - it is acceptable to keep a read-only `expected_manifest_id` property if that is the smallest way to preserve existing parity-suite call sites, but the value must be derived from `bundle.manifest.manifest_id` rather than stored twice; and
  - `load_fixture_bundles(...)` validates `FixtureBundleSpec.expected_manifest_id` against the loaded `FixtureManifest.manifest_id` before materializing a bundle and raises a clear `ValueError` on mismatch instead of silently storing the wrong expectation.
- Preserve existing parity-support behavior exactly:
  - bundle tuple order remains input order for both loaders;
  - selected-case bundles preserve the requested case-id order;
  - published whole-manifest bundles still keep `expected_case_ids is None`;
  - expected pattern sets, `(operation, helper)` counters, and text-model sets stay unchanged for the same inputs; and
  - do not change fixtures under `tests/conformance/fixtures/`.
- `tests/python/test_fixture_parity_support_contract.py` adds focused coverage for the validated shared builder path:
  - one happy-path check that `FixtureBundle` no longer stores `expected_manifest_id` as a dataclass field while the loaded bundle still exposes the manifest id through its live surface;
  - one mismatch check that `load_fixture_bundles(...)` now raises a clear `ValueError` when `FixtureBundleSpec.expected_manifest_id` disagrees with the actual manifest id; and
  - the existing whole-manifest and selected-case bundle contract coverage keeps passing without broadening into suite-specific behavior.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_public_surface_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from collections import Counter
    from dataclasses import fields
    from pathlib import Path

    from tests.python.fixture_parity_support import (
        FixtureBundle,
        FixtureBundleSpec,
        load_fixture_bundles,
        load_published_fixture_bundles,
    )

    assert "expected_manifest_id" not in {field.name for field in fields(FixtureBundle)}

    good_spec = FixtureBundleSpec(
        fixture_name="named_backreference_workflows.py",
        expected_manifest_id="named-backreference-workflows",
        expected_patterns=frozenset({r"(?P<word>ab)(?P=word)"}),
        expected_operation_helper_counts=Counter(
            {
                ("compile", None): 1,
                ("module_call", "search"): 1,
                ("pattern_call", "search"): 1,
            }
        ),
    )
    (bundle,) = load_fixture_bundles((good_spec,))
    assert bundle.manifest.manifest_id == "named-backreference-workflows"

    (published_bundle,) = load_published_fixture_bundles(
        (Path("tests/conformance/fixtures/named_backreference_workflows.py"),)
    )
    assert published_bundle.manifest.manifest_id == "named-backreference-workflows"

    bad_spec = FixtureBundleSpec(
        fixture_name="named_backreference_workflows.py",
        expected_manifest_id="wrong-manifest-id",
        expected_patterns=good_spec.expected_patterns,
        expected_operation_helper_counts=good_spec.expected_operation_helper_counts,
    )
    try:
        load_fixture_bundles((bad_spec,))
    except ValueError as exc:
        assert "expected_manifest_id" in str(exc) or "wrong-manifest-id" in str(exc)
    else:
        raise AssertionError("expected manifest-id mismatch failure")

    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup structural only. Do not change correctness fixtures, Rust code, `python/rebar/`, benchmark workloads, published reports, README text, or tracked state files outside this task.
- Prefer deleting duplicated bundle state and constructor logic over adding another wrapper layer, registry, or suite-specific helper.
- Do not broaden into parity-suite spec cleanup such as removing redundant `expected_case_ids=` declarations from individual test modules in the same run.

## Notes
- `RBR-0544` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned bytes parity follow-on, so `RBR-0545` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The duplicate bundle-construction surface is concrete in the current checkout:
  - `from dataclasses import fields; [field.name for field in fields(FixtureBundle)]` currently returns `['manifest', 'cases', 'expected_manifest_id', 'expected_patterns', 'expected_operation_helper_counts', 'expected_case_ids', 'expected_text_models']`;
  - a `FixtureBundleSpec` with `expected_manifest_id='wrong-manifest-id'` currently loads successfully and produces `bundle.expected_manifest_id == 'wrong-manifest-id'` while `bundle.manifest.manifest_id == 'named-backreference-workflows'`; and
  - `inspect.getsource(...)` currently shows both `load_fixture_bundles(...)` and `load_published_fixture_bundles(...)` still contain direct `FixtureBundle(` construction.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_public_surface_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` passes (`1129 passed in 0.89s`).
  - The inline probe in this task currently fails immediately at `assert "expected_manifest_id" not in {field.name for field in fields(FixtureBundle)}`, which is the exact redundant-field cleanup this task is meant to complete before the mismatch-validation branch can turn green.

## Completion
- Replaced the duplicate direct `FixtureBundle(...)` construction sites with one shared `_build_fixture_bundle(...)` helper that now owns bundle materialization, the existing `expected_case_ids` and `expected_text_models` defaults, and manifest-id validation for spec-backed loads.
- Removed `expected_manifest_id` from the `FixtureBundle` dataclass fields while preserving the existing `bundle.expected_manifest_id` surface as a read-only property derived from `bundle.manifest.manifest_id`.
- Added focused contract coverage for the derived manifest-id surface and the new manifest-id mismatch failure without changing parity-suite expectations or fixture contents.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_public_surface_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` (`1131 passed in 0.94s`)
- `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` task probe (`ok`)
