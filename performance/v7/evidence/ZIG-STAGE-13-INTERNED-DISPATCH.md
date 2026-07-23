# Zig: reuse interned pattern attributes

**Outcome: all 22 compatibility stages passed; faster than Python on public practice; not a final winner.** The from-scratch Zig implementation achieved **1.281412365×** Python's speed in one public practice run, with a 95% interval of **1.234485699–1.330033512×**. This is not the final benchmark: its separate **24,576 hidden cases** remain **NOT ACCESSED** and **NOT MEASURED**.

| Implementation | Speed relative to Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.315798804× | 1.269917517–1.368604831× | 438/624 | 48/624 |
| Zig | 1.281412365× | 1.234485699–1.330033512× | 361/624 | 95/624 |
| Rust | 1.141205743× | 1.095380115–1.187054562× | 264/624 | 116/624 |

Here **1× means Python's unchanged `re`**. Each interval compares one implementation against Python in the **same** public practice run. Every implementation was compared on the same 624 cases. All **259** substantial slowdowns are included: **48 C**, **95 Zig**, and **116 Rust**. “More than 20% slower” means a case takes strictly more than 1.2 times Python's time; it is not a change of denominator or an omitted inconclusive result.

## What changed

Zig's independently implemented parser, compiler, and matching engine did not change. Its native Python bridge now interns and reuses the seven existing pattern-attribute names `pattern`, `flags`, `groups`, `_groupindex`, `_handle`, `_literal`, and `_templates`. It retrieves each attribute with Python's normal `PyObject_GetAttr(pattern, key)`, using the reused key.

This keeps ordinary Python attribute and descriptor lookup. In particular, it does not bypass custom `__getattribute__`, subclasses, raised exceptions, or attribute descriptors. Search, match, full match, iteration, scanning, splitting, replacement, and replacement counts retain the existing native calling convention, argument handling, method identity, cleanup, and error propagation. The bridge does not call Python's regex engine, an external regex package, the C implementation, or the Rust implementation.

The exact five production artifacts are:

| Production artifact | SHA-256 |
| --- | --- |
| Zig native bridge source | `92d4039e1db2e01757edfd4edf56006c4735c3bc64352b6ce9c5d1f69decafcf` |
| Loaded Zig native bridge | `80d7dab57cbee317ee1727862e27cd7dcf4cb22e1a944f4b29f2e4e983f940ed` |
| Zig matching-engine source | `4deca5a442cccd02bebfcecd4ceeb73de62a68837c5a3bdadee4dcaf84cf0ee3` |
| Loaded Zig matching engine | `70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614` |
| Public Zig Python interface | `95a2010152099f2db61595927542b2f25a675eb72bd33125659969d804360239` |

## Correctness was established before timing

Pinned CPython **3.14.6** was the reference. The exact same Zig source and loaded native libraries passed:

- [223,198 frozen matching comparisons across 49 categories](../../../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-13.json.gz), with no mismatches; compressed SHA-256 `b31af0559e865b93a506e0915073cef141a805b4462e7e4d4a692e11aff393fc`.
- [393 detailed Python object, method, descriptor, and error-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-13.json.gz), with no public mismatches; compressed SHA-256 `1adc32659fab774aeb77f74d3df6b005c14d2aec3aae52e5d6fdf6791bcd151e`.
- [479 observable Python-behavior checks](../../../candidates/evidence/rust-v8-observability-zig-qualified-stage-13.json.gz), including self-oracle validation, with no failures; compressed SHA-256 `99caa13c501461f9a95a71188ba41a00ead9b90bc2a816c9db307544032da081`.
- [All 22 sealed compatibility stages](../../../candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json), including Python's own regular-expression tests, replacement callbacks, crash and recursion isolation, and **4,494,555 full-Unicode comparisons**; SHA-256 `4ba7cb9c45a70b747cc0a6eb721f6bb51081157f527d1bf5e578e603715ae5dc`.
- [The independent from-scratch and no-delegation audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json), including the independent engine families, loaded native libraries, and malicious-delegation controls; SHA-256 `5ce9df468d136b47c435456e59d372aed74d89f80fe1f877988dd7dba784b737`.

The compatibility campaign recorded performance **NOT MEASURED**, did not access the hidden cases, and independently bound the actual production source and binaries. The subsequent practice measurements found **zero correctness failures**.

## Where the Zig result comes from

The complete practice record contains **12 regular-expression operations**, **624 cases per implementation**, **7 paired trials per case**, **4 warmups**, **499 prespecified confidence resamples**, **17,472 original timing rows**, and **52,416 correctness checks**. It preserves all **1,872 implementation-by-case results** and all **259** substantial slowdowns.

The table below exposes every repeatedly used compiled-operation category, including the weak ones. “Clearly faster” is the same recorded statistical classification used for the overall table; all comparisons use Python as the baseline.

| Zig operation | Public cases | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: |
| Find all matches, compiled | 78 | 53 | 8 |
| Iterate over matches, compiled | 65 | 43 | 10 |
| Full match, compiled | 47 | 24 | 22 |
| Match, compiled | 48 | 2 | 26 |
| Match-object behavior, compiled | 48 | 24 | 3 |
| Scanner, compiled | 48 | 25 | 6 |
| Search, compiled | 35 | 11 | 14 |
| Split, compiled | 47 | 36 | 0 |
| Replace, compiled | 33 | 28 | 2 |
| Replace and count, compiled | 37 | 30 | 1 |
| Other public, cold, and module-level cases | 138 | 85 | 3 |
| **All public Zig cases** | **624** | **361** | **95** |

The individual compiled categories are direct observations from the version-seven practice summary. They motivate continuing to investigate the cost of calls between Python and native code, but they do **not** establish that interning caused any measured change, that Zig is faster on every operation, or that a separate run is statistically comparable.

- [Every practice case, interval, ranking, and substantial slowdown](three-qualified-engines-public-practice-v7-summary.json); SHA-256 `89cf98bee40bb8e3ecc95861e07f302eff6c5f6288130854ea806578e8b76d79`.
- [Every original same-run timing observation](three-qualified-engines-public-practice-v7-raw.jsonl.gz); compressed SHA-256 `574f62be23725529decaa7bbab67a575faae040470ccef9f528213c50866385c`; uncompressed SHA-256 `59a04863d5cc2f0727222ac8d4388255411803793c741975d4c8abb3bfc3a696`.

## Preserve the earlier results and the limitations

The [previous four-way practice record](three-qualified-engines-public-practice-v6-summary.json) is retained without modification. That earlier run recorded Zig at **1.014920038×**, **231/624** clearly faster cases, and **235/624** substantial slowdowns. It recorded **407** substantial slowdowns across all three candidates. Version seven records Zig at **1.281412365×**, **361/624**, and **95/624**, and records **259** slowdowns across all candidates.

These are **different measurement runs**. There is no paired confidence interval between versions, no statistically established cross-run improvement, and no proof that the attribute change caused their difference. The earlier C and Rust observations, the original C experiment report, and the other previous evidence remain historical results, not replacements for their same-run version-seven measurements.

Memory observations in the practice record describe **Python-traced temporary allocations only**. Per-engine native allocations and full independently isolated process memory are **NOT MEASURED**.

The [separate verification and isolation incident record](ZIG-STAGE-13-VERIFIER-INCIDENTS.md), SHA-256 `84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff`, discloses a quarantined read-only reviewer-role incident. It did not provide authorization to inspect hidden cases, open the final benchmark, alter production artifacts, or perform measurements; it does not constitute a final result.

Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
