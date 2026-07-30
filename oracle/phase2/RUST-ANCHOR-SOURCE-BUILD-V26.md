# First-party Rust mandatory-anchor source build V26

This is a phase-two source-build freeze, not a successful replacement or a
final speed comparison. The goal is to compile the already committed,
independently written Rust search improvement together with the already
committed memory-safe capture bridge and corrected Python adapter.

The engine has one first-party Cargo package and zero external dependencies.
Neither source is a wrapper around Python `re`, `_sre`, CPython's engine,
another candidate, an installed matching package, or an external regex engine.
The optimization looks for required later bytes, including alternatives, before
attempting a match. This is a search architecture, not a parser optimization.

## Existing results remain visible

- Latest completed V25 full compatibility run: **FAIL**, with 1,352 unexplained
  differences (240 substitution and 1,112 shape errors), 15,877 verified
  passing cases, 13 completed suites, 13 actual workers, and zero infrastructure
  failures. The previous V24 full run also failed with the same 1,352 errors.
- Latest compiled Rust development result: 416 of 416 public cases agree with
  Python, but those 416 cases are not the full compatibility test.
- Four rounds produced 1,664 public paired measurements: 723 faster, 937 slower,
  and four tied. The equal-case overall speed is 0.8485646292880136 times
  Python, so the existing Rust candidate is slower overall.
- The main dense-search workload is 0.41613883193210616 times Python. Its full
  recorded times are 21,797,729 ns for Python and 102,371,349 ns for Rust. The
  worst measured alternative-search case totals 254,724 ns for Python against
  2,554,459 ns for Rust.
- Native profiling failed before the Rust profiler started. Native profiling,
  confidence intervals, memory, undefined behavior, the optimized candidate's
  complete correctness, and the optimized candidate's speed are **NOT
  MEASURED**.
- The separate strict independence audit remains **FAIL; PRIVATE GETTER
  PRESENT**. Its single finding is
  `CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE`: the private bridge getter can reach
  `inspect`, `tokenize`, and `re.compile`. Public matching delegation is not
  proven, but overall non-delegation is **NOT ESTABLISHED** and the candidate
  does not qualify.
- The expanded 141,557,760-case comparison is only a proposal. Its final
  protocol is not frozen, its cases have not been generated, and it has not
  been opened. Zero independent candidate families currently qualify; three
  are required before final benchmarking can begin.

## SOURCE-ONLY WALL

Normal source verification and sterile self-verification first install an
irreversible, deny-default Python audit wall. They read only individually
authenticated existing public plaintext sources, frozen documents, committed
variants, and already published public development measurements. Every source
has its own exact path, complete SHA-256, byte count, device, inode, mode,
owner, and single-link checks; descriptor identities are checked again after
reading.

The source-only gates rederive both complete optimized Rust sources using the
already frozen first-party transformer and rerun its 11,328 deterministic
source-only semantic checks. They authenticate the actual successful V25
compiler and private-root *public receipts*, both the latest actual V25 and
historical V24 full compatibility failures, the strict failed audit, every one
of the 416 public correctness cases and 1,664 public paired rows, and the
unopened expanded proposal metadata.
They never open an archive, native library, installed candidate, historical
private root, generated case, fixture, or holdout. They start zero compilers,
candidate processes, native libraries, profilers, or benchmark processes,
sample zero clocks, and make zero filesystem changes.

All commands use the separately pinned official CPython 3.14.6 executable with
`-I -B -S`. Source rendering uses `--render-contract` with independent source
and protocol hashes. Normal verification uses `--verify-frozen-context`; the
sterile gate uses `--self-test` and exercises physically intercepted hostile
clock, inherited-descriptor, process, native, private-root, holdout, mutation,
and network events without performing any of those actions. Both gates
independently pin all three complete committed source, protocol, and contract
files.

## Root-authorized actual native build

Only after this complete source freeze has been documented, committed, and
pushed may the root agent invoke `--build`. The command requires explicit
`--root-authorized` and `--frozen-committed-pushed` flags; distinct caller pins
for this controller, protocol, and contract; the complete previous V25 source
freeze and both real V25 success receipts; the committed first-party anchor
transformer, application receipt, and both materialized Rust sources; the safe
capture-clamp bridge; the reconstructed corrected Python adapter; both the
latest failed V25 and historical failed V24 full-correctness receipts; both
distinct strict-audit and runtime-guard V4 triples; the actual strict-audit
failure receipt; phase-one V4; the unopened expanded proposal; and all nine
original Rust source hashes.

The actual controller reuses the authenticated V22/V16/V9/V7 first-party build
lineage. It creates exactly two fresh private `/tmp` source trees with mode
`0700`. Each tree contains exactly nine canonical paths: five unchanged source
owners plus four exclusive, synchronized, reread, mode-`0600` private overlays:

1. Optimized `candidates/rust/src/lib.rs`:
   `5fa8c47c88c1f5d830a59735946378910374afab6f1558d281f0254207ad5e84`,
   189,369 bytes.
2. Optimized `candidates/rust/src/search.rs`:
   `4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7`,
   24,305 bytes.
3. Safe first-party capture-clamp bridge:
   `a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54`,
   178,805 bytes.
4. Reconstructed corrected Python adapter:
   `d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`,
   31,934 bytes.

The optimized Rust sources are independently audited for zero external regex
dependencies. Each private phase executes the same 14 real compiler and ELF
inspection roles as the earlier build, for 28 distinct actual process IDs in
total. Cargo remains locked, frozen, offline, and dependency-free. The entire
engine ELF and bridge ELF must each be byte-identical across the two distinct
private builds; their actual resulting hashes are **NOT MEASURED** until
observed. The historical engine hash must not be assumed to equal the optimized
engine hash.

Actual PASS or FAIL evidence is separately, exclusively, and durably published.
Publication PASS means only that evidence was durably written. A successful
native build retains its exact private root and additionally publishes complete
root provenance, all 28 actual process identities, all 18 independent private
source identities, the two reproduced ELF outputs, all eight overlay
applications, and the exact unchanged identities of every original source and
all four installed runtime targets. A failed native build retains its durable
failure report without inventing root provenance.

The actual build does not import or execute a candidate, run a compatibility
case, sample a clock, execute a timing trial, open the holdout, claim
non-delegation, qualify a candidate, or select a winner. Completing this build
does not resolve the 1,352 earlier compatibility failures, remove the private
getter audit finding, or prove that the new architecture is faster.
