# Independent Go regular-expression experiment

Status: **SOURCE FROZEN. NOT BUILT. NOT RUN. NOT QUALIFIED.**

This is source for an additional matching architecture. It is not a
finished replacement for Python's `re`, a passing candidate, benchmark
evidence, or a selected winner. No Go compiler, C compiler, candidate worker,
correctness oracle, holdout, performance fixture, timer, or memory measurement
has been run for this experiment.

## Ownership

The complete source boundary is exactly:

1. `experiments/go_from_scratch_v1/go.mod`.
2. `experiments/go_from_scratch_v1/engine.go`.
3. `experiments/go_from_scratch_v1/exports.go`.
4. `experiments/go_from_scratch_v1/python_bridge.c`.
5. `experiments/go_from_scratch_v1/PROTOCOL.md`.

The Go module declares no external dependencies. `engine.go` defines its own
lexer, expression nodes, parser, character-class and flag interpretation,
capture state, ordered continuation-based backtracking, and matching executor.
It does not import Go's `regexp` or `regexp/syntax`, Python's `re` or `_sre`,
PCRE, RE2, a third-party package, or the parser, compiler, executor, or binary
of another candidate. No other candidate's source was consulted to author this
experiment.

`exports.go` declares an explicit versioned C ABI. A compiled expression is
owned by the Go runtime and is identified exclusively by `runtime/cgo.Handle`.
The C caller owns Unicode input, bytes input, error structures, and capture
output. Go copies input code points before matching, does not retain C or
Python pointers, converts recovered runtime panics into structured failures,
and deletes each successful handle explicitly.

`python_bridge.c` is a separately authored CPython adapter. It defines owned
native pattern, match, and scanner types and real C method descriptors. It reads
Unicode with `PyUnicode_KIND`, `PyUnicode_DATA`, and Python's 1-, 2-, or
4-byte code units. It obtains contiguous bytes with `PyObject_GetBuffer` and
holds and releases independent `Py_buffer` exports for the lifetime of byte
matches and scanners. It supplies GC traversal, cycle clearing, deterministic
native cleanup, and a genuine callable iterator over an owned scanner. The
public scanner's `_sre.SRE_Scanner` type name is metadata on an independently
defined native type; it is not an import, a shared type, or a call into `_sre`.
Its `rebar_go_python_bridge` source build constraint deliberately excludes the
CPython adapter from the default Go cgo library. A future separately reviewed
C-extension build must compile this C file with the pinned Python headers and
link against the independently built Go ABI; no generated header or binary is
present in this source-first experiment.

The only Python standard-library import in the adapter is `copyreg` for the
public scanner's ordinary object-reconstruction metadata. It does not compile,
search, interpret a regular expression, choose matching results, or import a
regular-expression implementation on the experiment's behalf.

## Proposed capabilities, not test results

The source contains implementations for:

- Separate string and bytes pattern domains.
- Unicode and ASCII-aware character classes and matching flags.
- Literals, ranges, categories, anchors, word boundaries, and dot.
- Prioritized alternatives and explicit capture snapshots.
- Numbered and named groups and backreferences.
- Greedy, lazy, and possessive quantifiers.
- Scoped and leading inline flags.
- Positive and negative lookahead and fixed-width lookbehind.
- Atomic groups and conditionals for previously defined groups.
- Pattern search, anchored match, and full match.
- Stateful scanners and real built-in callable iterators.
- Named and numbered match groups, capture coordinates, and cached `regs`.
- Non-overlapping iteration, `findall`, and captured splitting.
- Literal and callable substitution, including callbacks returning `None`.
- Public escaping and structured pattern exceptions.

These are claims about identifiable source paths, not claims that the source
compiles, runs, agrees with Python, survives hostile inputs, or passes any
correctness case.

## Explicit gaps

The source-only experiment is not complete or qualified. In particular, the
following have not been implemented or proved equivalent:

- Numbered or named replacement templates and `Match.expand`.
- Python's full generated Unicode name and case-folding databases.
- Every Unicode identifier exception and Unicode version.
- Real process locales and the `LOCALE` flag.
- `DEBUG` output and every public diagnostic and warning location.
- Forward conditional references and lookbehind group-reference details.
- Every repeated-capture, backtracking, error-position, and overflow edge.
- Python's actual `RegexFlag` enumeration and all public module exports.
- Observable compilation-cache identity, eviction, and `purge` behavior.
- Public `Scanner` lexicons and generic pattern and match aliases.
- Every pickle, copy, weak-reference, and exception-serialization contract.
- Noncontiguous buffers and every released-buffer exception detail.
- Exact cycle finalization, hostile user callbacks, and instrumentation.
- Thread safety, free-threaded CPython, and multiple subinterpreters.
- Build, ABI, loader, sanitizers, native ownership, and anti-delegation audits.
- The existing full frozen Python correctness campaigns and public matrices.
- Memory, compilation time, matching time, confidence intervals, or rankings.

