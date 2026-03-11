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
- Tracked state, task queue directories, and seeded ready tasks under `ops/`.

## What Does Not Exist Yet
- Rust parser source code.
- CPython extension module or drop-in `re` compatibility layer.
- Correctness test harness.
- Benchmark harness.
- Concrete syntax and module-compatibility documents under `docs/`.

## Operational Notes
- Launch the forever loop from a normal shell on a writable checkout. Nested runs inside another sandboxed Codex session can still distort child-agent behavior and reporting.
- On the dedicated EC2 forever-run path, default child Codex sessions to `danger-full-access`. The `workspace-write` sandbox has produced false write failures for nested worker sessions on the VM even when the checkout itself is writable.
- On the current VM path, invoke Codex with `--dangerously-bypass-approvals-and-sandbox` instead of relying on `--sandbox danger-full-access --ask-for-approval never`. The explicit bypass flag has proven necessary for actual write access in non-interactive `exec` runs.
- The harness now classifies any unexpected child `sandbox: read-only` result as an environment mismatch even when `danger-full-access` was requested, and it waits before retrying that worker again.
- The harness now ignores the child stdout/stderr transcript when inferring sandbox mismatches and trusts only the explicit sandbox banner plus the child last message, because both streams can include echoed prompts and tool traces that mention `read-only` for unrelated reasons.
- Worker environment backoff is now five minutes instead of thirty so a false-positive probe or transient VM issue does not stall the ready queue for half an hour.
- Supervisors can now run `python3 scripts/rebar_ops.py cycle --force-agent implementation` to validate a fixed worker path immediately instead of waiting for environment backoff to expire.
- Supervisors should only force a manual `cycle` when no other cycle is already running in the checkout; the harness now rejects overlapping cycle attempts with a runtime lock instead of letting them race.
- Implementation agents are expected to verify write failures in the current run instead of trusting historical runtime artifacts about sandbox state.

## Immediate Next Steps
- Let the live forever loop complete a full cycle on the corrected supervisor environment-detection path and confirm the dashboard stops reporting false supervisor sandbox anomalies.
- If the next completed cycle still leaves the ready queue untouched, treat it as a worker-dispatch or task-finalization regression rather than a raw child-write problem.
- Use the implementation agent to write the Rust drop-in target, syntax spec, correctness plan, and benchmark plan documents now that bypass-mode child writes and isolated probe validation are both in place.
- After those land, start Rust crate scaffolding, CPython-extension scaffolding, and the first parser tests.

## Risks
- The project can drift into premature implementation without a clear compatibility target.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Nested supervisor runs inside a live forever loop can still create misleading runtime anomalies even when the underlying worker write path is healthy.
- The implementation worker still has not completed a task in a full bounded cycle, so a remaining dispatch or terminal-state bug may still surface after the sandbox-reporting fix.
