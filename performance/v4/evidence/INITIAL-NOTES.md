# Large performance holdout: plain-language notes

The first full run compares unmodified Python `re` with the three independently written engines on **1,224 holdout** and **1,224 practice** tasks. It keeps all **127,296** paired timing rows, checks the result before and after every timed batch, and uses the frozen weights and seeds. Raw SHA-256: `e2c320457eeeecec63efbcc80c3ab0a17b1e27332a45d34155fa9819ffd13f2b`.

## What the results say

| Engine | Holdout speed | Measured range | Clearly faster | Large holdout slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Native C / `rebar` | **1.561×** | **1.559–1.564×** | **1,130/1,224 (92%)** | **11** |
| Rust | 0.181× | 0.181–0.182× | 72/1,224 (6%) | 1,124 |
| Python | 0.033× | 0.033–0.033× | 36/1,224 (3%) | 1,157 |

Native C meets both experiment thresholds: at least **1.5×** overall and clearly faster on at least **60%** of tasks. Practice results are consistent at **1.527×** and **1,133/1,224** clearly faster. Rust and Python remain much slower on short and multi-result calls even after the earlier architecture-specific improvements; their complete losses and causes are retained in [INITIAL.md](INITIAL.md).

## Native slowdowns

All **11** large holdout slowdowns are the email-like `findall` variations: `hold.large.everyday-address.01`, `.04`, `.07`, `.10`, `.13`, `.16`, `.19`, `.22`, `.25`, `.28`, and `.31`. They run at **0.727–0.772×** of Python `re`. The matching practice cases are also slow; short practice-only window searches add 32 more losses. No case is removed from the denominator.

The [correctness-checked native profile](native-everyday-address-profile.json) explains the holdout loss. The email expression returns two to sixteen matches and uses several repeated character classes. Per call, the compact matcher performs **26–230 character-class checks**, **60–518 repeated-character checks**, and **20–160 execution steps** as result count grows. It creates **zero** general-backtracking states or clones. The remaining cost is repeated scanning and collection, not fallback, delegation, or unsafe behavior.

Every Python/Rust slowdown is also listed in the full report and grouped by its cause: Python execution/state and result creation dominate the Python engine, while repeated native-boundary/conversion and collection work dominate the Rust engine. Cold compilation, Unicode/category handling, callbacks, and multi-result APIs amplify these costs. Memory and every confidence range remain visible in the generated charts.

The complete, reproducible artifacts are [raw rows](initial-raw.jsonl), [summary](initial-summary.json), [all tasks and losses](INITIAL.md), [overall chart](initial-overall.svg), [family chart](initial-family-speed.svg), [all-case speed/confidence chart](initial-speed-cloud.svg), [memory chart](initial-memory-cloud.svg), [win/loss chart](initial-regressions.svg), and [rankings](initial-rankings.svg).
