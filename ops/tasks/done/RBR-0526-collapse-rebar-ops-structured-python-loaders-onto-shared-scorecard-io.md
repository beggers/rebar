# RBR-0526: Collapse `rebar_ops` structured Python loaders onto shared scorecard IO

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining duplicated Python-module and structured scorecard loading logic from `scripts/rebar_ops.py` so the ops harness reuses the shared loader path in `python/rebar_harness/scorecard_io.py` instead of carrying a second `importlib.util` implementation plus its own `.py`/`.json` suffix switch.

## Deliverables
- `scripts/rebar_ops.py`
- `tests/python/test_ops_harness.py`
- `tests/python/test_readme_reporting.py`
- `python/rebar_harness/scorecard_io.py`

## Acceptance Criteria
- `scripts/rebar_ops.py` stops owning its own structured Python-module and scorecard loading machinery:
  - `load_config()`, `load_optional_python_dict_attribute()`, `load_agent_specs()`, and `scorecard_from_config()` route through shared helper(s) from `python/rebar_harness/scorecard_io.py`;
  - `load_python_dict_attribute(...)` and `read_structured_dict(...)` may remain as public helpers only if they are thin adapters over that shared helper path and preserve the current return values plus default-on-error behavior for existing callers;
  - the module no longer imports `importlib.util`, calls `spec_from_file_location(...)`, `module_from_spec(...)`, or `exec_module(...)`, and no longer branches on `path.suffix == ".json"` / `path.suffix == ".py"` for scorecard loading; and
  - importing `scripts/rebar_ops.py` by filesystem path from a checkout without `PYTHONPATH=python` and then calling `load_config()`, `load_python_dict_attribute(...)`, `read_structured_dict(...)`, and `scorecard_from_config(...)` still works.
- `python/rebar_harness/scorecard_io.py` exposes the smallest shared helper surface `scripts/rebar_ops.py` needs:
  - reuse the existing `.py` / scratch `.json` scorecard loader path instead of rebuilding a second suffix switch in `scripts/rebar_ops.py`;
  - if a tiny wrapper is needed for non-scorecard Python dict modules, add it here rather than reintroducing importlib logic in `scripts/rebar_ops.py`; and
  - keep the current `REPORT` attribute expectation, published/legacy scorecard paths, and scratch `.json` behavior unchanged.
- `tests/python/test_ops_harness.py` and `tests/python/test_readme_reporting.py` still validate the ops/reporting surface after the consolidation and should only change where the shared loader path makes an old local-implementation assumption obsolete.
- Preserve current external behavior exactly:
  - do not change `ops/config/loop.py`, `ops/reporting/readme.py`, agent `SPEC` data, runtime JSON state readers/writers, README rendering, task/commit flow, or published scorecard payloads;
  - do not change correctness or benchmark harness behavior outside the shared loader consolidation; and
  - this task explicitly authorizes edits to `scripts/rebar_ops.py`, but not to `AGENTS.md`, `ops/agents/`, `ops/config/`, or `scripts/loop_forever.sh`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/python/test_ops_harness.py`
  - ```bash
    ./.venv/bin/python - <<'PY'
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path("scripts/rebar_ops.py")
    spec = importlib.util.spec_from_file_location("rebar_ops_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    config = module.load_config()
    assert config["reporting"]["readme_config_path"] == "ops/reporting/readme.py"
    assert (
        module.load_python_dict_attribute(
            module.CONFIG_PATH,
            attribute="CONFIG",
            label="ops config",
        )["reporting"]["readme_config_path"]
        == "ops/reporting/readme.py"
    )
    assert (
        module.read_structured_dict(
            module.REPO_ROOT / "reports" / "correctness" / "latest.py",
            default=None,
            label="scorecard",
        )["suite"]
        == "correctness"
    )
    assert (
        module.scorecard_from_config(
            config,
            "correctness_scorecard",
            "Correctness Scorecard",
            "reports/correctness/latest.py",
        )["available"]
        is True
    )
    assert (
        module.scorecard_from_config(
            config,
            "benchmark_scorecard",
            "Benchmark Snapshot",
            "reports/benchmarks/latest.py",
        )["available"]
        is True
    )
    print("ok")
    PY
    ```
  - `rg -n "import importlib\\.util|spec_from_file_location\\(|module_from_spec\\(|exec_module\\(|path\\.suffix == \\\"\\.json\\\"|path\\.suffix == \\\"\\.py\\\"" scripts/rebar_ops.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not broaden it into runtime-state JSON IO cleanup, README/report rendering changes, agent-registry changes, or queue/dispatch behavior.
- Prefer deleting the duplicate loader branches in `scripts/rebar_ops.py` over introducing another wrapper layer beside `python/rebar_harness/scorecard_io.py`.
- Preserve the existing `load_config()`, `load_optional_python_dict_attribute()`, `load_agent_specs()`, `load_python_dict_attribute(...)`, `read_structured_dict(...)`, and `scorecard_from_config(...)` call sites unless a minimal test-covered rename is clearly simpler.

## Notes
- `RBR-0525` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0526` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining duplicate loader surface is concrete and still live in the current checkout:
  - `scripts/rebar_ops.py` still imports `importlib.util`, owns its own `spec_from_file_location(...)` / `module_from_spec(...)` / `exec_module(...)` path, and still branches on `path.suffix == ".json"` / `".py"` in `read_structured_dict(...)`;
  - `python/rebar_harness/scorecard_io.py` already exposes shared `load_python_dict_attribute(...)` and `load_scorecard_report(...)` helpers that cover the same Python-module and scorecard-loading job; and
  - `tests/python/test_ops_harness.py` plus `tests/python/test_readme_reporting.py` still exercise the `rebar_ops` helper surface this cleanup should keep stable.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/python/test_ops_harness.py` passes (`26 passed, 17 subtests passed in 1.59s`).
  - The no-`PYTHONPATH` inline probe above currently prints `ok`.
- `rg -n "import importlib\\.util|spec_from_file_location\\(|module_from_spec\\(|exec_module\\(|path\\.suffix == \\\"\\.json\\\"|path\\.suffix == \\\"\\.py\\\"" scripts/rebar_ops.py` currently returns the six duplicate-loader matches this task is meant to delete.
- 2026-03-17: Routed `load_config()`, `load_optional_python_dict_attribute()`, `load_agent_specs()`, `read_structured_dict()`, and `scorecard_from_config()` through shared helpers in `python/rebar_harness/scorecard_io.py`, removed the local `importlib.util` / scorecard suffix-switch loader code from `scripts/rebar_ops.py`, and verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_readme_reporting.py tests/python/test_ops_harness.py`, the no-`PYTHONPATH` inline probe from this task, and `rg -n "import importlib\\.util|spec_from_file_location\\(|module_from_spec\\(|exec_module\\(|path\\.suffix == \\\"\\.json\\\"|path\\.suffix == \\\"\\.py\\\"" scripts/rebar_ops.py` (no matches).
