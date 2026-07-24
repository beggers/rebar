# A fair public comparison of three independently built Python regex engines

Status: **PROSPECTIVE. NOT MEASURED.** A one-time manifest may be frozen
only after this exact source and protocol are committed and pushed.
Measurement remains forbidden until the resulting manifest is also committed
and pushed. The existing **65,536-case final test has not been opened**. The
**8,192 cases below are public development examples, not a blind or held-out
test**.

Compare unmodified CPython **3.14.6** with three regex engines independently
written from scratch in Rust, C, and Zig. None may wrap an external regex
package, use Python's regex engine, call another candidate, fall back to another
implementation, or recognize the benchmark. Preserve all earlier reports and
the original, unchanged [`GOAL.md`](../../GOAL.md), SHA-256
`e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.

## The current public comparison

Use exactly the **8,192** equally weighted, unique public development examples
in the frozen version-six public manifest. Preserve the original input,
expected result, category, operation, and lifecycle. Include all **260**
workload categories and all **12** public operations:

| Python operation | Examples |
| --- | ---: |
| `compile` | 210 |
| `escape` | 161 |
| `findall` | 2,040 |
| `finditer` | 2,041 |
| `fullmatch` | 358 |
| `match` | 229 |
| Match-object access | 241 |
| `scanner` | 427 |
| `search` | 1,057 |
| `split` | 451 |
| `sub` | 447 |
| `subn` | 530 |
| **Total** | **8,192** |

Use selection seed `2026072404`, paired-order seed `2026072405`, and
confidence seed `2026072406`. Run **four warmups**, **13 paired trials**, and
**2,000** predeclared confidence resamples. Include compiled, module-level,
and cold-start calls; text, bytes, byte arrays, and memory views; and the
original result-count groups.

Publish all **425,984** timed observations, **1,277,952** exact-result checks,
**24,579** confidence intervals, and **65,544** process and native-library
guards. Publish every operation, category, case, denominator, and slowdown.
Never remove an inconvenient example or change a denominator after the fact.

## Prove that every engine is independently written and correct

Require both current version-five, independently source-bound checks:

- [From-scratch source audit](../../candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V5.json),
  SHA-256
  `42bd73acf6831b67df9a9873fa35c1882f2af09c41933774ba841d2290e6c198`:
  all **12** current candidate source files, all **five** native libraries,
  **76** original checks, and **198** current verifier checks.
- [No-delegation audit](../../candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V5.json),
  SHA-256
  `50031133a2aa20b1ef91b126a883a622d916f582fdcbea4ba1763267199c03bb`:
  **76** inherited checks, **32** independent production checks, **676**
  current verifier checks, and the separately authenticated original guarded
  worker. Reject any external regex package or another engine's parser,
  compiler, or executor.

Require the [genuine-locale CPython compatibility report](../../oracle/cpython-3.14.6/evidence/postfinal-locale-v1-all.json),
SHA-256
`bc17ee74409543d1b57f3aee65088e990ab21ac83dc75ac46fbd1f97f04b6621`.
The unchanged CPython baseline, Rust, C, and Zig must each pass all **146**
selected official tests: **584 actual test results**, with no skipped test,
failure, crash, or timeout. The real ISO-8859-1 and UTF-8 locales must also
pass both official compiled-locale tests. A historical **144-test** snapshot
is not a substitute and cannot qualify any current engine.

Require the [all-engine public Python compatibility report](../../candidates/evidence/python-re-universal-public-oracle-v6-all.json),
SHA-256
`bf4f7cc82c876ee54e55c0971c65db209f6fdf0c8b00baa8c57fbc5f460b1528`:
**1,179,648** completed comparisons against CPython, **8,192** deterministic
public inputs, **48** observations per input per engine, **16** grammar
groups, **16** input groups, **32** examples per group, and zero mismatches.

Also require the
[current, independently source-bound Python compatibility suite](../../tools/python_re_universal_public_oracle_stage10.py),
SHA-256
`a24cfa72f44931c76b425ea3eb6568ff67dc87236c8d5fe930837a14c2f58f08`,
and its
[frozen compatibility protocol](../../oracle/cpython-3.14.6/PUBLIC-CONTRACT-V10.md),
SHA-256
`c0194ee2ef1e32bd64dc646e2f395bee6036b9c053e31d95ebb3cfbc52b0a543`.
Its **3,584** examples include public Python functions and signatures,
invalid patterns, real system locales, byte-buffer ownership and lifetime,
match-object behavior, callbacks and scanners, patterns shared among threads,
and difficult Unicode text. The exact eight-category example list is bound to
SHA-256
`0233ca9bc1229b2f905192f9b8ae0c0268b7d23ba3621124192993c6d486f3db`.

First require the
[passing independent-CPython comparison](../../oracle/cpython-3.14.6/evidence/public-contract-v10-self-oracle.json),
SHA-256
`5207ca3829216b9482f0b5a2928b339261e2c51d673cce7d80da0f4f4622a8f9`.
Two separate standard-Python references perform **7,168** checks and agree on
all **3,584** examples. Then require the
[passing report for all three from-scratch engines](../../candidates/evidence/python-re-universal-public-oracle-v10-all.json),
SHA-256
`0af512f940ce7c28e50c1977794e3fbb8a2c33206e77dd2379d4fa12b391fec7`.
Rust, C, and Zig each match Python on all **3,584** examples: **10,752** new
engine comparisons, zero mismatches, and **1,190,400** cumulative public
comparisons including the preserved earlier suite.

For each engine, inspect all **256** public signatures in a process separate
from production matching. Verify all five native-library loading routes are
blocked, cached Python-regex aliases are poisoned, and the matcher loads
neither Python inspection nor tokenization machinery. The exact signature
observation is bound to SHA-256
`41dde3a1364426a1d4d9fe34136e987fce29afd54a0eaf2cdea4d2032a6cac65`.

Preserve the
[original independent-reference failure](../../oracle/cpython-3.14.6/evidence/public-contract-v7-self-oracle-failures.json),
SHA-256
`765e635745a7e332a1bd22426065c43fd52036d013add0d88d840d8fde1121e0`,
with all **32** nondeterministic hash observations. Also preserve the
[original Rust-observer failure](../../candidates/evidence/python-re-universal-public-oracle-v8-rust-failures.json),
SHA-256
`f509cedf5f58d1c211b63177fb843bfba3dc0b132469a392df43a9c802e323b1`,
with all **256** test-harness failures and all **3,328** separately passing
matching observations. These reports document defects in previous test and
observation harnesses; they must never be hidden, discarded, or described as
production-engine matching failures.

Independently require all nine source- and native-library-bound proofs:

| Engine | 223,198 matching checks | 393 Python-object checks | 479 visibility and callback checks |
| --- | --- | --- | --- |
| Rust | [Matching](../../candidates/evidence/rust-v7-edge-oracle-rust-postfinal-locale-v1.json.gz) | [Objects](../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-POSTFINAL-LOCALE-V1.json.gz) | [Callbacks](../../candidates/evidence/rust-v8-observability-rust-qualified-postfinal-locale-v1.json.gz) |
| C | [Matching](../../candidates/evidence/rust-v7-edge-oracle-vm-postfinal-locale-v1.json.gz) | [Objects](../../candidates/audits/RUST-V8-DEEP-CONTRACT-C-POSTFINAL-LOCALE-V1.json.gz) | [Callbacks](../../candidates/evidence/rust-v8-observability-vm-qualified-postfinal-locale-v1.json.gz) |
| Zig | [Matching](../../candidates/evidence/rust-v7-edge-oracle-zig-postfinal-locale-v1.json.gz) | [Objects](../../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-POSTFINAL-LOCALE-V1.json.gz) | [Callbacks](../../candidates/evidence/rust-v8-observability-zig-qualified-postfinal-locale-v1.json.gz) |

Finally, require three **new, separately produced, passing version-five sealed
campaigns** from the same
[independently source-bound version-five controller](../../tools/rust_v8_multi_candidate_campaign_postfinal_v5.py),
SHA-256
`50a39f8338b176b9376cac1437a7c0aaeb343594af0ebfea797a7beea04e86d9`.
The controller must also authenticate its actual version-four ancestor,
SHA-256
`67a7555976ab60c371c9aad1b7f94c112bd1c6aaf990e39c02f4484f3010e799`:

- Rust: [passing, independently verified version-five campaign](../../candidates/evidence/rust-v8-rust-postfinal-locale-v5-sealed-campaign.json),
  SHA-256
  `bdc10bbdf1f6a7711283826b04c1fe7f4ab700a7cf97d4c8f0595d20cab80024`.
- C: [passing, independently verified version-five campaign](../../candidates/evidence/rust-v8-vm-postfinal-locale-v5-sealed-campaign.json),
  SHA-256
  `3156b02d4dd428b82c6c3947b620fa046330234b1ce0fd66058dff4a3d0c6d16`.
- Zig: [passing, independently verified version-five campaign](../../candidates/evidence/rust-v8-zig-postfinal-locale-v5-sealed-campaign.json),
  SHA-256
  `e9a096349fd3b3cd9c91464b6033880ef9f2d30dece18e04d0c2a79efc6812cf`.

Each report must authenticate its actual version-five producer path and source
hash, current candidate, both current audits, actual matching proof, genuine
locales, all **146** individually identified official tests, all **22**
successful and correctly ordered stages, and **4,494,555** passing
full-Unicode checks. Historical version-one through version-four campaigns
remain preserved but cannot substitute for a new version-five campaign. Until
all three actual reports independently pass, this protocol cannot be frozen or
measured.

## Measure and report without hiding losses

The planning process must never import a candidate. A later authorized
measurement must use four separate, persistent, guarded processes: unchanged
CPython and one process per independent engine. Check every candidate's answer
against CPython before and after the timed operation. Keep process
communication and answer checking outside the measured operation while
separately publishing startup and Python-to-native boundary costs.

Publish a single clearly labeled speed comparison for Rust, C, and Zig against
the same baseline: **1×** means equal to CPython; higher is faster. Include
paired **95%** uncertainty intervals and show separate, exhaustive counts for
faster, uncertain, and slower cases, always out of **8,192**. A case counts as
statistically faster only when its entire interval is above **1×**. Publish
every case more than **20%** slower, not a selected sample.

Report process resident memory and Python-traced allocations separately. Exact
allocation inside a native engine is **NOT MEASURED** unless separately and
directly instrumented. The **1.5×** overall speed target and the requirement
that at least **60%** of cases be statistically faster cannot be claimed until
complete evidence is verified.

The one-time manifest, this protocol, the exact version-seven runner, and
`GOAL.md` must be committed and pushed on `main` before an explicit
version-seven measurement is accepted. Freezing may read only pinned public
cases and explicitly named correctness proofs. It must not inspect historical
speed results, start an engine, take a timing, or open either a final test or
any case selected by a private seed.

## A larger public comparison is a separate future protocol

A larger public development comparison must not silently change these
**8,192** examples or claim to be blind. A proposed separate version can use
exactly **33,280** examples: **128** independently generated examples in each
of the **260** categories. Preserve the original **8,192** public examples,
generate exactly **25,088** additional distinct examples from a frozen public
seed, and obtain every expected answer from isolated, unmodified CPython.

The current public cases include **72** categories containing only one
example. Equal category coverage therefore needs genuine new generation; it
cannot be created by repeating the existing fixture. Equal category coverage
also changes the current balance among the **12** operations. Declare the
actual operation, lifecycle, input, and result-count totals before measuring;
do not claim the old operation totals are preserved.

With the same **13** trials and **2,000** confidence resamples, this separate
design would require **1,730,560** timed observations, **5,191,680** exact
answer checks, **99,843** intervals, and **266,248** process guards. Its
runtime and memory requirements are **NOT MEASURED**. A separately frozen
and pushed public practice protocol is required first.

## A genuinely blind expanded final test requires an external steward

A proposed new blind final test contains **266,240** privately generated
cases: **1,024** in each of the **260** categories. An independent external
steward must privately generate and commit to a fresh **256-bit** seed and
the exact generator source before the protocol is frozen, committed, and
pushed. The implementation authors, engines, and public repository must never
receive the seed or cases in advance.

Only that steward may generate and evaluate the cases in a separate,
network-disabled environment against pinned CPython and the frozen candidate
binaries. Publish the signed seed commitment, exact case identifiers,
category and operation denominators, correctness outcomes, paired
measurements, uncertainty intervals, and every regression without publishing
the private case inputs prematurely.

At **13** paired trials, the proposed blind test would require
**13,844,480** timed observations, **41,533,440** exact-result checks,
**798,723** intervals, and **2,129,928** process guards. An independent
steward, isolated execution environment, elapsed runtime, and memory budget
are **NOT AVAILABLE OR NOT MEASURED**. This is a prospective design, not a
generated, opened, or completed test. The existing **65,536-case** sealed
final test remains **NOT OPENED**.

The public version-seven comparison is **NOT MEASURED**. No final winner or
final-test result has been established.
