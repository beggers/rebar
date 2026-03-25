## RBR-1259: Move collection-replacement literal-replacement gap ownership onto dedicated support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining collection-replacement literal-replacement benchmark-gap ownership block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the giant combined benchmark broker stops owning checks and helper signatures that belong to the existing dedicated collection-replacement support surfaces.

## Deliverables
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these two inline benchmark-gap assertions out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome equivalent checks into `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`:
  - `test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit(...)`
  - `test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit(...)`
- Rehome the collection-replacement-owned literal-replacement signature helpers out of the combined suite and onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - `_collection_replacement_literal_replacement_correctness_case_signature(...)`
  - `_collection_replacement_literal_replacement_workload_signature(...)`
- Keep the moved gap assertions owned by the existing collection-replacement route surface rather than by the combined broker:
  - continue to derive the module lane from `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["module"]` plus `_COLLECTION_REPLACEMENT_MODULE_LITERAL_REPLACEMENT_SELECTOR`;
  - continue to derive the pattern lane from `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES["pattern"]` plus `_COLLECTION_REPLACEMENT_PATTERN_LITERAL_REPLACEMENT_SELECTOR`; and
  - continue to compare live published correctness-case signatures against live benchmark-workload signatures without introducing copied workload-id tables or another wrapper module.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the moved literal-replacement signature helpers from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, delete the two moved tests, and delete the now-local-only helper definitions.
- Preserve the current bounded behavior exactly:
  - the module literal-replacement gap set must remain empty;
  - the pattern literal-replacement gap set must remain empty;
  - the signature helpers must keep matching the current literal replacement route semantics for `sub()` and `subn()` across `str` and `bytes`; and
  - the combined suite must keep using the same helper behavior for the existing standard benchmark anchor definitions at the collection-replacement literal-replacement owner rows.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def test_collection_replacement_(module|pattern)_literal_replacement_benchmark_gap_stays_explicit|def _collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark files listed above.
- Prefer the existing collection-replacement support module and dedicated support suite over adding another broker test file, helper wrapper, or ownership layer.
- Preserve the live route usage, signature normalization behavior, and current empty-gap contract exactly.

## Notes
- `RBR-1259` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1259|RBR-1260|RBR-1261|RBR-1262" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -g '*.md'` found no reserved follow-on ids in this range outside historical note references.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `10574` lines in this run;
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `1327` lines; and
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `869` lines.
- The target block is still uniquely inline in the combined suite in this run:
  - `rg -n 'test_collection_replacement_(module|pattern)_literal_replacement_benchmark_gap_stays_explicit' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - `rg -n '_collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `38 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `128 tests collected`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit or collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit'` passed with `2 passed, 88 deselected`.
  - `bash -lc "! rg -n 'def test_collection_replacement_(module|pattern)_literal_replacement_benchmark_gap_stays_explicit|def _collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the two gap tests and two helper definitions still live inline in the combined suite, and that failure belongs to the exact cleanup queued here.

## Completion
- 2026-03-25: Moved the collection-replacement literal-replacement signature helpers into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, rehomed the two literal-replacement gap assertions into `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, and removed the duplicated inline ownership from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `40 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `128 tests collected`.
  - `bash -lc "! rg -n 'def test_collection_replacement_(module|pattern)_literal_replacement_benchmark_gap_stays_explicit|def _collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.
