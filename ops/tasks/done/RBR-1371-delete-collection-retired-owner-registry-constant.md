## RBR-1371: Delete collection retired owner registry constant

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the test-only `COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES` export from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so the collection benchmark owner module stops carrying bookkeeping that exists only to satisfy one ownership assertion and does not participate in runtime benchmark behavior.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Delete `COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so `test_collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias` no longer reads an exported retired-name registry from the owner module.
- Replace the registry-based assertion with direct checks that keep the same architectural contract narrow:
  - the collection owner still routes through `tests.benchmarks.benchmark_test_support`;
  - it still does not define a local `source_tree_support` alias or source-tree contract-builder surface; and
  - it still avoids reintroducing the specific shared-support names that matter to this route.
- Do not add a replacement registry, forwarding alias, or another exported bookkeeping constant elsewhere.
- Keep the cleanup structural only; do not change benchmark workload data, benchmark execution behavior, scorecard logic, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias'`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"`

## Constraints
- Prefer deleting the exported retired-name registry over moving it sideways or recreating it under another module.
- Keep the run bounded to this single test-only registry cleanup and the one support test that currently depends on it.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1371|RBR-1372|RBR-1373' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - A first probe into the remaining conditional-callable signature helpers on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` showed they are still owner-specific collection logic, not generic shared support, so that move was not a safe simplification target.
  - A second probe found `COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES` is referenced only by `tests/benchmarks/test_benchmark_test_support.py` and exists only to feed that ownership assertion.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias'` passed with `1 passed, 169 deselected in 0.17s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"` currently fails because the exported registry constant still exists, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"` currently fails because the support test still depends on that registry, and that failure belongs exactly to this cleanup

## Completion
- Removed `COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of moving it sideways.
- Rewrote the owner-surface assertion in `tests/benchmarks/test_benchmark_test_support.py` to pin the narrow contract directly: the module still routes through `tests.benchmarks.benchmark_test_support`, still avoids a local `source_tree_support` alias and `_SourceTreeContractBuilderSpec`, and still does not reintroduce the specific shared-support names that matter to this route.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_support_reaches_source_tree_owner_surface_through_benchmark_test_support_alias'`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES\\s*=' tests/benchmarks/collection_replacement_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'COLLECTION_REPLACEMENT_SUPPORT_RETIRED_BENCHMARK_OWNER_NAMES' tests/benchmarks/test_benchmark_test_support.py"`
