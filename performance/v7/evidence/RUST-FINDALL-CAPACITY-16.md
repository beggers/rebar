# Rust: a smaller buffer for finding all matches

This is a **public practice result**, not the final speed test. The Rust, C, and Zig implementations were compared with Python's unchanged `re` in the same **624-case** run, after the actual Rust source passed the original complete compatibility campaign. The sealed **24,576-case final benchmark is NOT MEASURED and NOT ACCESSED**.

| Engine | Overall speed against Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.325288487× | 1.27839835–1.37896156× | 451/624 | 46/624 |
| Rust | 1.151248920× | 1.10638691–1.19686063× | 272/624 | 109/624 |
| Zig | 1.010909001× | 0.965004934–1.056668895× | 229/624 | 232/624 |

Here **1× is the speed of Python's `re`**. Every interval compares one candidate with Python in this particular run; it does not compare separately run experiments. All **387 substantial slowdowns** are reported: C **46**, Rust **109**, and Zig **232**. A substantial slowdown is a case taking **strictly more than 20% longer** than Python.

## The one-line experiment

The single production change sets our own Rust bridge's `RUST_FINDALL_BATCH_CAPACITY` from **128 to 16**. For the existing four-group inline layout, the temporary on-stack result buffer consequently decreases from **9,216 bytes to 1,152 bytes**. The existing from-scratch matcher, Rust parser and compiler, Python interface, match semantics, Unicode behavior, and replacement engine are unchanged.

The existing continuation logic continues fetching results in batches of up to **16** until every match is returned. The tradeoff is explicit: when a subject has many matches, smaller batches can require more calls into the native matcher. The run still contains **33** `findall` cases taking more than 20% longer than Python; they are included, not removed.

A separate inspection of the compiled native code found two **4,096-byte stack-page probes** at the older entry. The smaller-buffer path is inlined into `rust_pattern_findall_direct`; its entry reserves `0x598` bytes and has no 4,096-byte page probe. This is an observed difference in the machine code. It is **not** a direct timing experiment and does not establish that stack probes, inlining, or the buffer change caused the observed overall speed.

## The first failure is preserved

The [original failed first campaign](../../../candidates/evidence/RUST-FINDALL-CAPACITY-16-INITIAL-AUDIT-FAILURE.md) remains part of the record. It stopped when the actual original 22-stage runner's in-process from-scratch audit reported a failure, even though the independent audit and the matching, deep-contract, and behavior checks had already passed. The frozen exception did not retain the detailed audit result, so the cause of that first failure is **NOT ESTABLISHED**. It is not reported as a regular-expression mismatch or a completed compatibility run.

After concurrent work stopped, the **unchanged** original campaign was rerun with the identical source, native library, checks, and limits. [All 22 real stages then passed](../../../candidates/evidence/rust-v8-rust-findall-capacity-16-sealed-campaign.json), including **4,494,555 Unicode comparisons**, replacement and callback checks, and isolated crash and recursion checks. The passing report has SHA-256 `89793a597ac74551742d05bdf1c5af61f1121d89466e00ac2902c8942aaeef4d`. The successful retry does not explain or erase the first failure.

Additional source-bound proofs are the [223,198 matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-findall-capacity-16.json.gz), [393 Python object and method checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-FINDALL-CAPACITY-16.json.gz), [479 observable-behavior checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-findall-capacity-16.json.gz), and [passing independent source and native-library audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json). The audit has SHA-256 `af69f41966a26d9ec1892e34b16f1bc02eb095c41767899d0a3deb612591d8fc`. None of these correctness checks opens or times the final benchmark.

## What was actually measured

The same four-way practice run used **624 cases**, **7 paired trials** per case, **4 warmups**, and **499 preselected confidence resamples.** It records **17,472 timing rows** and **52,416 correctness checks**. The actual Rust bridge source is SHA-256 `83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed`; the loaded native bridge is SHA-256 `1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34`. Both source bindings agree before and after the run.

- [All 624 cases, confidence intervals, and 387 substantial slowdowns](three-qualified-engines-public-practice-v3-summary.json); SHA-256 `33ebdff8ecb061e3544b9cd4bc687040b8278aa037f3c993abe654daa665d155`.
- [Every original paired timing observation](three-qualified-engines-public-practice-v3-raw.jsonl.gz); compressed SHA-256 `d17ae80c1a2d8adddf2ddeecd3ff84377e72f293d8ca8add2ad1c533bcf562b1`; uncompressed SHA-256 `225c3c83e4a8170f5851586f70aed0c58cc056778a8c718b7799abc896bf169c`.

The [earlier fused-call experiment](RUST-FUSED-VECTORCALL.md) and its [original measurements](three-qualified-engines-public-practice-v2-summary.json) remain unchanged. That separate run reported Rust at **1.136192×**, with **252** clearly faster cases and **112** substantial slowdowns; the current run reports **1.151249×**, **272**, and **109**. These are descriptive results from different runs: there is **no paired confidence interval across runs and no proven causal claim** about their difference.

The recorded allocation figures describe **Python-traced temporary memory only**. All four implementations shared the measurement process; per-engine total native memory was **NOT MEASURED**.

## Independent verification and charts

The following are the exact version-three integrity, verification-tool, and graph destinations. A link is not a claim that the artifact has already been generated or successfully verified; results count only when the recorded source-bound files and self-checks actually pass. Self-checks belong to the linked tools; no nonexistent self-test reports are claimed.

- [Independent verification of every observation and source hash](three-qualified-engines-public-practice-v3-integrity.json).
- [Version-three verifier and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v3_audit.py).
- [Version-three chart generator and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v3_charts.py).
- [Overall speeds and confidence intervals](three-qualified-engines-public-practice-v3-overall.svg).
- [Candidate rankings relative to Python](three-qualified-engines-public-practice-v3-rankings.svg).
- [Results for each regular-expression operation](three-qualified-engines-public-practice-v3-api.svg).
- [Faster, slower, and inconclusive cases](three-qualified-engines-public-practice-v3-outcomes.svg).
- [Every substantial slowdown](three-qualified-engines-public-practice-v3-regressions.svg).
- [Python-traced temporary memory and its limitations](three-qualified-engines-public-practice-v3-memory.svg).

Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
