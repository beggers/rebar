# rebar: a faster Python `re` experiment

Build a faster, fully compatible replacement for Python 3.14.6's
regular-expression module:

```python
import rebar as re
```

Every candidate must use its own matching engine built from scratch. Wrapping
Python, another regular-expression package, or another candidate does not count.

## Headline results

The Python baseline covers **31,237** frozen compatibility checks. Independent
C, Rust, Zig, C++, and Go engines are being explored; none is yet a fully
qualified replacement. Earlier scanner tests found **116** failures for
previous Rust and C builds and **1,364** for an earlier Zig build. The
repaired C and Rust engines have now each produced **two fresh, matching
builds with no outside regex dependency**. Zig also compiled twice, but
its engine retained two build-directory-dependent bytes, so its
reproducibility check failed. A separately frozen deterministic Zig
retry has not yet run. No current binary has yet run the full
compatibility test. Current speed is
**NOT MEASURED**. The final comparison is **NOT OPENED**.

The first full-suite C attempt exposed a recovery-record verification
bug before any compatibility check ran. Its original binary was safely
restored; the failed attempt is preserved.

![Previously recorded starting checks: Python and the independently built Rust, C, and Zig engines each pass 2,807 out of 2,807; full compatibility remains unmeasured](docs/evidence/candidate-correctness-overview-v2.svg)

![Expanded replacement checks: Python passes all 5,120 checks; Rust, C, and Zig have not yet been measured](docs/evidence/substitution-buffer-overview-v2.svg)

![Historical scanner checks: Python passes all 2,854; earlier Rust and C builds each fail 116; an earlier Zig build fails 1,364](docs/evidence/scanner-verbose-overview-v1.svg)

![Additional memory-safety checks: Python, Rust, C, and Zig all pass all 1,024 checks](docs/evidence/managed-buffer-lifetime-overview-v1.svg)

| Engine | From scratch | Current build | Earlier starting checks | Earlier memory checks | Earlier scanner checks | Full compatibility | Speed vs Python |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Python `re` | Baseline | Baseline | 2,807 / 2,807 | 1,024 / 1,024 | 2,854 / 2,854 | 31,237 / 31,237 | 1.000× reference |
| Rust | PASS | Two matching builds | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| C | PASS | Two matching builds | 2,807 / 2,807 | 1,024 / 1,024 | 2,738 / 2,854 | NOT MEASURED | NOT MEASURED |
| Zig | PASS | Different build bytes | 2,807 / 2,807 | 1,024 / 1,024 | 1,490 / 2,854 | NOT MEASURED | NOT MEASURED |
| C++ | PASS | NOT BUILT | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| Go | PASS | NOT BUILT | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |

All starting, memory, and scanner numbers are earlier development
measurements, not results for the repaired C, Rust, or Zig engines. The
current C and Rust sources have each produced two matching, independently
verified builds with no external regex dependencies. Both current Zig
builds compiled without an external regex dependency, but their debug
data recorded different build paths. Its reproducibility gate therefore
**FAILED**. The Rust and Zig engines and bridges have now passed
both frozen ownership checks and strict compiler checks. The new C++ and Go engines have passed
source and compiler checks but have **NOT BEEN BUILT**. Go's Unicode
case handling and strict C portability have been corrected at source
level; its actual build, complete compatibility, memory, and speed are
still **NOT MEASURED**. No engine has passed all
**31,237** checks.
Python's baseline is not a timing result.

## Detailed compatibility

