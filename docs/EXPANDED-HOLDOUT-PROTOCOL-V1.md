# Expanded final speed comparison

Status: **PROPOSED; NOT FROZEN, NOT GENERATED, NOT OPENED, and NOT
MEASURED. There is no winner.** This document does not create a final-test
seed, manifest, case, measurement, or result.

The question is whether an independently written Python `re` replacement
is both fully compatible and genuinely faster than unmodified, pinned
CPython 3.14.6 on complete Python-visible operations. A binding to an
external regular-expression package is not a candidate. Neither is an
engine that calls Python's `re`, `_sre`, another candidate's matcher, or
any hidden fallback. Language choice and an ordinary foreign-function
interface do not establish engine independence: each qualifying family
must own its parser, compiler, and matching implementation.

## Preserve the earlier plans

The previous **1,048,576-case** proposal is preserved as published:
`16 × 16 × 4 × 4 × 256`. It was explicitly **NOT FROZEN** and **NOT
OPENED**; it must not be described as an existing, generated final
test. The new proposal increases the variant axis fourfold. Any earlier
opened, contaminated, invalidated, or historical “final” remains
historical and invalid. Do not inspect, import, reuse, reinterpret,
replace, or delete its cases, secrets, timings, or evidence.

## Exactly what would be compared

The final denominator is **4,194,304 independently generated valid
cases**:

`16 operation cohorts × 16 pattern families × 4 subject types`

`× 4 valid operation-specific lifecycles × 1,024 unique variants`.

Every case has weight `1 / 4,194,304`; every one of the **4,096**
operation/family/subject/lifecycle strata contains exactly **1,024**
cases. No invalid combination, duplicated variant, silently dropped
case, operation-dependent weight, or replacement denominator counts.

The 16 equally weighted operation cohorts must collectively include all
36 operations already frozen in the public development suite:

1. Cached compilation and genuinely fresh compile-and-search.
2. Module and compiled-pattern search.
3. Module and compiled-pattern match.
4. Module and compiled-pattern full match.
5. Module and compiled-pattern find-all.
6. Module and compiled-pattern iterators and their exhaustion.
7. Module and compiled-pattern splitting, including positional calls.
8. Literal and positional substitution.
9. Literal and positional substitution with a returned count.
10. Callback substitution, including callback and positional errors.
11. Counted callback substitution, including positional callback errors.
12. Compiled-pattern scanner search.
13. Compiled-pattern scanner matching and repeated scanner iteration.
14. Lexicon scanning and lexicon-callback errors.
15. Match groups and captures.
16. Match-template expansion.

The families cover literals, prefixes, alternation, greedy and lazy
repetition, atomic or possessive matching, character classes, Unicode
and ASCII rules, anchors and boundaries, numbered and named captures,
backreferences, lookahead, fixed-width lookbehind, scoped flags,
conditionals, and zero-length matches. The four subject types are
`str`, `bytes`, `bytearray`, and genuine `memoryview`; readonly and
writable views must each occupy half of the applicable variants.
Pattern, flags, replacement, callback, scanner, and lifecycle are
chosen from **valid, separately defined domains for their exact
operation and subject**. Inapplicable Unicode flags, imaginary compiled
methods, and invented scanner combinations cannot fill matrix cells.

The four lifecycle states are genuinely relevant states defined in
advance for each operation: fresh work, a warm module cache, reusable
compiled state, and an existing match, iterator, scanner, or equivalent
valid state. A lifecycle that does not exist for an operation must be
replaced prospectively with a distinct valid operation-specific state,
not relabeled or silently counted.

## Participants and timing

The primary four-participant comparison admits exactly pinned,
unmodified CPython and **three fully correctness-qualified,
source-distinct, from-scratch engine families**. Pin the Python
executable and standard-library identity, original-test results,
complete compatibility and ownership audits, candidate source trees,
build recipes, and exact loaded native binaries **before** any final
secret exists. A wrapper, alternate binding, engine configuration,
partial implementation, or fallback cannot fill a participant slot.

