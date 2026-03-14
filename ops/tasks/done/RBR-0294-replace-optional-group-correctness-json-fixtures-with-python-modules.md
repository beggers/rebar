# RBR-0294: Replace the optional-group correctness JSON fixtures with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the remaining optional-group correctness manifests with ordinary Python fixture modules while preserving the published scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/optional_group_workflows.py`
- `tests/conformance/fixtures/optional_group_alternation_workflows.py`
- `tests/conformance/fixtures/optional_group_alternation_branch_local_backreference_workflows.py`
- Delete `tests/conformance/fixtures/optional_group_workflows.json`
- Delete `tests/conformance/fixtures/optional_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/optional_group_alternation_branch_local_backreference_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another loader, generator step, or package-discovery layer for this family.
- Each of the three targeted optional-group manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those three manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the three new `.py` files in the same ordering slots, so combined fixture inventory, `tests/conformance/correctness_expectations.py`, and `python -m rebar_harness.correctness --fixtures ...` continue to derive manifests from one path registry instead of a family-specific branch.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative optional-group case coverage for the targeted family except for the fixture path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed fixtures, including `tests.conformance.test_combined_correctness_scorecards` and `tests.conformance.test_correctness_optional_group_alternation_branch_local_backreference_workflows`.
- The live JSON file count decreases by exactly 3 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `76` to `73`.

## Constraints
- Keep the scope to these three optional-group correctness manifests; do not convert benchmark workloads, conditional-group manifests, or other correctness families in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline is already `76` because the checkout is dirty and the harness skipped auto-commit; verify reduction with `rg --files -g '*.json' | wc -l` until the staged deletions land.
- `optional_group_workflows.json` already carries the stabilized systematic optional-group slice inline, so keep that data as a plain checked-in `MANIFEST` module rather than reviving dedicated generator plumbing.
- The current worktree already contains separate uncommitted conditional-group and native-smoke manifest swaps; leave those out of scope instead of folding more in-flight cleanup into this task.

## Completion Notes
- Repointed the three optional-group entries in `python/rebar_harness/correctness.py` from `.json` to `.py` while keeping the existing shared `.json`/`.py` manifest loader path and validation flow unchanged.
- Replaced the three targeted JSON fixtures with one-manifest-per-file Python `MANIFEST` modules carrying the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads, then deleted the JSON originals.
- Regenerated `reports/correctness/latest.json`; the optional-group family kept the existing manifest ordering and aggregate `757` executed / `743` passed / `14` unimplemented summary, with the targeted fixture paths changing from `.json` to `.py` plus the regenerated timestamp.
- Verified with `PYTHONPATH=python python3 -m unittest tests.conformance.test_combined_correctness_scorecards tests.conformance.test_correctness_optional_group_alternation_branch_local_backreference_workflows`.
- Verified the live JSON count reduction as `76 -> 73` with `rg --files -g '*.json' | wc -l`.
