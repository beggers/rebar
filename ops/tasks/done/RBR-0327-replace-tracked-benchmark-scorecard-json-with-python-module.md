# RBR-0327: Replace the tracked benchmark scorecard JSON with a Python module

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Remove the final tracked JSON blob by moving the published benchmark scorecard from `reports/benchmarks/latest.json` to an ordinary Python report module, while keeping explicit temporary `.json` scorecard outputs available for narrow benchmark runs, tests, and ad hoc local checks.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `scripts/rebar_ops.py`
- `ops/reporting/readme.py`
- `README.md`
- `docs/benchmarks/plan.md`
- `ops/agents/feature_planning.md`
- `ops/state/current_status.md`
- `ops/state/backlog.md`
- `ops/state/decision_log.md`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/python/test_readme_reporting.py`
- `reports/benchmarks/latest.py`
- Delete `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` changes the tracked default report path from `reports/benchmarks/latest.json` to `reports/benchmarks/latest.py`, and the tracked publication becomes a data-only Python module exposing one top-level `REPORT` dict with the current benchmark-scorecard schema and payload.
- The benchmark harness supports mixed-format scorecard I/O by extension: explicit caller-selected temporary `.json` report paths still work for narrow or task-local runs, while the exact retired tracked path `reports/benchmarks/latest.json` is rejected with a clear error that points callers at `reports/benchmarks/latest.py` for the published scorecard or another non-tracked `.json` path for scratch output.
- The regenerated `reports/benchmarks/latest.py` preserves the current published benchmark payload aside from the path extension and regenerated timestamp: keep the same suite id, manifest ids and ordering, workload ids and ordering, baseline and implementation metadata, artifact manifest ordering, and combined summary totals as the deleted tracked JSON scorecard from the current checkout.
- `scripts/rebar_ops.py` and `ops/reporting/readme.py` stop hard-coding the deleted benchmark JSON path. The README status renderer and scorecard lookups load `reports/benchmarks/latest.py` through the existing structured-report path without adding a benchmark-only loader or second publication lane.
- `README.md`, `docs/benchmarks/plan.md`, `ops/agents/feature_planning.md`, and the current benchmark-publication guidance in `ops/state/current_status.md`, `ops/state/backlog.md`, and `ops/state/decision_log.md` all point operators and agents at `reports/benchmarks/latest.py` instead of the deleted tracked JSON path. Keep this bounded to active guidance and live publication references; do not churn historical completion bullets just because they mention earlier `.json` publications.
- The benchmark regression surface no longer assumes the tracked published scorecard lives at `reports/benchmarks/latest.json`: update `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/python/test_readme_reporting.py` so they cover the `.py` publication path while keeping their temporary benchmark runs on disposable `.json` files where that remains simpler.
- The mixed-format publication model still passes the directly coupled verification surface, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, `tests.python.test_readme_reporting`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`, and `./.venv/bin/python scripts/rebar_ops.py report`.
- The live tracked JSON count decreases by exactly `1`: both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` currently agree at `1` in this clean checkout and should finish at `0`, leaving no tracked JSON files in the repo. If the worker lands the deletion in an unstaged worktree where `git ls-files` lags, treat `rg --files -g '*.json' | wc -l` as the live source of truth until the harness commit records the removal.

## Constraints
- Keep the scope to the published benchmark scorecard, the directly coupled loader/writer path, the directly coupled README/state/prompt references, and the benchmark/reporting tests that still hard-code the tracked benchmark report path.
- Do not remove general `.json` scorecard support for temporary benchmark outputs; the cleanup is only about eliminating the tracked `reports/benchmarks/latest.json` publication slot.
- Do not change benchmark workloads, scorecard schema, correctness publications, runtime JSON artifacts under `.rebar/`, or regex behavior in this run.
- Prefer one plain Python report module plus shared mixed-format scorecard helpers over adding a generator format, compatibility shim JSON file, or separate benchmark-only report abstraction.

## Notes
- `.rebar/runtime/dashboard.md` is current in this checkout: it reports `tracked_json_blob_count: 1`, `tracked_json_blob_delta: -1`, a clean worktree, and no last-cycle anomalies.
- Live counts match the runtime report here: `git ls-files '*.json'` and `rg --files -g '*.json'` both list only `reports/benchmarks/latest.json`.
- `python/rebar_harness/benchmarks.py` already loads `.py` workload manifests and `scripts/rebar_ops.py` already reads structured `.py` or `.json` dict payloads, so this migration should reuse those existing patterns instead of inventing a second benchmark-specific format layer.

## Completion Notes
- 2026-03-14: Changed `python/rebar_harness.benchmarks` to publish `reports/benchmarks/latest.py` by default, added mixed `.py`/`.json` scorecard read-write support with an explicit rejection of the retired `reports/benchmarks/latest.json` path, and updated `scripts/rebar_ops.py`, README/reporting config, docs, state guidance, and the directly coupled benchmark/reporting tests to consume the Python-backed publication.
- Regenerated `reports/benchmarks/latest.py` from the pre-migration published payload, deleted `reports/benchmarks/latest.json`, and verified the load-bearing migration contract by comparing the restored `.py` scorecard against the saved JSON payload for suite id, summary totals, baseline metadata, implementation metadata, artifact manifest ordering, and workload ordering.
- Verification: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/python/test_readme_reporting.py` passed (`8` tests, `55` subtests). `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` passed. `./.venv/bin/python scripts/rebar_ops.py report` passed. `git diff --name-status -- reports/benchmarks/latest.json` reports `D`. `rg --files -g '*.json' | wc -l` is `0`, while `git ls-files '*.json' | wc -l` remains `1` in this unstaged worktree until the harness commit records the tracked deletion.
