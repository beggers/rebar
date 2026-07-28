# rebar: a faster Python `re` experiment

Build a faster, fully compatible replacement for Python 3.14.6's
regular-expression module:

```python
import rebar as re
```

Every candidate must use its own matching engine built from scratch. Wrapping
Python, another regular-expression package, or another candidate does not count.

## Headline results

The Python baseline covers **31,237** frozen compatibility checks. None of the
Rust, C, or Zig engines is yet a fully compatible replacement: extra scanner
tests find **116** failures for Rust and C and **1,364** for Zig. Current
candidate speed is **NOT MEASURED**. The final comparison is **NOT OPENED**.

![Previously recorded starting checks: Python and the independently built Rust, C, and Zig engines each pass 2,807 out of 2,807; full compatibility remains unmeasured](docs/evidence/candidate-correctness-overview-v2.svg)

![Expanded replacement checks: Python passes all 5,120 checks; Rust, C, and Zig have not yet been measured](docs/evidence/substitution-buffer-overview-v2.svg)

![Additional scanner checks: Python passes all 2,854; Rust and C each fail 116; Zig fails 1,364](docs/evidence/scanner-verbose-overview-v1.svg)

![Additional memory-safety checks: Python, Rust, C, and Zig all pass all 1,024 checks](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

| Engine | Built from scratch | Starting checks | Memory safety | Extra scanner checks | Full compatibility | Current speed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Python `re` | Baseline | 2,807 / 2,807 | 1,024 / 1,024 | 2,854 / 2,854 | 31,237 / 31,237 | 1.000× baseline |
| Rust | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| C | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| Zig | PASS | 2,807 / 2,807 | 1,024 / 1,024 | 1,490 / 2,854 | NOT MEASURED | NOT MEASURED |

The starting and memory-safety results are earlier development measurements;
they do not mean any engine passes all **31,237** checks. Every scanner
failure is included. Python's baseline is not a timing result.

## Detailed compatibility

| Python behavior | Cases | Rust | C | Zig |
| --- | ---: | ---: | ---: | ---: |
| Python's original runnable public tests | 151 | 151 | 151 | 151 |
| General public behavior | 864 | 864 | 864 | 864 |
| Scanners and callbacks | 1,024 | 1,024 | 1,024 | 1,024 |
| Memory views and buffers | 768 | 768 | 768 | 768 |
| Total matching checks | 2,807 | 2,807 | 2,807 | 2,807 |
| Additional memory-lifetime safety, counted separately | 1,024 | 1,024 | 1,024 | 1,024 |
| Additional scanner and pattern-comment checks, counted separately | 2,854 | 2,738; 116 failures | 2,738; 116 failures | 1,490; 1,364 failures |
| Additional public types, copying, and serialization | 6,912 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Corrected replacement and buffer checks; original test preserved | 5,120 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Corrected changing-size buffer checks; original test preserved | 10,240 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Broad public behavior and real locales | 1,376 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Python buffer exporters and retained scanners | 264 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Simultaneous isolated Python interpreters | 128 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Patterns shared across simultaneous Python threads | 512 | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Full frozen compatibility gate | 31,237 | NOT MEASURED | NOT MEASURED | NOT MEASURED |

Python's genuine debug-only test is skipped equally and is not included in the denominator.

![Detailed public correctness: Python and the Rust engine match on all 864 public examples](docs/evidence/rust-public-correctness-v1.svg)

![Falsified historical changing-buffer report: its 1,888 recorded C differences include 496 test-harness errors](docs/evidence/shape-changing-buffer-overview-v1.svg)

This historical graph contains a known test-harness error; its red bar is
**NOT QUALIFIED**. Complete failures, corrections, and raw reports remain in
the [experiment log](docs/EXPERIMENT-LOG.md).

## Detailed development speed

![Historical speed before the latest compatibility repairs: Python at 1.000 times, old Rust at 1.065 times, and the 1.5-times target](docs/evidence/rust-public-speed-v2-overall.svg)

![Results for all 864 public examples: 183 clearly faster, 213 clearly slower, and 468 inconclusive](docs/evidence/rust-public-speed-v2-outcomes.svg)

![Rust development speed for each of the 36 measured operations, including operations that are slower than Python](docs/evidence/rust-public-speed-v2-operations.svg)

![Measured slowdowns greater than 20 percent: zero among all 864 public development examples](docs/evidence/rust-public-speed-v2-regressions.svg)

These graphs measure an earlier Rust development build, not a current
candidate. Among all **864** historical cases, **183** were faster, **213**
were slower, and **468** were inconclusive. Current speed and memory remain
**NOT MEASURED**.

## Final comparison

The proposed final comparison will use **4,194,304** unseen examples and
**24** balanced measurement rounds. It will cover ordinary and unusual
patterns, text and bytes, compilation, repeated use, native-code overhead,
and memory.

Those final examples are **NOT FROZEN**, **NOT GENERATED**, and
**NOT OPENED**. Three independently built candidates must first pass every
compatibility and ownership check. Success requires at least **1.5×**
overall speedup, statistically faster results on at least **60%** of cases,
and an explanation of every slowdown greater than **20%**. There is no winner.

## Evidence and reproduction

- [Complete 31,237-check compatibility standard](oracle/phase1/P0-COMPLETENESS-V1.md), [machine-readable test inventory](oracle/phase1/p0-completeness-v1.json), and [independent fail-closed verifier](tools/verify_p0_completeness_v1.py).
- [Accounting for all 165 original Python tests](oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md), [exact upstream manifest](oracle/cpython-3.14.6/manifest-v5.json), and [independent original-test verifier](tools/verify_original_cpython_accounting_v1.py).
- [Independent general, scanner, and buffer reference protocol](oracle/cpython-3.14.6/PUBLIC-CONTRACT-BASELINES-V1.md) and [Python-only reference recorder](tools/record_independent_public_contract_baselines_v1.py).
- [Real simultaneous-thread reference protocol](oracle/cpython-3.14.6/PUBLIC-THREADED-PATTERN-V1.md), [complete thread reference](oracle/cpython-3.14.6/evidence/public-threaded-pattern-v1-self-oracle.json.gz), and [original publication receipt](oracle/cpython-3.14.6/evidence/public-threaded-pattern-v1-self-oracle-publication-receipt.json).
- [Independent from-scratch and no-delegation audit](tools/independent_from_scratch_audit_v3.py).
- [Reproducible headline graph inputs](docs/evidence/candidate-correctness-overview-v2.inputs.json) and [headline graph generator](tools/render_candidate_correctness_overview_v2.py).
- [Complete experiment log, raw evidence, rejected approaches, and preserved failures](docs/EXPERIMENT-LOG.md).
- [Proposed expanded final comparison](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); the final cases remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](AMENDMENTS.md).

Run the source-only safety checks without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
"$PY" -I -B tools/record_independent_public_contract_baselines_v1.py --self-test
"$PY" -I -B tools/python_re_threaded_pattern_oracle_v1.py --self-test
"$PY" -I -B tools/render_candidate_correctness_overview_v2.py --self-test
```

The [complete compatibility standard](oracle/phase1/P0-COMPLETENESS-V1.md)
contains the source-pinned, read-only full-verification command.
