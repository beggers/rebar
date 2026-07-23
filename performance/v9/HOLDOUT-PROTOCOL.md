# A larger, genuinely unseen speed test

This is a prospective, independent test of whether a regular-expression engine
written from scratch can replace Python 3.14.6 and run faster in real Python
programs. It is an addition to the previous experiments. It never changes,
opens, reuses, or discards the original 10,312-case test or the separately
frozen 12,288-case version 8.

Final version 9 performance: **NOT MEASURED**.

## What is tested

The final test has **24,576 genuinely distinct cases**:

- 12 public operation families.
- Eight types of regular-expression workload for each operation.
- 256 independently generated cases in each operation and workload.

Each public operation contributes exactly 2,048 cases. Search, match, full
match, finding results, splitting, and replacements are equally balanced
between ordinary and precompiled calls, text and bytes, and successful and
unsuccessful matches. Compilation, escaping, scanner progression, and
inspection of actual match objects have their own meaningful, predeclared
controls. A missing match is never described as a match object, and escaping
is never described as a precompiled-pattern method.

The workload types cover literal text, character classes and Unicode,
boundaries and search windows, greedy and lazy matching, atomic and possessive
matching, alternatives and backreferences, lookaround, replacements,
callbacks, logs, paths, addresses, and realistic identifiers.

Unlike the preceding protocol, the secret changes the **real pattern, real
subject, capture names, literal words, repetition, case-folding flags,
replacement, and search window**. It is not merely inserted into a comment or
case label. Every generated string, bytes, bytearray, and memoryview is an
actual object of the claimed kind.

## Keeping the test unseen

The prospective manifest contains a SHA-256 commitment to a separately held
32-byte random opening, not the opening itself. The only permitted opening path
is outside the repository:

    /tmp/rebar-v9-final-holdout-opening-20260723-24576-v1.bin

The file must be regular, owned by the current user, exactly 32 bytes, and
permission mode 0600. Permissions do not prevent another process running as
that same user from reading it; blindness is therefore honestly described as
procedural rather than an operating-system security boundary.

The normal verification, candidate-freezing, and preflight commands never
open that file, generate a real test case, import a candidate, run a benchmark,
or inspect previous final-test inputs. Self-tests use only explicitly labelled,
domain-separated synthetic openings and synthetic case identities.

Before any final manifest or opening exists, the following bounded check uses
only a public, in-memory dummy commitment and synthetic examples:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
      /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -B -m tools.rust_v9_holdout_protocol self-test --public-synthetic-only

It does not create or freeze a manifest, start a candidate, benchmark a case,
generate final inputs, or read either version's opening.

The final opening requires the complete current candidate freeze, a committed
optimization-stopping point, an exact authorization string, and four distinct
previously nonexistent evidence outputs. An exclusive one-use marker is
created before the opening. An interrupted or failed opening cannot be
retried, replaced, or quietly called a fresh experiment.

## The actual prospective seal

After the Rust, C, and Zig engines each passed the complete 22-stage correctness
campaign, and before any further candidate optimization, the
[public manifest](holdout-manifest.json) was generated from a single genuine
32-byte operating-system-random opening. Its SHA-256 commitment is
`3ad3ff2bc34fd1dc371aa6516ac0a122f1d3e3e9da373d0db8c5cb5589da5bbb`.
The opening remains outside the repository and has not been read back or used
to generate a final case.

The [custodian](../../tools/rust_v9_opening_custodian.py) creates the fixed
owner-only file exclusively, refuses an existing file or symlink, synchronizes
both the file and directory, erases its working secret buffer, and publishes
only its [public attestation](evidence/HOLDOUT-CUSTODIAN-ATTESTATION.json).
Its [27 synthetic-only controls](evidence/HOLDOUT-CUSTODIAN-SELF-TEST.json)
include partial writes, existing files, symlinks, and synchronization errors.
Its isolation is honestly **procedural**: processes running as the same user
could read the file. It is not a separate-user security boundary.

The [75-check manifest-bound synthetic proof](evidence/HOLDOUT-PROTOCOL-SELF-TEST.json)
and [independent protocol verification](evidence/HOLDOUT-PROTOCOL-VERIFIED.json)
confirm the exact prospective source, case weights, confidence rules, and
commitment. Both record **zero** final openings, final cases, imported
candidates, or performance measurements. They are distinct from the earlier
public-only, uncommitted synthetic self-test.

## Exactly what is timed

Every engine runs in a different persistent isolated Python process.
Candidate timing processes cannot import Python's regular-expression engine,
another candidate, or an external matching package.

