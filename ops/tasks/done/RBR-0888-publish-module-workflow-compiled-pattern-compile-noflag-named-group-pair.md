# RBR-0888: Publish the module-workflow compiled-pattern compile explicit-NOFLAG named-group pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile keyword neighbor, publishing the exact explicit `flags=re.NOFLAG` named-group `rebar.compile(compiled_pattern, ...)` pair for the existing `r"(?P<word>abc)"` anchor while keeping the Python-path benchmark frontier unchanged because the shared benchmark keyword path already normalizes this carrier onto the measured integer-zero route.

## Pattern Pair
- `re.compile("(?P<word>abc)")` through `compile(re.compile("(?P<word>abc)"), flags=re.NOFLAG)`
- `re.compile(b"(?P<word>abc)")` through `compile(re.compile(b"(?P<word>abc)"), flags=re.NOFLAG)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or benchmark-side churn:
  - teach the shared module-workflow publication helpers to preserve the explicit `RegexFlag` zero carrier on this owner path instead of collapsing `re.NOFLAG` onto the existing raw integer-zero signature;
  - extend the published compiled-pattern module-helper expectations by exactly two rows:
    - `workflow-module-compile-flags-noflag-str-compiled-pattern-named-group`
    - `workflow-module-compile-flags-noflag-bytes-compiled-pattern-named-group`
  - insert those rows immediately after the existing default named-group compiled-pattern compile rows and immediately before the explicit integer-zero neighbors for the same `str` and `bytes` anchors;
  - keep the already published default, explicit integer-zero, explicit bool-false, and explicit `IGNORECASE` compiled-pattern compile rows unchanged in this run;
  - update the shared published compiled-pattern owner-path counts from `52` rows to `54`, with the text-model split moving from `28` `str` / `24` `bytes` to `29` / `25`;
  - update the shared `module-workflow-surface` bundle expectations from `142` total rows to `144`, with the text-model split moving from `83` `str` / `59` `bytes` to `84` / `60`;
  - keep `pattern_call` expectations unchanged at `53` rows;
  - keep `compile` expectations unchanged at `9` rows; and
  - move the shared `module_call` total from `77` rows to `79`.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `module_call` rows:
  - add `workflow-module-compile-flags-noflag-str-compiled-pattern-named-group`;
  - add `workflow-module-compile-flags-noflag-bytes-compiled-pattern-named-group`;
  - keep both rows pinned to the exact existing named-group compiled-pattern compile anchors: `pattern == "(?P<word>abc)"`, `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and explicit `kwargs` that preserve the `NOFLAG` carrier instead of reusing the current raw integer-zero payload; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level named-group explicit `NOFLAG` spelling slice, not the default, raw integer-zero, bool-false, or nonzero-flag rejection slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1516` total / `1516` passed / `0` `unimplemented` across `114` manifests to `1518` / `1518` / `0` across the same `114` manifests;
  - `module.workflow` moves from `142` / `142` / `0` to `144` / `144` / `0`;
  - `module.workflow.str` moves from `83` / `83` / `0` to `84` / `84` / `0`;
  - `module.workflow.bytes` moves from `59` / `59` / `0` to `60` / `60` / `0`;
  - `module.workflow.module_call` moves from `77` / `77` / `0` to `79` / `79` / `0`;
  - `module.workflow.pattern_call` stays `53` / `53` / `0`; and
  - the new explicit-`NOFLAG` named-group compiled-pattern compile rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and named and noflag'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0888-module-workflow-compiled-pattern-compile-noflag-named-group-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.
- Keep the Python-path benchmark frontier unchanged here. The shared `module_boundary.py` benchmark keyword carrier already measures the normalized integer-zero path, so this run should not mint a duplicate `NOFLAG` benchmark row.

## Notes
- `RBR-0888` is the next available feature task id in the current checkout:
  - `RBR-0886` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0887` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0886` on the same `module-workflow-surface` owner path so the first explicit `NOFLAG` compiled-pattern named-group compile spelling publishes on the shared correctness surface once the adjacent benchmark-only `IGNORECASE` named-group catch-up drains.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier, but the publication path still needs the bounded selector/signature refinement:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and named and noflag'` passed in this run (`4 passed, 1210 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the exact named-group `NOFLAG` pair;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/feature-planning-module-workflow-probe.py` reported `142` executed / `142` passed in this run, confirming the shared owner path is otherwise stable before widening this slice;
  - direct publication probes in this run confirmed `workflow-module-compile-flags-noflag-str-compiled-pattern-named-group` and `workflow-module-compile-flags-noflag-bytes-compiled-pattern-named-group` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current `_workflow_keyword_kwargs_signature(...)` helper in `tests/python/test_module_workflow_parity_suite.py` still normalizes `RegexFlag(0)` through the generic integer branch, so this task must first preserve the explicit `NOFLAG` carrier on the shared publication path instead of pretending the new rows are already distinguishable from the existing integer-zero pair; and
  - no distinct benchmark follow-on currently survives for this exact spelling because the shared benchmark keyword route already normalizes zero-valued `flags=` carriers onto the published integer-zero workloads.

## Completion
- Landed the shared owner-path refinement in `tests/python/test_module_workflow_parity_suite.py`, teaching `_workflow_keyword_kwargs_signature(...)` to preserve the explicit zero-valued `RegexFlag` carrier and adding the matching direct named-group `compiled-pattern` `flags=re.NOFLAG` compile cases for both `str` and `bytes`.
- Added exactly two `module_call` rows to `tests/conformance/fixtures/module_workflow_surface.py`: `workflow-module-compile-flags-noflag-str-compiled-pattern-named-group` and `workflow-module-compile-flags-noflag-bytes-compiled-pattern-named-group`, each pinned to the existing `(?P<word>abc)` compiled-pattern `compile()` anchor with explicit `kwargs={"flags": re.NOFLAG}`.
- Refreshed `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked report now shows `1518` total / `1518` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `144`, `module.workflow.str` at `84`, `module.workflow.bytes` at `60`, `module.workflow.module_call` at `79`, and `module.workflow.pattern_call` unchanged at `53`.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and named and noflag'` -> `4 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` -> `1262 passed, 1 skipped, 2182 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0888-module-workflow-compiled-pattern-compile-noflag-named-group-pair.py` -> `144` executed / `144` passed
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` -> republished the tracked combined scorecard at the `1518` / `1518` / `0` totals above
- Benchmark manifests and benchmark publications were left unchanged in this run, as required.
