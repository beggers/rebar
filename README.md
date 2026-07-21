# rebar

This repository is a phase-gated experiment to find a compatible, materially faster replacement for Python's `re` module.

The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. Scope clarifications are in [AMENDMENTS.md](AMENDMENTS.md).

## Status

| Gate | Result |
| --- | --- |
| Correctness oracle | PASS v1.1 — 2,048/2,048, 38/38 obligations, zero invalid successes or false properties |
| Qualified candidates | 3/3 — independent AST, native bytecode VM, and Rust/FFI families each pass 2,048/2,048 |
| Performance oracle | PASS — 1,152 paired, correctness-gated rows per experiment; no candidate meets the speed target |
| Winner | NOT MEASURED |

The baseline is [CPython 3.14.6](oracle/v1/BASELINE.md). The [P0 matrix](oracle/v1/P0.md) covers the complete public API, documented syntax, errors, warnings, seeded differential/property/fuzz cases, and two explicitly named private waivers. The v1.1 fixture SHA-256 is `983885ee6411fd806edf3d72efbcc989f9b9f7775a6d127dc7c865673eeb0fed`; the denominator and all seeds are unchanged. Two isolated stdlib runs agree, and the committed failure list is empty. The pre-candidate strengthening is recorded in [AMENDMENTS.md](AMENDMENTS.md).

The [candidate discovery experiment](candidates/evidence/DISCOVERY.md) and all raw losses are preserved as rejected binding experiments. Three independent, dependency-free families are correctness-qualified: the [recursive AST backtracker](candidates/AST.md), the [iterative parser/native bytecode VM](candidates/VM.md), and the [Rust continuation arena/FFI](candidates/RUST.md). Native gates include sanitizer runs and zero-delegation audits. No performance claim has been made.

The [performance protocol](performance/v1/PROTOCOL.md) freezes 16 calibration and 16 holdout cases with equal weights, paired trials, seeds, lifecycle/boundary coverage, memory observations, confidence intervals, and regression rules. Its expected-result SHA-256 is `35d016d9f6f02f917a3c86df221a4b1fed3ede689c85646dd08aab34ec673344`. The [first pilot](performance/v1/evidence/PILOT.md) exposed severe repeated FFI boundary cost; the [native-search experiment](performance/v1/evidence/PILOT-NATIVE-SEARCH.md) removes it for all inputs and reruns both correctness oracles.

The [initial paired report](performance/v1/evidence/INITIAL-RESULTS.md) retains all 1,152 raw rows, all 96 case/candidate results, and all 92 regressions. Initial holdout geomeans are AST **0.0111x**, native VM **0.1141x**, and Rust/FFI **0.0140x**; only the VM's cold case is statistically faster (1/16).

The [native batching experiment](performance/v1/evidence/NATIVE-BATCH.md) moves repeated `findall`, `finditer`, and `split` searches across the C boundary once, reduces VM state allocation, and adds general prefix/suffix rejection. It passes both correctness oracles and preserves all 1,152 paired rows and 90 regressions. VM holdout improves to **0.3291x** with 2/16 statistically faster cases (long-boundary and cold); AST is **0.0112x** and Rust is **0.0141x**. The result still falsifies a speed win and points to public-result construction and execution-state cost as the next boundary. Winner remains NOT MEASURED.

The [stack-state executor experiment](performance/v1/evidence/STACK-STATE-REJECTED.md) is correctness-clean but rejected: copying a large fixed frame on every branch lowers VM holdout to **0.2435x** (2/16 faster) and preserves 90 regressions. All 1,152 paired rows and generated charts remain committed; the slower executor is removed. This isolates compact choice points and public result construction as the next useful experiments.

![Native batching holdout speed and confidence](performance/v1/evidence/native-batch-speed.svg)

![Native batching holdout memory](performance/v1/evidence/native-batch-memory.svg)

![Native batching regressions](performance/v1/evidence/native-batch-regressions.svg)

![Native batching rankings](performance/v1/evidence/native-batch-rankings.svg)

![Rejected stack-state holdout speed and confidence](performance/v1/evidence/stack-state-rejected-speed.svg)

![Rejected stack-state holdout memory](performance/v1/evidence/stack-state-rejected-memory.svg)

![Rejected stack-state regressions](performance/v1/evidence/stack-state-rejected-regressions.svg)

![Rejected stack-state rankings](performance/v1/evidence/stack-state-rejected-rankings.svg)

![Initial holdout speed and confidence](performance/v1/evidence/initial-speed.svg)

![Initial holdout memory](performance/v1/evidence/initial-memory.svg)

![Initial regressions](performance/v1/evidence/initial-regressions.svg)

![Initial rankings](performance/v1/evidence/initial-rankings.svg)

![Correctness oracle status](oracle/v1/evidence/correctness.svg)

![Raw candidate correctness status](candidates/evidence/discovery-correctness.svg)

![Qualified AST candidate correctness status](candidates/evidence/ast-correctness.svg)

![Qualified candidate correctness status](candidates/evidence/qualified-correctness.svg)

To regenerate and self-check the current oracle using the pinned runtime:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
"$PY" tools/oracle.py freeze
"$PY" tools/oracle.py verify --module re --output oracle/v1/evidence/correctness-self.json
"$PY" tools/oracle.py chart --input oracle/v1/evidence/correctness-self.json --output oracle/v1/evidence/correctness.svg
# Reproduce a single stable case ID, including fuzz/property cases:
"$PY" tools/oracle.py verify --module re --case fuzz.str.0377

# Verify the frozen performance cases before collecting timing data:
PYTHONPATH=. "$PY" tools/perf.py verify --output performance/v1/evidence/performance-correctness.json
```
