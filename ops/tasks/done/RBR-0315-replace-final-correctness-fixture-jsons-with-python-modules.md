# RBR-0315: Replace the final correctness fixture JSONs with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and finish the correctness harness fixture-input migration by replacing the last two tracked correctness fixture JSONs with ordinary Python `MANIFEST` modules, then deleting the correctness-manifest `.json` loader branch that exists only to support those files.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_nested_replacement_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_workflows.py`
- `tests/conformance/test_correctness_fixture_inventory_contract.py`
- Delete `tests/conformance/fixtures/conditional_group_exists_nested_replacement_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- Each targeted manifest becomes a one-manifest-per-file Python module exposing the same manifest id, suite id, defaults, case ids, case ordering, and case payloads that the deleted JSON file previously supplied, and no duplicate JSON copy of those two manifests remains in the tree.
- The converted manifests preserve the current checkout ids and case counts: `conditional-group-exists-nested-replacement-workflows` with `8` cases and `conditional-group-exists-quantified-alternation-workflows` with `10`.
- `DEFAULT_FIXTURE_PATHS` points at the two new `.py` files in the same ordering slots: `conditional_group_exists_nested_replacement_workflows.py` stays between `conditional_group_exists_alternation_replacement_workflows.py` and `conditional_group_exists_quantified_replacement_workflows.py`, and `conditional_group_exists_quantified_alternation_workflows.py` stays between `conditional_group_exists_quantified_workflows.py` and `quantified_alternation_conditional_workflows.py`.
- Because these are the last tracked correctness fixture JSONs under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py` no longer preserves a correctness-fixture `.json` loading branch; keep report JSON handling intact, but simplify fixture-manifest loading to the ordinary Python-module path and tighten `tests/conformance/test_correctness_fixture_inventory_contract.py` so the default registry accepts only `.py` fixture paths.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative coverage for the targeted manifests except for the fixture path extensions changing from `.json` to `.py`; the combined report remains `87` manifests, `787` total cases, `779` passes, `0` explicit failures, and `8` `unimplemented`.
- The existing verification surface still passes with the Python-backed fixtures and the `.py`-only correctness loader, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_fixture_inventory_contract`, `tests.conformance.test_correctness_manifest_loader_duplicate_contract`, `tests.conformance.test_python_fixture_manifest_contract`, `tests.conformance.test_correctness_conditional_group_exists_nested_replacement_workflows`, and `tests.conformance.test_correctness_conditional_group_exists_quantified_alternation_workflows`.
- The live JSON count decreases by exactly `2` relative to the current checkout baseline; in this checkout both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` start at `17` and should finish at `15`, with `rg --files -g '*.json' | wc -l` as the source of truth if the worker runs in a dirty tree where deleted tracked paths linger in `git ls-files`.

## Constraints
- Keep the scope to the two correctness manifests plus the now-dead correctness-loader and fixture-inventory cleanup that follows directly from converting them; do not convert report JSON, agent/config JSON, benchmark/report plumbing, or unrelated conformance fixtures in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still shows a stale pre-checkpoint JSON count of `25`, but the live checkout is already at `17`: `python3 scripts/rebar_ops.py status` reports `tracked_json_blob_count=17` and `tracked_json_blob_delta=-8`, and both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` currently agree at `17`.
- This is the last tracked correctness-fixture JSON block. After it lands, the remaining tracked JSON should be limited to ops agent/config/report files and published report artifacts, so later architecture burn-down can move out of `tests/conformance/fixtures/` and into harness/report plumbing.

## Completion Notes
- Replaced the last two tracked correctness fixture JSONs with one-manifest-per-file Python `MANIFEST` modules, preserved manifest ids/defaults/case ordering/payloads, and deleted the JSON originals.
- Repointed `DEFAULT_FIXTURE_PATHS` to the new `.py` fixtures in the same ordering slots and removed the correctness-fixture `.json` loader branch, so `load_fixture_manifest()` now accepts only Python fixture modules while report JSON handling stays unchanged.
- Tightened `tests/conformance/test_correctness_fixture_inventory_contract.py` to require `.py` fixture paths, regenerated `reports/correctness/latest.json`, and preserved the combined report totals at `87` manifests, `787` total cases, `779` passed, `0` failed, and `8` unimplemented. The converted fixture paths in the report now end in `.py`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`, and `PYTHONPATH=python .venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_correctness_manifest_loader_duplicate_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_correctness_conditional_group_exists_nested_replacement_workflows.py tests/conformance/test_correctness_conditional_group_exists_quantified_alternation_workflows.py` (`9` tests passed).
- Live JSON count is now `15` by `rg --files -g '*.json' | wc -l`; `git ls-files '*.json' | wc -l` still shows `17` in this dirty checkout until the harness commit records the deletions.
