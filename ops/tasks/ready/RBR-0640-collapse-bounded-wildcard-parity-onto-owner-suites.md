# RBR-0640: Collapse the bounded-wildcard parity suite onto the literal-flag and module-workflow owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_bounded_wildcard_parity_suite.py` by moving its literal-flag and collection/helper coverage onto `tests/python/test_literal_flag_parity_suite.py` and `tests/python/test_module_workflow_parity_suite.py`, so the bounded nonliteral `a.c` slice stops living on a detached cross-cutting suite with a special delegated-case constant.

## Deliverables
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/fixture_parity_support.py`
- Delete `tests/python/test_bounded_wildcard_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_literal_flag_parity_suite.py` becomes the sole owner for the published `literal-flag-workflows` manifest:
  - absorb `flag-unsupported-nonliteral-ignorecase-search` into `TARGET_FIXTURE_CASE_IDS` or an equivalent file-local selector on the existing fixture-backed literal-flag path;
  - preserve that case's current published pattern/helper shape (`"a.c"` through module `search(..., IGNORECASE)`) instead of renaming or widening it; and
  - `test_literal_flag_parity_suite_tracks_published_case_frontier()` no longer depends on an `expected_uncovered_case_ids` delegation escape hatch for the literal-flag bundle.
- `tests/python/test_module_workflow_parity_suite.py` becomes the sole owner for the remaining bounded-wildcard collection/workflow coverage:
  - absorb `module-findall-nonliteral-str` into `COLLECTION_TARGET_FIXTURE_CASE_IDS` or the existing collection owner surface without moving it to another suite or helper;
  - keep the bounded-wildcard direct coverage currently expressed by `COMPILE_CASES`, `PATTERN_MATCH_CASES`, `PATTERN_COLLECTION_CASES`, `test_rebar_bounded_wildcard_direct_workflow_matches_cpython()`, `test_rebar_bounded_wildcard_unsupported_paths_keep_placeholder_messages()`, and `test_fake_native_boundary_handles_bounded_wildcard_wrappers()` on the module-workflow owner file, using equivalent file-local tables/assertions if names change; and
  - preserve the current bounded `a.c` behaviors those tests cover: default plus `IGNORECASE` compile parity, narrowed-window pattern `search`/`match`/`fullmatch` coverage, bounded pattern `findall`/`finditer` coverage, direct cache reuse for `rebar.compile("a.c")`, placeholder behavior for the unsupported `[ab]c` and flagged `findall()` paths, and the fake-native-boundary call trace for `search()` plus `findall()`.
- `tests/python/fixture_parity_support.py` no longer exports `LITERAL_FLAG_DELEGATED_CASE_IDS`:
  - do not replace it with another delegation constant, another wildcard-specific support helper, or another sibling owner file.
- `tests/python/test_bounded_wildcard_parity_suite.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed wildcard-specific suite behind; and
  - keep the end state on the existing literal-flag and module-workflow owners rather than replacing one detached suite with another.
- Keep scope structural only:
  - do not change correctness fixtures, benchmark workloads, reports, Rust code, `python/rebar/`, or the public behavior of the bounded-wildcard slice; and
  - do not broaden into new nonliteral regex families, benchmark-anchor cleanup, or another support-module extraction in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import fixture_parity_support as support
from tests.python import test_literal_flag_parity_suite as literal_flag
from tests.python import test_module_workflow_parity_suite as module_workflow

assert "flag-unsupported-nonliteral-ignorecase-search" in literal_flag.TARGET_FIXTURE_CASE_IDS
assert "module-findall-nonliteral-str" in module_workflow.COLLECTION_TARGET_FIXTURE_CASE_IDS
assert not hasattr(support, "LITERAL_FLAG_DELEGATED_CASE_IDS")
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_bounded_wildcard_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural. Do not change runtime behavior, fixture contents, benchmark coverage, tracked reports, or any Rust/native implementation code.
- Prefer the two existing owner suites and their file-local tables over another helper module, another delegated selector, or another wildcard-specific suite split.
- Preserve the current case ids, placeholder messages, and fake-boundary call sequence; the point is to delete the detached owner file, not to reinterpret the bounded-wildcard slice.

## Notes
- `RBR-0640` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0640|RBR-0641|RBR-0642|RBR-0643|RBR-0644|RBR-0645" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returns no reserved or active task in that range.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task before this ticket is the feature-owned `RBR-0639`, with both task workers finishing `done` in the latest dashboard cycle.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_bounded_wildcard_parity_suite.py` is `386` lines, while the adjacent owners are already `588` lines in `tests/python/test_literal_flag_parity_suite.py` and `2927` lines in `tests/python/test_module_workflow_parity_suite.py`;
  - `rg -n "LITERAL_FLAG_DELEGATED_CASE_IDS|flag-unsupported-nonliteral-ignorecase-search|module-findall-nonliteral-str" tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/fixture_parity_support.py` shows the delegation constant exists only to keep the single literal-flag nonliteral row on the detached bounded-wildcard suite, while `module-findall-nonliteral-str` still lives only there instead of the module-workflow collection owner; and
  - a live probe from the current checkout shows `test_literal_flag_parity_suite.py` still selects only the twelve literal-flag rows while `test_module_workflow_parity_suite.py` still omits `module-findall-nonliteral-str` from `COLLECTION_TARGET_FIXTURE_CASE_IDS`.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py tests/python/test_module_workflow_parity_suite.py` passes (`512 passed in 0.40s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` passes (`162 passed in 0.20s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above currently fails exactly on this cleanup because the literal-flag suite still excludes `flag-unsupported-nonliteral-ignorecase-search`, the module-workflow suite still excludes `module-findall-nonliteral-str`, and `tests/python/fixture_parity_support.py` still exports `LITERAL_FLAG_DELEGATED_CASE_IDS`; and
  - `bash -lc "! rg --files tests/python | rg 'test_bounded_wildcard_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite file still exists.
