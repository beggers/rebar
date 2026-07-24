# Frozen comparison: from-scratch quote-aware Rust

## Status

This is a separately versioned **public development experiment**. Its
performance, rankings, confidence ranges, memory results, slowdowns, and
winner are **NOT MEASURED** until the exact frozen protocol is committed and
pushed and the subsequent complete measurement and independent replay finish.

The original one-time hidden final remains **FALSIFIED**. This experiment
never opens, reruns, repairs, extends, or substitutes for that final.

The [frozen 4,096-case manifest](manifest.json) has SHA-256
`2228e444ae142494def731d8b94ba5fcf08c69aa8a7e04cc1c47cbebeb149b4a`.
Its [versioned runner and verifier](../../tools/postfinal_public_practice_v2.py)
has SHA-256
`c971e63550d8c2ed5e51058b33909d4ca7fe79287080e9780cfef3262606be27`.

## Independently implemented engines

Compare the pinned, unmodified CPython **3.14.6** `re` implementation with
the independently written C, Rust, and Zig candidates in the same paired run.
Each candidate retains its own parser, compiler, and matcher. No candidate
calls or wraps Python's regex engine, another regex package, or another
candidate.

The sole Rust change recognizes a mathematically proven, capture-free
quote-aware delimiter using Rust's own parsed expression. Its own engine then
scans the relevant bytes. It retains the original Rust matcher for every
expression not proved to have exactly those semantics. The exact Rust source
is SHA-256
`2750f9c77a746e019b0bcfa14ffa329b66d571d0202d9423fe67f9b0e8bd2df2`;
its actual owned native engine is SHA-256
`0bdd8072d253dadce35358814dfdadb51bb83dd3d34b2e6d6c699592e14889c7`.

The original
[76-control from-scratch audit](../../candidates/audits/FROM-SCRATCH-AUDIT.json)
has SHA-256
`b84d07c0b30ccf41af3214c9255ced18835998f19038b90e8464d5fd2d3ed5e4`.
It verifies all independent source families and all **five** actually loaded
native libraries. Its
[first failed sandboxed attempt and unchanged passing retry](../v7/evidence/POSTFINAL-RUST-QUOTE-PARITY-INDEPENDENCE-INCIDENT.md)
are both preserved.

Before this freeze, the new Rust source passed the unchanged
[223,198-case matching oracle](../../candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-02-parity.json.gz),
[393-check public-object oracle](../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-02-PARITY.json.gz),
[479-check observability oracle](../../candidates/evidence/rust-v8-observability-rust-qualified-post-final-stage-02-parity.json.gz),
and
[complete original 22-stage campaign](../../candidates/evidence/rust-v8-rust-post-final-stage-02-parity-sealed-campaign.json),
including all **4,494,555** full-Unicode checks. The unchanged qualified C and
Zig engines retain their own separately frozen matching proofs. Public
correctness does not repair the original hidden Zig failure.

An additional
[independently isolated quote-pattern oracle](../../candidates/evidence/rust-postfinal-quote-parity-stage-02-oracle.json)
checks **83,968** exact observations across **1,312** deterministically
generated cases, with **zero mismatches**. It separately compares standard
Python with the actual audited Rust source and loaded native code. It covers
escaped and Latin-1 separators, six text and byte-buffer representations,
match windows, every split limit, all scanner modes, newline-sensitive
anchors, invalid inputs, captures, case and multiline flags, lazy and bounded
repeats, and expressions the generic Rust matcher must continue to handle.
Its reference and Rust observation hashes both equal
`6e74329a7d935ccf6c1187d44dbad7a31a06f8042a5f698b5d07a5bcc0f9f959`.
It uses no performance measurement, hidden input, or external regex engine.

## Exactly the same public cases

The experiment uses exactly the same **4,096 case IDs in the same order** as
the [previous public comparison](../postfinal-public-v1/PROTOCOL.md).
The SHA-256 of either newline-separated selected-case list is
`68be2a1b6bc12063e436305861ebf560b436451d7540a03b84cab8e3231ef30a`.
The source is the unchanged **10,312-case public calibration archive**, of
which **9,731** satisfy the existing input and result limits. No private or
hidden case is generated, decoded, or accessed.

All **260** available public workload categories and all **12** public regex
operations are retained:

| Operation | Cases |
| --- | ---: |
| Compile | 210 |
| Escape | 161 |
| Find all matches | 414 |
| Iterate matches | 414 |
| Full match | 358 |
| Match | 229 |
| Match-object behavior | 241 |
| Scanner | 413 |
| Search | 414 |
| Split | 414 |
| Replace | 414 |
| Replace and count | 414 |
| Total | 4,096 |

The cases include **3,616** text, **182** bytes, **169** bytearray, and
**129** memoryview inputs; **282** cold, **3,414** precompiled, and **400**
module-level pattern uses; and empty, single, few, and many-result
workloads. Every case has equal weight.

## Frozen measurement and reporting

Use **13** shuffled paired trials of Python, C, Rust, and Zig on each case,
**4** untimed warmups, and no more than **16** actual calls per timing sample.
The frozen selection, order, and confidence seeds are `2026072401`,
`2026072402`, and `2026072403`; confidence ranges use **2,000** bootstrap
draws.

The complete denominator is **212,992** timing observations and **638,976**
exact Python-answer checks: before timing, for the allocation sample, and
after timing. Independent verification recomputes all **12,291** case and
overall confidence ranges, verifies source and loaded-library fingerprints,
and discloses every slowdown greater than 20%.

Report all candidates, all cases, all wins and losses, all compressed raw
observations, all correctness failures, and the exact 4,096-case denominators.
State whether each candidate reaches **1.5×** and whether at least
**2,458/4,096** cases are statistically faster. Do not infer a paired
confidence interval between this run and the separately measured version-1
run. Python-traced allocations are not native-engine memory; native-engine
and isolated whole-process memory remain **NOT MEASURED**.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v2 self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v2 freeze

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v2 measure \
  --exclusive-slot postfinal-public-practice-v2

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v2 verify
```

Do not measure until this exact protocol, manifest, runner, all source-bound
correctness proofs, and the original passing audit have been committed and
pushed to `main`. The complete result is **NOT MEASURED** before then.
