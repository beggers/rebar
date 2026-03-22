# RBR-0925: Catch up the direct `Pattern.split()` keyword-error boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.split()` duplicate-`maxsplit=` / unexpected-keyword rejection pair that `RBR-0923` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing direct-`Pattern` collection/replacement keyword owner route and including only the minimal benchmark-harness support needed for these two exact rows.

## Pattern Pair
- `re.compile("abc").split("abcabc", 1, maxsplit=1)`
- `re.compile(b"abc").split(b"abcabc", missing=1)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` gains only the bounded direct-`Pattern.split()` keyword-error support needed for this pair:
  - keep the existing direct `Pattern.split()` success carriers unchanged for positional, `maxsplit=`, bool, and `__index__` keyword rows;
  - allow `pattern.split` expected-exception workloads on the shared pattern-helper keyword path to carry the lone unexpected `missing` keyword without widening unrelated pattern-helper operations or manifest scopes;
  - keep the duplicate-`maxsplit=` path expressible through the existing direct `Pattern.split()` callback builder so a workload carrying both top-level `maxsplit` and `kwargs["maxsplit"]` raises the CPython-shaped duplicate-argument `TypeError` instead of silently succeeding; and
  - keep the change narrow to direct `Pattern.split()` keyword-error workloads on the existing collection/replacement benchmark surface instead of widening search/match/fullmatch, module-helper, or compiled-pattern-first-argument benchmark semantics in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern.split()` keyword-error workloads:
  - add `pattern-split-duplicate-maxsplit-keyword-warm-str`; and
  - add `pattern-split-unexpected-keyword-warm-bytes`.
- Keep those two workloads pinned to the exact `RBR-0923` correctness anchors rather than widening the collection/replacement family:
  - `pattern-split-duplicate-maxsplit-keyword-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "abcabc"`, `flags == 0`, `maxsplit == 1`, `kwargs == {"maxsplit": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "split() takes at most 2 arguments (3 given)"}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-split-unexpected-keyword-warm-bytes` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "abcabc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "'missing' is an invalid keyword argument for split()"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-split-duplicate-maxsplit-keyword-str` and `workflow-pattern-split-unexpected-keyword-bytes`;
  - insert `pattern-split-duplicate-maxsplit-keyword-warm-str` immediately after `pattern-split-maxsplit-indexlike-keyword-warm-str` and immediately before `pattern-split-unexpected-keyword-warm-bytes`; and
  - insert `pattern-split-unexpected-keyword-warm-bytes` immediately after `pattern-split-duplicate-maxsplit-keyword-warm-str` and immediately before `pattern-sub-count-keyword-purged-bytes`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-split-duplicate-maxsplit-keyword-str` and `workflow-pattern-split-unexpected-keyword-bytes`;
  - extend the existing direct pattern-helper keyword contract coverage so the manifest round-trip, callback-time keyword materialization, and CPython exception-matching checks now cover the split duplicate/unexpected pair alongside the already-landed `Pattern.sub()` / `Pattern.subn()` keyword rows;
  - update the direct `Pattern` keyword replacement/split measured-row expectation from `15` workloads to `17`;
  - update the collection-replacement manifest expectations from `72` measured workloads to `74`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `880` total / `880` measured / `0` known gaps across `30` manifests to `882` / `882` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `872` to `874`; and
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 72`, `measured_workloads == 72`, and `known_gap_count == 0` to `74`, `74`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `72` to `74`;
  - the combined tracked summary moves from `880` total / `880` measured / `0` known gaps with `872` module workloads to `882` / `882` / `0` with `874` module workloads; and
  - the two new direct-`Pattern.split()` keyword-error workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or pattern_helper_collection_replacement or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0925-pattern-split-keyword-error-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to let the benchmark harness represent and time the exact direct `Pattern.split()` keyword-error pair above.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0923` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0923` first instead of widening this task.

## Notes
- `RBR-0925` is the next available feature task id in the current checkout:
  - `RBR-0923` is already occupied by the latest done feature task on this frontier;
  - `RBR-0924` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0923` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct `Pattern.split()` keyword-error pair reaches the tracked Python-path benchmark surface before another bound-pattern helper family reopens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier, but the benchmark path still needs the exact bounded support called out above:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").split("abcabc", 1, maxsplit=1) ... rebar.compile("abc").split("abcabc", 1, maxsplit=1) ... re.compile(b"abc").split(b"abcabc", missing=1) ... rebar.compile(b"abc").split(b"abcabc", missing=1) ... PY` now shows CPython and `rebar` agree on the exact direct `TypeError.args`: `("split() takes at most 2 arguments (3 given)",)` and `("'missing' is an invalid keyword argument for split()",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes'` currently passes in this checkout (`8 passed, 1335 deselected`), so the direct `Pattern.split()` owner path already exposes the exact error pair that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'` currently passes in this checkout (`30 passed, 527 deselected`), so the shared direct-`Pattern` collection/replacement keyword benchmark owner path is already green before widening the exact split-error spellings;
  - `rg -n 'pattern-split-duplicate-maxsplit-keyword|pattern-split-unexpected-keyword' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact direct-`Pattern.split()` benchmark workloads are still absent; and
  - a synthetic benchmark-harness probe in this run showed the remaining bounded harness gaps directly: the duplicate `Pattern.split()` workload shape does not yet surface the expected duplicate-argument `TypeError` through the current benchmark callback path, and the unexpected-keyword shape is still rejected during workload normalization with `benchmark workload kwargs for pattern.split only supports the \`maxsplit\` key; got unsupported keys ['missing']`.

## Completion
- 2026-03-22: Landed the bounded benchmark-path follow-on by allowing `pattern.split` expected-exception workloads to carry the exact unexpected `missing` keyword, adding the two direct `Pattern.split()` keyword-error rows to `benchmarks/workloads/collection_replacement_boundary.py`, extending the shared benchmark contract coverage for pattern-helper keyword round-trip/materialization/error parity, and republishing `reports/benchmarks/latest.py` at `882` total / `882` measured / `0` known gaps with `874` module workloads and `74` measured collection-replacement workloads. Verified with the task-specified parity pytest slice, the shared benchmark pytest slice, the narrow manifest benchmark rerun to `.rebar/tmp/rbr-0925-pattern-split-keyword-error-boundary-pair.py`, and the tracked full-suite benchmark publication command.
