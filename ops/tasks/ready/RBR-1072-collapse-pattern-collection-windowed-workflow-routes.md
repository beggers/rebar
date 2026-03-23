# RBR-1072: Collapse pattern collection windowed workflow routes

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining hand-maintained bounded `Pattern.findall()`, `Pattern.finditer()`, and `Pattern.split()` workload/case pair tables in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the pattern collection/replacement windowed workflow surface derives its ordered workload ids, correctness anchors, and measured-row checks from one smaller same-file route instead of three adjacent copy-shaped tables.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these three standalone pair tables:
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_WORKLOAD_CASE_PAIRS`
  - `_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_WORKLOAD_CASE_PAIRS`
  - `_PATTERN_COLLECTION_REPLACEMENT_SPLIT_WORKLOAD_CASE_PAIRS`
- Replace that split with one explicit same-file route owner, or a strictly smaller equivalent, reused by all of these existing consumers:
  - `test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured`
  - `test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured`
  - `test_collection_replacement_manifest_keeps_pattern_split_rows_measured`
  - `_pattern_collection_replacement_bounded_findall_correctness_case_signature(...)`
  - `_pattern_collection_replacement_bounded_finditer_correctness_case_signature(...)`
  - `_pattern_collection_replacement_split_correctness_case_signature(...)`
  - `_is_collection_replacement_pattern_findall_bounded_workload(...)`
  - `_is_collection_replacement_pattern_finditer_bounded_workload(...)`
  - `_is_collection_replacement_pattern_split_workload(...)`
  - the standard benchmark anchor definitions named `collection-replacement-pattern-findall-bounded`, `collection-replacement-pattern-finditer-bounded`, and `collection-replacement-pattern-split`
- Keep the current bounded `Pattern.findall()` contract intact after the cleanup:
  - the routed workload ids still stay exactly, in order:
    - `pattern-findall-bounded-warm-str`
    - `pattern-findall-bounded-no-match-warm-str`
    - `pattern-findall-bounded-purged-bytes`
  - the routed correctness case ids still stay exactly, in order:
    - `pattern-findall-str-bounded`
    - `pattern-findall-str-bounded-no-match`
    - `pattern-findall-bytes-bounded`
  - `test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured` still proves the same three measured rows on the shared collection/replacement manifest.
- Keep the current bounded `Pattern.finditer()` contract intact after the cleanup:
  - the routed workload ids still stay exactly, in order:
    - `pattern-finditer-bounded-warm-str`
    - `pattern-finditer-bounded-no-match-warm-str`
    - `pattern-finditer-bounded-purged-bytes`
  - the routed correctness case ids still stay exactly, in order:
    - `pattern-finditer-str-bounded`
    - `pattern-finditer-str-bounded-no-match`
    - `pattern-finditer-bytes-bounded`
  - `test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured` still proves the same three measured rows on the shared collection/replacement manifest.
- Keep the current bounded `Pattern.split()` contract intact after the cleanup:
  - the routed workload ids still stay exactly, in order:
    - `pattern-split-no-match-warm-str`
    - `pattern-split-repeated-warm-str`
    - `pattern-split-maxsplit-purged-bytes`
  - the routed correctness case ids still stay exactly, in order:
    - `pattern-split-str-no-match`
    - `pattern-split-str-repeated`
    - `pattern-split-bytes-maxsplit`
  - `test_collection_replacement_manifest_keeps_pattern_split_rows_measured` still proves the same three measured rows on the shared collection/replacement manifest; and
  - `test_pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor` still proves the implicit-zero `maxsplit` normalization on `pattern-split-no-match-warm-str`.
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not widen into workload manifests, correctness fixtures, harness code, implementation code, reports, or tracked state prose in this run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection-replacement-pattern-bounded-findall or collection-replacement-pattern-bounded-finditer or collection-replacement-pattern-split or pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor'`
- `bash -lc "! rg -n '^_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_WORKLOAD_CASE_PAIRS\\b|^_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_WORKLOAD_CASE_PAIRS\\b|^_PATTERN_COLLECTION_REPLACEMENT_SPLIT_WORKLOAD_CASE_PAIRS\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the three parallel workload/case tables over introducing another support module, registry file, or generated artifact.
- Keep the existing workload ids, case ids, ordering, measured-row counts, and anchor coverage intact.
- Do not broaden this into direct literal replacement routing, bounded wildcard routes, compiled-pattern contract families, or feature work in this run.

## Notes
- `RBR-1072` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this file is added; and
  - `rg -n 'RBR-1072|RBR-1073|RBR-1074' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical notes inside done-task files, not a live reservation or task file for those ids.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `rg -n '_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_WORKLOAD_CASE_PAIRS|_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_WORKLOAD_CASE_PAIRS|_PATTERN_COLLECTION_REPLACEMENT_SPLIT_WORKLOAD_CASE_PAIRS|_pattern_collection_replacement_(bounded_findall|bounded_finditer|split)_' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns the three table definitions plus the measured-row assertions, correctness-signature builders, workload selectors, and anchor-contract definitions that still consume them directly.
- The focused benchmark slice is already green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection-replacement-pattern-bounded-findall or collection-replacement-pattern-bounded-finditer or collection-replacement-pattern-split'` returned `5 passed, 717 deselected, 3 subtests passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_split_workload_signature_normalizes_implicit_zero_maxsplit_to_match_correctness_anchor'` returned `1 passed, 721 deselected` in this run.
  - `bash -lc "rg -n '^_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDALL_WORKLOAD_CASE_PAIRS\\b|^_PATTERN_COLLECTION_REPLACEMENT_BOUNDED_FINDITER_WORKLOAD_CASE_PAIRS\\b|^_PATTERN_COLLECTION_REPLACEMENT_SPLIT_WORKLOAD_CASE_PAIRS\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` returned all three table definitions in this run.
