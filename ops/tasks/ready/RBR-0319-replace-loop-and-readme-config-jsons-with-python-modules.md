# RBR-0319: Replace the loop and README reporting config JSONs with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Remove the last two ops-owned tracked JSON blobs by replacing `ops/config/loop.json` and `ops/reporting/readme.json` with ordinary data-only Python modules, so the harness no longer keeps a bespoke JSON config path for repo-owned operator settings.

## Deliverables
- `scripts/rebar_ops.py`
- `tests/python/test_ops_harness.py`
- `ops/state/decision_log.md`
- `ops/config/loop.py`
- `ops/reporting/readme.py`
- Delete `ops/config/loop.json`
- Delete `ops/reporting/readme.json`

## Acceptance Criteria
- `ops/config/loop.py` and `ops/reporting/readme.py` each expose one top-level dict constant for their configuration data, preserving the current runtime, task-recovery, git-policy, reporting, agent-directory, Codex-default, capability-track, scorecard, status-section, and README-limit values from the deleted JSON files.
- `scripts/rebar_ops.py` loads both tracked config files through the existing importlib-based Python-module path instead of `json.loads`, updates `CONFIG_PATH` and the default README reporting config path to the new `.py` files, and keeps the same fallback/default behavior now expressed against Python dicts.
- The loop config still points its README-reporting config path at `ops/reporting/readme.py`, and README rendering, queue/report paths, runtime paths, and agent loading behavior remain unchanged apart from the storage-format migration.
- `tests/python/test_ops_harness.py` is updated so the existing harness coverage passes against the `.py` config paths and adds at least one direct assertion that the loaded loop config and README reporting config come from Python-module files rather than the deleted JSON files.
- `ops/state/decision_log.md` no longer instructs operators to tune the loop through `ops/config/loop.json`; any directly coupled durable operator reference updated in this run points at the new `.py` path.
- The live tracked JSON count decreases by exactly `2`: both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` currently agree at `6` and should finish at `4`, leaving only `reports/benchmarks/latest.json`, `reports/benchmarks/native_full.json`, `reports/benchmarks/native_smoke.json`, and `reports/correctness/latest.json`.

## Constraints
- Keep the scope to the two ops-owned config files plus the directly coupled harness, test, and doc updates listed above; do not change runtime JSON artifacts or the published report JSON scorecards in this run.
- Do not change any loop cadence, timeout, push policy, reporting limit, scorecard path, README section mapping, or capability-track semantics beyond the storage-format migration.
- Prefer simple data-only Python modules and the shared dict-loader path already present in `scripts/rebar_ops.py`; do not introduce another config parser, metaclass layer, or generator.

## Notes
- Live counts are the source of truth for this run: `git status --short` is clean and both JSON-count commands agree at `6`, even though `.rebar/runtime/dashboard.md` still carries a stale dirty-worktree sample from an earlier point in the cycle.
- `RBR-0317` already introduced `load_python_dict_attribute()` for the agent registry. Reusing that same plain-Python loading pattern here keeps ops config aligned with the rest of the harness instead of preserving one more JSON-specific path.
- Landing this task removes every tracked JSON file under `ops/`, leaving only the four published report artifacts for the next JSON burn-down step.
