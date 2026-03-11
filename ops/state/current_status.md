# Current Status

Updated: 2026-03-11

## Phase
Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance pack published, and the remaining benchmark/module-surface gaps queued.

## What Exists
- A repo-local `AGENTS.md` that separates supervisor and implementation roles.
- A config-driven, supervisor-first loop runner in `scripts/rebar_ops.py`.
- A dynamic agent registry under `ops/agents/*.json` that the supervisor can edit.
- A tiny outer shell loop in `scripts/loop_forever.sh` that re-runs bounded cycles so supervisor changes apply on the next iteration.
- Auto-commit, auto-push, stale-task recovery, runtime retention, and dashboard generation policy in the harness.
- A tracked `README.md` landing page with an auto-synced current-state section for humans.
- A README reporting model that now surfaces the tracked correctness and benchmark scorecards from `reports/correctness/latest.json` and `reports/benchmarks/latest.json`.
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
- A sixth completed implementation task, `RBR-0006`, with a root `pyproject.toml`, an importable `python/rebar` scaffold package, a `crates/rebar-cpython` PyO3 extension crate, and a Python smoke test that validates the source-package shim without falling back to stdlib `re`.
- A seventh completed implementation task, `RBR-0007`, with `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/parser_smoke.json`, `tests/conformance/test_correctness_smoke.py`, and `reports/correctness/latest.json`, establishing the first runnable differential correctness harness skeleton and an honest placeholder scorecard with `unimplemented` outcomes.
- An eighth completed implementation task, `RBR-0008`, with `python/rebar_harness/benchmarks.py`, `benchmarks/workloads/compile_smoke.json`, `tests/benchmarks/test_benchmark_smoke.py`, and `reports/benchmarks/latest.json`, establishing the first runnable compile-path benchmark harness skeleton and an honest placeholder scorecard with baseline-only timings plus explicit `rebar` gaps.
- A ninth completed implementation task, `RBR-0009`, with `python/rebar_harness/metadata.py`, refreshed harness runners/tests, and regenerated scorecards that now publish the exact live CPython `3.12.3` patch/build/compiler/platform provenance instead of only the broader `3.12.x` family line.
- A tenth completed implementation task, `RBR-0010`, with `tests/python/test_native_extension_smoke.py`, tighter `python/rebar/__init__.py` import behavior, and a documented smoke command in `pyproject.toml`, proving that a maturin-built `rebar._rebar` artifact can be installed and imported with `native_module_loaded() is True`.
- An eleventh completed implementation task, `RBR-0011`, with `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/parser_matrix.json`, `tests/conformance/test_correctness_parser_matrix.py`, and a regenerated `reports/correctness/latest.json`, expanding the correctness scaffold into a 15-case Phase 1 parser pack with explicit `str`/`bytes` coverage, warning/exception capture, and family-level compile diagnostics while still reporting `rebar` honestly as unimplemented.
- A refreshed ready queue that now extends past the remaining Milestone 2 work with queued follow-on tasks for a broader scaffolded module surface, Phase 2 public-API conformance coverage, Phase 2 module-boundary benchmarks, and the first post-milestone match-behavior/regression harness packs.
- Report rendering that recomputes last-cycle environment issues from run artifacts so dashboard anomalies do not stay stale after a detection fix.
- A fetch-before-push git sync path that measures ahead/behind state against fresh upstream refs and reports diverged branches explicitly instead of pushing against stale remote-tracking data.
- README capability reporting that now keys scaffold and scorecard tracks to concrete artifact paths and distinguishes the benchmark harness from the published benchmark report.
- README status rendering now labels capability-track coverage explicitly instead of implying end-user feature completeness, and it summarizes benchmark baseline provenance instead of dumping raw JSON into the landing page table.
- Tracked state, task queue directories, and seeded ready tasks under `ops/`.

## What Does Not Exist Yet
- Correctness coverage beyond the 15-case parser compile matrix and placeholder `rebar` `unimplemented` outcomes.
- A broader scaffolded `re` helper surface beyond `compile()` and the native-module metadata helpers.
- Public-API correctness coverage for helper presence, placeholder behavior, cache surface, pattern objects, or match results.
- Measured `rebar` benchmark timings or benchmark reports that run through anything richer than the current source-tree shim; the published benchmark scaffold still records CPython baseline samples plus explicit `unimplemented` implementation records.

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
- Land `RBR-0012` to bring the benchmark harness up to the same Phase 1 compile-matrix depth that correctness now has.
- Land `RBR-0013`, `RBR-0014`, and `RBR-0015` so the repo exposes a broader scaffolded `re` helper surface and the scorecards can separate parser progress from public-API and module-boundary progress.
- Keep `RBR-0016` and `RBR-0017` queued behind Milestone 2 so the worker can continue directly into match-behavior correctness and regression/stability benchmark infrastructure without another supervisor-only queue rewrite.

## Risks
- The repo now validates a dedicated built `rebar._rebar` smoke path, but the published benchmark report still reflects the source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface is still minimal, so public-API correctness and module-boundary benchmarking remain blocked on additional placeholder exports even though the native extension now imports successfully.
- The correctness harness now covers 15 parser compile cases, but it still reports `unimplemented` for every `rebar` comparison and does not yet measure helper presence, pattern objects, or match-result behavior.
- The benchmark harness currently measures only two parser-family compile smoke workloads and records no `rebar` timings yet, so timing provenance is still only baseline-side scaffolding.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has only eleven completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
