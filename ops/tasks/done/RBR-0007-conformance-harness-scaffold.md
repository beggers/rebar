# RBR-0007: Scaffold the correctness conformance harness

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Create the first runnable differential correctness harness skeleton and publish an initial placeholder correctness scorecard.

## Deliverables
- `python/rebar_harness/__init__.py`
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/parser_smoke.json`
- `tests/conformance/test_correctness_smoke.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The harness can load versioned fixture records and run at least one compile-oriented smoke case through a structured observation pipeline against CPython stdlib `re`.
- The `rebar` side is represented by an explicit adapter boundary that can report `unimplemented` or equivalent placeholder outcomes without faking passing parity.
- `reports/correctness/latest.json` uses the top-level scorecard shape from `docs/testing/correctness-plan.md` and publishes honest counts for executed, skipped, or unimplemented cases.
- A smoke test or documented command exercises the runner end to end and regenerates the tracked scorecard.

## Constraints
- Keep this to the Phase 0 harness skeleton from the correctness plan; do not build a large corpus yet.
- Do not claim module or parser parity for behaviors the scaffold cannot execute.
- Keep the baseline pinned only to CPython `3.12.x` family metadata for now; exact patch-level pinning remains a follow-up after the runner exists.

## Notes
- Use `docs/testing/correctness-plan.md` as the primary task spec.
- Use `docs/spec/drop-in-re-compatibility.md` and `docs/spec/syntax-scope.md` to decide which fields the fixture and observation format must preserve.
- Keep the runner shape compatible with the benchmark harness plan in `docs/benchmarks/plan.md` so shared harness utilities can emerge later instead of two unrelated one-off scripts.

## Completion
- Added `python/rebar_harness/correctness.py` as a Phase 0 correctness runner with a versioned fixture loader, structured CPython/rebar adapter observations, explicit `unimplemented` handling, and JSON scorecard writing.
- Added `tests/conformance/fixtures/parser_smoke.json` plus `tests/conformance/test_correctness_smoke.py` to exercise compile success and compile failure cases end to end.
- Published the initial placeholder scorecard in `reports/correctness/latest.json` with honest `unimplemented` counts for the current scaffold-only `rebar` adapter.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.correctness` and `python3 -m unittest tests.conformance.test_correctness_smoke tests.python.test_import_rebar`.

## Follow-Up Notes
- Phase 1 should add generated parser fixture families, `bytes` cases, and parity comparisons beyond the current compile-only placeholder path.
