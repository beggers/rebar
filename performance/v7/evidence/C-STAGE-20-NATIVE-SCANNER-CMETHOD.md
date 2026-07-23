# C: create the scanner's search method directly

**Outcome: fully compatibility-qualified; promising on public practice; not a final winner.** Our independently implemented C regular-expression engine completed all 22 frozen correctness stages. In one four-way public practice run, it was faster than Python's `re` overall, but the separate **24,576-case** final benchmark is **NOT MEASURED** and **NOT ACCESSED**.

| Engine | Overall speed against Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.329964256× | 1.282642773–1.382929907× | 429/624 | 47/624 |
| Rust | 1.151338742× | 1.104064398–1.196281042× | 262/624 | 125/624 |
| Zig | 1.014920038× | 0.967448002–1.062232141× | 231/624 | 235/624 |

Here **1× is the speed of Python's unchanged `re`**. The confidence intervals compare each implementation against Python **in the same practice run**. All **407 substantial slowdowns** are preserved: C **47**, Rust **125**, and Zig **235**. A substantial slowdown means taking strictly more than **20% longer** than Python.

## The one-line change

Previously, the C engine constructed a find-all iterator by looking up the scanner's `search` method by name with `PyObject_GetAttrString(scanner, "search")`. The new implementation constructs the same native bound method directly:

```c
PyCMethod_New(&ScannerMethods[0], (PyObject *)iterator, NULL, &ScannerType)
```

`ScannerMethods[0]` is the existing native `search` method, and `&ScannerType` is its exact defining class. The change retains the existing fast native calling convention, scanner state, match ordering, empty-match continuation, reference counting, garbage collection, exception behavior, and callable iterator. It avoids one dynamic Python attribute lookup; it does **not** replace the matcher, wrap another regex library, call Python's regular-expression engine, or borrow the Rust or Zig implementation.

The exact C source has SHA-256 `696925d94c63fed442d547e9a0fbcce9dda271eae633130d01cdb4e68ea4af2f`; its actually loaded native library has SHA-256 `0e4d194fc14a2e307dd765ec5632acbe7b4192a0b2a74833a1126fbd0e5b5b91`.

## Correctness before timing

The same source and native library passed:

- [223,198 frozen matching checks](../../../candidates/evidence/rust-v8-edge-oracle-vm-deep-stage-20-native-scanner-cmethod.json.gz); SHA-256 `829c39f4ea838b229f4c7465e239e70509d9187de75a7d2f236da959c82f1343`.
- [393 Python object and method-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-C-STAGE-20-NATIVE-SCANNER-CMETHOD.json.gz); SHA-256 `75f4bfb3be85b30cf5abab5846ff53db653b651208cf2b7855b37e314a16eae0`.
- [479 observable Python behavior checks](../../../candidates/evidence/rust-v8-observability-vm-qualified-stage-20-native-scanner-cmethod.json.gz); SHA-256 `fc62219a7a07d176a8ee083d92ae406cb0162cdd05facd622529167cc4237899`.
- [All 22 original correctness stages](../../../candidates/evidence/rust-v8-vm-stage-20-native-scanner-cmethod-sealed-campaign.json), including Python's own tests, **4,494,555 Unicode comparisons**, replacement and callback behavior, and isolated crash and recursion checks; SHA-256 `c211d826032fed60c30024beb6de66c3e20b08fdcb936b53393d0a5fdba09721`.
- [The independent four-implementation, five-native-library from-scratch audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json), including all **76** malicious-delegation controls and actually loaded native mappings; SHA-256 `f875068b829482d0c5dd28290a5706dd0a5c0ed91018b857cee82b6defe40f0a`.

The correctness campaign itself declares performance **NOT MEASURED** and does not access the final benchmark.

## What the public practice result actually establishes

Python and the same C, Rust, and Zig implementations were measured together on **624** frozen public practice cases, using **7 paired trials** per case, **4 warmups**, and **499** preselected confidence resamples. The complete record retains **17,472** original timing rows, **52,416** correctness checks, and all **407** substantial slowdowns. Every candidate's source and loaded-library fingerprints agree before and after measurement.

- [Every public case, confidence interval, ranking, and slowdown](three-qualified-engines-public-practice-v6-summary.json); SHA-256 `22689cf92175274f935df81f51b07b4f2a0a90bafad3ae1bd2b0e9f905579fce`.
- [Every original same-run observation](three-qualified-engines-public-practice-v6-raw.jsonl.gz); compressed SHA-256 `9e38b7a20435d1479d88e0456ffb2849337983c7957ddad238c021d69c4913ee`; uncompressed SHA-256 `8098869ed442741e132567516341c73d78bef59db0e901280a940af40e25521e`.

The [previous common-prefix experiment](RUST-OWNED-MANDATORY-COMMON-PREFIX.md) and [its complete version-five practice record](three-qualified-engines-public-practice-v5-summary.json) remain intact. The earlier, independently measured C result was **1.317502593×**, with **443** clearly faster cases and **51** substantial slowdowns. The new result is **1.329964256×**, **429**, and **47**. These are **separate measurement runs**: there is no paired cross-run confidence interval, no demonstrated statistically significant improvement, and no proof that the one-line change caused their difference.

Memory figures describe **Python-traced temporary allocations only**. All implementations shared one measurement process. Independently isolated native memory and complete per-engine process memory are **NOT MEASURED**.

## Independent verification and graphs

The following are the exact version-six evidence, verification-tool, and graph destinations. Linking an expected destination does not claim it has already been generated or that its independent checks have passed. Self-checks are supplied by the version-six tools; no nonexistent self-test report is asserted.

- [Independent verification of every recorded case and source hash](three-qualified-engines-public-practice-v6-integrity.json).
- [Version-six verifier and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v6_audit.py).
- [Version-six graph generator and reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v6_charts.py).
- [Overall speeds and confidence intervals](three-qualified-engines-public-practice-v6-overall.svg).
- [Candidate rankings relative to Python](three-qualified-engines-public-practice-v6-rankings.svg).
- [Results by regular-expression operation](three-qualified-engines-public-practice-v6-api.svg).
- [Faster, slower, and inconclusive cases](three-qualified-engines-public-practice-v6-outcomes.svg).
- [Every substantial slowdown](three-qualified-engines-public-practice-v6-regressions.svg).
- [Python-traced temporary memory and its limitations](three-qualified-engines-public-practice-v6-memory.svg).

Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
