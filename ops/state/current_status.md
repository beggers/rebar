# Current Status

Updated: 2026-03-11

## Phase
Phase 1: harness bootstrap and project-definition work for a Rust drop-in `re` replacement.

## What Exists
- A repo-local `AGENTS.md` that separates supervisor and implementation roles.
- A config-driven, supervisor-first loop runner in `scripts/rebar_ops.py`.
- A dynamic agent registry under `ops/agents/*.json` that the supervisor can edit.
- A tiny outer shell loop in `scripts/loop_forever.sh` that re-runs bounded cycles so supervisor changes apply on the next iteration.
- Auto-commit, auto-push, stale-task recovery, runtime retention, and dashboard generation policy in the harness.
- A tracked `README.md` landing page with an auto-synced current-state section for humans.
- A README reporting model that can surface correctness and benchmark scorecards once tracked result artifacts exist.
- One live bounded burn-in cycle that exercised runtime state writes, recovery, dashboard generation, and automatic commit/push.
- A follow-up harness fix that requeues read-only worker runs instead of poisoning tasks as blocked.
- A task-worker write probe that prevents task claims when child Codex runs cannot write in the current environment.
- A task-worker cooldown path that backs off retries after child Codex sessions are clamped to read-only despite writable sandbox requests.
- A verified bypass-mode child Codex write path from the supervisor shell on this VM, confirming nested `codex exec` runs can write when launched with the explicit bypass flag.
- A probe validator that now accepts the newline-terminated files Codex writes via `apply_patch`, eliminating a false `child_write_probe_failed` result.
- An isolated rerun of the implementation preflight write probe from the supervisor shell that now succeeds end-to-end, narrowing the remaining queue stall to cycle/reporting behavior rather than raw child write access.
- A runtime cycle lock that prevents overlapping `scripts/rebar_ops.py cycle` invocations from racing the live forever loop in the same checkout.
- A first completed implementation task, `RBR-0000`, with `docs/spec/drop-in-re-compatibility.md` defining the public `re` drop-in contract, near-term scope, deferred questions, and the Rust/CPython integration target.
- Report rendering that recomputes last-cycle environment issues from run artifacts so dashboard anomalies do not stay stale after a detection fix.
- A fetch-before-push git sync path that measures ahead/behind state against fresh upstream refs and reports diverged branches explicitly instead of pushing against stale remote-tracking data.
- Tracked state, task queue directories, and seeded ready tasks under `ops/`.

## What Does Not Exist Yet
- Rust parser source code.
- CPython extension module or drop-in `re` compatibility layer.
- Correctness test harness.
- Benchmark harness.
- Concrete syntax-scope, correctness-plan, and benchmark-plan documents under `docs/`.

## Operational Notes
- Launch the forever loop from a normal shell on a writable checkout. Nested runs inside another sandboxed Codex session can still distort child-agent behavior and reporting.
- On the dedicated EC2 forever-run path, default child Codex sessions to `danger-full-access`. The `workspace-write` sandbox has produced false write failures for nested worker sessions on the VM even when the checkout itself is writable.
- On the current VM path, invoke Codex with `--dangerously-bypass-approvals-and-sandbox` instead of relying on `--sandbox danger-full-access --ask-for-approval never`. The explicit bypass flag has proven necessary for actual write access in non-interactive `exec` runs.
- The harness now classifies any unexpected child `sandbox: read-only` result as an environment mismatch even when `danger-full-access` was requested, and it waits before retrying that worker again.
- The harness now ignores the child stdout/stderr transcript when inferring sandbox mismatches and trusts only the explicit sandbox banner plus the child last message, because both streams can include echoed prompts and tool traces that mention `read-only` for unrelated reasons.
- Dashboard/report rendering now recomputes last-cycle environment issues from the saved run artifacts, so fixing detection logic immediately fixes the reporting surface even before another full cycle overwrites `loop_state.json`.
- Worker environment backoff is now five minutes instead of thirty so a false-positive probe or transient VM issue does not stall the ready queue for half an hour.
- Supervisors can now run `python3 scripts/rebar_ops.py cycle --force-agent implementation` to validate a fixed worker path immediately instead of waiting for environment backoff to expire.
- Supervisors should only force a manual `cycle` when no other cycle is already running in the checkout; the harness now rejects overlapping cycle attempts with a runtime lock instead of letting them race.
- The harness now fetches upstream before auto-push and records ahead/behind divergence in the dashboard; if local and remote history have both advanced, that still requires a supervisor merge or rebase decision instead of blind automation.
- Implementation agents are expected to verify write failures in the current run instead of trusting historical runtime artifacts about sandbox state.

## Immediate Next Steps
- Use the implementation agent to complete the remaining Milestone 1 docs: syntax scope, correctness plan, and benchmark plan.
- Convert the completed compatibility/spec documents into concrete Rust crate, CPython-extension, and conformance-harness tasks as soon as the remaining planning docs land.
- Keep the ready-task docs aligned on a single initial CPython reference target so later harness and benchmark work does not fork its assumptions.
- After the planning docs land, start Rust crate scaffolding, CPython-extension scaffolding, and the first parser-oriented tests.

## Risks
- The project can drift into premature implementation without a clear compatibility target.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- Only one implementation task has completed under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
