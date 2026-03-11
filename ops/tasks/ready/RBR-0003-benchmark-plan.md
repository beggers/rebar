# RBR-0003: Write the benchmark plan

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Define how `rebar` will measure parser and module-level performance against a CPython baseline.

## Deliverables
- `docs/benchmarks/plan.md`

## Acceptance Criteria
- The document identifies primary metrics, workloads, baseline comparisons, and where parser-only versus drop-in-module benchmarks differ.
- The document explains how benchmark noise and warmup will be handled.
- The document separates parser benchmarking from later regex execution benchmarking.
- The document states which CPython version/build will be the initial baseline and how that baseline stays consistent with the syntax-scope document, or it calls out a provisional baseline if the scope task lands later.
- The document describes the intended top-level fields for `reports/benchmarks/latest.json` well enough that later implementation work can publish a stable tracked scorecard.

## Constraints
- Focus on parser and importable-module performance, not the regex engine as a whole.
- Assume the implementation is Rust exposed through CPython and that benchmarking should happen from Python-facing entry points when relevant.
- Keep the methodology reproducible from a local developer machine.

## Notes
- This plan should make later optimization work falsifiable.
- Include what a tracked benchmark scorecard should eventually publish to `reports/benchmarks/latest.json`.
- Use `docs/spec/drop-in-re-compatibility.md` as the user-visible contract and make any temporary CPython-baseline assumptions explicit.
- 2026-03-11T17:30:12+00:00: harness requeued after failed or incomplete run after run `20260311T173012Z-implementation-RBR-0003-benchmark-plan` (exit=1, timed_out=false).
