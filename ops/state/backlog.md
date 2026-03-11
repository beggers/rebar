# Backlog

## Current Milestone
Milestone 1: define the Rust implementation target and drop-in `re` compatibility contract well enough that implementation work can start without re-litigating scope each run.

## Ordered Work
1. Turn the completed spec and planning docs into concrete Rust crate, CPython-extension, conformance-harness, and benchmark-harness tasks.
2. Build the first Rust package layout plus empty correctness and benchmark harness scaffolds from that seeded task pack.
3. Start differential parser and module-surface checks before any optimization work.
4. Start compile-path and module-boundary benchmark runs before any optimization work.
5. Publish initial placeholder correctness and benchmark scorecards once the harness skeletons exist.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
- Keep `RBR-0004` immediately behind `RBR-0003`; scaffold tickets should now inherit the finished benchmark methodology instead of guessing it.
