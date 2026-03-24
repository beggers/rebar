## RBR-1136: Collapse generated parity text builders onto shared support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining `WRAPPER_PAIRS`-driven generated-text builder mirrors from the quantified alternation, branch-local backreference, and conditional group-exists parity suites by routing them through one canonical helper surface on `tests/python/fixture_parity_support.py` instead of keeping four near-duplicate builders spread across three large test modules.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py` for the generated parity text patterns that currently duplicate the same wrapper-pair expansion shape:
  - keep the helper(s) on the existing parity-support module instead of adding another helper file, registry, protocol, or generic test-data layer;
  - cover the two actual shared shapes that exist today:
    - wrapping an already-computed ordered core-text sequence with the canonical `WRAPPER_PAIRS`; and
    - generating ordered wrapped texts from `body_atoms`, `candidate_lengths`, and an optional ordered terminal/suffix sequence; and
  - preserve current ordering, deduped cardinality, and plain-ASCII text output so the existing parity matrices remain stable.
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining its suite-local generated candidate-text builder and uses the shared helper path instead:
  - remove `_build_generated_quantified_alternation_candidate_texts`;
  - keep `GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS`, candidate-count assertions, and `str`/`bytes` generated parity matrices unchanged; and
  - preserve the current backtracking-heavy generated text frontier and compile-case anchoring.
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining its suite-local generated candidate-text builder and uses the same shared helper path instead:
  - remove `_build_generated_quantified_branch_local_candidate_texts`;
  - keep the existing per-spec `candidate_body_atoms`, `candidate_suffixes`, candidate-count assertions, and `str`/`bytes` generated parity matrices unchanged; and
  - preserve the current quantified and broader-range open-ended conditional branch-local generated parity coverage.
- `tests/python/test_conditional_group_exists_parity_suite.py` stops defining its two suite-local generated candidate-text builders and uses the same shared helper surface instead:
  - remove `_build_generated_fully_empty_alternation_candidate_texts`;
  - remove `_build_generated_quantified_conditional_candidate_texts`;
  - keep the existing quantified-conditional and fully-empty alternation candidate ordering, count assertions, and generated parity matrices unchanged; and
  - preserve the current compile-case anchoring and supplemental conditional workflow coverage.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused contract coverage for the new shared helper surface:
  - one check proves the shared wrapper helper preserves the declared `WRAPPER_PAIRS` ordering around a supplied core sequence;
  - one check proves the generated body/terminal helper preserves the current ordered matrix shape for at least one quantified-alternation-style and one branch-local-style input; and
  - keep the contract localized to `fixture_parity_support.py` instead of creating suite-specific helper tests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_text_matrix_matches_cpython tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_text_matrix_matches_cpython`
- `bash -lc "! rg -n 'def (_build_generated_quantified_alternation_candidate_texts|_build_generated_quantified_branch_local_candidate_texts|_build_generated_fully_empty_alternation_candidate_texts|_build_generated_quantified_conditional_candidate_texts)\\(' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the five files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting duplicated suite-local generation helpers over introducing a broader abstraction layer that obscures how each suite's candidate texts are formed.
- Preserve the current generated candidate ordering, parity failure messages, compile-case ids, manifest anchoring, and `bytes` encoding behavior in all three suites.

## Notes
- `RBR-1136` is the next available unreserved architecture task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1135`; and
  - `rg -n 'RBR-1136|RBR-1137|RBR-1138|RBR-1139' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 1`;
  - the current ready task is concrete feature work at `RBR-1135`, but the runtime artifacts do not show inherited-dirty churn or a stalled post-task refresh/commit path; and
  - the newest blocked task is feature task `RBR-1133`, not a blocked architecture cleanup that needs reopening or stale normalization.
- The live duplication is still concrete and cross-file:
  - `tests/python/test_quantified_alternation_parity_suite.py` still defines `_build_generated_quantified_alternation_candidate_texts`;
  - `tests/python/test_branch_local_backreference_parity_suite.py` still defines `_build_generated_quantified_branch_local_candidate_texts`;
  - `tests/python/test_conditional_group_exists_parity_suite.py` still defines both `_build_generated_fully_empty_alternation_candidate_texts` and `_build_generated_quantified_conditional_candidate_texts`; and
  - `tests/python/fixture_parity_support.py` exposes `WRAPPER_PAIRS` but no shared helper that owns these generated text matrices yet.
- Verification status in this run:
  - Landed one shared helper surface on `tests/python/fixture_parity_support.py`: `wrap_candidate_core_texts()` owns the `WRAPPER_PAIRS` expansion for precomputed ordered core strings, and `build_wrapped_body_candidate_texts()` owns the `body_atoms`/`candidate_lengths`/terminal matrix used by the quantified alternation and branch-local suites.
  - Routed `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `tests/python/test_conditional_group_exists_parity_suite.py` through those shared helpers and deleted the four suite-local generated candidate-text builders while keeping candidate ordering, count assertions, compile anchors, and `bytes` encoding behavior unchanged.
  - Added focused support-contract coverage in `tests/python/test_fixture_parity_support_contract.py` for wrapper ordering and representative generated matrix ordering.
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k "wrap_candidate_core_texts or build_wrapped_body_candidate_texts"` returned `2 passed` in this run.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_text_matrix_matches_cpython tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_text_matrix_matches_cpython` returned `60 passed` in this run.
  - `bash -lc "! rg -n 'def (_build_generated_quantified_alternation_candidate_texts|_build_generated_quantified_branch_local_candidate_texts|_build_generated_fully_empty_alternation_candidate_texts|_build_generated_quantified_conditional_candidate_texts)\\(' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"` returned success in this run, confirming the duplicated suite-local builders are gone.
