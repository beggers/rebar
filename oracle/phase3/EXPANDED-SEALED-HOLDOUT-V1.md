# A larger, unopened final Python `re` comparison

Status: **PRE-PHASE-3 PROPOSAL. NOT FROZEN. NOT GENERATED. NOT OPENED.
NOT RUN. Speed, memory, running time, statistical power, and required
disk space are NOT MEASURED. No replacement has qualified. No winner
has been selected.**

This proposal answers a simple question: if three separately written
replacements eventually behave exactly like Python's regular-expression
module, which one is actually faster for ordinary Python users?

It specifies **14,155,776** future cases, **3.375 times** the existing
**4,194,304**-case proposal. Both numbers describe proposals, not
existing tests. The older proposal,
`docs/EXPANDED-HOLDOUT-PROTOCOL-V1.md`, remains unchanged. This document
does not contain or create a generator, random seed, test input,
expected answer, timing, or final result. It is not permission to
start phase three.

## What has to happen first

Pinned, unmodified CPython **3.14.6** remains the reference. At least
**three independently authored engine families** must each actually
pass the complete original **31,237**-case Python suite, the separate
**8,244**-case differential and fuzz suite, callable and public import
checks, both original large-input requirements, buffer lifetime and
subinterpreter checks, an authenticated first-party native build, and
a live no-delegation audit. Each candidate must own its parser,
compiler, and matching engine. A normal Python-to-native binding is
allowed only when it calls that exact authenticated first-party engine.

Calling or wrapping Python `re`, `_sre`, PCRE, PCRE2, RE2, Rust
`regex`, Oniguruma, Hyperscan, Boost or C++ regular expressions, the
C-library POSIX matcher, ICU, Tcl, JavaScript, WebAssembly, another
candidate, a dynamic plugin, an external process, a network service,
or cached Python answers does not count. The prohibition applies to
indirect calls, imports, generated bindings, native symbols, child
interpreters, preload hooks, and fallbacks. The live guard must be
installed before candidate code loads and must remain active in every
worker and subinterpreter. Reading source code alone cannot establish
runtime independence.

At publication of this proposal, those gates remain **NOT PASSED**.
The independent reference and qualification requirements are recorded
in the following already-published documents:

- `oracle/phase1/P0-COMPLETENESS-V4.md`.
- `oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md`.
- `oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md`.
- `oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md`.
- `oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md`.
- `oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md`.
- `oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md`.

## Exactly what would be tested

The complete proposed denominator is:

`36 Python operations × 24 pattern families × 4 valid subject types`

`× 4 operation-specific lifecycle states × 1,024 distinct variants`

`= 14,155,776 independently verified and independently timed cases`.

There are exactly **13,824** equally weighted strata. Each stratum has
exactly **1,024** cases, every operation has **393,216** cases, and
every primary pattern family has **589,824** cases. Every individual
case has weight `1 / 14,155,776`. The timing denominator is exactly the
same **14,155,776** cases; there is no hidden timing sample, smaller
fast-path-only benchmark, discarded case, or substituted denominator.

The 36 prospectively named operations are:

1. Fresh compilation followed by a real search.
2. Warm, cached compilation followed by a real search.
3. Module `search`.
4. Compiled-pattern `search`.
5. Module `match`.
6. Compiled-pattern `match`.
7. Module `fullmatch`.
8. Compiled-pattern `fullmatch`.
9. Module `findall`.
10. Compiled-pattern `findall`.
11. Module `finditer`.
12. Compiled-pattern `finditer`.
13. Module `split` with keyword options.
14. Compiled-pattern `split` with keyword options.
15. Module `split` with valid positional options.
16. Compiled-pattern `split` with valid positional options.
17. Module literal `sub`.
18. Compiled-pattern literal `sub`.
19. Module callable `sub`.
20. Compiled-pattern callable `sub`.
21. Module literal `subn`.
22. Compiled-pattern literal `subn`.
23. Module callable `subn`.
24. Compiled-pattern callable `subn`.
25. Module `sub` with valid positional count and flags.
26. Compiled-pattern `sub` with valid positional count.
27. Module `subn` with valid positional count and flags.
28. Compiled-pattern `subn` with valid positional count.
29. Compiled scanner `search`.
30. Compiled scanner `match`.
31. Exhaustive, correctly advancing scanner `search`.
32. Exhaustive, correctly advancing scanner `match`.
33. Valid `re.Scanner` lexicon scanning.
34. Valid `re.Scanner` callback and callback-error behavior.
35. Match groups, named groups, spans, and indexing.
36. Match-template expansion.

Cases have exactly one of 24 disjoint, prospectively assigned primary
pattern labels: single literal; multiple-character literal; anchored
literal prefix; disjoint alternation; overlapping alternation; greedy
unbounded repeat; lazy unbounded repeat; bounded repeat; possessive
repeat; atomic grouping; positive character class; negative character
class; predefined categories and type-valid flags; start anchor; end
anchor; word boundary; numbered capture; named capture; numbered
backreference; named backreference; positive lookahead; negative
lookahead; fixed-width positive or negative lookbehind; and
conditionals or correctly advancing zero-length matches. Secondary
features never create a second primary label. Scoped flags, Unicode,
ASCII, bytes-only locale rules, empty matches, successful and failing
matches, warnings, expected exceptions, callback order, and side
effects must appear in valid variants and remain correctness-gated.

Subject types are `str`, `bytes`, `bytearray`, and a genuine
`memoryview`. Of the **1,024** memory-view cases in each applicable
stratum, exactly **512** use a read-only view and **512** use a
writable view. Pattern and replacement types must match their subject.
`LOCALE` is permitted only for valid bytes-pattern cases. A compiled
pattern never receives module-only flags. Lexicon rules use the
correct pattern type. Group and template operations first obtain an
actual match. Empty scanner matches must advance exactly as in the
reference. Expected callbacks, errors, warnings, and cleanup are
observed rather than treated as missing data.

