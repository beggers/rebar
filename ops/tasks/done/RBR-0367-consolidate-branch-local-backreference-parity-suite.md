# RBR-0367: Consolidate the branch-local-backreference parity modules into one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Replace the seven landed branch-local-backreference parity modules with one backend-parameterized pytest suite so this frontier stops living across repeated fixture loading, repeated `sys.path` setup, repeated compile/workflow/no-match assertions, and two leftover `unittest` classes.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`
- Delete `tests/python/test_branch_local_backreference_parity.py`
- Delete `tests/python/test_quantified_branch_local_backreference_parity.py`
- Delete `tests/python/test_optional_group_alternation_branch_local_backreference_parity.py`
- Delete `tests/python/test_conditional_group_exists_branch_local_backreference_parity.py`
- Delete `tests/python/test_nested_group_alternation_branch_local_backreference_parity.py`
- Delete `tests/python/test_quantified_alternation_branch_local_backreference_parity.py`
- Delete `tests/python/test_quantified_nested_group_alternation_branch_local_backreference_parity.py`

## Acceptance Criteria
- The new suite covers the currently landed numbered and named branch-local-backreference parity observations now spread across the seven superseded modules for:
  - `a((b)|c)\2d` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)d`
  - `a((b)+|c)\2d` and `a(?P<outer>(?P<inner>b)+|c)(?P=inner)d`
  - `a((b|c)\2)?d` and `a(?P<outer>(?P<inner>b|c)(?P=inner))?d`
  - `a((b)|c)\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)`
  - `a((b|c))\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d`
  - `a((b|c)\2){1,2}d` and `a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d`
  - `a((b|c)+)\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`
  - `a((b|c){1,4})\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`
- Case selection is driven from the published correctness fixtures already checked into the repo:
  - `tests/conformance/fixtures/branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/quantified_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/optional_group_alternation_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/nested_group_alternation_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_workflows.py`
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py`
  The consolidated suite keeps one manifest-alignment assertion per fixture covering the manifest id, published case-id set, compile-pattern set, and exact `operation`/`helper` distribution each fixture publishes today, including the broader `{1,4}` nested follow-on currently housed beside the `+` quantified slice.
- The implementation reuses the existing loader path in `rebar_harness.correctness`, especially `load_fixture_manifest(...)` and `FixtureCase`, rather than adding another manifest reader, another case format, or a generated registry for this family.
- Backend parameterization continues to flow through `tests/python/conftest.py` and the shared `regex_backend` fixture, so the consolidated suite uses one central cache-purge/native-availability path instead of repeated `setUp()` / `tearDown()` methods, `sys.path` bootstrap blocks, or per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth already asserted by the seven singleton files:
  - repeated `compile()` identity for the active backend
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`
  - match-result parity for `.group()`, `.groups()`, `.groupdict()`, `.span()`, `.start()`, `.end()`, `.lastindex`, `.lastgroup`, and `.regs` where those assertions exist today
  - named-group access parity for `outer` and `inner` where the pattern exposes them
  - match convenience parity through `match[index]`, `match[name]`, and `expand(...)` for the fixtures whose current pytest modules already assert that surface
  - `None` parity for no-match, absent-branch, optional-group-omitted, and broader-range overflow or missing-replay paths already covered today
- The new suite keeps the current explicit local negative-case coverage for mismatched replay, cross-branch replay, absent-branch failure, and broader-range overflow paths that the current singleton files assert outside the published fixture rows; do not silently drop those checks just because the main workflow tables move onto shared fixtures.
- After the consolidation lands, `rg --files tests/python | rg 'test_(branch_local_backreference|quantified_branch_local_backreference|optional_group_alternation_branch_local_backreference|conditional_group_exists_branch_local_backreference|nested_group_alternation_branch_local_backreference|quantified_alternation_branch_local_backreference|quantified_nested_group_alternation_branch_local_backreference)_parity\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to the branch-local-backreference Python parity surface listed above; do not fold in callable-replacement parity, non-branch-local backreference coverage, correctness-scorecard regeneration, benchmark workloads, or Rust/runtime changes.
- Keep the work on the Python test surface only. Do not change `python/rebar/`, `crates/`, correctness fixtures, benchmark manifests, or published reports to complete it.
- Use ordinary pytest parameterization plus existing shared helpers rather than introducing a new support package, code generation step, or custom fixture schema.

## Notes
- These seven modules total 1,632 lines and currently split one coherent parity frontier across five near-duplicate pytest files plus two older `unittest` classes.
- `ops/tasks/done/RBR-0337-consolidate-remaining-branch-local-backreference-correctness-scorecards.md` already collapsed the scorecard side of this family onto shared expectations; this task brings the Python parity surface up to the same shape instead of leaving branch-local checks scattered across singleton modules.

## Completion
- Added `tests/python/test_branch_local_backreference_parity_suite.py`, a single fixture-backed pytest suite that loads the eight published branch-local-backreference manifests through `load_fixture_manifest(...)`, keeps one manifest-alignment assertion per fixture, and routes backend coverage through the shared `regex_backend` fixture instead of repeated bootstrap, cache handling, and `unittest` skips.
- Preserved the prior parity surface for compile metadata, match metadata, named-group access, and match convenience APIs where the old pytest modules asserted them, while keeping the explicit supplemental miss cases for mismatched replay, cross-branch replay, missing replay, and broader-range overflow paths.
- Deleted the seven superseded parity modules so the branch-local-backreference Python parity frontier now lives in one shared suite.

## Verification
- `.venv/bin/python -m pytest tests/python/test_branch_local_backreference_parity_suite.py -q`
