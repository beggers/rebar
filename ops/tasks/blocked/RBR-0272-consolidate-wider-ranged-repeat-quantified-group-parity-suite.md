# RBR-0272: Consolidate the wider-ranged-repeat quantified-group parity frontier into one backend-parameterized pytest suite

Status: blocked
Owner: architecture-implementation
Created: 2026-03-13

## Goal
- Replace the current wider-ranged-repeat quantified-group parity `unittest` modules with one legible backend-parameterized pytest suite so this grouped counted-repeat frontier grows in one place instead of accumulating more native-gated standalone files.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- Delete the superseded frontier-specific parity modules under `tests/python/`:
- `tests/python/test_wider_ranged_repeat_quantified_group_parity.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_parity.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_broader_range_parity.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_conditional_parity.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_conditional_broader_range_parity.py`

## Acceptance Criteria
- The new suite covers the numbered and named compile, `module.search()`, and compiled-`Pattern.fullmatch()` parity observations currently spread across the four landed wider-ranged-repeat modules plus the post-`RBR-0271` broader-range conditional module for:
- `a(bc){1,3}d` and `a(?P<word>bc){1,3}d`
- `a((bc|de){1,3})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,3})?(?(outer)d|e)`
- `a((bc|b)c){1,3}d` and `a(?P<word>(bc|b)c){1,3}d`
- `a(bc|de){1,4}d` and `a(?P<word>bc|de){1,4}d`
- `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)`
- Case definitions are data-driven and backend-parameterized through the existing pytest backend fixture in `tests/python/conftest.py`, with one central native-availability gate instead of repeated per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth for compile metadata and match objects: `.pattern`, `.flags`, `.groups`, `.groupindex`, `Match.group()`, `.groups()`, `.groupdict()`, `.span()`, `.start()`, `.end()`, `.lastindex`, and `.lastgroup`, including the second capture group for conditional and backtracking-heavy cases and named-group access where present.
- Once the new suite is in place, none of the five superseded wider-ranged-repeat parity modules remain; the post-`RBR-0271` broader-range grouped-conditional slice is absorbed into the suite instead of living in another singleton file.

## Constraints
- Keep this task scoped to the wider-ranged-repeat quantified-group frontier listed above; do not attempt a repo-wide parity-suite migration here.
- Keep the work on the Python parity surface only. Do not change Rust, `python/rebar/`, correctness fixtures, or benchmark workload/report plumbing to complete it.
- Use ordinary Python case tables and shared pytest helpers rather than adding JSON manifests, generators, or new harness layers.

## Notes
- Build on `RBR-0271`.
- `RBR-0263` already established the intended pattern for grouped counted-repeat parity work with `tests/python/test_open_ended_quantified_group_parity_suite.py`; this task applies the same simplification to the still-duplicated `{1,3}` and `{1,4}` wider-ranged-repeat grouped frontier.

## Blocker Note
- Blocked on `RBR-0271`. In this checkout, `.venv/bin/python` still raises `NotImplementedError` from `rebar.compile()` for `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)`, so the required broader-range grouped-conditional coverage cannot be absorbed into the consolidated parity suite without masking an unmet feature dependency.
