# Rust repeat research

This is a record of two from-scratch Rust regular-expression experiments. It
preserves unsuccessful attempts as well as the fixes. Neither experiment uses
another regular-expression package or delegates matching to Python.

The detailed, reproducible record is
[rust-v6-repeat-lab.json.gz](rust-v6-repeat-lab.json.gz). It contains the actual
Rust source snapshots, all reported failures, frozen correctness results,
official CPython test results, every timed case, every regression, the original
paired timing rows, confidence intervals, and SHA-256 integrity checks.

All development timings below use the frozen **calibration** examples. Final
holdout performance: **NOT MEASURED**. A faster result in this research does
not establish that the complete Rust candidate is faster than Python `re`.

## Counting slowdowns correctly

An implementation is **more than 20% slower** only when its elapsed time is
more than `1.2 ×` the comparison time. Equivalently, its speedup is strictly
below `5/6`, not `0.8`. Exactly 20% slower is not included.

Some original measurement reports use the historical `0.8` cutoff. The archive
retains those reports and raw timing rows byte-for-byte, recomputes every case
using the correct boundary, and verifies paired trial counts, frozen seeds,
confidence intervals, and unchanged case denominators.

| Calibration experiment | Cases | >20% slower than previous Rust | >20% slower than Python |
| --- | ---: | ---: | ---: |
| First corrected repeat counter | 42 | 11 | 39 |
| Compact repeat counter | 42 | 9 | 39 |
| General lazy-match comparison | 56 | 6 | 43 |
| Larger lazy-match inputs | 64 | 7 | 60 |

## Repeating complicated expressions

The original Rust engine produced **24 differences** from CPython when a
repeated expression was itself allowed to consume different amounts of text.
The first attempted fix still produced **8 differences**. Both complete failure
lists are retained, not discarded.

For example, Python does not match `(?:a{1,2}){2,4}+` against `aa`. Making
only the outer repetition possessive is not enough: each individual iteration
must also remain atomic. Treating this as an ordinary atomic group produces a
plausible but incorrect match.

The corrected Rust implementation uses a compact repeat counter and restores
that counter when the search backtracks. Small repetitions retain their simpler
existing representation. Large and unbounded repetitions no longer require
expanding billions of instructions. Possessive repetitions preserve the exact
per-iteration behavior of CPython.

The isolated implementation and its integrated Python-facing overlay both pass
**343,436** seeded comparisons against pinned CPython 3.14.6, with zero
differences. The same overlay additionally passes:

| Compatibility check | Passing checks | Failures |
| --- | ---: | ---: |
| Frozen correctness version 2 | 8,244 | 0 |
| Frozen correctness version 3 | 44,084 | 0 |
| Frozen performance-case answers | 12,432 | 0 |
| Extra public-interface and Unicode checks | 53,432 | 0 |
| Official CPython regular-expression tests | 144 | 0 |

Two official tests have the original recorded skips. There are no crashes or
timeouts. These totals describe separate, partly overlapping checks and must
not be added together as a count of independent Python behaviors.

Two separate **42-case**, five-trial calibration comparisons preserve the first
corrected counter and the subsequent compact hybrid. Every result, regression,
timing row, and confidence interval is retained. These are architectural
experiments, not holdout results. The first counter measures **0.892×**
relative to the preceding Rust engine, with **11** individual slowdowns over
20%; the compact hybrid measures **0.899×**, with **9** such slowdowns. Neither
counter is claimed to be a performance improvement.

## Stopping lazy searches from rereading the entire input

The old Rust engine scanned to the end of the available text before attempting
the shortest possible match for patterns such as `.*?`. For quoted strings,
Markdown fences, and source comments, repeating that scan for every match made
larger inputs unnecessarily slow.

The corrected implementation checks only the minimum required characters. If
the rest of the pattern does not match, it checks exactly one additional
character before trying again. It preserves bounded repetitions, captured
groups, matching order, byte inputs, Unicode inputs, windows, lookarounds, and
possessive behavior.

It passes the same **343,436** seeded comparisons, **53,432** extra
public-interface checks, all three frozen correctness gates, and all **144**
executable official CPython tests without failures, crashes, or timeouts.

The first paired pilot covers **56 frozen calibration examples** across **14**
workload families and seven trials. Its overall change is **0.980×** relative
to the preceding Rust implementation: the smallest cases do not establish an
overall improvement, and **6** cases slow down by more than 20%. In particular,
the four small configuration-file cases have a **0.682×** geometric-mean
result. Those regressions and their raw timing rows remain in the archive.

The second paired pilot measures **64 calibration cases** covering four
families and 16 input sizes per family, with seven trials and all answers
checked against CPython:

| Type of work | Corrected Rust versus previous Rust | Largest observed gain |
| --- | ---: | ---: |
| Extract quoted strings | 2.84× | 15.39× |
| Read Markdown and code blocks | 2.65× | 13.65× |
| Remove source-code comments | 1.79× | 6.74× |
| Read configuration lines | 0.81× | 1.08× |
| All 64 calibration cases | 1.82× | — |

The slower configuration-file results are shown deliberately. On larger
configuration inputs, the change ranges from approximately **1.00× to 1.08×**;
short inputs account for the overall regression. The archive retains each
individual case, including all **7** direct slowdowns over 20%, instead of
removing slower results or changing the denominator.

Relative to Python itself, the four-family calibration result changes from
**0.276× to 0.510×**. Both numbers are still slower than Python, and neither is
a final holdout result.

## Next experiment

An additional exact first-byte filter for lazy matches is retained as a separate
candidate, not as an integrated engine change. It passes the **343,436**
repeat comparisons, **53,432** hidden public-interface checks, all frozen
correctness gates, and all **144** executable official CPython tests.

A new, independently seeded differential also checks **219,587** outcomes
from **4,257** patterns, including changed backreferences, high-byte strings,
**3,823** non-ASCII inputs, empty matches, nested captures, and **11,186**
additional partial or inverted search-window and scanner checks. It reports
zero differences.

This first-byte candidate has not been integrated or timed. Its performance
and final holdout results are **NOT MEASURED**.

## Verify and reproduce

The archive generator only reads previously captured evidence. It does not run
the candidate, modify a frozen fixture, or benchmark the holdout.

```sh
REBAR_REPEAT_PYTHON=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
"$REBAR_REPEAT_PYTHON" tools/rust_repeat_lab.py verify
"$REBAR_REPEAT_PYTHON" tools/rust_repeat_lab.py capture \
  --research-dir /tmp/rebar-rust-counter-research.XuFUZd
"$REBAR_REPEAT_PYTHON" tools/rust_repeat_lab.py verify
"$REBAR_REPEAT_PYTHON" tools/rust_repeat_lab.py extract \
  --directory /tmp/rebar-rust-repeat-lab-replay
```

Verification checks every embedded source hash, every original failure, every
corrected gate, every paired raw-data hash, the frozen-fixture identity, all
individual comparisons, and that no holdout case entered a calibration run.
The gzip archive is deterministic: the same recorded inputs produce exactly the
same compressed bytes. Extraction restores the original source, gate reports,
and raw timing files byte-for-byte and refuses to overwrite an existing file.
