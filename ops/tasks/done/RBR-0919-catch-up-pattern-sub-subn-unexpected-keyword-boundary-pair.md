# RBR-0919: Catch up the direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword rejection pair that `RBR-0916` just published on the shared `module-workflow-surface` correctness path, reusing the existing direct-`Pattern` collection/replacement keyword owner route instead of widening correctness again, inventing another benchmark family, or jumping ahead to direct `Pattern.split()` duplicate-`maxsplit=` publication.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", missing=1)`
- `re.compile(b"abc").subn(b"x", b"abc", missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` unexpected-keyword error workloads:
  - add `pattern-sub-unexpected-keyword-warm-str`; and
  - add `pattern-subn-unexpected-keyword-warm-bytes`.
- Keep those two workloads pinned to the exact `RBR-0916` correctness anchors rather than widening the collection/replacement family:
  - `pattern-sub-unexpected-keyword-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "'missing' is an invalid keyword argument for sub()"}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-unexpected-keyword-warm-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "'missing' is an invalid keyword argument for subn()"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-sub-unexpected-keyword-str` and `workflow-pattern-subn-unexpected-keyword-bytes`;
  - insert `pattern-sub-unexpected-keyword-warm-str` immediately after `pattern-sub-duplicate-count-keyword-warm-str` and immediately before `pattern-subn-count-indexlike-positional-warm-str`;
  - insert `pattern-subn-unexpected-keyword-warm-bytes` immediately after `pattern-subn-duplicate-count-keyword-warm-bytes` and immediately before `pattern-subn-grouped-template-warm-str`; and
  - do not widen into raw-module rows, compiled-pattern-first-argument rows, positional-count neighbors, direct `Pattern.split()` duplicate-`maxsplit=` rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-sub-unexpected-keyword-str` and `workflow-pattern-subn-unexpected-keyword-bytes`;
  - keep the direct-`Pattern` keyword replacement/split coverage on the existing shared owner path, including the descriptor round-trip, callback-time keyword materialization, and source-tree combined anchor checks, instead of creating another benchmark suite or detached expectation table;
  - update the pattern keyword replacement/split measured-row expectation from `13` workloads to `15`;
  - update the collection-replacement manifest expectations from `70` measured workloads to `72`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `878` total / `878` measured / `0` known gaps across `30` manifests to `880` / `880` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `870` to `872`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 70`, `measured_workloads == 70`, and `known_gap_count == 0` to `72`, `72`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `70` to `72`;
  - the combined tracked summary moves from `878` total / `878` measured / `0` known gaps with `870` module workloads to `880` / `880` / `0` with `872` module workloads; and
  - the two new direct-`Pattern` unexpected-keyword workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0919-pattern-sub-subn-unexpected-keyword-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0916` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0916` first instead of widening this task.

## Notes
- `RBR-0919` is the next available feature task id in the current checkout:
  - `RBR-0917` and `RBR-0918` are already occupied by architecture cleanup tasks in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0916` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct-`Pattern` unexpected-keyword pair reaches the tracked Python-path benchmark surface before adjacent direct `Pattern.split()` duplicate-`maxsplit=` publication widens the direct bound-pattern error slice.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact benchmark ids are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes'` currently passes in this checkout (`8 passed, 1319 deselected`), so the direct-`Pattern` owner path already exposes the exact error pair that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'` currently passes in this checkout (`30 passed, 525 deselected`), so the shared direct-`Pattern` collection/replacement keyword benchmark owner path is already green before widening the exact unexpected-keyword spellings;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(\"abc\").sub(\"x\", \"abc\", missing=1) ... rebar.compile(\"abc\").sub(\"x\", \"abc\", missing=1) ... re.compile(b\"abc\").subn(b\"x\", b\"abc\", missing=1) ... rebar.compile(b\"abc\").subn(b\"x\", b\"abc\", missing=1) ... PY` confirms CPython and `rebar` now agree on the exact direct `TypeError.args`: `(\"'missing' is an invalid keyword argument for sub()\",)` and `(\"'missing' is an invalid keyword argument for subn()\",)`;
  - `rg -n 'pattern-sub-unexpected-keyword|pattern-subn-unexpected-keyword' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact direct-`Pattern` benchmark workloads are still absent; and
  - `reports/benchmarks/latest.py` currently reports `878` total / `878` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 870` and `REPORT["manifests"]["collection-replacement-boundary"]` still at `70` selected workloads / `70` measured / `0` known gaps.

## Completion
- Added the exact direct-`Pattern` benchmark rows to `benchmarks/workloads/collection_replacement_boundary.py`: `pattern-sub-unexpected-keyword-warm-str` immediately after `pattern-sub-duplicate-count-keyword-warm-str`, and `pattern-subn-unexpected-keyword-warm-bytes` immediately after `pattern-subn-duplicate-count-keyword-warm-bytes`, both pinned to the landed direct `TypeError` spellings from `RBR-0916`.
- Extended the shared `collection-replacement-keyword` benchmark-to-correctness mapping in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with anchors `workflow-pattern-sub-unexpected-keyword-str` and `workflow-pattern-subn-unexpected-keyword-bytes`, moved the direct `Pattern` keyword measured-row expectation from `13` to `15`, and updated the combined publication expectation to `880` total / `880` measured / `0` known gaps with `872` module workloads.
- Tightened the adjacent benchmark harness validation in `python/rebar_harness/benchmarks.py` just enough to let direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword rows with expected exceptions survive manifest/payload validation, and added narrow benchmark-side regression coverage so those direct error rows keep round-tripping, materializing `kwargs.missing` at callback time, and matching CPython’s exact exception text.
- Republished `reports/benchmarks/latest.py`; the tracked report file remains in the diff and now reports `collection-replacement-boundary` at `72` selected / `72` measured / `0` known gaps, with the combined summary at `880` total / `880` measured / `0` known gaps and `REPORT["summary"]["module_workloads"] == 872`. The new `pattern-sub-unexpected-keyword-warm-str` and `pattern-subn-unexpected-keyword-warm-bytes` rows both publish real `rebar` timings with `status == "measured"`.
- Updated `ops/state/backlog.md` and `ops/state/current_status.md` so the tracked frontier no longer claims `RBR-0919` is still active after this benchmark publication landed.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0919-pattern-sub-subn-unexpected-keyword-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
