# Fresh prospective one-use holdout v1

Status: **unopened, prospective, and fail-closed**. This protocol does not
inspect, reuse, decrypt, or derive cases from any historical holdout, hidden
fixture, final campaign, or version-9 artifact. It does not report measurements.

## Frozen population and exact accounting

The case population is the complete Cartesian product of:

- 16 independently specified semantic regex families;
- 16 strata: text or byte-like input, default or family-specific flags, default
  or bounded positional window, and compiled or module lifecycle;
- 256 domain-separated, HMAC-generated fresh variants per family and stratum.

The population is therefore exactly `16 × 16 × 256 = 65,536` cases. Byte-like
strata deterministically include exact `bytes`, `bytearray`, and `memoryview`.
The families cover literals, classes, ordered alternation, greedy and lazy
repetition, counted repetition, named captures, named backreferences,
lookahead, fixed-width lookbehind, multiline anchors, dot/newline interaction,
case folding, Unicode/ASCII word categories, word boundaries, and zero-width
progression.

A completed measurement, if a future genuinely qualified executor is frozen,
must use 19 independently shuffled paired trials. Each trial contains one
isolated CPython standard-library baseline and one isolated from-scratch Rust,
C/VM, and Zig observation:

```text
65,536 cases × 19 trials × 4 participants = 4,980,736 raw observations
```

Every candidate trial must independently gate four documented, public
equivalence channels against the isolated standard-library reference:

1. Public compiled-pattern flags, metadata, groups, and named-group maps.
2. Return values, complete match/capture/span/position surfaces, and exact
   public bytes or buffer representation.
3. Exception class, public arguments, and documented `PatternError` fields.
4. Documented converter, callback, warning, scanner-exhaustion, and recovery
   traces.

These are four checks for **each** of three candidates, not an extrapolation
from a smaller existing worker:

```text
65,536 cases × 19 trials × 3 candidates × 4 channels
    = 14,942,208 candidate correctness gates
```

There must be one paired confidence interval per case and candidate, plus one
aggregate paired confidence interval per candidate:

```text
(65,536 cases × 3 candidates) + 3 aggregate intervals = 196,611 intervals
```

The prospective manifest fixes 2,000 bootstrap samples per interval. No
confidence interval, timing, gate, observation, result, or speedup exists
until an actual qualified execution completes.

## Interpreter, sources, and complete provenance

Freeze and eventual opening require the exact, isolated, bytecode-disabled
CPython interpreter:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
version: 3.14.6
SOABI:   cpython-314-x86_64-linux-gnu
required flags: -I -B
```

The manifest fingerprints the interpreter, this protocol, its generator, the
final public v4 isolated runner, the universal public oracle, both source-audit
tools and their passing reports, the public oracle's source-bound all-candidate
passing proof, the explicitly enumerated owned candidate Python and C/Rust/Zig
sources, the complete explicitly enumerated owned Rust source graph, all five
owned native binaries, project and Rust build manifests, and explicitly
requested additional public proof files.

The original from-scratch audit must contain all 76 passing controls, five
attested native artifacts, and passing actual isolated mappings. The
additional no-delegation audit must contain exactly 32 passing controls,
inherit all 76 original controls, verify the closed owned source graph, attest
each candidate in a continuously guarded separate worker, and bind every
source, report, and native fingerprint to the actual frozen bytes. The public
universal oracle must show a source-bound, all-candidate `PASS` for 8,192
public cases and 393,216 observations per candidate without reading a
historical holdout or running a benchmark.

Matching source and native fingerprints prove artifact identity, not hermetic
or independently reproducible compilation. Compiler, linker, sysroot, and
header provenance must not be represented as proven.

## Prospective commit and entropy order

The only authorized generator is:

```text
tools/postfinal_fresh_holdout_v1.py
```

First, run its candidate-free smoke controls, if independently authorized:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_fresh_holdout_v1.py self-test
```

The smoke controls use the public, fixed nonproduction key
`bytes(range(32))`. They do not draw OS production entropy, import a candidate,
create a guard, use a clock, write a fixture, or materialize a production
holdout case.

