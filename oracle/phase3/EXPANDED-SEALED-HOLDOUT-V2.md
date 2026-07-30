# An expanded, still-unopened Python `re` final comparison

Status: **PRE-PHASE-3 PROPOSAL. NOT FROZEN. NOT GENERATED. NOT OPENED.
NOT RUN. Speed, memory, elapsed time, confidence, machine suitability,
and actual total storage are NOT MEASURED. No candidate has qualified.
No winner has been selected.**

This is only a transparent successor proposal for a more detailed final
performance comparison. It neither replaces nor modifies the original
**4,194,304**-case proposal or the preserved **14,155,776**-case V1
successor. Those two immutable public proposals, including V1's
verifier, are authenticated as small plaintext sources. Their cases
have not been generated or opened. The proposed **141,557,760** future
cases are exactly **10 times** V1 and exactly **33.75 times** the first
proposal. None exists. This document contains no generator, hidden
input, case, answer, random seed, commitment secret, benchmark, timing,
memory measurement, candidate execution, or performance result.

## The existing phase gate is unchanged

Nobody may freeze, generate, or open a final holdout until at least
**three distinct independently authored candidates** each actually pass
the **complete original 31,237-case P0 suite** in all 13 original
groups, the separate 8,244-case differential suite, public-entrypoint
and callable compatibility, both original large-input requirements,
buffer ownership and cleanup, subinterpreter isolation, authenticated
first-party native provenance, and **live runtime no-delegation**.
The qualified count remains **zero**. A source inspection, partial P0
pass, private waiver, public practice result, favorable timing,
different binding around the same engine, or merely plausible candidate
does not satisfy the gate.

Each candidate must own its parser, compiler, and matching engine.
Python `re`, `_sre`, PCRE, PCRE2, RE2, Rust `regex`, Oniguruma,
Hyperscan, Boost, C++ or POSIX regular-expression implementations,
ICU, Tcl, JavaScript, WebAssembly, another candidate, plugins,
external processes, network matching, cached oracle answers, and hidden
fallbacks remain prohibited. The authenticated live guard must start
before candidate import/native loading and remain effective in every
worker and subinterpreter. These requirements cannot be relaxed by a
new proposal or a larger denominator.

The already-published qualification owners remain
`oracle/phase1/P0-COMPLETENESS-V4.md`,
`oracle/phase1/P0-CALLABLE-INTROSPECTION-V1.md`,
`oracle/phase1/P0-PUBLIC-ENTRYPOINT-IMPORT-V1.md`,
`oracle/phase1/P0-LARGE-INPUT-INDEXING-V1.md`,
`oracle/phase2/SIX-FAMILY-P0-PRODUCER-V5.md`,
`oracle/phase2/CANDIDATE-INDEPENDENCE-V2.md`, and
`oracle/phase2/CANDIDATE-RUNTIME-INDEPENDENCE-V2.md`.

## Exact complete denominator, not a sampling claim

The successor is an exact prospective cross-product:

`96 operations × 48 primary pattern families × 10 subject representations`

`× 8 operation-valid lifecycle states × 6 subject scales`

`× 4 match-density classes × 16 realistic corpus families`

`= 141,557,760 independently verified and independently timed cases`.

There are exactly **8,847,360 complete strata**, with exactly one case
from each of the **16 realistic corpus families** per stratum. Every
case has weight `1 / 141,557,760`; every one is timed, correctness
checked, retained, and reported. The exact balanced margins are:

- **1,474,560** cases per operation.
- **2,949,120** cases per primary pattern family.
- **14,155,776** cases per subject representation, exactly the complete
  preserved V1 denominator for each representation separately.
- **17,694,720** cases per operation-valid lifecycle state.
- **23,592,960** cases per subject scale.
- **35,389,440** cases per match-density class.
- **8,847,360** cases per realistic corpus family.

No discarded timeout, failure, unsupported feature, no-match, callback
error, cleanup error, replacement operation, scanner, cache miss,
large input, buffer exporter, or slow case may become a missing,
zero-weight, renamed, or substitute case. A failed observation aborts
and is published rather than silently shrinking the denominator. The
future legal-domain matrix must make every crossed axis materially
relevant to the exact public operation; an impossible operation/type
combination, ignored subject or density, duplicate operation, fake
lifecycle, invented method, or corpus pasted onto unused input cannot
inflate the denominator. If any one crossed cell has no rigorously
type-valid operation-specific equivalent, reject the entire generation;
never drop, reweight, rename, or replace that cell. The legal matrix
remains **NOT FROZEN**.

