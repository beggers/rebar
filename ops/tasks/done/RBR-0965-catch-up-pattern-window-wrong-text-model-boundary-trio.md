# RBR-0965: Catch up the direct Pattern window wrong-text-model boundary trio

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact direct `Pattern.search()` / `Pattern.match()` / `Pattern.fullmatch()` wrong-text-model trio that `RBR-0963` already published on the shared `module-workflow-surface` correctness path, while widening `haystack_text_model` validation only enough to admit this bounded `pattern-boundary` trio on the existing wrong-text-model owner route.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").search(b"abc")`
- `re.compile(b"abc").match("abc")`
- `re.compile("abc").fullmatch(b"abc")`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` admits `haystack_text_model` on `pattern-boundary` only for the exact direct-`Pattern` wrong-text-model window trio in this slice:
  - allow `manifest_id == "pattern-boundary"` when `use_compiled_pattern is False`;
  - allow only `pattern.search`, `pattern.match`, and `pattern.fullmatch` operations;
  - require positional helper calls (`kwargs == {}` and any `pos`/`endpos` carriers absent);
  - keep the existing `haystack_text_model != text_model` and `expected_exception["type"] == "TypeError"` requirements intact; and
  - keep unrelated manifests, same-text-model rows, keyword-carrier rows, and non-`TypeError` rows rejected with explicit validation coverage.
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three direct-`Pattern` wrong-text-model workloads:
  - add `pattern-search-on-bytes-string-warm-str`;
  - add `pattern-match-on-str-string-purged-bytes`; and
  - add `pattern-fullmatch-on-bytes-string-warm-str`.
  - keep `pattern-search-on-bytes-string-warm-str` on `operation == "pattern.search"` with `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `haystack_text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - keep `pattern-match-on-str-string-purged-bytes` on `operation == "pattern.match"` with `pattern == "abc"`, `haystack == "abc"`, `text_model == "bytes"`, `haystack_text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a bytes pattern on a string-like object"}`;
  - keep `pattern-fullmatch-on-bytes-string-warm-str` on `operation == "pattern.fullmatch"` with `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `haystack_text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - categorize the three rows under the shared direct-`Pattern` wrong-text-model path with helper-specific categories plus `wrong-text-model` and the existing warm/purged cache tags;
  - keep the syntax-feature surface bounded to the three exact helper spellings above; and
  - place the new rows on the existing search/match/fullmatch helper path rather than forking another benchmark manifest or detached wrong-text-model manifest.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `pattern-boundary` and shared wrong-text-model benchmark contract paths instead of creating another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` or an equivalent existing `pattern-boundary` assertion so the manifest count moves from `20` workloads to `23` while the new wrong-text-model trio also publishes as measured rows on the same zero-gap manifest;
  - add a bounded direct-`Pattern` window wrong-text-model anchor contract on `PATTERN_BOUNDARY_MANIFEST_PATH` mapping:
    - `pattern-search-on-bytes-string-warm-str` -> `workflow-pattern-search-str-pattern-on-bytes-string`;
    - `pattern-match-on-str-string-purged-bytes` -> `workflow-pattern-match-bytes-pattern-on-str-string`; and
    - `pattern-fullmatch-on-bytes-string-warm-str` -> `workflow-pattern-fullmatch-str-pattern-on-bytes-string`;
  - extend the shared wrong-text-model owner-spec coverage so manifest round-trip checks, internal workload probes, and callback/precompile-contract assertions cover the new direct-`Pattern` window trio on `pattern-boundary` alongside the existing collection/replacement and compiled-pattern module-helper wrong-text-model owners; and
  - extend the haystack-text-model validation tests so the exact bounded `pattern-boundary` trio is accepted while neighboring unsupported shapes on that manifest still fail for the documented reasons.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined tracked summary moves from `903` total / `903` measured / `0` known gaps with `895` module workloads to `906` / `906` / `0` with `898` module workloads;
  - `REPORT["manifests"]["pattern-boundary"]` moves from `selected_workload_count == 20`, `measured_workloads == 20`, and `known_gap_count == 0` to `23`, `23`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `pattern-boundary` on the same tracked manifest path while moving its `workload_count` from `20` to `23`; and
  - all three new direct-`Pattern` wrong-text-model workloads publish real `rebar` timings with `status == "measured"`, not placeholders.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or haystack_text_model_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0965-pattern-window-wrong-text-model-boundary-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only apart from the minimal `haystack_text_model` harness prerequisite needed to admit the exact `pattern-boundary` wrong-text-model trio above.
- Reuse the existing `pattern_boundary.py` manifest, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner routes, and shared wrong-text-model contract helpers. Do not create another benchmark manifest, another parity suite, or a detached validator layer in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Do not widen this task into direct `Pattern` keyword-window carriers, collection/replacement wrong-text-model siblings, compiled-pattern module-helper siblings, or any broader pattern-boundary expansion beyond the three helper calls above.

## Notes
- `RBR-0965` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 8` currently ends at `RBR-0964-collapse-compiled-pattern-module-helper-publication-owner-path-mirrors.md`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after `RBR-0963` because the shared `module-workflow-surface` correctness frontier already published the exact direct-`Pattern` wrong-text-model trio, and the next concrete missing slice on the same owner family is the adjacent Python-path benchmark catch-up.
- 2026-03-22 feature-planning probes confirm the slice is bounded and expose the exact harness prerequisite instead of a broader runtime gap:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string'` currently passes (`12 passed`), so the exact correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... re.compile('abc').search(b'abc') ... rebar.compile('abc').search(b'abc') ... re.compile(b'abc').match('abc') ... rebar.compile(b'abc').match('abc') ... re.compile('abc').fullmatch(b'abc') ... rebar.compile('abc').fullmatch(b'abc') ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args` for all three helper spellings;
  - `rg -n 'pattern-search-on-bytes-string-warm-str|pattern-match-on-str-string-purged-bytes|pattern-fullmatch-on-bytes-string-warm-str' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `903` total / `903` measured / `0` known gaps with `pattern-boundary` fixed at `20` measured workloads; and
  - a synthetic `run_internal_workload_probe(...)` attempt for the exact three direct-`Pattern` wrong-text-model payloads currently fails at `python/rebar_harness/benchmarks.py:validate_haystack_text_model_override(...)` with `ValueError: benchmark workload haystack_text_model is only supported on the \`collection-replacement-boundary\` manifest and the bounded \`module-boundary\` compiled-pattern wrong-text-model trio`, so this task must land that minimal benchmark-harness prerequisite along with the bounded manifest/report catch-up.
