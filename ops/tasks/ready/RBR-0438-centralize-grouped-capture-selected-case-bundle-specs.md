# RBR-0438: Centralize grouped-capture selected-case bundle specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining repeated selected-case `load_fixture_bundle(...)` declarations in `tests/python/test_grouped_capture_parity_suite.py` with one small declarative helper path, so the grouped-capture parity surface stops hand-maintaining the same selected-case bundle plumbing after the earlier whole-manifest and selector-backed cleanup passes.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` gains one small declarative helper surface for selected-case bundle declarations that is built on the existing `load_fixture_bundle(...)` path rather than a new registry, generated table, or extra support module. That helper surface owns all of the following:
  - one ordinary local spec value/type for selected-case bundle declarations, covering the current repeated `load_fixture_bundle(...)` inputs in `tests/python/test_grouped_capture_parity_suite.py`:
    - fixture filename;
    - expected manifest id;
    - ordered selected case ids;
    - expected pattern set;
    - expected `(operation, helper)` counter; and
    - optional expected text-model set;
  - one loader that preserves ordered spec-to-`FixtureBundle` materialization while reusing the current `load_fixture_bundle(...)` validation semantics; and
  - automatic exact case-id validation derived from each spec's ordered selected case ids, so the suite no longer repeats the same case ids in both `selected_case_ids` and `expected_case_ids`.
- `tests/python/test_grouped_capture_parity_suite.py` switches its bundle setup to the new declarative selected-case helper surface instead of open-coding eight `load_fixture_bundle(...)` calls.
- The grouped-capture suite keeps its current explicit frontier and suite-local expectations rather than hiding them in support code:
  - the suite still declares its own manifest ids, selected case ids, pattern sets, and `(operation, helper)` counters in the test file;
  - `_compile_cases(...)`, `CompileCase`, `SupplementalMissCase`, `BoundedPatternCase`, the supplemental miss cases, the bounded-pattern cases, the match-group-access case ids, and the `.regs` parity case ids all stay explicit in `tests/python/test_grouped_capture_parity_suite.py`;
  - `MATCH_GROUP_ACCESS_CASES` still uses `load_published_fixture_cases(...)` and the current published selector path; and
  - no fixture membership, selected-case order, case grouping, or parity assertions broaden or shrink as part of the refactor.
- `tests/python/test_grouped_capture_parity_suite.py` also routes its published-case fanout through the existing shared helper surface by setting `PUBLISHED_CASES = fixture_cases_from_bundles(FIXTURE_BUNDLES)` instead of open-coding the bundle-to-case comprehension.
- `tests/python/test_fixture_parity_support_contract.py` adds focused coverage for the new helper behavior:
  - one happy-path selected-case spec load that proves exact case-id validation is derived from the selected case ids and that selected-case order is preserved within a bundle; and
  - one ordered multi-spec load assertion that proves bundle order is preserved across the helper's returned bundle tuple.
- The refactor stays structural only:
  - do not change `tests/conformance/fixtures/*.py`, Rust code, `python/rebar/`, `python/rebar_harness/`, benchmark workloads, published reports, README text, or tracked state files beyond this task file; and
  - do not broaden into `tests/python/test_grouped_literal_replacement_template.py`, `tests/python/test_bounded_wildcard_parity_suite.py`, `tests/python/test_callable_replacement_parity_suite.py`, or other selected-case parity suites in the same run.
- After the cleanup:
  - `rg -n 'load_fixture_bundle\\(' tests/python/test_grouped_capture_parity_suite.py` returns no matches.
  - `rg -n 'expected_case_ids=' tests/python/test_grouped_capture_parity_suite.py` returns no matches.
  - `rg -n 'case for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_grouped_capture_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_capture_parity_suite.py`.

## Constraints
- Prefer extending `tests/python/fixture_parity_support.py` over adding `tests/python/grouped_capture_parity_support.py`, another registry, or another bundle abstraction layer.
- Keep helper names and signatures ordinary and local to the existing fixture-parity support surface; do not add a generic abstraction whose only job is to hide this suite's manifest expectations.
- Preserve the current exact case membership and ordering. This task is about deleting repeated selected-case bundle plumbing, not changing grouped-capture behavior.

## Notes
- `RBR-0437` is already reserved in tracked `README.md`, `ops/state/current_status.md`, and `ops/state/backlog.md` for the next feature-owned conditional replacement benchmark follow-on, so this architecture cleanup starts at `RBR-0438`.
- The runtime dashboard is lagging behind the live checkout (`dashboard HEAD: 8f2e69dee98a5a9426ee090013a9aea6c551d955`, live `git rev-parse HEAD`: `64128afc0094aa8e2be4bbe1f236ec57b21c9b1f`), so JSON status for this run was sized from live checks rather than the lagging report.
- Live JSON checks are fully burned down (`git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), the ready queue is empty, and recent runtime reporting shows no inherited-dirty or post-task refresh stall, so this run should seed one post-JSON duplicate-plumbing cleanup rather than no-op.
- `RBR-0427` already moved `tests/python/test_grouped_capture_parity_suite.py` onto the shared bundle loader, but the suite still carries eight inline selected-case bundle declarations plus one open-coded bundle-to-case fanout because `tests/python/fixture_parity_support.py` still lacks a declarative selected-case spec path.
