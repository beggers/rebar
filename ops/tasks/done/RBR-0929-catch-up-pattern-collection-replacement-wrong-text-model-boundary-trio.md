# RBR-0929: Catch up the direct `Pattern` collection/replacement wrong-text-model boundary trio

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` wrong-text-model rejection trio that `RBR-0927` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing direct bound-`Pattern` collection/replacement owner route and including only the minimal benchmark-harness support needed for these three exact rows.

## Pattern Pair
- `re.compile("abc").split(b"zabczz")` / `re.compile("abc").sub("x", b"zabczz")`
- `re.compile(b"abc").subn(b"x", "zabczz")`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` gains only the bounded direct `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` wrong-text-model support needed for this trio:
  - allow `haystack_text_model` on the existing `collection-replacement-boundary` owner path only for `pattern.split`, `pattern.sub`, and `pattern.subn` workloads with no keyword payloads, a mismatched haystack text model, and an expected `TypeError`;
  - keep the existing compiled-pattern-first-argument module-helper wrong-text-model path unchanged instead of widening its manifest scope or validation rules;
  - keep the direct `Pattern` callback path narrow so the timed callback still compiles the pattern outside the loop, then raises the CPython-shaped wrong-text-model `TypeError` from the direct helper invocation; and
  - do not widen this run into `pattern.search` / `pattern.match` / `pattern.fullmatch`, `pattern.findall` / `pattern.finditer`, module-helper mixed-text-model rows, or a new benchmark family.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three direct-`Pattern` wrong-text-model workloads:
  - add `pattern-split-on-bytes-string-warm-str`;
  - add `pattern-sub-on-bytes-string-warm-str`; and
  - add `pattern-subn-on-str-string-purged-bytes`.