| Python behavior | Cases | Rust | C | Zig |
| --- | ---: | ---: | ---: | ---: |
| Python's original runnable public tests | 151 | 151 | 151 | 151 |
| General public behavior | 864 | 864 | 864 | 864 |
| Scanners and callbacks | 1,024 | 1,024 | 1,024 | 1,024 |
| Memory views and buffers | 768 | 768 | 768 | 768 |
| Total matching checks | 2,807 | 2,807 | 2,807 | 2,807 |
| Additional memory-lifetime safety, counted separately | 1,024 | 1,024 | 1,024 | 1,024 |
| Historical scanner and pattern-comment checks, counted separately | 2,854 | 2,738; 116 failures | 2,738; 116 failures | 1,490; 1,364 failures |
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
- [Final source-verified 31,237-check candidate protocol](oracle/phase2/P0-CANDIDATE-PROTOCOL-V3.md), [exact version-three candidate inventory](oracle/phase2/p0-candidate-protocol-v3.json), and [crash-verified full candidate runner](tools/run_frozen_p0_candidate_v3.py).
- [Preserved C full-gate preflight failure](oracle/phase2/evidence/frozen-p0-candidate-v3-c-phase2-v3-failures.json.gz) and [independently verified C preflight failure receipt](oracle/phase2/evidence/frozen-p0-candidate-v3-c-phase2-v3-failures-publication-receipt.json); zero compatibility cases ran.
- [Complete shared candidate correctness protocol](oracle/phase2/P0-CANDIDATE-PROTOCOL-V2.md), [exact version-two candidate inventory](oracle/phase2/p0-candidate-protocol-v2.json), and [full 31,237-check candidate runner](tools/run_frozen_p0_candidate_v2.py).
- [Shared 31,237-check candidate test](oracle/phase2/P0-CANDIDATE-PROTOCOL-V1.md), [frozen candidate test inventory](oracle/phase2/p0-candidate-protocol-v1.json), and [fail-closed candidate test runner](tools/run_frozen_p0_candidate_v1.py).
- [Crash-verified real-interpreter correctness protocol](oracle/phase2/CANDIDATE-SUBINTERPRETERS-V2.md), [corrected interpreter test inventory](oracle/phase2/candidate-subinterpreters-v2.json), and [corrected real-interpreter candidate runner](tools/run_owned_candidate_subinterpreters_v2.py).
- [Real isolated-interpreter compatibility protocol](oracle/phase2/CANDIDATE-SUBINTERPRETERS-V1.md), [exact interpreter test inventory](oracle/phase2/candidate-subinterpreters-v1.json), and [independently checked interpreter test runner](tools/run_owned_candidate_subinterpreters_v1.py).
- [Corrected C, Rust, and Zig source-build protocol](oracle/phase2/NATIVE-SOURCE-BUILDS-V2.md), [version-safe offline native-build verifier](tools/reproduce_phase2_native_builds_v2.py), and [preserved original build protocol](oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md).
- [Deterministic, failure-preserving version-three native-build protocol](oracle/phase2/NATIVE-SOURCE-BUILDS-V3.md) and [independently verified native build recorder](tools/reproduce_phase2_native_builds_v3.py); a corrected Zig rebuild has not yet run.
- [Crash-safe verified native activation protocol](oracle/phase2/VERIFIED-NATIVE-ACTIVATION-V1.md) and [reversible, source-authenticated native activation and recovery](tools/activate_verified_native_candidate_v1.py).
- [Complete preserved Zig reproducibility failure](oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures.json.gz) and [independently verified Zig failure receipt](oracle/phase2/evidence/native-source-build-v2-zig-phase2-v2-failures-publication-receipt.json).
- [Complete corrected Rust source-build record](oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2.json.gz) and [independently verified corrected Rust build receipt](oracle/phase2/evidence/native-source-build-v2-rust-phase2-v2-publication-receipt.json).
- [Complete corrected C source-build record](oracle/phase2/evidence/native-source-build-v2-c-phase2-v2.json.gz) and [independently verified corrected C build receipt](oracle/phase2/evidence/native-source-build-v2-c-phase2-v2-publication-receipt.json).
- [Both reproducible C source builds and complete process records](oracle/phase2/evidence/native-source-build-v1-c-phase2-v1.json.gz), with the [source-built C publication receipt](oracle/phase2/evidence/native-source-build-v1-c-phase2-v1-publication-receipt.json).
- [Accounting for all 165 original Python tests](oracle/cpython-3.14.6/UPSTREAM-ACCOUNTING-V5.md), [exact upstream manifest](oracle/cpython-3.14.6/manifest-v5.json), and [independent original-test verifier](tools/verify_original_cpython_accounting_v1.py).
- [Independent general, scanner, and buffer reference protocol](oracle/cpython-3.14.6/PUBLIC-CONTRACT-BASELINES-V1.md) and [Python-only reference recorder](tools/record_independent_public_contract_baselines_v1.py).
- [Real simultaneous-thread reference protocol](oracle/cpython-3.14.6/PUBLIC-THREADED-PATTERN-V1.md), [complete thread reference](oracle/cpython-3.14.6/evidence/public-threaded-pattern-v1-self-oracle.json.gz), and [original publication receipt](oracle/cpython-3.14.6/evidence/public-threaded-pattern-v1-self-oracle-publication-receipt.json).
- [From-scratch engine ownership and no-delegation protocol](oracle/phase2/CANDIDATE-INDEPENDENCE-V1.md) and [independently tested static ownership audit](tools/audit_candidate_independence_v1.py).
- [Dependency-free Rust matching engine](candidates/rust/src/lib.rs), [interpreter-safe Rust Python bridge](candidates/rust/py_bridge.c), [frozen Rust lockfile](candidates/rust/Cargo.lock), and [Rust-backed Python interface](candidates/rust_candidate.py); full compatibility is not yet measured.
- [Independently written Zig matching engine](candidates/zig/mini_regex.zig), [owned interpreter-safe Zig Python bridge](candidates/zig/py_bridge.c), and [experimental Zig-backed Python interface](candidates/zig_candidate.py); full compatibility is not yet measured.
- [Independently written C++ matching engine](candidates/cpp/engine.cpp), [native Python bridge](candidates/cpp/py_bridge.cpp), and [experimental Python interface](candidates/cpp_candidate.py); source checks only.
- [Independently written Go matching engine](candidates/go/engine.go), [strictly portable Unicode-aware Python bridge](candidates/go/py_bridge.c), and [experimental Python interface](candidates/go_candidate.py); source checks only, not an executed compatibility result.
- [Reproducible headline graph inputs](docs/evidence/candidate-correctness-overview-v2.inputs.json) and [headline graph generator](tools/render_candidate_correctness_overview_v2.py).
- [Complete experiment log, raw evidence, rejected approaches, and preserved failures](docs/EXPERIMENT-LOG.md).
- [Proposed expanded final comparison](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md); the final cases remain **NOT GENERATED** and **NOT OPENED**.
- [Original objective](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; [later clarifications](AMENDMENTS.md).

Run the source-only safety checks without opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/verify_p0_completeness_v1.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v1.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v2.py --self-test
"$PY" -I -B tools/run_frozen_p0_candidate_v3.py --self-test
"$PY" -I -B tools/run_owned_candidate_subinterpreters_v1.py --self-test
"$PY" -I -B tools/run_owned_candidate_subinterpreters_v2.py --self-test
"$PY" -I -B tools/reproduce_phase2_native_builds_v1.py --self-test
"$PY" -I -B tools/reproduce_phase2_native_builds_v2.py --self-test
"$PY" -I -B tools/reproduce_phase2_native_builds_v3.py --self-test
"$PY" -I -B tools/activate_verified_native_candidate_v1.py --self-test
"$PY" -I -B tools/audit_candidate_independence_v1.py --self-test
"$PY" -I -B tools/record_independent_public_contract_baselines_v1.py --self-test
"$PY" -I -B tools/python_re_threaded_pattern_oracle_v1.py --self-test
"$PY" -I -B tools/render_candidate_correctness_overview_v2.py --self-test
```

The [complete compatibility standard](oracle/phase1/P0-COMPLETENESS-V1.md)
contains the source-pinned, read-only full-verification command.
