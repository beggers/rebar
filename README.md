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

Not yet. Every row below is a current, guarded run of the same
**223,198** original Python behavior checks.

| Engine built from scratch | Checks completed | Differences from Python | Deeper checks | Complete Python tests |
| --- | ---: | ---: | --- | --- |
| [Rust](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v11-qualified-pass.json.gz) | 223,198 | 0 | [PASS: 393 / 393](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json) | NOT RUN |
| [C](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v11-qualified-pass.json.gz) | 223,198 | 0 | NOT RUN | NOT RUN |
| [Zig](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v11-qualified-pass.json.gz) | 223,198 | 0 | NOT RUN | NOT RUN |

The separate [Rust ownership proof](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v11-qualified-pass-proof.json),
[C ownership proof](candidates/evidence/rust-v7-edge-oracle-vm-postfinal-current-build-v11-qualified-pass-proof.json),
and [Zig ownership proof](candidates/evidence/rust-v7-edge-oracle-zig-postfinal-current-build-v11-qualified-pass-proof.json)
verify that each engine performed its own matching. All three
complete behavior results are bound to both independently passing
three-engine inspections. None substitutes for Python's full
upstream tests.

The [complete upstream-test protocol](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V6.md)
requires all **152** original public Python tests, the genuine Python
test-support files, the full original test corpus, and real
multi-gigabyte inputs. There are no public-test waivers; the only
conditional skip is Python's own private-debug-build requirement.
[Python has passed the current complete reference suite twice](oracle/cpython-3.14.6/evidence/postfinal-locale-v6-self-oracle.json):
each independent run records all **152** original tests, **151**
actual passes, the one original debug-only skip, both genuine
**2 GiB** input tests, and real fresh locales. The candidate
upstream runs are **NOT RUN**. The frozen runner verifies that each
candidate uses its own engine immediately before and after every
original Python test.

The [expanded real-world compatibility contract](oracle/cpython-3.14.6/PUBLIC-SURFACE-V18.md)
adds **1,376** distinct cases across **43** categories. They cover
unusual flags, all serialization protocols, live byte buffers,
Unicode, genuine locale changes, callbacks, warnings, and complete
public Python objects. Every future candidate observation must run
inside that candidate's actual guarded matching process. Its first
[real Python reference failed](oracle/cpython-3.14.6/evidence/public-surface-v18-self-oracle-failures.json)
because the frozen observation recorder rejected a valid nested
public export. No passing reference or candidate result exists.

The [three-engine ownership inspection](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V10.json)
and [separate strict anti-delegation inspection](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V10.json)
each independently check all **12** original source files and all
**five** native binaries. Every engine performed its own matching
with Python's internal matcher, external regular-expression packages,
and the other candidates blocked. Each inspection passed all **48**
genuine serialization checks. These inspections prove independent
implementation, not complete compatibility. The complete upstream
candidate tests remain **NOT RUN**.

The [first rebuilt Rust safety check](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v8-diagnostic-native-owner-failure.json.gz)
found a genuine bug in the safety checker itself: a deliberately
blocked engine was mistaken for a real import. The check stopped
before running Rust or claiming a compatibility pass.

The [first corrected Rust isolation check](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-current-build-v9-diagnostic-native-owner-failure.json.gz)
found another real safety gap: an internal Python matcher was already
cached and could still be reached. The check correctly recorded a
failure before importing Rust or starting the behavior tests. Rust has
since passed the corrected edge qualification; no earlier failure was
hidden or waived.

The [cached-matcher-safe, from-scratch ownership protocol](candidates/audits/POSTFINAL-NATIVE-OWNERSHIP-V10.md)
closes both safety gaps. It requires each C, Rust, and Zig engine to do
its own matching, blocks Python's cached internal matchers, checks
genuine Python pattern and match objects, and repeats all protections
after matching. The first actual three-engine ownership inspection
and the separate stricter anti-delegation inspection both pass.

The [durable fresh-build correctness protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V11.md)
saves both the complete original Python behavior results and a
separate proof that the actual engine performed its own matching.
Its stronger, three-engine-qualified Rust, C, and Zig comparisons
all pass with zero differences from Python.

The first deeper Rust run completed **393** checks with zero
reported behavior differences, but its parent process omitted
Python's mandatory `PYTHONDONTWRITEBYTECODE=1` setting. The required
after-run verification therefore failed. Both the
[complete invalidated original output](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V11-INVALIDATED-AFTER-OWNER-FAILURE.json.gz)
and [exact setup-failure evidence](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V11-PRODUCER-CRASH.json.gz)
are preserved. That first run remains **FAIL**. The separately
authenticated [corrected Rust retry](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-CURRENT-BUILD-V12-RETRY-PASS-PROOF.json)
passes all **393** checks and proves who actually ran it.

The [append-only deep-test recovery protocol](oracle/cpython-3.14.6/POSTFINAL-EDGE-REFRESH-V12.md)
preserves that original failure and verifies the required Python
environment before any engine is started. Rust passes the corrected
deep test; the C and Zig deep tests are **NOT RUN**.

The expanded public-API reference fails at case `surface16.00.14`:
its observation recorder mistakes a valid, deeply nested Python
export for a recursive object. The actual failed reference is
preserved, and the suite cannot certify any candidate.

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
  tools/postfinal_cpython_locale_oracle_v6.py --self-test
"$PY" -I -B \
  tools/postfinal_current_build_proofs_v11.py --self-test
"$PY" -I -B \
  tools/postfinal_current_build_proofs_v12.py --self-test
"$PY" -I -B \
  tools/python_re_public_surface_oracle_stage17.py --self-test
"$PY" -I -B \
  tools/python_re_public_surface_oracle_stage18.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_published_pins_v8.py --self-test
```