- 2026-03-22 feature-implementation: Extended `python/rebar_harness/benchmarks.py` so `haystack_text_model` accepts only the bounded direct `Pattern.search()` / `Pattern.match()` / `Pattern.fullmatch()` wrong-text-model trio on `pattern-boundary` when the helper call stays positional (`kwargs == {}` and no `pos`/`endpos` carriers). Added the three direct-Pattern wrong-text-model workloads to `benchmarks/workloads/pattern_boundary.py`, extended the existing `pattern-boundary` anchor/owner-spec/validation coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and regenerated `reports/benchmarks/latest.py`.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-pattern-on-bytes-string or pattern-match-bytes-pattern-on-str-string or pattern-fullmatch-str-pattern-on-bytes-string'` passed (`12 passed`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or haystack_text_model_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'` passed (`63 passed, 612 deselected, 17 subtests passed`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids'` passed (`63 passed, 612 deselected`), keeping the new `pattern-boundary` wrong-text-model anchor definition on the shared benchmark-owner path.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'` passed (`1 passed, 674 deselected`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0965-pattern-window-wrong-text-model-boundary-trio.py` passed with `23` total / `23` measured / `0` known gaps for `pattern-boundary`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` regenerated the tracked report. `reports/benchmarks/latest.py` now records `906` total / `906` measured / `0` known gaps with `898` module workloads, and `REPORT["manifests"]["pattern-boundary"]` plus `REPORT["artifacts"]["manifests"]` now show `23` selected/measured/workload-count rows on `benchmarks/workloads/pattern_boundary.py`.
