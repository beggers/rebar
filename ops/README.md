# Rebar Ops

This directory is the tracked operating system for the project.

## Layout
- `agents/`: prompt bodies plus JSON agent specs that define who runs.
- `config/`: loop policy and Codex runner settings.
- `state/`: durable project context that future runs should read first.
- `tasks/`: task queue and task template.
- `user_asks/`: supervisor-owned intake for future human notes and harness requests.

## Workflow
1. The loop loads enabled agent specs from `ops/agents/*.json`.
2. The enabled supervisor runs first every cycle, owns `USER-ASK` harness work, and is the only agent that may retune the harness or active agent set.
3. The intended specialist order is: architecture, feature planning, feature implementation, QA/testing, implementation faithfulness, cleanup, then reporting.
4. The Feature Implementation Agent is the single ready-queue consumer and moves claimed tasks to `done/` or `blocked`.
5. Every agent should take at most one bounded action per run; non-implementation specialists should no-op freely when their role is not useful that cycle.
6. Feature planning should keep benchmark catch-up pointed through the Python-facing path when faithful `re` comparisons matter, cleanup should delete redundant checked-in cruft when justified, and reporting should only surface benchmark claims it believes are trustworthy.
7. `USER-ASK` notes should be dropped into `ops/user_asks/inbox/`; the supervisor handles them there and archives them into `ops/user_asks/done/` instead of sending them through the implementation queue.
8. Over time the agents should converge the repo toward one vanilla Python parity harness and one vanilla Python benchmark harness, minimizing bespoke JSON manifests, custom data plumbing, and opaque checked-in artifacts wherever practical.
9. `scripts/loop_forever.sh` re-invokes one bounded `cycle` at a time, so repo changes take effect on the next pass.
10. The harness auto-recovers stale `in_progress` tasks, syncs the tracked README status block from dedicated short summary sections in `ops/state/current_status.md`, auto-commits and auto-pushes repo changes, and writes a dashboard after each cycle.
11. `python3 scripts/rebar_ops.py report` also refreshes the published combined correctness scorecard when needed, the runtime dashboard files, and the README status block on demand, so a supervisor can resync human-facing status without waiting for another full cycle; the renderer caps README next-step and risk bullets so the landing page stays concise even as detailed ops state grows.
12. Runtime prompts, logs, metadata, task state, and anomaly summaries are written to ignored `.rebar/runtime/`.
13. Supervisors can force a specific agent through environment backoff with `python3 scripts/rebar_ops.py cycle --force-agent <agent>` when validating a harness fix.
14. `scripts/rebar_ops.py cycle` runs are serialized with a runtime lock so a manual cycle cannot overlap the forever loop in the same checkout.
15. Environment-mismatch detection trusts the explicit sandbox banner plus the child last message, but not the raw stdout/stderr transcript, because Codex echoes prompts and tool traces there.
16. End-of-cycle git sync now fetches the configured upstream before deciding whether to push, so dashboard state and git anomalies reflect real ahead/behind divergence instead of stale remote-tracking refs.

## Why It Exists
- Future agent runs should not need to infer project history from scratch.
- The supervisor needs a durable place to record decisions and retune the harness.
- The Feature Implementation Agent needs a narrow, concrete queue instead of a vague project brief.
- Specialist agents need a stable way to improve planning, architecture, QA, faithfulness, and reporting without freelancing each other’s roles.
- Harness ownership stays centralized in the supervisor so other agents cannot drift into accidental operating-system changes.
- Feature Planning owns backlog/frontier bookkeeping so the ready queue and tracked state do not drift apart over time.
