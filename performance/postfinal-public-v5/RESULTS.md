# Unicode-safe 8,192-case public performance results

Status: **PASS — independently replayed public comparison. This is not a
final test, a held-out result, or a replacement winner.**

This comparison measures unmodified CPython 3.14.6 and the independently
implemented Rust, C, and Zig regular-expression engines against the exact
frozen [public protocol](PROTOCOL.md) and [manifest](manifest.json). The
complete [measured summary](evidence/postfinal-public-practice-v5-summary.json)
covers **8,192/8,192** frozen public cases, all **12/12** operations, and
all **260/260** frozen workload categories for **each** candidate. Each
Python and candidate operation has four warmups and 13 counterbalanced
paired trials; confidence intervals use 2,000 predeclared bootstrap draws.

## Overall public ranking

Speed is `CPython elapsed time / candidate elapsed time`: **1×** is parity
with Python; larger is faster. The uncertainty range is the recomputed
95% confidence interval. A clearly faster case means its own confidence
interval establishes a speedup. A slowdown is counted only when the
candidate takes **more than 20% longer** than Python.

| Public rank | Engine | Geometric-mean speed | 95% confidence interval | Clearly faster public cases | More than 20% slower public cases |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Zig | 1.217315052× | 1.205539606–1.229540228× | 4,689/8,192 | 1,375/8,192 |
| 2 | C | 1.135877114× | 1.126020701–1.146377316× | 4,709/8,192 | 1,282/8,192 |
| 3 | Rust | 1.010414785× | 1.000378209–1.020779414× | 2,866/8,192 | 2,516/8,192 |

**None reaches the 1.5× overall public target. None is clearly faster on
60% of public cases:** at least `ceil(0.60 × 8,192) = 4,916/8,192`
clearly faster cases are required, while Zig reaches 4,689, C reaches
4,709, and Rust reaches 2,866. The public ordering does not establish a
final winner.

## Every operation and slowdown

The case column is the frozen denominator **for each engine**, not a
combined denominator. Each slowdown cell is counted directly from the
genuine measured summary's individually recorded `regressions` and
cross-checked against its `case_results` and frozen `public_operations`.
The final column counts candidate–case observations across all three
engines; it does not claim that 5,173 distinct Python inputs are slow.

| Frozen Python operation | Public cases per engine | Rust >20% slower | C >20% slower | Zig >20% slower | All candidate slowdowns |
| --- | ---: | ---: | ---: | ---: | ---: |
| `compile` | 210 | 0 | 0 | 0 | 0 |
| `escape` | 161 | 1 | 0 | 10 | 11 |
| `findall` | 2,040 | 882 | 584 | 213 | 1,679 |
| `finditer` | 2,041 | 656 | 381 | 335 | 1,372 |
| `fullmatch` | 358 | 168 | 59 | 155 | 382 |
| `match` | 229 | 70 | 0 | 113 | 183 |
| `match-surface` | 241 | 26 | 14 | 20 | 60 |
| `scanner` | 427 | 141 | 68 | 52 | 261 |
| `search` | 1,057 | 475 | 170 | 440 | 1,085 |
| `split` | 451 | 64 | 5 | 16 | 85 |
| `sub` | 447 | 26 | 0 | 15 | 41 |
| `subn` | 530 | 7 | 1 | 6 | 14 |
| **Total** | **8,192** | **2,516/8,192** | **1,282/8,192** | **1,375/8,192** | **5,173/24,576** |

All three engines genuinely cover every one of the frozen **260**
categories and all **12** operations. Their individual category and case
records remain in the measured summary; no aggregate category result or
selectively chosen workload is invented here.

## Complete measured accounting

| Frozen measurement | Recorded total |
| --- | ---: |
| Public cases per engine | 8,192 |
| Python and candidate engines | 4 |
| Paired trials per module and case | 13 |
| Original timing observations | 425,984 |
| Before, allocation-sample, and after correctness checks | 1,277,952 |
| Candidate–case confidence intervals | 24,576 |
| Overall candidate confidence intervals | 3 |
| Total recomputed 95% confidence intervals | 24,579 |
| Frozen operations | 12 |
| Frozen categories covered by each candidate | 260 |
| Process-isolated, continuously guarded workers | 4 |
| Runtime worker and native-integrity guard checks | 65,544 |
| Individually reported candidate slowdowns exceeding 20% | 5,173 |

