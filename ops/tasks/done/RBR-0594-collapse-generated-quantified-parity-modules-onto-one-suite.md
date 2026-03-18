# RBR-0594: Collapse the remaining generated quantified parity modules into one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace the two remaining generated quantified parity modules with one backend-parameterized pytest suite so this generated frontier stops repeating the same bundle loading, compile path, helper loop, and match-parity assertions across two near-identical files.

## Deliverables
- `tests/python/test_generated_quantified_parity_suite.py`
- Delete `tests/python/test_quantified_alternation_generated_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_quantified_generated_parity_suite.py`

## Acceptance Criteria
- The new suite covers exactly the five currently landed generated quantified slices now spread across the superseded modules:
  - bounded `{1,2}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_workflows.py`
  - broader-range `{1,3}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`
  - backtracking-heavy `{1,2}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`
  - quantified conditional from `tests/conformance/fixtures/conditional_group_exists_quantified_workflows.py`
  - quantified conditional alternation from `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_workflows.py`
- One local spec table in `tests/python/test_generated_quantified_parity_suite.py` owns the suite-specific metadata that is currently split across the two superseded modules:
  - fixture filename and expected manifest id;
  - the same ordered compile-case id tuples already declared in each superseded file;
  - the same expected pattern sets already declared in each superseded file;
  - the same expected operation-helper counts and text-model expectations already anchored by each current suite; and
  - the candidate-matrix metadata for each slice, including the existing quantified-alternation body-atom/depth builders, the existing quantified-conditional present-or-absent branch builders, the expected candidate count, and the current failure-prefix string.
- The consolidated suite preserves the current generated parity behavior exactly:
  - keep `HELPERS == ("search", "match", "fullmatch")`;
  - keep `WRAPPER_PAIRS == (("", ""), ("zz", ""), ("", "zz"), ("zz", "zz"))`;
  - keep `BODY_ATOMS == ("b", "c", "e")` plus the current `range(4)` and `range(5)` quantified-alternation candidate depths for the three quantified-alternation slices;
  - keep the current quantified-conditional and quantified-conditional-alternation candidate-text matrices built from the same present/absent capture choice plus the same branch-product choices;
  - keep the same bytes-versus-str candidate handling for the quantified-alternation slices, the same compile path through `compile_with_cpython_parity(...)`, and the same `assert_match_result_parity(...)`, convenience-API, valid-group-access, and invalid-group-access checks that the two current modules perform today; and
  - keep the current failure-preview truncation at twenty entries instead of widening or reformatting the failure surface.
- The consolidation stays on the existing fixture-backed parity path:
  - continue using `FixtureBundleSpec`, `load_fixture_bundles(...)`, `FixtureCase`, and the shared `regex_backend` fixture;
  - do not add a new helper module, code-generation step, or wrapper layer just to move the duplicated code elsewhere; and
  - do not widen scope into `tests/python/fixture_parity_support.py`, correctness fixtures, benchmarks, reports, Rust code, or `python/rebar/`.
- After the consolidation lands, `rg --files tests/python | rg 'test_(quantified_alternation|conditional_group_exists_quantified)_generated_parity_suite\\.py$'` returns no matches.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_generated_quantified_parity_suite.py`
  - `bash -lc "! rg --files tests/python | rg 'test_(quantified_alternation|conditional_group_exists_quantified)_generated_parity_suite\\.py$'"`

## Constraints
- Keep this task on the Python parity surface only. Do not change `python/rebar/`, `crates/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or queue/state files beyond this task file.
- Prefer one ordinary parametrized pytest module over two thin wrapper files or a new support package. The point is to delete duplicate harness code, not to move it behind another layer.
- Preserve the current generated text matrices, compile-case anchors, helper counts, and text-model expectations exactly so this remains a structural consolidation, not a feature or coverage change.

## Notes
- `RBR-0593` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active quantified-alternation conditional bytes benchmark task, so `RBR-0594` is the next available architecture id.
- No blocked architecture task exists to normalize first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` contain only `.gitkeep`;
  - `.rebar/runtime/dashboard.md` still reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `8ff528b40bd8def504999070d7d60c08a9abe62a` lags the live `git rev-parse HEAD` value `c93f559ebaf9434d03ce377896e9d32e7409ad22`, so the queue and JSON counts were cross-checked against the live checkout before seeding this task.
- JSON burn-down remains complete and aligned in tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicated generated-parity surface is concrete in the current checkout:
  - `tests/python/test_quantified_alternation_generated_parity_suite.py` and `tests/python/test_conditional_group_exists_quantified_generated_parity_suite.py` currently total `445` lines;
  - both files repeat the same `fixture_parity_support` import surface, a `GeneratedParitySpec` dataclass, `FIXTURE_BUNDLES` construction via `FixtureBundleSpec`, a manifest-id keyed spec lookup, the same `_record_match_failure(...)` helper, the same compile-through-`compile_with_cpython_parity(...)` flow, the same `HELPERS` loop, and the same pair of anchor tests; and
  - the only bounded differences are the per-slice metadata, the candidate-text builders, the helper-count and text-model expectations, and the failure-prefix strings that can sit in one spec table.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_generated_parity_suite.py tests/python/test_conditional_group_exists_quantified_generated_parity_suite.py` passes (`37 passed in 0.62s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_generated_quantified_parity_suite.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/python/test_generated_quantified_parity_suite.py`; and
  - `bash -lc "! rg --files tests/python | rg 'test_(quantified_alternation|conditional_group_exists_quantified)_generated_parity_suite\\.py$'"` currently fails exactly on this cleanup because both superseded files still exist.

## Completion Notes
- 2026-03-18: Added `tests/python/test_generated_quantified_parity_suite.py` with one local spec table covering the three quantified-alternation generated slices plus the quantified-conditional and quantified-conditional-alternation slices, while keeping the shared fixture-bundle loading, CPython compile path, helper loop, bytes-versus-str candidate handling, match/group parity assertions, and twenty-entry failure preview unchanged.
- 2026-03-18: Deleted `tests/python/test_quantified_alternation_generated_parity_suite.py` and `tests/python/test_conditional_group_exists_quantified_generated_parity_suite.py` after consolidating their metadata and candidate builders into the new suite.
- 2026-03-18 verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_generated_quantified_parity_suite.py` (`37 passed in 0.62s`)
  - `bash -lc "! rg --files tests/python | rg 'test_(quantified_alternation|conditional_group_exists_quantified)_generated_parity_suite\\.py$'"`
