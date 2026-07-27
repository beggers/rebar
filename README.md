# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace
[Python 3.14.6's](https://www.python.org/downloads/release/python-3146/)
`re` and run faster? The intended interface is `import rebar as re`.
Every candidate must use its own matching engine, not Python's engine,
an external regular-expression package, or another candidate.

**Current status:** The independently built Rust engine passes all
**151 runnable original Python tests**, **864 general examples**,
**1,024 scanner examples**, and **768 difficult memory-view examples**,
with **zero mismatches**. The Python-only debug test is skipped equally
for Python and Rust. An independent source, native-binary, and runtime
audit confirms **zero external regex packages or engine delegation**.

On **864** equally weighted public examples, the corrected Rust build
is **1.065×** as fast as Python, with **zero** slowdowns exceeding
20%. This remains below the **1.5×** goal. Three fully qualified
candidates, native memory use, the four-million-example final
comparison, and a winner remain **NOT ESTABLISHED**.

| Implementation | Speed relative to Python | Status |
| --- | ---: | --- |
| Python `re` | **1.000×** | Baseline |
| Our Rust engine | **1.065×** | Public development tests pass; speed goal not met |
| Our C engine | **NOT MEASURED** | **150 / 151** original Python tests; one pickling incompatibility |
| Our Zig engine | **NOT MEASURED** | Blocked by an independently recorded test-harness initialization bug |

## Current speed against Python

![Overall speed comparison: Python at 1.000 times, our Rust engine at 1.065 times, the 1.5-times goal, and our C and Zig engines honestly marked not yet measured](docs/evidence/rust-public-speed-v2-overall.svg)

Python is **1.000×**. Rust is **1.065×**, with a measured **1.049× to
1.081×** confidence interval. Of **864** examples, **183** are clearly
faster, **213** are clearly slower, and **468** are inconclusive.
Neither the **1.5×** overall target nor the **60%** faster-case target
has been met.

![All 864 public examples and the 60-percent faster-case goal: 183 faster, 213 slower, and 468 inconclusive](docs/evidence/rust-public-speed-v2-outcomes.svg)

This is a development measurement, not a hidden result or a prediction
about a final test. The
[complete current measurements](experiments/rust_public_practice_v1/rust-memoryview-native-exporter-fix-public-practice.json)
contain all **10,368** paired observations, including checking overhead.
Every chart is reproduced from that complete, correctness-checked
result by the independently frozen
[plain-language comparison generator](tools/render_rust_public_speed_v2.py).
C and Zig are shown as **NOT MEASURED**, not as successes or failures.

## Current compatibility

![Python and the current from-scratch Rust engine both pass all 864 independently frozen general compatibility checks](docs/evidence/rust-public-correctness-v1.svg)

| Python behavior | Current Rust result | Complete evidence |
| --- | ---: | --- |
| Original runnable Python tests | **151 / 151** | [Shared original Python suite](experiments/rust_public_practice_v1/rust-original-v4-shared-suite-v1.json) |
| General public behavior | **864 / 864** | [Shared general comparison](experiments/rust_public_practice_v1/rust-public-contract-v2-shared-suite-v1.json) |
| Scanners and callbacks | **1,024 / 1,024** | [Scanner comparison](experiments/rust_public_practice_v1/rust-native-scanner-v1-after-native-memoryview-exporter-fix.json) |
| Memory views and buffer errors | **768 / 768** | [Memory-view comparison](experiments/rust_public_practice_v1/rust-memoryview-expand-v1-after-native-exporter-fix.json) |

## Current speed by operation

![Every one of the 36 tested operations, showing exactly when our Rust engine is faster or slower than Python](docs/evidence/rust-public-speed-v2-operations.svg)

![Slowdowns over 20 percent: zero out of all 864 measured examples, with no examples excluded](docs/evidence/rust-public-speed-v2-regressions.svg)

Across all **864** current measured examples, **zero** are more than
20% slower than Python. The two earlier memory-view regressions now
use the owned native engine, and all **768** buffer checks pass.
Every earlier slowdown, failure, and intermediate result remains in
the
[experiment log](docs/EXPERIMENT-LOG.md).

Python's original test file contains **165** tests: **152** cover the
public interface, while **13** explicitly named tests concern private
Python internals. Python and Rust both pass all **151** runnable
public tests and report the same genuine debug-only skip. The original
test checks matcher ownership **304** times and warning safety **304**
times. The independently frozen
[shared original Python test suite](tools/independent_original_cpython_suite_v4.py)
preserves all of those tests and protections unchanged for each
separate Rust, C, and Zig implementation. No C or Zig test result is
assumed before that implementation actually runs. A separately frozen
[complete original-test result recorder](tools/record_independent_original_cpython_v4.py)
preserves every real test failure and never substitutes an invented
result for a crashed engine. The current Rust engine now passes
**151 / 151** runnable tests under this exact shared suite, with
**zero** public waivers and the same genuine Python-only debug skip.
The C engine passes **150 / 151**; its remaining genuine failure is
Python-compatible pickling, which must be corrected before it can
qualify.
Zig's first attempt exposed a bug in the test harness: it blocked
Python's own standard `ctypes` initialization before any Zig test
could run. Its compatibility is therefore **NOT YET MEASURED**, not
a claimed test failure.

The separately frozen
[shared Python behavior tests](tools/independent_public_contract_v2.py)
make all three engines face the same **864** general cases, **1,024**
scanner cases, and **768** memory-view cases. Each category is run
and reported separately using the
[complete behavior-test recorder](tools/record_independent_public_contract_v2.py);
C and Zig have **NOT YET RUN**.

The independently reviewed
[Rust ownership audit](tools/rust_from_scratch_audit_v1.py) and its
[complete current result](experiments/rust_public_practice_v1/rust-from-scratch-audit-v1-memoryview-native-exporter-fix.json)
verify that the Rust parser, matcher, and Python binding are built
from scratch. A separately frozen
[three-engine ownership audit](tools/independent_from_scratch_audit_v2.py)
applies the same no-external-regex rule to the separately owned Rust,
C, and Zig matchers. Its source is tested; actual C and Zig results
and reproducible native builds are **NOT YET ESTABLISHED**. The
[complete ownership-audit recorder](tools/record_independent_from_scratch_audit_v2.py)
preserves every genuine failure and crash without claiming a native
build has been reproduced.
The actual shared ownership results for
[Rust](experiments/rust_public_practice_v1/rust-from-scratch-audit-v2-shared-suite-v1.json)
[C](experiments/rust_public_practice_v1/c-from-scratch-audit-v2-shared-suite-v1.json),
and [Zig](experiments/rust_public_practice_v1/zig-from-scratch-audit-v2-shared-suite-v1.json)
confirm **three genuinely independent, from-scratch engines**,
**zero** external regex packages, and **zero** Python or
cross-candidate matching. This proves ownership, not full Python
compatibility or C/Zig performance.
The [Zig build protocol](docs/ZIG-SOURCE-BUILD-V1.md) now pins and
verifies the official stable compiler; rebuilding the owned Zig
engine with the independently frozen
[source-build controller](tools/reproduce_owned_zig_source_build_v1.py)
has **NOT YET RUN**.

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

Recheck the relevant frozen test and chart tools without running a
candidate or opening the final comparison:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/rust_public_practice_benchmark_v1.py --self-test
"$PY" -I -B tools/rust_from_scratch_audit_v1.py --self-test
"$PY" -I -B tools/independent_from_scratch_audit_v2.py --self-test
"$PY" -I -B tools/record_independent_from_scratch_audit_v2.py --self-test
"$PY" -I -B tools/rust_scanner_differential_v1.py --self-test
"$PY" -I -B tools/rust_memoryview_expand_differential_v1.py --self-test
"$PY" -I -B tools/record_rust_memoryview_expand_v1.py --self-test
"$PY" -I -B tools/rust_original_cpython_suite_v3.py --self-test
"$PY" -I -B tools/independent_original_cpython_suite_v4.py --self-test
"$PY" -I -B tools/record_independent_original_cpython_v4.py --self-test
"$PY" -I -B tools/independent_public_contract_v2.py --self-test
"$PY" -I -B tools/record_independent_public_contract_v2.py --self-test
"$PY" -I -B tools/record_rust_original_cpython_v3.py --self-test
"$PY" -I -B tools/record_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_rust_public_speed_v1.py --self-test
"$PY" -I -B tools/render_rust_public_speed_v2.py --self-test
"$PY" -I -B tools/reproduce_owned_zig_source_build_v1.py --self-test
```
