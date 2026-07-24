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

Not yet. Every row below uses the same **223,198** original Python
behavior checks. Rust is the current single-engine run; C and Zig show
their most recent preserved complete runs.

| Engine built from scratch | Checks completed | Differences from Python | Complete upstream tests |
| --- | ---: | ---: | --- |
| [Rust](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v10-diagnostic-pass.json.gz) | 223,198 | 0 | NOT RUN |
| [C](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v7-first-failure.json.gz) | 223,198 | 33 | NOT RUN |
| [Zig](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v7-first-failure.json.gz) | 223,198 | 16 | NOT RUN |

Rust's original test results are complete, but the runner did not save
its separate before-and-after engine-ownership proof. Rust therefore
remains **NOT QUALIFIED** until both records are preserved together.
The C and Zig engines have also been rebuilt from their own source;
their updated behavior checks are **NOT RUN**.

The [complete upstream-test protocol](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V5.md)
requires all **152** original public Python tests, the genuine Python
test-support files, the full original test corpus, and real
multi-gigabyte inputs. There are no public-test waivers; the only
conditional skip is Python's own private-debug-build requirement.
[Python has passed the complete reference suite twice](oracle/cpython-3.14.6/evidence/postfinal-locale-v5-self-oracle.json):
each independent run records all **152** original tests, **151**
actual passes, and the one original debug-only skip. The candidate
upstream runs are **NOT RUN**.

The [expanded real-world compatibility contract](oracle/cpython-3.14.6/PUBLIC-SURFACE-V17.md)
adds **1,376** distinct cases across **43** categories. They cover
unusual flags, all serialization protocols, live byte buffers,
Unicode, genuine locale changes, callbacks, warnings, and complete
public Python objects. Its reference and candidate runs are **NOT RUN**.

Independent inspections cover the engines' **12** source files and
**five** native binaries. They check that each engine is
[implemented from its own source](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json)
and [does not secretly call Python or another regular-expression package](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V7.json).
These inspections prove independent implementation, not complete
compatibility. Deeper correctness checks remain **NOT RUN**.

The [first rebuilt Rust safety check](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v8-diagnostic-native-owner-failure.json.gz)
found a genuine bug in the safety checker itself: a deliberately
blocked engine was mistaken for a real import. The check stopped
before running Rust or claiming a compatibility pass.

The [first corrected Rust isolation check](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v9-diagnostic-native-owner-failure.json.gz)
found another real safety gap: an internal Python matcher was already
cached and could still be reached. The check correctly recorded a
failure before importing Rust or starting the behavior tests. Rust has
not been qualified, and no failure was hidden or waived.

The [cached-matcher-safe, from-scratch ownership protocol](candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md)
closes both safety gaps. It requires each C, Rust, and Zig engine to do
its own matching, blocks Python's cached internal matchers, checks
genuine Python pattern and match objects, and repeats all protections
after matching. Its actual three-engine audits are **NOT RUN**.

The [fresh-build correctness protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V10.md)
keeps every original Python behavior check, verifies that the actual
engine performs its own work, and preserves passing and failing
results separately. The rebuilt-engine comparisons are **NOT RUN**.

An [immutable-source verification launcher](oracle/cpython-3.14.6/POSTFINAL-PUBLISHED-PINS-V8.md)
checks real published evidence without changing any frozen audit or
silently substituting another engine.

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
  tools/postfinal_current_build_proofs_v10.py --self-test
"$PY" -I -B \
  tools/python_re_public_surface_oracle_stage17.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_published_pins_v8.py --self-test
```
