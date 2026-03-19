# RBR-0669: Collapse the detached standard benchmark anchor suite onto the combined benchmark owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` by moving its remaining benchmark-manifest, built-native mode, and correctness-anchor contract coverage onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the benchmark harness has one legible owner suite instead of a detached second benchmark-side contract file.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Delete `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` becomes the sole owner for the detached benchmark-anchor contract surface currently isolated in `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`:
  - keep the built-native and manifest-loader support helpers file-local on the owner file instead of leaving them behind in another wrapper:
    - `anchor_support_cache_guard(...)`,
      `_clear_anchor_support_caches(...)`,
      `_synthetic_manifest(...)`,
      `_synthetic_case(...)`,
      `_synthetic_workload(...)`,
      `_tracked_benchmark_manifest_paths(...)`,
      `_write_test_manifest(...)`,
      `_build_minimal_built_native_scorecard(...)`,
      `_assert_built_native_runner_uses_optional_report_path(...)`,
      `_assert_built_native_cli_uses_optional_report_path(...)`,
      `_assert_built_native_mode_requires_real_built_runtime(...)`, and
      `_assert_built_native_combined_scorecard_fields(...)`;
  - keep the benchmark-anchor registry and lookup surface file-local on the owner file instead of leaving a detached benchmark-contract suite beside it:
    - `AnchoredWorkloadCasePair`,
      `StandardBenchmarkAnchorContractDefinition`,
      `_manifest_workloads(...)`,
      `_selected_manifest_workloads(...)`,
      `assert_anchored_workload_case_result_parity(...)`,
      `assert_benchmark_workload_matches_expected_result(...)`,
      `_definition_workloads_by_id(...)`,
      `_direct_parity_case_ids_by_signature(...)`,
      `_manual_expected_result(...)`,
      `_expected_workload_ids(...)`,
      `_expected_anchor_case_ids_for_manifest(...)`,
      `_anchored_case_ids(...)`,
      `_unanchored_case_ids(...)`,
      `_all_unanchored_case_ids(...)`,
      `_expected_callback_anchor_case_ids(...)`,
      `_expected_legacy_anchor_case_ids(...)`, and
      `_expected_anchored_pairs(...)`;
  - keep the representative detached benchmark tests defined directly on the owner file:
    - `test_built_native_smoke_runner_uses_explicit_report_paths_only(...)`,
      `test_built_native_full_runner_uses_explicit_report_paths_only(...)`,
      `test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(...)`,
      `test_standard_benchmark_manifest_materializes_bytes_template_replacements_for_nested_group_workloads(...)`,
      `test_standard_benchmark_manifest_rejects_missing_and_non_dict_manifest_values(...)`,
      `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(...)`,
      `test_standard_benchmark_workload_callbacks_match_anchor_case_results(...)`, and
      `test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries(...)`;
  - do not leave those tests behind in a renamed compatibility shell, a new `tests/benchmarks/*support*.py` module, or `tests/conftest.py`.
- `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` is deleted outright:
  - do not leave an import-only wrapper, renamed compatibility module, or new detached benchmark-anchor support layer behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, `python/rebar_harness/correctness.py`, `tests/python/fixture_parity_support.py`, published reports, or tracked project-state prose in this run; and
  - preserve the current built-native explicit-report behavior, benchmark-manifest loader behavior, anchor-signature matching, and manual expected-result checks exactly.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `./.venv/bin/python - <<'PY'
from pathlib import Path

benchmarks = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
needles = (
    "def anchor_support_cache_guard(",
    "class StandardBenchmarkAnchorContractDefinition:",
    "def test_built_native_smoke_runner_uses_explicit_report_paths_only(",
    "def test_standard_benchmark_manifest_materializes_callable_replacement_descriptors(",
    "def test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(",
    "def test_standard_benchmark_workload_callbacks_match_anchor_case_results(",
)
for needle in needles:
    assert needle in benchmarks, needle
assert not Path("tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py").exists()
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_standard_benchmark_correctness_anchor_contracts\\.py$'"`

## Constraints
- Keep this cleanup structural only. The point is to delete a detached benchmark-side contract suite, not to reinterpret benchmark scorecard semantics, built-native strictness, manifest selection, or correctness-anchor matching.
- Prefer the existing combined benchmark owner and file-local helpers over another shared support module.
- Do not move this benchmark-anchor surface onto `tests/python/test_ops_harness.py` or `tests/conformance/test_combined_correctness_scorecards.py`; it stays with the benchmark owner.

## Notes
- `RBR-0669` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-066[89]|RBR-067[0-9]|RBR-068[0-9]" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` currently returns only the landed feature task `RBR-0668` plus historical mentions inside done-task notes; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0668*' -o -name 'RBR-0669*' -o -name 'RBR-0670*' -o -name 'RBR-0671*' -o -name 'RBR-0672*' -o -name 'RBR-0673*' -o -name 'RBR-0674*' -o -name 'RBR-0675*' -o -name 'RBR-0676*' -o -name 'RBR-0677*' -o -name 'RBR-0678*' -o -name 'RBR-0679*' -o -name 'RBR-0680*' \) | sort` currently returns only `ops/tasks/done/RBR-0668-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-pack.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/`, `ops/tasks/ready/`, and `ops/tasks/in_progress/` are currently empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both `architecture-implementation` and `feature-implementation` finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached benchmark-anchor suite is concrete, isolated, and still redundant beside the owner file in the current checkout:
  - `wc -l tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports `3366` lines for the detached suite and `4540` lines for the combined benchmark owner;
  - `rg -n "from tests\\.benchmarks\\.test_standard_benchmark_correctness_anchor_contracts import|import tests\\.benchmarks\\.test_standard_benchmark_correctness_anchor_contracts" -g '*.py' tests python` currently returns no matches, so the detached file is not an import dependency for other suites;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`43 passed, 1188 subtests passed in 24.19s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` currently passes (`111 passed, 3 skipped in 0.23s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: class StandardBenchmarkAnchorContractDefinition:` because the combined owner does not yet carry the moved anchor-contract surface; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'test_standard_benchmark_correctness_anchor_contracts\\.py$'"` currently fails exactly on this cleanup because the detached benchmark-anchor suite still exists.
- This simplification matches the current benchmark information flow:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns the tracked source-tree benchmark scorecard expectations, benchmark reruns, and publication assertions; and
  - `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` is now a detached second benchmark-side contract surface rather than a separate cross-owner boundary.

## Completion
- Moved the detached benchmark-anchor helper stack, manifest/anchor registry, and pytest contract coverage onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Deleted `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`; `git diff --name-status -- tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` now shows `D` for the detached suite and `M` for the combined owner.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`154 passed, 3 skipped, 1188 subtests passed`), the inline source/deletion probe from Acceptance (`ok`), and `bash -lc "! rg --files tests/benchmarks | rg 'test_standard_benchmark_correctness_anchor_contracts\\.py$'"`.