Each case is one complete, homogeneous **public-operation transaction**,
not a fictitious single call. Its six scale bins prospectively require,
respectively, exactly **4, 5, 6, 7, 8, and 9** real invocations of
that one named public operation on separately observable, type-valid
subject windows from the named corpus. Four or more actual windows
permit distinct no-match, one-match sparse, dispersed dense, and
adjacent clustered/zero-width outcome distributions even for anchored
patterns, public `match`/`fullmatch`, callbacks, scanners, and patterns
whose individual invocation can return only one result. Anchored
families use legal subject-sensitive anchored variants such as a
literal following the anchor; zero-width cases use a legal
subject-dependent context. Expected callback exceptions are caught,
recorded, and correctness-gated before the next real invocation.

Subject scale materially changes the exact invocation count as well as
the actual subject windows; corpus materially changes every window;
match density materially changes their verified outcome distribution;
type materially changes the actual argument/exporter; and lifecycle
materially changes the equal public/cache state. Every individual
public invocation must be independently correctness-gated inside its
transaction. A future generator must prospectively prove all such
transformations for every complete cell or reject the entire
generation; it cannot declare an impossible cross-product valid.

## The 96 operations

The first 36 operation names are exactly the preserved V1 operations;
the first 24 primary pattern names are exactly V1's preserved names.
The machine-readable companion pins all 96 names and all 48 names in
order. The expanded operations include:

1. Fresh/cached compile plus actual search or match; genuinely cold
   compilation after purge; cache hits, misses, repeated compilation,
   cache-near-capacity, capacity-boundary churn, over-capacity eviction,
   purge/recovery, and invalid-pattern/invalid-flag recovery followed by
   a real type-valid subject operation. Bytes-only `LOCALE` is used only
   for bytes-compatible subjects; the equal text-domain equivalent
   uses a type-valid ASCII/Unicode flag.
2. Public module and compiled-pattern `search`, `match`, and
   `fullmatch`, including flags, positional bounds, and `endpos`.
3. Module/pattern `findall` and `finditer`, first-result and complete
   exhaustion, empty-match advancement, and all returned capture shapes.
4. Module/pattern `split`, keyword/positional arguments, zero and small
   limits, capture retention, empty matches, and failure observability.
5. Module/pattern `sub` and `subn`, literal and parsed templates,
   numbered/named backreferences, counts, Python callbacks, callback
   order and side effects, callback exceptions, and cleanup.
6. Compiled scanner search/match, repeated scanning, exhaustion,
   zero-width advancement, `re.Scanner` lexicons, mixed tokens,
   unmatched remainder, callback output, callback errors, and lifetime.
7. Match groups, named/positional indexing, defaults, group dictionaries,
   template expansion, spans, match materialization, and no-match
   behavior.

Invalid-path demonstrations must also perform the valid subject
operation where necessary so the subject, scale, match density, corpus,
and lifecycle axes remain real. Every operation uses the same complete
public Python entry point for the reference and candidate.

## Pattern complexity, representation, lifecycle, and workload

The **48 primary pattern families** preserve all 24 V1 families and add
nested/shared-prefix/shared-suffix alternation, ASCII and Unicode
case-folding, scoped/global flags and verbose comments, multiline and
dotall interactions, type-valid Unicode/bytes/locale classes, astral
and surrogate literals or their valid byte encodings, combining marks
or valid encoded sequences, zero-width progress, nested
bounded/lazy repetition, deep groups, many named/numbered captures,
conditionals, nested lookarounds, fixed-width lookbehind alternatives,
large classes, escaping/templates, and safely bounded adversarial
repeat shapes. Every case has exactly one prospectively assigned
primary family; secondary syntax never changes its weight. Future
timeouts and adversarial-size ceilings require a prospective safety
review and remain **NOT FROZEN** and **NOT MEASURED**.

