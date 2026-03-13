# RBR-0263: Consolidate the open-ended quantified-group parity frontier into one backend-parameterized pytest suite

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Replace the six current open-ended quantified-group parity `unittest` modules with one backend-parameterized pytest suite so the just-landed `{1,}` and `{2,}` grouped frontier is asserted through one Python-path contract instead of repeated case tables and native-gate boilerplate.

## Deliverables
- `pyproject.toml`
- `tests/python/conftest.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- Delete the superseded frontier-specific parity modules under `tests/python/`:
- `tests/python/test_open_ended_quantified_group_alternation_parity.py`
- `tests/python/test_open_ended_quantified_group_alternation_conditional_parity.py`
- `tests/python/test_open_ended_quantified_group_alternation_backtracking_heavy_parity.py`
- `tests/python/test_broader_range_open_ended_quantified_group_alternation_parity.py`
- `tests/python/test_broader_range_open_ended_quantified_group_alternation_conditional_parity.py`
- `tests/python/test_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_parity.py`

## Acceptance Criteria
- The new pytest suite covers the numbered and named compile, `module.search()`, and compiled-`Pattern.fullmatch()` parity observations currently spread across the six superseded modules for:
- `a(bc|de){1,}d` and `a(?P<word>bc|de){1,}d`
- `a((bc|de){1,})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,})?(?(outer)d|e)`
- `a((bc|b)c){1,}d` and `a(?P<word>(bc|b)c){1,}d`
- `a(bc|de){2,}d` and `a(?P<word>bc|de){2,}d`
- `a((bc|de){2,})?(?(1)d|e)` and `a(?P<outer>(bc|de){2,})?(?(outer)d|e)`
- `a((bc|b)c){2,}d` and `a(?P<word>(bc|b)c){2,}d`
- Case definitions are data-driven and backend-parameterized so the same observations run against stdlib `re` and public `rebar` entrypoints, with one central native-availability gate instead of repeated per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth for compile metadata and match objects: `.pattern`, `.flags`, `.groups`, `.groupindex`, `Match.group()`, `.groups()`, `.groupdict()`, `.span()`, `.start()`, `.end()`, `.lastindex`, and `.lastgroup`.
- `pytest` becomes an explicit tracked test dependency or configuration surface for this suite; the task must not rely on undeclared ambient tooling.
- Once the new suite is in place, the six old frontier-specific parity modules are removed so the grouped `{1,}`/`{2,}` frontier no longer duplicates the same Python-path contract in multiple files.

## Constraints
- Keep this task scoped to the six current open-ended quantified-group parity modules; do not attempt a repo-wide parity-suite migration here.
- Keep the work on the Python test surface only. Do not change Rust or `python/rebar/` runtime behavior to complete this task.
- Use ordinary Python fixtures and case tables rather than adding JSON manifests, generators, or new benchmark plumbing.

## Notes
- Build on `RBR-0262`.
- This task exists because the benchmark wrapper surface is now consolidated, but the parity surface for the current grouped frontier still lives in six near-duplicate `unittest` modules rather than the intended backend-parameterized pytest harness.

## Completion
- Completed 2026-03-13.
- Added explicit `pytest` test dependency/configuration in `pyproject.toml`, created `tests/python/conftest.py` with shared Python-path setup, cache purging, and one native-gated `regex_backend` fixture, and replaced the six frontier-specific `unittest` modules with `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Verified with `/tmp/rebar-pytest-venv/bin/python -m pytest tests/python/test_open_ended_quantified_group_parity_suite.py -q` (`72 passed`).
