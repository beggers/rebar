# Expanded public comparison: corrected V10

This experiment asks how three independently implemented Python regular-
expression engines compare with the unmodified `re` module across a broader,
balanced collection of real Python operations. It does not wrap or substitute
another regex package. The three candidates are the separately owned Rust,
native-C and Zig implementations.

Every example, seed, source fixture and generation rule is public development
data. No independently controlled secret test set exists. Results are not a
secret holdout, final qualification or evidence that all Python `re` programs
are faster.

## Preserve the real failed experiment

The pushed V8 experiment failed before it created a manifest, started a
candidate or collected a timing. Its original public fixture correctly hashes
result values as unescaped UTF-8 JSON. V8 incorrectly checked those values as
ASCII-escaped JSON. Exactly 577 of 10,312 genuine public records fail the
incorrect check: 483 `findall`, 48 `escape` and 46 `split`. The first failure
is `cal.unicode.words`.

V10 never edits, overwrites or reclassifies that failure. Before accessing a
fixture or starting a reference process, authenticate these exact artifacts:

- `tools/postfinal_public_expansion_v8.py`:
  `e921d5962746d564381a0a11d22eb125b080370b572ffd0f630e925025f1ec97`.
- `tools/postfinal_public_practice_v8.py`:
  `7818577b36bb822cc99e02a07fcd5ba74e20f1ecf6f0dcb3c0913d2a97bd244f`.
- `performance/postfinal-public-v8/PROTOCOL.md`:
  `e19d504f6d7504b4052f2bbfbc0a584596178919c5396e076d3e6261356a2095`.
- `tools/postfinal_public_expansion_v8_failure.py`:
  `800963bc33227c936a2f8506fa80057672acb1c831b772a1bb412aec6540eb94`.
- `performance/postfinal-public-v8/evidence/postfinal-public-freeze-failure-v8.json`:
  `e46a5b0482293a016c1ba6d0bcadb4c5bcf97ea15af9a2027734ac855c688aba`.

Validate the entire recorded failure, both actual reproduction commands, the
10,312/577 denominators, first case, both result hashes, all affected
operations, the zero deserialized archive-history values and the absence of
candidate execution and timing. Bind one exact 18-field `v8_failure` proof in
the new manifest.

## Two separate hashes

Structural JSON, deterministic selection, case identity, manifests, process
requests and provenance use sorted, ASCII-escaped canonical JSON.

Only an actual Python regex **result** uses the original fixture producer's
exact result codec:

```python
hashlib.sha256(
    json.dumps(
        result,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
```

Use that codec for all 10,312 original fixture answers, both independently
started reference workers, every preserved original answer, every generated
answer, the frozen manifest and every later candidate correctness gate.
Neither digest silently replaces the other. Invalid UTF-8, including a lone
surrogate in a result, fails closed.

## Before any measurement

- Pin the unmodified isolated CPython **3.14.6** baseline.
- Retain all three independently audited Rust, native-C and Zig candidates,
  their 12 exact owned source files, five actual native binaries and all V5
  from-scratch, no-delegation, locale and broad compatibility proofs.
- Authenticate the exact already-pushed public V7 manifest
  `performance/postfinal-public-v7/manifest.json` with SHA-256
  `465c751c6756cbea73bc3dc6d4397e2777d04a107b9a607241697b148c9c5f26`,
  together with its already-frozen V7 generator and protocol. Require its
  8,192 selected cases, ordering, operation counts and all 260 category
  counts to exactly equal the pinned public V6 parent. Bind both the V6 and
  V7 parent paths and hashes in the new manifest; never read an earlier
  timing, archived result, holdout or final case to check this parity.
