# Rust public development/practice benchmark v2

PUBLIC DEVELOPMENT/PRACTICE ONLY. This is not the sealed final holdout, does
not qualify a candidate for that holdout, does not select a winner, and must
never open, enumerate, copy, derive from, or modify sealed cases, fixtures,
archives, private benchmarks, or hidden tests.

## Frozen independent matrix

- Source: `tools/rust_public_practice_benchmark_v2.py`.
- Schema: `rebar-rust-independent-public-practice-v2`.
- Published deterministic seed: `5928217332825411634`
  (`0x52454241525f5032`).
- Canonical matrix SHA-256:
  `0c88d1ec7066ede05466c1a91126086cd52256548eda13a31778ff284439d97d`.
- Exact denominator: **10,434 public cases**, formed from **94 independently
  authored public datasets × 111 operations**.
- Domain balance: **47 text datasets / 5,217 text cases** and **47 bytes or
  byte-like datasets / 5,217 bytes cases**. Every case has exactly the same
  weight, including misses, warnings, exceptions, and slower workloads.
- Operation families: 32 module operations, 50 compiled-pattern operations,
  16 match-object operations, five public Scanner operations, and eight explicit
  compile/cache/reuse lifecycle operations.
- 59 workload classes and ten lifecycle classes; public subject lengths span
  three through 2,050 text characters or bytes.
- For comparison only, the predecessor contains 864 cases, 24 datasets, and
  36 operations. The v2 case denominator is more than twelve times larger.

The literals and published seed above are the complete source of the matrix.
Constructing or verifying it never opens a benchmark, fixture, sealed case,
archive, or holdout. The JSON alongside this document is only a public protocol
commitment; it contains no measured candidate results and no hidden cases.

## Public coverage

The text workload includes ASCII and Unicode words, combining marks, astral
characters, Kelvin sign, long-s, Turkish-I and Greek-sigma case folding,
Unicode digits/whitespace, explicit ASCII boundaries, line and absolute
anchors, lazy DOTALL, VERBOSE, lookbehind/lookahead, prefix alternations,
backreferences, conditional/atomic/possessive groups, scoped flags, repeated
and nested patterns, route/email/log-shaped subjects, complete misses, scanner
remainders, and long repeated haystacks.

The equally weighted bytes domain includes high-bit and embedded-NUL bytes,
hex/octal classes, ASCII flags, the same structural matching families, mutable
bytearrays, mutable/readonly PEP 3118 memoryviews, and PEP 688 exporters.

Additional deliberately public compatibility and performance shapes include:

- Scoped `I`, `S`, `M`, `A`, and text `U` enable/disable/override cases in both
  direct pattern use and real `re.Scanner` lexicons. These are compatibility
  probes; no claim is made that any particular candidate fails them.
- Unknown named-Unicode escapes inside ignored `(?#...)`, global VERBOSE
  comments, and scoped VERBOSE comments, plus an actually active valid named
  Unicode escape.
- Opposite prefilter shapes with grouped/search/finditer-capable patterns and
  2,048-unit haystacks: dense-first/sparse-last `aaaaab(?=\d)\d` and
  sparse-first/dense-last `bcaaaa` on `b` + `d` + many `a` units. Both remain
  in the frozen denominator; neither direction can be silently dropped.
- Exact bound native method signatures, `__text_signature__`, binding,
  qualified name, and callable shape for search, match, fullmatch, findall,
  finditer, split, sub, subn, and scanner.
- Pattern scanner `__reduce_ex__` protocols `-1`, `0`, `1`, `2`, `5`, the
  string `"0"`, and `2**40`, preserving exact successful reconstruction
  structure or exact public `TypeError`/`OverflowError` observations.
- PEP 688 replacement and subject acquisition/release order, including a
  deterministic subject whose first acquired view is the original public
  bytes and whose later acquisitions are `b"X"`; captured spans are compared
  to CPython's real clamped result rather than hand-simulated.
- Invalid replacement-template precedence using an exporter that raises and
  records `BAD+` if the subject is acquired: actual public pattern errors and
  actual subject-acquisition order are both preserved.