The **10 subject representations** are separately balanced ASCII `str`,
non-ASCII/astral/combining-mark Unicode `str`, `bytes`, `bytearray`,
read-only contiguous `memoryview`, writable contiguous `memoryview`,
contiguous unsigned-byte `array`, contiguous signed-byte `array`,
read-only `mmap`, and writable `mmap`. Each receives exactly
**14,155,776** cases. Read-only/writable views are exactly balanced,
as are read-only/writable mappings and ASCII/Unicode text. Python's
legitimate bytes-buffer acceptance, mutability, export lifetime,
memory shape, release, callback mutation, subject pinning, invalid
views, locale restrictions, and exception behavior must match the
unchanged Python baseline; a subject type incompatible with a pattern
must not masquerade as an independently valid combination.

The **8 operation-valid lifecycle states** distinguish a real cold
compile after purge, real hot cache hit, compiled-object reuse, cache
near capacity, eviction/churn, explicit purge recovery, existing
iterator/scanner/match state, and error/callback/resource-cleanup
state. Each operation requires eight genuinely different legal states;
where a generic description cannot apply, a prospectively documented
operation-specific equivalent must exercise distinct public work. No
renamed cache hit, skipped compile, shared candidate-only warm state,
or invalid preconstructed result is allowed.

The **6 subject scales** are length 0–16, 17–64, 65–256, 257–4,096,
4,097–65,536, and 65,537–1,048,576, using a prospectively declared and
equal Python character/byte accounting rule. Empty or one-character
subjects are selected only when their requested outcome class is
actually legal; dense and clustered tiny-bin cells use sufficiently
long in-bin windows. The **4 match-density classes** are no-match/full
scan, single/sparse match, dispersed dense non-overlapping matches,
and clustered/overlapping/zero-width-progress workloads, each defined
by verified outcomes across the complete real invocation transaction.
No-match, expected exceptions, empty progress, warnings, callbacks,
output side effects, resource release, and observed failures are part
of correctness; none is a missing timing category.

The **16 realistic corpus families** are web access logs; structured
JSON event streams; Python source/docstrings; C/C++/Rust source;
HTML/XML text; CSV/TSV records; email headers/bodies; URI paths and
queries; filesystem paths/shell transcripts; multilingual natural
language; combining marks/graphemes/normalization; emoji, astral and
surrogate edges; genomic ASCII windows; network/binary frames; stack
traces; and synthetic redaction-token shapes. Future corpus-to-subject
transformations must preserve each requested argument type: ASCII text
uses documented ASCII-safe source windows/transliterations, Unicode
uses actual Unicode windows, and bytes/buffer exporters use documented
valid encodings or original binary windows. Regex patterns, flags,
replacement templates, scanner lexicons, and callbacks receive their
matching `str` or `bytes` domain. These are public descriptions, not
corpus contents; no actual input is chosen or read.

## Equal reference conditions and paired randomized observations

The initial prospective comparison has exactly one unchanged, pinned
CPython **3.14.6** baseline and the first **three distinct independently
qualified candidate families**. Every participant gets the exact same
public operation, pattern/flags, subject/exporter, mutable state,
lifecycle/cache state, positional bounds, callbacks and side effects,
output, exception, process isolation, affinity/noise controls, clock,
full Python-to-native boundary, object creation, and cleanup. Candidate
and Python preconditions are equal; Python compilation is not charged
only to the baseline, and candidate compilation, wrappers, callbacks,
FFI, allocation, errors, and cleanup are never removed from the timed
interval. Preparation and independent correctness checking happen
outside that interval for every participant identically.

All **141,557,760** cases first receive a complete untimed baseline and
candidate transaction correctness check, producing **566,231,040**
disclosed participant-transaction preflight observations and exactly
**3,680,501,760** individually verified underlying public-operation
invocations. Every case then receives all 24 permutations
of the four participant orders, exactly once per paired round. Every
participant occupies each position six times, on exactly the same case,
under the same prospectively randomized schedule. Every single timed
call is separately correctness-gated. Prospective exact totals are:

- **13,589,544,960** timed, separately checked participant transactions:
  `141,557,760 × 24 × 4`.
- **88,332,042,240** separately correctness-gated actual public API
  invocations inside those transactions:
  `23,592,960 × (4 + 5 + 6 + 7 + 8 + 9) × 24 × 4`.
- **10,192,158,720** same-case candidate-versus-Python paired ratios:
  `141,557,760 × 24 × 3`.
- **108,716,359,680** bytes, exactly **101.25 GiB**, of unsigned
  eight-byte raw clock values **only**.
