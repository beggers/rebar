# Current Python regular-expression speed results

Status: **PASS. Independently verified public benchmark. No winner.**

The frozen [public protocol](PROTOCOL.md) compares unmodified Python
**3.14.6** with the current, independently implemented Rust, C, and Zig
engines. Its [exact manifest](manifest.json) was committed and pushed
before timing began. All **8,192** cases, all **12** operations, all
**260** workload categories, all **13** paired trials, and all **2,000**
confidence resamples are independently replayed.

This is a public development comparison. The **65,536**-case final test
remains **NOT OPENED**. There is no final winner or proven drop-in
replacement.

## Overall results

**1× means Python's speed; higher is faster.** A case is counted as
clearly faster only when its complete 95% confidence interval is above
**1×**. A slowdown means the candidate takes more than **20%** longer
than Python.

![Verified overall Python, Rust, C, and Zig speeds and confidence intervals](evidence/postfinal-public-practice-v6-clear-overall.svg)

| Public rank | Engine | Overall speed | 95% confidence interval | Clearly faster cases | More than 20% slower |
| ---: | --- | ---: | ---: | ---: | ---: |
| Baseline | Python | 1.000× | Baseline | — | — |
| 1 | Zig | 1.213742× | 1.202297–1.225950× | 4,680/8,192 (57.1%) | 1,401/8,192 |
| 2 | C | 1.124233× | 1.114016–1.134686× | 4,511/8,192 (55.1%) | 1,433/8,192 |
| 3 | Rust | 0.957154× | 0.947638–0.967306× | 2,444/8,192 (29.8%) | 3,106/8,192 |

**No candidate reaches the 1.5× overall target or the requirement to be
clearly faster on 60% of cases.** That case target requires at least
**4,916/8,192**. The first Rust matching-state optimization is correctly
implemented but slower than Python; its performance hypothesis is rejected.

![Every clearly faster, uncertain, and slower current candidate-case result](evidence/postfinal-public-practice-v6-clear-outcomes.svg)

## Every operation and every slowdown

Each candidate receives the complete case count in the second column.
The final column counts candidate–case observations, not distinct Python
inputs. All **5,940** recorded slowdowns are included.

| Python operation | Cases per engine | Rust slower | C slower | Zig slower | All slowdowns |
| --- | ---: | ---: | ---: | ---: | ---: |
| `compile` | 210 | 0 | 0 | 0 | 0 |
| `escape` | 161 | 0 | 0 | 1 | 1 |
| `findall` | 2,040 | 1,060 | 647 | 257 | 1,964 |
| `finditer` | 2,041 | 860 | 430 | 337 | 1,627 |
| `fullmatch` | 358 | 183 | 53 | 159 | 395 |
| `match` | 229 | 125 | 3 | 126 | 254 |
| Match-object access | 241 | 29 | 66 | 26 | 121 |
| `scanner` | 427 | 251 | 86 | 55 | 392 |
| `search` | 1,057 | 492 | 145 | 396 | 1,033 |
| `split` | 451 | 65 | 2 | 24 | 91 |
| `sub` | 447 | 36 | 0 | 16 | 52 |
| `subn` | 530 | 5 | 1 | 4 | 10 |
| **Total** | **8,192** | **3,106/8,192** | **1,433/8,192** | **1,401/8,192** | **5,940/24,576** |

![Every current-engine result across all 12 operations and 260 workloads](evidence/postfinal-public-practice-v6-clear-api.svg)

![All 5,940 individually identified slowdowns against Python](evidence/postfinal-public-practice-v6-clear-regressions.svg)

## Memory and complete accounting

![Python-visible temporary allocations and current worker memory limitations](evidence/postfinal-public-practice-v6-clear-memory.svg)

Python's `tracemalloc` reports **Python-visible temporary allocations
only**. Worker memory is a separate whole-process observation. Neither
measurement identifies exact native-engine allocations. Exact native
memory and final-test memory remain **NOT MEASURED**.

| Independently verified measurement | Recorded total |
| --- | ---: |
| Frozen public cases per engine | 8,192 |
| Python and independent engines | 4 |
| Paired trials per case | 13 |
| Original timing observations | 425,984 |
| Exact-answer correctness checks | 1,277,952 |
| Recomputed 95% confidence intervals | 24,579 |
| Continuously guarded workers | 4 |
| Worker and native-integrity checks | 65,544 |
| Frozen Python operations | 12 |
| Frozen workload categories | 260 |
| Individually preserved slowdowns | 5,940 |

![Current verified speed ranking for the independent Zig, C, and Rust engines](evidence/postfinal-public-practice-v6-clear-rankings.svg)

## Exact recorded evidence

| Frozen or independently verified input | SHA-256 |
| --- | --- |
| Frozen public manifest | `65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a` |
| Frozen public benchmark source | `16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3` |
| Complete measured summary | `539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c` |
| Independent complete replay | `8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2` |
| Compressed timing observations | `ec5783d5ad02c9bcfd1814d881e4f3de872d54929a16f352dd7baa6b0222fd6b` |
| Uncompressed timing observations | `d203ad1afd8209cd11ae3eccf83256ce6598b97794d58974e64b645944ed2dae` |
| Source-bound detailed graph renderer | `a8fb1924bebf4b3784e4b873b1c185d4690f98449c16ab127896c63979c2de90` |
| Independently verified clear graph renderer | `16f1689d91586917274ff057c75a1d1f15856e5345d848ed34ef2a676ad223f8` |

The [complete measured summary](evidence/postfinal-public-practice-v6-summary.json),
[independent replay](evidence/postfinal-public-practice-v6-integrity.json),
and [all original observations](evidence/postfinal-public-practice-v6-raw.jsonl.gz)
are preserved unchanged. Both fresh independence audits, all **12**
candidate compatibility proofs, and all **1,179,648** public Python
compatibility checks are bound to the exact Rust, C, and Zig sources and
five actual native libraries.

## Reproduce the clear graphs

The renderer authenticates all four exact fingerprints, the independently
replayed result, every candidate, and every slowdown before it generates
or verifies the six current graphs:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  tools/postfinal_public_practice_presentation_v2.py \
  --summary performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-summary.json \
  --summary-sha256 539fe6ba0ac492ffab121845da21033676ad7e7154ce9107f7f1778f55ceed4c \
  --integrity performance/postfinal-public-v6/evidence/postfinal-public-practice-v6-integrity.json \
  --integrity-sha256 8eb2e6bba6894a71f63e32cc35cca5317bb1beccc32c2905bbeacebedb868fd2 \
  --manifest performance/postfinal-public-v6/manifest.json \
  --manifest-sha256 65e024a1a79d13b03e4e5ad0f3d4ae010dbb6e4f09b52a8542837a2ea4c6198a \
  --runner-sha256 16a56d1573526894733b6284204ff3712b4d4e2a9c63027d51b8de1869df3fc3 \
  --output-dir performance/postfinal-public-v6/evidence
```

The [original archived-engine comparison](../postfinal-public-v5/RESULTS.md)
remains unchanged. Its old Rust engine and this rebuilt Rust engine were
measured in separate runs; no statistically paired improvement or
regression between those runs is claimed.

The **65,536-case hidden final test remains NOT OPENED**. Final speed,
final confidence intervals, and native memory remain **NOT MEASURED**.
There is **no qualified final winner**.
