# rebar: a faster Python `re` experiment

Can a regular-expression engine built from scratch replace Python 3.14.6's
`re` and run faster? The intended interface is `import rebar as re`. The
three competing engines are independently implemented in C, Rust, and Zig;
none may use Python's matching engine or wrap another regex package.

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

Python also lets programs use and serialize types such as
`re.Pattern[str]` and `re.Match[bytes]`. The
[frozen 128-case compatibility test](oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V11.md)
first confirmed the expected answers in
[two independent real Python processes](oracle/cpython-3.14.6/evidence/public-generic-alias-v11-self-oracle.json).
Its [preserved first Rust run](candidates/evidence/python-re-generic-alias-public-oracle-v11-rust-failures.json)
then exposed **16 genuine failures** in normal Python serialization. That
run stopped before testing C or Zig; the old failure has not been erased.

All three native engines now use their genuinely owned pattern and match
types, and their rebuilt match objects display their true native type.
Targeted checks pass **24 exact official-style representations** and
**48 ordinary Python serialization round trips** across C, Rust, and
Zig. These smoke checks are **not** a full official test or a fresh audit.

The [previous 128-case compatibility suite](oracle/cpython-3.14.6/PUBLIC-GENERIC-ALIASES-V12.md)
was frozen against the earlier genuinely audited native builds. Its
candidate-free design passes **86** independent safety checks and
retains the original 16 Rust failures. Its
[actual two-Python reference](oracle/cpython-3.14.6/evidence/public-generic-alias-v12-self-oracle.json)
passes all **128** cases and **256** independent observations.
The [actual three-engine comparison](candidates/evidence/python-re-generic-alias-public-oracle-v12-all.json)
passes **128/128** cases for those Rust, C, and Zig builds:
**384/384** matching answers and **zero** mismatches. Those results
predate the latest representation fixes and do not qualify the new
source files or native binaries.

The [new official Python test design](oracle/cpython-3.14.6/POSTFINAL-LOCALE-V2.md)
preserves all **146** selected upstream tests, the **403-pattern**
official corpus, and both genuine locale tests. It passes **113**
candidate-free safety checks. Its first real run is **FALSIFIED**:
Rust passes **145/146** tests and fails the genuine match-object
representation test. The run stops before testing C or Zig. The
[preserved actual failure](oracle/cpython-3.14.6/evidence/postfinal-locale-v2-rust-failures.json)
records what was actually observed without inventing missing results.

Earlier [official Python test results](oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json),
[22-stage engine campaigns](candidates/evidence/rust-v8-rust-postfinal-locale-v5-sealed-campaign.json),
[from-scratch audit](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json),
and [independent-execution audit](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json)
are real historical results for their exact earlier source files and native
builds. **They do not qualify the newly modified engines.** The
[earlier source audit](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V6.json)
and [earlier independent-execution audit](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V6.json)
remain valid evidence for their recorded, pre-fix binaries only.
The [fresh version-seven source audit](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V7.json)
now actually passes for all **12** corrected source files and
**five** native binaries. It verifies **48** real serialization
checks and all **six** exact official text-and-byte representation
reproductions; its candidate-free design passes **468** controls.
The [new independent-execution audit design](oracle/cpython-3.14.6/POSTFINAL-NO-DELEGATION-V7.md)
passes **131** further controls and retains **676** inherited
anti-delegation checks. Its actual audit and the complete official
rerun are **NOT RUN**. The earlier genuine Rust failure remains
preserved.

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

Candidate-free checks of the frozen compatibility test and the preserved
benchmark-design failure can be repeated with the pinned Python:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v7.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v7.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v6.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v6.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage12.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_oracle_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_cpython_locale_v2_failure.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage11.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_expansion_v10_failure.py --self-test
```
