# RBR-0492: Collapse the correctness loader onto one typed manifest/case surface

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining duplicated correctness-loader API so the harness, correctness expectation helpers, and fixture parity support stop carrying both `FixtureManifest` objects and separate `FixtureCase` lists for the same manifest data. The intended end state is one typed manifest surface whose `cases` are already `FixtureCase` records, with scorecard/report payloads staying unchanged.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_correctness_scorecard_registry_contract.py`
- `tests/conformance/test_python_fixture_manifest_contract.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` makes `FixtureManifest` the single loader return surface:
  - `FixtureManifest` stores typed `cases: list[FixtureCase]`, not a sibling loader return value;
  - `load_fixture_manifest(path: pathlib.Path)` returns `FixtureManifest`; and
  - `load_fixture_manifests(paths: Sequence[pathlib.Path])` returns `list[FixtureManifest]`.
- Duplicate-id validation remains intact after the loader collapse:
  - duplicate fixture manifest ids still raise the same `ValueError`;
  - duplicate fixture case ids across the selected manifests still raise the same `ValueError`; and
  - published fixture ordering and case ordering remain unchanged for the same fixture path selection.
- Correctness execution and scorecard expectation helpers stop threading a second manifest-case collection through the call graph:
  - `run_correctness_harness(...)` flattens typed cases from the returned manifests before evaluation;
  - the inventory and case-selection helpers in `tests/conformance/correctness_expectations.py` stop caching `(path, manifest, cases)` triples and instead read typed cases from `manifest.cases`; and
  - the conformance contract tests stop unpacking loader tuples and assert case ordering through `manifest.cases`.
- `tests/python/fixture_parity_support.py` preserves bundle ordering and selected-case lookup through `manifest.cases` instead of reparsing raw manifest rows into fresh `FixtureCase` objects:
  - `load_fixture_bundles(...)` and `load_published_fixture_bundles(...)` stop unpacking loader tuples;
  - `manifest_case_ids(...)` and `ordered_manifest_cases_from_bundles(...)` use typed manifest-owned cases rather than `FixtureCase.from_dict(bundle.manifest, raw_case)`; and
  - it is acceptable to keep the existing raw descriptor lookup helper local to `raw_fixture_cases_by_id(...)` if that is the smallest way to preserve descriptor-shape assertions in `tests/python/test_fixture_parity_support_contract.py`.
- Preserve published correctness behavior exactly:
  - keep fixture summary counts, manifest ordering, case ordering, suite summaries, diagnostics, representative case ids, and scorecard case payloads unchanged for the same selected fixtures; and
  - keep `reports/correctness/latest.py` format and semantics unchanged.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0492-correctness-loader-shape.py`
  - `rg -n 'def load_fixture_manifest\\(path: pathlib\\.Path\\) -> tuple\\[FixtureManifest, list\\[FixtureCase\\]\\]|def load_fixture_manifests\\(paths: Sequence\\[pathlib\\.Path\\]\\) -> tuple\\[list\\[FixtureManifest\\], list\\[FixtureCase\\]\\]|manifest, cases = load_fixture_manifest\\(|_, cases = load_fixture_manifest\\(|manifests, cases = load_fixture_manifests\\(|_, manifest_cases = load_fixture_manifest\\(|manifest, _ = load_fixture_manifest\\(' python/rebar_harness/correctness.py tests/conformance tests/python -g '*.py'`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from pathlib import Path
    from rebar_harness.correctness import load_fixture_manifest, load_fixture_manifests

    path = Path("tests/conformance/fixtures/grouped_alternation_replacement_workflows.py")
    manifest = load_fixture_manifest(path)
    assert not isinstance(manifest, tuple), type(manifest)
    assert manifest.manifest_id == "grouped-alternation-replacement-workflows"
    assert all(hasattr(case, "case_id") for case in manifest.cases)

    manifests = load_fixture_manifests([path])
    assert len(manifests) == 1
    assert manifests[0].manifest_id == "grouped-alternation-replacement-workflows"
    print("ok")
    PY
    ```

## Constraints
- Keep the cleanup structural only. Do not change files under `tests/conformance/fixtures/`, do not change `reports/correctness/latest.py`, README text, or tracked state files, and do not broaden into feature/frontier work already queued in `RBR-0491`.
- Prefer deleting the duplicated loader surfaces over adding compatibility wrappers. The end state should be one obvious typed loader API, not `load_fixture_manifest(...)` plus a second helper that preserves the old tuple shape.
- Do not broaden this task into benchmark-harness cleanup, correctness-fixture selector rewrites, or a raw-descriptor payload redesign. The cleanup target is the manifest/case definition flow inside the correctness harness and its direct consumers.

## Notes
- `RBR-0490` already made the benchmark side use one typed manifest/workload loader surface; this is the matching correctness-side follow-on now that JSON burn-down is complete.
- Rule 10 does not apply in the current checkout: `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `Last Cycle Anomalies: none`, while the last cycle completed both `RBR-0490` and `RBR-0489` cleanly.
- JSON-burn-down is complete, so this run moved to the next post-JSON simplification lane:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The old tuple-return correctness loader API still has 15 live signature/call-site matches across the harness and tests in the current checkout, which makes this a concrete deletion task rather than speculative cleanup.
- `tests/python/fixture_parity_support.py` also still has one `manifest.raw` lookup and one `FixtureCase.from_dict(bundle.manifest, raw_case)` reconstruction; the loader collapse should at minimum eliminate the typed-case reconstruction even if the raw descriptor helper remains.
- 2026-03-16 architecture probe:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance` passes in the current checkout (`12 passed, 1204 subtests passed in 25.17s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` passes in the current checkout (`99 passed in 0.12s`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/grouped_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0492-correctness-loader-shape.py` currently succeeds and reports `{"executed_cases": 8, "failed_cases": 0, "passed_cases": 8, "skipped_cases": 0, "total_cases": 8, "unimplemented_cases": 0}`.
  - The `rg -n ...` command above currently returns the old tuple signatures and tuple-unpack call sites, which is the exact surface this task should delete rather than wrap.
  - The typed-loader probe above currently fails with `AssertionError: <class 'tuple'>`, which is the exact public-shape cleanup this task is meant to complete.