The four lifecycle states must be defined **separately for every named
operation and every legal subject** before any case can be generated.
They distinguish real fresh work, real warm cache, real compiled reuse,
and a real existing match, iterator, scanner, or other operation-valid
state. Where a generic label is not meaningful, four distinct valid
operation-specific states are required; an invented compiled method,
invalid subject, repeated state, or renamed cache hit cannot complete
a stratum. The concrete legal-domain tables and generator are
**NOT FROZEN** and **NOT GENERATED**.

## How every future timing would work

The initial design includes exactly four participants: unchanged
CPython and the **three eligible independently authored first-party
families**. Every one of the **14,155,776** cases must first pass an
untimed Python-versus-candidate correctness check for every
participant. These are **56,623,104** separately disclosed preflight
observations, not timing observations or extra cases. Every one of
the same cases must then run in each of **24** paired rounds. Each
round uses a different one of the **24** possible orders of the same
four participants, so each participant occupies every position
exactly six times. The case result is verified again for every timed
call; any mismatch, crash, unsafe behavior, or missing observation
aborts the run without dropping or replacing a case.

The prospective four-participant totals are exactly:

- **1,358,954,496** separately correctness-gated timed calls:
  `14,155,776 × 24 × 4`.
- **1,019,215,872** paired candidate-versus-Python observations:
  `14,155,776 × 24 × 3`.
- **10,871,635,968** bytes, or exactly **10.125 GiB**, for the timed
  calls' raw, unsigned, eight-byte clock values **alone**.
- **864** operation-by-family raw-clock shards, each containing
  **12,582,912** clock bytes.

These byte counts exclude identifiers, correctness data, side effects,
raw inputs, process metadata, authentication, indexes, compression,
memory records, and filesystem overhead. Actual elapsed time,
throughput, compressed size, total disk use, hardware suitability,
statistical power, and ability to finish remain **NOT MEASURED**.
No case or clock has been sampled.

Preparing inputs and checking results occurs outside the timed
interval. The complete public Python call, Python-to-native boundary,
matching, promised compilation, output creation, and object lifetime
remain inside it. The exact clock, worker isolation, CPU settings,
thermal and system-noise controls, randomized case order, participant
rotation, failures, raw record layout, and machine configuration must
be prospectively frozen after eligibility and before any secret.

If more than three independent families qualify, include **all** of
them; do not select the quickest three. Four-participant totals and
24-permutation balance then no longer apply. Before any hidden seed
exists, publish a new participant-specific balanced order, at least
24 paired rounds, and recomputed observation and storage denominators.
Do not reuse a four-participant figure for a larger comparison.

## Scores, uncertainty, memory, and slowdowns

Each candidate's case score is the geometric mean of its **24 actual
paired Python-versus-candidate ratios**. The headline score equally
weights all **14,155,776** case scores. Estimate its two-sided 95%
interval with **9,999** reproducibly seeded stratified bootstrap
replicates over all **13,824** complete strata. That is
**138,226,176** stratum selections per candidate, not evidence that
any bootstrap has already run.

For each case, use the exact two-sided paired sign test with an
explicit, prospectively fixed treatment of ties. Correct across all
**42,467,328** candidate-and-case hypotheses using
Benjamini–Hochberg at `q = 0.05`. Publish faster, slower,
inconclusive, missing, and failed counts over the same complete
denominator. A separately reported 24-round median interval is not a
multiple-comparison-adjusted significance claim.

Collect **221,184** balanced memory cases, exactly 16 per stratum,
and **55,296** balanced boundary cases, exactly four per stratum.
For four participants these produce at least **884,736** memory
observations and **221,184** boundary observations. Record
Python-visible allocations separately from actual native allocation
and resident memory. Measure a precisely matched first-party
empty-call control to describe boundary overhead, but keep the full
real boundary in every main timing. Any unobservable native memory
remains **NOT MEASURED**.

A future winner must pass every original compatibility and independence
gate; have zero unexplained failures, crashes, or unsafe behavior;
achieve a **lower 95% overall confidence bound of at least 1.5×**;
and be significantly faster after the declared correction on at least
**8,493,466 of 14,155,776** cases. Explain and publish every observed
slowdown greater than **20%**. Preserve every candidate, trial,
regression, rejection, and denominator.

## The seal stays closed

Freeze a final protocol, participant list, legal-domain tables,
generator, independent integrity review, timing schedule, accounting
rules, and reporting format only **after three eligible engines
actually pass**. Only then generate a new, domain-separated secret,
publish its commitment, and create final cases. Earlier public,
historical, or contaminated data must never contribute to the seed,
inputs, tuning, or results.

`tools/verify_expanded_sealed_holdout_v1.py` checks only the arithmetic,
this public proposal, its JSON companion, and already-published
qualification documents. Its `--self-test` and
`--verify-frozen-context` names refer only to authenticating the
**proposal's source files**; they do not freeze a final protocol,
generate a case, import a candidate or matcher, start a worker, build
native code, sample a clock, run a benchmark, or open a holdout.

Reproduce both source-only modes using the three independently
obtained file hashes:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_expanded_sealed_holdout_v1.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_expanded_sealed_holdout_v1.py --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat each with `env -i PATH=/usr/bin:/bin LC_ALL=C`. A passing
verification means only **PRE-PHASE-3 PROPOSAL VERIFIED**. The final
holdout remains **NOT FROZEN, NOT GENERATED, NOT OPENED, and NOT RUN**.
Performance remains **NOT MEASURED**. No winner is selected.
