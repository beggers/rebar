# RBR-0009: Pin the exact CPython baseline metadata

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Record and publish the exact CPython `3.12.x` patch/build used by the initial correctness and benchmark harness runs instead of only the broader family line.

## Deliverables
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `tests/conformance/test_correctness_smoke.py`
- `tests/benchmarks/test_benchmark_smoke.py`
- `reports/correctness/latest.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The correctness and benchmark runners both emit baseline metadata that identifies the executing CPython interpreter more precisely than `3.12.x`, including at least the exact Python version and enough build/platform detail to distinguish patch-level drift.
- The tracked correctness and benchmark scorecards are regenerated so their published baseline metadata matches the runner output instead of a hand-written placeholder string.
- Smoke tests cover the metadata path so future scaffold changes cannot silently drop the exact-version pin from either report.
- The implementation still reports missing `rebar` functionality honestly; this task only improves baseline provenance and must not inflate parity or performance claims.

## Constraints
- Do not expand the fixture corpus or workload corpus in this task.
- Do not broaden the `rebar` API surface or claim regex support that does not exist yet.
- Derive the exact baseline from the interpreter running the harness rather than hard-coding a guessed patch/build string in multiple places.

## Notes
- This task depends on `RBR-0007` and `RBR-0008` having landed first; it is queued behind them so the worker sees it only after both harness scaffolds exist.
- Use `docs/testing/correctness-plan.md` and `docs/benchmarks/plan.md` for the expected report shapes.
- Keep the correctness and benchmark metadata schema aligned so README/report consumers can compare both scorecards without special cases.

## Completion
- Added `python/rebar_harness/metadata.py` so both harnesses derive the exact CPython baseline from the live interpreter in one place instead of duplicating patch/build metadata logic.
- Updated `python/rebar_harness/correctness.py` and `python/rebar_harness/benchmarks.py` to publish aligned baseline metadata including exact Python version, build tuple, compiler, platform, executable path, and `re` module identity.
- Regenerated `reports/correctness/latest.json` and `reports/benchmarks/latest.json` from the current `/usr/bin/python3` interpreter so the tracked scorecards now reflect the real CPython `3.12.3` baseline and build provenance.
- Expanded the correctness and benchmark smoke tests to lock the metadata path, and fixed the correctness runner to resolve CLI paths before writing reports so relative-path invocations regenerate the tracked scorecard cleanly.

## Follow-Up Notes
- Benchmark timing samples remain environment-dependent; future tasks should continue treating `reports/benchmarks/latest.json` as a point-in-time measurement artifact rather than a stable golden timing fixture.
