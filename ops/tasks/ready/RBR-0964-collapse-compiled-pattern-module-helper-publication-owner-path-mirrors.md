# RBR-0964: Collapse compiled-pattern module-helper publication owner-path mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining mirrored compiled-pattern module-helper publication inventories from `tests/python/test_module_workflow_parity_suite.py` so one file-local owner-path surface owns the same 62-row fixture-to-direct mapping instead of retyping it across the selector helper and the publication assertion test.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer repeats the same six direct-case family bundle in two places:
  - `_published_compiled_pattern_module_helper_fixture_cases()` and
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`
  must stop carrying separate `(*COMPILED_PATTERN_COMPILE_CASES, *COMPILED_PATTERN_MODULE_HELPER_CASES, *COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES, *COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES, *COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES, *BOUNDED_WILDCARD_MODULE_MATCH_CASES)` expressions.
- The publication assertion test no longer hard-codes four independent mirrored case-id inventories for the same owner path:
  - the `str` fixture case-id tuple,
  - the `bytes` fixture case-id tuple,
  - the full published fixture case-id tuple, and
  - the full selected direct case-id tuple.
- Replace those mirrors with one file-local canonical owner-path surface or equivalent helper that stays explicit but smaller than the current duplication:
  - keep it local to `tests/python/test_module_workflow_parity_suite.py`;
  - it may be a tiny frozen dataclass tuple, a tuple of `(fixture_case_id, direct_case_id, text_model)` rows, or an equivalent file-local representation;
  - derive the text-model subsets and full-order assertions from that one canonical surface instead of retyping the same workflow ids multiple times; and
  - do not add a shared helper module, another selector registry, or a checked-in data layer.
- Preserve the current live compiled-pattern module-helper publication contract exactly:
  - `_published_compiled_pattern_module_helper_fixture_cases()` still resolves to `62` published fixture rows;
  - the published text-model split stays `Counter({"str": 33, "bytes": 29})`;
  - the published helper split stays `Counter({"compile": 20, "sub": 10, "subn": 10, "split": 7, "search": 4, "fullmatch": 4, "match": 3, "findall": 2, "finditer": 2})`;
  - the first five `str` fixture ids stay:
    - `workflow-module-compile-str-compiled-pattern`
    - `workflow-module-compile-flags-noflag-str-compiled-pattern`
    - `workflow-module-compile-flags-int-zero-str-compiled-pattern`
    - `workflow-module-compile-flags-bool-false-str-compiled-pattern`
    - `workflow-module-compile-flags-ignorecase-str-compiled-pattern`
  - the last five `bytes` fixture ids stay:
    - `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`
    - `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-bytes-compiled-pattern-on-str-string`
  - the published fixture order and the selected direct-case order still stay aligned through the same signature matching that covers:
    - `COMPILED_PATTERN_COMPILE_CASES`
    - `COMPILED_PATTERN_MODULE_HELPER_CASES`
    - `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES`
    - `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES`
    - `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES`
    - `BOUNDED_WILDCARD_MODULE_MATCH_CASES`
  - `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()` stays green without widening this cleanup into the adjacent keyword-frontier publication logic.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter

from tests.python.test_module_workflow_parity_suite import (
    _fixture_cases_for_text_model,
    _published_compiled_pattern_module_helper_fixture_cases,
)

published = _published_compiled_pattern_module_helper_fixture_cases()

assert len(published) == 62
assert Counter(case.text_model for case in published) == Counter(
    {"str": 33, "bytes": 29}
)
assert Counter(case.helper for case in published) == Counter(
    {
        "compile": 20,
        "sub": 10,
        "subn": 10,
        "split": 7,
        "search": 4,
        "fullmatch": 4,
        "match": 3,
        "findall": 2,
        "finditer": 2,
    }
)
assert tuple(
    case.case_id for case in _fixture_cases_for_text_model(published, "str")[:5]
) == (
    "workflow-module-compile-str-compiled-pattern",
    "workflow-module-compile-flags-noflag-str-compiled-pattern",
    "workflow-module-compile-flags-int-zero-str-compiled-pattern",
    "workflow-module-compile-flags-bool-false-str-compiled-pattern",
    "workflow-module-compile-flags-ignorecase-str-compiled-pattern",
)
assert tuple(
    case.case_id for case in _fixture_cases_for_text_model(published, "bytes")[-5:]
) == (
    "workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern",
    "workflow-module-subn-unexpected-keyword-bytes-compiled-pattern",
    "workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern",
    "workflow-module-subn-count-alias-keyword-bytes-compiled-pattern",
    "workflow-module-subn-bytes-compiled-pattern-on-str-string",
)

print("ok", len(published))
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from pathlib import Path

text = Path("tests/python/test_module_workflow_parity_suite.py").read_text()

assert text.count("*COMPILED_PATTERN_COMPILE_CASES,") == 1
assert text.count('"workflow-module-compile-str-compiled-pattern",') == 1
assert text.count('"workflow-module-subn-bytes-compiled-pattern-on-str-string",') == 1

print("ok")
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/python/test_module_workflow_parity_suite.py`.
- Do not edit fixture manifests, benchmark manifests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.
- Prefer deleting duplicated owner-path mirrors over introducing another detached lookup table, registry, or helper module.

## Notes
- `RBR-0964` is the next available task id in the current checkout:
  - `rg -n 'RBR-0964|RBR-0965|RBR-0966|RBR-0967|RBR-0968' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0963-publish-pattern-window-wrong-text-model-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'` currently passes (`2 passed, 1423 deselected`);
  - the publication-surface probe in Verification currently passes (`ok 62`), proving the live owner path already resolves to the expected 62-row surface with the current helper/text-model counts; and
  - the structural probe in Verification currently fails only because `tests/python/test_module_workflow_parity_suite.py` still carries two `*COMPILED_PATTERN_COMPILE_CASES,` bundle occurrences plus duplicate fixture-id mirror literals for the compiled-pattern module-helper publication path.
