# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace
[Python 3.14.6's](https://www.python.org/downloads/release/python-3146/)
`re` and run faster? The intended interface is `import rebar as re`.
Every candidate must use its own matching engine, not Python's engine,
an external regular-expression package, or another candidate.

**Last durably recorded public development result:** Rust matched Python on
**824 of 864** examples before the scanner fix. All **40** recorded
differences were scanner results or scanner callback errors;
[every failing example is preserved](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner.json).
The original missing pattern-pickling feature now passes Python's real
test for all **six** pickle formats. A fresh complete original-test run
and fresh independent engine proofs are **NOT RUN**. C and Zig have
**NOT RUN** the original tests. Current speed and memory are
**NOT MEASURED**. There is no winner.

## Last completed original Python tests

![Last completed original Python tests before the latest Rust compatibility fix: 150 passes, one historical pickling failure, one debug-only skip, and C and Zig not yet tested](docs/evidence/current-native-correctness-v6.svg)

Python's original test file contains **165** tests. **152** test the
public replacement interface; the other **13** test CPython's private
implementation and are explicitly excluded in two named classes:
`DebugTests` (**4**) and `ImplementationTest` (**9**). No public test is
waived. Both actual Python reference runs pass **151** public tests;
the remaining test genuinely requires a Python debug build.

In the last completed run, Rust passed **150** of the same **152**
public-test records, exposed the missing pickling hook, and skipped the
same debug-only test. The hook has since been fixed and checked against
all six pickle formats; the complete original suite has **not** yet been
rerun. The earlier **11** test-harness errors were resolved, not hidden.
C and Zig are **NOT RUN**. The graph is
[generated from complete, independently verified historical evidence](docs/evidence/current-native-correctness-v6.json).

## Headline results from the last completed comparison

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
improvement on at least 60% of examples. The numbers do not predict how the
current builds will perform.

![Faster, uncertain, and slower cases for every archived engine](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## More detail from that archived comparison

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

## Independent engines and compatibility

Each engine uses its own implementation. The frozen source and native-binary
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
**864**. The preserved pre-fix Rust
[result](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner.json)
and [receipt](experiments/rust_public_practice_v1/rust-module-v1-before-native-scanner-publication-receipt.json)
record all **824** matches and **40** scanner failures. The separately
frozen [correctness graph generator](tools/render_rust_public_correctness_v1.py)
accepts only complete, independently authenticated recorded results; it
cannot invent a pass or measure speed.

A separately frozen [scanner compatibility check](tools/rust_scanner_differential_v1.py)
covers **1,024** new examples across **32** scanner features, including
text, bytes, callbacks, warnings, flags, captures, and changed inputs.
Two independent Python runs agree on all **1,024**. The changed Rust
scanner has **NOT RUN** this test. This is a public development check,
not the unopened million-example comparison.

The additional [1,376 public-interface checks](oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md),
[buffer-lifetime checks](oracle/cpython-3.14.6/PUBLIC-BUFFER-EXPORTER-V2.md),
and [128 interpreter-isolation checks](oracle/cpython-3.14.6/PUBLIC-SUBINTERPRETER-V1.md)
do not yet qualify the current engines. The original Rust pickling failure
and both actual Python references remain in the
[experiment log](docs/EXPERIMENT-LOG.md). C++ and Go are
[documented possibilities](experiments/FROM-SCRATCH-LANGUAGE-LANDSCAPE-V1.md),
not built or qualified candidates.

## Larger fair speed comparison

The planned public comparison and separately generated final test will
each cover **1,048,576 examples**: eight times the previous
**131,072-example** plan. Both will balance everyday matching, searching,
splitting, replacements, Unicode, bytes, compilation, cached patterns,
iterators, callbacks, unusual inputs, memory, and the cost of calling each
native engine from Python. Only combinations that are genuinely valid for
the operation and input count toward the total.

Freeze and open the final test only after all three genuinely separate,
from-scratch engines pass every required correctness and independence
check. Run Python and each qualifying engine on exactly the same cases,
with at least **11** paired rounds; report overall speed, uncertainty,
memory, and every slowdown. To satisfy the 60% faster-case requirement,
an engine must be statistically faster on at least **629,146** final
examples. The expanded test is **NOT FROZEN** and **NOT OPENED**. Current
speed, memory, uncertainty, slowdowns, and rankings are **NOT MEASURED**.

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
"$PY" -I -B tools/rust_scanner_differential_v1.py --self-test
"$PY" -I -B tools/record_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_rust_public_correctness_v1.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --self-test
"$PY" -I -B tools/render_current_correctness_v6.py --check
```
