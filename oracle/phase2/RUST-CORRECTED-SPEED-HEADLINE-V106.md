# How fast are the different versions?

Freeze a clear, user-facing public-practice speed graph. Python is always the
**1.00×** baseline. The exact first-party Rust build that actually passed
**31,237/31,237** original checks and **10,434/10,434** separate broader public
checks was measured at **1.2424347186648022×** Python, with a 95% interval of
**1.189358106927207×–1.301024782265517×**. Say **1.24×**, or about **24%
faster**, in the picture. This is actual public-practice evidence, not a hidden
final benchmark, replacement qualification, runtime non-delegation proof, or
winner.

Show all five relative-speed bars clearly:

* Rust — fully correct: **1.24×**, marked as passing both correctness suites.
* Python — original: **1.00×**, clearly identified as the baseline.
* V26 — earlier experiment: **1.25×**, failed **1,145** broader checks.
* V27 — earlier experiment: **0.80×**, failed **1,145** broader checks.
* V28 — earlier experiment: **1.23×**, failed **1,145** broader checks.

Each bar comes from the same 416 public-practice tasks. The corrected Rust run
includes all **1,664** counterbalanced paired timing rows, with four rounds per
task. Rust was faster on **252/416** tasks, slower on **164/416**, and more than
20% slower on exactly **14**. Display every one of the 14 larger regressions in
the graph itself and preserve all 164 slower rows, all 14 full regression
records, and all three historical losses in both graph data artifacts and the
frozen contract. Do not silently average away inconvenient losses.

The independently observed memory result is **111,026** traced peak bytes for
Rust versus **181,952** for Python. Whole-process peak memory was the same,
**44,032 KiB**, with exactly **1,248** public profiling executions per engine.

Authenticate the actual corrected V4 receipt and complete timing summary:

```text
oracle/phase2/evidence/rust-corrected-public-performance-v4-v33-corrected-performance-run-001-publication-receipt.json
db9288ea7c0a00e0c702acb7520e74482f8fb3c90cccee8f6e247f592811f2b3

experiments/rust_corrected_public_performance_v4/v33-corrected-performance-run-001/public-416-performance-summary.raw.json
7366a81a3fa1352cb6e8a165d5c45871f0081bda7e5c392e07d7bbf3f3a4cfef

experiments/rust_corrected_public_performance_v4/v33-corrected-performance-run-001/public-416-paired-timing.raw.json
2677471e5cd835b2cbf63ef2bc3e22c2069ef24953be98fa7dae1930ea980a26
```

The original and broader-public receipts must authenticate the same exact
first-party engine, native bridge, and complete Python adapter:

```text
engine  e692633896b61141734d4bb6ddce4a66b2c93bbeaa29b940fcf85904cf6a42e8
bridge  ecb19eb814430aeb571f60dd50ba4de4b3f54e7f57f056d2436c41714a257000
adapter f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227
```

Independently authenticate the entire frozen V4 controller triple, the entire
V105 same-build correctness source triple, the exact actual original/public PASS
receipts, the static-only first-party audit, the actual performance receipt,
the complete summary, all 1,664 actual paired rows, and the complete historical
V26/V27/V28 summaries and FAIL receipts. Check expected byte size, SHA-256,
physical device, pinned immutable inode, owner, mode, and one hard link.

Source-only verification never opens or stats hidden/final proposal files,
private build roots, candidate sources, native binaries, archives, case
fixtures, secret seeds, or hidden cases. Never execute a candidate, compiler,
native loader, matcher, profiler, clock, Git action, thread, or network call.
Run `--verify-frozen-context` and `--self-test` normally and in an empty
environment with pinned `-I -B -S` CPython 3.14.6. Hostile controls must reject
invented speedups or confidence intervals; erased slower cases or regressions;
incorrect memory results; omitted, promoted, or misrepresented historical
experiments; mismatched same-build correctness identities; candidate
qualification; invented runtime independence; hidden access; and a winner.

Only root may invoke `--render-graph --root-authorized
--frozen-committed-pushed --frozen-commit COMMIT --pushed-commit COMMIT`, after
this exact renderer, protocol, and contract have actually been committed and
pushed. The renderer then exclusively creates the fresh V106 SVG, inputs, and
summary without modifying any existing graph. The complete title must be
**How fast are the different versions?** No final winner is selected.
