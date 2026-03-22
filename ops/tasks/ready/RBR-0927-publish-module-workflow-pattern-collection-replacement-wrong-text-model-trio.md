# RBR-0927: Publish the module-workflow direct `Pattern` collection/replacement wrong-text-model trio

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the adjacent direct bound-`Pattern` collection/replacement wrong-text-model trio, so the shared owner path publishes the already-landed CPython-visible `TypeError` behavior for `split()` / `sub()` / `subn()` before Python-path benchmark catch-up or another bound-pattern helper family reopens the queue.

## Pattern Pair
- `re.compile("abc").split(b"zabczz")` / `re.compile("abc").sub("x", b"zabczz")`
- `re.compile(b"abc").subn(b"x", "zabczz")`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly three new `pattern_call` rows:
  - add `workflow-pattern-split-str-pattern-on-bytes-string`;
  - add `workflow-pattern-sub-str-pattern-on-bytes-string`; and
  - add `workflow-pattern-subn-bytes-pattern-on-str-string`.
- Keep those three rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUND_PATTERN_TYPE_ERROR_CASES`:
  - `pattern-split-str-pattern-on-bytes-string` keeps `helper == "split"`, `pattern == "abc"`, `args == [b"zabczz"]`, and the str pattern/bytes haystack mismatch on the direct bound helper path;
  - `pattern-sub-str-pattern-on-bytes-string` keeps `helper == "sub"`, `pattern == "abc"`, `args == ["x", b"zabczz"]`, and the str pattern/bytes haystack mismatch on the direct bound helper path; and
  - `pattern-subn-bytes-pattern-on-str-string` keeps `helper == "subn"`, `pattern == b"abc"`, `args == [b"x", "zabczz"]`, and the bytes pattern/str haystack mismatch on the direct bound helper path.
- Keep the manifest routing narrow and ordered on the existing direct bound-pattern collection/replacement owner path:
  - insert `workflow-pattern-split-str-pattern-on-bytes-string` immediately after `workflow-pattern-split-unexpected-keyword-bytes`;
  - insert `workflow-pattern-sub-str-pattern-on-bytes-string` immediately after `workflow-pattern-sub-unexpected-keyword-str`;
  - insert `workflow-pattern-subn-bytes-pattern-on-str-string` immediately after `workflow-pattern-subn-unexpected-keyword-bytes`;
  - categorize the new rows under `["workflow", ..., "literal", ..., "wrong-text-model"]` with the correct `split` / `sub` / `subn` helper tags and `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the direct bound `Pattern` wrong-text-model rejection spellings adjacent to the already-published keyword-carrying and keyword-error rows, not a broader helper dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path instead of creating another manifest, another parity suite, or a detached wrong-text-model table:
  - add a focused published direct bound-pattern wrong-text-model assertion path that maps exactly the three new fixture rows back to `pattern-split-str-pattern-on-bytes-string`, `pattern-sub-str-pattern-on-bytes-string`, and `pattern-subn-bytes-pattern-on-str-string`;
  - update the `module-workflow-surface` bundle expectations from `160` rows to `163`, with the text-model split moving from `91` `str` / `69` `bytes` to `93` / `70`;
  - keep `module_call` expectations unchanged at `85` rows;
  - move `pattern_call` expectations from `63` rows to `66`; and
  - keep the already-published direct bound-pattern keyword-error slice unchanged at six rows instead of folding these wrong-text-model rows into that keyword-only selector.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1534` total / `1534` passed / `0` unimplemented across `114` manifests to `1537` / `1537` / `0` across the same `114` manifests;
  - `module.workflow` moves from `160` / `160` / `0` to `163` / `163` / `0`;
  - `module.workflow.str` moves from `91` / `91` / `0` to `93` / `93` / `0`;
  - `module.workflow.bytes` moves from `69` / `69` / `0` to `70` / `70` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`; and
  - `module.workflow.pattern_call` moves from `63` / `63` / `0` to `66` / `66` / `0`, with the three new direct bound-pattern wrong-text-model rows visible in the tracked scorecard as representative `module-workflow-surface` exception cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string or module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0927-module-workflow-pattern-collection-replacement-wrong-text-model-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct bound-pattern wrong-text-model publication file.
- Keep the scope pinned to the three collection/replacement wrong-text-model rows above. Leave direct `Pattern` collection/replacement wrong-text-model benchmark catch-up for a later task.

## Notes
- `RBR-0927` is the next available feature task id in the current checkout:
  - `RBR-0925` is the latest done feature task on this frontier;
  - `RBR-0926` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0925` on the same shared direct bound-pattern collection/replacement owner path so the adjacent wrong-text-model exception slice reaches the tracked correctness surface before Python-path benchmark catch-up or another helper family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-pattern-on-bytes-string or pattern-sub-str-pattern-on-bytes-string or pattern-subn-bytes-pattern-on-str-string'` currently passes in this checkout (`6 passed, 1357 deselected`);
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(\"abc\").split(b\"zabczz\") ... rebar.compile(\"abc\").split(b\"zabczz\") ... re.compile(\"abc\").sub(\"x\", b\"zabczz\") ... rebar.compile(\"abc\").sub(\"x\", b\"zabczz\") ... re.compile(b\"abc\").subn(b\"x\", \"zabczz\") ... rebar.compile(b\"abc\").subn(b\"x\", \"zabczz\") ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `(\"cannot use a string pattern on a bytes-like object\",)` for the split/sub str-pattern rows and `(\"cannot use a bytes pattern on a string-like object\",)` for the `subn()` bytes-pattern row;
  - `rg -n 'workflow-pattern-split-str-pattern-on-bytes-string|workflow-pattern-sub-str-pattern-on-bytes-string|workflow-pattern-subn-bytes-pattern-on-str-string' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py` returned no matches in this run, so the exact direct bound-pattern publication rows are still absent; and
  - `reports/correctness/latest.py` currently reports `1534` total / `1534` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `160`, `module.workflow.str` at `91`, `module.workflow.bytes` at `69`, `module.workflow.module_call` at `85`, and `module.workflow.pattern_call` at `63`.
