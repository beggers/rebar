# RBR-0739: Collapse open-ended supplemental-bytes case sidecar onto canonical surface specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES` tuple from `tests/python/test_open_ended_quantified_group_parity_suite.py` so `OPEN_ENDED_BYTES_CASE_SURFACES` becomes the sole canonical owner of supplemental bytes-case ordering and case payload routing inside the open-ended parity owner.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining or reading `OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES`.
- The seven supplemental-bytes parity tests derive their parametrization directly from `OPEN_ENDED_BYTES_CASE_SURFACES` instead of from the deleted top-level tuple:
  - `test_supplemental_bytes_compile_metadata_matches_cpython`
  - `test_supplemental_bytes_module_search_matches_cpython`
  - `test_supplemental_bytes_module_search_convenience_api_matches_cpython`
  - `test_supplemental_bytes_module_search_match_group_access_matches_cpython`
  - `test_supplemental_bytes_pattern_fullmatch_matches_cpython`
  - `test_supplemental_bytes_pattern_fullmatch_convenience_api_matches_cpython`
  - `test_supplemental_bytes_pattern_fullmatch_match_group_access_matches_cpython`
- Preserve the current effective supplemental-case order exactly. The canonical flattening of `OPEN_ENDED_BYTES_CASE_SURFACES` must stay:
  - `open-ended-grouped-alternation-numbered-bytes`
  - `open-ended-grouped-alternation-named-bytes`
  - `open-ended-grouped-conditional-numbered-bytes`
  - `open-ended-grouped-conditional-named-bytes`
  - `broader-range-open-ended-grouped-alternation-numbered-bytes`
  - `broader-range-open-ended-grouped-alternation-named-bytes`
  - `open-ended-grouped-backtracking-heavy-numbered-bytes`
  - `open-ended-grouped-backtracking-heavy-named-bytes`
  - `broader-range-open-ended-grouped-conditional-numbered-bytes`
  - `broader-range-open-ended-grouped-conditional-named-bytes`
  - `broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes`
  - `broader-range-open-ended-grouped-backtracking-heavy-named-bytes`
  - `nested-open-ended-grouped-alternation-numbered-bytes`
  - `nested-open-ended-grouped-alternation-named-bytes`
- Keep canonical ownership otherwise unchanged:
  - do not change `OPEN_ENDED_BYTES_CASE_SURFACES` membership, `follow_on_id` values, supplemental bytes-case payloads, expected operation-helper counts, expected module-search or pattern-fullmatch text maps, or the current per-spec case ordering;
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `OPEN_ENDED_TRACE_BUNDLES`, `OPEN_ENDED_TRACE_CASES`, or the published direct parity surface they represent; and
  - if a tiny file-local helper is useful, keep it derived from `OPEN_ENDED_BYTES_CASE_SURFACES` instead of introducing another mirrored tuple/list/map block.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_open_ended_quantified_group_parity_suite as mod

assert tuple(case.id for spec in mod.OPEN_ENDED_BYTES_CASE_SURFACES for case in spec.cases) == (
    "open-ended-grouped-alternation-numbered-bytes",
    "open-ended-grouped-alternation-named-bytes",
    "open-ended-grouped-conditional-numbered-bytes",
    "open-ended-grouped-conditional-named-bytes",
    "broader-range-open-ended-grouped-alternation-numbered-bytes",
    "broader-range-open-ended-grouped-alternation-named-bytes",
    "open-ended-grouped-backtracking-heavy-numbered-bytes",
    "open-ended-grouped-backtracking-heavy-named-bytes",
    "broader-range-open-ended-grouped-conditional-numbered-bytes",
    "broader-range-open-ended-grouped-conditional-named-bytes",
    "broader-range-open-ended-grouped-backtracking-heavy-numbered-bytes",
    "broader-range-open-ended-grouped-backtracking-heavy-named-bytes",
    "nested-open-ended-grouped-alternation-numbered-bytes",
    "nested-open-ended-grouped-alternation-named-bytes",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the open-ended parity suite, not to reinterpret which grouped open-ended bytes cases stay explicit, move any family between the shared buckets and the direct follow-on path, or broaden the suite beyond the current published slice.
- Do not edit `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0739` is the next available task id in the current checkout: `rg -n "RBR-0739|RBR-0740|RBR-0741|RBR-0742|RBR-0743|RBR-0744|RBR-0745" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches before this task was added.
- No blocked architecture task exists to reopen first, and rule 10 does not block another cleanup task here: `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added, and `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views: `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l` returned `0`, and `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` currently passes (`3923 passed in 2.69s`);
  - `rg -n "OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES" tests/python/test_open_ended_quantified_group_parity_suite.py` shows one declaration plus the seven target parametrizations in this file;
  - the canonical-order import probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the mirrored tuple still exists.
- This stays on the same bounded open-ended parity-harness cleanup track as `RBR-0725` and `RBR-0727`: those tasks removed generic-bucket and direct-test bucket sidecars from the same owner file, and `OPEN_ENDED_BYTES_CASE_SURFACES` already carries the case payloads and ordering needed to delete this remaining flattened tuple without changing behavior.