- Keep those three workloads pinned to the exact `RBR-0927` correctness anchors rather than widening the collection/replacement family:
  - `pattern-split-on-bytes-string-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zabczz"`, `flags == 0`, `maxsplit == 0`, `text_model == "str"`, `haystack_text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - `pattern-sub-on-bytes-string-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "str"`, `haystack_text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and the same wrong-text-model `TypeError`;
  - `pattern-subn-on-str-string-purged-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `flags == 0`, `count == 0`, `text_model == "bytes"`, `haystack_text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a bytes pattern on a string-like object"}`;
  - anchor the three workloads to `workflow-pattern-split-str-pattern-on-bytes-string`, `workflow-pattern-sub-str-pattern-on-bytes-string`, and `workflow-pattern-subn-bytes-pattern-on-str-string`;
  - insert `pattern-split-on-bytes-string-warm-str` immediately after `pattern-split-unexpected-keyword-warm-bytes` and immediately before `pattern-finditer-literal-warm-str`;
  - insert `pattern-sub-on-bytes-string-warm-str` immediately after `pattern-sub-unexpected-keyword-warm-str` and immediately before `pattern-subn-count-indexlike-positional-warm-str`; and
  - insert `pattern-subn-on-str-string-purged-bytes` immediately after `pattern-subn-unexpected-keyword-warm-bytes` and immediately before `pattern-subn-grouped-template-warm-str`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - add one bounded direct `Pattern` wrong-text-model benchmark-to-correctness anchor definition for the new workload ids above, mapped to the three `workflow-pattern-*wrong-text-model*` correctness rows named above;
  - extend the shared benchmark contract coverage so the manifest round-trip, callback-time haystack text-model materialization, precompiled helper invocation, and CPython exception-matching checks now cover the direct `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` wrong-text-model trio;
  - add a focused manifest assertion that the collection-replacement manifest now keeps exactly `3` direct `Pattern` wrong-text-model rows measured;
  - update the collection-replacement manifest expectations from `74` measured workloads to `77`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `882` total / `882` measured / `0` known gaps across `30` manifests to `885` / `885` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `874` to `877`; and
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 74`, `measured_workloads == 74`, and `known_gap_count == 0` to `77`, `77`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `74` to `77`;
  - the combined tracked summary moves from `882` total / `882` measured / `0` known gaps with `874` module workloads to `885` / `885` / `0` with `877` module workloads; and
  - the three new direct-`Pattern` wrong-text-model workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0929-pattern-collection-replacement-wrong-text-model-boundary-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to let the benchmark harness represent and time the exact direct `Pattern` wrong-text-model trio above.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0927` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0927` first instead of widening this task.

## Notes
- `RBR-0929` is the next available feature task id in the current checkout:
  - `RBR-0927` is the latest done feature task on this frontier;
  - `RBR-0928` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0927` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct `Pattern` wrong-text-model trio reaches the tracked Python-path benchmark surface before another bound-pattern helper family reopens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier, but the benchmark path still needs the exact bounded support called out above:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'` currently passes in this checkout (`6 passed, 1358 deselected`), so the direct `Pattern` owner path already exposes the exact wrong-text-model trio that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(\"abc\").split(b\"zabczz\") ... rebar.compile(\"abc\").split(b\"zabczz\") ... re.compile(\"abc\").sub(\"x\", b\"zabczz\") ... rebar.compile(\"abc\").sub(\"x\", b\"zabczz\") ... re.compile(b\"abc\").subn(b\"x\", \"zabczz\") ... rebar.compile(b\"abc\").subn(b\"x\", \"zabczz\") ... PY` now shows CPython and `rebar` agree on the exact direct `TypeError` text for all three bounded wrong-text-model rows;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... workload_from_payload({... 'manifest_id': 'collection-replacement-boundary', 'operation': 'pattern.split', 'haystack_text_model': 'bytes', ...}) ... PY` currently fails with `ValueError: benchmark workload haystack_text_model currently only supports compiled-pattern module.split/module.findall/module.finditer/module.sub/module.subn workloads`, so the existing benchmark payload model still rejects this exact bounded direct-`Pattern` trio;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or pattern_helper_collection_replacement or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'` currently passes in this checkout (`38 passed, 523 deselected, 17 subtests passed`), so the shared collection/replacement benchmark owner path is green before widening the exact wrong-text-model spellings; and
  - `rg -n 'pattern-split-on-bytes-string-warm-str|pattern-sub-on-bytes-string-warm-str|pattern-subn-on-str-string-purged-bytes' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact direct-`Pattern` benchmark workloads are still absent.

## Completion Notes
- 2026-03-22: Added the bounded direct `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` wrong-text-model benchmark support in `python/rebar_harness/benchmarks.py`, including the existing-manifest-only `haystack_text_model` validation path for these three positional helper rows and callback-time haystack materialization so the wrong-text-model `TypeError` still comes from the direct bound helper invocation after compile.
- 2026-03-22: Added exactly three workloads to `benchmarks/workloads/collection_replacement_boundary.py`: `pattern-split-on-bytes-string-warm-str`, `pattern-sub-on-bytes-string-warm-str`, and `pattern-subn-on-str-string-purged-bytes`, in the required positions beside the existing direct `Pattern` keyword rows.
- 2026-03-22: Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the direct `Pattern` wrong-text-model anchor contract, manifest-count assertion, validation coverage, manifest round-trip coverage, callback-time haystack materialization coverage, probe coverage, and precompile-before-timing callback checks for this trio.
- 2026-03-22: Republished `reports/benchmarks/latest.py`; the tracked report now shows `collection-replacement-boundary` at `77` selected / `77` measured / `0` known gaps with the same manifest path and `workload_count == 77`, and the combined tracked summary at `885` total / `885` measured / `0` known gaps with `877` module workloads, `8` parser workloads, and `8` regression workloads. The three new direct-`Pattern` wrong-text-model workload ids all publish `status == "measured"`.
- 2026-03-22: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_wrong_text_model or pattern_helper_collection_replacement_wrong_text_model or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'haystack_text_model_validation_matches_manifest_and_payload_entry_points'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0929-pattern-collection-replacement-wrong-text-model-boundary-trio.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
