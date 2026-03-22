# RBR-0910: Publish the module-workflow `Pattern.sub()` / `Pattern.subn()` duplicate-`count=` keyword pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier immediately after `RBR-0908` by publishing the exact direct `Pattern.sub()` / `Pattern.subn()` duplicate-`count=` keyword rejection pair on the shared bound-pattern error owner path, while leaving the Python-path benchmark frontier unchanged in this run because the runtime parity prerequisite still drains first.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", 1, count=1)`
- `re.compile(b"abc").subn(b"x", b"abc", 1, count=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing direct bound-pattern error owner path instead of creating another fixture file, another parity suite, or a detached keyword-error table:
  - assume `RBR-0908` has already widened the shared `PatternHelperErrorCase` / `_invoke_bound_pattern_helper()` route to carry keyword arguments; if that prerequisite is still missing, stop and finish `RBR-0908` first instead of re-implementing the same parity work here;
  - extend the shared direct bound-pattern error cases by exactly two published direct cases:
    - `pattern-sub-duplicate-count-keyword-str`
    - `pattern-subn-duplicate-count-keyword-bytes`
  - pin those direct cases to the exact `Pattern.sub()` / `Pattern.subn()` duplicate-`count=` calls above, with `helper == "sub"` / `"subn"`, `pattern == "abc"` / `b"abc"`, `args == ("x", "abc", 1)` / `(b"x", b"abc", 1)`, and `kwargs == {"count": 1}`;
  - add a focused published direct bound-pattern keyword-error fixture assertion path that maps exactly two published rows:
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
  - keep the existing direct bound-pattern keyword-helper subset unchanged at `27` rows, keep the published direct bound-pattern positional `__index__` subset unchanged at `9` rows, and keep the already-published wrong-text-model bound-pattern error cases on the same owner path unchanged in this run;
  - update the full `module-workflow-surface` bundle expectations from `154` rows to `156`, with the text-model split moving from `88` `str` / `66` `bytes` to `89` / `67`;
  - keep `module_call` expectations unchanged at `85` rows;
  - move `pattern_call` expectations from `57` rows to `59`; and
  - move the published `pattern_call` helper breakdown from `sub: 5` / `subn: 5` to `sub: 6` / `subn: 6` without widening into direct bound-pattern unexpected-keyword or `split()` duplicate-`maxsplit=` publication in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-sub-duplicate-count-keyword-str`;
  - add `workflow-pattern-subn-duplicate-count-keyword-bytes`;
  - keep both rows on the existing direct bound-pattern owner path with no module-level wrapper call, `kwargs == {"count": 1}`, and the exact direct argument payloads above;
  - insert `workflow-pattern-sub-duplicate-count-keyword-str` immediately after `workflow-pattern-sub-count-bool-true-bytes` and immediately before `workflow-pattern-subn-count-keyword-str`;
  - insert `workflow-pattern-subn-duplicate-count-keyword-bytes` immediately after `workflow-pattern-subn-count-bool-true-str` and immediately before `workflow-pattern-search-str-pos-indexlike-positional`;
  - categorize the new rows under `["workflow", ..., "duplicate-keyword"]` with `count` and the correct `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the direct bound-pattern duplicate-`count=` rejection spellings adjacent to the already published direct replacement keyword rows, not a broader direct bound-pattern keyword-error dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1528` total / `1528` passed / `0` unimplemented across `114` manifests to `1530` / `1530` / `0` across the same `114` manifests;
  - `module.workflow` moves from `154` / `154` / `0` to `156` / `156` / `0`;
  - `module.workflow.str` moves from `88` / `88` / `0` to `89` / `89` / `0`;
  - `module.workflow.bytes` moves from `66` / `66` / `0` to `67` / `67` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`;
  - `module.workflow.pattern_call` moves from `57` / `57` / `0` to `59` / `59` / `0`; and
  - the two new direct bound-pattern duplicate-`count=` rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0910-module-workflow-pattern-sub-subn-duplicate-count-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct bound-pattern keyword-error publication file.
- Keep the scope pinned to the duplicate-`count=` pair above. Leave direct bound-pattern unexpected-keyword publication and direct `Pattern.split()` duplicate-`maxsplit=` publication for follow-on tasks.
- Assume `RBR-0908` has already landed the matching runtime parity. If it has not, stop and finish `RBR-0908` first instead of widening this task.

## Notes
- `RBR-0910` is the next available feature task id in the current checkout:
  - `RBR-0908` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0909` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0908` on the same shared direct bound-pattern replacement frontier so the exact duplicate-`count=` diagnostics reach the tracked correctness surface before Python-path benchmark catch-up or adjacent direct bound-pattern unexpected-keyword / `split()` duplicate-`maxsplit=` follow-ons widen the error slice.
- 2026-03-22 feature-planning probes confirm this follow-on is the right post-parity publication slice:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").sub("x", "abc", 1, count=1) ... rebar.compile("abc").sub("x", "abc", 1, count=1) ... re.compile(b"abc").subn(b"x", b"abc", 1, count=1) ... rebar.compile(b"abc").subn(b"x", b"abc", 1, count=1) ... PY` still shows the exact parity gap that `RBR-0908` fixes first in this run: CPython raises `("sub() takes at most 3 arguments (4 given)",)` / `("subn() takes at most 3 arguments (4 given)",)`, while `rebar` still raises `("Pattern.sub() got multiple values for argument 'count'",)` / `("Pattern.subn() got multiple values for argument 'count'",)`;
  - `rg 'workflow-pattern-sub-duplicate-count-keyword-str|workflow-pattern-subn-duplicate-count-keyword-bytes' tests/conformance/fixtures/module_workflow_surface.py tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py tests/python/test_module_workflow_parity_suite.py` returned no matches in this run, so the exact direct bound-pattern publication rows are still absent;
  - `reports/correctness/latest.py` currently reports `1528` total / `1528` passed / `0` unimplemented across `114` manifests, with `module.workflow` still at `154` / `154` / `0`; and
  - `tests/python/test_module_workflow_parity_suite.py` currently keeps the direct bound-pattern keyword-helper publication slice at `27` rows while the shared bound-pattern error owner path still covers only the wrong-text-model cases, so the next bounded publication step is the duplicate-`count=` error pair rather than another helper family.

