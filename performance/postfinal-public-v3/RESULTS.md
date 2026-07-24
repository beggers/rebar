# Results: independently written Python regex engines

This is a completed, independently replayed **public development
experiment**, not a hidden final. The original one-time hidden test remains
failed. There is no qualified final winner.

## Overall performance

Pinned CPython **3.14.6** and three separately written C, Rust, and Zig engines
ran the same **4,096** public cases. Each case has **13** paired trials,
**2,000** fixed confidence resamples, and an exact Python-answer check before
performance is accepted. A speed of **1×** means equal to standard Python;
higher is faster.

![Overall speed compared with standard Python, with individually verified 95% confidence intervals](evidence/postfinal-public-practice-v3-overall.svg)

| Engine | Speed compared with Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Independently written C | 1.217× | 1.200–1.233× | 2,637/4,096 | 461/4,096 |
| Independently written Zig | 1.215× | 1.196–1.236× | 2,156/4,096 | 786/4,096 |
| Independently written Rust | 1.115× | 1.096–1.135× | 1,664/4,096 | 1,066/4,096 |

The prespecified speed requirement is **1.5×**, with at least **2,458 of
4,096** cases clearly faster. No engine reaches **1.5×**. Only C reaches the
faster-case threshold; it still fails the overall speed requirement. C's and
Zig's confidence intervals overlap, so their small observed difference does
not establish that either is consistently faster than the other.

## What was measured

- **260** workload categories and all **12** Python regex operations.
- **212,992** complete paired observations.
- **638,976** exact-answer checks; **zero failures**.
- **12,291** independently recomputed confidence intervals.
- **2,313** individually preserved substantial slowdowns.
- All three independent engines, all five identified native libraries, and
  the original audit's **76** recorded from-scratch controls.
- Python-visible temporary allocations only. Native-engine allocations and
  isolated whole-process memory are **NOT MEASURED**.

![Every faster, uncertain, and slower public result](evidence/postfinal-public-practice-v3-outcomes.svg)

## All substantial slowdowns

Every entry counts cases where that engine is more than **20% slower** than
the same pinned Python baseline. Zero entries are shown explicitly.

| Python operation | Cases per engine | C slowdowns | Zig slowdowns | Rust slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Compile a pattern | 210 | 0 | 0 | 0 |
| Escape special characters | 161 | 0 | 0 | 0 |
| Find all matches | 414 | 159 | 114 | 203 |
| Iterate over matches | 414 | 76 | 127 | 116 |
| Match the entire input | 358 | 64 | 162 | 184 |
| Match at the start | 229 | 0 | 138 | 133 |
| Inspect match objects | 241 | 10 | 7 | 13 |
| Scan successive matches | 413 | 71 | 61 | 156 |
| Search for a match | 414 | 80 | 156 | 169 |
| Split on a pattern | 414 | 0 | 4 | 55 |
| Replace matches | 414 | 1 | 16 | 37 |
| Replace and count matches | 414 | 0 | 1 | 0 |
| **Total** | **4,096** | **461** | **786** | **1,066** |

![All 12 Python regex operations and all 260 public workload categories](evidence/postfinal-public-practice-v3-api.svg)

![All 2,313 substantial slowdowns, without omitted cases](evidence/postfinal-public-practice-v3-regressions.svg)

## What changed in Rust

Rust keeps its own parser, compiler, bytecode, matching engine, and Python
binding. Its bridge now reads ordinary compiled-pattern metadata in one
guarded pass. It retains strong references, rolls back incomplete reads, and
keeps the original descriptor-aware fallback. Replacement still initializes
templates in the same observable order. Buffer ownership, Python errors,
custom attributes, callback behavior, and free-threaded safeguards remain
unchanged.

All **54** quote-aware splitting cases are clearly faster than Python,
averaging **11.81×**, with zero substantial slowdowns. This narrow result is
not an overall victory. In the separately measured previous public run Rust
was **1.100×**, with **1,116** substantial slowdowns. The current run is
**1.115×**, with **1,066**; these separate runs are not paired with each
other, so this comparison does not prove a causal or statistically
significant improvement.

The exact Rust source independently passes **223,198** edge checks, **393**
public-object checks, **479** observability checks, all **22** original
correctness stages, **4,494,555** Unicode comparisons, and **83,968**
additional quote-specific observations.

## Reproducibility and frozen evidence

The [prospective protocol](PROTOCOL.md), complete manifest, Rust source,
correctness evidence, and chart renderer were committed and pushed **before**
timing. Preserve the complete
[compressed paired observations](evidence/postfinal-public-practice-v3-raw.jsonl.gz),
[measurement and every slowdown](evidence/postfinal-public-practice-v3-summary.json),
and [independent candidate-free verification](evidence/postfinal-public-practice-v3-integrity.json).

| Frozen or independently verified file | SHA-256 |
| --- | --- |
| Manifest | `5f49f255271b8f71786e7fa67a61827b53c1330e1ad7afe29c8750991df4b90f` |
| Runner | `aa2b22de82894dc41622378d1bd782636358fa360454be37f3b8fedbc6e4989a` |
| Rust Python bridge | `bad5961266b4697f4c6fde8a0658319c85c9c97f2583de75718262fcc54b2f61` |
| Original independence audit | `d53d9dbfdd1d43284cefdbd189ff29ca181de9c49789da41ce11b5f138430999` |
| Additional quote oracle | `094d96305efbe59bf7f54bf772c97135103615e6de1ed0f68d2ece13ec34714f` |
| Compressed paired observations | `a36fa62a2ddcbbfb6e37ed14d340629f9f952348e5efacab255ae53ab7a253d3` |
| Measurement summary | `a5c5b3ad70c8fcb1df81da63ab30e727793e8a98c04c0889ca27ae9dce808bfc` |
| Independent replay | `52112057986f8a50cde14528c3fac9f22a688bd8f55bc418dc2a29f279e54ee4` |

![Python-visible temporary allocations; native and whole-process memory is not measured](evidence/postfinal-public-practice-v3-memory.svg)

![Public development ranking; not a final holdout result](evidence/postfinal-public-practice-v3-rankings.svg)

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v3 verify

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_charts_v3.py \
  --summary performance/postfinal-public-v3/evidence/postfinal-public-practice-v3-summary.json \
  --integrity performance/postfinal-public-v3/evidence/postfinal-public-practice-v3-integrity.json \
  --manifest performance/postfinal-public-v3/manifest.json \
  --output-dir performance/postfinal-public-v3/evidence
```

The historical consumed final remains **FALSIFIED**. Final speed, final
confidence intervals, final native memory, and a final winner are
**NOT MEASURED**.
