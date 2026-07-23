# Rust: common-prefix filtering did not establish an improvement

**Outcome: correctness qualified; the new performance design is REJECTED.** The independently implemented Rust engine remains faster than Python's `re` in this particular practice run, but the new common-prefix design does not demonstrate an improvement over the simpler, separately measured Rust implementation. This is a **624-case public practice test**, not the final speed test. The sealed **24,576-case** final benchmark is **NOT MEASURED** and **NOT ACCESSED**.

The [verification-incident record](RUST-OWNED-MANDATORY-COMMON-PREFIX-VERIFIER-INCIDENTS.md) preserves the initial failed synthetic verifier test and the quarantined, out-of-scope source review. No hidden final input was accessed.

| Engine | Overall speed against Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.317502593× | 1.270019803–1.372256642× | 443/624 | 51/624 |
| Rust | 1.143275840× | 1.098594086–1.189422726× | 255/624 | 113/624 |
| Zig | 1.005850526× | 0.960063719–1.051017934× | 223/624 | 243/624 |

Here **1× means Python's speed**. Each confidence interval compares one candidate with Python **inside this run**; it is not a comparison against a previous run. All **407 substantial slowdowns** remain visible: C **51**, Rust **113**, and Zig **243**. A substantial slowdown is a case taking strictly more than **20% longer** than Python. Rust is clearly faster in **255 of 624** cases, not the **60%** required for final success.

## What was tried

The owned Rust regular-expression compiler analyzes its own parsed pattern to discover a sequence of case-sensitive bytes that **every successful alternative must start with**. It stores at most **16 bytes** and traverses at most **64** nested pattern levels. Diverging alternatives shorten the common prefix and are not incorrectly treated as the entire pattern. Unknown character classes, case folding, lookarounds, backreferences, conditionals, variable repetitions, and wider Unicode character representations conservatively disable or shorten the filter; exact fixed repetitions have checked limits.

The filter is applied only to unrestricted searches over actual contiguous byte or one-byte text, after the existing valid-start filter. Checked arithmetic preserves the search window. When a candidate prefix matches, the original ordered, capture-aware Rust matching engine still decides the result. Anchored matching, empty matches, captures, Unicode, replacement, scanners, and backtracking are not replaced by an approximation.

This change is entirely inside the from-scratch Rust engine. It does not wrap an external regular-expression library, call Python's matcher, add a package, borrow the C or Zig engine, or change the existing Python bridge.

## Actual complete correctness qualification

The new Rust engine source is SHA-256 `d6e0cd31b06cd4edb1af7f8fb7409c23027289818934b35a03d5b3cc17444784`; its actually loaded native engine is SHA-256 `37ab3d8598bdbbe9097810a35b54f3558fd0473db903d0a0c6b6527068dbf7cb`. The unchanged bridge source is SHA-256 `83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed`; the unchanged loaded bridge is SHA-256 `1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34`.

Before the practice measurement, this exact implementation passed:

- [223,198 frozen matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-owned-mandatory-common-prefix.json.gz).
- [393 Python object and method-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-MANDATORY-COMMON-PREFIX.json.gz).
- [479 observable Python behavior checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-owned-mandatory-common-prefix.json.gz).
- [All 22 original frozen correctness stages](../../../candidates/evidence/rust-v8-rust-owned-mandatory-common-prefix-sealed-campaign.json), including all **4,494,555 Unicode comparisons**, Python's own tests, replacement and callbacks, and isolated crash and recursion checks.
- [The passing independent from-scratch and actual native-library audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json); SHA-256 `4856f38bac3f54a1c0758e4c32c8d738a55128f932ecbc451025ea170108709d`.

The complete, source-bound 22-stage report has SHA-256 `9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688`. The correctness campaign does not time or access the final benchmark.

## What was actually measured

Python, Rust, C, and Zig were measured together on **624 public cases**, with **7 paired trials** per case, **4 warmups**, and **499 preselected confidence resamples.** The practice record includes all **17,472 timing rows**, **52,416 correctness checks**, and **407 substantial slowdowns**. Candidate source and loaded native-library fingerprints match before and after the run.

- [Every case, confidence interval, and slowdown](three-qualified-engines-public-practice-v5-summary.json); SHA-256 `98c611410895f831d0b97a1677723186cc1e06d438d3437bfec9519743b1ad69`.
- [Every original paired timing observation](three-qualified-engines-public-practice-v5-raw.jsonl.gz); compressed SHA-256 `bfb82c4ac326163db2d3ae463817e2a56821e0c5f1b72ee693c26690c23e4a7d`; uncompressed SHA-256 `8a1b998c140046ac3b795cf912c5ccb958ac182d44b1a49b7f055aed25f80eb2`.

The preceding [Zig buffer experiment](ZIG-STAGE-12-SPAN-256.md) and its [complete historical practice run](three-qualified-engines-public-practice-v4-summary.json) remain intact. That separately recorded run reported the existing simpler Rust engine at **1.146317870×**, with **266** clearly faster cases and **112** substantial slowdowns. The common-prefix run reports **1.143275840×**, **255**, and **113**. There is **no paired confidence interval between the separate runs**. These observations neither demonstrate an improvement nor prove that common-prefix filtering caused the numerical difference. The more complicated design is therefore **REJECTED as an unproven improvement**, while its passing correctness evidence remains recorded.

Temporary memory values describe **Python-traced allocations only**. All engines shared a process; independently isolated native or whole-process memory for each engine is **NOT MEASURED**.

## Independent verification and graphs

The following are the exact version-five integrity, verification-tool, and graph destinations. A link does not assert that a file has already been generated or that its checks passed. Self-checks belong to the actual version-five tools; no nonexistent self-test reports are represented as evidence.

- [Independent verification of every observation and native source hash](three-qualified-engines-public-practice-v5-integrity.json).
- [Version-five independent verifier and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v5_audit.py).
- [Version-five graph generator and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v5_charts.py).
- [Overall speeds and confidence intervals](three-qualified-engines-public-practice-v5-overall.svg).
- [Candidate rankings against Python](three-qualified-engines-public-practice-v5-rankings.svg).
- [Results by regular-expression operation](three-qualified-engines-public-practice-v5-api.svg).
- [Faster, slower, and inconclusive cases](three-qualified-engines-public-practice-v5-outcomes.svg).
- [Every substantial slowdown](three-qualified-engines-public-practice-v5-regressions.svg).
- [Python-traced temporary memory and its limitations](three-qualified-engines-public-practice-v5-memory.svg).

Common-prefix design: **CORRECTNESS QUALIFIED; PERFORMANCE REJECTED**. Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