The accounting is `8,192 × 4 × 13 = 425,984` timing observations,
`425,984 × 3 = 1,277,952` exact-answer checks, and
`(8,192 × 3) + 3 = 24,579` confidence intervals. The paired controller
reports that it did not import a candidate. The manifest additionally
binds all **12** independent current-source correctness artifacts and the
all-engine Python oracle's **1,179,648** comparisons, with zero recorded
mismatches.

## Six public graphs

All six graphs are generated directly from the independently verified
original observations, frozen manifest, exact candidate rankings, and every
recorded slowdown. The original frozen graphs remain unchanged; this clearer
presentation independently verifies every input before producing additional
images.

![Public geometric-mean speed and 95% confidence intervals against CPython](evidence/postfinal-public-practice-v5-clear-overall.svg)

![Every faster, uncertain, and slower public candidate-case outcome](evidence/postfinal-public-practice-v5-clear-outcomes.svg)

![All 12 frozen public Python operations and workload coverage](evidence/postfinal-public-practice-v5-clear-api.svg)

![All 5,173 individually recorded public slowdowns exceeding 20 percent](evidence/postfinal-public-practice-v5-clear-regressions.svg)

![Python-visible traced temporary allocations and isolated-worker memory limitations](evidence/postfinal-public-practice-v5-clear-memory.svg)

![All three public candidate rankings and confidence intervals](evidence/postfinal-public-practice-v5-clear-rankings.svg)

`tracemalloc` measures **Python-visible temporary allocations only**.
Worker RSS and high-water marks are separate process-level observations;
neither establishes exact native-engine allocations or native per-case
memory. **Final memory is not measured.** A native binary's forced
full-content hash is taken before its first and after its last case;
intermediate checks authenticate mappings and exact file metadata, but
cannot cryptographically exclude a malicious change that preserves that
metadata between full hashes.

## Exact public provenance

The independent replay verifies every original timing observation, all
**24,579** confidence intervals, the compressed and uncompressed raw-stream
digests, candidate isolation, and all **5,173** reported slowdowns.

| Frozen or measured public input | SHA-256 |
| --- | --- |
| Frozen V5 public manifest | `c9950c87079ccc1909ba4470ed573b08afe1f275b85a8932cbfe83b547b24f96` |
| Complete measured V5 summary | `d9dd1e712a97d0d1716308e1e468e0c9d2b6d6058e501bccd871492bc66a6b4c` |
| Independently verified V5 replay | `ff86c9421747373df9f5cf640f8a081331661c7d79e8b12969cb0952c86d9246` |
| Verified uncompressed raw observations | `d788d79e14be1cf72b80f3c9de05aeea5615821421daf133a15be004971776a6` |
| Verified compressed raw observation stream | `283f2b33ad476a50fa9d70c7dd841982837a6f1d0fba892eb1b8242955392c40` |
| Frozen Unicode-safe V5 runner | `f4294a3b5434f43a92970635a958cf3b39db0eb926adef50e242ac0f6b9a1d22` |
| Source-bound six-chart V5 renderer | `7684cf5d3696ce97699406ae5b6451d47482ad707c1b74261972a1f2bfd39196` |
| Clear, independently validated presentation source | `53538d3a501388281b1603866f1336cb2ede067f2899a45b6c56c5a12d110842` |
| Preserved failed V4 public manifest | `15789a8ab6ab35ea97b657fed2ae4be0e944da6300067bc7cb3e8222c7c5ea55` |
| Preserved failed V4 partial timing stream | `4132e485b605f924fbc4edf09324987f09361f0562a9884fd0ceb06e09544f8a` |

The [failed V4 public comparison](../postfinal-public-v4/RESULTS.md)
remains failed: its original manifest, surrogate-transport failure, and
all **310,700** partial timing rows are preserved, never replaced, and
are explicitly fingerprinted by the V5 manifest. V5 changes the private
worker transport to ASCII-safe JSON; it does not turn V4's partial
observations into a complete result.

The [independent replay](evidence/postfinal-public-practice-v5-integrity.json)
passes all **425,984** raw observations, **1,277,952** correctness checks,
**24,579** recomputed confidence intervals, and all **5,173** slowdowns.
It reports zero failures, zero candidate imports, and no holdout access.

The separate **65,536-case final holdout remains NOT OPENED**. The
historical one-use hidden failure remains failed. Final speed, final
confidence intervals, final memory, and final rankings are **NOT
MEASURED**. There is **no final or drop-in replacement winner**.
