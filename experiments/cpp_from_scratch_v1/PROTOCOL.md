# An independently written C++ regular-expression experiment

Status: **SOURCE FROZEN. NOT BUILT. NOT RUN. NOT QUALIFIED.**

This directory proposes an additional, independently implemented
regular-expression engine. Its existence is not evidence that the engine
compiles, matches Python, is memory-safe, or improves performance. It is not
part of `rebar`, is not registered as a project candidate, and must not enter
any candidate comparison until its source is separately frozen and all
existing correctness and independence requirements actually pass.

## Exactly what is written from scratch

`engine.hpp` defines this experiment's own characters, flags, classes,
captures, instructions, program, interpreter, and replacement interface.

`engine.cpp` owns a separate recursive-descent parser, syntax tree, width
analysis, bytecode emitter, explicit prioritized backtracking stack,
capture-state snapshots, counted repetition, atomic-group boundaries,
lookaround subprograms, replacement-template parser, and escaping logic.
Greedy, lazy, and possessive repetitions each use the same original counted
instruction representation. Its parser and instruction format are local to
this directory.

`py_bridge.cpp` owns a direct CPython C-API extension. It builds its own
compiled-pattern, match, match-iterator, and scanner types; accepts Unicode
strings and contiguous byte buffers; implements a bounded, independently
owned compiled-pattern cache; and routes public functions directly into the
C++ engine. Python's public Unicode character classification and case-mapping
functions are used only as character-data providers, never as matchers.

The proposed extension name is `rebar_cpp_from_scratch_v1`. It is not the
published `rebar` interface and is not a replacement until the whole project
genuinely qualifies it.

The implementation must never import, link to, dynamically resolve, invoke,
copy the semantic pipeline of, or delegate matching to Python `re`, `_sre`,
`std::regex`, POSIX regular expressions, PCRE, PCRE2, RE2, Hyperscan, Rust
regex libraries, a Python regex package, or another project candidate. It
must not use a subprocess, fallback matcher, hardcoded oracle result, or test
or benchmark detection. The only proposed production dependencies are the
C++ standard library, the direct CPython C API, and ordinary character and
locale classification.

## Correctness must come before any candidate status

Before this experiment can be built or considered a candidate, the project
owner must freeze, commit, and push these exact four source files. A future
build must use the pinned CPython 3.14.6 headers and ABI and must identify
its exact compiler, command, native source fingerprints, extension artifact,
and dynamically loaded dependencies. No prebuilt binary is acceptable.

The first gate is the unchanged, previously frozen, complete project
correctness oracle for Python 3.14.6. Its official upstream tests, public
interface checks, full Unicode checks, deterministic differential and
property checks, resource and boundary checks, true locale tests, original
seeds, and exact denominators must all run against this extension. No case
may be removed, weakened, translated into an expected approximation, or
described as passing before an actual run. Every mismatch, crash, exception,
resource failure, or undefined-behavior finding disqualifies the experiment.

A separate future source-and-binary audit must independently show that this
extension owns and executes its own parser, compiler, matching instructions,
captures, replacements, and native artifacts, and that no forbidden matching
implementation is reachable. A successful parser unit test or an isolated
example is not a passing project oracle.

## Additional reproducible differential campaign

After the exact project oracle passes, predeclare an additional campaign of
**48 cohorts of 128 observations each**, for **6,144** individually recorded
observations per engine. This campaign is **NOT GENERATED** and **NOT RUN**.
It is additional to the frozen project correctness oracle and cannot replace
or reduce that oracle.

Use the pinned standard-library Python 3.14.6 implementation in two separate
oracle-only processes. Preserve both complete independently generated
reference record arrays. Run this experiment in a separate candidate
process that does not import the standard-library matcher. Compare complete
results, exception types and locations, capture values and spans, match
attributes, object types, and observable mutations. A reference disagreement
stops the experiment before the candidate starts.

Freeze the unsigned 64-bit seed `0x4350505f56315f01`. Derive the starting
state of cohort `i` as
`(seed + i * 0x9e3779b97f4a7c15) mod 2**64`, numbering cohorts from zero.
For each generated value, advance with SplitMix64:

