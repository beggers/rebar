# Frozen candidate correctness protocol, version 6

This protocol checks whether independently implemented replacements actually
behave like Python 3.14.6 `re`. It does not benchmark a candidate, inspect a
holdout, select a winner, or authorize wrapping an existing regular-expression
package.

The original correctness denominator is exactly 31,237 runnable cases across
13 previously frozen suites. There are 152 original CPython test records but
only 151 runnable cases: `ReTests.test_memory_leaks` is the one genuine
debug-build skip. The 13 specifically named private waivers remain private
waivers, not passing public cases.

| Frozen original suite | Runnable cases |
| --- | ---: |
| Original CPython tests | 151 |
| Public contract | 864 |
| Scanner contract | 1,024 |
| Buffer contract | 768 |
| Managed buffer lifetimes | 1,024 |
| Verbose scanner and comments | 2,854 |
| Public types and serialization | 6,912 |
| Substitution and buffer semantics | 5,120 |
| Shape-changing buffer semantics | 10,240 |
| Complete public surface and real locales | 1,376 |
| Real independent Python interpreters | 128 |
| PEP 688 buffer exporters | 264 |
| Real threaded compiled patterns | 512 |
| Total | 31,237 |

The exact original case identities, complete seeds, source hashes, matrices,
reference hashes, recorder routes, archived genuine failures and build owners
are independently frozen in `p0-candidate-protocol-v6.json`. Its matching
validator is `tools/run_frozen_p0_candidate_worker_v4.py`; its whole-candidate
recorder is `tools/run_frozen_p0_candidate_v6.py`. The caller must separately
pin all four published V6 source, worker, prose, and machine-inventory bytes.
Changing any one requires a new freeze and a new focused commit before any
candidate executes.

Use the actual pinned CPython executable, not merely a matching version or
path:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
SHA-256 255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
```

The worker verifies those exact executable bytes using a bounded, no-follow,
unchanged-inode read. Every invocation is isolated (`-I -B`). Synthetic
`--self-test` checks execute no files, candidates, reference workers, builds,
promotions, interpreters, clocks, or measurements. Real
`--verify-frozen-context` checks are read-only and actively forbid writable
file handles, writable descriptors, temporary outputs, promotions, native
candidate imports, processes, clocks, interpreters, networks, and threads.
Run both checks under the ordinary environment and `env -i` before authorizing
any candidate.

## Independently written candidates

Each candidate must use its own independently owned parser, compiler, and
execution engine. Python's `re`, `_sre`, CPython's regex implementation,
external regex packages, another candidate's engine, fallbacks, approximate
answers, benchmark detection, and hard-coded oracle results are forbidden in
production. Original CPython is a separately isolated correctness oracle,
never a production matcher.

Rust and C must use independently reproduced native source build version 2.
Zig must use independently reproduced native source build version 3. All
families must prove two distinct fresh source-build phases, their exact
source-built native bytes, the genuine corrected version-2 canonical
activation, all actual durable promotion intentions, the complete recovery
journal, the unchanged original matcher guard, and the complete independent
source-owner closure. A wrapper or multiple configurations of one semantic
engine do not count as independent candidates.

The 128 original interpreter cases use only the separately published and
independently corrected nested version-3 owner:

```text
tools/run_owned_candidate_subinterpreters_v3.py
21febe241549963a2818af2a20782da81bdf952fb7be8affc4289d9ccc9ad5b4

oracle/phase2/candidate-subinterpreters-v3.json
17dac72e6a0ae75bf1f013656b9779a1e948e71439cf336499c1e680beb19284

oracle/phase2/CANDIDATE-SUBINTERPRETERS-V3.md
97354130b4d1ab97ee2c684b43b72e29a0a68439c2a1ead5a4f45edc20e6c9b4
```

A passing interpreter result must show the real original 128 cases, 394
observed interpreter calls, 11 created and destroyed interpreters, 11 real
initializations, 11 guard cleanups, all original reference comparisons, the
actual family-specific native byte sizes, closed real pipes, and restored
locale and interpreter state. Those 128 cases count exactly once in the
original 31,237; they are not additional cases.

## Preserve genuine failures

The protocol independently reads and authenticates all 32 already published
C/Rust version-5 artifacts and both separate restoration receipts. It retains
the exact genuine results rather than trusting the earlier aggregate's zero:

| Previous candidate | Passing suites | Passing runnable cases | Actual mismatches | Result |
| --- | ---: | ---: | ---: | --- |
| C | 7 | 7,197 | 2,094 | Failed |
| Rust | 8 | 7,461 | 2,042 | Failed |

For both families, the real specialized failures were 248 public-type
mismatches, 336 substitution mismatches, and 1,392 shape-changing-buffer
mismatches. C had another 114 public-surface mismatches and four buffer
exporter mismatches. Rust had another 66 public-surface mismatches; its 264
buffer exporter cases really passed. The archived C interpreter worker
created and destroyed two interpreters but executed zero original cases. Rust
failed before establishing an interpreter worker; its interpreter lifecycle
is `NOT ESTABLISHED`, not zero or a pass.

Candidate producers can legitimately return exit status 1 while successfully
publishing complete failure evidence. A receipt marked `PASS` means only
that the report was durably written. Its separately authenticated
`candidate_result_status` or `candidate_status` determines the actual
candidate outcome. Both receipt and report paths are fixed before process
execution; a child cannot choose a replacement path.

Full expected and actual outcomes are reconstructed from the exact signed
original baseline and complete, hash-authenticated candidate stdout. Public
types and substitutions store hashed mismatch ledgers, so the validator
independently reconstructs both actual outcomes and checks each ledger hash.
Shape-changing buffers retain complete expected and actual lifetime events.
Surface, PEP 688, threaded, and common-contract cases preserve every
source-ordered actual mismatch. The original public-surface and threaded
digests have no trailing newline; PEP 688 and common-controller digests use
their genuine source-specific representation. Reference exceptions are
expected observations when the original reference also raises.

Original archives can require up to 256 MiB; genuine nested V3 reports use
their own independently frozen bound. Newly published worker and aggregate
reports each have a 32 MiB limit, deterministic gzip, exclusive creation,
no-follow and unchanged-inode checks, complete readback, and file and
directory synchronization. Existing evidence is never overwritten.

## Phase gate

A candidate is correctness-qualified only when all 13 authentic original
producers pass, all 31,237 runnable cases actually execute, all original
interpreter and thread lifecycles are proved, and there are zero unexplained
mismatches, crashes, timeouts, undefined behavior, external-engine loads,
or candidate cross-delegations.

Three genuinely independent passing candidates are required before moving to
performance. Until that gate passes, performance, holdout data, timing,
memory, confidence intervals, rankings, and speedup are **NOT MEASURED**.
This correctness protocol never opens or expands the holdout and never
selects `rebar` or claims `import rebar as re` is ready.
