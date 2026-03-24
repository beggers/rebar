# RBR-1143: Collapse generated compile-anchor plumbing onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining generated-manifest compile-anchor plumbing that is still duplicated across the quantified alternation, branch-local backreference, and conditional group-exists parity suites by routing it through one shared helper surface on `tests/python/fixture_parity_support.py` instead of keeping suite-local manifest lookup and compile-case flattening mechanics beside the already-shared parity support layer.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that file, for the generated compile-anchor shape that is still repeated across these suites:
  - cover ordered generated-spec collections keyed by `spec.bundle.expected_manifest_id`;
  - cover flattening the generated compile cases from `spec.bundle` selections without each suite rebuilding the same `tuple(... for spec ... for case in fixture_cases_for_operation((spec.bundle,), "compile"))` shape;
  - cover manifest-id lookup for generated specs with an explicit owner label in the failure message instead of keeping suite-local `_generated_*_spec(...)` helpers or ad hoc manifest-id maps; and
  - keep the helper path on the existing parity-support module instead of adding another helper file, registry, protocol, or data-description layer.
- `tests/python/test_quantified_alternation_parity_suite.py` stops owning the repeated generated compile-anchor plumbing:
  - remove `GENERATED_QUANTIFIED_ALTERNATION_COMPILE_CASES`;
  - remove `_generated_quantified_alternation_spec(...)`;
  - route the existing generated compile-anchor checks through the shared helper surface while keeping `GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS`, `BODY_ATOMS`, `candidate_lengths`, expected manifest ordering, expected compile case ids, expected pattern sets, expected text models, and candidate-count assertions unchanged; and
  - preserve the current generated parity frontier and failure messaging exactly.
- `tests/python/test_branch_local_backreference_parity_suite.py` stops owning the same compile-anchor plumbing locally:
  - remove `GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES`;
  - remove `_generated_quantified_branch_local_spec(...)`;
  - route the existing generated compile-anchor checks through the same shared helper surface while keeping per-spec `candidate_body_atoms`, `candidate_suffixes`, `candidate_lengths`, expected manifest ordering, compile case ids, pattern sets, text models, and candidate-count assertions unchanged; and
  - preserve the current quantified nested-group and broader-range open-ended conditional branch-local generated parity frontier exactly.
- `tests/python/test_conditional_group_exists_parity_suite.py` uses the same shared helper path for its generated compile-anchor plumbing instead of keeping owner-local collection wiring:
  - remove `GENERATED_QUANTIFIED_CONDITIONAL_COMPILE_CASES`;
  - replace `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPEC_BY_MANIFEST_ID` with the shared manifest-id lookup path unless a strictly smaller equivalent on `tests/python/fixture_parity_support.py` makes that map unnecessary;
  - keep `GENERATED_CONDITIONAL_CANDIDATE_TEXTS_BY_MANIFEST_ID`, `GENERATED_FULLY_EMPTY_ALTERNATION_PARITY_SPEC`, branch-choice ordering, candidate texts, expected compile case ids, expected pattern sets, and current `str`-only boundary unchanged; and
  - preserve the existing quantified and fully-empty generated conditional parity coverage without widening into bytes, nested conditionals, or broader manifest sorting changes.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the new shared helper surface instead of adding another owner-specific contract block:
  - one check proves the shared helper preserves ordered manifest-id lookup and owner-labeled assertion failures;
  - one check proves the shared helper preserves generated compile-case flattening order across more than one bundle; and
  - one check proves the shared helper preserves the expected compile-anchor contract inputs used by one representative generated suite.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
- `bash -lc "! rg -n 'GENERATED_(QUANTIFIED_ALTERNATION|QUANTIFIED_BRANCH_LOCAL|QUANTIFIED_CONDITIONAL)_COMPILE_CASES = tuple\\(|def (_generated_quantified_alternation_spec|_generated_quantified_branch_local_spec)\\(' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the five files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting duplicated owner-local plumbing over introducing a broader abstraction that hides the existing generated parity frontier declarations.
- Preserve current generated manifest ordering, compile case ids, pattern sets, text models, candidate-cardinality checks, parity failure messages, and suite-local frontier constants exactly.

## Notes
- `RBR-1143` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in this run;
  - `ops/tasks/blocked/` contains only feature task `RBR-1135`; and
  - `rg -n "RBR-1143|RBR-1144|RBR-1145|RBR-1146|RBR-1147" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical notes inside completed tasks and did not reveal a live reserved future task id at `RBR-1143`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is still concrete and cross-file:
  - `tests/python/test_quantified_alternation_parity_suite.py` still defines `GENERATED_QUANTIFIED_ALTERNATION_COMPILE_CASES` plus `_generated_quantified_alternation_spec(...)`;
  - `tests/python/test_branch_local_backreference_parity_suite.py` still defines `GENERATED_QUANTIFIED_BRANCH_LOCAL_COMPILE_CASES` plus `_generated_quantified_branch_local_spec(...)`;
  - `tests/python/test_conditional_group_exists_parity_suite.py` still defines `GENERATED_QUANTIFIED_CONDITIONAL_COMPILE_CASES` plus the owner-local `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPEC_BY_MANIFEST_ID` map; and
  - `tests/python/fixture_parity_support.py` currently has shared helper surfaces for pytest ids, generated text builders, trace builders, and grouped direct-bytes specs, but not for generated compile-anchor collection and manifest lookup.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest` returned `8 passed` in this run.
  - `git status --short` returned a clean worktree before this task file was written.

## Completion
- Completed 2026-03-24 by collapsing generated compile-anchor manifest indexing, owner-labelled manifest lookup, and compile-case flattening onto shared helpers in `tests/python/fixture_parity_support.py`, then routing the quantified alternation, branch-local backreference, and conditional group-exists parity suites through that support without changing their published frontier assertions.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n 'GENERATED_(QUANTIFIED_ALTERNATION|QUANTIFIED_BRANCH_LOCAL|QUANTIFIED_CONDITIONAL)_COMPILE_CASES = tuple\\(|def (_generated_quantified_alternation_spec|_generated_quantified_branch_local_spec)\\(' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`
