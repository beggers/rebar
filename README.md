# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace Python 3.14.6's
`re` and run faster? The intended interface is `import rebar as re`. The
three competing engines are independently implemented in C, Rust, and Zig;
none may use Python's matching engine or wrap another regex package.

Separately written [C++](experiments/cpp_from_scratch_v1/PROTOCOL.md)
and [Go](experiments/go_from_scratch_v1/PROTOCOL.md) engines are
additional experiments. Both are **NOT BUILT, NOT RUN, and NOT
QUALIFIED**.

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

## What the current engines still need to prove

Python, Rust, C, and Zig have each independently passed the same
[146 selected upstream Python tests](oracle/cpython-3.14.6/evidence/postfinal-locale-v3-all.json),
including **403** original patterns and genuine locale tests. These
are **146 of Python's 152 public test methods**, and the earlier runner
used simplified Python test support. Its **584** saved results do not
prove that the complete, authentic upstream suite passes.

The [complete original 152-test protocol](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V4.md)
now freezes Python's actual test-support files, the full original test
corpus, and the real multi-gigabyte test requirements. It allows no
public-test waivers; the only conditional skip is Python's original
private-debug-build requirement. The complete upstream reference and
all three candidate runs are **NOT RUN**.

Two independent inspections verify that the three engines
[are built from their own source code](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json)
and [cannot secretly use Python or another regex engine](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json).
These checks cover all **12** implementation files and **five** native
binaries.

The [new 128-case public type and serialization test](oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V14.md)
[passes for all three current engines](candidates/evidence/python-re-generic-alias-public-oracle-v14-all.json):
**128/128** cases each, with zero mismatches. Its
[two independent Python reference runs](oracle/cpython-3.14.6/evidence/public-generic-alias-v14-self-oracle.json)
preserve all **256** Python results; the candidate evidence preserves
all **384** Rust, C, and Zig results. The
[original serialization failure](candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json)
and [original official-test failure](oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json)
remain available; older successful checks do not certify modified code.

The [next 3,584-case compatibility test](oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15.md)
covers public functions, errors, flags, locales, buffers, replacements,
scanners, Unicode, and concurrent matching. Its
[first Python-only run](oracle/cpython-3.14.6/evidence/public-contract-v15-self-oracle.json)
revealed a fault in the test itself: both Python processes returned the
same **7,168** results, but the recorded result hashes are incorrect.
Independent validation rejects the report, so this attempt is
**FALSIFIED**; Rust, C, and Zig were **NOT RUN**. The
[corrected 3,584-case test](oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17.md)
now has [7,168 independently verified Python reference results](oracle/cpython-3.14.6/evidence/public-contract-v17-self-oracle.json),
including Unicode checks on the exact saved bytes.
[All three current engines pass every case](candidates/evidence/python-re-universal-public-oracle-v17-all.json):
**3,584/3,584** each and **10,752/10,752** total, with zero
mismatches. Complete public-interface and caching tests remain
**NOT RUN**. A complete drop-in replacement is not yet proven.

The [separately frozen failure audit](oracle/cpython-3.14.6/PUBLIC-CONTRACT-V15-FAILURE.md)
distinguishes the stored-JSON hash from the original test's conflicting
Unicode-validation hash. Its
[independently verified failure record](oracle/cpython-3.14.6/evidence/public-contract-v15-reference-failures.json)
preserves both hashes and confirms no candidate was rerun.

The complete three-engine result is 20 MB because it keeps every
observation. A [strictly size-limited evidence reader](oracle/cpython-3.14.6/PUBLIC-CONTRACT-V17-EVIDENCE.md)
verifies the full result without weakening file-safety checks or
discarding data.

The [complete 22-stage compatibility campaign](oracle/cpython-3.14.6/POSTFINAL-CAMPAIGN-V7.md)
includes **4,494,555 Unicode comparisons per engine**. The
[first Rust attempt](candidates/evidence/rust-v8-rust-postfinal-locale-v7-sealed-campaign-first-failure.json)
correctly stopped before testing: its old proof belonged to an earlier
Rust build.

The [fresh current-build proof protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V7.md)
first requires **223,198** edge cases and **393** additional behavior
checks for each engine. It preserves complete failed and successful
results separately. The
[first complete Rust edge run](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v7-first-failure.json.gz)
found **16 Python-visible differences in 223,198 checks**. Its deeper
checks are **NOT RUN**. The
[first complete C edge run](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz)
found **33 differences in the same 223,198 checks**. Its deeper checks
and the Zig run are **NOT RUN**.

## Larger fair speed comparison

The previously frozen [8,192-example public comparison](performance/postfinal-public-v7/PROTOCOL.md)
has [published test inputs](performance/postfinal-public-v7/manifest.json),
but the current engines have **not** been timed against it. Two proposed
33,280-example expansions exposed real test-design mistakes; the
[first recorded failure](performance/postfinal-public-v8/evidence/postfinal-public-freeze-failure-v8.json)
and [second recorded failure](performance/postfinal-public-v10/evidence/postfinal-public-freeze-failure-v10.json)
remain available rather than being hidden or overwritten.

The corrected 33,280-example comparison is **NOT FROZEN**. Current
runtime, uncertainty, rankings, regressions, and memory use are
**NOT MEASURED**. The independent final test for the rebuilt engines is
**NOT OPENED**.

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

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v7.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v7.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage14.py --self-test
```
