# Final speed experiment: falsified

**Final result: FAIL. No winning replacement was established.** The sealed **24,576-case** benchmark was genuinely and irreversibly opened. The unchanged final protocol stopped because the Zig candidate returned a result different from pinned CPython during the warmup for a previously unseen case. The error and process exit were:

```text
v9 sealed protocol rejected: pinned CPython result mismatch: v9.split.literal-and-long-prefix.006:warmup:candidates.zig_candidate
```

Final process exit status: **2**.

This is an actual hidden-benchmark correctness failure, not a timeout, incomplete performance win, inconclusive confidence interval, or permission to retry. No case contents, hidden subjects, or external seed are reproduced here.

## The opening cannot be repeated

The genuine [unseal marker](V9-FINAL-HOLDOUT-24576-UNSEAL-MARKER.json) records the state `irreversibly-authorized-no-retry`. Its SHA-256 is `1df71b41bfdad7e850344242c16dc15c79039b9b925b1fbc709de18cce917cb2`.

The fail-fast benchmark stopped at the first actual comparison against pinned CPython that did not match. The final run must not be restarted, continued, resumed with a changed candidate, reopened, repeated under another name, or converted into a partial ranking. The marker, original protocol, frozen candidates, hidden cases, and partial observations must remain unchanged.

## Exactly how far the real run progressed

The [preserved original raw timing archive](V9-FINAL-HOLDOUT-24576-RAW.jsonl.gz) is a valid gzip file with SHA-256 `b93b5318fbd260d0778196f1ab5c668f003647c86b66b015fe369261f72ac53e`. It contains **1,778,408** recorded rows, representing **14,342** completely finished cases, **31** paired rounds, and all **4** modules per finished case:

```text
14,342 completed cases × 31 rounds × 4 modules = 1,778,408 rows
24,576 required cases  × 31 rounds × 4 modules = 3,047,424 required rows
```

The original stopping point is **14,342 of 24,576**, not a completed benchmark. The remaining **10,234** cases were not completed. No final summary or complete final memory archive exists, and there is no successful independent audit of complete final results. Partial rows must not be presented as a final ranking, complete timing result, or statistically valid candidate comparison.

In particular, although C and Rust passed their public, frozen correctness qualifications, the final protocol required **all three replacements and Python to complete the same entire hidden workload**. The early Zig mismatch prevented that. It is therefore not established that C or Rust passed the uncompleted cross-candidate final test. None may be declared the winner.

## Frozen correctness qualification remains genuine

The original independent public matching tests, Python behavior tests, and complete 22-stage correctness campaigns are not undone, edited, or reclassified. Their [unchanged four-family, five-native-library, 76-control from-scratch audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json) has SHA-256 `a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326`.

The source-bound, independently qualifying final candidates are preserved exactly:

- [C's complete 22-stage public correctness campaign](../../../candidates/evidence/rust-v8-vm-stage-21-singleton-split-memchr-sealed-campaign.json).
- [Rust's complete 22-stage public correctness campaign](../../../candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json).
- [Zig's complete 22-stage public correctness campaign](../../../candidates/evidence/rust-v8-zig-stage-13-sealed-campaign.json).

These reports establish passage of the specified **public** correctness obligations. They do not establish passage of the later unseen final benchmark. Preserving that distinction is necessary to make the experiment falsifiable.

## Immutable final provenance

No original rule, candidate, final fixture, threshold, or measurement protocol was changed to avoid the failure.

- Original frozen protocol SHA-256: `a699ce1e661ead447af0643584d69f080e72712059ad611fbd6b998f2ca19219`.
- Frozen final manifest SHA-256: `d747bfbca78e94b7dada3fdc24acd027fc8cd2e31a46a9441c328fb72153460f`.
- Frozen candidate-selection evidence SHA-256: `52066760bb4210a57f7b10f13e9ff73e36c53982a5b97aff40ead330c79edf41`.
- Immutable objective SHA-256: `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.
- Unchanged complete from-scratch audit SHA-256: `a790fe1a75c8748df7f8bb6f1e39d0be841636055358aaee94db0aa35523f326`.

The [earlier missing-`time` incident](FINAL-PREUNSEAL-MISSING-TIME-INCIDENT.md) occurred **before** any marker, subprocess, hidden case, or opening and was separately recorded. The subsequent standard-library-only bootstrap preserved the original protocol byte-for-byte. Unlike that preliminary failure, the mismatch documented here occurred **after the real irreversible opening**, with genuinely recorded final rows. The two incidents must not be conflated.

Final hidden correctness: **FAIL**. Final benchmark: **OPENED; INCOMPLETE; NO RETRY**. Complete final **24,576-case** speed: **NOT MEASURED**. Final **1.5×** threshold: **NOT MEASURED**. Final **60% faster-case** threshold: **NOT MEASURED**. Final winner: **NONE**.
