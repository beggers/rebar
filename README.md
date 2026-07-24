# rebar: a faster Python `re` experiment

`rebar` asks whether a regular-expression engine written from scratch can
replace Python 3.14.6's `re` module and run faster. The intended interface
is `import rebar as re`. Its C, Rust, and Zig candidates have independent
matching engines. None wraps an external regular-expression package, calls
Python's matching engine, or delegates to another candidate.

All three currently installed candidates match Python in **1,179,648**
public correctness checks. The newly rebuilt Rust engine's speed is
**NOT MEASURED**. The independent final test is **NOT OPENED**.
**There is no proven winner.**

## Latest completed public comparison

All six charts show the same completed comparison of the
[archived C, Zig, and previous Rust engines](performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md).
They do **not** measure the newly rebuilt Rust engine. Those three engines
and unmodified Python 3.14.6 ran the same **8,192** public workloads. The
[predeclared comparison](performance/postfinal-public-v6/PROTOCOL.md)
records **425,984** paired observations, **1,277,952** exact-answer checks,
and **24,579** independently replayed confidence intervals. **1× means
Python's speed; higher is faster. The target is 1.5×.**

![Overall measured speed of the archived Rust, C, and Zig engines compared with Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-overall.svg)

| Engine | Public speed | 95% uncertainty range | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Python baseline | 1.000× | Baseline | — | — |
| Zig | 1.214× | 1.2023–1.2260× | 4,680/8,192 (57.1%) | 1,401/8,192 |
| C | 1.124× | 1.1140–1.1347× | 4,511/8,192 (55.1%) | 1,433/8,192 |
| Previous Rust | 0.957× | 0.9476–0.9673× | 2,444/8,192 (29.8%) | 3,106/8,192 |

**No candidate reaches 1.5× or is clearly faster on 60% of cases.
There is no winner.** The previous Rust engine is slower than Python and
was rejected. All **5,940** slowdowns of more than 20% remain visible in
the [independently verified full results](performance/postfinal-public-v6/RESULTS.md).

![Every faster, uncertain, and slower result from the completed three-engine comparison](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## Details of that comparison

![Measured speed across 12 regular-expression operations and 260 kinds of public workload](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-api.svg)

![All 5,940 measured cases where an archived engine is more than 20 percent slower than Python](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-regressions.svg)

![Python-visible temporary memory use across all 8,192 cases in the completed comparison](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-memory.svg)

The memory chart reports Python-visible temporary allocations. Separate
whole-process worker readings cannot identify allocations inside a native
engine; exact native memory remains **NOT MEASURED**.

![Overall measured speed ranking of the archived Zig, C, and previous Rust engines](performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-clear-rankings.svg)

The [earlier comparison and its original graphs](performance/postfinal-public-v5/RESULTS.md)
retain all **5,173** historical slowdowns. Its
[five original native libraries](performance/postfinal-public-v5/NATIVE-ARCHIVE-V1.md)
are preserved separately from the
[five native libraries used in the latest completed comparison](performance/postfinal-public-v6/NATIVE-ARCHIVE-V1.md).
Those two historical Rust engines and the newly rebuilt Rust engine are
different. Separate runs do not prove a paired change in Rust's speed.

## What the new Rust engine actually passes

The [new comparison against Python](candidates/evidence/python-re-universal-public-oracle-v5-all.json)
covers all three currently installed engines: **8,192** patterns,
**48** observations per pattern, and **1,179,648** total comparisons,
with **zero** mismatches. Fresh
[from-scratch](candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V3.json)
and
[independent-execution](candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V3.json)
audits verify the actual Rust source and binary alongside the unchanged
C and Zig engines.

The rebuilt Rust engine also passes **33** native tests, an independent
[223,198-check matching and parser test](candidates/evidence/rust-v7-edge-oracle-rust-postfinal-assertion-snapshot-v1.json.gz),
a
[393-check Python-object test](candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-ASSERTION-SNAPSHOT-V1.json.gz),
and a
[479-check callback, iterator, scanner, and buffer test](candidates/evidence/rust-v8-observability-rust-qualified-postfinal-assertion-snapshot-v1.json.gz).
The [accepted full compatibility campaign](candidates/evidence/rust-v8-rust-postfinal-assertion-snapshot-v2-sealed-campaign.json)
passes all **22** stages and **4,494,555** Unicode comparisons. Of
**146** named official Python `re` tests, **144** pass; the other **2**
are explicitly recorded locale-dependent skips. Correctness does not
establish speed: the new Rust engine's performance and exact native
memory remain **NOT MEASURED**.

## Final-test status

An earlier one-time final test found a real Zig `split` mismatch. Its
[failure report](performance/v9/evidence/FINAL-HOLDOUT-FAILURE.md)
remains unchanged; that test cannot be rerun. The separate
[65,536-case final test](performance/postfinal-fresh-holdout-v1/PROTOCOL.md)
is **NOT OPENED**. Its
[audited adapter](performance/postfinal-fresh-holdout-v1/ADAPTER-AUDIT.md)
was checked against the archived original engines, not the newly rebuilt
Rust engine. The one-use executor is **NOT YET INTEGRATED**. Final speed,
final memory, and a qualified winner remain **NOT MEASURED**.

The [experiment log](docs/EXPERIMENT-LOG.md) preserves earlier results,
rejected designs, actual failures, and their resolutions.

## Reproduce and inspect

The objective in [GOAL.md](GOAL.md) has immutable SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
[AMENDMENTS.md](AMENDMENTS.md) records later clarifications separately.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_from_scratch_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_no_delegation_audit_v3.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/python_re_universal_public_oracle_stage05.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/rust_v8_multi_candidate_campaign_postfinal_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -I -B -c \
  'import sys;sys.path.insert(0,".");from tools.postfinal_public_practice_v6 import main;main(["--self-test"])'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_charts_v6.py --self-test
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_presentation_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v2.py --self-test
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v2.py --verify
PYTHONDONTWRITEBYTECODE=1 "$PY" -I -B \
  tools/postfinal_public_native_archive_v1.py --verify

jq '{status, cases, observations_per_case, observations_per_candidate,
     total_comparisons, mismatches, completed_candidates}' \
  candidates/evidence/python-re-universal-public-oracle-v5-all.json

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
