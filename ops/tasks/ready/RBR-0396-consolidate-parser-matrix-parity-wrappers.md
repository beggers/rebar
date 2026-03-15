# RBR-0396: Consolidate the parser-matrix parity wrappers into one fixture-backed pytest suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Delete the five remaining legacy parser-matrix parity wrappers by replacing them with one fixture-backed pytest suite tied directly to `tests/conformance/fixtures/parser_matrix.py`, so this compile-only parser surface stops living across repeated `unittest` classes, repeated repo bootstrap code, repeated cache-purge hooks, and repeated file-local CPython parity helpers.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`
- Delete `tests/python/test_parser_character_class_parity.py`
- Delete `tests/python/test_parser_construct_compile_parity.py`
- Delete `tests/python/test_parser_diagnostic_parity.py`
- Delete `tests/python/test_parser_inline_flag_parity.py`
- Delete `tests/python/test_parser_lookbehind_parity.py`

## Acceptance Criteria
- The new suite loads its published parser rows through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` from exactly `tests/conformance/fixtures/parser_matrix.py` instead of restating the same patterns, flags, and expected behaviors across five standalone modules.
- The suite keeps one manifest-alignment assertion for the absorbed parser subset, pinning `manifest_id == "parser-matrix"` and exactly these case ids:
- `str-character-class-ignorecase-success`
- `str-possessive-quantifier-success`
- `str-atomic-group-success`
- `str-fixed-width-lookbehind-success`
- `str-variable-width-lookbehind-error`
- `str-nested-set-warning`
- `str-invalid-repeat-error`
- `str-invalid-inline-flag-position-error`
- `str-inline-unicode-flag-success`
- `str-inline-locale-flag-error`
- `bytes-inline-unicode-flag-error`
- `bytes-inline-locale-flag-success`
- `bytes-unicode-escape-error`
- The consolidated suite preserves the current compile-only success coverage for the supported parser rows already exercised today:
- compile identity for the active backend on repeated `compile(...)` calls;
- compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`;
- `Pattern.search(...)` remains the current scaffold placeholder for the successful compile-only rows already checked by the deleted modules (`str-character-class-ignorecase-success`, `str-possessive-quantifier-success`, `str-atomic-group-success`, `str-fixed-width-lookbehind-success`, `str-inline-unicode-flag-success`, `bytes-inline-locale-flag-success`, and `str-nested-set-warning`).
- The consolidated suite preserves the current cache and purge observations from the deleted modules:
- normalized-flag cache identity for the character-class row, where `IGNORECASE` and `IGNORECASE | UNICODE` still resolve to the same compiled object;
- repeated compile identity plus post-`purge()` object replacement for the possessive, atomic-group, fixed-width lookbehind, inline-flag, and nested-set warning rows;
- warning re-emission for `str-nested-set-warning` after `purge()`.
- The consolidated suite preserves the current warning and diagnostic parity depth:
- `str-nested-set-warning` still matches CPython on warning category and message;
- `str-invalid-repeat-error`, `str-invalid-inline-flag-position-error`, `str-inline-locale-flag-error`, `bytes-inline-unicode-flag-error`, and `bytes-unicode-escape-error` still match CPython on exception type, message text, `pos`, `lineno`, and `colno`;
- `str-variable-width-lookbehind-error` still matches the current CPython-shaped message while keeping `pos`, `lineno`, and `colno` at `None`.
- The `rebar` path keeps the current no-stdlib-delegation coverage already asserted by the deleted wrappers by patching `rebar._stdlib_re.compile` inside the shared suite for:
- `str-character-class-ignorecase-success`
- `str-possessive-quantifier-success`
- `str-atomic-group-success`
- `str-fixed-width-lookbehind-success`
- `str-variable-width-lookbehind-error`
- `str-inline-unicode-flag-success`
- `bytes-inline-locale-flag-success`
- Backend parameterization flows through `tests/python/conftest.py` and the existing `regex_backend` fixture so the new suite uses the shared cache-purge hook and native-availability gate instead of file-local `setUp()` / `tearDown()` methods, `sys.path` bootstrapping, or repeated `@unittest.skipUnless(...)` decorators.
- If helper extraction is needed, keep it inside `tests/python/fixture_parity_support.py`; do not add another parser-specific support module or another manifest reader.
- After the consolidation lands, `rg --files tests/python | rg 'test_parser_(character_class|construct_compile|diagnostic|inline_flag|lookbehind)_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the absorbed scope bounded to the parser-matrix rows already covered by the five deleted modules. Do not broaden the cleanup into the literal baseline parser rows, `tests/python/test_conditional_group_exists_assertion_diagnostic_parity.py`, or another parser frontier in the same run.
- Prefer one readable fixture-backed pytest suite plus deleted wrappers over another compatibility layer. Do not introduce generators, codegen, or another bespoke parser harness abstraction.

## Notes
- The current runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are already zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- The five targeted parser wrappers still total 373 lines of repeated repo bootstrap, manual cache management, compile metadata assertions, and direct CPython comparison even though the same bounded surface already lives as ordinary Python data in `tests/conformance/fixtures/parser_matrix.py`.
- This cleanup should follow the same repo shape as the recent parity consolidations: one fixture-backed pytest suite, one explicit manifest-alignment assertion for the absorbed subset, and no new helper layer unless a generic addition to `tests/python/fixture_parity_support.py` clearly reduces duplication.
