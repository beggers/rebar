# RBR-0803: Collapse the benchmark selector expectation table onto live registry invariants

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the mirrored selector-filename table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; `BENCHMARK_SELECTOR_EXPECTATION_TABLE` and `BENCHMARK_SELECTOR_EXPECTATIONS` currently restate the same nondefault selector filenames that `python/rebar_harness/benchmarks.py` already owns in `_BENCHMARK_MANIFEST_FILENAMES_BY_SELECTOR`.
- Keep the benchmark selector contract coverage focused on durable invariants: declared selector constants, membership in the published full-suite inventory, published-order preservation, and real manifest-path validation, instead of maintaining a second handwritten filename registry in the test file.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or references:
  - `BENCHMARK_SELECTOR_EXPECTATION_TABLE`; or
  - `BENCHMARK_SELECTOR_EXPECTATIONS`.
- The selector contract coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still proves the shared benchmark selectors behave as expected, but without a second mirrored filename registry:
  - every declared nondefault `*_MANIFEST_SELECTOR` exported by `python/rebar_harness/benchmarks.py` is still exercised exactly once;
  - `select_benchmark_manifest_paths(selector)` still resolves to a non-empty, duplicate-free, published-order-preserving subset of `select_benchmark_manifest_paths(PUBLISHED_FULL_SUITE_MANIFEST_SELECTOR)` for each exercised nondefault selector; and
  - every resolved path still stays under `BENCHMARK_WORKLOADS_ROOT`, points at a real `.py` benchmark manifest, and remains part of the published full-suite selector inventory.
- Preserve the current higher-signal published-inventory coverage in the same file:
  - keep `test_default_benchmark_published_full_suite_selector_covers_tracked_manifests()`, `test_declared_benchmark_manifest_selectors_match_registry_keys()`, and `test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order()` intact in substance;
  - keep the built-native smoke selector covered through the shared invariant-based parametrization instead of a new one-off filename table;
  - keep the unknown-selector assertion intact; and
  - do not change `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, reports, README copy, or tracked project-state prose.
- Do not broaden into `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, anchor expectation cleanup, or other benchmark-contract rewrites in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selector or published_full_suite_manifest_selector or built_native_smoke_manifest_selector'`
  - `bash -lc "! rg -n '^(BENCHMARK_SELECTOR_EXPECTATION_TABLE|BENCHMARK_SELECTOR_EXPECTATIONS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the mirrored selector table over adding another shared selector helper, another duplicated filename registry, or another wrapper around `select_benchmark_manifest_paths(...)`.

## Notes
- `RBR-0803` is free in the current checkout:
  - `rg -n "RBR-0803|RBR-0804|RBR-0805" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returned no reserved or queued `RBR-0803`-series matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0803|^RBR-0804|^RBR-0805'` returned no conflicting live task files.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and isolated in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selector or published_full_suite_manifest_selector or built_native_smoke_manifest_selector'` currently passes (`6 passed, 172 deselected in 0.10s`);
  - `rg -n '^(BENCHMARK_SELECTOR_EXPECTATION_TABLE|BENCHMARK_SELECTOR_EXPECTATIONS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports only this file (`55:BENCHMARK_SELECTOR_EXPECTATION_TABLE = (` and `66:BENCHMARK_SELECTOR_EXPECTATIONS = tuple(`); and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness import benchmarks
import tests.benchmarks.test_source_tree_combined_boundary_benchmarks as mod
for selector, expected_filenames, _ in mod.BENCHMARK_SELECTOR_EXPECTATION_TABLE:
    resolved = tuple(path.name for path in benchmarks.select_benchmark_manifest_paths(selector))
    assert resolved == expected_filenames, (selector, resolved, expected_filenames)
print("ok")
PY` currently passes (`ok`), showing the handwritten table is a direct mirror of live selector resolution rather than an independent contract source.
- This is the benchmark-side follow-on to `RBR-0801`, which deleted the analogous correctness selector mirror; keeping the two selector contract owners aligned reduces one more piece of duplicated harness metadata without changing published behavior.
