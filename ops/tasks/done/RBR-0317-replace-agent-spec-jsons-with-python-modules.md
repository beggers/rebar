# RBR-0317: Replace the agent-spec JSON registry with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify harness startup by replacing the nine tracked agent spec JSON files under `ops/agents/` with ordinary Python `SPEC` modules, then deleting the JSON-only loader path that still treats agent metadata differently from the Python-backed correctness and benchmark manifests.

## Deliverables
- `scripts/rebar_ops.py`
- `tests/python/test_ops_harness.py`
- `AGENTS.md`
- `ops/README.md`
- `ops/agents/README.md`
- `ops/agents/supervisor.md`
- `ops/agents/architecture.py`
- `ops/agents/architecture_implementation.py`
- `ops/agents/cleanup.py`
- `ops/agents/feature_implementation.py`
- `ops/agents/feature_planning.py`
- `ops/agents/implementation_faithfulness.py`
- `ops/agents/qa_testing.py`
- `ops/agents/reporting.py`
- `ops/agents/supervisor.py`
- Delete `ops/agents/architecture.json`
- Delete `ops/agents/architecture_implementation.json`
- Delete `ops/agents/cleanup.json`
- Delete `ops/agents/feature_implementation.json`
- Delete `ops/agents/feature_planning.json`
- Delete `ops/agents/implementation_faithfulness.json`
- Delete `ops/agents/qa_testing.json`
- Delete `ops/agents/reporting.json`
- Delete `ops/agents/supervisor.json`

## Acceptance Criteria
- Each targeted agent spec becomes a one-agent-per-file Python module exposing a top-level `SPEC` dict with the same `name`, `kind`, `description`, `enabled`, `cycle_order`, `prompt_path`, `dispatch`, and `codex` values as the deleted JSON file, and no duplicate `.json` copy of those nine specs remains in the tree.
- `scripts/rebar_ops.py` loads agent specs only from Python modules in the configured `ops/agents` directory through one shared loader path that requires a dict `SPEC`; it no longer globs or parses `ops/agents/*.json`, and its operator-facing help text stops hard-coding the old `.json` path pattern.
- The loaded registry remains behaviorally identical to the current checkout: the enabled agent set, cycle ordering, single-enabled-supervisor constraint, task-owner routing, dirty-worktree allowances, timeout values, and `model_reasoning_effort="xhigh"` codex config all stay unchanged, with `AgentSpec.spec_path` now resolving to the new `.py` files.
- The harness-facing docs and prompts that currently tell humans or agents to edit `ops/agents/*.json` are updated to point at `ops/agents/*.py`; at minimum `AGENTS.md`, `ops/README.md`, `ops/agents/README.md`, and `ops/agents/supervisor.md` stay accurate after the migration.
- `tests/python/test_ops_harness.py` is updated so the existing harness coverage passes against the `.py`-backed registry without preserving JSON-specific assumptions about spec paths.
- The live tracked JSON count decreases by exactly `9` relative to the current clean-checkout baseline: both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` currently start at `15` and should finish at `6`, leaving only `ops/config/loop.json`, `ops/reporting/readme.json`, `reports/benchmarks/latest.json`, `reports/benchmarks/native_full.json`, `reports/benchmarks/native_smoke.json`, and `reports/correctness/latest.json`.

## Constraints
- Keep the scope to agent-registry storage plus the directly coupled harness, test, and doc updates listed above; do not convert `ops/config/loop.json`, `ops/reporting/readme.json`, runtime JSON, or published report JSON in the same run.
- Do not change the actual enabled agent set, role ordering, dispatch policy, timeout values, or prompt behavior beyond the storage-format migration.
- Prefer simple data-only Python `SPEC` modules and the same importlib-style loading pattern already used for correctness and benchmark manifests over introducing another parser, code generator, or metaconfiguration layer.

## Notes
- `.rebar/runtime/dashboard.md` is current for this clean checkout: it reports `tracked_json_blob_count: 15` and `tracked_json_blob_delta: -10`, and both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` agree at `15`.
- This is the largest remaining non-report JSON block in the repo: `9` of the `11` remaining non-report JSON files are the agent specs. Landing it leaves only loop/reporting config JSON plus the four published report artifacts for the next burn-down step.
- `scripts/rebar_ops.py` already treats correctness and benchmark manifests as Python modules, so agent specs should converge on that same plain-Python representation instead of keeping a bespoke JSON registry.

## Completion Notes
- Replaced the nine tracked `ops/agents/*.json` files with one-agent-per-file Python modules exposing top-level `SPEC` dicts, preserved each agent's existing names, kinds, descriptions, enabled flags, cycle ordering, prompt paths, dispatch settings, and Codex config, and deleted the JSON originals.
- Updated `scripts/rebar_ops.py` so `load_agent_specs()` now loads only `ops/agents/*.py` modules through a shared importlib-based `SPEC` loader, preserves the existing enabled-agent ordering and single-supervisor validation, and updates the `render` CLI help text to point at the `.py` registry.
- Updated `AGENTS.md`, `ops/README.md`, `ops/agents/README.md`, and `ops/agents/supervisor.md` to describe the Python-backed registry, and refreshed the durable harness-state references in `ops/state/current_status.md` and `ops/state/decision_log.md` so they no longer describe the live agent registry as JSON-backed.
- Updated `tests/python/test_ops_harness.py` to use `.py` spec paths in the direct `AgentSpec` fixtures and added explicit coverage that the loaded registry resolves agent `spec_path` values to existing Python modules.
- Verified with `./.venv/bin/python -m pytest tests/python/test_ops_harness.py` (`11` passed) and `./.venv/bin/python scripts/rebar_ops.py render supervisor`.
- Live JSON count is now `6` by `rg --files -g '*.json' | wc -l`, leaving only `ops/config/loop.json`, `ops/reporting/readme.json`, `reports/benchmarks/latest.json`, `reports/benchmarks/native_full.json`, `reports/benchmarks/native_smoke.json`, and `reports/correctness/latest.json`. `git ls-files '*.json' | wc -l` still reports `15` in this dirty checkout until the harness commit records the deletions.
