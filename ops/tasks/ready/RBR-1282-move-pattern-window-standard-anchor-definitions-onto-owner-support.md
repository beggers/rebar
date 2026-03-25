## RBR-1282: Move pattern-window standard anchor definitions onto owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining pattern-window standard-anchor definition block that still lives inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark layer keeps those pattern-boundary-specific definition objects beside the existing pattern-window selectors and signatures in `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` instead of centralizing that family in the generic standard-support file.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` so the existing owner-owned `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` tuple becomes the single owner of this full five-definition pattern-boundary family, in this exact order:
  - `pattern-window-positional-indexlike`
  - `pattern-window-keyword`
  - `pattern-boundary-bounded-wildcard`
  - `pattern-boundary-verbose-regression`
  - `pattern-boundary-wrong-text-model`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices that expanded `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` tuple into the overall `STANDARD_BENCHMARK_DEFINITIONS` inventory instead of defining the two `pattern-window-*` entries inline there.
- Preserve current behavior exactly:
  - keep the current definition order inside the full standard definition tuple;
  - keep the same manifest path, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, callback-result parity flags, and any other current definition metadata for both moved `pattern-window-*` entries; and
  - do not introduce a new benchmark-definition registry, compatibility alias, second pattern-boundary owner export, or another broker layer between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` should own the full pattern-boundary definition tuple because it already owns the adjacent pattern-window, bounded-wildcard, verbose-regression, and wrong-text-model selectors and signature helpers those definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the one place that assembles the full cross-domain standard definition inventory, but it should no longer carry the pattern-window-specific definition bodies themselves.
- Add focused coverage in `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` that pins the simplified owner boundary directly:
  - assert the owner module exports `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` with the exact five definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that owner-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="pattern-window-..."` definition literals; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(pattern-window-positional-indexlike|pattern-window-keyword)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer extending the existing `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` export over creating another pattern-boundary tuple or proxy helper. The point is to delete one remaining owner-specific block from the generic standard-support file, not to split one owner surface into smaller indirections.
- Keep imports direct and ordinary. If a tiny file-local builder detail is needed to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split.
- Do not change definition semantics, manifest inventories, anchor expectations, or benchmark scope in this task.

## Notes
- `RBR-1282` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the latest live task file is `RBR-1281` in `ops/tasks/done/`; and
  - `rg -n "RBR-1282|RBR-1283|RBR-1284|RBR-1285|RBR-12(8[0-9]|9[0-9])|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found only historical mentions inside older done-task notes, not a live reservation for `RBR-1282`.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the last `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/loop_state.json` shows no current environment issue or inherited-dirty retry state for either task worker.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` already owns `_is_pattern_window_positional_indexlike_workload`, `_pattern_window_positional_indexlike_correctness_case_signature`, `_pattern_window_positional_indexlike_workload_signature`, `_is_pattern_keyword_window_workload`, `_pattern_keyword_window_correctness_case_signature`, `_pattern_keyword_window_workload_signature`, and the existing lazy `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` export; and
  - `rg -n 'pattern-window-(positional-indexlike|keyword)' tests/benchmarks/standard_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py` matched only the inline definition names in `tests/benchmarks/standard_benchmark_anchor_support.py` in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `215 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `27 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `330 tests collected`; and
  - the negative `rg` check in `Verification` currently fails because the two `pattern-window-*` definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.
