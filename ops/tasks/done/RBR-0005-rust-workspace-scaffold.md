# RBR-0005: Scaffold the Rust workspace and parser core crate

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Create the first Rust workspace layout for `rebar` so later parser and extension work land in stable crate boundaries instead of ad hoc files.

## Deliverables
- `Cargo.toml`
- `crates/rebar-core/Cargo.toml`
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-core/tests/smoke.rs`

## Acceptance Criteria
- The repo has a root Cargo workspace that includes `crates/rebar-core` and leaves room for later companion crates such as the CPython bridge.
- `crates/rebar-core` builds as a library crate and exposes a deliberately small placeholder API that future extension work can link against without pretending parser semantics already exist.
- `cargo test -p rebar-core` passes.
- The scaffold is clearly documented in code comments or crate metadata as a placeholder for the CPython `3.12.x` parser target rather than a partial parser implementation.

## Constraints
- Do not implement real regex parsing or matching logic in this task.
- Do not add Python packaging or CPython-extension files here beyond what is strictly necessary for the Rust workspace to compile.
- Keep the public Rust surface intentionally narrow so later compatibility work can evolve it without undoing fake APIs.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` and `docs/spec/syntax-scope.md` as the compatibility boundary.
- Leave obvious integration room for the correctness and benchmark harnesses described in `docs/testing/correctness-plan.md` and `docs/benchmarks/plan.md`.
- This task should establish durable crate names and directories so follow-on work does not need another layout decision.

## Completion Note
- Completed on 2026-03-11.
- Added a root Cargo workspace plus the `crates/rebar-core` library crate scaffold.
- Exposed a deliberately narrow placeholder API: CPython target metadata and a parser entrypoint that returns `ParseError::Unimplemented`.
- Added `crates/rebar-core/tests/smoke.rs` and verified the scaffold with `cargo test -p rebar-core`.
