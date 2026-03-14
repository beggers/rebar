# RBR-0343: Consolidate the exact-repeat quantified-group alternation correctness scorecard into the shared suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the last standalone exact-repeat quantified-group alternation correctness wrapper with the existing data-driven combined scorecard path so this counted-repeat alternation slice is asserted through shared expectation data instead of bespoke cargo-build, subprocess, tracked-report, and hand-expanded case boilerplate.

## Deliverables
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- Delete `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py`

## Acceptance Criteria
- The correctness scorecard contract currently spread across `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py` is covered from the existing `tests/conformance/test_combined_correctness_scorecards.py` suite by extending the current `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS` / `combined_correctness_case(...)` path rather than adding another one-manifest helper or subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit representative-case entry for `exact-repeat-quantified-group-alternation-workflows`, and the shared expectation data keeps all 10 currently published numbered and named cases explicit, including:
  - compile metadata for `a(bc|de){2}d` and `a(?P<word>bc|de){2}d`
  - module `search()` hits for the `bc/bc` and `bc/de` repetition pairs
  - `Pattern.fullmatch()` success on the `de/de` branch pair
  - the short numbered no-match and extra-repetition named no-match observations
- Fixture-prefix selection remains derived from `python/rebar_harness/correctness.py` and the ordered `DEFAULT_FIXTURE_PATHS` inventory; the implementation must not reintroduce manual `cargo build`, `python -m rebar_harness.correctness`, temporary-report loading, or tracked-report assertions for this manifest.
- Representative-case assertions continue to flow through `evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter` instead of hard-coded `pass` / `unimplemented` fragments or bespoke `assert_compile_case()` / `assert_match_case()` helpers, so the suite stays valid as this slice evolves.
- After the consolidation lands, `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py` no longer exists, and `rg --files tests/conformance | rg 'test_correctness_exact_repeat_quantified_group_alternation_workflows\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to correctness test architecture for `exact-repeat-quantified-group-alternation-workflows`; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Prefer deleting the wrapper over introducing another expectation family: this manifest already sits in `DEFAULT_FIXTURE_PATHS`, so the existing combined cumulative-prefix path should stay the source of truth unless the current checkout proves that impossible.
- Keep adjacent counted-repeat manifests such as `exact-repeat-quantified-group-workflows`, `ranged-repeat-quantified-group-workflows`, and `wider-ranged-repeat-quantified-group-workflows` on their current shared paths; do not widen this task into another multi-manifest reorganization.

## Notes
- `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py` is 330 lines and is now the only remaining `tests/conformance/test_correctness_.*workflows.py` wrapper outside the shared suite.
- `tests/conformance/correctness_expectations.py` currently has no entry for `exact-repeat-quantified-group-alternation-workflows`, so `test_combined_correctness_scorecards.py` cannot absorb this manifest until that single manifest-keyed expectation is added.
