## RBR-1280: Move pattern-boundary standard anchor definitions onto owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining pattern-boundary standard-anchor definition block that still lives inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark layer keeps those owner-specific definition objects beside the existing pattern-boundary selectors, signatures, and wrong-text-model support in `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` instead of centralizing that family in the generic standard-support file.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` so it becomes the single owner of a support-owned tuple named `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` covering this exact pattern-boundary definition family currently built inline in `tests/benchmarks/standard_benchmark_anchor_support.py`:
  - `pattern-boundary-bounded-wildcard`
  - `pattern-boundary-verbose-regression`
  - `pattern-boundary-wrong-text-model`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` into the overall `STANDARD_BENCHMARK_DEFINITIONS` inventory instead of defining those three pattern-boundary entries inline there.
- Preserve current behavior exactly:
  - keep the current definition order inside the full standard definition tuple;
  - keep the same manifest path, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, and callback-result parity flags for all moved definitions; and
  - do not introduce a new registry, generator, compatibility alias, or another broker layer between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` should own the pattern-boundary definition tuple because it already owns the adjacent bounded-wildcard, verbose-regression, and wrong-text-model selectors and signature helpers those definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the one place that assembles the full cross-domain standard definition inventory, but it should no longer carry the pattern-boundary-specific definition bodies themselves.
- Add focused coverage in `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` that pins the new owner boundary directly:
  - assert the owner module exports `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` with the exact three definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that support-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="pattern-boundary-..."` definition literals for the moved family; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(pattern-boundary-bounded-wildcard|pattern-boundary-verbose-regression|pattern-boundary-wrong-text-model)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the definition bodies onto the existing pattern-boundary owner module over introducing another shared helper layer. The point is to delete one remaining owner-specific block from the generic standard-support file, not to create a fresh registry abstraction.
- Keep imports direct and ordinary. If you need a tiny local factory or lazy import to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split or proxy object.
- Do not change definition semantics, manifest inventories, anchor expectations, or benchmark scope in this task.

## Notes
- `RBR-1280` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1280|RBR-1281|RBR-1282|RBR-1283|RBR-1284" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found only historical mentions inside older done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the last `architecture-implementation` run finished `done`; and
  - the only recorded anomaly in the latest dashboard snapshot is a `qa-testing` nonzero exit, not inherited-dirty checkpoint churn or a post-task refresh/commit stall on the shared ready queue.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` already owns the bounded-wildcard selectors/signatures, verbose-regression selectors/signatures, and wrong-text-model support helpers that the remaining standard definitions depend on; and
  - `rg -n 'name=\"(pattern-boundary-bounded-wildcard|pattern-boundary-verbose-regression|pattern-boundary-wrong-text-model)\"' tests/benchmarks/standard_benchmark_anchor_support.py` matched only `tests/benchmarks/standard_benchmark_anchor_support.py` in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `205 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `25 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `318 tests collected`; and
  - the negative `rg` check in `Verification` currently fails because those three pattern-boundary definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.
