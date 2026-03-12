# Current Status

Updated: 2026-03-12

## Phase
Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary benchmark pack and public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, and the remaining symbol-surface, pattern-object, provenance, and honest-behavior gaps queued.

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
- A twelfth completed implementation task, `RBR-0012`, with `python/rebar_harness/benchmarks.py`, `benchmarks/workloads/compile_matrix.json`, `tests/benchmarks/test_compile_benchmark_matrix.py`, and a regenerated `reports/benchmarks/latest.json`, expanding the benchmark scaffold into a six-workload Phase 1 compile-path suite with cold/warm/purged cache labels, environment metadata, and explicit source-tree-shim provenance while still reporting `rebar` honestly as unimplemented.
- A thirteenth completed implementation task, `RBR-0013`, with expanded module-helper scaffolding in `python/rebar/__init__.py`, matching native placeholder hooks in `crates/rebar-cpython/src/lib.rs`, and `tests/python/test_module_surface_scaffold.py`, exposing the first bounded `re`-shaped helper surface while keeping unimplemented behavior loud and preserving the built native-load smoke path.
- A fourteenth completed implementation task, `RBR-0014`, with `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/public_api_surface.json`, `tests/conformance/test_correctness_public_api_surface.py`, and a regenerated `reports/correctness/latest.json`, expanding the correctness scorecard into a 22-case Phase 2 report that separates the 15-case parser pack from a 7-case module API surface pack with helper-presence, placeholder-behavior, and cache-surface observations.
- A fifteenth completed implementation task, `RBR-0015`, with a generalized multi-manifest benchmark runner in `python/rebar_harness/benchmarks.py`, a new `benchmarks/workloads/module_boundary.json` workload pack, `tests/benchmarks/test_module_boundary_benchmarks.py`, and a regenerated `reports/benchmarks/latest.json`, expanding the published benchmark scorecard into a combined 14-workload report that keeps the six-workload compile-path parser family and the new eight-workload module-boundary family separate while reporting `rebar` helper timings honestly as unimplemented.
- A sixteenth completed implementation task, `RBR-0016`, with `python/rebar_harness/correctness.py`, `tests/conformance/fixtures/match_behavior_smoke.json`, `tests/conformance/test_correctness_match_behavior.py`, and a regenerated `reports/correctness/latest.json`, expanding the correctness scorecard into a 28-case combined report that adds a six-case Phase 3 match-behavior pack with tiny `search`/`match`/`fullmatch` success and no-match observations for both `str` and `bytes` while continuing to report `rebar` gaps honestly.
- A seventeenth completed implementation task, `RBR-0017`, with `python/rebar_harness/benchmarks.py`, `benchmarks/workloads/regression_matrix.json`, `tests/benchmarks/test_regression_benchmark_pack.py`, and a regenerated `reports/benchmarks/latest.json`, expanding the published benchmark scorecard into a 19-workload combined report that adds a five-workload Phase 3 regression/stability pack with smoke-tagged rerun coverage, manifest-level provenance, and honest known-gap accounting.
- A refreshed ready queue that now centers Milestone 2 on exported-symbol and compiled-pattern scaffolding plus benchmark-provenance hardening, while still extending into post-scaffold correctness and the first literal-only/cache/escape behavior follow-on tasks.
- Report rendering that recomputes last-cycle environment issues from run artifacts so dashboard anomalies do not stay stale after a detection fix.
- A fetch-before-push git sync path that measures ahead/behind state against fresh upstream refs and reports diverged branches explicitly instead of pushing against stale remote-tracking data.
- README capability reporting that now keys scaffold and scorecard tracks to concrete artifact paths and distinguishes the benchmark harness from the published benchmark report.
- README status rendering now labels capability-track coverage explicitly instead of implying end-user feature completeness, and it summarizes benchmark baseline provenance instead of dumping raw JSON into the landing page table.
- Tracked state, task queue directories, and seeded ready tasks under `ops/`.

## What Does Not Exist Yet
- Correctness coverage beyond the 28-case parser, module-API, and match-behavior packs; exported-symbol, compiled-pattern, and module-workflow scorecards are still missing.
- Exported flags/constants, helper types, and compiled-pattern scaffolds beyond the landed helper surface and native-module metadata helpers.
- Built-native benchmark provenance and timing coverage are still absent from the published benchmark report; the tracked scorecard now covers parser compile-path, module-boundary, and regression/stability workloads, but it still runs through the source-tree shim.
- Measured `rebar` helper-call benchmark timings remain mostly absent; the published benchmark report now includes import timings plus the new regression pack, but helper-call rows still end in explicit `unimplemented` results.

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
- Land `RBR-0018`, `RBR-0019`, and `RBR-0020` so the new regression/stability benchmark pack is followed by exported-symbol scaffolding, a concrete compiled-pattern surface, and truthful native-versus-shim benchmark provenance.
- Keep `RBR-0021` and `RBR-0022` queued directly behind that work so the worker can continue into exported-symbol and pattern-object correctness packs without another supervisor-only queue rewrite.
- Use `RBR-0023` through `RBR-0027` as the next slice after the current scaffold wave so the queue turns newly landed `Pattern` and `Match` surface area into narrow honest behavior, cache/purge observability, `escape()` parity, pattern-boundary benchmark coverage, and module-workflow correctness.

## Risks
- The repo now validates a dedicated built `rebar._rebar` smoke path, but the published benchmark report still reflects the source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer and a published match-behavior smoke pack, but exported flags/constants and compiled-pattern objects are still outside the measured compatibility surface.
- The correctness harness now covers 28 cases across parser, module-API, and match-behavior layers, but 24 `rebar` comparisons still end in honest `unimplemented` outcomes and there is no compiled-pattern or module-workflow layer yet.
- The benchmark harness now measures the six parser-family compile-path workloads, the eight-workload module-boundary pack, and the five-workload regression/stability pack, but only import rows produce real `rebar` timings so helper-call comparisons are still mostly placeholder gaps and the suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has seventeen completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