Unsupported features must raise an explicit exception. They must not fall
back to a different engine, approximate a result, detect a benchmark, contain
precomputed oracle answers, or be excluded silently from a correctness
denominator.

## Proposed first differential cohort

Status: **UNFROZEN. REFERENCES NOT RUN. CANDIDATE NOT RUN.**

Proposed seed: `2026072491`. Proposed domain:
`rebar/python-re/independent-go/source-first/v1`. The proposed first matrix
contains exactly 12 groups of four cases, or 48 individual case identities.
It is a small development screen, not a comprehensive suite or a holdout.
The expected value of every case must be observed independently from two
fresh isolated CPython 3.14.6 standard-library processes. Exceptions, public
attributes, buffer state, callback events, and iterator exhaustion are records,
not guessed answers.

| Group | Four proposed independently recorded cases |
| --- | --- |
| Text literals | Search a literal; full-match a literal; match an escaped period; reject a different literal. |
| Byte literals | Search bytes; full-match bytes; reject a text subject for bytes; reject a bytes subject for text. |
| Unicode and ASCII | Unicode decimal class; ASCII decimal class; Unicode case-insensitive literal; ASCII case-insensitive literal. |
| Capture groups | Numbered capture; named capture; numbered backreference; named backreference. |
| Ordered alternatives | First successful branch; shared literal prefix; empty left branch; captured alternative. |
| Repetition | Greedy star; lazy star; exact bounded repetition; bounded optional repetition. |
| Empty progression | Empty-pattern scanner; empty lookahead scanner; optional-pattern iterator; exhaustion repeated twice. |
| Lookaround | Positive lookahead; negative lookahead; fixed-width positive lookbehind; fixed-width negative lookbehind. |
| Committed matching | Atomic success; atomic rejection; possessive success; possessive rejection. |
| Matching windows | Negative start; negative end; oversized end; start after end. |
| Buffers | Mutable bytearray; contiguous memoryview; noncontiguous memoryview; released memoryview. |
| Replacement | Literal text replacement; literal bytes replacement; callable replacement; callable returning `None`. |

Do not substitute this 48-case screen for any already frozen campaign. Do not
reduce the matrix, turn an unsupported-feature exception into a success,
remove difficult cases, or declare the cohort frozen until a runnable source
and exact case-generator fingerprint have first been reviewed, committed,
and pushed.

## Mandatory future order

1. Root reviews these five exact source files and records their fingerprints.
2. Root commits and pushes this source-first experiment before attempting a
   build or starting any reference or candidate process.
3. A separately reviewed build protocol specifies the actual Go version, cgo
   configuration, CPython 3.14.6 headers, shared-library link and loader
   ownership, and reproducible artifact fingerprints.
4. A separately reviewed correctness runner freezes all 48 exact identities,
   the seed, normalization, independent two-reference comparison, failure
   preservation, anti-delegation guards, and exclusive output paths.
5. Only after those sources are independently committed and pushed may root
   build or run the first references. Self-oracle disagreement blocks the
   candidate.
6. Only after both references pass may root run the guarded Go experiment.
   Preserve every genuine mismatch, crash, timeout, unsupported feature,
   native error, and denominator.
7. A 48-case pass, if one ever occurs, is preliminary. Full qualification
   still requires the complete immutable upstream, fuzz, property, public,
   Unicode, locale, resource, lifecycle, native-ownership, and no-delegation
   campaigns applicable to all other candidate families.
8. Holdout and performance work remain inaccessible until the project's
   correctness phase and its prerequisite commits and pushes have genuinely
   completed.

Source fingerprints: **SOURCE FROZEN**.

Build and loader verification: **NOT BUILT**.

Independent CPython references: **NOT RUN**.

Go candidate and compatibility: **NOT RUN. NOT QUALIFIED.**

Benchmark, holdout, memory, regressions, rankings, and speed: **NOT
MEASURED**.
