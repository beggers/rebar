# RBR-0375: Fold the quantified nested-group alternation callable-replacement parity module into the shared callable suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace `tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py` with one expanded shared suite in `tests/python/test_callable_replacement_parity_suite.py` so this callable frontier stops living across two parallel fixture loaders and near-duplicate parity harnesses.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`
- Delete `tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py`

## Acceptance Criteria
- The shared suite continues to discover published `*callable_replacement_workflows.py` fixtures through its existing `CALLABLE_FIXTURE_PATHS` plus `load_fixture_manifest(...)` path. Do not add another manifest-specific callable-replacement harness, registry, or loader layer.
- `tests/python/test_callable_replacement_parity_suite.py` keeps one explicit manifest-alignment assertion for `quantified_nested_group_alternation_callable_replacement_workflows.py` covering:
  - manifest id `quantified-nested-group-alternation-callable-replacement-workflows`;
  - the published case-id set currently asserted in the standalone module;
  - the exact compile-pattern set `{r"a((b|c)+)d", r"a(?P<outer>(?P<inner>b|c)+)d"}`; and
  - the exact `Counter((operation, helper))` distribution `Counter({("module_call", "sub"): 2, ("module_call", "subn"): 2, ("pattern_call", "sub"): 2, ("pattern_call", "subn"): 2})`.
- The consolidation preserves the current parity depth from the deleted module for this bounded slice inside the shared suite:
  - repeated `compile()` identity plus compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`;
  - module and compiled-`Pattern` `sub()` / `subn()` result parity against CPython for the published fixture rows;
  - callback `Match` snapshot parity for the same rows through the existing callable-replacement support helpers; and
  - explicit callback-no-op coverage for the focused near-miss rows currently hard-coded in the standalone module, including the too-short `zzadzz` miss and the invalid-branch `zzabedzz` miss across both module and compiled-pattern `sub` / `subn()` variants.
- Keep the current literal callable coverage and the rest of the shared published callable-bundle coverage intact. This task deletes split coverage; it must not narrow `tests/python/test_callable_replacement_parity_suite.py` to only the quantified nested-group manifest.
- Reuse the existing local helper path (`tests/python/callable_replacement_support.py`) only if a truly generic helper from the deleted module needs to move. Do not add another support module under `tests/python/` and do not move this callable family into `python/rebar_harness`.
- After the consolidation lands, `rg --files tests/python | rg 'test_quantified_nested_group_alternation_callable_replacement_parity\\.py$'` returns no matches.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README/status files, or queue/state files beyond this task file.
- Do not fold the branch-local-backreference callable suites, the broader `{1,4}` and `{1,}` callable follow-ons, or replacement-template parity into the same run.
- Use ordinary pytest parameterization plus the existing callable/fixture helpers already in the repo. Do not add code generation, another manifest schema, or another bespoke parity wrapper.

## Notes
- `tests/python/test_callable_replacement_parity_suite.py` already globs every published `*callable_replacement_workflows.py` fixture, including `quantified_nested_group_alternation_callable_replacement_workflows.py`.
- `tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py` is still a 245-line legacy singleton that repeats fixture loading, compile metadata assertions, module/pattern result parity, callback match-snapshot parity, and bounded no-match checks for one manifest the shared suite already executes.
- Recent feature tasks such as `RBR-0362` and the current `RBR-0374` already treat the shared callable-replacement suite as the canonical parity surface for this frontier. This cleanup should bring the Python test shape in line with that direction instead of keeping one manifest-specific holdout alive.

## Verification
- `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
- `rg --files tests/python | rg 'test_quantified_nested_group_alternation_callable_replacement_parity\\.py$'`
