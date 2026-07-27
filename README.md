# rebar: a faster Python `re` experiment

Build a genuine, faster replacement for Python 3.14.6's regular-expression module:

```python
import rebar as re
```

Each candidate must use its own matching engine built from scratch. Wrapping Python's engine, an external regular-expression package, or another candidate does not count.

## Headline results

![Compatibility against the same 2,807 Python checks: Rust and C both pass all 2,807, and Zig passes 1,717 and fails 1,090](docs/evidence/candidate-correctness-overview-v2.svg)

![Overall public development speed: Python at 1.000 times, Rust at 1.065 times, the 1.5-times target, and C and Zig not yet measured](docs/evidence/rust-public-speed-v2-overall.svg)

| Implementation | Original 2,807 checks | Extra 1,024 safety checks | Speed relative to Python |
| --- | ---: | ---: | ---: |
| Python `re` | 2,807 / 2,807 | 1,024 / 1,024 | 1.000× |
| Our Rust engine | 2,807 / 2,807 | NOT MEASURED | 1.065× on public development examples |
| Our C engine | 2,807 / 2,807 | 787 / 1,024; 237 failures | NOT MEASURED |
| Our Zig engine | 1,717 / 2,807; 1,090 failures | NOT MEASURED | NOT MEASURED |

All three engines are independently built from scratch. Green indicates a real matching result; red indicates a real mismatch. Every engine faces exactly the same 2,807 checks. Failures and older results are preserved, never excluded.

Rust's 1.065× result is from 864 public development examples, not the final comparison. Its measured 95% interval is 1.049×–1.081×. It does not meet the 1.5× target. The final comparison remains closed until Zig also matches Python and all three engines pass the added memory-lifetime checks.

## Detailed compatibility

| Python behavior | Cases | Rust | C | Zig |
| --- | ---: | ---: | ---: | ---: |
| Python's original runnable public tests | 151 | 151 | 151 | 151 |
| General public behavior | 864 | 864 | 864 | 824 |
| Scanners and callbacks | 1,024 | 1,024 | 1,024 | 32 |
| Memory views and buffers | 768 | 768 | 768 | 710 |
| Total matching checks | 2,807 | 2,807 | 2,807 | 1,717 |
| Additional memory-lifetime safety, counted separately | 1,024 | NOT MEASURED | 787 | NOT MEASURED |

Python's genuine debug-only test is skipped equally and is not included in the denominator.

![Detailed public correctness: Python and the Rust engine match on all 864 public examples](docs/evidence/rust-public-correctness-v1.svg)

An additional, frozen 1,024-case memory-lifetime safety suite has a passing two-Python baseline. C matches 787 cases and fails 237; Rust and Zig are **NOT MEASURED**. These cases are counted separately and are never silently added to the 2,807 original checks.

## Detailed development speed

![Results for all 864 public examples: 183 clearly faster, 213 clearly slower, and 468 inconclusive](docs/evidence/rust-public-speed-v2-outcomes.svg)

![Rust development speed for each of the 36 measured operations, including operations that are slower than Python](docs/evidence/rust-public-speed-v2-operations.svg)

![Measured slowdowns greater than 20 percent: zero among all 864 public development examples](docs/evidence/rust-public-speed-v2-regressions.svg)

These development graphs include every measured result. On the 864 public examples, 183 are clearly faster, 213 are clearly slower, and 468 are inconclusive. No result is hidden. Final speed, native memory use, and timings for C and Zig are **NOT MEASURED**.

## Larger final comparison

The proposed final comparison contains 4,194,304 separately generated examples and 24 fairly ordered measurement rounds. It covers common Python operations, unusual patterns, strings, bytes, compilation, reuse, Python-to-native overhead, and memory.

The final examples will remain **NOT FROZEN**, **NOT GENERATED**, and **NOT OPENED** until three independently built candidates pass the same complete compatibility and ownership checks. Success requires at least a 1.5× overall speedup, statistically faster results on at least 60% of cases, and an explanation of every slowdown greater than 20%. There is **no winner**.

## Evidence and reproduction

- [Complete experiment log, raw results, rejected designs, and failure history](docs/EXPERIMENT-LOG.md).
- [Authenticated headline graph inputs](docs/evidence/candidate-correctness-overview-v2.inputs.json), [generated graph data](docs/evidence/candidate-correctness-overview-v2.json), and [graph generator](tools/render_candidate_correctness_overview_v2.py).
- [Frozen original Python compatibility tests](tools/independent_original_cpython_suite_v5.py) and [shared candidate behavior tests](tools/independent_public_contract_v3.py).
- [Independent from-scratch engine ownership checks](tools/independent_from_scratch_audit_v2.py).
- [Additional frozen memory-lifetime safety checks](tools/independent_managed_buffer_lifetime_v1.py), [complete baseline recorder](tools/record_independent_managed_buffer_lifetime_v1.py), [independent three-candidate recorder](tools/record_independent_managed_buffer_candidates_v1.py), [verified lossless baseline evidence](docs/evidence/managed-buffer-lifetime-baseline-v1.archive.json), and [safe report restoration](tools/restore_managed_buffer_lifetime_baseline_v1.py).
- [Reproducible, source-pinned Zig build controller](tools/reproduce_owned_zig_source_build_v4.py).
- [Proposed expanded final-comparison protocol](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md).
- [Original objective](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](AMENDMENTS.md).

Verify the frozen test and chart tools without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/independent_original_cpython_suite_v5.py --self-test
"$PY" -I -B tools/independent_public_contract_v3.py --self-test
"$PY" -I -B tools/record_independent_public_contract_v3.py --self-test
"$PY" -I -B tools/independent_from_scratch_audit_v2.py --self-test
"$PY" -I -B tools/independent_managed_buffer_lifetime_v1.py --self-test
"$PY" -I -B tools/record_independent_managed_buffer_lifetime_v1.py --self-test
"$PY" -I -B tools/record_independent_managed_buffer_candidates_v1.py --self-test
"$PY" -I -B tools/restore_managed_buffer_lifetime_baseline_v1.py --self-test
"$PY" -I -B tools/reproduce_owned_zig_source_build_v4.py --self-test
"$PY" -I -B tools/render_candidate_correctness_overview_v2.py --self-test
```
