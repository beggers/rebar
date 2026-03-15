# RBR-0400: Consolidate literal-flag parity wrappers into a fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the remaining standalone literal-flag parity wrappers with one fixture-backed pytest owner tied to `tests/conformance/fixtures/literal_flag_workflows.py`, so bounded `IGNORECASE`, inline `(?i)`, and bytes-`LOCALE` flows stop living across three bespoke `unittest` files with duplicate repo bootstrap, cache management, and fake-native-boundary scaffolding.

## Deliverables
- `tests/python/test_literal_flag_parity_suite.py`
- Delete `tests/python/test_literal_ignorecase_behavior.py`
- Delete `tests/python/test_inline_flag_literal_workflows.py`
- Delete `tests/python/test_locale_bytes_literal_workflows.py`

## Acceptance Criteria
- `tests/python/test_literal_flag_parity_suite.py` loads `tests/conformance/fixtures/literal_flag_workflows.py` through `load_fixture_manifest(...)` / `FixtureCase` and keeps one manifest-alignment assertion covering exactly these literal-only rows from manifest id `literal-flag-workflows`, leaving the bounded-wildcard nonliteral row on its existing suite:
  - `flag-module-search-ignorecase-str-hit`
  - `flag-module-search-ignorecase-str-miss`
  - `flag-module-fullmatch-ignorecase-bytes-hit`
  - `flag-pattern-search-ignorecase-str-hit`
  - `flag-pattern-match-ignorecase-bytes-hit`
  - `flag-pattern-fullmatch-ignorecase-str-miss`
  - `flag-cache-hit-bytes-ignorecase`
  - `flag-cache-distinct-str-normalized`
  - `flag-unsupported-inline-flag-search`
  - `flag-unsupported-locale-bytes-search`
- The new suite preserves the direct CPython parity currently split across the three deleted modules without introducing another wrapper layer:
  - module `search()`, `match()`, and `fullmatch()` parity for the bounded literal `IGNORECASE` str/bytes cases already asserted today;
  - compiled `Pattern.search()`, `Pattern.match()`, and `Pattern.fullmatch()` parity for the bounded literal `IGNORECASE` str/bytes cases already asserted today;
  - cache reuse and distinct-entry behavior stay explicit for repeated `compile("abc")`, `compile("abc", rebar.IGNORECASE)`, `compile("abc", rebar.IGNORECASE | rebar.UNICODE)`, and `compile(b"AbC", rebar.IGNORECASE)`;
  - the current bounded placeholder-message checks stay explicit for unsupported `IGNORECASE | ASCII`, collection-helper, and compiled unsupported-flag paths.
- The suite absorbs the direct inline-flag and bytes-`LOCALE` workflow parity from the deleted wrappers through shared pytest flow instead of standalone `@unittest.skipUnless(...)` modules:
  - `rebar.search("(?i)abc", "ABC")` and `rebar.compile("(?i)abc").search("ABC")` still match CPython when `rebar._rebar` is available, including compiled flag parity;
  - `rebar.search(b"abc", b"abc", rebar.LOCALE)` and `rebar.compile(b"abc", rebar.LOCALE).search(b"abc")` still match CPython when `rebar._rebar` is available, including compiled flag parity.
- The new suite absorbs the fake-native-boundary observations from `tests/python/test_inline_flag_literal_workflows.py` and `tests/python/test_locale_bytes_literal_workflows.py` by patching `rebar._native` inside pytest:
  - `rebar.purge()` still triggers the fake purge hook;
  - inline `(?i)abc` search still records the current `("compile", "(?i)abc", 0)` then `("match", "(?i)abc", int(rebar.IGNORECASE | rebar.UNICODE), "search", "ABC", 0, None)` sequence for both module and compiled-search flows;
  - bytes `LOCALE` search still records the current `("compile", b"abc", int(rebar.LOCALE))` then `("match", b"abc", int(rebar.LOCALE), "search", b"abc", 0, None)` sequence through module and compiled-search flows.
- The inline-locale diagnostic regression formerly checked from `tests/python/test_locale_bytes_literal_workflows.py` stays covered by the existing `tests/python/test_parser_matrix_parity_suite.py` row `str-inline-locale-flag-error`; do not duplicate a second bespoke diagnostic wrapper if that suite already preserves type/message/position parity.
- Backend setup and cache purging continue to flow through `tests/python/conftest.py`; the consolidated suite does not reintroduce file-local `sys.path` bootstrapping, `setUp()` / `tearDown()`, `unittest.TestCase`, or another literal-flag-specific support module.
- After the consolidation lands, `rg --files tests/python | rg 'test_(literal_ignorecase_behavior|inline_flag_literal_workflows|locale_bytes_literal_workflows)\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/python/test_parser_matrix_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep `flag-unsupported-nonliteral-ignorecase-search` on `tests/python/test_bounded_wildcard_parity_suite.py`; do not broaden this cleanup into bounded-wildcard or collection/replacement refactors in the same run.
- Prefer one readable pytest module plus deleted wrappers over another helper layer. If small generic reuse is needed, keep it inside `tests/python/fixture_parity_support.py`.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/conformance/fixtures/literal_flag_workflows.py` already publishes `11` cases, but Python parity ownership for its literal rows is still split across `tests/python/test_literal_ignorecase_behavior.py`, `tests/python/test_inline_flag_literal_workflows.py`, and `tests/python/test_locale_bytes_literal_workflows.py`, while `tests/python/test_bounded_wildcard_parity_suite.py` separately owns the nonliteral wildcard row from the same manifest.
- The three targeted wrappers total `326` lines of repeated repo bootstrap, manual cache purging, built-native gating, and fake-native-boundary scaffolding that can now live on one standard pytest path.

## Completion
- 2026-03-15: Replaced the three standalone `unittest` wrappers with `tests/python/test_literal_flag_parity_suite.py`, selecting the ten literal-only `literal-flag-workflows` rows through `load_fixture_manifest(...)` / `FixtureCase` while keeping direct pytest coverage for bounded `IGNORECASE`, cache reuse and distinct entries, unsupported placeholder paths, built-native inline/bytes-`LOCALE` parity, and the fake-native-boundary call sequences.
- 2026-03-15: Deleted `tests/python/test_literal_ignorecase_behavior.py`, `tests/python/test_inline_flag_literal_workflows.py`, and `tests/python/test_locale_bytes_literal_workflows.py`.
- 2026-03-15: Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/python/test_parser_matrix_parity_suite.py` (`72 passed, 21 skipped`) and confirmed `rg --files tests/python | rg 'test_(literal_ignorecase_behavior|inline_flag_literal_workflows|locale_bytes_literal_workflows)\.py$'` returns no matches.