Run **24 paired rounds per case**, using each of the **24 permutations
of the four participants exactly once**. Thus every participant appears
six times in each order position, and each pair runs first exactly 12
times. Order rotation is fixed before measurement. Each engine executes
in its own pinned, isolated, serialized worker on the same machine.
Run four untimed warm-ups per participant and stratum; preserve cold
cache and fresh-compilation semantics. Verify the actual observable
result, exception, callback effects, captures, warning, buffer state,
and match identity against Python. Prepare inputs and normalize
results outside the timed interval, but retain the complete
Python-to-native call and any promised compilation inside it. Abort and
preserve the full evidence on any correctness failure.

This comparison produces exactly **402,653,184 timed observations**
and **301,989,888 paired candidate-versus-Python observations**.
Four unsigned 64-bit nanosecond times per case and round require
**3,221,225,472 raw clock bytes (3.000 GiB)** before case metadata,
correctness results, checksums, or compression. Stream all records;
do not build a giant JSON document or omit raw trials. Use **256**
operation/family shards of **12,582,912 uncompressed clock bytes**
each, with authenticated case order, every candidate identity, and
both uncompressed and losslessly compressed content hashes. Publish
all 16 operation cohorts separately as focused, reproducible commits.
Compressed size, running time, and machine suitability are **NOT
MEASURED**.

If more than three independent engines eventually qualify, freeze the
complete eligible participant list before generating a secret; never
select three by observed final speed. The 24-permutation schedule and
the observation totals above apply **only to four participants**. For
any other participant count, prospectively freeze a new schedule and
new exact denominators: use cyclic participant orders paired with
their reverses, repeat complete balanced cycles, and admit at least
24 rounds. Report all eligible engines without calling that schedule
the four-engine result.

## Statistics, memory, and passing rules

For each candidate, report the equally case-weighted geometric mean
of its actual paired speed ratios. Calculate the two-sided overall
95% interval using **9,999** prospectively seeded stratified
bootstrap resamples of all **4,096** complete, equally sized stratum
scores. This requires **40,955,904** stratum selections per
candidate; it does not pretend that a 4-million-case resample or
1,000 per-case bootstraps were actually run.

Compute each case's exact, two-sided paired sign-test probability
from its 24 genuine rounds; conservatively retain ties. Separately
report the distribution-free **97.734%** median-ratio interval
between its seventh and eighteenth ordered observations. Classify
“statistically faster” or “statistically slower” only after a
prospectively specified Benjamini–Hochberg false-discovery correction
at `q = 0.05` across **all candidate-and-case comparisons**. An
unadjusted case interval is not a multiple-comparison-corrected
claim. Report faster, slower, inconclusive, and missing counts using
the exact full denominator, and explain **every** slowdown over 20%.

Measure memory and binding overhead separately from timing: **65,536**
balanced memory cases, or 16 per stratum, and **16,384** balanced
boundary cases, or four per stratum. For four participants, these
imply at least **262,144** memory observations and **65,536**
boundary observations. Record Python-visible allocations and actual
native/process memory separately. If native memory cannot be
observed reliably, label it **NOT MEASURED**; do not substitute
Python-only allocation figures.

A candidate can win only if it has zero unexplained compatibility
failures, crashes, or unsafe behavior; its overall lower 95%
confidence bound is at least **1.5×** Python; and at least
**2,516,583 of 4,194,304** final cases are statistically faster after
the declared correction. Preserve all engine results, uncertainty,
failures, raw observations, and regressions.

## Opening gate

Freeze the final generator, valid domains, exact weights, timing
schedule, participant identities, statistics, recording format,
memory protocol, and independent reviewer-approved integrity checks
**only after at least three independent engines have passed every
original Python, public-interface, lifetime, isolation, ownership,
and no-delegation gate**. Only then create a fresh independent secret,
publish its commitment without revealing it, and generate final
cases from separately domain-separated secret material. Public
development cases use a different, openly documented domain. Never
open, derive from, or optimize against previous hidden cases.

Until these gates, the final generator, secret, cases, comparisons,
native memory, charts, rankings, and winner remain **NOT FROZEN**,
**NOT GENERATED**, **NOT OPENED**, or **NOT MEASURED**, as appropriate.
