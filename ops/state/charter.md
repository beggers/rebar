# Rebar Charter

## Objective
Create a regex parsing library that is measurably competitive with, and eventually faster than, the parser used by CPython.

## Ground Rules
- Correctness before speed claims.
- Spec before optimization.
- Benchmarks must compare against a concrete baseline.
- Durable project knowledge belongs in tracked files, not only in agent memory or logs.

## Planned Phases
1. **Harness bootstrap**
   - Supervisor/implementation roles exist.
   - Loop policy exists.
   - Durable state and task queue exist.
2. **Compatibility and scope**
   - Define the exact subset or version of CPython regex syntax we target first.
   - Define AST and error-reporting expectations.
3. **Correctness infrastructure**
   - Build parsing conformance tests and fixtures.
   - Add differential checks against CPython where practical.
4. **Benchmark infrastructure**
   - Add reproducible parser benchmarks and baseline comparisons.
5. **Parser implementation**
   - Build the first complete parser and AST.
6. **Optimization**
   - Use benchmark data to drive speed work.

## Near-Term Exit Criteria
- The repo has a concrete syntax scope document.
- There is a written plan for correctness testing.
- There is a written plan for benchmark methodology.
- Implementation tasks are concrete enough that workers can start shipping artifacts without restating the whole project.
