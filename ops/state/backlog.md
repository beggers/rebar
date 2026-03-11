# Backlog

## Current Milestone
Milestone 1: define the Rust implementation target and drop-in `re` compatibility contract well enough that implementation work can start without re-litigating scope each run.

## Ordered Work
1. Write the correctness-harness plan against the pinned CPython `3.12.x` syntax target.
2. Write the benchmark plan against the same baseline.
3. Turn the completed spec/planning docs into concrete Rust crate, CPython-extension, conformance-harness, and benchmark-harness tasks.
4. Build the first Rust package layout and empty conformance test harness.
5. Start differential parser and module-surface checks before any optimization work.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
