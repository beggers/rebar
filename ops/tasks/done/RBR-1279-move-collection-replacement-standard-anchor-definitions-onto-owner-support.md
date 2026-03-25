## RBR-1279: Move collection-replacement standard anchor definitions onto owner support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining collection-replacement standard-anchor definition block that still lives inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark layer keeps those owner-specific definition objects beside the existing collection-replacement selectors, routes, and signature helpers in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of centralizing that whole family in the generic standard-support file.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so it becomes the single owner of a support-owned tuple named `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS` covering this exact collection-replacement definition family currently built inline in `tests/benchmarks/standard_benchmark_anchor_support.py`:
  - `collection-replacement-module-positional-indexlike`
  - `collection-replacement-keyword`
  - `collection-replacement-compiled-pattern-literal-success`
  - `collection-replacement-compiled-pattern-wrong-text-model`
  - `pattern-helper-collection-replacement-wrong-text-model`
  - `collection-replacement-pattern-findall-bounded`
  - `collection-replacement-pattern-finditer-bounded`
  - `collection-replacement-pattern-split`
  - `collection-replacement-module-literal-replacement`
  - `collection-replacement-pattern-literal-replacement`
  - `collection-replacement-grouped-callable-replacement`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS` into the overall `STANDARD_BENCHMARK_DEFINITIONS` inventory instead of defining those eleven collection-replacement entries inline there.
- Preserve current behavior exactly:
  - keep the current definition order inside the full standard definition tuple;
  - keep the same manifest paths, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, callback-result parity flags, and any excluded/special workload metadata for all moved definitions; and
  - do not introduce a new benchmark-definition registry, code generator, compatibility alias, or another broker module between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` should own the collection-replacement definition tuple because it already owns the adjacent route, selector, workload-id, and signature logic those definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the one place that assembles the full cross-domain standard definition inventory, but it should no longer carry the collection-replacement-specific definition bodies themselves.
- Add focused coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` that pins the new owner boundary directly:
  - assert the owner module exports `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS` with the exact eleven definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that support-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="collection-replacement-..."` definition literals for the moved family; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(collection-replacement-module-positional-indexlike|collection-replacement-keyword|collection-replacement-compiled-pattern-literal-success|collection-replacement-compiled-pattern-wrong-text-model|pattern-helper-collection-replacement-wrong-text-model|collection-replacement-pattern-findall-bounded|collection-replacement-pattern-finditer-bounded|collection-replacement-pattern-split|collection-replacement-module-literal-replacement|collection-replacement-pattern-literal-replacement|collection-replacement-grouped-callable-replacement)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the definition bodies onto the existing collection-replacement owner module over introducing another shared helper layer. The point is to delete one remaining owner-specific block from the generic standard-support file, not to create a fresh registry abstraction.
- Keep imports direct and ordinary. If you need a tiny local factory or lazy import to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split or proxy object.
- Do not change definition semantics, manifest inventories, anchor expectations, or benchmark scope in this task.

## Notes
- `RBR-1279` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1279|RBR-1280|RBR-1281|RBR-1282|RBR-1283" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found only historical mentions inside older done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently stalled:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no last-cycle anomalies; and
  - the latest recorded cycle finished both `architecture-implementation` and `feature-implementation` tasks as `done`.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/standard_benchmark_anchor_support.py` is `1881` lines in this run and still defines the entire collection-replacement standard-anchor family inline;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `1646` lines and already owns the adjacent collection-replacement routes, selectors, workload inventories, and signature helpers those definitions depend on;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` is `411` lines; and
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `2782` lines.
- The live checkout still centralizes those eleven definitions in the generic standard-support file:
  - `rg -n 'collection-replacement-(module-positional-indexlike|keyword|compiled-pattern-literal-success|compiled-pattern-wrong-text-model|pattern-findall-bounded|pattern-finditer-bounded|pattern-split|module-literal-replacement|pattern-literal-replacement|grouped-callable-replacement)' tests/benchmarks/standard_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/standard_benchmark_anchor_support.py` for the definition names in this run, plus one existing grouped-callable assertion in the collection-replacement owner suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `203 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `58 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `349 tests collected`; and
  - the negative `rg` check in `Verification` currently fails because the collection-replacement definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.

## Completion
- 2026-03-25: Moved the 11 collection-replacement standard benchmark definition objects onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` behind the exported owner-owned `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS` tuple, spliced that tuple back into `tests/benchmarks/standard_benchmark_anchor_support.py` in the same order, and added focused tests that pin the exported order, object reuse, and the absence of inline collection-replacement `name="..."` literals in the central standard-support source.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `bash -lc "! rg -n 'name=\"(collection-replacement-module-positional-indexlike|collection-replacement-keyword|collection-replacement-compiled-pattern-literal-success|collection-replacement-compiled-pattern-wrong-text-model|pattern-helper-collection-replacement-wrong-text-model|collection-replacement-pattern-findall-bounded|collection-replacement-pattern-finditer-bounded|collection-replacement-pattern-split|collection-replacement-module-literal-replacement|collection-replacement-pattern-literal-replacement|collection-replacement-grouped-callable-replacement)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`
