# Frozen 4,096-case public performance protocol

## Status

**Frozen before timing. Performance, speed, uncertainty ranges, memory,
regressions, rankings, and any winner are NOT MEASURED.**

This is a new, post-final **public** development benchmark. The original
24,576-case hidden experiment has already failed, cannot be retried, and has
no winner. This protocol never opens its secret, reuses its hidden cases, or
presents a public result as a final holdout result.

The exact [public-case manifest](manifest.json) is SHA-256
`4b541eaa1602855aeb67655c8732635d4c951a61ca2fae37f395a1b080a78d1e`.
Its prospective [benchmark and independent verifier](../../tools/postfinal_public_practice_v1.py)
is SHA-256
`9c5a84ded6c7d62b4c5022098e3001559a44bdabdcd9fcf50572ced551dd345a`.
The candidate stopping point is commit
`7db20714b440512a0e141969585a181526960f85`.

## Baseline and independently built candidates

The baseline is the exact pinned CPython 3.14.6 executable. It is compared in
one shuffled, paired run against:

1. `candidates.rust_candidate`, including the complete post-final Rust proof.
2. `candidates.vm_candidate`, the independently written C engine.
3. `candidates.zig_candidate`, the independently written Zig engine.

The original [76-control from-scratch audit](../../candidates/audits/FROM-SCRATCH-AUDIT.json)
binds all four source families and five actual native libraries; its frozen
SHA-256 is
`7c6575ee8a4dd373ebf7d59ce853fac47985b592429b9120f7d545fd184f2048`.
All three candidates have separate **223,198-check** public matching proofs
and complete **22-stage** compatibility campaigns. No candidate may call
stdlib `re`, `_sre`, an external regex package, another candidate, a hidden
test, or a benchmark-detection mechanism.

## Frozen cases

The sole source is the already-frozen **10,312-case public calibration
archive**. It contains no held-out records or private seeds. **9,731** cases
meet the unchanged subject limit of **8,192** code points and result limit of
**128** items. The selection fixes **4,096** equal-weight cases from that
eligible public pool, covers all **260** available workload categories, and
retains every available input, result-density, API, and lifetime group.

| Public operation | Frozen cases |
| --- | ---: |
| Compile | 210 |
| Escape | 161 |
| Find all matches | 414 |
| Iterate matches | 414 |
| Full match | 358 |
| Match | 229 |
| Match-object behavior | 241 |
| Scanner | 413 |
| Search | 414 |
| Split | 414 |
| Replace | 414 |
| Replace and count | 414 |
| Total | 4,096 |

Coverage includes **3,616** text, **182** bytes, **169** bytearray, and
**129** memoryview cases; **282** cold, **3,414** compiled, and **400**
module-level pattern lifetimes; and no-result, single-result, few-result,
and many-result workloads. The selection seed is `2026072401`.

These inputs are public practice cases. Some may overlap earlier public
measurements. This is **not** a new hidden holdout and must never be described
as independently blinded final evidence.

## Fixed measurement and acceptance reporting

Each case receives **13 paired trials** for each of the **four** engines,
four untimed warmups, and up to **16 genuine regex operations** per timed
sample. Execution order is shuffled with seed `2026072402`. Every single
observation has three exact correctness gates: before timing, during the
allocation sample, and immediately after timing.

The complete denominator is **212,992 paired timing observations** and
**638,976 Python-answer checks**. Confidence ranges use **2,000** seeded
bootstrap draws with seed `2026072403`. The independent replay recomputes
all **12,291** case and overall confidence ranges.

Report all four engines, all 4,096 cases, every operation, every slowdown
greater than 20%, all failed correctness checks, raw and compressed hashes,
and Python-visible temporary allocations. Native-engine memory and isolated
whole-process memory remain **NOT MEASURED**. Record whether each engine
reaches **1.5×** and whether at least **2,458 of 4,096** cases are
statistically faster; do not change a denominator or select a candidate early.

## Reproduction and outputs

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v1 self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v1 freeze

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v1 measure \
  --exclusive-slot postfinal-public-practice-v1

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v1 verify
```

Measurement is permitted only after this exact prospective protocol,
manifest, source, candidate fingerprints, and original audit are committed
and pushed to `main`. It creates unique, non-overwriting compressed raw,
summary, and independent-integrity records in `evidence/`. Until that
measurement genuinely completes, every expanded performance result is
**NOT MEASURED**.
