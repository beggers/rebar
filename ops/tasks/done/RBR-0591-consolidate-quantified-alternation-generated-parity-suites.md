# RBR-0591: Consolidate the generated quantified-alternation parity modules into one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Replace the three generated quantified-alternation parity modules with one backend-parameterized pytest suite so this frontier stops repeating the same bundle loading, generated text-matrix construction, compile path, and match-parity assertions across three singleton files.

## Deliverables
- `tests/python/test_quantified_alternation_generated_parity_suite.py`
- Delete `tests/python/test_backtracking_heavy_quantified_alternation_generated_parity_suite.py`
- Delete `tests/python/test_bounded_quantified_alternation_generated_parity_suite.py`
- Delete `tests/python/test_broader_range_quantified_alternation_generated_parity_suite.py`

## Acceptance Criteria
- The new suite covers exactly the three currently landed generated quantified-alternation slices now spread across the superseded modules:
  - bounded `{1,2}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_workflows.py`
  - broader-range `{1,3}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`
  - backtracking-heavy `{1,2}` quantified alternation from `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`
- One local spec table in `tests/python/test_quantified_alternation_generated_parity_suite.py` owns the suite-specific metadata that is currently copied across the three modules:
  - fixture filename and expected manifest id;
  - the same ordered `EXPECTED_COMPILE_CASE_IDS` tuple already declared in each superseded file;
  - the same `EXPECTED_PATTERNS` set already declared in each superseded file; and
  - the generated-text depth and expected candidate count for each slice (`range(4)` and `160` for bounded, `range(5)` and `484` for broader-range and backtracking-heavy).
- The consolidated suite preserves the current generated parity behavior exactly:
  - keep `HELPERS == ("search", "match", "fullmatch")`;
  - keep `BODY_ATOMS == ("b", "c", "e")`;
  - keep `WRAPPER_PAIRS == (("", ""), ("zz", ""), ("", "zz"), ("zz", "zz"))`;
  - keep the same bytes-versus-str candidate-text handling, compile path through `compile_with_cpython_parity(...)`, and the same `assert_match_result_parity(...)`, convenience-API, valid-group-access, and invalid-group-access checks that the three current modules perform today; and
  - keep the current failure-preview truncation at twenty entries instead of widening or reformatting the failure surface.
- The consolidation stays on the existing fixture-backed parity path:
  - continue using `FixtureBundleSpec`, `load_fixture_bundles(...)`, `FixtureCase`, and the shared `regex_backend` fixture;
  - do not add a new helper module, code-generation step, or another wrapper layer just to move the duplicated code elsewhere; and
  - do not widen scope into `tests/python/test_quantified_alternation_parity_suite.py`, correctness fixtures, benchmarks, reports, Rust code, or `python/rebar/`.
- After the consolidation lands, `rg --files tests/python | rg 'test_(backtracking_heavy_quantified_alternation_generated|bounded_quantified_alternation_generated|broader_range_quantified_alternation_generated)_parity_suite\\.py$'` returns no matches.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_generated_parity_suite.py`
  - `bash -lc "! rg --files tests/python | rg 'test_(backtracking_heavy_quantified_alternation_generated|bounded_quantified_alternation_generated|broader_range_quantified_alternation_generated)_parity_suite\\.py$'"`

## Constraints
- Keep this task on the Python parity surface only. Do not change `python/rebar/`, `crates/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or queue/state files beyond this task file.
- Prefer one ordinary parametrized pytest module over three thin wrapper files or a new support package. The point is to delete duplicate harness code, not to move it behind another layer.
- Preserve the current compile-case anchors and generated text matrices exactly so this remains a structural consolidation, not a feature or coverage change.

## Notes
- `RBR-0590` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active quantified-alternation conditional bytes publication task, so `RBR-0591` is the next available architecture id.
- No blocked architecture task exists to normalize first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `0e29f41827f679b1aad98413b2343fad49655fd7` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and aligned in tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicated generated-harness surface is concrete in the current checkout:
  - `tests/python/test_backtracking_heavy_quantified_alternation_generated_parity_suite.py`, `tests/python/test_bounded_quantified_alternation_generated_parity_suite.py`, and `tests/python/test_broader_range_quantified_alternation_generated_parity_suite.py` currently total `454` lines;
  - all three files repeat the same `HELPERS`, `BODY_ATOMS`, and `WRAPPER_PAIRS` constants, the same `_candidate_texts(...)` helper, the same `_record_match_failure(...)` helper, the same bundle-contract anchor test shape, and the same generated text-matrix parity test shape; and
  - the only bounded differences are fixture metadata, the ordered compile-case ids and pattern sets already declared in each file, the candidate-text depth (`range(4)` versus `range(5)`), and the failure-prefix string.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_backtracking_heavy_quantified_alternation_generated_parity_suite.py tests/python/test_bounded_quantified_alternation_generated_parity_suite.py tests/python/test_broader_range_quantified_alternation_generated_parity_suite.py` passes (`27 passed in 0.54s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_generated_parity_suite.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/python/test_quantified_alternation_generated_parity_suite.py`; and
  - `bash -lc "! rg --files tests/python | rg 'test_(backtracking_heavy_quantified_alternation_generated|bounded_quantified_alternation_generated|broader_range_quantified_alternation_generated)_parity_suite\\.py$'"` currently fails exactly on this cleanup because all three superseded files still exist.

## Completion
- 2026-03-18: Added `tests/python/test_quantified_alternation_generated_parity_suite.py` with one local generated-slice spec table covering the bounded `{1,2}`, broader-range `{1,3}`, and backtracking-heavy `{1,2}` quantified-alternation compile bundles, while keeping the shared `HELPERS`, `BODY_ATOMS`, `WRAPPER_PAIRS`, CPython compile path, bytes-versus-str candidate handling, parity assertions, and twenty-entry failure preview unchanged.
- 2026-03-18: Deleted `tests/python/test_backtracking_heavy_quantified_alternation_generated_parity_suite.py`, `tests/python/test_bounded_quantified_alternation_generated_parity_suite.py`, and `tests/python/test_broader_range_quantified_alternation_generated_parity_suite.py` after moving their duplicated generated text-matrix parity logic into the consolidated fixture-backed suite.

## Verification
- 2026-03-18: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_generated_parity_suite.py` (`27 passed in 0.54s`)
- 2026-03-18: `bash -lc "! rg --files tests/python | rg 'test_(backtracking_heavy_quantified_alternation_generated|bounded_quantified_alternation_generated|broader_range_quantified_alternation_generated)_parity_suite\\.py$'"` (no matches)
