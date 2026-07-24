# Results: 4,096-case public regex comparison

## Outcome

**No candidate reaches the 1.5× speed target.** This is a complete,
independently replayed **public** comparison, not the failed one-time hidden
final and not a final winner.

The [prospective protocol](PROTOCOL.md) and
[exact 4,096-case manifest](manifest.json) were committed and pushed at
`5a65274dc1f2e4190e16ee5c193d6379515666bd` before any timing. Python 3.14.6,
the independent C engine, the independent Zig engine, and the post-final Rust
engine ran the same public cases, all 260 workload categories, and all 12
regex operations.

![Complete public comparison of each independently written candidate against standard Python](evidence/postfinal-public-practice-v1-overall.svg)

| Engine | Speed compared with Python | 95% uncertainty range | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | `1.222×` | `1.205–1.238×` | `2,689/4,096` | `449/4,096` |
| Zig | `1.215×` | `1.196–1.236×` | `2,188/4,096` | `797/4,096` |
| Rust | `1.033×` | `1.017–1.048×` | `1,504/4,096` | `1,302/4,096` |

C is statistically faster on more than 60% of these public cases but does not
reach the required `1.5×` overall speed. Zig and Rust reach neither the
overall threshold nor the `2,458/4,096` clearly-faster-case threshold. None
repairs the original hidden Zig correctness failure.

## What was actually measured

- Exactly **4,096** predetermined public cases, with equal case weights.
- Exactly **13** paired trials per case and engine.
- Exactly **212,992** original raw timing observations.
- Exactly **638,976** matching checks against the pinned Python answer.
- Exactly **2,000** predetermined confidence resamples.
- Exactly **12,291** independently recomputed confidence intervals.
- Exactly **2,548** disclosed slowdowns greater than 20%.
- All **five** actual source-bound native libraries and all original
  no-delegation and compatibility proofs.

The benchmark did not access, generate, decode, reopen, or rerun any hidden
final test case. The original one-time final remains **FALSIFIED**, with no
final speed, final confidence range, final memory result, or final winner.

## Every substantial slowdown

| Operation | C | Zig | Rust |
| --- | ---: | ---: | ---: |
| Compile | 0 | 0 | 0 |
| Escape | 0 | 0 | 0 |
| Find all matches | 150 | 91 | 211 |
| Iterate matches | 75 | 124 | 129 |
| Full match | 64 | 162 | 217 |
| Match | 0 | 154 | 181 |
| Match-object behavior | 7 | 11 | 37 |
| Scanner | 72 | 59 | 158 |
| Search | 80 | 164 | 201 |
| Split | 0 | 16 | 120 |
| Replace | 1 | 15 | 47 |
| Replace and count | 0 | 1 | 1 |
| Total | **449** | **797** | **1,302** |

The [complete regression graph](evidence/postfinal-public-practice-v1-regressions.svg)
individually names **all 2,548** measured losses. The Rust `split` architecture
still loses by more than 20% in `120/414` split cases; the `findall`, search,
and matching methods account for most of its other regressions. Exact
per-regression profiling and native-engine memory are **NOT MEASURED** and
are not guessed.

## Complete source-bound evidence

- [The exact prospectively frozen case manifest](manifest.json), SHA-256
  `4b541eaa1602855aeb67655c8732635d4c951a61ca2fae37f395a1b080a78d1e`.
- [All original compressed observations](evidence/postfinal-public-practice-v1-raw.jsonl.gz),
  SHA-256 `66f2fb699085c0fc8436554a2aca28794f4e3411f91ddf3f332cc194400e676f`.
- [The complete measured summary](evidence/postfinal-public-practice-v1-summary.json),
  SHA-256 `2f478bd2bbca7af5c635d9d40ba8ffa41a13f7a0ab92b2ab09d1bf3d2eed32a8`.
- [The independent, candidate-free replay](evidence/postfinal-public-practice-v1-integrity.json),
  SHA-256 `794466f52191cbce4c914e8e8c1e39eb61e3312954ade07982175844c70bdd8b`.
- [All wins and losses](evidence/postfinal-public-practice-v1-outcomes.svg),
  [all operations and workload categories](evidence/postfinal-public-practice-v1-api.svg),
  [all substantial slowdowns](evidence/postfinal-public-practice-v1-regressions.svg),
  [Python-visible allocation only](evidence/postfinal-public-practice-v1-memory.svg),
  and [public performance ordering](evidence/postfinal-public-practice-v1-rankings.svg).

Python-traced allocations are not native-engine allocations or isolated
whole-process memory. Both remain **NOT MEASURED**.
