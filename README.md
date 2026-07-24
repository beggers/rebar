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

**Current status: all three independently rebuilt Rust, C, and Zig engines
pass all 223,198 original and all 393 deeper compatibility cases without
calling Python's matcher or another regex engine. The complete Python
tests are still NOT RUN. Current speed and memory are NOT MEASURED.
There is no winner.** The
headline graphs below describe earlier, archived builds, not the engines
currently under test.

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

Not yet. The rebuilt Rust, C, and Zig engines all pass every original
and deeper compatibility case. All three must still pass the complete
Python compatibility tests.
[Zig's own native Python bridge](candidates/zig/py_bridge.c) has been
rebuilt to correct its genuine `Pattern` versus `re.Pattern` bug. The
current results are separately verified against the rebuilt engines.

| Engine built from scratch | Original cases | Deeper cases | Complete Python tests |
| --- | --- | --- | --- |
| Rust | [PASS: 223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v24-qualified-pass-proof.json) | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |
| C | [PASS: 223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v24-qualified-pass-proof.json) | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |
| Zig | [PASS: 223,198 / 223,198](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v24-qualified-pass-proof.json) | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V24-PASS-PROOF.json) | NOT RUN |

The [earlier Zig deeper-test failure](candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-CURRENT-BUILD-V12-INVALIDATED-AFTER-OWNER-FAILURE.json.gz)
remains preserved. The rebuilt bridge now passes the same frozen cases.

The [normalized rebuild inspection](oracle/cpython-3.14.6/POSTFINAL-INDEPENDENT-ENGINE-AUDIT-V21.md)
checks all **12** current engine source files and all **five** current
native binaries. Both the
[actual three-engine ownership check](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21.json)
and the separately executed
[strict no-delegation check](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21.json)
pass. Each C, Rust, and Zig engine performs genuine matching without
using Python's matcher, an external regex package, or another engine.
The [ownership receipt](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V21-PUBLICATION-RECEIPT.json)
and [strict receipt](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21-PUBLICATION-RECEIPT.json)
preserve the actual successful report writes. These checks establish
independence, not full Python compatibility or speed. All four earlier
inspection failures remain documented in the
[experiment log](docs/EXPERIMENT-LOG.md).
A [later duplicate invocation](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V21-DUPLICATE-PREFLIGHT-FAILURE.json)
was safely refused before any engine ran or evidence was changed.
The [first full-check integration](candidates/audits/POSTFINAL-CURRENT-BUILD-V22-READONLY-INTEGRATION-PREFLIGHT-FAILURE.json)
then rejected an authentic historical failure before starting any
engine. Its exact cause is preserved; it did not qualify any engine.

The [corrected full-check protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V24.md)
now [passes its read-only three-engine integration](candidates/audits/POSTFINAL-CURRENT-BUILD-V24-READONLY-INTEGRATION-PASS.json).
It verifies all five real failures, both independent ownership checks,
and every native source without running a candidate or opening the
holdout.

The corrected protocol requires all **223,198** original cases and
all **393** deeper cases to be repeated against each independently
inspected engine. Rust, C, and Zig each pass all **223,198** original
cases in **49** categories and all **393** deeper checks, including
**64** fixed-seed difficult cases, with zero mismatches.

The [frozen full upstream Python test protocol](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V12.md)
preserves Python's exact original test suite. Python itself has
[twice passed its complete reference tests](oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json).
Each run covers all **152** original public tests, including the genuine
multi-gigabyte cases. The only skipped test requires Python's own private
debug build. These complete tests have **NOT RUN** against the candidates.

The [frozen expanded compatibility tests](oracle/cpython-3.14.6/PUBLIC-SURFACE-V27.md)
preserve the [original Python reference](oracle/cpython-3.14.6/PUBLIC-SURFACE-V19.md)
and all **1,376** distinct examples in **43** categories, including
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

The current engine-isolation, full-correctness, and public-compatibility
designs can be checked without running a candidate or benchmark:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

"$PY" -I -B tools/postfinal_independent_engine_audit_v21.py --self-test
"$PY" -I -B tools/postfinal_current_build_proofs_v24.py --self-test
"$PY" -I -B tools/postfinal_cpython_locale_oracle_v12.py --self-test
"$PY" -I -B tools/python_re_public_surface_oracle_stage27.py --self-test
```
