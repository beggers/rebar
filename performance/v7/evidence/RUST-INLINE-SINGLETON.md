# Rust practice experiment: remove a per-pattern allocation

This report uses only the frozen **624-case practice test**. The **24,576-case** final test has not been created, opened, or measured.

The previously verified Rust search filter built and allocated a 256-entry lookup table to find a single required character. The independently written Rust engine now keeps that one character inline in its compiled pattern and uses its existing safely bounded byte-search implementation. It still checks every necessary preceding character, honors matching flags, captures and search windows, and runs the original complete matcher whenever a match is possible. This change removes that per-pattern allocation; total native memory has **NOT BEEN MEASURED**.

| Practice result | Previous search filter | Inline required character |
| --- | ---: | ---: |
| Overall speed relative to Python | 1.1094× | 1.1209× |
| 95% confidence interval | 1.0666–1.1536× | 1.0773–1.1652× |
| Clearly faster cases | 246/624 | 265/624 |
| More than 20% slower | 142/624 | 143/624 |
| Match-object operations | 2.1401× | 2.2003× |
| Match-object slowdowns greater than 20% | 5/48 | 6/48 |
| Pattern compilation | 2.3963× | 2.4222× |
| Paired trials per case | 7 | 7 |
| Timing observations | 8,736 | 8,736 |
| Timing correctness checks | 26,208 | 26,208 |

Each experiment is independently paired against pinned Python 3.14.6; these are not paired measurements of the two Rust designs against each other. The new overall confidence interval is above **1×** on the practice cases only. It does not demonstrate the final **1.5×** requirement or a final-test result.

| Operation | Cases | Speed relative to Python | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Compile | 48 | 2.422× | 48 | 0 |
| Escape | 48 | 1.034× | 21 | 0 |
| Find all | 80 | 0.849× | 23 | 33 |
| Find iterator | 67 | 0.905× | 15 | 21 |
| Full match | 47 | 0.920× | 12 | 22 |
| Match | 48 | 0.874× | 0 | 13 |
| Match-object operations | 48 | 2.200× | 23 | 6 |
| Scanner | 48 | 0.885× | 3 | 16 |
| Search | 48 | 1.022× | 15 | 18 |
| Split | 47 | 1.166× | 31 | 11 |
| Replace | 48 | 1.239× | 39 | 3 |
| Replace and count | 47 | 1.153× | 35 | 0 |

The exact native engine passes the [complete 22-stage correctness campaign](../../../candidates/evidence/rust-v8-rust-inline-singleton-sealed-campaign.json), [30,800 additional search checks](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-focused-controls.json), [all 223,198 matching cases](../../../candidates/evidence/rust-v7-edge-oracle-rust-mandatory-prefix-inline-singleton.json.gz), [all 393 object cases](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-MANDATORY-PREFIX-INLINE-SINGLETON.json.gz), [all 479 tracing cases](../../../candidates/evidence/rust-v8-observability-rust-qualified-mandatory-prefix-inline-singleton.json.gz), and the [complete](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-replacement-adversarial.json.gz) [replacement suites](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-replacement-adversarial-deep.json.gz). The [direct comparison](../../../candidates/evidence/rust-v8-rust-mandatory-prefix-inline-singleton-direct-replacement-controls.json) retains all unrelated failures.

The [complete raw practice observations](rust-v7-calibration-inline-singleton-raw.jsonl.gz), [all 624 case results](rust-v7-calibration-inline-singleton-summary.json), and [39-control independent integrity audit](rust-v7-calibration-inline-singleton-integrity.json) are committed. The audit recalculates all **625** confidence intervals and verifies the exact source and loaded native engine. The [generated overall](rust-v7-calibration-overall.svg), [operation](rust-v7-calibration-api.svg), [win and loss](rust-v7-calibration-win-loss.svg), [slowdown](rust-v7-calibration-regressions.svg), and [Python-visible allocation](rust-v7-calibration-memory.svg) graphs retain every result from all eight designs.

Final performance: **NOT MEASURED**. Final test: **NOT ACCESSED**.
