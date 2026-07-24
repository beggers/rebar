# Frozen comparison: one-pass Rust pattern calls

## Status

This is an additive **public development experiment**. Performance, speed,
confidence ranges, regressions, memory, rankings, and a winner are **NOT
MEASURED** until this protocol, all candidate source and correctness proofs,
and the predetermined graphs have been pushed, followed by one complete
measurement and an independent raw-data replay.

The original one-time hidden experiment remains **FALSIFIED**. No hidden
case, final marker, final seed, or held-out result is accessed or retried.

The [frozen public manifest](manifest.json) has SHA-256
`5f49f255271b8f71786e7fa67a61827b53c1330e1ad7afe29c8750991df4b90f`.
Its [pinned runner](../../tools/postfinal_public_practice_v3.py) has SHA-256
`aa2b22de82894dc41622378d1bd782636358fa360454be37f3b8fedbc6e4989a`.

## What changed

The Rust engine, parser, compiler, and matcher remain independently written.
Its native Python bridge now acquires ordinary compiled-pattern metadata in
one guarded pass. It applies the same safe mechanism to matching, finding,
scanning, splitting, and replacement. It keeps strong references and preserves
the complete original fallback for custom descriptors, overridden attributes,
changed type versions, audit hooks, free-threaded builds, unusual arguments,
template initialization, errors, and mutable buffers.

The exact [native bridge source](../../candidates/rust/py_bridge.c) has
SHA-256 `bad5961266b4697f4c6fde8a0658319c85c9c97f2583de75718262fcc54b2f61`.
No production candidate calls standard-library `re`, `_sre`, another
candidate, or an external regex library.

The original
[76-control from-scratch audit](../../candidates/audits/FROM-SCRATCH-AUDIT.json)
has SHA-256
`d53d9dbfdd1d43284cefdbd189ff29ca181de9c49789da41ce11b5f138430999`.
It verifies all independent candidate families and all five actually loaded
native libraries. Before the public freeze, the precise candidate passed its
fresh [223,198 matching checks](../../candidates/evidence/rust-v7-edge-oracle-rust-post-final-stage-03-slot-batch.json.gz),
[393 public-object checks](../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POST-FINAL-STAGE-03-SLOT-BATCH.json.gz),
[479 observability checks](../../candidates/evidence/rust-v8-observability-rust-qualified-post-final-stage-03-slot-batch.json.gz),
and [complete 22-stage campaign](../../candidates/evidence/rust-v8-rust-post-final-stage-03-slot-batch-sealed-campaign.json),
including all **4,494,555** full-Unicode checks.

The exact source and loaded binary also pass
[83,968 quote-pattern comparisons](../../candidates/evidence/rust-postfinal-quote-parity-stage-03-slot-batch-oracle.json)
across **1,312** independently generated cases with zero mismatches. Their
reference and Rust observation hashes match exactly; their pinned workers
block Python's regex engine, external regex packages, and other candidates
from the Rust process.

## Fixed public cases

Use the same **4,096 public cases in the same order** as the complete
[version-2 comparison](../postfinal-public-v2/RESULTS.md). The SHA-256 of
both newline-separated case lists is
`68be2a1b6bc12063e436305861ebf560b436451d7540a03b84cab8e3231ef30a`.

The unchanged source contains **10,312** public calibration cases, of which
**9,731** meet the unchanged safety bounds. The selection contains all **260**
public workload categories, all **12** public APIs, every observed lifecycle
and input representation, and equal case weights.

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

## Fixed measurement

Pinned CPython **3.14.6**, C, Rust, and Zig receive **13** shuffled paired
trials per case, **4** warmups, no more than **16** genuine regex calls per
sample, and **2,000** predetermined confidence resamples. The fixed public
selection, order, and confidence seeds are `2026072401`, `2026072402`, and
`2026072403`.

Record all **212,992** raw observations and all **638,976** correctness
checks. Independently recompute all **12,291** confidence intervals, validate
all source and loaded-binary fingerprints, display all three candidates,
report all substantial slowdowns, and preserve complete raw data and six
deterministic graphs. The overall speed target is **1.5×**; the faster-case
threshold is **2,458 of 4,096**. Never claim paired confidence between
separate runs or omit an observed loss.

Python-visible temporary memory is not native-engine memory or isolated
whole-process memory; both remain **NOT MEASURED**.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v3 self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v3 freeze

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v3 measure \
  --exclusive-slot postfinal-public-practice-v3

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. "$PY" -B \
  -m tools.postfinal_public_practice_v3 verify
```

Do not time a candidate until this complete protocol, exact manifest, source,
full correctness proofs, from-scratch audit, and graph verifier have been
committed and pushed to `main`.
