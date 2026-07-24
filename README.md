# rebar: a faster Python `re` experiment

`rebar` asks whether an independently written regular-expression engine can
replace Python 3.14.6's `re` module and run faster. The intended interface is
`import rebar as re`. Its C, Rust, and Zig candidates have separate parsers,
compilers, and matching engines. None wraps another regex package, calls
Python's regex engine, or delegates matching to another candidate.

All three current engines match Python in **1,179,648** public correctness
checks. The first redesigned Rust engine is correct but slower than Python,
so its performance experiment is rejected. The independent final test
remains **NOT OPENED**. **There is no proven replacement or winner.**

## Overall public performance

All three current, independently implemented engines and unmodified Python
3.14.6 ran the same **8,192** public workloads. The
[predeclared comparison](performance/postfinal-public-v6/PROTOCOL.md)
records **425,984** paired observations, **1,277,952** exact-answer checks,
and **24,579** independently replayed confidence intervals. **1× means
Python's speed; higher is faster. The target is 1.5×.**

![Overall verified speed and confidence intervals for the current Rust, C, and Zig engines compared with Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-overall.svg)

| Engine | Public speed | 95% uncertainty range | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Python baseline | 1.000× | Baseline | — | — |
| Zig | 1.214× | 1.2023–1.2260× | 4,680/8,192 (57.1%) | 1,401/8,192 |
| C | 1.124× | 1.1140–1.1347× | 4,511/8,192 (55.1%) | 1,433/8,192 |
| Rust | 0.957× | 0.9476–0.9673× | 2,444/8,192 (29.8%) | 3,106/8,192 |

**No candidate reaches 1.5× or is clearly faster on 60% of cases.
There is no winner.** The first Rust optimization is correct but slower
than Python, so it is rejected. All **5,940** slowdowns of more than 20%
remain visible in the [independently verified current results](performance/postfinal-public-v6/RESULTS.md).

![Every measured faster, uncertain, and slower result for all three current regex engines](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## Detailed public results

![Verified performance across all 12 Python regular-expression operations and 260 workload categories](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-api.svg)

![All 5,940 individually verified cases where a current engine is more than 20 percent slower than Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-regressions.svg)

![Python-visible temporary allocations across all 8,192 current public cases](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-memory.svg)

The memory chart reports Python-visible temporary allocations. Separate
whole-process worker readings cannot identify allocations inside a native
engine; exact native memory remains **NOT MEASURED**.

![Verified overall speed rankings for the current independently implemented Zig, C, and Rust engines](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-rankings.svg)

The [earlier benchmark and original graphs](performance/postfinal-public-v5/RESULTS.md)
remain available with all **5,173** historical slowdowns. They measured
the [archived original engines](performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md),
not the newly modified Rust engine. Separate runs do not prove a
statistically paired change between old and new Rust.

## Final-test status

The original one-time hidden test found a genuine Zig `split` mismatch and
cannot be rerun. Its [unchanged failure report](performance/v9/evidence/FINAL-HOLDOUT-FAILURE.md)
remains part of the experiment. The separate, newly planned
[65,536-case final test](performance/postfinal-fresh-holdout-v1/PROTOCOL.md)
is **NOT OPENED**. The
[independently audited four-engine adapter](performance/postfinal-fresh-holdout-v1/ADAPTER-AUDIT.md)
passed **2,176** public cases and **26,112** separate checks with the
original, archived engines; it does not qualify the newly modified Rust
engine. The one-use final-test executor is **NOT YET INTEGRATED**. Final
speed, final memory, and a qualified winner remain **NOT MEASURED**.

## What is actually verified

The new [8,192-pattern Python comparison](candidates/evidence/python-re-universal-public-oracle-v4-all.json)
checks all three current engines against Python. The
[Rust optimization and full compatibility evidence](candidates/evidence/RUST-POSTFINAL-INLINE-STATE-V1.md)
record the exact modified source, native engine, unchanged Python bridge,
matching tests, Python-object behavior, callbacks, scanners, and complete
Unicode campaign. The Rust engine passes all **22** compatibility stages,
including **4,494,555** Unicode checks, **223,198** matching and parser
checks, **393** Python-object checks, and **479** callback, buffer, and
scanner checks.

The fresh [from-scratch audit](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V2.json)
and [isolated-engine audit](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V2.json)
confirm that the current engines do not use Python's regex engine, another
candidate, or an external regex package. Their exact control counts,
limitations, and source fingerprints are documented in the
[current requalification record](candidates/audits/POSTFINAL-REQUALIFICATION-V2.md).
A separately documented [next-engine safety plan](candidates/audits/POSTFINAL-REQUALIFICATION-V3.md)
requires fresh checks before any further Rust change; it does not claim
new measurements or final-test results.
The original source and isolation audits remain historical evidence.
The [five original benchmarked native libraries](performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
are independently preserved and verified. The
[experiment log](docs/EXPERIMENT-LOG.md) preserves
earlier measurements, rejected designs, and the unchanged
[interrupted Unicode-sensitive comparison](performance/postfinal-public-v4/RESULTS.md).

## Reproduce and inspect

The objective in [GOAL.md](GOAL.md) has immutable SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
[AMENDMENTS.md](AMENDMENTS.md) records later clarifications separately.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage04.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -I -B -c \
  'import sys;sys.path.insert(0,".");from tools.postfinal_public_practice_v6 import main;main(["--self-test"])'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_charts_v6.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_presentation_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v1.py --verify

jq '{result, cases_per_candidate, raw_rows, correctness_checks,
     confidence_intervals_recomputed, strict_regressions, rankings}' \
  performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-integrity.json

sha256sum \
  performance/postfinal-public-v6/manifest.json \
  tools/postfinal_public_practice_v6.py \
  performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-summary.json \
  performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-integrity.json \
  performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-raw.jsonl.gz
gzip -dc \
  performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-raw.jsonl.gz \
  | sha256sum
```
