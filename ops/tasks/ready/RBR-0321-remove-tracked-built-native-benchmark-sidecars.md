# RBR-0321: Remove the tracked built-native benchmark sidecars

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Delete the two remaining tracked built-native benchmark sidecar JSON blobs and the sidecar-specific README/reporting plumbing that exists only to point at them, so the repo keeps one tracked benchmark publication (`reports/benchmarks/latest.json`) plus strict on-demand built-native benchmark modes instead of a second stale checked-in report lane.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `scripts/rebar_ops.py`
- `tests/benchmarks/native_benchmark_test_support.py`
- `tests/benchmarks/test_built_native_benchmark_smoke.py`
- `tests/benchmarks/test_built_native_full_suite_benchmarks.py`
- `tests/python/test_readme_reporting.py`
- `README.md`
- `ops/state/current_status.md`
- `ops/state/backlog.md`
- `ops/state/decision_log.md`
- Delete `reports/benchmarks/native_smoke.json`
- Delete `reports/benchmarks/native_full.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` no longer defines tracked default paths for `reports/benchmarks/native_smoke.json` or `reports/benchmarks/native_full.json`, and `--native-smoke`, `--native-full`, `run_built_native_smoke_benchmarks()`, and `run_built_native_full_benchmarks()` stop auto-publishing to tracked sidecar files while still returning scorecards and still honoring an explicit caller-provided `report_path`.
- The strict built-native benchmark paths stay intact: they still require a real built native wheel, still fail loudly instead of falling back to the source-tree shim, and still support temporary or caller-selected report outputs for tests and ad hoc local runs.
- `scripts/rebar_ops.py` removes the native-sidecar existence probe and the README-rendering branch that links to `reports/benchmarks/native_full.json` / `reports/benchmarks/native_smoke.json`; the rendered benchmark status still makes clear that `reports/benchmarks/latest.json` is shim-backed and that built-native smoke/full coverage exists as strict benchmark modes rather than tracked sidecar artifacts.
- `README.md`, `ops/state/current_status.md`, `ops/state/backlog.md`, and `ops/state/decision_log.md` no longer describe tracked native sidecars as part of the current publication model. Update the directly coupled durable wording so it points at the remaining tracked benchmark report plus the existing strict built-native benchmark modes/tests instead of the deleted files.
- The built-native benchmark tests keep covering the strict failure path and scorecard contract entirely through temporary report paths under their existing `maturin` skip conditions. Add direct coverage that the native runners do not depend on tracked `reports/benchmarks/native_*.json` paths anymore.
- `reports/benchmarks/native_smoke.json` and `reports/benchmarks/native_full.json` are deleted, and both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` drop from `4` to `2`, leaving only `reports/benchmarks/latest.json` and `reports/correctness/latest.json` tracked in the repo.

## Constraints
- Keep the scope to the two tracked native sidecars and the directly coupled harness, test, README, and durable-state updates listed above; do not convert `reports/benchmarks/latest.json` or `reports/correctness/latest.json` in this run.
- Do not remove or weaken the built-native smoke/full benchmark entry points themselves; the simplification is deleting the checked-in sidecar publication lane, not deleting native benchmark coverage.
- Do not change benchmark workload semantics, scorecard schema, or regex behavior beyond the publication-path cleanup.

## Notes
- The live JSON count and the tracked JSON count currently agree at `4`, so there is no dashboard lag to account for in this checkout.
- `reports/benchmarks/latest.json` already points at the current `.py` workload manifests, while the tracked built-native sidecars still embed deleted `.json` workload paths and no longer reflect the live benchmark registry shape. That makes them stale duplicated artifacts, not a second trustworthy publication surface.
- This is the cleanest remaining JSON burn-down step that deletes report-specific plumbing instead of replacing those blobs with another tracked storage format.