- Require the already passing eight-category Stage10 correctness contract.
  Authenticate the producer, protocol and two genuine passing reports with
  SHA-256 values `a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`,
  `c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`,
  `5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`
  and `0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7`.
  Require 3,584 cases, two agreeing Python processes, 7,168 reference answers,
  10,752 passing candidate answers and case-matrix hash
  `0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.
- Preserve the genuine earlier 32-observation Python-oracle failure and
  256-observation Rust-harness failure. Require all five forbidden native
  loader aliases and the separately guarded, isolated candidate families.
  Record precisely the agreed 13-field `stage10_correctness`; do not substitute
  another stage or report.
- Before freezing, an explicitly selected, read-only `--verify-public-fixture`
  can independently check all 10,312 public answers. It uses the frozen
  selective JSON decoder, observes all 10,312 opaque history keys, deserializes
  none of their values, confirms all UTF-8 hashes, reproduces the 577 incorrect
  ASCII comparisons, authenticates the exact pushed V6 and V7 parents and all
  8,192 matching original descriptors, and never creates a manifest, runs a
  candidate, starts a worker, samples a clock or measures performance.
- The complete 10,312-record public source archive includes exactly **9,731**
  workloads eligible under the original subject and result safety limits and
  **581** valid but ineligible source records. Authenticate the result of
  every archived record; never reject or conceal an archive record merely
  because it is too large to measure. Exclude every ineligible record from
  original selection, generated templates, reference workers and measurement.
  Publish both exact eligibility denominators and the 12 original bounded
  operation capacities.
- Expand the public fixture to **33,280** cases: the same **260** categories,
  exactly **128** cases in each, with the exact **8,192** original cases,
  descriptors, answers and ordering preserved first.
- Retain all 12 APIs: compile, escape, findall, finditer, fullmatch, match,
  match-surface, scanner, search, split, sub and subn. Publish actual operation
  counts instead of estimating them.
- Preserve exact `str`, `bytes`, `bytearray` and `memoryview` subjects,
  pattern flags, complete API arguments and operation lifecycles. Reject
  duplicates, identity collisions, changed original descriptions, inputs
  exceeding 8,192 units and results exceeding 128 values.
- Use domain `rebar/public-development/v10`; selection seed **2026072450**.
  Use `rebar/public-development/v10/paired-order` and seed **2026072451**
  for pairing; use `rebar/public-development/v10/bootstrap` and seed
  **2026072452** for confidence resampling. The domains and seeds remain
  distinct and fixed before measurement.
- Dynamically bind the exact V10 generator, this protocol and the separately
  authored V10 measurement runner. Rehash all three immediately before and
  after the independent reference workers. Never invent a circular static
  source hash.

## Generating additional public cases

For each original category, deterministically select public calibration
templates with the frozen V10 seed. Preserve all source operation arguments,
input types, lifecycle and flags. For matching and compilation, append a
fixed-width, deterministic, semantically inert regex comment. For `escape`,
append a fixed-width public literal and compute the changed answer. Use fresh
V10 case identities; preserve all 8,192 original identities unchanged.

Two separately started pinned, isolated CPython reference processes must
reproduce every original fixture result and independently agree on all
33,280 cases before a manifest is exclusively created. For generated matching
cases, require the exact original matching result; for compilation, require
unchanged flags and capture structure. The source archive's unrelated
`historical` field is always skipped without JSON deserialization. Previous
timing, case rankings, candidate answers, private cases and final data are not
inputs.

## Measurement and reporting

Freeze **4** warmups, **13** paired trials per operation and engine and
**2,000** deterministic confidence resamples. Before timing, independently
qualify every candidate against every generated reference answer. Check the
correct answer before, during and after every timed observation. Run all four
engines under identical conditions.

Publish **1,730,560** raw rows, **5,191,680** before/inside/after answers,
**99,843** confidence intervals and **266,248** process/native checks.
Publish every category, operation, candidate, regression and denominator.
Report overall geometric-mean speedup relative to Python `re`, confidence
intervals, the number and share of statistically faster cases and every case
more than **20%** slower. Do not remove losses or choose a winner early.

Report process memory and traced Python allocations separately. Exact
inside-native allocation, standalone interpreter startup and standalone
Python-to-native call costs are **NOT MEASURED** unless separately and
truthfully instrumented. Public development data remains public, and a
performance goal is **NOT MET** until the predeclared conditions are actually
measured and passed.

The generator's `--self-test` is exclusively in memory and explicitly blocks
real files, gzip, subprocesses, clocks and manifest creation. The read-only
public fixture verification is separate. Only an explicit later `--freeze`
may start the two baseline workers or exclusively create the V10 manifest.
