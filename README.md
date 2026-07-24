# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace Python 3.14.6's
`re` and run faster? The intended interface is `import rebar as re`. The
three competing engines are independently implemented in C, Rust, and Zig;
none may use Python's matching engine or wrap another regex package.

The [official stable Zig compiler](toolchains/zig-0.16.0.lock.json) is
independently pinned and verified so the Zig engine can be rebuilt
directly from its own source.

A [from-scratch language and Python-boundary inventory](experiments/FROM-SCRATCH-LANGUAGE-LANDSCAPE-V1.md)
records the three C, Rust, and Zig implementations, separately written
[C++](experiments/cpp_from_scratch_v1/STATIC-GAPS-V1.md) and
[Go](experiments/go_from_scratch_v1/STATIC-GAPS-V1.md) designs, and the
compilers actually available. C++ and Go are **NOT BUILT, NOT RUN,
and NOT QUALIFIED**. Bindings are not extra matching engines.

**Current status: no engine is yet proved to be a complete replacement. New
speed and memory results are NOT MEASURED. There is no winner.** The
headline graphs below describe earlier, archived builds, not the modified
engines currently under test.

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

## Are the current engines compatible with Python?

Not yet. [Zig's own native Python bridge](candidates/zig/py_bridge.c)
has been rebuilt to correct its genuine `Pattern` versus `re.Pattern`
bug. Changing a native binary invalidates the earlier three-engine
inspection. The earlier results below are preserved, but none proves
the rebuilt engines pass.

| Engine built from scratch | Earlier original checks | Earlier deeper checks | Fresh rebuilt-engine proof | Complete Python tests |
| --- | --- | --- | --- | --- |
| [Rust](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v11-qualified-pass.json.gz) | PASS: 223,198 / 223,198 | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json) | NOT RUN | NOT RUN |
| [C](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v11-qualified-pass.json.gz) | PASS: 223,198 / 223,198 | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json) | NOT RUN | NOT RUN |
| [Zig](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v11-qualified-pass.json.gz) | PASS: 223,198 / 223,198 | [FAIL: 26 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V12-INVALIDATED-AFTER-OWNER-FAILURE.json.gz) | NOT RUN | NOT RUN |

The [independent implementation inspection](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json)
and [separate no-delegation inspection](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json)
checked all **12** earlier engine source files and all **five** earlier
native binaries. They confirmed that those versions performed their own
matching without using Python's matcher, an external regex package, or
one another. They do not certify the changed native binary.

The [fresh rebuild-inspection protocol](oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V13.md)
requires both inspections to be repeated against the actual changed source
files and native binaries. These new inspections are **NOT RUN**.

The [fresh original correctness protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V14.md)
then requires all **223,198** original cases and all **393** deeper
cases to be repeated against each independently inspected engine.
These rebuilt-engine tests are **NOT RUN**.

Python itself has [twice passed its original complete reference tests](oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json).
Each run covers all **152** original public tests, including the genuine
multi-gigabyte cases. The only skipped test requires Python's own private
debug build. These complete tests have **NOT RUN** against the candidates.

The [expanded real-world compatibility tests](oracle/cpython-3.14.6/PUBLIC-SURFACE-V19.md)
preserve **1,376** distinct examples in **43** categories, including
Unicode, byte buffers, callbacks, warnings, serialization, unusual flags,
real system locales, and Python's complete public regex objects. The
[previous reference failure](oracle/cpython-3.14.6/evidence/public-surface-v18-self-oracle-failures.json)
is preserved. [Both corrected Python references now pass all 1,376 examples](oracle/cpython-3.14.6/evidence/public-surface-v19-self-oracle.json).
The expanded tests against the actual engines remain **NOT RUN**.
Changing an engine invalidates its earlier ownership and compatibility
proofs; those checks must be run again.

The [experiment log](docs/EXPERIMENT-LOG.md) contains the full failure
records, individual experiments, audits, reproduction commands, and
rejected designs.

## Larger fair speed comparison

A larger, **33,280-example** public comparison and a separate,
independently generated **33,280-example** final test are planned.
Neither has been frozen or used to measure the current engines. The
final test is **NOT OPENED**. Current speed, memory use, uncertainty,
slowdowns, and rankings are **NOT MEASURED**.

## Evidence and reproduction

The [experiment log](docs/EXPERIMENT-LOG.md) records the detailed
experiments, rejected designs, genuine failures, and their resolutions.
The original objective in [GOAL.md](GOAL.md) remains unchanged, with
SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
[AMENDMENTS.md](AMENDMENTS.md) records later clarifications separately.

The current source, isolation, upstream-test, and public-type designs can
be checked without running any candidates or benchmarks:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B \
  tools/postfinal_from_scratch_audit_v10.py --self-test
"$PY" -I -B \
  tools/postfinal_no_delegation_audit_v10.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v5.py --self-test
"$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v6.py --self-test
"$PY" -I -B \
  tools/postfinal_current_build_proofs_v11.py --self-test
"$PY" -I -B \
  tools/postfinal_current_build_proofs_v12.py --self-test
"$PY" -I -B \
  tools/python_re_public_surface_oracle_stage19.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_published_pins_v8.py --self-test
```