```text
state = (state + 0x9e3779b97f4a7c15) mod 2**64
z = state
z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) mod 2**64
z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) mod 2**64
value = z ^ (z >> 31)
```

Do not substitute the host's random-number generator. Record the cohort,
zero-based observation, seed, generator state, exact pattern and subject,
subject kind, flags, method, argument values, reference records, candidate
record, and any failure. A failed case must reproduce from its original
cohort and observation without opening or sampling another test collection.

The fixed cohorts are:

1. Unicode literals, including embedded NULs.
2. Bytes literals across all 256 byte values.
3. Unicode surrogate literals and adjacent non-surrogates.
4. Empty patterns and empty subjects.
5. Dot with and without the all-lines flag.
6. Beginning and end anchors in single-line subjects.
7. Beginning and end anchors in multiline subjects.
8. Absolute beginning and absolute end anchors.
9. Positive digit classes under Unicode and ASCII flags.
10. Negative digit classes under Unicode and ASCII flags.
11. Positive whitespace classes under Unicode and ASCII flags.
12. Negative whitespace classes under Unicode and ASCII flags.
13. Positive word classes under Unicode and ASCII flags.
14. Negative word classes under Unicode and ASCII flags.
15. Word and non-word boundaries, including empty subjects.
16. Positive character sets and character ranges.
17. Negative character sets and escaped set characters.
18. Unicode simple-case matching and its special characters.
19. ASCII-restricted case-insensitive matching.
20. Exact-count repetition, including zero counts.
21. Bounded greedy repetition.
22. Bounded lazy repetition.
23. Unbounded greedy repetition.
24. Unbounded lazy repetition.
25. Possessive repetition.
26. Atomic groups and discarded backtracking choices.
27. Empty-width repetition and progress termination.
28. Ordered alternatives and common prefixes.
29. Numbered captures and unmatched capture groups.
30. Named captures and named capture dictionaries.
31. Numeric backreferences and octal ambiguity.
32. Named backreferences.
33. Conditional groups and absent captures.
34. Positive lookahead and propagated captures.
35. Negative lookahead.
36. Fixed-width positive lookbehind.
37. Fixed-width negative lookbehind.
38. Verbose patterns, comments, and scoped flags.
39. Literal and numeric replacement templates.
40. Named and unmatched replacement templates.
41. Callable replacements and callback exceptions.
42. Reentrant callbacks and cache mutation.
43. Empty and nonempty match iteration.
44. Splitting with zero-width and captured delimiters.
45. Bytes, bytearray, and contiguous memory-view subjects.
46. Compiled-pattern and match attributes, aliases, and errors.
47. Cache identity, bounded eviction, and purge behavior.
48. Fresh process, locale, object-lifetime, and scanner behavior.

The cohort names, case count, seed, generator, oracle separation, complete
record retention, exact project gates, and no-delegation rule must be frozen
before any execution. Do not silently change a denominator or count an
example as passing because it exercises an implemented instruction.

## Known limitations; no implied compatibility

The source has not been compiled, imported, audited, or tested. In
particular, the experiment does not yet establish Python `enum.IntFlag`
identity, the complete `re.__all__` surface, the module-level lexical
`Scanner`, pickling and copy semantics, non-ASCII group-name identifiers,
forward conditional references, exact exception messages and attributes,
all Unicode simple-case equivalences, locale and buffer lifetime semantics,
subinterpreter-local module state, cycle collection, complete parser
diagnostics, exact debug and template behavior, concurrent access, sanitizer
cleanliness, or faithful behavior under resource exhaustion. These are
unresolved correctness obligations, not private waivers. No mismatch may be
suppressed.

The frozen project oracle is **NOT RUN**. The additional differential
campaign is **NOT GENERATED** and **NOT RUN**. Build, import, native audit,
memory safety, compatibility, qualification, runtime, memory usage,
rankings, and relative performance are **NOT MEASURED**. This source-only
experiment has **NO WINNER** and is **NOT A QUALIFIED CANDIDATE**.
