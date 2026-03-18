# RBR-0638: Collapse the detached simple-backreference parity suite onto the shared backreference owner

Status: done
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_simple_backreference_parity_suite.py` by moving its named and numbered backreference coverage onto `tests/python/test_branch_local_backreference_parity_suite.py`, so the backreference frontier lives on one fixture-backed owner suite instead of a second small module that repeats the same compile/workflow/bounds/miss structure.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`
- Delete `tests/python/test_simple_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` becomes the sole owner for the simple named/numbered backreference surface:
  - absorb `named-backreference-workflows` and `numbered-backreference-workflows` into `FIXTURE_BUNDLE_SPECS` ahead of the existing branch-local manifests;
  - preserve the current simple-backreference case ids, pattern sets, and `Counter((operation, helper), ...)` expectations exactly instead of reinterpreting the frontier; and
  - keep the absorbed rows on the suite's existing shared compile/workflow paths rather than another helper module, manifest wrapper, or sibling suite.
- The shared workflow coverage in `tests/python/test_branch_local_backreference_parity_suite.py` keeps the absorbed simple rows on the same explicit convenience and group-access surfaces they already use today:
  - `MATCH_CONVENIENCE_CASE_IDS` or an equivalent file-local selector includes all six simple workflow case ids:
    - `named-backreference-module-search-str`
    - `named-backreference-pattern-search-str`
    - `numbered-backreference-module-search-str`
    - `numbered-backreference-pattern-search-str`
    - `numbered-backreference-segment-module-search-str`
    - `numbered-backreference-prefix-pattern-search-str`
  - `MATCH_GROUP_ACCESS_CASE_IDS` or an equivalent file-local selector includes the same six case ids, so the named/numbered search rows and the grouped-segment/prefix search pair still receive both valid and invalid accessor parity coverage.
- The existing bounded-window coverage from `tests/python/test_simple_backreference_parity_suite.py` survives unchanged on the shared backreference owner:
  - absorb these `PATTERN_BOUNDS_MATCH_CASES` ids with the same `pattern_case_id`, `helper`, `string`, and `bounds` payloads:
    - `numbered-backreference-match-honors-narrowed-window`
    - `named-backreference-fullmatch-honors-narrowed-window`
    - `numbered-backreference-segment-search-honors-narrowed-window`
    - `numbered-backreference-prefix-search-normalizes-negative-and-oversized-bounds`
  - absorb these `PATTERN_BOUNDS_NO_MATCH_CASES` ids with the same payloads:
    - `numbered-backreference-search-skips-match-before-pos`
    - `named-backreference-fullmatch-does-not-expand-to-the-whole-string`
    - `numbered-backreference-segment-search-skips-match-before-pos`
    - `numbered-backreference-prefix-search-fails-when-endpos-truncates-the-replay`
- The current negative-path miss coverage survives on the shared backreference owner:
  - preserve the named, numbered, and grouped-segment miss texts (`"zzabzz"` and `"zzz"`) for both module and compiled-pattern paths on the existing supplemental negative-path assertion surface instead of dropping them or moving them into another helper.
