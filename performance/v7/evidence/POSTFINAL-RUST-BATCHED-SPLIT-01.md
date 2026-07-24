# Post-final Rust experiment 01: batched splitting

## Result

**Rejected as a speed improvement.** The independently written Rust engine
passes every original public compatibility and no-delegation check, but batching
up to 16 split matches per native call does not meet the speed goal. On one
shared, correctness-gated 624-case comparison, Rust is `1.136×` as fast as
CPython, with a 95% range of `1.091–1.183×`, `261/624` clearly faster cases,
and `119/624` cases more than 20% slower.

The original one-time hidden experiment remains **FALSIFIED**. It was not
reopened; there is no final winner, final speed, or final ranking.

## The actual same-run comparison

All four implementations received the same 624 public cases, seven paired
trials, 499 confidence draws, and three correctness checks per observation.
The independent verifier rechecked all `17,472` original timing rows,
`52,416` correctness checks, `1,875` confidence intervals, five loaded native
libraries, and all `255` substantial slowdowns.

| Independently written engine | Speed compared with Python | 95% range | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | `1.335×` | `1.286–1.389×` | `449/624` | `47/624` |
| Zig | `1.282×` | `1.233–1.332×` | `362/624` | `89/624` |
| Rust | `1.136×` | `1.091–1.183×` | `261/624` | `119/624` |

The Rust `split` operation still has `11/47` substantial slowdowns. On the
particularly costly public case `cal.deeper.csv-split-even.22`, Python took
`706,875 ns` and Rust took `3,218,629.5 ns` in this run. On
`cal.deeper.csv-split-even.43`, Python took `13,493.7 ns` and Rust took
`73,977.3 ns`. The change cannot be credited with resolving those losses.

Rust's substantial slowdowns are fully retained: `findall 31`, `finditer 20`,
`fullmatch 21`, `search 16`, `split 11`, `match 10`, `scanner 7`, and
`escape`, `match-surface`, and `sub` one each. A specific native profiling
explanation for each slowdown is **NOT MEASURED**. The
[complete slowdown chart](postfinal-rust-batched-split-01-regressions.svg)
names all 255 losses individually instead of hiding them.

## What changed

Only Rust's owned Python/native bridge changes matching execution. Its existing
Rust-built parser, compiler, executor, and ASCII/Unicode bulk collectors remain
independent of CPython `_sre`, external regex packages, C, and Zig. The bridge
collects at most 16 matches at a time and preserves capture groups, unmatched
`None`, Python `maxsplit`, empty-match progression, Unicode code points,
borrowed buffers, descriptors, and cleanup.

- Rust bridge source: `4379d491a68f6b218a0c0feacc9295f8d2a75ffe2ac2c5e21bd68d688c212ca2`.
- Actually loaded Rust bridge: `0371f3e36fe23564562d99dae480d684a0e122fd12ffda221f62394ed84c08c3`.
- Unchanged owned Rust engine: `e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255`.
- Original 76-control, five-library no-delegation audit:
  `7c6575ee8a4dd373ebf7d59ce853fac47985b592429b9120f7d545fd184f2048`.
- Original 22-stage correctness campaign:
  `38f222f89694e13ce48bd33eb433a1234ab4da83b9e4f63b3656ac793b997413`.

The campaign passes all `223,198` matching checks, `393` public-object checks,
`479` observability checks, the complete `4,494,555`-case Unicode comparison,
replacement and callbacks, crash and recursion safety, and official Python
tests. The initial genuine independence-audit and campaign preflight failures
are separately preserved in
[the independence incident](POSTFINAL-RUST-BATCHED-SPLIT-INDEPENDENCE-INCIDENT.md).

## Reproducible evidence

- [Original compressed timing observations](postfinal-rust-batched-split-01-raw.jsonl.gz).
- [Complete public measurement](postfinal-rust-batched-split-01-summary.json).
- [Independent integrity verification](postfinal-rust-batched-split-01-integrity.json).
- [Overall speed](postfinal-rust-batched-split-01-overall.svg),
  [wins and losses](postfinal-rust-batched-split-01-outcomes.svg),
  [results by operation](postfinal-rust-batched-split-01-api.svg),
  [every major slowdown](postfinal-rust-batched-split-01-regressions.svg),
  [Python-visible allocation only](postfinal-rust-batched-split-01-memory.svg),
  and [public rankings](postfinal-rust-batched-split-01-rankings.svg).

The memory chart measures Python-traced temporary allocations. Native-engine
and isolated whole-process memory are **NOT MEASURED**. This is public
development evidence, not a successful hidden final experiment.
