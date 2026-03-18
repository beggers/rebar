# RBR-0628: Collapse the grouped replacement-template parity suite onto shared owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_grouped_literal_replacement_template.py` by moving its grouped-match rows onto `tests/python/test_grouped_capture_parity_suite.py` and its grouped/named replacement-template rows onto `tests/python/test_fixture_backed_replacement_parity_suite.py`, so the replacement lane stops carrying a detached 777-line owner file beside the existing shared grouped-capture and replacement parity suites.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- Delete `tests/python/test_grouped_literal_replacement_template.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` becomes the sole direct owner of the current `grouped-match-workflows` frontier instead of leaving two single-capture rows on the deleted grouped-template suite:
  - `GROUPED_MATCH_TRACKED_CASE_IDS` expands to exactly:
    - `grouped-module-search-single-capture-str`
    - `grouped-module-fullmatch-single-capture-str`
    - `grouped-pattern-search-single-capture-str`
    - `grouped-pattern-match-single-capture-str`
    - `grouped-module-fullmatch-two-capture-gap-str`
    - `grouped-pattern-fullmatch-two-capture-gap-str`
  - `GROUPED_MATCH_UNCOVERED_CASE_IDS` becomes empty instead of leaving the fullmatch/match single-capture rows delegated to another file; and
  - the grouped-capture suite keeps those rows on its existing compile/module/pattern/match-group-access information flow without introducing another helper module, manifest wrapper, or compatibility shell.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` absorbs every replacement-template surface that is currently stranded on `tests/python/test_grouped_literal_replacement_template.py`, and no replacement-template coverage is left on the deleted file:
  - the absorbed grouped-template/replacement surface keeps the current fixture ownership explicit through one file-local `ReplacementSurfaceSpec` in `tests/python/test_fixture_backed_replacement_parity_suite.py`;
  - that absorbed surface covers exactly these current manifest ids and selected-case surface ids:
    - `collection-replacement-workflows` with the selected `module-sub-grouping-template` row;
    - `named-group-replacement-workflows`;
    - `grouped-alternation-replacement-workflows`;
    - `nested-group-replacement-workflows`;
    - `nested-group-alternation-replacement-workflows`;
    - `nested-group-alternation-wrapper-replacement-workflows`;
    - `quantified-nested-group-replacement-workflows`;
  - the absorbed rows stay on the existing shared replacement parity path:
    - compile metadata still runs through `compile_with_cpython_parity(...)`;
    - module and compiled-`Pattern` replacement parity still runs through the existing shared replacement assertions already used in `tests/python/test_fixture_backed_replacement_parity_suite.py`;
    - grouped/named template-expand assertions remain explicit on the shared replacement owner instead of moving into a new sibling suite; and
    - the current grouped/nested no-match and repeated-replacement supplements remain covered without inventing another replacement-only helper layer;
  - keep this absorbed grouped replacement surface `str`-only; do not turn this cleanup into a bytes follow-on, a callable-replacement merge, a selector-plumbing rewrite, or a correctness-fixture change.
- Keep the structure ordinary and local:
  - prefer extending the two existing owner suites over adding a new support module, selector, registry, or forwarding shell; and
  - do not leave `tests/python/test_grouped_literal_replacement_template.py` behind as an import-only shim.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_grouped_capture_parity_suite as grouped
from tests.python import test_fixture_backed_replacement_parity_suite as repl

assert grouped.GROUPED_MATCH_TRACKED_CASE_IDS == (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-module-fullmatch-two-capture-gap-str",
    "grouped-pattern-fullmatch-two-capture-gap-str",
)
assert grouped.GROUPED_MATCH_UNCOVERED_CASE_IDS == ()
assert tuple(surface.spec.id for surface in repl.REPLACEMENT_SURFACES) == (
    "grouped-replacement-template",
    "open-ended-quantified-group-replacement",
    "conditional-group-exists-replacement",
)
assert tuple(
    bundle.expected_manifest_id for bundle in repl.REPLACEMENT_SURFACES[0].bundles
) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "nested-group-alternation-wrapper-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_grouped_literal_replacement_template\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_grouped_capture_parity_suite as grouped
from tests.python import test_fixture_backed_replacement_parity_suite as repl

assert grouped.GROUPED_MATCH_TRACKED_CASE_IDS == (
    "grouped-module-search-single-capture-str",
    "grouped-module-fullmatch-single-capture-str",
    "grouped-pattern-search-single-capture-str",
    "grouped-pattern-match-single-capture-str",
    "grouped-module-fullmatch-two-capture-gap-str",
    "grouped-pattern-fullmatch-two-capture-gap-str",
)
assert grouped.GROUPED_MATCH_UNCOVERED_CASE_IDS == ()
assert tuple(surface.spec.id for surface in repl.REPLACEMENT_SURFACES) == (
    "grouped-replacement-template",
    "open-ended-quantified-group-replacement",
    "conditional-group-exists-replacement",
)
assert tuple(
    bundle.expected_manifest_id for bundle in repl.REPLACEMENT_SURFACES[0].bundles
) == (
    "collection-replacement-workflows",
    "named-group-replacement-workflows",
    "grouped-alternation-replacement-workflows",
    "nested-group-replacement-workflows",
    "nested-group-alternation-replacement-workflows",
    "nested-group-alternation-wrapper-replacement-workflows",
    "quantified-nested-group-replacement-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_grouped_literal_replacement_template\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, correctness fixtures under `tests/conformance/fixtures/`, benchmark workloads, reports, Rust code, or `python/rebar/`.
- Do not broaden into `tests/python/test_callable_replacement_parity_suite.py`, selector constants in `python/rebar_harness/correctness.py`, or a new replacement-manifest registry layer.
- Preserve the current grouped/named replacement-template and grouped single-capture parity coverage while moving ownership; do not narrow the covered case frontier as part of deleting the detached suite.

## Notes
- `RBR-0628` is the next available task id:
  - `rg -n "RBR-0628|RBR-0629|RBR-0630" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0628'` returned no matches before this file was added.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest dashboard cycle shows both task workers finishing at `done`, so the shared queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete in the current checkout:
  - `tests/python/test_grouped_literal_replacement_template.py` is `777` lines, `tests/python/test_grouped_capture_parity_suite.py` is `887` lines, and `tests/python/test_fixture_backed_replacement_parity_suite.py` is `1476` lines;
  - `tests/python/test_grouped_capture_parity_suite.py` already owns `grouped-match-workflows` but still leaves `grouped-module-fullmatch-single-capture-str` and `grouped-pattern-match-single-capture-str` in `GROUPED_MATCH_UNCOVERED_CASE_IDS`; and
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` already owns the adjacent shared replacement-template lane through file-local `ReplacementSurfaceSpec` tables, so the grouped/named replacement manifests can move there without inventing another harness path.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py tests/python/test_fixture_backed_replacement_parity_suite.py` passes (`876 passed in 0.63s`);
  - the inline ownership probe above currently fails exactly on this cleanup with `AssertionError` because the grouped-capture suite still leaves two grouped-match rows uncovered and `tests/python/test_fixture_backed_replacement_parity_suite.py` still exposes only the `open-ended-quantified-group-replacement` and `conditional-group-exists-replacement` surfaces; and
  - `bash -lc "! rg --files tests/python | rg 'test_grouped_literal_replacement_template\\.py$'"` currently fails exactly on this cleanup because the detached grouped replacement-template suite still exists.
