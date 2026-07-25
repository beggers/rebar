# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace
[Python 3.14.6's](https://www.python.org/downloads/release/python-3146/)
`re` and run faster? The intended interface is `import rebar as re`.
Every candidate must use its own matching engine, not Python's engine,
an external regular-expression package, or another candidate.

**Current public development result:** The from-scratch Rust engine matches
Python on **864 of 864** general examples and **1,024 of 1,024**
separately frozen scanner examples. It also passes all **151 runnable
tests from Python's original regex suite**, with the same single
debug-build-only skip as Python. All three comparisons have **zero**
mismatches; none is the unopened final speed test. A newly expanded
**768-case** buffer test exposes **53 additional edge-case
incompatibilities**, so Rust is not yet a universal drop-in. In a first
**864-case**, **12-round** development comparison, Rust is **1.058×**
as fast as Python overall. This does not meet the **1.5×** target. Final
speed and native memory are **NOT MEASURED**. Three independently
qualified candidates and a final winner remain **NOT ESTABLISHED**.

## Current speed against Python

![Current from-scratch Rust engine at 1.058 times Python's speed in the public development comparison, with the complete 95 percent confidence interval and the 1.5-times target](docs/evidence/rust-public-speed-v1-overall.svg)

Python is **1.000×**. Rust is **1.058×**, with a measured **1.042× to
1.075×** confidence interval. Of **864** examples, **185** are clearly
faster, **231** are clearly slower, and **448** are inconclusive.

![All 864 public examples classified as faster, slower, or inconclusive relative to Python](docs/evidence/rust-public-speed-v1-outcomes.svg)

This is a development measurement, not a hidden result or a prediction
about a final test. The [complete original measurements](experiments/rust_public_practice_v1/rust-native-scanner-v1-public-practice.json)
contain all **10,368** paired observations.

## Current compatibility

![Python and the current from-scratch Rust engine each passing all 864 frozen public development checks, with zero scanner failures](docs/evidence/rust-public-correctness-v1.svg)

The graph is generated from the
[complete recorded current result](experiments/rust_public_practice_v1/rust-module-v1-after-native-scanner.json),
its [independently verified receipt](experiments/rust_public_practice_v1/rust-module-v1-after-native-scanner-publication-receipt.json),
and the exact Rust source and native binaries. The
[separate 1,024-example scanner result](experiments/rust_public_practice_v1/rust-native-scanner-v1-independent-differential.json)
also passes every test. The original
[824-pass, 40-failure result](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner.json)
is preserved, not overwritten.

## Current speed by operation

![All 36 tested regular-expression operations compared directly with Python, including every observed speedup and slowdown](docs/evidence/rust-public-speed-v1-operations.svg)

![Every current Rust example more than 20 percent slower than Python](docs/evidence/rust-public-speed-v1-regressions.svg)

Exactly **two** examples exceed a **20%** slowdown. Both are
`match.expand` with mutable or read-only memory-view inputs. Their exact
inputs and confidence intervals are retained in the
[complete measurements](experiments/rust_public_practice_v1/rust-native-scanner-v1-public-practice.json).
The cause is visible in the engine: both valid memory-view inputs miss
the existing native replacement path and use a slower Python template
fallback. A separately reviewed
[768-case memory-view compatibility test](tools/rust_memoryview_expand_differential_v1.py)
first freezes Python's actual behavior for writable, read-only,
sliced, strided, released, and changed buffers. Its first Rust
comparison found **53** mismatches: **32** released views, **16**
failing buffer exporters, and **five** incorrect-template exceptions.
The [complete recorded failure](experiments/rust_public_practice_v1/rust-memoryview-expand-v1-before-native-fix.json)
and its [independently verified receipt](experiments/rust_public_practice_v1/rust-memoryview-expand-v1-before-native-fix-publication-receipt.json)
preserve every mismatch and all actual process output. The earlier
[truncated first-run summary](experiments/rust_public_practice_v1/rust-memoryview-expand-v1-first-unrecorded-summary.json)
is retained honestly. Correctness fixes, their resulting speed, and
native memory remain **NOT MEASURED**.

## Earlier three-engine speed comparison

The archived C, Rust, and Zig builds each ran the same 8,192 public examples
as unmodified Python. In these graphs, **1× is Python's speed, higher is
faster, and 1.5× is the target**.

![Overall speed of three archived engines compared with Python; these results do not measure the current builds](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-overall.svg)

| Archived engine | Speed compared with Python | Clearly faster examples | More than 20% slower |
| --- | ---: | ---: | ---: |
| Python baseline | 1.000× | — | — |
| Zig | 1.214× | 4,680 / 8,192 (57.1%) | 1,401 / 8,192 |
| C | 1.124× | 4,511 / 8,192 (55.1%) | 1,433 / 8,192 |
| Previous Rust | 0.957× | 2,444 / 8,192 (29.8%) | 3,106 / 8,192 |

No archived engine achieved both the 1.5× speed target and a clear speed
improvement on at least 60% of examples. These are historical results,
not measurements of the current engines.

![Faster, uncertain, and slower cases for every archived engine](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## More detail from the earlier comparison

![Archived speed results by regular-expression operation and kind of workload](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-api.svg)

![Every archived example running more than 20 percent slower than Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-regressions.svg)

![Temporary Python-visible memory used by the archived engines](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-memory.svg)

The memory graph shows temporary allocations visible to Python; memory
allocated privately by the native engines remains **NOT MEASURED**.

![Overall ranking of the archived engines; this is not a ranking of the current builds](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-rankings.svg)

The [published comparison](performance/postfinal-public-v6/RESULTS.md),
[preserved exact builds](performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md),
and [predeclared measurement rules](performance/postfinal-public-v6/PROTOCOL.md)
retain the complete results, uncertainty ranges, and all regressions.

## Original Python compatibility

Python's original test file contains **165** tests. **152** cover the
public replacement interface; **13** test private CPython internals and
are excluded only under the named `DebugTests` and `ImplementationTest`
waivers. Python and Rust both pass all **151** runnable public tests
and report the same genuine debug-build-only skip. The
[complete current original-test result](experiments/rust_public_practice_v1/rust-original-v3-native-scanner-first-run.json)
and its [independently verified receipt](experiments/rust_public_practice_v1/rust-original-v3-native-scanner-first-run-publication-receipt.json)
preserve both full test vectors, **zero** mismatches, all traceback
data, and the unchanged native engine.

The independently reviewed
[original-test controller](tools/rust_original_cpython_suite_v3.py)
performs **304** real matcher-ownership checks and **304**
warning-safety checks. It never delegates matching to Python. Earlier
test-environment and warning-guard failures remain unchanged in the
[experiment log](docs/EXPERIMENT-LOG.md). C and Zig have **NOT RUN**
against this complete original-test controller.

## Independent engines and compatibility

An independently reviewed
[from-scratch Rust audit](tools/rust_from_scratch_audit_v1.py) checks
the complete owned parser, compiler, matcher, Python binding, native
libraries, and **zero** external Rust dependencies. It rejects
Python's matcher, third-party regex packages, other candidates,
hidden fallbacks, and dynamic-loading escapes. Its first real
current-engine audit is **NOT RUN** until the audit source has been
committed and pushed.

Historical source and native-binary
[ownership check](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json)
and independent
[no-delegation check](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json)
verify that none uses Python's matcher, an external regex package, or another
candidate. Those checks do not establish full compatibility or speed.

The recorded correctness figures below predate the latest Rust changes.
They do not qualify a changed engine.

A [stricter next engine-independence check](oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V23.md)
has been frozen and independently verified before any engine changes.
Running that check against newly changed engines is **NOT RUN**.
A [matching correctness-proof protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V26.md)
has also been frozen. Fresh proofs for changed engines are **NOT RUN**.

| From-scratch engine | Initial correctness cases | Harder correctness cases | 152 original public-test records |
| --- | --- | --- | --- |
| Rust | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | [150 passes, 1 incompatibility, 1 debug skip](oracle/cpython-3.14.6/evidence/postfinal-locale-v16-rust-failures-production-summary.json) |
| C | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |
| Zig | [223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass-proof.json) | [393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |

An independently reviewed
[public development check](tools/rust_public_practice_benchmark_v1.py)
covers **864** fixed examples across **36** Python operations, equally
split between text and bytes. Two Python reference runs agree on all
**864**, and the
[current recorded Rust result](experiments/rust_public_practice_v1/rust-module-v1-after-native-scanner.json)
matches all **864**. The historical
[40 scanner failures](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner.json)
and [original durable receipt](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner-publication-receipt.json)
remain available. The separately
frozen [correctness graph generator](tools/render_rust_public_correctness_v1.py)
accepts only complete, independently authenticated recorded results; it
cannot invent a pass or measure speed.

A separately frozen [scanner compatibility check](tools/rust_scanner_differential_v1.py)
covers **1,024** new examples across **32** scanner features, including
text, bytes, callbacks, warnings, flags, captures, and changed inputs.
Two independent Python runs agree on all **1,024**, and the
[changed Rust scanner passes all 1,024](experiments/rust_public_practice_v1/rust-native-scanner-v1-independent-differential.json).
This is a public development check, not a final comparison.

The additional [1,376 public-interface checks](oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md),
[buffer-lifetime checks](oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V2.md),
and [128 interpreter-isolation checks](oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V1.md)
do not yet qualify the current engines. The original Rust pickling failure
and both actual Python references remain in the
[experiment log](docs/EXPERIMENT-LOG.md). C++ and Go are
[documented possibilities](experiments/FROM-SCRATCH-LANGUAGE-LANDSCAPE-V1.md),
not built or qualified candidates.

## Larger fair speed comparison

A previous final test was opened once, exposed a real Zig `split`
failure, and is **FALSIFIED**. It cannot be reused. The previously
proposed **1,048,576-example** replacement was never generated. The
[new independently reviewed proposal](docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md)
expands it fourfold to **4,194,304** separately generated, valid
examples covering every public operation, ordinary and unusual
patterns, text and byte inputs, native-call overhead, and lifecycles.

Freeze and generate a new final test only after three genuinely
separate, from-scratch candidates pass all original Python tests and
the independent no-delegation audit. Measure Python and each
qualifying candidate on the same cases in **24** fairly ordered
rounds. Report complete results, uncertainty, memory, and every
slowdown. Success requires at least **1.5×** overall and statistically
faster results on **2,516,583 of 4,194,304** cases.

The newly proposed final test is **NOT FROZEN**, **NOT GENERATED**,
and **NOT OPENED**. Final speed, confidence, rankings, and native
memory remain **NOT MEASURED**.

## Evidence and reproduction

The [experiment log](docs/EXPERIMENT-LOG.md) records the detailed
experiments, rejected designs, genuine failures, and their resolutions.
The original objective in [GOAL.md](GOAL.md) remains unchanged, with
SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
[AMENDMENTS.md](AMENDMENTS.md) records later clarifications separately.

Recheck the frozen current-engine audits, original public-test runner,
expanded public tests, and the exact generated headline chart without
benchmarking a candidate:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/postfinal_independent_engine_audit_v21.py --self-test
"$PY" -I -B tools/postfinal_independent_engine_audit_v23.py --self-test
"$PY" -I -B tools/postfinal_current_build_proofs_v24.py --self-test
"$PY" -I -B tools/postfinal_current_build_proofs_v26.py --self-test
"$PY" -I -B tools/postfinal_cpython_locale_oracle_v15.py --self-test
"$PY" -I -B tools/postfinal_cpython_locale_oracle_v16.py --self-test
"$PY" -I -B tools/python_re_public_surface_oracle_stage27.py --self-test
"$PY" -I -B tools/python_re_buffer_exporter_oracle_v1.py --self-test
"$PY" -I -B tools/python_re_buffer_exporter_oracle_v2.py --self-test
"$PY" -I -B tools/python_re_subinterpreter_oracle_v1.py --self-test
"$PY" -I -B tools/rust_public_practice_benchmark_v1.py --self-test
"$PY" -I -B tools/rust_from_scratch_audit_v1.py --self-test
"$PY" -I -B tools/rust_scanner_differential_v1.py --self-test
"$PY" -I -B tools/rust_memoryview_expand_differential_v1.py --self-test
"$PY" -I -B tools/record_rust_memoryview_expand_v1.py --self-test
"$PY" -I -B tools/rust_original_cpython_suite_v1.py --self-test
"$PY" -I -B tools/rust_original_cpython_suite_v2.py --self-test
"$PY" -I -B tools/rust_original_cpython_suite_v3.py --self-test
"$PY" -I -B tools/record_rust_original_cpython_v1.py --self-test
"$PY" -I -B tools/record_rust_original_cpython_v2.py --self-test
"$PY" -I -B tools/record_rust_original_cpython_v3.py --self-test
"$PY" -I -B tools/record_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_rust_public_speed_v1.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --check
```
