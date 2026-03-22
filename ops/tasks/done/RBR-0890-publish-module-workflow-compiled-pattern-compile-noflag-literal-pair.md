# RBR-0890: Publish the module-workflow compiled-pattern compile explicit-NOFLAG literal pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Keep the existing `module-workflow-surface` correctness frontier moving after `RBR-0888` by publishing the adjacent literal compiled-pattern `compile(..., flags=re.NOFLAG)` pair on the shared correctness surface, reusing the zero-carrier distinction that `RBR-0888` lands and leaving the Python-path benchmark frontier unchanged because the shared benchmark keyword path already normalizes this carrier onto the measured integer-zero route.

## Pattern Pair
- `re.compile("abc")` through `compile(re.compile("abc"), flags=re.NOFLAG)`
- `re.compile(b"abc")` through `compile(re.compile(b"abc"), flags=re.NOFLAG)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or benchmark-side churn:
  - assume `RBR-0888` has already taught the shared module-workflow publication helpers to preserve the explicit `RegexFlag` zero carrier instead of collapsing `re.NOFLAG` onto the raw integer-zero signature;
  - extend the published compiled-pattern module-helper expectations by exactly two rows:
    - `workflow-module-compile-flags-noflag-str-compiled-pattern`
    - `workflow-module-compile-flags-noflag-bytes-compiled-pattern`
  - insert those rows immediately after the existing default literal compiled-pattern compile rows and immediately before the explicit integer-zero neighbors for the same `str` and `bytes` anchors;
  - keep the already published named-group `NOFLAG` rows from `RBR-0888` unchanged in this run;
  - keep the already published explicit integer-zero, explicit bool-false, and explicit `IGNORECASE` compiled-pattern compile rows unchanged in this run;
  - update the shared published compiled-pattern owner-path counts from `54` rows to `56`, with the text-model split moving from `29` `str` / `25` `bytes` to `30` / `26`;
  - update the shared `module-workflow-surface` bundle expectations from `144` total rows to `146`, with the text-model split moving from `84` `str` / `60` `bytes` to `85` / `61`;
  - keep `pattern_call` expectations unchanged at `53` rows;
  - keep `compile` expectations unchanged at `9` rows; and
  - move the shared `module_call` total from `79` rows to `81`.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `module_call` rows:
  - add `workflow-module-compile-flags-noflag-str-compiled-pattern`;
  - add `workflow-module-compile-flags-noflag-bytes-compiled-pattern`;
  - keep both rows pinned to the exact existing literal compiled-pattern compile anchors: `pattern == "abc"`, `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and explicit `kwargs` that preserve the `NOFLAG` carrier instead of reusing the raw integer-zero payload; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level literal explicit `NOFLAG` spelling slice, not the default, raw integer-zero, bool-false, named-group, or nonzero-flag rejection slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1518` total / `1518` passed / `0` `unimplemented` across `114` manifests to `1520` / `1520` / `0` across the same `114` manifests;
  - `module.workflow` moves from `144` / `144` / `0` to `146` / `146` / `0`;
  - `module.workflow.str` moves from `84` / `84` / `0` to `85` / `85` / `0`;
  - `module.workflow.bytes` moves from `60` / `60` / `0` to `61` / `61` / `0`;
  - `module.workflow.module_call` moves from `79` / `79` / `0` to `81` / `81` / `0`;
  - `module.workflow.pattern_call` stays `53` / `53` / `0`; and
  - the new explicit-`NOFLAG` literal compiled-pattern compile rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and literal'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0890-module-workflow-compiled-pattern-compile-noflag-literal-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.
- Keep the Python-path benchmark frontier unchanged here. The shared `module_boundary.py` benchmark keyword carrier already measures the normalized integer-zero path, so this run should not mint a duplicate `NOFLAG` benchmark row.

## Notes
- `RBR-0890` is the next available feature task id in the current checkout:
  - `RBR-0888` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0889` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0888` on the same `module-workflow-surface` owner path so the literal compiled-pattern `NOFLAG` spelling catches up on the shared correctness surface once the named-group zero-carrier publication slice drains.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier, while the publication path still lacks the bounded literal pair:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and literal'` passed in this run (`16 passed, 1198 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the exact literal `NOFLAG` pair;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on `compile(rebar.compile("abc"), flags=rebar.NOFLAG)` and `compile(rebar.compile(b"abc"), flags=rebar.NOFLAG)`, preserving identity plus matching `pattern`, `flags`, and `groupindex`;
  - direct publication probes in this run confirmed `workflow-module-compile-flags-noflag-str-compiled-pattern` and `workflow-module-compile-flags-noflag-bytes-compiled-pattern` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` still publish no distinct `NOFLAG` literal benchmark rows, which is intentional because the benchmark keyword path already normalizes zero-valued `flags=` carriers onto the measured integer-zero route; and
  - if `RBR-0888` has not landed yet, stop and finish that prerequisite first so this follow-on can reuse the shared `RegexFlag(0)` signature distinction instead of reintroducing it here.

## Completion Note
- Added the two missing published module-workflow fixture rows for literal compiled-pattern `compile(..., flags=re.NOFLAG)` on the `str` and `bytes` paths, keeping their order directly after the default literal compiled-pattern rows and before the explicit integer-zero neighbors.
- Updated the shared module-workflow parity expectations and combined scorecard manifest expectations to include those rows and the new `146`/`85`/`61`/`81` owner-path counts.
- Regenerated `reports/correctness/latest.py`; the tracked publication now reports `1520` total cases, `1520` passed, `0` unimplemented, `114` manifests, and includes both new module-workflow case ids.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython and literal'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0890-module-workflow-compiled-pattern-compile-noflag-literal-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
- Benchmark manifests and `reports/benchmarks/latest.py` were intentionally left unchanged in this task.