Real compiled-pattern cases retain their actual compiled pattern outside the
measurement. Cold and warm compilation remain separately defined. Real input
buffers, callbacks, and replacement functions are also constructed outside the
clock.

Each paired observation times exactly **16 actual public Python operations**.
The timer stops before a result is converted, compared, serialized, or
exhausted. In particular, constructing a finditer iterator is not secretly
measured as exhausting it. Returned objects, callback observations, scanner
results, and complete match details are independently checked after timing.
The raw data records both total nanoseconds and nanoseconds per operation.

All workers set and verify the actual C locale. A timeout uses a single
monotonic deadline for the complete request and response; a slowly delivered
response cannot extend the timeout indefinitely.

There are **four warmups and 31 paired rounds** per case. Seeded,
counterbalanced engine order ensures that, with Python and three candidates,
each engine is first either seven or eight times per case.

The minimum four-engine comparison has exactly:

- **3,047,424 timing rows:** 24,576 cases × 31 rounds × four engines.
- **9,142,272 correctness checks:** three exact Python comparisons per row.
- **48,758,784 timed public operations:** 16 for each timing row.

If additional independently qualified engines are included, the denominator
is explicitly 24,576 × 31 × engine count. Missing rows, duplicate rows,
timeouts, crashes, nonpositive timings, incorrect results, incorrect operation
counts, changed engines, and changed locales fail the complete test.

## From scratch means from scratch

The minimum final comparison requires independently built VM, Rust, and Zig
implementations, not three wrappers around one parser or matching engine.
Each selected engine must pass:

- All **223,198** exact frozen compatibility checks in all **49** categories.
- The full **4,494,555**-check Unicode oracle.
- All **20,480** grammar and **14,783** object-behavior checks.
- All **479** Python-observability and **34** native-boundary safety checks.
- All **393** independently frozen real-user public-contract checks.
- A complete, current, performance-blind campaign of at least **22 stages**.
- The complete from-scratch source, lockfile, native-symbol, and loaded-code
  audit.

Campaigns, public-contract results, source code, native bridges, native
engines, the static ELF audit, and actual isolated process mappings must all
agree on the exact same current file paths and SHA-256 hashes. A passing
report for a previous build cannot qualify a newer build. All five owned VM,
Rust, and Zig native artifacts and all three distinct semantic pipelines are
mandatory.

Python's re, _sre, external regex packages, PCRE, RE2, Hyperscan, Oniguruma,
another candidate, fallback engines, hidden benchmark detection, and omitted
correctness failures cannot be used as a production implementation.

## How speed and memory are scored

Each case uses all 31 paired log ratios:

    log(Python nanoseconds per operation / candidate nanoseconds per operation)

A case is statistically faster only when the lower end of its predeclared,
two-sided 95% Student-t interval is strictly greater than 1×.

The headline speed equally weights all 12 public operations, all eight
workload families, and all 256 cases in each family. Its two-sided 95%
interval uses **9,999 seeded, stratified whole-case bootstrap draws**. Complete
paired case clusters remain intact; repeated rounds are not falsely counted as
independent workload examples.

A successful replacement must meet both conditions:

- The lower end of the overall 95% speed interval is at least **1.5×**.
- At least **14,746 of 24,576 cases** are individually, statistically faster.

Every workload taking strictly more than 20% longer must be reported and
explained. For the ratio Python time divided by candidate time, the exact
threshold is strictly below **5/6**. A ratio equal to 5/6 is not counted as a
greater-than-20% slowdown.

Memory is measured separately on **1,536 balanced cases**. Python allocation
peaks from tracemalloc are labelled as Python allocations, not Rust, Zig, or C
allocation. Whole-process current and peak resident memory are reported
separately. The tracemalloc worker is not the timing worker because Python's
instrumentation imports re and _sre. Python/native argument conversion and
returned-object creation remain part of the actual timed public call.

## Reproducibility and status

The primary implementation is:

    tools/rust_v9_holdout_protocol.py

The future prospective public manifest is:

    performance/v9/holdout-manifest.json

The manifest-generating command accepts only an independently provided
SHA-256 commitment. It does not create, display, inspect, or import a secret.
The manifest, synthetic evidence, candidate freeze, raw timing rows, memory
rows, one-use marker, final case results, and later graphs must each be
committed in their own correct project phase.

Version 7 results, version 8 evidence, and version 9 results are always
labelled and reported separately. Any combined score requires weights
predeclared before either final test is opened. No final winner, expanded
holdout speed, combined speed, or corrected-candidate original-holdout result
has been measured or claimed by this document.