## Completion
- Added exactly two `pattern_call` publication rows to `tests/conformance/fixtures/module_workflow_surface.py`: `workflow-pattern-sub-duplicate-count-keyword-str` and `workflow-pattern-subn-duplicate-count-keyword-bytes`, in the required positions beside the existing bound replacement keyword rows.
- Extended `tests/python/test_module_workflow_parity_suite.py` with a focused `_published_pattern_keyword_error_fixture_cases()` selector and a direct bound-pattern keyword-error publication assertion that maps only the two landed duplicate-`count=` rows back to `pattern-sub-duplicate-count-keyword-str` and `pattern-subn-duplicate-count-keyword-bytes`, while keeping the existing 27-row helper slice and 9-row positional `__index__` slice unchanged.
- Updated the module-workflow bundle expectations in `tests/python/test_module_workflow_parity_suite.py` to `156` total rows, `89` `str`, `67` `bytes`, `59` `pattern_call`, and `sub: 6` / `subn: 6`, without widening into unexpected-keyword or `split()` duplicate-`maxsplit=` publication.
- Refreshed `tests/conformance/test_combined_correctness_scorecards.py` representative coverage and republished `reports/correctness/latest.py`; the tracked report on disk now shows `1530` total / `1530` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `156`, `module.workflow.str` at `89`, `module.workflow.bytes` at `67`, `module.workflow.module_call` unchanged at `85`, and `module.workflow.pattern_call` at `59`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0910-module-workflow-pattern-sub-subn-duplicate-count-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