- `tests/python/test_simple_backreference_parity_suite.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or `*_support.py` helper behind; and
  - keep the end state on the existing shared backreference owner suite rather than replacing one detached file with another.
- Keep scope structural only:
  - do not change correctness fixtures, benchmark manifests, reports, Rust code, `python/rebar/`, or `tests/python/fixture_parity_support.py`; and
  - do not broaden into benchmark-anchor cleanup, named/numbered correctness-manifest consolidation, or a cross-family suite rename in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_branch_local_backreference_parity_suite as mod

expected_simple_workflow_case_ids = {
    "named-backreference-module-search-str",
    "named-backreference-pattern-search-str",
    "numbered-backreference-module-search-str",
    "numbered-backreference-pattern-search-str",
    "numbered-backreference-segment-module-search-str",
    "numbered-backreference-prefix-pattern-search-str",
}

assert tuple(spec.expected_manifest_id for spec in mod.FIXTURE_BUNDLE_SPECS[:2]) == (
    "named-backreference-workflows",
    "numbered-backreference-workflows",
)
assert expected_simple_workflow_case_ids.issubset(mod.MATCH_CONVENIENCE_CASE_IDS)
assert expected_simple_workflow_case_ids.issubset(set(mod.MATCH_GROUP_ACCESS_CASE_IDS))
assert {
    "numbered-backreference-match-honors-narrowed-window",
    "named-backreference-fullmatch-honors-narrowed-window",
    "numbered-backreference-segment-search-honors-narrowed-window",
    "numbered-backreference-prefix-search-normalizes-negative-and-oversized-bounds",
}.issubset({case.id for case in mod.PATTERN_BOUNDS_MATCH_CASES})
assert {
    "numbered-backreference-search-skips-match-before-pos",
    "named-backreference-fullmatch-does-not-expand-to-the-whole-string",
    "numbered-backreference-segment-search-skips-match-before-pos",
    "numbered-backreference-prefix-search-fails-when-endpos-truncates-the-replay",
}.issubset({case.id for case in mod.PATTERN_BOUNDS_NO_MATCH_CASES})
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_simple_backreference_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change runtime behavior, fixture contents, bytes routing, benchmark-anchor coverage, or published reports.
- Prefer one real owner suite with file-local tables over another helper layer or a renamed family split.
- Preserve the current named/numbered case ids and bounded negative-path texts exactly; the point is to delete a redundant owner file, not to reinterpret the simple backreference slice.

## Notes
- `RBR-0638` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-063[8-9]|RBR-064[0-9]" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returns no reserved or active task in that range outside a stale range note inside `RBR-0634`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task is the feature-owned `RBR-0637`, with both task workers finishing `done` in the latest dashboard cycle.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_simple_backreference_parity_suite.py` is `388` lines and `tests/python/test_branch_local_backreference_parity_suite.py` is `1870` lines;
  - the two suites already pass together on the live checkout with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_simple_backreference_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` (`520 passed in 0.80s`);
  - `tests/python/test_simple_backreference_parity_suite.py` carries only two manifests and repeats the same fixture-backed compile/workflow/bounds/miss ownership shape already present in the larger branch-local suite; and
  - `rg -n "test_simple_backreference_parity_suite\\.py|simple_backreference_parity_suite|named-backreference-workflows|numbered-backreference-workflows" tests python ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/state` shows no other active code depending on the suite file path outside the suite itself plus the underlying manifest/fixture contract checks.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` passes (`477 passed in 0.77s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` passes (`162 passed in 0.20s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above currently fails exactly on this cleanup because `tests/python/test_branch_local_backreference_parity_suite.py` still starts with the branch-local manifests and does not yet expose the simple workflow or bounded-window surfaces there; and
  - `bash -lc "! rg --files tests/python | rg 'test_simple_backreference_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite file still exists.

## Completion Notes
- 2026-03-18: Folded `named-backreference-workflows` and `numbered-backreference-workflows` into `tests/python/test_branch_local_backreference_parity_suite.py`, added the six simple workflow case ids to the shared match-convenience and match-group-access selectors, preserved the four bounded-window match rows, four bounded-window no-match rows, and the named/numbered/grouped-segment miss texts on the shared supplemental miss surface, and deleted `tests/python/test_simple_backreference_parity_suite.py`.
- 2026-03-18: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` (`559 passed in 0.85s`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` (`162 passed in 0.20s`), the task’s inline `PY` probe (`ok`), `bash -lc "! rg --files tests/python | rg 'test_simple_backreference_parity_suite\\.py$'"` (passes), and `git diff --name-status -- tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_simple_backreference_parity_suite.py` (`M` on the shared suite and `D` on the deleted detached suite).
