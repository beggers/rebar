# RBR-0411: Replace literal collection case tables with a fixture-backed parity suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove the duplicate literal collection workflow tables from `tests/python/test_literal_collection_helpers.py`, so the source-tree collection parity suite reads the published `tests/conformance/fixtures/collection_replacement_workflows.py` rows it already shares with correctness reporting and keeps only a small explicit supplement for source-surface-only bounds and error cases.

## Deliverables
- `tests/python/test_literal_collection_helpers.py`

## Acceptance Criteria
- `tests/python/test_literal_collection_helpers.py` loads `tests/conformance/fixtures/collection_replacement_workflows.py` through `load_fixture_manifest(...)` / `FixtureCase` and keeps one manifest-alignment assertion covering exactly these published literal collection rows:
  - `module-split-str-leading-trailing`
  - `module-split-str-no-match`
  - `pattern-split-bytes-maxsplit`
  - `module-findall-bytes-repeated`
  - `pattern-findall-str-no-match`
  - `module-finditer-str-repeated`
  - `pattern-finditer-bytes-bounded`
- The rewritten suite preserves the direct CPython parity currently asserted outside those published rows without re-encoding the shared fixture cases a second time:
  - module and compiled-pattern `split()` still cover the existing additional `str` / `bytes` maxsplit, repeated-match, no-match, and negative-maxsplit cases;
  - module and compiled-pattern `findall()` still cover the existing additional `str` / `bytes` repeated/no-match and bounded `pos` / `endpos` cases;
  - module and compiled-pattern `finditer()` still cover the existing additional `str` / `bytes` repeated/no-match and bounded `pos` / `endpos` cases, including iterator exhaustion and `Match` metadata parity.
- The mismatch `TypeError` surface stays explicit for both module and compiled-pattern collection helpers, with messages still matched against CPython.
- The current loud-placeholder checks stay explicit for unsupported module flags, unsupported nonliteral or empty patterns, and compiled unsupported-flag or empty-pattern collection calls.
- The suite uses the existing pytest import and cache path under `tests/python/conftest.py` instead of file-local repo bootstrap:
  - no `REPO_ROOT` / `PYTHON_SOURCE` constants; and
  - no file-local `sys.path.insert(...)`.
- `module-findall-nonliteral-str` stays owned by `tests/python/test_bounded_wildcard_parity_suite.py`; do not duplicate that nonliteral wildcard row in this suite after the rewrite.
- After the rewrite, `rg -n "REPO_ROOT =|PYTHON_SOURCE =|sys\\.path\\.insert\\(" tests/python/test_literal_collection_helpers.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_literal_collection_helpers.py tests/python/test_bounded_wildcard_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Prefer reusing `tests/python/fixture_parity_support.py` plus ordinary pytest parameterization over adding a new support module or another manifest-specific harness layer.
- Do not broaden this run into `tests/python/test_module_surface_scaffold.py`, `tests/python/test_grouped_literal_replacement_template.py`, `tests/python/test_rust_collection_replacement_boundary.py`, or benchmark-harness cleanup.

## Notes
- The runtime dashboard is clean and current for `HEAD`, the ready queue is empty, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should queue a post-JSON duplicate-fixture cleanup instead of another JSON burn-down task.
- `RBR-0410` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned benchmark catch-up, so this cleanup intentionally uses `RBR-0411`.
- `tests/python/test_literal_collection_helpers.py` is still a `310`-line source-tree parity file with file-local repo bootstrap plus hard-coded `split` / `findall` / `finditer` case tables, even though `tests/conformance/fixtures/collection_replacement_workflows.py` already publishes the overlapping literal collection rows for correctness reporting.
- The existing nonliteral collection row, `module-findall-nonliteral-str`, already lives on `tests/python/test_bounded_wildcard_parity_suite.py`; this cleanup should reduce duplicate literal fixture data without collapsing that separate bounded-wildcard owner.
