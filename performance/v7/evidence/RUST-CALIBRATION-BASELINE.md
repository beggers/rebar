# Corrected Rust: practice-only starting point

This is a diagnostic, not the final speed test. All **10,312** unseen cases remain sealed.

The corrected from-scratch Rust engine was compared directly with pinned CPython 3.14.6 using the frozen **624-case** practice plan. Every case was measured for **seven paired trials**, with four warmups and **8,736** complete timing records. All **26,208** before-, during-, and after-measurement correctness checks passed.

| Measure | Corrected Rust, practice cases only |
| --- | ---: |
| Overall speed compared with Python | **0.994×** |
| 95% confidence interval | **0.956–1.034×** |
| Cases demonstrably faster | **245/624** |
| Cases demonstrably slower | **263/624** |
| Cases not statistically resolved | **116/624** |
| Cases taking more than 20% longer | **175/624** |

The confidence interval includes **1×**, so the corrected Rust baseline has not demonstrated an overall speedup. Every large slowdown is retained in the complete summary; no task, operation, or result is omitted.

The frozen workload includes all 12 public operations:

| Operation | Practice cases | Overall speed | More than 20% slower |
| --- | ---: | ---: | ---: |
| Accessing match objects | 48 | 0.327× | 48 |
| Scanner | 48 | 0.827× | 25 |
| Find all | 80 | 0.906× | 31 |
| Match | 48 | 0.909× | 5 |
| Full match | 47 | 0.939× | 19 |
| Escape | 48 | 0.998× | 0 |
| Find iterator | 67 | 1.018× | 15 |
| Search | 48 | 1.024× | 18 |
| Replace and count | 47 | 1.191× | 2 |
| Split | 47 | 1.241× | 11 |
| Replace | 48 | 1.259× | 1 |
| Compile | 48 | 2.432× | 0 |

These groups contain exactly **624** cases and exactly **175** large slowdowns. A large slowdown means `Python time / Rust time < 5/6`; this is strictly more than 20% additional elapsed time, not a claim about statistical significance. Operation-level speeds are geometric means across all cases in that operation.

The practice sample also includes **260** workload categories, **486** precompiled, **80** module-level, and **58** cold-compilation cases; text, bytes, byte arrays, and memory views; and zero, one, few, and many results.

The median Python-traced temporary-memory ratio is **0.288×**. This measures allocations observed by Python's memory tracer; it does not establish Rust-only process memory, resident memory, or native allocator usage.

- [All 8,736 original paired observations](rust-v7-calibration-corrected-v4-baseline-raw.jsonl.gz).
- [All 624 case results and all 175 large slowdowns](rust-v7-calibration-corrected-v4-baseline-summary.json).
- [Independent full-result and native-artifact integrity audit](rust-v7-calibration-corrected-v4-baseline-integrity.json).
- [Overall practice speed and confidence interval](rust-v7-calibration-overall.svg).
- [All 12 public operations](rust-v7-calibration-api.svg).
- [Every faster, slower, unresolved, and substantially slower case](rust-v7-calibration-win-loss.svg).
- [All 175 substantial slowdowns, grouped by operation](rust-v7-calibration-regressions.svg).
- [Python-traced temporary memory for all 12 operations](rust-v7-calibration-memory.svg).
- [Practice-data isolation and the frozen 624-case plan](../../../candidates/evidence/RUST-V7-CALIBRATION-ISOLATION.md).

The native engine, native Python bridge, both native sources, and Python interface are fingerprinted before and after the run. Their independently frozen correctness report passes **223,198/223,198** checks. No external regular-expression package, Python regex fallback, benchmark-detection shortcut, full performance suite, or unseen test case is used.

Final unseen Rust speed: **NOT MEASURED**. Unseen cases read: **0**.

Reproduce the independent audit and charts without accessing the final benchmark:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/rust_v7_calibration_result_audit.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_result_audit.py
PYTHONPATH=. "$PY" tools/rust_v7_calibration_charts.py --self-test
PYTHONPATH=. "$PY" tools/rust_v7_calibration_charts.py
```