- **4,608** operation-by-pattern-family raw-clock shards, exactly
  **23,592,960** clock bytes each.

These figures are arithmetic, not observed runtime, benchmark
feasibility, completed storage, statistical power, or measured speed.
They exclude inputs, outputs, metadata, correctness records, memory
records, indexes, signatures, compression, overhead, and filesystem
cost. Actual machine requirements and completion remain **NOT
MEASURED**. If a fourth or later genuinely independent family qualifies,
include every qualified family; freeze a new complete participant
rotation, minimum paired-round rule, and recomputed denominators before
creating any secret. Never pick the three fastest or misapply the
four-participant totals to a larger field.

## Confidence, regressions, memory, and Python-to-native boundaries

A candidate's case score is the geometric mean of all 24 actual,
same-case, correctness-gated baseline-to-candidate ratios. The overall
headline equally weights the complete **141,557,760**-case
denominator. A future two-sided 95% stratified bootstrap with **9,999**
replicates over all **8,847,360 complete strata** prospectively entails
**88,464,752,640** stratum draws per candidate; no replicate has run.
Prospectively define ties and use a two-sided paired sign test on all
**424,673,280** candidate-by-case hypotheses with Benjamini–Hochberg
false-discovery control `q = 0.05`. Faster, slower, tied,
inconclusive, missing, failed, and aborted cases all use the same
complete denominator. A selective confidence interval never authorizes
a different denominator.

Collect a secondary, balanced cohort of **35,389,440** memory cases,
exactly four in every full stratum, producing **141,557,760**
prospective participant observations. Separately collect
**17,694,720** balanced Python/FFI-boundary cases, exactly two in every
stratum, producing **70,778,880** participant observations. Publish
Python-visible allocations/peaks separately from authenticated
first-party native allocation counts/bytes/peaks, retained arenas,
resident growth, buffer pins, exception cleanup, and callback cleanup.
Unknown or unobservable native allocation/resident memory stays **NOT
MEASURED**. An equivalent first-party empty-call control can explain
argument marshaling, exporter acquisition/release, wrappers,
trampolines, result materialization, and exception translation, but
must never subtract or omit those costs from any main timed call.

Any future winner must still pass every original correctness and live
no-delegation gate, have no unexplained failed/missing/unsafe case,
achieve an overall lower 95% confidence bound of at least **1.5×**,
and be multiplicity-corrected significantly faster on at least
**84,934,656 of 141,557,760** complete cases (60%). Preserve, explain,
and publish every slowdown greater than **20%**, every rejected
candidate, every regression, every observation, and every denominator.

## Future anti-contamination and strictly source-only verification

After, and only after, three qualified independent candidates have
passed complete P0 and live no-delegation, independently review and
freeze the final legal-domain tables, prospective case families,
candidate participant identities, equal conditions, process/clock and
randomization rules, candidate-independent scoring, safety limits,
accounting, independent custodians, and reporting. Then a separate
custodian may create a fresh domain-separated secret, publish only a
commitment, and generate new final cases. Historical/public/practice
inputs, prior proposal cases, existing evidence, known answers,
candidate tuning, and earlier seeds must never contaminate generation,
selection, scoring, final inputs, or disclosure. Before the gate is
passed, it remains forbidden to freeze, generate, or open anything.

`tools/verify_expanded_sealed_holdout_v2.py` accepts only
`--verify-source` and `--self-test`. Both authenticate the successor's
three public source files plus small, pinned, already-published
plaintext proposal and qualification sources, and perform hostile
arithmetic/phase-gate tests. Neither mode authenticates or reads an
executable, evidence archive, candidate, holdout case, generated
input, secret, or seed. An installed audit hook rejects candidate and
matcher imports, native loading, process creation, clocks, networking,
directory enumeration, executable/archive/holdout reads, and every
filesystem write. Verification does not freeze a protocol.

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_expanded_sealed_holdout_v2.py --verify-source \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/verify_expanded_sealed_holdout_v2.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Repeat both commands with `env -i PATH=/usr/bin:/bin LC_ALL=C`.
Passing means only **PRE-PHASE-3 SUCCESSOR PROPOSAL VERIFIED**. The
final holdout remains **NOT FROZEN, NOT GENERATED, NOT OPENED, and NOT
RUN**. Performance remains **NOT MEASURED**; no winner is selected.
