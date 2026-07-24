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

All three native engines have now been changed so their pattern and match
types honestly belong to their own implementations. A targeted smoke check
confirmed **48 successful, ordinary Python serialization round trips**
across C, Rust, and Zig and all four tested pickle protocols, plus six
basic text-and-bytes matches. This smoke check is **not** a full
compatibility pass or an audit.

Earlier [official Python test results](oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json),
[22-stage engine campaigns](candidates/evidence/rust-v8-rust-postfinal-locale-v5-sealed-campaign.json),
[from-scratch audit](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json),
and [independent-execution audit](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json)
are real historical results for their exact earlier source files and native
builds. **They do not qualify the newly modified engines.** The new
from-scratch audit design passes **324 candidate-free safety checks**;
its actual audit is **NOT RUN**. Fresh no-delegation audits, the complete
official Python tests, and the expanded compatibility comparison must
also pass again for all three.

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
  tools/postfinal_from_scratch_audit_v6.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_generic_alias_public_oracle_stage11.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_expansion_v10_failure.py --self-test
```