- Module compile identity, alternate compile identity, purge, hot cache,
  fresh-cache-miss compilation, cache churn, scanner recreation, and repeated
  precompiled/module matching.
- Positional 3.14 deprecation warnings, ordinary/public pattern exceptions,
  replacement callbacks and callback failures, scanner callback matches,
  exact remainder types/mutability, captures, bounds, group/index errors,
  copy/deepcopy, escaping, flags, and result materialization.

## Isolation and fail-closed provenance

Only the exact pinned CPython 3.14.6 executable may run the harness, using
`-I -B` and the real owned repository/source paths. No third-party regex engine
is imported. The standard-library `re` module is used as the actual matching
oracle only in separately launched, explicitly labeled `stdlib` workers; the
named owned Rust adapter/compiled extension is imported only in separately
launched, explicitly labeled `rust` workers.

Some standard-library support imports such as JSON/inspection can incidentally
preload `re`/`_sre` in either harness process. This is not an oracle invocation.
Each worker snapshots those preexisting module objects before loading its
engine. A Rust worker fails if candidate loading or candidate-owned matching
adds or replaces any `re`/`_sre` module, retains such a matching module on its
adapter, loads a recognized external regex package, or loads a candidate
runtime module outside the owned first-party candidate directory. Stdlib and
Rust workers expose distinct provenance counters and cannot share a process.

Source-only `--self-test` and `--verify-source` start zero workers, import no
candidate, invoke no matching oracle, sample no clock, and read/write no case,
fixture, sealed/hidden, archive, or output file. They independently reject
duplicate JSON keys, nonfinite/truncated/concatenated/noncanonical process
documents, forged byte encodings and memoryviews, omitted/duplicated/
reweighted/injected cases, changed bounds, and unauthorized output paths.

`--correctness-only` launches one isolated stdlib and one isolated Rust worker,
performs no timing and no writes, and emits **every** mismatch with both exact
public outcomes. It does not claim a candidate passes when any mismatch exists.
`--run` refuses to time anything unless the two complete 10,434-case outcome
vectors and their digests are identical.

## Paired measurement and confidence

For an explicitly authorized public run, each default case receives eight
paired trials, one correctness-checked warmup per engine, four timed
correctness-checked iterations, and one untimed correctness-checked postcheck.
Engines run in separate processes. Every trial uses the same deterministically
shuffled full-case order for both engines, and engine-first order alternates
exactly across the eight rounds. The timed interval includes the complete
public API call, materialization, callbacks, warning/result normalization, and
comparison with the genuine standard-library outcome.

The report preserves every raw paired nanosecond row, worker PID and order,
full frozen case matrix, full stdlib correctness vector, and complete per-case
results. Per-case speedup is the geometric mean of all paired ratios. Overall
speedup is the equally weighted geometric mean of all 10,434 case estimates.
Both case and overall 95% intervals use 400 deterministic published-seed paired
bootstrap resamples; overall resampling includes both cases and paired trials.
All statistically slower cases and all regressions exceeding 20% remain visible.

Output, if explicitly requested, is exclusively created under
`experiments/rust_public_practice_v2/` with no-follow directory traversal,
`O_EXCL`, file and directory `fsync`, bounded canonical JSON, and no overwrite.

## Commands and execution boundary

Pure source-only checks:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/rust_public_practice_benchmark_v2.py --verify-source

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/rust_public_practice_benchmark_v2.py --self-test
```

Only the root coordinating agent may execute the actual candidate after the
new source/protocol have been committed and pushed:

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/rust_public_practice_benchmark_v2.py --correctness-only

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/rust_public_practice_benchmark_v2.py \
  --run --trials 8 --iterations 4 --warmups 1 \
  --output experiments/rust_public_practice_v2/public-v2-paired.json
```

Even a completely passing public run leaves
`candidate_qualified_for_sealed_final_holdout=false`,
`sealed_final_holdout_opened=false`, and `final_winner_selected=false`.
