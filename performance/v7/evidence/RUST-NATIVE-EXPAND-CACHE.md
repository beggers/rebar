# Rust experiment: render match expansions natively

This is a complete **624-case practice-only** experiment. The **24,576-case** final benchmark has not been created or opened.

The Rust engine now expands ordinary match templates using its own existing native replacement cache and output writer. Subclasses, mixed text and bytes, unusual buffers, invalid templates, and mutable-subject lifetimes retain the original safe behavior. The same direct compatibility matrix exposed a previously untested Python error: unhashable replacement objects must raise their real hashing error. The owned native bridge now preserves that error rather than inventing a different one. Neither change imports or delegates to another regular-expression engine.

| Practice result | Previous checked Rust | Native expansion and correct replacement errors |
| --- | ---: | ---: |
| Overall speed relative to Python | 0.9290× | **0.9705×** |
| 95% confidence interval | 0.8931–0.9668× | 0.9376–1.0066× |
| Clearly faster cases | 211/624 | **212/624** |
| More than 20% slower | 243/624 | **230/624** |
| Match-object operation speed | 0.3451× | **0.6192×** |
| Match-object slowdowns over 20% | 48/48 | **31/48** |
| Paired trials per case | 7 | 7 |
| Raw timing observations | 8,736 | 8,736 |
| Before-, during-, and after-timing correctness checks | 26,208 | 26,208 |

Both designs were independently paired against pinned Python. They were not directly paired against one another. The new confidence interval crosses **1×**, so this is not reported as a statistically established speedup over Python or a final-benchmark result.

| Operation | Cases | Speed relative to Python | More than 20% slower |
| --- | ---: | ---: | ---: |
| Compile | 48 | 2.371× | 0 |
| Escape | 48 | 1.002× | 0 |
| Find all | 80 | 0.848× | 34 |
| Find iterator | 67 | 0.897× | 27 |
| Full match | 47 | 0.820× | 26 |
| Match | 48 | 0.732× | 47 |
| Match-object access | 48 | 0.619× | 31 |
| Scanner | 48 | 0.878× | 17 |
| Search | 48 | 0.914× | 32 |
| Split | 47 | 1.116× | 11 |
| Replace | 48 | 1.185× | 5 |
| Replace and count | 47 | 1.109× | 0 |

The expanded direct replacement comparison retains all **39,000** observations. Its first run records **480** actual Rust mismatches and **504** separate public-prototype mismatches. After the fix, Rust passes **13,000/13,000**; the **504** unrelated public-prototype failures remain visible. The optimized Rust engine separately passes all **8,862** standard replacements, all **11,266** deeper replacements, all **223,198** matching checks, all **393** public-object checks, all **479** tracing checks, and its complete **22-stage** frozen correctness campaign, including **4,494,555** Unicode comparisons.

- [Original complete 39,000-case failure record](../../../candidates/evidence/rust-v8-rust-native-expand-direct-replacement-controls-failures.json).
- [Complete repaired 39,000-case record, including all remaining non-Rust failures](../../../candidates/evidence/rust-v8-rust-native-expand-direct-replacement-controls-repaired.json).
- [Complete raw practice observations](rust-v7-calibration-native-expand-cache-raw.jsonl.gz).
- [Every practice case, slowdown, and confidence interval](rust-v7-calibration-native-expand-cache-summary.json).
- [Independent 39-control practice and native-library integrity audit](rust-v7-calibration-native-expand-cache-integrity.json).
- [Frozen 223,198-case Rust matching proof](../../../candidates/evidence/rust-v7-edge-oracle-rust-native-expand-cache.json.gz).
- [Frozen public-object proof](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-EXPAND-CACHE.json.gz).
- [Frozen tracing and native-argument proof](../../../candidates/evidence/rust-v8-observability-rust-qualified-native-expand-cache.json.gz).
- [Complete 22-stage Rust compatibility campaign](../../../candidates/evidence/rust-v8-rust-native-expand-cache-sealed-campaign.json).
- [Overall performance of all four recorded Rust architectures](rust-v7-calibration-overall.svg).
- [All operations and all recorded architectures](rust-v7-calibration-api.svg).
- [Every faster case and slowdown](rust-v7-calibration-win-loss.svg).
- [Every slowdown over 20%](rust-v7-calibration-regressions.svg).
- [Python-traced temporary allocations](rust-v7-calibration-memory.svg).

Final performance: **NOT MEASURED**. Final benchmark: **NOT ACCESSED**.