Prepare only the prospective manifest:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_fresh_holdout_v1.py freeze
```

The first successful invocation exclusively creates
`performance/postfinal-fresh-holdout-v1/FREEZE-MANIFEST.json`. This manifest
contains distributions, bounds, contract counts, and fingerprints, but no
production key, case, expected value, timing, confidence interval, or result.
It cannot overwrite an existing manifest. Its prerequisites include the passing
committed-quality source, no-delegation, and all-candidate public-oracle
reports; additional public proofs can be added with repeated `--proof PATH`
arguments.

Commit **and push** the exact manifest, this generator and protocol, all
enumerated candidate sources and binaries, final runner/oracle/audit sources,
and every pinned passing proof before invoking the identical `freeze` command
again. The generator verifies all worktree bytes against Git `HEAD` blobs,
requires a clean repository apart from its exact one-use guard, requires
`HEAD` to equal the configured upstream, and independently confirms the same
commit using `git ls-remote`. It never trusts a merely local branch.

Only after successful verification does the second invocation:

1. Create `.FRESH-HOLDOUT-V1.one-use.guard` using
   `O_CREAT | O_EXCL | O_NOFOLLOW` and private mode `0600`.
2. Append the public `armed-before-entropy` event.
3. `fsync` both the guard and its parent directory.
4. Reverify the entire committed and remotely pushed manifest, source graph,
   five native artifacts, audits, and proofs.
5. Draw the protocol's sole production key with `secrets.token_bytes(32)`.
6. Append a public sealed event and a private key event without rewriting,
   truncating, replacing, or reopening the guard for creation.
7. `fsync` the guard and parent directory again.

A creation error, interruption, changed commit, changed artifact, failed
remote verification, short write, or entropy failure leaves the exclusively
created guard present and permanently poisoned. It must never be overwritten,
deleted, recreated, or treated as an unused key. No external user-provided
secret is required. No production case can be known by an optimizer or
candidate before the distribution, source, binary, proof, and manifest freeze.

## Opening, isolated oracle, and current honest limitation

Any future opening requires the explicit affirmative command:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/postfinal_fresh_holdout_v1.py open --affirm-one-use
```

It first rechecks the exact pinned interpreter, live remote commit, committed
canonical manifest, every artifact and audit, and the first two public
append-only guard events. The private key must never appear in an argument,
environment variable, worker output, result, manifest, or candidate-accessible
path. A genuinely completed executor must stream production cases to a
separate guarded standard-library oracle and the three permanently guarded
candidate workers; compare all four public observable-equivalence channels;
validate exact owned mappings before and after case processing; shuffle paired
trial order; keep IPC and correctness validation outside timed regions; and
produce the exact fully counted observations and confidence intervals.

**No such four-channel holdout adapter is currently frozen.** The available
public v4 guarded worker honestly returns only three per-observation correctness
checks. It cannot establish this protocol's fourth callback/converter/warning
channel, 14,942,208 gates, or a source-bound isolated streaming fresh oracle.
Accordingly, `open --affirm-one-use` intentionally exits `FAIL_CLOSED` after
validating the public freeze and guard. It does not read the third private key
event, derive a production case, import a candidate, spawn a worker, perform a
timing, generate expected output, consume or overwrite the guard, or claim
holdout results. Changing this limitation requires a new, explicitly
authorized, independently audited, prospectively committed adapter and a new
genuine freeze; it cannot be silently relaxed.

## Resource bounds and accurate memory labels

Patterns are bounded to 512 UTF-8 bytes, subjects to 4,096 UTF-8 bytes,
scanner or iterator results to 64 matches, and trial work to 1,024 operations.
Frozen JSON, source, native-artifact, Git-response, and guard-event reads also
have explicit finite limits.

`tracemalloc` is **Python-visible traced allocation only**; it does not measure
Rust, C, Zig, allocator-external, or otherwise native engine memory. Process
RSS/high-water is for the **whole isolated worker process**, not an exact
per-case or engine-exclusive native allocation. Neither metric may be labeled
as exact Rust/C/Zig engine allocation.
