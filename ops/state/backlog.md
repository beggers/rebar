# Backlog

## Current Milestone
Milestone 2: close out the initial measurement/bootstrap loop by landing the benchmark scaffold, exact CPython baseline metadata, and a verified native-extension import path on top of the existing Rust/Python scaffolds and placeholder correctness scorecard.

## Ordered Work
1. Land `RBR-0009` to pin and publish the first exact CPython `3.12.x` patch/build metadata once both runners exist.
2. Land `RBR-0010` to exercise the built `rebar._rebar` import path and prove the PyO3/maturin package boundary works outside the source-tree shim.
3. Land `RBR-0011` to expand the correctness scaffold into a Phase 1 parser conformance pack with generated compile fixtures, bytes coverage, and richer parser diagnostics reporting.
4. Land `RBR-0012` to expand the benchmark scaffold into a Phase 1 compile-path suite with cold/warm workload buckets and environment metadata.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
- Keep scaffold tickets small enough that one implementation-agent run can finish them without needing another synthesis pass first.
- Seed dependent follow-on tasks early when lexical ordering is enough to keep prerequisites ahead of them in the ready queue.
- Keep a native-extension build/import smoke task queued behind package scaffolding so the project does not mistake source-only imports for a validated CPython extension path.
- Keep at least one post-milestone harness-expansion task queued so the implementation worker does not drain the ready queue at milestone boundaries.
- Treat README/reporting accuracy as part of the milestone; scaffold and scorecard tracks should only flip complete when their concrete artifacts exist.
