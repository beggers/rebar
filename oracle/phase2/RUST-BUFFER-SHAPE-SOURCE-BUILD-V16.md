# Freeze a reproducible Rust build for both first-party bridge repairs

This is a source freeze, not a native build, a compatibility result, or a speed measurement. The final bridge remains one implementation of our own Rust matching engine; it does not wrap, call, link, import, or download another regular-expression engine.

## Preserve what was actually measured

CPython 3.14.6 remains the independently pinned reference. Preserve all 13 original groups, all 31,237 original case executions, and exactly the 13 named private exclusions. Keep the 50 additional callable checks separate.

The last completed Rust correctness run failed with exactly 928 differences and 8,965 genuinely observed passing cases. All 13 original workers completed, there were no infrastructure failures, and all four original Rust targets were restored. Do not subtract 928 from 31,237 to invent passing cases.

The corrected Python reference actually passed with two distinct worker process IDs, 81 and 82, each observing 6,912 original public-type cases, including the 96 subclass-cache cases. Preserve the complete records and their distinct cache-record hash.

Only the separately committed, independently pinned V49 buffer-shape and V50 combined-buffer-and-pickle source freezes describe the proposed corrections. Both are first-party modifications of the same historically corrected V13 Rust bridge. The intermediate buffer bridge is exactly 180,436 bytes, SHA-256 29421096dc81759ca11c53080b7f838cc29ad16baa7e379c18c8417d35ab37b3. The final combined bridge is exactly 181,004 bytes, SHA-256 00271ad5fff71e2f2e30cda6b446a61d0c300cb91eec2091b8ada17662d9a335. Its three additional, independently reproduced source transformations preserve the existing Match constructor, buffer behavior, scanner reconstruction, and Python adapter. Their new matching results are NOT RUN. The last actual Rust result stays a failure until the full frozen original suite is independently rerun.

The actually committed version-50 graph contains 176 authenticated evidence owners and 181 authenticated references. Its four independently pinned artifacts are renderer 4077fbf6703e98325c4b4eacea95d27608a3bb21a93143024094154385787f45, inputs 8506587243c98fa75a14dfc74cfc918772a74eadebc3f2728772d1d0d94bd726, summary 60f0648be19016e5d8ebfa01f93c2c50c32aa4fb981fc0d518902b8b9985005e, and chart a114a7b813c4c1fc470950639adc50ffb7118dd91a31d9f63dee6ba46e04f8b9. The earlier version-48 168/173 and version-49 172/177 counts remain historical; neither may replace the actual current lower bounds. No exact global census is claimed.

The independently frozen buffer feature has source 9c2a3642f2cda9fc85fd391baf4e0d57b25117f444d3a831592e8b62de3a627b, protocol 67ba62acc8e51a6868404ea3faeb1aaaacb1d053cc1c915bef0c397edf5ac408, and canonical contract ffa76d1724396fae5816cf96e0ae2104bcce8fc5eb246b8306d4441db0fe4a1b. The independent combined feature has source 85383f4cdf93eef0130390e1114cbd1703edce154ca274d2427c6943e46b3517, protocol fad29fdcd3956ae99f9db40afae33b51eb99fb743baf89540a4ee7aafb7ac1af, and canonical contract 5456535223cb029d41e8739696bde30b2b7127995fd0ef30286ff0488b1ed133.

Do not read, pin, or require mutable README, experiment-log, or reproducing files. Treat all previous documentation hashes only as historical provenance. Use independently identified immutable graph artifacts and genuine publication receipts. Never read or inflate any historical matching, reference, or build archive.

## Freeze one future two-phase build

Only a separate, caller-pinned --build operation may create owner-only fresh temporary directories under /tmp. Precreate reference-a and reference-b before either source overlay. Authenticate all nine original Rust source owners, the pinned single-package Cargo manifest and lock, the unchanged original adapter and bridge, both independently frozen source-feature triples, the exact final combined bridge bytes, and the historically corrected 31,934-byte public adapter.

In each independent phase, create exactly seven unchanged Rust sources, one exact combined first-party C bridge, and one exact historical corrected Python adapter. Use genuine distinct 0700 directories and exclusive, no-follow 0600 source files. Authenticate every full source and inode, and recheck the original repository sources without changing any canonical target.

Run exactly fourteen genuinely successful pinned compiler and ELF-inspector processes per phase, with unique process IDs. Rust Cargo must stay locked, frozen, and offline with an independent private Cargo home and target. Use the frozen first-party V9 and V7 low-level build and ELF-audit kernels only after explicit build authorization. Compare the full independently created engine and bridge ELF bytes from both phases.

A real future success or failure receives a unique bounded deterministic archive and an independently durable exclusive, fsynced receipt. A successful publication means only that the build evidence was preserved; it never proves matching. Preserve actual process counts and errors on a failed build.

## Source-only verification

Run --self-test and --verify-frozen-context with isolated pinned CPython 3.14.6 and independently caller-pinned source, explanation, and canonical machine contract, both ordinarily and with a clean environment.

The synthetic self-test must physically block source reads and writes, clocks, compiler or candidate processes, matching imports, network access, threads, locks, signals, native loading, and archive decompression. Reject substituted feature owners, stale histories, missing or reused phase and source identities, altered compiler roles, forged process IDs, external regular-expression dependencies, omitted errors, premature matching and publication, changed original case counts, extra waivers, invented performance, and opened holdouts.

The read-only context may authenticate only pinned immutable source files, canonical contracts, the final immutable graph, original source owners, and independently durable small receipts. It must not execute historical high-level build or campaign controllers, touch original native targets, read compressed archive bytes, pin mutable documentation, run candidate matching, start a compiler, open the holdout, or claim that the future build has happened.

Corrected matching, performance, memory, confidence intervals, and undefined behavior remain NOT MEASURED. No replacement is qualified. The 4,194,304-case final holdout is NOT OPENED.
