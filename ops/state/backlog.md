# Backlog

## Current Milestone
Milestone 2: establish the first runnable Rust/Python project skeleton and placeholder correctness/benchmark scorecards so later parser work lands in stable directories and measurable harnesses.

## Ordered Work
1. Land `RBR-0006` to add the CPython extension and Python-package scaffold on top of the Rust workspace.
2. Land `RBR-0007` to create the first differential correctness harness skeleton and placeholder correctness scorecard.
3. Land `RBR-0008` to create the first benchmark harness skeleton and placeholder benchmark scorecard.
4. Land `RBR-0009` to pin and publish the first exact CPython `3.12.x` patch/build metadata once both runners exist.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
- Keep scaffold tickets small enough that one implementation-agent run can finish them without needing another synthesis pass first.
- Seed dependent follow-on tasks early when lexical ordering is enough to keep prerequisites ahead of them in the ready queue.
- Treat README/reporting accuracy as part of the milestone; scaffold and scorecard tracks should only flip complete when their concrete artifacts exist.
