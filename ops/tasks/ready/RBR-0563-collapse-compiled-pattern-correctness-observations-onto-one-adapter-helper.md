# RBR-0563: Collapse compiled-pattern correctness observations onto one adapter helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the repeated compiled-pattern observation plumbing from `python/rebar_harness/correctness.py` so one `Adapter` helper owns the warnings/compile/finalize flow for compile, pattern-metadata, and pattern-call observations instead of `CpythonReAdapter` and `RebarAdapter` reimplementing the same three methods.

## Deliverables
- `python/rebar_harness/correctness.py`

## Acceptance Criteria
- `Adapter` grows one private helper named `_observe_compiled_pattern(...)` that owns the shared compiled-pattern observation flow:
  - accept the `FixtureCase` plus a callback that receives the compiled pattern object;
  - open the warning capture block and normalize warnings through `normalize_warning_records(...)`;
  - call `self._compile_pattern(case)` exactly once per observation;
  - run the callback only after a successful compile; and
  - finalize exception observations through a second helper named `_observation_outcome_for_exception(...)` so adapter-specific outcome mapping stays explicit.
- `Adapter` also grows a concrete `_observation_outcome_for_exception(...)` hook whose default outcome is `"exception"`.
- `Adapter.observe_compile(...)`, `Adapter.observe_pattern_metadata(...)`, and `Adapter.observe_pattern_call(...)` become concrete methods that delegate through `_observe_compiled_pattern(...)` instead of remaining placeholder stubs.
- `observe_compile(...)` still returns normalized pattern metadata via `normalize_pattern_metadata(...)`, `observe_pattern_metadata(...)` still returns normalized pattern-object metadata via `normalize_pattern_object_metadata(...)`, and `observe_pattern_call(...)` still returns `_normalize_value(...)` of the bound `Pattern` helper result.
- `observe_pattern_call(...)` still requires `case.helper` and still invokes the bound compiled-pattern helper with the existing `case.args` and `case.kwargs` payloads; preserve the current error surface when a helper name is missing.
- `CpythonReAdapter` and `RebarAdapter` stop overriding `observe_compile(...)`, `observe_pattern_metadata(...)`, and `observe_pattern_call(...)`; the only adapter-specific compiled-pattern behavior left in those subclasses is `_compile_pattern(...)` plus `RebarAdapter`'s `_observation_outcome_for_exception(...)` override that preserves `NotImplementedError -> "unimplemented"`.
- Preserve current behavior exactly:
  - `RebarAdapter` still reports `NotImplementedError` as `unimplemented` for these three observation paths and still reports other exceptions as `exception`;
  - `CpythonReAdapter` keeps treating all exceptions as `exception`;
  - do not refactor `observe_cache_workflow(...)`, `observe_purge_workflow(...)`, `observe_cache_distinct_workflow(...)`, or the module-attribute/module-call helpers in this run; and
  - do not change fixture manifests, scorecard schemas, published reports, README text, or tracked state files outside this task.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_observation_contract.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    path = Path("python/rebar_harness/correctness.py")
    module = ast.parse(path.read_text())
    classes = {
        node.name: node
        for node in module.body
        if isinstance(node, ast.ClassDef)
    }

    failures: list[str] = []
    adapter_methods = {
        node.name: node
        for node in classes["Adapter"].body
        if isinstance(node, ast.FunctionDef)
    }

    for name in (
        "_observe_compiled_pattern",
        "_observation_outcome_for_exception",
        "observe_compile",
        "observe_pattern_metadata",
        "observe_pattern_call",
    ):
        if name not in adapter_methods:
            failures.append(f"Adapter:missing:{name}")

    for name in ("observe_compile", "observe_pattern_metadata", "observe_pattern_call"):
        node = adapter_methods.get(name)
        if node is None:
            continue
        names = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
        attrs = {
            child.attr
            for child in ast.walk(node)
            if isinstance(child, ast.Attribute)
        }
        if "_observe_compiled_pattern" not in names and "_observe_compiled_pattern" not in attrs:
            failures.append(f"Adapter:{name}:missing-compiled-helper")

    for subclass_name in ("CpythonReAdapter", "RebarAdapter"):
        subclass_methods = {
            node.name
            for node in classes[subclass_name].body
            if isinstance(node, ast.FunctionDef)
        }
        for name in ("observe_compile", "observe_pattern_metadata", "observe_pattern_call"):
            if name in subclass_methods:
                failures.append(f"{subclass_name}:still-overrides:{name}")

    rebar_methods = {
        node.name
        for node in classes["RebarAdapter"].body
        if isinstance(node, ast.FunctionDef)
    }
    if "_observation_outcome_for_exception" not in rebar_methods:
        failures.append("RebarAdapter:missing-exception-outcome-hook")

    if failures:
        raise SystemExit("\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup local to `python/rebar_harness/correctness.py`. Do not add another harness support module, registry, or adapter subclass.
- Prefer moving the shared behavior into `Adapter` over adding a second layer of wrapper functions beside the existing class hierarchy.
- Leave cache and module-helper observation refactors for later work; this task is only about the duplicated compiled-pattern observation path.

## Notes
- `RBR-0561` is reserved in `ops/state/backlog.md` and already filed as the active feature task, and `RBR-0562` is already used by the most recent architecture cleanup, so `RBR-0563` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty before this task was added.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/dashboard.md` HEAD `fee132ab2295c8c9f0d9b8edadb67f4b0f9f966a` matches `git rev-parse HEAD`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate compiled-pattern observation plumbing is concrete in the current checkout:
  - `python/rebar_harness/correctness.py:833-901` and `python/rebar_harness/correctness.py:1010-1102` restate the same warning-capture, compile, callback, and finalize flow across `observe_compile(...)`, `observe_pattern_metadata(...)`, and `observe_pattern_call(...)`;
  - the only behavioral difference in those duplicated blocks is that `RebarAdapter` treats `NotImplementedError` as `unimplemented`, which is why this task keeps that distinction in an explicit adapter hook instead of hard-coding another branch in each method; and
  - the AST probe above currently fails exactly on the missing-helper cleanup with `Adapter:missing:_observe_compiled_pattern`, `Adapter:missing:_observation_outcome_for_exception`, the three `Adapter:*:missing-compiled-helper` failures, and the current subclass override failures for both adapters.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_observation_contract.py` passes (`9 passed, 1260 subtests passed in 28.67s`).
