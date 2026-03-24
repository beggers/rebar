# RBR-1222: Move collection-replacement indexlike contracts onto dedicated suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining collection-replacement positional-indexlike manifest and callback-time materialization contract block that still lives inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing collection-replacement keyword contract owner, so the giant combined benchmark suite stops owning another collection-replacement contract surface.

## Deliverables
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` so it becomes the owner for the current positional-indexlike contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests out of the combined suite without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation`
  - `test_collection_replacement_indexlike_descriptors_materialize_on_each_helper_call`
  - `test_pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor`
- Keep the extracted positional-indexlike surface pinned to current live behavior exactly:
  - preserve the current six-row manifest round-trip coverage for `module.split`, `module.sub`, `module.subn`, `pattern.split`, `pattern.sub`, and `pattern.subn`, including the same encoded `{"type": "indexlike", "value": 2}` payloads and the same `run_benchmark_workload_with_cpython(...)` result expectations;
  - preserve the callback-time materialization contract exactly for those same six rows, including the current `build_callable(...)` path, the repeated callback invocation behavior, and the same two-entry observed-field-name expectations for `maxsplit` and `count`; and
  - preserve the current implicit-zero `pattern.split` anchor normalization expectation for `pattern-split-no-match-warm-str`, including the exact signature tuple `("pattern.split", "abc", ("zzz",), (), 0, "str")`.
- Reuse existing collection-replacement support instead of inventing another layer:
  - keep `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` as the dedicated owner for this extracted block;
  - if the split-signature normalization check needs shared helper access outside the combined suite, source that helper from the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` path rather than importing the giant combined suite into the dedicated suite; and
  - do not add a new `*_support.py` module, a new sibling benchmark contract suite, or wrappers/aliases left behind in the combined suite.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving duplicate copies behind.
- Keep this cleanup structural and bounded to the three files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation or collection_replacement_indexlike_descriptors_materialize_on_each_helper_call or pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor'`
- `bash -lc "! rg -n 'def test_(standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation|collection_replacement_indexlike_descriptors_materialize_on_each_helper_call|pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1222` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1222|RBR-1223|RBR-1224|RBR-1225" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical notes in done-task files and did not reveal a live reservation or sibling task at `RBR-1222`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed `RBR-1221` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `11739` lines in this run, while `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` is `1940` lines;
  - `rg -n "def test_(standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation|collection_replacement_indexlike_descriptors_materialize_on_each_helper_call|pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` currently matches only the combined-suite block at lines `11220`, `11516`, and `11659`;
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` already owns the adjacent collection-replacement keyword and callback-time materialization contract surface; and
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` already owns the adjacent collection-replacement signature helpers, so this cleanup can reuse existing support instead of adding another architectural layer.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation or collection_replacement_indexlike_descriptors_materialize_on_each_helper_call or pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor'` currently fails exactly on this cleanup because the stranded combined-suite callback-time materialization test still references `_record_numeric_materialization_fields` after that helper ownership moved elsewhere (`6 failed, 2 passed, 212 deselected`);
  - the two passing selections in that same probe confirm the surrounding positional-indexlike contract surface is otherwise stable enough to extract; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those three tests still live in the combined suite.

## Completion
- Moved the positional-indexlike manifest round-trip, callback-time materialization, and implicit-zero `pattern.split` signature tests onto `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`.
- Added `_collection_replacement_pattern_split_workload_signature(...)` to `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so the dedicated suite can assert the split anchor contract without importing the combined suite.
- Deleted the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation or collection_replacement_indexlike_descriptors_materialize_on_each_helper_call or pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor'`
  - `bash -lc "! rg -n 'def test_(standard_benchmark_manifest_preserves_indexlike_numeric_descriptors_until_helper_invocation|collection_replacement_indexlike_descriptors_materialize_on_each_helper_call|pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
