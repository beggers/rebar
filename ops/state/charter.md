# Rebar Charter

## Objective
Create a Rust implementation of Python's `re` stack that is bug-for-bug compatible at the module boundary and eventually faster than CPython's parser when loaded through a CPython-facing extension module.

## Ground Rules
- Correctness before speed claims.
- Spec before optimization.
- Benchmarks must compare against a concrete baseline.
- Public `re` compatibility matters, not just internal parser acceptance.
- The implementation language target is Rust, with CPython integration as a first-class requirement.
- Durable project knowledge belongs in tracked files, not only in agent memory or logs.

## Planned Phases
1. **Harness bootstrap**
   - Supervisor/implementation roles exist.
   - Loop policy exists.
   - Durable state and task queue exist.
2. **Compatibility and scope**
   - Define the exact subset or version of CPython regex syntax we target first.
   - Define the public-module compatibility target for a drop-in `re` replacement.
   - Define AST and error-reporting expectations.
3. **Correctness infrastructure**
   - Build parsing and public-API conformance tests and fixtures.
   - Add differential checks against CPython where practical.
4. **Benchmark infrastructure**
   - Add reproducible parser and module-level benchmarks against CPython.
5. **Rust implementation**
   - Build the first complete Rust parser and AST.
   - Build a CPython-facing extension module and packaging layer.
6. **Optimization**
   - Use benchmark data to drive speed work.

## Near-Term Exit Criteria
- The repo has a concrete syntax scope document.
- The repo has a concrete drop-in compatibility target for the `re` module surface.
- There is a written plan for correctness testing.
- There is a written plan for benchmark methodology.
- Implementation tasks are concrete enough that workers can start shipping artifacts without restating the whole project.
