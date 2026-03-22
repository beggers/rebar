# RBR-0900: Catch up the compiled-pattern module `sub()`/`subn()` bool-count complement boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact compiled-pattern-first-argument bool-count complement pair that `RBR-0898` publishes on the shared `module-workflow-surface` correctness path, reusing the existing compiled-pattern keyword-carrier owner route instead of widening the correctness surface again, inventing another benchmark family, or reopening unrelated collection/replacement helpers.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abcabc", count=False)`
- `re.subn(re.compile(b"abc"), b"x", b"abcabc", count=True)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument bool-count complement workloads:
  - add `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`; and
  - add `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact `RBR-0898` correctness anchors rather than inventing a broader helper family:
  - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `use_compiled_pattern == True`, and `kwargs == {"count": False}`;
  - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `use_compiled_pattern == True`, and `kwargs == {"count": True}`;
  - anchor the two workloads to `workflow-module-sub-count-bool-false-str-compiled-pattern` and `workflow-module-subn-count-bool-true-bytes-compiled-pattern`;
  - insert `module-sub-count-bool-false-keyword-warm-str-compiled-pattern` immediately after `module-sub-count-bool-keyword-warm-str-compiled-pattern` and immediately before `module-sub-on-bytes-string-warm-str-compiled-pattern`;
  - insert `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern` immediately after `module-subn-count-bool-keyword-purged-bytes-compiled-pattern` and immediately before `module-subn-on-str-string-purged-bytes-compiled-pattern`; and
  - do not widen into raw-module bool carriers, compiled-pattern `__index__` neighbors, keyword-error rows, wrong-text-model rows, direct-`Pattern` replacement workloads, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern collection/replacement benchmark suite:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_CARRIER_CASES` by exactly two cases for the new workload ids above, with expected results `"xx"` and `(b"xabc", 1)` plus `expected_field_names == ("kwargs.count",)`;
  - wire the two new workload ids to the exact correctness anchors listed above in the shared collection/replacement benchmark-to-correctness mapping;
  - keep the compiled-pattern keyword-carrier contract on the existing shared owner path, including the payload round-trip, callback-time keyword materialization, internal probe, and precompiled-first-argument timing checks, instead of creating another benchmark suite or another detached expectation table;
  - update the collection-replacement manifest expectations from `62` measured workloads to `64`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `870` total / `870` measured / `0` known gaps across `30` manifests to `872` / `872` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `862` to `864`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 62`, `measured_workloads == 62`, and `known_gap_count == 0` to `64`, `64`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `62` to `64`;
  - the two new compiled-pattern-first-argument bool-count complement workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0900-compiled-pattern-module-sub-subn-bool-count-complement-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0898` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0898` first instead of widening this task.

## Notes
- `RBR-0900` is the next available feature task id in the current checkout:
  - `RBR-0898` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0899` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0898` on the same shared module-workflow/collection-replacement frontier so the newly published compiled-pattern bool-count complement pair reaches the tracked Python-path benchmark surface before another owner-path widening invents a different helper family.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact benchmark ids are still missing:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.sub(rebar.compile("abc"), "x", "abcabc", count=False) ... rebar.subn(rebar.compile(b"abc"), b"x", b"abcabc", count=True) ... PY` matched stdlib `re` for both exact calls in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` passed in this run (`39 passed, 509 deselected`), so the shared compiled-pattern keyword-carrier benchmark owner path is already green before widening the exact bool-count complement spellings;
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently publish only `module-sub-count-bool-keyword-warm-str-compiled-pattern` anchored to `workflow-module-sub-count-bool-true-str-compiled-pattern` and `module-subn-count-bool-keyword-purged-bytes-compiled-pattern` anchored to `workflow-module-subn-count-bool-false-bytes-compiled-pattern`, not the exact `count=False` / `count=True` complement rows queued here; and
  - `reports/benchmarks/latest.py` currently reports `REPORT["summary"]["total_workloads"] == 870`, `REPORT["summary"]["measured_workloads"] == 870`, `REPORT["summary"]["known_gap_count"] == 0`, and `REPORT["summary"]["module_workloads"] == 862`, with `REPORT["manifests"]["collection-replacement-boundary"]` at `62` selected / `62` measured / `0` known gaps.

## Completion
- Added the two missing compiled-pattern-first-argument bool-count complement workloads to `benchmarks/workloads/collection_replacement_boundary.py` in the required positions:
  - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`
  - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`
- Finished the shared benchmark-suite wiring in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by mapping those workload ids to `workflow-module-sub-count-bool-false-str-compiled-pattern` and `workflow-module-subn-count-bool-true-bytes-compiled-pattern`, and by updating the published full-suite summary expectation to `872` total / `872` measured / `0` known gaps with `864` module workloads.
- Republished `reports/benchmarks/latest.py`; the tracked report now records `collection-replacement-boundary` at `64` selected / `64` measured / `0` known gaps, keeps the manifest path unchanged, and exposes both new workload ids with `status == "measured"`. The combined tracked summary now reports `872` total / `872` measured / `0` known gaps across `30` manifests, with `864` module workloads, `8` parser workloads, and `8` regression workloads.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` (`44 passed, 511 deselected`)
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'` (`1 passed, 554 deselected`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0900-compiled-pattern-module-sub-subn-bool-count-complement-boundary-pair.py` (`64` measured / `0` known gaps)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (`872` measured / `0` known gaps)
