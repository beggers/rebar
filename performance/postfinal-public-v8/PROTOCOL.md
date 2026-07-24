# Expanded public development comparison

This comparison asks a plain question: how do three independently built Python
regular-expression engines perform against the unchanged `re` module across a
much broader collection of real Python `re` operations?

Every example in this comparison is **known public development data**. The
existing calibration fixture, the generation method, the seed and all source
examples are public. No independently controlled, genuinely secret test set is
available. Consequently, the results can support development and falsification,
but **cannot be described as independent secret-test or final evidence**.

## What is fixed before any measurement

- Baseline: unmodified, isolated CPython **3.14.6** and its standard `re`.
- Comparisons: the separately owned Rust, native C and Zig candidate engines;
  each must first pass the current from-scratch, no-delegation, original Python
  compatibility, public locale and broad public correctness checks.
- Mandatory prerequisite: the finalized **Stage10** eight-category Python
  compatibility contract, before opening or expanding the V8 public fixture.
  Two independent standard-library processes must agree on **3,584** exact
  cases (**7,168** reference answers), and all three owned candidate families
  must independently pass all **10,752** candidate answers. Bind the exact
  finalized Stage10 producer and protocol, the actual two published passing
  evidence files, and matrix SHA-256
  `0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
  If any source, protocol or report changes, V8 freezing stays **BLOCKED**;
  earlier evidence is never substituted for the actual passing Stage10.
- Examples: **33,280**, made from **260 original public categories × 128
  examples each**. The exact **8,192** existing V6 cases and their frozen
  answers remain first and unchanged. Cases remain `cohort="calibration"`.
- Operations: all **12** public operations: compile, escape, findall, finditer,
  fullmatch, match, match-surface, scanner, search, split, sub and subn. Publish
  each operation's actual generated denominator. Do not guess the counts.
- Public selection seed domain: `rebar/public-development/v8`; selection
  seed **`2026072428`**. Paired-order seed domain:
  `rebar/public-development/v8/paired-order`; paired-order seed
  **`2026072429`**. Confidence-resampling seed domain:
  `rebar/public-development/v8/bootstrap`; confidence-resampling seed
  **`2026072430`**. The three purposes and three seeds are distinct; the
  runner must use the manifest's exact values. Every identity includes
  operation, pattern, flags, subject and its exact text/bytes/buffer type,
  lifecycle and complete operation arguments. Reject all collisions and
  publish the ordered identity digest.
- Measurement: **4** warmups, **13** paired trials per engine and example,
  and **2,000** deterministic resamples for every published interval.
- Subject bound: **8,192** input units. Result bound: **128** results.
- Required checked-in result sizes:
  **1,730,560** individual measurement rows;
  **5,191,680** before/inside/after correctness answers;
  **99,843** candidate confidence intervals, including each overall result;
  **266,248** process and native-binary checks.

The generation tool binds the exact SHA-256 hashes of `GOAL.md`, the original
V6 public manifest, the single-cohort public calibration fixture and manifest,
the relevant public generators, V5 from-scratch and no-delegation verifiers
and audits, the current all-candidate locale and broad Python compatibility
producers and evidence, and the Rust, native C and Zig
source/native/contract/observability evidence. Rehash all **12** actual owned
candidate source files and all **5** exact, audit-mapped native binaries. Hash
the actual V8 generator and this exact protocol dynamically immediately before
and after the two reference runs; publish both paths and hashes in the
manifest. A stale, missing, replaced, symlinked or mixed-source proof stops
generation before an output is created.

The Stage10 files are exactly
`tools/python_re_universal_public_oracle_stage10.py`,
`oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md`,
`oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json`, and
`candidates/evidence/python-re-universal-public-oracle-v10-all.json`.
Their respective frozen SHA-256 values are
`a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`,
`c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`,
`5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`,
and
`0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7`.
The production path first verifies these exact files, uses the frozen
Stage10 validator and its lossless Unicode restoration, and verifies both
baseline roles, all eight exact case categories and all three genuinely
passing candidate reports. Each candidate must retain its independently
owned native binaries, all five forbidden native-loader aliases, separately
observed public metadata, and a matching process with neither Python
introspection nor tokenization imported.

Stage07's actual 32-observation Python hash failure and Stage08's actual
256-observation Rust-isolation-harness failure are retained, hash-checked and
explicitly acknowledged in the passing Stage10 proof. They are not erased,
reclassified as successful candidate runs or substituted for the passing
Stage10 evidence. No V8 fixture is read and no V8 reference process is started
before this prerequisite has passed. The expanded manifest records this proof
under the single truthful field `stage10_correctness`.

The archived fixture contains unrelated old per-case information. The V8
fixture decoder treats that JSON field as opaque bytes: it is skipped without
deserializing, reading or using its contents. Selection depends only on frozen
public case definitions, public reference answers, categories and the declared
V8 seed. No earlier measurements, case rankings or candidate answers influence
the selection.

## Preserve and expand the public examples

Retain the original V6 descriptors, case definitions, categories, operation
arguments and reference answers exactly and in their original order. For each
of the 260 existing categories, deterministically draw additional source cases
from the pinned 10,312-case public-only calibration fixture until the category
contains exactly 128 unique semantic identities.

For matching and compilation operations, the additional case preserves the
exact source subject, flags, operation arguments, lifecycle and source
category, including its precise `text`, `bytes`, `bytearray` or `memoryview`
input. It appends a fixed-width, uniquely seeded regex comment to the source
pattern. The comment changes pattern identity but has no matching semantics.
Two separately started isolated CPython 3.14.6 processes must confirm that
each matching result is exactly the original source result. For compilation,
they must confirm that flags and capture structure remain unchanged. For the
escape operation, append a fixed-width public literal and independently compute
the exact changed standard-library answer. Fail if an identity collides, a
bound is exceeded, the category meaning changes, or the independent reference
processes disagree.

This creates genuine, uniquely identifiable public workload cases, not a new
secret dataset. The manifest must state how every new case was derived and
retain each unchanged original descriptor. Publish and independently verify
the full 33,280 per-case semantic identities and their ordered digest. The
generated cases are not a claim
that 128 independently sourced real-world examples existed for each category.

## Required execution and reporting

Do not begin measuring until both isolated CPython reference processes have
reproduced every original frozen answer and agreed on every added case. Then
qualify each candidate against every generated answer before it is measured.
Run the baseline and each of the three candidate families under identical
conditions. Check the exact reference answer immediately before, inside and
immediately after each timed trial. Use deterministic paired ordering without
branching on a candidate name or an observed result.

Publish all raw rows, all examples, all four engines, all category and
operation denominators, all paired intervals, and every loss. Report each
overall candidate result relative to standard Python as a geometric-mean
speedup with its confidence interval, the number and percentage of examples
on which it is statistically faster, and every example where candidate time
exceeds **120%** of baseline time. Never omit losses, alter denominators after
seeing results, select a winner in advance or freeze a replacement protocol.

Report process resident memory and Python-traced allocations separately. A
Python allocation tracer does not observe all allocations inside a C, Rust or
Zig engine. Exact inside-native allocations are **NOT MEASURED**. Unless
separately and explicitly instrumented, standalone interpreter startup and
isolated Python-to-native call-boundary costs are **NOT MEASURED**; an
end-to-end operation may include those costs without identifying them.

The tool's `--self-test` is exclusively synthetic and in memory. It does not
open a real fixture, generate a real case, write a manifest, run an oracle,
import a candidate, start a worker or measure time. Every clock, real file,
compressed fixture, process and output operation is actively blocked and
poison-tested. Real generation requires a separate, explicit `--freeze`
action and creates its output only after every provenance, category,
uniqueness and independent-reference gate has passed.
