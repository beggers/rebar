# Rust experiment: rule out impossible searches

This is a complete **624-case practice-only** experiment. The **24,576-case** final benchmark has not been created or opened.

Some slow practice operations search for patterns that cannot possibly match. The independently written Rust compiler can recognize when its own bytecode requires a run of matching characters immediately before one exact character. The matcher searches for that required character and checks every required preceding character using the existing Rust character-class and Unicode logic. It rejects a search only if **no** possible matching position exists. Any possible match runs through the original full matching engine with its existing captures, backtracking, flags, windows, errors, and object behavior.

This is general compiled-bytecode analysis, not a hard-coded pattern or answer. It is disabled for branches, assertions, optional prefixes, ambiguous character widths, wide Unicode, case-insensitive required characters, anchored matching, and unsupported search windows. The compiler does allocate one small search structure for an eligible pattern; native allocation is not claimed to be free or independently measured.

| Practice result | Previous direct native calls | Compiled-pattern search filter |
| --- | ---: | ---: |
| Overall speed relative to Python | 1.0257× | **1.1094×** |
| 95% confidence interval | 0.9916–1.0635× | **1.0666–1.1536×** |
| Clearly faster cases | 241/624 | **246/624** |
| More than 20% slower | 155/624 | **142/624** |
| Match-related operations | 0.6422× | **2.1401×** |
| Match-related slowdowns over 20% | 24/48 | **5/48** |
| Compilation speed relative to Python | 2.4118× | 2.3963× |
| Paired trials per case | 7 | 7 |
| Raw timing observations | 8,736 | 8,736 |
| Before-, during-, and after-timing correctness checks | 26,208 | 26,208 |

Both architectures are independently paired against pinned Python 3.14.6, not directly paired against each other. The new overall confidence interval is completely above **1×**, establishing a statistically supported improvement **on this practice cohort only**. It does not establish **1.5×**, the hidden-test speed, the final win-rate requirement, or candidate rankings.

| Operation | Cases | Speed relative to Python | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Compile | 48 | 2.396× | 48 | 0 |
| Escape | 48 | 1.008× | 3 | 0 |
| Find all | 80 | 0.854× | 22 | 37 |
| Find iterator | 67 | 0.902× | 16 | 25 |
| Full match | 47 | 0.925× | 16 | 20 |
| Match | 48 | 0.893× | 0 | 8 |
| Match-related operations | 48 | 2.140× | 23 | 5 |
| Scanner | 48 | 0.876× | 6 | 15 |
| Search | 48 | 1.003× | 15 | 17 |
| Split | 47 | 1.140× | 32 | 12 |
| Replace | 48 | 1.202× | 32 | 3 |
| Replace and count | 47 | 1.132× | 33 | 0 |

The new filter independently passes **30,800** targeted Python comparisons, including matches, misses, all required preceding characters, captures, repeated and optional patterns, scoped case rules, mutable buffers, Unicode, empty and inverted windows, later possible delimiters, and **384** seeded patterns. The entire frozen **22-stage** campaign passes, including all **4,494,555** Unicode checks, all **72,248** extended cases, all **223,198** matching cases, all **393** object cases, all **479** tracing cases, and both replacement suites. The **39,000-case** direct replacement control retains all **504** unrelated prototype failures. The independently refreshed all-engine audit rejects all **76** hidden-delegation and substituted-native-code controls.

- [All 30,800 targeted correctness comparisons](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-focused-controls.json).
- [Complete 22-stage correctness campaign](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-sealed-campaign.json).
- [Direct replacement controls and all preserved unrelated failures](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-direct-replacement-controls.json).
- [All standard replacements](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-replacement-adversarial.json.gz).
- [All deeper replacements](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-filter-replacement-adversarial-deep.json.gz).
- [All frozen matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-mandatory-prefix-filter.json.gz).
- [Native object and lifetime checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-MANDATORY-PREFIX-FILTER.json.gz).
- [Tracing, unusual arguments, and anti-delegation checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-mandatory-prefix-filter.json.gz).
- [Current four-engine native provenance audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json).
- [Complete raw practice timing](rust-v7-calibration-mandatory-prefix-filter-raw.jsonl.gz).
- [Every case, confidence interval, and slowdown](rust-v7-calibration-mandatory-prefix-filter-summary.json).
- [Independent 39-control timing and native-binary integrity audit](rust-v7-calibration-mandatory-prefix-filter-integrity.json).
- [Overall results for all seven recorded Rust designs](rust-v7-calibration-overall.svg).
- [Every operation and design](rust-v7-calibration-api.svg).
- [Every faster and slower practice case](rust-v7-calibration-win-loss.svg).
- [Every slowdown exceeding 20%](rust-v7-calibration-regressions.svg).
- [Temporary allocations visible to Python](rust-v7-calibration-memory.svg).

Final performance: **NOT MEASURED**. Final benchmark: **NOT ACCESSED**.
