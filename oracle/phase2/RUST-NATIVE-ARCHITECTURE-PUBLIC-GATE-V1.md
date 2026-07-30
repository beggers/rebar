# Independent Rust architecture public gate, version 1

This frozen controller tests two independently built, from-scratch Rust
architectures without replacing the installed candidate. V26 contains the
mandatory-position search architecture; V27 contains the compiler-allocation
architecture. Both use their exact first-party build outputs, the existing
first-party CPython extension, and an independently authenticated corrected
first-party Python adapter.

The pinned interpreter is CPython 3.14.6. Public correctness has exactly 10,434
cases: 94 public datasets multiplied by 111 operations, balanced between text
and bytes. Public profiling has exactly 416 cases: 16 datasets multiplied by 26
operations. Four paired rounds produce exactly 1,664 timing comparisons with
three measured iterations, one warmup, alternating process order, and complete
correctness checks around every timing. Three correctness-gated passes measure
Python heap usage, process maximum resident memory, and user/system CPU time.
External native CPU sampling is **NOT MEASURED**.

The frozen source authenticates both successful independent-build publication
and root-provenance receipts, every existing public correctness and profiling
tool and protocol, public comparison evidence, the original 31,237-case oracle,
and the most recent fully observed original failure. That failure remains 1,352
mismatches: 240 substitution cases and 1,112 shape cases. Public success cannot
erase original failures or establish independence: the strict V4 runtime audit
still has one failure, so runtime nondelegation is **NOT ESTABLISHED** and no
candidate is qualified.

Actual workers use a fresh private `/tmp` overlay. Only unchanged authenticated
public harness sources, the receipt-authenticated corrected adapter, and the
selected exact native engine and bridge are copied into it. Separate pinned
CPython `-I -B -S` processes execute standard-library and candidate work. The
canonical adapter, engine, bridge, and three canonical sources are verified
before and after the operation and are never rewritten, activated, renamed, or
loaded from their canonical paths.

All 10,434 public cases run even when some fail, and every mismatch is saved.
All 416 profiling cases must match before any timing or memory profiling. A
10,434-case failure with complete 416-case parity still permits 1,664 explicitly
exploratory correctness-gated public pairs; the architecture remains failed and
unqualified. Any 416-case mismatch produces zero timing and profiling work. Raw
observations, all timing pairs, all regressions over 20%, deterministic
confidence intervals, per-operation and per-cohort comparisons, memory data,
and an exclusive publication receipt are preserved.

Source-only rendering, verification, and self-test install a physical
deny-default wall before opening any listed owner. The wall rejects every
candidate or native artifact, any private source, final or hidden case content,
dynamic execution, imports, subprocesses, clocks, directory enumeration, and
writes. It never inspects final-holdout metadata or contents. Its holdout claim
is explicitly limited to this frozen controller and its authorized workers;
other agents' historical accesses are **NOT ATTESTED**. The earlier V2 final
proposal is **COMPROMISED AND RETIRED** after a separate out-of-scope read; this
controller never opens or inspects that proposal. The current final holdout is
**INVALIDATED; REKEYED SUCCESSOR REQUIRED**. Hidden case files generated and
hidden cases read by this controller are both zero. Final cases remain
**NOT GENERATED**, the final protocol is **NOT FROZEN**, qualified independent
families remain zero of the required three, and no winner is selected.

Actual execution requires root authorization, identical explicit frozen and
pushed Git commit hashes containing exactly 40 lowercase hexadecimal characters,
exact 64-character controller source/protocol/contract SHA-256 hashes, exact
publication and root-receipt hashes for both V26 and V27, an architecture
choice, and an exclusive architecture-prefixed public session. It is permitted
only after this complete controller/protocol/contract chunk has been committed
and pushed. It never reads, changes, or evaluates a sealed final holdout.
