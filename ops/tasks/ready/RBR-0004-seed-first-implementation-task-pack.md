# RBR-0004: Seed the first implementation task pack

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Translate the completed Milestone 1 spec and planning documents into the first concrete implementation-task pack for scaffolding and harness work.

## Deliverables
- `ops/tasks/ready/RBR-0005-rust-workspace-scaffold.md`
- `ops/tasks/ready/RBR-0006-cpython-extension-scaffold.md`
- `ops/tasks/ready/RBR-0007-conformance-harness-scaffold.md`
- `ops/tasks/ready/RBR-0008-benchmark-harness-scaffold.md`

## Acceptance Criteria
- Each new task is bounded to one implementation-agent run and has concrete deliverables, acceptance criteria, and constraints.
- The task pack separates Rust parser/workspace scaffolding, CPython-facing module scaffolding, correctness-harness scaffolding, and benchmark-harness scaffolding instead of collapsing them into one oversized task.
- Each new task cites the relevant source docs from `docs/spec/drop-in-re-compatibility.md`, `docs/spec/syntax-scope.md`, `docs/testing/correctness-plan.md`, and `docs/benchmarks/plan.md`.
- Each new task preserves the initial CPython `3.12.x` baseline unless it explicitly explains why a narrower patch-level pin is required.
- The resulting filenames and IDs keep prerequisite tasks ahead of dependent tasks in lexical queue order.

## Constraints
- Do not implement the scaffold or harness work in this task.
- Do not rewrite the milestone docs; this task is only about turning them into executable queue items.
- Prefer smaller, immediately actionable tasks over a large umbrella ticket.

## Notes
- This task is intentionally ordered after `RBR-0002` and `RBR-0003` so the worker reaches it only once the remaining planning docs exist.
- The result should leave `ops/tasks/ready/` populated with the first post-planning implementation work without requiring another supervisor rewrite pass.
