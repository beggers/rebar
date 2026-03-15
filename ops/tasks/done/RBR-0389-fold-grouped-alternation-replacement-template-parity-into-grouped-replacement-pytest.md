# RBR-0389: Fold grouped-alternation replacement-template parity into the grouped replacement pytest module

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove `tests/python/test_grouped_alternation_replacement_template_parity.py` as a standalone parity surface by folding its bounded grouped-alternation replacement-template coverage into `tests/python/test_grouped_literal_replacement_template.py`, so the grouped replacement frontier no longer keeps this numbered and named alternation slice on a legacy `unittest` path with private `sys.path` bootstrapping and file-local case tuples.

## Deliverables
- `tests/python/test_grouped_literal_replacement_template.py`
- Delete `tests/python/test_grouped_alternation_replacement_template_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_literal_replacement_template.py` absorbs `tests/conformance/fixtures/grouped_alternation_replacement_workflows.py` through the module's existing fixture-backed pytest path instead of leaving grouped alternation replacement on a separate `unittest` module.
- The grouped replacement pytest module keeps the absorbed grouped-alternation fixture explicit by adding one manifest-alignment assertion covering exactly these published case ids and no broader alternation frontier:
  - `module-sub-template-grouped-alternation-str`
  - `module-subn-template-grouped-alternation-str`
  - `pattern-sub-template-grouped-alternation-str`
  - `pattern-subn-template-grouped-alternation-str`
  - `module-sub-template-named-grouped-alternation-str`
  - `module-subn-template-named-grouped-alternation-str`
  - `pattern-sub-template-named-grouped-alternation-str`
  - `pattern-subn-template-named-grouped-alternation-str`
- The absorbed grouped-alternation replacement bundle keeps the current manifest contract explicit inside `tests/python/test_grouped_literal_replacement_template.py`:
  - manifest id `grouped-alternation-replacement-workflows`
  - compile patterns `a(b|c)d` and `a(?P<word>b|c)d`
  - operation/helper counts `("module_call", "sub"): 2`, `("module_call", "subn"): 2`, `("pattern_call", "sub"): 2`, and `("pattern_call", "subn"): 2`
- The absorbed grouped-alternation slice reuses the module's existing shared pytest flow rather than new local helpers, so this slice now receives:
  - compile metadata parity through the same `regex_backend` path already used by the grouped replacement pytest module
  - direct module `sub()` and `subn()` result parity for the published numbered and named grouped-alternation replacement rows
  - direct compiled-`Pattern` `sub()` and `subn()` result parity for the published numbered and named grouped-alternation replacement rows
- The consolidation preserves the existing grouped literal replacement-template and grouped single-capture match assertions already anchored in `tests/conformance/fixtures/collection_replacement_workflows.py` and `tests/conformance/fixtures/grouped_match_workflows.py`; do not delete or silently narrow that current grouped replacement coverage while absorbing the alternation slice.
- No new suite, support module, manifest registry, or generated case layer is introduced. Expand the existing grouped replacement pytest module directly.
- After the consolidation lands, `rg --files tests/python | rg 'test_grouped_alternation_replacement_template_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the grouped-alternation replacement rows on the existing grouped replacement pytest path. Do not create a second grouped-replacement suite and do not broaden this cleanup into nested-group replacement, quantified nested-group replacement, callable replacement, or benchmark catch-up work.
- Reuse the existing helpers already in the repo, especially `load_fixture_manifest(...)`, `FixtureCase`, and the backend-parameterized `regex_backend` fixture, instead of adding another fixture loader or file-local parity harness.

## Notes
- Both tracked and live JSON counts are zero in the current checkout (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_grouped_alternation_replacement_template_parity.py` is still a 76-line standalone `unittest` module with local `sys.path` bootstrapping, manual cache purges, and hand-maintained numbered and named replacement cases that restate the exact workflows already published in `tests/conformance/fixtures/grouped_alternation_replacement_workflows.py`.
- `tests/python/test_grouped_literal_replacement_template.py` already owns the adjacent grouped literal replacement-template and grouped single-capture match surface through a shared fixture-backed pytest path, making it the natural home for this remaining grouped replacement wrapper.

## Completion
- Completed 2026-03-15.
- Folded the grouped-alternation replacement-template rows from `tests/conformance/fixtures/grouped_alternation_replacement_workflows.py` into `tests/python/test_grouped_literal_replacement_template.py`, adding one manifest-alignment assertion for the exact eight published case ids plus compile-pattern and operation/helper-count coverage, and reusing the shared `regex_backend` pytest path for compile, module, and compiled-`Pattern` parity checks.
- Removed the superseded `tests/python/test_grouped_alternation_replacement_template_parity.py` standalone `unittest` wrapper.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py` (`44 passed`) and `rg --files tests/python | rg 'test_grouped_alternation_replacement_template_parity\.py$'` (no matches).
