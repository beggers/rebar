# Current Status

Updated: 2026-03-11

## Phase
Phase 3: implementation and harness bootstrap, with the Rust workspace scaffold landed and the Python/package plus harness scaffolds queued.

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
- A second completed implementation task, `RBR-0001`, with `docs/spec/syntax-scope.md` pinning the first parser target to CPython `3.12.x`, mapping major regex construct families, and recording deferred parser-adjacent scope.
- A third completed implementation task, `RBR-0002`, with `docs/testing/correctness-plan.md` defining fixture sources, layered differential checks, parser-versus-module correctness boundaries, phased harness delivery, and the planned `reports/correctness/latest.json` scorecard shape.
- A fourth completed implementation task, `RBR-0003`, with `docs/benchmarks/plan.md` defining parser-versus-module benchmark families, workload design, warmup/noise policy, incremental harness delivery, and the planned `reports/benchmarks/latest.json` scorecard shape.
- A supervisor-completed queue-shaping task, `RBR-0004`, that split post-planning work into four concrete scaffold tickets for the Rust workspace, CPython extension, correctness harness, and benchmark harness.
- A fifth completed implementation task, `RBR-0005`, with a root `Cargo.toml` workspace, a `crates/rebar-core` library crate, and a smoke-tested placeholder parser API pinned to the initial CPython `3.12.x` target line.
- Report rendering that recomputes last-cycle environment issues from run artifacts so dashboard anomalies do not stay stale after a detection fix.
- A fetch-before-push git sync path that measures ahead/behind state against fresh upstream refs and reports diverged branches explicitly instead of pushing against stale remote-tracking data.
- README capability reporting that now keys scaffold and scorecard tracks to concrete artifact paths and distinguishes the benchmark harness from the published benchmark report.
- Tracked state, task queue directories, and seeded ready tasks under `ops/`.

## What Does Not Exist Yet
- A CPython extension module or importable Python package scaffold for `rebar`.
- A runnable correctness harness or published correctness scorecard.
- A runnable benchmark harness or published benchmark scorecard.

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
- Land `RBR-0006` to add a PyO3/maturin-backed CPython extension scaffold plus an importable `python/rebar` package on top of the new workspace.
- Land `RBR-0007` and `RBR-0008` to create runnable correctness and benchmark harness skeletons plus placeholder published reports.
- Land `RBR-0009` after both harness scaffolds so the reports record an exact CPython `3.12.x` patch/build instead of only the family line.

## Risks
- The repo now validates only the Rust core-crate path; Python packaging, native-module loading, and import-path assumptions still have no exercised artifact.
- The first CPython-extension scaffold now needs to lock in packaging choices such as PyO3/maturin and module layout; if that remains implicit, later tasks will churn on setup instead of compatibility work.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- The prose pin to CPython `3.12.x` is not yet backed by differential fixtures, so hidden patch-level drift could still surface once harness work starts.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has only five completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
