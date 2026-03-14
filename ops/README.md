# Rebar Ops

This directory is the tracked operating system for the project.

## Layout
- `agents/`: prompt bodies plus Python `SPEC` modules that define who runs.
- `config/`: loop policy and Codex runner settings.
- `state/`: durable project context that future runs should read first.
- `tasks/`: task queue and task template.
- `user_asks/`: supervisor-owned intake for future human notes and harness requests.

## Workflow
1. The loop loads enabled agent specs from `ops/agents/*.py`.
2. The enabled supervisor runs first every cycle, owns `USER-ASK` harness work, is the only agent that may retune the harness or active agent set, and should review recent sub-agent output quality so it can trim or retune weak prompts quickly.
3. The intended specialist order is: architecture, architecture implementation, feature planning, feature implementation, QA/testing, implementation faithfulness, cleanup, then reporting.
4. The ready queue is owner-routed: `architecture-implementation` claims architecture/refactor tasks and `feature-implementation` claims feature/parity/benchmark tasks, and each worker moves its assigned task to `done/` or `blocked`.
5. Every agent should take at most one bounded action per run; architecture, QA/testing, and cleanup should keep landing one concrete improvement per cycle while bounded work remains instead of defaulting to no-op.
6. Feature planning should keep benchmark catch-up pointed through the Python-facing path when faithful `re` comparisons matter, cleanup should first delete JSON blobs and their generator/plumbing when that preserves needed surfaces, and reporting should only surface benchmark claims it believes are trustworthy.
7. `USER-ASK` notes should be dropped into `ops/user_asks/inbox/`; the supervisor handles them there and archives them into `ops/user_asks/done/` instead of sending them through the implementation queue.
8. Over time the agents should converge the repo toward one vanilla Python parity harness and one vanilla Python benchmark harness, minimizing bespoke JSON manifests, custom data plumbing, and opaque checked-in artifacts wherever practical.
9. `scripts/loop_forever.sh` re-invokes one bounded `cycle` at a time, so repo changes take effect on the next pass.
10. The harness auto-recovers stale `in_progress` tasks, syncs the tracked README status block from dedicated short summary sections in `ops/state/current_status.md`, commits each agent's work immediately after its run, auto-pushes repo changes at the end of the cycle, and writes a dashboard after each cycle.
11. Those per-agent commits use the format `<agent-name>: <brief description>` and a detailed body derived from the agent's final message, so every agent should leave a clear end-of-run summary with verification details.
12. `python3 scripts/rebar_ops.py report` also refreshes the published combined correctness scorecard when needed, the runtime dashboard files, and the README status block on demand, so a supervisor can resync human-facing status without waiting for another full cycle; the renderer caps README next-step and risk bullets so the landing page stays concise even as detailed ops state grows.
13. Runtime prompts, logs, metadata, task state, and anomaly summaries are written to ignored `.rebar/runtime/`.
14. Supervisors can force a specific agent through environment backoff with `python3 scripts/rebar_ops.py cycle --force-agent <agent>` when validating a harness fix.
15. `scripts/rebar_ops.py cycle` runs are serialized with a runtime lock so a manual cycle cannot overlap the forever loop in the same checkout.
16. Environment-mismatch detection trusts the explicit sandbox banner plus the child last message, but not the raw stdout/stderr transcript, because Codex echoes prompts and tool traces there.
17. End-of-cycle git sync now fetches the configured upstream and merges it into the local branch before pushing when the branch is behind, so remote-only upstream commits stop stalling progress and dashboard state reflects the post-merge reality.

## Why It Exists
- Future agent runs should not need to infer project history from scratch.
- The supervisor needs a durable place to record decisions and retune the harness.
- The Feature Implementation Agent needs a narrow, concrete queue instead of a vague project brief.
- Specialist agents need a stable way to improve planning, architecture, QA, faithfulness, and reporting without freelancing each other’s roles.
- Harness ownership stays centralized in the supervisor so other agents cannot drift into accidental operating-system changes.
- Feature Planning owns backlog/frontier bookkeeping so the ready queue and tracked state do not drift apart over time.
